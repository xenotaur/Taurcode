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

- By default, import is a fresh staging import: simple matches with only `trigger` and `replace` are converted into new Markdown prompt files in the chosen output directory.
- Use `--merge` when importing an updated Espanso package into an existing curated prompt directory:

  ```bash
  taurcode import espanso --input build/espanso/taurcode --output prompts/taurcode --merge
  ```

- Merge import matches existing prompts first by frontmatter `keyword` matching the Espanso `trigger`, then by filename stem matching Taurcode's generated trigger slug. It does not use the curated prompt `name` as the primary key.
- For matched Markdown prompts, merge import preserves human-authored frontmatter such as `name`, `description`, `id`, and unknown fields. When the Espanso `trigger` already matches the prompt `keyword`, Taurcode reuses the existing frontmatter text exactly, preserving comments, quoting, field order, and line wrapping while updating only the prompt body.
- If merge import must change an Espanso-derived frontmatter field such as `keyword`, Taurcode uses a targeted edit for that field where practical rather than running the whole frontmatter block through generic YAML serialization. The conservative prompt formatter remains available when users explicitly want safe normalization.
- Taurcode normalizes generated or re-written Markdown prompt files to exactly one final newline during fresh import and merge import. This reduces noisy diffs such as missing-EOF-newline markers and improves round-trip idempotence. Taurcode only normalizes the final newline count; it does not strip or normalize other prompt body whitespace.
- Merge import creates new Markdown files for new Espanso matches. Existing Markdown prompts with no matching Espanso entry are kept and reported as warnings; merge import does not prune or delete prompt files.
- Merge import fails with a clear error when matching is ambiguous, such as multiple Markdown prompts with the same `keyword` for one Espanso trigger or multiple Espanso matches mapping to one Markdown file.
- If present in the source Espanso package, `_manifest.yml`, `README.md`, and `LICENSE` are copied into `<output>/espanso/` for later export. The `<output>/espanso/` directory is reserved for package metadata and its Markdown files are not treated as prompt sources during merge matching, validation, or export. Copied metadata assets, including `LICENSE`, are preserved exactly rather than newline-normalized.
- `replace` block scalars (`|` literal and `>` folded) are preserved according to YAML parsing semantics.
- Unsupported or complex matches are preserved under `<output>/imported_raw/*.yml`.
- Raw fallback keeps unsupported match YAML content so prompt text is not lost.
- The importer prints a summary with total, converted, and raw fallback match counts.

Suggested migration workflow:

```bash
taurcode import espanso --input <path-to-package.yml-or-directory> --output prompts/imported
# Review and curate staged imports into prompts/taurcode/ before treating them as canonical.
taurcode import espanso --input <updated-package.yml-or-directory> --output prompts/taurcode --merge
taurcode validate --prompts prompts/taurcode
taurcode export espanso --prompts prompts/taurcode --output build/espanso/taurcode
```

For curated prompt packages, `--merge` plus final-newline normalization is the recommended update path from Espanso sources because it keeps curated frontmatter human-readable and diff-friendly while making rewritten Markdown deterministic.

In this workflow, `prompts/imported/` is only a temporary staging area that records import provenance. Curated prompts belong in `prompts/taurcode/`.

### Espanso preflight diagnostics

`taurcode lint espanso --input <path>` accepts either a `package.yml` file or a package directory containing `package.yml`. The same preflight diagnostics run automatically before `taurcode import espanso` parses package contents.

The linter reports metadata **errors** separately from **warnings**. Errors represent invalid or unsafe package output and return a nonzero status. Warnings represent likely stale or low-quality metadata and are non-blocking by default. Export also runs build-output metadata linting; warning-only metadata does not fail the export, while metadata errors do fail it.

The linter checks for errors such as:

- missing `package.yml` when the input is a directory
- invalid UTF-8 bytes
- parser-sensitive invisible Unicode line break characters: `U+2028 LINE SEPARATOR`, `U+2029 PARAGRAPH SEPARATOR`, and `U+0085 NEXT LINE`
- malformed YAML, including parser line and column information when PyYAML provides it
- missing build output files: `package.yml`, `_manifest.yml`, or `README.md`
- invalid Espanso package metadata, including malformed `_manifest.yml`, missing or mismatched manifest names, package names outside lowercase letters/digits/hyphen, missing versions, or versions without a numeric `MAJOR.MINOR.PATCH` core

The linter checks for warnings such as:

- empty or very small `README.md` files
- README content that does not mention the package name or manifest title
- placeholder manifest `description` or `author` values
- homepage values that are not `http://` or `https://` URLs
- homepage repository slugs that obviously point at a different package

Invisible Unicode line separators can be troublesome because some tools may treat them like line breaks while YAML parsers reject them or report confusing locations. Taurcode reports the file, line, column, character name, and a manual fix suggestion. For example, replace an invisible separator inside a block scalar with a normal newline and keep the following content indented under the scalar.

