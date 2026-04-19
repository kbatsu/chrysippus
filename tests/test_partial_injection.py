"""Tests for the marker-injection / featured-filter / JSON field-replace
machinery added to scripts/render.py for the persona-add scaling refactor."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = ROOT / "scripts"
RULES_DIR = ROOT / "rules"

sys.path.insert(0, str(SCRIPTS_DIR))
import render  # noqa: E402


class TestMarkerIdValidation(unittest.TestCase):
    """marker_id charset is enforced consistently across render_zone /
    inject_marker / check_marker / find_markers."""

    def test_render_zone_rejects_uppercase_id(self):
        text = "<!-- chrysippus:Bad BEGIN -->\nx\n<!-- chrysippus:Bad END -->"
        with self.assertRaises(ValueError) as ctx:
            render.render_zone(text, ".md", "Bad", "y")
        self.assertIn("invalid marker id", str(ctx.exception))

    def test_render_zone_rejects_underscore_id(self):
        text = "<!-- chrysippus:my_id BEGIN -->\nx\n<!-- chrysippus:my_id END -->"
        with self.assertRaises(ValueError):
            render.render_zone(text, ".md", "my_id", "y")

    def test_check_marker_rejects_invalid_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "x.md"
            path.write_text("any")
            with self.assertRaises(ValueError):
                render.check_marker(path, "Bad", "x")

    def test_render_zone_accepts_valid_id_chars(self):
        for valid_id in ("abc", "abc-def", "x123", "a-b-c-1-2-3"):
            text = (
                f"<!-- chrysippus:{valid_id} BEGIN -->\n"
                f"x\n"
                f"<!-- chrysippus:{valid_id} END -->"
            )
            with self.subTest(id=valid_id):
                # Should not raise
                render.render_zone(text, ".md", valid_id, "y")


class TestRenderZoneRecursionGuard(unittest.TestCase):
    """Content fed into render_zone must not contain marker syntax for the
    same id — would create nested zones that confuse later renders."""

    def test_rejects_content_containing_begin_marker(self):
        text = "<!-- chrysippus:t BEGIN -->\nold\n<!-- chrysippus:t END -->"
        bad = "<!-- chrysippus:t BEGIN -->\nnested\n<!-- chrysippus:t END -->"
        with self.assertRaises(ValueError) as ctx:
            render.render_zone(text, ".md", "t", bad)
        self.assertIn("nested zones", str(ctx.exception))

    def test_allows_content_with_unrelated_marker(self):
        # Different id should not trigger the guard.
        text = "<!-- chrysippus:t BEGIN -->\nold\n<!-- chrysippus:t END -->"
        ok = (
            "<!-- chrysippus:other BEGIN -->\n"
            "different id\n"
            "<!-- chrysippus:other END -->"
        )
        out = render.render_zone(text, ".md", "t", ok)
        self.assertIn("chrysippus:other", out)


class TestRenderZone(unittest.TestCase):
    """Pure-function tests for render_zone — string in, string out."""

    def test_replaces_inner_content_md(self):
        text = (
            "before\n"
            "<!-- chrysippus:tbl BEGIN -->\n"
            "old content\n"
            "<!-- chrysippus:tbl END -->\n"
            "after\n"
        )
        out = render.render_zone(text, ".md", "tbl", "new content")
        self.assertIn("new content", out)
        self.assertNotIn("old content", out)
        self.assertIn("before\n", out)
        self.assertIn("after\n", out)

    def test_replaces_inner_content_sh(self):
        text = (
            "#!/usr/bin/env bash\n"
            "# chrysippus:allow BEGIN\n"
            "shakespeare|pirate\n"
            "# chrysippus:allow END\n"
        )
        out = render.render_zone(text, ".sh", "allow", "shakespeare|pirate|gen-alpha")
        self.assertIn("shakespeare|pirate|gen-alpha", out)
        self.assertIn("#!/usr/bin/env bash", out)

    def test_idempotent(self):
        text = (
            "<!-- chrysippus:x BEGIN -->\n"
            "content\n"
            "<!-- chrysippus:x END -->"
        )
        once = render.render_zone(text, ".md", "x", "content")
        twice = render.render_zone(once, ".md", "x", "content")
        self.assertEqual(once, twice)

    def test_missing_marker_raises(self):
        with self.assertRaises(ValueError):
            render.render_zone("plain text", ".md", "missing", "content")

    def test_duplicate_marker_raises(self):
        text = (
            "<!-- chrysippus:dup BEGIN -->\n"
            "first\n"
            "<!-- chrysippus:dup END -->\n"
            "<!-- chrysippus:dup BEGIN -->\n"
            "second\n"
            "<!-- chrysippus:dup END -->"
        )
        with self.assertRaises(ValueError) as ctx:
            render.render_zone(text, ".md", "dup", "anything")
        self.assertIn("appears 2 times", str(ctx.exception))

    def test_yaml_marker_uses_hash_comments(self):
        text = (
            "name: foo\n"
            "# chrysippus:skills BEGIN\n"
            "skills: [a, b]\n"
            "# chrysippus:skills END\n"
        )
        out = render.render_zone(text, ".yaml", "skills", "skills: [a, b, c]")
        self.assertIn("skills: [a, b, c]", out)


class TestInjectMarker(unittest.TestCase):
    """File-level tests for inject_marker — reads, writes, returns changed."""

    def test_returns_false_when_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "x.md"
            path.write_text(
                "<!-- chrysippus:t BEGIN -->\n"
                "same content\n"
                "<!-- chrysippus:t END -->\n"
            )
            changed = render.inject_marker(path, "t", "same content")
            self.assertFalse(changed)

    def test_returns_true_and_writes_when_changed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "x.md"
            path.write_text(
                "<!-- chrysippus:t BEGIN -->\n"
                "old\n"
                "<!-- chrysippus:t END -->\n"
            )
            changed = render.inject_marker(path, "t", "new")
            self.assertTrue(changed)
            self.assertIn("new", path.read_text())
            self.assertNotIn("old", path.read_text())

    def test_unsupported_suffix_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "x.json"
            path.write_text("{}")
            with self.assertRaises(ValueError) as ctx:
                render.inject_marker(path, "x", "y")
            self.assertIn("use update_json_field", str(ctx.exception))


class TestCheckMarker(unittest.TestCase):
    def test_returns_true_when_zone_matches(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "x.md"
            path.write_text(
                "<!-- chrysippus:t BEGIN -->\n"
                "expected\n"
                "<!-- chrysippus:t END -->\n"
            )
            self.assertTrue(render.check_marker(path, "t", "expected"))

    def test_returns_false_when_zone_drifts(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "x.md"
            path.write_text(
                "<!-- chrysippus:t BEGIN -->\n"
                "drifted manually\n"
                "<!-- chrysippus:t END -->\n"
            )
            self.assertFalse(render.check_marker(path, "t", "expected"))


class TestFindMarkers(unittest.TestCase):
    def test_finds_all_marker_pairs(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "x.md"
            path.write_text(
                "<!-- chrysippus:a BEGIN -->\nA\n<!-- chrysippus:a END -->\n"
                "<!-- chrysippus:b BEGIN -->\nB\n<!-- chrysippus:b END -->\n"
            )
            ids = sorted(mid for mid, _ in render.find_markers(path))
            self.assertEqual(ids, ["a", "b"])

    def test_returns_empty_for_unsupported_suffix(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "x.json"
            path.write_text("{}")
            self.assertEqual(render.find_markers(path), [])


class TestUpdateJsonField(unittest.TestCase):
    def test_mutator_changes_field(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "p.json"
            path.write_text('{\n  "version": "1.0.0",\n  "name": "foo"\n}\n')
            changed = render.update_json_field(
                path, lambda d: d.update(version="2.0.0")
            )
            self.assertTrue(changed)
            data = json.loads(path.read_text())
            self.assertEqual(data["version"], "2.0.0")
            self.assertEqual(data["name"], "foo")

    def test_no_op_mutator_returns_false(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "p.json"
            path.write_text('{\n  "name": "foo"\n}\n')
            changed = render.update_json_field(path, lambda d: None)
            self.assertFalse(changed)

    def test_preserves_trailing_newline(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "p.json"
            path.write_text('{\n  "x": 1\n}\n')
            render.update_json_field(path, lambda d: d.update(x=2))
            self.assertTrue(path.read_text().endswith("\n"))

    def test_no_op_on_4space_indented_does_not_rewrite(self):
        """Hand-edited JSON with non-canonical formatting should be left
        alone when the mutator is a no-op (semantic-equality check)."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "p.json"
            original = '{\n    "x": 1,\n    "y": 2\n}\n'  # 4-space
            path.write_text(original)
            changed = render.update_json_field(path, lambda d: None)
            self.assertFalse(changed,
                             "no-op mutator must not rewrite non-canonical JSON")
            self.assertEqual(path.read_text(), original,
                             "file must be byte-identical after no-op mutator")

    def test_accepts_return_value_style_mutator(self):
        """A mutator that returns a new dict (instead of mutating in place)
        should still take effect — silently dropping the return is a footgun."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "p.json"
            path.write_text('{"x": 1}')

            def returning_mutator(d):
                return {"x": 999}

            changed = render.update_json_field(path, returning_mutator)
            self.assertTrue(changed)
            self.assertEqual(json.loads(path.read_text())["x"], 999)

    def test_canonicalizes_when_mutator_changes_data(self):
        """When there IS a real semantic change, output is canonical 2-space."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "p.json"
            path.write_text('{\n    "x": 1\n}\n')  # 4-space input
            render.update_json_field(path, lambda d: d.update(x=2))
            text = path.read_text()
            # 2-space indent
            self.assertIn('"x": 2', text)
            self.assertIn('  "x"', text)  # 2-space, not 4
            self.assertNotIn('    "x"', text)


