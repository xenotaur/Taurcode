import tempfile
import unittest
from pathlib import Path

from taurcode.cli import main


class TestEspansoImport(unittest.TestCase):
    def test_import_supported_match_to_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source = base / "package.yml"
            output = base / "prompts"
            source.write_text(
                """matches:\n  - trigger: \":tc-example\"\n    replace: |\n      Hello world\n""",
                encoding="utf-8",
            )

            rc = main(
                ["import", "espanso", "--input", str(source), "--output", str(output)]
            )
            self.assertEqual(rc, 0)

            imported = output / "tc-example.md"
            self.assertTrue(imported.exists())
            self.assertEqual(
                imported.read_text(encoding="utf-8"),
                """---\nid: tc-example\nname: Tc Example\ndescription: Imported from Espanso\nkeyword: \":tc-example\"\n---\n\nHello world\n""",
            )

    def test_import_unsupported_match_to_raw_yaml(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source = base / "package.yml"
            output = base / "prompts"
            source.write_text(
                """matches:\n  - trigger: \":tc-form\"\n    replace: \"Hi {{name}}\"\n    vars:\n      - name: name\n""",
                encoding="utf-8",
            )

            rc = main(
                ["import", "espanso", "--input", str(source), "--output", str(output)]
            )
            self.assertEqual(rc, 0)

            raw_file = output / "imported_raw" / "match-1.yml"
            self.assertTrue(raw_file.exists())
            self.assertEqual(
                raw_file.read_text(encoding="utf-8"),
                """  - trigger: \":tc-form\"
    replace: \"Hi {{name}}\"
    vars:
      - name: name
""",
            )

    def test_import_mixed_and_duplicate_trigger(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source = base / "package.yml"
            output = base / "prompts"
            source.write_text(
                """matches:\n  - trigger: \":tc-dupe\"\n    replace: first\n  - trigger: \":tc-dupe\"\n    replace: \"\"\n  - trigger: \":tc-complex\"\n    replace: thing\n    shell: echo hi\n""",
                encoding="utf-8",
            )

            rc = main(
                ["import", "espanso", "--input", str(source), "--output", str(output)]
            )
            self.assertEqual(rc, 0)

            self.assertTrue((output / "tc-dupe.md").exists())
            self.assertTrue((output / "tc-dupe-2.md").exists())
            self.assertEqual(
                (output / "tc-dupe-2.md").read_text(encoding="utf-8").split("\n")[-1],
                "",
            )
            self.assertTrue((output / "imported_raw" / "match-1.yml").exists())

    def test_import_preserves_supported_metadata_assets(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source_dir = base / "espanso-package"
            source_dir.mkdir()
            output = base / "prompts"
            manifest = b'name: sample\n# keep comment\ntitle: "Sample Package"\n'
            readme = b"# Sample Package\n\nKeep this README exactly.\n"
            license_text = b"Sample license text.\n\nAll rights reserved.\n"
            (source_dir / "package.yml").write_text(
                """matches:
  - trigger: ":tc-meta"
    replace: |
      Metadata body
""",
                encoding="utf-8",
            )
            (source_dir / "_manifest.yml").write_bytes(manifest)
            (source_dir / "README.md").write_bytes(readme)
            (source_dir / "LICENSE").write_bytes(license_text)

            rc = main(
                [
                    "import",
                    "espanso",
                    "--input",
                    str(source_dir),
                    "--output",
                    str(output),
                ]
            )
            self.assertEqual(rc, 0)

            self.assertTrue((output / "tc-meta.md").exists())
            metadata_dir = output / "espanso"
            self.assertEqual((metadata_dir / "_manifest.yml").read_bytes(), manifest)
            self.assertEqual((metadata_dir / "README.md").read_bytes(), readme)
            self.assertEqual((metadata_dir / "LICENSE").read_bytes(), license_text)

    def test_import_does_not_create_metadata_dir_without_supported_assets(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source_dir = base / "espanso-package"
            source_dir.mkdir()
            output = base / "prompts"
            (source_dir / "package.yml").write_text(
                """matches:
  - trigger: ":tc-plain"
    replace: plain
""",
                encoding="utf-8",
            )

            rc = main(
                [
                    "import",
                    "espanso",
                    "--input",
                    str(source_dir),
                    "--output",
                    str(output),
                ]
            )
            self.assertEqual(rc, 0)
            self.assertFalse((output / "espanso").exists())

    def test_import_invalid_yaml_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source = base / "package.yml"
            source.write_text("matches:\n  - invalid", encoding="utf-8")

            rc = main(
                [
                    "import",
                    "espanso",
                    "--input",
                    str(source),
                    "--output",
                    str(base / "prompts"),
                ]
            )
            self.assertEqual(rc, 1)

    def test_import_folded_block_scalar(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source = base / "package.yml"
            output = base / "prompts"
            source.write_text(
                """matches:
  - trigger: ":folded"
    replace: >
      This is folded
      onto one paragraph.

      This is a second paragraph.
""",
                encoding="utf-8",
            )

            rc = main(
                ["import", "espanso", "--input", str(source), "--output", str(output)]
            )
            self.assertEqual(rc, 0)
            imported = (output / "folded.md").read_text(encoding="utf-8")
            self.assertTrue(
                imported.endswith(
                    "This is folded onto one paragraph.\nThis is a second paragraph.\n"
                )
            )

    def test_import_literal_block_scalar_with_blank_lines(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source = base / "package.yml"
            output = base / "prompts"
            source.write_text(
                """matches:
  - trigger: ":address"
    replace: |
      Addressing Code Review Feedback
      I got some comments on the associated PR. For each comment, ask:

      - Does this comment refer to issues which are still present?
      - Does this comment raise valid issues?

      PR:
      ----Comments Follow—————————————————————
""",
                encoding="utf-8",
            )
            rc = main(
                ["import", "espanso", "--input", str(source), "--output", str(output)]
            )
            self.assertEqual(rc, 0)
            imported = (output / "address.md").read_text(encoding="utf-8")
            self.assertIn(
                "Addressing Code Review Feedback\n"
                "I got some comments on the associated PR. For each comment, ask:\n\n"
                "- Does this comment refer to issues which are still present?\n"
                "- Does this comment raise valid issues?\n\n"
                "PR:\n"
                "----Comments Follow—————————————————————\n",
                imported,
            )

    def test_import_unsupported_block_scalar_preserves_full_raw_yaml(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source = base / "package.yml"
            output = base / "prompts"
            source.write_text(
                """matches:
  - trigger: ":complex"
    replace: |
      paragraph one

      paragraph two
    vars:
      - name: name
""",
                encoding="utf-8",
            )
            rc = main(
                ["import", "espanso", "--input", str(source), "--output", str(output)]
            )
            self.assertEqual(rc, 0)
            self.assertFalse((output / "complex.md").exists())
            raw_file = output / "imported_raw" / "match-1.yml"
            self.assertTrue(raw_file.exists())
            self.assertIn(
                "    replace: |\n      paragraph one\n\n      paragraph two\n",
                raw_file.read_text(encoding="utf-8"),
            )

    def test_import_raw_fallback_with_matches_header_comment(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source = base / "package.yml"
            output = base / "prompts"
            source.write_text(
                """matches:  # inline comment
  - trigger: ":complex"
    replace: |
      keep me

      too
    vars:
      - name: name
""",
                encoding="utf-8",
            )
            rc = main(
                ["import", "espanso", "--input", str(source), "--output", str(output)]
            )
            self.assertEqual(rc, 0)
            raw_file = output / "imported_raw" / "match-1.yml"
            self.assertTrue(raw_file.exists())
            self.assertIn("      keep me\n\n      too\n", raw_file.read_text("utf-8"))

    def test_import_raw_fallback_ignores_top_level_comments_between_matches(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source = base / "package.yml"
            output = base / "prompts"
            source.write_text(
                """matches:
  - trigger: ":one"
    replace: ok
# top-level comment between matches and global vars
  - trigger: ":complex"
    replace: |
      first

      second
    vars:
      - name: name
""",
                encoding="utf-8",
            )
            rc = main(
                ["import", "espanso", "--input", str(source), "--output", str(output)]
            )
            self.assertEqual(rc, 0)
            self.assertTrue((output / "one.md").exists())
            raw_file = output / "imported_raw" / "match-1.yml"
            self.assertTrue(raw_file.exists())
            self.assertIn("      first\n\n      second\n", raw_file.read_text("utf-8"))

    def test_import_ignores_non_match_lists_after_matches(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source = base / "package.yml"
            output = base / "prompts"
            source.write_text(
                """matches:
  - trigger: ":tc-one"
    replace: ok
global_vars:
  - name: test
    type: shell
    params:
      cmd: echo nope
""",
                encoding="utf-8",
            )
            rc = main(
                ["import", "espanso", "--input", str(source), "--output", str(output)]
            )
            self.assertEqual(rc, 0)
            self.assertTrue((output / "tc-one.md").exists())
            self.assertFalse((output / "tc-one-2.md").exists())

    def test_import_seeds_existing_prompt_ids_and_raw_indices(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source = base / "package.yml"
            output = base / "prompts"
            output.mkdir(parents=True)
            (output / "tc-example.md").write_text("existing", encoding="utf-8")
            raw_dir = output / "imported_raw"
            raw_dir.mkdir(parents=True)
            (raw_dir / "match-1.yml").write_text("old", encoding="utf-8")
            source.write_text(
                """matches:
  - trigger: ":tc-example"
    replace: new
  - trigger: ":tc-complex"
    replace: thing
    shell: echo hi
""",
                encoding="utf-8",
            )
            rc = main(
                ["import", "espanso", "--input", str(source), "--output", str(output)]
            )
            self.assertEqual(rc, 0)
            self.assertTrue((output / "tc-example-2.md").exists())
            self.assertTrue((raw_dir / "match-2.yml").exists())


if __name__ == "__main__":
    unittest.main()
