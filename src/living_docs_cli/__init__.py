from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

VERSION = "2.1.0"
PACKAGE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = PACKAGE_DIR / "assets"
STYLE_NAMES = ("atlas",)
INTEGRATION_ORDER = ("codex", "claude", "copilot", "cursor", "gemini", "generic")
INTEGRATION_ALIASES = {
    "claude-code": "claude",
    "github": "copilot",
    "github-copilot": "copilot",
    "gemini-cli": "gemini",
}
TEXT_SUFFIXES = {
    ".css",
    ".json",
    ".js",
    ".jsx",
    ".md",
    ".mdx",
    ".mjs",
    ".ts",
    ".tsx",
    ".txt",
    ".yml",
    ".yaml",
}


@dataclass(frozen=True)
class Integration:
    key: str
    label: str
    skills_dir: str
    context_file: str
    next_step: str
    invocation_prefix: str | None = None
    context_preamble: str = ""


INTEGRATIONS = {
    "codex": Integration(
        key="codex",
        label="Codex",
        skills_dir=".agents/skills",
        context_file="AGENTS.md",
        next_step="Start Codex in this project and invoke skills such as $living-docs-change.",
        invocation_prefix="$",
    ),
    "claude": Integration(
        key="claude",
        label="Claude Code",
        skills_dir=".claude/skills",
        context_file="CLAUDE.md",
        next_step="Start Claude Code in this project and invoke skills such as /living-docs-change.",
        invocation_prefix="/",
    ),
    "copilot": Integration(
        key="copilot",
        label="GitHub Copilot",
        skills_dir=".github/skills",
        context_file=".github/copilot-instructions.md",
        next_step="Use the installed GitHub Copilot skills under .github/skills.",
    ),
    "generic": Integration(
        key="generic",
        label="Generic",
        skills_dir=".living-docs/skills",
        context_file=".living-docs/AGENT_CONTEXT.md",
        next_step="Read .living-docs/skills for portable skill instructions.",
    ),
    "cursor": Integration(
        key="cursor",
        label="Cursor",
        skills_dir=".living-docs/skills",
        context_file=".cursor/rules/living-docs.mdc",
        next_step="Open the project in Cursor; the project rule points to .living-docs/skills.",
        context_preamble=(
            "---\n"
            "description: Use living-docs workflows when creating or maintaining project documentation\n"
            "alwaysApply: false\n"
            "---\n\n"
        ),
    ),
    "gemini": Integration(
        key="gemini",
        label="Gemini CLI",
        skills_dir=".living-docs/skills",
        context_file="GEMINI.md",
        next_step="Start Gemini CLI in this project; GEMINI.md points to .living-docs/skills.",
    ),
}

CONTEXT_START = "<!-- LIVING-DOCS START -->"
CONTEXT_END = "<!-- LIVING-DOCS END -->"


class CliError(RuntimeError):
    pass


def project_name(path: Path) -> str:
    return path.resolve().name or "Docs"


def render_text(content: str, variables: dict[str, str]) -> str:
    for key, value in variables.items():
        content = content.replace(f"__{key}__", value)
    return content


def is_text_file(path: Path) -> bool:
    return path.suffix in TEXT_SUFFIXES or path.name in {".gitignore"}


def iter_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*") if path.is_file())


def copy_asset_tree(
    source: Path,
    target: Path,
    *,
    variables: dict[str, str],
    force: bool,
) -> list[Path]:
    if not source.is_dir():
        raise CliError(f"asset directory not found: {source}")

    collisions: list[Path] = []
    for src in iter_files(source):
        rel = src.relative_to(source)
        dst = target / rel
        if dst.exists() and not force:
            collisions.append(dst)
    if collisions:
        shown = "\n".join(f"  - {p}" for p in collisions[:12])
        extra = "" if len(collisions) <= 12 else f"\n  ... {len(collisions) - 12} more"
        raise CliError(
            "refusing to overwrite existing files without --force:\n"
            f"{shown}{extra}"
        )

    written: list[Path] = []
    for src in iter_files(source):
        rel = src.relative_to(source)
        dst = target / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if is_text_file(src):
            dst.write_text(render_text(src.read_text(), variables))
        else:
            shutil.copy2(src, dst)
        written.append(dst)
    return written


