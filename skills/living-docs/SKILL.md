---
name: living-docs
description: 为任意代码项目维护一套可视化 HTML 文档体系——按领域（可扩展，如 api/web/worker…）× 类型（architecture 总架构 / changes 变更记录 / plans 计划蓝图）组织，外加全局的系统总架构、路线图、术语总表 glossary。配套校验闸门与脚手架。当用户要求"写文档/变更记录/架构文档/更新架构图/写计划"，或一次重构、新功能、架构调整完成后需要留痕时使用。
---

# living-docs

为项目维护**居中正文 + 左侧目录**的可视化 HTML 文档，共享一套样式表，按「领域 × 类型」组织。
文档系统的两个敌人是**腐化**（与代码脱节）和**摩擦**（写起来累就不写）；这个 skill 用统一样式、
脚手架、校验闸门来同时压制这两点。文档放在项目根的 `docs/`（可用 `LIVING_DOCS_DIR` 改子目录名）。

> 路径约定：下文 `$SKILL/` 指本 skill 的安装目录（如 `~/.claude/skills/living-docs/`）。
> 脚本按**当前工作目录所在的项目**定位 `docs/`（git 根 → 含 docs/ 的祖先 → cwd），
> 所以在任意项目根运行都对那个项目生效。

## 心智模型：领域 × 类型（都可扩展）

```text
docs/
  index.html                 总导航（列全部领域 + 全局文档）
  architecture.html          系统总架构（跨领域，纯 CSS 盒子图）
  roadmap.html               产品路线图（跨领域，可选）
  glossary.html              实体与术语总表（汇总各文档术语，生成产物）
  assets/doc.css             唯一样式表（改样式只改这里）
  assets/mermaid.min.js      本地 vendored mermaid（file:// 可渲染）
  assets/diagram.js          mermaid 初始化（经典脚本）
  <domain>/                  一个领域 = 一个目录（按你的子系统命名，如 api / web / worker / billing）
    architecture.html        该领域当前总架构（活文档）
    changes/
      index.html             变更时间线
      YYYY-MM-DD-<topic>.html 一次修改 = 一篇（不可变）
    plans/
      index.html             计划列表
      <topic>.html           计划 / 蓝图
```

- **领域（domain）可扩展**：按项目的子系统划分。新子系统就 `new_domain.py <domain>`，会建目录并挂进首页。
- **类型有三类**：
  - **architecture**：回答「现在整体长什么样」。活文档，每次大改后更新到最新。
  - **changes**：回答「这一次改了什么、为什么」。一次修改一篇，不可变。
  - **plans**：计划 / 蓝图 / 未落地的后续方向。落地后写一篇 changes，并更新 architecture。
- **全局文档（跨领域）**：`architecture.html`（系统总架构）、`roadmap.html`（路线图）、`glossary.html`（术语总表）。

## 每次大修改后的固定动作

1. 写一篇变更记录 `docs/<domain>/changes/YYYY-MM-DD-<topic>.html`（用脚手架起手）。
2. 更新 `docs/<domain>/architecture.html` 反映改完后的当前架构；若影响跨领域全局，更新顶层 `docs/architecture.html`。
3. 在 `docs/<domain>/changes/index.html` 时间线顶部加一行链接（脚手架会自动做）。
4. 若有新实体/术语，**刷新 `docs/glossary.html`**（见下「术语总表」）。
5. 计划落地或调整时，相应更新 `docs/<domain>/plans/`。
6. 必要时更新 `docs/index.html`（新领域要加领域区）。

日期用真实当天日期，不要编造。

## HTML 写法

每篇文档可复制 `$SKILL/template.html` 作骨架（或用脚手架生成），然后填内容。要点：

- **引用共享样式**，不要内联 CSS：`<link rel="stylesheet" href="<相对路径>/assets/doc.css" />`
  - `docs/index.html` → `assets/doc.css`
  - `docs/<domain>/architecture.html` → `../assets/doc.css`
  - `docs/<domain>/changes/x.html` → `../../assets/doc.css`
- **若用 mermaid**，按相对深度在 `</body>` 前引入两个经典脚本（不是 module，否则 file:// 不渲染）：
  `<script src="<相对路径>/assets/mermaid.min.js"></script>` 再
  `<script src="<相对路径>/assets/diagram.js"></script>`。纯 CSS 架构图不需要脚本。
- `<html lang="zh-CN">`，正文用**中文**（技术标识符保留原文）。
- 结构：左侧 `.toc`（编号目录 + meta）+ `main > .content`（正文，CSS 已居中；目录钉左、正文在右侧居中）。
- 间距由 CSS 自动处理（`.content section > * + *`），不要手写 margin。
- 善用组件类：`.panel`（含 blue/green/red/amber/violet）、`.grid.two/.three/.four`、`.before-after`、
  `.flow`/`.flow-row`/`.flow-body`/`.step`、`.timeline`、`.note`/`.note.warn`、`.code-block`、`.chip`、
  `table`、`.term-grid`/`.term`、`.archmap`/`.tier`/`.abox`、`.nav-grid`/`.nav-card`。
