# shakespeare (+ sibling skills)

Portable Claude Code skills that change the register of Claude's prose
while leaving code, file paths, command output, error text, and anything
inside backticks verbatim.

Two skills ship from this repo:

- **`shakespeare`** — Early Modern English (c. 1600, Bardic register).
- **`pirate`** — Treasure Island / Pirates-of-the-Caribbean register.

Inspired by [caveman](https://github.com/JuliusBrussee/caveman). Same
mechanism, different aesthetics: instead of compressing speech, these
skills retune it.

## Demo

### Shakespeare

> **Plain Claude:**
> *"I read the file. Found three TODOs. Want me to address them now?"*

> **Bardic Claude (courtly flavor):**
> *"I have perused the scroll, and lo — three TODOs lie scattered therein.
> Prithee, sir, shall I set hand to them anon?"*

> **Bardic Claude (tavern flavor):**
> *"Hark! Three TODOs lurk within yon scroll like rogues in an alley.
> Speak the word, and I shall rout them all!"*

> **Bardic Claude (sonnet flavor — only on task completion):**
> *"Three tests are writ, the bug on line is slain,*
> *No crimson error mars the verdant plain."*

### Pirate

> **Plain Claude:**
> *"I read the file. Found three TODOs. Want me to address them now?"*

> **Pirate Claude (scurvy-dog flavor):**
> *"Aye, hauled up the scroll. Three TODOs lurkin' below decks, matey.
> Speak the word and I'll rout 'em."*

> **Pirate Claude (captain flavor):**
> *"The scroll is read. Three TODOs await. Thy orders, sir."*

> **Pirate Claude (drunk flavor):**
> *"YARRRR, three TODOs skulkin' below decks! Pour the rum and give the
> order — we'll run 'em through afore sundown!"*

> **Pirate Claude (shanty flavor — only on task completion):**
> *"Three tests writ, the bug be slain,*
> *Cannons silent, calm the main,*
> *Hoist the colors, drink yer rum,*
> *Cap'n's pleased — the work be done!"*

### Gen-Alpha

> **Plain Claude:**
> *"I read the file. Found three TODOs. Want me to address them now?"*

> **Gen-Alpha Claude (unhinged flavor):**
> *"read the file. 3 TODOs in there. wild. want me to handle 'em rq?"*

> **Gen-Alpha Claude (corporate flavor):**
> *"Per my last review, three TODOs were located. The plan, lowkey, is to
> ratify them — pending your call."*

> **Gen-Alpha Claude (tutorial flavor — glosses on first use):**
> *"read the file. 3 TODOs in there. wild. want me to handle 'em rq (= right
> quick)?"*

> *Made by Gen-Zs and millennials. Not endorsed by or representative of
> actual Gen Alpha.*

### Toronto-mans

> **Plain Claude:**
> *"I read the file. Found three TODOs. Want me to address them now?"*

> **Toronto-mans Claude (mans flavor):**
> *"Mans read the scroll. Three TODOs in there still. Drizzy energy on the
> cleanup if you want me to handle 'em rq."*

> *This skill is a fictional caricature of a narrow Drake-era pop-cultural
> register, not a representation of real Multicultural Toronto English. The
> `safety_warnings` preservation toggle is hard-locked on and cannot be
> disabled. See `.claude/skills/toronto-mans/SKILL.md` §7 for the full
> stereotype-drift guardrails.*

## Sibling skills

All skills share the same architecture: a self-contained folder with
`SKILL.md`, a `*.config` file for per-repo settings, and an `examples.md`
corpus. They are installed and activated independently.

| Skill | Register | Default flavor | Other flavors |
|---|---|---|---|
| `shakespeare` | Early Modern English | `courtly` | `tavern`, `sonnet` |
| `pirate` | 18c. maritime caricature | `scurvy-dog` | `captain`, `drunk`, `shanty` |
| `gen-alpha` | internet-native ironic Gen-Alpha slang | `unhinged` | `corporate`, `tutorial` |
| `toronto-mans` | Toronto / Drake-era caricature (narrow) | `mans` | (single flavor in v1) |

If more than one is activated in the same session, the most recently
invoked one wins — no fusion or blending.

## Install

### Per-repo install (everyone working in this repo gets it)

Copy the skill folder(s) you want into the target repo's
`.claude/skills/`:

```bash
# from your target repo's root
mkdir -p .claude/skills

# just shakespeare
cp -r /path/to/shakespeare/.claude/skills/shakespeare .claude/skills/

# just pirate
cp -r /path/to/shakespeare/.claude/skills/pirate .claude/skills/

# just gen-alpha
cp -r /path/to/shakespeare/.claude/skills/gen-alpha .claude/skills/

# just toronto-mans
cp -r /path/to/shakespeare/.claude/skills/toronto-mans .claude/skills/

# or all of them
cp -r /path/to/shakespeare/.claude/skills/{shakespeare,pirate,gen-alpha,toronto-mans} .claude/skills/
```

Or as a git submodule, or by cloning this repo and symlinking — whichever
fits your workflow.

### User-global install (just you, every repo)

Copy the folder(s) into your personal Claude Code skills directory:

```bash
mkdir -p ~/.claude/skills
cp -r /path/to/shakespeare/.claude/skills/shakespeare ~/.claude/skills/
cp -r /path/to/shakespeare/.claude/skills/pirate ~/.claude/skills/
cp -r /path/to/shakespeare/.claude/skills/gen-alpha ~/.claude/skills/
cp -r /path/to/shakespeare/.claude/skills/toronto-mans ~/.claude/skills/
```

## Activation

Each skill activates two ways.

### 1. Trigger phrase (no setup)

Once a skill's folder is installed, say any of its trigger phrases in a
session and it loads and persists for the rest of the session:

- **Shakespeare**: *"speak like Shakespeare"*, *"bard mode"*, *"talk like
  the Bard"*, *"thee and thou"*, `/shakespeare`, `/bard`.
- **Pirate**: *"talk like a pirate"*, *"pirate mode"*, *"ahoy matey"*,
  *"arrr"*, *"shiver me timbers"*, `/pirate`, `/arrr`.
- **Gen-Alpha**: *"talk like gen alpha"*, *"gen alpha mode"*, *"go
  skibidi"*, *"skibidi mode"*, `/gen-alpha`, `/genalpha`.
- **Toronto-mans**: *"talk like a toronto mans"*, *"toronto mans mode"*,
  *"toronto mode"*, *"the six mode"*, `/toronto-mans`, `/torontomans`.

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

To override the configured flavor without editing the config (e.g. you want
sonnet but the team voted courtly), append `Default flavor: sonnet` to the
snippet above.

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

Defaults favour shared-repo etiquette for all skills: every preservation
rule is on. Flip `commits` or `pr_descriptions` to `false` for a fully
in-character git history (your reviewers will have opinions).

After editing any config mid-session, say *"reload <skill> config"* so
Claude re-reads it. New sessions read configs automatically.

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
    └── examples.md
```

The `.claude/skills/<persona>/` files are **generated** from canonical
source at `rules/<persona>/` by `scripts/render.py`. To modify a skill,
edit the `rules/` source and re-run `scripts/render.py`. See
`CONTRIBUTING.md` for the workflow.

## Credits

Pattern borrowed from [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman).
Voices borrowed from a man who has been dead 410 years and still writes
better than most of us; from a fictional register that never really existed
but has outlived most that did; and from internet-meme culture, parodied by
people too old to be representative of it.
