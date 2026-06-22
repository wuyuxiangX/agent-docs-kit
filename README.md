# agent-docs-kit

Project Atlas documentation system for agent-assisted projects.

agent-docs-kit bootstraps a Fumadocs + MDX Project Atlas, project-local
scaffolding scripts, reusable MDX templates, and agent skills for Codex, Claude
Code, Copilot, Cursor, Gemini CLI, or a generic agent directory.

The main goal is a broad architecture map: modules, layers, core flows, and
architecture direction. It is not a project-management platform and does not
ask you to document every feature.

agent-docs-kit is skills-first. It installs `SKILL.md` workflow skills into the
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
uvx agent-docs-kit init
uvx agent-docs-kit web --open
```

Persistent install:

```bash
uv tool install agent-docs-kit
agent-docs-kit init
```

The PyPI distribution installs one public CLI command: `agent-docs-kit`.

`agent-docs-kit init` is interactive in a terminal:

```text
? Target project [.]:
? Docs directory [docs]:
? Agent integrations
  Up/Down or j/k moves. Space selects. a selects all. Enter confirms.
  > [x] Codex (codex)
    [ ] Claude Code (claude)
    [ ] GitHub Copilot (copilot)
    [ ] Cursor (cursor)
    [ ] Gemini CLI (gemini)
    [ ] Generic (generic)
? Style [atlas]:
? Overwrite existing managed files if needed? [y/N]:
```

Use explicit flags for scripts or CI:

```bash
agent-docs-kit init . --integration codex
agent-docs-kit init . --integration codex --integration claude --integration copilot
agent-docs-kit init . --integration codex --integration cursor --integration gemini
agent-docs-kit init . --integration codex --docs-dir docs --style atlas --yes
agent-docs-kit web
agent-docs-kit atlas --force
agent-docs-kit skills
```

The starter uses the `atlas` style by default:

```bash
agent-docs-kit init . --style atlas --interactive
agent-docs-kit styles
```

## Supported Agent Platforms

agent-docs-kit installs the same workflow skills into the best available
instruction surface for each agent. Native skill platforms get direct skill
folders; other agents get portable `SKILL.md` workflow files plus a project
context file that points to them.

| Integration | Context file | Workflow files |
| --- | --- | --- |
| `codex` | `AGENTS.md` | `.agents/skills/agent-docs-kit-*` |
| `claude` | `CLAUDE.md` | `.claude/skills/agent-docs-kit-*` |
| `copilot` | `.github/copilot-instructions.md` | `.github/skills/agent-docs-kit-*` |
| `cursor` | `.cursor/rules/agent-docs-kit.mdc` | `.agent-docs-kit/skills/agent-docs-kit-*` |
| `gemini` | `GEMINI.md` | `.agent-docs-kit/skills/agent-docs-kit-*` |
| `generic` | `.agent-docs-kit/AGENT_CONTEXT.md` | `.agent-docs-kit/skills/agent-docs-kit-*` |

You can repeat `--integration` to install several surfaces in one project.
`cursor`, `gemini`, and `generic` share `.agent-docs-kit/skills`, so a project can
support multiple agents without duplicating the portable workflow files.

## User Paths

There is one bootstrap path: install the CLI, then run `agent-docs-kit init` in
the target project. The project-local skills are generated during init.

```text
<project>/.agent-docs-kit/
<project>/docs/
<project>/.agents/skills/agent-docs-kit-*   # Codex integration
<project>/.claude/skills/agent-docs-kit-*    # Claude integration
<project>/.github/skills/agent-docs-kit-*    # Copilot integration
<project>/.cursor/rules/agent-docs-kit.mdc   # Cursor integration
<project>/GEMINI.md                       # Gemini CLI integration
<project>/.agent-docs-kit/skills/agent-docs-kit-* # Portable workflows
```

The per-project workflow skills live in the CLI assets under
`src/living_docs_cli/assets/workflow-skills/` and are copied into each target
project during `init`, so they can use that project's
`.agent-docs-kit/config.json`, templates, scripts, and context file. There is no
separate global `agent-docs-kit` helper skill.

## What Init Creates

```text
.agent-docs-kit/
  config.json
  templates/
    atlas.mdx
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
    atlas.mdx
  lib/
  package.json
  source.config.ts

