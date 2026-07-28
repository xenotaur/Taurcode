---
execution_id: 2026_07_27_18_15_21_LRH_BACKPORT_AND_HARDENING_REVIEW
prompt_id: PROMPT(AD_HOC:LRH_BACKPORT_AND_HARDENING_REVIEW)[2026-07-26T16:53:42-04:00]
work_item: AD_HOC
status: landed
rerun_of:
pr: https://github.com/xenotaur/Taurcode/pull/67
commit: d05b9b5e68f8d751dd7a23e58c25a8a09d269b05
created_at: 2026-07-27T18:15:21-04:00
agent: claude_app
instruction_source: https://github.com/xenotaur/Taurcode/pull/67
session_transcript: claude-app:bbea97a2-74d5-4f02-ab32-ab5ff59b2454
---

# Summary

Addressed open review comments on PR #67 (design proposal
`lrh-backport-and-hardening`): two inaccurate file:line citations, a design
gap in the `--prompts all` discovery rule, and a missing README index entry.

# Result

- Fixed: `copilot-pull-request-reviewer`'s citation-accuracy comment
  (appeared twice). `espanso_export.py:56` corrected to `espanso_export.py:60`
  (where `package_name = output.name` actually is); `prompt_loader.py:52-53`
  corrected to `prompt_loader.py:57-61` (the actual `load_prompts()` function
  and its directory walk — the old citation pointed into
  `_normalize_targets` instead).
- Fixed: `chatgpt-codex-connector`'s `--prompts all` design-gap comment (P2).
  Decision 5 now states that `all` must resolve against an explicit,
  maintained list of canonical corpus directories rather than a naive glob
  of `prompts/*/`, since that would sweep in `prompts/examples/` and
  `prompts/imported/` (`IMPORT_STAGING_DIR`, `cli.py:18`) after any import —
  grounded in `AGENTS.md:47`'s "avoid hidden magic in repo discovery".
- Fixed: `chatgpt-codex-connector`'s missing-index comment (P2). Added the
  proposal to `project/design/proposals/README.md`'s "Current Proposals >
  Proposed" list, per that README's own "Adding a Proposal" step 4.

All three comments passed the presence/validity/feasibility triage; none
were skipped.

# Validation

- `scripts/version tools` — taurcode 0.1.0, Python 3.11.8, black 26.3.1,
  ruff 0.15.12, coverage 7.13.5 (all match `constraints-dev.txt`).
- `scripts/format --check --diff` — 28 files unchanged.
- `scripts/lint` — ruff and black checks passed.
- `scripts/test` — 199 tests, OK.
- `lrh validate` — 0 errors, 0 warnings.

Pushed directly to the open PR branch (`xenotaur/feat/lrh-backport-and-hardening`,
commit `61f1f18`).

# Follow-up

- `session_transcript` is `pending` — update to `claude-app:<session-id>`
  after this session ends.
- Run `/lrh-confirm-fixes` on PR #67 before merge to verify these fixes
  against the current diff and resolve the review threads.
