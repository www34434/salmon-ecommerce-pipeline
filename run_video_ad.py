#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
三文鱼广告环执行器（Stage 5）
执行 Generative-Media-Skills 的 product-video-ad-maker 配方：
  Phase A: 高级商品渲染图（复用 Stage 4 图片环产物）
  Phase B: 图生视频商业广告（DashScope 万相 i2v）
产出: ad_creatives/*.mp4 + ad_manifest.json
"""
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
API_KEY = os.environ.get("DASHSCOPE_API_KEY", "")
BASE = "https://dashscope.aliyuncs.com/api/v1"

MODELS = ["wan2.6-i2v-flash", "wan2.5-i2v-preview", "wan2.2-i2v-flash"]

AD_PROMPT = (
    "A cinematic product advertisement video. Smooth, slow-motion camera movement "
    "panning across the fresh premium salmon fillet on the slate plate. Subtle "
    "environmental movements: soft kitchen light shifting, gentle light reflections "
    "on the moist flesh, mint leaves swaying slightly. High-quality commercial food "
    "cinematography, elegant transitions, appetizing professional look."
)


def clean_image_to_data_uri(image_path: str) -> str:
    """重编码为标准 JPEG（修正万相输出『PNG 数据挂 .jpg 扩展名』问题），返回 base64 data URI"""
    import base64
    import io
    from PIL import Image
    im = Image.open(image_path)
    print(f"[image] 原始格式: {im.format} {im.size} mode={im.mode}")
    if im.mode != "RGB":
        im = im.convert("RGB")
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=90)
    b64 = base64.b64encode(buf.getvalue()).decode()
    print(f"[image] 重编码 JPEG: {len(buf.getvalue())/1024:.0f} KB -> data URI {len(b64)/1024:.0f} KB")
    return f"data:image/jpeg;base64,{b64}"


def create_video_task(model: str, img_url: str):
    r = requests.post(
        f"{BASE}/services/aigc/video-generation/video-synthesis",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
            "X-DashScope-Async": "enable",
        },
        json={"model": model, "input": {"prompt": AD_PROMPT, "img_url": img_url},
              "parameters": {"prompt_extend": True, "resolution": "1080P",
                             "duration": 5, "audio": False}},
        timeout=60,
    )
    return r


def poll_task(task_id: str, max_wait: int = 480):
    url = f"{BASE}/tasks/{task_id}"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    start = time.time()
    while time.time() - start < max_wait:
        r = requests.get(url, headers=headers, timeout=30)
        data = r.json()
        status = data.get("output", {}).get("task_status", "UNKNOWN")
        print(f"[poll] {int(time.time()-start)}s status={status}")
        if status == "SUCCEEDED":
            return data["output"].get("video_url") or data["output"].get("video_mp4_url")
        if status in ("FAILED", "CANCELED"):
            print(f"[poll] task failed: {json.dumps(data.get('output', {}), ensure_ascii=False)[:500]}")
            return None
        time.sleep(12)
    print("[poll] timeout")
    return None


def main():
    if not API_KEY:
        print("DASHSCOPE_API_KEY 未设置")
        sys.exit(1)

    # 选择参考图：默认场景展示图（最具商业感），可命令行覆盖
    image = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "image_set", "场景展示图.jpg")
    if not os.path.exists(image):
        print(f"参考图不存在: {image}")
        sys.exit(1)

    out_dir = os.path.join(HERE, "ad_creatives")
    os.makedirs(out_dir, exist_ok=True)

    # ── Phase B: 图生视频 ──
    img_url = clean_image_to_data_uri(image)
    video_url = None
    used_model = None
    for model in MODELS:
        print(f"\n[video] 尝试模型: {model}")
        r = create_video_task(model, img_url)
        body = r.json()
        if r.status_code != 200:
            print(f"[video] {model} 创建失败: {str(body)[:200]}")
            continue
        task_id = body["output"]["task_id"]
        print(f"[video] task_id={task_id}")
        video_url = poll_task(task_id)
        if video_url:
            used_model = model
            break
        print(f"[video] {model} 未成功，尝试下一个模型")

    if not video_url:
        print("\n[FAIL] 所有模型均未成功生成视频")
        sys.exit(1)

    # ── 下载视频 ──
    mp4 = os.path.join(out_dir, "salmon_product_ad.mp4")
    print(f"\n[download] {video_url[:100]}...")
    with requests.get(video_url, stream=True, timeout=600) as resp:
        resp.raise_for_status()
        with open(mp4, "wb") as f:
            for chunk in resp.iter_content(1024 * 512):
                f.write(chunk)
    size_mb = os.path.getsize(mp4) / 1024 / 1024
    print(f"[download] OK -> {mp4} ({size_mb:.1f} MB)")

    # ── 产出广告清单（视频 + 文案变体，来自 product.json 卖点）──
    with open(os.path.join(HERE, "product.json"), "r", encoding="utf-8") as f:
        product = json.load(f)
    sp = product.get("selling_points", [])
    manifest = {
        "reference_image": image,
        "recipe": "muapi-product-video-ad-maker (Phase A=Stage4套图, Phase B=wan i2v)",
        "model": used_model,
        "creatives": [
            {
                "type": "product_video_ad",
                "path": mp4,
                "duration_estimate": "5-10s",
                "platform": ["douyin", "shipinhao", "xiaohongshu"],
                "source_image": image,
            },
            {"type": "copy_main", "copy": "挪威原切 · 刺身级 · 一口尝尽北大西洋", "platform": "douyin"},
            {"type": "copy_variant_B", "copy": f"{sp[0]['zh']}｜{sp[1]['zh']}｜{sp[2]['zh']}" if len(sp) >= 3 else "优质新鲜｜天然食材｜精致摆盘", "platform": "xiaohongshu"},
            {"type": "copy_variant_C", "copy": "健身餐必备：高蛋白低脂三文鱼，每周直送", "platform": "taobao"},
        ],
        "prompt": AD_PROMPT,
    }
    mpath = os.path.join(HERE, "ad_manifest.json")
    with open(mpath, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"\n[DONE] 视频: {mp4}")
    print(f"[DONE] 广告清单: {mpath}")


if __name__ == "__main__":
    main()