def write_json(path: Path, payload: dict, *, force: bool) -> None:
    if path.exists() and not force:
        raise CliError(f"refusing to overwrite existing file without --force: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def parse_integration_selection(raw: str, *, default: list[str]) -> list[str]:
    if not raw.strip():
        return default

    selected: list[str] = []
    tokens = [token for token in re.split(r"[\s,]+", raw.strip().lower()) if token]
    if any(token in {"all", "*"} for token in tokens):
        return list(INTEGRATION_ORDER)

    for token in tokens:
        if token.isdigit():
            index = int(token) - 1
            if index < 0 or index >= len(INTEGRATION_ORDER):
                raise CliError(f"unknown integration number: {token}")
            key = INTEGRATION_ORDER[index]
        else:
            key = INTEGRATION_ALIASES.get(token, token)
            if key not in INTEGRATIONS:
                raise CliError(f"unknown integration: {token}")

        if key not in selected:
            selected.append(key)

    return selected


def prompt_text(label: str, default: str) -> str:
    suffix = f" [{default}]" if default else ""
    value = input(f"? {label}{suffix}: ").strip()
    return value or default


def prompt_bool(label: str, default: bool = False) -> bool:
    default_label = "Y/n" if default else "y/N"
    while True:
        value = input(f"? {label} [{default_label}]: ").strip().lower()
        if not value:
            return default
        if value in {"y", "yes"}:
            return True
        if value in {"n", "no"}:
            return False
        print("  Enter y or n.")


def prompt_integrations(default: list[str]) -> list[str]:
    print("? Agent integrations")
    for index, key in enumerate(INTEGRATION_ORDER, start=1):
        integration = INTEGRATIONS[key]
        marker = " (default)" if key in default else ""
        print(f"  {index}. {key} - {integration.label}{marker}")
    print("  Enter names or numbers separated by commas, or 'all'.")

    while True:
        raw = input(f"  Selection [{', '.join(default)}]: ")
        try:
            return parse_integration_selection(raw, default=default)
        except CliError as exc:
            print(f"  {exc}")


def should_prompt_init(args: argparse.Namespace) -> bool:
    if args.yes:
        return False
    if args.interactive:
        return True
    return (
        sys.stdin.isatty()
        and args.target is None
        and args.integration is None
        and args.docs_dir == "docs"
        and args.style == "atlas"
        and not args.force
    )


def collect_interactive_init_args(args: argparse.Namespace) -> None:
    if not sys.stdin.isatty():
        raise CliError("--interactive requires an interactive terminal")

    print("living-docs init")
    args.target = prompt_text("Target project", args.target or ".")
    args.docs_dir = prompt_text("Docs directory", args.docs_dir)
    args.integration = prompt_integrations(args.integration or ["codex"])
    args.style = prompt_text("Style", args.style)
    if args.style not in STYLE_NAMES:
        raise CliError(
            "unknown style: " + args.style + f". Available: {', '.join(STYLE_NAMES)}"
        )
    args.force = prompt_bool("Overwrite existing managed files if needed?", args.force)
    print()


def skill_lines(integration: Integration) -> str:
    names = [
        ("living-docs-write", "route general documentation requests"),
        ("living-docs-architecture", "document current architecture"),
        ("living-docs-change", "record shipped changes"),
        ("living-docs-plan", "draft future plans"),
        ("living-docs-glossary", "regenerate glossary"),
        ("living-docs-check", "validate documentation health"),
    ]
    lines: list[str] = []
    for name, purpose in names:
        if integration.invocation_prefix:
            lines.append(f"- `{integration.invocation_prefix}{name}` to {purpose}")
        else:
            lines.append(f"- `{integration.skills_dir}/{name}/SKILL.md` to {purpose}")
    return "\n".join(lines)


def context_block(*, docs_dir: str, integration: Integration) -> str:
    return f"""{CONTEXT_START}
This project uses living-docs for its documentation system.

Documentation system:
- Framework: Fumadocs + MDX
- Docs app: `{docs_dir}/`
- Content source: `{docs_dir}/content/docs/`
- Project config: `.living-docs/config.json`
- Managed scripts: `.living-docs/scripts/`
- Workflow skill files: `{integration.skills_dir}/living-docs-*/SKILL.md`

Use living-docs skills when the user asks to create or update project documentation:
{skill_lines(integration)}

Keep MDX as the source of truth. Do not hand-edit generated HTML output.
Run `node .living-docs/scripts/check.mjs` or `living-docs check` before treating docs work as complete.
{CONTEXT_END}
"""


def upsert_context_file(project_root: Path, rel_path: str, block: str, *, preamble: str = "") -> Path:
    path = project_root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        original = path.read_text()
    else:
        original = preamble

    pattern = re.compile(
        re.escape(CONTEXT_START) + r".*?" + re.escape(CONTEXT_END) + r"\n?",
        re.S,
    )
    if pattern.search(original):
        updated = pattern.sub(block, original)
    else:
        prefix = "" if not original.strip() else original.rstrip() + "\n\n"
        updated = prefix + block
    path.write_text(updated)
    return path


def init_project(args: argparse.Namespace) -> int:
    if should_prompt_init(args):
        collect_interactive_init_args(args)

    if args.framework != "fumadocs":
        raise CliError("only --framework fumadocs is currently supported")

    target_arg = args.target or "."
    target = Path(target_arg).expanduser()
    if target_arg == ".":
        target = Path.cwd()
    target = target.resolve()
    if target.exists() and not target.is_dir():
        raise CliError(f"target exists but is not a directory: {target}")
    target.mkdir(parents=True, exist_ok=True)

    integrations = args.integration or ["codex"]
    unknown = [name for name in integrations if name not in INTEGRATIONS]
    if unknown:
        raise CliError(
            "unknown integration(s): "
            + ", ".join(unknown)
            + f". Available: {', '.join(INTEGRATION_ORDER)}"
        )

    docs_dir = args.docs_dir.strip().strip("/")
    if not docs_dir or docs_dir.startswith("..") or "/.." in docs_dir:
        raise CliError("--docs-dir must be a project-relative directory")

    variables = {
        "PROJECT_NAME": project_name(target),
        "DOCS_DIR": docs_dir,
        "TODAY": date.today().isoformat(),
        "LIVING_DOCS_VERSION": VERSION,
    }

    starter_src = ASSETS_DIR / "fumadocs-starter"
    project_src = ASSETS_DIR / "project"
    style_src = ASSETS_DIR / "styles" / f"{args.style}.css"
    if not style_src.is_file():
        raise CliError(f"style preset not found: {args.style}")

    written: list[Path] = []
    written += copy_asset_tree(
        starter_src,
        target / docs_dir,
        variables=variables,
        force=args.force,
    )
    written += copy_asset_tree(
        project_src,
        target,
        variables=variables,
        force=args.force,
    )

    style_dst = target / docs_dir / "app" / "global.css"
    style_dst.write_text(render_text(style_src.read_text(), variables))
    written.append(style_dst)

    config = {
        "version": VERSION,
        "framework": "fumadocs",
        "style": args.style,
        "docsRoot": docs_dir,
        "contentDir": f"{docs_dir}/content/docs",
        "defaultLanguage": "match-user",
        "integrations": integrations,
        "createdAt": date.today().isoformat(),
    }
    write_json(target / ".living-docs" / "config.json", config, force=args.force)

    skill_src = ASSETS_DIR / "workflow-skills"
    installed_skill_dirs: set[str] = set()
    for integration_name in integrations:
        integration = INTEGRATIONS[integration_name]
        if integration.skills_dir not in installed_skill_dirs:
            written += copy_asset_tree(
                skill_src,
                target / integration.skills_dir,
                variables=variables,
                force=args.force,
            )
            installed_skill_dirs.add(integration.skills_dir)
        written.append(
            upsert_context_file(
                target,
                integration.context_file,
                context_block(docs_dir=docs_dir, integration=integration),
                preamble=integration.context_preamble,
            )
        )

    rel_written = [str(path.relative_to(target)) for path in written]
    print(f"living-docs {VERSION}")
    print(f"Initialized Fumadocs documentation system in {target}")
    print(f"Docs app: {docs_dir}/")
    print(f"Style preset: {args.style}")
    print(f"Managed config: .living-docs/config.json")
    print(f"Installed integrations: {', '.join(integrations)}")
    print(f"Files written: {len(rel_written) + 1}")
    print()
    print("Next steps:")
    print(f"  1. cd {target}")
    print(f"  2. cd {docs_dir} && npm install && npm run dev -- --port 3333")
    print("  3. living-docs skills")
    for integration_name in integrations:
        print(f"  - {INTEGRATIONS[integration_name].next_step}")
    print("  - Run `living-docs check` or `node .living-docs/scripts/check.mjs` before committing docs changes.")
    return 0


def find_project_root(start: Path) -> Path:
    current = start.resolve()
    for candidate in [current, *current.parents]:
        if (candidate / ".living-docs" / "config.json").is_file():
            return candidate
    return current


def load_config(root: Path) -> dict:
    path = root / ".living-docs" / "config.json"
    if not path.is_file():
        raise CliError("not a living-docs project: missing .living-docs/config.json")
    return json.loads(path.read_text())


def extract_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    data: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if not line.strip() or line.startswith(" ") or line.startswith("-"):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def check_project(args: argparse.Namespace) -> int:
    root = find_project_root(Path.cwd())
    config = load_config(root)
    content_dir = root / config.get("contentDir", "docs/content/docs")
    docs_root = root / config.get("docsRoot", "docs")
    errors: list[str] = []

    if not docs_root.is_dir():
        errors.append(f"docs root missing: {docs_root.relative_to(root)}")
    if not content_dir.is_dir():
        errors.append(f"content directory missing: {content_dir.relative_to(root)}")

    mdx_files = sorted(content_dir.rglob("*.mdx")) if content_dir.is_dir() else []
    if not mdx_files:
        errors.append("no MDX files found")

    for file in mdx_files:
        rel = file.relative_to(root)
        text = file.read_text()
        frontmatter = extract_frontmatter(text)
        if not frontmatter.get("title"):
            errors.append(f"{rel}: missing frontmatter title")

        doc_type = frontmatter.get("type")
        if "/changes/" in rel.as_posix() and doc_type != "change":
            errors.append(f"{rel}: changes pages must set type: change")
        if "/plans/" in rel.as_posix() and doc_type != "plan":
            errors.append(f"{rel}: plan pages must set type: plan")
        if file.name == "architecture.mdx" and doc_type not in {"architecture", ""}:
            errors.append(f"{rel}: architecture pages should set type: architecture")

        if doc_type in {"architecture", "change"}:
            has_component_diagram = any(
                marker in text
                for marker in ("<ArchMap", "<FlowSteps", "<StateFlow", "```mermaid")
            )
            if not has_component_diagram:
                errors.append(
                    f"{rel}: architecture/change docs need <ArchMap />, <FlowSteps />, "
                    "<StateFlow />, or a mermaid block"
                )

        if doc_type in {"architecture", "change", "plan"}:
            if "terms:" not in text and "<TermGrid" not in text:
                errors.append(f"{rel}: managed docs should define terms or render <TermGrid />")

    glossary = content_dir / "glossary.mdx"
    if not glossary.is_file():
        errors.append("missing generated glossary: run node .living-docs/scripts/glossary.mjs")

    if errors:
        print(f"living-docs check failed ({len(errors)} issue(s))")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(f"living-docs check passed ({len(mdx_files)} MDX file(s))")
    return 0


def version_command(_: argparse.Namespace) -> int:
    print(f"living-docs {VERSION}")
    return 0


def skills_command(_: argparse.Namespace) -> int:
    root = find_project_root(Path.cwd())
    is_project = (root / ".living-docs" / "config.json").is_file()
    config: dict = {}
    if is_project:
        config = load_config(root)

    docs_root = config.get("docsRoot", "docs")
    style = config.get("style", "atlas")
    integrations = config.get("integrations", sorted(INTEGRATIONS))

    print("living-docs skills")
    print()
    print("CLI:")
    print("  living-docs init")
    print("  living-docs init [target] --integration codex --integration claude")
    print("  living-docs init . --integration codex --integration cursor --integration gemini")
    print("  living-docs init . --docs-dir docs --style atlas --yes")
    print("  living-docs init . --style atlas --interactive")
    print("  living-docs check")
    print("  living-docs skills")
    print("  living-docs styles")
    print("  living-docs version")
    print("  living-docs self check")
    print(f"  current style: {style}")
    print("  available integrations: " + ", ".join(sorted(INTEGRATIONS)))
    print()
    print("Docs app:")
    print(f"  cd {docs_root}")
    print("  npm install")
    print("  npm run dev -- --port 3333")
    print("  npm run typecheck")
    print("  npm run build")
    print()
    print("Project scripts:")
    print('  node .living-docs/scripts/create-doc.mjs architecture <domain> <slug> "<Title>"')
    print('  node .living-docs/scripts/create-doc.mjs change <domain> <slug> "<Title>"')
    print('  node .living-docs/scripts/create-doc.mjs plan <domain> <slug> "<Title>"')
    print("  node .living-docs/scripts/glossary.mjs")
    print("  node .living-docs/scripts/check.mjs")
    print()
    print("Agent integrations:")
    for integration_name in integrations:
        integration = INTEGRATIONS.get(integration_name)
        if not integration:
            continue
        print(f"  {integration.label} ({integration.skills_dir}):")
        for name in [
            "living-docs-write",
            "living-docs-architecture",
            "living-docs-change",
            "living-docs-plan",
            "living-docs-glossary",
            "living-docs-check",
        ]:
            if integration.invocation_prefix:
                print(f"    {integration.invocation_prefix}{name}")
            else:
                print(f"    {integration.skills_dir}/{name}/SKILL.md")
    return 0


def styles_command(_: argparse.Namespace) -> int:
    print("living-docs styles")
    print()
    print("  atlas  product documentation with clear hierarchy")
    print()
    print("Use:")
    print("  living-docs init")
    print("  living-docs init . --style atlas --interactive")
    print("  living-docs init . --style atlas --yes")
    return 0


def self_check(_: argparse.Namespace) -> int:
    print(f"living-docs {VERSION}")
    print(f"assets: {ASSETS_DIR}")
    missing = [
        path
        for path in [
            ASSETS_DIR / "fumadocs-starter",
            ASSETS_DIR / "project",
            ASSETS_DIR / "styles",
            ASSETS_DIR / "workflow-skills",
        ]
        if not path.exists()
    ]
    if missing:
        print("missing bundled assets:")
        for path in missing:
            print(f"  - {path}")
        return 1
    print("self check passed")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="living-docs",
        description="Bootstrap and maintain a Fumadocs MDX documentation system.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="initialize a Fumadocs documentation system")
    init.add_argument("target", nargs="?", default=None, help="project directory or '.'")
    init.add_argument("--framework", default="fumadocs", choices=["fumadocs"])
    init.add_argument(
        "--integration",
        action="append",
        choices=sorted(INTEGRATIONS),
        help="agent integration to install; repeat for multiple integrations",
    )
    init.add_argument("--docs-dir", default="docs", help="project-relative docs app directory")
    init.add_argument("--style", default="atlas", choices=STYLE_NAMES, help="visual style preset")
    init.add_argument("--force", action="store_true", help="overwrite managed files")
    init.add_argument("--interactive", action="store_true", help="prompt for init options")
    init.add_argument("-y", "--yes", action="store_true", help="accept defaults and skip prompts")
    init.set_defaults(func=init_project)

    check = sub.add_parser("check", help="validate a living-docs project")
    check.set_defaults(func=check_project)

    skills = sub.add_parser("skills", help="print installed skill names and supporting CLI/script actions")
    skills.set_defaults(func=skills_command)

    styles = sub.add_parser("styles", help="list visual style presets")
    styles.set_defaults(func=styles_command)

    version = sub.add_parser("version", help="print version")
    version.set_defaults(func=version_command)

    self_parser = sub.add_parser("self", help="manage the living-docs CLI")
    self_sub = self_parser.add_subparsers(dest="self_command", required=True)
    self_check_parser = self_sub.add_parser("check", help="validate bundled CLI assets")
    self_check_parser.set_defaults(func=self_check)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except CliError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
