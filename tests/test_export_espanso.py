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


if __name__ == "__main__":
    unittest.main()
