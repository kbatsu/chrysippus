# chrysippus

Portable persona skills for AI coding agents. Change the register of the
agent's prose without changing what code it writes.

## What it is

`chrysippus` ships four persona skills for AI coding agents — Claude Code,
Codex, Cursor, Windsurf, Aider, Cline, and Gemini CLI. Each persona changes
how the agent *talks* (vocabulary, tone, register) while leaving what it
*does* (code, commands, tool output) untouched.

| Persona | Register | Flavors |
|---|---|---|
| [`shakespeare`](personas/shakespeare.md) | Early Modern English (c. 1600, Bardic) | `courtly`, `tavern`, `sonnet` |
| [`pirate`](personas/pirate.md) | Treasure Island / Pirates-of-the-Caribbean | `scurvy-dog`, `captain`, `drunk`, `shanty` |
| [`gen-alpha`](personas/gen-alpha.md) | Internet-native ironic Gen-Alpha slang | `unhinged`, `corporate`, `tutorial` |
| [`toronto-mans`](personas/toronto-mans.md) | Toronto / MTE caricature (with attribution) | `mans` |

## What doesn't change

Regardless of active persona:

- **Code, file paths, errors, command output** — verbatim, hard rule.
- **Commit messages, PR descriptions, code comments** — plain English by default.
- **Safety warnings, destructive-op confirmations** — plain English by default.
- **Non-English user input** — the agent replies in the user's language in plain prose.

## Quickstart (30 seconds)

For Claude Code users:

```bash
claude plugin marketplace add kbatsu/chrysippus
claude plugin install chrysippus@chrysippus
```

Then in any Claude Code session:

```
/chrysippus:shakespeare
```

Done. The Bard greets you.

For other agents, see the [install guide](install/index.md) — each agent
has its own one-line setup.

## Docs

- **[Install](install/index.md)** — per-agent setup (Claude Code, Cursor,
  Codex, Windsurf, Aider, Cline, Gemini).
- **[Personas](personas/index.md)** — one page per skill with demos,
  flavor matrix, and preservation rules.
- **[Extending](extending.md)** — add a new persona, add a flavor, update
  a lexicon.
- **[Security](security.md)** — supply-chain posture, hook model,
  SHA256 verification.

## Credits

Pattern borrowed from [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman).
Repo named after [Chrysippus of Soli](https://en.wikipedia.org/wiki/Chrysippus),
the Stoic philosopher who championed emotional restraint and rationality —
a deliberately ironic choice for a repo of theatrical persona voices.
