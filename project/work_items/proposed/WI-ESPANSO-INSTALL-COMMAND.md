---
resolution: null
blocked_reason: null
blocked: false
id: WI-ESPANSO-INSTALL-COMMAND
title: Implement macOS-only taurcode install espanso subcommand
type: deliverable
status: proposed
owner: anthony
contributors:
  - anthony
assigned_agents: []
related_focus:
  - FOCUS-BOOTSTRAP
related_roadmap: []
related_workstreams: []
related_design:
  - project/design/design.md
  - project/design/proposals/adopted/espanso-match-force-clipboard/00_proposal.md
depends_on: []
blocked_by: []
expected_actions:
  - create_file
  - edit_file
  - add_cli_command
  - run_tests
  - write_docs
  - create_pr
forbidden_actions:
  - force_push
  - delete_branch
  - merge_pr
  - implement_linux_windows_paths
  - implement_continuous_sync
  - write_to_real_espanso_dir_in_tests
acceptance:
  - taurcode install espanso writes package.yml and metadata assets into <packages-dir>/<name>/ via espanso_export.export_espanso, with the generated manifest name matching the directory name
  - On non-darwin platforms the command prints a clear unsupported-platform message and exits nonzero without writing files or guessing a path
  - --restart is opt-in; without it the command prints the espanso restart instruction, and with it a missing espanso binary is a clear error and nonzero exit rather than a traceback
  - Every automated test resolves its install target through an injected or parameterized directory; no test writes under the real Espanso application-support path
  - FOCUS-BOOTSTRAP Non-Goal narrowed to permit CLI commands that have a dedicated work item and tests
  - docs/reference/espanso-integration.md points at the new command as the preferred sync path, keeping manual steps as fallback
  - scripts/format --check --diff, scripts/lint, scripts/test, and lrh validate pass with 0 new failures
required_evidence:
  - lrh_validate
  - test_output
  - manual_review
artifacts_expected:
  - src/taurcode/espanso_install.py
  - src/taurcode/cli.py
  - tests/espanso_install_test.py
  - tests/cli_defaults_test.py
  - docs/reference/espanso-integration.md
  - README.md
  - project/focus/current_focus.md
---

# Implement macOS-only taurcode install espanso subcommand

## Summary

Add a macOS-only `taurcode install espanso` subcommand that exports the
canonical prompt corpus directly into the local Espanso match-packages
directory, with opt-in `--restart`, so a merged exporter or prompt change can
be made live in one command.

## Problem / Context

Taurcode's Espanso export is a plain file write to a caller-supplied
directory, and installing generated packages is documented as an explicit
non-goal (`docs/reference/espanso-integration.md`, "Out of scope"). That gap
caused a real incident: the `espanso-match-force-clipboard` fix merged in
PR #49 never reached the package actually installed at
`~/Library/Application Support/espanso/match/packages/taurcode/`, which
silently stayed on a stale snapshot and kept reproducing the original bug in
live testing until it was caught by hand. PR #50 documented the manual
re-export plus `espanso restart` workaround in a new "Keeping a
manually-installed package in sync" subsection; this work item replaces that
manual path with a command and reduces the subsection to a fallback
description.

`project/design/design.md` (Processing and output boundary) and roadmap
Phase 3 both anticipate "a future explicit install command" once export and
roundtrip validation are trusted. That precondition is now met: the Espanso
roundtrip foundation is complete per `project/status/`, so this is scoped
feature work rather than unfinished foundation work.

### Duplication search
- In-repo: No existing implementation found — no install, platform-detection, or `subprocess` code exists anywhere in `src/` or `tests/`.
- Sibling repos: None identified. Espanso references in `LogicalRoboticsHarness` are skill documentation; those in `Promptspace` are archived Taurcode prompts.
- External libraries: Considered Espanso's own CLI. `espanso package install --external --git` installs only from a git repository of a package, which is the wrong shape for a locally generated export. `espanso path packages` prints the real packages directory but would make the core install depend on the binary being present; use the hardcoded macOS default plus a `--packages-dir` override instead, and cite `espanso path packages` in docs as the way to find a non-default location.
- Recommendation: Proceed.

### Demand search
- Work items: None found.
- Proposals: None found. Anticipated, not requested, by `project/design/design.md` (Processing and output boundary) and roadmap Phase 3.
- Backlog: No `project/design/backlog.md` file exists in this repo.
- Recommendation: Offer to update `project/design/design.md` and roadmap Phase 3 at closeout, since both currently describe install as deferred or future.

## Scope

- Add a single `install espanso` CLI subcommand plus a new
  `espanso_install` module that reuses `espanso_export.export_espanso`.
- Gate strictly on macOS; fail clearly and nonzero on every other platform.
- Make `espanso restart` opt-in behind `--restart`.
- Update the Espanso integration reference and README to lead with the new
  command, and narrow the FOCUS-BOOTSTRAP Non-Goal that this work would
  otherwise contradict.

## Required Changes

