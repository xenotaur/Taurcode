import collections
import dataclasses
import pathlib
from typing import Any

import frontmatter
import yaml

from taurcode import espanso_lint, prompt_loader

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
    force_clipboard: bool = False
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
            if key not in {"trigger", "replace", "force_clipboard"}
        )
        body = _normalize_text(replace)
        prompts.append(
            NormalizedPrompt(
                key=trigger,
                trigger=trigger,
                body=body,
                force_clipboard=match.get("force_clipboard") is True,
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
                body=prompt_loader.extract_prompt_body(text),
                prompt_id=prompt_id,
                name=_optional_str(metadata.get("name")),
                description=_optional_str(metadata.get("description")),
                tags=_normalize_tags(metadata.get("tags")),
                force_clipboard=_force_clipboard_from_metadata(metadata),
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
        _compare_asset("_manifest.yml", expected.manifest, actual.manifest, mode)
    )
    differences.extend(
        _compare_asset("README.md", expected.readme, actual.readme, mode)
    )
    differences.extend(
        _compare_asset("LICENSE", expected.license_text, actual.license_text, mode)
    )
    return differences


def _compare_prompts(
    expected: tuple[NormalizedPrompt, ...],
    actual: tuple[NormalizedPrompt, ...],
    mode: str,
) -> list[SemanticDifference]:
    differences: list[SemanticDifference] = []
    expected_by_key = _group_prompts_by_key(expected)
    actual_by_key = _group_prompts_by_key(actual)

    for key in sorted(expected_by_key.keys() | actual_by_key.keys()):
        expected_group = expected_by_key.get(key, [])
        actual_group = actual_by_key.get(key, [])
        if not expected_group:
            differences.append(
                SemanticDifference(
                    f"prompts[{key}]",
                    f"Unexpected {len(actual_group)} extra prompt(s)",
                )
            )
            continue
        if not actual_group:
            differences.append(
                SemanticDifference(
                    f"prompts[{key}]",
                    f"Expected {len(expected_group)} prompt(s) missing",
                )
            )
            continue
        if len(expected_group) == 1 and len(actual_group) == 1:
            differences.extend(
                _compare_single_prompt(key, expected_group[0], actual_group[0], mode)
            )
            continue
        differences.extend(
            _compare_prompt_group(key, expected_group, actual_group, mode)
        )
    return differences


def _group_prompts_by_key(
    prompts: tuple[NormalizedPrompt, ...],
) -> dict[str, list[NormalizedPrompt]]:
    grouped: dict[str, list[NormalizedPrompt]] = {}
    for prompt in prompts:
        grouped.setdefault(prompt.key, []).append(prompt)
    return grouped


def _compare_single_prompt(
    key: str, expected: NormalizedPrompt, actual: NormalizedPrompt, mode: str
) -> list[SemanticDifference]:
    differences: list[SemanticDifference] = []
    if expected.trigger != actual.trigger:
        differences.append(
            SemanticDifference(
                f"prompts[{key}].trigger",
                "Prompt trigger differs: "
                f"expected {expected.trigger!r}, got {actual.trigger!r}",
            )
        )
    if expected.body != actual.body:
        differences.append(
            SemanticDifference(f"prompts[{key}].body", "Prompt body differs")
        )
    if expected.force_clipboard != actual.force_clipboard:
        differences.append(
            SemanticDifference(
                f"prompts[{key}].force_clipboard",
                "force_clipboard differs: "
                f"expected {expected.force_clipboard!r}, got {actual.force_clipboard!r}",
            )
        )
    if _unsupported_fields_differ(expected, actual, mode):
        differences.append(
            SemanticDifference(
                f"prompts[{key}].unsupported_fields",
                "Unsupported Espanso fields differ: "
                f"expected {_short_repr(expected.unsupported_fields)}, "
                f"got {_short_repr(actual.unsupported_fields)}",
            )
        )
    if mode == CANONICAL_SEMANTIC_MODE:
        differences.extend(_compare_canonical_prompt_fields(key, expected, actual))
    return differences


def _compare_prompt_group(
    key: str,
    expected: list[NormalizedPrompt],
    actual: list[NormalizedPrompt],
    mode: str,
) -> list[SemanticDifference]:
    include_unsupported = mode == CANONICAL_SEMANTIC_MODE or any(
        prompt.unsupported_fields for prompt in expected
    )
    expected_counter = collections.Counter(
        _prompt_signature(prompt, mode, include_unsupported) for prompt in expected
    )
    actual_counter = collections.Counter(
        _prompt_signature(prompt, mode, include_unsupported) for prompt in actual
    )

    differences: list[SemanticDifference] = []
    for signature, count in sorted((expected_counter - actual_counter).items()):
        differences.append(
            SemanticDifference(
                f"prompts[{key}]",
                f"Expected {count} prompt occurrence(s) missing: "
                f"{_prompt_signature_message(signature)}",
            )
        )
    for signature, count in sorted((actual_counter - expected_counter).items()):
        differences.append(
            SemanticDifference(
                f"prompts[{key}]",
                f"Unexpected {count} extra prompt occurrence(s): "
                f"{_prompt_signature_message(signature)}",
            )
        )
    return differences


def _prompt_signature(
    prompt: NormalizedPrompt, mode: str, include_unsupported: bool
) -> tuple[Any, ...]:
    signature: tuple[Any, ...] = (prompt.trigger, prompt.body, prompt.force_clipboard)
    if include_unsupported:
        signature = (*signature, prompt.unsupported_fields)
    if mode == CANONICAL_SEMANTIC_MODE:
        signature = (
            *signature,
            prompt.prompt_id,
            prompt.name,
            prompt.description,
            prompt.tags,
        )
    return signature


def _prompt_signature_message(signature: tuple[Any, ...]) -> str:
    trigger, body, *_rest = signature
    return f"trigger={trigger!r}, body={_short_repr(body)}"


def _unsupported_fields_differ(
    expected: NormalizedPrompt, actual: NormalizedPrompt, mode: str
) -> bool:
    if mode == CANONICAL_SEMANTIC_MODE:
        return expected.unsupported_fields != actual.unsupported_fields
    if not expected.unsupported_fields:
        return False
    return expected.unsupported_fields != actual.unsupported_fields


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
    name: str, expected: Any | None, actual: Any | None, mode: str
) -> list[SemanticDifference]:
    if expected == actual:
        return []
    if expected is None:
        if mode == ESPANSO_SEMANTIC_MODE:
            return []
        return [SemanticDifference(name, f"Unexpected extra metadata asset: {name}")]
    if actual is None:
        return [SemanticDifference(name, f"Expected metadata asset is missing: {name}")]
    return [
        SemanticDifference(
            name,
            f"Metadata asset differs: {name}; "
            f"expected {_short_repr(expected)}, got {_short_repr(actual)}",
        )
    ]


def _short_repr(value: Any, limit: int = 160) -> str:
    rendered = repr(value)
    if len(rendered) <= limit:
        return rendered
    return rendered[: limit - 3] + "..."


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


def _force_clipboard_from_metadata(metadata: dict[str, Any]) -> bool:
    targets = metadata.get("targets")
    if not isinstance(targets, dict):
        return False
    espanso = targets.get("espanso")
    if not isinstance(espanso, dict):
        return False
    return espanso.get("force_clipboard") is True
