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
        for name in self.EXPECTED_ROOT_FILES:
            with self.subTest(file=name):
                path = ROOT / name
                self.assertTrue(path.exists(), f"missing {path}")
                content = path.read_text()
                # Each multi-agent file should document "persona" concept
                # and list all 4 persona names in its body.
                self.assertIn("persona", content.lower()[:2000])
                for persona in ("shakespeare", "pirate", "gen-alpha", "toronto-mans"):
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


if __name__ == "__main__":
    unittest.main()
