---
resolution: null
blocked_reason: null
blocked: false
id: WI-ESPANSO-MATCH-FORCE-CLIPBOARD
title: Implement per-match force_clipboard opt-in for Espanso export
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
  - project/design/proposals/adopted/espanso-match-force-clipboard/00_proposal.md
depends_on: []
blocked_by: []
expected_actions:
  - edit_file
  - run_tests
  - create_pr
forbidden_actions:
  - force_push
  - delete_branch
  - merge_pr
  - implement_force_mode_keys
acceptance:
  - taurcode validate rejects non-mapping targets/targets.espanso and non-boolean force_clipboard; accepts absent or false
  - taurcode export espanso emits force_clipboard: true only for prompts that set targets.espanso.force_clipboard: true; all other prompts' package.yml output is byte-identical to before
  - taurcode import espanso --merge round-trips force_clipboard: true back into targets.espanso.force_clipboard: true on both fresh and merge import, without imported_raw fallback or an orphan warning
  - taurcode roundtrip espanso fails on a regression fixture where the exporter drops or corrupts force_clipboard
  - taurcode lint prompts warns (non-blocking) on a prompt body under 100 characters missing force_clipboard
  - prompts/taurcode/dashes.md sets targets.espanso.force_clipboard: true
  - scripts/test and lrh validate pass with 0 new failures
required_evidence:
  - lrh_validate
  - test_output
  - manual_review
artifacts_expected:
  - src/taurcode/validate.py
  - src/taurcode/espanso_export.py
  - src/taurcode/espanso_import.py
  - src/taurcode/semantic_normalize.py
  - src/taurcode/prompt_lint.py
  - docs/reference/canonical-prompt-format.md
  - docs/reference/espanso-integration.md
  - prompts/taurcode/dashes.md
  - tests/prompt_validation_test.py
  - tests/espanso_export_test.py
  - tests/espanso_import_test.py
  - tests/prompt_lint_test.py
  - tests/semantic_normalize_test.py
  - tests/fixtures/roundtrip/
---

# Implement per-match force_clipboard opt-in for Espanso export

## Summary

Implement the adopted proposal `espanso-match-force-clipboard`: an opt-in
`targets.espanso.force_clipboard` frontmatter field, threaded through
validation, export, import, semantic-roundtrip checks, and prompt lint, so
short Taurcode prompts can force Espanso's Clipboard-backend delivery
instead of Espanso's default Inject backend.

## Problem / Context

Espanso's `Auto` backend delivers matches under 100 characters via
simulated keypresses (`Inject`), which sends a trailing `\n` as a real
Return keypress — submitting a chat input bound to "Enter sends" (observed
via `:dashes`). The adopted design in
`project/design/proposals/adopted/espanso-match-force-clipboard/00_proposal.md`
specifies a per-match opt-in field, validated shape requirements, and
round-trip coverage in the importer and semantic-normalize layers, ordered
so each step's precondition lands before what depends on it.

### Duplication search
- In-repo: No existing implementation found; only the design proposal exists.
- Sibling repos: None identified.
- External libraries: None identified.
- Recommendation: Proceed.

### Demand search
- Work items: None found.
- Proposals: Found: PROP espanso-match-force-clipboard — adopted; this item is exactly what it calls for.
- Backlog: No `project/design/backlog.md` file exists in this repo.
- Recommendation: No action.

## Scope

- Add `targets.espanso.force_clipboard` type validation to `taurcode validate`.
- Add exporter support to emit `force_clipboard: true` on matching prompts.
- Add importer support to round-trip `force_clipboard` on fresh and merge import.
- Add semantic-roundtrip coverage so a dropped/corrupted `force_clipboard` fails `taurcode roundtrip espanso`.
- Add an advisory prompt-lint warning for short bodies missing the flag.
- Apply the field to `prompts/taurcode/dashes.md` and update docs.

## Required Changes

