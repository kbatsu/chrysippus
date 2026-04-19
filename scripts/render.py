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

Zero runtime dependencies — Python 3.10+ stdlib only.
"""

import argparse
import difflib
import json
import re
import shutil
import sys
import tempfile
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RULES_DIR = ROOT / "rules"
SKILLS_DIR = ROOT / ".claude" / "skills"
TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"

DESC_WRAP_WIDTH = 70

# Directories that render.py fully owns — every file under these is expected
# to be produced by a render run. Anything committed under one of these
# directories that doesn't match a rendered output is an orphan (stale;
# typically left behind when a persona is removed from rules/).
MANAGED_OUTPUT_DIRS = (
    Path(".claude") / "skills",
    Path(".cursor") / "rules",
)


# ────────────────────────────────────────────────────────────────────────────
# Marker-based partial injection (machinery — Phase 1)
# ────────────────────────────────────────────────────────────────────────────
#
# Some files outside MANAGED_OUTPUT_DIRS contain persona-driven content that
# would otherwise need hand-updating per persona (counts, tables, lists).
# These files are mostly hand-written, but specific zones inside them are
# bracketed by marker comments and rendered from _meta.json:
#
#   <!-- chrysippus:persona-table BEGIN -->
#   ...auto-generated content...
#   <!-- chrysippus:persona-table END -->
#
# Marker syntax depends on the host file's comment style — markdown uses
# HTML comments, bash/yaml use #-style. JSON has no comment syntax, so
# JSON files use field-replace mode (parse-mutate-serialize) instead of
# marker injection — see update_json_field() below.

MARKER_FORMATS = {
    ".md":   ("<!-- chrysippus:{id} BEGIN -->", "<!-- chrysippus:{id} END -->"),
    ".mdc":  ("<!-- chrysippus:{id} BEGIN -->", "<!-- chrysippus:{id} END -->"),
    ".sh":   ("# chrysippus:{id} BEGIN",        "# chrysippus:{id} END"),
    ".yml":  ("# chrysippus:{id} BEGIN",        "# chrysippus:{id} END"),
    ".yaml": ("# chrysippus:{id} BEGIN",        "# chrysippus:{id} END"),
}

# Marker ids must be lowercase alphanumeric + hyphens. This is the same
# charset find_markers() searches for, so they stay in sync.
MARKER_ID_RE = re.compile(r"^[a-z0-9\-]+$")


def _validate_marker_id(marker_id):
    if not MARKER_ID_RE.match(marker_id):
        raise ValueError(
            f"invalid marker id {marker_id!r} — must match [a-z0-9-]+"
        )


def _markers_for(path):
    """Return (begin_line, end_line) marker strings for a file's suffix."""
    suffix = Path(path).suffix
    if suffix not in MARKER_FORMATS:
        raise ValueError(
            f"no marker format registered for suffix {suffix!r} "
            f"({path}); register one in MARKER_FORMATS"
        )
    return MARKER_FORMATS[suffix]


def _zone_pattern(begin, end):
    """Build a regex matching one BEGIN/.../END zone, capturing inner content."""
    return re.compile(
        r"(?P<begin>" + re.escape(begin) + r")"
        r"(?P<inner>.*?)"
        r"(?P<end>" + re.escape(end) + r")",
        re.DOTALL,
    )


def render_zone(text, suffix, marker_id, content):
    """Return `text` with the named zone's inner content replaced by `content`.

    The marker lines themselves are preserved. `content` is sandwiched between
    newlines so the markers stay on their own lines and the zone is readable
    when viewed raw.

    Raises ValueError if:
    - `marker_id` is not [a-z0-9-]+
    - the marker pair is missing or appears more than once
    - `content` itself contains the begin or end marker for this id
      (would create nested zones that confuse later renders)
    """
    _validate_marker_id(marker_id)

    if suffix not in MARKER_FORMATS:
        raise ValueError(
            f"no marker format registered for suffix {suffix!r}"
        )

    begin_tmpl, end_tmpl = MARKER_FORMATS[suffix]
    begin = begin_tmpl.format(id=marker_id)
    end = end_tmpl.format(id=marker_id)

    if begin in content or end in content:
        raise ValueError(
            f"render_zone refusing to inject content containing the "
            f"{marker_id!r} marker — would create nested zones"
        )

    pattern = _zone_pattern(begin, end)
    matches = list(pattern.finditer(text))
    if not matches:
        raise ValueError(
            f"marker zone {marker_id!r} not found "
            f"(expected {begin!r} ... {end!r})"
        )
    if len(matches) > 1:
        raise ValueError(
            f"marker zone {marker_id!r} appears {len(matches)} times "
            f"(expected exactly 1)"
        )

    replacement = f"{begin}\n{content.rstrip()}\n{end}"
    return pattern.sub(lambda _: replacement, text, count=1)


