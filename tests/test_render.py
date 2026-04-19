"""Tests for scripts/render.py — the canonical source-of-truth generator."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RULES_DIR = ROOT / "rules"
SCRIPTS_DIR = ROOT / "scripts"

sys.path.insert(0, str(SCRIPTS_DIR))
import render  # noqa: E402


class TestRenderRoundTrip(unittest.TestCase):
    """Rendering the source should produce output that matches what's committed."""

    def test_check_reports_clean_on_fresh_render(self):
        """`render.py --check` must report clean against the committed outputs."""
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "render.py"), "--check"],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )
        self.assertEqual(
            result.returncode, 0,
            msg=f"--check reported drift:\nstdout: {result.stdout}\nstderr: {result.stderr}",
        )

    def test_render_is_idempotent(self):
        """Running render twice produces byte-identical output."""
        with tempfile.TemporaryDirectory() as tmp1, tempfile.TemporaryDirectory() as tmp2:
            subprocess.run(
                [sys.executable, str(SCRIPTS_DIR / "render.py"), "--out", tmp1],
                check=True, cwd=str(ROOT),
            )
            subprocess.run(
                [sys.executable, str(SCRIPTS_DIR / "render.py"), "--out", tmp2],
                check=True, cwd=str(ROOT),
            )

            files_1 = sorted(Path(tmp1).rglob("*"))
            files_2 = sorted(Path(tmp2).rglob("*"))
            self.assertEqual(
                [f.relative_to(tmp1) for f in files_1 if f.is_file()],
                [f.relative_to(tmp2) for f in files_2 if f.is_file()],
                msg="render produced different file sets on two runs",
            )
            for f1 in files_1:
                if not f1.is_file():
                    continue
                f2 = Path(tmp2) / f1.relative_to(tmp1)
                self.assertEqual(
                    f1.read_bytes(), f2.read_bytes(),
                    msg=f"{f1.relative_to(tmp1)} differs between two renders",
                )


class TestRenderedClaudeSkills(unittest.TestCase):
    """Check per-persona Claude Code skill output structure."""

    def test_every_persona_has_skill_md_with_frontmatter(self):
        for persona_dir in RULES_DIR.iterdir():
            if not persona_dir.is_dir():
                continue
            skill_md = ROOT / ".claude" / "skills" / persona_dir.name / "SKILL.md"
            with self.subTest(persona=persona_dir.name):
                self.assertTrue(skill_md.exists(), f"missing {skill_md}")
                content = skill_md.read_text()
                self.assertTrue(
                    content.startswith("---\n"),
                    f"{skill_md} does not start with YAML frontmatter",
                )
                self.assertIn("name: ", content[:200])
                self.assertIn("description: >", content[:500])

    def test_every_persona_has_config(self):
        for persona_dir in RULES_DIR.iterdir():
            if not persona_dir.is_dir():
                continue
            config = ROOT / ".claude" / "skills" / persona_dir.name / f"{persona_dir.name}.config"
            with self.subTest(persona=persona_dir.name):
                self.assertTrue(config.exists(), f"missing {config}")
                content = config.read_text()
                self.assertIn("flavor:", content)
                self.assertIn("preserve:", content)
                self.assertIn("safety_warnings:", content)

    def test_preserve_locked_rendered_with_marker(self):
        """Persona metas with preserve_locked should show the lock in the .config."""
        for persona_dir in RULES_DIR.iterdir():
            if not persona_dir.is_dir():
                continue
            meta = json.loads((persona_dir / "_meta.json").read_text())
            locked = meta.get("preserve_locked") or []
            if not locked:
                continue
            config = ROOT / ".claude" / "skills" / persona_dir.name / f"{persona_dir.name}.config"
            content = config.read_text()
            for key in locked:
                with self.subTest(persona=persona_dir.name, key=key):
                    self.assertIn(
                        "HARD-LOCKED", content,
                        f"{persona_dir.name}: preserve_locked key '{key}' has no HARD-LOCKED marker in config",
                    )


