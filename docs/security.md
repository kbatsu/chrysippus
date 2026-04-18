# Security

Summarises the security model for `chrysippus` — where the trust
boundaries are, what risks exist, and how to verify releases.

For vulnerability reporting, see [`SECURITY.md`](https://github.com/kbatsu/chrysippus/blob/main/SECURITY.md)
in the repo root.

## Surface of trust

`chrysippus` consists of:

| Component | Trust surface |
|---|---|
| Persona skill rules (markdown) | Text only — injected into AI agent context. Low risk. |
| `scripts/render.py` | Python 3 stdlib only. No network calls. Runs at build time, not runtime. |
| `hooks/session-start.sh` | Bash — runs on every Claude Code session start **if installed**. |
| `hooks/activate.sh` | Bash — user-invoked helper for setting the active persona. |
| Plugin manifest | JSON — metadata only, no execution. |

The only runtime-execution components are the two bash scripts in `hooks/`.

## Hook security model

Per Claude Code's design (verified against official docs 2026-04-17),
hooks shipped in a plugin run **unsandboxed at the user's shell
privilege**, with **no per-invocation permission prompt**.

In plain terms: installing a hook from any plugin — including this one —
gives that plugin's code execution rights inside your shell. If you don't
trust the plugin source, don't install its hooks.

### Defenses we ship

- **Hooks are opt-in per project.** `claude plugin install chrysippus` does
  not enable the SessionStart hook globally. The hook emits no output
  unless the user has run `hooks/activate.sh <persona>` in the project.
- **Short and auditable.** Both hook scripts are under 100 lines. Read
  before running:
  - [hooks/session-start.sh](https://github.com/kbatsu/chrysippus/blob/main/hooks/session-start.sh)
  - [hooks/activate.sh](https://github.com/kbatsu/chrysippus/blob/main/hooks/activate.sh)
- **No network calls.** Nothing in the hook scripts reaches out to the
  internet.
- **No `eval` / no `exec` of user-provided strings.** Persona names are
  validated against a hard-coded allow-list.
- **`set -euo pipefail`** in every script.
- **`shellcheck`-clean** (checked in CI).
- **Zero runtime dependencies.** Python 3 stdlib + bash. No PyPI, no npm.

## Release verification

Every `v*` release tag produces a tarball + a SHA256 checksum, both
attached to the GitHub release.

To verify before install:

```bash
VERSION=0.7.0
curl -LO "https://github.com/kbatsu/chrysippus/releases/download/v${VERSION}/chrysippus-${VERSION}.tar.gz"
curl -LO "https://github.com/kbatsu/chrysippus/releases/download/v${VERSION}/chrysippus-${VERSION}.tar.gz.sha256"
sha256sum -c "chrysippus-${VERSION}.tar.gz.sha256"
```

If the checksum fails, **do not install**. Open a Security Advisory.

## Supply-chain posture

- **Zero runtime dependencies.** Skills are markdown; hooks are bash;
  generator is Python stdlib. No `npm install`, no `pip install`.
- **CI dependencies pinned** (GitHub Actions versions in `.github/workflows/`,
  updated weekly by dependabot).
- **Release tags signed** with GPG.
- **`scripts/render.py --check` gate** in CI prevents drift between
  canonical source (`rules/`) and generated outputs.

## Pinning for safety

When installing from the marketplace or from a tarball, pin to a specific
tag rather than `main`:

```bash
# marketplace — pin to tag
claude plugin install chrysippus@kbatsu-plugins --version v1.0.2

# tarball
curl -LO "https://github.com/kbatsu/chrysippus/archive/refs/tags/v0.7.0.tar.gz"
```

This ensures your environment doesn't silently pick up breaking changes
or (hypothetically) compromised upstream commits.

## Prompt-injection considerations

The persona skill descriptions and instructions are injected into the AI
agent's context when activated. A malicious fork could slip instructions
into a SKILL.md that override safety guardrails.

Mitigations:

- **Trust the source.** Install only from the official
  [`kbatsu/chrysippus`](https://github.com/kbatsu/chrysippus) repo.
- **Review instructions.md before installing a fork.** It's markdown;
  read it.
- **Report suspicious forks** via GitHub Security Advisory.

## What to do if something is off

- **Reporting a vulnerability**: open a GitHub Security Advisory at
  [`kbatsu/chrysippus` → Security → Advisories](https://github.com/kbatsu/chrysippus/security/advisories).
- **Reporting stereotype-drift or cultural concerns**: open a regular
  issue; the maintainer will take it seriously.
- **Reporting a broken install**: open a regular issue with repro steps.
