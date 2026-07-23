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

`targets` may be authored as a nested mapping. Taurcode loads it into prompt objects for target-specific metadata. The Espanso exporter reads one nested field from it today — `targets.espanso.force_clipboard` — and otherwise exports the core prompt fields.

| Field | Type | Rule |
| --- | --- | --- |
| `targets.espanso.force_clipboard` | boolean | Optional. When present, `taurcode validate` requires `targets` and `targets.espanso` to be mappings and `force_clipboard` to be a boolean; any other shape is a validation error. When `true`, export emits Espanso's native `force_clipboard: true` match property, forcing Clipboard-backend delivery for that match. Import round-trips the field back into this same shape on both fresh and merge import. Absent or `false` is not an error and is not emitted. |

Espanso's `Auto` backend delivers matches shorter than its `clipboard_threshold` default (100 characters) via simulated keypresses (`Inject`), which sends a trailing `\n` in the match as a real Return keypress rather than inserted text — this can prematurely submit a chat input bound to "Enter sends". `force_clipboard` lets an individual short prompt opt out of that behavior without changing the default for every other prompt. See `docs/reference/espanso-integration.md` for the mechanism, and `project/design/proposals/adopted/espanso-match-force-clipboard/00_proposal.md` for the design rationale.

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
