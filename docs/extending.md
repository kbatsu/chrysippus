# Extending chrysippus

How to add a persona, add a flavor, or refresh a lexicon.

## Source-of-truth pattern

All rendered files (`.claude/skills/<persona>/`, `AGENTS.md`, `GEMINI.md`,
`.cursor/rules/`, etc.) are **generated** by `scripts/render.py` from
canonical source at `rules/<persona>/`.

**Never edit generated files directly.** CI runs `scripts/render.py --check`
and will reject PRs where generated files have drifted.

## Adding a new persona

Let's say you want to add a `valley-girl` persona.

### 1. Discuss it first

Open an issue describing the register, its flavors, and the stereotype-drift
guardrails you'll put in place. We'd rather not have ten half-baked personas.

### 2. Create the canonical source

```bash
mkdir -p rules/valley-girl
```

Create three required files:

**`rules/valley-girl/_meta.json`**:

```json
{
  "name": "valley-girl",
  "version": "0.1.0",
  "description": "...",
  "triggers": [
    "talk like a valley girl",
    "valley girl mode",
    "/valley-girl"
  ],
  "flavors": [
    {"name": "classic", "description": "...", "default": true}
  ],
  "preserve_defaults": {
    "commits": true,
    "pr_descriptions": true,
    "code_comments": true,
    "safety_warnings": true,
    "errors_verbatim": true
  }
}
```

**`rules/valley-girl/instructions.md`** — the canonical persona rules.
Follow the section structure used by existing personas:

1. *(optional)* Attribution paragraph if the register borrows from a
   specific community
2. Activation and persistence
3. Read the config first
4. Style rules (pronouns, verb forms, vocabulary, cadence)
5. Flavors
6. Preservation rules (table)
7. Worked examples (before/after)
8. Edge cases and conflicts
9. Stereotype-drift guardrail (hard rules, no exceptions)

**`rules/valley-girl/examples.md`** — extended before/after corpus, copied
through verbatim by render.py.

Optionally:

- **`rules/valley-girl/lexicon.md`** — if the register has a refreshable
  vocabulary, extract it here (pattern: `gen-alpha`, `toronto-mans`).

### 3. Regenerate

```bash
python3 scripts/render.py
```

This creates `.claude/skills/valley-girl/`, a `.cursor/rules/valley-girl.mdc`,
and updates `AGENTS.md` / `GEMINI.md` / `CONVENTIONS.md` / `.windsurfrules` /
`.clinerules`.

### 4. Add plugin-distribution files (hand-written, not generated)

- `commands/valley-girl.md` — slash command template
- `agents/valley-girl-reviewer.md` — subagent (must declare `skills: [valley-girl]`)
- Update `agents/dramaturg.md` to include the new persona in its `skills:` list
- Update `hooks/activate.sh` allow-list to include the new persona
- Update `hooks/session-start.sh` allow-list

### 5. Update docs

- Add demo to `README.md` sibling-skills table
- Add entry to `docs/personas/index.md`
- Create `docs/personas/valley-girl.md`
- Add rubric skeleton at `evals/rubrics/valley-girl.yml`

### 6. Update tests

- Extend `tests/test_lexicon.py` with persona-specific assertions if the
  register has guardrails that can be checked mechanically.
- Use a Conventional Commit subject (`feat(<persona>): introduce …`) so
  the next release tag's commit-log section reads cleanly.

### 7. Run CI locally

```bash
scripts/ci.sh
```

If everything's green, open a PR.

## Adding a flavor to an existing persona

Let's say you want to add a `hamlet` flavor to `shakespeare`.

### 1. Edit `rules/shakespeare/_meta.json`

Add an entry in `flavors`:

```json
{
  "name": "hamlet",
  "description": "moody, brooding, existential; soliloquy-adjacent even in small talk"
}
```

### 2. Edit `rules/shakespeare/instructions.md`

Add a `### \`hamlet\`` subsection under `## 4. Flavors` describing the
register differences and showing a brief example.

### 3. Edit `rules/shakespeare/examples.md`

Add worked examples under each situation category for the new flavor.

### 4. Regenerate and update

```bash
python3 scripts/render.py
```

Update `README.md`, `docs/personas/shakespeare.md`, and `evals/rubrics/shakespeare.yml`
if the new flavor has specific required/forbidden tokens.

## Updating a lexicon

Lexicons age out fast (esp. `gen-alpha` — 6–18 month half-life). Quarterly
review is the suggested cadence.

### 1. Edit the lexicon

Edit `rules/<persona>/lexicon.md`. Keep the category structure. For each
term:

- Include provenance in a parenthetical tag: `(origin: Jamaican Patois)`,
  `(origin: AAVE)`, etc.
- Include a 1-line gloss usable by the `tutorial` flavor.
- If removing a stale term, explain why in the PR description and commit
  message (*"ohio aged out, replaced by ..."*).

### 2. Regenerate

```bash
python3 scripts/render.py
```

The updated lexicon is copied through to `.claude/skills/<persona>/lexicon.md`.

### 3. Update `evals/rubrics/<persona>.yml`

If added terms are worth tracking as register markers, add them to
`required_tokens`. If removed terms should be explicitly rejected, add to
`forbidden_tokens`.

### 4. PR

`lexicon:` conventional-commit scope is conventional:

```
lexicon(gen-alpha): quarterly refresh — add "6'7", remove "skibidi"
```

## Testing your changes

```bash
scripts/ci.sh                     # full local CI (render check, tests, JSON, shell)
tests/run.sh -v                   # just the unit tests, verbose
python3 scripts/render.py --check # just the render drift gate
```
