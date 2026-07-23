import json
import shutil
from pathlib import Path

from taurcode import espanso_lint, espanso_metadata, prompt_model, text_normalization

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


def export_espanso_metadata_assets(
    prompt_collection_dir: str | Path | None, output: Path
) -> set[str]:
    metadata_dir = None
    if prompt_collection_dir is not None:
        candidate = Path(prompt_collection_dir) / "espanso"
        if candidate.is_dir():
            metadata_dir = candidate

    copied: set[str] = set()
    for asset_name in _METADATA_ASSETS:
        destination = output / asset_name
        source = metadata_dir / asset_name if metadata_dir is not None else None
        if source is not None and source.is_file():
            shutil.copyfile(source, destination)
            copied.add(asset_name)
        elif destination.is_file() or destination.is_symlink():
            destination.unlink()
    return copied


def _load_manifest_for_readme(output: Path, package_name: str) -> dict:
    manifest_path = output / "_manifest.yml"
    if manifest_path.is_file():
        try:
            manifest_text = manifest_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return {}
        return espanso_metadata.parse_manifest_text(manifest_text)
    return espanso_metadata.generate_default_manifest(package_name)


def export_espanso(
    prompts: list[prompt_model.Prompt], output_dir: str, source_dir: str | None = None
) -> espanso_lint.LintResult:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    package_name = output.name

    package_lines = ["matches:"]
    for prompt in prompts:
        package_lines.append(f"  - trigger: {_yaml_quote(prompt.keyword)}")
        package_lines.append("    replace: |")
        package_lines.append(_as_block(prompt.body).rstrip("\n"))
        if prompt.targets.get("espanso", {}).get("force_clipboard") is True:
            package_lines.append("    force_clipboard: true")

    package_content = "\n".join(package_lines) + "\n"

    default_manifest = espanso_metadata.generate_default_manifest(package_name)
    manifest_content = espanso_metadata.manifest_to_yaml(default_manifest)

    (output / "package.yml").write_text(package_content, encoding="utf-8")

    copied_metadata = export_espanso_metadata_assets(source_dir, output)
    if "_manifest.yml" not in copied_metadata:
        (output / "_manifest.yml").write_text(manifest_content, encoding="utf-8")
    if "README.md" not in copied_metadata:
        readme_manifest = _load_manifest_for_readme(output, package_name)
        readme_content = espanso_metadata.generate_default_readme(
            package_name, readme_manifest
        )
        readme_content = text_normalization.normalize_final_newline(readme_content)
        (output / "README.md").write_text(readme_content, encoding="utf-8")

    result = espanso_lint.lint_espanso_package_build(output)
    if result.has_errors():
        raise ValueError(espanso_lint.format_lint_result(result))
    return result
