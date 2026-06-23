#!/usr/bin/env python3
"""
scenario-english 页面渲染器

将"场景脚本内容 JSON"渲染成一页自包含的成人英语学习 HTML（可截图发小红书）。

用法:
    python build_page.py --content content.json --out page.html --style editorial
    python build_page.py --content content.json --out page.html --style editorial --tts-key sk-xxx

  --style  : editorial(默认/赤陶米白) | minimal(黑白·黄高亮) | journal(暖绿手帐)
  --tts-key: laozhang.ai API Key，提供后自动为英文内容生成真人 TTS 音频并内嵌

TTS 规则:
  - 句型框例句: 每句独立，nova 音色
  - 情境对话: 每个 beat 合并，You=nova / Other=onyx，字节顺序拼接
  - 地道对照: 仅地道表达，nova 音色
  - 救命句: 每句独立，nova 音色
  - 场景词: 所有词汇合并为 1 条，nova 音色
  - 不完整句子 (___): 中间空格用停顿(...)替代，句尾空格直接去掉
"""

import argparse
import base64
import html as _html
import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.request import Request, urlopen

TEMPLATE = Path(__file__).resolve().parent.parent / "assets" / "page_template.html"
TTS_URL = "https://api.laozhang.ai/v1/audio/speech"
TTS_MODEL = "tts-1"
TTS_WORKERS = 4

# ---------------------------------------------------------------- 风格预设
PRESETS = {
    "editorial": """:root{
  --bg:#FBF7F0; --ink:#2A2420; --ink-soft:#4A4038; --muted:#8C8073;
  --accent:#C2552F; --accent-ink:#7A2E14; --accent-soft:#F6E7DD; --accent-line:#EAD2C4;
  --card:#FFFDF9; --line:#EAE0D2;
  --shadow:0 1px 2px rgba(60,40,20,.04),0 6px 18px rgba(60,40,20,.05);
  --glow:rgba(194,85,47,.06); --glow2:rgba(180,140,90,.05);
  --hl:#FBE3C9; --bad:#C2552F;
  --rescue-bg:#F0F4EE; --rescue-line:#CBD8C2; --rescue-ink:#4E6A3E;
  --body:'Hanken Grotesk','Noto Sans SC',system-ui,sans-serif;
  --display:'Fraunces','Noto Serif SC',Georgia,serif;
}""",
    "minimal": """:root{
  --bg:#FFFFFF; --ink:#0C0C0C; --ink-soft:#2A2A2A; --muted:#7A7A7A;
  --accent:#111111; --accent-ink:#111111; --accent-soft:#F4F4F2; --accent-line:#E6E6E2;
  --card:#FFFFFF; --line:#E8E8E6;
  --shadow:0 1px 2px rgba(0,0,0,.03),0 4px 14px rgba(0,0,0,.04);
  --glow:rgba(0,0,0,0); --glow2:rgba(0,0,0,0);
  --hl:#FFE99A; --bad:#D14848;
  --rescue-bg:#FAFAF8; --rescue-line:#111111; --rescue-ink:#111111;
  --body:'Hanken Grotesk','Noto Sans SC',system-ui,sans-serif;
  --display:'Hanken Grotesk','Noto Sans SC',system-ui,sans-serif;
}""",
    "journal": """:root{
  --bg:#F7F4EC; --ink:#27302A; --ink-soft:#3E4A41; --muted:#7E8B7C;
  --accent:#3F7A5E; --accent-ink:#2C5A43; --accent-soft:#E6EFE6; --accent-line:#CBDFCC;
  --card:#FEFCF6; --line:#E2E2D2;
  --shadow:0 1px 2px rgba(40,60,40,.04),0 6px 18px rgba(40,60,40,.05);
  --glow:rgba(63,122,94,.06); --glow2:rgba(150,160,110,.05);
  --hl:#D8EBC9; --bad:#C2552F;
  --rescue-bg:#FBF1E6; --rescue-line:#E0C49E; --rescue-ink:#9A6B3A;
  --body:'Hanken Grotesk','Noto Sans SC',system-ui,sans-serif;
  --display:'Fraunces','Noto Serif SC',Georgia,serif;
}""",
}


