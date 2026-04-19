# Install

`chrysippus` supports multiple AI coding agents from a single canonical
source. Pick your agent below.

| Agent | Install page | Primary file |
|---|---|---|
| Claude Code | [claude-code.md](claude-code.md) | `.claude-plugin/plugin.json` (via marketplace) |
| Cursor IDE | [cursor.md](cursor.md) | `.cursor/rules/<persona>.mdc` |
| Codex (OpenAI) | [agents-md.md](agents-md.md) | `AGENTS.md` |
| Cline | [agents-md.md](agents-md.md) | `AGENTS.md` or `.clinerules` |
| Aider | [aider.md](aider.md) | `CONVENTIONS.md` or `AGENTS.md` |
| Windsurf | [windsurf.md](windsurf.md) | `.windsurfrules` |
| Gemini CLI | [gemini.md](gemini.md) | `GEMINI.md` |
| Kiro IDE | *coming soon* | — |

All generated files — `AGENTS.md`, `GEMINI.md`, `.cursor/rules/*.mdc`,
`.windsurfrules`, `.clinerules`, `CONVENTIONS.md`, `.claude/skills/<persona>/` —
are committed in this repo alongside the canonical source at `rules/`. Copy
the files your agent reads into your project.

## Two install models

### Per-project

The `chrysippus` files live in your project's root alongside your code.
Every contributor to that project gets the personas when they use a
supported agent. Good for personal projects or team-opt-in.

### User-global

The `chrysippus` files live in your user-global agent config (e.g.
`~/.claude/skills/` for Claude Code). You get the personas across every
project. Good for solo use.

Each agent's install page covers both models.

## After installing

Trigger any persona with one of its phrases:

<!-- chrysippus:trigger-phrases BEGIN -->
- **Gen-Alpha**: *"talk like gen alpha"*, *"gen alpha mode"*, *"go skibidi"*, *"skibidi mode"*, `/gen-alpha`, `/genalpha`.
- **Ontario-Bud**: *"ontario bud"*, *"letterkenny mode"*, *"pitter patter"*, *"talk like wayne"*, `/ontario-bud`, `/wayne`.
- **Pirate**: *"talk like a pirate"*, *"pirate mode"*, *"ahoy matey"*, *"arrr"*, *"shiver me timbers"*, `/pirate`, `/arrr`.
- **Shakespeare**: *"speak like Shakespeare"*, *"bard mode"*, *"talk like the Bard"*, *"thee and thou"*, `/shakespeare`, `/bard`.
- **Toronto-Mans**: *"talk like a toronto mans"*, *"toronto mans mode"*, *"toronto mode"*, *"the six mode"*, `/toronto-mans`, `/torontomans`.
<!-- chrysippus:trigger-phrases END -->

Deactivate with *"stop &lt;persona&gt;"* or *"speak plainly"*.

See the [personas](../personas/index.md) pages for full trigger lists,
flavor tables, and per-persona preservation rules.
