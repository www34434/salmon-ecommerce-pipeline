#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APIFY 竞品评论抓取客户端（Stage 2 data live 模式）
运行 junglee/amazon-reviews-scraper 抓头部竞品真实评论，
提取差评主题词云 + 好评主题，归一化为流水线 competitive_intel.json 契约。

鉴权: APIFY_TOKEN 环境变量
用法:
  python apify_reviews_client.py --asins B0732ZP2HC,B08CP5DBC6 --out competitive_intel.json
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
import urllib.parse
import ssl
from collections import Counter

API_BASE = "https://api.apify.com"
RUN_ACTOR = "/v2/acts/{actor}/runs"
RUN_STATUS = "/v2/actor-runs/{run_id}"
DATASET_ITEMS = "/v2/datasets/{ds_id}/items"
REVIEWS_ACTOR = "junglee~amazon-reviews-scraper"

# 差评/好评英文关键词 → 中文主题（对齐流水线负面词云契约：化冻/冷链断链/缺重/异味...）
NEG_THEMES = {
    "化冻": ["thaw", "melt", "slimy", "soft", "warm", "partially frozen"],
    "不新鲜": ["not fresh", "stale", "expired", "old", "off", "gone bad", "rotten"],
    "异味": ["smell", "odor", "stink", "fishy"],
    "包装破损": ["packaging", "leak", "broken", "damaged", "crushed", "opened"],
    "冷链断链": ["ice pack", "melted ice", "dry ice", "no ice", "cold pack", "insulation"],
    "缺重": ["short weight", "underweight", "less than", "small portion", "tiny"],
    "口感差": ["mushy", "dry", "tough", "rubbery", "watery", "bland"],
}
POS_THEMES = {
    "新鲜": ["fresh", "freshness"],
    "口感好": ["taste", "delicious", "flavor", "tender", "buttery", "rich"],
    "品质稳定": ["quality", "consistent", "reliable", "never disappoint"],
    "冷链可靠": ["arrived cold", "well packed", "still frozen", "cold on arrival"],
    "性价比": ["value", "price", "affordable", "worth"],
    "复购意愿": ["will buy again", "reorder", "subscribe", "again and again"],
}

# 竞品默认 ASIN（candidate_products_live.json 头部，评论量加权）
DEFAULT_ASINS = "B0732ZP2HC,B08CP5DBC6,B07NRCDJNX,B07ZS3D7WB,B0BWNW4B2D,B00LKX6PEQ"


def _request(url, method="GET", body=None, timeout=60):
    headers = {"Accept": "application/json", "Content-Type": "application/json",
               "User-Agent": "salmon-pipeline/1.0"}
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode("utf-8", "replace"))
        except Exception:
            return e.code, None
    except Exception as e:
        return None, {"error": str(e)}


def _pick(d, names, default=None):
    for n in names:
        if isinstance(d, dict) and d.get(n) is not None:
            return d[n]
    return default


def run_actor(actor, run_input, token, wait_secs=300):
    url = (API_BASE + RUN_ACTOR.format(actor=actor)
           + f"?token={urllib.parse.quote(token)}&waitForFinish={wait_secs}")
    status, run = _request(url, method="POST", body=run_input, timeout=wait_secs + 60)
    if status not in (200, 201) or not run:
        return None, f"运行创建失败 HTTP {status}: {json.dumps(run, ensure_ascii=False)[:200]}"
    run = run.get("data", run)
    run_id = run.get("id")
    poll = 0
    while run.get("status") in ("READY", "RUNNING") and poll < 36:
        time.sleep(10)
        poll += 1
        s, run = _request(API_BASE + RUN_STATUS.format(run_id=run_id) + f"?token={urllib.parse.quote(token)}")
        if s != 200 or not run:
            break
        run = run.get("data", run)
        print(f"[live] 运行中 {poll*10}s status={run.get('status')}")
    return run, None


def fetch_items(dataset_id, token, limit=500):
    url = (API_BASE + DATASET_ITEMS.format(ds_id=dataset_id)
           + f"?token={urllib.parse.quote(token)}&limit={limit}&clean=true")
    status, items = _request(url, timeout=180)
    if status != 200 or not isinstance(items, list):
        return None, f"数据集拉取失败 HTTP {status}"
    return items, None