class TestFeaturedFilter(unittest.TestCase):
    def test_filters_by_featured_field(self):
        metas = {
            "a": {"featured": True},
            "b": {"featured": False},
            "c": {},  # missing field defaults to False
        }
        self.assertEqual(list(render.featured_personas(metas)), ["a"])
        self.assertEqual(sorted(render.catalog_personas(metas)), ["b", "c"])

    def test_preserves_insertion_order(self):
        metas = {p: {"featured": True} for p in
                 ["zzz", "aaa", "mmm", "bbb"]}
        self.assertEqual(
            list(render.featured_personas(metas)),
            ["zzz", "aaa", "mmm", "bbb"],
        )

    def test_truthy_non_bool_does_not_promote(self):
        """`featured: "false"` (string) is truthy in Python — must NOT be
        treated as featured. Strict-bool check defends against malformed
        manifests slipping past load_meta."""
        metas = {
            "a": {"featured": True},
            "b": {"featured": "false"},  # string — would be truthy
            "c": {"featured": "true"},   # string — would be truthy
            "d": {"featured": 1},        # int — truthy
            "e": {"featured": 0},        # int — falsy
        }
        # Only "a" has featured === True (strict bool identity)
        self.assertEqual(list(render.featured_personas(metas)), ["a"])
        # Everything else (including the truthy strings) goes to catalog
        self.assertEqual(sorted(render.catalog_personas(metas)),
                         ["b", "c", "d", "e"])


