"""Minimal frontmatter-compatible loader for offline environments."""

from dataclasses import dataclass
from pathlib import Path


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
    if not text.startswith("---"):
        return Post(metadata={}, content=text)

    parts = text.split("\n---\n", 1)
    if len(parts) != 2:
        raise ValueError("Invalid frontmatter block")

    fm_block = parts[0].splitlines()[1:]
    content = parts[1]
    metadata = {}
    for line in fm_block:
        if not line.strip():
            continue
        key, _, value = line.partition(":")
        metadata[key.strip()] = _parse_scalar(value)
    return Post(metadata=metadata, content=content)


def load(path: str | Path) -> Post:
    return loads(Path(path).read_text(encoding="utf-8"))
