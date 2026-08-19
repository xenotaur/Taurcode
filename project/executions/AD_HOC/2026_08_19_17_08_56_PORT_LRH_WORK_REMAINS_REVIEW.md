---
execution_id: 2026_08_19_17_08_56_PORT_LRH_WORK_REMAINS_REVIEW
prompt_id: PROMPT(AD_HOC:PORT_LRH_WORK_REMAINS_REVIEW)[2026-08-14T17:55:31+00:00]
work_item: AD_HOC
status: in_progress
rerun_of: 
pr: https://github.com/xenotaur/Taurcode/pull/80
commit: 031adabff338d31b3e35ad07bbf6617feb4328e9
created_at: 2026-08-19T17:08:56+00:00
agent: claude_app
instruction_source: https://github.com/xenotaur/Taurcode/pull/80
session_transcript: claude-app:00715f1b-2706-4fb2-97ae-b29df73c3417
---

# Summary

Addressed open review comments on PR #80 (port of the landed
`lrh-work-remains` LRH skill into `prompts/lrh/lrh-remains.md`, and the
trim of `prompts/taurcode/remains.md` back to repo-agnostic): a
read-only-guarantee contradiction, a missed Espanso-export regen, a
self-contradictory remote-name instruction, an incomplete-closeouts check
that only looked locally, and a stale README prompt list.

# Result

- Fixed (P1, codex): `lrh-remains.md` told the agent to `pipx install lrh`
  when `lrh` is absent, contradicting the prompt's own "strictly
  read-only" guarantee. Dropped the install instruction; the prompt now
  reports `lrh` as unavailable and falls back to the documented direct
  file-read fallbacks. Also fixed by the same change: Copilot's
  independent framing of the same issue ("scope read-only explicitly to
  the target repository").
- Fixed (P1, codex): the new `:lrh-remains` trigger was missing from the
  checked-in Espanso export. Re-ran `taurcode export espanso --prompts
  prompts/lrh --output exports/espanso/lrh` so the package now carries all
  5 LRH triggers.
- Fixed (P2, codex): category 7 (incomplete closeouts) only grepped the
  local checkout, missing an `in_progress` record that exists only on the
  remote default branch. Added a remote-tree enumeration step
  (`gh api .../git/trees/<default-branch>?recursive=true`) whose result is
  unioned with the local grep before cross-checking each candidate's `pr:`
  field.
- Fixed (P2, codex): the README's "Currently backported" list only named
  4 prompts. Added `:lrh-remains` (`prompts/lrh/lrh-remains.md`). Also
  fixed by the same change: Copilot's independent report of the same gap.
- Fixed (Copilot): category 4's guidance said "don't hard-code the remote
  name `origin`" immediately after using `git symbolic-ref
  refs/remotes/origin/HEAD`, which does exactly that. Reordered to prefer
  `gh repo view` first, and made the `git symbolic-ref` fallback resolve
  the remote name via `git remote` before using it.
- Skipped: none — all 5 distinct comments (7 raw comments, 2 duplicated
  across bots) passed presence/validity/feasibility and were fixed.

# Validation

- `scripts/version tools`: taurcode 0.0.1.dev259+g0815f08c7.d20260731,
  Python 3.11.8, black 25.11.0, ruff 0.15.0
- `scripts/format --check --diff`: 1 pre-existing failure in
  `tests/espanso_import_test.py` (Black version drift, untouched by this
  change — confirmed identical on the pre-fix commit via `git stash`)
- `scripts/lint`: ruff clean; same pre-existing Black drift as above
- `scripts/test`: 207 tests, OK
- `lrh validate`: 4 pre-existing errors in unrelated resolved work items
  (`WORK_ITEM_BLOCKED_REASON_NOT_NULL`), confirmed identical on the
  pre-fix commit via `git stash`
- `taurcode lint prompts --prompts prompts`: same pre-existing
  errors/warnings as before this change, nothing new from the files
  touched here

# Follow-up

- `session_transcript` is populated with the resolved Claude Code host
  session ID; no further update needed.
- Suggest running `/lrh-confirm-fixes` against PR #80 before merge to
  verify these fixes against the current diff and resolve the review
  threads.
