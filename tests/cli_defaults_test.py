import unittest

from taurcode import cli


class TestCliDefaults(unittest.TestCase):
    def test_validate_uses_canonical_prompt_corpus_by_default(self) -> None:
        args = cli.build_parser().parse_args(["validate"])

        self.assertEqual(args.prompts, cli.CANONICAL_PROMPTS_DIR)

    def test_export_uses_canonical_prompts_and_generated_output_by_default(
        self,
    ) -> None:
        args = cli.build_parser().parse_args(["export", "espanso"])

        self.assertEqual(args.prompts, cli.CANONICAL_PROMPTS_DIR)
        self.assertEqual(args.output, cli.ESPANSO_OUTPUT_DIR)

    def test_format_uses_canonical_prompt_corpus_by_default(self) -> None:
        args = cli.build_parser().parse_args(["format", "prompts"])

        self.assertEqual(args.prompts, cli.CANONICAL_PROMPTS_DIR)

    def test_import_uses_staging_directory_by_default(self) -> None:
        args = cli.build_parser().parse_args(
            ["import", "espanso", "--input", "espanso/package/package.yml"]
        )

        self.assertEqual(args.output, cli.IMPORT_STAGING_DIR)


if __name__ == "__main__":
    unittest.main()
