from pathlib import Path
from typing import List

import frontmatter
import yaml

from .prompt_model import Prompt

_RESERVED_PROMPT_DIRS = {"espanso"}


def _is_reserved_prompt_file(prompt_file: Path, directory: Path) -> bool:
    relative_parts = prompt_file.relative_to(directory).parts
    return bool(relative_parts and relative_parts[0] in _RESERVED_PROMPT_DIRS)


def _extract_prompt_body(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
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


def load_prompts(prompts_dir: str) -> List[Prompt]:
    directory = Path(prompts_dir)
    prompts: List[Prompt] = []

    for prompt_file in sorted(directory.rglob("*.md")):
        if not prompt_file.is_file():
            continue
        if _is_reserved_prompt_file(prompt_file, directory):
            continue
        text = prompt_file.read_text(encoding="utf-8")
        try:
            post = frontmatter.loads(text)
        except yaml.YAMLError as error:
            raise ValueError(
                f"Malformed YAML frontmatter in {prompt_file}: {error}"
            ) from error
        body = _extract_prompt_body(text)
        prompts.append(
            Prompt(
                id=post.metadata.get("id", ""),
                name=post.metadata.get("name", ""),
                description=post.metadata.get("description", ""),
                keyword=post.metadata.get("keyword", ""),
                body=body,
                source=str(prompt_file),
                targets=post.metadata.get("targets", {}) or {},
            )
        )

    prompts.sort(key=lambda prompt: (prompt.id, prompt.source))
    return prompts
