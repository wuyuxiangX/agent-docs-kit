---
name: living-docs-plan
description: Create or update future plans, blueprints, design direction, implementation plans, or proposal MDX pages in a living-docs Fumadocs project. Use when documenting intended work before it ships or when the user wants a plan separated from current architecture and shipped change records.
---

# living-docs-plan

Use this skill only inside a project that has `.living-docs/config.json`. If that file is missing, tell the user to run `living-docs init` first.

Plan pages describe future intent. They should be explicit about scope, assumptions, validation, and open questions.

## Source Priority

1. `.living-docs/config.json` for docs location and project settings.
2. Existing architecture and change pages under the configured `contentDir`.
3. Source files, APIs, schemas, config, tests, or runtime surfaces that constrain the proposed work.
4. User-provided goals and constraints.

## Workflow

1. Read `.living-docs/config.json`.
2. Choose the target domain and topic slug.
3. Create a plan page:

```bash
node .living-docs/scripts/create-doc.mjs plan <domain> <topic-slug> "<Title>"
```

4. Fill the plan with:
   - goal
   - scope and non-goals
   - proposed architecture or flow
   - validation plan
   - open questions
5. Use built-in components when a diagram clarifies the plan:
   - `<ArchMap />` for target architecture.
   - `<FlowSteps />` for proposed execution flow.
   - `<StateFlow />` for lifecycle or state transitions.
   - mermaid for complex graphs, branches, or sequence diagrams.
6. Keep shipped facts out of plan pages; when the plan ships, create a change record and update architecture.
7. Add/update frontmatter `terms`.
8. Run:

```bash
node .living-docs/scripts/glossary.mjs
node .living-docs/scripts/check.mjs
```

## Write Safety

- Do not present a plan as current architecture or shipped behavior.
- Keep speculative details clearly labeled as assumptions or open questions.
- If a plan depends on unknown runtime behavior, add a validation task instead of guessing.

Report the plan page path, major assumptions, open questions, and validation result.
