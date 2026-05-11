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
- For matched Markdown prompts, merge import preserves human-authored frontmatter such as `name`, `description`, `id`, and unknown fields. It updates Espanso-derived `keyword` and the prompt body from the Espanso `trigger` and `replace`.
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

For curated prompt packages, `--merge` plus final-newline normalization is the recommended update path from Espanso sources because it keeps curated frontmatter while making rewritten Markdown deterministic.

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

## Validate prompts
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
