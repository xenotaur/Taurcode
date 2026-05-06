# Taurcode
Taurcode is a set of prompts for AI-generated coding with tools to format them for various injection systems like Espanso.

## Canonical prompts
The checked-in Taurcode prompt corpus lives under `prompts/taurcode/`. This directory is the authoritative source of truth for the Taurcode prompt package.

Espanso package files are generated from that corpus into `build/espanso/taurcode/`; Espanso is an export target, not the canonical storage location.

Example prompt:

```markdown
---
id: test-prompt
name: Test Prompt
description: A test prompt
keyword: ":tc-test"
---

This is a test prompt body.
```

## Import from Espanso
Use the CLI to import an Espanso package into a staging directory:

```bash
taurcode import espanso --input espanso/package/package.yml --output prompts/imported
```

For local Espanso package debugging, run the preflight linter first and then import:

```bash
taurcode lint espanso --input ~/Library/Application\ Support/espanso/match/packages/taurcode/
taurcode import espanso --input ~/Library/Application\ Support/espanso/match/packages/taurcode/ --output prompts/imported
```

Import behavior:

- Simple matches with only `trigger` and `replace` are converted into Markdown prompt files in the chosen output directory.
- `replace` block scalars (`|` literal and `>` folded) are preserved according to YAML parsing semantics.
- Unsupported or complex matches are preserved under `<output>/imported_raw/*.yml`.
- Raw fallback keeps unsupported match YAML content so prompt text is not lost.
- The importer prints a summary with total, converted, and raw fallback match counts.

Suggested migration workflow:

```bash
taurcode import espanso --input <path-to-package.yml-or-directory> --output prompts/imported
# Review and curate staged imports into prompts/taurcode/ before treating them as canonical.
taurcode validate --prompts prompts/taurcode
taurcode export espanso --prompts prompts/taurcode --output build/espanso/taurcode
```

In this workflow, `prompts/imported/` is only a temporary staging area that records import provenance. Curated prompts belong in `prompts/taurcode/`.

### Espanso preflight diagnostics

`taurcode lint espanso --input <path>` accepts either a `package.yml` file or a package directory containing `package.yml`. The same preflight diagnostics run automatically before `taurcode import espanso` parses package contents.

The linter checks for:

- missing `package.yml` when the input is a directory
- invalid UTF-8 bytes
- parser-sensitive invisible Unicode line break characters: `U+2028 LINE SEPARATOR`, `U+2029 PARAGRAPH SEPARATOR`, and `U+0085 NEXT LINE`
- malformed YAML, including parser line and column information when PyYAML provides it

Invisible Unicode line separators can be troublesome because some tools may treat them like line breaks while YAML parsers reject them or report confusing locations. Taurcode reports the file, line, column, character name, and a manual fix suggestion. For example, replace an invisible separator inside a block scalar with a normal newline and keep the following content indented under the scalar.

Taurcode does not silently rewrite, normalize, or repair source Espanso files. Fix the source package manually, rerun `taurcode lint espanso`, and then rerun the import.

## Export to Espanso
Use the CLI to export canonical prompts to an Espanso package:

```bash
taurcode export espanso --prompts prompts/taurcode --output build/espanso/taurcode
```

Generated output:

- `build/espanso/taurcode/package.yml`
- `build/espanso/taurcode/_manifest.yml`

Note: installation into a local Espanso configuration is currently manual.

## Validate prompts
Validate all canonical prompt files before export:

```bash
taurcode validate --prompts prompts/taurcode
```

Validation rules:

- Prompt files are loaded from the provided directory recursively.
- Only `.md` files are considered.
- Required fields: `id`, `name`, `description`, `keyword`, `body`.
- `id` values must be unique.
- `keyword` values must be unique.
- `keyword` must start with `:`.
- `body` must be non-empty.

Common errors:

- `Duplicate keyword ':tc-test' found in prompts/taurcode/a.md and prompts/taurcode/b.md`
- `Missing required field 'id' in prompts/taurcode/example.md`

Export commands run the same validation step and fail if prompt data is invalid.

## Development workflow

Run operability checks from repository root:

```bash
scripts/develop
scripts/lint
scripts/format
scripts/test
scripts/coverage
taurcode --help
```

Testing conventions:

- Test framework: `unittest`
- Discovery pattern: `*_test.py`
- `scripts/test` fails if zero tests are discovered.
