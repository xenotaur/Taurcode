import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

import yaml

from taurcode import espanso_metadata


@dataclass(frozen=True)
class Diagnostic:
    path: Path
    line: int | None
    column: int | None
    code: str
    message: str
    detail: str = ""
    suggestion: str = ""


@dataclass(frozen=True)
class LintResult:
    errors: list[Diagnostic]
    warnings: list[Diagnostic]

    def has_errors(self) -> bool:
        return bool(self.errors)

    def has_warnings(self) -> bool:
        return bool(self.warnings)


_PARSER_SENSITIVE_LINE_BREAKS = {
    "\u2028": "U+2028 LINE SEPARATOR",
    "\u2029": "U+2029 PARAGRAPH SEPARATOR",
    "\u0085": "U+0085 NEXT LINE",
}
_REQUIRED_BUILD_FILES = ("package.yml", "_manifest.yml", "README.md")
_PACKAGE_NAME_RE = re.compile(r"^[a-z0-9-]+$")
_VERSION_CORE_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+].*)?$")
_PLACEHOLDER_VALUES = {
    "description": {"generated prompt package"},
    "author": {"taurcode"},
}
_TINY_README_CHARS = 20


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
    lines = [
        f"{_location_prefix(diagnostic)}: [{diagnostic.code}] {diagnostic.message}"
    ]
    if diagnostic.detail:
        lines.append(diagnostic.detail)
    if diagnostic.suggestion:
        lines.append(f"Suggestion: {diagnostic.suggestion}")
    return "\n".join(lines)


def format_diagnostics(diagnostics: list[Diagnostic]) -> str:
    return "\n\n".join(format_diagnostic(diagnostic) for diagnostic in diagnostics)


def format_lint_result(result: LintResult) -> str:
    sections = []
    if result.errors:
        sections.append("Errors:\n" + format_diagnostics(result.errors))
    if result.warnings:
        sections.append("Warnings:\n" + format_diagnostics(result.warnings))
    return "\n\n".join(sections)


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


def lint_espanso_package_source(package_dir: str | Path) -> LintResult:
    package_path = Path(package_dir)
    metadata_dir = package_path / "espanso"
    manifest_path = metadata_dir / "_manifest.yml"
    readme_path = metadata_dir / "README.md"
    package_name = package_path.name

    if manifest_path.is_file():
        manifest, manifest_error = _load_manifest(manifest_path)
        errors = [manifest_error] if manifest_error is not None else []
    else:
        manifest = espanso_metadata.generate_default_manifest(package_name)
        errors = []
    warnings: list[Diagnostic] = []

    if _invalid_package_name(package_name):
        errors.append(_invalid_package_name_diagnostic(package_path, package_name))
    if manifest is not None:
        errors.extend(
            _manifest_error_diagnostics(manifest_path, package_name, manifest)
        )
        warnings.extend(
            _manifest_warning_diagnostics(manifest_path, package_name, manifest)
        )
    warnings.extend(_readme_warning_diagnostics(readme_path, package_name, manifest))
    return LintResult(errors=errors, warnings=warnings)


def lint_espanso_package_build(output_dir: str | Path) -> LintResult:
    output = Path(output_dir)
    package_name = output.name
    errors: list[Diagnostic] = []
    warnings: list[Diagnostic] = []

    for required_file in _REQUIRED_BUILD_FILES:
        required_path = output / required_file
        if not required_path.is_file():
            errors.append(
                Diagnostic(
                    path=required_path,
                    line=None,
                    column=None,
                    code="missing-build-file",
                    message=f"Build output is missing required {required_file}.",
                    suggestion="Export the package again or restore the missing file.",
                )
            )

    if _invalid_package_name(package_name):
        errors.append(_invalid_package_name_diagnostic(output, package_name))

    manifest_path = output / "_manifest.yml"
    manifest: dict | None = None
    if manifest_path.is_file():
        manifest, manifest_error = _load_manifest(manifest_path)
        if manifest_error is not None:
            errors.append(manifest_error)
        elif manifest is not None:
            errors.extend(
                _manifest_error_diagnostics(manifest_path, package_name, manifest)
            )
            warnings.extend(
                _manifest_warning_diagnostics(manifest_path, package_name, manifest)
            )

    warnings.extend(
        _readme_warning_diagnostics(output / "README.md", package_name, manifest)
    )
    return LintResult(errors=errors, warnings=warnings)


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


def _manifest_yaml_diagnostic(path: Path, exc: yaml.YAMLError) -> Diagnostic:
    diagnostic = diagnostic_from_yaml_error(path, exc)
    return Diagnostic(
        path=diagnostic.path,
        line=diagnostic.line,
        column=diagnostic.column,
        code="manifest-malformed-yaml",
        message="Invalid Espanso _manifest.yml: malformed YAML",
        detail=diagnostic.detail,
        suggestion="Fix the manifest YAML syntax and rerun the export.",
    )


def _load_manifest(path: Path) -> tuple[dict | None, Diagnostic | None]:
    try:
        manifest_text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        return None, Diagnostic(
            path=path,
            line=None,
            column=None,
            code="manifest-utf8-decode-error",
            message="Invalid Espanso _manifest.yml: UTF-8 decode error",
            detail=str(exc),
            suggestion="Save _manifest.yml as valid UTF-8.",
        )
    try:
        parsed = yaml.safe_load(manifest_text)
    except yaml.YAMLError as exc:
        return None, _manifest_yaml_diagnostic(path, exc)
    if not isinstance(parsed, dict):
        return {}, None
    return parsed, None


def _invalid_package_name(package_name: str) -> bool:
    return not bool(_PACKAGE_NAME_RE.fullmatch(package_name))