class TestRenderedMultiAgent(unittest.TestCase):
    """Check the presence and basic structure of multi-agent output files."""

    EXPECTED_ROOT_FILES = [
        "AGENTS.md",
        "GEMINI.md",
        "CONVENTIONS.md",
        ".windsurfrules",
        ".clinerules",
    ]

    def test_root_multi_agent_files_present(self):
        all_personas = sorted(p.name for p in RULES_DIR.iterdir() if p.is_dir())
        for name in self.EXPECTED_ROOT_FILES:
            with self.subTest(file=name):
                path = ROOT / name
                self.assertTrue(path.exists(), f"missing {path}")
                content = path.read_text()
                # Each multi-agent file should document "persona" concept
                # and list every persona name in its body.
                self.assertIn("persona", content.lower()[:2000])
                for persona in all_personas:
                    self.assertIn(
                        persona, content,
                        f"{name}: missing persona name '{persona}'",
                    )

    def test_every_persona_has_cursor_mdc(self):
        personas = sorted(
            p.name for p in RULES_DIR.iterdir() if p.is_dir()
        )
        for persona in personas:
            with self.subTest(persona=persona):
                mdc = ROOT / ".cursor" / "rules" / f"{persona}.mdc"
                self.assertTrue(mdc.exists(), f"missing {mdc}")
                content = mdc.read_text()
                self.assertTrue(content.startswith("---\n"))
                self.assertIn("description: ", content[:1000])
                self.assertIn("alwaysApply:", content[:1000])


class TestHandWrittenPerPersonaFiles(unittest.TestCase):
    """Per-persona slash command and reviewer subagent files are
    intentionally hand-written (not auto-generated). These tests enforce
    that every persona has them, so a new persona PR can't merge with
    them missing."""

    def test_every_persona_has_command_md(self):
        for persona_dir in RULES_DIR.iterdir():
            if not persona_dir.is_dir():
                continue
            cmd = ROOT / "commands" / f"{persona_dir.name}.md"
            with self.subTest(persona=persona_dir.name):
                self.assertTrue(
                    cmd.exists(),
                    f"missing hand-written {cmd} — every persona needs a "
                    f"slash-command file under commands/",
                )
                # Sanity: must declare itself as a slash command (has
                # YAML frontmatter with a description).
                content = cmd.read_text(encoding="utf-8")
                self.assertTrue(content.startswith("---\n"),
                                f"{cmd} missing YAML frontmatter")
                self.assertIn("description:", content[:300])

    def test_every_persona_has_reviewer_md(self):
        for persona_dir in RULES_DIR.iterdir():
            if not persona_dir.is_dir():
                continue
            rev = ROOT / "agents" / f"{persona_dir.name}-reviewer.md"
            with self.subTest(persona=persona_dir.name):
                self.assertTrue(
                    rev.exists(),
                    f"missing hand-written {rev} — every persona needs a "
                    f"reviewer subagent under agents/",
                )
                content = rev.read_text(encoding="utf-8")
                self.assertTrue(content.startswith("---\n"))
                # Must declare the corresponding skill in frontmatter so
                # the reviewer loads the right register.
                self.assertIn(f"skills: [{persona_dir.name}]", content[:500])


class TestRenderFunctions(unittest.TestCase):
    """Unit-level tests of the render.py module functions."""

    def test_render_config_includes_all_preserve_keys(self):
        meta = render.load_meta("shakespeare")
        config = render.render_config(meta)
        for key in meta["preserve_defaults"]:
            with self.subTest(key=key):
                self.assertIn(f"{key}:", config)

    def test_render_skill_md_frontmatter_is_well_formed(self):
        meta = render.load_meta("pirate")
        skill_md = render.render_claude_skill_md(meta)
        self.assertTrue(skill_md.startswith("---\n"))
        head, _, _ = skill_md.partition("\n---\n")
        self.assertIn("name: pirate", head)
        self.assertIn("description: >", head)

    def test_render_rejects_unknown_persona(self):
        with self.assertRaises(FileNotFoundError):
            render.load_meta("no-such-persona")

    def test_render_config_locked_keys_show_no_double_dash_when_no_comment(self):
        """Regression: HARD-LOCKED suffix used to leak a leading ' — ' when
        the underlying preserve_comments lookup returned an empty string."""
        meta = {
            "name": "synthetic",
            "flavors": [{"name": "x", "description": "x", "default": True}],
            "preserve_defaults": {"unknown_key_with_no_comment": True},
            "preserve_locked": ["unknown_key_with_no_comment"],
        }
        out = render.render_config(meta)
        # Should contain the lock note without leading " — "
        self.assertIn("HARD-LOCKED, cannot be changed", out)
        self.assertNotIn("#  — HARD-LOCKED", out)
        self.assertNotIn("# — HARD-LOCKED", out)


