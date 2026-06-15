#!/usr/bin/env python3
"""脚手架：生成一篇变更记录骨架并挂进时间线。

    python3 <skill>/new_change.py <domain> <topic-slug>
    例：python3 <skill>/new_change.py memory ttl-sweep-tuning

按当前工作目录所在项目定位 docs/。自动：正确相对深度的 css/mermaid/diagram 引用、
id="entities" 占位、一张图占位、meta 用当天日期 + 当前 git short commit；并在
docs/<domain>/changes/index.html 时间线顶部插链接。生成后填内容，再跑 check_docs.py / build_glossary.py。
"""
from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SKILL_DIR))
from _common import docs_dir, short_commit  # noqa: E402

DOCS = docs_dir()


def page(domain: str, title: str, fname: str, today: str, commit: str) -> str:
    cap = domain.capitalize()
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{title} · Sumx</title>
<link rel="stylesheet" href="../../assets/doc.css" />
</head>
<body>
<div class="shell">
  <aside class="toc">
    <a class="back" href="../architecture.html">← {cap} 架构</a>
    <div class="brand"><div class="mark" aria-hidden="true"></div><strong>Sumx · {cap}</strong></div>
    <p class="subtitle">变更记录</p>
    <a href="#s1"><span class="n">01</span>这次改了什么</a>
    <a href="#entities"><span class="n">02</span>实体与术语</a>
    <div class="meta">
      Date: {today}<br />
      Base commit: <code>{commit}</code><br />
      Source: TODO<br />
      Tests: TODO
    </div>
  </aside>
  <main>
    <div class="content">
      <div class="eyebrow">{cap} · Change</div>
      <h1>{title}</h1>
      <p class="lead">TODO：一句话说清这次改了什么、为什么。</p>

      <section id="s1">
        <h2><span class="num">01</span>这次改了什么</h2>
        <p class="section-desc">TODO：动机 / 做法 / 取舍。</p>
        <pre class="mermaid">
flowchart TD
  A["TODO"] --> B["TODO"]
        </pre>
        <p class="figcaption">TODO：图注</p>
      </section>

      <section id="entities">
        <h2><span class="num">02</span>实体与术语字典</h2>
        <p class="section-desc">逐条解释本文涉及的类型/概念（必含）。</p>
        <dl class="term-grid">
          <div class="term"><dt>TODO</dt><dd>TODO</dd></div>
        </dl>
      </section>

      <footer>架构事实以实现与 <a href="../architecture.html">{cap} 架构</a> 为准。</footer>
    </div>
  </main>
  <script src="../../assets/mermaid.min.js"></script>
  <script src="../../assets/diagram.js"></script>
</body>
</html>
"""


def link_into_timeline(index: Path, fname: str, title: str, mmdd: str) -> None:
    s = index.read_text()
    row = (
        '          <div class="time-row">\n'
        f'            <div class="time">{mmdd}</div>\n'
        f'            <div class="panel green"><div class="panel-title">'
        f'<a href="./{fname}">{title}</a> <span class="chip green">最新</span></div>'
        "<p>TODO</p></div>\n"
        "          </div>"
    )
    # 去掉旧的「最新」标记
    s = s.replace(' <span class="chip green">最新</span>', "")
    if '<div class="timeline">' in s:
        s = s.replace('<div class="timeline">', '<div class="timeline">\n' + row, 1)
    elif '<div class="note">' in s:  # 空索引占位 → 起一个 timeline
        s = re.sub(
            r'<div class="note">.*?</div>',
            '<div class="timeline">\n' + row + "\n        </div>",
            s, count=1, flags=re.S,
        )
    else:
        print("  ! 未能自动挂链接，请手动在 changes/index.html 加一行")
        return
    index.write_text(s)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 2
    domain, topic = argv
    domain_dir = DOCS / domain
    if not (domain_dir / "changes").is_dir():
        print(f"✗ 领域不存在：docs/{domain}/changes/（先用 new_domain.py 建领域）")
        return 1
    slug = re.sub(r"[^a-z0-9-]+", "-", topic.lower()).strip("-")
    today = date.today()
    fname = f"{today.isoformat()}-{slug}.html"
    out = domain_dir / "changes" / fname
    if out.exists():
        print(f"✗ 已存在：{out.relative_to(DOCS.parent)}")
        return 1
    title = topic.replace("-", " ")
    out.write_text(page(domain, title, fname, today.isoformat(), short_commit()))
    link_into_timeline(domain_dir / "changes" / "index.html", fname, title, today.strftime("%m-%d"))
    print(f"✓ 已生成 {out.relative_to(DOCS.parent)} 并挂进时间线")
    print("  下一步：填内容 → 更新对应 architecture.html → 跑 check_docs.py / build_glossary.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
