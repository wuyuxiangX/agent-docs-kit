---
name: living-docs-change
description: Record shipped changes in a living-docs Fumadocs project. Use after refactors, features, contract changes, architecture changes, or operational fixes that need an immutable paper trail.
---

# living-docs-change

Use this skill only inside a project that has `.living-docs/config.json`.

## Workflow

1. Read `.living-docs/config.json`.
2. Inspect the relevant source diff, tests, logs, or runtime surface before writing.
3. Choose a domain and short topic slug.
4. Create a change record:

```bash
node .living-docs/scripts/create-doc.mjs change <domain> <topic-slug> "<Title>"
```

Optional metadata:

```bash
LIVING_DOCS_SOURCE="commit/diff/runtime source" LIVING_DOCS_TESTS="test or verification summary" node .living-docs/scripts/create-doc.mjs change <domain> <topic-slug> "<Title>"
```

5. Fill the MDX page:
   - what changed
   - why it changed
   - important trade-offs
   - verification performed
   - user-visible or system-visible behavior
6. Include at least one diagram component:
   - Use `<FlowSteps />` for before/change/after behavior.
   - Use `<StateFlow />` when the change affects lifecycle states.
   - Use `<ArchMap />` when the current architecture shape changed.
   - Use mermaid only for complex graphs, branches, or sequence diagrams.
7. Update the relevant architecture page if the current shape changed.
8. Add/update frontmatter `terms`.
9. Run:

```bash
node .living-docs/scripts/glossary.mjs
node .living-docs/scripts/check.mjs
```

Report the change page, any architecture page touched, and validation result.
