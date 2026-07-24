"""Install a generated Espanso package into the local Espanso configuration.

This is a thin, macOS-only wrapper over `espanso_export.export_espanso`: it
resolves the platform's Espanso `match/packages` directory, derives the package
name from curated metadata, exports into a staging directory, and replaces the
live package only after the export and its build lint both succeed. Installing
is otherwise identical to exporting — the installed package is byte-for-byte
what `taurcode export espanso` would produce.
"""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Callable

from taurcode import espanso_export, espanso_metadata, prompt_model

MACOS_PACKAGES_DIR = "~/Library/Application Support/espanso/match/packages"
DEFAULT_PACKAGE_NAME = "taurcode"


class InstallError(ValueError):
    """Raised when installation cannot proceed or an external step fails.

    Subclasses `ValueError` so `cli.main`'s existing `except (OSError,
    ValueError)` handler reports it as a clean error rather than a traceback.
    """


def resolve_packages_dir(platform: str, override: str | None) -> Path:
    """Return the Espanso match-packages directory for the current platform.

    Only macOS (`platform == "darwin"`) is supported for now; every other
    platform raises `InstallError` rather than guessing a path. Both the
    default and the `override` are passed through `expanduser()` — `Path` does
    not expand a leading `~`, so skipping this would silently create a relative
    `<cwd>/~/Library/...` tree while reporting a successful install.
    """
    if platform != "darwin":
        raise InstallError(
            f"taurcode install espanso currently supports macOS only; "
            f"platform '{platform}' is not supported yet. Export with "
            f"'taurcode export espanso' and copy the package manually."
        )
    return Path(override if override is not None else MACOS_PACKAGES_DIR).expanduser()


def resolve_package_name(source_dir: str | Path | None) -> str:
    """Derive the installed package name from curated metadata.

    Returns the `name:` field of `<source_dir>/espanso/_manifest.yml` when that
    curated manifest exists, else `DEFAULT_PACKAGE_NAME`. The name must be
    derived from the manifest rather than imposed on it: export copies a curated
    `_manifest.yml` verbatim while `lint_espanso_package_build` derives the
    expected name from the output directory name, so any disagreement is a hard
    `manifest-name-mismatch` lint error.
    """
    if source_dir is not None:
        manifest_path = Path(source_dir) / "espanso" / "_manifest.yml"
        if manifest_path.is_file():
            try:
                manifest_text = manifest_path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                return DEFAULT_PACKAGE_NAME
            manifest = espanso_metadata.parse_manifest_text(manifest_text)
            name = manifest.get("name")
            if isinstance(name, str) and name.strip():
                return name.strip()
    return DEFAULT_PACKAGE_NAME


def install_espanso(
    prompts: list[prompt_model.Prompt],
    packages_dir: str | Path,
    source_dir: str | None = None,
) -> Path:
    """Export the prompts into `<packages_dir>/<name>/`, staging first.

    The export runs into a staging directory whose own basename equals the
    resolved package name (staging at `<tmp>/<name>/`, not `<tmp>/`, so the
    `output.name`-derived build lint sees the right name). The live package is
    replaced only after `export_espanso` returns successfully — which means its
    build lint passed. If the export raises, the previously installed package is
    left byte-identical and no staging directory is left behind. Returns the
    installed package path.
    """
    packages_dir = Path(packages_dir)
    name = resolve_package_name(source_dir)
    packages_dir.mkdir(parents=True, exist_ok=True)
    target = packages_dir / name

    # The staging parent lives inside packages_dir so the final swap is a
    # same-filesystem os.replace. Dot-prefixed so a crash-leftover stays out of
    # Espanso's way.
    staging_parent = Path(
        tempfile.mkdtemp(prefix=".taurcode-install-", dir=packages_dir)
    )
    try:
        staged_package = staging_parent / name
        # export_espanso writes files then runs its build lint, raising on
        # failure; because this targets staging, a failure never touches target.
        espanso_export.export_espanso(
            prompts, str(staged_package), source_dir=source_dir
        )

        # Move any existing install aside first: os.replace cannot rename a
        # directory onto a non-empty directory. The backup lands inside
        # staging_parent so the finally clause deletes it either way.
        if target.exists():
            os.replace(target, staging_parent / f"{name}.backup")
        os.replace(staged_package, target)
        return target
    finally:
        shutil.rmtree(staging_parent, ignore_errors=True)


def restart_espanso(
    runner: Callable[..., "subprocess.CompletedProcess"] = subprocess.run,
    which: Callable[[str], str | None] = shutil.which,
) -> None:
    """Restart Espanso so a freshly installed package takes effect.

    `runner` and `which` are injectable so tests never shell out to a real
    `espanso` binary. A missing binary or a nonzero exit is an `InstallError`,
    not a traceback.
    """
    if which("espanso") is None:
        raise InstallError(
            "espanso binary not found on PATH; cannot restart. "
            "Run 'espanso restart' manually once it is installed."
        )
    result = runner(["espanso", "restart"])
    if result.returncode != 0:
        raise InstallError(
            f"'espanso restart' failed with exit code {result.returncode}."
        )
