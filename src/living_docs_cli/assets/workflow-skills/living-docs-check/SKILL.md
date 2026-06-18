---
name: living-docs-check
description: Validate a living-docs Fumadocs project. Use before committing docs changes, after generated docs or glossary files change, or whenever the user asks whether the documentation system, MDX content, glossary, or living-docs setup is healthy.
---

# living-docs-check

Use this skill only inside a project that has `.living-docs/config.json`. If that file is missing, report that this is not initialized as a living-docs project.

## Validation Order

Run the local validation gate first because it is always project-local:

```bash
node .living-docs/scripts/check.mjs
```

If the global CLI is installed, also run:

```bash
living-docs check
```

For docs-app changes, run the Fumadocs/TypeScript checks when dependencies are installed:

```bash
cd docs
npm run typecheck
npm run build
```

Fix failures only if the user asked for fixes or the failure is caused by documentation changes you just made. Report the exact failing files, skipped checks with reasons, and final result.
