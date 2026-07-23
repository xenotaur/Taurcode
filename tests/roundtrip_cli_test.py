import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from taurcode import cli


class TestRoundtripCli(unittest.TestCase):
    def test_roundtrip_success_from_exported_package(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            prompts_dir = base / "prompts"
            output_dir = base / "sample"
            _write_prompt_package(prompts_dir, include_metadata=True)

            export_rc, _stdout, _stderr = _run_cli(
                [
                    "export",
                    "espanso",
                    "--prompts",
                    str(prompts_dir),
                    "--output",
                    str(output_dir),
                ]
            )
            self.assertEqual(export_rc, 0)

            rc, stdout, stderr = _run_cli(
                [
                    "roundtrip",
                    "espanso",
                    "--input",
                    str(output_dir),
                    "--prompts",
                    str(prompts_dir),
                ]
            )

            self.assertEqual(rc, 0, stderr)
            self.assertIn("Roundtrip semantic comparison passed.", stdout)
            self.assertIn("Prompts compared: 2", stdout)
            self.assertIn("Metadata assets compared: 3", stdout)
            self.assertIn("Differences: 0", stdout)

    def test_roundtrip_reports_prompt_body_difference(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            prompts_dir = base / "prompts"
            package_dir = base / "espanso"
            _write_prompt_package(prompts_dir, include_metadata=True)
            _write_equivalent_espanso_package(package_dir, include_metadata=True)
            (package_dir / "package.yml").write_text(
                """matches:
  - trigger: ":alpha"
    replace: "Changed body.\\n"
  - trigger: ":beta"
    replace: "Beta body.\\n"
""",
                encoding="utf-8",
            )

            rc, stdout, _stderr = _run_cli(
                [
                    "roundtrip",
                    "espanso",
                    "--input",
                    str(package_dir),
                    "--prompts",
                    str(prompts_dir),
                ]
            )

            self.assertEqual(rc, 1)
            self.assertIn("Roundtrip semantic comparison failed.", stdout)
            self.assertIn("prompts[:alpha].body", stdout)
            self.assertIn("Prompt body differs", stdout)

    def test_roundtrip_reports_trigger_difference(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            prompts_dir = base / "prompts"
            package_dir = base / "espanso"
            _write_prompt_package(prompts_dir, include_metadata=True)
            _write_equivalent_espanso_package(package_dir, include_metadata=True)
            (package_dir / "package.yml").write_text(
                """matches:
  - trigger: ":changed-alpha"
    replace: "Alpha body.\\n"
  - trigger: ":beta"
    replace: "Beta body.\\n"
""",
                encoding="utf-8",
            )

            rc, stdout, _stderr = _run_cli(
                [
                    "roundtrip",
                    "espanso",
                    "--input",
                    str(package_dir / "package.yml"),
                    "--prompts",
                    str(prompts_dir),
                ]
            )

            self.assertEqual(rc, 1)
            self.assertIn("Roundtrip semantic comparison failed.", stdout)
            self.assertIn("prompts[:alpha]", stdout)
            self.assertIn("prompts[:changed-alpha]", stdout)

    def test_roundtrip_reports_dropped_force_clipboard(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            prompts_dir = base / "prompts"
            package_dir = base / "espanso"
            prompts_dir.mkdir(parents=True)
            (prompts_dir / "short.md").write_text(
                """---
id: short
name: Short
description: A short prompt
keyword: ":tc-short"
targets:
  espanso:
    force_clipboard: true
---

Short body.
""",
                encoding="utf-8",
            )

            export_rc, _stdout, export_stderr = _run_cli(
                [
                    "export",
                    "espanso",
                    "--prompts",
                    str(prompts_dir),
                    "--output",
                    str(package_dir),
                ]
            )
            self.assertEqual(export_rc, 0, export_stderr)
            exported = (package_dir / "package.yml").read_text(encoding="utf-8")
            self.assertIn("force_clipboard: true", exported)

            # Simulate an exporter regression that silently drops force_clipboard.
            (package_dir / "package.yml").write_text(
                exported.replace("    force_clipboard: true\n", ""), encoding="utf-8"
            )

            rc, stdout, _stderr = _run_cli(
                [
                    "roundtrip",
                    "espanso",
                    "--input",
                    str(package_dir),
                    "--prompts",
                    str(prompts_dir),
                ]
            )

            self.assertEqual(rc, 1)
            self.assertIn("Roundtrip semantic comparison failed.", stdout)
            self.assertIn("prompts[:tc-short].force_clipboard", stdout)
            self.assertIn("force_clipboard differs", stdout)

    def test_roundtrip_reports_metadata_difference(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            prompts_dir = base / "prompts"
            package_dir = base / "espanso"
            _write_prompt_package(prompts_dir, include_metadata=True)
            _write_equivalent_espanso_package(package_dir, include_metadata=True)
            (package_dir / "_manifest.yml").write_text(
                _changed_manifest_text(), encoding="utf-8"
            )

            rc, stdout, _stderr = _run_cli(
                [
                    "roundtrip",
                    "espanso",
                    "--input",
                    str(package_dir),
                    "--prompts",
                    str(prompts_dir),
                ]
            )

            self.assertEqual(rc, 1)
            self.assertIn("Roundtrip semantic comparison failed.", stdout)
            self.assertIn("_manifest.yml", stdout)
            self.assertIn("Metadata asset differs", stdout)

    def test_roundtrip_accepts_formatting_only_yaml_differences(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            prompts_dir = base / "prompts"
            package_dir = base / "espanso"
            _write_prompt_package(prompts_dir, include_metadata=True)
            _write_equivalent_espanso_package(package_dir, include_metadata=True)
            (package_dir / "package.yml").write_text(
                """matches:
  - replace: >
      Beta body.
    trigger: ":beta"
  - replace: "Alpha body.\\n"
    trigger: ":alpha"
""",
                encoding="utf-8",
            )
            (package_dir / "_manifest.yml").write_text(
                """description: Sample description
tags: [ai, prompts]
author: Example Author
version: 1.0.0
title: Sample Package
name: sample
""",
                encoding="utf-8",
            )

            rc, stdout, stderr = _run_cli(
                [
                    "roundtrip",
                    "espanso",
                    "--input",
                    str(package_dir),
                    "--prompts",
                    str(prompts_dir),
                ]
            )

            self.assertEqual(rc, 0, stderr)
            self.assertIn("Roundtrip semantic comparison passed.", stdout)
            self.assertIn("Differences: 0", stdout)

    def test_roundtrip_reports_missing_expected_metadata_asset(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            prompts_dir = base / "prompts"
            package_dir = base / "espanso"
            _write_prompt_package(prompts_dir, include_metadata=True)
            _write_equivalent_espanso_package(package_dir, include_metadata=True)
            (package_dir / "LICENSE").unlink()

            rc, stdout, _stderr = _run_cli(
                [
                    "roundtrip",
                    "espanso",
                    "--input",
                    str(package_dir),
                    "--prompts",
                    str(prompts_dir),
                ]
            )

            self.assertEqual(rc, 1)
            self.assertIn("LICENSE", stdout)
            self.assertIn("Expected metadata asset is missing", stdout)

    def test_roundtrip_allows_generated_metadata_when_canonical_has_none(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            prompts_dir = base / "prompts"
            package_dir = base / "espanso"
            _write_prompt_package(prompts_dir, include_metadata=False)
            _write_equivalent_espanso_package(package_dir, include_metadata=True)

            rc, stdout, stderr = _run_cli(
                [
                    "roundtrip",
                    "espanso",
                    "--input",
                    str(package_dir),
                    "--prompts",
                    str(prompts_dir),
                ]
            )

            self.assertEqual(rc, 0, stderr)
            self.assertIn("Metadata assets compared: 0", stdout)
            self.assertIn("Differences: 0", stdout)

    def test_real_corpus_export_roundtrip_smoke(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        prompts_dir = repo_root / "prompts" / "taurcode"
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "taurcode"

            export_rc, _stdout, _stderr = _run_cli(
                [
                    "export",
                    "espanso",
                    "--prompts",
                    str(prompts_dir),
                    "--output",
                    str(output_dir),
                ]
            )
            self.assertEqual(export_rc, 0)

            rc, stdout, stderr = _run_cli(
                [
                    "roundtrip",
                    "espanso",
                    "--input",
                    str(output_dir),
                    "--prompts",
                    str(prompts_dir),
                ]
            )

            self.assertEqual(rc, 0, stderr)
            self.assertIn("Roundtrip semantic comparison passed.", stdout)
            self.assertIn("Differences: 0", stdout)


def _run_cli(args: list[str]) -> tuple[int, str, str]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        rc = cli.main(args)
    return rc, stdout.getvalue(), stderr.getvalue()


def _write_prompt_package(prompts_dir: Path, include_metadata: bool) -> None:
    prompts_dir.mkdir(parents=True)
    (prompts_dir / "alpha.md").write_text(
        """---
id: alpha
name: Alpha
description: Alpha prompt
keyword: ":alpha"
tags:
  - curated
---

Alpha body.
""",
        encoding="utf-8",
    )
    (prompts_dir / "beta.md").write_text(
        """---
id: beta
name: Beta
description: Beta prompt
keyword: ":beta"
---

Beta body.
""",
        encoding="utf-8",
    )
    if include_metadata:
        metadata_dir = prompts_dir / "espanso"
        metadata_dir.mkdir()
        _write_metadata_assets(metadata_dir)


def _write_equivalent_espanso_package(
    package_dir: Path, include_metadata: bool
) -> None:
    package_dir.mkdir(parents=True)
    (package_dir / "package.yml").write_text(
        """matches:
  - trigger: ":alpha"
    replace: |
      Alpha body.
  - trigger: ":beta"
    replace: |
      Beta body.
""",
        encoding="utf-8",
    )
    if include_metadata:
        _write_metadata_assets(package_dir)


def _write_metadata_assets(directory: Path) -> None:
    (directory / "_manifest.yml").write_text(_manifest_text(), encoding="utf-8")
    (directory / "README.md").write_text(
        "# Sample Package\n\nSample package README.\n", encoding="utf-8"
    )
    (directory / "LICENSE").write_text("Sample license.\n", encoding="utf-8")


def _manifest_text() -> str:
    return """name: sample
title: Sample Package
version: 1.0.0
description: Sample description
author: Example Author
tags:
  - ai
  - prompts
"""


def _changed_manifest_text() -> str:
    return """name: sample
title: Changed Package
version: 2.0.0
description: Sample description
author: Example Author
tags:
  - ai
  - prompts
"""


if __name__ == "__main__":
    unittest.main()