def inject_marker(file_path, marker_id, content):
    """Read `file_path`, replace the named zone, write back.

    Returns True if the file changed, False if already correct.
    """
    suffix = Path(file_path).suffix
    if suffix not in MARKER_FORMATS:
        raise ValueError(
            f"no marker format for suffix {suffix!r}; "
            f"use update_json_field() for JSON files"
        )
    text = Path(file_path).read_text(encoding="utf-8")
    new_text = render_zone(text, suffix, marker_id, content)
    if new_text == text:
        return False
    Path(file_path).write_text(new_text, encoding="utf-8")
    return True


def check_marker(file_path, marker_id, expected_content):
    """Return True if `file_path`'s marker zone matches `expected_content`.

    Comparison strips trailing whitespace only (matches what `inject_marker`
    actually writes, which is `\\n{content.rstrip()}\\n`). Leading whitespace
    in `content` is preserved by both inject and check, so an indented zone
    and a flush-left zone are NOT considered equal.
    """
    _validate_marker_id(marker_id)
    suffix = Path(file_path).suffix
    if suffix not in MARKER_FORMATS:
        return False
    text = Path(file_path).read_text(encoding="utf-8")
    begin_tmpl, end_tmpl = MARKER_FORMATS[suffix]
    begin = begin_tmpl.format(id=marker_id)
    end = end_tmpl.format(id=marker_id)
    pattern = _zone_pattern(begin, end)
    m = pattern.search(text)
    if not m:
        return False
    # Strip a single trailing newline from each side (boundary tolerance);
    # do NOT strip leading whitespace (an indented zone is meaningfully
    # different from a flush-left one).
    actual = m.group("inner").lstrip("\n").rstrip()
    expected = expected_content.lstrip("\n").rstrip()
    return actual == expected


def find_markers(file_path):
    """Return [(marker_id, suffix), ...] for every marker pair in the file.

    Used by tests to assert no orphan markers (markers in source files that
    aren't fed by any generator). The id charset matches MARKER_ID_RE.
    """
    suffix = Path(file_path).suffix
    if suffix not in MARKER_FORMATS:
        return []
    text = Path(file_path).read_text(encoding="utf-8")
    begin_tmpl, _ = MARKER_FORMATS[suffix]
    # Match a literal "chrysippus:<id> BEGIN" inside whatever comment style
    # this file uses, by templating with the same wildcard charset that
    # _validate_marker_id enforces.
    begin_re = re.escape(begin_tmpl).replace(r"\{id\}", r"(?P<id>[a-z0-9\-]+)")
    return [(m.group("id"), suffix) for m in re.finditer(begin_re, text)]


# ────────────────────────────────────────────────────────────────────────────
# JSON field-replace (for files that have no comment syntax)
# ────────────────────────────────────────────────────────────────────────────

def update_json_field(file_path, mutator):
    """Read JSON, apply `mutator`, write back if and only if the parsed data
    actually changed.

    `mutator` may either:
      - mutate the dict in place (idiomatic), OR
      - return a new dict (the return value, if not None, replaces the data).

    The semantic-equality check (vs string-equality) means a hand-edited
    file with non-canonical formatting (e.g. 4-space indent, reordered
    keys) is NOT rewritten when the mutator is a no-op. Only meaningful
    changes trigger a rewrite, and the rewrite is canonicalised to
    2-space indent.

    Returns True if the file was rewritten.
    """
    import copy

    path = Path(file_path)
    original_text = path.read_text(encoding="utf-8")
    original_data = json.loads(original_text)
    data = copy.deepcopy(original_data)

    result = mutator(data)
    if result is not None:
        data = result

    if data == original_data:
        return False

    new_text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    path.write_text(new_text, encoding="utf-8")
    return True


