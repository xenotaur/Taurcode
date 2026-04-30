# Taurcode
Taurcode is a set of prompts for AI-generated coding with tools to format them for various injection systems like Espanso.

## Canonical prompts
Canonical prompts are authored in Markdown files under `prompts/*.md` with YAML frontmatter metadata.

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
Use the CLI to import an Espanso package into canonical prompts:

```bash
PYTHONPATH=src python -m taurcode.cli import espanso --input espanso/package/package.yml --output prompts
```

Import behavior:

- Simple matches with only `trigger` and `replace` are converted into `prompts/*.md`.
- `replace` block scalars (`|` literal and `>` folded) are preserved according to YAML parsing semantics.
- Unsupported or complex matches are preserved under `prompts/imported_raw/*.yml`.
- Raw fallback keeps unsupported match YAML content so prompt text is not lost.
- The importer prints a summary with total, converted, and raw fallback match counts.

Suggested migration workflow:

```bash
PYTHONPATH=src python -m taurcode.cli import espanso --input <path-to-package.yml-or-directory> --output prompts
PYTHONPATH=src python -m taurcode.cli validate --prompts prompts
PYTHONPATH=src python -m taurcode.cli export espanso --prompts prompts --output build/espanso/taurcode
```

## Export to Espanso
Use the CLI to export canonical prompts to an Espanso package:

```bash
PYTHONPATH=src python -m taurcode.cli export espanso --prompts prompts --output build/espanso/taurcode
```

Generated output:

- `build/espanso/taurcode/package.yml`
- `build/espanso/taurcode/_manifest.yml`

Note: installation into a local Espanso configuration is currently manual.

## Validate prompts
Validate all prompt files before export:

```bash
PYTHONPATH=src python -m taurcode.cli validate --prompts prompts
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

- `Duplicate keyword ':tc-test' found in prompts/a.md and prompts/b.md`
- `Missing required field 'id' in prompts/example.md`

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
