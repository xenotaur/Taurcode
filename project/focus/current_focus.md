---
id: FOCUS-BOOTSTRAP
title: Bootstrap focus (canonical prompt alignment phase)
status: active
priority: high
owner: TBD
---

# Current Focus

## Active Priority
- Align project control-plane artifacts around canonical Markdown/frontmatter prompt authoring and Espanso-as-export-target behavior.

## Why This Appears Current
- Existing repository evidence is Espanso package-centric.
- A design decision is needed so future implementation PRs converge on one canonical format.

## Priorities
1. Treat `prompts/*.md` as the intended source of truth.
2. Define v1 required/optional canonical fields and validation checks.
3. Define deterministic export path `build/espanso/<package>/` with no automatic local install.
4. Capture migration expectations from existing Espanso package assets.

## Non-Goals
- Implementing the Python package or CLI in this alignment PR.
- Claiming support for advanced Espanso features without explicit handling.

## Exit Criteria
- Design docs clearly describe canonical prompt format and source-of-truth boundary.
- Work item backlog includes implementation slices for loader/validator/exporter/importer/docs.
- Execution record exists for this design-alignment prompt.
