---
execution_id: 2026_07_23_15_10_23_ESPANSO_INSTALL_DRIFT_DOCS
prompt_id: PROMPT(AD_HOC:ESPANSO_INSTALL_DRIFT_DOCS)[2026-07-23T15:09:01-04:00]
work_item: AD_HOC
status: landed
rerun_of: 
pr: https://github.com/xenotaur/Taurcode/pull/50
commit: 491c535a8d788217d3eaeaaff351256fb5df73e2
created_at: 2026-07-23T15:10:23-04:00
agent: claude_app
instruction_source: ad_hoc conversation — live incident during the espanso-match-force-clipboard closeout, where the locally-installed Espanso package went stale after merge
session_transcript: claude-app:a1c6f1d5-79a1-4dbc-a2d3-6183c738a3cc
---

# Summary

Document, in `docs/reference/espanso-integration.md`, that a manually
installed local Espanso package requires a manual re-export/reinstall
step after any change to `prompts/taurcode/` or the exporter — Taurcode
has no sync mechanism and this can silently drift stale, as directly
observed this session.

# Result

Added a "Keeping a manually-installed package in sync" subsection under
"Out of scope" in `docs/reference/espanso-integration.md`, with the
concrete `taurcode export espanso` + `espanso restart` commands. Also
recorded the same fact as a session memory (`feedback_espanso_install_drift.md`)
for future Claude Code sessions in this repo, per the user's explicit
request.

This is one of three follow-ups discussed after the live incident
(memory, docs, install command); the user asked to complete memory and
docs first and hold off on the install-command work until these land.

# Validation

```
$ scripts/test
Ran 171 tests in 1.242s — OK (docs-only change, no code touched)
$ lrh validate
19 pre-existing errors, 0 new
```

# Follow-up

- A `taurcode install espanso` CLI command was discussed as the real
  structural fix (automating what this doc now describes manually), but
  deliberately deferred: `project/focus/current_focus.md`'s Non-Goals
  currently say "Adding new CLI commands in this closeout phase," and
  building it should go through this repo's usual work-item process
  rather than being added ad hoc. Not started.
