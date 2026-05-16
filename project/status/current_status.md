---
id: STATUS-CURRENT
title: Current Project Status
scope: project
status: active
health: green
---

# Current Status

## Summary
- The Espanso roundtrip foundation is complete and operational for Taurcode's current
  v1 scope.
- `prompts/taurcode/*.md` is the canonical Markdown/frontmatter prompt corpus, and
  Espanso package files are import/export artifacts rather than the long-term authoring
  source.
- The CLI now supports validation, Espanso import/export, prompt-source linting and
  formatting, Espanso preflight diagnostics, semantic Espanso roundtrip checks, and
  deterministic operational scripts.
- The checked-in prompt corpus has been migrated into the canonical location and
  documented through the Diátaxis-style docs structure.

## Completed Espanso Roundtrip Foundation
- Canonical Markdown prompt format with stable frontmatter fields and validation.
- Deterministic Espanso export from canonical prompts.
- Espanso import and merge import for supported static replacements.
- Raw fallback preservation and clear diagnostics for unsupported Espanso constructs.
- Espanso package metadata roundtrip for `_manifest.yml`, `README.md`, and `LICENSE`
  assets.
- Semantic normalization and `taurcode roundtrip espanso` comparison for supported
  roundtrip behavior.
- Espanso lint/preflight diagnostics and prompt-source lint/format checks.
- Operational scripts for development setup, linting, formatting, tests, and coverage.
- Unit tests and coverage command wiring for the implemented foundation.
- Diátaxis-style documentation covering tutorials, how-to guides, reference pages, and
  explanations.

## Evidence Basis
- `README.md`
- `docs/README.md`
- `docs/reference/canonical-prompt-format.md`
- `docs/reference/espanso-integration.md`
- `docs/how-to/check-espanso-roundtrip-fidelity.md`
- `prompts/taurcode/`
- `project/design/design.md`
- `project/design/proposals/adopted/espanso_metadata_roundtrip.md`
- `project/work_items/resolved/WI-CANONICAL-PROMPTS-0002.md`
- `project/evidence/EV-0002.md`
- `project/evidence/EV-0004.md`

## Current Health
- **Green**: the v1 canonical prompt and Espanso roundtrip foundation has
  implementation, docs, tests, and local validation commands.

## Active Priorities
- Keep the canonical prompt source-of-truth boundary stable.
- Treat future Espanso feature expansion as separate, explicitly scoped work.
- Preserve semantic roundtrip guarantees when changing loader, importer, exporter,
  lint, or formatter behavior.
- Continue project-plane cleanup separately from runtime roundtrip work.

## Risks
- Unsupported advanced Espanso constructs can still exceed Taurcode's current v1 model
  and should remain explicit diagnostics or raw fallback data rather than silently
  normalized behavior.
- Future exporter targets may introduce metadata layout pressure; keep target-specific
  assets isolated unless a broader metadata model is deliberately designed.
- Project-plane validation cleanup remains a separate active hygiene item.

## Recommended Next Actions
1. Use the existing validation path before prompt or exporter changes: `scripts/lint`,
   `scripts/test`, `taurcode validate --prompts prompts/taurcode`, export, and
   `taurcode roundtrip espanso`.
2. Keep any future Espanso construct support in narrow design/implementation PRs with
   fixtures and semantic normalization rules.
3. Resolve remaining project-plane validation cleanup under
   `WI-PROJECT-PLANE-VALIDATION-CLEANUP` without changing roundtrip behavior.
