# Install — Codex / Cline (AGENTS.md convention)

Codex, Cline, and other AI coding agents that follow the `AGENTS.md`
convention read a single `AGENTS.md` file at the project root.
`chrysippus` ships a concatenated `AGENTS.md` with all installed personas.

## Per-project install

```bash
cd your-project
curl -o AGENTS.md https://raw.githubusercontent.com/kbatsu/chrysippus/main/AGENTS.md
```

Or clone and copy:

```bash
git clone https://github.com/kbatsu/chrysippus /tmp/chrysippus
cp /tmp/chrysippus/AGENTS.md .
```

That's it. The agent will read the file at the start of every session.

## What's in AGENTS.md

- **Installed personas table** — shakespeare, pirate, gen-alpha, toronto-mans.
- **Activation cheat-sheet** — trigger phrases + mid-session controls.
- **Precedence and preservation rules** — what changes, what stays plain.
- **Per-persona full instructions** — the complete ruleset for each skill.

The file is self-contained; no cross-references required.

## Cline-specific: prefer `.clinerules`

Cline reads both `AGENTS.md` and `.clinerules`. `.clinerules` has the same
content as `AGENTS.md` in this repo, so either works. If Cline prioritises
`.clinerules` in your setup, use that:

```bash
cp /tmp/chrysippus/.clinerules .
```

## Activation

Say any trigger phrase from the persona's section:

- *"speak like Shakespeare"* / *"bard mode"* → shakespeare
- *"talk like a pirate"* / *"pirate mode"* → pirate
- *"talk like gen alpha"* / *"skibidi mode"* → gen-alpha
- *"talk like a toronto mans"* / *"toronto mode"* → toronto-mans

## Keeping up to date

If the upstream `chrysippus` updates (new lexicon, flavor, persona), re-run
the curl or copy command to pull in changes. The files are generated from
`rules/<persona>/` so updates are cheap.
