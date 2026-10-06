#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cart API 实时找品客户端（Stage 1 sourcing live 模式）
直接调用 Cart REST API（api.usecart.com），无需 Node.js/MCP 服务器。

鉴权: CART_API_KEY 环境变量（cart_sk_...，从 usecart.com/developers 获取）
输出: 与 run_pipeline.py 数据契约一致的 candidate_products.json

用法:
  python cart_api_client.py --keyword "salmon 三文鱼" --out candidate_products.json
"""
import argparse
import json
import os
import sys
import urllib.request
import urllib.error
import ssl

API_BASE = "https://api.usecart.com"
# 候选端点：404=路径不存在, 401/403=路径存在但未授权（以此区分有效路径）
CANDIDATE_PATHS = [
    "/v1/products/search",
    "/v1/search",
    "/v1/products",
    "/v1/discovery/products/search",
    "/products/search",
    "/search",
]
# 鉴权头候选方案
AUTH_SCHEMES = [
    ("Authorization", "Bearer {key}"),
    ("X-API-Key", "{key}"),
    ("Authorization", "{key}"),
]


def _request(url, headers, timeout=30):
    req = urllib.request.Request(url, headers={**headers, "Accept": "application/json",
                                               "User-Agent": "salmon-pipeline/1.0"})
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8", "replace")), None
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8", "replace")[:300]
        except Exception:
            pass
        return e.code, None, body
    except Exception as e:
        return None, None, str(e)


def discover(key):
    """探测可用端点 + 鉴权方案，返回 (path, headers) 或 (None, 原因)"""
    for hname, htpl in AUTH_SCHEMES:
        headers = {hname: htpl.format(key=key)}
        for path in CANDIDATE_PATHS:
            url = f"{API_BASE}{path}?q=salmon&keyword=salmon"
            status, data, err = _request(url, headers)
            if status in (401, 403):
                # 路径存在但该鉴权头未通过
                continue
            if status == 404:
                continue
            if status == 200 and data is not None:
                return path, headers
            if status is None:
                print(f"[discover] 网络错误 {url}: {err}")
        # 每种鉴权方案试完全部路径后打点
    return None, "所有端点/鉴权组合均未返回 200（密钥无效或端点变更）"


def _pick(d, *names, default=None):
    for n in names:
        if isinstance(d, dict) and n in d and d[n] is not None:
            return d[n]
    return default


def normalize(data, keyword):
    """将 Cart API 响应归一化为流水线契约（字段名自适应）"""
    items = None
    if isinstance(data, dict):
        items = _pick(data, "products", "items", "results", "data", "hits")
        if isinstance(items, dict):
            items = _pick(items, "products", "items", "results")
    elif isinstance(data, list):
        items = data
    if items is None:
        items = []

    candidates = []
    for it in items[:50]:
        if not isinstance(it, dict):
            continue
        price = _pick(it, "price", "current_price", "min_price", "lowest_price")
        try:
            price = round(float(price), 2) if price is not None else None
        except (TypeError, ValueError):
            price = None
        candidates.append({
            "sku": str(_pick(it, "sku", "id", "product_id", "asin", default="")),
            "title": str(_pick(it, "title", "name", "product_title", "product_name", default="")),
            "price": price,
            "store": str(_pick(it, "store", "vendor", "seller", "brand", "merchant", default="")),
            "url": _pick(it, "url", "link", "product_url", default=""),
            "trending": bool(_pick(it, "trending", "is_trending", default=False)),
            "velocity": str(_pick(it, "velocity", "sales_velocity", "trend", default="unknown")),
        })

    prices = sorted(c["price"] for c in candidates if c["price"] is not None)
    pricing = {
        "min": prices[0] if prices else None,
        "max": prices[-1] if prices else None,
        "median": prices[len(prices) // 2] if prices else None,
        "common": sorted({p for p in prices})[:5],
    }
    # 店铺聚合
    vendors = {}
    for c in candidates:
        if c["store"]:
            vendors[c["store"]] = vendors.get(c["store"], 0) + 1

    return {
        "keyword": keyword,
        "candidates": candidates,
        "pricing": pricing,
        "vendors": [{"name": k, "product_count": v} for k, v in sorted(vendors.items(), key=lambda x: -x[1])],
        "suppliers": [],  # Cart API 不含供应商，沿用模拟数据由调用方合并
        "opportunity_score": None,
        "recommended_focus": "",
        "raw_response_sample": json.dumps(data, ensure_ascii=False)[:500],
        "mode": "live",
    }


def main():
    ap = argparse.ArgumentParser(description="Cart API 实时找品客户端")
    ap.add_argument("--keyword", default="salmon")
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    key = os.environ.get("CART_API_KEY", "").strip()
    if not key:
        print("[ERROR] CART_API_KEY 未设置", file=sys.stderr)
        sys.exit(2)

    print(f"[live] 发现可用端点与鉴权方案...")
    path, headers = discover(key)
    if path is None:
        print(f"[ERROR] {headers}", file=sys.stderr)
        sys.exit(3)
    print(f"[live] 命中端点: {path}")

    url = f"{API_BASE}{path}?q={urllib.parse.quote(args.keyword)}&keyword={urllib.parse.quote(args.keyword)}&limit=50"
    status, data, err = _request(url, headers)
    if status != 200 or data is None:
        print(f"[ERROR] 搜索失败 HTTP {status}: {err}", file=sys.stderr)
        sys.exit(4)

    result = normalize(data, args.keyword)
    out = args.out or "candidate_products.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"[live] {len(result['candidates'])} 个候选 -> {out}")


if __name__ == "__main__":
    import urllib.parse
    main()
