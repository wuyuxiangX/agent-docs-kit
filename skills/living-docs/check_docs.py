#!/usr/bin/env python3
"""文档校验闸门 —— 提交前必须通过。

    python3 <skill>/check_docs.py

按当前工作目录所在项目定位 docs/，一次跑完：样式/脚本引用、相对深度、禁内联 style、
术语字典、图、mermaid 块平衡、内部链接可达、孤儿页、代码-文档一致性（<code> 里的路径
真实存在）、glossary 是否过期。有任何问题 → 退出码 1 并打印清单。
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SKILL_DIR))
from _common import docs_dir, project_root  # noqa: E402

REPO = project_root()
DOCS = docs_dir()

# 路径首段属于这些目录之一时，才当作「代码路径」校验（避免误判 oauth/token 这类 API 路径）。
# 通用集合，覆盖常见项目布局；最终是否报错以「全仓库后缀匹配不到」为准，故宁可宽。
KNOWN_DIRS = {
    "apps", "app", "src", "lib", "libs", "packages", "pkg", "internal", "cmd",
    "modules", "core", "tools", "services", "components", "server", "client",
    "docs", "scripts", "config", "test", "tests", "assets",
}
CODE_EXTS = (".py", ".ts", ".tsx", ".js", ".css", ".html", ".json", ".sql", ".yaml", ".yml")
# 含这些字符的不是纯路径（方法调用、HTML 实体、占位符、含空格的句子）
FORBIDDEN = set("()&<>{}…*|, ")
# 只对「描述当前状态的活文档」做代码路径校验；历史 changes / 计划 plans / 生成的 glossary / 导航 index 豁免
STRICT_PATH_DOCS = {"architecture.html", "provider-onboarding.html"}
_PRUNE = {".venv", ".git", "node_modules", "__pycache__", "dist", ".next", ".turbo"}


def depth_of(rel: Path) -> int:
    return len(rel.parts) - 1


def build_repo_index() -> set[str]:
    """全仓库文件的相对路径集合（剪掉依赖/构建目录），用于按后缀匹配代码路径。"""
    files: set[str] = set()
    for root, dirs, names in os.walk(REPO):
        dirs[:] = [d for d in dirs if d not in _PRUNE]
        for n in names:
            files.add(str(Path(root, n).relative_to(REPO)))
    return files


def looks_like_path(text: str) -> bool:
    if "/" not in text or text.startswith(("/", ".")):
        return False
    if any(c in FORBIDDEN for c in text):
        return False
    first = text.split("/", 1)[0]
    return text.endswith(CODE_EXTS) or first in KNOWN_DIRS


def path_in_index(cand: str, index: set[str]) -> bool:
    cand = cand.rstrip("/")
    suffix = "/" + cand
    return any(f == cand or f.endswith(suffix) for f in index)


def check() -> list[str]:
    errs: list[str] = []
    htmls = sorted(DOCS.rglob("*.html"))
    linked: set[Path] = set()
    repo_index = build_repo_index()

    for f in htmls:
        rel = f.relative_to(DOCS)
        s = f.read_text()
        prefix = "../" * depth_of(rel)

        # 样式 / 脚本 / 禁内联
        if "<style" in s:
            errs.append(f"{rel}: 含内联 <style>（应只用 assets/doc.css）")
        if f'href="{prefix}assets/doc.css"' not in s:
            errs.append(f'{rel}: 缺正确的 doc.css 引用（应为 href="{prefix}assets/doc.css"）')
        uses_mermaid = '<pre class="mermaid">' in s
        if uses_mermaid:
            for asset in ("mermaid.min.js", "diagram.js"):
                if f'src="{prefix}assets/{asset}"' not in s:
                    errs.append(f'{rel}: 用了 mermaid 但缺 src="{prefix}assets/{asset}"')
            if s.count('<pre class="mermaid">') != s.count("</pre>"):
                errs.append(f"{rel}: mermaid <pre> 与 </pre> 数量不平衡")

        is_index = f.name == "index.html"
        is_glossary = f.name == "glossary.html"

        # 术语字典（内容页必含）
        if not is_index and not is_glossary and 'id="entities"' not in s:
            errs.append(f"{rel}: 缺 id=\"entities\" 实体与术语字典")

        # 图（architecture 与 changes/<date>-*.html 至少一张）
        is_arch = f.name == "architecture.html"
        is_change = rel.parts[-2:-1] == ("changes",) and re.match(r"\d{4}-\d{2}-\d{2}-", f.name)
        if (is_arch or is_change) and 'class="archmap"' not in s and 'class="mermaid"' not in s:
            errs.append(f"{rel}: 缺图示（architecture/changes 至少一张 .archmap 或 mermaid）")

        # 内部链接可达
        for m in re.findall(r'href="([^"]+)"', s):
            if m.startswith(("#", "http", "mailto:")):
                continue
            target = (f.parent / m.split("#")[0]).resolve()
            if m.endswith(".html"):
                linked.add(target)
                if not target.exists():
                    errs.append(f"{rel}: 断链 -> {m}")
            elif m.endswith((".css", ".js")):
                if not target.exists():
                    errs.append(f"{rel}: 资源链接失效 -> {m}")

        # 代码-文档一致性（仅活文档：architecture / provider-onboarding）
        if f.name in STRICT_PATH_DOCS:
            for code in re.findall(r"<code>(.*?)</code>", s, re.S):
                code = code.strip()
                if looks_like_path(code) and not path_in_index(code, repo_index):
                    errs.append(f"{rel}: <code> 引用的路径不存在 -> {code}")

    # 孤儿页（根 index.html 是入口，豁免）
    root_index = (DOCS / "index.html").resolve()
    for f in htmls:
        if f.resolve() == root_index:
            continue
        if f.resolve() not in linked:
            errs.append(f"{f.relative_to(DOCS)}: 孤儿页（没有任何页面链向它）")

    # glossary 新鲜度
    sys.path.insert(0, str(SKILL_DIR))
    try:
        import build_glossary

        expected = build_glossary.render(build_glossary.collect())
        gloss = DOCS / "glossary.html"
        actual = gloss.read_text() if gloss.exists() else ""
        if expected.strip() != actual.strip():
            errs.append("glossary.html 过期（stale），请重跑 build_glossary.py")
    except Exception as exc:  # noqa: BLE001
        errs.append(f"glossary 新鲜度检查失败: {exc}")

    return errs


def main() -> int:
    errs = check()
    if errs:
        print(f"✗ 文档校验失败，{len(errs)} 个问题：")
        for e in errs:
            print(f"  - {e}")
        return 1
    n = len(list(DOCS.rglob("*.html")))
    print(f"✓ 文档校验通过（{n} 个 HTML，无问题）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
