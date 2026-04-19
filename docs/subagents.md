# Subagents

chrysippus ships Claude Code subagents in the `agents/` directory of the
plugin. One per persona is a code reviewer in that register; one
(`dramaturg`) is a meta-agent that audits persona adherence. This page
covers what they do, when to use them, and how to invoke them.

## What is a subagent?

A subagent is a Claude Code sidekick with its own system prompt, tool
allowlist, and (optionally) preloaded skills. You invoke a subagent when
you want a self-contained task done in an isolated context — the
subagent starts fresh, does its work, and returns a result to your main
conversation without polluting your main context with intermediate
chatter.

Practical differences from the main conversation:

- **Isolated context** — the subagent has its own token budget and
  doesn't see your full conversation history.
- **Skills don't inherit** — subagents must declare any skills they need
  in their frontmatter. chrysippus's reviewer subagents do this
  automatically (e.g., `shakespeare-reviewer` declares
  `skills: [shakespeare]`).
- **Tool allowlist** — each subagent declares which tools it can use.
  Reviewers here have `Read, Grep, Glob, Bash`.
- **Foreground or background** — runs inline by default; press **Ctrl+B**
  to background it while you keep working.

## What chrysippus ships

<!-- chrysippus:subagents-table BEGIN -->
| Subagent | Purpose |
|---|---|
| `gen-alpha-reviewer` | PR / branch review in gen-alpha voice |
| `ontario-bud-reviewer` | PR / branch review in ontario-bud voice |
| `pirate-reviewer` | PR / branch review in pirate voice |
| `shakespeare-reviewer` | PR / branch review in shakespeare voice |
| `toronto-mans-reviewer` | PR / branch review in toronto-mans voice |
| `dramaturg` | Meta-agent — audits persona rule-adherence |
<!-- chrysippus:subagents-table END -->

The per-persona reviewers all do the same substantive work (code-review
against a diff or branch); only the voice differs. The dramaturg is
different in kind — it audits OTHER responses for drift and is
intentionally plain-spoken itself.

## How to invoke

When installed via the marketplace, subagents are **namespaced** as
`chrysippus:<subagent-name>`.

### Three invocation forms

#### 1. `@`-mention (recommended for targeted use)

Type `@` in a Claude Code session. A typeahead picker appears with all
installed subagents including plugin-namespaced ones:

```
@chrysippus:shakespeare-reviewer review this branch
```

The entire message becomes the subagent's task prompt. Context you
reference (files, branch names, diffs) is passed through the surrounding
text — there is no separate argument syntax.

#### 2. Natural language (let Claude decide)

Claude will auto-delegate to a subagent whose `description` matches your
intent:

```
Use the shakespeare-reviewer to do a pass over my latest PR.
```

Claude reads the reviewer's `description` frontmatter, sees a match,
delegates. Less predictable than `@`-mention but more ergonomic.

#### 3. Session-wide default (for long sessions)

If you want every response to come from a specific subagent for the rest
of a session:

```bash
claude --agent chrysippus:shakespeare-reviewer
```

Or persist in `.claude/settings.json`:

```json
{ "agent": "chrysippus:shakespeare-reviewer" }
```

Uncommon for this plugin — the reviewers are designed for targeted review
passes, not session-wide work.

### Passing context

There is no separate argument slot. Whatever you put around the `@`-mention
is the task prompt. Practical examples:

```
@chrysippus:pirate-reviewer review PR #42

@chrysippus:gen-alpha-reviewer look at the auth module — focus on the token refresh logic

@chrysippus:shakespeare-reviewer just the diff against main

@chrysippus:dramaturg audit this response for shakespeare-skill adherence:
<paste the response>
```

Subagents can run `git diff`, `gh pr view`, `grep`, etc. via their `Bash`
tool allowlist, so they gather their own context when you give them a
branch name or PR number.

## Per-subagent usage

### `shakespeare-reviewer`, `pirate-reviewer`, `gen-alpha-reviewer`, `toronto-mans-reviewer`

**What they do.** Review a PR, branch, patch, or specific files. Produce
substantive technical feedback — correctness, maintainability,
performance, security, tests — rendered in the persona's voice. Severity
markers (`blocker` / `major` / `minor` / `nit`) stay in plain English so
you can skim quickly.