# ---------------------------------------------------------------- 工具函数
def esc(s) -> str:
    return _html.escape(str(s if s is not None else "")).replace("\n", "<br>")


def slotify(frame_en: str) -> str:
    """把句型框里的 ___ 占位渲染成高亮空槽（视觉透明虚线）。"""
    safe = esc(frame_en)
    out, i = [], 0
    while i < len(safe):
        if safe[i] == "_":
            j = i
            while j < len(safe) and safe[j] == "_":
                j += 1
            if j - i >= 3:
                out.append('<span class="slot">___</span>')
                i = j
                continue
        out.append(safe[i])
        i += 1
    return "".join(out)


def embed_img(path: str) -> str:
    p = Path(path)
    if not p.exists():
        return ""
    mime = "image/png" if p.suffix.lower() == ".png" else "image/jpeg"
    b64 = base64.b64encode(p.read_bytes()).decode()
    return f'<img class="beat-illus" src="data:{mime};base64,{b64}" alt="">'


# ---------------------------------------------------------------- TTS
def clean_for_tts(text: str) -> str:
    """处理 ___ 空槽：中间替换为停顿，句尾直接去掉。"""
    t = re.sub(r'_+', '...', text.strip())
    # 去掉句尾的 ... 及其前后标点空格
    t = re.sub(r'[\s.,!?:;]*\.\.\.[\s.,!?:;]*$', '', t).strip()
    return t


class TTSPlan:
    """收集所有需要生成音频的条目。"""

    def __init__(self, enabled: bool = False):
        self.enabled = enabled
        self.items: list[dict] = []   # [{id, segs:[{text,voice}]}]

    def add(self, tid: str, segs: list[dict]) -> str:
        """注册一条 TTS 项，返回 data-tts="tid" 属性字符串（或空串）。"""
        if not self.enabled:
            return ""
        clean = [{"text": clean_for_tts(s["text"]), "voice": s.get("voice", "nova")}
                 for s in segs if s.get("text", "").strip()]
        if not clean:
            return ""
        self.items.append({"id": tid, "segs": clean})
        return f' data-tts="{tid}"'

    def add_word(self, tid: str, word: str) -> str:
        """注册单个词汇条目（用于场景词顺序播放），返回 tid 或空串。"""
        if not self.enabled or not word.strip():
            return ""
        self.items.append({"id": tid, "segs": [{"text": word.strip(), "voice": "nova"}]})
        return tid


def _tts_call(text: str, voice: str, api_key: str) -> bytes:
    body = json.dumps({
        "model": TTS_MODEL, "input": text, "voice": voice, "response_format": "mp3"
    }).encode()
    req = Request(TTS_URL, data=body, method="POST", headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    })
    for attempt in range(3):
        if attempt:
            time.sleep(5 * attempt)
        try:
            with urlopen(req, timeout=45) as r:
                return r.read()
        except Exception as e:
            if attempt == 2:
                raise RuntimeError(str(e))
    return b""


def _generate_item(item: dict, api_key: str) -> tuple[str, bytes]:
    """为一条 TTS 项生成音频（多段字节顺序拼接）。"""
    parts = []
    for seg in item["segs"]:
        if seg["text"].strip():
            parts.append(_tts_call(seg["text"], seg["voice"], api_key))
    return item["id"], b"".join(parts)


def generate_all_tts(plan: TTSPlan, api_key: str) -> dict[str, str]:
    """并发生成所有 TTS 音频，返回 {tid: base64_mp3}。"""
    if not plan.items:
        return {}
    total = len(plan.items)
    print(f"\n🔊 TTS 生成 {total} 条音频...", file=sys.stderr)
    result: dict[str, str] = {}
    done = 0
    with ThreadPoolExecutor(max_workers=TTS_WORKERS) as pool:
        futures = {pool.submit(_generate_item, item, api_key): item["id"]
                   for item in plan.items}
        for fut in as_completed(futures):
            tid = futures[fut]
            try:
                _, mp3 = fut.result()
                result[tid] = base64.b64encode(mp3).decode()
                done += 1
                print(f"  ✓ [{done}/{total}] {tid}", file=sys.stderr)
            except Exception as e:
                print(f"  ✗ {tid}: {e}", file=sys.stderr)
    return result