class TestConsumerMarkerWiring(unittest.TestCase):
    """Tests for the inject_consumer_markers / check_consumer_markers
    wiring in scripts/render.py."""

    def _setup_minimal_consumer_files(self, root):
        """Create minimal consumer files at `root` with marker pairs that
        match what's registered in CONSUMER_MARKER_INJECTIONS."""
        from collections import defaultdict
        per_file = defaultdict(set)
        for rel_path, marker_id, _ in render.CONSUMER_MARKER_INJECTIONS:
            per_file[rel_path].add(marker_id)
        for rel_path, ids in per_file.items():
            target = root / rel_path
            target.parent.mkdir(parents=True, exist_ok=True)
            suffix = Path(rel_path).suffix
            begin_tmpl, end_tmpl = render.MARKER_FORMATS[suffix]
            blocks = []
            for mid in ids:
                begin = begin_tmpl.format(id=mid)
                end = end_tmpl.format(id=mid)
                blocks.append(f"{begin}\nplaceholder\n{end}")
            target.write_text("\n\n".join(blocks) + "\n", encoding="utf-8")

    def test_subset_render_does_not_corrupt_consumer_markers(self):
        """REGRESSION (C1): scripts/render.py shakespeare must not rewrite
        consumer-file marker zones to a 1-row table claiming only
        shakespeare ships. inject_consumer_markers must always render
        with the FULL persona set, ignoring the caller's subset."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            self._setup_minimal_consumer_files(tmp_root)
            # Caller passes a 1-element subset
            one_persona = {"shakespeare": render.load_meta("shakespeare")}
            render.inject_consumer_markers(one_persona, tmp_root)
            # README's sibling-skills-table zone should contain ALL personas
            readme = (tmp_root / "README.md").read_text(encoding="utf-8")
            for persona in ("shakespeare", "pirate", "gen-alpha",
                            "toronto-mans", "ontario-bud"):
                with self.subTest(persona=persona):
                    self.assertIn(
                        persona, readme,
                        f"README zone missing {persona!r} after subset render — "
                        f"inject_consumer_markers should ignore the caller's "
                        f"subset and always render the full persona set",
                    )

    def test_check_distinguishes_missing_marker_from_drift(self):
        """REGRESSION (M2): when a marker pair is missing entirely (someone
        deleted them), the error message must say 'marker pair missing'
        not 'content drifted' — the two need different fixes."""
        # We can't easily corrupt the live repo; instead test via
        # find_markers + check_consumer_markers logic on a tmp file.
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            (tmp_root / "README.md").write_text(
                "no markers here\n", encoding="utf-8"
            )
            # Patch ROOT for the duration; check_consumer_markers reads
            # from render.ROOT directly.
            old_root = render.ROOT
            render.ROOT = tmp_root
            try:
                drifts = render.check_consumer_markers({})
            finally:
                render.ROOT = old_root
        # At least one drift entry should mention "marker pair missing"
        # for README's sibling-skills-table (no markers in our tmp file).
        missing_msgs = [d for d in drifts if "marker pair missing" in d]
        self.assertTrue(
            missing_msgs,
            f"expected at least one 'marker pair missing' entry; got: {drifts}",
        )

    def test_inject_batches_errors_across_zones(self):
        """REGRESSION (N1): an error in one zone shouldn't hide problems
        in subsequent zones. inject_consumer_markers should attempt all
        zones, accumulate errors, and raise once at the end with all
        problems listed."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            # Touch every registered file but leave them empty (no markers).
            seen_files = {rel for rel, _, _ in render.CONSUMER_MARKER_INJECTIONS}
            for rel_path in seen_files:
                target = tmp_root / rel_path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("no markers\n", encoding="utf-8")
            with self.assertRaises(ValueError) as ctx:
                render.inject_consumer_markers({}, tmp_root)
            err = str(ctx.exception)
            # All registered zones should be mentioned.
            for rel_path, marker_id, _ in render.CONSUMER_MARKER_INJECTIONS:
                with self.subTest(zone=f"{rel_path}#{marker_id}"):
                    self.assertIn(
                        f"{rel_path}#{marker_id}", err,
                        f"batched error should mention every failing zone",
                    )


