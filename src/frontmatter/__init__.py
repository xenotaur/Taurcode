"""Minimal frontmatter-compatible loader for offline environments."""

from dataclasses import dataclass
from pathlib import Path
from typing import Union


@dataclass
class Post:
    metadata: dict
    content: str


def _parse_scalar(value: str):
    value = value.strip()
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    if value == "[]":
        return []
    return value


def loads(text: str) -> Post:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = normalized.split("\n")

    if not lines or lines[0] != "---":
        return Post(metadata={}, content=normalized)

    closing_index = None
    for i in range(1, len(lines)):
        if lines[i] == "---":
            closing_index = i
            break

    if closing_index is None:
        raise ValueError("Invalid frontmatter block")

    fm_block = lines[1:closing_index]
    content = "\n".join(lines[closing_index + 1 :])
    metadata = {}
    for line in fm_block:
        if not line.strip():
            continue
        key, _, value = line.partition(":")
        metadata[key.strip()] = _parse_scalar(value)
    return Post(metadata=metadata, content=content)


def load(path: Union[str, Path]) -> Post:
    return loads(Path(path).read_text(encoding="utf-8"))
