# Install — Windsurf (Codeium)

Windsurf reads `.windsurfrules` at the project root.

## Per-project install

```bash
cd your-project
curl -o .windsurfrules https://raw.githubusercontent.com/kbatsu/chrysippus/main/.windsurfrules
```

Or clone and copy:

```bash
git clone https://github.com/kbatsu/chrysippus /tmp/chrysippus
cp /tmp/chrysippus/.windsurfrules .
```

Windsurf picks up the file automatically.

## Activation

Trigger a persona by its phrase:

- *"speak like Shakespeare"* / *"bard mode"*
- *"talk like a pirate"* / *"pirate mode"*
- *"talk like gen alpha"* / *"skibidi mode"*
- *"talk like a toronto mans"* / *"toronto mode"*

## Keeping up to date

Re-run the copy when upstream `chrysippus` publishes a new release. The
file is regenerated on every release tag.