def check_json_field(file_path, expected_mutator):
    """Return True if applying `expected_mutator` to the file's JSON would
    produce no semantic change (i.e., the file already matches expected).

    Like `update_json_field`, supports both mutate-in-place and
    return-new-dict mutator styles."""
    import copy

    path = Path(file_path)
    original_data = json.loads(path.read_text(encoding="utf-8"))
    data = copy.deepcopy(original_data)

    result = expected_mutator(data)
    if result is not None:
        data = result

    return data == original_data


# ────────────────────────────────────────────────────────────────────────────
# Featured-tier filter
# ────────────────────────────────────────────────────────────────────────────

def featured_personas(personas_meta):
    """Return only personas with featured === true, preserving insertion order.

    Strict identity check (`is True`) so truthy non-bool values like
    `"false"` or `1` from a malformed _meta.json don't sneak through.
    `load_meta` already validates the field type at load, but this is
    defense-in-depth for callers using synthetic dicts.
    """
    return {p: m for p, m in personas_meta.items() if m.get("featured") is True}


def catalog_personas(personas_meta):
    """Return personas with featured !== true (false, missing, or wrong type)."""
    return {p: m for p, m in personas_meta.items() if m.get("featured") is not True}


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


# ────────────────────────────────────────────────────────────────────────────
# Consumer-file marker injection registry
# ────────────────────────────────────────────────────────────────────────────
#
# Each entry: (relative_file_path, marker_id, generator_callable)
#   - relative_file_path: file in the live repo (relative to ROOT).
#   - marker_id: matches MARKER_ID_RE and is the id used in the file's
#     <!-- chrysippus:<id> BEGIN/END --> markers (or # equivalents).
#   - generator_callable: takes personas_meta dict, returns string for
#     the zone interior.
#
# IMPORTANT: marker comments must be flush-left (column 0) in source
# files — the regex preserves text BEFORE the BEGIN marker but rewrites
# everything from BEGIN through END. An indented BEGIN with an indented
# END would have the END's indentation lost on each render. See N4
# review fix.

def _allow_list_pattern(personas_meta):
    """Generate the bash case-pattern line for hooks/activate.sh and
    hooks/session-start.sh. Two-space indented to match surrounding case
    body style; trailing `)` closes the case pattern."""
    return f"  {gen_hooks_allow_list(personas_meta)})"


# Registry entries reference gen_* functions defined later in the file.
# Lambdas defer name lookup to call time, so the registry can be defined
# here (alongside the inject/check helpers that consume it) without
# requiring a forward declaration of every generator.

CONSUMER_MARKER_INJECTIONS = [
    # hooks/ — bash case allow-list
    ("hooks/activate.sh", "allow-list",
        lambda m: _allow_list_pattern(m)),
    ("hooks/session-start.sh", "allow-list",
        lambda m: _allow_list_pattern(m)),

    # README.md
    ("README.md", "sibling-skills-table",
        lambda m: gen_persona_table(m, link_prefix="docs/personas/")),
    ("README.md", "trigger-phrases",
        lambda m: gen_trigger_phrases_list(m)),
    ("README.md", "cp-skills-per-repo",
        lambda m: gen_cp_skills_block(
            m, ".claude/skills/", src_prefix="/path/to/chrysippus")),
    ("README.md", "cp-skills-user-global",
        lambda m: gen_cp_skills_block(
            m, "~/.claude/skills/", src_prefix="/path/to/chrysippus")),

    # docs/index.md (landing — links one level down to personas/)
    ("docs/index.md", "personas-table",
        lambda m: gen_persona_table(m, link_prefix="personas/")),

    # docs/personas/index.md (catalog page — sibling links)
    ("docs/personas/index.md", "personas-table",
        lambda m: gen_personas_catalog_index_body(m)),

    # docs/subagents.md
    ("docs/subagents.md", "subagents-table",
        lambda m: gen_subagents_table(m)),

    # docs/install/
    ("docs/install/claude-code.md", "slash-commands-table",
        lambda m: gen_slash_commands_table(m)),
    ("docs/install/claude-code.md", "subagents-table",
        lambda m: gen_subagents_table(m)),
    ("docs/install/claude-code.md", "cp-skills-per-repo",
        lambda m: gen_cp_skills_block(m, ".claude/skills/")),
    ("docs/install/claude-code.md", "cp-skills-user-global",
        lambda m: gen_cp_skills_block(m, "~/.claude/skills/")),
    ("docs/install/index.md", "trigger-phrases",
        lambda m: gen_trigger_phrases_list(m)),
]


