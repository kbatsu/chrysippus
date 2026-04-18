# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

_(nothing yet)_

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

[Unreleased]: https://github.com/kbatsu/chrysippus/compare/v0.6.0...HEAD
[0.6.0]: https://github.com/kbatsu/chrysippus/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/kbatsu/chrysippus/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/kbatsu/chrysippus/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/kbatsu/chrysippus/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/kbatsu/chrysippus/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/kbatsu/chrysippus/releases/tag/v0.1.0
