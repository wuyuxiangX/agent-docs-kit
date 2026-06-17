---
name: living-docs-write
description: General entrypoint for creating or updating living-docs MDX documentation in a project initialized with living-docs. Use when the user asks to write docs, update docs, explain an architecture, record a change, draft a plan, or maintain the Fumadocs documentation system.
---

# living-docs-write

Use this skill only inside a project that has `.living-docs/config.json`.

## Routine

1. Read `.living-docs/config.json`.
2. Inspect existing docs under the configured `contentDir`.
3. Choose the specific workflow:
   - Architecture/current system shape: use `living-docs-architecture`.
   - Shipped behavior or implementation change: use `living-docs-change`.
   - Future direction or blueprint: use `living-docs-plan`.
   - Terms changed: use `living-docs-glossary`.
   - Validation only: use `living-docs-check`.
4. Keep MDX as the source of truth. Do not edit generated HTML output.
5. Prefer built-in MDX components for common diagrams:
   - `<ArchMap />` for architecture layers.
   - `<FlowSteps />` for runtime or behavior flows.
   - `<StateFlow />` for state transitions.
   - `<TermGrid />` for page-local vocabulary.
6. Match the language and tone of the existing docs unless the user asks otherwise.

## Required Finish

Run one of:

```bash
node .living-docs/scripts/check.mjs
living-docs check
```

Report the changed MDX files and the validation result.
