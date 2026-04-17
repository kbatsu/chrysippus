# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `rules/<persona>/` source-of-truth directory holding canonical
  `_meta.json` + `instructions.md` + `examples.md` for each persona.
- `scripts/render.py` — Python 3 stdlib-only generator that walks `rules/`
  and emits `.claude/skills/<persona>/{SKILL.md, <persona>.config, examples.md}`.
- `scripts/render.py --check` — CI gate that fails on any drift between
  generated output and committed `.claude/skills/` files.
- `config_extra_notes` field in `_meta.json` for persona-specific warnings
  in generated `.config` files (used by pirate's drunken-safety-warning combo).

### Changed

- `.claude/skills/shakespeare/{SKILL.md, shakespeare.config}` and
  `.claude/skills/pirate/pirate.config` are now generated from `rules/`
  rather than hand-edited. Behaviour unchanged; format normalised.

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

[Unreleased]: https://github.com/kbatsu/chrysippus/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/kbatsu/chrysippus/releases/tag/v0.1.0
