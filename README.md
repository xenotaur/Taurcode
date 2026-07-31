# Taurcode
Taurcode is a set of prompts for AI-generated coding with tools to format them for various injection systems like Espanso.

## Documentation

Start with the [Taurcode documentation index](docs/README.md) for tutorials, how-to guides, reference pages, and explanations. The docs include the canonical prompt workflow, Espanso import/export integration, semantic roundtrip checks, and prompt-authoring best practices.

## Canonical prompts
The checked-in Taurcode prompt corpus lives under `prompts/taurcode/`. This directory is the authoritative source of truth for the Taurcode prompt package.

Espanso package files are generated from that corpus into `build/espanso/taurcode/`; Espanso is an export target, not the canonical storage location.

Prompt authors and reviewers should use [`docs/how-to/best-practices/prompting-best-practices.md`](docs/how-to/best-practices/prompting-best-practices.md) for the canonical Taurcode prompting principles and review rubric.
Use the `:prompt-review` prompt (`prompts/taurcode/prompt-review.md`) when you want a reusable assistant-assisted review that applies that guide without duplicating the whole rubric inline.
Use the `:lrh-template-review` prompt (`prompts/taurcode/lrh-template-review.md`) for guidance-only reviews of Logical Robotics Harness request templates when LRH template files are not being edited directly in an LRH checkout.

### LRH prompt backport (`lrh` package)

`prompts/lrh/` is a second, independently-installable prompt package that backports proven LRH slash-command skills into short, paste-able `:lrh-`-prefixed Espanso triggers, for sessions that don't have the LRH skills installed or don't support Claude Code slash commands directly. It ships separately from the `taurcode` package (see [the governing design proposal](project/design/proposals/proposed/lrh-backport-and-hardening/00_proposal.md) for why), so users can install one without the other. On macOS:

```bash
taurcode install espanso --prompts prompts/lrh --restart
```

On other platforms, `taurcode install espanso` is unsupported (see "Install into Espanso (macOS)" below); export and copy the package manually instead:

```bash
taurcode export espanso --prompts prompts/lrh --output exports/espanso/lrh
```

### Printing a snippet without Espanso

Use `taurcode show <keyword>` to print a snippet's body to stdout for sessions that don't run Espanso at all:

```bash
taurcode show :lrh-implement                      # searches every canonical corpus (prompts/taurcode, prompts/lrh)
taurcode show :lrh-implement --prompts all         # same as the default above, explicitly
taurcode show :lrh-implement --prompts prompts/lrh # searches only that one directory
```

`--prompts` defaults to searching an explicit, maintained list of canonical corpora — never a glob of `prompts/*/`, so uncurated directories like `prompts/examples/` or the `taurcode import` staging directory are never treated as canonical. A keyword matching no corpus, or matching more than one, prints an error to stderr and exits non-zero rather than guessing.

Currently backported: `:lrh-implement` (`prompts/lrh/lrh-implement.md`), `:lrh-review-response` (`prompts/lrh/lrh-review-response.md`), `:lrh-confirm-fixes` (`prompts/lrh/lrh-confirm-fixes.md`), and `:lrh-closeout` (`prompts/lrh/lrh-closeout.md`). The generated package is checked in at `exports/espanso/lrh/`, mirroring `exports/espanso/taurcode/`.

### Prompt lifecycle snippets

Use `:execute` (`prompts/taurcode/execute.md`) to drive a work item through the full LRH lifecycle — implement, PR, review, merge, and closeout — nearly autonomously in a single pasted session. Use `:land` (`prompts/taurcode/land.md`) instead when the PR is already open and only the post-PR tail (review through closeout) is needed.

Both snippets bound their autonomy with the same two contracts:

- **Merge gate** — the one point that always stops for a human. The snippet asks for explicit approval before merging, and summarizes what the PR accomplishes and how it changed over the review cycle first.
- **Review-landed rule** — automated reviewers post minutes after a PR opens or is pushed, so an empty comment-thread list right after pushing is not proof of a clean review. The snippet waits for review to actually complete (with or without findings) before acting on it.

At closeout, both snippets use a find-or-backfill rule for the PR's primary execution record: they update its `status` if one already exists, or honestly reconstruct a backfill record when the PR was authored outside the skill chain and drew no prior record — always surfaced before it is pushed, never written silently. Either way, a one-line `CHAIN-NOTE` evidence signal (`lrh search executions "CHAIN-NOTE"` finds every run) is landed as durable evidence of the run: written directly into a newly authored (backfill) record's `# Result` section, or — since a merged primary record's body is immutable — into a small separate `landed` closeout-note record when the primary record was only found and its status flipped.

Use `:assess` (`prompts/taurcode/assess.md`) to evaluate an existing pull request on its technical merits — not on who authored it — and get a decisive PROCEED AS-IS / PROCEED WITH CHANGES / RECONSIDER recommendation grounded in the diff, review comments, and repository conventions.

### Manual prompt review workflow

Use the prompt-review system as a lightweight manual review aid rather than as a required automation layer:

