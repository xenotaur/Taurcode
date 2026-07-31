---
execution_id: 2026_07_31_04_41_02_WI_TAURCODE_RELEASE_HARDENING_CLOSEOUT
prompt_id: PROMPT(AD_HOC:WI_TAURCODE_RELEASE_HARDENING_CLOSEOUT)[2026-07-31T04:40:52+00:00]
work_item: AD_HOC
status: landed
rerun_of:
pr: https://github.com/xenotaur/Taurcode/pull/74
commit: 1baae1221263e31885ef1f2ba03fe1fc62434138
created_at: 2026-07-31T04:41:02+00:00
agent: claude_app
instruction_source: https://github.com/xenotaur/Taurcode/pull/74
session_transcript: claude-app:bbea97a2-74d5-4f02-ab32-ab5ff59b2454
---

# Summary

`/lrh-land` chain-run backfill record for PR #74 (`WI-TAURCODE-RELEASE-HARDENING`
creation). No primary execution record ever existed for this branch —
`taurcode:lrh-work-item` doesn't create one — so this record is authored
directly as the backfill, with the CHAIN-NOTE in this Result section per the
found-or-backfill matrix.

# Result

`taurcode:lrh-work-item` created
`project/work_items/proposed/WI-TAURCODE-RELEASE-HARDENING.md`, scoping the
third and final track in `WS-LRH-BACKPORT-AND-HARDENING`: dynamic versioning
via setuptools-scm, a trimmed `scripts/release-smoke` (isolated
build/install/invoke/leak-check core, skipping LRH's package-data
template-loading checks), tag-triggered `release.yml` +
`testpypi-rehearsal.yml` using PyPI Trusted Publishing, targeting a `v0.1.0`
tag/rehearsal. Two scoping questions were confirmed with the user rather
than assumed: one work item (not split further, given the pieces are
tightly coupled) and `v0.1.0` as the target semver. The workstream's
`work_items:` list was updated to include this item in the same PR — all
three tracks of `WS-LRH-BACKPORT-AND-HARDENING` now have work items, none
implemented yet.

CHAIN-NOTE: `cycles=1; stops=0; gates=[merge]; friction=none; note="Single review-response -> confirm-fixes cycle, converged clean (4 comments, all fixed). Two were substantive, not just polish: a forbidden_actions/acceptance-criteria contradiction (publish_package vs. the required TestPyPI upload), and a genuine tag-collision safety gap between the rehearsal tag and release.yml's production-publish trigger, resolved via an explicit Risk Notes ordering requirement rather than scope expansion. Applied the (planning only) PR-title convention from the prior round's memory finding. Merge gate fired normally; user approved explicitly in-session."`

# Validation

- `lrh validate` — 0 errors, 0 warnings, confirmed after all closeout edits.

# Follow-up

- Work item remains `proposed` — implementation is separate, future work.
- Workstream intentionally left open — 0 of 3 listed tracks resolved yet.
- This was the last of the three tracks to reach the planning stage; the
  workstream now has full coverage but zero implementation.
