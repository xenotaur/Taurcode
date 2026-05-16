# Canonical Prompt Format

Canonical Taurcode prompts are Markdown files with YAML frontmatter. The checked-in Taurcode prompt corpus lives under `prompts/taurcode/`.

## Basic shape

```markdown
---
id: debug
name: Debug an Issue
description: Debug an Issue
keyword: ":debug"
targets:
  espanso:
    enabled: true
    package: taurcode
---

Prompt body text goes here.
```

## Required fields

| Field | Type | Rule |
| --- | --- | --- |
| `id` | string | Required and unique within the prompt package. |
| `name` | string | Required human-readable name. |
| `description` | string | Required human-readable description. |
| `keyword` | string | Required, unique, and must start with `:`. Export maps this to Espanso `trigger`. |
| body | Markdown text | Required and non-empty. Export maps this to Espanso `replace`. |

## Optional fields

`targets` may be authored as a nested mapping. Taurcode loads it into prompt objects for target-specific metadata, but the current Espanso exporter validates and exports the core prompt fields.

Unknown or user-defined frontmatter fields are allowed. Import and formatting workflows should preserve them where practical instead of treating them as errors.

## Prompt discovery

Taurcode loads `.md` files recursively from the selected prompt directory. Reserved metadata directories such as `espanso/` are ignored during prompt discovery, validation, linting, and export because they store package-level target metadata rather than prompt content.

## Validation

Run:

```bash
taurcode validate --prompts prompts/taurcode
```

Validation checks required fields, unique `id` values, unique `keyword` values, `keyword` prefix rules, and non-empty prompt bodies. Export runs validation before writing an Espanso package.

## Prompt-source linting

Run:

```bash
taurcode lint prompts --prompts prompts/taurcode
```

Prompt-source linting checks Markdown source structure before prompt loading. Errors are objective source problems and return nonzero. Warnings call out reviewable source quality issues such as unquoted keywords, filename/keyword slug mismatches, non-standard final newlines, and wrapped descriptions.

## Formatting

Run:

```bash
taurcode format prompts --prompts prompts/taurcode --check
```

The formatter is intentionally conservative. It can quote simple unquoted `keyword` values and normalize formatted prompt files to exactly one final newline. It does not run the whole frontmatter block through a generic YAML dumper, reorder fields, wrap descriptions, or normalize prompt body whitespace beyond final newline count.

## Preferred authoring style

Keep frontmatter field order stable as `id`, `name`, `description`, `keyword`, then any user-defined extra fields such as `targets`. Quote `keyword` values because they are syntax-like and quote preservation avoids roundtrip churn.
