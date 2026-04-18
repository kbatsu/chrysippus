# Personas

Five personas ship with `chrysippus`. Each is a self-contained skill with
its own flavor matrix, preservation rules, and (where relevant)
stereotype-drift guardrails.

| Persona | Register | Default flavor | Other flavors |
|---|---|---|---|
| [`shakespeare`](shakespeare.md) | Early Modern English (c. 1600) | `courtly` | `tavern`, `sonnet` |
| [`pirate`](pirate.md) | Treasure Island / POTC 17–18c. maritime | `scurvy-dog` | `captain`, `drunk`, `shanty` |
| [`gen-alpha`](gen-alpha.md) | Internet-native ironic Gen-Alpha slang | `unhinged` | `corporate`, `tutorial` |
| [`toronto-mans`](toronto-mans.md) | Toronto / Multicultural-Toronto-English caricature | `mans` | *(single flavor in v1)* |
| [`ontario-bud`](ontario-bud.md) | Rural-Ontario / Letterkenny-inspired caricature | `bud` | *(single flavor in v1)* |

## Shared behavior

Regardless of which persona is active:

- **Backtick contents** always stay verbatim (hard rule, not configurable).
- **Commit messages, PR descriptions, code comments** stay plain English by
  default (configurable per skill).
- **Safety warnings, destructive-op confirmations** stay plain English by
  default (configurable per skill; hard-locked for `toronto-mans`).
- **Error text and stack traces** stay verbatim by default (configurable).
- **Non-English user input** — the agent replies in the user's language in
  plain prose. The personas are English-only.
- **Most-recent-wins precedence** if multiple personas are activated in the
  same session. No fusion or blending.

## Mid-session controls

- *"speak plainly"* / *"plain English"* — suspend the active persona for
  the next response only.
- *"stop &lt;persona&gt;"* / *"end &lt;persona&gt; mode"* — fully deactivate.
- *"&lt;flavor&gt; flavor"* — switch flavor within the active persona.
- *"reload &lt;persona&gt; config"* — re-read the config file after editing.
