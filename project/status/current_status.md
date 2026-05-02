---
id: STATUS-CURRENT
title: Current Project Status
scope: project
status: active
health: yellow
---

# Current Status

## Summary
- The repository intent is now explicitly documented as canonical Markdown/frontmatter prompts feeding deterministic target exporters (including Espanso).
- Runtime implementation for this design is not yet present.

## Evidence Basis
- `README.md`
- `espanso/package/package.yml`
- `espanso/package/_manifest.yml`
- `project/design/design.md`
- `project/work_items/active/WI-CANONICAL-PROMPTS-0002.md`

## Current Health
- **Yellow**: Direction is clearer, but implementation and validation tooling are pending.

## Active Priorities
- Preserve canonical prompt design and source-of-truth boundary in future PRs.
- Implement loader/validator/exporter/importer slices incrementally.

## Risks
- Legacy Espanso assumptions may leak back into canonical authoring decisions.
- Install behavior could be introduced too early before export validation is trustworthy.

## Recommended Next Actions
1. Start implementation scaffold and CLI entrypoint under `src/taurcode`.
2. Implement canonical prompt parser/validator plus uniqueness checks.
3. Implement deterministic exporter to `build/espanso/<package>/` and document review workflow.
