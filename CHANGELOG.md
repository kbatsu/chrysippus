# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed — production review pass

A deep code review surfaced two real bugs and a clutch of doc/robustness
issues. All fixed; 8 new regression tests added (49 tests total, up from 41).

**Bugs**:

- `scripts/render.py` `--check` could not detect orphaned committed files.
  If a persona was removed from `rules/`, the stale `.claude/skills/<persona>/`
  and `.cursor/rules/<persona>.mdc` files would pass the drift check
  unnoticed. Added `find_orphans()` plus an enumeration of
  `MANAGED_OUTPUT_DIRS` (`.claude/skills/`, `.cursor/rules/`); `run_check`
  now flags any committed file in those dirs that wasn't produced by the
  current render. Three new tests cover clean-repo, synthetic-orphan, and
  unmanaged-dir cases.
- `scripts/render.py` `_activation_line` used `f"*{t!r}*".replace("'", '"')`
  to format trigger phrases in `AGENTS.md` / `GEMINI.md` / etc. This relied
  on `repr()` always emitting single quotes; `repr()` switches to double
  quotes when the string contains a single quote, defeating the replace and
  silently corrupting the output. Replaced with an explicit
  `_quote_trigger_for_markdown()` helper that escapes embedded double
  quotes. Four new tests cover the previously-broken paths.

**Documentation**:

- `README.md` install snippets used `/path/to/shakespeare/` as the source
  directory placeholder; corrected to `/path/to/chrysippus/` to match the
  actual repo name.
- `README.md` "Once `v0.6.0+` is published" qualifier was stale (v1.0.0 is
  current); reworded to "Available via the Claude Code marketplace:".
- `README.md` sibling-skills table description for `toronto-mans` still
  read "Toronto / Drake-era caricature (narrow)" — the v0.4.0 lexicon
  expansion explicitly removed all Drake/Raptors/Tim Hortons references.
  Updated to "Toronto / MTE caricature (Patois + AAVE borrows)".
- `README.md` documented a `Default flavor: sonnet` override mechanism
  appended to the CLAUDE.md snippet, but no skill actually parses such a
  directive. Replaced with an accurate description of the trigger-phrase
  flavor switch (`"sonnet flavor"`) and config-file edits.
- `CLAUDE.md` heading included "(skills repo, currently dir-named
  `shakespeare`)" — internal scaffolding from the in-progress directory
  rename. Removed; ships clean to downstream Claude Code installs.

**Robustness**:

- `scripts/render.py` `render_config`: simplified the `HARD-LOCKED`
  comment-suffix logic from a brittle `lstrip(" —")` pattern to an
  explicit conditional. New regression test covers the
  empty-base-comment path.
- `scripts/render.py` `_persona_table_row`: removed redundant outer
  parentheses.
- `scripts/render.py` `load_meta`: dropped unused `_src_dir` field on
  the meta dict.
- `scripts/render.py` docstring: updated "Python 3.8+" claim to
  "Python 3.10+" — matches what CI actually exercises.
- `hooks/session-start.sh`: corrected misleading "trim whitespace; take
  first non-empty line" comment to accurately describe the
  strip-all-whitespace + cap-at-64-bytes + allow-list-validate behavior.
- `.github/workflows/ci.yml`: shellcheck job now also scans `scripts/`
  and `tests/`, not only `hooks/`. (Closes the gap where the local
  `scripts/ci.sh` was stricter than CI.)
- `.github/workflows/ci.yml`: removed `continue-on-error: true` from the
  markdownlint job — the linter is now load-bearing on PRs.
- `.github/workflows/release.yml`: error message in CHANGELOG-extraction
  step now goes to stderr (was stdout, getting mixed into the would-be
  `release-notes.md`). The script also writes its output via `pathlib`
  instead of via shell-redirect, so a partial / failed run no longer
  leaves a corrupt `release-notes.md` lingering.
- `.github/workflows/release.yml`: removed unused `id: changelog` and
  `id: sha` step ids.
- New `.markdownlint.json` config disables a small set of well-known
  noisy rules (line length, inline HTML, autolink-bare-URLs, etc.) so
  the now-blocking markdownlint step passes on the existing prose
  without false positives.

