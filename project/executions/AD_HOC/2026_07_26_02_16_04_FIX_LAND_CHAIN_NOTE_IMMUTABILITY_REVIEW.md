---
execution_id: 2026_07_26_02_16_04_FIX_LAND_CHAIN_NOTE_IMMUTABILITY_REVIEW
prompt_id: PROMPT(AD_HOC:FIX_LAND_CHAIN_NOTE_IMMUTABILITY_REVIEW)[2026-07-26T02:12:18-04:00]
work_item: AD_HOC
status: landed
rerun_of: 2026_07_25_23_58_32_LAND_CHAIN_NOTE_IMMUTABILITY
pr: https://github.com/xenotaur/Taurcode/pull/64
commit: 4b9f7a2694028c701365e915ef247c853d857292
created_at: 2026-07-26T02:16:04-04:00
agent: claude_app
instruction_source: https://github.com/xenotaur/Taurcode/pull/64
session_transcript: claude-app:919ce4f1-d413-4149-a4f7-28c74883c40d
---

# Summary

PR #64 (fixing `:land`/`:execute`'s CHAIN-NOTE immutability violation) drew
6 review comments from Copilot and Codex: one P1 (Codex) and five
citation/wording issues (one P2 from Codex, four from Copilot) all rooted in
the same underlying gap.

# Result

Addressed all 6 comments:

- **P1 (Codex) — CHAIN-NOTE dropped in the common case.** The prior draft's
  "found" case (primary record already merged, only `status` flipping)
  reported the CHAIN-NOTE in chat only, never persisting it — which breaks
  `project/workstreams/active/WS-PROMPT-LIFECYCLE-TOOLKIT.md`'s exit
  criterion that "a one-line CHAIN-NOTE evidence signal lands with each
  closeout." Valid and feasible: fixed by minting a small new `AD_HOC`
  closeout-note record in that case (`rerun_of` the primary,
  `status: landed` immediately), with the CHAIN-NOTE written fresh into its
  own `# Result` — durable and greppable without touching the merged
  primary record's body.
- **P2 (Codex) + 4× Copilot — misleading citation to
  `project/executions/README.md`.** All correct and the same root cause:
  this repo's own copy of that file was a bare naming/minimum-fields stub
  that never documented the immutability rule, even though
  `prompts/taurcode/land.md`, `execute.md`, their Espanso export, and this
  PR's own execution record all cited it as the authority. Valid and
  feasible: added the rule to `project/executions/README.md` (scoped
  precisely — immutable from merge onward, not during in-PR iteration,
  matching the actual precedent in PR #60's own record, which was edited
  across pushes before it merged). Also tightened the `land.md`/`execute.md`
  wording to explicitly scope the rule to the *primary* record (Copilot's
  ambiguity concern) and state the merge-time boundary. The `package.yml`
  comment was addressed by fixing the source prompts and regenerating the
  export rather than hand-editing the generated file, per the reviewer's own
  suggestion.

No comments were skipped.

Regenerated `exports/espanso/taurcode/package.yml` after the source prompt
edits.

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
- `lrh validate` — 0 errors

Publication: pushed directly to the open PR branch
(`fix-land-chain-note-immutability`, commit `dbe732c`).

# Follow-up

Suggest running `/lrh-confirm-fixes https://github.com/xenotaur/Taurcode/pull/64`
before merge to verify the fixes against the current diff and resolve the
review threads.
