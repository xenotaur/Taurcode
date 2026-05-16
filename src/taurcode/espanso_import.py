import json
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from . import espanso_lint, text_normalization

_SIMPLE_KEYS = {"trigger", "replace"}
_METADATA_ASSETS = ("_manifest.yml", "README.md", "LICENSE")
_RESERVED_PROMPT_DIRS = {"espanso"}


@dataclass
class ExistingPrompt:
    path: Path
    metadata: dict[str, Any]
    body: str
    frontmatter_text: str | None = None


@dataclass
class ImportResult:
    total: int
    converted: int
    raw_fallback: int
    warnings: list[str]


def is_simple_match(match: dict) -> bool:
    return isinstance(match, dict) and set(match.keys()) == _SIMPLE_KEYS


def _normalize_id(trigger: str) -> str:
    base = trigger.lstrip(":").lower()
    base = re.sub(r"[^a-z0-9]+", "-", base).strip("-")
    return base or "imported-prompt"


def _unique_id(base_id: str, used_ids: set[str]) -> str:
    candidate = base_id
    i = 2
    while candidate in used_ids:
        candidate = f"{base_id}-{i}"
        i += 1
    used_ids.add(candidate)
    return candidate


def _derive_name(prompt_id: str) -> str:
    return " ".join(part.capitalize() for part in prompt_id.split("-"))


def _is_reserved_prompt_file(prompt_file: Path, directory: Path) -> bool:
    relative_parts = prompt_file.relative_to(directory).parts
    return bool(relative_parts and relative_parts[0] in _RESERVED_PROMPT_DIRS)


def _iter_prompt_files(output: Path) -> list[Path]:
    if not output.exists():
        return []
    prompt_files: list[Path] = []
    for prompt_file in sorted(output.rglob("*.md")):
        if not prompt_file.is_file():
            continue
        if _is_reserved_prompt_file(prompt_file, output):
            continue
        prompt_files.append(prompt_file)
    return prompt_files


def _seed_used_ids(output: Path) -> set[str]:
    return {prompt_file.stem for prompt_file in _iter_prompt_files(output)}


def _next_raw_index(raw_dir: Path) -> int:
    max_idx = 0
    if raw_dir.exists():
        for p in raw_dir.glob("match-*.yml"):
            m = re.match(r"match-(\d+)\.yml$", p.name)
            if m:
                max_idx = max(max_idx, int(m.group(1)))
    return max_idx + 1


def _split_raw_match_blocks(text: str) -> list[str]:
    lines = text.splitlines(keepends=True)
    in_matches = False
    base_indent: int | None = None
    current_block: list[str] = []
    blocks: list[str] = []

    for line in lines:
        stripped = line.strip()
        indent = len(line) - len(line.lstrip(" "))

        if not in_matches:
            if re.fullmatch(r"matches:\s*(?:#.*)?", stripped):
                in_matches = True
                base_indent = indent
            continue

        if stripped and not stripped.startswith("#") and indent <= (base_indent or 0):
            break

        if stripped.startswith("- ") and indent == (base_indent or 0) + 2:
            if current_block:
                blocks.append("".join(current_block))
            current_block = [line]
            continue

        if current_block:
            current_block.append(line)

    if current_block:
        blocks.append("".join(current_block))
    return blocks


def _parse_espanso_package(package_path: Path) -> list[tuple[dict, str]]:
    text = package_path.read_text(encoding="utf-8")
    if "matches:" not in text:
        raise ValueError(
            "Invalid Espanso package.yml: expected top-level 'matches' list"
        )
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        diagnostic = espanso_lint.diagnostic_from_yaml_error(package_path, exc)
        raise ValueError(espanso_lint.format_diagnostic(diagnostic)) from exc
    if not isinstance(data, dict) or not isinstance(data.get("matches"), list):
        raise ValueError(
            "Invalid Espanso package.yml: expected top-level 'matches' list"
        )

    matches: list = data["matches"]
    raw_blocks = _split_raw_match_blocks(text)
    if len(raw_blocks) < len(matches):
        raise ValueError(
            "Invalid Espanso package.yml: could not reliably extract all raw match blocks"
        )
    entries: list[tuple[dict, str]] = []
    for index, match in enumerate(matches):
        if not isinstance(match, dict):
            raise ValueError(
                "Invalid Espanso package.yml: each match entry must be a mapping"
            )
        raw_block = raw_blocks[index]
        entries.append((match, raw_block))
    return entries


