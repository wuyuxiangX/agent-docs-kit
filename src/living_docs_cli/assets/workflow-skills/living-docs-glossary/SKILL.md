---
name: living-docs-glossary
description: Regenerate and review the glossary in a living-docs Fumadocs project. Use whenever MDX frontmatter terms were added, changed, duplicated, renamed, or need consistency cleanup before docs are committed.
---

# living-docs-glossary

Use this skill only inside a project that has `.living-docs/config.json`. If that file is missing, tell the user to run `living-docs init` first.

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

## Write Safety

- Do not hand-edit the generated glossary except to replace it by rerunning the script.
- Do not merge two terms when they may represent different project concepts.
- Preserve the language and naming style already used in nearby docs unless the user asks for a rename.

Report the generated glossary path, any source frontmatter changed, and validation result.