1. Open `docs/how-to/best-practices/prompting-best-practices.md` and the prompt you want to review.
2. Start an assistant session with `:prompt-review`, or paste `prompts/taurcode/prompt-review.md` into the session.
3. Attach or paste the target prompt after the `Prompt or prompt template to review:` divider. Representative first targets are `prompts/taurcode/debug.md` and `prompts/taurcode/plan.md` because they exercise task framing, workflow steps, and output expectations.
4. Ask for severity-ranked findings and make only minimal, intent-preserving edits unless a blocker is clear.
5. Rerun prompt validation before export:

   ```bash
   taurcode validate --prompts prompts/taurcode
   taurcode lint prompts --prompts prompts/taurcode
   taurcode format prompts --prompts prompts/taurcode --check
   ```

For LRH request-template review, use `:lrh-template-review` with a rendered example when available. If the LRH template source or renderer is not present in the checkout, keep the result as review guidance and defer direct template edits to a dedicated LRH change.

Deferred follow-up ideas that should stay lightweight until justified include prompt metadata validation, prompt-review examples, prompt evaluation fixtures, LRH template rendering tests, and future automation hooks for recurring reviews.

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
- If `--input` points to an Espanso package directory and package-level `_manifest.yml`, `README.md`, or `LICENSE` files are present, they are copied into `<output>/espanso/` for later export. The `<output>/espanso/` directory is reserved for package metadata and its Markdown files are not treated as prompt sources during merge matching, validation, or export. Copied metadata assets, including `LICENSE`, are preserved exactly rather than newline-normalized.
- Missing metadata assets do not block import. Taurcode reports warnings for missing supported assets and continues importing prompts. If `--input` points directly to `package.yml`, prompt import still works but metadata asset import is skipped with a warning because sibling files may not be discoverable from that invocation.
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

### Espanso metadata ownership

Taurcode uses `prompts/<package>/espanso/` as the curated source of truth for Espanso package metadata assets. Import copies `_manifest.yml`, `README.md`, and `LICENSE` into that directory as a starting point, and users may then edit or curate those files in source control. Export prefers curated files from `prompts/<package>/espanso/` and copies them to `build/espanso/<package>/` before generating any fallback metadata. Taurcode does not attempt a three-way merge for metadata assets in the MVP. Importing into an output directory is an explicit write to that destination, so existing supported metadata files there may be replaced by the imported package copies; review staged metadata before treating it as canonical. Local Espanso install or sync remains out of scope.

### Espanso preflight diagnostics

`taurcode lint espanso --input <path>` accepts either a `package.yml` file or a package directory containing `package.yml`. Import runs the parser-safety package diagnostics before reading matches. Run the linter directly when you also want package-build metadata checks before import.

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

The optional `prompts/<package>/espanso/` directory is reserved for Espanso package metadata. When `_manifest.yml` or `README.md` exists there, export copies it into the generated package instead of treating it as prompt content; otherwise Taurcode generates conservative defaults for Markdown-only packages. Generated README files are normalized to exactly one final newline. When `LICENSE` exists there, export copies it exactly; otherwise no `LICENSE` is generated. Export removes stale supported metadata assets from the generated output when no curated source exists and no default is generated for that asset, so `build/espanso/<package>/` remains a generated view of the canonical prompt package.

## Install into Espanso (macOS)
On macOS, install the canonical prompts straight into the local Espanso configuration:

```bash
taurcode install espanso --prompts prompts/taurcode --restart
```

This re-exports into `~/Library/Application Support/espanso/match/packages/<name>/` and, with `--restart`, runs `espanso restart` so the change takes effect. Without `--restart` it prints the restart command for you to run. The install is staged and swapped into place only after the export and its build lint succeed, so a failed export leaves any existing installed package untouched. The command is macOS-only; on other platforms it exits non-zero, and you should export and copy the package manually. See [docs/reference/espanso-integration.md](docs/reference/espanso-integration.md) for `--packages-dir` and the name-derivation rules.

## Espanso roundtrip checks
Taurcode uses semantic normalization as the comparison model for Espanso roundtrip checks. The goal is to compare prompt meaning instead of raw YAML bytes, because YAML emitters can change field ordering, quoting, scalar style, and list formatting without changing the package Espanso receives.

Run the CLI after exporting a package to verify that the Espanso output still matches the canonical Taurcode prompt semantics:

```bash
taurcode export espanso --prompts prompts/taurcode --output tmp/exported/taurcode
taurcode roundtrip espanso --input tmp/exported/taurcode --prompts prompts/taurcode
```

`--input` accepts either an Espanso package directory or a direct `package.yml` path. `--prompts` points at the canonical prompt directory, such as `prompts/taurcode`. The command prints a human-readable pass/fail summary and returns exit code `0` when the normalized semantics are equivalent. It returns nonzero when semantic differences are found or when inputs are malformed and cannot be parsed.

The normalization layer currently lives in `src/taurcode/semantic_normalize.py`. It can normalize an Espanso package directory, a direct `package.yml` path, or a canonical Taurcode prompt collection such as `prompts/taurcode/`. Text values are normalized to `\n` line endings, but Taurcode otherwise preserves final-newline semantics: a parsed YAML value ending in `\n` compares equal to another parsed value ending in `\n`, while a value without that newline remains different.

