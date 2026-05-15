import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from taurcode.cli import main


class TestEspansoImport(unittest.TestCase):
    def test_import_supported_match_to_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source = base / "package.yml"
            output = base / "prompts"
            source.write_text(
                """matches:\n  - trigger: \":tc-example\"\n    replace: |\n      Hello world\n""",
                encoding="utf-8",
            )

            rc = main(
                ["import", "espanso", "--input", str(source), "--output", str(output)]
            )
            self.assertEqual(rc, 0)

            imported = output / "tc-example.md"
            self.assertTrue(imported.exists())
            self.assertEqual(
                imported.read_text(encoding="utf-8"),
                """---\nid: tc-example\nname: Tc Example\ndescription: Imported from Espanso\nkeyword: \":tc-example\"\n---\n\nHello world\n""",
            )

    def test_import_normalizes_prompt_with_no_final_newline_to_one(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source = base / "package.yml"
            output = base / "prompts"
            source.write_text(
                """matches:
  - trigger: ":no-final-newline"
    replace: |-
      Body without source final newline
""",
                encoding="utf-8",
            )

            rc = main(
                ["import", "espanso", "--input", str(source), "--output", str(output)]
            )
            self.assertEqual(rc, 0)
            imported = (output / "no-final-newline.md").read_bytes()
            self.assertTrue(imported.endswith(b"Body without source final newline\n"))
            self.assertFalse(imported.endswith(b"\n\n"))

    def test_import_normalizes_multiple_final_newlines_to_one(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source = base / "package.yml"
            output = base / "prompts"
            source.write_text(
                """matches:
  - trigger: ":many-final-newlines"
    replace: |+
      Body with extra source final newlines


""",
                encoding="utf-8",
            )

            rc = main(
                ["import", "espanso", "--input", str(source), "--output", str(output)]
            )
            self.assertEqual(rc, 0)
            imported = (output / "many-final-newlines.md").read_bytes()
            self.assertTrue(
                imported.endswith(b"Body with extra source final newlines\n")
            )
            self.assertFalse(imported.endswith(b"\n\n"))

    def test_import_unsupported_match_to_raw_yaml(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source = base / "package.yml"
            output = base / "prompts"
            source.write_text(
                """matches:\n  - trigger: \":tc-form\"\n    replace: \"Hi {{name}}\"\n    vars:\n      - name: name\n""",
                encoding="utf-8",
            )

            rc = main(
                ["import", "espanso", "--input", str(source), "--output", str(output)]
            )
            self.assertEqual(rc, 0)

            raw_file = output / "imported_raw" / "match-1.yml"
            self.assertTrue(raw_file.exists())
            self.assertEqual(
                raw_file.read_text(encoding="utf-8"),
                """  - trigger: \":tc-form\"
    replace: \"Hi {{name}}\"
    vars:
      - name: name
""",
            )

    def test_import_mixed_and_duplicate_trigger(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source = base / "package.yml"
            output = base / "prompts"
            source.write_text(
                """matches:\n  - trigger: \":tc-dupe\"\n    replace: first\n  - trigger: \":tc-dupe\"\n    replace: \"\"\n  - trigger: \":tc-complex\"\n    replace: thing\n    shell: echo hi\n""",
                encoding="utf-8",
            )

            rc = main(
                ["import", "espanso", "--input", str(source), "--output", str(output)]
            )
            self.assertEqual(rc, 0)

            self.assertTrue((output / "tc-dupe.md").exists())
            self.assertTrue((output / "tc-dupe-2.md").exists())
            self.assertEqual(
                (output / "tc-dupe-2.md").read_text(encoding="utf-8").split("\n")[-1],
                "",
            )
            self.assertTrue((output / "imported_raw" / "match-1.yml").exists())

    def test_import_preserves_supported_metadata_assets(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source_dir = base / "espanso-package"
            source_dir.mkdir()
            output = base / "prompts"
            manifest = b'name: sample\n# keep comment\ntitle: "Sample Package"\n'
            readme = b"# Sample Package\n\nKeep this README exactly.\n"
            license_text = b"Sample license text.\n\nAll rights reserved.\n"
            (source_dir / "package.yml").write_text(
                """matches:
  - trigger: ":tc-meta"
    replace: |
      Metadata body
""",
                encoding="utf-8",
            )
            (source_dir / "_manifest.yml").write_bytes(manifest)
            (source_dir / "README.md").write_bytes(readme)
            (source_dir / "LICENSE").write_bytes(license_text)

            rc = main(
                [
                    "import",
                    "espanso",
                    "--input",
                    str(source_dir),
                    "--output",
                    str(output),
                ]
            )
            self.assertEqual(rc, 0)

            self.assertTrue((output / "tc-meta.md").exists())
            metadata_dir = output / "espanso"
            self.assertEqual((metadata_dir / "_manifest.yml").read_bytes(), manifest)
            self.assertEqual((metadata_dir / "README.md").read_bytes(), readme)
            self.assertEqual((metadata_dir / "LICENSE").read_bytes(), license_text)

    def test_import_preserves_license_without_final_newline_exactly(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source_dir = base / "espanso-package"
            source_dir.mkdir()
            output = base / "prompts"
            license_text = b"Sample license text.\n\nAll rights reserved."
            (source_dir / "package.yml").write_text(
                """matches:
  - trigger: ":tc-license"
    replace: Body
""",
                encoding="utf-8",
            )
            (source_dir / "LICENSE").write_bytes(license_text)

            rc = main(
                [
                    "import",
                    "espanso",
                    "--input",
                    str(source_dir),
                    "--output",
                    str(output),
                ]
            )
            self.assertEqual(rc, 0)
            self.assertEqual(
                (output / "espanso" / "LICENSE").read_bytes(), license_text
            )

    def test_import_does_not_create_metadata_dir_without_supported_assets(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source_dir = base / "espanso-package"
            source_dir.mkdir()
            output = base / "prompts"
            (source_dir / "package.yml").write_text(
                """matches:
  - trigger: ":tc-plain"
    replace: plain
""",
                encoding="utf-8",
            )

            rc = main(
                [
                    "import",
                    "espanso",
                    "--input",
                    str(source_dir),
                    "--output",
                    str(output),
                ]
            )
            self.assertEqual(rc, 0)
            self.assertFalse((output / "espanso").exists())

    def test_import_missing_metadata_reports_warnings_and_continues(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source_dir = base / "espanso-package"
            source_dir.mkdir()
            output = base / "prompts"
            (source_dir / "package.yml").write_text(
                """matches:
  - trigger: ":tc-missing-meta"
    replace: Body
""",
                encoding="utf-8",
            )

            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                rc = main(
                    [
                        "import",
                        "espanso",
                        "--input",
                        str(source_dir),
                        "--output",
                        str(output),
                    ]
                )
            self.assertEqual(rc, 0)
            self.assertTrue((output / "tc-missing-meta.md").exists())
            self.assertFalse((output / "espanso").exists())
            self.assertIn("metadata asset missing", stderr.getvalue())

    def test_package_yml_input_skips_metadata_asset_import(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source_dir = base / "espanso-package"
            source_dir.mkdir()
            output = base / "prompts"
            package_yml = source_dir / "package.yml"
            package_yml.write_text(
                """matches:
  - trigger: ":tc-package-file"
    replace: Body
""",
                encoding="utf-8",
            )
            (source_dir / "README.md").write_text(
                "# Sibling README should be skipped\n", encoding="utf-8"
            )

            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                rc = main(
                    [
                        "import",
                        "espanso",
                        "--input",
                        str(package_yml),
                        "--output",
                        str(output),
                    ]
                )
            self.assertEqual(rc, 0)
            self.assertTrue((output / "tc-package-file.md").exists())
            self.assertFalse((output / "espanso").exists())
            self.assertIn("metadata asset import skipped", stderr.getvalue())

    def test_import_invalid_yaml_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source = base / "package.yml"
            source.write_text("matches:\n  - invalid", encoding="utf-8")

            rc = main(
                [
                    "import",
                    "espanso",
                    "--input",
                    str(source),
                    "--output",
                    str(base / "prompts"),
                ]
            )
            self.assertEqual(rc, 1)

    def test_import_folded_block_scalar(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source = base / "package.yml"
            output = base / "prompts"
            source.write_text(
                """matches:
  - trigger: ":folded"
    replace: >
      This is folded
      onto one paragraph.

      This is a second paragraph.
""",
                encoding="utf-8",
            )

            rc = main(
                ["import", "espanso", "--input", str(source), "--output", str(output)]
            )
            self.assertEqual(rc, 0)
            imported = (output / "folded.md").read_text(encoding="utf-8")
            self.assertTrue(
                imported.endswith(
                    "This is folded onto one paragraph.\nThis is a second paragraph.\n"
                )
            )

    def test_import_literal_block_scalar_with_blank_lines(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source = base / "package.yml"
            output = base / "prompts"
            source.write_text(
                """matches:
  - trigger: ":address"
    replace: |
      Addressing Code Review Feedback
      I got some comments on the associated PR. For each comment, ask:

      - Does this comment refer to issues which are still present?
      - Does this comment raise valid issues?

      PR:
      ----Comments Follow—————————————————————
""",
                encoding="utf-8",
            )
            rc = main(
                ["import", "espanso", "--input", str(source), "--output", str(output)]
            )
            self.assertEqual(rc, 0)
            imported = (output / "address.md").read_text(encoding="utf-8")
            self.assertIn(
                "Addressing Code Review Feedback\n"
                "I got some comments on the associated PR. For each comment, ask:\n\n"
                "- Does this comment refer to issues which are still present?\n"
                "- Does this comment raise valid issues?\n\n"
                "PR:\n"
                "----Comments Follow—————————————————————\n",
                imported,
            )

    def test_import_unsupported_block_scalar_preserves_full_raw_yaml(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source = base / "package.yml"
            output = base / "prompts"
            source.write_text(
                """matches:
  - trigger: ":complex"
    replace: |
      paragraph one

      paragraph two
    vars:
      - name: name
""",
                encoding="utf-8",
            )
            rc = main(
                ["import", "espanso", "--input", str(source), "--output", str(output)]
            )
            self.assertEqual(rc, 0)
            self.assertFalse((output / "complex.md").exists())
            raw_file = output / "imported_raw" / "match-1.yml"
            self.assertTrue(raw_file.exists())
            self.assertIn(
                "    replace: |\n      paragraph one\n\n      paragraph two\n",
                raw_file.read_text(encoding="utf-8"),
            )

    def test_import_raw_fallback_with_matches_header_comment(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source = base / "package.yml"
            output = base / "prompts"
            source.write_text(
                """matches:  # inline comment
  - trigger: ":complex"
    replace: |
      keep me

      too
    vars:
      - name: name
""",
                encoding="utf-8",
            )
            rc = main(
                ["import", "espanso", "--input", str(source), "--output", str(output)]
            )
            self.assertEqual(rc, 0)
            raw_file = output / "imported_raw" / "match-1.yml"
            self.assertTrue(raw_file.exists())
            self.assertIn("      keep me\n\n      too\n", raw_file.read_text("utf-8"))

    def test_import_raw_fallback_ignores_top_level_comments_between_matches(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source = base / "package.yml"
            output = base / "prompts"
            source.write_text(
                """matches:
  - trigger: ":one"
    replace: ok
# top-level comment between matches and global vars
  - trigger: ":complex"
    replace: |
      first

      second
    vars:
      - name: name
""",
                encoding="utf-8",
            )
            rc = main(
                ["import", "espanso", "--input", str(source), "--output", str(output)]
            )
            self.assertEqual(rc, 0)
            self.assertTrue((output / "one.md").exists())
            raw_file = output / "imported_raw" / "match-1.yml"
            self.assertTrue(raw_file.exists())
            self.assertIn("      first\n\n      second\n", raw_file.read_text("utf-8"))

    def test_import_ignores_non_match_lists_after_matches(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source = base / "package.yml"
            output = base / "prompts"
            source.write_text(
                """matches:
  - trigger: ":tc-one"
    replace: ok
global_vars:
  - name: test
    type: shell
    params:
      cmd: echo nope
""",
                encoding="utf-8",
            )
            rc = main(
                ["import", "espanso", "--input", str(source), "--output", str(output)]
            )
            self.assertEqual(rc, 0)
            self.assertTrue((output / "tc-one.md").exists())
            self.assertFalse((output / "tc-one-2.md").exists())

    def test_import_seeds_existing_prompt_ids_and_raw_indices(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source = base / "package.yml"
            output = base / "prompts"
            output.mkdir(parents=True)
            (output / "tc-example.md").write_text("existing", encoding="utf-8")
            raw_dir = output / "imported_raw"
            raw_dir.mkdir(parents=True)
            (raw_dir / "match-1.yml").write_text("old", encoding="utf-8")
            source.write_text(
                """matches:
  - trigger: ":tc-example"
    replace: new
  - trigger: ":tc-complex"
    replace: thing
    shell: echo hi
""",
                encoding="utf-8",
            )
            rc = main(
                ["import", "espanso", "--input", str(source), "--output", str(output)]
            )
            self.assertEqual(rc, 0)
            self.assertTrue((output / "tc-example-2.md").exists())
            self.assertTrue((raw_dir / "match-2.yml").exists())

    def test_merge_preserves_curated_metadata_and_updates_body(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source = base / "package.yml"
            output = base / "prompts"
            output.mkdir()
            (output / "debug.md").write_text(
                """---
id: debug
name: Debug Issue Carefully
description: Debug an Issue
keyword: ":debug"
owner: docs-team
---

Old body
""",
                encoding="utf-8",
            )
            source.write_text(
                """matches:
  - trigger: ":debug"
    replace: |
      New Espanso body
""",
                encoding="utf-8",
            )

            rc = main(
                [
                    "import",
                    "espanso",
                    "--input",
                    str(source),
                    "--output",
                    str(output),
                    "--merge",
                ]
            )
            self.assertEqual(rc, 0)

            merged = (output / "debug.md").read_text(encoding="utf-8")
            self.assertIn("name: Debug Issue Carefully\n", merged)
            self.assertIn("description: Debug an Issue\n", merged)
            self.assertIn("owner: docs-team\n", merged)
            self.assertIn('keyword: ":debug"\n', merged)
            self.assertTrue(merged.endswith("New Espanso body\n"))
            self.assertNotIn("Imported from Espanso", merged)

    def test_merge_preserves_frontmatter_text_when_only_body_changes(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source = base / "package.yml"
            output = base / "prompts"
            output.mkdir()
            prompt = output / "debug.md"
            frontmatter = (
                "---\n"
                "# keep leading comment\n"
                "owner: docs-team  # keep inline comment\n"
                "id: debug\n"
                "name: Debug Issue Carefully\n"
                "description: This intentionally long description stays on one line so merge import does not create cosmetic wrapping churn in human-authored prompt packages.\n"
                'keyword: ":debug"\n'
                "---\n"
            )
            prompt.write_text(frontmatter + "\nOld body\n", encoding="utf-8")
            source.write_text(
                """matches:
  - trigger: ":debug"
    replace: |
      New Espanso body
""",
                encoding="utf-8",
            )

            rc = main(
                [
                    "import",
                    "espanso",
                    "--input",
                    str(source),
                    "--output",
                    str(output),
                    "--merge",
                ]
            )
            self.assertEqual(rc, 0)

            merged = prompt.read_text(encoding="utf-8")
            self.assertEqual(
                merged,
                frontmatter + "\nNew Espanso body\n",
            )

    def test_merge_preserves_yaml_safe_metadata_scalars(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source = base / "package.yml"
            output = base / "prompts"
            output.mkdir()
            prompt = output / "safe.md"
            prompt.write_text(
                """---
id: safe
name: Safe Metadata
description: "desc # keep"
keyword: ":safe"
enabled: true
count: 2
tags:
  - review
---

Old body
""",
                encoding="utf-8",
            )
            source.write_text(
                """matches:
  - trigger: ":safe"
    replace: Updated once
""",
                encoding="utf-8",
            )

            rc = main(
                [
                    "import",
                    "espanso",
                    "--input",
                    str(source),
                    "--output",
                    str(output),
                    "--merge",
                ]
            )
            self.assertEqual(rc, 0)
            merged = prompt.read_text(encoding="utf-8")
            self.assertNotIn("\n...\n", merged)
            self.assertIn('description: "desc # keep"\n', merged)
            self.assertIn("enabled: true\n", merged)
            self.assertIn("count: 2\n", merged)
            self.assertIn("tags:\n  - review\n", merged)

            source.write_text(
                """matches:
  - trigger: ":safe"
    replace: Updated twice
""",
                encoding="utf-8",
            )
            rc = main(
                [
                    "import",
                    "espanso",
                    "--input",
                    str(source),
                    "--output",
                    str(output),
                    "--merge",
                ]
            )
            self.assertEqual(rc, 0)
            merged_again = prompt.read_text(encoding="utf-8")
            self.assertIn('description: "desc # keep"\n', merged_again)
            self.assertIn("enabled: true\n", merged_again)
            self.assertTrue(merged_again.endswith("Updated twice\n"))

    def test_merge_updates_keyword_when_matched_by_filename(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source = base / "package.yml"
            output = base / "prompts"
            output.mkdir()
            (output / "rename-me.md").write_text(
                """---
id: rename-me
name: Rename Me
description: Keep me
keyword: ":old-trigger"
---

Old body
""",
                encoding="utf-8",
            )
            source.write_text(
                """matches:
  - trigger: ":rename-me"
    replace: New body
""",
                encoding="utf-8",
            )

            rc = main(
                [
                    "import",
                    "espanso",
                    "--input",
                    str(source),
                    "--output",
                    str(output),
                    "--merge",
                ]
            )
            self.assertEqual(rc, 0)
            merged = (output / "rename-me.md").read_text(encoding="utf-8")
            self.assertIn('keyword: ":rename-me"\n', merged)
            self.assertIn("description: Keep me\n", merged)
            self.assertTrue(merged.endswith("New body\n"))

    def test_merge_keyword_edit_preserves_inline_comment_and_spacing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source = base / "package.yml"
            output = base / "prompts"
            output.mkdir()
            prompt = output / "rename-me.md"
            prompt.write_text(
                """---
id: rename-me
name: Rename Me
description: Keep me
keyword:    ":old-trigger"  # keep keyword comment
---

Old body
""",
                encoding="utf-8",
            )
            source.write_text(
                """matches:
  - trigger: ":rename-me"
    replace: New body
""",
                encoding="utf-8",
            )

            rc = main(
                [
                    "import",
                    "espanso",
                    "--input",
                    str(source),
                    "--output",
                    str(output),
                    "--merge",
                ]
            )
            self.assertEqual(rc, 0)
            merged = prompt.read_text(encoding="utf-8")
            self.assertIn('keyword:    ":rename-me"  # keep keyword comment\n', merged)
            self.assertTrue(merged.endswith("New body\n"))

    def test_merge_keyword_edit_falls_back_for_block_scalar_keyword(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source = base / "package.yml"
            output = base / "prompts"
            output.mkdir()
            prompt = output / "rename-me.md"
            prompt.write_text(
                """---
id: rename-me
name: Rename Me
description: Keep me
keyword: >-
  :old-trigger
---

Old body
""",
                encoding="utf-8",
            )
            source.write_text(
                """matches:
  - trigger: ":rename-me"
    replace: New body
""",
                encoding="utf-8",
            )

            rc = main(
                [
                    "import",
                    "espanso",
                    "--input",
                    str(source),
                    "--output",
                    str(output),
                    "--merge",
                ]
            )
            self.assertEqual(rc, 0)
            merged = prompt.read_text(encoding="utf-8")
            self.assertIn("keyword: :rename-me\n", merged)
            self.assertNotIn("  :old-trigger", merged)
            self.assertTrue(merged.endswith("New body\n"))

    def test_merge_keyword_edit_uses_json_string_escaping(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source = base / "package.yml"
            output = base / "prompts"
            output.mkdir()
            prompt = output / "rename-me.md"
            prompt.write_text(
                """---
id: rename-me
name: Rename Me
description: Keep me
keyword: ":old-trigger"
---

Old body
""",
                encoding="utf-8",
            )
            source.write_text(
                'matches:\n  - trigger: ":rename\\tme"\n    replace: New body\n',
                encoding="utf-8",
            )

            rc = main(
                [
                    "import",
                    "espanso",
                    "--input",
                    str(source),
                    "--output",
                    str(output),
                    "--merge",
                ]
            )
            self.assertEqual(rc, 0)
            merged = prompt.read_text(encoding="utf-8")
            self.assertIn('keyword: ":rename\\tme"\n', merged)
            self.assertNotIn('keyword: ":rename\tme"\n', merged)
            self.assertTrue(merged.endswith("New body\n"))

    def test_merge_creates_new_prompt_for_new_match(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source = base / "package.yml"
            output = base / "prompts"
            output.mkdir()
            source.write_text(
                """matches:
  - trigger: ":new-prompt"
    replace: Created body
""",
                encoding="utf-8",
            )

            rc = main(
                [
                    "import",
                    "espanso",
                    "--input",
                    str(source),
                    "--output",
                    str(output),
                    "--merge",
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue((output / "new-prompt.md").exists())

    def test_merge_warns_and_keeps_orphan_prompt(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source = base / "package.yml"
            output = base / "prompts"
            output.mkdir()
            orphan = output / "orphan.md"
            orphan.write_text(
                """---
id: orphan
name: Orphan
description: Keep orphan
keyword: ":orphan"
---

Do not delete
""",
                encoding="utf-8",
            )
            source.write_text(
                """matches:
  - trigger: ":new-prompt"
    replace: Created body
""",
                encoding="utf-8",
            )

            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                rc = main(
                    [
                        "import",
                        "espanso",
                        "--input",
                        str(source),
                        "--output",
                        str(output),
                        "--merge",
                    ]
                )
            self.assertEqual(rc, 0)
            self.assertTrue(orphan.exists())
            self.assertIn("Orphan prompt", stderr.getvalue())
            self.assertIn(str(orphan), stderr.getvalue())

    def test_merge_fails_on_ambiguous_duplicate_keyword_matches(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source = base / "package.yml"
            output = base / "prompts"
            output.mkdir()
            for filename in ("one.md", "two.md"):
                (output / filename).write_text(
                    """---
id: {0}
name: Duplicate
description: Duplicate
keyword: ":dupe"
---

Body
""".format(filename.removesuffix(".md")),
                    encoding="utf-8",
                )
            source.write_text(
                """matches:
  - trigger: ":dupe"
    replace: New
""",
                encoding="utf-8",
            )

            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                rc = main(
                    [
                        "import",
                        "espanso",
                        "--input",
                        str(source),
                        "--output",
                        str(output),
                        "--merge",
                    ]
                )
            self.assertEqual(rc, 1)
            self.assertIn("Ambiguous Espanso import match", stderr.getvalue())
            self.assertIn("one.md", stderr.getvalue())
            self.assertIn("two.md", stderr.getvalue())

    def test_merge_fails_when_multiple_espanso_matches_target_one_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source = base / "package.yml"
            output = base / "prompts"
            output.mkdir()
            (output / "dupe.md").write_text(
                """---
id: dupe
name: Duplicate
description: Duplicate
keyword: ":dupe"
---

Body
""",
                encoding="utf-8",
            )
            source.write_text(
                """matches:
  - trigger: ":dupe"
    replace: First
  - trigger: ":dupe"
    replace: Second
""",
                encoding="utf-8",
            )

            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                rc = main(
                    [
                        "import",
                        "espanso",
                        "--input",
                        str(source),
                        "--output",
                        str(output),
                        "--merge",
                    ]
                )
            self.assertEqual(rc, 1)
            self.assertIn("multiple Espanso matches map", stderr.getvalue())
            self.assertIn("dupe.md", stderr.getvalue())

    def test_merge_ignores_espanso_metadata_readme(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source = base / "package.yml"
            output = base / "prompts"
            metadata_dir = output / "espanso"
            metadata_dir.mkdir(parents=True)
            (metadata_dir / "README.md").write_text(
                "# Package metadata\n", encoding="utf-8"
            )
            source.write_text(
                """matches:
  - trigger: ":readme"
    replace: README body
""",
                encoding="utf-8",
            )

            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                rc = main(
                    [
                        "import",
                        "espanso",
                        "--input",
                        str(source),
                        "--output",
                        str(output),
                        "--merge",
                    ]
                )
            self.assertEqual(rc, 0)
            self.assertEqual(stderr.getvalue(), "")
            self.assertEqual(
                (metadata_dir / "README.md").read_text(encoding="utf-8"),
                "# Package metadata\n",
            )
            self.assertTrue((output / "readme.md").exists())

    def test_merge_into_empty_output_uses_fresh_import_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source = base / "package.yml"
            output = base / "prompts"
            source.write_text(
                """matches:
  - trigger: ":fresh"
    replace: Fresh body
""",
                encoding="utf-8",
            )

            rc = main(
                [
                    "import",
                    "espanso",
                    "--input",
                    str(source),
                    "--output",
                    str(output),
                    "--merge",
                ]
            )
            self.assertEqual(rc, 0)
            self.assertEqual(
                (output / "fresh.md").read_text(encoding="utf-8"),
                """---
id: fresh
name: Fresh
description: Imported from Espanso
keyword: ":fresh"
---

Fresh body
""",
            )


if __name__ == "__main__":
    unittest.main()