def resolve_espanso_package_dir(input_path: str | Path) -> Path | None:
    path = Path(input_path)
    if path.is_dir():
        return path
    return None


def import_espanso_metadata_assets(
    package_dir: Path | None, prompt_collection_dir: Path
) -> tuple[set[str], list[str]]:
    if package_dir is None:
        warning = (
            "Warning: Espanso metadata asset import skipped because --input points "
            "directly to package.yml; pass the package directory to import sibling "
            "metadata assets."
        )
        print(warning, file=sys.stderr)
        return set(), [warning]

    copied: set[str] = set()
    warnings: list[str] = []
    metadata_dir = prompt_collection_dir / "espanso"
    for asset_name in _METADATA_ASSETS:
        source = package_dir / asset_name
        if not source.is_file():
            warning = f"Warning: Espanso metadata asset missing; skipped {source}"
            warnings.append(warning)
            print(warning, file=sys.stderr)
            continue

        metadata_dir.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, metadata_dir / asset_name)
        copied.add(asset_name)
    return copied, warnings


def _normalize_replace(value: object) -> str:
    return str(value).replace("\r\n", "\n").replace("\r", "\n")


def _fresh_prompt_content(prompt_id: str, trigger: str, replace: str) -> str:
    return text_normalization.normalize_final_newline(
        "---\n"
        f"id: {prompt_id}\n"
        f"name: {_derive_name(prompt_id)}\n"
        "description: Imported from Espanso\n"
        f'keyword: "{trigger}"\n'
        "---\n\n"
        f"{replace}"
    )


def _read_prompt_file(prompt_file: Path) -> ExistingPrompt:
    text = prompt_file.read_text(encoding="utf-8")
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = normalized.split("\n")
    if not lines or lines[0] != "---":
        return ExistingPrompt(
            path=prompt_file, metadata={}, body=normalized, frontmatter_text=None
        )

    closing_index = None
    for index in range(1, len(lines)):
        if lines[index] == "---":
            closing_index = index
            break
    if closing_index is None:
        raise ValueError(f"Invalid frontmatter block in {prompt_file}")

    metadata_text = "\n".join(lines[1:closing_index])
    metadata = yaml.safe_load(metadata_text) if metadata_text.strip() else {}
    if metadata is None:
        metadata = {}
    if not isinstance(metadata, dict):
        raise ValueError(f"Invalid frontmatter mapping in {prompt_file}")
    body = "\n".join(lines[closing_index + 1 :])
    if body.startswith("\n"):
        body = body[1:]
    return ExistingPrompt(
        path=prompt_file,
        metadata=dict(metadata),
        body=body,
        frontmatter_text=metadata_text,
    )


def _load_existing_prompts(output: Path) -> list[ExistingPrompt]:
    return [
        _read_prompt_file(prompt_file) for prompt_file in _iter_prompt_files(output)
    ]


def _dump_prompt(metadata: dict[str, Any], body: str) -> str:
    metadata_text = yaml.safe_dump(
        metadata,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
    ).rstrip("\n")
    return _compose_prompt(metadata_text, body)


def _compose_prompt(frontmatter_text: str, body: str) -> str:
    normalized_body = body.replace("\r\n", "\n").replace("\r", "\n")
    return text_normalization.normalize_final_newline(
        "---\n" + frontmatter_text + "\n---\n\n" + normalized_body
    )


