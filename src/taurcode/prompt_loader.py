from pathlib import Path
from typing import List

import frontmatter

from .prompt_model import Prompt


def load_prompts(prompts_dir: str) -> List[Prompt]:
    directory = Path(prompts_dir)
    prompts: List[Prompt] = []

    for prompt_file in sorted(directory.rglob("*.md")):
        if not prompt_file.is_file():
            continue
        post = frontmatter.load(prompt_file)
        body = post.content.replace("\r\n", "\n")
        if body.startswith("\n"):
            body = body[1:]
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
