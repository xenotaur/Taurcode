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


if __name__ == "__main__":
    unittest.main()
