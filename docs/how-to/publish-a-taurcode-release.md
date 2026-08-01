# Publish a Taurcode Release

Human-only runbook for the two remaining exit criteria on
`WS-LRH-BACKPORT-AND-HARDENING` (search `project/workstreams/` for that ID —
not linked directly here, since Phase B step 8 moves the file from
`proposed/` to `resolved/` and a path-based link would go stale): a
successful TestPyPI rehearsal, and a real tagged PyPI release. Every step
here is a `forbidden_actions` entry on
[`WI-TAURCODE-RELEASE-HARDENING`](../../project/work_items/resolved/WI-TAURCODE-RELEASE-HARDENING.md)
(`register_pypi_trusted_publisher`, `configure_github_environment`,
`tag_or_publish_real_release`), so none of it was — or should be —
performed by an agent. Do this by hand, once for Phase A, then per release
for Phase B.

For the mechanics of the tooling this guide drives (`scripts/version
verify`, `scripts/release-smoke`, what each workflow does), see the
[Release process section of the README](../../README.md#release-process).
This guide is the setup and sequencing checklist, not the tooling
reference.

## Phase A — One-time PyPI setup

Do this before pushing any `vMAJOR.MINOR.PATCH` tag, including a rehearsal
tag — pushing any such tag fires `release.yml`'s production-publish
trigger too, since both workflows match the same pattern. The `pypi`
environment's approval gate is the only thing standing between a rehearsal
push and an unintended production publish.

1. **Create the `pypi` GitHub Environment.**
   - Repo → Settings → Environments → New environment → name it `pypi`.
   - Add yourself as a required reviewer. This is the mandatory approval
     gate — do not skip it, even "just for the rehearsal."
2. **Create the `testpypi` GitHub Environment.**
   - Same steps, name it `testpypi`. A required reviewer here is
     recommended but not load-bearing the way `pypi`'s is.
3. **Register the PyPI Trusted Publisher** (OIDC — no API tokens stored
   anywhere).
   - If this is the first time `taurcode` is being published (the project
     doesn't exist on PyPI yet), use the **pending publisher** flow on
     [pypi.org](https://pypi.org/manage/account/publishing/) instead of
     the per-project publisher settings — the pending-publisher form is
     the only one available before a project exists:
     - PyPI project name: `taurcode`
     - Owner: `xenotaur`
     - Repository name: `Taurcode`
     - Workflow name: `release.yml`
     - Environment name: `pypi`
   - If `taurcode` already exists on PyPI (a prior release already
     published it), register the Trusted Publisher instead from that
     existing project's own "Publishing" settings page — the fields are
     the same, just reached from a different starting point.
4. **Register the TestPyPI Trusted Publisher.**
   - You'll need a separate [test.pypi.org](https://test.pypi.org)
     account if you don't already have one — it is not the same login as
     pypi.org.
   - Same pending-publisher-vs-existing-project distinction as step 3,
     on TestPyPI:
     - PyPI project name: `taurcode`
     - Owner: `xenotaur`
     - Repository name: `Taurcode`
     - Workflow name: `testpypi-rehearsal.yml`
     - Environment name: `testpypi`

Once both environments and both trusted publishers exist, Phase A is done
and does not need to be repeated for future releases.

## Phase B — Rehearsal, real release, workstream closeout

> `v0.1.0` below is a placeholder for the intended next release version —
> replace every occurrence with the actual `vMAJOR.MINOR.PATCH` you're
> releasing before copy/pasting these commands.

5. **Create and push a rehearsal tag.**
   ```bash
   git checkout main && git pull
   git tag v0.1.0
   scripts/version verify v0.1.0
   scripts/release-smoke v0.1.0 --strict-isolation
   git push origin v0.1.0
   ```
   The tag must exist locally *before* running `scripts/version verify`/
   `scripts/release-smoke` against it — `setuptools-scm` resolves an
   untagged development version otherwise, and the smoke test will fail
   its version-match check.
   Pushing the tag will also queue `release.yml` — do **not** approve its
   `pypi` environment gate yet. Leave it pending while you run the
   rehearsal below; you'll either approve it in step 7 (promoting this
   same tag to a real release) or explicitly reject/cancel it if you
   decide to rehearse under a throwaway tag instead.

6. **Run the TestPyPI rehearsal.**
   ```bash
   gh workflow run testpypi-rehearsal.yml --ref v0.1.0
   ```
   Or via the GitHub UI: Actions → "TestPyPI rehearsal publish" → Run
   workflow → select the `v0.1.0` tag.
   - Approve the `testpypi` environment gate if one is configured.
   - Confirm the run's `build-check-smoke` and `publish-testpypi` jobs
     both succeed.
   - Verify the published package:
     ```bash
     python -m venv /tmp/taurcode-testpypi-check
     /tmp/taurcode-testpypi-check/bin/pip install \
       -i https://test.pypi.org/simple/ \
       --extra-index-url https://pypi.org/simple/ \
       taurcode==0.1.0
     /tmp/taurcode-testpypi-check/bin/taurcode --help
     ```
     (`--extra-index-url` is needed because `taurcode`'s dependencies
     aren't published on TestPyPI.)

7. **Promote to a real release.**
   - If the rehearsal succeeded against the `v0.1.0` tag pushed in step
     5, go to the already-queued `release.yml` run for that tag (Actions
     tab) and approve the `pypi` environment gate.
   - If you rehearsed under a different tag, push `v0.1.0` now instead —
     `release.yml` fires automatically on any `v*.*.*` push — then
     approve the `pypi` gate when prompted.
   - Confirm the `publish-pypi` job succeeds, then verify:
     ```bash
     python -m venv /tmp/taurcode-pypi-check
     /tmp/taurcode-pypi-check/bin/pip install taurcode==0.1.0
     /tmp/taurcode-pypi-check/bin/taurcode --help
     ```

8. **Close out the workstream.**
   - Both `WS-LRH-BACKPORT-AND-HARDENING` exit criteria involving PyPI are
     now satisfied. Run `/lrh-closeout` (or move the workstream file to
     `project/workstreams/resolved/` by hand), citing the rehearsal run
     URL and the release run URL as evidence.
   - `lrh validate` should report 0 errors after the move.

## If something goes wrong

- **Wrong version published / bad tag:** PyPI and TestPyPI do not allow
  re-uploading a given version, even after deletion. Bump to the next
  patch version and start Phase B over — do not try to reuse a tag that
  already reached `publish-pypi` or `publish-testpypi`.
- **Rehearsal tag accidentally triggers a production publish:** this is
  exactly what the `pypi` environment's required-reviewer gate in Phase A
  step 1 exists to prevent — reject the pending deployment in the
  Actions run's Environments panel instead of approving it.
