import dataclasses
import pathlib
from typing import Any

import frontmatter
import yaml

from taurcode import espanso_lint

ESPANSO_SEMANTIC_MODE = "espanso"
CANONICAL_SEMANTIC_MODE = "canonical"
_METADATA_ASSETS = ("_manifest.yml", "README.md", "LICENSE")
_RESERVED_PROMPT_DIRS = {"espanso"}


@dataclasses.dataclass(frozen=True)
class NormalizedPrompt:
    key: str
    trigger: str
    body: str
    prompt_id: str | None = None
    name: str | None = None
    description: str | None = None
    tags: tuple[str, ...] = ()
    unsupported_fields: tuple[tuple[str, Any], ...] = ()


@dataclasses.dataclass(frozen=True)
class NormalizedPackage:
    prompts: tuple[NormalizedPrompt, ...]
    manifest: Any | None = None
    readme: str | None = None
    license_text: str | None = None


@dataclasses.dataclass(frozen=True)
class SemanticDifference:
    path: str
    message: str


def normalize_espanso_package(path: str | pathlib.Path) -> NormalizedPackage:
    package_path = espanso_lint.resolve_package_yml(path)
    package_dir = package_path.parent
    package_data = _load_yaml_mapping(package_path, "Espanso package.yml")
    matches = package_data.get("matches")
    if not isinstance(matches, list):
        raise ValueError(
            "Invalid Espanso package.yml: expected top-level 'matches' list"
        )

    prompts: list[NormalizedPrompt] = []
    for index, match in enumerate(matches):
        if not isinstance(match, dict):
            raise ValueError(
                "Invalid Espanso package.yml: each match entry must be a mapping"
            )
        trigger = match.get("trigger")
        replace = match.get("replace")
        if not isinstance(trigger, str) or not isinstance(replace, str):
            raise ValueError(
                "Invalid Espanso package.yml: each normalized match needs string "
                f"trigger and replace fields at matches[{index}]"
            )
        unsupported = tuple(
            (str(key), _normalize_data(value))
            for key, value in sorted(match.items(), key=lambda item: str(item[0]))
            if key not in {"trigger", "replace"}
        )
        body = _normalize_text(replace)
        prompts.append(
            NormalizedPrompt(
                key=trigger,
                trigger=trigger,
                body=body,
                unsupported_fields=unsupported,
            )
        )

    return NormalizedPackage(
        prompts=tuple(sorted(prompts, key=lambda prompt: prompt.key)),
        manifest=_load_manifest_asset(package_dir / "_manifest.yml"),
        readme=_load_text_asset(package_dir / "README.md"),
        license_text=_load_text_asset(package_dir / "LICENSE"),
    )


def normalize_canonical_prompts(path: str | pathlib.Path) -> NormalizedPackage:
    prompts_dir = pathlib.Path(path)
    prompts: list[NormalizedPrompt] = []
    for prompt_file in sorted(prompts_dir.rglob("*.md")):
        if not prompt_file.is_file():
            continue
        if _is_reserved_prompt_file(prompt_file, prompts_dir):
            continue
        text = prompt_file.read_text(encoding="utf-8")
        try:
            post = frontmatter.loads(text)
        except yaml.YAMLError as error:
            raise ValueError(
                f"Malformed YAML frontmatter in {prompt_file}: {error}"
            ) from error
        metadata = dict(post.metadata)
        prompt_id = _optional_str(metadata.get("id"))
        trigger = _optional_str(metadata.get("keyword")) or ""
        key = trigger or prompt_id or str(prompt_file.relative_to(prompts_dir))
        prompts.append(
            NormalizedPrompt(
                key=key,
                trigger=trigger,
                body=_extract_prompt_body(text),
                prompt_id=prompt_id,
                name=_optional_str(metadata.get("name")),
                description=_optional_str(metadata.get("description")),
                tags=_normalize_tags(metadata.get("tags")),
            )
        )

    metadata_dir = prompts_dir / "espanso"
    return NormalizedPackage(
        prompts=tuple(sorted(prompts, key=lambda prompt: prompt.key)),
        manifest=_load_manifest_asset(metadata_dir / "_manifest.yml"),
        readme=_load_text_asset(metadata_dir / "README.md"),
        license_text=_load_text_asset(metadata_dir / "LICENSE"),
    )


def compare_packages(
    expected: NormalizedPackage,
    actual: NormalizedPackage,
    mode: str = ESPANSO_SEMANTIC_MODE,
) -> list[SemanticDifference]:
    if mode not in {ESPANSO_SEMANTIC_MODE, CANONICAL_SEMANTIC_MODE}:
        raise ValueError(f"Unsupported semantic comparison mode: {mode}")

    differences: list[SemanticDifference] = []
    differences.extend(_compare_prompts(expected.prompts, actual.prompts, mode))
    differences.extend(
        _compare_asset("_manifest.yml", expected.manifest, actual.manifest)
    )
    differences.extend(_compare_asset("README.md", expected.readme, actual.readme))
    differences.extend(
        _compare_asset("LICENSE", expected.license_text, actual.license_text)
    )
    return differences


