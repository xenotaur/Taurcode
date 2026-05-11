import shutil
import tempfile
import unittest
from pathlib import Path

from taurcode.cli import main

FIXTURES = Path(__file__).parent / "fixtures" / "roundtrip"


class TestEspansoRoundTrip(unittest.TestCase):
    def test_merge_import_preserves_curated_frontmatter_and_final_newline(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source_dir = FIXTURES / "espanso_source"
            prompts_dir = base / "prompts"
            output_dir = base / "build" / "espanso" / "fixture"
            shutil.copytree(FIXTURES / "existing_prompts", prompts_dir)

            rc = main(
                [
                    "import",
                    "espanso",
                    "--input",
                    str(source_dir),
                    "--output",
                    str(prompts_dir),
                    "--merge",
                ]
            )
            self.assertEqual(rc, 0)

            merged_bytes = (prompts_dir / "debug.md").read_bytes()
            expected_bytes = (FIXTURES / "expected_prompts" / "debug.md").read_bytes()
            self.assertEqual(merged_bytes, expected_bytes)
            self.assertTrue(merged_bytes.endswith(b"\n"))
            self.assertFalse(merged_bytes.endswith(b"\n\n"))

            rc = main(
                [
                    "export",
                    "espanso",
                    "--prompts",
                    str(prompts_dir),
                    "--output",
                    str(output_dir),
                ]
            )
            self.assertEqual(rc, 0)
            package_text = (output_dir / "package.yml").read_text(encoding="utf-8")
            self.assertIn('trigger: ":debug"', package_text)
            self.assertIn("New body from Espanso", package_text)
            self.assertIn("Preserve this internal blank line.", package_text)

    def test_merge_export_merge_round_trip_is_stable(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            prompts_dir = base / "prompts"
            first_export = base / "build" / "espanso" / "fixture"
            shutil.copytree(FIXTURES / "existing_prompts", prompts_dir)

            rc = main(
                [
                    "import",
                    "espanso",
                    "--input",
                    str(FIXTURES / "espanso_source"),
                    "--output",
                    str(prompts_dir),
                    "--merge",
                ]
            )
            self.assertEqual(rc, 0)
            after_first_merge = (prompts_dir / "debug.md").read_bytes()

            rc = main(
                [
                    "export",
                    "espanso",
                    "--prompts",
                    str(prompts_dir),
                    "--output",
                    str(first_export),
                ]
            )
            self.assertEqual(rc, 0)

            rc = main(
                [
                    "import",
                    "espanso",
                    "--input",
                    str(first_export),
                    "--output",
                    str(prompts_dir),
                    "--merge",
                ]
            )
            self.assertEqual(rc, 0)
            self.assertEqual((prompts_dir / "debug.md").read_bytes(), after_first_merge)


if __name__ == "__main__":
    unittest.main()
