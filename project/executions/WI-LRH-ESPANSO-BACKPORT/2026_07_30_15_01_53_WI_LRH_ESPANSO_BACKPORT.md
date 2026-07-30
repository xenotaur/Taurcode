---
execution_id: 2026_07_30_15_01_53_WI_LRH_ESPANSO_BACKPORT
prompt_id: PROMPT(WI-LRH-ESPANSO-BACKPORT:WI_LRH_ESPANSO_BACKPORT)[2026-07-30T14:54:15-04:00]
work_item: WI-LRH-ESPANSO-BACKPORT
status: in_progress
rerun_of:
pr: https://github.com/xenotaur/Taurcode/pull/72
commit: e49418c
created_at: 2026-07-30T15:01:53-04:00
agent: claude_app
instruction_source: project/work_items/proposed/WI-LRH-ESPANSO-BACKPORT.md
session_transcript: pending
---

# Summary

Implemented `WI-LRH-ESPANSO-BACKPORT`: a curated `prompts/lrh/` Espanso
corpus (`:lrh-implement`, `:lrh-review-response`, `:lrh-confirm-fixes`,
`:lrh-closeout`) backporting proven LRH slash-command skills, shipped as a
separate `lrh` package independent of `taurcode`, checked in at
`exports/espanso/lrh/`.

# Result

- Created `prompts/lrh/espanso/{_manifest.yml,README.md,LICENSE}` with
  `lrh`-specific identity — `name: lrh`, `homepage:
  https://github.com/xenotaur/logical_robotics_harness` (the real LRH repo,
  not Taurcode's).
- Created `prompts/lrh/lrh-implement.md`, `lrh-review-response.md`,
  `lrh-confirm-fixes.md`, `lrh-closeout.md`, condensed self-contained
  versions of the corresponding LRH skills, each with a `:lrh-<name>`
  keyword.
- **Deviation from the WI's literal filenames:** the WI's `artifacts_expected`
  named `implement.md`, `review-response.md`, etc. (no `lrh-` prefix).
  `taurcode lint prompts` flagged this via its `prompt-filename-slug` rule —
  the filename stem must match the keyword slug — confirmed correct against
  the existing `prompts/taurcode/lrh-template-review.md` precedent (whose
  filename already includes the full `lrh-` prefix). Renamed all four files
  to `lrh-<name>.md` to lint clean; this satisfies the WI's actual intent
  (correct `:lrh-<name>` keywords existing) even though it doesn't match the
  WI's literal filename text.
- Ran `taurcode export espanso --prompts prompts/lrh --output exports/espanso/lrh`
  and committed the generated package. One expected warning:
  `manifest-homepage-package-mismatch` (the lint heuristic expects the
  homepage's repo slug to equal the package name; here `lrh`'s homepage
  correctly points to `logical_robotics_harness`, the actual upstream repo,
  not a literal `lrh`-named one — verified this is the check working as
  intended, not a defect, and exactly the bug class this whole design
  proposal was meant to prevent).
- Ran `taurcode install espanso --prompts prompts/lrh` on macOS — confirmed
  `lrh` installs independently under `~/Library/Application Support/espanso/
  match/packages/`, alongside the pre-existing `taurcode` package, neither
  disturbing the other.
- Updated `README.md` with a new "LRH prompt backport (`lrh` package)"
  section documenting the new package and its four snippets.
- Did not touch `prompts/taurcode/implement.md` or `lrh-template-review.md`,
  `taurcode show`, or any release-hardening work, per the WI's Non-Goals and
  `forbidden_actions`.

Prior-art check was already present in the work item (Duplication/Demand
search both recorded there) — no re-check needed per Step 1.5.

# Validation

- `scripts/develop` — re-synced editable install.
- `scripts/version tools` — taurcode 0.1.0, Python 3.11.8, black 26.3.1,
  ruff 0.15.12, coverage 7.13.5 — all matching `constraints-dev.txt`.
- `scripts/format --check --diff` — 28 files unchanged.
- `scripts/lint` — ruff and black checks passed.
- `scripts/test` — 199 tests, OK.
- `taurcode validate --prompts prompts/lrh` — 4 prompts, passed.
- `taurcode lint prompts --prompts prompts/lrh` — passed (after the filename
  rename above).
- `taurcode export espanso --prompts prompts/lrh --output exports/espanso/lrh`
  — package name `lrh`, curated manifest used; one expected/reviewed warning
  (see Result).
- `taurcode install espanso --prompts prompts/lrh` — installed independently
  of `taurcode` (macOS).
- `lrh validate` — 0 errors, 0 warnings.

# Follow-up

- `session_transcript` is `pending` — update to `claude-app:<session-id>`
  after this session ends.
- The WI's own Open Question (whether to retire `prompts/taurcode/implement.md`
  once `:lrh-implement` exists) remains unresolved — not addressed here, by
  design.
- Run `/lrh-review-response` on PR #72 (repeat as needed), then
  `/lrh-confirm-fixes` before merge.
