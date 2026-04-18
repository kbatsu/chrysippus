"""Tests for persona lexicons and stereotype-drift guardrails."""

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RULES_DIR = ROOT / "rules"


class TestLexiconPresence(unittest.TestCase):
    """Every persona that should have a lexicon.md has one."""

    PERSONAS_WITH_LEXICON = ("gen-alpha", "toronto-mans")

    def test_lexicons_exist(self):
        for persona in self.PERSONAS_WITH_LEXICON:
            with self.subTest(persona=persona):
                lex = RULES_DIR / persona / "lexicon.md"
                self.assertTrue(lex.exists(), f"missing {lex}")
                self.assertGreater(
                    len(lex.read_text()), 500,
                    f"{lex} looks suspiciously short",
                )


class TestTorontoMansGuardrails(unittest.TestCase):
    """Verify the toronto-mans hard exclusions are present in the lexicon."""

    EXCLUDED_FORBIDDEN_PRESENCE = [
        "bumbaclot",
        "bloodclaat",
        "raasclaat",
        "pussyclaat",
    ]

    EXPECTED_EXCLUSION_LABELS = [
        "Patois expletives",
        "fake-accent respellings",
        "Real-person",
        "brand",
        "gang",
    ]

    def setUp(self):
        self.lexicon = (RULES_DIR / "toronto-mans" / "lexicon.md").read_text()
        self.instructions = (RULES_DIR / "toronto-mans" / "instructions.md").read_text()

    def test_excluded_patois_expletives_mentioned_only_in_excluded_section(self):
        # Each forbidden word must appear in the lexicon (it's documented as
        # excluded), but the file must clearly label it as forbidden.
        for word in self.EXCLUDED_FORBIDDEN_PRESENCE:
            with self.subTest(word=word):
                self.assertIn(word, self.lexicon)
                # Sanity: the word should appear in the "Excluded" half of the file
                excluded_section_start = self.lexicon.find("## Excluded")
                self.assertGreater(excluded_section_start, 0, "no Excluded section in lexicon")
                first_occurrence = self.lexicon.find(word)
                self.assertGreaterEqual(
                    first_occurrence, excluded_section_start,
                    f"'{word}' appears in the lexicon BEFORE the Excluded section — guardrail leak?",
                )

    def test_exclusion_categories_labeled(self):
        combined = (self.lexicon + self.instructions).lower()
        for label in self.EXPECTED_EXCLUSION_LABELS:
            with self.subTest(label=label):
                self.assertIn(
                    label.lower(), combined,
                    f"toronto-mans lexicon/instructions missing exclusion category: '{label}'",
                )

    def test_safety_warnings_hard_locked(self):
        meta = json.loads((RULES_DIR / "toronto-mans" / "_meta.json").read_text())
        self.assertIn(
            "safety_warnings", meta.get("preserve_locked", []),
            "toronto-mans: safety_warnings must be in preserve_locked",
        )

    def test_attribution_paragraph_present(self):
        self.assertIn("Multicultural Toronto English", self.instructions)
        self.assertIn("Jamaican Patois", self.instructions)
        self.assertIn("AAVE", self.instructions)


class TestGenAlphaDisclaimer(unittest.TestCase):
    """Verify the gen-alpha self-aware disclaimer is present."""

    def test_disclaimer_in_instructions(self):
        content = (RULES_DIR / "gen-alpha" / "instructions.md").read_text()
        # Collapse whitespace so line-wraps don't break exact-string matches.
        collapsed = " ".join(content.split())
        self.assertIn(
            "Gen-Zs and millennials", collapsed,
            "gen-alpha disclaimer missing ('Made by Gen-Zs and millennials...')",
        )
        self.assertIn("not endorsed by or representative", collapsed)


class TestPirateGuardrails(unittest.TestCase):
    """Verify the pirate stereotype-drift guardrails are still in place."""

    EXPECTED_EXCLUSIONS = [
        "Caribbean",
        "slavery",
        "savage",
    ]

    def test_guardrail_keywords_present(self):
        content = (RULES_DIR / "pirate" / "instructions.md").read_text()
        for kw in self.EXPECTED_EXCLUSIONS:
            with self.subTest(keyword=kw):
                self.assertIn(
                    kw, content,
                    f"pirate guardrail missing discussion of '{kw}'",
                )


class TestMetaSchema(unittest.TestCase):
    """Basic structural validation of rules/<persona>/_meta.json files."""

    REQUIRED_FIELDS = ["name", "version", "description", "triggers", "flavors", "preserve_defaults"]

    def test_all_meta_files_have_required_fields(self):
        for persona_dir in RULES_DIR.iterdir():
            if not persona_dir.is_dir():
                continue
            meta = json.loads((persona_dir / "_meta.json").read_text())
            for field in self.REQUIRED_FIELDS:
                with self.subTest(persona=persona_dir.name, field=field):
                    self.assertIn(field, meta, f"{persona_dir.name}: missing required field '{field}'")

    def test_every_persona_has_exactly_one_default_flavor(self):
        for persona_dir in RULES_DIR.iterdir():
            if not persona_dir.is_dir():
                continue
            meta = json.loads((persona_dir / "_meta.json").read_text())
            defaults = [f for f in meta["flavors"] if f.get("default")]
            with self.subTest(persona=persona_dir.name):
                self.assertEqual(
                    len(defaults), 1,
                    f"{persona_dir.name}: expected exactly 1 default flavor, got {len(defaults)}",
                )


if __name__ == "__main__":
    unittest.main()
