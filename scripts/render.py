#!/usr/bin/env python3
"""
chrysippus render — generate persona files for multiple AI coding agents
from the canonical source at rules/.

Usage:
    scripts/render.py                    # render all personas, all targets
    scripts/render.py shakespeare        # render single persona
    scripts/render.py --check            # CI gate: render to tmp, diff vs
                                         # committed files; exit 1 on drift
    scripts/render.py --out OUTDIR       # render to a custom output root

Reads `rules/<persona>/_meta.json` + `rules/<persona>/instructions.md`
(plus optional `examples.md`, `lexicon.md`) and emits files for multiple
AI coding agents:

  Per-persona:
    .claude/skills/<persona>/SKILL.md        (Claude Code skill)
    .claude/skills/<persona>/<persona>.config
    .claude/skills/<persona>/examples.md     (copied through)
    .claude/skills/<persona>/lexicon.md      (copied through if present)
    .cursor/rules/<persona>.mdc              (Cursor IDE)

  Single-file, concatenated across all personas:
    AGENTS.md         (universal convention — Codex, Cline, Aider, etc.)
    GEMINI.md         (Gemini CLI, same content as AGENTS.md)
    CONVENTIONS.md    (Aider)
    .windsurfrules    (Windsurf / Codeium)
    .clinerules       (Cline)

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


# ────────────────────────────────────────────────────────────────────────────
# CLI
# ────────────────────────────────────────────────────────────────────────────

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
        help="Output root dir (default: repo root)",
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

    out_root = args.out.resolve() if args.out else ROOT
    return do_render(personas, out_root)


def do_render(personas, out_root):
    personas_meta = {p: load_meta(p) for p in personas}
    text_outputs = build_text_outputs(personas_meta, out_root)
    copy_outputs = build_copy_outputs(personas, out_root)

    for target, content in text_outputs:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)

    for target, src in copy_outputs:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, target)

    total = len(text_outputs) + len(copy_outputs)
    print(f"rendered {len(personas)} persona(s) to {total} output file(s)")
    return 0


def run_check(personas):
    """Render to a tmp dir; diff each file against committed; exit 1 on drift."""
    drifts = []
    with tempfile.TemporaryDirectory() as tmp:
        tmp_root = Path(tmp)
        do_render(personas, tmp_root)

        # Compare every file we rendered against the committed equivalent
        personas_meta = {p: load_meta(p) for p in personas}
        text_outputs = build_text_outputs(personas_meta, tmp_root)
        copy_outputs = build_copy_outputs(personas, tmp_root)

        for target, _ in text_outputs + copy_outputs:
            rel = target.relative_to(tmp_root)
            committed = ROOT / rel
            if not committed.exists():
                drifts.append(f"  {rel}: rendered but not committed")
                continue
            a = committed.read_text().splitlines()
            b = target.read_text().splitlines()
            if a != b:
                diff = "\n".join(difflib.unified_diff(
                    a, b,
                    fromfile=f"committed/{rel}",
                    tofile=f"rendered/{rel}",
                    lineterm="",
                ))
                drifts.append(diff)

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


# ────────────────────────────────────────────────────────────────────────────
# Source loading
# ────────────────────────────────────────────────────────────────────────────

def load_meta(persona):
    src = RULES_DIR / persona
    meta_path = src / "_meta.json"
    if not meta_path.exists():
        raise FileNotFoundError(f"missing {meta_path}")
    meta = json.loads(meta_path.read_text())
    meta["_instructions"] = (src / "instructions.md").read_text()
    meta["_src_dir"] = src
    return meta


# ────────────────────────────────────────────────────────────────────────────
# Output composition
# ────────────────────────────────────────────────────────────────────────────

def build_text_outputs(personas_meta, out_root):
    """Return [(target_path, text_content), ...] — everything render-generated."""
    outputs = []

    for persona, meta in personas_meta.items():
        # Claude Code: SKILL.md + <persona>.config
        claude_dir = out_root / ".claude" / "skills" / persona
        outputs.append((claude_dir / "SKILL.md", render_claude_skill_md(meta)))
        config_name = meta.get("config_path") or f"{persona}.config"
        outputs.append((claude_dir / config_name, render_config(meta)))

        # Cursor: .cursor/rules/<persona>.mdc
        mdc = out_root / ".cursor" / "rules" / f"{persona}.mdc"
        outputs.append((mdc, render_cursor_mdc(meta)))

    # Single-file multi-agent targets (all personas concatenated)
    outputs.append((out_root / "AGENTS.md",       render_agents_md(personas_meta)))
    outputs.append((out_root / "GEMINI.md",       render_gemini_md(personas_meta)))
    outputs.append((out_root / "CONVENTIONS.md",  render_conventions_md(personas_meta)))
    outputs.append((out_root / ".windsurfrules",  render_windsurfrules(personas_meta)))
    outputs.append((out_root / ".clinerules",     render_clinerules(personas_meta)))

    return outputs


def build_copy_outputs(personas, out_root):
    """Return [(target_path, source_path), ...] — files copied verbatim."""
    outputs = []
    for persona in personas:
        src_dir = RULES_DIR / persona
        claude_dir = out_root / ".claude" / "skills" / persona
        for name in ("examples.md", "lexicon.md"):
            src = src_dir / name
            if src.exists():
                outputs.append((claude_dir / name, src))
    return outputs


# ────────────────────────────────────────────────────────────────────────────
# Claude Code skill — SKILL.md
# ────────────────────────────────────────────────────────────────────────────

def render_claude_skill_md(meta):
    name = meta["name"]
    description = meta["description"]
    body = meta["_instructions"]

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


# ────────────────────────────────────────────────────────────────────────────
# Claude Code skill — <persona>.config
# ────────────────────────────────────────────────────────────────────────────

PRESERVE_COMMENTS = {
    "commits":         "commit message subject, body, and trailers",
    "pr_descriptions": "PR titles, bodies, and checklists",
    "code_comments":   "comments and docstrings written into source files",
    "safety_warnings": "destructive-op confirmations + warnings (strongly recommended on)",
    "errors_verbatim": "error text and stack traces reproduced from tools",
}


def _wrap_comment_paragraph(text, width=76):
    collapsed = " ".join(text.split())
    wrapped = textwrap.fill(
        collapsed,
        width=width,
        break_long_words=False,
        break_on_hyphens=False,
    )
    return "\n".join(f"# {line}" for line in wrapped.splitlines())


def render_config(meta):
    name = meta["name"]
    flavors = meta["flavors"]
    default_flavor = next(f["name"] for f in flavors if f.get("default"))

    width = max(len(f["name"]) for f in flavors)
    flavor_lines = []
    for f in flavors:
        marker = " (default)" if f.get("default") else ""
        flavor_lines.append(f"# {f['name']:<{width}}  — {f['description']}{marker}")
    flavors_doc = "\n".join(flavor_lines)

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


# ────────────────────────────────────────────────────────────────────────────
# Cursor MDC — .cursor/rules/<persona>.mdc
# ────────────────────────────────────────────────────────────────────────────

def render_cursor_mdc(meta):
    """Cursor rules file. MDC frontmatter + full instructions body."""
    name = meta["name"]
    triggers = ", ".join(f'"{t}"' for t in meta["triggers"])
    description = (
        f"Apply the `{name}` persona when the user wants {name}-styled prose, "
        f"uses trigger phrases ({triggers}), or has already activated this "
        f"persona earlier in the session. The register changes only the prose; "
        f"code, paths, commits, errors, and safety warnings stay in plain "
        f"English per the preservation rules in the body."
    )

    body = meta["_instructions"]

    return (
        "---\n"
        f"description: {description}\n"
        "globs:\n"
        "alwaysApply: false\n"
        "---\n"
        "\n"
        f"{body}"
    )


# ────────────────────────────────────────────────────────────────────────────
# Multi-agent single-file targets — shared body
# ────────────────────────────────────────────────────────────────────────────

def _persona_table_row(persona, meta):
    default_flavor = next(f["name"] for f in meta["flavors"] if f.get("default"))
    others = [f["name"] for f in meta["flavors"] if not f.get("default")]
    others_str = ", ".join(f"`{f}`" for f in others) if others else "(none)"
    return (
        f"| `{persona}` | `{default_flavor}` | {others_str} |"
    )


def _activation_line(persona, meta):
    triggers = ", ".join(f"*{t!r}*".replace("'", '"') for t in meta["triggers"])
    return f"- **`{persona}`** — triggers: {triggers}"


def build_multi_agent_body(personas_meta):
    """The shared body used by AGENTS.md / GEMINI.md / CONVENTIONS.md / etc."""
    parts = []

    # Summary table
    parts.append("## Installed personas")
    parts.append("")
    parts.append("| Persona | Default flavor | Other flavors |")
    parts.append("|---|---|---|")
    for persona, meta in personas_meta.items():
        parts.append(_persona_table_row(persona, meta))
    parts.append("")

    # Activation cheat-sheet
    parts.append("## Activation")
    parts.append("")
    parts.append("Say any trigger phrase to activate a persona. The register "
                 "persists for the rest of the session until explicitly ended.")
    parts.append("")
    for persona, meta in personas_meta.items():
        parts.append(_activation_line(persona, meta))
    parts.append("")
    parts.append("**Mid-session controls**:")
    parts.append("- *\"speak plainly\"* / *\"plain English\"* — suspend the "
                 "active persona for the next response only.")
    parts.append("- *\"stop <persona>\"* / *\"end <persona> mode\"* — fully "
                 "deactivate the named persona for the session.")
    parts.append("- *\"<flavor> flavor\"* — switch flavor within the active persona.")
    parts.append("- *\"reload <persona> config\"* — re-read the persona's "
                 "config file after editing.")
    parts.append("")
    parts.append("**Precedence**: if more than one persona is activated in a "
                 "session, the most recently invoked wins. Do not fuse or blend "
                 "registers.")
    parts.append("")
    parts.append("**What stays plain English regardless of active persona**:")
    parts.append("- Anything inside backticks (`foo()`, `null`, file paths, flags).")
    parts.append("- Commit messages, PR descriptions, code comments (by default).")
    parts.append("- Safety warnings, destructive-op confirmations, error text "
                 "(by default).")
    parts.append("- Replies in non-English languages.")
    parts.append("")

    # Per-persona full rules
    for persona, meta in personas_meta.items():
        parts.append("---")
        parts.append("")
        parts.append(f"# Persona: `{persona}`")
        parts.append("")
        triggers = ", ".join(f"`{t}`" for t in meta["triggers"])
        parts.append(f"*Trigger phrases: {triggers}*")
        parts.append("")
        parts.append(meta["_instructions"].rstrip())
        parts.append("")

    return "\n".join(parts)


# ────────────────────────────────────────────────────────────────────────────
# AGENTS.md — universal convention (Codex, Cline, Aider, future agents)
# ────────────────────────────────────────────────────────────────────────────

AGENTS_HEADER = """# AGENTS.md — persona skills for AI coding agents

