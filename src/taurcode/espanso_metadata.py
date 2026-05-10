from typing import Any

import yaml

HOMEPAGE = "https://github.com/xenotaur/Taurcode"


def title_from_package_name(package_name: str) -> str:
    words = package_name.replace("_", "-").split("-")
    return " ".join(word.capitalize() for word in words if word) or package_name


def generate_default_manifest(package_name: str) -> dict[str, Any]:
    return {
        "name": package_name,
        "title": title_from_package_name(package_name),
        "description": "Generated prompt package",
        "version": "0.1.0",
        "author": "Taurcode",
        "tags": [],
        "homepage": HOMEPAGE,
    }


def manifest_to_yaml(manifest: dict[str, Any]) -> str:
    return yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True)


def parse_manifest_text(manifest_text: str) -> dict[str, Any]:
    try:
        parsed = yaml.safe_load(manifest_text)
    except yaml.YAMLError:
        return {}
    if isinstance(parsed, dict):
        return parsed
    return {}


def manifest_title(package_name: str, manifest: dict[str, Any]) -> str:
    title = manifest.get("title")
    if isinstance(title, str) and title.strip():
        return title.strip()
    return title_from_package_name(package_name)


def generate_default_readme(package_name: str, manifest: dict[str, Any]) -> str:
    title = manifest_title(package_name, manifest)
    return f"# {title}\n\nGenerated Espanso package from Taurcode prompt sources.\n"
