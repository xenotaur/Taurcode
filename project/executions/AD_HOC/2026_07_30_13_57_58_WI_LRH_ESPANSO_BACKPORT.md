---
execution_id: 2026_07_30_13_57_58_WI_LRH_ESPANSO_BACKPORT
prompt_id: PROMPT(AD_HOC:WI_LRH_ESPANSO_BACKPORT)[2026-07-30T13:55:54-04:00]
work_item: AD_HOC
status: in_progress
rerun_of:
pr: https://github.com/xenotaur/Taurcode/pull/71
commit: 683c7cb
created_at: 2026-07-30T13:57:58-04:00
agent: claude_app
instruction_source: project/work_items/proposed/WI-LRH-ESPANSO-BACKPORT.md
session_transcript: pending
---

# Summary

Created `WI-LRH-ESPANSO-BACKPORT`, the first of three tracks under
`WS-LRH-BACKPORT-AND-HARDENING`: the `prompts/lrh/` Espanso backport (curated
`:lrh-`-prefixed snippets shipped as a separate `lrh` package, with a
checked-in generated export at `exports/espanso/lrh/`).

# Result

Wrote `project/work_items/proposed/WI-LRH-ESPANSO-BACKPORT.md` with a
duplication/demand prior-art check (both clean — no existing implementation,
no unresolved demand beyond the governing proposal itself), Scope, Required
Changes, Non-Goals, Acceptance Criteria, and Validation sections. Opened
PR #71 with the work item file. This record documents the item's *creation*
only — the item itself remains `proposed` and unimplemented.

# Validation

- `lrh validate` — 0 errors, 0 warnings, run before writing the file and
  again after.

# Follow-up

- `session_transcript` is `pending` — update to `claude-app:<session-id>`
  after this session ends.
- Step 11 offer (adding this WI to `WS-LRH-BACKPORT-AND-HARDENING`'s
  `work_items:` list) is still open — not yet actioned in this PR.
- The work item's own Open Question (whether to retire
  `prompts/taurcode/implement.md` once `:lrh-implement` exists) is
  unresolved by design, not an oversight.
