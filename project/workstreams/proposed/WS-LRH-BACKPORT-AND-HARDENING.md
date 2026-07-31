---
id: WS-LRH-BACKPORT-AND-HARDENING
kind: planning_node
title: LRH Prompt Backport (Espanso) and Taurcode PyPI Release Hardening
status: proposed
stage: designed
origin: design_review
summary: Coordinate the three tracks from the proposed design (prompts/lrh/ Espanso backport, taurcode show CLI, and Taurcode PyPI release hardening on LRH's proven pipeline) through work items to closeout.
related_focus:
  - FOCUS-BOOTSTRAP
related_roadmap: []
related_design:
  - project/design/proposals/proposed/lrh-backport-and-hardening/00_proposal.md
work_items:
  - WI-LRH-ESPANSO-BACKPORT
  - WI-TAURCODE-SHOW-COMMAND
  - WI-TAURCODE-RELEASE-HARDENING
exit_criteria:
  - "The lrh Espanso package builds from prompts/lrh/ with a curated manifest (not the tool's generated default) and installs independently of the taurcode package."
  - "taurcode show resolves --prompts all against an explicit, maintained corpus list, not a directory glob of prompts/*/."
  - "Taurcode's release pipeline (dynamic versioning via setuptools-scm, scripts/release-smoke, scripts/version verify, release.yml, testpypi-rehearsal.yml) is in place and a TestPyPI rehearsal succeeds."
  - "A real tagged PyPI release of Taurcode is published, following the author's own PyPI Trusted Publisher and GitHub Environment configuration."
  - "Each deliverable above has a corresponding resolved work item."
---

# LRH Prompt Backport (Espanso) and Taurcode PyPI Release Hardening

## Purpose

This workstream coordinates the implementation of `project/design/proposals/proposed/lrh-backport-and-hardening/00_proposal.md` (merged via PR #67): backporting LRH slash-command skills into `:lrh-`-prefixed Espanso snippets shipped as a separate `lrh` package, adding a `taurcode show` CLI command, and hardening Taurcode's release tooling for an actual PyPI release using LRH's own proven pipeline as the template.

## Scope

- Curated `prompts/lrh/` corpus and `lrh` Espanso package, sourced from this repo for now.
- `taurcode show <keyword> --prompts <dir|all>` CLI command.
- Taurcode release hardening: dynamic versioning, trimmed `scripts/release-smoke`, `scripts/version verify`, `release.yml` + `testpypi-rehearsal.yml`, then a TestPyPI rehearsal and a real tagged release.

## Prior Art Check

### Duplication search
- In-repo: No existing implementation of this workstream's scope found. Related prior art: `prompts/taurcode/implement.md` (existing hand-authored `:implement` backport of `/lrh-implement`) and `prompts/taurcode/lrh-template-review.md` (existing `:lrh-` namespace precedent) — both already identified by the governing proposal as artifacts this work extends/relocates rather than duplicates. Also matched: the proposal's own listing in `project/design/proposals/README.md`.
- Sibling repos: None identified beyond what the governing proposal already covers (LRH has no Espanso tooling; Taurworks and Prosoc share Taurcode's identical unresolved `scripts/publish` stub, noted as a longer-horizon, undecided angle in the proposal's Open Questions).
- External libraries: None identified — composes existing tools (Espanso, setuptools-scm, `pypa/gh-action-pypi-publish`) per the proposal.
- Recommendation: Proceed.

### Demand search
- Work items: None found in `project/work_items/proposed/`.
- Proposals: None found beyond the governing proposal itself.
- Backlog: No `project/design/backlog.md` exists in this repo.
- Recommendation: No action.

## Work Items

- **WI-LRH-ESPANSO-BACKPORT** — Add the `prompts/lrh/` Espanso backport package.
- **WI-TAURCODE-SHOW-COMMAND** — Implement the `taurcode show` CLI command.
- **WI-TAURCODE-RELEASE-HARDENING** — Harden Taurcode's release pipeline for PyPI.

All three tracks now have work items; none are implemented yet.

## Exit Criteria

See frontmatter `exit_criteria:` above.

## Non-Goals

- Does not move `prompts/lrh/` into LRH's own repo — deferred pending a real PyPI release and proven dogfooding value, a judgment call for the proposal's author to make personally.
- Does not decide the fleet-wide skill-extraction ordering (harden Taurcode first vs. design a reusable LRH skill first vs. build them together) — see Open Questions.
- Does not perform PyPI Trusted Publisher registration or GitHub Environment configuration — human account/repo-admin actions only.
- Does not harden Taurworks, LCATS, or Prosoc directly.
- Does not port LRH's full `release_smoke.py` (696 lines) verbatim — only the generically-useful isolation-check core.

## Relationship to Design

- Design proposal: `project/design/proposals/proposed/lrh-backport-and-hardening/00_proposal.md`

## Open Questions

- Fleet-wide skill-extraction ordering (the proposal's Decision 7 / Open Questions): harden Taurcode by hand first and extract a reusable LRH skill afterward, design the skill first and apply it, or build both together with Taurcode as the reference implementation. Deferred — Taurworks and Prosoc share the identical blocker, so this has payoff beyond Taurcode, but the ordering isn't decided.
