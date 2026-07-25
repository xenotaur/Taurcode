# Design Backlog

Lightweight list of deferred ideas that are not yet ready for a formal
proposal or work item. Each entry should record what was noted, why it was
deferred, and where it came from so a future reader can act on it without
re-deriving context.

---

## Backfill `session_transcript` on pre-existing `pending` execution records

**Noted:** 2026-07-25, while landing PR #47 and PR #60 and updating one
`_CONFIRM` record's `session_transcript` from `pending` to the real
`claude-app:<uuid>` transcript once the session URL became available.

**Idea:** Several execution records under `project/executions/AD_HOC/`
still carry `session_transcript: pending` from earlier sessions:
`2026_07_23_18_36_51_WI_ESPANSO_INSTALL_COMMAND_REVIEW.md`,
`2026_07_23_23_59_59_WI_ESPANSO_INSTALL_COMMAND_CONFIRM.md`,
`2026_07_24_13_48_18_PROJECT_PLANE_VALIDATION_CLEANUP_REVIEW.md`, and
`2026_07_24_13_51_23_PROJECT_PLANE_VALIDATION_CLEANUP_CONFIRM.md`. Sweep
these and backfill the real `claude-app:<uuid>` transcript on each, once the
originating session's `claude.ai/.../local_<uuid>` URL can be recovered.

**Status:** Deferred — this is pure traceability hygiene, not a functional
gap. `lrh validate`'s `session_transcript` checks are advisory-only
(warnings, never errors — see
`src/lrh/control/validator.py:175-207` in
`LogicalRoboticsHarness/logical_robotics_harness`), and `pending` is itself
an accepted sentinel value, not a validation finding. None of these four
records can be backfilled without the session URL from whoever ran that
original session; revisit if those URLs surface, or fold into a future
"session-transcript hygiene sweep" pass across the whole project control
plane rather than fixing them one at a time.

**Related:** `project/executions/AD_HOC/2026_07_23_18_36_51_WI_ESPANSO_INSTALL_COMMAND_REVIEW.md`;
`project/executions/AD_HOC/2026_07_23_23_59_59_WI_ESPANSO_INSTALL_COMMAND_CONFIRM.md`;
`project/executions/AD_HOC/2026_07_24_13_48_18_PROJECT_PLANE_VALIDATION_CLEANUP_REVIEW.md`;
`project/executions/AD_HOC/2026_07_24_13_51_23_PROJECT_PLANE_VALIDATION_CLEANUP_CONFIRM.md`.
