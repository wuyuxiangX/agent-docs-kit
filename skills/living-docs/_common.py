"""living-docs 公共定位逻辑。

作为可分发 skill，脚本被安装到 ~/.claude/skills/living-docs/（或软链），运行时按
**当前工作目录所在的项目**定位 docs/，而不是 skill 自身的位置。

定位顺序：
1. 环境变量 LIVING_DOCS_ROOT（显式指定项目根）
2. 当前目录的 git 仓库根（git rev-parse --show-toplevel）
3. 从当前目录向上找第一个含 docs/ 的目录
4. 兜底：当前目录

文档子目录默认 docs/，可用 LIVING_DOCS_DIR 覆盖。
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path


def project_root() -> Path:
    env = os.environ.get("LIVING_DOCS_ROOT")
    if env:
        return Path(env).expanduser().resolve()
    cwd = Path.cwd()
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=cwd, capture_output=True, text=True, check=True,
        )
        top = out.stdout.strip()
        if top:
            return Path(top)
    except Exception:
        pass
    for d in (cwd, *cwd.parents):
        if (d / "docs").is_dir():
            return d
    return cwd


def docs_dir() -> Path:
    return project_root() / os.environ.get("LIVING_DOCS_DIR", "docs")


def short_commit(root: Path | None = None) -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=root or project_root(), capture_output=True, text=True, check=True,
        )
        return out.stdout.strip() or "unknown"
    except Exception:
        return "unknown"
