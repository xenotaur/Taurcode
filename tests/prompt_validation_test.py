import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from taurcode.cli import main


def _write_prompt(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class TestPromptValidation(unittest.TestCase):
    def test_validate_and_export_are_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            prompts_dir = base / "prompts"
            output_dir = base / "build" / "espanso" / "taurcode"

            _write_prompt(
                prompts_dir / "b.md",
                """---\nid: b\nname: Prompt B\ndescription: Desc B\nkeyword: ":tc-b"\n---\n\nBody B\n""",
            )
            _write_prompt(
                prompts_dir / "a.md",
                """---\nid: a\nname: Prompt A\ndescription: Desc A\nkeyword: ":tc-a"\n---\n\nBody A\n""",
            )

            rc_validate = main(["validate", "--prompts", str(prompts_dir)])
            self.assertEqual(rc_validate, 0)

            rc_export = main(
                [
                    "export",
                    "espanso",
                    "--prompts",
                    str(prompts_dir),
                    "--output",
                    str(output_dir),
                ]
            )
            self.assertEqual(rc_export, 0)
            first_output = (output_dir / "package.yml").read_text(encoding="utf-8")

            rc_export_again = main(
                [
                    "export",
                    "espanso",
                    "--prompts",
                    str(prompts_dir),
                    "--output",
                    str(output_dir),
                ]
            )
            self.assertEqual(rc_export_again, 0)
            second_output = (output_dir / "package.yml").read_text(encoding="utf-8")

            self.assertEqual(first_output, second_output)
            self.assertLess(
                first_output.find('trigger: ":tc-a"'),
                first_output.find('trigger: ":tc-b"'),
            )

    def test_malformed_yaml_frontmatter_validate_fails_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prompts_dir = Path(tmpdir) / "prompts"
            _write_prompt(
                prompts_dir / "broken.md",
                """---
id: [unterminated
name: Broken Prompt
---

Body
""",
            )

            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                rc = main(["validate", "--prompts", str(prompts_dir)])

            self.assertEqual(rc, 1)
            self.assertIn("Error: Malformed YAML frontmatter", stderr.getvalue())
            self.assertIn("broken.md", stderr.getvalue())
            self.assertNotIn("Traceback", stderr.getvalue())

    def test_malformed_yaml_frontmatter_export_fails_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            prompts_dir = base / "prompts"
            output_dir = base / "build" / "espanso" / "taurcode"
            _write_prompt(
                prompts_dir / "broken.md",
                """---
id: [unterminated
name: Broken Prompt
---

Body
""",
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
            self.assertIn("Error: Malformed YAML frontmatter", stderr.getvalue())
            self.assertIn("broken.md", stderr.getvalue())
            self.assertNotIn("Traceback", stderr.getvalue())

    def test_duplicate_id_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prompts_dir = Path(tmpdir) / "prompts"
            _write_prompt(
                prompts_dir / "a.md",
                """---\nid: shared\nname: A\ndescription: Desc\nkeyword: ":tc-a"\n---\n\nBody A\n""",
            )
            _write_prompt(
                prompts_dir / "b.md",
                """---\nid: shared\nname: B\ndescription: Desc\nkeyword: ":tc-b"\n---\n\nBody B\n""",
            )

            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                rc = main(["validate", "--prompts", str(prompts_dir)])
            self.assertEqual(rc, 1)
            self.assertIn("Duplicate id 'shared'", stderr.getvalue())

    def test_duplicate_keyword_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prompts_dir = Path(tmpdir) / "prompts"
            _write_prompt(
                prompts_dir / "a.md",
                """---\nid: a\nname: A\ndescription: Desc\nkeyword: ":tc-shared"\n---\n\nBody A\n""",
            )
            _write_prompt(
                prompts_dir / "b.md",
                """---\nid: b\nname: B\ndescription: Desc\nkeyword: ":tc-shared"\n---\n\nBody B\n""",
            )

            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                rc = main(["validate", "--prompts", str(prompts_dir)])
            self.assertEqual(rc, 1)
            self.assertIn("Duplicate keyword ':tc-shared'", stderr.getvalue())

    def test_missing_field_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prompts_dir = Path(tmpdir) / "prompts"
            _write_prompt(
                prompts_dir / "a.md",
                """---\nname: A\ndescription: Desc\nkeyword: ":tc-a"\n---\n\nBody A\n""",
            )

            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                rc = main(["validate", "--prompts", str(prompts_dir)])
            self.assertEqual(rc, 1)
            self.assertIn("Missing required field 'id'", stderr.getvalue())

    def test_invalid_keyword_format_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prompts_dir = Path(tmpdir) / "prompts"
            _write_prompt(
                prompts_dir / "a.md",
                """---\nid: a\nname: A\ndescription: Desc\nkeyword: "tc-a"\n---\n\nBody A\n""",
            )

            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                rc = main(["validate", "--prompts", str(prompts_dir)])
            self.assertEqual(rc, 1)
            self.assertIn("must start with ':' and not be empty", stderr.getvalue())

    def test_empty_body_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prompts_dir = Path(tmpdir) / "prompts"
            _write_prompt(
                prompts_dir / "a.md",
                """---\nid: a\nname: A\ndescription: Desc\nkeyword: ":tc-a"\n---\n""",
            )

            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                rc = main(["validate", "--prompts", str(prompts_dir)])
            self.assertEqual(rc, 1)
            self.assertIn("Missing required field 'body'", stderr.getvalue())

    def test_whitespace_only_body_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prompts_dir = Path(tmpdir) / "prompts"
            _write_prompt(
                prompts_dir / "a.md",
                """---\nid: a\nname: A\ndescription: Desc\nkeyword: ":tc-a"\n---\n\n   \n\t\n""",
            )

            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                rc = main(["validate", "--prompts", str(prompts_dir)])
            self.assertEqual(rc, 1)
            self.assertIn("Prompt body must not be blank", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