class TestRegistryValidity(unittest.TestCase):
    """Every entry in CONSUMER_MARKER_INJECTIONS must be reachable: the
    file must exist in the live repo, and the marker pair must be present
    in it. Catches typo'd marker_ids and stale registry entries that
    point at deleted files."""

    def test_every_registered_file_exists(self):
        for rel_path, marker_id, _ in render.CONSUMER_MARKER_INJECTIONS:
            with self.subTest(file=rel_path):
                self.assertTrue(
                    (render.ROOT / rel_path).exists(),
                    f"CONSUMER_MARKER_INJECTIONS lists {rel_path!r} but it "
                    f"doesn't exist — fix the path or remove the entry",
                )

    def test_every_registered_marker_is_present_in_its_file(self):
        for rel_path, marker_id, _ in render.CONSUMER_MARKER_INJECTIONS:
            target = render.ROOT / rel_path
            if not target.exists():
                continue  # covered by previous test
            present = {mid for mid, _ in render.find_markers(target)}
            with self.subTest(file=rel_path, marker_id=marker_id):
                self.assertIn(
                    marker_id, present,
                    f"CONSUMER_MARKER_INJECTIONS registers marker_id "
                    f"{marker_id!r} for {rel_path}, but no such marker pair "
                    f"is present in the file. Either add the markers or "
                    f"remove the registry entry.",
                )

    def test_no_duplicate_file_marker_pairs(self):
        seen = set()
        for rel_path, marker_id, _ in render.CONSUMER_MARKER_INJECTIONS:
            key = (rel_path, marker_id)
            with self.subTest(key=key):
                self.assertNotIn(
                    key, seen,
                    f"duplicate registry entry for ({rel_path!r}, "
                    f"{marker_id!r}) — only the last one would take effect",
                )
                seen.add(key)