**When to use them.**

- You want a second-pass review before merging, and you want the feedback
  rendered in a specific register.
- You want the feedback to be shareable as-is (e.g., paste into a PR
  comment) without Claude's usual "I'm an AI" framing.
- You want the review *isolated* from your current coding session
  (fresh context, no interference from whatever you were working on).

**Invocation pattern.**

```
@chrysippus:shakespeare-reviewer review the auth changes on my-branch
```

**Output shape** (paraphrased):

```
## Review of branch `my-branch`

**Verdict**: request changes

### Findings

- **[blocker]** Line 42 of `auth/login.ts` — `parse_input()` returneth
  `null` for empty strings, yet the caller doth call `.trim()` upon the
  result. Null-pointer dereference awaits.
- **[minor]** `auth/token.ts:18` — the timeout constant is magic; prithee
  extract it to a named constant for clarity.

### Questions for the author

- Wherefore is there no test for the empty-string branch of
  `parse_input()`?
```

Register differs per reviewer; the findings themselves are substantive
and concrete.

**Guardrails apply.** Each reviewer honours its persona's
preservation-rules and stereotype-drift guardrails. Security-critical
findings always render in plain English with a short preface
(*"The bard yields the floor for thy safety, good sir."*).

### `dramaturg` (meta-agent)

**What it does.** Audits a given response or transcript against a
persona's rules. Reports whether the persona's register was correctly
applied, whether preservation toggles were honoured, and whether any
stereotype-drift guardrails were violated.

**When to use it.**

- You think a persona response drifted off-register and want to confirm.
- You want to verify a guardrail held (e.g., toronto-mans didn't use a
  Patois expletive, pirate didn't reference slavery).
- You're debugging why a specific skill rule didn't fire.

**Invocation pattern.**

```
@chrysippus:dramaturg audit this response for shakespeare skill adherence:

"<paste the response>"
```

**Key quirk.** The dramaturg does **not** adopt any persona voice itself.
It speaks plainly — its job is to name drift, not perform. If you get a
flowery dramaturg response, something has gone wrong.

**Output shape** (paraphrased):

```
## Dramaturg audit — persona `shakespeare`

**Active flavor** (inferred): `courtly`

**Verdict**: partial drift

### Findings

- ✅ **Register correctness** — pronouns and verb endings consistent.
- ❌ **Preservation — commits** — the response rewrote a commit message
  in Bardic register despite `commits: true` being the default. Quote:
  "Hark, I shall commit this as..."
- ✅ **Guardrails** — no excluded vocabulary detected.

### Suggested fixes

- Review SKILL.md §5 preservation table — commit messages should remain
  plain English regardless of active flavor.
```

## Gotchas

1. **Subagents can't spawn subagents.** Your main conversation can fan
   out to multiple subagents; a subagent itself cannot. If you want
   "dramaturg audits the reviewer's output", run both from the main
   conversation sequentially, or have the main conversation hand the
   reviewer's output to the dramaturg.

2. **Ctrl+B backgrounds a running subagent.** Useful when the review is
   taking a while and you want to keep working. Results show up later as
   a summarized message.

3. **Plugin-namespaced subagents show as `chrysippus:<name>` in the `@`
   picker.** If you don't see them, the plugin install may have failed —
   try `claude plugin list` to verify chrysippus is installed, and
   `claude plugin marketplace update kbatsu-plugins` if the cache is
   stale.

4. **Fresh context means the subagent re-reads the skill.** Expect a
   small latency at the start of each invocation while the skill's
   SKILL.md loads.

5. **The reviewers don't follow your active persona** — they follow the
   persona declared in their own `skills:` frontmatter. So
   `shakespeare-reviewer` always reviews in Bardic register, even if
   your main session has pirate active.

## Security note

All reviewer subagents have `Read, Grep, Glob, Bash` in their tool
allowlist. They can read any file in your repo and run any bash command
(including `git`, `gh`, destructive operations if you ask them to).
Treat a subagent the same as you treat Claude itself — it has the same
access level.

The `dramaturg` has `Read` only — can read files, cannot run commands or
modify anything. Safer to give paste-and-audit tasks to.

See the [security page](security.md) for the full trust model.
