---
execution_id: 2026_07_31_19_38_08_WI_TAURCODE_RELEASE_HARDENING_IMPL_REVIEW
prompt_id: PROMPT(AD_HOC:WI_TAURCODE_RELEASE_HARDENING_IMPL_REVIEW)[2026-07-31T19:38:02+00:00]
work_item: AD_HOC
status: landed
rerun_of: 
pr: https://github.com/xenotaur/Taurcode/pull/76
commit: 77ff01cb9641a23f4baa0cb67b17a1a464fac119
created_at: 2026-07-31T19:38:08+00:00
agent: claude_app
instruction_source: https://github.com/xenotaur/Taurcode/pull/76
session_transcript: claude-app:bbea97a2-74d5-4f02-ab32-ab5ff59b2454
---

# Summary

`/lrh-review-response` pass on PR #76 (`WI-TAURCODE-RELEASE-HARDENING`
implementation). Codex left no findings; GitHub Copilot's automated review
left 6 inline comments, all substantive, all fixed.

# Result

- **P1 — tag-collision safety** (`release.yml`): README previously
  described the `pypi` environment's required-reviewer gate as "ideal."
  Strengthened to a mandatory precondition, with an explicit note that
  pushing a rehearsal tag also fires the production trigger since both
  workflows match the same `v*.*.*` pattern.
- **P2 — missing verify step** (`testpypi-rehearsal.yml`): added a
  "Verify release tag semantics and repository checks" step
  (`scripts/version verify "$TAG_UNDER_TEST"`) before the smoke-test step,
  matching `release.yml`'s gate so a rehearsal build cannot skip
  lint/format/test.
- **P2 — tag-ordering doc bug** (`README.md`): the documented commands
  referenced a tag that did not yet exist. Reworded to `git tag
  vMAJOR.MINOR.PATCH` first, then run `scripts/version verify` /
  `scripts/release-smoke` against it, before pushing.
- **Wheel-glob bug under `set -e`** (`scripts/release-smoke`): `ls
  dist/*.whl | head -n1` exited the script early via `set -e`/`pipefail`
  on a zero-match glob (the friendly "no wheel found" message never ran),
  and silently picked an arbitrary wheel on multiple matches. Replaced
  with a `nullglob` array, explicit zero-match and multi-match error
  checks.
- **Shallow-checkout bug** (both workflows): `actions/checkout`'s default
  shallow fetch can omit the tags `setuptools-scm` needs to resolve the
  real version, risking a fallback-version build or a spurious
  version-mismatch smoke failure. Added `fetch-depth: 0` to both
  checkout steps.

No comments were dismissed as out of scope; all 6 were genuine defects or
gaps, not style preferences.

# Validation

- `scripts/format --check --diff` — 29 files unchanged.
- `scripts/lint` — ruff and black checks passed.
- `scripts/release-smoke --strict-isolation` (no tag) — full pipeline
  passed after the wheel-glob fix.
- `scripts/test` — 207 tests, OK.
- `lrh validate` — 0 errors, 0 warnings.

# Follow-up

- Run `/lrh-confirm-fixes` on PR #76 next.