def _all_personas_meta():
    """Always-load-everything: marker zones describe the WHOLE persona set,
    independent of which subset the caller asked render to regenerate.

    Returns a meta dict keyed by sorted persona name (matches the order
    used everywhere else in the renderer for stability)."""
    available = sorted(p.name for p in RULES_DIR.iterdir() if p.is_dir())
    return {p: load_meta(p) for p in available}


def inject_consumer_markers(personas_meta_unused, root):
    """Inject auto-generated content into the marker zones of consumer
    files. Returns list of relative paths actually rewritten.

    Note: `personas_meta_unused` is intentionally ignored — consumer
    marker zones always describe the full persona set, never a subset.
    This prevents `scripts/render.py shakespeare` from silently
    corrupting README/docs/hooks tables to a 1-row table claiming only
    shakespeare ships. The arg is kept for backward-compatible signature.

    Errors from individual zone injections (missing marker pair, etc.)
    are accumulated and raised together at the end, so a typo in one
    file doesn't hide problems in the others.
    """
    del personas_meta_unused  # See docstring.
    full_meta = _all_personas_meta()
    modified = []
    errors = []
    for rel_path, marker_id, gen_fn in CONSUMER_MARKER_INJECTIONS:
        target = root / rel_path
        if not target.exists():
            # Consumer file may not exist when rendering to a fresh tmp.
            continue
        try:
            content = gen_fn(full_meta)
            if inject_marker(target, marker_id, content):
                modified.append(rel_path)
        except ValueError as e:
            errors.append(f"  {rel_path}#{marker_id}: {e}")
    if errors:
        raise ValueError(
            "marker injection failed for one or more zones:\n"
            + "\n".join(errors)
        )
    return modified


def check_consumer_markers(personas_meta_unused):
    """Return list of drift descriptions for any consumer marker zone
    whose content does not match what its generator would produce.

    Operates on files at ROOT directly — these are not under
    MANAGED_OUTPUT_DIRS and are not rendered to the tmp out_root.

    Distinguishes "marker pair missing" (structural — markers were
    deleted from the file) from "content drifted" (markers exist but
    their interior doesn't match what render would produce). The two
    states need different fixes, so they get different error messages.

    `personas_meta_unused` is ignored for the same reason as
    inject_consumer_markers — checks always run against the full
    persona set.
    """
    del personas_meta_unused  # See docstring.
    full_meta = _all_personas_meta()
    drifts = []
    for rel_path, marker_id, gen_fn in CONSUMER_MARKER_INJECTIONS:
        target = ROOT / rel_path
        if not target.exists():
            drifts.append(
                f"  {rel_path}: marker target file is missing"
            )
            continue
        # Detect "marker pair missing" structurally so the error message
        # tells the user the right thing to do (add the markers vs
        # re-render to refresh content).
        present_ids = {mid for mid, _ in find_markers(target)}
        if marker_id not in present_ids:
            drifts.append(
                f"  {rel_path}#{marker_id}: marker pair missing — "
                f"add the BEGIN/END comment markers around the "
                f"auto-rendered zone"
            )
            continue
        expected = gen_fn(full_meta)
        if not check_marker(target, marker_id, expected):
            drifts.append(
                f"  {rel_path}#{marker_id}: marker zone content drifted "
                f"(re-run `scripts/render.py` to regenerate)"
            )
    return drifts


