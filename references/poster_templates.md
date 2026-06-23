# 海报设计模板库

每类卡片的构图规范、比例、提示词模板。从内容 JSON 生成 `prompts.json` 时必须对照此文件选模板。

---

## 通用前缀（所有海报通用）

```
An Instagram-style English learning knowledge poster, [RATIO] format.
Warm golden natural light, photorealistic editorial quality, shallow depth of field.
No Chinese characters anywhere in the image. No cartoon. No illustration style.
```

**禁止事项（所有海报）：**
- 不得出现汉字（包括标签、说明、任何文字）
- 不得卡通化（人物必须是真实成年人比例）
- 不得把中文类别标签翻译成英文（如不要写 "SENTENCE FRAME 1" 这种类别注释）
- 不得把所有知识点塞进一张图（知识密度大时拆分，见各类型拆分规则）

---

## TEMPLATE A · 句型框（Frame Cards）

**适用**：可迁移句型框，展示一个可填空的语言结构  
**比例**：`4:3`（横版）  
**拆分规则**：每张只展示一个句型框

**构图规范：**
- 顶部 20%：深色底（#1C1C1E）+ 大号粗体无衬线白色标题显示框文本，空槽用 `___` 虚线下划线表示；底部加小标签说明使用场景（如 `SOFT REQUEST · USE WITHOUT PRESSURE`）
- 底部 80%：Instagram 风格场景，展示该句型在真实职场中被使用的瞬间；说话者有云朵气泡，气泡内是完整例句

**提示词模板：**
```
A professional English learning knowledge poster, landscape 4:3 format,
Instagram editorial aesthetic. Clean two-section vertical layout.

TOP SECTION (top 20%): deep charcoal background (#1C1C1E).
Large bold sans-serif white headline centered: "[FRAME_TEXT]"
— the blank rendered as a dashed italic underline.
Small uppercase label below: [USAGE_LABEL].

BOTTOM SECTION (bottom 80%): Instagram-style lifestyle photography.
[SCENE_DESCRIPTION]. Warm golden natural light, rich color palette,
editorial magazine quality.
One professional speaks with a white cloud-shaped speech bubble,
thin border, clean black text: "[EXAMPLE_SENTENCE]"

No Chinese characters. No cartoon. Photorealistic.
```

**变量说明：**
- `FRAME_TEXT`：框文本，如 `Could we ___ on that?`
- `USAGE_LABEL`：2-4 词使用说明，如 `SOFT REQUEST FRAME`
- `SCENE_DESCRIPTION`：场景描述，涵盖人物、地点、动作，不提文字内容
- `EXAMPLE_SENTENCE`：完整例句，填入空槽的版本

---

## TEMPLATE B · 情境对话·普通拍（Beat Cards · Regular）

**适用**：情境对话中的普通节点（开场、对齐、收尾）  
**比例**：`16:9`（宽版）  
**拆分规则**：每拍一张，不合并

**构图规范：**
- 全幅场景（会议室、视频通话、办公室），两人在画面中自然出现
- 对话以云朵气泡嵌入场景，从说话人自然延伸，无独立文字面板
- 顶角有小 badge 标注是第几拍（如 `SCENE 1 · OPENING`）
- 气泡内只放当前最关键的一两句，不列完整对话

**提示词模板：**
```
An Instagram-style English learning knowledge poster, landscape 16:9 format.
Full-bleed photorealistic scene: [SCENE_DESCRIPTION].
Warm golden office light, shallow depth of field, editorial photography quality.
Two professionals visible — [SPEAKER_A_DESCRIPTION] and [SPEAKER_B_DESCRIPTION].

[SPEAKER_A] has a white cloud-shaped speech bubble: "[LINE_A]"
[SPEAKER_B] has a white cloud-shaped speech bubble: "[LINE_B]"

Small badge in top corner: [BEAT_LABEL] — white text on semi-transparent dark pill.
Cloud speech bubbles: rounded cloud shape, thin border, clean black sans-serif text.
No text panels. No Chinese characters. No cartoon. Photorealistic.
```

