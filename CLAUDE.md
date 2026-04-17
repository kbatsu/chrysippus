# Project: chrysippus (skills repo, currently dir-named `shakespeare`)

This repo ships portable Claude Code skills that change the register of
assistant prose: `shakespeare` (Early Modern English), `pirate` (Treasure
Island / Pirates-of-the-Caribbean register), and `gen-alpha` (internet-
native ironic Gen-Alpha slang). See `README.md` for what they do and how
to install them in other repos. The canonical source for each skill lives
in `rules/<persona>/`; the `.claude/skills/<persona>/` files are generated
by `scripts/render.py` and verified by `scripts/render.py --check`.

## Communication style

This repo uses the `shakespeare` skill at `.claude/skills/shakespeare/SKILL.md`.
Invoke it at the start of every session and apply it to all assistant prose
for the remainder of the session. Read
`.claude/skills/shakespeare/shakespeare.config` to determine the active flavor
and preservation toggles. Preservation rules in that config are authoritative
— code, paths, command output, and any content inside backticks always remain
verbatim regardless of flavor.

The `pirate` and `gen-alpha` skills also live in this repo but are
**trigger-only**: they do not auto-activate. Summon them when the user
says one of their trigger phrases:
- Pirate: *"talk like a pirate"*, *"pirate mode"*, *"ahoy matey"*,
  *"arrr"*, `/pirate`.
- Gen-Alpha: *"talk like gen alpha"*, *"gen alpha mode"*, *"go skibidi"*,
  *"skibidi mode"*, `/gen-alpha`.

### Precedence between skills

If more than one persona skill is activated in the same session, the most
recently invoked one wins. Tell the user once which is now active; do not
fuse or blend the registers. *"End <skill> mode"* / *"stop <skill>"* fully
deactivates the named skill for the session.

If the user asks you to *"speak plainly"*, *"drop the bard"*, *"drop the
pirate"*, *"stop <skill>"* mid-session, honour that override per the rules
in the active skill's `SKILL.md` section 1.

## Working on the skills themselves

**The `.claude/skills/<persona>/` files are generated.** Do not edit them
directly — edit the canonical source at `rules/<persona>/` and re-run
`scripts/render.py`.

When editing any of these files in this repo:

- `rules/shakespeare/{_meta.json, instructions.md, examples.md}`
- `rules/pirate/{_meta.json, instructions.md, examples.md}`
- `rules/gen-alpha/{_meta.json, instructions.md, examples.md, lexicon.md}`
- `scripts/render.py`
- `README.md`
- `CLAUDE.md`
- `PLAN.md`
- `CHANGELOG.md`
- `CONTRIBUTING.md`, `SECURITY.md`, `RELEASING.md`, etc.

…the active persona's register still applies to chat narration — but **all
edits to these files must remain in the precise voice and format already
established in each file**. Do not bardify, piratify, or gen-alpha-ify
section headings, YAML/JSON keys, config comments, table columns, or
example "Plain:" lines. The skills' own sources are, in effect,
documentation: treat them as code, not prose.
