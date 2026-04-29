from pathlib import Path
from typing import List

import frontmatter

from .prompt_model import Prompt


def load_prompts(prompts_dir: str) -> List[Prompt]:
    directory = Path(prompts_dir)
    prompts: List[Prompt] = []

    for prompt_file in sorted(directory.glob("*.md")):
        post = frontmatter.load(prompt_file)
        body = post.content.replace("\r\n", "\n")
        prompts.append(
            Prompt(
                id=post.metadata.get("id", ""),
                name=post.metadata.get("name", ""),
                description=post.metadata.get("description", ""),
                keyword=post.metadata.get("keyword", ""),
                body=body,
                targets=post.metadata.get("targets", {}) or {},
            )
        )

    return prompts
