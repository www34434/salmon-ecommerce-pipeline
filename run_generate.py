#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""包装脚本：读取 product.json，调用 generate.py 生成三文鱼套图"""
import json
import subprocess
import sys
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PRODUCT = os.path.join(HERE, "product.json")
GENERATE = os.path.join(os.path.dirname(HERE), "ecommerce-image-suite", "scripts", "generate.py")
OUT = os.path.join(HERE, "image_set")

with open(PRODUCT, "r", encoding="utf-8") as f:
    product = json.load(f)

product_str = json.dumps(product, ensure_ascii=False)
print(f"[run_generate] product JSON loaded, len={len(product_str)}")
print(f"[run_generate] output dir: {OUT}")
print(f"[run_generate] types: white_bg,key_features,lifestyle")

cmd = [
    sys.executable, GENERATE,
    "--product", product_str,
    "--provider", "tongyi",
    "--lang", "zh",
    "--types", "white_bg,key_features,lifestyle",
    "--output-dir", OUT,
]
print(f"[run_generate] cmd: {cmd[0]} {GENERATE} --provider tongyi --lang zh --types white_bg,key_features,lifestyle --output-dir {OUT}")
print("[run_generate] launching generate.py ...\n")

result = subprocess.run(cmd)
print(f"\n[run_generate] generate.py exited with code {result.returncode}")
