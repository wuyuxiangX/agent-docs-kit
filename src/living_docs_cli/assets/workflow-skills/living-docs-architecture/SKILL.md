---
name: living-docs-architecture
description: Create or update Project Atlas and architecture MDX pages in a living-docs Fumadocs project. Use whenever the user asks for a project overview, architecture map, system shape, subsystem boundaries, data flow, runtime chain, contracts, ownership, onboarding map, refactor context, or architecture diagrams.
---

# living-docs-architecture

Use this skill only inside a project that has `.living-docs/config.json`. If that file is missing, tell the user to run `living-docs init` first.

Architecture pages describe current runtime truth. The Project Atlas is the
project-level map: modules, layers, core flows, and architecture direction. It
should stay broad and should not become feature-by-feature documentation.

## Source Priority

1. `.living-docs/config.json` for docs location and project settings.
2. Existing MDX pages under the configured `contentDir`.
3. Source files, routes, schemas, config, tests, logs, traces, or rendered runtime surfaces that prove the current shape.
4. User-provided context, marked as unverified when it has not been checked against the repo or runtime.

## Workflow

1. Read `.living-docs/config.json` and inspect the configured `contentDir`.
2. Identify the target level:
   - Use `Project Atlas` for broad project overviews, onboarding maps, refactor context, or "how this project is structured" requests.
   - Use a domain architecture page when the user asks about one subsystem.
3. If the user needs a Project Atlas draft, preview it first:

```bash
living-docs atlas --stdout
```

If the existing `atlas.mdx` is still the starter page or the user asked to
replace it, write the scanned draft:

```bash
living-docs atlas --force
```

If the CLI is unavailable and `atlas.mdx` does not exist, use:

```bash
node .living-docs/scripts/create-doc.mjs atlas system project-atlas "Project Atlas"
```

4. If a domain architecture page does not exist, create it:

```bash
node .living-docs/scripts/create-doc.mjs architecture <domain> <domain> "<Title>"
```

5. Edit the MDX page to reflect current runtime truth:
   - project-level modules and layers
   - entry points
   - core flows
   - storage, provider, or deployment boundaries
   - contracts and ownership boundaries
   - known constraints or structural risks
6. Include at least one diagram component:
   - Use `<SystemMap />` for the Project Atlas module map.
   - Use `<LayerMap />` for repo, runtime, or ownership layers.
   - Use `<FlowMap />` for project-level request/job/data paths.
   - Use `<RoadmapMap />` for compact architecture direction.
   - Use `<ArchMap />` for subsystem layers and ownership boundaries.
   - Use `<FlowSteps />` for runtime request/job/event paths.
   - Use `<StateFlow />` for lifecycle or state transitions.
   - Use mermaid only for complex graphs, branches, sequence diagrams, or diagrams that do not fit the built-in components.
7. Keep history out of architecture pages; history belongs in change records.
8. Add or update frontmatter `terms`.
9. Run:

```bash
node .living-docs/scripts/glossary.mjs
node .living-docs/scripts/check.mjs
```

## Write Safety

- Do not document aspirational behavior as current architecture.
- Do not create one page per feature by default. Prefer a broad Project Atlas plus domain pages only where they clarify the system shape.
- If the current shape differs from an existing page, update the architecture page and consider whether a separate change record is needed.
- If a diagram would be speculative, write the uncertainty explicitly or inspect more code before adding it.

Report the architecture page path, key source files or runtime evidence used, and validation result.
