import argparse
import sys
from typing import List, Optional

from taurcode import (
    espanso_export,
    espanso_import,
    espanso_install,
    espanso_lint,
    prompt_format,
    prompt_lint,
    prompt_loader,
    roundtrip,
    validate,
)

CANONICAL_PROMPTS_DIR = "prompts/taurcode"
IMPORT_STAGING_DIR = "prompts/imported"
ESPANSO_OUTPUT_DIR = "build/espanso/taurcode"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="taurcode")
    subparsers = parser.add_subparsers(dest="command", required=True)

    export_parser = subparsers.add_parser("export")
    export_subparsers = export_parser.add_subparsers(dest="target", required=True)

    espanso = export_subparsers.add_parser("espanso")
    espanso.add_argument("--prompts", default=CANONICAL_PROMPTS_DIR)
    espanso.add_argument("--output", default=ESPANSO_OUTPUT_DIR)

    lint_parser = subparsers.add_parser("lint")
    lint_subparsers = lint_parser.add_subparsers(dest="target", required=True)

    lint_espanso_parser = lint_subparsers.add_parser("espanso")
    lint_espanso_parser.add_argument("--input", required=True)

    lint_prompts_parser = lint_subparsers.add_parser("prompts")
    lint_prompts_parser.add_argument("--prompts", default=CANONICAL_PROMPTS_DIR)

    format_parser = subparsers.add_parser("format")
    format_subparsers = format_parser.add_subparsers(dest="target", required=True)

    format_prompts_parser = format_subparsers.add_parser("prompts")
    format_prompts_parser.add_argument("--prompts", default=CANONICAL_PROMPTS_DIR)
    format_prompts_parser.add_argument(
        "--check",
        action="store_true",
        help="Check whether prompt files are formatted without writing changes",
    )

    roundtrip_parser = subparsers.add_parser("roundtrip")
    roundtrip_subparsers = roundtrip_parser.add_subparsers(dest="target", required=True)

    roundtrip_espanso_parser = roundtrip_subparsers.add_parser("espanso")
    roundtrip_espanso_parser.add_argument("--input", required=True)
    roundtrip_espanso_parser.add_argument("--prompts", default=CANONICAL_PROMPTS_DIR)

    install_parser = subparsers.add_parser("install")
    install_subparsers = install_parser.add_subparsers(dest="target", required=True)

    install_espanso_parser = install_subparsers.add_parser("espanso")
    install_espanso_parser.add_argument("--prompts", default=CANONICAL_PROMPTS_DIR)
    install_espanso_parser.add_argument(
        "--packages-dir",
        default=None,
        help="Espanso match-packages directory (defaults to the macOS location)",
    )
    install_espanso_parser.add_argument(
        "--restart",
        action="store_true",
        help="Run 'espanso restart' after installing (requires espanso on PATH)",
    )

    import_parser = subparsers.add_parser("import")
    import_subparsers = import_parser.add_subparsers(dest="target", required=True)

    import_espanso_parser = import_subparsers.add_parser("espanso")
    import_espanso_parser.add_argument("--input", required=True)
    import_espanso_parser.add_argument("--output", default=IMPORT_STAGING_DIR)
    import_espanso_parser.add_argument(
        "--merge",
        action="store_true",
        help="Merge into existing Markdown prompts while preserving curated metadata",
    )

    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("--prompts", default=CANONICAL_PROMPTS_DIR)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "export" and args.target == "espanso":
            prompts = prompt_loader.load_prompts(args.prompts)
            validate.validate_prompts(prompts)
            result = espanso_export.export_espanso(
                prompts, args.output, source_dir=args.prompts
            )
            if result.has_warnings():
                print(espanso_lint.format_lint_result(result), file=sys.stderr)
            return 0
        if args.command == "install" and args.target == "espanso":
            prompts = prompt_loader.load_prompts(args.prompts)
            validate.validate_prompts(prompts)
            packages_dir = espanso_install.resolve_packages_dir(
                sys.platform, args.packages_dir
            )
            installed_path = espanso_install.install_espanso(
                prompts, packages_dir, source_dir=args.prompts
            )
            print(f"Installed Espanso package: {installed_path}")
            if args.restart:
                espanso_install.restart_espanso()
                print("Restarted espanso.")
            else:
                print("Run 'espanso restart' to activate the updated package.")
            return 0
        if args.command == "lint" and args.target == "espanso":
            package_path = espanso_lint.resolve_package_yml(args.input)
            diagnostics = espanso_lint.lint_espanso_package(package_path)
            metadata_result = espanso_lint.LintResult(errors=[], warnings=[])
            if not diagnostics:
                metadata_result = espanso_lint.lint_espanso_package_build(
                    package_path.parent
                )
            result = espanso_lint.LintResult(
                errors=[*diagnostics, *metadata_result.errors],
                warnings=metadata_result.warnings,
            )
            if result.has_errors() or result.has_warnings():
                print(espanso_lint.format_lint_result(result), file=sys.stderr)
            if result.has_errors():
                return 1
            print(f"Espanso lint passed: {args.input}")
            return 0
        if args.command == "lint" and args.target == "prompts":
            result = prompt_lint.lint_prompt_package(args.prompts)
            if result.has_errors() or result.has_warnings():
                print(espanso_lint.format_lint_result(result), file=sys.stderr)
            if result.has_errors():
                return 1
            print(f"Prompt lint passed: {args.prompts}")
            return 0
        if args.command == "format" and args.target == "prompts":
            result = prompt_format.format_prompt_package(args.prompts, check=args.check)
            for changed_file in result.changed_files:
                action = "Would format" if args.check else "Formatted"
                print(f"{action}: {changed_file}")
            if args.check and result.has_changes():
                return 1
            print(f"Prompt format passed: {args.prompts}")
            return 0
        if args.command == "import" and args.target == "espanso":
            espanso_import.import_espanso(args.input, args.output, merge=args.merge)
            return 0
        if args.command == "roundtrip" and args.target == "espanso":
            comparison = roundtrip.compare_espanso_roundtrip(args.input, args.prompts)
            print(roundtrip.format_roundtrip_summary(comparison))
            if comparison.passed():
                return 0
            return 1
        if args.command == "validate":
            prompts = prompt_loader.load_prompts(args.prompts)
            validate.validate_prompts(prompts)
            print(f"Validation passed: {len(prompts)} prompt(s) in {args.prompts}")
            return 0
    except (OSError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    parser.error("Unsupported command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