This file follows the `AGENTS.md` convention used by Codex, Cline, Aider,
and other AI coding agents. It documents **persona skills** shipped with
this repo that change the register of the agent's assistant prose — without
changing what code is written, what commands are run, or what output comes
back from tools.

Personas activate by **trigger phrase** and persist for the session. Code,
file paths, command output, commit messages, PR descriptions, code
comments, safety warnings, and error text all stay in plain English by
default, per the preservation rules in each persona's full rules below.

**Generated file.** This file is rendered by `scripts/render.py` from the
canonical source at `rules/<persona>/`. Do not edit directly — edit the
source and re-render. See `CONTRIBUTING.md` for the workflow.

---

"""


def render_agents_md(personas_meta):
    return AGENTS_HEADER + build_multi_agent_body(personas_meta)


# ────────────────────────────────────────────────────────────────────────────
# GEMINI.md — Gemini CLI
# ────────────────────────────────────────────────────────────────────────────

GEMINI_HEADER = """# GEMINI.md — persona skills for Gemini CLI

This file is read by Gemini CLI. It carries the same persona-skill rules
as `AGENTS.md` in this repo; both are generated from the same source at
`rules/<persona>/`.

Apply the persona rules below to all assistant prose in this session.
Code, paths, command output, commits, PR descriptions, comments, safety
warnings, and error text remain in plain English by default.

