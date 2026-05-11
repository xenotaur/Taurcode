import unittest

from taurcode import text_normalization


class TestTextNormalization(unittest.TestCase):
    def test_no_final_newline_becomes_one_final_newline(self) -> None:
        self.assertEqual(
            text_normalization.normalize_final_newline("body"),
            "body\n",
        )

    def test_multiple_final_newlines_become_one_final_newline(self) -> None:
        self.assertEqual(
            text_normalization.normalize_final_newline("body\n\n\n"),
            "body\n",
        )

    def test_crlf_final_newlines_become_one_lf_final_newline(self) -> None:
        self.assertEqual(
            text_normalization.normalize_final_newline("body\r\n\r\n"),
            "body\n",
        )

    def test_cr_final_newlines_become_one_lf_final_newline(self) -> None:
        self.assertEqual(
            text_normalization.normalize_final_newline("body\r\r"),
            "body\n",
        )

    def test_internal_blank_lines_and_other_whitespace_are_preserved(self) -> None:
        self.assertEqual(
            text_normalization.normalize_final_newline("  body\n\nnext  \n\n"),
            "  body\n\nnext  \n",
        )


if __name__ == "__main__":
    unittest.main()
