import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from taurcode import cli


class TestCliShow(unittest.TestCase):
    def test_show_single_corpus_lookup(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prompts_dir = Path(tmpdir) / "prompts"
            _write_prompt(prompts_dir, "alpha", ":alpha", "Alpha body.\n")

            rc, stdout, stderr = _run_cli(
                ["show", ":alpha", "--prompts", str(prompts_dir)]
            )

            self.assertEqual(rc, 0, stderr)
            self.assertEqual(stdout, "Alpha body.\n")

    def test_show_default_searches_every_canonical_corpus(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            first_dir = base / "prompts" / "taurcode"
            second_dir = base / "prompts" / "lrh"
            _write_prompt(first_dir, "alpha", ":alpha", "Alpha body.\n")
            _write_prompt(second_dir, "beta", ":beta", "Beta body.\n")

            with _patched_canonical_dirs(str(first_dir), str(second_dir)):
                rc, stdout, stderr = _run_cli(["show", ":beta"])

            self.assertEqual(rc, 0, stderr)
            self.assertEqual(stdout, "Beta body.\n")

    def test_show_explicit_all_searches_every_canonical_corpus(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            first_dir = base / "prompts" / "taurcode"
            second_dir = base / "prompts" / "lrh"
            _write_prompt(first_dir, "alpha", ":alpha", "Alpha body.\n")
            _write_prompt(second_dir, "beta", ":beta", "Beta body.\n")

            with _patched_canonical_dirs(str(first_dir), str(second_dir)):
                rc, stdout, stderr = _run_cli(["show", ":beta", "--prompts", "all"])

            self.assertEqual(rc, 0, stderr)
            self.assertEqual(stdout, "Beta body.\n")

    def test_show_not_found_errors_nonzero(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prompts_dir = Path(tmpdir) / "prompts"
            _write_prompt(prompts_dir, "alpha", ":alpha", "Alpha body.\n")

            rc, stdout, stderr = _run_cli(
                ["show", ":missing", "--prompts", str(prompts_dir)]
            )

            self.assertEqual(rc, 1)
            self.assertEqual(stdout, "")
            self.assertIn(":missing", stderr)

    def test_show_ambiguous_match_lists_corpora_and_errors_nonzero(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            first_dir = base / "prompts" / "taurcode"
            second_dir = base / "prompts" / "lrh"
            _write_prompt(first_dir, "dup", ":dup", "First body.\n")
            _write_prompt(second_dir, "dup", ":dup", "Second body.\n")

            with _patched_canonical_dirs(str(first_dir), str(second_dir)):
                rc, stdout, stderr = _run_cli(["show", ":dup"])

            self.assertEqual(rc, 1)
            self.assertEqual(stdout, "")
            self.assertIn(str(first_dir), stderr)
            self.assertIn(str(second_dir), stderr)

    def test_show_all_does_not_treat_all_as_a_literal_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            first_dir = base / "prompts" / "taurcode"
            _write_prompt(first_dir, "alpha", ":alpha", "Alpha body.\n")

            with _patched_canonical_dirs(str(first_dir)):
                rc, stdout, stderr = _run_cli(["show", ":alpha", "--prompts", "all"])

            self.assertEqual(rc, 0, stderr)
            self.assertEqual(stdout, "Alpha body.\n")


@contextlib.contextmanager
def _patched_canonical_dirs(*dirs: str):
    original = cli.CANONICAL_PROMPT_DIRS
    cli.CANONICAL_PROMPT_DIRS = tuple(dirs)
    try:
        yield
    finally:
        cli.CANONICAL_PROMPT_DIRS = original


def _write_prompt(prompts_dir: Path, stem: str, keyword: str, body: str) -> None:
    prompts_dir.mkdir(parents=True, exist_ok=True)
    (prompts_dir / f"{stem}.md").write_text(
        f"""---
id: {stem}
name: {stem.title()}
description: {stem.title()} prompt
keyword: "{keyword}"
---

{body}""",
        encoding="utf-8",
    )


def _run_cli(args: list[str]) -> tuple[int, str, str]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        rc = cli.main(args)
    return rc, stdout.getvalue(), stderr.getvalue()


if __name__ == "__main__":
    unittest.main()
