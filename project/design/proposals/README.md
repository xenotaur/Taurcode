# Design Proposals

This directory contains lightweight architectural proposals for Taurcode and the LRH project control plane.

Proposals should be detailed enough to guide later implementation prompts and work-item planning, but they should avoid premature overengineering. Accepted implementation work can be split into follow-up PRs and LRH work items.

Use this directory for design direction that is more specific than `project/design/design.md`. Proposed files capture open design direction; adopted files preserve accepted rationale that may later be distilled into canonical top-level design documentation.

## Lifecycle Buckets

Proposal lifecycle state is represented in two places: YAML frontmatter and bucket placement. Frontmatter `status` is authoritative; bucket placement should agree with it.

- `proposed/` contains proposals that are still being considered, scoped, or implemented.
- `adopted/` contains accepted proposals whose design direction has been adopted by the project.

Taurcode proposal status values are:

- `proposed`: the proposal is open for consideration or has not yet been accepted.
- `accepted`: the proposal has been adopted as project design direction.

Move a proposal to `adopted/` when its frontmatter status changes to `accepted`. When an adopted proposal's decisions become canonical long-term behavior, distill or promote the durable guidance into top-level `project/design/` documentation and leave the proposal as historical rationale.

## Adding a Proposal

1. Create a Markdown file under `proposed/`.
2. Start it with YAML frontmatter containing `id`, `type: design_proposal`, `status: proposed`, and `title`.
3. Keep the body focused on the problem, goals, non-goals, proposed direction, validation, and follow-up work.
4. Link the proposal from this README.

## Closing or Promoting a Proposal

1. Update frontmatter `status` to `accepted` when the project adopts the proposal.
2. Update any body-level status note so it does not contradict the frontmatter.
3. Move the file from `proposed/` to `adopted/`.
4. Update links that referenced the old path.
5. If the decision is now canonical project behavior, copy the durable rule into the appropriate top-level design document.

## Traceability Fields

Adopted design proposal frontmatter may include implementation traceability. Keep these fields ID-based so LRH validation can resolve them:

- `implemented_by` entries must reference work item IDs, such as `WI-CANONICAL-PROMPTS-0002`.
- `evidence` entries must reference evidence record IDs, such as `EV-0002`.
- Execution-record paths may be cited in evidence record bodies, but should not be used as `implemented_by` or `evidence` frontmatter values.

## Current Proposals

### Proposed

- [Prompting Best Practices and Review Framework](proposed/prompting-best-practices-and-review-framework.md)
- [Semantic Roundtrip and Regression Suite Design Proposal](proposed/semantic_roundtrip_regression_design.md)

### Adopted

- [Espanso Metadata Round-Trip Proposal](adopted/espanso_metadata_roundtrip.md)
- [Frontmatter Dependency Audit](adopted/frontmatter-dependency-audit.md) audits the local `frontmatter` shim, its interaction with `python-frontmatter`, and the implemented migration path.
