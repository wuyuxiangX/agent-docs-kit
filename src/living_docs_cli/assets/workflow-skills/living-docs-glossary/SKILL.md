---
name: living-docs-glossary
description: Regenerate and review the glossary in a living-docs Fumadocs project. Use when MDX frontmatter terms were added, changed, or need consistency cleanup.
---

# living-docs-glossary

Use this skill only inside a project that has `.living-docs/config.json`.

## Workflow

1. Read `.living-docs/config.json`.
2. Inspect frontmatter `terms` in the relevant MDX files.
3. Normalize duplicate terms only when they clearly mean the same project concept.
4. Run:

```bash
node .living-docs/scripts/glossary.mjs
node .living-docs/scripts/check.mjs
```

5. If the generated glossary looks wrong, fix source page frontmatter rather than hand-editing `glossary.mdx`.

Report the generated glossary path and validation result.
