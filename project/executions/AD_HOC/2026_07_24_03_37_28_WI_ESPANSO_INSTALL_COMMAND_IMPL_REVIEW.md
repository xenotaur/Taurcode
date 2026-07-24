---
execution_id: 2026_07_24_03_37_28_WI_ESPANSO_INSTALL_COMMAND_IMPL_REVIEW
prompt_id: PROMPT(AD_HOC:WI_ESPANSO_INSTALL_COMMAND_IMPL_REVIEW)[2026-07-24T03:32:24-04:00]
work_item: AD_HOC
status: in_progress
rerun_of: 2026_07_24_00_45_06_WI_ESPANSO_INSTALL_COMMAND
pr: https://github.com/xenotaur/Taurcode/pull/53
commit: cc76836062d722f5195ea92121452de69fde0a3e
created_at: 2026-07-24T03:37:28-04:00
agent: claude_app
instruction_source: https://github.com/xenotaur/Taurcode/pull/53
session_transcript: claude-app:1db010f2-96d0-4343-b909-d503a88b3fca
---

# Summary

Addressed six reviewer comments on PR #53 (the `install espanso`
implementation). All six were valid; two were genuine correctness/security
bugs in code this session wrote. Nothing was skipped.

# Result

Fixed, most severe first:

1. **P1 path traversal (codex).** `resolve_package_name` returned the curated
   `_manifest.yml` `name:` verbatim, and `install_espanso` joined it straight
   into a path. A name like `../victim` or an absolute path escaped
   `staging_parent`; because `export_espanso` writes files before its lint, a
   later-failing install could clobber `packages_dir/victim/` or write outside
   the packages directory, and cleanup would not restore it. Added a
   `_PACKAGE_NAME_RE = ^[a-z0-9-]+$` check (mirroring the lint rule Espanso
   package names already satisfy) applied to the derived name *before* it is
   used in any path; a non-matching name raises `InstallError` early.
2. **Rollback gap (copilot).** If the `staged -> target` `os.replace` failed
   after the live package had been moved to the backup inside `staging_parent`,
   the `finally` clause would delete `staging_parent` — and the backup with it —
   leaving no install at all, violating the byte-identical guarantee. Added a
   rollback: on a swap `OSError`, restore the backup to `target` before
   re-raising.
3. **Relative `--packages-dir` (copilot).** A relative override installed into
   `<cwd>/...` rather than the real Espanso config location. `resolve_packages_dir`
   now rejects a non-absolute resolved path with `InstallError`.
4. **`restart_espanso` (copilot).** It checked `which("espanso")` but then
   invoked the bare `"espanso"`, so a `FileNotFoundError` (PATH race) would
   surface as an `OSError`. Now invokes the `which`-resolved path and wraps
   `FileNotFoundError` into `InstallError`.
5. **Test nit (copilot).** Dropped the environment-dependent
   `Path("~").exists()` assertion; `assertNotIn("~", resolved.parts)` already
   verifies the `expanduser()` behavior without depending on filesystem state.
6. **Atomic wording (codex P2).** The two-`os.replace` swap has a window where
   the target is briefly absent, so it is crash-safe but not concurrency-atomic.
   The README no longer calls it atomic; it is "staged and swapped into place
   only after the export and its build lint succeed." (The work item's Risk
   Notes already acknowledged the non-atomicity; only the README overclaimed.)

Test coverage restructured around the new name guard: the invalid-name case
(`Bad Name`, `../victim`, `/abs`) now asserts early `InstallError` with no path
escape and nothing written; the export-failure and swap-failure-rollback paths
are covered separately via injected failures (`export_espanso` patched to
raise; `os.replace` patched to fail on the second call and the original
restore asserted). Added a relative-override rejection test and a
`FileNotFoundError`-wrapping test.

# Validation

- `scripts/version tools` — **failed the gate again**: Black had drifted back
  to 25.11.0 against the pinned 26.3.1 (the recurring Taurcode toolchain drift;
  at the wrong version `scripts/format` reported a spurious reformat). Ran
  `scripts/develop` to resync to 26.3.1 and re-ran. No source changed in
  response to the stale result.
- `scripts/format --check` — clean, 28 files unchanged.
- `scripts/lint` — passed (ruff + black check).
- `scripts/test` — 190 tests, OK (was 186; +4 net after restructuring).
- `lrh validate` — 19 errors, identical to clean `main`; 0 new.
- Manual guards verified live: `install espanso --packages-dir reldir` exits
  with "must be an absolute path"; a synthetic `name: ../victim` manifest is
  rejected with `InstallError` and no `victim` directory escapes. Install
  output remains byte-identical to `export espanso` (`diff -r` empty), with no
  staging directory left behind.

# Follow-up

- Run `/lrh-confirm-fixes https://github.com/xenotaur/Taurcode/pull/53` before
  merge to verify these fixes against the current diff and resolve the threads.
- Update `session_transcript` once the session ends (already set to this
  session's ID here, but confirm at closeout).
- The Black 26.3.1 drift recurred mid-session — worth running `scripts/develop`
  at the start of any Taurcode turn that will format or lint.
