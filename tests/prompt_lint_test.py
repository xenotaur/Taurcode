import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from taurcode import prompt_lint
from taurcode.cli import main


class TestPromptLint(unittest.TestCase):
    def test_valid_prompt_file_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prompt_dir = Path(tmpdir)
            _write_prompt(prompt_dir / "debug.md")

            result = prompt_lint.lint_prompt_package(prompt_dir)

            self.assertFalse(result.has_errors())
            self.assertFalse(result.has_warnings())

    def test_missing_frontmatter_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prompt = Path(tmpdir) / "debug.md"
            prompt.write_text("body only\n", encoding="utf-8")

            result = prompt_lint.lint_prompt_package(tmpdir)

            self.assertDiagnosticCode(result.errors, "prompt-frontmatter-missing")

    def test_invalid_yaml_frontmatter_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prompt = Path(tmpdir) / "debug.md"
            prompt.write_text(
                "---\n"
                "id: debug\n"
                "name: Debug\n"
                "description: [unterminated\n"
                'keyword: ":debug"\n'
                "---\n\n"
                "body\n",
                encoding="utf-8",
            )

            result = prompt_lint.lint_prompt_package(tmpdir)

            self.assertDiagnosticCode(result.errors, "prompt-frontmatter-yaml")

    def test_non_mapping_frontmatter_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prompt = Path(tmpdir) / "debug.md"
            prompt.write_text("---\n- debug\n---\n\nbody\n", encoding="utf-8")

            result = prompt_lint.lint_prompt_package(tmpdir)

            self.assertDiagnosticCode(result.errors, "prompt-frontmatter-not-mapping")

    def test_missing_required_field_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            _write_prompt(Path(tmpdir) / "debug.md", omit_field="description")

            result = prompt_lint.lint_prompt_package(tmpdir)

            self.assertDiagnosticCode(result.errors, "prompt-required-field-missing")

    def test_keyword_missing_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            _write_prompt(Path(tmpdir) / "debug.md", omit_field="keyword")

            result = prompt_lint.lint_prompt_package(tmpdir)

            self.assertDiagnosticCode(result.errors, "prompt-keyword-missing")

    def test_keyword_non_string_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            _write_prompt(Path(tmpdir) / "debug.md", keyword="[debug]")

            result = prompt_lint.lint_prompt_package(tmpdir)

            self.assertDiagnosticCode(result.errors, "prompt-keyword-not-string")

    def test_keyword_not_starting_with_colon_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            _write_prompt(Path(tmpdir) / "debug.md", keyword='"debug"')

            result = prompt_lint.lint_prompt_package(tmpdir)

            self.assertDiagnosticCode(result.errors, "prompt-keyword-invalid-prefix")

    def test_duplicate_keyword_errors_within_package(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prompt_dir = Path(tmpdir)
            _write_prompt(prompt_dir / "debug.md")
            _write_prompt(prompt_dir / "debug-copy.md", prompt_id="debug-copy")

            result = prompt_lint.lint_prompt_package(prompt_dir)

            self.assertDiagnosticCode(result.errors, "prompt-duplicate-keyword")

    def test_espanso_readme_is_ignored_as_prompt(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prompt_dir = Path(tmpdir)
            _write_prompt(prompt_dir / "debug.md")
            espanso_dir = prompt_dir / "espanso"
            espanso_dir.mkdir()
            (espanso_dir / "README.md").write_text(
                "# Package metadata readme without frontmatter\n", encoding="utf-8"
            )

            result = prompt_lint.lint_prompt_package(prompt_dir)

            self.assertFalse(result.has_errors())

    def test_empty_body_warning(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            _write_prompt(Path(tmpdir) / "debug.md", body="   ")

            result = prompt_lint.lint_prompt_package(tmpdir)

            self.assertDiagnosticCode(result.warnings, "prompt-body-empty")

    def test_missing_final_newline_warning(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prompt = Path(tmpdir) / "debug.md"
            _write_prompt(prompt)
            prompt.write_text(
                prompt.read_text(encoding="utf-8").rstrip("\n"), encoding="utf-8"
            )

            result = prompt_lint.lint_prompt_package(tmpdir)

            self.assertDiagnosticCode(result.warnings, "prompt-final-newline")

    def test_unquoted_keyword_warning(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            _write_prompt(Path(tmpdir) / "debug.md", keyword=":debug")

            result = prompt_lint.lint_prompt_package(tmpdir)

            self.assertDiagnosticCode(result.warnings, "prompt-keyword-unquoted")

    def test_wrapped_description_warning(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prompt = Path(tmpdir) / "debug.md"
            prompt.write_text(
                "---\n"
                "id: debug\n"
                "name: Debug\n"
                "description: This description was wrapped by a serializer and\n"
                "  continued on the next line\n"
                'keyword: ":debug"\n'
                "---\n\n"
                "body\n",
                encoding="utf-8",
            )

            result = prompt_lint.lint_prompt_package(tmpdir)

            self.assertDiagnosticCode(result.warnings, "prompt-description-wrapped")

    def test_errors_fail_cli(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prompt = Path(tmpdir) / "debug.md"
            prompt.write_text("body only\n", encoding="utf-8")
            stderr = io.StringIO()

            with contextlib.redirect_stderr(stderr):
                rc = main(["lint", "prompts", "--prompts", tmpdir])

            self.assertEqual(rc, 1)
            self.assertIn("prompt-frontmatter-missing", stderr.getvalue())

    def test_warnings_do_not_fail_cli_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            _write_prompt(Path(tmpdir) / "debug.md", keyword=":debug")
            stdout = io.StringIO()
            stderr = io.StringIO()

            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                rc = main(["lint", "prompts", "--prompts", tmpdir])

            self.assertEqual(rc, 0)
            self.assertIn("Prompt lint passed", stdout.getvalue())
            self.assertIn("prompt-keyword-unquoted", stderr.getvalue())

    def assertDiagnosticCode(self, diagnostics, code: str) -> None:
        codes = [diagnostic.code for diagnostic in diagnostics]
        self.assertIn(code, codes)


def _write_prompt(
    path: Path,
    prompt_id: str = "debug",
    keyword: str = '":debug"',
    body: str = "Debug this issue.",
    omit_field: str = "",
) -> None:
    values = {
        "id": prompt_id,
        "name": "Debug",
        "description": "Debug an issue",
        "keyword": keyword,
    }
    lines = ["---"]
    for field_name in ("id", "name", "description", "keyword"):
        if field_name == omit_field:
            continue
        lines.append(f"{field_name}: {values[field_name]}")
    lines.extend(["---", "", body])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