def _invalid_package_name_diagnostic(path: Path, package_name: str) -> Diagnostic:
    return Diagnostic(
        path=path,
        line=None,
        column=None,
        code="invalid-package-name",
        message=(
            f"Package name '{package_name}' must use only lowercase letters, "
            "digits, and hyphen."
        ),
        suggestion="Rename the package directory and manifest name to a registry-safe slug.",
    )


def _manifest_error_diagnostics(
    manifest_path: Path, package_name: str, manifest: dict
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    name = manifest.get("name")
    if not isinstance(name, str) or not name.strip():
        diagnostics.append(
            Diagnostic(
                path=manifest_path,
                line=None,
                column=None,
                code="manifest-name-missing",
                message="Manifest name is missing.",
                suggestion="Set _manifest.yml name to the package directory name.",
            )
        )
    else:
        manifest_name = name.strip()
        if manifest_name != package_name:
            diagnostics.append(
                Diagnostic(
                    path=manifest_path,
                    line=None,
                    column=None,
                    code="manifest-name-mismatch",
                    message=(
                        f"Manifest name '{manifest_name}' does not match package "
                        f"directory name '{package_name}'."
                    ),
                    suggestion="Keep the manifest name and package directory name identical.",
                )
            )
        if _invalid_package_name(manifest_name):
            diagnostics.append(
                _invalid_package_name_diagnostic(manifest_path, manifest_name)
            )

    version = manifest.get("version")
    if not isinstance(version, str) or not version.strip():
        diagnostics.append(
            Diagnostic(
                path=manifest_path,
                line=None,
                column=None,
                code="manifest-version-missing",
                message="Manifest version is missing.",
                suggestion="Set _manifest.yml version to a numeric MAJOR.MINOR.PATCH value.",
            )
        )
    elif _VERSION_CORE_RE.fullmatch(version.strip()) is None:
        diagnostics.append(
            Diagnostic(
                path=manifest_path,
                line=None,
                column=None,
                code="manifest-version-invalid",
                message=(
                    f"Manifest version '{version}' must include a numeric "
                    "MAJOR.MINOR.PATCH core."
                ),
                suggestion="Use a value such as 0.1.0, optionally with SemVer suffixes.",
            )
        )
    return diagnostics


def _manifest_warning_diagnostics(
    manifest_path: Path, package_name: str, manifest: dict
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for field_name in ("description", "author"):
        value = manifest.get(field_name)
        normalized = value.strip().lower() if isinstance(value, str) else ""
        if not normalized or normalized in _PLACEHOLDER_VALUES[field_name]:
            diagnostics.append(
                Diagnostic(
                    path=manifest_path,
                    line=None,
                    column=None,
                    code=f"manifest-{field_name}-placeholder",
                    message=f"Manifest {field_name} is empty or still a generated placeholder.",
                    suggestion=f"Replace {field_name} with package-specific metadata.",
                )
            )

    homepage = manifest.get("homepage")
    if isinstance(homepage, str) and homepage.strip():
        homepage_text = homepage.strip()
        parsed = urlparse(homepage_text)
        if parsed.scheme not in {"http", "https"}:
            diagnostics.append(
                Diagnostic(
                    path=manifest_path,
                    line=None,
                    column=None,
                    code="manifest-homepage-non-http",
                    message="Manifest homepage should be an http:// or https:// URL.",
                    detail=homepage_text,
                    suggestion="Use an HTTP(S) project page or omit homepage.",
                )
            )
        else:
            slug = _homepage_slug(parsed.path)
            if slug and slug != package_name:
                diagnostics.append(
                    Diagnostic(
                        path=manifest_path,
                        line=None,
                        column=None,
                        code="manifest-homepage-package-mismatch",
                        message=(
                            "Manifest homepage repository slug appears to point to "
                            f"'{slug}' instead of package '{package_name}'."
                        ),
                        suggestion="Confirm the homepage points to this package or update it.",
                    )
                )
    return diagnostics


def _homepage_slug(path: str) -> str:
    parts = [part for part in path.strip("/").split("/") if part]
    if len(parts) < 2:
        return ""
    return parts[1].removesuffix(".git").lower()


def _readme_warning_diagnostics(
    readme_path: Path, package_name: str, manifest: dict | None
) -> list[Diagnostic]:
    if not readme_path.is_file():
        return []
    try:
        readme_text = readme_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        return [
            Diagnostic(
                path=readme_path,
                line=None,
                column=None,
                code="readme-utf8-decode-error",
                message="README.md could not be decoded as UTF-8.",
                detail=str(exc),
                suggestion="Save README.md as valid UTF-8.",
            )
        ]

    diagnostics: list[Diagnostic] = []
    stripped = readme_text.strip()
    if len(stripped) < _TINY_README_CHARS:
        diagnostics.append(
            Diagnostic(
                path=readme_path,
                line=None,
                column=None,
                code="readme-too-small",
                message="README.md is empty or very small.",
                suggestion="Add a short description of the Espanso package.",
            )
        )

    title = ""
    if manifest is not None:
        manifest_title = manifest.get("title")
        if isinstance(manifest_title, str):
            title = manifest_title.strip()
    haystack = readme_text.lower()
    mentions_package = package_name.lower() in haystack
    mentions_title = bool(title) and title.lower() in haystack
    if stripped and not mentions_package and not mentions_title:
        diagnostics.append(
            Diagnostic(
                path=readme_path,
                line=None,
                column=None,
                code="readme-missing-package-name",
                message="README.md does not mention the package name or manifest title.",
                suggestion="Mention the package name or title so package metadata stays recognizable.",
            )
        )
    return diagnostics
