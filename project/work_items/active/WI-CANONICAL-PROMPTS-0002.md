---
id: WI-CANONICAL-PROMPTS-0002
title: Implement canonical prompt pipeline and Espanso export flow
status: active
priority: high
owner: TBD
related_focus: FOCUS-BOOTSTRAP
---

# Work Item: Implement canonical prompt pipeline and Espanso export flow

## Objective
Implement the canonical prompt system defined in project design docs without treating Espanso files as the canonical source format.

## Scope
- Add implementation scaffolding and CLI entrypoint.
- Add canonical Markdown/frontmatter loading and validation.
- Add deterministic Espanso export generation into `build/espanso/<package>/`.
- Add migration importer for simple static Espanso replacements.
- Add docs for authoring/validation/export/migration.

## Suggested Delivery Slices
1. Add `src/taurcode` package scaffold and CLI skeleton.
2. Add canonical Markdown/frontmatter prompt loader and validator.
3. Add Espanso exporter to `build/espanso/<package>/`.
4. Add Espanso importer for simple static replacements.
5. Add docs for authoring, validation, export, and migration.

## Constraints
- Do not auto-install generated output into local Espanso paths in v1.
- Detect unsupported Espanso features explicitly (variables/forms/scripts/regex/imports/global variables).
- Keep exporter deterministic and generated YAML parseable.

## Definition of Done
- Canonical prompts in `prompts/taurcode/*.md` load into validated prompt objects.
- Export command emits reviewable Espanso package output under `build/espanso/<package>/`.
- Import path handles simple static replacements and flags unsupported feature usage.
- Contributor docs explain the end-to-end canonical workflow.
