import json
import shutil
from pathlib import Path

from .prompt_model import Prompt

_METADATA_ASSETS = ("_manifest.yml", "README.md", "LICENSE")


def _yaml_quote(value: str) -> str:
    return json.dumps(value)


def _as_block(value: str, indent: str = "      ") -> str:
    lines = value.split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]
    if not lines:
        return f"{indent}\n"
    return "\n".join(f"{indent}{line}" for line in lines) + "\n"


def _copy_metadata_assets(source_dir: str | None, output: Path) -> set[str]:
    if source_dir is None:
        return set()

    metadata_dir = Path(source_dir) / "espanso"
    if not metadata_dir.is_dir():
        return set()

    copied: set[str] = set()
    for asset_name in _METADATA_ASSETS:
        source = metadata_dir / asset_name
        if source.is_file():
            shutil.copyfile(source, output / asset_name)
            copied.add(asset_name)
    return copied


def export_espanso(
    prompts: list[Prompt], output_dir: str, source_dir: str | None = None
) -> None:
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

    copied_metadata = _copy_metadata_assets(source_dir, output)
    if "_manifest.yml" not in copied_metadata:
        (output / "_manifest.yml").write_text(manifest_content, encoding="utf-8")