class TestActivationLineQuoting(unittest.TestCase):
    """Regression tests for the trigger-quoting bug in _activation_line.

    The previous implementation used `f"*{t!r}*".replace("'", '"')` which
    silently corrupted triggers containing single quotes (because repr would
    switch to double-quoted form, defeating the replace).
    """

    def test_quote_trigger_handles_plain_text(self):
        self.assertEqual(
            render._quote_trigger_for_markdown("speak like Shakespeare"),
            '*"speak like Shakespeare"*',
        )

    def test_quote_trigger_handles_single_quote(self):
        # Was previously broken: repr would emit `"thee 'n' thou"` (double-
        # quoted) and the .replace would corrupt the inner single quotes.
        out = render._quote_trigger_for_markdown("thee 'n' thou")
        self.assertEqual(out, '*"thee \'n\' thou"*')

    def test_quote_trigger_escapes_double_quote(self):
        out = render._quote_trigger_for_markdown('say "hello"')
        self.assertEqual(out, '*"say \\"hello\\""*')

    def test_activation_line_uses_safe_quoting(self):
        meta = {"triggers": ["foo", "bar's baz"]}
        line = render._activation_line("synthetic", meta)
        self.assertIn('*"foo"*', line)
        self.assertIn('*"bar\'s baz"*', line)


class TestFindOrphans(unittest.TestCase):
    """Regression tests for orphan-file detection in run_check.

    The previous run_check only iterated over rendered outputs; if a persona
    was removed from rules/, the stale .claude/skills/<persona>/ files would
    pass the drift check unnoticed.
    """

    def test_no_orphans_in_clean_repo(self):
        # All files under MANAGED_OUTPUT_DIRS in the live repo should be
        # accounted for by a fresh render. (This is what `--check` itself
        # asserts in CI; here we exercise find_orphans directly.)
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            personas = sorted(p.name for p in render.RULES_DIR.iterdir() if p.is_dir())
            render.do_render(personas, tmp_root)
            personas_meta = {p: render.load_meta(p) for p in personas}
            text_outputs = render.build_text_outputs(personas_meta, tmp_root)
            copy_outputs = render.build_copy_outputs(personas, tmp_root)
            rendered = {t.relative_to(tmp_root) for t, _ in text_outputs + copy_outputs}
            orphans = render.find_orphans(rendered)
        self.assertEqual(orphans, [], f"unexpected orphans in clean repo: {orphans}")

    def test_orphan_detected_in_managed_dir(self):
        """Synthesise a stale committed file in a temp 'committed' tree and
        verify find_orphans flags it."""
        with tempfile.TemporaryDirectory() as tmp:
            committed = Path(tmp)
            stale_skill = committed / ".claude" / "skills" / "ghost-persona" / "SKILL.md"
            stale_skill.parent.mkdir(parents=True)
            stale_skill.write_text("# stale\n")
            stale_mdc = committed / ".cursor" / "rules" / "ghost-persona.mdc"
            stale_mdc.parent.mkdir(parents=True)
            stale_mdc.write_text("---\n")

            rendered = set()  # nothing rendered → both files are orphans
            orphans = render.find_orphans(rendered, committed_root=committed)

        self.assertEqual(
            sorted(str(p) for p in orphans),
            sorted([
                str(Path(".claude/skills/ghost-persona/SKILL.md")),
                str(Path(".cursor/rules/ghost-persona.mdc")),
            ]),
        )

    def test_orphan_detection_ignores_unmanaged_dirs(self):
        """Files outside MANAGED_OUTPUT_DIRS must never be flagged as orphans."""
        with tempfile.TemporaryDirectory() as tmp:
            committed = Path(tmp)
            unmanaged = committed / "src" / "user_code.py"
            unmanaged.parent.mkdir(parents=True)
            unmanaged.write_text("# user file, not chrysippus's business\n")
            orphans = render.find_orphans(set(), committed_root=committed)
        self.assertEqual(orphans, [])


if __name__ == "__main__":
    unittest.main()