def _quoted_frontmatter_string(value: str) -> str:
    return json.dumps(value)


def _keyword_line(trigger: str) -> str:
    return f"keyword: {_quoted_frontmatter_string(trigger)}"


def _frontmatter_with_keyword(frontmatter_text: str, trigger: str) -> str | None:
    lines = frontmatter_text.split("\n")
    for index, line in enumerate(lines):
        match = re.match(r"^(?P<prefix>keyword\s*:\s*)(?P<rest>.*)$", line)
        if match is None:
            continue

        updated_line = _keyword_line_with_existing_format(match, trigger)
        if updated_line is None:
            return None
        lines[index] = updated_line
        return "\n".join(lines)

    lines.append(_keyword_line(trigger))
    return "\n".join(lines)


def _keyword_line_with_existing_format(
    match: re.Match[str], trigger: str
) -> str | None:
    rest = match.group("rest")
    if rest.lstrip().startswith(("|", ">")):
        return None

    _value, space, comment = _split_plain_value_and_comment(rest)
    return (
        f'{match.group("prefix")}{_quoted_frontmatter_string(trigger)}{space}{comment}'
    )


def _split_plain_value_and_comment(rest: str) -> tuple[str, str, str]:
    quote: str | None = None
    escaped = False
    for index, character in enumerate(rest):
        if escaped:
            escaped = False
            continue
        if quote == '"' and character == "\\":
            escaped = True
            continue
        if character in {"'", '"'}:
            if quote is None:
                quote = character
                continue
            if quote == character:
                quote = None
                continue
        if quote is not None or character != "#":
            continue
        if index > 0 and rest[index - 1] not in {" ", "\t"}:
            continue

        space_start = index
        while space_start > 0 and rest[space_start - 1] in {" ", "\t"}:
            space_start -= 1
        return rest[:space_start], rest[space_start:index], rest[index:]

    return rest, "", ""


def _render_merged_prompt(existing: ExistingPrompt, trigger: str, body: str) -> str:
    existing_keyword = str(existing.metadata.get("keyword", ""))
    if existing.frontmatter_text is not None and existing_keyword == trigger:
        return _compose_prompt(existing.frontmatter_text, body)
    metadata = dict(existing.metadata)
    metadata["keyword"] = trigger
    if existing.frontmatter_text is not None:
        frontmatter_text = _frontmatter_with_keyword(existing.frontmatter_text, trigger)
        if frontmatter_text is not None:
            return _compose_prompt(frontmatter_text, body)

    return _dump_prompt(metadata, body)


def _match_existing_prompt(
    match: dict, existing_prompts: list[ExistingPrompt]
) -> ExistingPrompt | None:
    trigger = str(match["trigger"])
    trigger_matches = [
        prompt
        for prompt in existing_prompts
        if str(prompt.metadata.get("keyword", "")) == trigger
    ]
    if len(trigger_matches) > 1:
        paths = ", ".join(str(prompt.path) for prompt in trigger_matches)
        raise ValueError(
            f"Ambiguous Espanso import match for trigger {trigger!r}: "
            f"multiple Markdown prompts have that keyword: {paths}"
        )
    if trigger_matches:
        return trigger_matches[0]

    prompt_id = _normalize_id(trigger)
    stem_matches = [
        prompt for prompt in existing_prompts if prompt.path.stem == prompt_id
    ]
    if len(stem_matches) > 1:
        paths = ", ".join(str(prompt.path) for prompt in stem_matches)
        raise ValueError(
            f"Ambiguous Espanso import match for trigger {trigger!r}: "
            f"multiple Markdown prompt filenames match {prompt_id!r}: {paths}"
        )
    if stem_matches:
        return stem_matches[0]
    return None


