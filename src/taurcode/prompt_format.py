import dataclasses
import re
from pathlib import Path

from taurcode import text_normalization

_RESERVED_PROMPT_DIRS = {"espanso"}
_KEYWORD_FORMAT_LINE_RE = re.compile(
    r"^(?P<prefix>keyword\s*:\s*)" r"(?P<rest>[^\r\n]*)" r"(?P<newline>\r?\n?)$"
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
    # Uses find()/slicing instead of splitlines() on the entire file to avoid
    # allocating an intermediate list of lines for large prompt bodies.
    if not text.startswith("---"):
        return text

    first_newline = text.find("\n")
    if first_newline == -1:
        if text.rstrip("\r") == "---":
            return text
        return text

    if text[:first_newline].rstrip("\r") != "---":
        return text

    match = re.search(r"\r?\n---\r?\n|\r?\n---$", text)
    if not match:
        return text

    end_idx = match.start()
    frontmatter = text[:end_idx]

    lines = frontmatter.splitlines(keepends=True)
    for i in range(1, len(lines)):
        lines[i] = _format_keyword_line(lines[i])

    return "".join(lines) + text[end_idx:]


def _line_content(line: str) -> str:
    return line.removesuffix("\n").removesuffix("\r")


def _format_keyword_line(line: str) -> str:
    match = _KEYWORD_FORMAT_LINE_RE.match(line)
    if match is None:
        return line

    rest = match.group("rest")
    if _rest_starts_with_preserved_scalar(rest):
        return line

    raw_value, space, comment = _split_plain_value_and_comment(rest)
    value = raw_value.strip()
    if not value:
        return line

    escaped_value = value.replace("\\", "\\\\").replace('"', '\\"')
    return (
        f'{match.group("prefix")}"{escaped_value}"'
        f'{space}{comment}{match.group("newline")}'
    )


def _rest_starts_with_preserved_scalar(rest: str) -> bool:
    value = rest.lstrip()
    return value.startswith(('"', "'", "|", ">"))


def _split_plain_value_and_comment(rest: str) -> tuple[str, str, str]:
    for index, character in enumerate(rest):
        if character != "#":
            continue
        if index > 0 and rest[index - 1] not in {" ", "\t"}:
            continue

        space_start = index
        while space_start > 0 and rest[space_start - 1] in {" ", "\t"}:
            space_start -= 1
        return rest[:space_start], rest[space_start:index], rest[index:]

    return rest, "", ""
