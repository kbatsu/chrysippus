"""Tests for the shell scripts in hooks/."""

import os
import shutil
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOOKS_DIR = ROOT / "hooks"


class TestHooksFilePresence(unittest.TestCase):
    def test_expected_hook_files_exist(self):
        for name in ("hooks.json", "session-start.sh", "activate.sh"):
            with self.subTest(file=name):
                path = HOOKS_DIR / name
                self.assertTrue(path.exists(), f"missing {path}")

    def test_shell_scripts_are_executable(self):
        for name in ("session-start.sh", "activate.sh"):
            with self.subTest(file=name):
                path = HOOKS_DIR / name
                mode = path.stat().st_mode
                self.assertTrue(
                    mode & stat.S_IXUSR,
                    f"{path} is not executable by owner",
                )


class TestHooksSyntaxClean(unittest.TestCase):
    def test_shell_scripts_pass_syntax_check(self):
        for name in ("session-start.sh", "activate.sh"):
            with self.subTest(file=name):
                result = subprocess.run(
                    ["bash", "-n", str(HOOKS_DIR / name)],
                    capture_output=True, text=True,
                )
                self.assertEqual(
                    result.returncode, 0,
                    f"{name} has shell syntax errors:\n{result.stderr}",
                )


class TestHooksJson(unittest.TestCase):
    def test_hooks_json_parses_and_declares_sessionstart(self):
        import json
        data = json.loads((HOOKS_DIR / "hooks.json").read_text())
        self.assertIn("hooks", data)
        self.assertIn("SessionStart", data["hooks"])


class TestActivateScript(unittest.TestCase):
    """Run activate.sh against a tmpdir-mocked $CLAUDE_PROJECT_DIR."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.env = {**os.environ, "CLAUDE_PROJECT_DIR": self.tmp}
        self.state_file = Path(self.tmp) / ".claude" / "personas" / "active"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_activate(self, *args):
        return subprocess.run(
            ["bash", str(HOOKS_DIR / "activate.sh"), *args],
            capture_output=True, text=True,
            env=self.env,
        )

    def test_activate_shakespeare_writes_state_file(self):
        result = self.run_activate("shakespeare")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(self.state_file.exists())
        self.assertEqual(self.state_file.read_text().strip(), "shakespeare")

    def test_activate_off_removes_state_file(self):
        self.run_activate("shakespeare")
        result = self.run_activate("off")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertFalse(self.state_file.exists())

    def test_activate_rejects_unknown_persona(self):
        result = self.run_activate("not-a-real-persona")
        self.assertNotEqual(result.returncode, 0, "should fail for unknown persona")
        self.assertFalse(self.state_file.exists())

    def test_activate_status_when_set(self):
        self.run_activate("pirate")
        result = self.run_activate("status")
        self.assertEqual(result.returncode, 0)
        self.assertIn("pirate", result.stdout)

    def test_activate_status_when_unset(self):
        result = self.run_activate("status")
        self.assertEqual(result.returncode, 0)
        self.assertIn("no auto-activation", result.stdout)

    def test_activate_is_idempotent(self):
        self.run_activate("shakespeare")
        result = self.run_activate("shakespeare")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(self.state_file.read_text().strip(), "shakespeare")


class TestSessionStartHook(unittest.TestCase):
    """Run session-start.sh against a tmpdir-mocked project."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.env = {**os.environ, "CLAUDE_PROJECT_DIR": self.tmp}
        self.state_file = Path(self.tmp) / ".claude" / "personas" / "active"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_hook(self):
        return subprocess.run(
            ["bash", str(HOOKS_DIR / "session-start.sh")],
            capture_output=True, text=True,
            env=self.env,
        )

    def test_emits_nothing_when_state_missing(self):
        result = self.run_hook()
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "")

    def test_emits_activation_when_state_set(self):
        self.state_file.parent.mkdir(parents=True)
        self.state_file.write_text("shakespeare\n")
        result = self.run_hook()
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("shakespeare", result.stdout)
        self.assertIn("auto-activate", result.stdout.lower())

    def test_silently_ignores_unknown_persona(self):
        self.state_file.parent.mkdir(parents=True)
        self.state_file.write_text("not-a-real-persona\n")
        result = self.run_hook()
        # Unknown persona → exit 0, emit nothing on stdout (log to stderr).
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "")

    def test_handles_empty_state_file(self):
        self.state_file.parent.mkdir(parents=True)
        self.state_file.write_text("")
        result = self.run_hook()
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "")


if __name__ == "__main__":
    unittest.main()
