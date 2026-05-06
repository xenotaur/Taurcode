# Design

## Purpose
- Provide an LRH control plane for a repository that manages AI coding prompts and packages them for target text-replacement workflows.

## Scope
- Control-plane artifacts for intent, execution, constraints, and evidence.
- Repository-level interpretation of canonical prompt sources and generated packaging assets.

## Core Structure
- Intent layer: principles/goal/roadmap
- Execution layer: focus/work_items/contributors
- Constraint layer: guardrails
- Truth layer: evidence/status/memory

## Precedence and Interpretation Notes
- principles → goal → roadmap → focus → work_items → guardrails/runtime context

## Canonical Prompt Design Direction (v1)

### Source of truth
- `prompts/taurcode/*.md` is the intended canonical source of truth for the Taurcode prompt package.
- Canonical prompt files should be one Markdown file per prompt.
- Each file should use YAML frontmatter for machine-readable metadata and an unindented Markdown body for prompt text.
- Existing Espanso files should be treated as legacy input and/or generated target artifacts, not canonical authoring format.

### Canonical file shape

```markdown
---
id: codex-review
name: Codex Review
description: Ask Codex Cloud to review a proposed change.
keyword: ":tc-codex-review"
tags:
  - codex
targets:
  espanso:
    enabled: true
    package: taurcode
---

Review the following change.

Follow repository-specific instruction files (for example `AGENTS.md`, `CONTRIBUTING.md`, or `project/context/agents.md`).
Follow repository conventions and the surrounding file's style.

Return a concise implementation plan first.
```

### Required fields (v1)
- `id`
- `name`
- `description`
- `keyword`
- Markdown body text after frontmatter

### Optional fields (v1)
- `tags`
- `targets.espanso.enabled`
- `targets.espanso.package`

### Processing and output boundary
- Espanso is an export target, not the canonical source format.
- Espanso package generation should be deterministic and reviewable.
- Generated packages should be emitted to `build/espanso/<package>/`.
- v1 should not auto-copy generated packages into a local Espanso install location.
- A future explicit install command may be considered after validation/export behavior is trusted.

### Intended pipeline

```text
prompts/taurcode/*.md
  -> canonical Prompt objects
  -> validation
  -> target exporters
  -> build/espanso/<package>/
```

### Migration path from current assets

```text
existing espanso package files
  -> importer
  -> prompts/imported/ staging
  -> curated canonical prompts/taurcode/*.md
  -> validator
  -> exporter
  -> build/espanso/<package>/
```

### Validation expectations for implementation PRs
- frontmatter exists
- required fields exist
- body is nonempty
- prompt IDs are unique
- keywords are unique
- Espanso-enabled prompts have valid package metadata
- generated Espanso YAML can be parsed
- unsupported Espanso features are detected (not silently discarded) during import

### Espanso v1 scope
- Focus support on simple static replacements:
  - `trigger` maps from canonical `keyword`
  - `replace` maps from canonical Markdown body
- Detect/document complex features before claiming support:
  - variables
  - forms
  - scripts
  - regex triggers
  - imports
  - global variables

## Current Implementation Boundary
- Repository content includes the canonical `prompts/taurcode/` corpus plus legacy Espanso package artifacts under `espanso/package/`.
- The canonical Markdown/frontmatter system has an implemented loader, validator, importer, and Espanso exporter.

## Canonical vs legacy asset boundary
- Canonical authoring should occur in `prompts/taurcode/*.md`.
- Existing Espanso package files are legacy inputs and/or generated outputs for migration and interoperability.
- Contributors should avoid treating Espanso YAML as the long-term authoring source once canonical prompts are introduced.
