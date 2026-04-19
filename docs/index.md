# chrysippus

> *Named after [Chrysippus of Soli](https://en.wikipedia.org/wiki/Chrysippus)
> (c. 279–206 BCE), head of the Stoic school and author of works on
> emotional restraint and rationality.*

Persona skills for AI coding agents. Same prompt, multiple voices,
identical code output.

Works with: **Claude Code** (first-class plugin) · **Codex** · **Cursor** ·
**Windsurf** · **Aider** · **Cline** · **Gemini CLI**.

[Install in 30 seconds →](#install-in-30-seconds)

## Demo 1 — "What does this repo do?"

> 🎭 **[shakespeare](personas/shakespeare.md) — courtly**
> *"A trove of personas, good sir — five registers for thy AI agent to
> don. Bardic, piratey, youthful, Toronto-coded, or rural-Ontarian. The
> code remaineth verbatim; only the voice doth shift."*

> 🏴‍☠️ **[pirate](personas/pirate.md) — scurvy-dog**
> *"Aye matey — five voices for Claude Code and its kin. Ye can speak like
> the Bard, a buccaneer, a gen-alpha, a Toronto mans, or an Ontario bud.
> Code stays as writ; only the words change."*

> 🫠 **[gen-alpha](personas/gen-alpha.md) — unhinged**
> *"ok so 5 voices for claude code. shakespeare pirate gen-alpha
> toronto-mans ontario-bud. code untouched fr. purely for vibes no cap.
> also made by millennials bc of course."*

> 6️⃣ **[toronto-mans](personas/toronto-mans.md) — mans**
> *"Mans ship five persona skills for AI coding agents fam. Bard, pirate,
> gen-alpha, toronto-mans, and ontario-bud — you're reading it. Code stays
> plain no cap, only the voice shifts still."*

> 🇨🇦 **[ontario-bud](personas/ontario-bud.md) — bud**
> *"Five voices in here, bud. Bardic, piratey, gen-alpha, toronto-mans,
> and ontario-bud — that's me. Code stays plain English, just the voice
> changes. Pitter patter."*

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

> 🇨🇦 **ontario-bud**
> *"Bug on line 42 of `parse.ts` there, bud — `null` ain't being
> handled. Easy fix: drop a null-guard in afore the call. Sorted."*

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

## Personas

<!-- chrysippus:personas-table BEGIN -->
| Persona | Register | Default flavor | Other flavors |
|---|---|---|---|
| [`gen-alpha`](personas/gen-alpha.md) | Internet-native ironic Gen-Alpha slang | `unhinged` | `corporate`, `tutorial` |
| [`ontario-bud`](personas/ontario-bud.md) | Rural-Ontario / Letterkenny-inspired caricature | `bud` | *(single flavor in v1)* |
| [`pirate`](personas/pirate.md) | Treasure Island / POTC 17–18c. maritime | `scurvy-dog` | `captain`, `drunk`, `shanty` |
| [`shakespeare`](personas/shakespeare.md) | Early Modern English (c. 1600) | `courtly` | `tavern`, `sonnet` |
| [`toronto-mans`](personas/toronto-mans.md) | Toronto / Multicultural-Toronto-English caricature | `mans` | *(single flavor in v1)* |
<!-- chrysippus:personas-table END -->

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
- **[Subagents](subagents.md)** — the per-persona reviewers + the
  dramaturg meta-agent: what they do and how to invoke them.
- **[Recipes](recipes.md)** — worked examples for common tasks
  ("Bardic prose but plain commits", "full pirate git history", etc.).
- **[Extending](extending.md)** — add a new persona, add a flavor, update
  a lexicon.
- **[Security](security.md)** — supply-chain posture, hook model,
  SHA256 verification.