class TestLoadMetaValidation(unittest.TestCase):
    """load_meta() validates _meta.json schema and fails loudly on
    contributor mistakes that would otherwise silently produce broken
    output downstream."""

    def _write_meta(self, dir_, data):
        meta_path = dir_ / "_meta.json"
        meta_path.write_text(json.dumps(data), encoding="utf-8")
        (dir_ / "instructions.md").write_text("body\n", encoding="utf-8")

    def _good_meta(self, name="x"):
        return {
            "name": name,
            "version": "0.1.0",
            "description": "desc",
            "register_short": "Test register",
            "triggers": ["t"],
            "flavors": [{"name": "a", "description": "a", "default": True}],
            "preserve_defaults": {
                "commits": True, "pr_descriptions": True,
                "code_comments": True, "safety_warnings": True,
                "errors_verbatim": True,
            },
            "featured": True,
        }

    def test_accepts_valid_meta(self):
        # Smoke-test the rest of the suite's good_meta fixture.
        with tempfile.TemporaryDirectory() as tmp:
            persona_dir = Path(tmp) / "rules" / "x"
            persona_dir.mkdir(parents=True)
            self._write_meta(persona_dir, self._good_meta())
            old_root = render.RULES_DIR
            render.RULES_DIR = Path(tmp) / "rules"
            try:
                meta = render.load_meta("x")
                self.assertEqual(meta["name"], "x")
                self.assertTrue(meta["featured"])
            finally:
                render.RULES_DIR = old_root

    def _assert_load_raises(self, mutate, expected_msg_fragment):
        with tempfile.TemporaryDirectory() as tmp:
            persona_dir = Path(tmp) / "rules" / "x"
            persona_dir.mkdir(parents=True)
            data = self._good_meta()
            mutate(data)
            self._write_meta(persona_dir, data)
            old_root = render.RULES_DIR
            render.RULES_DIR = Path(tmp) / "rules"
            try:
                with self.assertRaises(ValueError) as ctx:
                    render.load_meta("x")
                self.assertIn(expected_msg_fragment, str(ctx.exception))
            finally:
                render.RULES_DIR = old_root

    def test_rejects_string_featured(self):
        self._assert_load_raises(
            lambda d: d.update(featured="false"),
            "must be true or false",
        )

    def test_rejects_int_featured(self):
        self._assert_load_raises(
            lambda d: d.update(featured=1),
            "must be true or false",
        )

    def test_rejects_missing_register_short(self):
        self._assert_load_raises(
            lambda d: d.pop("register_short"),
            "register_short",
        )

    def test_rejects_empty_register_short(self):
        self._assert_load_raises(
            lambda d: d.update(register_short="   "),
            "register_short",
        )

    def test_rejects_pipe_in_register_short(self):
        """REGRESSION (M1): `|` would break markdown table column boundaries."""
        self._assert_load_raises(
            lambda d: d.update(register_short="bash | zsh | fish"),
            "table-breaking",
        )

    def test_rejects_newline_in_register_short(self):
        self._assert_load_raises(
            lambda d: d.update(register_short="multi\nline"),
            "table-breaking",
        )

    def test_rejects_backtick_in_register_short(self):
        self._assert_load_raises(
            lambda d: d.update(register_short="uses `code spans`"),
            "table-breaking",
        )

    def test_rejects_no_default_flavor(self):
        self._assert_load_raises(
            lambda d: d.update(flavors=[{"name": "a", "description": "a"}]),
            "exactly one flavor",
        )

    def test_rejects_two_default_flavors(self):
        self._assert_load_raises(
            lambda d: d.update(flavors=[
                {"name": "a", "default": True},
                {"name": "b", "default": True},
            ]),
            "exactly one flavor",
        )

    def test_rejects_empty_triggers(self):
        self._assert_load_raises(
            lambda d: d.update(triggers=[]),
            "triggers",
        )

    def test_rejects_missing_required_field(self):
        self._assert_load_raises(
            lambda d: d.pop("description"),
            "description",
        )


