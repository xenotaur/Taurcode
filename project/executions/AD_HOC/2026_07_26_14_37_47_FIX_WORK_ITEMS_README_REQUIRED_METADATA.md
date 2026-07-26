---
execution_id: 2026_07_26_14_37_47_FIX_WORK_ITEMS_README_REQUIRED_METADATA
prompt_id: PROMPT(AD_HOC:FIX_WORK_ITEMS_README_REQUIRED_METADATA)[2026-07-26T14:37:47-04:00]
work_item: AD_HOC
status: in_progress
rerun_of: 
pr: https://github.com/xenotaur/Taurcode/pull/66
commit: 
created_at: 2026-07-26T14:37:47-04:00
agent: claude_code
instruction_source: interactive session (chat-driven, no work item); user asked for a `project/*/README.md` drift audit against LogicalRoboticsHarness's canonical copies, modeled on the pattern in PR #64
session_transcript: https://claude.ai/epitaxy/local_68756041-6b13-4f5a-9816-a741cb1f7ac5
---

# Summary

Audited Taurcode's ten `project/*/README.md` files against LRH's own live
(dogfooded) copies at
[`xenotaur/logical_robotics_harness` project/](https://github.com/xenotaur/logical_robotics_harness/tree/main/project)
for load-bearing drift — the pattern PR #64 found and fixed in
`project/executions/README.md`. Only 4 of 10 dirs (`audits`, `executions`,
`work_items`, `workstreams`) have a live LRH canonical copy to diff against;
the other 6 (`focus`, `goal`, `memory`, `principles`, `roadmap`, `status`)
have no LRH live README at all, only the bootstrap stub, which Taurcode's
copies already match verbatim and which nothing cites.

# Result

Found one confirmed load-bearing gap: `project/work_items/README.md`
documented only `id`/`status` as required frontmatter, but every actual
Taurcode work item (`WI-BOOTSTRAP-0001.md`, `WI-ESPANSO-INSTALL-COMMAND.md`,
etc.) sets `blocked`, `blocked_reason`, and `resolution`, and
`src/lrh/control/work_item_policy.py` in LRH confirms `lrh validate`
genuinely enforces those fields (`blocked_reason` required when
`blocked: true`; `resolution` required for terminal statuses, must be null
otherwise). LRH's own canonical `project/work_items/README.md` documents
this under "Required metadata." Applied the minimal fix: added a "Required
metadata" section to Taurcode's `project/work_items/README.md`, scoped to
only what Taurcode actually relies on (not a wholesale copy of LRH's fuller
workflow sections).

PR #66 review (Codex, Copilot) caught two gaps in the initial fix, both
verified against `src/lrh/control/validator.py` in LRH before applying:
`WORK_ITEM_REQUIRED_FIELDS` also requires `title` and `type` (missing from
the first pass, confirmed every existing Taurcode work item sets both), and
the `null`/`""` wording for `blocked_reason`/`resolution` was ambiguous —
`resolution` specifically must be exactly `null` (not `""`) for non-terminal
status per `WORK_ITEM_RESOLUTION_NON_TERMINAL`. Also added the missing
`abandoned` bucket to the status-bucket list, and replaced an absolute local
filesystem path in this record with a GitHub URL to the upstream LRH repo.

No drift found in `audits/README.md` (Taurcode's own conventions stub
matches its only citation) or `workstreams/README.md` (well-maintained;
diffs against LRH were narrative-only, not policy). The 6 no-canonical-doc
dirs and `executions/README.md` (already fixed by PR #64) needed no changes.

# Validation

- `lrh validate` — 0 errors, 0 warnings, both before and after the change.
- Documentation-only change; no code, tests, or exporter behavior affected.

# Follow-up

None. `commit` above will be backfilled once review converges and the PR
merges.
