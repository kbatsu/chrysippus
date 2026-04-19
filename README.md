# chrysippus

[![CI](https://github.com/kbatsu/chrysippus/actions/workflows/ci.yml/badge.svg)](https://github.com/kbatsu/chrysippus/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/tag/kbatsu/chrysippus?sort=semver&label=release)](https://github.com/kbatsu/chrysippus/releases)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Docs](https://img.shields.io/badge/docs-mkdocs--material-purple)](https://kbatsu.github.io/chrysippus/)

> *Named after [Chrysippus of Soli](https://en.wikipedia.org/wiki/Chrysippus)
> (c. 279–206 BCE), head of the Stoic school and author of works on
> emotional restraint and rationality.*

Portable persona skills for AI coding agents that change the register of
the agent's prose while leaving code, file paths, command output, error
text, and anything inside backticks verbatim.

Persona skills ship from this repo:

- **`shakespeare`** — Early Modern English (c. 1600, Bardic register).
- **`pirate`** — Treasure Island / Pirates-of-the-Caribbean register.
- **`gen-alpha`** — Internet-native ironic Gen-Alpha slang.
- **`toronto-mans`** — Toronto / Multicultural-Toronto-English caricature.
- **`ontario-bud`** — Rural-Ontario / Letterkenny-inspired caricature.

Supported agents: **Claude Code** (first-class plugin), **Codex**, **Cline**,
**Aider**, **Cursor**, **Windsurf**, **Gemini CLI**. Generated from a single
canonical source at `rules/<persona>/`.

Inspired by [caveman](https://github.com/JuliusBrussee/caveman). Same
mechanism, different goal: caveman compresses speech to **save tokens**;
chrysippus retunes register **for fun**. There are no token savings here
— if anything, register-shifting adds a touch of overhead. Run it
because you want your agent to sound like the Bard, not because you want
a smaller bill.

## Quickstart

**Claude Code** (one command):

```bash
claude plugin marketplace add kbatsu/chrysippus
claude plugin install chrysippus@kbatsu-plugins
# then in any session: /chrysippus:shakespeare
```

If you installed via the marketplace, `/chrysippus:personas` lists every
persona and its flavors — handy when you forget what's available. Every
persona activation also announces the active flavor, the other flavors,
and how to switch/stop.

**Other agents**: copy the generated file that your agent reads.

```bash
git clone https://github.com/kbatsu/chrysippus /tmp/chrysippus
cd your-project

cp /tmp/chrysippus/AGENTS.md .              # Codex, Cline, Aider (AGENTS.md convention)
cp /tmp/chrysippus/GEMINI.md .              # Gemini CLI
cp /tmp/chrysippus/CONVENTIONS.md .         # Aider (alternative)
cp /tmp/chrysippus/.windsurfrules .         # Windsurf
cp /tmp/chrysippus/.clinerules .            # Cline
cp -r /tmp/chrysippus/.cursor .             # Cursor IDE
```

Then trigger any persona with its phrase:

```
speak like Shakespeare
talk like a pirate
talk like gen alpha
talk like a toronto mans
ontario bud
```

Deactivate with *"stop &lt;persona&gt;"* or *"speak plainly"*.

Full documentation: **<https://kbatsu.github.io/chrysippus/>**
(rendered with mkdocs-material; source in [`docs/`](docs/), built and
deployed automatically by `.github/workflows/docs.yml` on every push to
`main` that touches `docs/` or `mkdocs.yml`).

## Demo

> **Plain**: *"I read the file. Found three TODOs. Want me to address them now?"*
>
> **Bardic** (`shakespeare`): *"I have perused the scroll, and lo — three
> TODOs lie scattered therein. Prithee, sir, shall I set hand to them
> anon?"*

Same prompt rendered in every persona's voice (with multiple flavors per
persona) lives on the docs site:
**[Full demos for each persona →](https://kbatsu.github.io/chrysippus/personas/)**.

## Sibling skills

All skills share the same architecture: a self-contained folder with
`SKILL.md`, a `*.config` file for per-repo settings, and an `examples.md`
corpus. They are installed and activated independently.

<!-- chrysippus:sibling-skills-table BEGIN -->
| Persona | Register | Default flavor | Other flavors |
|---|---|---|---|
| [`gen-alpha`](docs/personas/gen-alpha.md) | Internet-native ironic Gen-Alpha slang | `unhinged` | `corporate`, `tutorial` |
| [`ontario-bud`](docs/personas/ontario-bud.md) | Rural-Ontario / Letterkenny-inspired caricature | `bud` | *(single flavor in v1)* |
| [`pirate`](docs/personas/pirate.md) | Treasure Island / POTC 17–18c. maritime | `scurvy-dog` | `captain`, `drunk`, `shanty` |
| [`shakespeare`](docs/personas/shakespeare.md) | Early Modern English (c. 1600) | `courtly` | `tavern`, `sonnet` |
| [`toronto-mans`](docs/personas/toronto-mans.md) | Toronto / Multicultural-Toronto-English caricature | `mans` | *(single flavor in v1)* |
<!-- chrysippus:sibling-skills-table END -->

If more than one is activated in the same session, the most recently
invoked one wins — no fusion or blending.

## Install

### Claude Code marketplace install (recommended for Claude Code users)

Available via the Claude Code marketplace:

```bash
claude plugin marketplace add kbatsu/chrysippus
claude plugin install chrysippus@kbatsu-plugins
```

This installs the plugin — all personas, the slash commands, the
reviewer subagents, and the SessionStart hook — into your user-global
Claude Code settings. To enable auto-activation of a persona for a
specific project:

```bash
cd your-project
bash "${CLAUDE_PLUGIN_ROOT}/hooks/activate.sh" shakespeare
# (or: pirate / gen-alpha / toronto-mans / ontario-bud / off / status)
```

### Per-repo install (copy the skill folders by hand)

Copy the skill folder(s) you want into the target repo's
`.claude/skills/`:

```bash
# from your target repo's root
mkdir -p .claude/skills

# or all of them
<!-- chrysippus:cp-skills-per-repo BEGIN -->
cp -r /path/to/chrysippus/.claude/skills/gen-alpha .claude/skills/
cp -r /path/to/chrysippus/.claude/skills/ontario-bud .claude/skills/
cp -r /path/to/chrysippus/.claude/skills/pirate .claude/skills/
cp -r /path/to/chrysippus/.claude/skills/shakespeare .claude/skills/
cp -r /path/to/chrysippus/.claude/skills/toronto-mans .claude/skills/
<!-- chrysippus:cp-skills-per-repo END -->
```

Or as a git submodule, or by cloning this repo and symlinking — whichever
fits your workflow.

### User-global install (just you, every repo)

Copy the folder(s) into your personal Claude Code skills directory:

```bash
mkdir -p ~/.claude/skills
<!-- chrysippus:cp-skills-user-global BEGIN -->
cp -r /path/to/chrysippus/.claude/skills/gen-alpha ~/.claude/skills/
cp -r /path/to/chrysippus/.claude/skills/ontario-bud ~/.claude/skills/
cp -r /path/to/chrysippus/.claude/skills/pirate ~/.claude/skills/
cp -r /path/to/chrysippus/.claude/skills/shakespeare ~/.claude/skills/
cp -r /path/to/chrysippus/.claude/skills/toronto-mans ~/.claude/skills/
<!-- chrysippus:cp-skills-user-global END -->
```

## Activation

Each skill activates two ways.

### 1. Trigger phrase (no setup)

Once a skill's folder is installed, say any of its trigger phrases in a
session and it loads and persists for the rest of the session:

<!-- chrysippus:trigger-phrases BEGIN -->
- **Gen-Alpha**: *"talk like gen alpha"*, *"gen alpha mode"*, *"go skibidi"*, *"skibidi mode"*, `/gen-alpha`, `/genalpha`.
- **Ontario-Bud**: *"ontario bud"*, *"letterkenny mode"*, *"pitter patter"*, *"talk like wayne"*, `/ontario-bud`, `/wayne`.
- **Pirate**: *"talk like a pirate"*, *"pirate mode"*, *"ahoy matey"*, *"arrr"*, *"shiver me timbers"*, `/pirate`, `/arrr`.
- **Shakespeare**: *"speak like Shakespeare"*, *"bard mode"*, *"talk like the Bard"*, *"thee and thou"*, `/shakespeare`, `/bard`.
- **Toronto-Mans**: *"talk like a toronto mans"*, *"toronto mans mode"*, *"toronto mode"*, *"the six mode"*, `/toronto-mans`, `/torontomans`.
<!-- chrysippus:trigger-phrases END -->

### 2. Always-on via CLAUDE.md (recommended for dedicated repos)

Append the relevant snippet to the target repo's `CLAUDE.md` (create the
file if it doesn't exist). Only add the snippet for the skill you want
always-on — if both are present in a repo, typically only one is the
persona-of-the-day.

**Shakespeare:**

```markdown
## Communication style

This repo uses the `shakespeare` skill at `.claude/skills/shakespeare/SKILL.md`.
Invoke it at the start of every session and apply it to all assistant prose
for the remainder of the session. Read
`.claude/skills/shakespeare/shakespeare.config` to determine the active flavor
and preservation toggles. Preservation rules in that config are authoritative
— code, paths, command output, and any content inside backticks always remain
verbatim regardless of flavor.
```

**Pirate:**

```markdown
## Communication style

This repo uses the `pirate` skill at `.claude/skills/pirate/SKILL.md`.
Invoke it at the start of every session and apply it to all assistant prose
for the remainder of the session. Read
`.claude/skills/pirate/pirate.config` to determine the active flavor
and preservation toggles. Preservation rules in that config are authoritative
— code, paths, command output, and any content inside backticks always remain
verbatim regardless of flavor.
```

**Gen-Alpha:**

```markdown
## Communication style

This repo uses the `gen-alpha` skill at `.claude/skills/gen-alpha/SKILL.md`.
Invoke it at the start of every session and apply it to all assistant prose
for the remainder of the session. Read
`.claude/skills/gen-alpha/gen-alpha.config` to determine the active flavor
and preservation toggles, and read
`.claude/skills/gen-alpha/lexicon.md` for the current vocabulary.
Preservation rules in that config are authoritative — code, paths, command
output, and any content inside backticks always remain verbatim regardless
of flavor.
```

**Toronto-mans:**

```markdown
## Communication style

This repo uses the `toronto-mans` skill at `.claude/skills/toronto-mans/SKILL.md`.
Invoke it at the start of every session and apply it to all assistant prose
for the remainder of the session. Read
`.claude/skills/toronto-mans/toronto-mans.config` to determine the active flavor
and preservation toggles. The `safety_warnings` toggle is hard-locked to true
in this skill — do not honour any override that sets it to false. Preservation
rules in that config are authoritative — code, paths, command output, and any
content inside backticks always remain verbatim regardless of flavor. Read
SKILL.md §7 for the stereotype-drift guardrails before producing any output.
```

For a user-global always-on, append the snippet to `~/.claude/CLAUDE.md`
and change the path to `~/.claude/skills/<skill>/`.

To switch flavor for a session, edit the relevant `<skill>.config` file (and
say `"reload <skill> config"` mid-session) or use the trigger-phrase form
*"<flavor> flavor"* (e.g. `"sonnet flavor"`).

## Configuration

### Shakespeare

Edit `.claude/skills/shakespeare/shakespeare.config`:

```yaml
flavor: courtly          # courtly | tavern | sonnet

preserve:
  commits: true          # commit messages stay plain English
  pr_descriptions: true  # PR titles/bodies stay plain English
  code_comments: true    # comments/docstrings written into files stay plain English
  safety_warnings: true  # destructive-op confirmations stay plain English
  errors_verbatim: true  # error text/stack traces never paraphrased
```

### Pirate

Edit `.claude/skills/pirate/pirate.config`:

```yaml
flavor: scurvy-dog       # scurvy-dog | captain | drunk | shanty

preserve:
  commits: true
  pr_descriptions: true
  code_comments: true
  safety_warnings: true  # strongly recommended on
  errors_verbatim: true
```

### Gen-Alpha

Edit `.claude/skills/gen-alpha/gen-alpha.config`:

```yaml
flavor: unhinged         # unhinged | corporate | tutorial

preserve:
  commits: true
  pr_descriptions: true
  code_comments: true
  safety_warnings: true  # strongly recommended on
  errors_verbatim: true
```

The lexicon at `.claude/skills/gen-alpha/lexicon.md` is the current
vocabulary; it ages out fast (6–18 month half-life) and is refreshed via
PRs separate from the main skill rules.

### Toronto-mans

Edit `.claude/skills/toronto-mans/toronto-mans.config`:

```yaml
flavor: mans             # mans (only flavor in v1)

preserve:
  commits: true
  pr_descriptions: true
  code_comments: true
  safety_warnings: true  # HARD-LOCKED — cannot be changed
  errors_verbatim: true
```

The `safety_warnings` toggle is **hard-locked to true** in this skill. Even
if the file says `false`, the skill treats it as `true`. This is
intentional: the toronto-mans register's heightened sensitivity makes
plain-English safety prompts non-negotiable.

The lexicon at `.claude/skills/toronto-mans/lexicon.md` is the authoritative
vocabulary, with per-term provenance tags. Do not pull Patois, MTE, or AAVE
vocabulary from outside this lexicon — stay within the allowed surface.

Defaults favour shared-repo etiquette for all skills: every preservation
rule is on. Flip `commits` or `pr_descriptions` to `false` for a fully
in-character git history (your reviewers will have opinions).

After editing any config mid-session, say *"reload <skill> config"* so
Claude re-reads it. New sessions read configs automatically.

See [**docs/configuration.md**](docs/configuration.md) for the full
config model — every toggle explained, hard-locks, reload mechanics,
and danger combos. See [**docs/recipes.md**](docs/recipes.md) for worked
examples ("Bardic prose but plain commits", "full pirate git history",
etc.).

## Mid-session controls

Shared across all skills:

- `"speak plainly"` / `"plain English"` — suspend the active skill for the
  next response only.
- `"stop shakespeare"` / `"end bard mode"` — fully deactivate shakespeare.
- `"stop pirate"` / `"end pirate mode"` — fully deactivate pirate.
- `"stop gen alpha"` / `"end gen alpha"` — fully deactivate gen-alpha.
- `"stop toronto mans"` / `"end toronto mans"` — fully deactivate toronto-mans.
- `"<flavor> flavor"` — switch flavor within the active skill (e.g.
  `"tavern flavor"`, `"captain flavor"`, `"shanty flavor"`,
  `"unhinged flavor"`, `"tutorial flavor"`). Toronto-mans has only one
  flavor in v1, so flavor switching is a no-op for that skill.
- `"reload <skill> config"` / `"reload <skill> lexicon"` — re-read the
  named skill's config or lexicon after editing.

## What stays plain English (always)

- Anything inside backticks: `` `foo()` ``, `` `null` ``, file paths, flags.
  **Hard rule, not configurable.**
- Anything covered by an enabled `preserve.*` toggle in the active skill's config.
- Slash command output and harness messages (those aren't Claude's prose anyway).
- Replies in non-English languages — neither the Bard nor the buccaneer spoke anything else.

## Slash commands (Claude Code plugin)

When installed via the marketplace, `chrysippus` exposes these commands
(auto-namespaced by Claude Code as `/chrysippus:<command>`):

| Command | Effect |
|---|---|
| `/chrysippus:shakespeare` | Activate the shakespeare persona for the session |
| `/chrysippus:pirate` | Activate the pirate persona |
| `/chrysippus:gen-alpha` | Activate gen-alpha |
| `/chrysippus:toronto-mans` | Activate toronto-mans (hard-lock on safety warnings) |
| `/chrysippus:personas` | List installed personas and show which is active |

Pass a flavor as an argument to switch flavor on activation:
`/chrysippus:pirate shanty`.

## Reviewer subagents

Four per-persona code-review subagents, plus a meta "dramaturg":

| Agent | Purpose |
|---|---|
| `shakespeare-reviewer` | PR review in Bardic register, substantive feedback |
| `pirate-reviewer` | PR review in pirate register |
| `gen-alpha-reviewer` | PR review in gen-alpha voice |
| `toronto-mans-reviewer` | PR review in toronto-mans register |
| `dramaturg` | Meta-agent: audits persona rule-adherence in a conversation; speaks plainly itself |

Each reviewer declares the corresponding skill in its frontmatter, so the
persona's full rules load automatically when the subagent runs.

Invoke with an `@`-mention:

```
@chrysippus:shakespeare-reviewer review my latest PR
```

See [**docs/subagents.md**](docs/subagents.md) for the full invocation
guide — natural-language, session-default, passing context, when to
use a subagent vs. your main session, and an example of what each
reviewer's output looks like.

## SessionStart hook (opt-in auto-activation)

`hooks/session-start.sh` reads `.claude/personas/active` in the project dir
on every session start. If the file names a valid persona, the hook tells
Claude to auto-activate it for the session.

Enable for a project:

```bash
bash hooks/activate.sh shakespeare   # or pirate / gen-alpha / toronto-mans
bash hooks/activate.sh status        # check current state
bash hooks/activate.sh off           # disable
```

**Security**: the hook runs unsandboxed at your shell privilege (per Claude
Code's hook model). It contains no network calls, no `eval`, and under
100 lines; read it before running. See `SECURITY.md` for the full
disclosure.

## Multi-agent support

As of `v0.5.0`, the same canonical rules at `rules/<persona>/` are rendered
into formats for multiple AI coding agents. `scripts/render.py` emits all
targets; `scripts/render.py --check` verifies no drift.

| Agent | Generated file(s) | Status |
|---|---|---|
| Claude Code | `.claude/skills/<persona>/SKILL.md` + `<persona>.config` + `examples.md` + `lexicon.md` | ✅ |
| Codex / Cline / Aider (AGENTS.md convention) | `AGENTS.md` | ✅ |
| Gemini CLI | `GEMINI.md` | ✅ |
| Aider (project conventions) | `CONVENTIONS.md` | ✅ |
| Windsurf (Codeium) | `.windsurfrules` | ✅ |
| Cline | `.clinerules` | ✅ |
| Cursor IDE | `.cursor/rules/<persona>.mdc` | ✅ |
| Kiro IDE | *(coming soon — awaiting stable spec)* | ⏳ |

All multi-agent files are checked into the repo alongside the Claude Code
skills. Downstream users get activation in their preferred agent without
needing to regenerate anything.

## File layout

```
.claude/skills/
├── shakespeare/
│   ├── SKILL.md            # the skill: register, flavors, preservation rules
│   ├── shakespeare.config  # per-repo settings
│   └── examples.md         # extended before/after corpus
├── pirate/
│   ├── SKILL.md
│   ├── pirate.config
│   └── examples.md
├── gen-alpha/
│   ├── SKILL.md
│   ├── gen-alpha.config
│   ├── examples.md
│   └── lexicon.md          # current vocabulary, refreshable
└── toronto-mans/
    ├── SKILL.md
    ├── toronto-mans.config
    ├── examples.md
    └── lexicon.md          # vocabulary w/ per-term provenance (MTE, Patois, AAVE)
```

At the repo root, generated multi-agent files also live alongside the
Claude Code skills:

```
AGENTS.md              # universal (Codex, Cline, Aider, others)
GEMINI.md              # Gemini CLI
CONVENTIONS.md         # Aider project conventions
.windsurfrules         # Windsurf (Codeium)
.clinerules            # Cline
.cursor/rules/<persona>.mdc  # Cursor IDE (one per persona)
```

All of the above **and** `.claude/skills/<persona>/` are **generated** from
canonical source at `rules/<persona>/` by `scripts/render.py`. To modify a
skill, edit the `rules/` source and re-run `scripts/render.py`. See
`CONTRIBUTING.md` for the workflow.

## Credits

Voices borrowed from a man who has been dead 410 years and still writes
better than most of us; from a fictional register that never really existed
but has outlived most that did; and from internet-meme culture, parodied by
people too old to be representative of it.
