from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import webbrowser
from dataclasses import dataclass
from datetime import date
from pathlib import Path

VERSION = "2.2.0"
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
ATLAS_IGNORED_DIRS = {
    ".git",
    ".next",
    ".turbo",
    ".venv",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "target",
}
ATLAS_MANIFEST_NAMES = {
    "package.json",
    "pyproject.toml",
    "Cargo.toml",
    "go.mod",
    "pom.xml",
    "build.gradle",
    "composer.json",
    "Gemfile",
}
ATLAS_CONFIG_NAMES = {
    "Dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    "next.config.js",
    "next.config.mjs",
    "next.config.ts",
    "vite.config.js",
    "vite.config.ts",
    "tsconfig.json",
    "tailwind.config.js",
    "tailwind.config.ts",
}
ATLAS_LAYER_HINTS = (
    (
        "User and agent surfaces",
        {"app", "apps", "web", "frontend", "pages", "components", "public", ".agents", ".claude", ".cursor"},
        "User-facing routes, UI shells, or agent instruction surfaces.",
        "blue",
    ),
    (
        "Application and domain code",
        {"src", "lib", "packages", "server", "backend", "api", "routes", "services", "modules"},
        "Core implementation boundaries and domain logic.",
        "green",
    ),
    (
        "Data and integration boundaries",
        {"db", "database", "migrations", "models", "schemas", "prisma", "graphql", "openapi"},
        "Persistence, schemas, external contracts, or generated API surfaces.",
        "amber",
    ),
    (
        "Delivery and knowledge system",
        {"docs", ".github", ".living-docs", "scripts", "deploy", "infra", "ops"},
        "Documentation, automation, deployment, and operating knowledge.",
        "violet",
    ),
)


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
        ("living-docs-architecture", "document current architecture and Project Atlas maps"),
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
Use `living-docs atlas --force` to replace the starter Project Atlas with a repository-structure draft.
Use `living-docs skills` to list available workflows and `living-docs web` to preview the docs site locally.
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
    print("  2. living-docs web")
    print("  3. living-docs atlas --force")
    print("  4. living-docs skills")
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


def mdx_string(value: str) -> str:
    compact = re.sub(r"\s+", " ", value.strip())
    return "'" + compact.replace("\\", "\\\\").replace("'", "\\'") + "'"


def yaml_string(value: str) -> str:
    return json.dumps(value)


def mdx_array(values: list[str], *, indent: str = "      ") -> str:
    if not values:
        return ""
    return "\n".join(f"{indent}{mdx_string(value)}," for value in values)