### Removed

- `PLAN.md` — the durable execution roadmap added in `v0.1.0` and kept in
  sync through each phase. Scope achieved with the `v1.0.0` release;
  `CHANGELOG.md` is now the authoritative history. Any forward-looking
  items are tracked as "Deferred to follow-up" entries in recent release
  notes, or in GitHub issues.
- References to `PLAN.md` cleaned up in `CLAUDE.md`, `RELEASING.md`,
  `evals/README.md`, and `.github/workflows/ci.yml`.

## [1.0.0] — 2026-04-17 — first public release

### Added — docs site + polish (Phase 8)

**`docs/` content for mkdocs-material**:
- `docs/index.md` — landing page with quickstart and table of personas.
- `docs/install/` — per-agent install pages (claude-code, cursor,
  agents-md [Codex/Cline], aider, windsurf, gemini) plus overview.
- `docs/personas/` — per-persona pages with demo, flavor matrix,
  preservation rules, and guardrails for all four skills.
- `docs/extending.md` — step-by-step guide for adding a new persona,
  adding a flavor, or refreshing a lexicon.
- `docs/security.md` — supply-chain posture, hook model, SHA256
  verification, prompt-injection considerations.

**Static site**:
- `mkdocs.yml` — mkdocs-material config with dark/light theme toggle,
  navigation, search.
- `.github/workflows/docs.yml` — on push-to-main touching `docs/` or
  `mkdocs.yml`, builds the site and deploys to GitHub Pages.
  Site lives at `https://kbatsu.github.io/chrysippus/`.

**README polish**:
- Badges at top: CI status, latest release, MIT license, docs site link.
- Quickstart section at top with one-command install for Claude Code and
  file-copy instructions for each other agent.
- Project title updated from `shakespeare` to `chrysippus` to match the
  final repo name.

### Bumped

- `plugin.json` and `marketplace.json` → `1.0.0`.
- CHANGELOG → `[1.0.0]`.

### Notes

This is the first public release. All 8 planned phases (foundation →
multi-agent → Claude distribution → quality → polish) have shipped. The
eval runner remains deferred (rubrics are locked in at
`evals/rubrics/<persona>.yml`; the runner that calls the Claude API to
grade outputs will come in a later minor release).

## [0.7.0] — 2026-04-17

### Added — quality stack (Phase 7)

**Tests** (`tests/`) — 41 unit tests across four modules. Python 3 stdlib
only (`unittest`). Runs via `tests/run.sh`.

- `tests/test_render.py` — render round-trip, check-drift gate,
  per-persona SKILL.md/config presence, preserve_locked marker, cursor
  MDC structure, multi-agent file presence, render module unit tests.
- `tests/test_manifest.py` — plugin.json + marketplace.json schema
  validation, version ↔ CHANGELOG sync check, component-path existence.
- `tests/test_lexicon.py` — lexicon presence, toronto-mans guardrail
  integrity (Patois expletives stay in Excluded section, attribution
  paragraph present, safety_warnings hard-locked), gen-alpha disclaimer
  presence, pirate stereotype-drift keywords, `_meta.json` schema.
- `tests/test_hooks.py` — shell script syntax, executable bit,
  `hooks/activate.sh` behavior against a tmpdir-mocked project,
  `hooks/session-start.sh` output when state set / missing / invalid.

**CI** (`.github/workflows/`):

- `ci.yml` — on PR + push-to-main: runs unit tests on Python 3.10 + 3.12,
  `render.py --check` drift gate, shellcheck on hooks, markdownlint on
  hand-written docs, JSON manifest validation. Fails PRs on any
  regression.
- `release.yml` — on `v*` tag push: verifies `plugin.json` version
  matches the tag, extracts the CHANGELOG section for the release,
  builds a git-archive tarball, computes SHA256, creates a GitHub Release
  with the tarball + checksum attached. Release notes sourced from the
  CHANGELOG entry.
- `dependabot.yml` — weekly GitHub Actions update sweeps.

**Local CI** — `scripts/ci.sh` runs the same checks locally (render drift,
unit tests, JSON validation, shell syntax, optional shellcheck). Useful
before opening a PR.

**Evals scaffold** (`evals/`):

