---
execution_id: 2026_07_31_08_31_21_WI_TAURCODE_SHOW_COMMAND_IMPL_REVIEW
prompt_id: PROMPT(AD_HOC:WI_TAURCODE_SHOW_COMMAND_IMPL_REVIEW)[2026-07-31T08:25:02+00:00]
work_item: AD_HOC
status: landed
rerun_of: 2026_07_31_07_45_44_WI_TAURCODE_SHOW_COMMAND
pr: https://github.com/xenotaur/Taurcode/pull/75
commit: 6a30e6d5f98170829b8a44282c53d7e25024668f
created_at: 2026-07-31T08:31:21+00:00
agent: claude_app
instruction_source: https://github.com/xenotaur/Taurcode/pull/75
session_transcript: claude-app:bbea97a2-74d5-4f02-ab32-ab5ff59b2454
---

# Summary

Addressed one open review comment on PR #75 (implementation of
`WI-TAURCODE-SHOW-COMMAND`): the ambiguous-match error message was
misleading for single-directory searches and could show duplicate
directory names.

# Result

- Fixed: `copilot-pull-request-reviewer`'s comment that the ambiguous-match
  error always said "matched more than one canonical corpus," even when
  `--prompts <dir>` was a single directory (where the real ambiguity is two
  prompt files within that directory sharing a keyword), and could repeat
  the same directory name if duplicates existed within one corpus. Tailored
  the message: single-directory searches now list the actual conflicting
  prompt file paths (`prompt.source`), not a repeated directory name;
  multi-corpus searches dedupe the matched-corpus list via
  `dict.fromkeys(...)`. Added
  `test_show_ambiguous_match_within_single_dir_lists_sources_not_corpus` to
  `tests/cli_show_test.py` covering the previously-untested single-directory
  duplicate-keyword case.

Note: this correlates to `rerun_of:` the primary implementation record
(`2026_07_31_07_45_44_WI_TAURCODE_SHOW_COMMAND`), not the older
`2026_07_31_03_33_21_WI_TAURCODE_SHOW_COMMAND_CLOSEOUT` backfill record from
PR #73's chain — both matched the slug search since the primary-record
exclusion glob only excludes `_REVIEW.md`/`_CONFIRM.md`, not `_CLOSEOUT.md`;
picked the correct one by content, not glob alone.

# Validation

- `scripts/version tools` — taurcode 0.1.0, black 26.3.1, ruff 0.15.12 —
  matching `constraints-dev.txt`.
- `scripts/format --check --diff` — initially found 1 file needing
  reformatting after the fix; ran `scripts/format` to apply, then
  re-confirmed clean (29 files unchanged).
- `scripts/lint` — ruff and black checks passed.
- `scripts/test` — 207 tests, OK (1 new).
- Manual check: `taurcode show :dup --prompts <dir-with-two-:dup-files>` now
  prints `Error: keyword ':dup' matched more than one prompt in <dir>:
  <file1>, <file2>` — no more misleading "canonical corpus" wording.
- `lrh validate` — 0 errors, 0 warnings.

Pushed directly to the open PR branch (`xenotaur/feat/wi-taurcode-show-command-impl`,
commit `238526b`).

# Follow-up

- Proceeding to `/lrh-confirm-fixes` per this `/lrh-land` run's chain.
