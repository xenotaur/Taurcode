import contextlib
import io
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
            manifest_file = output_dir / "_manifest.yml"
            readme_file = output_dir / "README.md"
            self.assertTrue(package_file.exists())
            self.assertTrue(manifest_file.exists())
            self.assertTrue(readme_file.exists())

            package_text = package_file.read_text(encoding="utf-8")
            manifest_text = manifest_file.read_text(encoding="utf-8")
            readme_text = readme_file.read_text(encoding="utf-8")
            self.assertIn('trigger: ":tc-test"', package_text)
            self.assertIn("replace: |", package_text)
            self.assertIn("This is a test prompt body.", package_text)
            self.assertIn("name: taurcode", manifest_text)
            self.assertIn("title: Taurcode", manifest_text)
            self.assertTrue(readme_text.strip())
            self.assertIn("Taurcode", readme_text)

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
                b"version: 1.0.0\ndescription: Sample package\nauthor: Example Author\n"
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

    def test_export_prefers_curated_metadata_over_generated_defaults(self) -> None:
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
            curated_manifest = (
                b"name: sample\n"
                b"title: Curated Title\n"
                b"version: 9.9.9\n"
                b"description: Curated description\n"
                b"author: Curator\n"
            )
            curated_readme = b"# Curated Title\n\nCurated README.\n"
            (metadata_dir / "_manifest.yml").write_bytes(curated_manifest)
            (metadata_dir / "README.md").write_bytes(curated_readme)

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
            self.assertEqual(
                (output_dir / "_manifest.yml").read_bytes(), curated_manifest
            )
            self.assertEqual((output_dir / "README.md").read_bytes(), curated_readme)
            self.assertNotIn(
                "Generated prompt package",
                (output_dir / "_manifest.yml").read_text(encoding="utf-8"),
            )

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
            self.assertTrue((output_dir / "README.md").exists())
            self.assertIn(
                "Generated Espanso package",
                (output_dir / "README.md").read_text(encoding="utf-8"),
            )
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

    def test_generated_readme_prefers_source_manifest_title(self) -> None:
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
            (metadata_dir / "_manifest.yml").write_text(
                "name: sample\ntitle: Custom Sample Title\nversion: 1.0.0\ndescription: Sample package\nauthor: Example Author\n",
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

            readme_text = (output_dir / "README.md").read_text(encoding="utf-8")
            self.assertTrue(readme_text.strip())
            self.assertIn("Custom Sample Title", readme_text)
            self.assertIn("Generated Espanso package", readme_text)

    def test_export_reports_warnings_without_failing(self) -> None:
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
            (metadata_dir / "README.md").write_text("tiny\n", encoding="utf-8")

            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
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
            self.assertIn("Warnings:", stderr.getvalue())
            self.assertTrue((output_dir / "package.yml").exists())

    def test_export_fails_metadata_errors(self) -> None:
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
            (metadata_dir / "_manifest.yml").write_text(
                "name: sample\ndescription: Missing version\nauthor: Example Author\n",
                encoding="utf-8",
            )

            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
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

            self.assertEqual(rc, 1)
            self.assertIn("manifest-version-missing", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
