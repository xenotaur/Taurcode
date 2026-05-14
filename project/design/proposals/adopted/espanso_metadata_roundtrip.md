---
id: espanso-metadata-roundtrip
type: design_proposal
status: adopted
implementation_status: implemented
implemented_by:
  - project/executions/2026-05-09-taurcode-espanso-metadata-roundtrip-preserve.md
  - project/executions/2026-05-09-taurcode-espanso-metadata-roundtrip-defaults.md
  - project/executions/2026-05-10-taurcode-espanso-metadata-roundtrip-lint.md
  - project/executions/2026-05-10-taurcode-roundtrip-merge-import.md
  - project/executions/2026-05-10-taurcode-roundtrip-newline-normalization-tests.md
  - project/executions/2026-05-11-taurcode-prompt-source-lint-policy.md
  - project/executions/2026-05-11-taurcode-safe-prompt-formatter.md
  - project/executions/2026-05-12-preserve-frontmatter-merge.md
evidence:
  - project/executions/2026-05-10-taurcode-roundtrip-newline-normalization-tests.md
  - project/executions/2026-05-12-preserve-frontmatter-merge.md
title: Espanso Metadata Round-Trip
---

# Espanso Metadata Round-Trip Proposal

## Status

Accepted and implemented on main.

## Implementation Note

The metadata round-trip scope has been implemented on main. Completed capabilities include Espanso package metadata preservation, generated required Espanso defaults, metadata linting, merge import preserving curated prompt frontmatter, final-newline normalization, prompt-source lint policy, conservative prompt formatting, and frontmatter-format-preserving merge import. The expected local smoke test for this proposal is export -> merge import -> no prompt diffs.

Remaining future work belongs to broader Espanso construct coverage and semantic round-trip regression testing, not the metadata round-trip proposal itself.

## Summary

This proposal defines Taurcode's design direction for preserving Espanso package metadata while keeping prompt Markdown files as the canonical editable source. The chosen source layout is Option B: prompt files remain directly under `prompts/<package>/`, and Espanso-specific package assets live under `prompts/<package>/espanso/`.

The design is intentionally lightweight. It preserves the metadata needed for useful Espanso round trips, generates complete basic Espanso packages, adds conservative linting without turning Taurcode into an Espanso package registry validator, and defines the next merge-import behavior needed for curated Taurcode prompt packages.

## Problem Statement

Taurcode is intended to keep canonical prompt sources in a human-readable Markdown layout such as:

```text
prompts/taurcode/
  address.md
  debug.md
  design.md
  options.md
  package.md
  plan.md
  proandcon.md
  prompt.md
  think.md
```

The current import/export round trip focuses on prompt content and `package.yml`. A user's original local Espanso package may also contain package metadata and supporting files such as `_manifest.yml`, `README.md`, and `LICENSE`:

```text
~/Library/Application Support/espanso/match/packages/taurcode/
  _manifest.yml
  package.yml
  README.md
  LICENSE
```

