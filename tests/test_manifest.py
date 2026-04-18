"""Tests for plugin.json and marketplace.json manifest validity."""

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class TestPluginJson(unittest.TestCase):
    def setUp(self):
        self.manifest_path = ROOT / ".claude-plugin" / "plugin.json"
        self.assertTrue(self.manifest_path.exists(), f"missing {self.manifest_path}")
        self.manifest = json.loads(self.manifest_path.read_text())

    def test_required_fields_present(self):
        self.assertIn("name", self.manifest)
        self.assertEqual(self.manifest["name"], "chrysippus")

    def test_version_is_semver_shaped(self):
        version = self.manifest.get("version", "")
        parts = version.split(".")
        self.assertEqual(len(parts), 3, f"version '{version}' is not semver-shaped")
        for part in parts:
            self.assertTrue(part.isdigit(), f"version part '{part}' is not numeric")

    def test_component_paths_exist(self):
        for key in ("skills", "commands", "agents", "hooks"):
            value = self.manifest.get(key)
            if value is None:
                continue
            target = ROOT / value
            with self.subTest(key=key, path=value):
                self.assertTrue(
                    target.exists(),
                    f"plugin.json declares {key}={value} but {target} does not exist",
                )

    def test_license_is_mit(self):
        self.assertEqual(self.manifest.get("license"), "MIT")

    def test_keywords_include_persona_names(self):
        keywords = self.manifest.get("keywords", [])
        for persona in ("shakespeare", "pirate", "gen-alpha", "toronto-mans"):
            with self.subTest(persona=persona):
                self.assertIn(persona, keywords, f"keywords missing '{persona}'")


class TestMarketplaceJson(unittest.TestCase):
    def setUp(self):
        self.manifest_path = ROOT / ".claude-plugin" / "marketplace.json"
        self.assertTrue(self.manifest_path.exists(), f"missing {self.manifest_path}")
        self.manifest = json.loads(self.manifest_path.read_text())

    def test_required_fields_present(self):
        self.assertIn("name", self.manifest)
        self.assertIn("owner", self.manifest)
        self.assertIn("name", self.manifest["owner"])
        self.assertIn("plugins", self.manifest)
        self.assertIsInstance(self.manifest["plugins"], list)
        self.assertGreater(len(self.manifest["plugins"]), 0)

    def test_plugin_source_is_github(self):
        entry = self.manifest["plugins"][0]
        source = entry.get("source")
        self.assertIsInstance(source, dict, "source should be an object")
        self.assertEqual(source.get("source"), "github")
        self.assertIn("/", source.get("repo", ""), "repo should be 'owner/name'")


if __name__ == "__main__":
    unittest.main()