def build_tts_injection(audio_map: dict[str, str]) -> str:
    """生成隐藏音频标签 + 播放 JS，注入到 </body> 前。"""
    if not audio_map:
        return ""
    tags = "".join(
        f'<audio id="{tid}" src="data:audio/mpeg;base64,{b64}" preload="auto"></audio>'
        for tid, b64 in sorted(audio_map.items())
    )
    js = """<script>
(function(){
  var cur=null;
  function stop(){
    if(cur){cur.a.pause();cur.a.currentTime=0;
      cur.b.classList.remove('playing');cur.b.textContent='▶';cur=null;}
  }
  document.addEventListener('DOMContentLoaded',function(){
    document.querySelectorAll('[data-tts]').forEach(function(el){
      var a=document.getElementById(el.getAttribute('data-tts'));
      if(!a)return;
      var b=document.createElement('button');
      b.className='tts-btn';b.textContent='▶';b.title='朗读';
      b.onclick=function(e){
        e.stopPropagation();
        if(cur&&cur.b===b){stop();return;}
        stop();
        a.currentTime=0;a.play();
        b.classList.add('playing');b.textContent='■';
        cur={a:a,b:b};
        a.addEventListener('ended',function(){if(cur&&cur.b===b)stop();},{once:true});
      };
      el.appendChild(b);
    });
  });
})();
</script>"""
    return f'<div id="tts-reg" style="display:none">{tags}</div>\n{js}\n'


# ---------------------------------------------------------------- 各模块渲染
def build_brief(meta: dict) -> str:
    chips = []
    for label, key in [("角色", "role"), ("目标", "goal"), ("语域", "register"),
                        ("地区", "region"), ("水平", "level")]:
        if meta.get(key):
            chips.append(f'<span class="chip"><b>{esc(label)}</b> {esc(meta[key])}</span>')
    return "".join(chips)


def build_pain(meta: dict) -> str:
    if not meta.get("pain"):
        return ""
    return f'<div class="pain"><b>你卡在哪：</b>{esc(meta["pain"])}</div>'


def sec_head(num: str, zh: str, en: str = "", star: bool = False) -> str:
    s = ' <span class="star">★</span>' if star else ""
    en_html = f'<span class="en">{esc(en)}</span>' if en else ""
    return (f'<div class="sec-head"><span class="sec-num">{esc(num)}</span>'
            f'<span class="sec-title">{esc(zh)}{s}{en_html}</span></div>')


def build_frames(frames: list, num: str, tts: TTSPlan) -> str:
    if not frames:
        return ""
    cards = []
    for fi, f in enumerate(frames):
        fills = ""
        for si, fl in enumerate(f.get("fills", [])):
            en_text = fl.get("en", "")
            ta = tts.add(f"tts-fill-{fi:02d}-{si:02d}",
                         [{"text": en_text, "voice": "nova"}])
            zh = f'<span class="zh">{esc(fl.get("zh", ""))}</span>' if fl.get("zh") else ""
            fills += f'<div class="fill"><span class="en"{ta}>{esc(en_text)}</span>{zh}</div>'
        fills = f'<div class="fills">{fills}</div>' if fills else ""
        meta_rows = ""
        if f.get("register_note"):
            meta_rows += (f'<div class="row"><span class="tag">语气</span>'
                          f'<span>{esc(f["register_note"])}</span></div>')
        if f.get("transfers_to"):
            meta_rows += (f'<div class="row"><span class="tag">可迁移到</span>'
                          f'<span>{esc(f["transfers_to"])}</span></div>')
        meta_rows = f'<div class="frame-meta">{meta_rows}</div>' if meta_rows else ""
        zh = f'<span class="frame-zh">{esc(f.get("frame_zh", ""))}</span>' if f.get("frame_zh") else ""
        cards.append(
            f'<div class="frame"><div class="frame-top">'
            f'<span class="frame-en">{slotify(f.get("frame_en", ""))}</span>{zh}</div>'
            f'{fills}{meta_rows}</div>'
        )
    head = sec_head(num, "可迁移句型框", "Transferable Frames", star=True)
    hint = '<div class="sec-hint">这页的主角。框比句子值钱——记住框，换个场景照样调得出。</div>'
    return f"<section>{head}{hint}{''.join(cards)}</section>"


