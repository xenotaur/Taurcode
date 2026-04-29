# Roadmap

## Horizon
Roadmap for moving from current Espanso-centric assets to canonical prompt authoring and deterministic exports.

## Phase 0 — LRH Bootstrap (Completed)
- Create authoritative LRH artifacts under `project/`.
- Record baseline evidence and status.

## Phase 1 — Canonical Prompt Design Alignment (Current)
- Record canonical prompt file design in project docs.
- Define source-of-truth boundary and exporter target behavior.
- Define validation expectations and declared v1 Espanso support scope.

## Phase 2 — Canonical Prompt System Implementation
- Add `src/taurcode` package scaffold and CLI skeleton.
- Add canonical Markdown/frontmatter loader and validator.
- Add deterministic Espanso exporter to `build/espanso/<package>/`.
- Add importer for simple static Espanso replacements.
- Add docs for authoring, validation, export, and migration.

## Phase 3 — Install and Extended Feature Support (Deferred)
- Evaluate explicit install command only after export/validation behavior is reliable.
- Evaluate support for advanced Espanso constructs with explicit detection and compatibility documentation.
