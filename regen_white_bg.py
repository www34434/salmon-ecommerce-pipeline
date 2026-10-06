#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
白底主图 v2 重生成（严格纯白背景，去除石板道具）
直调 wan2.7-image-pro 异步接口，输出 image_set/白底主图v2.jpg
"""
import base64
import json
import os
import sys
import time
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
_orig = requests.Session.request
def _no_ssl(self, method, url, **kw):
    kw.setdefault("verify", False)
    return _orig(self, method, url, **kw)
requests.Session.request = _no_ssl

HERE = os.path.dirname(os.path.abspath(__file__))
KEY = os.environ.get("DASHSCOPE_API_KEY", "")
MODEL = "wan2.7-image-pro"

PROMPT = (
    "E-commerce product main image, strict pure white seamless background (RGB 255,255,255). "
    "Fresh premium Norwegian salmon sashimi fillet, vivid orange-pink flesh with clear white fat "
    "lines, sliced into thick sashimi pieces fanned in an elegant arc directly on the pure white "
    "surface, no plate, no slate, no wooden board, no props, no garnish. Soft even studio lighting, "
    "subtle natural shadow beneath the fish only, glistening moist texture, ultra fresh appearance. "
    "Centered composition filling 85% of frame, top-down 15-degree angle, professional food "
    "photography, hyper-detailed, appetizing. Absolutely nothing in the frame except the salmon "
    "and the white background."
)


def main():
    if not KEY:
        print("DASHSCOPE_API_KEY 未设置")
        sys.exit(1)
    headers = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}
    r = requests.post(
        "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation",
        headers=headers,
        json={"model": MODEL,
              "input": {"messages": [{"role": "user", "content": [{"text": PROMPT}]}]},
              "parameters": {"size": "2048*2048", "n": 1, "watermark": False}},
        timeout=60,
    )
    body = r.json()
    if r.status_code != 200:
        print(f"[ERROR] 创建任务失败: {str(body)[:300]}")
        sys.exit(2)

    # 同步响应直接解析图片
    choices = body.get("output", {}).get("choices", [])
    img_url = None
    if choices:
        content = choices[0].get("message", {}).get("content", [])
        if content:
            img_url = content[0].get("image")
    if not img_url:
        results = body.get("output", {}).get("results", [])
        if results:
            img_url = results[0].get("url")
    if not img_url:
        print(f"[ERROR] 响应中无图片: {str(body)[:400]}")
        sys.exit(4)
    print(f"[img] {img_url[:100]}")

    out = os.path.join(HERE, "image_set", "白底主图v2.jpg")
    with requests.get(img_url, stream=True, timeout=120) as resp:
        resp.raise_for_status()
        with open(out, "wb") as f:
            for chunk in resp.iter_content(1024 * 256):
                f.write(chunk)
    print(f"[DONE] {out} ({os.path.getsize(out)/1024/1024:.1f} MB)")


if __name__ == "__main__":
    main()
