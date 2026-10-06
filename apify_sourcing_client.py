#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APIFY 实时找品客户端（Stage 1 sourcing live 模式 · 备选方案）
通过 Apify Actors API 运行 Amazon Product Scraper，抓取真实三文鱼商品数据，
归一化为流水线 candidate_products.json 契约。

鉴权: APIFY_TOKEN 环境变量（apify.com → Settings → API & Integrations）
用法:
  python apify_sourcing_client.py --keyword "salmon" --out candidate_products.json
"""
import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error
import urllib.parse
import ssl

API_BASE = "https://api.apify.com"
STORE_SEARCH = "/v2/store?search={q}&limit={n}"
RUN_ACTOR = "/v2/acts/{actor}/runs"          # actor 形如 username~actorName
RUN_STATUS = "/v2/actor-runs/{run_id}"
DATASET_ITEMS = "/v2/datasets/{ds_id}/items"

# Amazon 输出字段候选（实测 igview-owner/amazon-search-scraper schema + 常见抓取器自适应归一化）
F = {
    "sku": ["asin", "id", "product_id"],
    "title": ["product_title", "title", "name"],
    "price": ["product_price", "currentPrice", "price", "priceValue"],
    "store": ["sellerName", "brand", "merchantName", "soldBy", "store"],
    "url": ["product_url", "url", "productUrl", "link"],
    "rating": ["product_star_rating", "rating", "stars"],
    "reviews": ["product_num_ratings", "reviewsCount", "reviewsNumber", "numberOfReviews"],
    "sales_volume": ["sales_volume", "boughtPastMonth"],
}

# 找品 input 关键字段候选（实测 igview-owner/amazon-search-scraper 用 query）
INPUT_KEYWORD_KEYS = ["query", "search_query", "keyword", "search", "searchTerms", "phrase"]


def parse_price(v):
    """解析 '$59.99' / '$1,299.00' / 59.99 等为 float"""
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return round(float(v), 2)
    import re
    m = re.search(r"[\d][\d,.]*", str(v))
    if not m:
        return None
    s = m.group(0).replace(",", "")
    try:
        return round(float(s), 2)
    except ValueError:
        return None


def parse_velocity(sales_volume, reviews):
    """sales_volume（如 '1K+ bought in past month'）优先，评论量兜底"""
    if sales_volume:
        sv = str(sales_volume)
        if "K+" in sv or "M+" in sv:
            return "very high"
        import re
        m = re.search(r"(\d+)\+", sv)
        if m and int(m.group(1)) >= 300:
            return "high"
        if m:
            return "rising"
    return ("very high" if reviews >= 5000 else
            "high" if reviews >= 1000 else
            "rising" if reviews >= 100 else "niche")


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


# 优先级 Actor 列表：关键词搜索型在前（junglee~Amazon-crawler 为 URL 型，仅作兜底）
PREFERRED_ACTORS = [
    "igview-owner~amazon-search-scraper",
    "epctex~amazon-scraper",
    "junglee~Amazon-crawler",
]


def find_amazon_actor():
    """优先用关键词搜索型 Actor；store 搜索结果为校验和兜底"""
    url = API_BASE + STORE_SEARCH.format(q=urllib.parse.quote("amazon product scraper"), n=8)
    status, data = _request(url)
    store_names = set()
    if status == 200 and data:
        for it in data.get("data", {}).get("items", []):
            store_names.add(f"{it.get('username')}~{it.get('name')}")
            if it.get("username") == "igview-owner" and it.get("name") == "amazon-search-scraper":
                return {"actor": "igview-owner~amazon-search-scraper", "title": it.get("title"),
                        "defaultRunInput": it.get("defaultRunInput")}, None
    for actor in PREFERRED_ACTORS:
        if actor in store_names or actor == "igview-owner~amazon-search-scraper":
            return {"actor": actor, "title": actor, "defaultRunInput": None}, None
    if store_names:
        it_actor = next(iter(store_names))
        return {"actor": it_actor, "title": it_actor, "defaultRunInput": None}, None
    return None, "Store 无结果"


def build_input(actor_meta, keyword):
    """优先用 Actor 的 defaultRunInput 模板替换关键词，否则构造最小 input"""
    raw = (actor_meta or {}).get("defaultRunInput")
    if raw:
        try:
            tpl = json.loads(raw) if isinstance(raw, str) else dict(raw)
            if isinstance(tpl, dict):
                for k in INPUT_KEYWORD_KEYS:
                    if k in tpl:
                        tpl[k] = keyword
                        return tpl
                tpl["keyword"] = keyword  # 模板无关键词字段时补一个
                return tpl
        except (ValueError, TypeError):
            pass
    return {INPUT_KEYWORD_KEYS[0]: keyword, "maxPages": 1}


def run_actor(actor, run_input, token, wait_secs=240):
    """运行 Actor：先长等待，超时则轮询"""
    url = (API_BASE + RUN_ACTOR.format(actor=actor)
           + f"?token={urllib.parse.quote(token)}&waitForFinish={wait_secs}")
    status, run = _request(url, method="POST", body=run_input, timeout=wait_secs + 60)
    if status not in (200, 201) or not run:
        return None, f"运行创建失败 HTTP {status}: {json.dumps(run, ensure_ascii=False)[:200]}"
    run = run.get("data", run)
    run_id = run.get("id")
    poll = 0
    while run.get("status") in ("READY", "RUNNING") and poll < 30:
        time.sleep(10)
        poll += 1
        s, run = _request(API_BASE + RUN_STATUS.format(run_id=run_id) + f"?token={urllib.parse.quote(token)}")
        if s != 200 or not run:
            break
        run = run.get("data", run)
        print(f"[live] 运行中 {poll*10}s status={run.get('status')}")
    return run, None


def fetch_items(dataset_id, token, limit=50):
    url = (API_BASE + DATASET_ITEMS.format(ds_id=dataset_id)
           + f"?token={urllib.parse.quote(token)}&limit={limit}&clean=true")
    status, items = _request(url, timeout=120)
    if status != 200 or not isinstance(items, list):
        return None, f"数据集拉取失败 HTTP {status}"
    return items, None


def normalize(items, keyword, actor):
    candidates = []
    for it in items[:50]:
        if not isinstance(it, dict):
            continue
        price = parse_price(_pick(it, F["price"]))
        reviews = _pick(it, F["reviews"]) or 0
        try:
            reviews = int(reviews)
        except (TypeError, ValueError):
            reviews = 0
        # 月销信号优先，评论量兜底
        velocity = parse_velocity(_pick(it, F["sales_volume"]), reviews)
        title = str(_pick(it, F["title"], default=""))[:120]
        # 三文鱼相关性过滤（搜手机等默认词或脏数据时剔除）
        kw = [w for w in keyword.lower().split() if len(w) > 2]
        if kw and not any(w in title.lower() for w in kw):
            continue
        candidates.append({
            "sku": str(_pick(it, F["sku"], default="")),
            "title": title,
            "price": price,
            "store": str(_pick(it, F["store"], default=""))[:60],
            "url": _pick(it, F["url"], default=""),
            "rating": _pick(it, F["rating"]),
            "reviews": reviews,
            "sales_volume": _pick(it, F["sales_volume"], default=""),
            "trending": velocity in ("high", "very high"),
            "velocity": velocity,
        })

    prices = sorted(c["price"] for c in candidates if c["price"] is not None)
    pricing = {
        "min": prices[0] if prices else None,
        "max": prices[-1] if prices else None,
        "median": prices[len(prices) // 2] if prices else None,
        "common": sorted({p for p in prices})[:5],
    }
    vendors = {}
    for c in candidates:
        if c["store"]:
            vendors[c["store"]] = vendors.get(c["store"], 0) + 1
    hot = [c for c in candidates if c["trending"]]
    return {
        "keyword": keyword,
        "candidates": candidates,
        "pricing": pricing,
        "vendors": [{"name": k, "product_count": v} for k, v in sorted(vendors.items(), key=lambda x: -x[1])],
        "suppliers": [],
        "opportunity_score": None,
        "recommended_focus": (f"高热商品 {len(hot)}/{len(candidates)} 个（月销300+/评论1000+）"
                              if candidates else ""),
        "source": {"provider": "apify", "actor": actor},
        "mode": "live",
    }


def main():
    ap = argparse.ArgumentParser(description="APIFY 实时找品客户端")
    ap.add_argument("--keyword", default="salmon")
    ap.add_argument("--out", default="candidate_products.json")
    ap.add_argument("--limit", type=int, default=50)
    ap.add_argument("--run-id", default="", help="挂接已有运行（不新起 run，避免重复计费）")
    args = ap.parse_args()

    token = os.environ.get("APIFY_TOKEN", "").strip()
    if not token:
        print("[ERROR] APIFY_TOKEN 未设置（apify.com → Settings → API & Integrations）", file=sys.stderr)
        sys.exit(2)

    if args.run_id:
        run = {"id": args.run_id, "status": "READY"}
        actor = "(attached)"
        # 轮询已有运行至结束
        poll = 0
        while run.get("status") in ("READY", "RUNNING") and poll < 60:
            time.sleep(10)
            poll += 1
            s, run = _request(API_BASE + RUN_STATUS.format(run_id=args.run_id)
                              + f"?token={urllib.parse.quote(token)}")
            if s != 200 or not run:
                break
            run = run.get("data", run)
            print(f"[live] 挂接运行 {poll*10}s status={run.get('status')}")
    else:
        actor_meta, err = find_amazon_actor()
        if actor_meta is None:
            print(f"[ERROR] {err}", file=sys.stderr)
            sys.exit(3)
        actor = actor_meta["actor"]
        print(f"[live] Actor: {actor} ({actor_meta['title']})")
        run_input = build_input(actor_meta, args.keyword)
        print(f"[live] 运行 input: {json.dumps(run_input, ensure_ascii=False)[:200]}")
        run, err = run_actor(actor, run_input, token)
        if run is None:
            print(f"[ERROR] {err}", file=sys.stderr)
            sys.exit(4)
    status = run.get("status")
    print(f"[live] 运行结束 status={status}")
    if status != "SUCCEEDED":
        print(f"[ERROR] 运行未成功: {status}", file=sys.stderr)
        sys.exit(5)

    ds_id = run.get("defaultDatasetId")
    items, err = fetch_items(ds_id, token, args.limit)
    if items is None:
        print(f"[ERROR] {err}", file=sys.stderr)
        sys.exit(6)
    print(f"[live] 抓到 {len(items)} 条原始商品数据")

    result = normalize(items, args.keyword, actor)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"[live] {len(result['candidates'])} 个候选 -> {args.out}")


if __name__ == "__main__":
    main()
