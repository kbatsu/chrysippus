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

The canonical persona content lives in `rules/<persona>/`. The files at
`.claude/skills/<persona>/`, `AGENTS.md`, `GEMINI.md`, `.cursor/rules/`,
`.windsurfrules`, `CONVENTIONS.md`, and `.clinerules` are **generated** by
`scripts/render.py`. Do not edit them by hand — your changes will be
overwritten on the next render.

After editing anything in `rules/`, run:

```bash
scripts/render.py
```

CI runs `scripts/render.py --check` and will fail your PR if generated files
drift from source.

The generator is Python 3.10+ stdlib-only (no PyPI dependencies). To run it
locally you need only a Python interpreter.

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

1. Discuss in an issue first — we'd rather not have ten half-baked personas.
2. Create `rules/<new-persona>/_meta.yml` and `rules/<new-persona>/instructions.md`
   following the pattern of existing personas.
3. Include a `## Stereotype-drift guardrail` section in `instructions.md`
   listing what the persona must **never** do, with reasons.
4. Add at least 5 worked before/after examples for completion summaries.
5. Run `scripts/render.py` and commit the regenerated outputs.
6. Update `README.md` with a demo block.

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
