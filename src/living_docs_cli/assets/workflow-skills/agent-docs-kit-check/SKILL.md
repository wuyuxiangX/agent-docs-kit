---
name: agent-docs-kit-check
description: Validate an agent-docs-kit Fumadocs project. Use before committing docs changes, after generated docs or glossary files change, or whenever the user asks whether the documentation system, MDX content, glossary, or agent-docs-kit setup is healthy.
---

# agent-docs-kit-check

Use this skill only inside a project that has `.agent-docs-kit/config.json`. If that file is missing, report that this is not initialized as an agent-docs-kit project.

## Validation Order

Run the validation gate:

```bash
uvx agent-docs-kit check
```

For docs-app changes, run the Fumadocs/TypeScript checks when dependencies are installed:

```bash
cd docs
npm run typecheck
npm run build
```

Fix failures only if the user asked for fixes or the failure is caused by documentation changes you just made. Report the exact failing files, skipped checks with reasons, and final result.
