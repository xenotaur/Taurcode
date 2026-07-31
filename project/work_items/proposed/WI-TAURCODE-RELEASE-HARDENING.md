---
resolution: null
blocked_reason: null
blocked: false
id: WI-TAURCODE-RELEASE-HARDENING
title: Harden Taurcode release pipeline for PyPI (setuptools-scm, release-smoke, CI)
type: deliverable
status: proposed
owner: anthony
contributors:
  - anthony
assigned_agents: []
related_focus:
  - FOCUS-BOOTSTRAP
related_roadmap: []
related_workstreams:
  - WS-LRH-BACKPORT-AND-HARDENING
related_design:
  - project/design/proposals/proposed/lrh-backport-and-hardening/00_proposal.md
depends_on: []
blocked_by: []
expected_actions:
  - create_file
  - edit_file
  - modify_ci_pipeline
  - run_tests
  - create_pr
forbidden_actions:
  - force_push
  - delete_branch
  - merge_pr
  - publish_to_production_pypi
  - implement_espanso_backport_content
  - implement_taurcode_show
  - register_pypi_trusted_publisher
  - configure_github_environment
  - tag_or_publish_real_release
acceptance:
  - pyproject.toml uses dynamic = ["version"] via setuptools-scm instead of a static version string, and scripts/version (with no argument) still resolves the correct version through importlib.metadata
  - scripts/version verify <tag> exists and verifies the tag matches vMAJOR.MINOR.PATCH format and repo state, mirroring LRH's scripts/version verify
  - scripts/release-smoke <tag> --strict-isolation exists, builds sdist/wheel in an isolated venv, installs the wheel, and runs real installed-CLI invocations (not source-tree invocations), checking for editable-install/.pth leakage — limited to the generically-useful isolation-check core, not LRH's package-data template-loading checks (Taurcode ships no runtime package-data resources)
  - .github/workflows/release.yml exists, tag-triggered on v*.*.*, running tag-format validation, scripts/version verify, scripts/release-smoke --strict-isolation, then a publish-pypi job using PyPI Trusted Publishing (id-token: write, pypa/gh-action-pypi-publish@release/v1) — the actual Trusted Publisher and GitHub Environment configuration is a separate, human-performed step not included in this item's scope
  - .github/workflows/testpypi-rehearsal.yml exists (workflow_dispatch), running the same build-check-smoke steps and publishing to TestPyPI
  - A TestPyPI rehearsal against a v0.1.0-tagged checkout succeeds end to end (requires the human-performed TestPyPI Trusted Publisher setup first — tracked as a Follow-up, not blocking file changes)
  - scripts/format --check --diff, scripts/lint, scripts/test, and lrh validate pass with 0 new failures
required_evidence:
  - lrh_validate
  - test_output
  - manual_review
artifacts_expected:
  - pyproject.toml
  - scripts/version
  - scripts/release-smoke
  - .github/workflows/release.yml
  - .github/workflows/testpypi-rehearsal.yml
  - constraints-dev.txt
  - README.md
---

# Harden Taurcode release pipeline for PyPI (setuptools-scm, release-smoke, CI)

## Summary

Harden Taurcode's release tooling to the point of an actual PyPI release, porting LRH's own already-proven pipeline (dynamic versioning, an isolated installed-wheel smoke test, tag-triggered CI, PyPI Trusted Publishing) as the concrete template, scoped down to what Taurcode's simpler package surface actually needs.

## Problem / Context

