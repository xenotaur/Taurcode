import tempfile
import unittest
from pathlib import Path

from taurcode.cli import main


class TestEspansoExport(unittest.TestCase):
    def test_export_from_markdown_prompt(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            prompts_dir = base / "prompts"
            output_dir = base / "build" / "espanso" / "taurcode"
            prompts_dir.mkdir(parents=True)

            prompt_file = prompts_dir / "prompt.md"
            prompt_file.write_text(
                """---\nid: test-prompt\nname: Test Prompt\ndescription: A test prompt\nkeyword: \":tc-test\"\n---\n\nThis is a test prompt body.\n""",
                encoding="utf-8",
            )

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

            package_file = output_dir / "package.yml"
            self.assertTrue(package_file.exists())

            package_text = package_file.read_text(encoding="utf-8")
            self.assertIn('trigger: ":tc-test"', package_text)
            self.assertIn("replace: |", package_text)
            self.assertIn("This is a test prompt body.", package_text)

    def test_export_supports_crlf_frontmatter(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            prompts_dir = base / "prompts"
            output_dir = base / "build" / "espanso" / "taurcode"
            prompts_dir.mkdir(parents=True)

            prompt_file = prompts_dir / "prompt.md"
            prompt_file.write_bytes(
                b'---\r\nid: crlf-prompt\r\nname: CRLF Prompt\r\ndescription: CRLF test\r\nkeyword: ":tc-crlf"\r\n---\r\n\r\nBody from CRLF.\r\n'
            )

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
            self.assertIn('trigger: ":tc-crlf"', package_text)
            self.assertIn("Body from CRLF.", package_text)

    def test_export_copies_source_metadata_assets(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            prompts_dir = base / "prompts"
            metadata_dir = prompts_dir / "espanso"
            output_dir = base / "build" / "espanso" / "sample"
            metadata_dir.mkdir(parents=True)
            manifest = (
                b'name: sample\n# preserve manifest formatting\ntitle: "Sample"\n'
            )
            readme = b"# Sample\n\nPreserve this README exactly.\n"
            license_text = b"Sample license\n\nLine two.\n"
            (prompts_dir / "prompt.md").write_text(
                """---
id: test-prompt
name: Test Prompt
description: A test prompt
keyword: ":tc-test"
---

This is a test prompt body.
""",
                encoding="utf-8",
            )
            (metadata_dir / "_manifest.yml").write_bytes(manifest)
            (metadata_dir / "README.md").write_bytes(readme)
            (metadata_dir / "LICENSE").write_bytes(license_text)

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

            self.assertEqual((output_dir / "_manifest.yml").read_bytes(), manifest)
            self.assertEqual((output_dir / "README.md").read_bytes(), readme)
            self.assertEqual((output_dir / "LICENSE").read_bytes(), license_text)

    def test_export_removes_stale_metadata_assets(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            prompts_dir = base / "prompts"
            metadata_dir = prompts_dir / "espanso"
            output_dir = base / "build" / "espanso" / "sample"
            metadata_dir.mkdir(parents=True)
            (prompts_dir / "prompt.md").write_text(
                """---
id: test-prompt
name: Test Prompt
description: A test prompt
keyword: ":tc-test"
---

This is a test prompt body.
""",
                encoding="utf-8",
            )
            (metadata_dir / "README.md").write_text("old source", encoding="utf-8")
            (metadata_dir / "LICENSE").write_text("old license", encoding="utf-8")

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
            self.assertTrue((output_dir / "README.md").exists())
            self.assertTrue((output_dir / "LICENSE").exists())

            (metadata_dir / "README.md").unlink()
            (metadata_dir / "LICENSE").unlink()

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
            self.assertFalse((output_dir / "README.md").exists())
            self.assertFalse((output_dir / "LICENSE").exists())

    def test_export_ignores_espanso_readme_as_prompt_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            prompts_dir = base / "prompts"
            metadata_dir = prompts_dir / "espanso"
            output_dir = base / "build" / "espanso" / "sample"
            metadata_dir.mkdir(parents=True)
            (prompts_dir / "prompt.md").write_text(
                """---
id: test-prompt
name: Test Prompt
description: A test prompt
keyword: ":tc-test"
---

This is a test prompt body.
""",
                encoding="utf-8",
            )
            (metadata_dir / "README.md").write_text(
                "# Metadata README\n\nThis is not a prompt.\n", encoding="utf-8"
            )

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
            self.assertIn('trigger: ":tc-test"', package_text)
            self.assertNotIn("Metadata README", package_text)
            self.assertEqual(
                (output_dir / "README.md").read_text(encoding="utf-8"),
                "# Metadata README\n\nThis is not a prompt.\n",
            )


if __name__ == "__main__":
    unittest.main()
