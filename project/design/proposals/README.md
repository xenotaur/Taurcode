# Design Proposals

This directory contains lightweight architectural proposals for Taurcode and the LRH project control plane.

Proposals should be detailed enough to guide later implementation prompts and work-item planning, but they should avoid premature overengineering. Accepted implementation work can be split into follow-up PRs and LRH work items.

Use this directory for design direction that is more specific than `project/design/design.md` but not yet ready to be treated as implemented project behavior.

## Current Proposals

- [Espanso Metadata Round-Trip Proposal](espanso_metadata_roundtrip.md)
- [Prompting Best Practices and Review Framework](prompting-best-practices-and-review-framework.md)
- [Semantic Roundtrip and Regression Suite Design Proposal](semantic_roundtrip_regression_design.md)
- [Frontmatter Dependency Audit](frontmatter-dependency-audit.md) audits the local `frontmatter` shim, its interaction with `python-frontmatter`, and the recommended migration path.
