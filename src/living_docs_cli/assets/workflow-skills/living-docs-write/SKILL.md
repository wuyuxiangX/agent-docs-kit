---
name: living-docs-write
description: General entrypoint for creating or updating living-docs MDX documentation in a project initialized with living-docs. Use whenever the user asks to write docs, update docs, create a Project Atlas, explain current architecture, map a repo, record a shipped change, draft a future plan, refresh glossary terms, validate docs health, or maintain the generated Fumadocs documentation system.
---

# living-docs-write

Use this skill only inside a project that has `.living-docs/config.json`. If that file is missing, tell the user to run `living-docs init` before writing living-docs content.

This is the portable entrypoint for agents that do not have native slash or skill invocation. For Codex, Claude Code, and similar skill-aware agents, route to the named living-docs skill directly when it is available. For Cursor, Gemini CLI, Copilot, or generic agents, read the matching `SKILL.md` file from the installed workflow directory before editing docs.

## Routine

1. Read `.living-docs/config.json`.
2. Inspect existing docs under the configured `contentDir`.
3. Choose the specific workflow:
   - Project overview, repo map, onboarding map, architecture/current system shape: use `living-docs-architecture`.
   - Shipped behavior or implementation change: use `living-docs-change`.
   - Future direction or blueprint: use `living-docs-plan`.
   - Terms changed: use `living-docs-glossary`.
   - Validation only: use `living-docs-check`.
4. Keep MDX as the source of truth. Do not edit generated HTML output.
5. Prefer built-in MDX components for common diagrams:
   - `<SystemMap />`, `<LayerMap />`, `<FlowMap />`, and `<RoadmapMap />` for Project Atlas pages.
   - `<ArchMap />` for architecture layers.
   - `<FlowSteps />` for runtime or behavior flows.
   - `<StateFlow />` for state transitions.
   - `<TermGrid />` for page-local vocabulary.
6. Match the language and tone of the existing docs unless the user asks otherwise.

## Write Safety

- Do not invent architecture or verification details. Inspect source files, diffs, tests, logs, or the runtime surface first.
- Do not create a page for every feature by default. For broad project understanding, update the Project Atlas before adding narrower pages.
- Do not overwrite an existing MDX page unless the user asked to update that page or the selected workflow clearly targets it.
- Keep historical facts in change records, current facts in architecture pages, and future intent in plan pages.
- If the request mixes shipped facts and future intent, create or update separate change and plan pages instead of blending them.

## Finish Gate

Run one of:

```bash
node .living-docs/scripts/check.mjs
living-docs check
```

Report the changed MDX files and the validation result.
