---
id: WI-CANONICAL-PROMPTS-0002
title: Implement canonical prompt pipeline and Espanso export flow
type: work_item
status: resolved
priority: high
owner: TBD
related_focus:
  - FOCUS-BOOTSTRAP
blocked: false
blocked_reason: ""
resolution: >-
  Resolved by the completed Espanso roundtrip foundation: canonical prompts,
  validation, Espanso import/export, metadata preservation, semantic roundtrip
  checks, operational scripts, tests, migrated corpus, and documentation are in
  place.
---

# Work Item: Implement canonical prompt pipeline and Espanso export flow

## Objective
Implement the canonical prompt system defined in project design docs without treating Espanso files as the canonical source format.

## Scope
- Add implementation scaffolding and CLI entrypoint.
- Add canonical Markdown/frontmatter loading and validation.
- Add deterministic Espanso export generation into `build/espanso/<package>/` or
  another explicitly requested output directory.
- Add migration importer for simple static Espanso replacements.
- Add docs for authoring/validation/export/migration.

## Completed Delivery Slices
1. Added `src/taurcode` package scaffold, CLI entrypoint, and operational scripts.
2. Added canonical Markdown/frontmatter prompt loading, validation, prompt-source
   linting, and conservative formatting.
3. Added deterministic Espanso export for supported static replacement prompts.
4. Added Espanso import and merge import for supported static replacements.
5. Added raw fallback preservation and diagnostics for unsupported Espanso constructs.
6. Added Espanso package metadata preservation and generated defaults for
   `_manifest.yml`, `README.md`, and `LICENSE`.
7. Added semantic normalization and `taurcode roundtrip espanso` for the supported
   roundtrip contract.
8. Migrated the real Taurcode prompt corpus into `prompts/taurcode/`.
9. Added tests, coverage command wiring, and Diátaxis-style documentation for the workflow.

## Constraints
- Do not auto-install generated output into local Espanso paths in v1.
- Detect unsupported Espanso features explicitly rather than silently treating them as
  supported static replacements.
- Keep exporter output deterministic and generated YAML parseable.

## Definition of Done
- Canonical prompts in `prompts/taurcode/*.md` load into validated prompt objects.
- Export command emits reviewable Espanso package output.
- Import path handles supported static replacements and flags unsupported feature usage.
- Merge import preserves curated canonical prompt metadata where Espanso does not own
  it.
- Metadata assets roundtrip through the `prompts/<package>/espanso/` layout.
- Semantic roundtrip command verifies supported Espanso package behavior against
  canonical prompts.
- Contributor docs explain the end-to-end canonical workflow.

## Evidence
- `project/evidence/EV-0002.md`
- `project/evidence/EV-0004.md`
- `project/executions/2026-04-29-AD_HOC-20260428-TAURCODE-CANONICAL-PROMPTS-DESIGN.md`
- `project/executions/2026-04-29-AD_HOC-20260429-TAURCODE-MVP-EXPORT-SLICE.md`
- `project/executions/2026-04-29-AD_HOC-20260429-TAURCODE-ESPANSO-IMPORTER.md`
- `project/executions/2026-05-06-canonical-corpus-location.md`
- `project/executions/2026-05-06-taurcode-espanso-preflight-linter.md`
- `project/executions/2026-05-07-taurcode-design-espanso-metadata-roundtrip.md`
- `project/executions/2026-05-15-taurcode-espanso-metadata-roundtrip-mvp.md`
- `project/executions/2026-05-16-semantic-normalization-model.md`
- `project/executions/2026-05-16-AD_HOC-20260515-TAURCODE-ROUNDTRIP-CLI.md`
- `project/executions/2026-05-16-AD_HOC-20260516-TAURCODE-DIATAXIS-DOCS-UPDATE.md`
- `project/executions/2026-05-16-AD_HOC-20260516-TAURCODE-ESPANSO-ROUNDTRIP-CLOSEOUT.md`
