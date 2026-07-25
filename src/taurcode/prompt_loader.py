from pathlib import Path

import frontmatter
import yaml

from taurcode import prompt_model

_RESERVED_PROMPT_DIRS = {"espanso"}


def _is_reserved_prompt_file(prompt_file: Path, directory: Path) -> bool:
    relative_parts = prompt_file.relative_to(directory).parts
    return bool(relative_parts and relative_parts[0] in _RESERVED_PROMPT_DIRS)


_FRONTMATTER_DELIMITER = "---"
_FRONTMATTER_CLOSING = f"\n{_FRONTMATTER_DELIMITER}\n"


def extract_prompt_body(text: str) -> str:
    # Uses find()/slicing instead of split()/join() to avoid allocating an
    # intermediate list of lines for large prompt files. See .jules/bolt.md
    # for the perf rationale; kept here brief since benchmarks age quickly.
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    if not (
        normalized == _FRONTMATTER_DELIMITER
        or normalized.startswith(_FRONTMATTER_DELIMITER + "\n")
    ):
        return normalized

    end_frontmatter = normalized.find(_FRONTMATTER_CLOSING, len(_FRONTMATTER_DELIMITER))
    if end_frontmatter != -1:
        body = normalized[end_frontmatter + len(_FRONTMATTER_CLOSING) :]
        if body.startswith("\n"):
            return body[1:]
        return body

    if normalized.endswith("\n" + _FRONTMATTER_DELIMITER):
        return ""

    return normalized


def _extract_prompt_body(text: str) -> str:
    return extract_prompt_body(text)


def load_prompts(prompts_dir: str) -> list[prompt_model.Prompt]:
    directory = Path(prompts_dir)
    prompts: list[prompt_model.Prompt] = []

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
        body = extract_prompt_body(text)
        prompts.append(
            prompt_model.Prompt(
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