def theme_counts(texts, themes):
    """对评论文本集合做主题匹配，返回 [(主题, 命中数)] 降序"""
    counts = Counter()
    for t in texts:
        tl = t.lower()
        for theme, kws in themes.items():
            if any(kw in tl for kw in kws):
                counts[theme] += 1
    return counts.most_common()


def normalize(items, asins):
    ratings = []
    neg_texts, pos_texts = [], []
    neg_examples = []
    per_product = {}
    for it in items:
        if not isinstance(it, dict):
            continue
        r = _pick(it, ["reviewRating", "rating", "stars", "starRating"])
        try:
            r = int(float(str(r).split("/")[0].strip()))
        except (TypeError, ValueError):
            r = None
        title = str(_pick(it, ["reviewTitle", "title"], default="") or "")
        desc = str(_pick(it, ["reviewDescription", "description", "text"], default="") or "")
        text = (title + " " + desc).strip()
        asin = str(_pick(it, ["productAsin", "asin", "product_id"], default="") or "")
        if not text:
            continue
        if asin:
            p = per_product.setdefault(asin, {"total": 0, "neg": 0, "sum_rating": 0})
            p["total"] += 1
            if r is not None:
                p["sum_rating"] += r
                ratings.append(r)
            if r is not None and r <= 3:
                p["neg"] += 1
                neg_texts.append(text)
                if len(neg_examples) < 8:
                    neg_examples.append({"asin": asin, "rating": r,
                                         "title": title[:80], "text": desc[:160]})
            else:
                pos_texts.append(text)
        elif r is not None:
            ratings.append(r)

    avg = round(sum(ratings) / len(ratings), 2) if ratings else None
    neg_cloud = [{"theme": k, "count": v} for k, v in theme_counts(neg_texts, NEG_THEMES)]
    pos_cloud = [{"theme": k, "count": v} for k, v in theme_counts(pos_texts, POS_THEMES)]
    competitors = []
    for a, p in per_product.items():
        competitors.append({
            "asin": a,
            "reviews_scraped": p["total"],
            "avg_rating": round(p["sum_rating"] / p["total"], 2) if p["total"] else None,
            "negative_rate": round(p["neg"] / p["total"], 3) if p["total"] else None,
        })
    competitors.sort(key=lambda x: -(x["reviews_scraped"] or 0))
    return {
        "reviews": {
            "avg": avg,
            "scraped_total": len(ratings),
            "negatives": [k for k, _ in neg_cloud],
            "negatives_detail": neg_cloud,
            "positives": [k for k, _ in pos_cloud],
            "examples_negative": neg_examples,
        },
        "competitor_reviews": competitors,
        "mode": "live",
    }


def main():
    ap = argparse.ArgumentParser(description="APIFY 竞品评论抓取客户端")
    ap.add_argument("--asins", default=DEFAULT_ASINS, help="逗号分隔的 Amazon ASIN")
    ap.add_argument("--max-reviews", type=int, default=40, help="每个商品最多抓取评论数")
    ap.add_argument("--out", default="competitive_intel.json")
    args = ap.parse_args()

    token = os.environ.get("APIFY_TOKEN", "").strip()
    if not token:
        print("[ERROR] APIFY_TOKEN 未设置", file=sys.stderr)
        sys.exit(2)

    asins = [a.strip() for a in args.asins.split(",") if a.strip()]
    urls = [f"https://www.amazon.com/dp/{a}" for a in asins]
    run_input = {"productUrls": urls, "maxReviews": args.max_reviews}
    print(f"[live] {len(asins)} 个竞品 × 每品 ≤{args.max_reviews} 条评论")

    run, err = run_actor(REVIEWS_ACTOR, run_input, token)
    if run is None:
        print(f"[ERROR] {err}", file=sys.stderr)
        sys.exit(4)
    status = run.get("status")
    print(f"[live] 运行结束 status={status}")
    if status != "SUCCEEDED":
        print(f"[ERROR] 运行未成功: {status}", file=sys.stderr)
        sys.exit(5)

    items, err = fetch_items(run.get("defaultDatasetId"), token)
    if items is None:
        print(f"[ERROR] {err}", file=sys.stderr)
        sys.exit(6)
    print(f"[live] 抓到 {len(items)} 条评论")

    result = normalize(items, asins)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"[live] 差评词云: {[d['theme'] for d in result['reviews']['negatives_detail']]}")
    print(f"[live] -> {args.out}")


if __name__ == "__main__":
    main()
