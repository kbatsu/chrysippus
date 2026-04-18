#!/usr/bin/env python3
"""
chrysippus render — generate Claude Code skill files from rules/ source.

Usage:
    scripts/render.py                    # render all personas
    scripts/render.py shakespeare        # render single persona
    scripts/render.py --check            # CI gate: render to tmp, diff vs committed,
                                         #          exit 1 on drift
    scripts/render.py --out OUTDIR       # render to a custom output base dir

Reads `rules/<persona>/_meta.json` + `rules/<persona>/instructions.md` and
emits canonical Claude Code skill files at `.claude/skills/<persona>/`:

  - SKILL.md            (frontmatter from _meta.json + body from instructions.md)
  - <persona>.config    (defaults from _meta.json)
  - examples.md         (copied from rules/<persona>/examples.md if present)
  - lexicon.md          (copied from rules/<persona>/lexicon.md if present)

Zero runtime dependencies — Python 3.8+ stdlib only.
"""

import argparse
import difflib
import json
import shutil
import sys
import tempfile
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RULES_DIR = ROOT / "rules"
SKILLS_DIR = ROOT / ".claude" / "skills"

DESC_WRAP_WIDTH = 70


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "personas",
        nargs="*",
        help="Personas to render (default: all subdirectories of rules/)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Render to a temp dir, diff against committed; exit 1 on any drift",
    )
    parser.add_argument(
        "--out",
        type=Path,
        help="Output base dir (default: .claude/skills/)",
    )
    args = parser.parse_args(argv)

    if not RULES_DIR.exists():
        print(f"error: rules/ not found at {RULES_DIR}", file=sys.stderr)
        return 2

    available = sorted(p.name for p in RULES_DIR.iterdir() if p.is_dir())
    personas = args.personas or available

    unknown = set(personas) - set(available)
    if unknown:
        print(
            f"error: unknown persona(s): {', '.join(sorted(unknown))}\n"
            f"available: {', '.join(available)}",
            file=sys.stderr,
        )
        return 2

    if args.check:
        return run_check(personas)

    out_base = args.out.resolve() if args.out else SKILLS_DIR
    for persona in personas:
        target = out_base / persona
        render_persona(persona, target)
        print(f"rendered {persona} -> {target.relative_to(ROOT) if target.is_relative_to(ROOT) else target}")
    return 0


def run_check(personas):
    """Render to a tmp dir; diff each file against committed; exit 1 on drift."""
    drifts = []
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        for persona in personas:
            tmp_target = tmp_dir / persona
            render_persona(persona, tmp_target)
            drifts.extend(diff_persona(persona, tmp_target, SKILLS_DIR / persona))

    if drifts:
        print("DRIFT — generated output does not match committed files:", file=sys.stderr)
        print("", file=sys.stderr)
        for d in drifts:
            print(d, file=sys.stderr)
        print("", file=sys.stderr)
        print("To fix: run scripts/render.py and commit the result.", file=sys.stderr)
        return 1

    print(f"clean — {len(personas)} persona(s) match committed output")
    return 0


def diff_persona(persona, tmp_path, committed_path):
    drifts = []
    if not committed_path.exists():
        drifts.append(f"  {persona}: not present in {committed_path}")
        return drifts

    tmp_files = {f.name for f in tmp_path.iterdir() if f.is_file()}
    cmt_files = {f.name for f in committed_path.iterdir() if f.is_file()}

    for missing in sorted(tmp_files - cmt_files):
        drifts.append(f"  {persona}/{missing}: rendered but not committed")
    for extra in sorted(cmt_files - tmp_files):
        drifts.append(f"  {persona}/{extra}: committed but not rendered (stale?)")

    for name in sorted(tmp_files & cmt_files):
        a = (committed_path / name).read_text().splitlines()
        b = (tmp_path / name).read_text().splitlines()
        if a != b:
            diff = "\n".join(
                difflib.unified_diff(
                    a, b,
                    fromfile=f"committed/{persona}/{name}",
                    tofile=f"rendered/{persona}/{name}",
                    lineterm="",
                )
            )
            drifts.append(diff)
    return drifts


