# Plan: productionize the personas repo + add `gen-alpha` and `toronto-mans` skills

> Living roadmap for taking this repo from prototype (two skills, no infrastructure)
> to a production-grade Claude Code persona collection with multi-agent reach,
> marketplace distribution, evals, CI, and polish.
>
> **Status**: approved 2026-04-17. Execution sequenced in phases, each tagged on completion.

---

## Context

The repo currently hosts two persona skills (`shakespeare`, `pirate`) plus a
`CLAUDE.md` and a `README.md`. It is **not yet a git repo**, has **no license**,
**no multi-agent support**, **no marketplace presence**, **no tests/evals**,
and **no CI**. Goal: take it to caveman-grade production with a full
distribution stack, multi-agent reach, security posture, and two new skills.

### Decisions already made

- **Scope**: all 5 tiers (foundation → multi-agent → Claude distribution → quality → polish).
- **`toronto-mans`**: build as-is with a strong disclaimer. The user has explicitly
  accepted the cultural-caricature risk; the plan must include robust guardrails
  and a prominent disclaimer surface.
- **`gen-alpha`**: build with multiple flavors (`unhinged` default, `corporate`, `tutorial`).
- **Repo strategy**: single repo, **named `chrysippus`** (lowercase, matching
  the GitHub repo). The Stoic philosopher who championed emotional restraint and
  rationality — a deliberately ironic name for a repo that ships highly affected
  character-voiced personas.
- **GitHub remote**: `git@github.com:kbatsu/chrysippus.git` (created 2026-04-17).

---

## The four skills after this work

| Skill | Status | Default flavor | Other flavors |
|---|---|---|---|
| `shakespeare` | exists | `courtly` | `tavern`, `sonnet` |
| `pirate` | exists | `scurvy-dog` | `captain`, `drunk`, `shanty` |
| `gen-alpha` | **new** | `unhinged` | `corporate`, `tutorial` |
| `toronto-mans` | **new** | `mans` | (single flavor for v1; expand later if warranted) |

### `gen-alpha` design

- **Register**: internet-native ironic Gen-Alpha slang (skibidi, rizz, fanum tax,
  sigma, ohio, no cap, bussin, mid, gyatt, NPC, brainrot, cooked, lowkey/highkey).
- **Source-of-truth lexicon** in `lexicon.md` — separated from `SKILL.md` so it
  can be refreshed annually without touching the skill rules. `SKILL.md` instructs
  Claude to read the lexicon on activation.
- **Flavors**:
  - `unhinged` (default) — full ironic Gen-Alpha. Maximum density of slang,
    sentence-fragments, all-lowercase by default, occasional emoji.
  - `corporate` — Gen-Alpha trying to be professional. Slang slipped into otherwise
    formal prose (*"Per my last email, the rizz of this proposal is undeniable."*).
    Comedy is in the register collision.
  - `tutorial` — every slang term it uses gets a brief parenthetical gloss the
    first time per response (*"this commit is bussin (= really good)"*) — for users
    who want the voice but also want to learn what the words mean.
- **Staleness curve documented**: `SKILL.md` notes the lexicon ages out fast (6–18
  months), points users at `lexicon.md` for community PR-able updates.
- **Self-aware disclaimer** in `SKILL.md` (also surfaced once in README and the
  marketplace listing): *"Made by Gen-Zs and millennials. Not endorsed by or
  representative of actual Gen Alpha."* Defuses the "how do you do, fellow kids"
  reading by naming what it is: a parody by adults, not authentic Gen-Alpha speech.

### `toronto-mans` design

- **Register**: Toronto/Multicultural-Toronto-English caricature, Drake-era
  pop-cultural reference points. **Acknowledged caricature, not dialect.**
- **Single flavor for v1**: `mans` (standard register).
- **Lexicon kept narrow and Toronto-specific** (avoids broader UK roadman / AAVE
  vocabulary):
  - Toronto place markers: the 6, the 6ix, the dot, Scarberia, the Annex.
  - Structural quirks: "mans" as singular subject ("mans gonna handle it"),
    "still" as sentence-final emphasis, "you done know".
  - Cultural references: Drake/Drizzy as touchstone (the philosophical/melancholic
    tone), the Raptors, Tim Hortons (sparingly).
  - **Explicitly excluded**: Patois loanwords (wagwan, ting, yute, gyal),
    AAVE-marker terms claimed as register identity, fake-accent respellings (no
    "ting" for "thing"), any borrowing from cultures we are not part of.
