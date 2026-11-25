# Docs Audit Artifact Convention (v1)

A documentation audit records inventory, findings, and a proposed scope for
documentation organization. Taurcode stores audits in the LRH control plane
at `project/audits/docs/docs-audit-YYYY-MM-DD.md`. The date identifies the
audit. The documentation itself lives under `docs/`.

## Frontmatter

```yaml
---
id: AUDIT-DOCS-YYYY-MM-DD
audit_type: docs
schema_version: 1
status: proposed
repo_root: .
project_root: project
docs_root: docs
control_root: project
package_roots:
  - src/taurcode
framework: diataxis
recommended_next_prompt: organize_docs
recommended_phase: scaffold
---
```

- `id` uses the date in the audit filename. A new audit starts at `proposed`.
- The root and package fields describe the paths discovered during the audit.
  Use repository-relative paths so the artifact can be read from any clone.
- `framework` identifies the classification model. Diataxis separates tutorial,
  how-to, reference, and explanation content by reader need. Audits can also
  identify mixed documents and project-management material.
- `recommended_next_prompt` and `recommended_phase` identify the suggested
  follow-up workflow and starting phase.

## Required Sections

Write the following second-level headings in order. Subheadings may appear
within each section.

```markdown
## Summary
## Scope and roots inspected
## Current documentation inventory
## Current project and package layout
## Diataxis classification
## Navigation findings
## Accuracy findings
## Stale or ambiguous links
## Project-control-plane vs human-docs boundary
## Recommended target documentation structure
## Recommended phased PRs
## Proposed first PR scope
## Risks and cautions
## Validation commands for follow-up PRs
```

`lrh-doc-organize` reads `Proposed first PR scope` for phase 1 and uses
`Recommended phased PRs` for subsequent phases. The first scope names the
files to add, update, or move in one reviewable PR. Findings cite repository
evidence and distinguish shipping behavior from planned work.

See the [August 25, 2026 Taurcode audit](../../project/audits/docs/docs-audit-2026-08-25.md)
for a complete artifact.
