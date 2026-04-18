# chrysippus

> *Named after [Chrysippus of Soli](https://en.wikipedia.org/wiki/Chrysippus)
> (c. 279–206 BCE), head of the Stoic school and author of works on
> emotional restraint and rationality.*

Four persona skills for AI coding agents. Same prompt, four voices,
identical code output.

Works with: **Claude Code** (first-class plugin) · **Codex** · **Cursor** ·
**Windsurf** · **Aider** · **Cline** · **Gemini CLI**.

[Install in 30 seconds →](#install-in-30-seconds)

## Demo 1 — "What does this repo do?"

> 🎭 **[shakespeare](personas/shakespeare.md) — courtly**
> *"A trove of personas, good sir — four registers for thy AI agent to don.
> Bardic, piratey, youthful, or Toronto-coded. The code remaineth verbatim;
> only the voice doth shift."*

> 🏴‍☠️ **[pirate](personas/pirate.md) — scurvy-dog**
> *"Aye matey — four voices for Claude Code and its kin. Ye can speak like
> the Bard, a buccaneer, a gen-alpha, or a Toronto mans. Code stays as
> writ; only the words change."*

> 🫠 **[gen-alpha](personas/gen-alpha.md) — unhinged**
> *"ok so 4 voices for claude code. shakespeare pirate gen-alpha
> toronto-mans. code untouched fr. purely for vibes no cap. also made by
> millennials bc of course."*

> 6️⃣ **[toronto-mans](personas/toronto-mans.md) — mans**
> *"Mans ship four persona skills for AI coding agents fam. Bard, pirate,
> gen-alpha, and toronto-mans — you're reading it. Code stays plain no
> cap, only the voice shifts still."*

## Demo 2 — "Bug on line 42 of `parse.ts` — `null` isn't handled. Advice?"

> 🎭 **shakespeare**
> *"Upon line 42 of `parse.ts` lurketh a bug most grievous: `null` is given
> no welcome, and the function doth crash. Place a null-guard afore the
> call, that the stream may flow unbroken."*

> 🏴‍☠️ **pirate**
> *"Kraken on line 42 of `parse.ts`, matey — `null` walks in and the
> function be capsized. Add a null-guard, and the seas stay calm."*

> 🫠 **gen-alpha**
> *"line 42 of `parse.ts` is cooked — `null` not handled. add a guard,
> move on. W fix."*

> 6️⃣ **toronto-mans**
> *"Bug on line 42 of `parse.ts` still fam — `null` ain't being handled.
> Easy ting to fix: null-guard before the call. Bare simple no cap."*

> Notice `parse.ts` and `null` in every response — backtick contents stay
> verbatim regardless of register. That's the preservation rule, one of
> several. [See the full config model →](configuration.md)

## What `chrysippus` is

Each persona changes how the agent **talks** (register, vocabulary, tone)
while leaving what it **does** untouched (code, commits, errors, tool
output). Inspired by [caveman](https://github.com/JuliusBrussee/caveman) —
same mechanism, opposite goal. caveman compresses speech to save tokens;
chrysippus retunes register for fun. No savings here, just vibes.

## Install in 30 seconds

For Claude Code users:

```bash
claude plugin marketplace add kbatsu/chrysippus
claude plugin install chrysippus@kbatsu-plugins
```

Then in any Claude Code session:

```
/chrysippus:shakespeare
```

Done. The Bard greets you.

For other agents, see the [install guide](install/index.md) — each agent
has its own one-line setup.

## The four personas

| Persona | Register | Flavors |
|---|---|---|
| [`shakespeare`](personas/shakespeare.md) | Early Modern English (c. 1600, Bardic) | `courtly`, `tavern`, `sonnet` |
| [`pirate`](personas/pirate.md) | Treasure Island / Pirates-of-the-Caribbean | `scurvy-dog`, `captain`, `drunk`, `shanty` |
| [`gen-alpha`](personas/gen-alpha.md) | Internet-native ironic Gen-Alpha slang | `unhinged`, `corporate`, `tutorial` |
| [`toronto-mans`](personas/toronto-mans.md) | Toronto / MTE caricature (with attribution) | `mans` |

## What's preserved regardless of active persona

- **Anything inside backticks** — hard rule, not configurable.
- **Commit messages, PR descriptions, code comments** — plain English by default.
- **Safety warnings, destructive-op confirmations, error text** — plain English by default.
- **Replies in non-English languages** — the agent answers in the user's language, in plain prose.
- **Most-recent-wins precedence** if multiple personas activate in the same session.

## Docs

- **[Install](install/index.md)** — per-agent setup (Claude Code, Cursor,
  Codex, Windsurf, Aider, Cline, Gemini).
- **[Personas](personas/index.md)** — one page per skill with demos,
  flavor matrix, and register-specific guardrails.
- **[Configuration](configuration.md)** — the config-file model,
  preservation toggles, hard-locks, reload mechanics.
- **[Subagents](subagents.md)** — the 4 per-persona reviewers + the
  dramaturg meta-agent: what they do and how to invoke them.
- **[Recipes](recipes.md)** — worked examples for common tasks
  ("Bardic prose but plain commits", "full pirate git history", etc.).
- **[Extending](extending.md)** — add a new persona, add a flavor, update
  a lexicon.
- **[Security](security.md)** — supply-chain posture, hook model,
  SHA256 verification.

## Credits

Hat tip to [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman)
for the initial idea.