def do_render(personas, out_root):
    personas_meta = {p: load_meta(p) for p in personas}
    text_outputs = build_text_outputs(personas_meta, out_root)
    copy_outputs = build_copy_outputs(personas, out_root)

    for target, content in text_outputs:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    for target, src in copy_outputs:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, target)

    # Marker injection only runs when rendering to the actual repo
    # (out_root == ROOT). For --out (tmp dir for tests) the consumer
    # files don't exist in tmp, so we skip silently.
    marker_modified = []
    if out_root == ROOT:
        marker_modified = inject_consumer_markers(personas_meta, out_root)

    total = len(text_outputs) + len(copy_outputs) + len(marker_modified)
    print(f"rendered {len(personas)} persona(s) to {total} output file(s)")
    return 0


def run_check(personas):
    """Render to a tmp dir; diff each file against committed; check marker
    zones in consumer files; exit 1 on any drift."""
    drifts = []
    with tempfile.TemporaryDirectory() as tmp:
        tmp_root = Path(tmp)
        do_render(personas, tmp_root)

        # Compare every file we rendered against the committed equivalent
        personas_meta = {p: load_meta(p) for p in personas}
        text_outputs = build_text_outputs(personas_meta, tmp_root)
        copy_outputs = build_copy_outputs(personas, tmp_root)

        rendered_rel_paths = set()
        for target, _ in text_outputs + copy_outputs:
            rel = target.relative_to(tmp_root)
            rendered_rel_paths.add(rel)
            committed = ROOT / rel
            if not committed.exists():
                drifts.append(f"  {rel}: rendered but not committed")
                continue
            a = committed.read_text(encoding="utf-8").splitlines()
            b = target.read_text(encoding="utf-8").splitlines()
            if a != b:
                diff = "\n".join(difflib.unified_diff(
                    a, b,
                    fromfile=f"committed/{rel}",
                    tofile=f"rendered/{rel}",
                    lineterm="",
                ))
                drifts.append(diff)

        # Detect orphans — committed files in managed dirs that weren't rendered
        # this run (typically stale files left behind when a persona was removed
        # from rules/).
        for orphan in find_orphans(rendered_rel_paths):
            drifts.append(
                f"  {orphan}: committed but not rendered (stale — "
                "persona removed from rules/?)"
            )

    # Check marker zones in consumer files (operate on ROOT directly,
    # not the tmp render — these files live in the repo, not in
    # MANAGED_OUTPUT_DIRS).
    personas_meta = {p: load_meta(p) for p in personas}
    drifts.extend(check_consumer_markers(personas_meta))

    if drifts:
        print("DRIFT — generated output does not match committed files:", file=sys.stderr)
        print("", file=sys.stderr)
        for d in drifts:
            print(d, file=sys.stderr)
        print("", file=sys.stderr)
        print(
            "To fix: run scripts/render.py and commit the result. If stale "
            "files are reported, `git rm` them.",
            file=sys.stderr,
        )
        return 1

    print(f"clean — {len(personas)} persona(s) match committed output")
    return 0


def find_orphans(rendered_rel_paths, committed_root=None):
    """Return sorted list of relative Paths committed under MANAGED_OUTPUT_DIRS
    that are NOT in `rendered_rel_paths`.

    `rendered_rel_paths` must be a set of Paths relative to the output root.
    """
    committed_root = Path(committed_root) if committed_root else ROOT
    orphans = []
    for sub in MANAGED_OUTPUT_DIRS:
        full = committed_root / sub
        if not full.exists():
            continue
        for f in full.rglob("*"):
            if not f.is_file():
                continue
            rel = f.relative_to(committed_root)
            if rel not in rendered_rel_paths:
                orphans.append(rel)
    return sorted(orphans)


# ────────────────────────────────────────────────────────────────────────────
# Source loading
# ────────────────────────────────────────────────────────────────────────────

REQUIRED_META_FIELDS = (
    "name", "version", "description", "triggers", "flavors",
    "preserve_defaults", "register_short",
)