The governing design (`project/design/proposals/proposed/lrh-backport-and-hardening/00_proposal.md`, Decision 6, merged via PR #67) identified this as the third and final track of `WS-LRH-BACKPORT-AND-HARDENING`, and the precondition for eventually moving `prompts/lrh/` into LRH's own repo as a real dependency. `scripts/publish` has unconditionally exited 1 ("Publishing not yet supported until taurcode is more heavily tested / fleshed out") since it was written, with no defined completion criteria until now. Re-verified against the current repo (not the proposal-writing session's numbers, which could have drifted — they hadn't):

- `pyproject.toml` still has a static `version = "0.1.0"` (no `dynamic`/setuptools-scm).
- `scripts/version` (`scripts/version:21-32`) only supports `""` and `tools` — no `verify` subcommand.
- `scripts/smoke` (`scripts/smoke:1-9`) is a plain `unittest discover` against source, not an isolated-install smoke test.
- `.github/workflows/` has `coverage.yml, lint.yml, meta.yml, smoke.yml, tests.yml` — no release path.
- `scripts/publish:10` still unconditionally exits 1.
- No `scripts/build` exists at all (unlike sibling project Prosoc, which has one and has already produced a local `dist/`).
- No git tags exist in this repo yet (`git tag --list` is empty) — this item's rehearsal will be the first.

### Duplication search
- In-repo: No existing implementation found.
- Sibling repos: LRH has the proven pipeline this item ports from. Taurworks and Prosoc share the identical unresolved `scripts/publish` stub; this item doesn't harden them, but is expected to become their template later (a separate, longer-horizon question flagged in the governing proposal's Open Questions, not part of this item's scope).
- External libraries: None identified — composes existing tools (setuptools-scm, `pypa/gh-action-pypi-publish`).
- Recommendation: Proceed.

### Demand search
- Work items: None found beyond this one. `WI-TAURCODE-SHOW-COMMAND`'s own Non-Goals reference this track as separate, future work — not a duplicate request.
- Proposals: Found: the governing proposal itself — this work item is its intended implementation.
- Backlog: No `project/design/backlog.md` exists in this repo.
- Recommendation: No action.

## Scope

- Dynamic versioning via setuptools-scm.
- `scripts/version verify <tag>`.
- A trimmed `scripts/release-smoke` (isolated build/install/invoke/leak-check core only).
- `release.yml` (tag-triggered) and `testpypi-rehearsal.yml` (`workflow_dispatch`) using PyPI Trusted Publishing.
- A TestPyPI rehearsal against a `v0.1.0` tag, once the human-performed Trusted Publisher setup is done. Uploading to **TestPyPI** as part of this rehearsal is explicitly in scope and permitted; `forbidden_actions: publish_to_production_pypi` only prohibits publishing to the real, production PyPI index.

## Required Changes

1. Migrate `pyproject.toml` to `dynamic = ["version"]` with `setuptools-scm`; add `setuptools-scm` to `[build-system] requires`; verify `scripts/version` (no argument) still resolves correctly via `importlib.metadata`.
2. Extend `scripts/version` with a `verify <tag>` subcommand: validate `vMAJOR.MINOR.PATCH` format and check repo/tag state, mirroring LRH's `scripts/version verify`.
3. Add `scripts/release-smoke <tag> --strict-isolation`: build sdist/wheel (add a build step or `scripts/build` if not folded directly into this script), install into an isolated venv, run real CLI invocations against the installed package, check for editable-install/`.pth` leakage. Port only the generically-useful isolation-check core from LRH's `release_smoke.py` — skip its package-data template-loading checks (not applicable; Taurcode ships no runtime package-data resources).
4. Add `.github/workflows/release.yml`: tag-triggered on `v*.*.*`, job graph mirroring LRH's (validate tag format → install → `scripts/version tools` → `scripts/version verify` → `scripts/release-smoke --strict-isolation` → upload dist artifact → `publish-pypi` job with `environment: pypi`, `permissions: id-token: write`, `pypa/gh-action-pypi-publish@release/v1`).
5. Add `.github/workflows/testpypi-rehearsal.yml`: `workflow_dispatch`, same build-check-smoke steps, publishing to TestPyPI (`environment: testpypi`).
6. Update `constraints-dev.txt` if `setuptools-scm` or other new dev-tooling pins are needed.
7. Document the release process in `README.md` (or a new `docs/how-to/` page) — what a maintainer runs, what's automated, what's still manual (Trusted Publisher setup, environment configuration).
8. `WI-TAURCODE-RELEASE-HARDENING` is already listed in `WS-LRH-BACKPORT-AND-HARDENING`'s `work_items:` — done as part of creating this work item, not deferred to implementation.

## Non-Goals

- Does not touch `prompts/lrh/` or Espanso packaging — `WI-LRH-ESPANSO-BACKPORT`, already done.
- Does not implement `taurcode show` — `WI-TAURCODE-SHOW-COMMAND`, already scoped, not yet implemented.
- Does not perform PyPI Trusted Publisher registration or GitHub Environment configuration — human account/repo-admin actions on external services, explicitly out of scope for any agent.
- Does not cut a real `v0.1.0` release to production PyPI — this item builds and rehearses the pipeline through a TestPyPI rehearsal only.
- Does not harden Taurworks, LCATS, or Prosoc directly.
- Does not port LRH's full `release_smoke.py` verbatim, or its package-data template-loading checks.
- Does not decide the fleet-wide skill-extraction ordering (the proposal's Open Decision 7).

## Acceptance Criteria

See frontmatter `acceptance:` above.

## Validation

- `scripts/version tools`
- `scripts/format --check --diff`
- `scripts/lint`
- `scripts/test`
- `scripts/version verify v0.1.0`
- `scripts/release-smoke v0.1.0 --strict-isolation`
- `lrh validate`

## Risk Notes

- The TestPyPI rehearsal acceptance criterion depends on a human completing the Trusted Publisher setup on pypi.org/GitHub first — this item's file changes are independently completable and validatable without that setup, but the rehearsal itself can't run until it's done. Tracked as a Follow-up, not a blocker on landing the code.
- `scripts/release-smoke`'s isolated-venv build/install pattern is the most novel piece for this repo (nothing like it exists in Taurcode today) — budget extra validation time here relative to the other Required Changes items.
- **Tag-collision safety gap:** `release.yml` triggers its production `publish-pypi` job on any push matching `v*.*.*` — the same pattern the TestPyPI rehearsal's tag (`v0.1.0`) must use. Configuring the `pypi` GitHub Environment's required-reviewer gate is explicitly out of this item's scope (see Non-Goals), so if that gate is not configured *before* the `v0.1.0` tag is ever pushed, `release.yml` could attempt an unguarded production-publish the moment PyPI Trusted Publishing is set up — even though the rehearsal only intends to exercise TestPyPI. **The human must configure the `pypi` environment's approval gate before pushing any `v*.*.*`-pattern tag, including for rehearsal purposes** — this ordering constraint is a precondition for safely completing the TestPyPI rehearsal acceptance criterion, not something this item's code changes can enforce on their own.

## Open Questions

- Whether `scripts/build` should be a standalone wrapper (matching Prosoc's convention) or inlined directly into `scripts/release-smoke` — left to the implementor's judgment, not decided here.
