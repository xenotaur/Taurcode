def normalize_final_newline(text: str) -> str:
    """Return text with exactly one trailing newline.

    Only the final newline count is normalized; other leading and trailing
    whitespace is preserved exactly.
    """
    return text.rstrip("\n") + "\n"
