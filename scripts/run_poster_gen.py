#!/usr/bin/env python3
"""
海报逐张生成器

从 prompts.json 读取提示词，逐张调用 Gemini API 生成 2K 高质量 PNG。
提示词与脚本分离——脚本只负责调度和 IO，不持有任何提示词内容。

用法:
    python run_poster_gen.py --prompts prompts.json --out-dir ./out --api-key KEY
"""

import argparse
import base64
import json
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

API_URL = "https://api.laozhang.ai/v1beta/models/gemini-3-pro-image-preview:generateContent"
REQUEST_TIMEOUT = 150
MAX_RETRIES = 2
RETRY_WAIT = 8      # 首次重试等待秒数
REQUEST_GAP = 6     # 两次请求之间的间隔（避免 429）


def call_api(prompt: str, ratio: str, api_key: str) -> bytes:
    body = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["image", "text"],
            "aspectRatio": ratio,
            "imageSize": "2K",
        },
    }).encode()

    req = Request(API_URL, data=body, method="POST", headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    })

    last_err = None
    for attempt in range(1 + MAX_RETRIES):
        if attempt:
            wait = RETRY_WAIT * attempt
            print(f"    retry {attempt}/{MAX_RETRIES} in {wait}s…", file=sys.stderr)
            time.sleep(wait)
        try:
            with urlopen(req, timeout=REQUEST_TIMEOUT) as r:
                resp = json.loads(r.read().decode())
            return _extract(resp)
        except HTTPError as e:
            body_txt = e.read().decode("utf-8", "replace")
            last_err = f"HTTP {e.code}"
            if e.code == 401:
                sys.exit("✗ API key invalid or expired")
            if e.code in (402,) or "insufficient" in body_txt.lower():
                sys.exit("✗ Insufficient API balance")
            print(f"    HTTP {e.code}: {body_txt[:120]}", file=sys.stderr)
        except (URLError, TimeoutError) as e:
            last_err = str(e)
            print(f"    network error: {e}", file=sys.stderr)

    raise RuntimeError(f"Failed after {MAX_RETRIES} retries: {last_err}")


def _extract(resp: dict) -> bytes:
    for cand in resp.get("candidates", []):
        for part in cand.get("content", {}).get("parts", []):
            data = (part.get("inlineData") or {}).get("data")
            if data:
                return base64.b64decode(data)
    raise RuntimeError(f"No image in response: {json.dumps(resp)[:300]}")


def main():
    ap = argparse.ArgumentParser(description="Prompts JSON → PNG 海报序列")
    ap.add_argument("--prompts", "-p", required=True, help="prompts.json 路径")
    ap.add_argument("--out-dir", "-o", required=True, help="PNG 输出目录")
    ap.add_argument("--api-key", required=True, help="laozhang.ai API Key")
    ap.add_argument("--only", help="只生成指定 id（逗号分隔），调试用")
    args = ap.parse_args()

    spec = json.loads(Path(args.prompts).read_text(encoding="utf-8"))
    posters = spec.get("posters", [])
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    only_ids = set(args.only.split(",")) if args.only else None

    total = len([p for p in posters if not only_ids or p["id"] in only_ids])
    done, failed = 0, []

    print(f"\n场景: {spec.get('scene', '')}  —  {total} 张海报\n", file=sys.stderr)

    for i, poster in enumerate(posters):
        pid = poster["id"]
        if only_ids and pid not in only_ids:
            continue

        ratio = poster.get("ratio", "3:4")
        prompt = poster.get("prompt", "")
        out_path = out_dir / f"{pid}.png"

        seq = done + len(failed) + 1
        print(f"[{seq}/{total}] {pid}  ({ratio})", file=sys.stderr)

        # 请求间隔（第一张不等）
        if seq > 1:
            time.sleep(REQUEST_GAP)

        try:
            img = call_api(prompt, ratio, args.api_key)
            out_path.write_bytes(img)
            size_kb = out_path.stat().st_size // 1024
            print(f"    ✓  {out_path.name}  ({size_kb} KB)", file=sys.stderr)
            print(str(out_path))          # stdout：成功路径
            done += 1
        except Exception as e:
            print(f"    ✗  {e}", file=sys.stderr)
            failed.append(pid)

    print(f"\n完成 {done}/{total}，失败 {len(failed)} 张", file=sys.stderr)
    if failed:
        ids = ",".join(failed)
        print(f"失败列表: {ids}", file=sys.stderr)
        print(f"重跑失败项: python run_poster_gen.py --prompts {args.prompts} "
              f"--out-dir {out_dir} --api-key KEY --only {ids}", file=sys.stderr)


if __name__ == "__main__":
    main()