class TestGeneratorEmptyInputGuards(unittest.TestCase):
    """Empty input previously produced bash-syntax-error allow lists and
    rowless markdown tables. Generators now raise loudly."""

    def test_persona_table_rejects_empty(self):
        with self.assertRaises(ValueError):
            render.gen_persona_table({})

    def test_personas_command_table_rejects_empty(self):
        with self.assertRaises(ValueError):
            render.gen_personas_command_table({})

    def test_slash_commands_table_rejects_empty(self):
        with self.assertRaises(ValueError):
            render.gen_slash_commands_table({})

    def test_subagents_table_rejects_empty(self):
        with self.assertRaises(ValueError):
            render.gen_subagents_table({})

    def test_trigger_phrases_rejects_empty(self):
        with self.assertRaises(ValueError):
            render.gen_trigger_phrases_list({})

    def test_cp_skills_block_rejects_empty(self):
        with self.assertRaises(ValueError):
            render.gen_cp_skills_block({}, ".claude/skills/")

    def test_hooks_allow_list_rejects_empty(self):
        with self.assertRaises(ValueError):
            render.gen_hooks_allow_list({})

    def test_dramaturg_skills_rejects_empty(self):
        with self.assertRaises(ValueError):
            render.gen_dramaturg_skills({})


class TestTriggerMarkdownEscape(unittest.TestCase):
    """Triggers containing markdown special characters must not break
    rendered output. Italic-quoted (non-slash) triggers are escaped;
    backtick-wrapped slash triggers are literal."""

    def test_asterisk_in_trigger_is_escaped(self):
        metas = {"x": {"triggers": ["*hot tip*"]}}
        out = render.gen_trigger_phrases_list(metas)
        # Asterisks must be backslash-escaped so they don't render as bold
        self.assertIn(r"\*hot tip\*", out)

    def test_brackets_in_trigger_are_escaped(self):
        metas = {"x": {"triggers": ["see [docs](url)"]}}
        out = render.gen_trigger_phrases_list(metas)
        self.assertIn(r"\[docs\]", out)

    def test_backtick_in_trigger_is_escaped(self):
        metas = {"x": {"triggers": ["use `foo`"]}}
        out = render.gen_trigger_phrases_list(metas)
        self.assertIn(r"\`foo\`", out)

    def test_slash_trigger_not_escaped_inside_backticks(self):
        # Slash triggers go inside `...` code spans; markdown is literal there.
        metas = {"x": {"triggers": ["/foo*bar"]}}
        out = render.gen_trigger_phrases_list(metas)
        self.assertIn("`/foo*bar`", out)

    def test_plain_trigger_unaffected(self):
        metas = {"x": {"triggers": ["talk like wayne"]}}
        out = render.gen_trigger_phrases_list(metas)
        self.assertIn('*"talk like wayne"*', out)


class TestPersonaDefaultFlavorErrorMessage(unittest.TestCase):
    """When a synthetic meta has no default flavor (load_meta would have
    caught it, but a test/caller may construct one), error must be a
    clear ValueError with the persona name — not StopIteration."""

    def test_raises_value_error_with_persona_name(self):
        meta = {"name": "synthetic", "flavors": [{"name": "a"}]}
        with self.assertRaises(ValueError) as ctx:
            render._persona_default_flavor(meta)
        self.assertIn("synthetic", str(ctx.exception))
        self.assertIn("default", str(ctx.exception))