def _merge_simple_matches(
    entries: list[tuple[dict, str]], output: Path, used_ids: set[str]
) -> tuple[int, set[Path], list[str]]:
    existing_prompts = _load_existing_prompts(output)
    matched_paths: set[Path] = set()
    existing_updates: list[tuple[ExistingPrompt, str, str]] = []
    new_prompts: list[tuple[str, str]] = []
    warnings: list[str] = []

    for match, _raw_block in entries:
        if not is_simple_match(match):
            continue
        trigger = str(match["trigger"])
        replace = _normalize_replace(match["replace"])
        existing = _match_existing_prompt(match, existing_prompts)
        if existing is None:
            new_prompts.append((trigger, replace))
            continue
        if existing.path in matched_paths:
            raise ValueError(
                f"Ambiguous Espanso import match for trigger {trigger!r}: "
                f"multiple Espanso matches map to {existing.path}"
            )
        matched_paths.add(existing.path)
        existing_updates.append((existing, trigger, replace))

    for existing, trigger, replace in existing_updates:
        existing.path.write_text(
            _render_merged_prompt(existing, trigger, replace), encoding="utf-8"
        )

    for trigger, replace in new_prompts:
        prompt_id = _unique_id(_normalize_id(trigger), used_ids)
        (output / f"{prompt_id}.md").write_text(
            _fresh_prompt_content(prompt_id, trigger, replace), encoding="utf-8"
        )

    for existing in existing_prompts:
        if existing.path not in matched_paths:
            warning = (
                f"Warning: Orphan prompt has no matching Espanso source entry; "
                f"kept {existing.path}"
            )
            warnings.append(warning)
            print(warning, file=sys.stderr)
    return len(existing_updates) + len(new_prompts), matched_paths, warnings


def import_espanso(
    input_path: str, output_dir: str, merge: bool = False
) -> ImportResult:
    package_path = espanso_lint.resolve_package_yml(input_path)
    diagnostics = espanso_lint.lint_espanso_package(package_path)
    if diagnostics:
        raise ValueError(espanso_lint.format_diagnostics(diagnostics))

    entries = _parse_espanso_package(package_path)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    package_dir = resolve_espanso_package_dir(input_path)
    _copied_metadata, metadata_warnings = import_espanso_metadata_assets(
        package_dir, output
    )
    raw_dir = output / "imported_raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    used_ids = _seed_used_ids(output)
    next_raw_index = _next_raw_index(raw_dir)
    converted = 0
    raw_fallback = 0
    warnings: list[str] = [*metadata_warnings]

    if merge:
        converted, _matched_paths, merge_warnings = _merge_simple_matches(
            entries, output, used_ids
        )
        warnings.extend(merge_warnings)
    else:
        for match, _raw_block in entries:
            if not is_simple_match(match):
                continue
            trigger = str(match["trigger"])
            replace = _normalize_replace(match["replace"])
            prompt_id = _unique_id(_normalize_id(trigger), used_ids)
            content = _fresh_prompt_content(prompt_id, trigger, replace)
            (output / f"{prompt_id}.md").write_text(content, encoding="utf-8")
            converted += 1

    for index, (match, raw_block) in enumerate(entries, start=1):
        if is_simple_match(match):
            continue
        raw_name = f"match-{next_raw_index}.yml"
        next_raw_index += 1
        (raw_dir / raw_name).write_text(raw_block, encoding="utf-8")
        raw_fallback += 1
        keys = sorted(match.keys())
        unsupported = sorted(set(keys) - _SIMPLE_KEYS)
        print(
            f"Warning: Unsupported match in {package_path} at index {index}; fields={unsupported}. Saved raw YAML to {raw_dir / raw_name}",
            file=sys.stderr,
        )

    print(
        f"Import summary: total={len(entries)} converted={converted} raw_fallback={raw_fallback}"
    )
    return ImportResult(
        total=len(entries),
        converted=converted,
        raw_fallback=raw_fallback,
        warnings=warnings,
    )
