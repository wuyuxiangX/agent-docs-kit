#!/usr/bin/env python3
"""从各文档的「实体与术语字典」(.term-grid) 汇总生成 <docs>/glossary.html。

每篇文档内仍各自保留术语；这里做一个跨文档的总表，按领域分组、按术语去重
（同名取第一次出现，并记录还出现在哪些文档）。改完文档后重新跑：

    python3 <skill>/build_glossary.py

领域自动发现：docs/ 下的子目录各为一个领域，顶层文件归入「system」。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import docs_dir  # noqa: E402

SYSTEM = "system"
DOMAIN_LABEL_OVERRIDE = {SYSTEM: "全局 / 系统"}

TERM_RE = re.compile(
    r'<div class="term">\s*<dt>(?P<dt>.*?)</dt>\s*<dd>(?P<dd>.*?)</dd>\s*</div>',
    re.S,
)


def domain_of(rel: Path) -> str:
    parts = rel.parts
    return parts[0] if len(parts) > 1 else SYSTEM


def domain_label(d: str) -> str:
    return DOMAIN_LABEL_OVERRIDE.get(d, d.capitalize())


def strip_tags(s: str) -> str:
    return re.sub(r"<[^>]+>", "", s).strip().lower()


def collect() -> dict[str, list[tuple[str, str, list[str]]]]:
    """domain -> [(dt_html, dd_html, source_paths)]，按领域分组、按术语去重。"""
    root = docs_dir()
    buckets: dict[str, dict] = {}
    for f in sorted(root.rglob("*.html")):
        if f.name in {"index.html", "glossary.html"}:
            continue
        rel = f.relative_to(root)
        dom = domain_of(rel)
        bucket = buckets.setdefault(dom, {})
        for m in TERM_RE.finditer(f.read_text()):
            dt = " ".join(m.group("dt").split())
            dd = " ".join(m.group("dd").split())
            key = strip_tags(dt)
            if not key:
                continue
            if key in bucket:
                bucket[key][2].append(str(rel))
            else:
                bucket[key] = [dt, dd, [str(rel)]]
    # 顺序：system 优先，其余领域字母序
    ordered = ([SYSTEM] if SYSTEM in buckets else []) + sorted(d for d in buckets if d != SYSTEM)
    return {d: list(buckets[d].values()) for d in ordered}


def render(groups: dict[str, list]) -> str:
    total = sum(len(v) for v in groups.values())
    toc = "\n".join(
        f'    <a href="#{d}"><span class="n">{i + 1:02d}</span>{domain_label(d)}</a>'
        for i, d in enumerate(groups)
    )
    sections = []
    for d in groups:
        terms = sorted(groups[d], key=lambda t: strip_tags(t[0]))
        cards = []
        for dt, dd, srcs in terms:
            uniq = sorted(set(srcs))
            src_note = (
                f'<span class="muted" style="font-size:11px">见 {", ".join(uniq)}</span>'
                if len(uniq) > 1
                else ""
            )
            cards.append(f'          <div class="term"><dt>{dt}</dt><dd>{dd} {src_note}</dd></div>')
        sections.append(
            f'      <section id="{d}">\n'
            f'        <h2><span class="num">{domain_label(d)}</span></h2>\n'
            f'        <p class="section-desc">{len(terms)} 条。</p>\n'
            f'        <dl class="term-grid">\n' + "\n".join(cards) + "\n        </dl>\n"
            f"      </section>"
        )
    body = "\n\n".join(sections)
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>实体与术语总表 · 文档</title>
<link rel="stylesheet" href="assets/doc.css" />
</head>
<body>
<div class="shell">
  <aside class="toc">
    <a class="back" href="index.html">← 文档首页</a>
    <div class="brand"><div class="mark" aria-hidden="true"></div><strong>术语总表</strong></div>
    <p class="subtitle">实体与术语</p>
{toc}
    <div class="meta">
      自动生成（勿手改）<br />
      来源: 各文档 .term-grid<br />
      共 {total} 条
    </div>
  </aside>
  <main>
    <div class="content">
      <div class="eyebrow">Glossary</div>
      <h1>实体与术语总表</h1>
      <p class="lead">
        汇总各文档「实体与术语字典」的总表，按领域分组、按术语去重，方便一处速查（各文档内仍保留各自的术语）。
        本页由 living-docs 的 <code>build_glossary.py</code> 生成，改完文档后重新跑即可刷新。
      </p>

{body}

      <footer>自动生成 · 改文档后跑 <code>build_glossary.py</code> 刷新。</footer>
    </div>
  </main>
</div>
</body>
</html>
"""


def main() -> None:
    groups = collect()
    (docs_dir() / "glossary.html").write_text(render(groups))
    total = sum(len(v) for v in groups.values())
    print(f"glossary.html 生成完成：{total} 条，领域 {list(groups)}")


if __name__ == "__main__":
    main()
