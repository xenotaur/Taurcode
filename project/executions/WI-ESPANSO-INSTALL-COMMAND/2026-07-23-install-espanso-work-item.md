---
prompt_id: PROMPT(WI-ESPANSO-INSTALL-COMMAND:IMPLEMENT_INSTALL_ESPANSO)[2026-07-23T17:42:32-04:00]
date: 2026-07-23
scope: WI-ESPANSO-INSTALL-COMMAND
status: in_progress
---

## Summary

Planning stage for a macOS-only `taurcode install espanso` subcommand. Ran the
prior art check, resolved two open design questions with the user, and created
the work item `project/work_items/proposed/WI-ESPANSO-INSTALL-COMMAND.md`.

## Result

- Prior art: no in-repo implementation (no install, platform-detection, or
  `subprocess` code exists in `src/` or `tests/`); no sibling-repo
  implementation; Espanso's own `package install --external --git` and
  `espanso path packages` were assessed and not adopted as dependencies.
- Demand: `project/design/design.md` (Processing and output boundary) and
  roadmap Phase 3 both anticipate an explicit install command. Neither is a
  closeable request, but both should be updated at closeout since they
  currently describe install as deferred.
- Design decision 1 (user): `--restart` is opt-in and off by default; a
  missing `espanso` binary must be a clear error with nonzero exit.
- Design decision 2 (user): narrow the `FOCUS-BOOTSTRAP` Non-Goal on new CLI
  commands rather than archiving the focus. `FOCUS-BOOTSTRAP` cannot be
  resolved while `WI-PROJECT-PLANE-VALIDATION-CLEANUP` remains open, because
  its own Exit Criteria depend on accurate project-plane state.
- Work item created and opened as PR #52. Implementation has not started.

## Validation

- `lrh validate`: 19 errors on this branch, 19 errors on clean `main` — 0 new.
  All are the known project-plane issues tracked by
  `WI-PROJECT-PLANE-VALIDATION-CLEANUP`; none reference the new file.
- Code validation commands (`scripts/develop`, `scripts/format --check
  --diff`, `scripts/lint`, `scripts/test`) not run at this stage: this commit
  changes no Python. They are required before the implementation PR.

## Follow-up

- Implement the work item (`/lrh-implement`), running `scripts/develop` before
  claiming installability or CLI operability.
- At closeout, offer to update `project/design/design.md` and roadmap Phase 3,
  which currently describe install as future work.
- Note for tooling: `scripts/prompts/label-prompt`, documented in `PROMPTS.md`,
  does not exist in this repo — only `scripts/prompts/record-execution` does.
  The prompt ID for this cycle was constructed by hand.
