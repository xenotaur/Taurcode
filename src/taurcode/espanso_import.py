import re
import sys
from pathlib import Path

import yaml

from . import espanso_lint

_SIMPLE_KEYS = {"trigger", "replace"}


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


def _seed_used_ids(output: Path) -> set[str]:
    used: set[str] = set()
    if output.exists():
        for md in output.glob("*.md"):
            used.add(md.stem)
    return used


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


def import_espanso(input_path: str, output_dir: str) -> None:
    package_path = espanso_lint.resolve_package_yml(input_path)
    diagnostics = espanso_lint.lint_espanso_package(package_path)
    if diagnostics:
        raise ValueError(espanso_lint.format_diagnostics(diagnostics))

    entries = _parse_espanso_package(package_path)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    raw_dir = output / "imported_raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    used_ids = _seed_used_ids(output)
    next_raw_index = _next_raw_index(raw_dir)
    converted = 0
    raw_fallback = 0

    for index, (match, raw_block) in enumerate(entries, start=1):
        if is_simple_match(match):
            trigger = str(match["trigger"])
            replace = str(match["replace"]).replace("\r\n", "\n").replace("\r", "\n")
            prompt_id = _unique_id(_normalize_id(trigger), used_ids)
            content = (
                "---\n"
                f"id: {prompt_id}\n"
                f"name: {_derive_name(prompt_id)}\n"
                "description: Imported from Espanso\n"
                f'keyword: "{trigger}"\n'
                "---\n\n"
                f"{replace}" + ("" if replace.endswith("\n") else "\n")
            )
            (output / f"{prompt_id}.md").write_text(content, encoding="utf-8")
            converted += 1
        else:
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