1. `src/taurcode/validate.py` — require `targets`, when present, to be a mapping; `targets.espanso`, when present, to be a mapping; `targets.espanso.force_clipboard`, when present, to be a boolean. Non-conforming shapes are validation errors.
2. `src/taurcode/espanso_export.py` — read `targets.espanso.force_clipboard` per match; emit `force_clipboard: true` when set; unchanged output otherwise.
3. `src/taurcode/espanso_import.py` — extend `_SIMPLE_KEYS`/`is_simple_match` to accept an optional `force_clipboard: true` key; map it back to `targets.espanso.force_clipboard: true` on both fresh import (`import_espanso`) and merge import (`_merge_simple_matches`).
4. `src/taurcode/semantic_normalize.py` — capture `targets.espanso.force_clipboard` explicitly on `NormalizedPrompt` in both `normalize_canonical_prompts` and `normalize_espanso_package`. `_compare_canonical_prompt_fields` only runs under `CANONICAL_SEMANTIC_MODE`, but `taurcode roundtrip espanso` (`roundtrip.compare_espanso_roundtrip`) runs under `ESPANSO_SEMANTIC_MODE` — compare `force_clipboard` in both mode paths, and include it in `_prompt_signature` (used for duplicate/missing/extra prompt-occurrence detection in `_compare_prompt_group`) so a signature collision can't mask a dropped or corrupted value. Add a roundtrip regression fixture for a dropped/corrupted field that exercises `taurcode roundtrip espanso` directly, not just canonical-mode comparison.
5. `src/taurcode/prompt_lint.py` — add a `_style_warnings` warning for prompt bodies under 100 characters (Espanso's `clipboard_threshold` default) missing `force_clipboard`.
6. `docs/reference/canonical-prompt-format.md` — add `force_clipboard` to the Optional fields table, including the shape-validation rule from step 1.
7. `docs/reference/espanso-integration.md` — short note on the Inject/Clipboard split and why the field exists.
8. `prompts/taurcode/dashes.md` — set `targets.espanso.force_clipboard: true`.
9. Tests: extend `tests/prompt_validation_test.py`, `tests/espanso_export_test.py`, `tests/espanso_import_test.py`, `tests/prompt_lint_test.py`, `tests/semantic_normalize_test.py`; update roundtrip fixtures under `tests/fixtures/roundtrip/` for the `:dashes`-equivalent fixture.

## Non-Goals

- Do not expose Espanso's `force_mode: "keys"` — no current use case (proposal Non-Goal).
- Do not change exporter output for any prompt that doesn't set the field.
- Do not touch or revert the machine-local `backend: Clipboard` override in any user's local Espanso config — that's outside this repo's scope.
- Do not add a hard validation error for a short body missing the flag — the lint warning is advisory only.

## Acceptance Criteria

- `taurcode validate` rejects non-mapping `targets`/`targets.espanso` and non-boolean `force_clipboard`; accepts absent or `false`.
- `taurcode export espanso` emits `force_clipboard: true` only for prompts that set the field; all other prompts' `package.yml` output is byte-identical to before.
- `taurcode import espanso --merge` round-trips `force_clipboard: true` on both fresh and merge import, without `imported_raw` fallback or an orphan warning.
- `taurcode roundtrip espanso` fails on a regression fixture where the exporter drops or corrupts `force_clipboard`.
- `taurcode lint prompts` warns (non-blocking) on a short body missing `force_clipboard`.
- `prompts/taurcode/dashes.md` sets `targets.espanso.force_clipboard: true`.
- `scripts/test` and `lrh validate` pass with 0 new failures.

## Validation

- `scripts/version tools`
- `scripts/format --check --diff`
- `scripts/lint`
- `scripts/test`
- `lrh validate`
- `taurcode export espanso --prompts prompts/taurcode --output <tmp-dir>` (spot-check `:dashes` block includes `force_clipboard: true`)
- `taurcode roundtrip espanso` (confirms the new regression fixture behavior)

## Risk Notes

- The importer and semantic-normalize changes touch shared round-trip machinery used by every prompt, not just `:dashes` — regressions there would be silent for prompts that never use `force_clipboard`, since `is_simple_match`/`unsupported_fields` handling is shared code path. Keep step 3 and step 4 changes minimal and covered by their own fixtures.
- Sequencing matters: step 1 (validation) must land before step 2 (exporter read) is exercised against real prompt files, since the exporter's chained `.get()` access relies on validation already having rejected malformed shapes.

## Related Workstream and Designs

- Design: `project/design/proposals/adopted/espanso-match-force-clipboard/00_proposal.md`
- Focus: `project/focus/current_focus.md` (`FOCUS-BOOTSTRAP`) — priority 5, "Scope future exporter targets... as separate design/implementation work," which this item satisfies.
