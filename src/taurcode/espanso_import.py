import re
import sys
from pathlib import Path

_SIMPLE_KEYS = {"trigger", "replace"}
_BLOCK_SCALAR_RE = re.compile(r"^[|>][-+]?$")


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


def _unquote(value: str) -> str:
    value = value.strip()
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    return value


def _folded(lines: list[str]) -> str:
    out: list[str] = []
    pending = False
    for line in lines:
        if line == "":
            out.append("\n")
            pending = False
        else:
            if out and pending:
                out.append(" ")
            out.append(line)
            pending = True
    return "".join(out)


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


def _parse_espanso_package(package_path: Path) -> list[tuple[dict, str]]:
    text = package_path.read_text(encoding="utf-8")
    if "matches:" not in text:
        raise ValueError(
            "Invalid Espanso package.yml: expected top-level 'matches' list"
        )

    lines = text.splitlines(keepends=True)
    entries: list[tuple[dict, str]] = []
    in_matches = False
    current_block: list[str] = []
    current_dict: dict = {}
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not in_matches:
            if stripped == "matches:":
                in_matches = True
            i += 1
            continue

        if not line.startswith("  ") and stripped:
            if current_block:
                entries.append((current_dict, "".join(current_block)))
                current_block = []
            break

        if line.startswith("  - "):
            if current_block:
                entries.append((current_dict, "".join(current_block)))
            current_block = [line]
            current_dict = {}
            remainder = line[4:].strip()
            if remainder:
                if ":" not in remainder:
                    raise ValueError(
                        "Invalid Espanso package.yml: malformed match entry"
                    )
                k, v = remainder.split(":", 1)
                current_dict[k.strip()] = _unquote(v)
            i += 1
            continue

        if current_block and line.startswith("    "):
            current_block.append(line)
            if ":" in stripped and not stripped.startswith("- "):
                k, v = stripped.split(":", 1)
                key = k.strip()
                marker = v.strip()
                if _BLOCK_SCALAR_RE.match(marker):
                    block_lines: list[str] = []
                    j = i + 1
                    while j < len(lines) and lines[j].startswith("      "):
                        current_block.append(lines[j])
                        block_lines.append(lines[j][6:].rstrip("\n"))
                        j += 1
                    current_dict[key] = (
                        _folded(block_lines)
                        if marker.startswith(">")
                        else "\n".join(block_lines)
                    )
                    i = j
                    continue
                current_dict[key] = _unquote(v)
            i += 1
            continue

        i += 1

    if current_block:
        entries.append((current_dict, "".join(current_block)))

    return entries


def import_espanso(input_path: str, output_dir: str) -> None:
    input_obj = Path(input_path)
    package_path = input_obj / "package.yml" if input_obj.is_dir() else input_obj
    if not package_path.exists() or package_path.name != "package.yml":
        raise ValueError(
            "Input must be an Espanso package.yml file or a directory containing package.yml"
        )

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
