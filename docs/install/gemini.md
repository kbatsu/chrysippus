# Install — Gemini CLI

Gemini CLI reads `GEMINI.md` at the project root.

## Per-project install

```bash
cd your-project
curl -o GEMINI.md https://raw.githubusercontent.com/kbatsu/chrysippus/main/GEMINI.md
```

Or clone and copy:

```bash
git clone https://github.com/kbatsu/chrysippus /tmp/chrysippus
cp /tmp/chrysippus/GEMINI.md .
```

`GEMINI.md` carries the same content as `AGENTS.md` in this repo — both
are generated from the same `rules/<persona>/` source. Use whichever your
agent prefers.

## Activation

Same as other agents:

- *"speak like Shakespeare"*
- *"talk like a pirate"*
- *"talk like gen alpha"*
- *"talk like a toronto mans"*

## Note on size

`GEMINI.md` is ~45KB (all four personas concatenated). That's within
Gemini's context budget. If you only want one persona, you can trim the
file to just that persona's section; the activation triggers and
preservation rules still need to be present.
