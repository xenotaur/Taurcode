---
execution_id: 2026_07_23_18_36_51_WI_ESPANSO_INSTALL_COMMAND_REVIEW
prompt_id: PROMPT(AD_HOC:WI_ESPANSO_INSTALL_COMMAND_REVIEW)[2026-07-23T18:23:01-04:00]
work_item: AD_HOC
status: landed
rerun_of: 2026-07-23-install-espanso-work-item
pr: https://github.com/xenotaur/Taurcode/pull/52
commit: 768e605895fbe815ac99f7547ebf84cf145e2800
created_at: 2026-07-23T18:36:51-04:00
agent: claude_app
instruction_source: https://github.com/xenotaur/Taurcode/pull/52
session_transcript: claude-app:1db010f2-96d0-4343-b909-d503a88b3fca
---

# Summary

Addressed four reviewer comments on PR #52. All four targeted the plan in
`WI-ESPANSO-INSTALL-COMMAND` rather than code — the PR contains no Python —
and three identified defects that would have become real bugs at
implementation time. All four were fixed in the work item.

# Result

Fixed, in order of severity:

1. **P1 — `~` not expanded (codex).** The work item prescribed
   `MACOS_PACKAGES_DIR = "~/Library/Application Support/espanso/match/packages"`
   with no `expanduser()`. `Path` does not expand `~`, so an implementer
   following the plan literally would have created a relative
   `<cwd>/~/Library/Application Support/...` tree, reported a successful
   install, and left the real Espanso package untouched. Required Change 1 now
   mandates `expanduser()` on both the default and the `--packages-dir`
   override, with an acceptance criterion and a test.
2. **P2 — `--name` versus curated metadata (codex).** The work item claimed
   the manifest name "tracks `<name>` automatically" via
   `package_name = output.name`. That is true only when no curated
   `_manifest.yml` exists — and `prompts/taurcode/espanso/_manifest.yml` does
   exist, pinned to `name: taurcode`, and is copied verbatim by
   `export_espanso_metadata_assets`. Any non-default `--name` therefore failed
   `lint_espanso_package_build` with `manifest-name-mismatch`, making two of
   the item's own acceptance criteria unachievable. Per user decision, `--name`
   is removed entirely and the installed directory name is now *derived from*
   the curated manifest (defaulting to `taurcode`), so the mismatch is
   impossible by construction rather than prevented by documentation. Recorded
   as a Non-Goal that install must never rewrite curated metadata.
3. **P2 — unsafe write into the live package (codex).** `export_espanso`
   writes `package.yml` and all metadata assets *before* running its build
   lint and raising. Exporting straight into the live package directory would
   therefore corrupt an installed package on any lint or I/O failure — the
   exact class of silent breakage this work item exists to prevent. Required
   Change 1 now stages the export in a temp directory and replaces the live
   package only after export and lint both succeed.
4. **Wording (copilot).** "match-packages" → `match/packages`, matching the
   path terminology used everywhere else in the repo.

Additionally recorded one interaction the reviewers did not flag: the staging
directory's own basename must equal the resolved package name (stage at
`<tmp>/<name>/`, not `<tmp>/`), because `lint_espanso_package_build` derives
the expected manifest name from `output.name`. A conventionally-named staging
directory would fail with both `manifest-name-mismatch` and
`invalid-package-name`, so fixing comment 3 naively would have reintroduced
comment 2's failure on the staging path.

Nothing was skipped. All four comments passed the presence, validity, and
feasibility checks.

# Validation

Reproduction evidence for comments 2 and 3, both from a single command
(`python -m taurcode.cli export espanso --prompts prompts/taurcode --output
<tmp>/foo`):

```text
Error: .../foo/_manifest.yml: [manifest-name-mismatch] Manifest name 'taurcode'
does not match package directory name 'foo'.
EXIT=1
files left behind despite failure: LICENSE README.md _manifest.yml package.yml
```

Comment 1 evidence: `Path('~/Library/...')` reports `is_absolute: False`.

Canonical validation on commit `1180227`:

- `scripts/version tools` — **initially failed the version gate**: installed
  Black was 25.11.0 against `constraints-dev.txt`'s pinned 26.3.1. At that
  version `scripts/format --check --diff` reported
  `tests/espanso_import_test.py` as needing reformatting — a false positive
  from stale tooling, and notably the same file PR #51 had just fixed
  formatting on. Ran `scripts/develop` to sync (Black 25.11.0 → 26.3.1) and
  re-ran. No source file was changed in response to the stale result.
- `scripts/format --check --diff` — passed, 26 files unchanged.
- `scripts/lint` — passed (ruff + black check).
- `scripts/test` — passed, 171 tests, OK.
- `lrh validate` — 19 errors, identical to the count on clean `main`; 0 new.
  All are the known project-plane issues tracked by
  `WI-PROJECT-PLANE-VALIDATION-CLEANUP`.

# Follow-up

- Run `/lrh-confirm-fixes https://github.com/xenotaur/Taurcode/pull/52` before
  merge to verify these fixes against the current diff and resolve the review
  threads.
- Update `session_transcript: pending` to `claude-app:<session-id>` after the
  session ends.
- The toolchain drift caught here recurs across sessions. `scripts/develop`
  should be run at the start of any Taurcode session that will run
  `scripts/format` or `scripts/lint`, not after a failure.
