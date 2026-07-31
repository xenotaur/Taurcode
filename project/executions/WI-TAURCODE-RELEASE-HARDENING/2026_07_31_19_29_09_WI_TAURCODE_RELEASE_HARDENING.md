---
execution_id: 2026_07_31_19_29_09_WI_TAURCODE_RELEASE_HARDENING
prompt_id: PROMPT(WI-TAURCODE-RELEASE-HARDENING:WI_TAURCODE_RELEASE_HARDENING)[2026-07-31T18:54:14+00:00]
work_item: WI-TAURCODE-RELEASE-HARDENING
status: in_progress
rerun_of: 
pr: https://github.com/xenotaur/Taurcode/pull/76
commit: 
created_at: 2026-07-31T19:29:09+00:00
agent: claude_app
instruction_source: project/work_items/proposed/WI-TAURCODE-RELEASE-HARDENING.md
session_transcript: claude-app:bbea97a2-74d5-4f02-ab32-ab5ff59b2454
---

# Summary

Implemented `WI-TAURCODE-RELEASE-HARDENING`: dynamic setuptools-scm
versioning, `scripts/version verify`, an isolated-venv installed-wheel
`scripts/release-smoke`, and tag/dispatch-triggered PyPI/TestPyPI publish
workflows using Trusted Publishing.

# Result

- `pyproject.toml`: `dynamic = ["version"]` with `[tool.setuptools_scm]
  fallback_version = "0.0.0"`; added `build` to the `dev` extra.
- `scripts/version`: added a `verify <tag>` subcommand — validates
  `vMAJOR.MINOR.PATCH` tag format, requires a clean working tree, then runs
  `scripts/lint`, `scripts/format --check`, and `scripts/test`.
- `scripts/build` (new): thin `python -m build` wrapper, clears `dist/`
  first.
- `scripts/release-smoke` (new): `[<tag>] [--strict-isolation]` — builds
  via `scripts/build`, creates a temp venv, checks `taurcode` is not
  importable pre-install (hard error under `--strict-isolation`, warning
  otherwise), installs the built wheel with `--force-reinstall`, confirms
  the `taurcode` console script exists, runs `taurcode --help` and a real
  functional call (`taurcode show :implement --prompts prompts/taurcode`)
  against the *installed* CLI, checks for stray `.pth` files pointing back
  at this checkout's `src/` (editable-install leakage), and — when a tag is
  given — asserts the installed version matches the tag with the `v`
  prefix stripped. Trimmed from LRH's `release_smoke.py` to the
  generically-useful isolation-check core; skipped LRH's package-data
  template-loading checks (Taurcode ships no runtime package-data) and
  `twine check`, per the WI's own scope note.
- `.github/workflows/release.yml` (new): tag-triggered on `v*.*.*`; builds,
  verifies, and smoke-tests the tagged checkout, then publishes to PyPI via
  the `pypi` GitHub Environment using `pypa/gh-action-pypi-publish@release/v1`
  with OIDC Trusted Publishing (`id-token: write`, no stored secrets).
- `.github/workflows/testpypi-rehearsal.yml` (new): `workflow_dispatch`,
  requires a tag ref, same build/verify/smoke steps, publishes to TestPyPI
  via the `testpypi` GitHub Environment.
- `constraints-dev.txt`: pinned `build==1.5.0` (matching what
  `scripts/develop` resolves); `setuptools-scm` left unpinned, matching
  LRH's own constraints file, since it's a build-system requirement
  resolved in an isolated PEP 517 build env, not the dev venv.
- `README.md`: new "Release process" section documenting the tag format,
  `scripts/version verify`/`scripts/release-smoke` usage, both workflows,
  and the human-performed Trusted Publisher/GitHub Environment setup
  precondition.
- Did not touch `register_pypi_trusted_publisher`,
  `configure_github_environment`, or `tag_or_publish_real_release` — all
  three remain `forbidden_actions` per the work item, left entirely to a
  human.

No deviations from the work item's Required Changes.

# Validation

- `scripts/develop` — reinstalled with `build==1.5.0` pinned, no drift.
- `scripts/version tools` — taurcode (dev-resolved via setuptools-scm),
  Python 3.11.8, black 26.3.1, ruff 0.15.12, coverage 7.13.5 — matching
  `constraints-dev.txt`.
- `scripts/version verify v0.1.0` — negative-path checks: correctly failed
  on dirty working tree; `scripts/version verify not-a-tag` correctly
  failed on tag-format regex, exit 1.
- `scripts/build` — produced a matching sdist/wheel pair in `dist/`.
- `scripts/release-smoke --strict-isolation` (no tag) — full pipeline
  passed: pre-install visibility check, install, console-script check,
  `--help`, functional `taurcode show` call, `.pth` leakage check.
- `scripts/release-smoke v0.0.1` — negative-path check: correctly failed
  with a version mismatch against the untagged dev checkout (expected,
  since no real tag exists yet).
- `scripts/format --check --diff` — 29 files unchanged.
- `scripts/lint` — ruff and black checks passed.
- `scripts/test` — 207 tests, OK.
- `lrh validate` — 0 errors, 0 warnings.

# Follow-up

- `session_transcript` will be confirmed/updated after this session ends.
- Run `/lrh-review-response` on PR #76 (repeat as needed), then
  `/lrh-confirm-fixes` before merge.
- After merge: a human must register the PyPI and TestPyPI Trusted
  Publishers and configure the `pypi`/`testpypi` GitHub Environments
  (ideally with a required-reviewer approval gate) before either workflow
  is used for a real publish or TestPyPI rehearsal — tracked as a
  follow-up, not blocking this PR.
