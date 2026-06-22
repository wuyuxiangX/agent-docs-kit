---
name: agent-docs-kit-change
description: Record shipped changes in an agent-docs-kit Fumadocs project. Use after refactors, features, bug fixes, API or data-contract changes, architecture changes, migrations, deploy changes, or operational fixes that need an immutable paper trail.
---

# agent-docs-kit-change

Use this skill only inside a project that has `.agent-docs-kit/config.json`. If that file is missing, tell the user to run `agent-docs-kit init` first.

Change records are immutable shipped-history pages. They should explain what changed, why it changed, and how it was verified. They are not the place for unshipped plans.

## Source Priority

1. `.agent-docs-kit/config.json` for docs location and project settings.
2. Git diff, commits, changed source files, migrations, config, tests, logs, or runtime checks that prove the shipped change.
3. Existing architecture pages that may need to be updated to match the new current state.
4. User-provided context, marked as unverified when it has not been checked against the repo or runtime.

## Workflow

1. Read `.agent-docs-kit/config.json`.
2. Inspect the relevant source diff, tests, logs, or runtime surface before writing.
3. Choose a domain and short topic slug.
4. Create a change record:

```bash
uvx agent-docs-kit create-doc change <domain> <topic-slug> "<Title>"
```

Optional metadata:

```bash
AGENT_DOCS_KIT_SOURCE="commit/diff/runtime source" AGENT_DOCS_KIT_TESTS="test or verification summary" uvx agent-docs-kit create-doc change <domain> <topic-slug> "<Title>"
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
uvx agent-docs-kit glossary
uvx agent-docs-kit check
```

## Write Safety

- Do not record a change as shipped if it is only proposed or partially implemented.
- Do not rewrite old change records to change history; create a new record for a new shipped correction.
- If the current architecture changed, update the relevant architecture page in the same pass.

Report the change page, any architecture page touched, the evidence used, and validation result.