.agents/skills/                 # codex integration
.claude/skills/                 # claude integration
.github/skills/                 # copilot skills mode
.cursor/rules/agent-docs-kit.mdc   # cursor integration
GEMINI.md                       # gemini integration
.agent-docs-kit/skills/            # portable workflow skills
AGENTS.md / CLAUDE.md / ...     # managed agent-docs-kit context block
```

The managed context block is bounded by:

```markdown
<!-- AGENT-DOCS-KIT START -->
...
<!-- AGENT-DOCS-KIT END -->
```

Re-running init replaces only that block and preserves surrounding project instructions.

## Day-to-Day Workflow

Start the local docs site from the project root:

```bash
agent-docs-kit web
```

The command installs docs dependencies when `node_modules` is missing, finds an
available local port starting at `3333`, and prints the URL. Add `--open` to
open the browser automatically.

Use generated skills from your agent:

- `agent-docs-kit-write` for routing a general docs request to the right workflow
- `agent-docs-kit-architecture` for Project Atlas and current architecture docs
- `agent-docs-kit-change` for shipped change records
- `agent-docs-kit-plan` for future design plans
- `agent-docs-kit-glossary` after terms change
- `agent-docs-kit-check` before committing docs changes

Common commands:

```bash
agent-docs-kit skills
agent-docs-kit web --open
agent-docs-kit atlas --force
agent-docs-kit create-doc change api auth-flow "Auth Flow Update"
agent-docs-kit glossary
agent-docs-kit check
```

The generated `.agent-docs-kit/scripts/` files are implementation details used
by the project-local skills.

Use `agent-docs-kit atlas --stdout` after init to preview an editable Project
Atlas draft from repository structure. It writes `docs/content/docs/atlas.mdx`
by default. New projects already include a starter `atlas.mdx`, so pass
`--force` only when you want to replace that starter page.

## MDX Components

agent-docs-kit ships reusable MDX components in the generated Fumadocs app. Use
them directly in `.mdx` pages:

```mdx
<SystemMap
  title="System map"
  nodes={[
    { title: 'Web app', body: 'User-facing routes.', tone: 'blue' },
    { title: 'API', body: 'Server boundary.', tone: 'green' },
  ]}
  links={[{ from: 'Web app', to: 'API', label: 'calls' }]}
/>

<LayerMap
  title="Project layers"
  layers={[
    {
      title: 'Surfaces',
      body: 'User-visible or agent-visible entry points.',
      tone: 'blue',
      items: ['app/', 'api/', 'cli/'],
    },
  ]}
/>

<FlowMap
  title="Primary runtime path"
  flows={[
    { title: 'Entry', body: 'Input and routing boundary.', tone: 'blue', steps: ['Request', 'Route'] },
    { title: 'Execution', body: 'Core modules and state changes.', tone: 'green', steps: ['Validate', 'Persist'] },
  ]}
/>

<RoadmapMap
  items={[
    { title: 'Current shape', body: 'What the repo and runtime prove today.', status: 'now', tone: 'green' },
    { title: 'Next structural move', body: 'The next architecture-level change.', status: 'next', tone: 'blue' },
  ]}
/>

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
agent-docs-kit check
```

## Run the Docs Site

```bash
agent-docs-kit web
```

Fumadocs reads MDX from `docs/content/docs`. If you prefer to run the generated
app directly, use `cd docs && npm install && npm run dev -- --port 3333`.

## Publish to PyPI

Releases are published from GitHub Actions with PyPI Trusted Publishing. This
avoids long-lived PyPI API tokens in the repository or on a local machine.

One-time PyPI setup for a new package:

1. Open <https://pypi.org/manage/account/publishing/>.
2. Add a pending GitHub Actions publisher with:
   - PyPI project name: `agent-docs-kit`
   - Owner: `wuyuxiangX`
   - Repository name: `agent-docs-kit`
   - Workflow filename: `publish.yml`
   - Environment name: `pypi`

After that, publish a release by tagging the commit:

```bash
git tag -a v2.2.2 -m v2.2.2
git push origin v2.2.2
```

The workflow builds the Python package with `uv build` and uploads the
distribution files to PyPI.

## Authoring Contract

- MDX is the source of truth.
- The Project Atlas is the first project-level architecture surface.
- Architecture pages describe current state.
- Change pages are immutable records of shipped changes.
- Plan pages describe future intent.
- Glossary pages are generated from frontmatter `terms`.
- Architecture and change pages should include an Atlas/architecture component or mermaid diagram.
- Do not create feature-level pages by default; prefer a broad Atlas first.
- Validation must pass before treating docs work as complete.

## CLI

```bash
agent-docs-kit init
agent-docs-kit init [target] [--integration codex|claude|copilot|cursor|gemini|generic] [--docs-dir docs] [--force] [--yes]
agent-docs-kit init . --style atlas --interactive
agent-docs-kit web [target] [--port 3333] [--host 127.0.0.1] [--open] [--no-install]
agent-docs-kit atlas [target] [--output docs/content/docs/atlas.mdx] [--force] [--stdout]
agent-docs-kit create-doc <atlas|architecture|change|plan> <domain> [slug] ["Title"]
agent-docs-kit glossary
agent-docs-kit check
agent-docs-kit skills
agent-docs-kit styles
agent-docs-kit version
agent-docs-kit self check
```

## License

MIT