def _validate_meta(meta, persona):
    """Raise ValueError on a malformed _meta.json. Catches contributor typos
    early instead of letting them silently produce broken output."""

    missing = [f for f in REQUIRED_META_FIELDS if f not in meta]
    if missing:
        raise ValueError(
            f"rules/{persona}/_meta.json missing required field(s): "
            f"{', '.join(missing)}"
        )

    # Strict bool — accept True/False only. JSON allows strings, so
    # `"featured": "false"` is truthy in Python and would silently promote.
    if "featured" in meta and not isinstance(meta["featured"], bool):
        raise ValueError(
            f"rules/{persona}/_meta.json: 'featured' must be true or false "
            f"(got {meta['featured']!r}, type {type(meta['featured']).__name__})"
        )

    if not isinstance(meta["register_short"], str) or not meta["register_short"].strip():
        raise ValueError(
            f"rules/{persona}/_meta.json: 'register_short' must be a "
            f"non-empty string (got {meta['register_short']!r})"
        )

    # register_short is rendered into markdown table cells. Pipes break
    # the column count, newlines break the row entirely, backticks would
    # need balancing. Reject these to avoid silently-corrupted tables.
    bad_chars = [c for c in ("|", "\n", "\r", "`") if c in meta["register_short"]]
    if bad_chars:
        raise ValueError(
            f"rules/{persona}/_meta.json: 'register_short' contains "
            f"table-breaking characters {bad_chars!r}; remove them "
            f"(register_short is rendered into markdown table cells)"
        )

    flavors = meta["flavors"]
    if not isinstance(flavors, list) or not flavors:
        raise ValueError(
            f"rules/{persona}/_meta.json: 'flavors' must be a non-empty list"
        )
    defaults = [f for f in flavors if f.get("default")]
    if len(defaults) != 1:
        raise ValueError(
            f"rules/{persona}/_meta.json: exactly one flavor must have "
            f"\"default\": true (found {len(defaults)})"
        )

    triggers = meta["triggers"]
    if not isinstance(triggers, list) or not triggers:
        raise ValueError(
            f"rules/{persona}/_meta.json: 'triggers' must be a non-empty list"
        )


def load_meta(persona):
    src = RULES_DIR / persona
    meta_path = src / "_meta.json"
    if not meta_path.exists():
        raise FileNotFoundError(f"missing {meta_path}")
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    _validate_meta(meta, persona)
    meta["_instructions"] = (src / "instructions.md").read_text(encoding="utf-8")
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

    # Persona-driven single files in shared dirs (commands/, agents/).
    # NOT in MANAGED_OUTPUT_DIRS because these dirs also contain
    # hand-written per-persona files that must not be flagged as orphans.
    outputs.append((out_root / "commands" / "personas.md",
                    render_personas_command_md(personas_meta)))
    outputs.append((out_root / "agents" / "dramaturg.md",
                    render_dramaturg_md(personas_meta)))

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
            lock_note = "HARD-LOCKED, cannot be changed"
            comment = f"{comment} — {lock_note}" if comment else lock_note
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
# Partial generators — pure functions returning markdown / shell strings
# ────────────────────────────────────────────────────────────────────────────
#
# Each `gen_*` returns a string ready to drop into a marker zone in a
# consumer file. Generators are pure: given the same personas_meta, the
# same string. Phase 2 will wire these into render runs that inject into
# README, docs/, install/, hooks/.

def _persona_default_flavor(meta):
    """Return the name of the default flavor, or raise ValueError with a
    clear message naming the offending persona (NOT a cryptic
    StopIteration)."""
    for f in meta["flavors"]:
        if f.get("default"):
            return f["name"]
    raise ValueError(
        f"persona {meta.get('name', '?')!r} has no flavor with "
        f"\"default\": true (load_meta should have caught this; "
        f"the input dict was constructed manually)"
    )


def _persona_other_flavors(meta, *, empty_label, fmt="`{}`", joiner=", "):
    others = [f["name"] for f in meta["flavors"] if not f.get("default")]
    if not others:
        return empty_label
    return joiner.join(fmt.format(f) for f in others)


def _persona_title(persona):
    """'gen-alpha' → 'Gen-Alpha', 'toronto-mans' → 'Toronto-Mans'."""
    return "-".join(part.capitalize() for part in persona.split("-"))


# Markdown special characters that need escaping inside trigger phrases
# rendered as italic-quoted prose. Keep this list narrow — we don't want
# to over-escape and produce ugly output for the common case.
_MARKDOWN_SPECIAL = ("\\", "*", "_", "`", "[", "]", "<", ">")