def build_dialogue(dialogue, num: str, tts: TTSPlan) -> str:
    if not dialogue:
        return ""
    beats = dialogue.get("beats", []) if isinstance(dialogue, dict) else dialogue
    if not beats:
        return ""
    blocks = []
    for bi, b in enumerate(beats):
        # 收集这个 beat 所有台词（双音色）
        beat_segs = [
            {"text": ln.get("en", ""),
             "voice": "nova" if str(ln.get("side", "")).lower() == "you" else "onyx"}
            for ln in b.get("lines", []) if ln.get("en", "").strip()
        ]
        ta_beat = tts.add(f"tts-beat-{bi:02d}", beat_segs)

        cls = "beat tricky" if b.get("tricky") else "beat"
        label = (f'<span class="beat-label"{ta_beat}>{esc(b.get("label", ""))}</span>'
                 if b.get("label") else "")
        narr = (f'<div class="beat-narration">{esc(b.get("narration", ""))}</div>'
                if b.get("narration") else "")
        illus = embed_img(b["illustration"]) if b.get("illustration") else ""
        lines = ""
        for ln in b.get("lines", []):
            side = "you" if str(ln.get("side", "")).lower() == "you" else "other"
            who = esc(ln.get("who", "You" if side == "you" else ""))
            zh = f'<div class="zh">{esc(ln.get("zh", ""))}</div>' if ln.get("zh") else ""
            lines += (f'<div class="line {side}"><div class="who">{who}</div>'
                      f'<div class="bubble"><div class="en">{esc(ln.get("en", ""))}</div>'
                      f'{zh}</div></div>')
        blocks.append(f'<div class="{cls}">{label}{narr}{illus}{lines}</div>')
    head = sec_head(num, "情境对话", "Run the Scene")
    intro = ""
    if isinstance(dialogue, dict) and dialogue.get("intro"):
        intro = f'<div class="sec-hint">{esc(dialogue["intro"])}</div>'
    return f"<section>{head}{intro}{''.join(blocks)}</section>"


def build_authentic(auth: list, num: str, tts: TTSPlan) -> str:
    if not auth:
        return ""
    rows = []
    for ai, a in enumerate(auth):
        goods = a.get("good", [])
        if isinstance(goods, str):
            goods = [goods]
        good_lines = ""
        for gi, g in enumerate(goods):
            ta = tts.add(f"tts-auth-{ai:02d}-{gi:02d}", [{"text": g, "voice": "nova"}])
            good_lines += (f'<div class="auth-line good"><span class="mark">✅</span>'
                           f'<span class="text"{ta}>{esc(g)}</span></div>')
        why = f'<div class="auth-why">{esc(a["why"])}</div>' if a.get("why") else ""
        rows.append(
            f'<div class="auth-row"><div class="auth-intent">{esc(a.get("intent", ""))}</div>'
            f'<div class="auth-pair">'
            f'<div class="auth-line bad"><span class="mark">❌</span>'
            f'<span class="text">{esc(a.get("bad", ""))}</span></div>'
            f'{good_lines}</div>{why}</div>'
        )
    head = sec_head(num, "你以为的 vs 地道", "Don't Say / Say")
    return f'<section>{head}<div class="auth">{"".join(rows)}</div></section>'


def build_rescue(rescue: list, num: str, tts: TTSPlan) -> str:
    if not rescue:
        return ""
    items = []
    for ri, r in enumerate(rescue):
        ta = tts.add(f"tts-rescue-{ri:02d}", [{"text": r.get("en", ""), "voice": "nova"}])
        zh = f'<div class="rescue-zh">{esc(r.get("zh", ""))}</div>' if r.get("zh") else ""
        use = f'<div class="rescue-use">{esc(r.get("use", ""))}</div>' if r.get("use") else ""
        items.append(
            f'<div class="rescue-item"><span class="rescue-ic">🛟</span>'
            f'<div><div class="rescue-en"{ta}>{esc(r.get("en", ""))}</div>{zh}{use}</div></div>'
        )
    head = sec_head(num, "临场救命句", "When You Freeze")
    hint = '<div class="sec-hint">没听懂、卡住、要思考时间——这些话让对话不死。成人最该背的就是这一组。</div>'
    return f'<section>{head}{hint}<div class="rescue">{"".join(items)}</div></section>'


