# Install — Cursor IDE

Cursor reads `.cursor/rules/*.mdc` files for project rules. `chrysippus`
ships one MDC file per persona, already committed in this repo.

## Per-project install

```bash
cd your-project
mkdir -p .cursor/rules
git clone https://github.com/kbatsu/chrysippus /tmp/chrysippus
cp /tmp/chrysippus/.cursor/rules/*.mdc .cursor/rules/
```

You're done. Cursor will auto-attach each persona's rule when the user's
intent matches its `description` frontmatter — "speak like Shakespeare",
"pirate mode", etc.

## Cherry-pick a single persona

```bash
mkdir -p .cursor/rules
cp /tmp/chrysippus/.cursor/rules/shakespeare.mdc .cursor/rules/
```

## MDC frontmatter

Each rule file looks like this:

```mdc
---
description: Apply the `shakespeare` persona when the user wants shakespeare-styled prose...
globs:
alwaysApply: false
---

# Shakespeare skill
...
```

- `description` — used by Cursor's auto-attach to match user intent.
- `globs` — empty; applies regardless of which files are open.
- `alwaysApply: false` — Cursor loads the rule only when description matches
  or the user invokes it explicitly.

## Activation

Say any of the trigger phrases from the persona's `description`, or
reference the rule explicitly (e.g., `@shakespeare`).

## Multiple personas

Copy multiple MDC files. Cursor will match the rule whose `description`
best fits the user's intent. If two match, the more recently invoked one
wins per chrysippus's precedence rule (documented in each rule body).