class TestPartialGeneratorsByteIdentical(unittest.TestCase):
    """Generators produce stable output across calls. (Backwards-compat
    against the live repo is asserted by test_render.py's --check oracle.)"""

    def setUp(self):
        self.metas = {
            p: render.load_meta(p)
            for p in sorted(d.name for d in RULES_DIR.iterdir() if d.is_dir())
        }

    def test_persona_table_includes_register_short(self):
        out = render.gen_persona_table(self.metas)
        for persona, meta in self.metas.items():
            with self.subTest(persona=persona):
                self.assertIn(meta["register_short"], out)

    def test_slash_commands_table_lists_every_persona(self):
        out = render.gen_slash_commands_table(self.metas)
        for persona in self.metas:
            with self.subTest(persona=persona):
                self.assertIn(f"`/chrysippus:{persona}`", out)
        self.assertIn("`/chrysippus:personas`", out)

    def test_subagents_table_lists_every_reviewer_plus_dramaturg(self):
        out = render.gen_subagents_table(self.metas)
        for persona in self.metas:
            with self.subTest(persona=persona):
                self.assertIn(f"`{persona}-reviewer`", out)
        self.assertIn("`dramaturg`", out)

    def test_trigger_phrases_list_uses_triggers(self):
        out = render.gen_trigger_phrases_list(self.metas)
        for persona, meta in self.metas.items():
            for trig in meta["triggers"]:
                with self.subTest(persona=persona, trigger=trig):
                    if trig.startswith("/"):
                        self.assertIn(f"`{trig}`", out)
                    else:
                        self.assertIn(trig, out)

    def test_hooks_allow_list_pipe_separated(self):
        out = render.gen_hooks_allow_list(self.metas)
        # No trailing/leading pipes; one pipe between each pair
        names = list(self.metas.keys())
        self.assertEqual(out, "|".join(names))

    def test_dramaturg_skills_yaml_inline_list(self):
        out = render.gen_dramaturg_skills(self.metas)
        names = list(self.metas.keys())
        self.assertEqual(out, "[" + ", ".join(names) + "]")

    def test_cp_skills_block_one_line_per_persona(self):
        out = render.gen_cp_skills_block(self.metas, ".claude/skills/")
        lines = [l for l in out.splitlines() if l.strip()]
        self.assertEqual(len(lines), len(self.metas))


class TestPersonasCommandMd(unittest.TestCase):
    def test_includes_all_personas_in_table(self):
        metas = {p: render.load_meta(p) for p in
                 sorted(d.name for d in RULES_DIR.iterdir() if d.is_dir())}
        out = render.render_personas_command_md(metas)
        for persona in metas:
            with self.subTest(persona=persona):
                self.assertIn(f"`{persona}`", out)


class TestDramaturgMd(unittest.TestCase):
    def test_skills_frontmatter_lists_all_personas(self):
        metas = {p: render.load_meta(p) for p in
                 sorted(d.name for d in RULES_DIR.iterdir() if d.is_dir())}
        out = render.render_dramaturg_md(metas)
        # First few lines should contain frontmatter with skills: [...]
        head = "\n".join(out.splitlines()[:10])
        for persona in metas:
            with self.subTest(persona=persona):
                self.assertIn(persona, head)


class TestCatalogIndexBody(unittest.TestCase):
    def test_no_catalog_section_when_all_featured(self):
        metas = {
            "a": {"featured": True, "name": "a", "flavors": [{"name": "x", "default": True}], "register_short": "R"},
            "b": {"featured": True, "name": "b", "flavors": [{"name": "y", "default": True}], "register_short": "R"},
        }
        out = render.gen_personas_catalog_index_body(metas)
        self.assertNotIn("Catalog", out)

    def test_catalog_section_appears_when_any_non_featured(self):
        metas = {
            "feat":   {"featured": True,  "name": "feat",   "flavors": [{"name": "x", "default": True}], "register_short": "R"},
            "extra":  {"featured": False, "name": "extra",  "flavors": [{"name": "y", "default": True}], "register_short": "R"},
        }
        out = render.gen_personas_catalog_index_body(metas)
        self.assertIn("Catalog", out)
        self.assertIn("`feat`", out)
        self.assertIn("`extra`", out)
