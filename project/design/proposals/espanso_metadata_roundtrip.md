# Espanso Metadata Round-Trip Proposal

## Status

Proposed.

## Summary

This proposal defines Taurcode's design direction for preserving Espanso package metadata while keeping prompt Markdown files as the canonical editable source. The chosen source layout is Option B: prompt files remain directly under `prompts/<package>/`, and Espanso-specific package assets live under `prompts/<package>/espanso/`.

The design is intentionally lightweight. It preserves the metadata needed for useful Espanso round trips, generates complete basic Espanso packages, and adds conservative linting without turning Taurcode into an Espanso package registry validator.

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

Without an explicit source location and round-trip policy for those files, Taurcode risks losing source package metadata, replacing it with generated defaults, or omitting files that Espanso expects in a complete basic package. This is especially problematic because Espanso's basic package specification requires `package.yml`, `_manifest.yml`, and `README.md`, while also allowing optional files such as `LICENSE`, additional YAML files, and scripts called by snippets.

## Goals

The design should:

- Keep Markdown prompt files in `prompts/<package>/` as the canonical editable prompt source.
- Preserve Espanso metadata during import/export where Taurcode can do so safely and predictably.
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
- Manifest `version` is not `MAJOR.MINOR.PATCH`.
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
- Package content changed but version did not, if Taurcode later has a reliable state mechanism for this check.

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

No migration is required for current Taurcode users. Users who want richer Espanso metadata can add `prompts/<package>/espanso/_manifest.yml`, `prompts/<package>/espanso/README.md`, or `prompts/<package>/espanso/LICENSE` incrementally.

## Alternatives Considered

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

## Implementation Plan

1. **PR 1: Design proposal and documentation only.** Add this proposal and any required proposal index/documentation updates.
2. **PR 2: Metadata preservation and generated README behavior.** Implement import/export support for `espanso/_manifest.yml`, `espanso/README.md`, and `espanso/LICENSE`; generate `README.md` for Markdown-only packages.
3. **PR 3: Minimal linting and tests.** Add source/build linting for errors and warnings, including tests for preserved metadata, generated defaults, and backward-compatible Markdown-only packages.

This PR should implement only the design proposal unless repository conventions require a README or index update.
