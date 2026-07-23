import tempfile
import unittest
from pathlib import Path

from taurcode import semantic_normalize


class TestSemanticNormalize(unittest.TestCase):
    def test_yaml_formatting_normalizes_away(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            first = base / "first"
            second = base / "second"
            first.mkdir()
            second.mkdir()
            (first / "package.yml").write_text(
                """matches:
  - trigger: ":hello"
    replace: |
      Hello
""",
                encoding="utf-8",
            )
            (second / "package.yml").write_text(
                'matches:\n  - replace: "Hello\\n"\n    trigger: ":hello"\n',
                encoding="utf-8",
            )
            (first / "_manifest.yml").write_text(
                """name: sample
title: Sample
tags:
  - ai
  - prompts
""",
                encoding="utf-8",
            )
            (second / "_manifest.yml").write_text(
                """tags: [ai, prompts]
title: Sample
name: sample
""",
                encoding="utf-8",
            )

            first_package = semantic_normalize.normalize_espanso_package(first)
            second_package = semantic_normalize.normalize_espanso_package(second)

            self.assertEqual(
                semantic_normalize.compare_packages(first_package, second_package), []
            )

    def test_prompt_ordering_normalizes_away(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            first = base / "first"
            second = base / "second"
            first.mkdir()
            second.mkdir()
            (first / "package.yml").write_text(
                """matches:
  - trigger: ":one"
    replace: One
  - trigger: ":two"
    replace: Two
""",
                encoding="utf-8",
            )
            (second / "package.yml").write_text(
                """matches:
  - trigger: ":two"
    replace: Two
  - trigger: ":one"
    replace: One
""",
                encoding="utf-8",
            )

            first_package = semantic_normalize.normalize_espanso_package(first)
            second_package = semantic_normalize.normalize_espanso_package(second)

            self.assertEqual(
                semantic_normalize.compare_packages(first_package, second_package), []
            )

    def test_body_changes_are_detected(self) -> None:
        first_package = semantic_normalize.NormalizedPackage(
            prompts=(
                semantic_normalize.NormalizedPrompt(
                    key=":hello", trigger=":hello", body="Hello\n"
                ),
            )
        )
        second_package = semantic_normalize.NormalizedPackage(
            prompts=(
                semantic_normalize.NormalizedPrompt(
                    key=":hello", trigger=":hello", body="Goodbye\n"
                ),
            )
        )

        differences = semantic_normalize.compare_packages(first_package, second_package)

        self.assertEqual(len(differences), 1)
        self.assertEqual(differences[0].path, "prompts[:hello].body")
        self.assertIn("body", differences[0].message)

    def test_trigger_changes_are_detected_as_missing_and_added_prompts(self) -> None:
        expected = semantic_normalize.NormalizedPackage(
            prompts=(
                semantic_normalize.NormalizedPrompt(
                    key=":old", trigger=":old", body="Body\n"
                ),
            )
        )
        actual = semantic_normalize.NormalizedPackage(
            prompts=(
                semantic_normalize.NormalizedPrompt(
                    key=":new", trigger=":new", body="Body\n"
                ),
            )
        )

        differences = semantic_normalize.compare_packages(expected, actual)

        self.assertEqual(
            {(difference.path, difference.message) for difference in differences},
            {
                ("prompts[:old]", "Expected 1 prompt(s) missing"),
                ("prompts[:new]", "Unexpected 1 extra prompt(s)"),
            },
        )

    def test_duplicate_triggers_are_not_collapsed(self) -> None:
        expected = semantic_normalize.NormalizedPackage(
            prompts=(
                semantic_normalize.NormalizedPrompt(
                    key=":dupe", trigger=":dupe", body="First\n"
                ),
                semantic_normalize.NormalizedPrompt(
                    key=":dupe", trigger=":dupe", body="Second\n"
                ),
            )
        )
        actual = semantic_normalize.NormalizedPackage(
            prompts=(
                semantic_normalize.NormalizedPrompt(
                    key=":dupe", trigger=":dupe", body="Second\n"
                ),
            )
        )

        differences = semantic_normalize.compare_packages(expected, actual)

        self.assertEqual(len(differences), 1)
        self.assertEqual(differences[0].path, "prompts[:dupe]")
        self.assertIn("missing", differences[0].message)
        self.assertIn("First", differences[0].message)

    def test_duplicate_prompt_ordering_normalizes_away(self) -> None:
        expected = semantic_normalize.NormalizedPackage(
            prompts=(
                semantic_normalize.NormalizedPrompt(
                    key=":dupe", trigger=":dupe", body="First\n"
                ),
                semantic_normalize.NormalizedPrompt(
                    key=":dupe", trigger=":dupe", body="Second\n"
                ),
            )
        )
        actual = semantic_normalize.NormalizedPackage(
            prompts=(
                semantic_normalize.NormalizedPrompt(
                    key=":dupe", trigger=":dupe", body="Second\n"
                ),
                semantic_normalize.NormalizedPrompt(
                    key=":dupe", trigger=":dupe", body="First\n"
                ),
            )
        )

        self.assertEqual(semantic_normalize.compare_packages(expected, actual), [])

    def test_espanso_mode_ignores_actual_only_unsupported_fields(self) -> None:
        expected = semantic_normalize.NormalizedPackage(
            prompts=(
                semantic_normalize.NormalizedPrompt(
                    key=":word", trigger=":word", body="Word\n"
                ),
            )
        )
        actual = semantic_normalize.NormalizedPackage(
            prompts=(
                semantic_normalize.NormalizedPrompt(
                    key=":word",
                    trigger=":word",
                    body="Word\n",
                    unsupported_fields=(("word", True),),
                ),
            )
        )

        self.assertEqual(semantic_normalize.compare_packages(expected, actual), [])

    def test_espanso_mode_detects_dropped_expected_unsupported_fields(self) -> None:
        expected = semantic_normalize.NormalizedPackage(
            prompts=(
                semantic_normalize.NormalizedPrompt(
                    key=":word",
                    trigger=":word",
                    body="Word\n",
                    unsupported_fields=(("word", True),),
                ),
            )
        )
        actual = semantic_normalize.NormalizedPackage(
            prompts=(
                semantic_normalize.NormalizedPrompt(
                    key=":word", trigger=":word", body="Word\n"
                ),
            )
        )

        differences = semantic_normalize.compare_packages(expected, actual)

        self.assertEqual(len(differences), 1)
        self.assertEqual(differences[0].path, "prompts[:word].unsupported_fields")
        self.assertIn("expected", differences[0].message)

    def test_espanso_mode_allows_actual_only_metadata_assets(self) -> None:
        expected = semantic_normalize.NormalizedPackage(prompts=())
        actual = semantic_normalize.NormalizedPackage(
            prompts=(),
            manifest=(("name", "sample"),),
            readme="# Sample\n",
            license_text="License\n",
        )

        self.assertEqual(semantic_normalize.compare_packages(expected, actual), [])

    def test_canonical_mode_reports_actual_only_metadata_assets(self) -> None:
        expected = semantic_normalize.NormalizedPackage(prompts=())
        actual = semantic_normalize.NormalizedPackage(
            prompts=(),
            manifest=(("name", "sample"),),
        )

        differences = semantic_normalize.compare_packages(
            expected, actual, mode=semantic_normalize.CANONICAL_SEMANTIC_MODE
        )

        self.assertEqual(len(differences), 1)
        self.assertEqual(differences[0].path, "_manifest.yml")
        self.assertIn("Unexpected extra metadata asset", differences[0].message)

    def test_metadata_difference_messages_include_expected_and_actual_values(
        self,
    ) -> None:
        expected = semantic_normalize.NormalizedPackage(
            prompts=(), manifest=(("version", "1.0.0"),)
        )
        actual = semantic_normalize.NormalizedPackage(
            prompts=(), manifest=(("version", "2.0.0"),)
        )

        differences = semantic_normalize.compare_packages(expected, actual)

        self.assertEqual(len(differences), 1)
        self.assertIn("1.0.0", differences[0].message)
        self.assertIn("2.0.0", differences[0].message)

    def test_metadata_assets_are_compared(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            first = base / "first"
            second = base / "second"
            changed = base / "changed"
            for package_dir in (first, second, changed):
                package_dir.mkdir()
                (package_dir / "package.yml").write_text(
                    'matches:\n  - trigger: ":hello"\n    replace: "Hello\\n"\n',
                    encoding="utf-8",
                )
            for package_dir in (first, second):
                (package_dir / "_manifest.yml").write_text(
                    "name: sample\ntags: [ai, prompts]\n",
                    encoding="utf-8",
                )
                (package_dir / "README.md").write_text(
                    "# Sample\n\nREADME text.\n",
                    encoding="utf-8",
                )
                (package_dir / "LICENSE").write_text(
                    "License text.\n",
                    encoding="utf-8",
                )
            (changed / "_manifest.yml").write_text(
                "name: sample\ntags: [changed]\n",
                encoding="utf-8",
            )
            (changed / "README.md").write_text(
                "# Sample\n\nChanged README.\n",
                encoding="utf-8",
            )
            (changed / "LICENSE").write_text(
                "Changed license.\n",
                encoding="utf-8",
            )

            first_package = semantic_normalize.normalize_espanso_package(first)
            second_package = semantic_normalize.normalize_espanso_package(second)
            changed_package = semantic_normalize.normalize_espanso_package(changed)

            self.assertEqual(
                semantic_normalize.compare_packages(first_package, second_package), []
            )
            differences = semantic_normalize.compare_packages(
                first_package, changed_package
            )
            self.assertEqual(
                {difference.path for difference in differences},
                {"_manifest.yml", "README.md", "LICENSE"},
            )

    def test_canonical_vs_exported_espanso_mode_ignores_curated_frontmatter(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            prompts_dir = base / "prompts"
            package_dir = base / "espanso"
            prompts_dir.mkdir()
            package_dir.mkdir()
            (prompts_dir / "prompt.md").write_text(
                """---
id: curated-prompt
name: Curated Prompt Name
description: Human-authored description that Espanso cannot represent.
keyword: ":curated"
tags:
  - useful
---

Shared body.
""",
                encoding="utf-8",
            )
            (package_dir / "package.yml").write_text(
                'matches:\n  - trigger: ":curated"\n    replace: "Shared body.\\n"\n',
                encoding="utf-8",
            )

            canonical = semantic_normalize.normalize_canonical_prompts(prompts_dir)
            espanso = semantic_normalize.normalize_espanso_package(package_dir)

            self.assertEqual(
                semantic_normalize.compare_packages(
                    canonical,
                    espanso,
                    mode=semantic_normalize.ESPANSO_SEMANTIC_MODE,
                ),
                [],
            )
            canonical_differences = semantic_normalize.compare_packages(
                canonical,
                espanso,
                mode=semantic_normalize.CANONICAL_SEMANTIC_MODE,
            )
            self.assertTrue(
                any(
                    difference.path == "prompts[:curated].name"
                    for difference in canonical_differences
                )
            )

    def test_force_clipboard_difference_is_detected_in_espanso_mode(self) -> None:
        expected = semantic_normalize.NormalizedPackage(
            prompts=(
                semantic_normalize.NormalizedPrompt(
                    key=":short",
                    trigger=":short",
                    body="Short\n",
                    force_clipboard=True,
                ),
            )
        )
        actual = semantic_normalize.NormalizedPackage(
            prompts=(
                semantic_normalize.NormalizedPrompt(
                    key=":short", trigger=":short", body="Short\n"
                ),
            )
        )

        differences = semantic_normalize.compare_packages(
            expected, actual, mode=semantic_normalize.ESPANSO_SEMANTIC_MODE
        )

        self.assertEqual(len(differences), 1)
        self.assertEqual(differences[0].path, "prompts[:short].force_clipboard")
        self.assertIn("True", differences[0].message)
        self.assertIn("False", differences[0].message)

    def test_force_clipboard_difference_is_detected_in_canonical_mode(self) -> None:
        expected = semantic_normalize.NormalizedPackage(
            prompts=(
                semantic_normalize.NormalizedPrompt(
                    key=":short",
                    trigger=":short",
                    body="Short\n",
                    force_clipboard=True,
                ),
            )
        )
        actual = semantic_normalize.NormalizedPackage(
            prompts=(
                semantic_normalize.NormalizedPrompt(
                    key=":short", trigger=":short", body="Short\n"
                ),
            )
        )

        differences = semantic_normalize.compare_packages(
            expected, actual, mode=semantic_normalize.CANONICAL_SEMANTIC_MODE
        )

        self.assertTrue(
            any(
                difference.path == "prompts[:short].force_clipboard"
                for difference in differences
            )
        )

    def test_force_clipboard_is_part_of_duplicate_prompt_signature(self) -> None:
        expected = semantic_normalize.NormalizedPackage(
            prompts=(
                semantic_normalize.NormalizedPrompt(
                    key=":dupe",
                    trigger=":dupe",
                    body="Same\n",
                    force_clipboard=True,
                ),
                semantic_normalize.NormalizedPrompt(
                    key=":dupe", trigger=":dupe", body="Same\n", force_clipboard=False
                ),
            )
        )
        actual = semantic_normalize.NormalizedPackage(
            prompts=(
                semantic_normalize.NormalizedPrompt(
                    key=":dupe", trigger=":dupe", body="Same\n", force_clipboard=False
                ),
                semantic_normalize.NormalizedPrompt(
                    key=":dupe", trigger=":dupe", body="Same\n", force_clipboard=False
                ),
            )
        )

        differences = semantic_normalize.compare_packages(expected, actual)

        # Two prompts share trigger+body, differing only in force_clipboard.
        # If force_clipboard were excluded from the duplicate signature, both
        # would collapse into one occurrence count and this drop would be
        # silently masked.
        self.assertEqual(len(differences), 2)
        messages = {difference.message for difference in differences}
        self.assertTrue(any("missing" in message for message in messages))
        self.assertTrue(any("extra" in message for message in messages))

    def test_canonical_normalization_captures_force_clipboard(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prompts_dir = Path(tmpdir)
            (prompts_dir / "short.md").write_text(
                """---
id: short
name: Short
description: A short prompt
keyword: ":tc-short"
targets:
  espanso:
    force_clipboard: true
---

Short body.
""",
                encoding="utf-8",
            )

            package = semantic_normalize.normalize_canonical_prompts(prompts_dir)

            self.assertEqual(len(package.prompts), 1)
            self.assertTrue(package.prompts[0].force_clipboard)

    def test_espanso_normalization_captures_force_clipboard(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            package_dir = Path(tmpdir)
            (package_dir / "package.yml").write_text(
                """matches:
  - trigger: ":tc-short"
    replace: |
      Short body.
    force_clipboard: true
""",
                encoding="utf-8",
            )

            package = semantic_normalize.normalize_espanso_package(package_dir)

            self.assertEqual(len(package.prompts), 1)
            self.assertTrue(package.prompts[0].force_clipboard)
            self.assertEqual(package.prompts[0].unsupported_fields, ())

    def test_real_corpus_canonical_normalization_smoke(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        prompts_dir = repo_root / "prompts" / "taurcode"

        package = semantic_normalize.normalize_canonical_prompts(prompts_dir)

        self.assertGreater(len(package.prompts), 0)
        self.assertEqual(
            package.prompts,
            tuple(sorted(package.prompts, key=lambda prompt: prompt.key)),
        )


if __name__ == "__main__":
    unittest.main()
