---
execution_id: 2026_07_24_16_45_00_FIX_ESPANSO_MANIFEST_NAME_MISMATCH
prompt_id: PROMPT(AD_HOC:FIX_ESPANSO_MANIFEST_NAME_MISMATCH)[2026-07-24T16:44:48-04:00]
work_item: AD_HOC
status: landed
rerun_of: 
pr: https://github.com/xenotaur/Taurcode/pull/57
commit: b19c06e062bbde8539b7658cd90dff2c263fda4f
created_at: 2026-07-24T16:45:00-04:00
agent: claude_code
instruction_source: interactive session (chat-driven, no work item); :land driven closeout
session_transcript: https://claude.ai/epitaxy/local_ed7726e5-900b-493d-ae77-ae5b6a7194d0
---

# Summary

Clear the pre-existing `taurcode lint espanso` `manifest-name-mismatch` error by
renaming the checked-in Espanso export directory `exports/espanso/package/` to
`exports/espanso/taurcode/`, so the directory name matches the manifest's
declared `name: taurcode`. Landed as PR #57. Follow-up spun off from the
`:execute`/`:land` snippets session (see
`AD_HOC/2026_07_24_15_40_01_ADD_EXECUTE_LAND_LIFECYCLE_SNIPPETS`).

# Result

Pure `git mv` of the four generated package artifacts — `LICENSE`, `README.md`,
`_manifest.yml`, `package.yml` — from `exports/espanso/package/` to
`exports/espanso/taurcode/`, with no content change. The new leaf name matches
the manifest `name:`, the export default convention (`build/espanso/taurcode`),
and the installed-package name
(`~/Library/Application Support/espanso/match/packages/taurcode/`).

Prior-art / reference check: `exports/espanso/package/` was the only real export
directory (no top-level `espanso/` exists; it was created by the earlier "Move
exported prompts to an exports directory" commit). Nothing in code, tests, CI,
or the default export/install paths referenced it — the `espanso/package/`
strings in README, docs, and `tests/cli_defaults_test.py` are illustrative
example paths, not this directory — so the rename is reference-safe.

CHAIN-NOTE: cycles=0; stops=0; gates=[merge]; friction=none; note="pure git-mv rename; review clean (Copilot 0 comments, Codex 👍); no execution record pre-existed, created at closeout"

# Validation

- `taurcode lint espanso --input exports/espanso/taurcode` — passes clean
  (previously errored `manifest-name-mismatch`; the related
  `manifest-homepage-package-mismatch` warning also cleared).
- `taurcode export espanso --prompts prompts/taurcode --output exports/espanso/taurcode`
  — produces no diff (checked-in export is idempotent and in sync).
- `taurcode validate` (22 prompts) / `lint prompts` / `format prompts --check`
  — all pass.
- PR #57 CI: coverage, lint, workflow-files, and tests all SUCCESS.
- Review landed clean: Copilot 0 comment threads, Codex reacted 👍; no changes
  required.

# Follow-up

None. The Espanso export/manifest drift and name-mismatch issues raised during
the snippets session are now all resolved (PRs #55, #56, #57).
