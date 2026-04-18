# Install — Aider

Aider reads `CONVENTIONS.md` as project conventions.

## Per-project install

```bash
cd your-project
curl -o CONVENTIONS.md https://raw.githubusercontent.com/kbatsu/chrysippus/main/CONVENTIONS.md
```

Or clone and copy:

```bash
git clone https://github.com/kbatsu/chrysippus /tmp/chrysippus
cp /tmp/chrysippus/CONVENTIONS.md .
```

Aider picks up `CONVENTIONS.md` automatically.

## Alternative: AGENTS.md

Aider also reads `AGENTS.md` in recent versions. If you'd rather use that
file (same content, shared with Codex/Cline), see
[agents-md.md](agents-md.md).

## Activation

Trigger a persona by its natural-language phrase:

- *"speak like Shakespeare"*
- *"talk like a pirate"*
- *"talk like gen alpha"*
- *"talk like a toronto mans"*

Or deactivate with *"speak plainly"* or *"stop &lt;persona&gt;"*.

## What's preserved regardless of persona

- Code, file paths, error messages, backtick contents.
- Commit messages — Aider's main artifact — stay in plain English.
- Safety warnings and destructive-op confirmations.

The `CONVENTIONS.md` body documents per-persona preservation rules in full.
