---
name: scenario-english
description: 为成人生成「场景英语脚本」——把学习者说出的一个真实场景或沟通痛点（开会、谈判、租车、拒绝加班、和外国同事 small talk…），变成一页可直接截图发小红书的英语学习卡。围绕「可迁移句型框 + 逐拍情境对话 + 你以为的vs地道 + 临场救命句」组织，刻意不做单词背诵。Use this skill whenever the user wants to create English learning material for adults, scenario/situational English, role-play dialogues, '场景英语', '地道表达 / 地道对照', or wants to turn a real-life situation or speaking pain-point into deployable English. 尤其适合「看得懂听得懂、一开口就卡」的中国成年人。当用户提到成人英语内容、情境对话、场景脚本、踩刹车/拒绝/寒暄怎么说、把某个具体场合做成学习材料时，都用这个 skill。
---

# Scenario English — 成人场景脚本生成器

把"一个真实场景/痛点"变成"一页能直接调用的英语脚本"。

> **这个 skill 的立场（不要忘）：** 成人不缺词，缺的是"调得出"。任何优化"认得/记得"的产物都掉进
> 流利性陷阱；这个 skill 只做"那一刻嘴里有话"。**主角是句型框和救命句，不是单词表。**
> （改造自 nano-banana-poster：抽出它的方法论内核，把产物从"单张卡通海报"换成"成人结构化脚本页"。）

## 产物长什么样

一页自包含 HTML（成人编辑感、双语、竖版、可截图发小红书），按需包含这些模块：

1. **★ 可迁移句型框**（主角）— 带空槽、能迁移、自带语气的结构，不是死句、不是词。
2. **情境对话** — 一通真实交互从头到尾，**高亮最容易卡住的那一拍**（反对/打断/没听懂/告别）。
3. **你以为的 vs 地道** — 真实中式石化错误的对照，解释机制（去石化）。
4. **临场救命句** — 卡壳那一秒让对话不死的元话术（成人相对儿童最大的增量）。
5. **场景词** — 刻意精简、刻意放最后，不抢戏。
6. **语气贴士** — 让 ta 不只说对词，还读对场。

对话分格插图为**可选**项，且只在"文字少"的前提下由 AI 生成；没有它，对话以纯文字呈现，页面依然完整。

---

## 工作流

### Phase 1 · 情境输入（必做）

输入从"词表/课文"翻转成"我要用英语去面对的那件事"。收集：

- **① 真实场景或痛点（必填）**：用自然语言。如「下周第一次和海外客户开启动会，怕冷场又怕想反对说不出口」。
- **② 可选锐化项**（缺了就用默认）：
  - 水平 level（默认：中级·能读写、开口卡壳）
  - 地区 region（默认 US；影响用词 gas/petrol 等）
  - 语域 register（默认 neutral-professional）
  - 学习者在场景里的**角色**（客户？店员？面试者？拒绝方？）

整理成 `Scenario_Spec`（字段见 [references/meta_prompt.md](references/meta_prompt.md)），用**中文回显给用户一轮确认**：
「我理解你要的场景是 X，你是 Y 角色，目标 Z，最卡的是 W——对吗？」确认后再生成，避免跑偏。

### Phase 2 · 配置脚本（想快就全默认）

**① 输出模式选择（必选）：**

```
请选择输出模式：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  A · HTML 长页     — 双语完整版，理解机制，可截图
  B · AI 知识海报   — 场景化图片系列，适合日常复习/社媒
  C · 两者都出      — HTML 打底 + 海报激活（推荐）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

- 用户只想快 → 选 A，全默认（TTS 关闭），直接进 Phase 3

**② 模块配置**（Mode A/C 生效，Mode B 自动映射全开）：

- **模块**：默认全开。可砍掉不需要的（如纯生活闲聊可能不要 vocab）。**frames 和 rescue 建议永远保留**——它们是成人核心增量。
- **视觉风格**（HTML 用）：`editorial`(默认/赤陶杂志) | `minimal`(黑白·黄高亮) | `journal`(暖绿手帐)。
  读 [references/style_presets.md](references/style_presets.md) 帮用户选；一个场景固定一种风格。
- **是否要插图**（默认否）。要 → Key 在 ④ 统一收集。

**③ 是否开启 TTS 语音**（Mode A/C 生效）：

```
是否为 HTML 内嵌真人语音（TTS）？
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Y · 开启 TTS   — 内嵌真人音色，边读边听，需要 laozhang.ai API Key
  N · 不开启     — 纯文字版，无需 API（默认）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

