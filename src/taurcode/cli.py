import argparse

from .espanso_export import export_espanso
from .prompt_loader import load_prompts
from .validate import validate_prompts


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="taurcode")
    subparsers = parser.add_subparsers(dest="command", required=True)

    export_parser = subparsers.add_parser("export")
    export_subparsers = export_parser.add_subparsers(dest="target", required=True)

    espanso = export_subparsers.add_parser("espanso")
    espanso.add_argument("--prompts", default="prompts")
    espanso.add_argument("--output", default="build/espanso/taurcode")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "export" and args.target == "espanso":
        prompts = load_prompts(args.prompts)
        validate_prompts(prompts)
        export_espanso(prompts, args.output)
        return 0

    parser.error("Unsupported command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
