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

    def test_multiple_line_separators_advance_diagnostic_locations(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            package = Path(tmpdir) / "package.yml"
            package.write_text(
                "matches:\n"
                '  - trigger: ":line"\n'
                "    replace: |\n"
                "      before\u2028after\u2029again\n",
                encoding="utf-8",
            )

            diagnostics = espanso_lint.lint_espanso_package(package)

            self.assertEqual(len(diagnostics), 2)
            self.assertEqual((diagnostics[0].line, diagnostics[0].column), (4, 13))
            self.assertEqual((diagnostics[1].line, diagnostics[1].column), (5, 6))

    def test_crlf_counts_as_single_newline_for_locations(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            package = Path(tmpdir) / "package.yml"
            package.write_text(
                "matches:\r\n"
                '  - trigger: ":line"\r\n'
                "    replace: |\r\n"
                "      before\r\n"
                "      abc\u2028after\r\n",
                encoding="utf-8",
                newline="",
            )

            diagnostics = espanso_lint.lint_espanso_package(package)

            self.assertEqual(len(diagnostics), 1)
            self.assertEqual((diagnostics[0].line, diagnostics[0].column), (5, 10))

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
            self.assertNotRegex(rendered, rf"malformed YAML at {package}:\d+:\d+")

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


class TestEspansoMetadataLint(unittest.TestCase):
    def _write_build_package(
        self,
        package_dir: Path,
        manifest: str | None = None,
        readme: str = "# sample\n\nSample package documentation.\n",
    ) -> None:
        package_dir.mkdir(parents=True)
        (package_dir / "package.yml").write_text("matches: []\n", encoding="utf-8")
        manifest_text = manifest or (
            "name: sample\n"
            "title: Sample\n"
            "description: Useful sample package\n"
            "version: 1.2.3\n"
            "author: Example Author\n"
            "homepage: https://github.com/example/sample\n"
        )
        (package_dir / "_manifest.yml").write_text(manifest_text, encoding="utf-8")
        (package_dir / "README.md").write_text(readme, encoding="utf-8")

    def _error_codes(self, result: espanso_lint.LintResult) -> set[str]:
        return {diagnostic.code for diagnostic in result.errors}

    def _warning_codes(self, result: espanso_lint.LintResult) -> set[str]:
        return {diagnostic.code for diagnostic in result.warnings}

    def test_invalid_yaml_manifest_produces_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            package_dir = Path(tmpdir) / "sample"
            self._write_build_package(package_dir, manifest="name: [unterminated\n")

            result = espanso_lint.lint_espanso_package_build(package_dir)

            self.assertIn("manifest-malformed-yaml", self._error_codes(result))
            self.assertIn("_manifest.yml", espanso_lint.format_lint_result(result))

    def test_manifest_name_missing_produces_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            package_dir = Path(tmpdir) / "sample"
            self._write_build_package(
                package_dir,
                manifest="title: Sample\nversion: 1.0.0\nauthor: Person\ndescription: Text\n",
            )

            result = espanso_lint.lint_espanso_package_build(package_dir)

            self.assertIn("manifest-name-missing", self._error_codes(result))

    def test_manifest_name_mismatch_produces_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            package_dir = Path(tmpdir) / "sample"
            self._write_build_package(
                package_dir,
                manifest="name: other\nversion: 1.0.0\nauthor: Person\ndescription: Text\n",
            )

            result = espanso_lint.lint_espanso_package_build(package_dir)

            self.assertIn("manifest-name-mismatch", self._error_codes(result))

    def test_invalid_package_name_produces_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            package_dir = Path(tmpdir) / "Bad_Name"
            self._write_build_package(
                package_dir,
                manifest="name: Bad_Name\nversion: 1.0.0\nauthor: Person\ndescription: Text\n",
            )

            result = espanso_lint.lint_espanso_package_build(package_dir)

            self.assertIn("invalid-package-name", self._error_codes(result))

    def test_missing_version_produces_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            package_dir = Path(tmpdir) / "sample"
            self._write_build_package(
                package_dir,
                manifest="name: sample\nauthor: Person\ndescription: Text\n",
            )

            result = espanso_lint.lint_espanso_package_build(package_dir)

            self.assertIn("manifest-version-missing", self._error_codes(result))

    def test_invalid_version_core_produces_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            package_dir = Path(tmpdir) / "sample"
            self._write_build_package(
                package_dir,
                manifest="name: sample\nversion: v1\nauthor: Person\ndescription: Text\n",
            )

            result = espanso_lint.lint_espanso_package_build(package_dir)

            self.assertIn("manifest-version-invalid", self._error_codes(result))

    def test_missing_required_build_output_file_produces_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            package_dir = Path(tmpdir) / "sample"
            self._write_build_package(package_dir)
            (package_dir / "README.md").unlink()

            result = espanso_lint.lint_espanso_package_build(package_dir)

            self.assertIn("missing-build-file", self._error_codes(result))

    def test_empty_or_tiny_readme_produces_warning(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            package_dir = Path(tmpdir) / "sample"
            self._write_build_package(package_dir, readme="tiny\n")

            result = espanso_lint.lint_espanso_package_build(package_dir)

            self.assertIn("readme-too-small", self._warning_codes(result))
            self.assertFalse(result.has_errors())

    def test_readme_missing_package_name_or_title_produces_warning(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            package_dir = Path(tmpdir) / "sample"
            self._write_build_package(
                package_dir,
                readme="# Completely Different\n\nHelpful documentation text.\n",
            )

            result = espanso_lint.lint_espanso_package_build(package_dir)

            self.assertIn("readme-missing-package-name", self._warning_codes(result))

    def test_placeholder_description_produces_warning(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            package_dir = Path(tmpdir) / "sample"
            self._write_build_package(
                package_dir,
                manifest=(
                    "name: sample\nversion: 1.0.0\n"
                    "description: Generated prompt package\nauthor: Person\n"
                ),
            )

            result = espanso_lint.lint_espanso_package_build(package_dir)

            self.assertIn(
                "manifest-description-placeholder", self._warning_codes(result)
            )

    def test_placeholder_author_produces_warning(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            package_dir = Path(tmpdir) / "sample"
            self._write_build_package(
                package_dir,
                manifest=(
                    "name: sample\nversion: 1.0.0\n"
                    "description: Useful package\nauthor: Taurcode\n"
                ),
            )

            result = espanso_lint.lint_espanso_package_build(package_dir)

            self.assertIn("manifest-author-placeholder", self._warning_codes(result))

    def test_non_http_homepage_produces_warning(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            package_dir = Path(tmpdir) / "sample"
            self._write_build_package(
                package_dir,
                manifest=(
                    "name: sample\nversion: 1.0.0\n"
                    "description: Useful package\nauthor: Person\n"
                    "homepage: git@example.com:example/sample.git\n"
                ),
            )

            result = espanso_lint.lint_espanso_package_build(package_dir)

            self.assertIn("manifest-homepage-non-http", self._warning_codes(result))

    def test_warnings_do_not_fail_lint_command_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            package_dir = Path(tmpdir) / "sample"
            self._write_build_package(package_dir, readme="tiny\n")

            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                rc = main(["lint", "espanso", "--input", str(package_dir)])

            self.assertEqual(rc, 0)
            self.assertIn("Warnings:", stderr.getvalue())
            self.assertIn("readme", stderr.getvalue().lower())

    def test_errors_fail_lint_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            package_dir = Path(tmpdir) / "sample"
            self._write_build_package(package_dir, manifest="name: sample\n")

            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                rc = main(["lint", "espanso", "--input", str(package_dir)])

            self.assertEqual(rc, 1)
            self.assertIn("Errors:", stderr.getvalue())

    def test_package_yml_input_runs_metadata_lint(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            package_dir = Path(tmpdir) / "sample"
            self._write_build_package(package_dir, manifest="name: sample\n")

            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                rc = main(
                    ["lint", "espanso", "--input", str(package_dir / "package.yml")]
                )

            self.assertEqual(rc, 1)
            self.assertIn("manifest-version-missing", stderr.getvalue())

    def test_source_lint_uses_defaults_when_metadata_is_absent(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            package_dir = Path(tmpdir) / "sample"
            package_dir.mkdir()

            result = espanso_lint.lint_espanso_package_source(package_dir)

            self.assertFalse(result.has_errors())
            self.assertIn(
                "manifest-description-placeholder", self._warning_codes(result)
            )


if __name__ == "__main__":
    unittest.main()
