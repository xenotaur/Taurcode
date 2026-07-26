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
violation of LRH's execution-record immutability model
(`project/executions/README.md`): the "Land the execution record" step in
`prompts/taurcode/land.md` and `prompts/taurcode/execute.md` unconditionally
told the agent to append a CHAIN-NOTE line to the primary execution record's
body under its `# Result` section before pushing — even when that record was
only having its `status` flipped to `landed`, not authored fresh. Appending
to an already-committed narrative body is a rewrite the LRH schema forbids.
Confirmed the bug had already fired in this repo: PR #60's execution record
(`2026_07_25_15_19_05_LAND_MINT_BEFORE_DIRECT_FIX.md`) had its `# Result`,
written at implement-time, mutated at land-time to append its CHAIN-NOTE.

# Result

Rewrote the "Land the execution record" closing paragraph in both
`prompts/taurcode/land.md` (Step 6) and `prompts/taurcode/execute.md`
(Step 8), identically:

- Added an explicit immutability statement: an existing record's narrative
  body (`# Summary`/`# Result`/`# Validation`/`# Follow-up`) must never be
  edited, even to fix a stale fact — corrections belong in a later, separate
  follow-up record. (This closes the other half of the same issue: the
  no-narrative-rewrite rule was previously only implicit.)
- Split the CHAIN-NOTE placement by case: in the **backfill** case (no prior
  record existed), the line is written into the new record's `# Result`
  section as part of authoring that body for the first time — that's fine,
  it's an original write, not a rewrite. In the **found** case (an existing
  primary record's `status` is only being flipped), its body was already
  committed in an earlier step, so the file is left untouched entirely; the
  CHAIN-NOTE line is reported in chat only. Considered minting a throwaway
  record just to hold the line in the found case, and considered carrying it
  as a new frontmatter key instead — rejected both: the README's allowed
  frontmatter-backfill fields (`status`, `pr`, `commit`, `agent`,
  `instruction_source`, `session_transcript`) don't include an open metric
  field, and forcing a new record purely to hold one line is unwarranted
  ceremony for the common (clean-review) case.
- Verified issues 2 (find-or-backfill, no-`pr:`-only selection) and 3
  (primary-record ambiguity stop-and-ask) were already correctly handled by
  a prior PR (#58) and needed no change.

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
