---
name: living-docs-plan
description: Create or update future plans, blueprints, and design direction MDX pages in a living-docs Fumadocs project. Use when documenting intended work before it ships.
---

# living-docs-plan

Use this skill only inside a project that has `.living-docs/config.json`.

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

Report the plan page path and validation result.
