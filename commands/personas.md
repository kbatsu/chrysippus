---
description: List installed persona skills (and which one is currently active, if any) or deactivate the active persona.
---

List the persona skills shipped with this plugin, and report which (if any)
is currently active in this session. If the user passes the argument `off`,
fully deactivate any active persona for the rest of the session.

Currently installed personas:

| Persona | Default flavor | Other flavors |
|---|---|---|
| `shakespeare` | `courtly` | `tavern`, `sonnet` |
| `pirate` | `scurvy-dog` | `captain`, `drunk`, `shanty` |
| `gen-alpha` | `unhinged` | `corporate`, `tutorial` |
| `toronto-mans` | `mans` | (single flavor in v1) |

Trigger each with `/chrysippus:<persona>` or its natural-language trigger
phrases. See `.claude/skills/<persona>/SKILL.md` for full rules.

Report briefly in plain English (do not adopt any persona voice for this
response).
