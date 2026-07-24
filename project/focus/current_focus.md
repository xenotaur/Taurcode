---
id: FOCUS-BOOTSTRAP
title: Post-roundtrip foundation stabilization
status: active
priority: high
owner: TBD
---

# Current Focus

## Active Priority
- Keep the completed canonical prompt and Espanso roundtrip foundation stable while separating
  project-plane cleanup and future feature expansion into narrow follow-up work.

## Why This Appears Current
- Taurcode now has the v1 implementation path that earlier project artifacts called for:
  canonical prompt sources, Espanso import/export, metadata preservation, semantic
  roundtrip checks, lint/preflight diagnostics, operational scripts, tests, a migrated
  prompt corpus, and Diátaxis-style docs.
- The next useful work is not another broad foundation slice; it is targeted hardening,
  project/control-plane hygiene, and separately designed feature expansion.

## Priorities
1. Treat `prompts/taurcode/*.md` as the canonical source of truth for the Taurcode
   prompt package.
2. Preserve supported Espanso roundtrip semantics when modifying prompt loading, export,
   import, linting, formatting, or docs.
3. Keep unsupported Espanso constructs explicit through diagnostics or raw fallback
   preservation instead of silently claiming support.
4. Complete project-plane validation cleanup under its dedicated work item.
5. Scope future exporter targets, install behavior, or advanced Espanso support as
   separate design/implementation work.

## Non-Goals
- Adding new CLI commands without a dedicated work item and tests.
- Expanding Espanso importer/exporter behavior without a dedicated design and tests.
- Building additional regression automation as part of the closeout itself.
- Collapsing project/control-plane cleanup into runtime feature work.

## Exit Criteria
- Current status, roadmap, focus, work item state, evidence, and execution records
  accurately show the Espanso roundtrip foundation as complete.
- Future work is represented as follow-up stabilization or explicitly scoped feature work,
  not as unfinished foundation implementation.