def _md_escape(s):
    """Backslash-escape markdown-significant chars in a string. Used so a
    trigger like `*"hot tip"*` doesn't render as bold. Backslash MUST be
    escaped first or it would double-escape subsequent escapes."""
    for c in _MARKDOWN_SPECIAL:
        s = s.replace(c, "\\" + c)
    return s


def _require_personas(personas_meta, fn_name):
    """Generators emit broken output (empty tables, empty `case` bodies)
    on empty input. Raise loudly instead so callers don't silently produce
    corrupt files."""
    if not personas_meta:
        raise ValueError(
            f"{fn_name}: personas_meta is empty — at least one persona "
            f"required to generate this output"
        )


def gen_persona_table(personas_meta, *, link_prefix=""):
    """Persona | Register | Default flavor | Other flavors — used in
    README sibling-skills section, docs/personas/index.md, etc.

    `link_prefix` is prepended to `<persona>.md` in the link cell
    (use `"personas/"` for tables that live one directory above the
    persona pages).
    """
    _require_personas(personas_meta, "gen_persona_table")
    rows = [
        "| Persona | Register | Default flavor | Other flavors |",
        "|---|---|---|---|",
    ]
    for persona, meta in personas_meta.items():
        link = f"[`{persona}`]({link_prefix}{persona}.md)"
        register = meta["register_short"]  # validated non-empty by load_meta
        default = f"`{_persona_default_flavor(meta)}`"
        others = _persona_other_flavors(
            meta, empty_label="*(single flavor in v1)*"
        )
        rows.append(f"| {link} | {register} | {default} | {others} |")
    return "\n".join(rows)


def gen_personas_command_table(personas_meta):
    """Plain table (no links, no register column) for commands/personas.md."""
    _require_personas(personas_meta, "gen_personas_command_table")
    rows = [
        "| Persona | Default flavor | Other flavors |",
        "|---|---|---|",
    ]
    for persona, meta in personas_meta.items():
        default = f"`{_persona_default_flavor(meta)}`"
        others = _persona_other_flavors(
            meta, empty_label="(single flavor in v1)"
        )
        rows.append(f"| `{persona}` | {default} | {others} |")
    return "\n".join(rows)


def gen_slash_commands_table(personas_meta):
    """| Command | Effect | rows for each persona's slash command + the
    /chrysippus:personas listing command."""
    _require_personas(personas_meta, "gen_slash_commands_table")
    rows = ["| Command | Effect |", "|---|---|"]
    for persona in personas_meta:
        rows.append(
            f"| `/chrysippus:{persona}` | "
            f"Activate {persona} for this session |"
        )
    rows.append(
        "| `/chrysippus:personas` | "
        "List installed personas; show which is active |"
    )
    return "\n".join(rows)


def gen_subagents_table(personas_meta):
    """| Subagent | Purpose | rows for each <persona>-reviewer + dramaturg."""
    _require_personas(personas_meta, "gen_subagents_table")
    rows = ["| Subagent | Purpose |", "|---|---|"]
    for persona in personas_meta:
        rows.append(
            f"| `{persona}-reviewer` | "
            f"PR / branch review in {persona} voice |"
        )
    rows.append(
        "| `dramaturg` | Meta-agent — audits persona rule-adherence |"
    )
    return "\n".join(rows)


def gen_trigger_phrases_list(personas_meta):
    """Bullet list, one per persona:
        - **Persona-Title**: *"phrase"*, *"phrase"*, `/slash`.
    Slash triggers (starting with /) get backticks; others get italic
    quotes with markdown-special characters backslash-escaped.
    """
    _require_personas(personas_meta, "gen_trigger_phrases_list")
    lines = []
    for persona, meta in personas_meta.items():
        title = _persona_title(persona)
        formatted = []
        for t in meta["triggers"]:
            if t.startswith("/"):
                # Inside backticks no escaping needed (code spans are literal)
                formatted.append(f"`{t}`")
            else:
                formatted.append(f'*"{_md_escape(t)}"*')
        lines.append(f"- **{title}**: {', '.join(formatted)}.")
    return "\n".join(lines)


