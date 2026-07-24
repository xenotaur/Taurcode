---
execution_id: 2026_07_24_00_45_06_WI_ESPANSO_INSTALL_COMMAND
prompt_id: PROMPT(WI-ESPANSO-INSTALL-COMMAND:WI_ESPANSO_INSTALL_COMMAND)[2026-07-24T00:19:57-04:00]
work_item: WI-ESPANSO-INSTALL-COMMAND
status: in_progress
rerun_of:
pr: https://github.com/xenotaur/Taurcode/pull/53
commit: baca91278fb07bc124ab90a565d614c08e54e13c
created_at: 2026-07-24T00:45:06-04:00
agent: claude_app
instruction_source: project/work_items/proposed/WI-ESPANSO-INSTALL-COMMAND.md
session_transcript: claude-app:1db010f2-96d0-4343-b909-d503a88b3fca
---

# Summary

Implemented the macOS-only `taurcode install espanso` subcommand per the
reviewed work item. This is the implementation half of the work item whose
planning artifact was created and merged in PR #52; opened as PR #53.

# Result

New module `src/taurcode/espanso_install.py` with four functions plus an
`InstallError(ValueError)` (caught by `cli.main`'s existing handler):

- `resolve_packages_dir(platform, override)` — macOS-only gate; `expanduser()`
  on both default and override so a literal `~` never yields a relative path.
- `resolve_package_name(source_dir)` — derives the installed directory name
  from the curated `_manifest.yml` `name:` (default `taurcode`), so the
  directory name and manifest name always agree.
- `install_espanso(prompts, packages_dir, source_dir)` — stages the export at
  `<tmp>/<name>/` inside the packages dir and `os.replace`-swaps into place
  only after `export_espanso` (which runs the build lint) succeeds. A failed
  export leaves any existing package byte-identical and no staging directory
  behind.
- `restart_espanso(runner, which)` — opt-in via `--restart`; missing binary or
  nonzero exit is a clear `InstallError`, and `runner`/`which` are injectable
  so tests never shell out.

`cli.py` wires `install espanso` with `--prompts`, `--packages-dir`, and
`--restart` (no `--name`). Docs and focus updated: `README.md` and
`docs/reference/espanso-integration.md` lead with the command and keep the
manual steps as a fallback; `project/focus/current_focus.md` narrows the
new-CLI Non-Goal to require a work item and tests (its Priority 5 anticipated
this). All three review defects from PR #52 (`~` expansion, `--name`/manifest
conflict, unsafe write to the live package) are addressed in the code as
specified, plus the staging-basename interaction the reviewers did not flag.

Prior-art check: present in the work item's Problem/Context (no in-repo or
sibling implementation; Espanso's own `package install --git` and
`espanso path packages` assessed and not adopted as dependencies). No demand
match to close beyond the design/roadmap notes already recorded.

# Validation

Toolchain synced this session (Black 26.3.1 per `constraints-dev.txt`), so the
version gate was clean before format/lint.

- `scripts/format --check --diff` — the two new files needed formatting; ran
  `scripts/format`, then clean (28 files unchanged).
- `scripts/lint` — passed (ruff + black check).
- `scripts/test` — 186 tests, OK (was 171; +15 in `tests/espanso_install_test.py`
  and 1 in `tests/cli_defaults_test.py`). New coverage: non-darwin platform
  gate; default/override `expanduser()` and no `~` directory created;
  installed manifest name equals installed directory name; default to
  `taurcode` without a curated manifest; failed export (invalid manifest name)
  leaves an existing package byte-identical with no staging leftover; restart
  invoked only with the flag via injected runner/`which`; missing-binary and
  nonzero-exit error paths; CLI non-darwin exits nonzero without writing; CLI
  install prints the manual restart hint.
- `lrh validate` — 19 errors, identical to clean `main`; 0 new. All are the
  known project-plane issues tracked by `WI-PROJECT-PLANE-VALIDATION-CLEANUP`.
- Manual: `python -m taurcode.cli install espanso --prompts prompts/taurcode
  --packages-dir <tmp>` installs into `<tmp>/taurcode/` with `name: taurcode`
  matching the directory, all four package files present, and no
  `.taurcode-install-*` staging directory left behind. `diff -r` against a
  plain `export espanso` of the same corpus is empty — install output is
  byte-identical to export.

# Follow-up

- `/lrh-review-response https://github.com/xenotaur/Taurcode/pull/53` for any
  reviewer comments, then `/lrh-confirm-fixes`, merge, and `/lrh-closeout`.
  This closeout WILL resolve WI-ESPANSO-INSTALL-COMMAND (unlike PR #52's, which
  only landed execution records) because this PR actually implements it.
- After merge, reinstall the local Espanso package so the dev machine reflects
  the change — now a one-liner: `taurcode install espanso --restart`.
