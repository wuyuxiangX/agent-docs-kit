# Changelog

## 1.0.0

首个版本。从 sumx 项目里沉淀出来的文档体系，通用化为可分发 skill。

- **领域 × 类型** 文档组织：`docs/<domain>/{architecture, changes/, plans/}`（领域可扩展）+ 全局
  `architecture.html` / `roadmap.html` / `glossary.html`。
- **共享样式** `assets/doc.css`：居中正文 + 左侧 sticky 目录，改一处全生效；不内联 CSS。
- **图示**：纯 CSS 架构盒子图 `.archmap`（零依赖、`file://` 一定显示）+ 本地 vendored mermaid
  流程图（经典脚本，`file://` 可渲染）。
- **术语**：每篇必含「实体与术语字典」，`build_glossary.py` 自动汇总成跨文档总表（领域自动发现、去重）。
- **校验闸门** `check_docs.py`：断链 / 孤儿页 / 缺图 / 缺术语 / 相对深度 / mermaid 块平衡 /
  代码-文档一致性（活文档 `<code>` 路径须真实存在）/ glossary 是否过期。
- **脚手架**：`init.py`（新项目落地 docs/ + 资产 + 首页/总架构骨架）、`new_domain.py`（建领域并挂首页）、
  `new_change.py`（建变更并挂时间线，自动填日期 + git commit）。
- 脚本按**当前工作目录所在项目**定位 `docs/`（git 根 → 含 docs/ 的祖先 → cwd），安装一次任意项目可用。
- 跨平台安装：`setup` 支持 Claude Code / Cursor / Codex / OpenClaw。
