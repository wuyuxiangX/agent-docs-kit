# Changelog

## 2.2.2

- Removed the legacy compatibility console entry point so installs expose only the `agent-docs-kit` command.
- Renamed generated project paths and workflow skill names to `.agent-docs-kit/` and `agent-docs-kit-*`.
- Cleaned README, starter docs, init output, and skills help so user-facing workflows use top-level `agent-docs-kit` commands instead of internal Node scripts.

## 2.2.1

- Replaced the integration prompt with a terminal multi-select UI: Up/Down or `j`/`k` moves, Space toggles, `a` selects all, and Enter confirms.
- Improved the text fallback parser for compact numeric selections such as `12`, spaced selections such as `1 2`, and normalized terminal input.
- Updated init next steps and generated agent context to prefer `uvx agent-docs-kit ...` commands so one-time `uvx` users do not hit `agent-docs-kit: command not found`.

## 2.2.0

- Added Project Atlas as the primary project-level architecture map.
- Added `agent-docs-kit atlas` to generate an editable Atlas MDX draft from repository structure.
- Added Atlas-oriented MDX components: `SystemMap`, `LayerMap`, `FlowMap`, and `RoadmapMap`.
- Added Atlas starter content, template support, and validation rules for the new map components.
- Updated architecture workflow guidance to prefer broad project maps over feature-by-feature docs sprawl.
- Added `agent-docs-kit web` to install docs dependencies when needed and start the local Fumadocs site on an available port.
- Added a generated docs app `postcss` override for the audited safe version used by Next.js.

## 2.1.0

- Added interactive `agent-docs-kit init` prompts for target project, docs directory, agent integrations, style, and overwrite behavior.
- Added `--interactive` and `--yes` flags so humans can choose options while scripts can stay non-interactive.
- Renamed the public distribution and repository identity to `agent-docs-kit` after PyPI project-name similarity checks blocked the earlier name.
- Clarified the split between the Python bootstrap CLI and the generated Node/Fumadocs docs app.

## 2.0.0

Major architecture shift from direct HTML generation to a generic documentation system.

- Added a Python CLI package with `agent-docs-kit init`, `agent-docs-kit check`, `agent-docs-kit version`, and `agent-docs-kit self check`.
- Added a Fumadocs + MDX starter app generated under `docs/`.
- Added project-local `.agent-docs-kit/` config, MDX templates, and Node scripts for doc creation, glossary generation, and validation.
- Added generated agent skills for architecture docs, change records, plans, glossary refresh, and docs checks.
- Added managed context blocks for `AGENTS.md`, `CLAUDE.md`, Copilot instructions, Cursor project rules, `GEMINI.md`, and generic agent context.
- Removed the root global helper skill and `setup` installer; `agent-docs-kit init` is the bootstrap path.
- Removed the old hand-authored HTML documentation path from the main skill.

## 1.1.0

Legacy HTML script reorganization.

## 1.0.0

Initial HTML agent-docs-kit prototype.
