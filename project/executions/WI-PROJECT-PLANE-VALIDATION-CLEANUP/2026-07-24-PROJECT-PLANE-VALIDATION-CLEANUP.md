---
prompt_id: PROMPT(WI-PROJECT-PLANE-VALIDATION-CLEANUP:APPLY_VALIDATION_FIXES)[2026-07-24T13:33:54-04:00]
date: 2026-07-24
scope: WI-PROJECT-PLANE-VALIDATION-CLEANUP
status: landed
pr: https://github.com/xenotaur/Taurcode/pull/54
commit: 3801f353c1fed70af9f625c1630eb1e780a04c2c
session_transcript: claude-app:6389d691-ab62-496c-b953-aada72706c77
---

## Summary
Resolved the outstanding `lrh validate` project-plane errors under
`WI-PROJECT-PLANE-VALIDATION-CLEANUP` by repairing work-item frontmatter to the
current LRH schema, removing a committed duplicate work-item file, and aligning
the cleanup item's status bucket. No LRH validation rules were weakened and no
Taurcode runtime behavior was changed.

## Result
- Removed the stray top-level duplicate
  `project/work_items/WI-PROJECT-PLANE-VALIDATION-CLEANUP.md` (byte-identical to
  the bucketed copy), clearing `WORK_ITEM_ID_DUPLICATE`,
  `PLANNING_DUPLICATE_ID`, and `WORK_ITEM_BUCKET_INVALID`.
- Moved `WI-PROJECT-PLANE-VALIDATION-CLEANUP` from `active/` to `proposed/` to
  match its `status: proposed`, clearing `WORK_ITEM_BUCKET_STATUS_MISMATCH`;
  set `type: operation`, `owner: anthony`, and `resolution: null`.
- `WI-BOOTSTRAP-0001`: added `type: deliverable`, converted `related_focus` to a
  list, added `blocked`/`blocked_reason`, added a non-empty `resolution`, and
  set `owner: anthony`.
- `WI-CANONICAL-PROMPTS-0002`: changed `resolution: >-` to `>` (LRH's
  frontmatter reader only recognizes the bare `>` folded-scalar token, so `>-`
  produced a `YAML_PARSE_ERROR` that also cascaded into
  `UNKNOWN_DESIGN_PROPOSAL_WORK_ITEM` for
  `design/proposals/adopted/espanso_metadata_roundtrip.md`) and set
  `type: deliverable`.

## Validation
- `lrh validate`: 0 errors, 0 warnings (was 19 errors).
- `scripts/lint`: passed (ruff + black).
- `scripts/test`: passed (190 tests).
- `scripts/version tools`: matches `constraints-dev.txt` pins
  (black 26.3.1, ruff 0.15.12, coverage 7.13.5).

## Follow-up
- The Background/Acceptance sections of the cleanup work item still quote the
  historical 14-error output; they can be refreshed or the item can be closed
  out now that its acceptance criteria (clean `lrh validate`, passing
  lint/test) are met.
