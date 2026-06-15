# living-docs

> **可视化的「活文档」体系，装一次，任意代码项目可用。**
> 为任何项目维护一套居中正文 + 左侧目录的 HTML 文档：按「领域（可扩展）× 类型
> （architecture 总架构 / changes 变更记录 / plans 计划）」组织，外加全局的系统总架构、
> 路线图、术语总表 glossary。共享单一 CSS、纯 CSS 架构图、本地 mermaid、自动汇总术语、
> 校验闸门、脚手架——专治文档的两个老毛病：腐化和摩擦。可安装到 Claude Code / Cursor /
> Codex / OpenCode。

文档放在每个项目根的 `docs/`，脚本按「当前工作目录所在的项目」定位它，所以这个 skill **装一次、任意项目通用**。

---

## 解决什么问题

文档会死，通常死于两个原因：

- **腐化（rot）**：文档和代码慢慢脱节——架构图过时、引用的文件早改名、术语各写各的。读的人不敢信，于是没人维护，于是更烂。
- **摩擦（friction）**：写起来累——每篇都要从零搭 HTML、手算相对路径、调样式、画图。累就不写，于是干脆不写。

living-docs 的对策是把这两件事都做掉：

| 敌人 | 对策 |
|---|---|
| **腐化** | **校验闸门** `check_docs.py` 提交前必须通过：断链、孤儿页、缺图、缺术语、`<code>` 里引用的路径在仓库里不存在、glossary 过期——任一红了不许提交。架构是活文档，每次大改后更新到最新。 |
| **摩擦** | **脚手架**自动生成骨架（正确深度的 CSS/mermaid 引用、日期、git commit、图与术语占位）并挂进时间线/首页；**共享单一 CSS**改一处全生效；架构图用**纯 CSS 盒子图**（零依赖，`file://` 一定显示）。 |

---

## 你得到什么

| 能力 | 它做什么 |
|---|---|
| **领域 × 类型结构** | 领域（domain）按子系统划分、可扩展（`api` / `web` / `worker` / `billing`…）；每个领域含三类文档：**architecture**（现在整体长什么样，活文档）、**changes**（这次改了什么、为什么，一次一篇、不可变）、**plans**（计划 / 蓝图）。 |
| **共享 CSS · 居中布局** | 全站唯一 `assets/doc.css`：左侧钉一个编号目录 `.toc`，正文在右侧居中。改样式只改这一处，全部文档一起变。文档**禁止内联 `<style>`**。 |
| **纯 CSS 架构图** | `.archmap` 分层盒子图（`.tier` / `.abox`，可着色 blue/green/violet/amber/red/ghost）。零 JS 依赖，`file://` 双击直接打开就能看——架构总览首选。 |
| **mermaid 流程图** | 流程 / 状态机 / 时序用 mermaid，由**本地 vendored** `mermaid.min.js` + `diagram.js`（经典脚本，非 module）渲染，`file://` 也能跑。中文节点标签用双引号。 |
| **术语字典 + glossary 汇总** | 每篇文档**必含**一个 `id="entities"` 的「实体与术语」section；`build_glossary.py` 从所有文档的 `.term-grid` 自动汇总成全局 `glossary.html`（按领域分组、按术语去重、记录出处）。glossary 是生成产物，不手改。 |
| **校验闸门** | `check_docs.py` 一次跑完：样式/脚本引用与相对深度、禁内联 style、缺术语、缺图、mermaid 块平衡、内部断链、孤儿页、代码-文档一致性（活文档 `<code>` 路径必须真实存在）、glossary 是否 stale。 |
| **脚手架** | `init.py`（初始化 docs/ + 复制 assets + 首页/总架构骨架）、`new_domain.py`（建领域并挂首页）、`new_change.py`（建变更并挂时间线）——自动算相对路径、填当天日期与 git short commit。 |

---

## 安装

仓库根有一个跨 host 安装脚本 `./setup`，默认装到 Claude Code：

```bash
git clone https://github.com/wuyuxiangX/living-docs ~/.living-docs \
  && ~/.living-docs/setup
```

装好后 skill 在 `~/.claude/skills/living-docs/`（SKILL.md + 脚本 + assets）。

### 其它 host / 选项

```bash
./setup                      # 默认 claude
./setup --host cursor        # → ~/.cursor/skills/living-docs
./setup --host codex         # → ~/.codex/skills/living-docs
./setup --host opencode      # → ~/.opencode/skills/living-docs
./setup --copy               # 复制而非软链（Windows 自动降级为 copy）
./setup --uninstall          # 从所选 host 移除
```

下文用 `$SKILL` 指代安装目录（如 `~/.claude/skills/living-docs`）。

---

## 在一个新项目里启用

`cd` 到目标项目根，跑一次 `init.py`——它会建 `docs/`、复制样式资产、生成首页与系统总架构骨架：

```bash
cd /path/to/your-project
python3 ~/.claude/skills/living-docs/init.py
```

它做了什么：