def render_persona(persona, target):
    src = RULES_DIR / persona
    meta_path = src / "_meta.json"
    if not meta_path.exists():
        raise FileNotFoundError(f"missing {meta_path}")

    meta = json.loads(meta_path.read_text())

    target.mkdir(parents=True, exist_ok=True)

    # SKILL.md
    (target / "SKILL.md").write_text(render_skill_md(meta, src))

    # <persona>.config
    config_name = meta.get("config_path") or f"{meta['name']}.config"
    (target / config_name).write_text(render_config(meta))

    # examples.md (copy through if present in rules/)
    examples_src = src / "examples.md"
    if examples_src.exists():
        shutil.copyfile(examples_src, target / "examples.md")

    # lexicon.md (copy through if present in rules/)
    lexicon_src = src / "lexicon.md"
    if lexicon_src.exists():
        shutil.copyfile(lexicon_src, target / "lexicon.md")


def render_skill_md(meta, src):
    """Compose SKILL.md = YAML frontmatter from meta + body from instructions.md."""
    name = meta["name"]
    description = meta["description"]
    body = (src / "instructions.md").read_text()

    # YAML folded scalar: collapse whitespace then re-wrap to fixed width
    collapsed = " ".join(description.split())
    wrapped = textwrap.fill(
        collapsed,
        width=DESC_WRAP_WIDTH,
        break_long_words=False,
        break_on_hyphens=False,
    )
    indented = "\n".join(f"  {line}" for line in wrapped.splitlines())

    frontmatter = (
        "---\n"
        f"name: {name}\n"
        "description: >\n"
        f"{indented}\n"
        "---\n\n"
    )
    return frontmatter + body


# Per-toggle inline comments shown in generated <persona>.config
PRESERVE_COMMENTS = {
    "commits":         "commit message subject, body, and trailers",
    "pr_descriptions": "PR titles, bodies, and checklists",
    "code_comments":   "comments and docstrings written into source files",
    "safety_warnings": "destructive-op confirmations + warnings (strongly recommended on)",
    "errors_verbatim": "error text and stack traces reproduced from tools",
}


def _wrap_comment_paragraph(text, width=76):
    """Wrap one paragraph as a `# ...`-prefixed comment block."""
    collapsed = " ".join(text.split())
    wrapped = textwrap.fill(
        collapsed,
        width=width,
        break_long_words=False,
        break_on_hyphens=False,
    )
    return "\n".join(f"# {line}" for line in wrapped.splitlines())


def render_config(meta):
    """Build a default <persona>.config from meta."""
    name = meta["name"]
    flavors = meta["flavors"]
    default_flavor = next(f["name"] for f in flavors if f.get("default"))

    # Aligned flavor docstring lines
    width = max(len(f["name"]) for f in flavors)
    flavor_lines = []
    for f in flavors:
        marker = " (default)" if f.get("default") else ""
        flavor_lines.append(f"# {f['name']:<{width}}  — {f['description']}{marker}")
    flavors_doc = "\n".join(flavor_lines)

    # Aligned preserve toggle lines with inline comments
    keys = list(meta["preserve_defaults"].keys())
    key_width = max(len(k) for k in keys)
    locked = set(meta.get("preserve_locked") or [])
    preserve_lines = []
    for key in keys:
        val = str(meta["preserve_defaults"][key]).lower()
        comment = PRESERVE_COMMENTS.get(key, "")
        if key in locked:
            comment = (comment + " — HARD-LOCKED, cannot be changed").lstrip(" —")
        line = f"  {key}:{' ' * (key_width - len(key))} {val}"
        if comment:
            line = f"{line:<32}  # {comment}"
        preserve_lines.append(line)
    preserve_block = "\n".join(preserve_lines)

    # Optional persona-specific extra notes (e.g., danger-combo warnings)
    extra_notes_block = ""
    for note in meta.get("config_extra_notes", []) or []:
        extra_notes_block += "#\n" + _wrap_comment_paragraph(note) + "\n"

    return f"""# {name.title()} skill configuration
#
# This file is read by the `{name}` skill on activation. Edit it to change
# the active flavor or to toggle which content stays in plain modern English.
# Format is YAML-style key: value. Comments begin with #.
#
# After editing this file mid-session, say "reload {name} config" so Claude
# re-reads it. New sessions read it automatically.

# ─── Active flavor ───────────────────────────────────────────────────────────
{flavors_doc}
flavor: {default_flavor}

# ─── Preservation toggles ────────────────────────────────────────────────────
# Anything set to `true` stays in plain modern English. Anything set to `false`
# becomes {name}-styled. Defaults favour shared-repo etiquette.
#
# Note: content inside backticks (`foo()`, `null`, file paths) ALWAYS stays
# verbatim regardless of any setting here. That rule is hard-coded in SKILL.md.
{extra_notes_block}preserve:
{preserve_block}
"""


if __name__ == "__main__":
    sys.exit(main())