def build_vocab(vocab: list, num: str, tts: TTSPlan) -> str:
    if not vocab:
        return ""
    chips = []
    for v in vocab:
        ipa = f'<span class="ipa">{esc(v.get("ipa", ""))}</span>' if v.get("ipa") else ""
        chips.append(f'<span class="vchip"><span class="w">{esc(v.get("w", ""))}</span>'
                     f'{ipa}<span class="z">{esc(v.get("zh", ""))}</span></span>')
    words_text = ". ".join(v.get("w", "") for v in vocab if v.get("w"))
    ta = tts.add("tts-vocab", [{"text": words_text, "voice": "nova"}])
    head = sec_head(num, "场景词", "Just the Words You Need")
    return f'<section>{head}<div class="vocab-wrap"{ta}>{"".join(chips)}</div></section>'


def build_tip(tip: dict, num: str) -> str:
    if not tip:
        return ""
    title = tip.get("title", "语气贴士")
    return (f'<section><div class="tip"><div class="tip-title">{esc(title)}</div>'
            f'<div class="tip-body">{esc(tip.get("body", ""))}</div></div></section>')


# ---------------------------------------------------------------- 主流程
def render(content: dict, style: str, tts: TTSPlan) -> str:
    meta = content.get("meta", {})
    tpl = TEMPLATE.read_text(encoding="utf-8")

    n = 0
    def nxt():
        nonlocal n; n += 1; return f"{n:02d}"

    frames_html   = build_frames(content.get("frames", []), nxt(), tts) if content.get("frames") else ""
    dialogue_html = build_dialogue(content.get("dialogue"), nxt(), tts) if content.get("dialogue") else ""
    auth_html     = build_authentic(content.get("authentic", []), nxt(), tts) if content.get("authentic") else ""
    rescue_html   = build_rescue(content.get("rescue", []), nxt(), tts) if content.get("rescue") else ""
    vocab_html    = build_vocab(content.get("vocab", []), nxt(), tts) if content.get("vocab") else ""
    tip_html      = build_tip(content.get("tip"), nxt()) if content.get("tip") else ""

    repl = {
        "{{STYLE_VARS}}":  PRESETS.get(style, PRESETS["editorial"]),
        "{{KICKER}}":      esc(meta.get("kicker", "场景英语脚本 · SCENARIO ENGLISH")),
        "{{SCENE_EN}}":    esc(meta.get("scene_en", "")),
        "{{SCENE_ZH}}":    esc(meta.get("scene_zh", "")),
        "{{BRIEF}}":       build_brief(meta),
        "{{PAIN}}":        build_pain(meta),
        "{{FRAMES}}":      frames_html,
        "{{DIALOGUE}}":    dialogue_html,
        "{{AUTHENTIC}}":   auth_html,
        "{{RESCUE}}":      rescue_html,
        "{{VOCAB}}":       vocab_html,
        "{{TIP}}":         tip_html,
        "{{FOOT_LEFT}}":   esc(meta.get("foot", "场景英语脚本生成器")),
    }
    for k, v in repl.items():
        tpl = tpl.replace(k, v)
    return tpl


def main():
    ap = argparse.ArgumentParser(description="场景脚本内容 JSON → HTML 页面")
    ap.add_argument("--content", "-c", required=True, help="内容 JSON 文件路径")
    ap.add_argument("--out", "-o", required=True, help="输出 HTML 路径")
    ap.add_argument("--style", "-s", default="editorial",
                    choices=list(PRESETS.keys()), help="视觉风格预设")
    ap.add_argument("--tts-key", default="", help="laozhang.ai API Key，提供后内嵌真人 TTS 音频")
    args = ap.parse_args()

    content = json.loads(Path(args.content).read_text(encoding="utf-8"))
    tts = TTSPlan(enabled=bool(args.tts_key))

    page = render(content, args.style, tts)

    if args.tts_key and tts.items:
        audio_map = generate_all_tts(tts, args.tts_key)
        injection = build_tts_injection(audio_map)
        page = page.replace("</body>", injection + "</body>")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