- 建 `docs/assets/` 并复制 `doc.css` / `mermaid.min.js` / `diagram.js`；
- 生成 `docs/index.html`（总导航）与 `docs/architecture.html`（系统总架构）骨架；
- 生成空的 `docs/glossary.html`（让 stale 检查从一开始就一致）。

然后加第一个领域、写第一篇变更：

```bash
python3 ~/.claude/skills/living-docs/new_domain.py api          # 建 docs/api/ 并挂进首页
python3 ~/.claude/skills/living-docs/new_change.py api init-auth # 建变更并挂进时间线
```

> 脚本定位 `docs/` 的顺序：环境变量 `LIVING_DOCS_ROOT` → 当前目录的 git 根 → 向上找第一个含 `docs/` 的目录 → 当前目录。
> 文档子目录默认 `docs/`，可用 `LIVING_DOCS_DIR` 改名。

---

## 日常用法

**每次大改（重构 / 新功能 / 架构调整 / 改对外契约）后**，固定动作：

```bash
# 1) 写一篇变更记录（自动算相对路径、填日期+commit、挂进时间线）
python3 $SKILL/new_change.py <domain> <topic-slug>
#    → 生成 docs/<domain>/changes/YYYY-MM-DD-<topic>.html，然后填内容

# 2) 更新该领域 docs/<domain>/architecture.html 到改完后的最新；
#    若影响跨领域，再更新顶层 docs/architecture.html

# 3) 若新增/改了术语，刷新全局术语总表
python3 $SKILL/build_glossary.py

# 4) 提交前跑校验闸门——必须通过，红了不许提交
python3 $SKILL/check_docs.py
```

小 bugfix / 改注释 / 改测试这类小改，先判断是否真需要更新文档，不确定就问一句，别为小修改硬写文档。动过术语先 `build_glossary.py` 再 `check_docs.py`（check 会兜底报 stale）。

---

## 文档结构

```text
docs/
  index.html                       总导航（列全部领域 + 全局文档）
  architecture.html                系统总架构（跨领域，纯 CSS 盒子图）
  roadmap.html                     产品路线图（跨领域，可选）
  glossary.html                    术语总表（生成产物，勿手改）
  assets/
    doc.css                        唯一样式表（改样式只改这里）
    mermaid.min.js                 本地 vendored mermaid（file:// 可渲染）
    diagram.js                     mermaid 初始化（经典脚本）
  <domain>/                        一个领域 = 一个目录（api / web / worker / billing…）
    architecture.html              该领域当前总架构（活文档）
    changes/
      index.html                   变更时间线
      YYYY-MM-DD-<topic>.html      一次修改 = 一篇（不可变）
    plans/
      index.html                   计划列表
      <topic>.html                 计划 / 蓝图
```

---

## 脚本清单

| 脚本 | 作用 |
|---|---|
| `init.py` | 在当前项目建 `docs/` + 复制 assets + 生成首页与系统总架构骨架 + 空 glossary。 |
| `new_domain.py <domain>` | 建 `docs/<domain>/`（architecture + changes/ + plans/ 骨架）并在首页插入该领域区。 |
| `new_change.py <domain> <topic>` | 生成一篇变更记录骨架（正确相对深度、日期、commit、图与术语占位）并挂进时间线。 |
| `check_docs.py` | 校验闸门：断链 / 孤儿 / 缺图 / 缺术语 / 内联 style / 过时代码引用 / glossary stale。 |
| `build_glossary.py` | 从各文档 `.term-grid` 汇总生成全局 `glossary.html`（领域自动发现、按术语去重）。 |
| `_common.py` | 公共定位逻辑：按 cwd 所在项目找 `docs/`、取 git short commit。 |
| `template.html` | 手写文档时可复制的骨架（左侧目录 + 居中正文 + 图与术语占位）。 |

---

## 设计约定

- **中文优先**：`<html lang="zh-CN">`，正文用中文，技术标识符（类名、文件名、函数名）保留原文。
- **不内联 CSS**：只引用共享 `assets/doc.css`，相对路径按文档深度（首页 `assets/…`、领域页 `../assets/…`、changes 页 `../../assets/…`）。脚手架已自动算好。
- **架构图优先用纯 CSS**：架构总览用 `.archmap` 盒子图，**绝不**用 mermaid（mermaid 依赖 JS，`file://` 可能不渲染）。流程 / 状态机才用 mermaid。
- **mermaid 用经典脚本**：在 `</body>` 前引入本地 `mermaid.min.js` + `diagram.js`（非 ES module），中文节点标签必须双引号。
- **每篇必含图 + 术语**：architecture 与 changes 至少一张图（`.archmap` 或 mermaid），且必含 `id="entities"` 术语字典。
- **changes 不可变，architecture 是活文档**：要修正旧变更就新开一篇并注明 supersede；架构文档直接改到最新，历史属于 changes。
- **准确优先**：引用的类名、路径、函数名、测试结论必须与当前代码一致——校验闸门会盯活文档里的 `<code>` 路径。

---

## License

MIT — see [LICENSE](./LICENSE).