- `evals/README.md` — framing, layout, contribution guidance.
- `evals/rubrics/<persona>.yml` — per-persona grading rubrics with
  required_tokens, forbidden_tokens, preservation_checks, and
  flavor_specific requirements. Toronto-mans rubric includes the full
  guardrail forbidden list (Patois expletives, fake-accent respellings,
  real-person refs, brand refs, gang-coded neighborhoods).

**Eval runner is deferred** — the Python script that actually calls the
Claude API to generate and grade outputs is deferred (rubric format is
locked in so the runner can be added without rubric churn).

### Changed

- `plugin.json` and `marketplace.json` bumped to `0.7.0`.
- CHANGELOG bumped to `[0.7.0]`.

## [0.6.0] — 2026-04-17

### Added — Claude Code distribution (Phase 6)

Marketplace-installable plugin layer around the skills and multi-agent
files. Users can install the full persona collection with two commands:

```
claude plugin marketplace add kbatsu/chrysippus
claude plugin install chrysippus@chrysippus
```

**New files**:
- `.claude-plugin/plugin.json` — plugin manifest (name, version, skills,
  commands, agents, hooks paths).
- `.claude-plugin/marketplace.json` — marketplace registration (owner,
  plugin source = `kbatsu/chrysippus` on GitHub, version).
- `commands/<persona>.md` — one slash command per persona, plus a repo-wide
  `commands/personas.md` that lists installed personas. Auto-namespaced by
  Claude Code as `/chrysippus:<persona>`. Flavor can be passed as an arg
  (e.g., `/chrysippus:pirate shanty`). Sub-actions (*plain*, *reload*,
  *flavor switch*) are natural-language triggers in the skill itself, not
  separate commands — the Claude Code slash-command `:` is reserved for
  plugin namespacing and cannot be user-extended for sub-commands.
- `agents/<persona>-reviewer.md` (4 files) — per-persona PR review
  subagents. Each declares `skills: [<persona>]` so the skill's rules
  load automatically when the subagent runs (subagents do not inherit
  parent-session skills per Claude Code spec).
- `agents/dramaturg.md` — meta-agent that audits persona rule-adherence.
  Declares all four personas in its `skills:` list so it can read any
  of their rule sets. Speaks plainly (no persona voice).
- `hooks/hooks.json` — declares the `SessionStart` hook.
- `hooks/session-start.sh` — reads `.claude/personas/active` (if present)
  and emits a persona auto-activation instruction. Allow-list validated;
  no network calls; `set -euo pipefail`; under 100 LOC.
- `hooks/activate.sh` — user-facing opt-in helper. Sets / clears the
  per-project active-persona state file. Idempotent, allow-list validated,
  no network calls.

### Changed

- README adds marketplace install section, slash-command table, reviewer
  subagent table, and SessionStart hook documentation.
- CLAUDE.md distinguishes generated files (under `rules/`-driven pipeline)
  from hand-written plugin distribution files (`.claude-plugin/`,
  `commands/`, `agents/`, `hooks/`).

### Deferred to later phases

- Per-session state (keying `.claude/personas/active-<session-id>`) — v1
  uses a single file per project. Works for single-terminal flows; may
  collide in multi-terminal use. Tracked as follow-up.
- Claude Code SDK / MCP-server wrapper — out of scope.

## [0.5.0] — 2026-04-17

### Added — multi-agent reach (Phase 5)

The same canonical rules at `rules/<persona>/` are now rendered into
formats for multiple AI coding agents beyond Claude Code. `scripts/render.py`
emits all targets in a single pass; `--check` diffs every generated file.

**New generated outputs**:
- `AGENTS.md` — universal convention read by Codex, Cline, Aider, and
  other agents that follow the `AGENTS.md` standard. Concatenates all
  personas with activation cheat-sheet and full per-persona instructions.
- `GEMINI.md` — for Gemini CLI. Same content as `AGENTS.md`; duplicated
  rather than shimmed so Gemini doesn't need to follow a cross-reference.
- `CONVENTIONS.md` — for Aider, as project conventions.
- `.windsurfrules` — for Windsurf (Codeium).
- `.clinerules` — for Cline.
- `.cursor/rules/<persona>.mdc` — one MDC rule file per persona for
  Cursor IDE. Includes Cursor-specific frontmatter (`description`,
  `globs`, `alwaysApply`).

