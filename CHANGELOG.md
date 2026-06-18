# Changelog

## 2.1.0

- Added interactive `living-docs init` prompts for target project, docs directory, agent integrations, style, and overwrite behavior.
- Added `--interactive` and `--yes` flags so humans can choose options while scripts can stay non-interactive.
- Renamed the public distribution and repository identity to `agent-docs-kit` because `living-docs` is blocked by PyPI's project-name similarity checks. The `living-docs` CLI command remains available.
- Clarified the split between the Python bootstrap CLI and the generated Node/Fumadocs docs app.

## 2.0.0

Major architecture shift from direct HTML generation to a generic documentation system.

- Added a Python CLI package with `living-docs init`, `living-docs check`, `living-docs version`, and `living-docs self check`.
- Added a Fumadocs + MDX starter app generated under `docs/`.
- Added project-local `.living-docs/` config, MDX templates, and Node scripts for doc creation, glossary generation, and validation.
- Added generated agent skills for architecture docs, change records, plans, glossary refresh, and docs checks.
- Added managed context blocks for `AGENTS.md`, `CLAUDE.md`, Copilot instructions, Cursor project rules, `GEMINI.md`, and generic agent context.
- Removed the root global helper skill and `setup` installer; `living-docs init` is the bootstrap path.
- Removed the old hand-authored HTML documentation path from the main skill.

## 1.1.0

Legacy HTML script reorganization.

## 1.0.0

Initial HTML living-docs prototype.
