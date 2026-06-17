---
name: living-docs-check
description: Validate a living-docs Fumadocs project. Use before committing docs changes or when the user asks whether the documentation system is healthy.
---

# living-docs-check

Use this skill only inside a project that has `.living-docs/config.json`.

Run the local validation gate:

```bash
node .living-docs/scripts/check.mjs
```

If the global CLI is installed, also run:

```bash
living-docs check
```

Fix failures only if the user asked for fixes or the failure is caused by documentation changes you just made. Report the exact failing files and final result.
