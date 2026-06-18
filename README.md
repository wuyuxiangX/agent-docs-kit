# living-docs

Generic documentation system for agent-assisted projects.

living-docs bootstraps a Fumadocs + MDX documentation app, project-local scaffolding scripts, reusable MDX templates, and agent skills for Codex, Claude Code, Copilot, Cursor, Gemini CLI, or a generic agent directory.

living-docs is skills-first. It installs `SKILL.md` workflow skills into the
target project instead of installing slash-command prompt files.

The model follows the same separation that makes tools like Spec Kit scale:

- **CLI**: install and manage the documentation system.
- **Project infra**: keep config, templates, scripts, and validation inside the repo.
- **Agent skills**: handle day-to-day authoring workflows.
- **Fumadocs**: render and organize the docs site.

The CLI is a small Python bootstrapper so it can be run with `uvx` without
requiring Node in the source package. The generated documentation app is still
Node/Fumadocs: after init, previewing, type-checking, and building docs happens
inside the generated `docs/` app with npm.

## Install

One-time usage:

```bash
uvx --from git+https://github.com/wuyuxiangX/living-docs.git living-docs init
```

Persistent install:

```bash
uv tool install git+https://github.com/wuyuxiangX/living-docs.git
living-docs init
```

`living-docs init` is interactive in a terminal:

```text
? Target project [.]:
? Docs directory [docs]:
? Agent integrations
  1. codex - Codex (default)
  2. claude - Claude Code
  3. copilot - GitHub Copilot
  4. cursor - Cursor
  5. gemini - Gemini CLI
  6. generic - Generic
  Enter names or numbers separated by commas, or 'all'.
  Selection [codex]:
? Style [atlas]:
? Overwrite existing managed files if needed? [y/N]:
```

Use explicit flags for scripts or CI:

```bash
living-docs init . --integration codex
living-docs init . --integration codex --integration claude --integration copilot
living-docs init . --integration codex --integration cursor --integration gemini
living-docs init . --integration codex --docs-dir docs --style atlas --yes
```

The starter uses the `atlas` style by default:

```bash
living-docs init . --style atlas --interactive
living-docs styles
```

## Supported Agent Platforms

living-docs installs the same workflow skills into the best available
instruction surface for each agent. Native skill platforms get direct skill
folders; other agents get portable `SKILL.md` workflow files plus a project
context file that points to them.

| Integration | Context file | Workflow files |
| --- | --- | --- |
| `codex` | `AGENTS.md` | `.agents/skills/living-docs-*` |
| `claude` | `CLAUDE.md` | `.claude/skills/living-docs-*` |
| `copilot` | `.github/copilot-instructions.md` | `.github/skills/living-docs-*` |
| `cursor` | `.cursor/rules/living-docs.mdc` | `.living-docs/skills/living-docs-*` |
| `gemini` | `GEMINI.md` | `.living-docs/skills/living-docs-*` |
| `generic` | `.living-docs/AGENT_CONTEXT.md` | `.living-docs/skills/living-docs-*` |

You can repeat `--integration` to install several surfaces in one project.
`cursor`, `gemini`, and `generic` share `.living-docs/skills`, so a project can
support multiple agents without duplicating the portable workflow files.

## User Paths

There is one bootstrap path: install the CLI, then run `living-docs init` in
the target project. The project-local skills are generated during init.

```text
<project>/.living-docs/
<project>/docs/
<project>/.agents/skills/living-docs-*   # Codex integration
<project>/.claude/skills/living-docs-*    # Claude integration
<project>/.github/skills/living-docs-*    # Copilot integration
<project>/.cursor/rules/living-docs.mdc   # Cursor integration
<project>/GEMINI.md                       # Gemini CLI integration
<project>/.living-docs/skills/living-docs-* # Portable workflows
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
.cursor/rules/living-docs.mdc   # cursor integration
GEMINI.md                       # gemini integration
.living-docs/skills/            # portable workflow skills
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

- `living-docs-write` for routing a general docs request to the right workflow
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

## Publish to PyPI

Releases are published from GitHub Actions with PyPI Trusted Publishing. This
avoids long-lived PyPI API tokens in the repository or on a local machine.

One-time PyPI setup for a new package:

1. Open <https://pypi.org/manage/account/publishing/>.
2. Add a pending GitHub Actions publisher with:
   - PyPI project name: `living-docs`
   - Owner: `wuyuxiangX`
   - Repository name: `living-docs`
   - Workflow filename: `publish.yml`
   - Environment name: `pypi`

After that, publish a release by tagging the commit:

```bash
git tag -a v2.1.0 -m v2.1.0
git push origin v2.1.0
```

The workflow builds the Python package with `uv build` and uploads the
distribution files to PyPI.

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
living-docs init
living-docs init [target] [--integration codex|claude|copilot|cursor|gemini|generic] [--docs-dir docs] [--force] [--yes]
living-docs init . --style atlas --interactive
living-docs check
living-docs skills
living-docs styles
living-docs version
living-docs self check
```

## License

MIT