Kiro IDE support deferred — marked `coming soon` in README pending a
stable rule-format spec.

### Changed

- `scripts/render.py` extensively refactored to support multiple output
  targets. Now emits 23 output files for 4 personas (up from 11).
- `build_text_outputs` / `build_copy_outputs` separation introduced for
  cleaner check/diff logic.
- README, CLAUDE.md updated with multi-agent support table and extended
  "generated files" list.

## [0.4.0] — 2026-04-17

### Changed — `toronto-mans` guardrails loosened for public release

The `toronto-mans` skill was shipped in v0.3.0 with a deliberately narrow
lexicon that excluded Patois loanwords and AAVE markers entirely. That
version felt evasive — a register called "toronto-mans" that excluded the
vocabulary that makes Toronto-mans speech distinctive. This release
loosens the lexicon to Level 3 (per the design discussion): full roadman
vocabulary including Patois loanwords and AAVE markers, with strict
guardrails held on the most contested territory.

**Now allowed** (each tagged with provenance in `lexicon.md`):
- **Patois loanwords** (origin: Jamaican Patois): wagwan, ting, yute,
  gyal, mandem, bredren, peng, bare, nuff, par / parring.
- **AAVE markers** (origin: African American Vernacular English): no cap,
  bussin, finna, deadass, based, slaps, bet, W / L.

**Newly excluded** (beyond what was already out):
- **Real-person references**: Drake, Drizzy — removed from the lexicon
  entirely. No putting words in real people's mouths.
- **Brand references**: Tim Hortons, double-double, Toronto Raptors — all
  removed. The register stands on vocabulary, not commercial touchstones.
- **Specific gang-coded neighborhoods**: Jane and Finch, Jungle, Rexdale,
  Regent Park, etc. — excluded for real-violence associations.

**Held firm** (non-negotiable regardless of how loose the rest gets):
- **All Patois expletives** (bumbaclot, bloodclaat, raasclaat, pussyclaat,
  etc.) remain excluded.
- **Fake-accent respellings** of standard English words remain excluded.
  The line: borrowing the Patois word *ting* is allowed; respelling *think*
  as *tink* is phonetic mockery of how a speaker sounds and is not.
- **Slurs, gang/drug/violence references, claims of authenticity** all
  remain excluded.
- **`safety_warnings` hard-lock** on the config remains.

### Added

- `rules/toronto-mans/lexicon.md` — new authoritative vocabulary file with
  per-term provenance tags (MTE / Patois / AAVE). Quarterly review cadence.
- **Attribution paragraph** prominently in `instructions.md` naming MTE,
  Jamaican Patois, broader Caribbean creoles, and AAVE as the sources the
  register borrows from. Explicitly states this skill does not claim
  ownership of the vocabulary or speak for those communities.
- README disclaimer expanded to reflect the new attribution and the
  exclusion of real-person / brand / gang-coded references.

### Changed

- `rules/toronto-mans/instructions.md` substantially rewritten for Level 3
  scope — §3 style rules updated with new allowed vocabulary categories,
  §6 examples rewritten, §7 stereotype-drift guardrail tightened to reflect
  the new exclusions.
- `rules/toronto-mans/examples.md` rewritten with new voice and updated
  anti-examples (§K) — Patois expletives / fake accents / brand refs /
  gang-coded neighborhoods / real-person mentions all appear in anti-examples.
- `rules/toronto-mans/_meta.json` bumped to `version: 0.2.0` internally;
  description rewritten to reflect new posture.

## [0.3.0] — 2026-04-17

### Added

- **`toronto-mans` persona skill** — single `mans` flavor; narrow Toronto /
  Drake-era pop-cultural caricature register. Vocabulary intentionally
  scoped to: "mans" as singular subject, sentence-final "still", Toronto
  place markers (the 6, the 6ix, the dot, Scarberia, the Annex), and
  Drake/Raptors/Tim Hortons cultural touchstones. **Explicitly excluded**:
  Patois loanwords, AAVE-marker terms claimed as identity, fake-accent
  respellings, gang/drug/violence references, slurs, claims of authenticity.