- 选 Y → 继续 ④ 收集 Key
- 选 N 或用户未明确表示 → 跳过 ④，TTS 默认关闭

**④ API Key 检查**（Mode B/C 或 TTS=Y 时执行，否则跳过）：

Mode B/C（海报/插图）和 TTS 共用同一个 laozhang.ai API Key，只需提供一次：

```bash
python3 scripts/generate_illustration.py --check-key --api-key <KEY>
```

- 验证成功 → Key 收妥，后续渲染/海报/TTS 均复用此 Key
- 验证失败 → 告知用户；海报/插图降级为 Mode A（纯文字），TTS 降级为无语音版，流程不中断

### Phase 3 · 生成内容 + 确认

1. 读 [references/meta_prompt.md](references/meta_prompt.md)（生成指令 + JSON schema）和
   [references/content_principles.md](references/content_principles.md)（质量红线）。
2. 按 schema 从 `Scenario_Spec` 生成**内容 JSON**。生成时严守 content_principles 的红线，生成后**逐条过自检**：
   句型框是不是主角？对话有没有标出最难那拍？救命句给了没？地道对照真不真实、why 解释机制了没？词汇有没有抢戏？
   > 最后一问最重要：**一个荒废多年的成年人下次真到这场景——ta 嘴里有话了吗？** 没过就重写。
3. 把内容用**中文摘要**回显确认：列出 3–5 个句型框、对话哪几拍（点明最难那拍）、几条地道对照、几句救命句。
   让用户确认或要求改（换框、改难点、调语气）。
4. 确认后保存 JSON：`~/scenario-english/YYYYMMDD_场景名/content.json`

### Phase 4 · 渲染页面（Mode A / C）

> **Mode C 执行顺序：先完成 Phase 4（HTML），用户确认内容无误后，再进入 Phase 4B（海报）。**
> 海报提示词从 content.json 生成，若用户看完 HTML 后要求改内容，需先更新 content.json 再草拟提示词，避免返工。

1. **（可选）插图**：对需要插图的 beat，用画面描述（来自该 beat、**绝不含文字内容**）生成 PNG：
   ```bash
   python3 scripts/generate_illustration.py -p "<画面描述>" --ratio 4:3 \
     -o ~/scenario-english/YYYYMMDD_场景名/assets/beat3.png --api-key <KEY>
   ```
   把返回路径填回该 beat 的 `illustration` 字段（build_page 会自动 base64 内嵌）。
2. **渲染**：
   ```bash
   # 不含 TTS（纯文字版）
   python3 scripts/build_page.py \
     --content ~/scenario-english/YYYYMMDD_场景名/content.json \
     --out ~/scenario-english/YYYYMMDD_场景名/index.html \
     --style editorial

   # 含 TTS（真人音色，内嵌音频，推荐）
   python3 scripts/build_page.py \
     --content ~/scenario-english/YYYYMMDD_场景名/content.json \
     --out ~/scenario-english/YYYYMMDD_场景名/index.html \
     --style editorial \
     --tts-key <laozhang.ai KEY>
   ```
   产出自包含 HTML。TTS 音频内嵌规则：
   - **句型框例句**：每句独立，nova 音色，点击句子旁 ▶ 播放
   - **情境对话**：每个 beat 合并为一条，You=nova / Other=onyx，点击 beat 标签旁 ▶ 播放
   - **地道对照**：仅 ✅ 地道表达生成音频（❌ 中式不生成），nova 音色
   - **救命句**：每句独立，nova 音色
   - **场景词**：所有词合并为一条，nova 音色，点击词汇区 ▶ 播放
   - 含 `___` 的句子：中间空槽用停顿替代，句尾空槽直接去掉

---

### Phase 4B · 海报生成（Mode B / C）

**必读**：[references/poster_templates.md](references/poster_templates.md)（每类卡片的构图规范和提示词模板）

#### Step 1 · 草拟提示词

从 `content.json` 为每张海报生成英文提示词，写入 `prompts.json`。