**变量说明：**
- `SCENE_DESCRIPTION`：场景环境，如 `a modern video call setup, laptop open, morning light`
- `SPEAKER_A/B_DESCRIPTION`：两人的位置和姿态，如 `seated at desk, relaxed posture`
- `LINE_A/B`：各自说的关键句，保持简短
- `BEAT_LABEL`：如 `SCENE 1 · OPENING MOVE`

---

## TEMPLATE B★ · 情境对话·最难那拍（Beat Card · The Hard One）

**适用**：对话中最容易卡住的一拍（推回、拒绝、打断、没听懂），用 ★ 标记  
**比例**：`1:1`（方图）  
**拆分规则**：独立一张，必须标注 ★

**构图规范：**
- 全幅虚化压暗会议室背景（60% 暗色遮罩）
- 前景：聊天气泡浮层，iMessage 风格
  - 每个气泡旁有圆形人物头像（小，肩颈以上）
  - 甲方（MARK）：浅灰气泡，左对齐
  - 己方（YOU）：暖色气泡（赤陶/琥珀），右对齐
- 顶部标签：`★ THE HARDEST BEAT`
- 底部：`[TECHNIQUE_FORMULA]`（如 `Empathy → Risk → Room to move`）

**提示词模板：**
```
An Instagram-style English learning knowledge poster, square 1:1 format.

BACKGROUND: full-bleed photorealistic meeting room scene —
[SCENE_DESCRIPTION]. Blurred with a dark overlay (60% opacity).

FOREGROUND — chat bubbles overlaid:
TOP STRIP: bold white sans-serif: ★ THE HARDEST BEAT.
Italic below: [TENSION_DESCRIPTION].

THREE CHAT BUBBLES (iMessage style, each with small circular portrait avatar):

BUBBLE 1 · [SPEAKER_B] (left-aligned): small circular portrait —
[SPEAKER_B_DESCRIPTION]. Light grey rounded bubble, dark text:
"[LINE_B]"

BUBBLE 2 · YOU (right-aligned): small circular portrait —
[YOU_DESCRIPTION]. Warm amber-terracotta rounded bubble, white text:
"[LINE_YOU_1]"

BUBBLE 3 · YOU (right-aligned, same avatar): warm amber bubble:
"[LINE_YOU_2]"

BOTTOM STRIP: clean white sans-serif: [TECHNIQUE_FORMULA]

No Chinese characters. No cartoon. Photorealistic avatars.
```

---

## TEMPLATE C · 地道对照（Authentic Comparison）

**适用**：中式表达 vs 地道表达的对照  
**比例**：`3:4`（竖版）  
**拆分规则**：⚠️ **每组对照独立一张**，绝不把多组对照塞进一张图。3组对比 = 3张海报

**构图规范：**
- 上方 45%：触发场景（第三方正在讲话/展示，交代"是什么情境触发了这个表达需求"）
- 下方 55%：同一会议室延续，两人并排，展示两种不同反应
  - 色调统一（不做明暗分割），同一暖光环境
  - 左侧人物：略显僵硬/不自然，云朵气泡含错误表达
  - 右侧人物：自信自然，云朵气泡含正确表达
  - 区分方式：每个气泡右上角小 badge（✗ 红色 / ✓ 绿色），不用颜色背景对比
- 无任何类别标签（不写 "PUSHING BACK" 之类的注释）

**提示词模板：**
```
An Instagram-style English learning knowledge poster, portrait 3:4 format.
A single unified warm editorial scene throughout — same lighting, same environment.

TOP SECTION (top 45%): [TRIGGER_SCENE_DESCRIPTION].
Warm golden office light, shallow depth of field, ins editorial photography.

BOTTOM SECTION (bottom 55%): the same office scene continues seamlessly.
Two colleagues seated side by side, both in the same warm ambient light.
No dark/light split. No color contrast between left and right.

LEFT PERSON: [WRONG_EXPRESSION_POSTURE]. Cloud speech bubble with
a small red ✗ badge in the corner: "[WRONG_PHRASE]"

RIGHT PERSON: [CORRECT_EXPRESSION_POSTURE]. Cloud speech bubble with
a small green ✓ badge in the corner: "[CORRECT_PHRASE]"

Cloud speech bubbles: white rounded cloud shape, thin dark border,
clean black sans-serif text. No labels. No annotations.
No Chinese characters. No cartoon. Photorealistic.
```

