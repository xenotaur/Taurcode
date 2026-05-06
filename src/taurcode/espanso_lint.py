from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class Diagnostic:
    path: Path
    line: int | None
    column: int | None
    code: str
    message: str
    detail: str = ""
    suggestion: str = ""


_PARSER_SENSITIVE_LINE_BREAKS = {
    "\u2028": "U+2028 LINE SEPARATOR",
    "\u2029": "U+2029 PARAGRAPH SEPARATOR",
    "\u0085": "U+0085 NEXT LINE",
}


def resolve_package_yml(input_path: str | Path) -> Path:
    path = Path(input_path)
    package_path = path / "package.yml" if path.is_dir() else path
    if path.is_dir() and not package_path.exists():
        raise ValueError(f"Missing Espanso package.yml in directory: {path}")
    if package_path.name != "package.yml":
        raise ValueError(
            "Input must be an Espanso package.yml file or a directory containing package.yml"
        )
    if not package_path.exists():
        raise ValueError(f"Espanso package.yml does not exist: {package_path}")
    return package_path


def _location_prefix(diagnostic: Diagnostic) -> str:
    if diagnostic.line is not None and diagnostic.column is not None:
        return f"{diagnostic.path}:{diagnostic.line}:{diagnostic.column}"
    return str(diagnostic.path)


def format_diagnostic(diagnostic: Diagnostic) -> str:
    lines = [f"{_location_prefix(diagnostic)}: {diagnostic.message}"]
    if diagnostic.detail:
        lines.append(diagnostic.detail)
    if diagnostic.suggestion:
        lines.append(f"Suggestion: {diagnostic.suggestion}")
    return "\n".join(lines)


def format_diagnostics(diagnostics: list[Diagnostic]) -> str:
    return "\n\n".join(format_diagnostic(diagnostic) for diagnostic in diagnostics)


def lint_espanso_package(input_path: str | Path) -> list[Diagnostic]:
    package_path = resolve_package_yml(input_path)
    try:
        content = package_path.read_bytes().decode("utf-8")
    except UnicodeDecodeError as exc:
        return [
            Diagnostic(
                path=package_path,
                line=None,
                column=None,
                code="utf8-decode-error",
                message="Invalid Espanso package.yml: UTF-8 decode error",
                detail=str(exc),
                suggestion="Save package.yml as valid UTF-8 before importing it.",
            )
        ]

    diagnostics = _line_break_diagnostics(package_path, content)
    if diagnostics:
        return diagnostics

    yaml_diagnostic = yaml_parse_diagnostic(package_path, content)
    if yaml_diagnostic is not None:
        return [yaml_diagnostic]
    return []


def _line_break_diagnostics(path: Path, content: str) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    line = 1
    column = 1
    index = 0
    while index < len(content):
        char = content[index]
        if char in _PARSER_SENSITIVE_LINE_BREAKS:
            name = _PARSER_SENSITIVE_LINE_BREAKS[char]
            diagnostics.append(
                Diagnostic(
                    path=path,
                    line=line,
                    column=column,
                    code="parser-sensitive-line-break",
                    message=f"found {name}",
                    detail=(
                        "This invisible character may be interpreted as a YAML "
                        "line break by some parsers."
                    ),
                    suggestion=(
                        "replace it with a normal newline indented inside the "
                        "block scalar."
                    ),
                )
            )
            line += 1
            column = 1
        elif char == "\r":
            line += 1
            column = 1
            if index + 1 < len(content) and content[index + 1] == "\n":
                index += 1
        elif char == "\n":
            line += 1
            column = 1
        else:
            column += 1
        index += 1
    return diagnostics


def diagnostic_from_yaml_error(path: Path, exc: yaml.YAMLError) -> Diagnostic:
    line: int | None = None
    column: int | None = None
    mark = getattr(exc, "problem_mark", None) or getattr(exc, "context_mark", None)
    if mark is not None:
        line = mark.line + 1
        column = mark.column + 1
    detail_parts = []
    context = getattr(exc, "context", None)
    problem = getattr(exc, "problem", None)
    if context:
        detail_parts.append(str(context))
    if problem:
        detail_parts.append(str(problem))
    if not detail_parts:
        detail_parts.append(str(exc))
    return Diagnostic(
        path=path,
        line=line,
        column=column,
        code="malformed-yaml",
        message="Invalid Espanso package.yml: malformed YAML",
        detail="\n".join(detail_parts),
        suggestion="Fix the YAML syntax and rerun the Espanso lint command.",
    )


def yaml_parse_diagnostic(path: Path, content: str) -> Diagnostic | None:
    try:
        yaml.safe_load(content)
    except yaml.YAMLError as exc:
        return diagnostic_from_yaml_error(path, exc)
    return None
