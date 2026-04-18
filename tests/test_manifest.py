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

    def test_plugin_name_matches_plugin_json(self):
        """plugin.json `name` must match marketplace.json plugin entry name."""
        marketplace = json.loads(
            (ROOT / ".claude-plugin" / "marketplace.json").read_text()
        )
        plugin_entry = marketplace["plugins"][0]
        self.assertEqual(self.manifest["name"], plugin_entry["name"])

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

    def test_plugin_source_is_a_valid_form(self):
        """Source must be one of the Claude Code plugin-marketplace source
        forms. For our monorepo setup (plugin content lives in the same repo
        as marketplace.json), './' is correct and avoids a second clone."""
        entry = self.manifest["plugins"][0]
        source = entry.get("source")

        if isinstance(source, str):
            # Relative-path form — must start with './' per schema.
            self.assertTrue(
                source.startswith("./"),
                f"string source must start with './' (got {source!r})",
            )
        elif isinstance(source, dict):
            kind = source.get("source")
            self.assertIn(
                kind, ("github", "url", "git-subdir", "npm"),
                f"unexpected source type: {kind!r}",
            )
            if kind == "github":
                self.assertIn("/", source.get("repo", ""), "repo should be 'owner/name'")
            elif kind == "url":
                url = source.get("url", "")
                self.assertTrue(
                    url.startswith(("https://", "git@")),
                    f"url source must start with https:// or git@ (got {url!r})",
                )
        else:
            self.fail(f"source must be a string or object; got {type(source).__name__}")

    def test_marketplace_has_top_level_description(self):
        """A top-level description helps discoverability in marketplace listings."""
        self.assertIn("description", self.manifest)
        self.assertTrue(
            len(self.manifest["description"]) > 20,
            "top-level description looks suspiciously short",
        )

    def test_marketplace_schema_reference(self):
        """$schema reference gives editor/tool validation; nice-to-have."""
        # Not strictly required, but if present it should point at the
        # Anthropic-hosted schema.
        schema = self.manifest.get("$schema")
        if schema is not None:
            self.assertIn("anthropic.com", schema)


if __name__ == "__main__":
    unittest.main()