1. `src/taurcode/espanso_install.py` — new module holding
   `MACOS_PACKAGES_DIR = "~/Library/Application Support/espanso/match/packages"`;
   an `InstallError(ValueError)` subclass so `cli.main`'s existing
   `except (OSError, ValueError)` handler catches it without a new clause;
   `resolve_packages_dir(platform, override)` raising `InstallError` on any
   non-`darwin` platform; `install_espanso(prompts, packages_dir, name,
   source_dir)` delegating to
   `espanso_export.export_espanso(prompts, str(packages_dir / name), source_dir=...)`
   — because `package_name = output.name` in `src/taurcode/espanso_export.py`,
   the generated manifest name tracks `<name>` automatically; and
   `restart_espanso()` using `shutil.which("espanso")` followed by
   `subprocess.run(["espanso", "restart"])`, raising `InstallError` on a
   missing binary or a nonzero exit.
2. `src/taurcode/cli.py` — add an `install` parser with an `espanso`
   subparser taking `--prompts` (default `CANONICAL_PROMPTS_DIR`), `--name`
   (default `taurcode`), `--packages-dir` (default `None`, meaning platform
   resolution), and `--restart` (`store_true`). The handler validates prompts
   first, installs, prints the resolved target path, then either restarts or
   prints the `espanso restart` instruction.
3. `tests/espanso_install_test.py` — cover the platform gate with injected
   `darwin`/`linux`/`win32` values; install into a temporary directory;
   assert the generated manifest name matches the directory name; cover the
   `--name` override; assert restart runs only with the flag, via an injected
   runner and `which` lookup; cover the missing-binary and nonzero-exit error
   paths.
4. `tests/cli_defaults_test.py` — add parser-default coverage for the new
   subcommand alongside the existing default tests.
5. `docs/reference/espanso-integration.md` — add an "Install command"
   section, amend the "Out of scope" sentence that currently says Taurcode
   does not install packages, and rewrite "Keeping a manually-installed
   package in sync" to lead with the command and retain the manual steps only
   as a description of what it automates.
6. `README.md` — add the new command to the CLI usage listing.
7. `project/focus/current_focus.md` — narrow the Non-Goal "Adding new CLI
   commands in this closeout phase" to "Adding new CLI commands without a
   dedicated work item and tests," consistent with the same document's
   Priority 5.

## Non-Goals

- Do not add Linux or Windows package paths. `--packages-dir` stays a
  macOS-only override for non-default configurations, so cross-platform
  support is not added through the back door.
- Do not implement continuous sync, watch mode, or freshness detection —
  this is one-shot install only.
- Do not shell out to `espanso` for anything beyond `restart`.
- Do not integrate with `espanso package install` or the Espanso hub.
- Do not archive or resolve `FOCUS-BOOTSTRAP` — its Exit Criteria depend on
  the still-open `WI-PROJECT-PLANE-VALIDATION-CLEANUP`.
- Do not change export, import, lint, or roundtrip semantics.
- Do not let any automated test write to the real Espanso application-support
  directory or restart a live Espanso process.

## Acceptance Criteria

- `taurcode install espanso` writes `package.yml` and metadata assets into
  `<packages-dir>/<name>/` through `espanso_export.export_espanso`, and the
  generated manifest `name:` matches the installed directory name.
- On any non-`darwin` platform the command prints a clear unsupported-platform
  message and exits nonzero without writing files or guessing a path.
- `--restart` is opt-in. Without it the command prints the `espanso restart`
  instruction; with it, a missing `espanso` binary produces a clear error and
  a nonzero exit rather than a traceback.
- Every automated test resolves its install target through an injected or
  parameterized directory; no test writes under the real Espanso
  application-support path.
- The `FOCUS-BOOTSTRAP` Non-Goal is narrowed to permit CLI commands that have
  a dedicated work item and tests.
- `docs/reference/espanso-integration.md` points at the new command as the
  preferred sync path, keeping the manual steps as fallback.
- `scripts/format --check --diff`, `scripts/lint`, `scripts/test`, and
  `lrh validate` pass with 0 new failures.

## Validation

- `scripts/develop`
- `scripts/version tools`
- `scripts/format --check --diff`
- `scripts/lint`
- `scripts/test`
- `lrh validate`
- `taurcode install espanso --packages-dir <tmp-dir>` (spot-check installed files and manifest name)

## Risk Notes

- This is the first Taurcode operation that writes to a machine-local
  location the user did not name on the command line. A wrong default or a
  wrong `--name` writes into the developer's live Espanso configuration.
- This is the first `subprocess` use in the codebase. A test that shells out
  for real would restart the developer's live Espanso, so the restart path
  must be injectable and never exercised against the real binary in tests.
- `export_espanso` calls `mkdir(parents=True, exist_ok=True)` and overwrites
  `package.yml` in place, so a mistyped `--name` silently creates a new
  package directory instead of failing.

## Related Workstream and Designs

- Design: `project/design/design.md` (Processing and output boundary — "A future explicit install command may be considered after validation/export behavior is trusted")
- Design precedent: `project/design/proposals/adopted/espanso-match-force-clipboard/00_proposal.md` (sibling scope and process precedent; this item does not modify it)
- Focus: `project/focus/current_focus.md` (`FOCUS-BOOTSTRAP`) — Priority 5, "Scope future exporter targets, install behavior, or advanced Espanso support as separate design/implementation work," which this item satisfies. Required Change 7 narrows the Non-Goal on line 35 accordingly, per explicit user decision.
