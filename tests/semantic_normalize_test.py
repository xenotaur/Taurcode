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
                ("prompts[:old]", "Expected prompt is missing"),
                ("prompts[:new]", "Unexpected extra prompt"),
            },
        )

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
