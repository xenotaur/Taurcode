---
execution_id: 2026_07_31_07_45_44_WI_TAURCODE_SHOW_COMMAND
prompt_id: PROMPT(WI-TAURCODE-SHOW-COMMAND:WI_TAURCODE_SHOW_COMMAND)[2026-07-31T04:57:32+00:00]
work_item: WI-TAURCODE-SHOW-COMMAND
status: landed
rerun_of:
pr: https://github.com/xenotaur/Taurcode/pull/75
commit: 6a30e6d5f98170829b8a44282c53d7e25024668f
created_at: 2026-07-31T07:45:44+00:00
agent: claude_app
instruction_source: project/work_items/proposed/WI-TAURCODE-SHOW-COMMAND.md
session_transcript: claude-app:bbea97a2-74d5-4f02-ab32-ab5ff59b2454
---

# Summary

Implemented `WI-TAURCODE-SHOW-COMMAND`: a `taurcode show <keyword> [--prompts
<dir|all>]` CLI command that prints a snippet body to stdout, resolving an
explicit canonical-corpus list (`prompts/taurcode`, `prompts/lrh`) by
default rather than a directory glob.

# Result

- Added `CANONICAL_PROMPT_DIRS = (CANONICAL_PROMPTS_DIR, "prompts/lrh")` in
  `src/taurcode/cli.py`, next to the existing `CANONICAL_PROMPTS_DIR`/
  `IMPORT_STAGING_DIR` constants.
- Added the `show` subparser: positional `keyword`, optional `--prompts`
  (default `None`).
- Implemented lookup logic in `main()`: `--prompts` unset or the literal
  string `"all"` both search every dir in `CANONICAL_PROMPT_DIRS`; an
  explicit `--prompts <dir>` searches only that directory. Matches are
  collected across all searched dirs, keyed on `prompt.keyword`.
- Implemented error handling: zero matches → stderr message naming the
  keyword and every directory searched, exit 1. More than one match (same
  keyword present in more than one canonical corpus) → stderr message
  listing which directories matched, exit 1. Neither case guesses or
  silently picks a match.
- Added `tests/cli_show_test.py` (6 tests): single-corpus lookup, default
  multi-corpus lookup, explicit `--prompts all`, not-found, ambiguous-match,
  and a dedicated check that `--prompts all` is never treated as a literal
  directory path. Used a `_patched_canonical_dirs` context manager to swap
  `cli.CANONICAL_PROMPT_DIRS` to temp-directory fixtures for the
  multi-corpus tests, following the existing `_run_cli`/`tempfile` pattern
  from `tests/roundtrip_cli_test.py`.
- Added one test to `tests/cli_defaults_test.py` confirming `show`'s
  `--prompts` argument defaults to `None`, matching that file's existing
  per-subcommand defaults-testing convention.
- Documented `taurcode show` in `README.md`, in a new "Printing a snippet
  without Espanso" section directly after the `lrh` package section.
- No changes to `prompts/lrh/`, Espanso packaging, or release hardening —
  the WI's Non-Goals and `forbidden_actions` were respected.

No deviations from the work item's Required Changes this time.

# Validation

- `scripts/version tools` — taurcode 0.1.0, Python 3.11.8, black 26.3.1,
  ruff 0.15.12, coverage 7.13.5 — matching `constraints-dev.txt` (no drift
  this run).
- `scripts/format --check --diff` — 29 files unchanged.
- `scripts/lint` — ruff and black checks passed.
- `scripts/test` — 206 tests, OK (7 new: 6 in `cli_show_test.py`, 1 in
  `cli_defaults_test.py`).
- `taurcode show :lrh-implement` — correctly resolved from `prompts/lrh/`
  via the default multi-corpus search.
- `taurcode show :lrh-implement --prompts all` — same result, explicit,
  exit 0.
- `taurcode show :lrh-implement --prompts prompts/lrh` — single-corpus,
  correct body printed.
- `taurcode show :does-not-exist` — `Error: no prompt found with keyword
  ':does-not-exist' in prompts/taurcode, prompts/lrh`, exit 1.
- `lrh validate` — 0 errors, 0 warnings.

# Follow-up

- `session_transcript` is `pending` — update to `claude-app:<session-id>`
  after this session ends.
- Run `/lrh-review-response` on PR #75 (repeat as needed), then
  `/lrh-confirm-fixes` before merge.
