# living-docs

Generic documentation system for agent-assisted projects.

living-docs bootstraps a Fumadocs + MDX documentation app, project-local scaffolding scripts, reusable MDX templates, and agent skills for Codex, Claude Code, Copilot, or a generic agent directory.

living-docs is skills-first. It installs `SKILL.md` workflow skills into the
target project instead of installing slash-command prompt files.

The model follows the same separation that makes tools like Spec Kit scale:

- **CLI**: install and manage the documentation system.
- **Project infra**: keep config, templates, scripts, and validation inside the repo.
- **Agent skills**: handle day-to-day authoring workflows.
- **Fumadocs**: render and organize the docs site.

## Install

One-time usage:

```bash
uvx --from git+https://github.com/wuyuxiangX/living-docs.git living-docs init .
```

Persistent install:

```bash
uv tool install living-docs --from git+https://github.com/wuyuxiangX/living-docs.git
living-docs init .
```

Initialize with explicit integrations:

```bash
living-docs init . --integration codex
living-docs init . --integration codex --integration claude --integration copilot
```

The starter uses the `atlas` style by default:

```bash
living-docs init . --style atlas
living-docs styles
```

## User Paths

There is one bootstrap path: install the CLI, then run `living-docs init` in
the target project. The project-local skills are generated during init.

```text
<project>/.living-docs/
<project>/docs/
<project>/.agents/skills/living-docs-*   # Codex integration
<project>/.claude/skills/living-docs-*    # Claude integration
<project>/.github/skills/living-docs-*    # Copilot integration
```

The per-project workflow skills live in the CLI assets under
`src/living_docs_cli/assets/workflow-skills/` and are copied into each target
project during `living-docs init`, so they can use that project's
`.living-docs/config.json`, templates, scripts, and context file. There is no
separate global `living-docs` helper skill.

## What Init Creates

```text
.living-docs/
  config.json
  templates/
    architecture.mdx
    change.mdx
    plan.mdx
    glossary.mdx
  scripts/
    create-doc.mjs
    glossary.mjs
    check.mjs

docs/
  app/
  components/
  content/docs/
  lib/
  package.json
  source.config.ts

.agents/skills/                 # codex integration
.claude/skills/                 # claude integration
.github/skills/                 # copilot skills mode
AGENTS.md / CLAUDE.md / ...     # managed living-docs context block
```

The managed context block is bounded by:

```markdown
<!-- LIVING-DOCS START -->
...
<!-- LIVING-DOCS END -->
```

Re-running init replaces only that block and preserves surrounding project instructions.

## Day-to-Day Workflow

Use generated skills from your agent:

- `living-docs-architecture` for current architecture docs
- `living-docs-change` for shipped change records
- `living-docs-plan` for future design plans
- `living-docs-glossary` after terms change
- `living-docs-check` before committing docs changes

The skills call project-local scripts:

```bash
node .living-docs/scripts/create-doc.mjs change api auth-flow "Auth Flow Update"
node .living-docs/scripts/glossary.mjs
node .living-docs/scripts/check.mjs
```

## MDX Components

living-docs ships reusable MDX components in the generated Fumadocs app. Use
them directly in `.mdx` pages:

```mdx
<ArchMap
  tiers={[
    {
      title: 'Entry points',
      boxes: [
        { title: 'Web app', body: 'User-facing route.', tone: 'blue' },
        { title: 'API', body: 'Server boundary.', tone: 'green' },
      ],
    },
  ]}
/>

<FlowSteps
  title="Request flow"
  steps={[
    { title: 'Receive input', body: 'Validate payload.', tone: 'blue' },
    { title: 'Run service', body: 'Execute domain action.', tone: 'green' },
    { title: 'Return result', body: 'Send status and telemetry.', tone: 'amber' },
  ]}
/>

<StateFlow
  title="Lifecycle"
  states={[
    { name: 'draft', description: 'Work in progress.', tone: 'amber' },
    { name: 'active', description: 'Current runtime truth.', tone: 'green' },
  ]}
/>
```

The generated docs include `/docs/components` with copyable examples. Use
mermaid for complex sequence diagrams, branches, or graphs that do not fit the
built-in components.

The global CLI can also validate the project:

```bash
living-docs check
```

## Run the Docs Site

```bash
cd docs
npm install
npm run dev -- --port 3333
```

Fumadocs reads MDX from `docs/content/docs`.

## Authoring Contract

- MDX is the source of truth.
- Architecture pages describe current state.
- Change pages are immutable records of shipped changes.
- Plan pages describe future intent.
- Glossary pages are generated from frontmatter `terms`.
- Architecture and change pages should include `<ArchMap />` or mermaid diagrams.
- Validation must pass before treating docs work as complete.

## CLI

```bash
living-docs init [target] [--integration codex|claude|copilot|generic] [--docs-dir docs] [--force]
living-docs init . --style atlas
living-docs check
living-docs skills
living-docs styles
living-docs version
living-docs self check
```

## License

MIT