Taurcode does not silently rewrite, normalize, or repair source Espanso files. Fix the source package manually, rerun `taurcode lint espanso`, and then rerun the import. Taurcode does not perform network validation of homepages, and it does not yet detect package-content-changed/version-unchanged freshness because no content-hash state is tracked.

## Export to Espanso
Use the CLI to export canonical prompts to an Espanso package:

```bash
taurcode export espanso --prompts prompts/taurcode --output build/espanso/taurcode
```

Generated output always includes the basic Espanso package files:

- `build/espanso/taurcode/package.yml`
- `build/espanso/taurcode/_manifest.yml`
- `build/espanso/taurcode/README.md`

The optional `prompts/<package>/espanso/` directory is reserved for Espanso package metadata. When `_manifest.yml` or `README.md` exists there, export copies it into the generated package instead of treating it as prompt content; otherwise Taurcode generates conservative defaults for Markdown-only packages. Generated README files are normalized to exactly one final newline. When `LICENSE` exists there, export copies it exactly; otherwise no `LICENSE` is generated.

Note: installation into a local Espanso configuration is currently manual.

## Validate and lint prompts
Validate all canonical prompt files before export:

```bash
taurcode validate --prompts prompts/taurcode
```

Validation rules:

- Prompt files are loaded from the provided directory recursively.
- Only `.md` files outside reserved metadata directories such as `espanso/` are considered.
- Required fields: `id`, `name`, `description`, `keyword`, `body`.
- `id` values must be unique.
- `keyword` values must be unique.
- `keyword` must start with `:`.
- `body` must be non-empty.

Common errors:

- `Duplicate keyword ':tc-test' found in prompts/taurcode/a.md and prompts/taurcode/b.md`
- `Missing required field 'id' in prompts/taurcode/example.md`

Export commands run the same validation step and fail if prompt data is invalid.

Prompt-source linting checks the Markdown files themselves before the loader converts
them into prompt objects:

```bash
taurcode lint prompts --prompts prompts/taurcode
```

Prompt-source lint **errors** are objective source problems and return a nonzero
status. They include missing or empty prompt package directories, missing
frontmatter delimiters, malformed YAML frontmatter, frontmatter that is not a
mapping, missing required frontmatter fields, missing or non-string keywords,
keywords that do not start with `:`, and duplicate keyword values within a
package.

Prompt-source lint **warnings** are non-blocking by default. They include filename
stems that do not match the keyword-derived slug, empty bodies, files that do not
end with exactly one final newline, unquoted keyword values, and descriptions that
appear to have been wrapped by a generic YAML dumper. Unknown frontmatter fields
are allowed and should not warn by default. The reserved `prompts/<package>/espanso/`
directory is ignored by prompt discovery and prompt-source linting because it holds
Espanso package metadata rather than prompt content.

Taurcode prompt files use YAML frontmatter parsed by the `python-frontmatter`
runtime dependency, which delegates YAML handling to `PyYAML`. Standard YAML
quoting, comments, and nested mappings are therefore supported during prompt
loading. The optional `targets` field may be authored as a nested mapping, for
example `targets.espanso.enabled` and `targets.espanso.package`; today it is
loaded into prompt objects for target-specific metadata, while Espanso export
still validates and exports the core prompt fields.

Preferred human-editable prompt frontmatter style is:

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
```

Keep frontmatter field order stable as `id`, `name`, `description`, `keyword`, then
any user-defined extra fields such as `targets`. Quote `keyword` because it is
syntax-like and quote preservation avoids round-trip churn such as
`keyword: ":debug"` becoming `keyword: :debug`. Keep `description` on one line
when practical. Unknown or user-defined fields are allowed and should be
preserved by prompt workflows. Generated or rewritten Markdown prompt files
should end with exactly one final newline.

Taurcode also provides an opt-in conservative prompt formatter:

```bash
taurcode format prompts --prompts prompts/taurcode
taurcode format prompts --prompts prompts/taurcode --check
```

The formatter is intended to reduce round-trip diff noise while preserving
human-authored prompt sources. Its safe fixes are intentionally narrow: it quotes
simple frontmatter `keyword` values such as `keyword: :debug` as
`keyword: ":debug"`, and it normalizes each formatted prompt file to exactly one
final newline. It does not run the frontmatter through a generic YAML dumper, wrap
or unwrap descriptions, change block scalar styles, trim or normalize prompt body
whitespace beyond the final newline count, or rewrite Espanso package metadata
under `prompts/<package>/espanso/`. Field ordering remains a documentation and
lint preference rather than an automatic rewrite so comments, unknown fields, and
existing frontmatter formatting are preserved.

## Design proposals

Architectural proposals for future Taurcode and LRH control-plane work live under `project/design/proposals/`. These documents capture design direction for later implementation prompts and work-item planning without making the proposed behavior immediately normative.

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

Formatting and linting:

- `scripts/format` runs Black over `src/` and `tests/`; use `scripts/format --check --diff` for CI-style checks.
- `scripts/lint` runs Ruff checks and a Black formatting gate.

Testing conventions:

- Test framework: `unittest`
- Discovery pattern: `*_test.py`
- `scripts/test` fails if zero tests are discovered.