def gen_cp_skills_block(personas_meta, dest, *, src_prefix="/tmp/chrysippus"):
    """One `cp -r` line per persona, copying the rendered skill folder into
    `dest`. Used in install docs to replace brace-expanded one-liners."""
    _require_personas(personas_meta, "gen_cp_skills_block")
    lines = []
    for persona in personas_meta:
        lines.append(
            f"cp -r {src_prefix}/.claude/skills/{persona} {dest}"
        )
    return "\n".join(lines)


def gen_hooks_allow_list(personas_meta):
    """Pipe-separated alternation for the bash `case` statement in
    hooks/activate.sh and hooks/session-start.sh:
        shakespeare|pirate|gen-alpha|toronto-mans|ontario-bud

    An empty result would be a bash syntax error in `case` — guard against it.
    """
    _require_personas(personas_meta, "gen_hooks_allow_list")
    return "|".join(personas_meta.keys())


def gen_dramaturg_skills(personas_meta):
    """YAML inline-list for agents/dramaturg.md frontmatter:
        [shakespeare, pirate, gen-alpha, toronto-mans, ontario-bud]
    """
    _require_personas(personas_meta, "gen_dramaturg_skills")
    return "[" + ", ".join(personas_meta.keys()) + "]"


def gen_personas_catalog_index_body(personas_meta):
    """Body of docs/personas/index.md — featured table first, then a
    Catalog section if any non-featured personas exist."""
    featured = featured_personas(personas_meta)
    catalog = catalog_personas(personas_meta)

    parts = [gen_persona_table(featured)]
    if catalog:
        parts.extend([
            "",
            "## Catalog (additional personas)",
            "",
            "These personas are installed but not featured on the landing"
            " demos.",
            "",
            gen_persona_table(catalog),
        ])
    return "\n".join(parts)


# ────────────────────────────────────────────────────────────────────────────
# Full-file generators — commands/personas.md, agents/dramaturg.md
# ────────────────────────────────────────────────────────────────────────────
#
# These files are short and almost-entirely persona-driven, so we template
# them whole. Both live in directories that also contain hand-written
# per-persona files (commands/<persona>.md, agents/<persona>-reviewer.md),
# so we register them as text_outputs but do NOT add their parent dirs to
# MANAGED_OUTPUT_DIRS — the orphan-check would flag the hand-written files.
#
# Body templates live in scripts/templates/ — moving them out of Python
# string literals keeps prose edits in plain markdown (reviewable as a
# normal diff) and avoids accidental \-escape bugs.

def _expand_template(text, **vars):
    """Tiny mustache-style expansion: {{key}} → value. Used so templates
    written in plain markdown can host a few persona-driven slots without
    needing str.format's brace-doubling rules."""
    for key, value in vars.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def _load_template(name):
    return (TEMPLATES_DIR / name).read_text(encoding="utf-8")


def render_personas_command_md(personas_meta):
    return _expand_template(
        _load_template("personas-command.md"),
        table=gen_personas_command_table(personas_meta),
    )


def render_dramaturg_md(personas_meta):
    return _expand_template(
        _load_template("dramaturg.md"),
        skills=gen_dramaturg_skills(personas_meta),
    )


# ────────────────────────────────────────────────────────────────────────────
# Multi-agent single-file targets — shared body
# ────────────────────────────────────────────────────────────────────────────

def _persona_table_row(persona, meta):
    default_flavor = next(f["name"] for f in meta["flavors"] if f.get("default"))
    others = [f["name"] for f in meta["flavors"] if not f.get("default")]
    others_str = ", ".join(f"`{f}`" for f in others) if others else "(none)"
    return f"| `{persona}` | `{default_flavor}` | {others_str} |"


def _quote_trigger_for_markdown(trigger):
    """Render a trigger phrase as a double-quoted italic token, escaping any
    embedded double quotes. Replaces a previous repr-based implementation that
    corrupted triggers containing single quotes."""
    escaped = trigger.replace('"', '\\"')
    return f'*"{escaped}"*'


def _activation_line(persona, meta):
    triggers = ", ".join(_quote_trigger_for_markdown(t) for t in meta["triggers"])
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