**Generated file.** Rendered by `scripts/render.py`.

---

"""


def render_gemini_md(personas_meta):
    return GEMINI_HEADER + build_multi_agent_body(personas_meta)


# ────────────────────────────────────────────────────────────────────────────
# CONVENTIONS.md — Aider
# ────────────────────────────────────────────────────────────────────────────

CONVENTIONS_HEADER = """# CONVENTIONS.md — persona skills for Aider

This file is read by Aider as project conventions. It documents **persona
skills** that change the register of Aider's prose output. Personas
activate via trigger phrase and persist until the user ends them.

Commit messages, code comments, and safety-critical content stay in plain
English regardless of active persona, unless explicitly toggled off in the
persona's config.

**Generated file.** Rendered by `scripts/render.py` from `rules/<persona>/`.

---

"""


def render_conventions_md(personas_meta):
    return CONVENTIONS_HEADER + build_multi_agent_body(personas_meta)


# ────────────────────────────────────────────────────────────────────────────
# .windsurfrules — Windsurf / Codeium
# ────────────────────────────────────────────────────────────────────────────

WINDSURF_HEADER = """# .windsurfrules — persona skills for Windsurf

This file is read by Windsurf (Codeium) as project rules. Persona skills
change the register of assistant prose without changing what code gets
written.

Activate by trigger phrase; persist for the session; most-recent-wins if
multiple are active. Commits, comments, and safety content stay in plain
English by default.

Generated by `scripts/render.py` from `rules/<persona>/`.

---

"""


def render_windsurfrules(personas_meta):
    return WINDSURF_HEADER + build_multi_agent_body(personas_meta)


# ────────────────────────────────────────────────────────────────────────────
# .clinerules — Cline
# ────────────────────────────────────────────────────────────────────────────

CLINE_HEADER = """# .clinerules — persona skills for Cline

This file is read by Cline as project rules. Persona skills change
register, not content — activate by trigger phrase, persist for the
session, most-recent-wins if multiple active. Preservation rules keep
code, commits, comments, and safety content in plain English by default.

Generated by `scripts/render.py` from `rules/<persona>/`.

---

"""


def render_clinerules(personas_meta):
    return CLINE_HEADER + build_multi_agent_body(personas_meta)


# ────────────────────────────────────────────────────────────────────────────
# entrypoint
# ────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    sys.exit(main())
