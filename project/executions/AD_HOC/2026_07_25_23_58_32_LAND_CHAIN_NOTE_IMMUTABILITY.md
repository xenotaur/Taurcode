---
execution_id: 2026_07_25_23_58_32_LAND_CHAIN_NOTE_IMMUTABILITY
prompt_id: PROMPT(AD_HOC:LAND_CHAIN_NOTE_IMMUTABILITY)[2026-07-25T23:58:16-04:00]
work_item: AD_HOC
status: in_progress
rerun_of: 
pr: 
commit: 
created_at: 2026-07-25T23:58:32-04:00
---

# Summary

Dogfooding `:land` end-to-end on an LRH governance PR (#417) surfaced a
violation of LRH's execution-record immutability model (the narrative body
of a record, once merged, must not be rewritten — an authoritative statement
of this rule lives upstream in `logical_robotics_harness`'s
`project/executions/README.md`; this repo's own copy at
`project/executions/README.md` didn't document it until this PR, see below):
the "Land the execution record" step in `prompts/taurcode/land.md` and
`prompts/taurcode/execute.md` unconditionally told the agent to append a
CHAIN-NOTE line to the primary execution record's body under its `# Result`
section before pushing — even when that record's PR had already merged in
the preceding step and only its `status` was being flipped to `landed`, not
authored fresh. Appending to an already-merged narrative body is a rewrite
the immutability rule forbids. Confirmed the bug had already fired in this
repo: PR #60's execution record
(`2026_07_25_15_19_05_LAND_MINT_BEFORE_DIRECT_FIX.md`) had its `# Result`,
written and merged at implement/review time, mutated after merge at
land-time to append its CHAIN-NOTE.

# Result

Rewrote the "Land the execution record" closing paragraph in both
`prompts/taurcode/land.md` (Step 6) and `prompts/taurcode/execute.md`
(Step 8), identically:

- Added an explicit immutability statement, scoped precisely: the *primary*
  record's narrative body (`# Summary`/`# Result`/`# Validation`/
  `# Follow-up`) becomes immutable once the PR that authored it has merged
  (Step 4/6's merge gate, which always fires before this land step) — even
  to fix a stale fact, corrections belong in a later, separate follow-up
  record. Editing that same record across pushes *within* the still-open PR
  that originally authored it (e.g. during `/lrh-review-response` /
  `/lrh-confirm-fixes` iteration) is normal authoring, not a rewrite — this
  closes the other half of the same issue, since the rule and its merge-time
  boundary were previously only implicit.
- Split the CHAIN-NOTE placement by case: in the **backfill** case (no prior
  record existed), the line is written into the new record's `# Result`
  section as part of authoring that body for the first time — that's fine,
  it's an original write, not a rewrite. In the **found** case (the primary
  record's PR already merged and only its `status` is being flipped), a
  small new `AD_HOC` closeout-note record is minted instead
  (`rerun_of: <primary execution_id>`, `status: landed` immediately), with
  the CHAIN-NOTE written fresh into *its* `# Result` — durable and greppable
  without touching the merged primary record. (Revised from this record's
  first draft, which skipped persisting the line in the found case entirely;
  PR #64 review — Codex, P1 — correctly flagged that as breaking
  `WS-PROMPT-LIFECYCLE-TOOLKIT`'s exit criterion that a CHAIN-NOTE lands with
  every closeout. Fixed via `/lrh-review-response`; see
  `2026_07_26_02_12_18_FIX_LAND_CHAIN_NOTE_IMMUTABILITY_REVIEW.md`.)
- Verified issues 2 (find-or-backfill, no-`pr:`-only selection) and 3
  (primary-record ambiguity stop-and-ask) were already correctly handled by
  a prior PR (#58) and needed no change.
- Added the immutability rule and its merge-time scope to this repo's own
  `project/executions/README.md` (previously a naming/minimum-fields stub
  with no mention of it — PR #64 review, Copilot and Codex, flagged the
  citation as misleading until this landed).

Regenerated `exports/espanso/taurcode/package.yml` via
`taurcode export espanso --prompts prompts/taurcode --output exports/espanso/taurcode`
since both changed prompt bodies are exported there.

# Validation

- `scripts/version tools` — Python 3.11.8, black 25.11.0 (pre-existing drift
  from `constraints-dev.txt`'s pinned 26.3.1, unrelated to this change — see
  `feedback_dev_toolchain_version_drift` memory), ruff 0.15.12
- `scripts/format --check --diff` / `scripts/lint` — only flag the
  pre-existing `tests/espanso_import_test.py` drift-reformat, untouched by
  this change
- `scripts/test` — 199 tests passed
- `taurcode validate --prompts prompts/taurcode` — 23 prompts, passed
- `taurcode roundtrip espanso --input exports/espanso/taurcode --prompts prompts/taurcode` — 0 differences
- `lrh validate` — 1 pre-existing error (`MISSING_FRONTMATTER` on an
  unrelated legacy execution record), unaffected by this change

# Follow-up

None outside this PR.