The `taurcode roundtrip espanso` command uses Espanso semantic mode. It compares the parts that roundtrip through Espanso package output today:

- prompt trigger/keyword values;
- prompt replacement/body text;
- parsed `_manifest.yml` semantics, independent of YAML field ordering or inline versus block list style;
- `README.md` and `LICENSE` text with normalized line endings;
- unsupported extra Espanso match fields when the expected normalized package contains them, so accidental loss is visible without failing canonical-to-Espanso comparisons solely because the Espanso side has extra match fields.

Espanso semantic mode intentionally ignores canonical-only prompt annotations such as curated `name`, `description`, and `tags` when comparing canonical prompt sources to exported Espanso packages. Plain Espanso `package.yml` does not represent those fields, so their absence in an exported package is not a semantic export failure. When the expected side has no curated metadata asset, Espanso semantic mode also allows an actual exported package to contain generated `_manifest.yml`, `README.md`, or `LICENSE` assets without treating them as unexpected semantic drift.

Canonical semantic mode is the fuller prompt-source comparison concept. It compares canonical prompt identity and annotation fields (`id`, `name`, `description`, `tags`) in addition to keyword/body semantics and package metadata assets. This mode is available for tests and future tooling, and it leaves room for richer target-specific metadata as Taurcode grows.

Missing metadata assets are deterministic: if the canonical prompt package has `_manifest.yml`, `README.md`, or `LICENSE` under `prompts/<package>/espanso/`, the Espanso package must contain the corresponding normalized asset. If the canonical prompt package has no curated metadata asset, Espanso semantic mode allows generated assets on the Espanso side and does not fail solely because they are present.

Limitations: Espanso semantic mode is not a byte-for-byte YAML diff, does not validate local Espanso installation state, and intentionally does not compare canonical-only prompt annotations that plain Espanso packages cannot represent. Canonical semantic mode remains available for tests and future tooling when full Taurcode prompt-source annotations need to be compared.

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

Architectural proposals for future Taurcode and LRH control-plane work live under `project/design/proposals/`. Proposed designs live in `project/design/proposals/proposed/`, and accepted proposal history lives in `project/design/proposals/adopted/`. These documents capture design direction for later implementation prompts and work-item planning; frontmatter status is authoritative for each proposal lifecycle state.

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

## Release process

Taurcode's version is derived from git tags via `setuptools-scm` (`pyproject.toml` declares `dynamic = ["version"]`); there is no version string to bump by hand. `scripts/version` (no arguments) prints the currently resolved version.

Release tags follow `vMAJOR.MINOR.PATCH` (for example, `v0.1.0`). `setuptools-scm` only resolves a real release version once the tag exists, so create the tag locally *before* running verification — do not push it until both checks pass:

```bash
git tag vMAJOR.MINOR.PATCH
scripts/version verify vMAJOR.MINOR.PATCH
scripts/release-smoke vMAJOR.MINOR.PATCH --strict-isolation
```

- `scripts/version verify <tag>` checks the tag format, requires a clean working tree, and re-runs `scripts/lint`, `scripts/format --check`, and `scripts/test`.
- `scripts/release-smoke <tag> --strict-isolation` builds the sdist/wheel (`scripts/build`), installs the wheel into an isolated venv, and runs real invocations of the *installed* `taurcode` CLI — catching editable-install/`.pth` leakage and confirming the installed version matches the tag. Without a tag argument, it skips the version check (useful for a quick local isolation check on an untagged commit).

Publishing is handled by two tag/dispatch-triggered GitHub Actions workflows, both using [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/) (OIDC — no stored API tokens):

- `.github/workflows/release.yml` — triggered by pushing a `v*.*.*` tag; builds, verifies, and smoke-tests the tagged checkout, then publishes to PyPI via the `pypi` GitHub Environment.
- `.github/workflows/testpypi-rehearsal.yml` — manually triggered (`workflow_dispatch`) against an existing tag; runs the same build/verify/smoke steps and publishes to TestPyPI via the `testpypi` GitHub Environment, for rehearsing a release without touching production PyPI.

**Tag-collision safety:** pushing *any* `vMAJOR.MINOR.PATCH` tag — including one only meant to drive a TestPyPI rehearsal — also fires `release.yml`'s production PyPI trigger, since both workflows match the same tag pattern. A required-reviewer approval gate on the `pypi` GitHub Environment is a **mandatory precondition**, not an optional hardening step, before pushing any release tag for the first time: it is the only thing standing between a rehearsal tag push and an unintended production publish. Configure that gate (along with the `testpypi` environment and both Trusted Publishers) before pushing a real tag at all.

Both the PyPI and TestPyPI Trusted Publishers, and the corresponding GitHub Environments (ideally with a required-reviewer approval gate), must be configured by a repository admin **before** either workflow is used — this is a one-time, human-performed setup step and is not automated by these workflows.
