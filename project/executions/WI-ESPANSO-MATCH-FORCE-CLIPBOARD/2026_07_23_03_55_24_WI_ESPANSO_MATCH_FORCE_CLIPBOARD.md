---
execution_id: 2026_07_23_03_55_24_WI_ESPANSO_MATCH_FORCE_CLIPBOARD
prompt_id: PROMPT(WI-ESPANSO-MATCH-FORCE-CLIPBOARD:WI_ESPANSO_MATCH_FORCE_CLIPBOARD)[2026-07-23T03:37:42-04:00]
work_item: WI-ESPANSO-MATCH-FORCE-CLIPBOARD
status: in_progress
rerun_of: 
pr: https://github.com/xenotaur/Taurcode/pull/49
commit: 90c5398
created_at: 2026-07-23T03:55:24-04:00
agent: claude_app
instruction_source: project/work_items/proposed/WI-ESPANSO-MATCH-FORCE-CLIPBOARD.md
session_transcript: pending
---

# Summary

Implement the adopted proposal `espanso-match-force-clipboard`, per
`WI-ESPANSO-MATCH-FORCE-CLIPBOARD`'s 9-step Required Changes: an opt-in
`targets.espanso.force_clipboard` frontmatter field threaded through
validation, export, import (fresh + merge round-trip), semantic-roundtrip
comparison, and prompt lint, resolving the original `:dashes`
premature-submit bug at the source.

# Result

All 9 Required Changes items implemented:

1. `src/taurcode/validate.py` — `_validate_espanso_targets` requires
   `targets`/`targets.espanso` to be mappings and `force_clipboard` to be a
   boolean, when present.
2. `src/taurcode/espanso_export.py` — emits `force_clipboard: true` per
   match when `targets.espanso.force_clipboard` is `True`.
3. `src/taurcode/espanso_import.py` — `is_simple_match` accepts an optional
   `force_clipboard: true` key; `_apply_force_clipboard` and
   `_existing_force_clipboard` handle round-trip on fresh import
   (`_fresh_prompt_content`) and merge import (`_render_merged_prompt`),
   covering preserve/add/remove cases.
4. `src/taurcode/semantic_normalize.py` — `NormalizedPrompt.force_clipboard`
   captured in both `normalize_canonical_prompts` and
   `normalize_espanso_package`; compared unconditionally in
   `_compare_single_prompt` (both `CANONICAL_SEMANTIC_MODE` and
   `ESPANSO_SEMANTIC_MODE`) and folded into `_prompt_signature`, per the
   PR #48 review revision (`chatgpt-codex-connector`'s P1 comment).
5. `src/taurcode/prompt_lint.py` — advisory `prompt-short-body-no-force-clipboard`
   warning for bodies under Espanso's 100-char `clipboard_threshold`
   default missing the flag.
6-7. `docs/reference/canonical-prompt-format.md` and
   `docs/reference/espanso-integration.md` — document the field and the
   Inject/Clipboard mechanism.
8. `prompts/taurcode/dashes.md` — sets
   `targets.espanso.force_clipboard: true`.
9. Tests added/extended across `tests/prompt_validation_test.py`,
   `tests/espanso_export_test.py`, `tests/espanso_import_test.py`,
   `tests/prompt_lint_test.py`, `tests/semantic_normalize_test.py`, and a
   new `tests/roundtrip_cli_test.py` regression exercising
   `taurcode roundtrip espanso` directly against a simulated dropped
   `force_clipboard`.

`tests/fixtures/roundtrip/` is unused by any active test (confirmed via
`grep -rl "fixtures/roundtrip" tests/` — no matches) — left untouched
rather than speculatively updated.

Two bugs found and fixed in my own new tests during development (not
product bugs): an export test that assumed alphabetical prompt ordering,
and an import test that assumed `imported_raw/` is only created on
fallback (it's always created upfront, pre-existing behavior).

# Validation

```
$ scripts/version tools
taurcode 0.1.0 / Python 3.11.8 / black 25.11.0 / ruff 0.15.12
$ scripts/format --check --diff
All done — 26 files unchanged (after running scripts/format once to fix
this PR's own new code; also reformatted the pre-existing drift in
tests/espanso_import_test.py noted in prior PRs' execution records, since
this PR already touches that file extensively)
$ scripts/lint
ruff: all checks passed; black: clean
$ scripts/test
Ran 167 tests in 0.758s — OK (147 pre-existing + 20 new)
$ lrh validate
19 pre-existing errors, 0 new
$ taurcode export espanso --prompts prompts/taurcode --output /tmp/taurcode
rc=0; :dashes block includes "force_clipboard: true"; :think and all
other prompts unchanged
$ taurcode roundtrip espanso --input /tmp/taurcode --prompts prompts/taurcode
Roundtrip semantic comparison passed. Prompts compared: 20. Differences: 0.
$ taurcode lint prompts --prompts prompts/taurcode
Prompt lint passed: prompts/taurcode (no other prompt is short enough to
trigger the new warning)
```
Also manually smoke-tested: fresh import of a `force_clipboard: true`
match (`converted=1, raw_fallback=0`, frontmatter correct); merge import
preserve/add/remove cases (verified frontmatter output for each); merge
import of a `force_clipboard: false` or non-boolean value correctly falls
back to `imported_raw` (not silently accepted).

# Follow-up

- `session_transcript` above is `pending` — update to
  `claude-app:<session-id>` after this session ends.
- Next: address PR review comments via `/lrh-review-response`, then
  `/lrh-confirm-fixes` before merge, then closeout (mark this record
  `landed`, resolve `WI-ESPANSO-MATCH-FORCE-CLIPBOARD`).