- **Hard guardrails in `SKILL.md`** (mirrors and exceeds pirate's stereotype-drift list):
  - Never use ethnic-coded accents or fake-respelling.
  - Never reference real living people beyond the Drake/Raptors cultural-touchstone level.
  - Never reference, joke about, or romanticise gang culture, drug trade, or violence.
  - Never use slurs of any kind.
  - Never claim authenticity — this is parody, declared as such.
  - **`safety_warnings: true` is hard-locked to true** (not configurable to false)
    — this skill's preservation of safety content is non-negotiable, given the
    heightened sensitivity.
- **No separate `DISCLAIMER.md` or runtime disclaimer surfacing** — guardrails
  baked directly into `SKILL.md` are the only mechanism. Decision: state-tracking
  for "first activation per session" is fragile across compaction and
  multi-session use; the inline guardrails are sufficient.

---

## Tier 1 — Foundation

### Standard project files

- `LICENSE` — MIT.
- `NOTICE` — copyright + acknowledgements (caveman pattern attribution, Anthropic
  Claude Code mention).
- `.gitignore` — Node, Python, OS junk, editor dirs, eval outputs, generated-rules outputs.
- `.gitattributes` — LF line endings everywhere; `*.md linguist-detectable=true`;
  `lexicon.md merge=union` for low-conflict community PRs.
- `CONTRIBUTING.md` — how to add a skill, how to add a flavor, how to PR a lexicon
  update, commit-message conventions.
- `SECURITY.md` — vulnerability reporting (email or GitHub Security Advisories),
  supported versions, supply-chain posture statement, and an explicit
  **hook-security disclosure**: hooks shipped in this plugin run unsandboxed at
  the user's shell privilege level. The `SessionStart` hook is opt-in via
  `hooks/install.sh`; users should read every hook script before installing.
  No network calls, no `eval`, < 100 LOC each, shellcheck-clean. SHA256 of
  release tarballs published in release notes.
- `CODE_OF_CONDUCT.md` — Contributor Covenant 2.1 standard text.
- `CHANGELOG.md` — Keep-a-Changelog format, seeded with `0.1.0` for what already exists.
- `AUTHORS` / `CODEOWNERS` — author attribution + review routing.
- `RELEASING.md` — release flow documentation.

### Git

- `git init`, set `main` as default branch, first commit captures current state,
  then a series of logical commits per tier.
- First **signed annotated tag** `v0.1.0` once Tier 1 ships.
- Branch protection on `main` (documented; user enables in GitHub UI later).

### Repo rename (one-time)

- Rename local directory `shakespeare/` → **`Chrysippus/`** (or `Janus/` as fallback).
- Why `Chrysippus`: Chrysippus of Soli (c. 279–206 BCE) led the Stoic school and
  championed emotional restraint and rationality. A deliberately ironic name for a
  repo whose entire purpose is to make Claude speak in highly affected,
  emotionally-charged character voices. The joke is the point; the name will age well.
- Capitalisation: `Chrysippus` (proper-noun cased) for the directory and the
  GitHub repo. The plugin/marketplace name can be lower-case `chrysippus` to match
  Anthropic's marketplace convention.
- Update all internal references: install paths in READMEs, snippets, `CLAUDE.md`,
  `AGENTS.md`, `GEMINI.md`, plugin manifests, command files, hook scripts.
- Document the rename in `CHANGELOG.md` (`### Changed — repo renamed from
  shakespeare to Chrysippus`).

---

## Tier 2 — Multi-agent reach (the linchpin)

### Source-of-truth pattern

The biggest risk in supporting 6+ agents is hand-maintaining 6 copies of the same
content. We solve it once with a **single source + generator**.

```
rules/
├── shakespeare/
│   ├── _meta.yml          # name, triggers, flavors, defaults, preservation toggles
│   └── instructions.md    # canonical persona rules (single source of truth)
├── pirate/
│   ├── _meta.yml
│   └── instructions.md
├── gen-alpha/
│   ├── _meta.yml
│   ├── instructions.md
│   └── lexicon.md         # extracted vocab, refreshable
└── toronto-mans/
    ├── _meta.yml
    ├── instructions.md
    └── DISCLAIMER.md

scripts/
├── render.sh              # walks rules/, emits per-agent files
├── lib/                   # render helpers (frontmatter, markdown ops)
└── check.sh               # CI: render --check; fails if generated files drift
```

`render.sh` outputs:

| Target | Path | Contents |
|---|---|---|
| Claude Code skill | `.claude/skills/<persona>/SKILL.md` | YAML frontmatter + instructions + lexicon (if any) |
| Claude Code config | `.claude/skills/<persona>/<persona>.config` | from `_meta.yml` defaults |
| Claude Code examples | `.claude/skills/<persona>/examples.md` | hand-curated; render copies it through |
| Codex / universal | `AGENTS.md` | concatenation of all personas with activation triggers |
| Gemini CLI | `GEMINI.md` | thin shim pointing to `AGENTS.md` (1-liner) |
| Cursor | `.cursor/rules/<persona>.mdc` | one rule file per persona, MDC frontmatter |
| Windsurf | `.windsurfrules` | concatenated, with section headers per persona |
| Aider | `CONVENTIONS.md` | terse summary, plain prose |
| Cline | `.clinerules` | similar to `.windsurfrules` |

**`AGENTS.md` for non-Claude tools, `CLAUDE.md` is its own first-class artifact.**
Per current Claude Code docs (verified 2026-04-17), Claude Code reads only
`CLAUDE.md` — it does **not** read `AGENTS.md`. So `CLAUDE.md` is generated as a
peer artifact (full content, Claude-specific paths and slash commands), and
`AGENTS.md` is generated separately for the convergent Codex / Cline / Aider
convention. Neither is subordinate to the other; both come from the same
canonical `rules/` source.

**Kiro**: research the format during execution; if specs aren't stable, mark
`coming soon` in docs and skip.

### CI gate

`check.sh` runs in CI and fails if any generated file differs from a fresh
`render.sh` run. This makes the generator the single source.

---

## Tier 3 — Claude Code distribution

### Marketplace + plugin manifest

```
.claude-plugin/
├── plugin.json            # plugin metadata (name, version, skills, commands, agents, hooks)
└── marketplace.json       # registers the plugin in Claude's marketplace
```

`plugin.json` declares all four skills, all commands, all agents, all hooks.
Versioned alongside `CHANGELOG.md`.

### Slash commands (`commands/`)

Claude Code's slash-command `:` is reserved for plugin namespacing
(`/<plugin>:<command>`); it cannot be user-extended for sub-commands. So
sub-actions become **arguments**, not separate commands.

Per persona:

- `/<persona>` — activate the skill (e.g., `/shakespeare`, `/pirate`,
  `/gen-alpha`, `/toronto-mans`). With no argument: just activate.
- `/<persona> plain` — drop the persona for the next response only.
- `/<persona> flavor <name>` — switch flavor (e.g., `/pirate flavor shanty`).
- `/<persona> reload` — re-read the persona's config.

Plus repo-wide:

- `/personas` — list all installed personas, the active one, and the active flavor.
- `/personas off` — fully deactivate any active persona.

Once installed via the `chrysippus` plugin, these will be auto-namespaced by
Claude Code as `/chrysippus:<persona>` etc.

### Subagents (`agents/`)

Per current Claude Code docs (verified 2026-04-17), subagents do **not** inherit
parent-session skills. Each subagent must declare `skills: [<persona>]` in its
YAML frontmatter, or it starts fresh with no persona context.

- `<persona>-reviewer` (one per skill, four total) — code review subagent that
  reviews PR-style diffs in the persona's voice. Each must include
  `skills: [<persona>]` in frontmatter.
- `dramaturg` — meta-subagent that audits whether the active persona's rules are
  being obeyed in the conversation; useful for self-debugging. Must declare
  `skills: [shakespeare, pirate, gen-alpha, toronto-mans]` to access all four
  rule sets simultaneously.

### Hooks (`hooks/`)

**Security model**: per Claude Code docs (verified 2026-04-17), hooks run
**unsandboxed at the user's shell privilege**, with no per-invocation permission
prompt. This is a meaningful trust delegation — installing a hook from an
untrusted plugin is equivalent to running an arbitrary script. Defenses we ship:

- All hooks `set -euo pipefail`, no network calls, no `eval`, no `exec` of
  user-provided strings, < 100 LOC each, shellcheck-clean.
- Hook installation is **opt-in via `hooks/install.sh`** — never auto-wired
  by `claude plugin install`.
- `SECURITY.md` documents the model and tells users to read every hook script
  before installing.
- Hooks live in `hooks/hooks.json` per Claude Code spec. Each hook script
  referenced from there is in the same `hooks/` directory.

Hooks shipped:

- `session-start.sh` — optional `SessionStart` hook that injects the active
  persona (read from per-session state file) into the system prompt on every
  session, removing the need for `CLAUDE.md` edits in target repos.
- `install.sh` — opt-in installer that wires up the session-start hook in the
  user's Claude Code settings. **Manual install path also documented** so users
  have a non-curl option.
- `hooks/hooks.json` — declares which scripts attach to which events.

### Install paths

- **Marketplace**: `claude plugin marketplace add <user>/chrysippus && claude plugin install chrysippus@chrysippus`
- **Manual clone + symlink**: `git clone … && ln -s <repo>/.claude/skills/* ~/.claude/skills/`
- **Tarball**: `gh release download` + extract to `~/.claude/skills/`

---

## Tier 4 — Quality (evals + tests + CI)

### Evals (`evals/`)

A small harness that:

1. Loads each skill in a controlled session.
2. Sends a fixed corpus of prompts.
3. Grades responses against rubrics (style markers, preservation rules, flavor
   consistency, safety yield).

Rubric examples per persona:

- **shakespeare**: at least one thou/thee/thy per response, preservation of
  backtick contents, safety warning yields to plain English with the bardic preface.
- **pirate**: at least one pirate-vocab token per response, no excluded
  ethnic-accent markers, shanty has 4 lines + AABB rhyme.
- **gen-alpha**: at least one current-lexicon term per response, sentence-fragment
  cadence in `unhinged` flavor, gloss present in `tutorial` flavor.
- **toronto-mans**: disclaimer surfaced once on first activation, no excluded
  loanwords, no slurs, safety warnings preserved (hard rule).

Eval grading uses Claude API as judge with structured output. Cost-gated: runs on
`release/*` branches and weekly cron, **not every PR**.

### Tests (`tests/`)

- `tests/render/` — bash tests for `scripts/render.sh` (golden file comparisons).
- `tests/install/` — tests for `hooks/install.sh` against a tmpdir-mocked `~/.claude/`.
- `tests/manifest/` — JSON-schema validation of `plugin.json` and `marketplace.json`.
- `tests/lexicon/` — assertion that `gen-alpha/lexicon.md` parses and that
  `toronto-mans` excluded-list isn't present.

Test runner: plain bash + `bats-core` (zero-runtime install via submodule or vendor).

### Lint

- `markdownlint` on all `.md`.
- `yamllint` on `_meta.yml` and `.config` files.
- `shellcheck` on all `scripts/` and `hooks/`.
- `prettier` on `plugin.json` / `marketplace.json` (or `jq --check`).

### CI (`.github/workflows/`)

- `ci.yml` — on every PR: lint + tests + `render.sh --check`.
- `evals.yml` — manual + weekly cron: full eval suite. Posts results as PR
  comment when manually triggered.
- `release.yml` — on `v*` tag: build tarball, `gh release create`, attach SHA256 sums.
- `dependabot.yml` — keep CI actions up to date (zero runtime deps means
  dependabot has little to do otherwise).

---

## Tier 5 — Polish

### Docs (`docs/`)

- `docs/install/` — one page per agent (Claude Code, Codex, Gemini, Cursor,
  Windsurf, Aider, Cline) with screenshots.
- `docs/personas/` — one page per skill with full demo and flavor matrix.
- `docs/extending/` — how to add a new persona, how to add a flavor, how to
  update a lexicon.
- `docs/security.md` — supply-chain posture, hook safety, install verification
  with SHA256.
- Optional: render with `mkdocs material` to a static site at `gh-pages`.

### README polish

- Animated GIFs for each persona (asciinema → svg-term).
- Badges: CI status, MIT license, marketplace version, `bats-core` tests passing.
- Quickstart at top: 3-line install + 1 trigger phrase.
- Sibling-skills table updated with all four personas.

### Release process (documented in `RELEASING.md`)

- Bump version in `plugin.json` + `CHANGELOG.md`.
- Sign annotated tag.
- CI builds tarball + computes SHA256.
- `gh release create` publishes notes from CHANGELOG section.
- `marketplace.json` points at the new tag.

---

## Phasing (recommended execution order)

To avoid one giant unmergeable change, ship in phases as separate work-streams.
Each phase keeps `main` always shippable.

| Phase | Scope | Effort | Tag on completion |
|---|---|---|---|
| 1 | Foundation: license, gitignore, contributing/security/coc, changelog, git init, **repo rename to `Chrysippus`** | 1–2 days | `v0.1.0` |
| 2 | Rules refactor: extract shakespeare + pirate to `rules/`, build `render.sh` + `check.sh`, regenerate existing files. **No behavior change.** | 1 day | (no tag) |
| 3 | `gen-alpha` skill (3 flavors + lexicon) | 1 day | `v0.2.0` |
| 4 | `toronto-mans` skill (1 flavor + DISCLAIMER + hard guardrails) | 1 day | `v0.3.0` |
| 5 | Multi-agent reach: render to `AGENTS.md`, `GEMINI.md`, `.cursor/rules/`, `.windsurfrules`, `CONVENTIONS.md`, `.clinerules` | 2 days | `v0.4.0` |
| 6 | Claude distribution: `plugin.json`, `marketplace.json`, `commands/`, `agents/`, `hooks/`, `install.sh` | 2 days | `v0.5.0` |
| 7 | Quality: tests, lint, CI workflows, evals harness | 3 days | `v0.6.0` |
| 8 | Polish: docs site, GIFs, badges, release automation | 2 days | `v1.0.0` — first public release |

**Total: ~13–15 working days.**

---

## What we will NOT build

- **Custom MCP server** — overkill for a styling skill.
- **Web UI / playground** — defer.
- **Telemetry** — privacy-fraught; skip.
- **Translation to other languages** — skills are inherently English-bound.
- **Kiro full support** — wait for spec stability; mark "coming soon".
- **Public Slack/Discord community** — out of scope; let users open issues.
- **Generated TypeScript types / SDK** — no consumers asking for it.

---

## Critical files

### To create (foundation)

- `LICENSE`, `NOTICE`, `.gitignore`, `.gitattributes`
- `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, `CHANGELOG.md`
- `AUTHORS`, `CODEOWNERS`, `RELEASING.md`

### To create (source of truth)

- `rules/shakespeare/{_meta.yml, instructions.md}` (extracted from existing `SKILL.md`)
- `rules/pirate/{_meta.yml, instructions.md}` (extracted from existing `SKILL.md`)
- `rules/gen-alpha/{_meta.yml, instructions.md, lexicon.md}` (new)
- `rules/toronto-mans/{_meta.yml, instructions.md}` (new — guardrails inline in instructions.md, no separate DISCLAIMER file)

### To create (generator + tests)

- `scripts/render.sh`, `scripts/check.sh`, `scripts/lib/*`
- `tests/render/*`, `tests/install/*`, `tests/manifest/*`, `tests/lexicon/*`

### To create (Claude distribution)

- `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`
- `commands/<persona>.md`, `commands/<persona>:plain.md`, etc. (~12 commands total)
- `agents/<persona>-reviewer.md` (4) + `agents/dramaturg.md`
- `hooks/session-start.sh`, `hooks/install.sh`

### To create (CI + docs)

- `.github/workflows/{ci.yml, evals.yml, release.yml}`
- `.github/dependabot.yml`
- `docs/install/*`, `docs/personas/*`, `docs/extending/*`, `docs/security.md`

### To regenerate (existing files)

- `.claude/skills/shakespeare/{SKILL.md, shakespeare.config, examples.md}` — now generated by `render.sh`.
- `.claude/skills/pirate/{SKILL.md, pirate.config, examples.md}` — now generated by `render.sh`.
- `.claude/skills/{gen-alpha, toronto-mans}/*` — generated.
- `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `README.md`, `CONVENTIONS.md` — all generated/updated by `render.sh`.

### To rename

- Repo directory: `shakespeare/` → `Chrysippus/` (or `Janus/` as fallback).
- Plugin / marketplace name: `chrysippus` (lower-case for marketplace).

---

## Patterns reused from current state

- File layout per skill: `SKILL.md` + `<persona>.config` + `examples.md` (now generated, but same shape).
- Frontmatter + activation rules + preservation table (all four skills inherit pirate's structure).
- Trigger-phrase activation grammar (`"talk like X"`, `/<persona>`, `<flavor> flavor`, `reload <persona> config`).
- Self-edit guardrail in `CLAUDE.md` (extended to cover the four skills' files).
- Most-recent-wins precedence rule (now covering four personas, no fusion).

---

## Verification

End-to-end checks for the user to run after each phase. Key gates:

1. **Phase 2 (rules refactor)**: `scripts/check.sh` green; existing shakespeare and
   pirate skills work unchanged in a fresh session.
2. **Phase 3 (gen-alpha)**: trigger `"talk like gen alpha"` → `unhinged` flavor
   responds with current-lexicon slang + sentence fragments. Switch to `tutorial`
   → terms get parenthetical glosses.
3. **Phase 4 (toronto-mans)**: trigger `"talk like a toronto mans"` → response
   in `mans` flavor, with `mans`-as-singular and Toronto place markers showing
   up; confirm none of the excluded loanwords appear. Confirm
   `safety_warnings: false` in the config is rejected (hard-locked).
4. **Phase 5 (multi-agent reach)**: open the project in Cursor →
   `.cursor/rules/shakespeare.mdc` activates the persona without any other setup.
   Repeat for Codex (`AGENTS.md`), Gemini, Aider, Cline.
5. **Phase 6 (Claude distribution)**: `claude plugin marketplace add <repo>` +
   `claude plugin install chrysippus` → all four personas installed; `/personas`
   lists them; `/shakespeare` activates.
6. **Phase 7 (quality)**: open a PR; CI runs lint + tests + `check.sh` and posts
   pass/fail. Manually trigger evals → eval report posted as PR comment.
7. **Phase 8 (polish)**: `gh release create v1.0.0` → tarball uploaded with SHA256
   attached; docs site visible at gh-pages URL.

### Security verification gates

- `shellcheck hooks/*` clean.
- No `curl | bash` patterns inside shipped hooks; install script paths documented
  for manual install.
- All hooks pass `grep -E '(eval|exec|curl|wget)' hooks/` review.
- SHA256 of release tarball published in release notes; `SECURITY.md` reporting
  channel published.

---

## Task tracking

Phase work is tracked as discrete tasks in the project task list (Claude Code's
TaskList). At time of writing:

- Tasks #14–#21 cover Phases 1–8 respectively.
- Each task has `blockedBy` set so the phases execute in the right order.
- Sub-tasks may be added during execution as work expands.

---

## Open follow-ups (not blocking v1.0.0)

- Decide whether to publish to npm as well as the Claude marketplace.
- Decide whether to add a `personas-deactivate-on-pr` hook that reverts to plain
  English when generating commit/PR text regardless of `preserve.commits`.
- Investigate Kiro support once Kiro's rule format stabilises.
- Consider a `lexicon-bot` GitHub Action that nudges quarterly reviews of the
  `gen-alpha` lexicon.
- Decide on a community lexicon-PR review cadence (monthly? quarterly?).

---

*Last updated: 2026-04-17. This document is the durable reference; the ephemeral
plan in `~/.claude/plans/` mirrors it during active planning sessions.*
