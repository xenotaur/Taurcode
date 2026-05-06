import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from taurcode import espanso_lint
from taurcode.cli import main


class TestEspansoLint(unittest.TestCase):
    def test_clean_package_has_no_diagnostics(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            package = Path(tmpdir) / "package.yml"
            package.write_text(
                """matches:
  - trigger: ":hello"
    replace: "hello"
""",
                encoding="utf-8",
            )

            diagnostics = espanso_lint.lint_espanso_package(package)

            self.assertEqual(diagnostics, [])
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                rc = main(["lint", "espanso", "--input", str(package)])
            self.assertEqual(rc, 0)
            self.assertIn("Espanso lint passed", stdout.getvalue())

    def test_line_separator_reports_location_and_suggestion(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            package = Path(tmpdir) / "package.yml"
            package.write_text(
                "matches:\n"
                '  - trigger: ":line"\n'
                "    replace: |\n"
                "      before\n"
                "      abc\u2028after\n",
                encoding="utf-8",
            )

            diagnostics = espanso_lint.lint_espanso_package(package)

            self.assertEqual(len(diagnostics), 1)
            rendered = espanso_lint.format_diagnostic(diagnostics[0])
            self.assertIn("U+2028 LINE SEPARATOR", rendered)
            self.assertIn(f"{package}:5:10", rendered)
            self.assertIn("Suggestion: replace it with a normal newline", rendered)

    def test_paragraph_separator_and_next_line_are_identified(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            package = Path(tmpdir) / "package.yml"
            package.write_text(
                "matches:\n"
                '  - trigger: ":line"\n'
                "    replace: |\n"
                "      before\u2029middle\u0085after\n",
                encoding="utf-8",
            )

            rendered = espanso_lint.format_diagnostics(
                espanso_lint.lint_espanso_package(package)
            )

            self.assertIn("U+2029 PARAGRAPH SEPARATOR", rendered)
            self.assertIn("U+0085 NEXT LINE", rendered)

    def test_missing_package_yml_in_directory_is_clear(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaisesRegex(ValueError, "Missing Espanso package.yml"):
                espanso_lint.lint_espanso_package(tmpdir)

            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                rc = main(["lint", "espanso", "--input", tmpdir])
            self.assertEqual(rc, 1)
            self.assertIn("Missing Espanso package.yml", stderr.getvalue())

    def test_malformed_yaml_reports_parser_location(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            package = Path(tmpdir) / "package.yml"
            package.write_text(
                """matches:
  - trigger: ":broken"
    replace: [unterminated
""",
                encoding="utf-8",
            )

            diagnostics = espanso_lint.lint_espanso_package(package)

            self.assertEqual(len(diagnostics), 1)
            rendered = espanso_lint.format_diagnostic(diagnostics[0])
            self.assertIn("Invalid Espanso package.yml: malformed YAML", rendered)
            self.assertRegex(rendered, rf"{package}:\d+:\d+")

    def test_utf8_decode_error_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            package = Path(tmpdir) / "package.yml"
            package.write_bytes(b"matches:\n  - trigger: \xff\n")

            rendered = espanso_lint.format_diagnostics(
                espanso_lint.lint_espanso_package(package)
            )

            self.assertIn("UTF-8 decode error", rendered)
            self.assertIn("valid UTF-8", rendered)

    def test_import_surfaces_preflight_diagnostic(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            package = base / "package.yml"
            output = base / "prompts"
            package.write_text(
                "matches:\n"
                '  - trigger: ":line"\n'
                "    replace: |\n"
                "      before\u2028after\n",
                encoding="utf-8",
            )

            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                rc = main(
                    [
                        "import",
                        "espanso",
                        "--input",
                        str(package),
                        "--output",
                        str(output),
                    ]
                )

            self.assertEqual(rc, 1)
            self.assertIn("U+2028 LINE SEPARATOR", stderr.getvalue())
            self.assertIn(
                "Suggestion: replace it with a normal newline", stderr.getvalue()
            )
            self.assertNotIn("malformed YAML", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
