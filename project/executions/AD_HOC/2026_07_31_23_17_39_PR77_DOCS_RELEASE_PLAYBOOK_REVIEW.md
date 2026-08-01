---
execution_id: 2026_07_31_23_17_39_PR77_DOCS_RELEASE_PLAYBOOK_REVIEW
prompt_id: PROMPT(AD_HOC:PR77_DOCS_RELEASE_PLAYBOOK_REVIEW)[2026-07-31T23:04:31+00:00]
work_item: AD_HOC
status: landed
rerun_of: 
pr: https://github.com/xenotaur/Taurcode/pull/77
commit: 9184450f43a9af52e69cb1e37283b81621723742
created_at: 2026-07-31T23:17:39+00:00
agent: claude_app
instruction_source: https://github.com/xenotaur/Taurcode/pull/77
session_transcript: claude-app:bbea97a2-74d5-4f02-ab32-ab5ff59b2454
---

# Summary

`/lrh-land`-driven review-response pass on PR #77 (docs-only: new PyPI
release playbook). One Codex finding, fixed.

# Result

- **P2 — tag-ordering bug** (`docs/how-to/publish-a-taurcode-release.md`,
  step 5): the documented rehearsal-tag code block ran `scripts/version
  verify v0.1.0` and `scripts/release-smoke v0.1.0 --strict-isolation`
  before `git tag v0.1.0` created the tag. Since `setuptools-scm` resolves
  an untagged development version until the tag exists, following the
  guide as written would fail the smoke test's version-match check on the
  very first release attempt. This is the same class of bug fixed in the
  README during PR #76's review — reintroduced here in the new playbook
  file. Reordered: `git tag v0.1.0` now runs before the verify/smoke
  commands, with an explanatory note added directly below the code block.
- Pushed directly to the PR branch (commit `9184450`).

# Validation

- `scripts/version tools` — toolchain matches `constraints-dev.txt`.
- `scripts/format --check --diff` — 29 files unchanged.
- `scripts/lint` — ruff and black checks passed.
- `scripts/test` — 207 tests, OK.
- `lrh validate` — 0 errors, 0 warnings.

# Follow-up

- Re-check REVIEW-LANDED against the new HEAD before confirm-fixes.
