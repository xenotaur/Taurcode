# Decision Log

## 2026-04-28: Bootstrap decision

### Summary
- Created a complete baseline LRH scaffold under `project/` using conservative, evidence-grounded content.

### Decisions
- Treated repository as `new` because no `project/` directory existed.
- Used README and Espanso package files as primary evidence for scope and design context.
- Marked owner/contributor identity as TBD rather than inferring names.

### Rationale
- Request required a standard LRH bootstrap when classification was `new`.
- Available repository signals were sufficient for a full scaffold but insufficient for specific ownership commitments.

### Uncertainty / Follow-ups
- Confirm maintainer identity and approval flow.
- Confirm broader integration targets beyond Espanso.
- Validate whether additional docs or workflows were intentionally omitted.

### Status
- Accepted (Bootstrap Phase)

## 2026-04-29: Canonical prompt source-of-truth decision

### Summary
- Adopted canonical Markdown prompt files with YAML frontmatter (`prompts/*.md`) as the design source of truth.
- Reframed Espanso as a generated export target, not canonical authoring format.

### Decisions
- Canonical prompt shape: YAML frontmatter metadata + unindented Markdown body text.
- Required v1 fields: `id`, `name`, `description`, `keyword`, and non-empty body.
- Optional v1 fields: `tags`, `targets.espanso.enabled`, `targets.espanso.package`.
- Export destination for generated Espanso packages: `build/espanso/<package>/`.
- No automatic copy/install into local Espanso paths in v1.

### Rationale
- Keeps prompt authoring human-readable, diffable, and close to final text.
- Enables deterministic validation and generation workflows.
- Supports migration from current Espanso assets while preserving a single canonical model.

### Follow-ups
- Implement loader/validator/exporter/importer slices in follow-on work.
- Detect unsupported Espanso features during import rather than silently dropping them.
- Revisit optional install command only after export/validation behavior is stable.

### Status
- Accepted (Design Direction)
