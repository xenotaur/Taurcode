import re
from pathlib import Path
from typing import Any

import yaml

from taurcode import espanso_lint

_RESERVED_PROMPT_DIRS = {"espanso"}
_REQUIRED_FRONTMATTER_FIELDS = ("id", "name", "description", "keyword")
_KEYWORD_LINE_RE = re.compile(r"^keyword\s*:\s*(?P<value>.*?)(?:\s+#.*)?$")
_DESCRIPTION_LINE_RE = re.compile(r"^description\s*:\s*(?P<value>.*?)(?:\s+#.*)?$")


def lint_prompt_package(prompt_dir: str | Path) -> espanso_lint.LintResult:
    directory = Path(prompt_dir)
    errors: list[espanso_lint.Diagnostic] = []
    warnings: list[espanso_lint.Diagnostic] = []
    keyword_sources: dict[str, Path] = {}

    for prompt_file in _iter_prompt_files(directory):
        file_errors, file_warnings, metadata, body, frontmatter_text = (
            _lint_prompt_file(prompt_file)
        )
        errors.extend(file_errors)
        warnings.extend(file_warnings)
        if file_errors:
            continue

        keyword = metadata.get("keyword")
        if isinstance(keyword, str):
            existing_source = keyword_sources.get(keyword)
            if existing_source is not None:
                errors.append(
                    espanso_lint.Diagnostic(
                        path=prompt_file,
                        line=_frontmatter_key_line(frontmatter_text, "keyword"),
                        column=1,
                        code="prompt-duplicate-keyword",
                        message=f"Duplicate keyword {keyword!r} in prompt package",
                        detail=(
                            f"Keyword {keyword!r} is already used by {existing_source}."
                        ),
                        suggestion="Use one unique keyword per prompt file.",
                    )
                )
            else:
                keyword_sources[keyword] = prompt_file

        warnings.extend(_style_warnings(prompt_file, metadata, body, frontmatter_text))

    return espanso_lint.LintResult(errors=errors, warnings=warnings)


def _iter_prompt_files(directory: Path) -> list[Path]:
    prompt_files: list[Path] = []
    if not directory.exists():
        return prompt_files
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


def _lint_prompt_file(
    prompt_file: Path,
) -> tuple[
    list[espanso_lint.Diagnostic],
    list[espanso_lint.Diagnostic],
    dict[str, Any],
    str,
    str,
]:
    errors: list[espanso_lint.Diagnostic] = []
    warnings: list[espanso_lint.Diagnostic] = []
    text = prompt_file.read_text(encoding="utf-8")
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")

    if not _has_exactly_one_final_newline(normalized):
        warnings.append(
            espanso_lint.Diagnostic(
                path=prompt_file,
                line=None,
                column=None,
                code="prompt-final-newline",
                message="Prompt file should end with exactly one final newline",
                suggestion="Rewrite the file so it has one trailing newline and no extra blank newline at EOF.",
            )
        )

    split_result = _split_frontmatter(normalized)
    if split_result is None:
        errors.append(
            espanso_lint.Diagnostic(
                path=prompt_file,
                line=1,
                column=1,
                code="prompt-frontmatter-missing",
                message="Prompt file lacks YAML frontmatter delimiters",
                suggestion="Start the file with a YAML frontmatter block delimited by --- lines.",
            )
        )
        return errors, warnings, {}, normalized, ""

    frontmatter_text, body = split_result
    try:
        metadata = yaml.safe_load(frontmatter_text)
    except yaml.YAMLError as exc:
        diagnostic = espanso_lint.diagnostic_from_yaml_error(prompt_file, exc)
        errors.append(
            espanso_lint.Diagnostic(
                path=diagnostic.path,
                line=_frontmatter_yaml_line(diagnostic.line),
                column=diagnostic.column,
                code="prompt-frontmatter-yaml",
                message="Prompt frontmatter is malformed YAML",
                detail=diagnostic.detail,
                suggestion="Fix the YAML frontmatter before loading or exporting this prompt.",
            )
        )
        return errors, warnings, {}, body, frontmatter_text

    if metadata is None:
        metadata = {}
    if not isinstance(metadata, dict):
        errors.append(
            espanso_lint.Diagnostic(
                path=prompt_file,
                line=2,
                column=1,
                code="prompt-frontmatter-not-mapping",
                message="Prompt frontmatter must be a YAML mapping/object",
                suggestion="Use key/value YAML frontmatter such as name, description, and keyword.",
            )
        )
        return errors, warnings, {}, body, frontmatter_text

    errors.extend(_schema_errors(prompt_file, metadata, frontmatter_text))
    if body.startswith("\n"):
        body = body[1:]
    return errors, warnings, metadata, body, frontmatter_text


def _split_frontmatter(text: str) -> tuple[str, str] | None:
    lines = text.split("\n")
    if not lines or lines[0] != "---":
        return None
    for index in range(1, len(lines)):
        if lines[index] == "---":
            frontmatter_text = "\n".join(lines[1:index])
            body = "\n".join(lines[index + 1 :])
            return frontmatter_text, body
    return None