def rel_path(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def is_atlas_ignored_dir(path: Path) -> bool:
    return path.name in ATLAS_IGNORED_DIRS


def walk_atlas_paths(root: Path, *, max_depth: int) -> tuple[list[Path], list[Path]]:
    dirs: list[Path] = []
    files: list[Path] = []
    for current, dirnames, filenames in os.walk(root):
        current_path = Path(current)
        try:
            rel_parts = current_path.relative_to(root).parts
        except ValueError:
            continue

        dirnames[:] = sorted(
            name
            for name in dirnames
            if name not in ATLAS_IGNORED_DIRS and not (name.startswith(".") and name not in {".github", ".living-docs", ".agents", ".claude", ".cursor"})
        )

        if len(rel_parts) > max_depth:
            dirnames[:] = []
            continue

        for dirname in dirnames:
            path = current_path / dirname
            if len(path.relative_to(root).parts) <= max_depth:
                dirs.append(path)

        for filename in sorted(filenames):
            path = current_path / filename
            if len(path.relative_to(root).parts) <= max_depth:
                files.append(path)

    return sorted(dirs), sorted(files)


def read_project_display_name(root: Path) -> str:
    package_json = root / "package.json"
    if package_json.is_file():
        try:
            name = json.loads(package_json.read_text()).get("name")
            if isinstance(name, str) and name.strip():
                return name.strip()
        except json.JSONDecodeError:
            pass

    pyproject = root / "pyproject.toml"
    if pyproject.is_file():
        match = re.search(r"(?m)^name\s*=\s*[\"']([^\"']+)[\"']", pyproject.read_text())
        if match:
            return match.group(1).strip()

    return project_name(root)


def describe_manifest(path: Path) -> str:
    name = path.name
    if name == "package.json":
        return "Node package manifest and scripts."
    if name == "pyproject.toml":
        return "Python package metadata and build configuration."
    if name == "Cargo.toml":
        return "Rust package and crate configuration."
    if name == "go.mod":
        return "Go module boundary and dependency root."
    if name in {"pom.xml", "build.gradle"}:
        return "JVM build and dependency configuration."
    if name == "composer.json":
        return "PHP package and dependency manifest."
    if name == "Gemfile":
        return "Ruby dependency manifest."
    return "Project manifest."


def describe_config(path: Path) -> str:
    rel = path.as_posix()
    name = path.name
    if rel.startswith(".github/workflows/"):
        return "GitHub Actions workflow."
    if name.startswith("next.config"):
        return "Next.js runtime/build configuration."
    if name.startswith("vite.config"):
        return "Vite build configuration."
    if name == "tsconfig.json":
        return "TypeScript project boundary."
    if name.startswith("tailwind.config"):
        return "Tailwind design-system configuration."
    if name == "Dockerfile":
        return "Container build boundary."
    if name.startswith("docker-compose"):
        return "Local or deployment service graph."
    return "Project configuration."


def collect_atlas_inventory(root: Path) -> dict[str, list[Path]]:
    dirs, files = walk_atlas_paths(root, max_depth=3)
    manifests = [path for path in files if path.name in ATLAS_MANIFEST_NAMES]
    configs = [
        path
        for path in files
        if path.name in ATLAS_CONFIG_NAMES or rel_path(root, path).startswith(".github/workflows/")
    ]
    return {
        "dirs": dirs,
        "manifests": manifests,
        "configs": configs,
    }


def classify_atlas_layers(root: Path, dirs: list[Path]) -> list[dict[str, object]]:
    remaining = {rel_path(root, path): path for path in dirs if not is_atlas_ignored_dir(path)}
    layers: list[dict[str, object]] = []

    for title, hints, body, tone in ATLAS_LAYER_HINTS:
        matches: list[str] = []
        for rel in sorted(remaining):
            parts = set(rel.split("/"))
            if parts.intersection(hints):
                matches.append(rel)
        if matches:
            layers.append(
                {
                    "title": title,
                    "body": body,
                    "tone": tone,
                    "items": matches[:8],
                }
            )

    if not layers:
        top_level = [rel_path(root, path) for path in dirs if len(path.relative_to(root).parts) == 1]
        layers.append(
            {
                "title": "Project directories",
                "body": "Top-level directories found by the atlas scan.",
                "tone": "blue",
                "items": top_level[:8] or ["TODO: add project modules"],
            }
        )

    return layers


def mdx_items(items: list[tuple[str, str, str | None]], *, indent: str = "    ") -> str:
    lines: list[str] = []
    for title, body, tone in items:
        tone_part = f", tone: {mdx_string(tone)}" if tone else ""
        lines.append(f"{indent}{{ title: {mdx_string(title)}, body: {mdx_string(body)}{tone_part} }},")
    return "\n".join(lines)


def render_project_atlas(root: Path, config: dict) -> str:
    inventory = collect_atlas_inventory(root)
    project = read_project_display_name(root)
    display_project = project.replace("`", "'")
    docs_root = config.get("docsRoot", "docs")
    content_dir = config.get("contentDir", "docs/content/docs")
    today = date.today().isoformat()

    manifest_items = [
        (rel_path(root, path), describe_manifest(path), "blue")
        for path in inventory["manifests"][:8]
    ]
    if not manifest_items:
        manifest_items = [("TODO: manifest", "Add the package or service manifest that defines this project.", "blue")]

    config_items = [
        (rel_path(root, path), describe_config(Path(rel_path(root, path))), "amber")
        for path in inventory["configs"][:8]
    ]
    if not config_items:
        config_items = [("TODO: configuration", "Add build, deploy, or runtime configuration once identified.", "amber")]

    layer_blocks: list[str] = []
    for layer in classify_atlas_layers(root, inventory["dirs"]):
        item_lines = mdx_array(list(layer["items"]), indent="        ")
        layer_blocks.append(
            "    {\n"
            f"      title: {mdx_string(str(layer['title']))},\n"
            f"      body: {mdx_string(str(layer['body']))},\n"
            f"      tone: {mdx_string(str(layer['tone']))},\n"
            "      items: [\n"
            f"{item_lines}\n"
            "      ],\n"
            "    },"
        )

    return f"""---
title: {yaml_string("Project Atlas")}
description: {yaml_string(f"Project-level architecture map for {project}.")}
domain: {yaml_string("system")}
type: {yaml_string("architecture")}
status: {yaml_string("draft")}
date: {yaml_string(today)}
terms:
  - name: "Project Atlas"
    description: "A project-level map of modules, layers, flows, and architecture direction."
  - name: "Module boundary"
    description: "A source, package, service, or ownership boundary visible in the repository."
---

# Project Atlas

This page is a generated architecture draft for `{display_project}`. Treat it as a map
of verified repository signals, then replace TODO text with runtime truth from
source files, tests, logs, traces, or the running product.

<SystemMap
  title="Repository signals"
  nodes={{[
{mdx_items(manifest_items, indent="    ")}
{mdx_items(config_items, indent="    ")}
    {{ title: {mdx_string(docs_root + "/")}, body: {mdx_string("Generated Fumadocs app root.")}, tone: 'violet' }},
    {{ title: {mdx_string(content_dir + "/")}, body: {mdx_string("MDX content source of truth.")}, tone: 'violet' }},
  ]}}
/>

<LayerMap
  title="Project layers"
  layers={{[
{chr(10).join(layer_blocks)}
  ]}}
/>

## Core Flow

Replace this section with the highest-value request, job, agent, or data flow.
Keep it at project level; do not turn this page into feature-by-feature notes.

<FlowMap
  title="Primary runtime path"
  flows={{[
    {{
      title: 'Entry',
      body: 'TODO: identify the user action, API request, CLI command, job, or agent task that enters the system.',
      tone: 'blue',
      steps: ['Input source', 'Validation or routing boundary'],
    }},
    {{
      title: 'Execution',
      body: 'TODO: identify the modules that own orchestration, state changes, and external calls.',
      tone: 'green',
      steps: ['Core module', 'Storage or provider boundary'],
    }},
    {{
      title: 'Output',
      body: 'TODO: identify the response, persisted state, event, or rendered surface.',
      tone: 'amber',
      steps: ['Result', 'Observability or follow-up'],
    }},
  ]}}
/>

## Architecture Direction

Use this as a compact evolution map, not a backlog. Keep only project-level
architecture shifts here.

<RoadmapMap
  items={{[
    {{ title: 'Current shape', body: 'Document what the repo and runtime prove today.', status: 'now', tone: 'green' }},
    {{ title: 'Next structural change', body: 'TODO: describe the next large architecture move, if any.', status: 'next', tone: 'blue' }},
    {{ title: 'Known risk', body: 'TODO: note coupling, missing ownership, or unclear runtime boundaries.', status: 'watch', tone: 'amber' }},
  ]}}
/>

<TermGrid
  items={{[
    {{ name: 'Project Atlas', description: 'A project-level map of modules, layers, flows, and architecture direction.' }},
    {{ name: 'Module boundary', description: 'A source, package, service, or ownership boundary visible in the repository.' }},
  ]}}
/>
"""


def atlas_command(args: argparse.Namespace) -> int:
    start = Path(args.target).expanduser() if args.target else Path.cwd()
    root = find_project_root(start)
    config = load_config(root)
    content_dir = root / config.get("contentDir", "docs/content/docs")
    output = Path(args.output) if args.output else content_dir / "atlas.mdx"
    if not output.is_absolute():
        output = root / output

    content = render_project_atlas(root, config)
    if args.stdout:
        print(content)
        return 0

    if output.exists() and not args.force:
        raise CliError(f"refusing to overwrite existing file without --force: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content)
    print(f"Project Atlas written: {output.relative_to(root)}")
    print("Review TODOs, verify runtime paths, then run `living-docs check`.")
    return 0


def is_port_available(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((host, port))
        except OSError:
            return False
    return True


def find_available_port(host: str, preferred: int) -> int:
    if preferred < 1 or preferred > 65535:
        raise CliError("--port must be between 1 and 65535")

    for port in range(preferred, min(preferred + 200, 65536)):
        if is_port_available(host, port):
            return port
    raise CliError(f"could not find an available port starting at {preferred}")


def web_command(args: argparse.Namespace) -> int:
    start = Path(args.target).expanduser() if args.target else Path.cwd()
    root = find_project_root(start)
    config = load_config(root)
    docs_root = root / config.get("docsRoot", "docs")
    package_json = docs_root / "package.json"
    if not package_json.is_file():
        raise CliError(f"docs app package.json not found: {docs_root.relative_to(root)}")

    npm = shutil.which("npm")
    if not npm:
        raise CliError("npm was not found on PATH; install Node.js/npm to preview the docs site")

    node_modules = docs_root / "node_modules"
    if not node_modules.is_dir():
        if args.no_install:
            raise CliError(
                f"docs dependencies are missing: {node_modules.relative_to(root)}. "
                "Run without --no-install or run npm install in the docs app."
            )
        print(f"Installing docs dependencies in {docs_root.relative_to(root)}...", flush=True)
        completed = subprocess.run([npm, "install"], cwd=docs_root)
        if completed.returncode:
            return completed.returncode

    port = find_available_port(args.host, args.port)
    url_host = "localhost" if args.host in {"127.0.0.1", "0.0.0.0"} else args.host
    url = f"http://{url_host}:{port}"
    if port != args.port:
        print(f"Port {args.port} is busy; using {port}.", flush=True)
    print(f"Starting docs site: {url}", flush=True)
    print("Press Ctrl+C to stop.", flush=True)
    if args.open:
        webbrowser.open(url)

    cmd = [npm, "run", "dev", "--", "--port", str(port)]
    if args.host != "127.0.0.1":
        cmd.extend(["--hostname", args.host])
    try:
        return subprocess.call(cmd, cwd=docs_root)
    except KeyboardInterrupt:
        return 130


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
                for marker in (
                    "<ArchMap",
                    "<FlowSteps",
                    "<StateFlow",
                    "<SystemMap",
                    "<LayerMap",
                    "<FlowMap",
                    "<RoadmapMap",
                    "```mermaid",
                )
            )
            if not has_component_diagram:
                errors.append(
                    f"{rel}: architecture/change docs need an architecture map, flow map, "
                    "state map, roadmap map, or mermaid block"
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
    print("  living-docs web")
    print("  living-docs atlas --force")
    print("  living-docs check")
    print("  living-docs skills")
    print("  living-docs styles")
    print("  living-docs version")
    print("  living-docs self check")
    print(f"  current style: {style}")
    print("  available integrations: " + ", ".join(sorted(INTEGRATIONS)))
    print()
    print("Docs app:")
    print("  living-docs web")
    print(f"  cd {docs_root}")
    print("  npm run typecheck")
    print("  npm run build")
    print()
    print("Project scripts:")
    print('  node .living-docs/scripts/create-doc.mjs architecture <domain> <slug> "<Title>"')
    print('  node .living-docs/scripts/create-doc.mjs atlas system project-atlas "Project Atlas"')
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

    web = sub.add_parser("web", help="install dependencies if needed and start the local docs site")
    web.add_argument("target", nargs="?", default=None, help="living-docs project directory or '.'")
    web.add_argument("--port", type=int, default=3333, help="preferred local port")
    web.add_argument("--host", default="127.0.0.1", help="host passed to the docs dev server")
    web.add_argument("--open", action="store_true", help="open the docs URL in the default browser")
    web.add_argument("--no-install", action="store_true", help="fail instead of running npm install when dependencies are missing")
    web.set_defaults(func=web_command)

    atlas = sub.add_parser("atlas", help="generate a Project Atlas MDX draft from repository structure")
    atlas.add_argument("target", nargs="?", default=None, help="living-docs project directory or '.'")
    atlas.add_argument("--output", default=None, help="project-relative output path; default is docs content atlas.mdx")
    atlas.add_argument("--force", action="store_true", help="overwrite an existing atlas file")
    atlas.add_argument("--stdout", action="store_true", help="print the generated MDX instead of writing a file")
    atlas.set_defaults(func=atlas_command)

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