- **`preserve_locked` field** in `_meta.json` — render.py honours it by
  marking the listed preserve toggles as `HARD-LOCKED` in the generated
  `.config` file. Used by toronto-mans to lock `safety_warnings` to true:
  destructive-op confirmations and security warnings always render in
  plain English regardless of any config override.
- Stereotype-drift guardrails (hard rules, no exceptions) baked inline
  into `rules/toronto-mans/instructions.md` §7. No separate DISCLAIMER
  file or runtime surfacing — guardrails are part of the skill itself.

### Changed

- README, CLAUDE.md updated for `toronto-mans` install, activation,
  configuration, file layout, and self-edit guardrail file list.
- `scripts/render.py` extended with `preserve_locked` support.

## [0.2.0] — 2026-04-17

### Added

- **`gen-alpha` persona skill** with three flavors: `unhinged` (default,
  max-density slang + sentence fragments + lowercase), `corporate` (slang
  in formal business prose for register-collision comedy), and `tutorial`
  (parenthetical glosses on first use of each term per response).
- `rules/gen-alpha/lexicon.md` — refreshable vocabulary file, separate
  from instructions.md. Quarterly PR cadence.
- Self-aware disclaimer baked into the `gen-alpha` skill: *"Made by Gen-Zs
  and millennials. Not endorsed by or representative of actual Gen Alpha."*
- `rules/<persona>/` source-of-truth directory holding canonical
  `_meta.json` + `instructions.md` + `examples.md` for each persona.
- `scripts/render.py` — Python 3 stdlib-only generator that walks `rules/`
  and emits `.claude/skills/<persona>/{SKILL.md, <persona>.config, examples.md, [lexicon.md]}`.
- `scripts/render.py --check` — CI gate that fails on any drift between
  generated output and committed `.claude/skills/` files.
- `config_extra_notes` field in `_meta.json` for persona-specific warnings
  in generated `.config` files (used by pirate's drunken-safety-warning
  combo and gen-alpha's disclaimer).

### Changed

- `.claude/skills/shakespeare/{SKILL.md, shakespeare.config}` and
  `.claude/skills/pirate/pirate.config` are now generated from `rules/`
  rather than hand-edited. Behaviour unchanged; format normalised.
- README, CLAUDE.md, and CONTRIBUTING.md updated for the source-of-truth
  pattern and the new `gen-alpha` skill.

## [0.1.0] — 2026-04-17

Initial public snapshot. Captures the two hand-written persona skills plus the
full Tier-1 production foundation.

### Added

- `shakespeare` skill at `.claude/skills/shakespeare/` with `courtly` (default),
  `tavern`, and `sonnet` flavors.
- `pirate` skill at `.claude/skills/pirate/` with `scurvy-dog` (default),
  `captain`, `drunk`, and `shanty` flavors.
- `README.md` documenting both skills, install paths, and activation.
- `CLAUDE.md` activating shakespeare always-on and keeping pirate trigger-only,
  with a self-edit guardrail and precedence rule for coexistence.
- Foundation files: `LICENSE` (MIT), `NOTICE`, `.gitignore`, `.gitattributes`,
  `CONTRIBUTING.md`, `SECURITY.md` (with hook-security disclosure),
  `CODE_OF_CONDUCT.md` (Contributor Covenant 2.1), `AUTHORS`, `CODEOWNERS`,
  `RELEASING.md`.
- `PLAN.md` — durable execution roadmap covering Phases 1–8.

### Changed

- Repo renamed from `shakespeare` to `chrysippus` to reflect that it now hosts
  multiple persona skills. The Stoic philosopher's name is a deliberately
  ironic choice for a repo of theatrical voices.

[Unreleased]: https://github.com/kbatsu/chrysippus/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/kbatsu/chrysippus/compare/v0.7.0...v1.0.0
[0.7.0]: https://github.com/kbatsu/chrysippus/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/kbatsu/chrysippus/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/kbatsu/chrysippus/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/kbatsu/chrysippus/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/kbatsu/chrysippus/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/kbatsu/chrysippus/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/kbatsu/chrysippus/releases/tag/v0.1.0
