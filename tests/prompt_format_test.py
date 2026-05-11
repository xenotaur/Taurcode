import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from taurcode import cli, prompt_format


class TestPromptFormat(unittest.TestCase):
    def test_quotes_keyword_values(self) -> None:
        document = _prompt_document(keyword=":debug")

        formatted = prompt_format.format_prompt_document(document)

        self.assertIn('keyword: ":debug"\n', formatted)

    def test_leaves_already_quoted_keyword_values_unchanged(self) -> None:
        document = _prompt_document(keyword='":debug"')

        formatted = prompt_format.format_prompt_document(document)

        self.assertEqual(document, formatted)

    def test_preserves_description_as_single_line(self) -> None:
        description = (
            "Use this deliberately long single-line description without wrapping it"
        )
        document = _prompt_document(keyword=":debug", description=description)

        formatted = prompt_format.format_prompt_document(document)

        self.assertIn(f"description: {description}\n", formatted)
        self.assertNotIn("\n  without wrapping", formatted)

    def test_preserves_prompt_body_except_final_newline_normalization(self) -> None:
        body = (
            "  keep leading body spaces\n\nKeep trailing spaces here   \nNo EOF newline"
        )
        document = _prompt_document(keyword=":debug", body=body).rstrip("\n")

        formatted = prompt_format.format_prompt_document(document)

        self.assertTrue(formatted.endswith("No EOF newline\n"))
        self.assertIn(body, formatted)

    def test_normalizes_no_final_newline_to_one_final_newline(self) -> None:
        document = _prompt_document().rstrip("\n")

        formatted = prompt_format.format_prompt_document(document)

        self.assertTrue(formatted.endswith("\n"))
        self.assertFalse(formatted.endswith("\n\n"))

    def test_normalizes_multiple_final_newlines_to_one_final_newline(self) -> None:
        document = _prompt_document() + "\n\n"

        formatted = prompt_format.format_prompt_document(document)

        self.assertTrue(formatted.endswith("\n"))
        self.assertFalse(formatted.endswith("\n\n"))

    def test_does_not_rewrite_files_under_espanso_metadata_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prompt_dir = Path(tmpdir)
            _write_prompt(prompt_dir / "debug.md", keyword=":debug")
            espanso_dir = prompt_dir / "espanso"
            espanso_dir.mkdir()
            metadata_file = espanso_dir / "README.md"
            metadata_original = "# metadata\n\n\n"
            metadata_file.write_text(metadata_original, encoding="utf-8")

            prompt_format.format_prompt_package(prompt_dir)

            self.assertEqual(
                metadata_original, metadata_file.read_text(encoding="utf-8")
            )
            self.assertIn(
                'keyword: ":debug"\n',
                (prompt_dir / "debug.md").read_text(encoding="utf-8"),
            )

    def test_formatter_is_idempotent(self) -> None:
        document = _prompt_document(keyword=":debug") + "\n\n"

        once = prompt_format.format_prompt_document(document)
        twice = prompt_format.format_prompt_document(once)

        self.assertEqual(once, twice)

    def test_cli_formats_prompt_package(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prompt = Path(tmpdir) / "debug.md"
            _write_prompt(prompt, keyword=":debug")
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                rc = cli.main(["format", "prompts", "--prompts", tmpdir])

            self.assertEqual(rc, 0)
            self.assertIn("Formatted:", stdout.getvalue())
            self.assertIn('keyword: ":debug"\n', prompt.read_text(encoding="utf-8"))

    def test_cli_check_reports_unformatted_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prompt = Path(tmpdir) / "debug.md"
            _write_prompt(prompt, keyword=":debug")
            original = prompt.read_text(encoding="utf-8")
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                rc = cli.main(["format", "prompts", "--prompts", tmpdir, "--check"])

            self.assertEqual(rc, 1)
            self.assertIn("Would format:", stdout.getvalue())
            self.assertEqual(original, prompt.read_text(encoding="utf-8"))


def _prompt_document(
    keyword: str = '":debug"',
    description: str = "Debug an issue",
    body: str = "Debug this issue.",
) -> str:
    return (
        "---\n"
        "id: debug\n"
        "name: Debug\n"
        f"description: {description}\n"
        f"keyword: {keyword}\n"
        "---\n\n"
        f"{body}\n"
    )


def _write_prompt(path: Path, keyword: str = '":debug"') -> None:
    path.write_text(_prompt_document(keyword=keyword), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
