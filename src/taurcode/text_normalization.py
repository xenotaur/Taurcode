def normalize_final_newline(text: str) -> str:
    """Return text with exactly one trailing newline.

    Final CRLF, LF, and CR sequences are treated as newline characters;
    other leading and trailing whitespace is preserved exactly.
    """
    return text.rstrip("\r\n") + "\n"