---

## TEMPLATE D · 救命句（Rescue Phrases）

**适用**：临场卡壳时的元话术  
**比例**：`3:4`（竖版）  
**拆分规则**：⚠️ **每句独立一张**，不在一张里列多句救命句

**构图规范：**
- 单一完整场景，主角前景（肩部以上），对话方虚化背景（暗示交流发生中）
- 主角：临场停顿瞬间，表情沉稳，微抬手或轻微停顿姿态
- 云朵气泡从主角自然延伸，内含该救命句
- 顶角：小 pill badge 标注使用时机（如 `RESCUE PHRASE · DIDN'T CATCH IT`）
- 无其他文字

**提示词模板：**
```
An Instagram-style English learning knowledge poster, portrait 3:4 format.

Setting: [SCENE_CONTEXT]. Warm golden light, shallow depth of field,
ins lifestyle photography quality.

MAIN SUBJECT (foreground): a professional in their 30s, [PAUSE_POSTURE].
Composed despite the moment — [EXPRESSION_DESCRIPTION].

BACKGROUND: [OTHER_PARTY_DESCRIPTION], slightly out of focus.

A white rounded cloud-shaped speech bubble floats naturally from the
main subject, thin border, clean black sans-serif text:
"[RESCUE_PHRASE]"

Small badge in the top corner: [BADGE_TEXT] — small white text on a
semi-transparent dark pill.

No other text. No Chinese characters. No cartoon. Photorealistic.
```

**badge 参考：**
- 没听清 → `RESCUE PHRASE · DIDN'T CATCH IT`
- 需要时间想 → `RESCUE PHRASE · BUYING TIME`
- 现在回答不了 → `RESCUE PHRASE · CIRCLE BACK`
- 优雅推迟 → `RESCUE PHRASE · GRACEFUL DEFERRAL`

---

## TEMPLATE E · 场景词（Vocabulary in Scene）

**适用**：该场景的核心词汇，嵌入真实环境  
**比例**：`16:9`（全景宽幅）  
**拆分规则**：词汇不超过 6 个时一张；超过 6 个拆两张

**构图规范：**
- 全幅沉浸式企业级场景（会议室/办公区/项目墙）
- 词汇**嵌入环境内部**而非叠加在图上：
  - 写在白板/PPT 标题上
  - 出现在桌上文件的标题/条目
  - 显示在手机/电脑屏幕的消息里
  - 标注在时间轴/项目看板上
- 每个词旁有**标注标签**：白色圆角矩形 + 细边框 + 阴影，词（加粗大字）+ 释义（稍小清晰字），不透明，高对比度
- 无其他叠加文字，标注即内容

**提示词模板：**
```
An Instagram-style English learning knowledge poster, landscape 16:9 wide format.
A sweeping cinematic panorama of [SCENE_SETTING] — [ATMOSPHERE_DESCRIPTION].
Warm editorial photography, sophisticated color grading, photorealistic.

Five vocabulary words are embedded INSIDE the scene as natural environmental elements,
each with a small clean white callout label:

[For each word:]
[N]. [HOW_WORD_APPEARS_IN_ENVIRONMENT] — callout label: [WORD] / [BRIEF_DEFINITION]

All callout labels: crisp white rounded rectangles, visible dark border,
subtle drop shadow. Text: large bold black sans-serif for the word,
slightly smaller but clearly readable for the definition.
Labels must be sharp, opaque, and prominent.

English only. No Chinese characters. No cartoon.
```

---

## 生图提示词检查清单（生成前必过）

在把提示词写入 `prompts.json` 之前，逐条确认：

- [ ] 包含英文学习内容（例句/对话/词汇）？
- [ ] 无汉字？
- [ ] 有真实人像（非卡通）？
- [ ] 比例正确（见各模板）？
- [ ] 需要拆分的卡片已拆分（地道对照/救命句）？
- [ ] 知识密度适中（一张图不超过一个核心知识点）？
- [ ] 场景化（不是静态文字格/表格）？
- [ ] 气泡/标注格式正确（cloud shape / callout label）？
