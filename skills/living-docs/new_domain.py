#!/usr/bin/env python3
"""脚手架：新建一个文档领域（architecture + changes/ + plans/）并挂进首页。

    python3 <skill>/new_domain.py <domain>
    例：python3 <skill>/new_domain.py billing

按当前工作目录所在项目定位 docs/，生成 docs/<domain>/{architecture.html, changes/index.html,
plans/index.html} 骨架，并在 docs/index.html 领域区后插入一个新领域 section。生成后填内容，再跑 check_docs.py。
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


def architecture_html(domain: str, today: str, commit: str) -> str:
    cap = domain.capitalize()
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{cap} 总架构 · Sumx</title>
<link rel="stylesheet" href="../assets/doc.css" />
</head>
<body>
<div class="shell">
  <aside class="toc">
    <a class="back" href="../index.html">← 文档首页</a>
    <div class="brand"><div class="mark" aria-hidden="true"></div><strong>Sumx · {cap}</strong></div>
    <p class="subtitle">总架构 · 活文档</p>
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
      <div class="eyebrow">{cap} Architecture</div>
      <h1>{cap} 总架构</h1>
      <p class="lead">TODO：{cap} 子系统是做什么的、整体长什么样。</p>

      <section id="overview">
        <h2><span class="num">01</span>总览</h2>
        <p class="section-desc">TODO</p>
        <div class="archmap">
          <div class="tier">
            <div class="tier-h">① TODO 层</div>
            <div class="tier-boxes">
              <div class="abox"><b>TODO</b><span>一句话</span></div>
            </div>
          </div>
        </div>
        <p class="figcaption">TODO：图注</p>
      </section>

      <section id="entities">
        <h2><span class="num">02</span>实体与术语字典</h2>
        <p class="section-desc">逐条解释本领域涉及的类型/概念（必含）。</p>
        <dl class="term-grid">
          <div class="term"><dt>TODO</dt><dd>TODO</dd></div>
        </dl>
      </section>

      <footer>架构活文档，每次大改后更新。变更见 <a href="./changes/index.html">时间线</a>。</footer>
    </div>
  </main>
</div>
</body>
</html>
"""


def list_index_html(domain: str, kind: str) -> str:
    cap = domain.capitalize()
    label = "变更时间线" if kind == "changes" else "计划 plans"
    eyebrow = f"{cap} · {'Changes' if kind == 'changes' else 'Plans'}"
    note = (
        "本领域暂无内容。用脚手架新增："
        f"<code>new_change.py {domain} &lt;topic&gt;</code>。"
        if kind == "changes"
        else "本领域暂无计划。后续计划写在这里。"
    )
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{cap} {label} · Sumx</title>
<link rel="stylesheet" href="../../assets/doc.css" />
</head>
<body>
<div class="shell">
  <aside class="toc">
    <a class="back" href="../../index.html">← 文档首页</a>
    <div class="brand"><div class="mark" aria-hidden="true"></div><strong>Sumx · {cap}</strong></div>
    <p class="subtitle">{label}</p>
    <a href="../architecture.html"><span class="n">▲</span>本领域总架构</a>
    <a href="#list"><span class="n">◷</span>列表</a>
    <div class="meta">类型: {label}</div>
  </aside>
  <main>
    <div class="content">
      <div class="eyebrow">{eyebrow}</div>
      <h1>{cap} {label}</h1>
      <p class="lead">TODO：本页列出 {cap} 的{label}。</p>
      <section id="list">
        <h2><span class="num">◷</span>列表</h2>
        <div class="note">{note}</div>
      </section>
      <footer>由 skill <code>sumx-doc</code> 维护。</footer>
    </div>
  </main>
</div>
</body>
</html>
"""


def link_into_home(domain: str) -> bool:
    index = DOCS / "index.html"
    s = index.read_text()
    cap = domain.capitalize()
    initial = cap[0]
    toc = f'    <a href="#{domain}"><span class="n">{initial}</span>{cap}</a>\n'
    section = f"""      <section id="{domain}">
        <h2><span class="num">{initial}</span>{cap} 子系统</h2>
        <p class="section-desc">TODO：一句话定位。</p>
        <div class="nav-grid">
          <a class="nav-card" href="./{domain}/architecture.html"><div class="k">ARCHITECTURE</div><h3>总架构 →</h3><p class="muted">TODO</p></a>
          <a class="nav-card" href="./{domain}/changes/index.html"><div class="k">CHANGES</div><h3>变更时间线 →</h3><p class="muted">TODO</p></a>
          <a class="nav-card" href="./{domain}/plans/index.html"><div class="k">PLANS</div><h3>计划/蓝图 →</h3><p class="muted">TODO</p></a>
        </div>
      </section>

"""
    ok = True
    if '<a href="#how">' in s:
        s = s.replace('    <a href="#how">', toc + '    <a href="#how">', 1)
    else:
        ok = False
    if '      <section id="how">' in s:
        s = s.replace('      <section id="how">', section + '      <section id="how">', 1)
    else:
        ok = False
    if ok:
        index.write_text(s)
    return ok


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print(__doc__)
        return 2
    domain = argv[0].strip().lower()
    if not re.fullmatch(r"[a-z][a-z0-9-]*", domain):
        print("✗ 领域名只能用小写字母/数字/连字符")
        return 1
    base = DOCS / domain
    if base.exists():
        print(f"✗ 已存在：docs/{domain}/")
        return 1
    today = date.today().isoformat()
    commit = short_commit()
    (base / "changes").mkdir(parents=True)
    (base / "plans").mkdir(parents=True)
    (base / "architecture.html").write_text(architecture_html(domain, today, commit))
    (base / "changes" / "index.html").write_text(list_index_html(domain, "changes"))
    (base / "plans" / "index.html").write_text(list_index_html(domain, "plans"))
    home_ok = link_into_home(domain)
    print(f"✓ 已生成 docs/{domain}/（architecture + changes/ + plans/）")
    print("  首页领域区：" + ("已自动挂入 ✓" if home_ok else "未能自动挂入，请手动在 docs/index.html 加领域 section"))
    print("  下一步：填 architecture 内容 → 跑 check_docs.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
