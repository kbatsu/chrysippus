# Security policy

## Reporting a vulnerability

Please report security vulnerabilities privately, **not** via public GitHub
issues.

Preferred channel: open a [GitHub Security Advisory](https://github.com/kbatsu/chrysippus/security/advisories/new).

Alternatively, email the maintainer (see `AUTHORS`).

We aim to acknowledge reports within 7 days and to publish a fix or mitigation
within 30 days for confirmed issues.

## Supported versions

Only the latest released version (latest `v*` tag) receives security fixes.
Older versions should upgrade.

## Hook security disclosure (READ BEFORE INSTALLING HOOKS)

This plugin ships shell hooks at `hooks/`. Per Claude Code's design (verified
2026-04-17 against official docs), hooks run **unsandboxed at the user's shell
privilege**, with **no per-invocation permission prompt**.

In plain terms: installing a hook from any plugin — including this one — gives
that plugin's code execution rights inside your shell. If you do not trust the
plugin's source, do not install its hooks.

### Defenses we ship

- **Hooks are opt-in.** `claude plugin install chrysippus` does **not** install
  hooks. To enable the optional `SessionStart` hook, you must explicitly run
  `hooks/install.sh`.
- **All hooks are short and auditable.** Each hook script in `hooks/` is
  under 100 lines, uses `set -euo pipefail`, makes no network calls, contains
  no `eval` or `exec` of user-provided strings, and passes `shellcheck`
  cleanly.
- **Released tarballs publish SHA256 sums.** Verify before extracting.
- **No `curl | bash` pattern in shipped install scripts.** A manual install
  path (clone + run a documented one-line command) is always available.

### What you should do

1. **Read every hook in `hooks/` before running `hooks/install.sh`.** Each one
   is short.
2. **Pin to a specific tag** when installing from the marketplace, not `main`.
3. **Verify SHA256** if installing from a release tarball.
4. **Audit your `~/.claude/settings.json`** periodically to confirm only the
   hooks you expect are wired up.

### Supply-chain posture

- Zero runtime dependencies. The plugin is bash + markdown.
- CI dependencies (markdownlint, yamllint, shellcheck, bats-core) are pinned
  in workflow files.
- Releases are signed with GPG (annotated tags).

## Disclosure timeline

When a confirmed vulnerability is fixed:

1. Patch released on the `main` branch.
2. New `v*` tag cut, with the security context summarised in the tag
   annotation message (the tag message is the GitHub Release body).
3. Security advisory published on GitHub with credit (if desired) to the
   reporter.
