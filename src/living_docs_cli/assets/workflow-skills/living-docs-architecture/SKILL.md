---
name: living-docs-architecture
description: Create or update architecture MDX pages in a living-docs Fumadocs project. Use when current architecture, system shape, subsystem boundaries, data flow, runtime chain, or architecture diagrams need documentation.
---

# living-docs-architecture

Use this skill only inside a project that has `.living-docs/config.json`.

## Workflow

1. Read `.living-docs/config.json` and inspect the configured `contentDir`.
2. Identify the target domain. Use `system` for cross-domain architecture.
3. If the domain architecture page does not exist, create it:

```bash
node .living-docs/scripts/create-doc.mjs architecture <domain> <domain> "<Title>"
```

4. Edit the MDX page to reflect current runtime truth:
   - entry points
   - core modules/components
   - data stores or external services
   - contracts and ownership boundaries
   - known constraints
5. Include at least one diagram component:
   - Use `<ArchMap />` for subsystem layers and ownership boundaries.
   - Use `<FlowSteps />` for runtime request/job/event paths.
   - Use `<StateFlow />` for lifecycle or state transitions.
   - Use mermaid only for complex graphs, branches, sequence diagrams, or diagrams that do not fit the built-in components.
6. Keep history out of architecture pages; history belongs in change records.
7. Add or update frontmatter `terms`.
8. Run:

```bash
node .living-docs/scripts/glossary.mjs
node .living-docs/scripts/check.mjs
```

Report the architecture page path and validation result.