def _schema_errors(
    prompt_file: Path, metadata: dict[str, Any], frontmatter_text: str
) -> list[espanso_lint.Diagnostic]:
    errors: list[espanso_lint.Diagnostic] = []
    for field_name in _REQUIRED_FRONTMATTER_FIELDS:
        if field_name not in metadata or metadata.get(field_name) in (None, ""):
            errors.append(
                espanso_lint.Diagnostic(
                    path=prompt_file,
                    line=_frontmatter_key_line(frontmatter_text, field_name),
                    column=1,
                    code="prompt-required-field-missing",
                    message=f"Missing required frontmatter field {field_name!r}",
                    suggestion=(
                        "Add required fields: id, name, description, and keyword."
                    ),
                )
            )

    keyword = metadata.get("keyword")
    if "keyword" not in metadata:
        errors.append(
            espanso_lint.Diagnostic(
                path=prompt_file,
                line=2,
                column=1,
                code="prompt-keyword-missing",
                message="Prompt keyword is missing",
                suggestion='Add a keyword such as keyword: ":debug".',
            )
        )
        return errors
    if not isinstance(keyword, str):
        errors.append(
            espanso_lint.Diagnostic(
                path=prompt_file,
                line=_frontmatter_key_line(frontmatter_text, "keyword"),
                column=1,
                code="prompt-keyword-not-string",
                message="Prompt keyword must be a string",
                suggestion='Quote syntax-like keywords, for example keyword: ":debug".',
            )
        )
        return errors
    if not keyword.startswith(":") or keyword == ":":
        errors.append(
            espanso_lint.Diagnostic(
                path=prompt_file,
                line=_frontmatter_key_line(frontmatter_text, "keyword"),
                column=1,
                code="prompt-keyword-invalid-prefix",
                message="Prompt keyword must start with ':' and not be empty",
                suggestion='Use an Espanso-style trigger such as keyword: ":debug".',
            )
        )
    return errors


def _style_warnings(
    prompt_file: Path, metadata: dict[str, Any], body: str, frontmatter_text: str
) -> list[espanso_lint.Diagnostic]:
    warnings: list[espanso_lint.Diagnostic] = []
    keyword = metadata.get("keyword")
    if isinstance(keyword, str):
        expected_stem = _slug_from_keyword(keyword)
        if expected_stem and prompt_file.stem != expected_stem:
            warnings.append(
                espanso_lint.Diagnostic(
                    path=prompt_file,
                    line=None,
                    column=None,
                    code="prompt-filename-slug",
                    message="Prompt filename stem does not match keyword slug",
                    detail=(
                        f"Expected filename stem {expected_stem!r} for keyword {keyword!r}."
                    ),
                    suggestion="Rename the prompt file or adjust the keyword.",
                )
            )
        if not _keyword_is_quoted(frontmatter_text):
            warnings.append(
                espanso_lint.Diagnostic(
                    path=prompt_file,
                    line=_frontmatter_key_line(frontmatter_text, "keyword"),
                    column=1,
                    code="prompt-keyword-unquoted",
                    message="Prompt keyword should be quoted in source frontmatter",
                    suggestion='Prefer keyword: ":debug" to avoid YAML formatting churn.',
                )
            )

    if not body.strip():
        warnings.append(
            espanso_lint.Diagnostic(
                path=prompt_file,
                line=None,
                column=None,
                code="prompt-body-empty",
                message="Prompt body is empty or whitespace-only",
                suggestion="Add prompt body text before exporting the prompt.",
            )
        )

    if _description_appears_wrapped(frontmatter_text):
        warnings.append(
            espanso_lint.Diagnostic(
                path=prompt_file,
                line=_frontmatter_key_line(frontmatter_text, "description"),
                column=1,
                code="prompt-description-wrapped",
                message="Prompt description appears to be wrapped by a YAML dumper",
                suggestion="Keep description on one line when practical.",
            )
        )
    return warnings


def _frontmatter_yaml_line(line: int | None) -> int | None:
    if line is None:
        return None
    return line + 1


def _frontmatter_key_line(frontmatter_text: str, key: str) -> int | None:
    for index, line in enumerate(frontmatter_text.split("\n"), start=2):
        if re.match(rf"^{re.escape(key)}\s*:", line):
            return index
    return None


def _has_exactly_one_final_newline(text: str) -> bool:
    return text.endswith("\n") and not text.endswith("\n\n")


def _keyword_is_quoted(frontmatter_text: str) -> bool:
    for line in frontmatter_text.split("\n"):
        match = _KEYWORD_LINE_RE.match(line)
        if match is None:
            continue
        value = match.group("value").strip()
        return len(value) >= 2 and value[0] in {'"', "'"} and value[-1] == value[0]
    return True


def _description_appears_wrapped(frontmatter_text: str) -> bool:
    lines = frontmatter_text.split("\n")
    for index, line in enumerate(lines):
        match = _DESCRIPTION_LINE_RE.match(line)
        if match is None:
            continue
        value = match.group("value").strip()
        if not value or value.startswith(("|", ">")):
            return False
        return index + 1 < len(lines) and lines[index + 1].startswith("  ")
    return False


def _slug_from_keyword(keyword: str) -> str:
    base = keyword.lstrip(":").lower()
    base = re.sub(r"[^a-z0-9]+", "-", base).strip("-")
    return base
