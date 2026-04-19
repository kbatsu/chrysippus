# Install — Claude Code

`chrysippus` is a first-class Claude Code plugin. The simplest path is the
marketplace install.

## Marketplace (recommended)

```bash
claude plugin marketplace add kbatsu/chrysippus
claude plugin install chrysippus@kbatsu-plugins
```

Two commands. You now have:

- Persona skills (auto-discovered under `.claude/skills/`)
- A slash command per persona (`/chrysippus:<persona>`) plus `/chrysippus:personas`
- A reviewer subagent per persona plus the `dramaturg` meta-agent
- One `SessionStart` hook (opt-in per project)

## Per-repo manual install

If you'd rather copy the skills in by hand:

```bash
cd your-project
mkdir -p .claude/skills
git clone https://github.com/kbatsu/chrysippus /tmp/chrysippus
<!-- chrysippus:cp-skills-per-repo BEGIN -->
cp -r /tmp/chrysippus/.claude/skills/gen-alpha .claude/skills/
cp -r /tmp/chrysippus/.claude/skills/ontario-bud .claude/skills/
cp -r /tmp/chrysippus/.claude/skills/pirate .claude/skills/
cp -r /tmp/chrysippus/.claude/skills/shakespeare .claude/skills/
cp -r /tmp/chrysippus/.claude/skills/toronto-mans .claude/skills/
<!-- chrysippus:cp-skills-per-repo END -->
```

For always-on activation in this repo, append to `CLAUDE.md`:

```markdown
## Communication style

This repo uses the `shakespeare` skill at `.claude/skills/shakespeare/SKILL.md`.
Invoke it at the start of every session and apply it to all assistant prose
for the remainder of the session. Read
`.claude/skills/shakespeare/shakespeare.config` for the active flavor and
preservation toggles.
```

(Swap `shakespeare` for any other persona.)

## User-global install (across all your repos)

```bash
mkdir -p ~/.claude/skills
git clone https://github.com/kbatsu/chrysippus /tmp/chrysippus
<!-- chrysippus:cp-skills-user-global BEGIN -->
cp -r /tmp/chrysippus/.claude/skills/gen-alpha ~/.claude/skills/
cp -r /tmp/chrysippus/.claude/skills/ontario-bud ~/.claude/skills/
cp -r /tmp/chrysippus/.claude/skills/pirate ~/.claude/skills/
cp -r /tmp/chrysippus/.claude/skills/shakespeare ~/.claude/skills/
cp -r /tmp/chrysippus/.claude/skills/toronto-mans ~/.claude/skills/
<!-- chrysippus:cp-skills-user-global END -->
```

## Enabling the auto-activation hook

The marketplace install ships a `SessionStart` hook that can auto-activate
a specific persona on every new session in a project. Opt in per-project:

```bash
cd your-project
# where $CLAUDE_PLUGIN_ROOT is set by Claude Code to the plugin install location
bash "${CLAUDE_PLUGIN_ROOT}/hooks/activate.sh" shakespeare

# check current state
bash "${CLAUDE_PLUGIN_ROOT}/hooks/activate.sh" status

# disable
bash "${CLAUDE_PLUGIN_ROOT}/hooks/activate.sh" off
```

The hook writes `.claude/personas/active` in the project dir. The
SessionStart hook reads it and injects activation instructions.

**Security**: hooks run unsandboxed at your shell privilege. Read the
[security](../security.md) page before enabling.

## Slash commands

<!-- chrysippus:slash-commands-table BEGIN -->
| Command | Effect |
|---|---|
| `/chrysippus:gen-alpha` | Activate gen-alpha for this session |
| `/chrysippus:ontario-bud` | Activate ontario-bud for this session |
| `/chrysippus:pirate` | Activate pirate for this session |
| `/chrysippus:shakespeare` | Activate shakespeare for this session |
| `/chrysippus:toronto-mans` | Activate toronto-mans for this session |
| `/chrysippus:personas` | List installed personas; show which is active |
<!-- chrysippus:slash-commands-table END -->

Pass a flavor argument to activate with that flavor from the start —
e.g. `/chrysippus:shakespeare sonnet`, `/chrysippus:pirate shanty`.

Every persona activation also announces the active flavor, the other
flavors, and how to switch/stop — so first-time users don't need to open
the docs to discover what's available.

The `:` between plugin and command is Claude Code's auto-namespacing —
don't add more colons for sub-actions. Sub-actions (plain / reload /
flavor switch) are natural-language triggers in the skill itself.

## Subagents

The plugin installs subagents:

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

The reviewers each load their persona's skill from frontmatter; the
dramaturg speaks plainly itself.

Invoke with an `@`-mention (plugin-namespaced):

```
@chrysippus:shakespeare-reviewer review my latest PR
@chrysippus:dramaturg audit this response for shakespeare adherence: "<paste>"
```

Each reviewer declares the corresponding skill in its frontmatter, so
the persona context loads automatically. See
[**Subagents**](../subagents.md) for the full invocation guide (natural-
language, session defaults, passing context, and example output).

## Troubleshooting

- **Skill doesn't activate** — Claude Code loads skills when the
  description matches user intent. Try the trigger phrase verbatim or use
  the slash command.
- **Config edits not taking effect mid-session** — say *"reload
  &lt;persona&gt; config"*.
- **Hook does nothing** — the hook emits nothing unless
  `.claude/personas/active` exists in the project. Run `activate.sh
  <persona>` to set it.

See [Security](../security.md) for the full hook model and SHA256
verification flow.
