import tempfile
import unittest
from pathlib import Path

from taurcode import prompt_loader


class TestPromptLoader(unittest.TestCase):
    def test_load_prompts_loads_scalar_metadata_and_normalized_body(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prompts_dir = Path(tmpdir)
            prompt_file = prompts_dir / "prompt.md"
            prompt_file.write_text(
                """---
id: scalar-prompt
name: Scalar Prompt
description: A prompt with scalar metadata
keyword: ":tc-scalar"
---

Prompt body.
""",
                encoding="utf-8",
            )

            prompts = prompt_loader.load_prompts(str(prompts_dir))

            self.assertEqual(len(prompts), 1)
            prompt = prompts[0]
            self.assertEqual(prompt.id, "scalar-prompt")
            self.assertEqual(prompt.name, "Scalar Prompt")
            self.assertEqual(prompt.description, "A prompt with scalar metadata")
            self.assertEqual(prompt.keyword, ":tc-scalar")
            self.assertEqual(prompt.body, "Prompt body.\n")

    def test_load_prompts_supports_yaml_quotes_comments_and_targets(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prompts_dir = Path(tmpdir)
            prompt_file = prompts_dir / "prompt.md"
            prompt_file.write_text(
                """---
id: quoted-prompt
name: "Quoted Prompt"
description: 'A prompt with YAML metadata comments'
# This comment should not become metadata.
keyword: ":tc-quoted" # Inline comment should be ignored.
targets:
  espanso:
    enabled: true
    package: taurcode
---

Prompt body.
""",
                encoding="utf-8",
            )

            prompts = prompt_loader.load_prompts(str(prompts_dir))

            self.assertEqual(len(prompts), 1)
            prompt = prompts[0]
            self.assertEqual(prompt.name, "Quoted Prompt")
            self.assertEqual(
                prompt.description,
                "A prompt with YAML metadata comments",
            )
            self.assertEqual(prompt.keyword, ":tc-quoted")
            self.assertEqual(
                prompt.targets,
                {"espanso": {"enabled": True, "package": "taurcode"}},
            )

    def test_load_prompts_raises_on_malformed_yaml_frontmatter(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prompts_dir = Path(tmpdir)
            prompt_file = prompts_dir / "prompt.md"
            prompt_file.write_text(
                """---
id: [unterminated
name: Broken Prompt
---

Prompt body.
""",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "Malformed YAML frontmatter"):
                prompt_loader.load_prompts(str(prompts_dir))

    def test_repository_no_longer_contains_frontmatter_shim(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]

        self.assertFalse((repo_root / "src" / "frontmatter" / "__init__.py").exists())


class TestExtractPromptBody(unittest.TestCase):
    def test_no_frontmatter_returns_text_unchanged(self) -> None:
        self.assertEqual(
            prompt_loader.extract_prompt_body("no frontmatter here"),
            "no frontmatter here",
        )

    def test_empty_string_returns_empty_string(self) -> None:
        self.assertEqual(prompt_loader.extract_prompt_body(""), "")

    def test_bare_delimiter_with_no_body_returns_unchanged(self) -> None:
        self.assertEqual(prompt_loader.extract_prompt_body("---"), "---")

    def test_unterminated_frontmatter_returns_text_unchanged(self) -> None:
        text = "---\nfoo: bar\nno closing delimiter"
        self.assertEqual(prompt_loader.extract_prompt_body(text), text)

    def test_delimiter_only_frontmatter_returns_empty_body(self) -> None:
        self.assertEqual(prompt_loader.extract_prompt_body("---\n---\n"), "")
        self.assertEqual(prompt_loader.extract_prompt_body("---\n---"), "")

    def test_frontmatter_with_no_trailing_newline_returns_empty_body(self) -> None:
        self.assertEqual(prompt_loader.extract_prompt_body("---\nfoo: bar\n---"), "")

    def test_body_leading_blank_line_is_stripped_once(self) -> None:
        text = "---\nfoo: bar\n---\n\nBody text.\n"
        self.assertEqual(prompt_loader.extract_prompt_body(text), "Body text.\n")

    def test_body_containing_delimiter_like_text_is_preserved(self) -> None:
        text = "---\nfoo: bar\n---\nbody\n---\nmore---stuff"
        self.assertEqual(
            prompt_loader.extract_prompt_body(text), "body\n---\nmore---stuff"
        )

    def test_crlf_line_endings_are_normalized(self) -> None:
        text = "---\r\nfoo: bar\r\n---\r\nbody\r\n"
        self.assertEqual(prompt_loader.extract_prompt_body(text), "body\n")


if __name__ == "__main__":
    unittest.main()