def _compare_prompts(
    expected: tuple[NormalizedPrompt, ...],
    actual: tuple[NormalizedPrompt, ...],
    mode: str,
) -> list[SemanticDifference]:
    differences: list[SemanticDifference] = []
    expected_by_key = {prompt.key: prompt for prompt in expected}
    actual_by_key = {prompt.key: prompt for prompt in actual}

    for key in sorted(expected_by_key.keys() - actual_by_key.keys()):
        differences.append(
            SemanticDifference(f"prompts[{key}]", "Expected prompt is missing")
        )
    for key in sorted(actual_by_key.keys() - expected_by_key.keys()):
        differences.append(
            SemanticDifference(f"prompts[{key}]", "Unexpected extra prompt")
        )

    for key in sorted(expected_by_key.keys() & actual_by_key.keys()):
        expected_prompt = expected_by_key[key]
        actual_prompt = actual_by_key[key]
        if expected_prompt.trigger != actual_prompt.trigger:
            differences.append(
                SemanticDifference(
                    f"prompts[{key}].trigger",
                    "Prompt trigger differs: "
                    f"expected {expected_prompt.trigger!r}, got {actual_prompt.trigger!r}",
                )
            )
        if expected_prompt.body != actual_prompt.body:
            differences.append(
                SemanticDifference(f"prompts[{key}].body", "Prompt body differs")
            )
        if expected_prompt.unsupported_fields != actual_prompt.unsupported_fields:
            differences.append(
                SemanticDifference(
                    f"prompts[{key}].unsupported_fields",
                    "Unsupported Espanso fields differ",
                )
            )
        if mode == CANONICAL_SEMANTIC_MODE:
            differences.extend(
                _compare_canonical_prompt_fields(key, expected_prompt, actual_prompt)
            )
    return differences


def _compare_canonical_prompt_fields(
    key: str, expected: NormalizedPrompt, actual: NormalizedPrompt
) -> list[SemanticDifference]:
    differences: list[SemanticDifference] = []
    for field in ("prompt_id", "name", "description", "tags"):
        expected_value = getattr(expected, field)
        actual_value = getattr(actual, field)
        if expected_value != actual_value:
            differences.append(
                SemanticDifference(
                    f"prompts[{key}].{field}",
                    f"Canonical prompt {field} differs: "
                    f"expected {expected_value!r}, got {actual_value!r}",
                )
            )
    return differences


def _compare_asset(
    name: str, expected: Any | None, actual: Any | None
) -> list[SemanticDifference]:
    if expected == actual:
        return []
    if expected is None:
        return [SemanticDifference(name, f"Unexpected extra metadata asset: {name}")]
    if actual is None:
        return [SemanticDifference(name, f"Expected metadata asset is missing: {name}")]
    return [SemanticDifference(name, f"Metadata asset differs: {name}")]


def _load_yaml_mapping(path: pathlib.Path, label: str) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise ValueError(f"Invalid {label}: UTF-8 decode error: {error}") from error
    try:
        parsed = yaml.safe_load(text)
    except yaml.YAMLError as error:
        diagnostic = espanso_lint.diagnostic_from_yaml_error(path, error)
        raise ValueError(espanso_lint.format_diagnostic(diagnostic)) from error
    if parsed is None:
        return {}
    if not isinstance(parsed, dict):
        raise ValueError(f"Invalid {label}: expected a YAML mapping")
    return parsed


def _load_manifest_asset(path: pathlib.Path) -> Any | None:
    if not path.is_file():
        return None
    manifest = _load_yaml_mapping(path, "Espanso _manifest.yml")
    return _normalize_data(manifest)


def _load_text_asset(path: pathlib.Path) -> str | None:
    if not path.is_file():
        return None
    text = path.read_text(encoding="utf-8")
    return _normalize_text(text)


def _normalize_data(value: Any) -> Any:
    if isinstance(value, dict):
        return tuple(
            (str(key), _normalize_data(child))
            for key, child in sorted(value.items(), key=lambda item: str(item[0]))
        )
    if isinstance(value, list):
        return tuple(_normalize_data(child) for child in value)
    if isinstance(value, str):
        return _normalize_text(value)
    return value


def _normalize_text(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _extract_prompt_body(text: str) -> str:
    normalized = _normalize_text(text)
    lines = normalized.split("\n")
    if not lines or lines[0] != "---":
        return normalized
    for index in range(1, len(lines)):
        if lines[index] == "---":
            body = "\n".join(lines[index + 1 :])
            if body.startswith("\n"):
                body = body[1:]
            return body
    return normalized


def _is_reserved_prompt_file(
    prompt_file: pathlib.Path, directory: pathlib.Path
) -> bool:
    relative_parts = prompt_file.relative_to(directory).parts
    return bool(relative_parts and relative_parts[0] in _RESERVED_PROMPT_DIRS)


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)


def _normalize_tags(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, list):
        return tuple(str(item) for item in value)
    return (str(value),)