- meta 区写：Date、Base commit（`git rev-parse --short HEAD`）、Source、Tests 结果。

## 必含：图示

每篇文档（architecture 与 changes）**必须**至少有一张图。两种画法，按场景选：

### 1) 架构图 → 纯 CSS 盒子图（首选，零依赖、file:// 一定显示）

系统/子系统的**架构总览**用 `.archmap` 盒子图，**绝不**用 mermaid（mermaid 依赖 JS，file:// 可能不渲染）。
先画总览分层，区域不够就「先总后细」分块展开：

```html
<div class="archmap">
  <div class="tier">
    <div class="tier-h">① 层标题</div>
    <div class="tier-boxes">
      <div class="abox blue"><b>组件名</b><span>一句话</span></div>
      <div class="abox"><b>组件名</b><span>一句话</span></div>
    </div>
  </div>
  <div class="tier-sep">↓</div>
  <div class="tier"> … 下一层 … </div>
</div>
<p class="figcaption">图注</p>
```

`.abox` 可加 `blue/green/violet/amber/red/ghost` 着色；`ghost` 表示「未来/未实现」。

### 2) 流程 / 状态机 → Mermaid（可选）

流程、状态流转、时序适合 Mermaid，写在 `<pre class="mermaid"> … </pre>`，由本地
`assets/mermaid.min.js` + `diagram.js` 渲染（经典脚本，已 vendored，file:// 可用）：

```html
<pre class="mermaid">
flowchart TD
  A["输入"] --> B{"判断?"}
  B -->|是| C["动作"]
</pre>
<p class="figcaption">一行图注</p>
```

- 中文节点标签**必须用双引号**包裹：`A["纯工具循环"]`；箭头注记用 `-->|文字|`。
- architecture：至少一张「整体架构图 / 核心数据流图」。changes：至少一张「本次改动的流程 / 状态机 / 前后对比」。
- 图要忠于代码，不杜撰节点。ASCII 图（`.code-block`）可作补充，但不替代图。

## 必含：实体与术语字典

每篇文档**必须**有一个 `id="entities"` 的「实体与术语」section（`.term-grid` + `.term`/`dt`/`dd`），
逐条解释涉及的类型、概念、约定。按本系统语境解释，不抄教科书定义。

## 术语总表 glossary（汇总）

各文档术语汇总进 `docs/glossary.html`。它是**生成产物**，不要手改——新增/改术语后重跑：

```bash
python3 "$SKILL/build_glossary.py"
```

脚本从所有文档的 `.term-grid` 提取，领域自动发现（docs/ 子目录各为一领域，顶层文件归 system），按术语去重。

## 脚手架（起手别手抄相对路径）

```bash
# 新变更：生成骨架（正确深度的 css/mermaid 引用、图/术语占位、自动填日期+commit）并挂进时间线
python3 "$SKILL/new_change.py" <domain> <topic-slug>
# 新领域：生成 architecture + changes/ + plans/ 骨架并挂进首页领域区
python3 "$SKILL/new_domain.py" <domain>
```

生成后填内容，再跑校验闸门。

## 提交前检查文档（重要）

**每次 `git commit` 前**，先判断这次代码改动是否需要更新文档，按改动大小分级：

- **大改**（重构 / 新功能 / 架构调整 / 新领域 / 改对外契约）：必须按「固定动作」更新 changes + architecture，
  必要时加 plans、刷新 glossary，连同代码一起提交。
- **小改 / 不确定**（小 bugfix、改注释、改测试、局部重命名等）：**先询问用户**是否需要更新文档，
  不要默认生成——避免为小修改浪费资源。用户说不用就跳过。
- **纯文档改动**：直接更新，无需问。

判断不了「算大算小」时，宁可问一句，也不要擅自跳过或擅自大动。

**只要动了 `docs/`，提交前必须跑校验闸门并通过：**

```bash
python3 "$SKILL/check_docs.py"   # 断链/孤儿/缺图/缺术语/过时代码引用/glossary stale
```

红了不许提交。动过术语先 `build_glossary.py` 再 check（check 会兜底报 stale）。

## 内容纪律

- 准确优先：引用的类名、文件路径、函数名、测试结论必须与当前代码一致，写前核对。
- 讲清「为什么」：变更记录要有动机/取舍，不是流水账。
- 变更记录不可变；要修正就新开一篇并注明 supersede 关系。
- 架构文档是活文档，直接改到最新；不要在里面堆历史，历史属于 changes。

## 首次在一个新项目启用

```bash
python3 "$SKILL/init.py"                  # 建 docs/ + 复制 assets + 生成 index/architecture/glossary 骨架
python3 "$SKILL/new_domain.py" <第一个领域>  # 建领域并挂进首页
```

之后填 `docs/architecture.html` 与 `docs/index.html` 的内容，用 `new_change.py` 写变更。
`init.py` 会自动把 `doc.css / mermaid.min.js / diagram.js` 复制到项目的 `docs/assets/`，无需手动搬。
