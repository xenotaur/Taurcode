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
  - trigger: ":tc-folded"
    replace: >-
      line one
      line two
""",
                encoding="utf-8",
            )

            rc = main(
                ["import", "espanso", "--input", str(source), "--output", str(output)]
            )
            self.assertEqual(rc, 0)
            imported = (output / "tc-folded.md").read_text(encoding="utf-8")
            self.assertTrue(imported.endswith("line one line two\n"))

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
