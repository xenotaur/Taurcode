# Roadmap

## Horizon
Roadmap for moving from Espanso-centric assets to canonical prompt authoring and deterministic, reviewable exports.

## Phase 0 — LRH Bootstrap (Completed)
- Create authoritative LRH artifacts under `project/`.
- Record baseline evidence and status.

## Phase 1 — Canonical Prompt Design Alignment (Completed)
- Record canonical prompt file design in project docs.
- Define source-of-truth boundary and exporter target behavior.
- Define validation expectations and declared v1 Espanso support scope.

## Phase 2 — Espanso Roundtrip Foundation (Completed)
- Add `src/taurcode` package scaffold and CLI skeleton.
- Add canonical Markdown/frontmatter loader and validator.
- Add deterministic Espanso exporter.
- Add importer and merge importer for supported static Espanso replacements.
- Preserve raw fallback data and diagnose unsupported Espanso constructs.
- Preserve Espanso package metadata assets and generate deterministic defaults.
- Add prompt-source lint/format checks and Espanso lint/preflight diagnostics.
- Add semantic normalization and `taurcode roundtrip espanso` for supported
  roundtrip behavior.
- Migrate the real Taurcode prompt corpus into `prompts/taurcode/`.
- Add tests, operational scripts, and Diátaxis-style documentation for the foundation
  workflow.

## Phase 3 — Hardening and Extended Feature Support (Current / Deferred by Scope)
- Keep project-plane validation cleanup separate from runtime behavior changes.
- Add future Espanso construct support only with explicit design, validation,
  importer/exporter behavior, and regression fixtures.
- Evaluate additional exporter targets after the Espanso foundation remains stable.
- Evaluate explicit install/sync commands only after export and roundtrip validation
  continue to be trusted.
