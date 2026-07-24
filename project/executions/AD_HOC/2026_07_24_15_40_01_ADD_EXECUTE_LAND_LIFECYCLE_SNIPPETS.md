---
execution_id: 2026_07_24_15_40_01_ADD_EXECUTE_LAND_LIFECYCLE_SNIPPETS
prompt_id: PROMPT(AD_HOC:ADD_EXECUTE_LAND_LIFECYCLE_SNIPPETS)[2026-07-24T15:39:05-04:00]
work_item: AD_HOC
status: landed
rerun_of: 
pr: https://github.com/xenotaur/Taurcode/pull/55
commit: e1cb50c990e2fd6d4bae6f660b9c94468df83ac5
created_at: 2026-07-24T15:40:01-04:00
agent: claude_code
instruction_source: interactive session (chat-driven, no work item)
---

# Summary

Add two Espanso prompt snippets encoding the LRH post-implementation lifecycle
chain in a "nearly autonomous except-for-issues" style: `:execute` (full chain
from `/lrh-implement` through PR, review, merge, and `/lrh-closeout`) and
`:land` (the post-PR tail only, for an already-open PR). Landed as PR #55. A
companion metadata-drift fix was split into PR #56 (see Follow-up).

# Result

New source prompts `prompts/taurcode/execute.md` (`:execute`) and
`prompts/taurcode/land.md` (`:land`), with the generated Espanso package
`exports/espanso/package/package.yml` regenerated to include both matches.
Both snippets encode:

- **one hard human MERGE GATE** (never merge without explicit in-session
  approval; summarize the PR and how it changed over review before asking), and
- a **REVIEW-LANDED timing rule** — do not act on review until it has actually
  completed; an empty thread list right after pushing is not a clean review, and
  a review that completes with zero findings is a clean pass (not an infinite
  wait);
- a one-line **CHAIN-NOTE** evidence signal appended to the execution record's
  Result section and echoed in the final report;
- an optional free-form postscript for per-run context (e.g. the
  `/lrh-closeout` session URL, still a manual paste).

Drafted behind two human gates (draft review, then execute). Two rounds of
human refinement before landing: a `:land` variant added alongside `:execute`
per the two-trigger decision, and the CHAIN-NOTE mechanism folded into the
existing record-landing step (no new numbered step, to keep step counts
stable). One review-response round on PR #55 resolved three Codex P1 findings —
`:execute` Step 2 no longer re-creates the PR that `/lrh-implement` already
opens; a zero-finding review now passes the review gate instead of looping; the
header reframed from "two human gates" to one merge gate plus a review-landed
rule — plus a Copilot note on the incidental `:dashes force_clipboard`
regeneration, kept as a faithful source-of-truth regen and documented in the PR.

CHAIN-NOTE: cycles=1; stops=0; gates=[merge]; friction="export regen sweeps in unrelated manifest + :dashes force_clipboard drift"; note="chat-driven session; execution record created retroactively at closeout"

# Validation

- `taurcode validate --prompts prompts/taurcode` — passed (22 prompts).
- `taurcode lint prompts --prompts prompts/taurcode` — passed.
- `taurcode format prompts --prompts prompts/taurcode --check` — passed.
- PR #55 CI: coverage, lint, workflow-files, and tests all SUCCESS.
- Review landed clean after fixes: Copilot and Codex both passed; all four
  review threads answered.

# Follow-up

- PR #56 (`fix-espanso-manifest-drift`, commit `a3df55d`) regenerates the stale
  checked-in `exports/espanso/package/_manifest.yml` to match the curated
  source; reviewed clean, at the merge gate as of this writing.
- Pre-existing `taurcode lint espanso` error `manifest-name-mismatch` (manifest
  `name: taurcode` vs package directory `package`) is unresolved — rename the
  directory or accept the mismatch.
- Post-merge: run `taurcode install espanso --prompts prompts/taurcode
  --restart` so the local Espanso package picks up `:execute` and `:land`
  (Taurcode does not sync it automatically).