**⚠️ prompts.json 必须是以下结构（裸数组会导致脚本报错）：**
```json
{
  "scene": "场景名",
  "posters": [
    { "id": "01_frame_1", "template": "A", "ratio": "4:3", "label": "...", "prompt": "..." },
    ...
  ]
}
```

**卡片 → 模板映射：**

| 内容类型 | 模板 | 比例 | 拆分规则 |
|---------|------|------|---------|
| 句型框 | Template A | 4:3 | 每框一张 |
| 对话·普通拍 | Template B | 16:9 | 每拍一张 |
| 对话·最难那拍 ★ | Template B★ | 1:1 | 独立一张，标 ★ |
| 地道对照 | Template C | 3:4 | ⚠️ 每组对比独立一张 |
| 救命句 | Template D | 3:4 | ⚠️ 每句独立一张 |
| 场景词 | Template E | 16:9 | ≤6词一张，超出拆分 |

提示词生成后过 poster_templates.md 末尾的**检查清单**，再展示给用户确认。

#### Step 2 · 用户审核提示词

中文摘要展示每张海报的构图意图，用户确认或指定修改，再进入生成。

#### Step 3 · 批量生成

```bash
# 全量
python3 scripts/run_poster_gen.py \
  --prompts ~/scenario-english/YYYYMMDD_场景名/prompts.json \
  --out-dir ~/scenario-english/YYYYMMDD_场景名/posters \
  --api-key <KEY>

# 只重跑失败项
python3 scripts/run_poster_gen.py \
  --prompts ~/scenario-english/YYYYMMDD_场景名/prompts.json \
  --out-dir ~/scenario-english/YYYYMMDD_场景名/posters \
  --api-key <KEY> \
  --only 02_beat_hard,05_rescue_1
```

---

### Phase 5 · 展示 + 迭代

输出目录结构：
```
~/scenario-english/YYYYMMDD_场景名/
  content.json        ← 内容 JSON
  index.html          ← HTML 长页（Mode A/C）
  prompts.json        ← 海报提示词存档（Mode B/C）
  posters/
    01_frame_1.png
    02_frame_2.png
    ...
```

- HTML → 用浏览器打开，可截图发小红书
- 海报 → 直接查看 PNG，存入相册
- 用户要局部改 → 回到对应 Phase 只重跑那一步，不必全部重来：
  - 改某个句型框 → 只改 content.json + 重跑 build_page / 重生成对应海报
  - 改某张海报提示词 → 只改 prompts.json + `--only` 重跑

---

## 文件地图

```
scenario-english/
├── SKILL.md                          ← 本文件：流程总纲
├── references/
│   ├── meta_prompt.md                ← 内容生成指令 + 严格 JSON schema（Phase 3 必读）
│   ├── content_principles.md         ← 质量红线：什么是"用"不是"练"（Phase 3 必读）
│   ├── style_presets.md              ← 三套成人风格 + 插图风格关键词（Phase 2/4）
│   └── poster_templates.md           ← 海报设计模板库（Phase 4B 必读）
├── scripts/
│   ├── build_page.py                 ← 内容 JSON → 自包含 HTML（核心；加 --tts-key 可内嵌真人语音）
│   ├── generate_illustration.py      ← 对话分格插图（可选，需 laozhang.ai key）
│   └── run_poster_gen.py             ← prompts.json → 海报 PNG（Mode B/C）
└── assets/
    └── page_template.html            ← HTML/CSS 模板（build_page 套用，含三套风格变量）
```

## 几条不要踩的线

- **别把这页做成伪装的单词表。** 一旦你在堆名词、给词配中文，就停——那是儿童词汇海报，是练不是用。
- **对话一定要有难点那一拍。** 顺滑寒暄没用，成人卡的是反对/打断/拒绝/告别。
- **救命句必给。** 这是成人最缺、最被低估的一组。
- **绝不卡通。** 风格一律成人编辑感；插图也不要 Q 版/拟人动物/绘本质感。
- **HTML 插图里无字，海报里必须有字。** HTML 的对话分格插图只画场景，文字由 HTML 负责；海报是知识海报，英文内容（例句/对话/词汇）必须出现在图中，纯场景图不合格。
- **没 key 不阻塞。** 插图和 TTS 都是锦上添花：key 缺失或验证失败时，海报/插图降级为 Mode A，TTS 降级为纯文字版，核心页始终能出。
