# Contributing to chrysippus

Thanks for considering a contribution. This repo ships persona "skills" for
Claude Code (and other agents) — registers that change how Claude speaks
without changing what it does. Most contributions fall into one of three
buckets: bug fixes, lexicon updates, and new personas.

## Before you start

- All persona content here is **caricature**, not authentic dialect. Read each
  skill's `instructions.md` guardrails before proposing additions to its
  lexicon. PRs that violate the guardrails (e.g., adding excluded loanwords,
  adding ethnic-coded accents, adding slurs) will be closed.
- The repo follows the [Contributor Covenant](CODE_OF_CONDUCT.md) Code of
  Conduct. Be civil; assume good faith.

## Source-of-truth pattern

The canonical persona content lives in `rules/<persona>/`. The generator
at `scripts/render.py` produces three classes of output:

1. **Fully generated files** (every byte rendered):
   `.claude/skills/<persona>/`, `AGENTS.md`, `GEMINI.md`, `.cursor/rules/`,
   `.windsurfrules`, `CONVENTIONS.md`, `.clinerules`, `commands/personas.md`,
   `agents/dramaturg.md`. Do not edit by hand — your changes will be
   overwritten on the next render.

2. **Marker-injected zones** in mostly-hand-written files. Look for
   marker comments like `<!-- chrysippus:<id> BEGIN -->` /
   `<!-- chrysippus:<id> END -->` (HTML-comment style for `.md`/`.mdc`
   files; `# chrysippus:<id> BEGIN` for shell/YAML). Content **between**
   the markers is auto-generated; content **outside** the markers is
   yours to edit. Files with marker zones today: `README.md`,
   `docs/index.md`, `docs/personas/index.md`, `docs/subagents.md`,
   `docs/install/claude-code.md`, `docs/install/index.md`,
   `hooks/activate.sh`, `hooks/session-start.sh`.

3. **Hand-written files** (untouched by the generator):
   `commands/<persona>.md`, `agents/<persona>-reviewer.md`,
   `docs/personas/<persona>.md`, `CLAUDE.md`, `CONTRIBUTING.md`, etc.
   When you add a new persona, create the per-persona ones manually
   (the test suite enforces their existence).

After editing anything in `rules/`, run:

```bash
scripts/render.py
```

CI runs `scripts/render.py --check` and will fail your PR if generated
files drift from source OR if a marker zone in a consumer file no longer
matches what the generator would produce.

The generator is Python 3.10+ stdlib-only (no PyPI dependencies). To run
it locally you need only a Python interpreter.

## Bug fixes

1. Open an issue describing the misbehavior with a transcript snippet.
2. PR with the fix in `rules/<persona>/instructions.md` and regenerated
   outputs. Use a Conventional Commit subject (`fix(persona): …`) so
   release notes are easy to assemble.

## Lexicon updates

`rules/gen-alpha/lexicon.md` ages out fast (6–18 month half-life). Quarterly
PRs adding/removing terms are welcome.

For each term:

- Add it under the appropriate category.
- Include a 1-line gloss for use by the `tutorial` flavor.
- If removing a stale term, explain why in the PR description and commit
  message ("ohio aged out, replaced by …").

## Adding a new persona

New personas default to **catalog tier** (`featured: false` in
`_meta.json`) — they appear in tables and dropdowns but not in the
landing-page demos. Promotion to **featured tier** is a maintainer act
that requires hand-writing demo prose. The cap on featured personas is 5.

### Catalog-tier persona (default)

Touch only these files. Everything else (README tables, install pages,
slash commands, subagent reviewers, hooks allow-list, dramaturg skills
list, `commands/personas.md`) auto-updates when you run
`scripts/render.py`.

1. **Discuss in an issue first** — we'd rather not have ten half-baked
   personas.
2. Create `rules/<new-persona>/_meta.json` with required fields:
   `name`, `version`, `description`, `register_short` (one-line summary
   used in tables), `triggers` (non-empty list), `flavors` (non-empty
   list with exactly one having `"default": true`), `preserve_defaults`.
   Optional: `featured` (default `false`), `preserve_locked`,
   `config_extra_notes`. `load_meta()` validates the schema and fails
   loudly on typos.
3. Create `rules/<new-persona>/instructions.md` — full register rules.
   Include a `## Stereotype-drift guardrail` section listing what the
   persona must **never** do, with reasons.
4. Create `rules/<new-persona>/examples.md` — at least 5 worked
   before/after examples.
5. (optional) Create `rules/<new-persona>/lexicon.md` if the persona
   borrows specific vocabulary that benefits from per-term provenance.
6. Create `commands/<new-persona>.md` — the slash-command activation
   file. Hand-written because it carries register-specific guidance
   (lexicon mentions, hard-locks, danger-combo notes, etc.). Follow
   the pattern of any existing command file.
7. Create `agents/<new-persona>-reviewer.md` — the reviewer subagent.
   Hand-written for the same reason. Frontmatter must include
   `skills: [<new-persona>]`. The `TestHandWrittenPerPersonaFiles`
   test in `tests/test_render.py` enforces (6) and (7).
8. Create `docs/personas/<new-persona>.md` — the per-persona docs page.
9. Add one nav line to `mkdocs.yml` under `Personas:`.
10. Run `scripts/render.py` to regenerate everything else and run
    `scripts/ci.sh`.
11. Commit. CI gates: `scripts/render.py --check` (drift) +
    `scripts/ci.sh` (tests + JSON + shell syntax).

### Promotion to featured tier (maintainer-only)

Featured personas appear in the landing-page demo blockquotes
(`docs/index.md`) and any per-persona prose blocks elsewhere. The
landing demos are hand-written featured-only prose — they're not
auto-generated.

To promote a catalog persona to featured:

1. Confirm the cap (≤5 featured) — current featured set:
   `shakespeare`, `pirate`, `gen-alpha`, `toronto-mans`, `ontario-bud`.
   If at the cap, demote another persona first (set `featured: false`
   and remove its hand-written demo prose from `docs/index.md` and
   `README.md`).
2. Set `"featured": true` in `rules/<persona>/_meta.json`.
3. Hand-write demo prose for `docs/index.md` Demo 1 (self-introduction)
   and Demo 2 (bug review) blockquotes.
4. Run `scripts/render.py` and verify the persona appears in landing
   tables.
5. CLAUDE.md is hand-edited; if the new persona is auto-activated in
   this repo, update CLAUDE.md's "Communication style" section.

## Commit messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):
`feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`, `ci:`, `lexicon:`.
Scope to a persona where applicable: `feat(pirate): add captain flavor`.

## Running tests locally

```bash
scripts/ci.sh          # full CI — render check, tests, JSON validation, shell syntax
tests/run.sh           # just the unit tests
tests/run.sh -v        # verbose unit tests
python3 -m unittest tests.test_render          # one module
```

Tests are Python 3 stdlib only — no PyPI deps needed.

## Pull request checklist

- [ ] `scripts/render.py` run; generated files match source (CI gate: `scripts/render.py --check`).
- [ ] PR title is a Conventional Commit (`feat:` / `fix:` / `docs:` / `chore:` / `lexicon:` …).
- [ ] Tests added for new generator logic; existing tests still pass (`scripts/ci.sh`).
- [ ] If adding a persona or flavor: README updated, demo added, rubric
      stub added at `evals/rubrics/<persona>.yml`.
- [ ] If touching guardrails: rationale documented in PR description, and
      corresponding `evals/rubrics/<persona>.yml` `forbidden_tokens` updated.

## Releases

Maintainers only — see `RELEASING.md`.
