import json
from pathlib import Path

from .prompt_model import Prompt


def _yaml_quote(value: str) -> str:
    return json.dumps(value)


def _as_block(value: str, indent: str = "      ") -> str:
    lines = value.split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]
    if not lines:
        return f"{indent}\n"
    return "\n".join(f"{indent}{line}" for line in lines) + "\n"


def export_espanso(prompts: list[Prompt], output_dir: str) -> None:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    package_lines = ["matches:"]
    for prompt in prompts:
        package_lines.append(f"  - trigger: {_yaml_quote(prompt.keyword)}")
        package_lines.append("    replace: |")
        package_lines.append(_as_block(prompt.body).rstrip("\n"))

    package_content = "\n".join(package_lines) + "\n"

    manifest_content = """name: taurcode
title: Taurcode
description: Generated prompt package
version: 0.1.0
author: Taurcode
tags: []
homepage: https://github.com/xenotaur/Taurcode
"""

    (output / "package.yml").write_text(package_content, encoding="utf-8")
    (output / "_manifest.yml").write_text(manifest_content, encoding="utf-8")
