#!/usr/bin/env python3
"""在当前项目初始化 living-docs 文档体系。

    python3 <skill>/init.py

按当前工作目录所在项目定位根，建 docs/ 与 docs/assets/，复制本 skill 自带的样式资产
（doc.css / diagram.js / mermaid.min.js），生成首页 index.html 与系统总架构 architecture.html
骨架，并生成空的 glossary.html。之后用 new_domain.py 加领域、new_change.py 写变更。
"""
from __future__ import annotations

import shutil
import sys
from datetime import date
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SKILL_DIR))
from _common import docs_dir, short_commit  # noqa: E402

ASSETS_SRC = SKILL_DIR / "assets"


def index_html() -> str:
    return """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>项目文档</title>
<link rel="stylesheet" href="assets/doc.css" />
</head>
<body>
<div class="shell">
  <aside class="toc">
    <div class="brand"><div class="mark" aria-hidden="true"></div><strong>Docs</strong></div>
    <p class="subtitle">设计文档首页</p>
    <a href="#global"><span class="n">◇</span>全局文档</a>
    <a href="#how"><span class="n">?</span>文档怎么组织</a>
    <div class="meta">由 skill <code>living-docs</code> 维护</div>
  </aside>
  <main>
    <div class="content">
      <div class="eyebrow">Documentation</div>
      <h1>项目设计文档</h1>
      <p class="lead">
        按<strong>领域 × 类型</strong>组织。领域可扩展（用 <code>new_domain.py</code> 添加）；
        每个领域有 architecture（总架构）/ changes（变更记录）/ plans（计划）三类。
        跨领域内容放全局。
      </p>

      <section id="global">
        <h2><span class="num">◇</span>全局文档</h2>
        <p class="section-desc">不属于单一领域、统揽全局的文档。</p>
        <div class="nav-grid">
          <a class="nav-card" href="./architecture.html"><div class="k">SYSTEM</div><h3>系统总架构 →</h3><p class="muted">分层盒子图 + 逐块细节。</p></a>
          <a class="nav-card" href="./glossary.html"><div class="k">GLOSSARY</div><h3>术语总表 →</h3><p class="muted">汇总各文档术语，一处速查。</p></a>
        </div>
      </section>

      <section id="how">
        <h2><span class="num">?</span>文档怎么组织</h2>
        <div class="note">
          领域：用 <code>new_domain.py &lt;domain&gt;</code> 新增，会建目录并在此加领域区。
          变更：用 <code>new_change.py &lt;domain&gt; &lt;topic&gt;</code>。
          提交前跑 <code>check_docs.py</code>，动术语后跑 <code>build_glossary.py</code>。
        </div>
      </section>

      <footer>由 skill <code>living-docs</code> 维护。</footer>
    </div>
  </main>
</div>
</body>
</html>
"""


def architecture_html(today: str, commit: str) -> str:
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>系统总架构 · 文档</title>
<link rel="stylesheet" href="assets/doc.css" />
</head>
<body>
<div class="shell">
  <aside class="toc">
    <a class="back" href="index.html">← 文档首页</a>
    <div class="brand"><div class="mark" aria-hidden="true"></div><strong>系统</strong></div>
    <p class="subtitle">总架构 · 全景</p>
    <a href="#overview"><span class="n">01</span>总览</a>
    <a href="#entities"><span class="n">02</span>实体与术语</a>
    <div class="meta">
      Date: {today}<br />
      Base commit: <code>{commit}</code><br />
      类型: architecture（活文档）
    </div>
  </aside>
  <main>
    <div class="content">
      <div class="eyebrow">System Architecture</div>
      <h1>系统总架构</h1>
      <p class="lead">TODO：一句话讲清整个系统怎么从输入走到输出。先看总览，再逐块下钻。</p>

      <section id="overview">
        <h2><span class="num">01</span>总览</h2>
        <p class="section-desc">TODO</p>
        <div class="archmap">
          <div class="tier">
            <div class="tier-h">① TODO 层</div>
            <div class="tier-boxes">
              <div class="abox blue"><b>TODO</b><span>一句话</span></div>
              <div class="abox"><b>TODO</b><span>一句话</span></div>
            </div>
          </div>
          <div class="tier-sep">↓</div>
          <div class="tier">
            <div class="tier-h">② TODO 层</div>
            <div class="tier-boxes">
              <div class="abox"><b>TODO</b><span>一句话</span></div>
            </div>
          </div>
        </div>
        <p class="figcaption">TODO：图注</p>
      </section>

      <section id="entities">
        <h2><span class="num">02</span>实体与术语字典</h2>
        <p class="section-desc">逐条解释系统级关键概念（必含）。</p>
        <dl class="term-grid">
          <div class="term"><dt>TODO</dt><dd>TODO</dd></div>
        </dl>
      </section>

      <footer>系统总架构（活文档），每次大改后更新。</footer>
    </div>
  </main>
</div>
</body>
</html>
"""


def main() -> int:
    docs = docs_dir()
    assets = docs / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    for name in ("doc.css", "diagram.js", "mermaid.min.js"):
        shutil.copy2(ASSETS_SRC / name, assets / name)
    today = date.today().isoformat()
    commit = short_commit()
    created = []
    for rel, content in (
        ("index.html", index_html()),
        ("architecture.html", architecture_html(today, commit)),
    ):
        target = docs / rel
        if target.exists():
            print(f"  跳过已存在：{rel}")
            continue
        target.write_text(content)
        created.append(rel)
    # 生成（可能为空的）glossary，使 check_docs 的 stale 检查从一开始就一致
    import build_glossary

    build_glossary.main()
    print(f"✓ 已在 {docs} 初始化 living-docs")
    print(f"  资产: assets/doc.css, diagram.js, mermaid.min.js；新建: {', '.join(created) or '（无）'}")
    print("  下一步：python3 <skill>/new_domain.py <第一个领域>，然后填 architecture.html / index.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
