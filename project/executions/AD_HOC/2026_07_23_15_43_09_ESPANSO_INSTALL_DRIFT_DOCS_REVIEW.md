---
execution_id: 2026_07_23_15_43_09_ESPANSO_INSTALL_DRIFT_DOCS_REVIEW
prompt_id: PROMPT(AD_HOC:ESPANSO_INSTALL_DRIFT_DOCS_REVIEW)[2026-07-23T15:14:06-04:00]
work_item: AD_HOC
status: in_progress
rerun_of: 2026_07_23_15_10_23_ESPANSO_INSTALL_DRIFT_DOCS
pr: https://github.com/xenotaur/Taurcode/pull/50
commit: abbe458
created_at: 2026-07-23T15:43:09-04:00
agent: claude_app
instruction_source: https://github.com/xenotaur/Taurcode/pull/50
session_transcript: pending
---

# Summary

Address open review comments on PR #50 (the install-drift docs update)
via the `lrh request review_response` protocol, and push the fixes to
the existing open PR branch.

# Result

Two comments from `chatgpt-codex-connector` and
`copilot-pull-request-reviewer` were triaged; both present, valid, and
feasible, verified against the actual repo before being treated as
confirmed:

- **CLI staleness for exporter changes** — confirmed `AGENTS.md:64`
  ("Run `scripts/develop` before claiming installability or CLI
  operability") is exactly the guardrail the comment cited, and
  `scripts/develop` performs an editable (`pip install -e`) install.
  Added a note that exporter-behavior changes require the `taurcode` CLI
  on `PATH` to actually reflect the current checkout, pointing to
  `scripts/develop` or invoking via `python -m taurcode.cli` directly;
  updated the example command itself to use `python -m taurcode.cli`.
- **Hardcoded `taurcode` vs. generic `<name>` placeholder** — confirmed
  the inconsistency in my own prior text. Clarified `<name>` means
  "whatever directory name you installed under," and that Taurcode's own
  exported package is always literally named `taurcode` (manifest name
  matches output directory name) before using that literal name in the
  command.

No comments skipped.

# Validation

```
$ git rev-parse HEAD
abbe458
$ scripts/version tools
taurcode 0.1.0 / Python 3.11.8 / black 25.11.0 / ruff 0.15.12
$ scripts/format --check --diff
All done — 26 files unchanged
$ scripts/lint
ruff: all checks passed; black: clean
$ scripts/test
Ran 171 tests in 1.078s — OK (docs-only change, no code touched)
$ lrh validate
19 pre-existing errors, 0 new
```

# Follow-up

- `session_transcript` above is `pending` — update to
  `claude-app:<session-id>` after this session ends.
- Suggest running `/lrh-confirm-fixes https://github.com/xenotaur/Taurcode/pull/50`
  before merge to independently verify these fixes and resolve the review
  threads.
