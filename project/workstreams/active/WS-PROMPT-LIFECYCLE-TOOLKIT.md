---
id: WS-PROMPT-LIFECYCLE-TOOLKIT
kind: planning_node
title: Prompt Lifecycle Toolkit
status: active
stage: reviewing
origin: ad_hoc
summary: Reusable Espanso prompt snippets that drive an LRH work item through its post-implementation lifecycle (implement, PR, review, merge, closeout) nearly autonomously, plus a PR go/no-go evaluator.
rationale: Added as a chain of ad-hoc chat-driven PRs with no planning artifact; this workstream captures the stream retroactively so its intent, scope, and remaining work stay visible and future ':remains' checks have exit criteria to grade against.
related_focus:
  - FOCUS-BOOTSTRAP
work_items:
  - WI-DOCUMENT-LIFECYCLE-SNIPPETS
execution_records:
  - 2026_07_24_15_40_01_ADD_EXECUTE_LAND_LIFECYCLE_SNIPPETS
  - 2026_07_24_16_45_00_FIX_ESPANSO_MANIFEST_NAME_MISMATCH
  - 2026_07_24_19_08_07_BACKFILL_LAND_FIND_OR_BACKFILL_EXECUTION_RECORD
  - 2026_07_25_02_17_56_BACKFILL_ADD_ASSESS_SNIPPET
  - 2026_07_25_15_19_05_LAND_MINT_BEFORE_DIRECT_FIX
exit_criteria:
  - ":execute and :land encode the LRH lifecycle with one merge gate and a review-landed rule."
  - "The land step finds or honestly backfills the execution record."
  - "A one-line CHAIN-NOTE evidence signal lands with each closeout."
  - "A reusable :assess PR go/no-go snippet exists."
  - "The corpus validates/lints/formats clean, exports idempotently, and installs locally."
  - "README/docs document :execute, :land, and :assess so they are discoverable."
---

# Prompt Lifecycle Toolkit

## Context

Taurcode's prompt corpus already covered planning, design, review, and
Codex-targeted implementation. This workstream adds the *tail* of the lifecycle:
reusable snippets that hand a session a work item (or an open PR) and drive it to
closeout with a disciplined human-in-the-loop contract.

## Scope

- `:execute` — full chain from `/lrh-implement` through PR, review, merge, and
  `/lrh-closeout`.
- `:land` — the post-PR tail only, for an already-open PR.
- The **CHAIN-NOTE** evidence line landed into the execution record at closeout.
- The **find-or-backfill** land step: identify the primary execution record for
  the PR, or honestly backfill an AD_HOC record when none exists.
- The **mint-before-fix** refinement (PR #60): `:land` mints the primary
  execution record before applying direct review fixes, mirroring
  `/lrh-implement`'s convention, so backfill becomes a safety net rather than the
  routine path.
- `:assess` — a PR go/no-go evaluator returning a decisive
  PROCEED / RECONSIDER recommendation, judged on merit not authorship.
- Supporting export-plane hygiene needed to land the above cleanly (manifest
  metadata sync and the export-directory rename).

## Status

Deliverables above have landed and closed out across PRs #55–#60, each with an
execution record. What remains before this workstream resolves is documentation:
README and `docs/` still name only `:prompt-review` and `:lrh-template-review`
and do not mention `:execute`, `:land`, or `:assess`, so the toolkit is
undiscoverable except by reading the corpus.

## Remaining work

- Document `:execute`, `:land`, and `:assess` in `README.md` / `docs/` (the open
  exit-criterion). Capture as a narrowly scoped work item when picked up.
- Track the eventual removal of the manual `<SESSION_URL — paste View > Copy URL>`
  step in `:execute` / `:land` once that requirement goes away.

## Relationship to the roadmap

This stream fits the roadmap Horizon ("canonical prompt authoring") and lands
under Phase 3 hardening as prompt-authoring workflow content. It does not change
exporter/importer runtime behavior.
