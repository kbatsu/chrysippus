# Recipes

Worked examples for common chrysippus configurations and invocations.
Each recipe is a short "I want X; here's how" pattern. For the
authoritative config model see the [Configuration page](configuration.md);
for subagent invocation see the [Subagents page](subagents.md).

## Activation and flavor

### Activate a persona

Slash command:

```
/chrysippus:shakespeare
```

Or natural-language trigger:

```
speak like Shakespeare
```

Either produces a 3-line announcement: active flavor, other flavors +
switch syntax, stop syntax.

### Activate with a specific flavor

Slash command with argument:

```
/chrysippus:shakespeare sonnet
```

Or natural-language:

```
speak like Shakespeare in sonnet flavor
```

### Switch flavor mid-session

No config edit needed. Just say:

```
tavern flavor
```

Works for any flavor that belongs to the currently-active persona. The
skill switches and persists.

### Stop a persona

```
stop shakespeare
```

Or `"end bard mode"`, `"speak plainly"` for a one-off pause without
deactivating.

### List installed personas

```
/chrysippus:personas
```

Shows every persona with its flavors, and which (if any) is active.

## Configuration

### I want Shakespeare for prose, but plain-English commits

**This is the default.** No config changes needed. The defaults keep
commits, PR descriptions, code comments, safety warnings, and errors in
plain English while the chat prose switches register.

### I want the full Bardic experience — commits, PRs, everything

Edit `.claude/skills/shakespeare/shakespeare.config`:

```yaml
flavor: courtly

preserve:
  commits:         false
  pr_descriptions: false
  code_comments:   false
  safety_warnings: true   # ← leave this on
  errors_verbatim: false
```

Then reload mid-session:

```
reload shakespeare config
```

Heads up: on a shared repo, your reviewers will see Bardic commit
messages. Fine for personal repos; jarring in a team context.

### I want pirate commits for my solo side project

Same pattern as above. Edit `.claude/skills/pirate/pirate.config`:

```yaml
flavor: scurvy-dog
preserve:
  commits:         false
  pr_descriptions: false
  code_comments:   true    # keep comments readable by others
  safety_warnings: true
  errors_verbatim: true
```

Reload:

```
reload pirate config
```

Result: commit messages like `plunder(parse): haul up the null-guard,
matey` while code comments stay plain.

### I want drunk pirate for fun but not a dangerous destructive prompt

**This is already the default.** `safety_warnings: true` is strongly
recommended for the drunk flavor specifically. If you flip it to `false`,
destructive-op confirmations render as a drunken slur — easy to misclick.
The config file carries an inline warning about this combo.

```yaml
flavor: drunk
preserve:
  safety_warnings: true   # ← don't touch
```

### I want toronto-mans but with in-character safety warnings

**Not possible.** `safety_warnings` is hard-locked to `true` in the
toronto-mans skill. Any override you put in the config is ignored, and
the skill tells you once that it was rejected. See
[Configuration → Hard-locks](configuration.md#hard-locks).

### I want gen-alpha for fun but I'm over 30

`tutorial` flavor is your friend:

```
/chrysippus:gen-alpha tutorial
```

Every slang term gets a parenthetical gloss on first use:
*"this commit is cooked (= broken) ngl (= not gonna lie)"*.

Also useful for screen-sharing with a non-Gen-Alpha audience.

### I want a professional voice but with the corporate-gen-alpha bit

```
/chrysippus:gen-alpha corporate
```

Formal punctuation and capitalization, slang slipped in for register-
collision comedy: *"Per my last review, the rizz of this PR is
undeniable; however line 42 is, frankly, mid."*

## Reviews and audits

### Run a PR review in Bardic register

```
@chrysippus:shakespeare-reviewer review my latest PR
```

Or with a branch name:

```
@chrysippus:shakespeare-reviewer review the feature/auth-refresh branch
```

Output: a `verdict` + `findings` list in Bardic voice, with severity
markers (`blocker` / `major` / `minor` / `nit`) in plain English for
scannability.

### Run a pirate review from a cold start (no persona active)

```
@chrysippus:pirate-reviewer review the changes to src/auth/
```

The reviewer preloads the pirate skill — it does NOT inherit from
whatever persona is active in your main session. Always pirate voice,
every time.

### Ask multiple reviewers in parallel for a gut check

Send three `@`-mentions in a single message:

```
Review my branch three ways:
@chrysippus:shakespeare-reviewer
@chrysippus:pirate-reviewer
@chrysippus:gen-alpha-reviewer
```

Each runs in parallel, returns its findings. Useful for a side-by-side
comparison when you're just exploring. Burns context quickly; don't do
this for every review.

### Check if a response drifted off-register

```
@chrysippus:dramaturg audit this response for shakespeare-skill adherence:

"<paste the response in question>"
```

The dramaturg audits against SKILL.md rules and reports compliant /
partial drift / major violation. Speaks plainly itself — no voice.

### Check if a guardrail held (toronto-mans specifically)

```
@chrysippus:dramaturg audit this response for toronto-mans guardrails:

"<paste>"

Focus: did the response use any Patois expletives, fake-accent
respellings, or real-person references?
```

Same pattern as above, with the audit scope narrowed.

## Mid-session controls

### Suspend the active persona for one response

```
speak plainly
```

Next response renders in plain English. The persona resumes automatically
on the turn after.

### Deactivate the active persona entirely

```
stop shakespeare
```

Or `"end bard mode"`, `"end pirate mode"`, etc. Session reverts to plain
English until you re-invoke a persona.

### Switch between personas

Activating a new persona deactivates the old one. Most-recent-wins.

```
speak like Shakespeare
# (some work in Bardic)
talk like a pirate
# (from here, pirate voice; shakespeare no longer active)
```

### Edit a config, see changes mid-session

```
# 1. Edit .claude/skills/pirate/pirate.config in your editor
# 2. Tell Claude:
reload pirate config
```

Without the reload, Claude keeps using the cached-at-activation values.

## Project-level auto-activation

### Make one persona auto-load for this project only

```bash
bash "${CLAUDE_PLUGIN_ROOT}/hooks/activate.sh" shakespeare
```

Writes `.claude/personas/active` in the project dir. The SessionStart
hook reads it on every new Claude Code session and auto-activates
shakespeare. One-time opt-in per project.

### Check what's set

```bash
bash "${CLAUDE_PLUGIN_ROOT}/hooks/activate.sh" status
```

### Disable auto-activation for this project

```bash
bash "${CLAUDE_PLUGIN_ROOT}/hooks/activate.sh" off
```

Hooks live in the plugin install directory under Claude Code's plugin
store. See the [Claude Code install page](install/claude-code.md) for
more on the `CLAUDE_PLUGIN_ROOT` variable.
