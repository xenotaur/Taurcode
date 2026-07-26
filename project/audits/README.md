# Audit Reports

This directory holds standalone audit reports: focused, evidence-based reviews of a specific area of
the repository or its behavior. Audits are analysis artifacts — they diagnose and recommend, but do
not themselves change code.

Use an audit when you want a durable, reviewable assessment to remain visible in `project/`, for
example a coverage survey, a security review, a documentation-consistency review, or a dogfooding
report on a workflow.

## Conventions

- One report per file, named `YYYY-MM-DD-<slug>-audit.md` or `<slug>_audit.md`.
- State the scope, method, findings (ideally severity-ranked), and recommendations.
- Ground findings in the actual repository state and cite `file:line` where practical.
- Keep audits analysis-only. When an audit recommends changes, capture the follow-up as a work item
  (`project/work_items/`) or a design update; do not fold implementation into the audit itself.

## Index

_No audit reports yet. Add a line here linking each report as it lands._