Without an explicit source location and round-trip policy for those files, Taurcode risks losing source package metadata, replacing it with generated defaults, or omitting files that Espanso expects in a complete basic package. This is especially problematic because the [Espanso v2 Package Specification](https://espanso.org/docs/packages/package-specification/) states that the most basic package contains `package.yml`, `_manifest.yml`, and `README.md`, and that optional package files can include `LICENSE`, additional YAML files, and scripts called by snippets.

A real import comparison exposed a related prompt-level round-trip problem. A fresh import from Espanso can recreate prompt bodies from `package.yml`, but `package.yml` cannot reconstruct Taurcode-specific manual annotations that are not represented in Espanso. Importing back into an existing curated prompt package can therefore overwrite human-authored Markdown frontmatter such as `name`, `description`, or user annotations with generic generated values like `Imported from Espanso`. Missing or extra final newlines in generated Markdown files can also create noisy diffs that obscure semantic changes. Taurcode needs merge semantics when importing into an existing prompt package because Espanso `package.yml` is not, by itself, a faithful store for all Taurcode Markdown frontmatter.

## Goals

The design should:

- Keep Markdown prompt files in `prompts/<package>/` as the canonical editable prompt source.
- Preserve Espanso metadata during import/export where Taurcode can do so safely and predictably.
- Support a safe merge import path for existing curated prompt packages.
- Preserve human-authored frontmatter by default during merge imports.
- Update Espanso-derived fields and prompt body content from the Espanso source.
- Add new Markdown prompt files for new Espanso matches.
- Warn about existing orphan Markdown prompt files that are no longer present in the Espanso source, without deleting them automatically.
- Normalize generated or rewritten Markdown prompt files to exactly one final newline.
- Generate Espanso packages that include `package.yml`, `_manifest.yml`, and `README.md`.
- Avoid silent metadata loss during common import/build workflows.
- Add lightweight linting and error checking for objective package issues without turning Taurcode into a full Espanso package registry validator.
- Preserve backward compatibility with existing Markdown-only packages.
- Keep the source layout easy for humans to browse, edit, diff, and share.

## Non-Goals

This proposal does not require Taurcode to:

- Introduce a heavyweight package schema before Taurcode has multiple export formats.
- Move prompt Markdown files into a nested `prompts/` or `package/` subdirectory yet.
- Require every package source directory to contain `espanso/` metadata.
- Perform network validation of homepage URLs.
- Infer whether a version bump is semantically correct beyond conservative warnings.
- Validate every possible Espanso package registry rule.
- Use `README.md` as canonical machine-readable storage for per-prompt metadata.
- Introduce a sidecar Taurcode metadata database yet.
- Automatically delete orphan Markdown prompts in the first merge-import implementation.
- Attempt a full semantic version freshness system in this work.
- Support every possible advanced Espanso construct unless already supported by the existing importer/exporter.
- Normalize user-provided metadata files unless the user explicitly requests normalization.

## Chosen Layout

Taurcode should use the Option B source layout:

```text
prompts/<package>/
  think.md
  design.md
  package.md
  espanso/
    _manifest.yml
    README.md
    LICENSE
```

The generated Espanso build layout should be:

```text
build/espanso/<package>/
  package.yml
  _manifest.yml
  README.md
  LICENSE
```

Root `*.md` files in `prompts/<package>/` remain Taurcode prompt sources. The `espanso/` subdirectory contains Espanso-specific package assets and should not be interpreted as prompt content.

This layout keeps Taurcode's primary editing experience simple: a human can open a prompt package directory and immediately see the prompt Markdown files. Espanso package metadata remains nearby, versionable, and easy to inspect, but it is separated enough to avoid confusing package metadata with prompt sources.

## Import Behavior

When importing from an Espanso package directory into `prompts/<package>/`:

1. `package.yml` should be converted into root Markdown prompt files.
2. `_manifest.yml`, `README.md`, and `LICENSE` should be copied into `prompts/<package>/espanso/` when present.
3. Missing metadata files should not be fabricated during import.
4. `LICENSE` should be copied exactly.
5. `README.md` should be copied as text without interpretation.
6. `_manifest.yml` may be parsed for linting, but should otherwise be preserved unless the user explicitly asks for normalization.

Import should avoid mutating metadata just because Taurcode can parse it. If a manifest is valid enough to preserve, Taurcode should preserve the user's bytes or text representation rather than rewriting field order, comments, quoting style, or formatting in an ordinary import operation.

If import finds additional Espanso package assets that Taurcode does not yet handle, such as extra YAML files or scripts, Taurcode should avoid deleting them from the original source. A follow-up implementation can define explicit copy rules for those assets. The initial metadata round-trip scope is `_manifest.yml`, `README.md`, and `LICENSE`.

## Fresh Import and Merge Import Modes

Taurcode should distinguish between fresh import and merge import behavior. The final CLI names can follow the terminology that best fits the implementation, but the semantics should be explicit so users can predict whether curated prompt metadata will be preserved or replaced.

### Fresh import

Fresh import is appropriate for empty output directories or explicitly requested replacement imports. In this mode Taurcode should:

1. Create Markdown files from Espanso matches in `package.yml`.
2. Generate default `name` and `description` values when no curated Taurcode data exists.
3. Preserve package-level Espanso metadata under `prompts/<package>/espanso/` when `_manifest.yml`, `README.md`, or `LICENSE` are present.
4. Treat generated Markdown files as Taurcode-owned output for newline normalization.

Fresh import should remain useful for bootstrapping a Taurcode package from an Espanso package, but it should not be treated as proof that Espanso `package.yml` contains every prompt-level annotation Taurcode users may care about.

### Merge import

Merge import is appropriate when importing Espanso changes into an existing curated Taurcode prompt package. In this mode Taurcode should:

1. Match Espanso entries to existing Markdown prompt files.
2. Preserve curated and unknown Markdown frontmatter fields.
3. Update Espanso-derived fields and prompt body content from the Espanso source.
4. Add new Markdown prompt files for new Espanso entries.
5. Warn about orphan existing Markdown prompt files that do not correspond to any source Espanso entry.
6. Avoid deleting orphan Markdown prompt files unless a future explicit prune flag is added.
7. Fail clearly when an Espanso entry ambiguously matches more than one existing Markdown file.
8. Preserve package-level Espanso metadata under `prompts/<package>/espanso/` using the metadata behavior defined above.

Merge import is the recommended update path for curated prompt packages because it treats Taurcode Markdown as the editable source of truth for prompt annotations while still allowing Espanso source changes to refresh trigger-derived data and bodies.

## Field Ownership During Merge Import

Merge import should use field ownership rules rather than rewriting the whole frontmatter block from generated defaults.

### Espanso-derived fields

Espanso-derived fields are owned by the Espanso source during merge import and should be updated from `package.yml`. They include:

- Taurcode `keyword`, which corresponds to Espanso `trigger`, and any fields directly needed to regenerate supported Espanso matches.
- Replacement/body content imported from Espanso.
- Other supported Espanso match fields, if Taurcode already models them.

### Taurcode-curated fields

Taurcode-curated fields are human-authored annotations that are not faithfully represented in Espanso `package.yml`. Merge import should preserve them by default. They include:

- `name`.
- `description`.
- Any user-authored annotations not represented in Espanso.

### Unknown and user fields

Unknown frontmatter fields should be preserved by default. Taurcode should only remove or rewrite them as part of a future explicit migration with documented behavior.

`README.md` should remain package documentation, not the canonical machine-readable store for per-prompt metadata. Per-prompt metadata belongs in prompt Markdown frontmatter unless a future design introduces another explicit metadata store.

## Matching Strategy During Merge Import

Merge import should avoid matching by `name` because curated names may intentionally differ from trigger-derived names. The proposed matching priority is:

1. Existing Markdown frontmatter `keyword` equals the Espanso trigger.
2. Existing Markdown filename stem equals the generated slug for the Espanso trigger.
3. Existing stable `id` field, if Taurcode already has one for prompt files.
4. Otherwise create a new Markdown file.

The merge design should match existing Taurcode prompt files by `keyword`, not by a new `trigger` frontmatter field. If a future schema migration introduces `trigger` as an alias or replacement, that migration should be explicit and tested before merge import relies on it.

If any priority level produces multiple possible matches for a single Espanso entry, Taurcode should fail the import with a clear ambiguity error and leave files unchanged. A future implementation may add a dry-run report or conflict-resolution command, but silent selection would risk overwriting the wrong curated prompt.

## Newline Normalization

Markdown prompt files generated or rewritten by Taurcode should end with exactly one final newline. This rule applies to fresh-import output and merge-import files that Taurcode rewrites.

Taurcode should not strip or normalize other body whitespace as part of this rule. Interior whitespace and intentional trailing spaces in prompt bodies are content and should remain unchanged unless a future formatter is explicitly requested by the user.

The newline rule is specific to generated or rewritten Markdown prompt files. Taurcode should not normalize copied `LICENSE` files. It should preserve copied package metadata files such as `espanso/README.md` and `espanso/_manifest.yml` as much as practical unless Taurcode is explicitly generating those files or a user requests metadata normalization.

## Build and Export Behavior

When building `build/espanso/<package>/`:

1. `package.yml` should be generated from root Markdown prompt files.
2. `_manifest.yml` should be copied from `prompts/<package>/espanso/_manifest.yml` if present.
3. If no source manifest is present, Taurcode should generate a minimal `_manifest.yml`.
4. `README.md` should be copied from `prompts/<package>/espanso/README.md` if present.
5. If no source README is present, Taurcode should generate a minimal non-empty `README.md`.
6. `LICENSE` should be copied from `prompts/<package>/espanso/LICENSE` if present.
7. If no source license is present, `LICENSE` should be omitted.

Existing Markdown-only packages should still build successfully. The only visible behavior change for those packages should be that the Espanso build output now includes a generated non-empty `README.md` alongside `package.yml` and `_manifest.yml`.

Generated defaults should be conservative and obvious. A generated manifest should contain enough information for a valid local package build, but it should not pretend to know details such as a real homepage, author, license, or polished description when those values are unavailable. A generated README should clearly identify the package and indicate that it was generated from Taurcode prompt sources.

## Minimal Linting Design

Taurcode should distinguish objective errors from non-blocking warnings.

### Errors

Errors should represent objective invalidity or missing output that Taurcode cannot safely ignore. They should block builds by default when detected in the operation being performed.

Errors should include:

- `_manifest.yml` does not parse as YAML.
- Manifest `name` is missing after source load/default generation.
- Manifest `name` does not match the package directory name.
- Package name contains characters outside lowercase letters, digits, and hyphen.
- Manifest `version` is missing.
- Manifest `version` does not contain a SemVer-compatible numeric `MAJOR.MINOR.PATCH` core.
- Build output lacks `package.yml`, `_manifest.yml`, or `README.md`.

### Warnings

Warnings should represent likely stale, incomplete, or low-quality metadata. They should not block builds by default.

Warnings should include:

- `README.md` is empty or very small.
- `README.md` does not mention the package name or manifest title.
- Manifest `description` is empty or still a generated placeholder.
- Manifest `author` is empty or still a generated placeholder.
- Manifest `homepage` exists but is not an `http://` or `https://` URL.
- Manifest `homepage` appears to point to an obviously different package or repository slug.
- Manifest `version` uses SemVer pre-release or build metadata, if Taurcode wants to discourage publishing those forms while still treating them as parseable versions.
- Package content changed but version did not, if Taurcode later has a reliable state mechanism for this check.

Espanso's v2 package specification says package versions should follow the standard `MAJOR.MINOR.PATCH` format. Taurcode should therefore require the numeric major, minor, and patch core, but should avoid rejecting otherwise SemVer-compatible pre-release or build metadata unless Espanso or the Hub validator is proven to reject those forms.

The linting design should remain intentionally modest. Taurcode should catch mistakes that cause round-trip loss, broken local builds, or obviously stale metadata, but it should avoid registry-level judgments that require network access, project-specific release policy, or human semantic review.

## Low-Level Implementation Sketch

The exact APIs may be adjusted to fit the existing Taurcode codebase, but the implementation should remain modular and explicit. A lightweight internal design could use functions or small data objects shaped roughly like:

```python
load_espanso_metadata(package_source_dir) -> EspansoPackageMetadata
write_espanso_metadata(metadata, output_dir, package_name)
generate_default_manifest(package_name) -> dict
generate_default_readme(package_name, manifest) -> str
lint_espanso_package_source(package_dir) -> LintResult
lint_espanso_package_build(output_dir) -> LintResult
import_espanso_package_fresh(source_dir, target_dir) -> ImportResult
import_espanso_package_merge(source_dir, target_dir) -> ImportResult
normalize_markdown_final_newline(text) -> str
```

`EspansoPackageMetadata` should represent the source metadata that Taurcode knows how to preserve, such as manifest text or parsed data, README text, and license text. It can also track whether each file was source-provided or generated so the build step and linter can produce useful diagnostics.

`LintResult` should contain separate error and warning collections. Callers should decide whether warnings are displayed, promoted, or ignored in a given command mode. The default build behavior should fail on errors and continue on warnings.

Default generation should be centralized. Import, build, tests, and future CLI commands should not each invent their own manifest or README fallback behavior.

## Backward Compatibility and Migration

Existing packages with only root Markdown files should continue to work without changes:

```text
prompts/<package>/
  think.md
  design.md
  package.md
```

If `prompts/<package>/espanso/` exists, the build/export path should use it for Espanso-specific metadata. If it does not exist, Taurcode should generate minimal build metadata as needed.

No migration is required for current Taurcode users. Users who want richer Espanso metadata can add `prompts/<package>/espanso/_manifest.yml`, `prompts/<package>/espanso/README.md`, or `prompts/<package>/espanso/LICENSE` incrementally. Existing curated prompt packages should be able to adopt merge import without moving root Markdown files or converting package documentation into machine-readable metadata.

## Alternatives Considered

### Continue fresh import only

Continuing with only fresh import would keep the importer simple, but it would keep overwriting or discarding curated Taurcode frontmatter during update workflows. It also would not address noisy Markdown newline diffs. This is not acceptable for curated prompt packages.

### Store extra per-prompt metadata in `README.md`

A package `README.md` could theoretically describe prompt names and descriptions, but it is a poor machine-readable source of truth. It is package documentation, may be copied from Espanso, and should remain free-form for humans. Using it as canonical per-prompt metadata would make imports brittle and would confuse package documentation with prompt records.

### Add a Taurcode sidecar metadata file

A sidecar metadata database could preserve fields that Espanso does not represent and might become useful if Taurcode supports many exporters. It is premature for the current workstream because the existing Markdown frontmatter already carries prompt annotations and is easy to preserve during merge import.

### Add merge import preserving existing frontmatter

Merge import preserves the current human-readable root Markdown layout, updates data that Espanso actually owns, and leaves curated fields intact. Combined with final-newline normalization for generated or rewritten Markdown prompt files, it directly addresses the observed round-trip failures with minimal new structure.

### Flat root metadata layout

In a flat root metadata layout, prompts and Espanso metadata all live directly in `prompts/<package>/`:

```text
prompts/<package>/
  think.md
  design.md
  package.md
  _manifest.yml
  README.md
  LICENSE
```

This is simple to implement, but it makes it less obvious which Markdown files are prompt sources. A root `README.md` is especially ambiguous because it is useful both as an Espanso package asset and as documentation for the Taurcode source directory.

### Option B: root prompts with `espanso/` metadata

Option B keeps prompt Markdown files in the package root and Espanso metadata in `prompts/<package>/espanso/`. This proposal chooses Option B because it best supports Taurcode's current purpose as a browsing and editing convenience, preserves simple human-editable Markdown prompts in the package root, avoids premature abstraction before there are multiple exporters, and separates Espanso metadata from prompt source files well enough for the current scope.

### More structured nested layout

A more structured layout could introduce nested prompt and package directories, such as:

```text
prompts/<package>/
  prompts/
    think.md
    design.md
  package/
    espanso/
      _manifest.yml
      README.md
      LICENSE
```

This may become attractive if Taurcode supports many export formats or richer package-level metadata. For now, it adds ceremony and makes the common prompt browsing workflow worse.

### Mirroring Espanso package format exactly

Taurcode could mirror Espanso's package format exactly and treat `package.yml`, `_manifest.yml`, and `README.md` as the canonical source. That would simplify Espanso passthrough behavior, but it would undermine Taurcode's main purpose: making prompts easy to read and edit as individual Markdown files.

## Risks and Mitigations

### Stale metadata

Preserved metadata can become stale as prompt content changes. Taurcode should mitigate this with warnings for placeholder or suspicious metadata and, later, a conservative content-changed/version-unchanged warning if the project has reliable state for that check.

### Ambiguous homepage and version freshness

Homepage relevance and semantic version correctness are partly human judgments. Taurcode should only warn on obvious issues, such as non-HTTP URLs or a homepage slug that clearly differs from the package name. It should not perform network validation or claim that a version bump is semantically correct.

### Additional Espanso YAML files or scripts

Espanso supports optional YAML files and scripts called by snippets. The initial metadata scope should not pretend to fully round-trip every possible package asset. The `espanso/` subdirectory leaves room to add explicit copy and lint rules for additional YAML files and script directories later.

### Future non-Espanso exporter metadata

A future exporter might need its own package assets. Keeping Espanso files under `espanso/` reduces collision risk and creates a repeatable pattern for future exporter-specific metadata, such as `prompts/<package>/<exporter>/`, without requiring that abstraction today.

### Generated defaults mistaken for polished metadata

Generated manifests and READMEs may be mistaken for user-authored package metadata. Defaults should use clear placeholder wording, and lint warnings should identify generated or placeholder fields so users can improve them before publishing packages more broadly.

### Ambiguous prompt matches

A merge import can be dangerous if one Espanso trigger appears to match multiple Markdown files. Taurcode should fail clearly rather than choosing a file heuristically. This keeps merge import conservative and prevents accidental loss of curated prompt metadata.

### Orphan prompt handling

Orphan Markdown prompts may be intentionally curated local prompts or stale entries removed from Espanso. The first merge-import implementation should warn and preserve them. A future explicit prune flag can define deletion behavior after users have had a chance to review dry-run output and tests.

### Whitespace churn

Whitespace-only diffs can make round-trip validation hard to review. Taurcode should normalize generated or rewritten Markdown prompt files to exactly one final newline while preserving other body whitespace and copied package assets.

## Implementation Plan

1. **Metadata PR 1: Design proposal and documentation only.** Add this proposal and any required proposal index/documentation updates.
2. **Metadata PR 2: Metadata preservation and generated README behavior.** Implement import/export support for `espanso/_manifest.yml`, `espanso/README.md`, and `espanso/LICENSE`; generate `README.md` for Markdown-only packages.
3. **Metadata PR 3: Minimal linting and tests.** Add source/build linting for errors and warnings, including tests for preserved metadata, generated defaults, and backward-compatible Markdown-only packages.
4. **Merge PR0: Design proposal/documentation update.** Extend this proposal with merge import and newline normalization behavior.
5. **Merge PR1: Merge import semantics and tests.** Implement matching, field ownership, orphan warnings, ambiguity failures, and preservation of curated frontmatter.
6. **Merge PR2: Newline normalization and round-trip fixture tests.** Normalize generated or rewritten Markdown prompt files to exactly one final newline and add fixture tests that prove semantic round-trip stability without newline churn.

Design-only PRs should not implement runtime behavior unless repository conventions require documentation validation changes.
