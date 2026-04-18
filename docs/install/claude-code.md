# Install — Claude Code

`chrysippus` is a first-class Claude Code plugin. The simplest path is the
marketplace install.

## Marketplace (recommended)

```bash
claude plugin marketplace add kbatsu/chrysippus
claude plugin install chrysippus@kbatsu-plugins
```

Two commands. You now have:

- Four persona skills (auto-discovered under `.claude/skills/`)
- Five slash commands (`/chrysippus:<persona>` + `/chrysippus:personas`)
- Five subagents (four `<persona>-reviewer` + `dramaturg`)
- One `SessionStart` hook (opt-in per project)

## Per-repo manual install

If you'd rather copy the skills in by hand:

```bash
cd your-project
mkdir -p .claude/skills
git clone https://github.com/kbatsu/chrysippus /tmp/chrysippus
cp -r /tmp/chrysippus/.claude/skills/{shakespeare,pirate,gen-alpha,toronto-mans} .claude/skills/
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
cp -r /tmp/chrysippus/.claude/skills/{shakespeare,pirate,gen-alpha,toronto-mans} ~/.claude/skills/
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

| Command | Effect |
|---|---|
| `/chrysippus:shakespeare` | Activate shakespeare for this session |
| `/chrysippus:shakespeare sonnet` | Activate with sonnet flavor |
| `/chrysippus:pirate` | Activate pirate |
| `/chrysippus:gen-alpha` | Activate gen-alpha |
| `/chrysippus:toronto-mans` | Activate toronto-mans |
| `/chrysippus:personas` | List installed personas; show which is active |

The `:` between plugin and command is Claude Code's auto-namespacing —
don't add more colons for sub-actions. Sub-actions (plain / reload /
flavor switch) are natural-language triggers in the skill itself.

## Subagents

Five subagents are installed:

- `shakespeare-reviewer`, `pirate-reviewer`, `gen-alpha-reviewer`,
  `toronto-mans-reviewer` — code review in the persona's voice, with
  substantive technical feedback.
- `dramaturg` — meta-agent that audits persona rule-adherence. Speaks
  plainly itself.

Invoke via the standard Claude Code subagent mechanism. Each reviewer
declares the corresponding skill in its frontmatter, so the persona
context loads automatically when the subagent runs.

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
