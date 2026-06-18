---
name: living-docs-architecture
description: Create or update architecture MDX pages in a living-docs Fumadocs project. Use whenever current architecture, system shape, subsystem boundaries, data flow, runtime chain, contracts, ownership, or architecture diagrams need documentation or correction.
---

# living-docs-architecture

Use this skill only inside a project that has `.living-docs/config.json`. If that file is missing, tell the user to run `living-docs init` first.

Architecture pages describe current runtime truth. They should not become historical changelogs or future plans.

## Source Priority

1. `.living-docs/config.json` for docs location and project settings.
2. Existing MDX pages under the configured `contentDir`.
3. Source files, routes, schemas, config, tests, logs, traces, or rendered runtime surfaces that prove the current shape.
4. User-provided context, marked as unverified when it has not been checked against the repo or runtime.

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

## Write Safety

- Do not document aspirational behavior as current architecture.
- If the current shape differs from an existing page, update the architecture page and consider whether a separate change record is needed.
- If a diagram would be speculative, write the uncertainty explicitly or inspect more code before adding it.

Report the architecture page path, key source files or runtime evidence used, and validation result.
