import dataclasses
import re
from pathlib import Path

from taurcode import text_normalization

_RESERVED_PROMPT_DIRS = {"espanso"}
_KEYWORD_FORMAT_LINE_RE = re.compile(
    r"^(?P<prefix>keyword\s*:\s*)"
    r"(?P<value>[^#\r\n]*?)"
    r"(?P<space>\s*)"
    r"(?P<comment>#.*)?"
    r"(?P<newline>\r?\n?)$"
)


@dataclasses.dataclass(frozen=True)
class FormatResult:
    changed_files: list[Path]

    def has_changes(self) -> bool:
        return bool(self.changed_files)


def format_prompt_document(text: str) -> str:
    """Apply safe, deterministic formatting to one prompt Markdown document.

    The formatter intentionally avoids a generic YAML load/dump cycle. It only
    quotes a simple frontmatter ``keyword`` value when present and normalizes the
    document to exactly one final newline.
    """
    return text_normalization.normalize_final_newline(_quote_keyword(text))


def format_prompt_package(prompt_dir: str | Path, check: bool = False) -> FormatResult:
    directory = Path(prompt_dir)
    if not directory.exists():
        raise ValueError(f"Prompt package directory does not exist: {directory}")
    if not directory.is_dir():
        raise ValueError(f"Prompt package path is not a directory: {directory}")

    changed_files: list[Path] = []

    for prompt_file in _iter_prompt_files(directory):
        original_text = prompt_file.read_text(encoding="utf-8")
        formatted_text = format_prompt_document(original_text)
        if formatted_text == original_text:
            continue
        changed_files.append(prompt_file)
        if not check:
            prompt_file.write_text(formatted_text, encoding="utf-8")

    return FormatResult(changed_files=changed_files)


def _iter_prompt_files(directory: Path) -> list[Path]:
    prompt_files: list[Path] = []
    for prompt_file in sorted(directory.rglob("*.md")):
        if not prompt_file.is_file():
            continue
        if _is_reserved_prompt_file(prompt_file, directory):
            continue
        prompt_files.append(prompt_file)
    return prompt_files


def _is_reserved_prompt_file(prompt_file: Path, directory: Path) -> bool:
    relative_parts = prompt_file.relative_to(directory).parts
    return bool(relative_parts and relative_parts[0] in _RESERVED_PROMPT_DIRS)


def _quote_keyword(text: str) -> str:
    lines = text.splitlines(keepends=True)
    if not lines or _line_content(lines[0]) != "---":
        return text

    closing_index = _frontmatter_closing_index(lines)
    if closing_index is None:
        return text

    formatted_lines = list(lines)
    for index in range(1, closing_index):
        formatted_lines[index] = _format_keyword_line(formatted_lines[index])
    return "".join(formatted_lines)


def _frontmatter_closing_index(lines: list[str]) -> int | None:
    for index in range(1, len(lines)):
        if _line_content(lines[index]) == "---":
            return index
    return None


def _line_content(line: str) -> str:
    return line.removesuffix("\n").removesuffix("\r")


def _format_keyword_line(line: str) -> str:
    match = _KEYWORD_FORMAT_LINE_RE.match(line)
    if match is None:
        return line

    raw_value = match.group("value")
    value = raw_value.strip()
    if not value or _value_is_quoted(value) or value.startswith(("|", ">")):
        return line

    comment = match.group("comment") or ""
    space = match.group("space")
    if comment and not space:
        space = " "
    escaped_value = value.replace("\\", "\\\\").replace('"', '\\"')
    return (
        f'{match.group("prefix")}"{escaped_value}"'
        f'{space}{comment}{match.group("newline")}'
    )


def _value_is_quoted(value: str) -> bool:
    return len(value) >= 2 and value[0] in {'"', "'"} and value[-1] == value[0]
