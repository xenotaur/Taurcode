import argparse
import sys
from typing import List, Optional

from .espanso_export import export_espanso
from .espanso_import import import_espanso
from .espanso_lint import format_diagnostics, lint_espanso_package
from .prompt_loader import load_prompts
from .validate import validate_prompts

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

    import_parser = subparsers.add_parser("import")
    import_subparsers = import_parser.add_subparsers(dest="target", required=True)

    import_espanso_parser = import_subparsers.add_parser("espanso")
    import_espanso_parser.add_argument("--input", required=True)
    import_espanso_parser.add_argument("--output", default=IMPORT_STAGING_DIR)

    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("--prompts", default=CANONICAL_PROMPTS_DIR)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "export" and args.target == "espanso":
            prompts = load_prompts(args.prompts)
            validate_prompts(prompts)
            export_espanso(prompts, args.output, source_dir=args.prompts)
            return 0
        if args.command == "lint" and args.target == "espanso":
            diagnostics = lint_espanso_package(args.input)
            if diagnostics:
                print(format_diagnostics(diagnostics), file=sys.stderr)
                return 1
            print(f"Espanso lint passed: {args.input}")
            return 0
        if args.command == "import" and args.target == "espanso":
            import_espanso(args.input, args.output)
            return 0
        if args.command == "validate":
            prompts = load_prompts(args.prompts)
            validate_prompts(prompts)
            print(f"Validation passed: {len(prompts)} prompt(s) in {args.prompts}")
            return 0
    except (OSError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    parser.error("Unsupported command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
