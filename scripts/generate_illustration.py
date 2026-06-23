#!/usr/bin/env python3
"""
scenario-english 对话分格插图生成器（可选）

复用 nano-banana 的生图机制（laozhang.ai → Gemini Image），但只做一件事：
为对话节拍生成一张 **成人向、无文字** 的氛围插图。

判断原则（重要）：插图只用于"文字少"的画面氛围。所有词/句/对话本身由 HTML 排版承载，
绝不靠生图（生图模型的文字必糊）。没有 API key 时跳过本步，对话以纯文字呈现，页面依然完整。

用法:
    # 先验 key
    python generate_illustration.py --check-key --api-key KEY
    # 生成一张分格插图（自动套成人插画风格、强制图里无字）
    python generate_illustration.py -p "two professionals on a video call, one looks thoughtful" \
        --ratio 4:3 -o beat3.png --api-key KEY

生成的 PNG 路径写到 stdout，便于填回内容 JSON 的 beat.illustration 字段。
"""

import argparse
import base64
import json
import os
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

API_URL = "https://api.laozhang.ai/v1beta/models/gemini-3-pro-image-preview:generateContent"
REQUEST_TIMEOUT = 120
MAX_RETRIES = 1

# 成人向插画风格锚点 —— 与卡通儿童海报彻底切割，且强制图里无字
STYLE_ANCHOR = (
    "clean modern editorial line illustration, minimal flat vector style, "
    "muted sophisticated color palette, adult professionals with neutral realistic proportions, "
    "calm and tasteful composition. "
    "ABSOLUTELY NO TEXT, no letters, no words, no speech bubbles in the image. "
    "Not cartoon, not childish, no anthropomorphic animals, no chibi style."
)


def build_body(prompt: str, ratio: str) -> dict:
    return {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["image", "text"],
            "aspectRatio": ratio,
            "imageSize": "2K",
        },
    }


def extract_image(resp: dict) -> bytes:
    for cand in resp.get("candidates", []):
        for part in cand.get("content", {}).get("parts", []):
            inline = part.get("inlineData")
            if inline and inline.get("data"):
                return base64.b64decode(inline["data"])
    print("错误: 未能从响应中提取图片", file=sys.stderr)
    print(json.dumps(resp, ensure_ascii=False)[:800], file=sys.stderr)
    sys.exit(1)


def call_api(prompt: str, ratio: str, key: str) -> bytes:
    data = json.dumps(build_body(prompt, ratio)).encode()
    req = Request(API_URL, data=data, method="POST", headers={
        "Content-Type": "application/json", "Authorization": f"Bearer {key}"})
    last = None
    for attempt in range(1 + MAX_RETRIES):
        if attempt:
            print(f"重试 {attempt}...", file=sys.stderr)
            time.sleep(3)
        try:
            with urlopen(req, timeout=REQUEST_TIMEOUT) as r:
                return extract_image(json.loads(r.read().decode()))
        except HTTPError as e:
            last = e
            body = e.read().decode("utf-8", "replace")
            if e.code == 401:
                print("错误: API Key 无效或过期", file=sys.stderr); sys.exit(1)
            if e.code == 402 or "insufficient" in body.lower():
                print("错误: API 余额不足", file=sys.stderr); sys.exit(1)
            print(f"API 错误 HTTP {e.code}: {body[:300]}", file=sys.stderr)
        except (URLError, TimeoutError) as e:
            last = e
            print(f"网络错误: {e}", file=sys.stderr)
    print(f"失败: {last}", file=sys.stderr)
    sys.exit(1)


def check_key(key: str):
    body = json.dumps({"contents": [{"parts": [{"text": "Hi"}]}],
                       "generationConfig": {"responseModalities": ["text"]}}).encode()
    req = Request(API_URL, data=body, method="POST", headers={
        "Content-Type": "application/json", "Authorization": f"Bearer {key}"})
    try:
        with urlopen(req, timeout=30) as r:
            r.read()
        print("API Key 验证通过")
        sys.exit(0)
    except HTTPError as e:
        b = e.read().decode("utf-8", "replace")
        msg = "无效或过期" if e.code == 401 else ("余额不足" if e.code == 402 else f"HTTP {e.code}: {b[:200]}")
        print(f"错误: {msg}", file=sys.stderr); sys.exit(1)
    except (URLError, TimeoutError) as e:
        print(f"网络错误: {e}", file=sys.stderr); sys.exit(1)


def main():
    ap = argparse.ArgumentParser(description="对话分格插图生成（成人向·无文字）")
    ap.add_argument("--prompt", "-p", help="画面描述（场景/人物/情绪），不要含文字内容")
    ap.add_argument("--file", "-f", help="从文件读取画面描述")
    ap.add_argument("--ratio", default="4:3", help="比例（默认 4:3，可 1:1 / 16:9）")
    ap.add_argument("--out", "-o", required=False, help="输出 PNG 路径")
    ap.add_argument("--raw", action="store_true", help="不自动叠加成人插画风格锚点")
    ap.add_argument("--api-key", help="laozhang.ai API Key（或环境变量 LAOZHANG_API_KEY）")
    ap.add_argument("--check-key", action="store_true", help="仅验证 key")
    args = ap.parse_args()

    key = args.api_key or os.environ.get("LAOZHANG_API_KEY", "")
    if args.check_key:
        if not key:
            print("错误: 未提供 API Key", file=sys.stderr); sys.exit(1)
        check_key(key)

    if not key:
        print("错误: 未提供 API Key（--api-key 或 LAOZHANG_API_KEY）", file=sys.stderr); sys.exit(1)

    desc = args.prompt or (Path(args.file).read_text(encoding="utf-8").strip() if args.file else "")
    if not desc:
        print("错误: 请用 -p 或 -f 提供画面描述", file=sys.stderr); sys.exit(1)

    prompt = desc if args.raw else f"{desc}. {STYLE_ANCHOR}"
    out = Path(args.out) if args.out else Path.cwd() / "illustration.png"
    out.parent.mkdir(parents=True, exist_ok=True)

    print(f"比例 {args.ratio}，正在生成插图...", file=sys.stderr)
    out.write_bytes(call_api(prompt, args.ratio, key))
    print(f"插图已保存: {out}", file=sys.stderr)
    print(out)


if __name__ == "__main__":
    main()
