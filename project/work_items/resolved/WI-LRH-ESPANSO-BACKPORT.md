---
resolution: "Implemented and merged in PR #72 (commit 661c9b3)."
blocked_reason: null
blocked: false
id: WI-LRH-ESPANSO-BACKPORT
title: Add prompts/lrh/ Espanso backport package
type: deliverable
status: resolved
owner: anthony
contributors:
  - anthony
assigned_agents: []
related_focus:
  - FOCUS-BOOTSTRAP
related_roadmap: []
related_workstreams:
  - WS-LRH-BACKPORT-AND-HARDENING
related_design:
  - project/design/proposals/proposed/lrh-backport-and-hardening/00_proposal.md
depends_on: []
blocked_by: []
expected_actions:
  - create_file
  - edit_file
  - run_tests
  - create_pr
forbidden_actions:
  - force_push
  - delete_branch
  - merge_pr
  - implement_taurcode_show
  - implement_release_hardening
  - move_prompts_to_lrh_repo
acceptance:
  - prompts/lrh/espanso/_manifest.yml, README.md, and LICENSE exist with curated content naming lrh (not Taurcode) as the package identity
  - prompts/lrh/implement.md, review-response.md, confirm-fixes.md, and closeout.md exist, each with a :lrh-<name>-prefixed keyword
  - taurcode export espanso --prompts prompts/lrh --output exports/espanso/lrh produces a package named lrh using the curated manifest, not espanso_metadata.generate_default_manifest()'s default
  - exports/espanso/lrh/ is committed, mirroring the existing exports/espanso/taurcode/ checked-in export
  - On macOS, taurcode install espanso --prompts prompts/lrh installs a package independent of the existing taurcode package; on other platforms, resolve_packages_dir rejects the install by design (espanso_install.py:39-53), so the equivalent check is that taurcode export espanso --prompts prompts/lrh produces a package.yml/_manifest.yml pair with lrh as the package name
  - taurcode validate --prompts prompts/lrh and taurcode lint prompts --prompts prompts/lrh pass with 0 errors
  - lrh validate passes with 0 errors
required_evidence:
  - lrh_validate
  - manual_review
artifacts_expected:
  - prompts/lrh/implement.md
  - prompts/lrh/review-response.md
  - prompts/lrh/confirm-fixes.md
  - prompts/lrh/closeout.md
  - prompts/lrh/espanso/_manifest.yml
  - prompts/lrh/espanso/README.md
  - prompts/lrh/espanso/LICENSE
  - exports/espanso/lrh/_manifest.yml
  - exports/espanso/lrh/README.md
  - exports/espanso/lrh/LICENSE
  - exports/espanso/lrh/package.yml
---

# Add prompts/lrh/ Espanso backport package

## Summary

Add a `prompts/lrh/` corpus of `:lrh-`-prefixed Espanso snippets backporting proven LRH slash-command skills (starting with `/lrh-implement`, `/lrh-review-response`, `/lrh-confirm-fixes`, `/lrh-closeout`), packaged separately from the existing `taurcode` Espanso package, with the generated package checked in at `exports/espanso/lrh/`.

## Problem / Context

`prompts/taurcode/implement.md` is the only existing hand-authored backport of an LRH slash-command skill (`:implement`), and `prompts/taurcode/lrh-template-review.md` is the only existing `:lrh-`-prefixed trigger. The governing design (`project/design/proposals/proposed/lrh-backport-and-hardening/00_proposal.md`, merged via PR #67) settled naming (`:lrh-` prefix), packaging (separate `lrh` package — required since Espanso's package manager only supports `install | list | uninstall | update`, no `enable`/`disable`), manifest curation (hand-written, not the tool's generated default, to avoid inheriting Taurcode's own hardcoded homepage), and source location (`prompts/lrh/` inside this repo, for now). This work item delivers that first track.

### Duplication search
- In-repo: No existing implementation found. The only in-repo matches were skill-authoring boilerplate examples referencing "lrh-implement" as illustrative text, not an implementation.
- Sibling repos: None identified — LRH has no Espanso tooling of its own (confirmed during the governing proposal's research).
- External libraries: None identified.
- Recommendation: Proceed.

### Demand search
- Work items: None found beyond this one.
- Proposals: Found: the governing proposal itself (`project/design/proposals/proposed/lrh-backport-and-hardening/00_proposal.md`) — this work item is the intended implementation, not a duplicate request.
- Backlog: No `project/design/backlog.md` exists in this repo.
- Recommendation: No action.

## Scope

- Curated `prompts/lrh/espanso/{_manifest.yml,README.md,LICENSE}`.
- `prompts/lrh/{implement,review-response,confirm-fixes,closeout}.md`, each with a `:lrh-<name>` keyword.
- Checked-in generated package at `exports/espanso/lrh/`, mirroring `exports/espanso/taurcode/`.
- Verify export/install produces a correctly-named, independently-installable `lrh` package.

## Required Changes

1. Create `prompts/lrh/espanso/_manifest.yml`, `README.md`, `LICENSE` with `lrh`-specific identity (name, title, homepage), following the shape of `prompts/taurcode/espanso/`.
2. Create `prompts/lrh/implement.md` (`:lrh-implement`), backporting/relocating the existing `prompts/taurcode/implement.md` content into the new namespace.
3. Create `prompts/lrh/review-response.md` (`:lrh-review-response`), `prompts/lrh/confirm-fixes.md` (`:lrh-confirm-fixes`), and `prompts/lrh/closeout.md` (`:lrh-closeout`), each backporting the corresponding LRH slash-command skill.
4. Run `taurcode validate --prompts prompts/lrh` and `taurcode lint prompts --prompts prompts/lrh` to confirm the new corpus is well-formed.
5. Run `taurcode export espanso --prompts prompts/lrh --output exports/espanso/lrh` and commit the generated `exports/espanso/lrh/` output.
6. On macOS, run `taurcode install espanso --prompts prompts/lrh` to confirm the package installs correctly as `lrh`, independent of `taurcode`. `taurcode install espanso` is macOS-only by design (`resolve_packages_dir` rejects every other platform, `src/taurcode/espanso_install.py:39-53`); on other platforms, rely on the export-based check in step 5 instead.
7. `WI-LRH-ESPANSO-BACKPORT` is already listed in `WS-LRH-BACKPORT-AND-HARDENING`'s `work_items:` — done as part of creating this work item, not deferred to implementation.

## Non-Goals

- Does not implement `taurcode show` — a separate work item under the same workstream.
- Does not perform any part of Taurcode's release hardening — a separate work item under the same workstream.
- Does not move `prompts/lrh/` into LRH's own repo — explicitly deferred per the governing proposal's Decision 4 and the workstream's Non-Goals.
- Does not decide the fleet-wide skill-extraction ordering (the proposal's Open Decision 7).
- Does not remove `prompts/taurcode/implement.md` or `lrh-template-review.md` — whether/how to retire or cross-reference the old `:implement` snippet once `:lrh-implement` exists is left open below.

## Acceptance Criteria

See frontmatter `acceptance:` above.

## Validation

- `scripts/develop`
- `scripts/version tools`
- `taurcode validate --prompts prompts/lrh`
- `taurcode lint prompts --prompts prompts/lrh`
- `taurcode export espanso --prompts prompts/lrh --output exports/espanso/lrh`
- `taurcode install espanso --prompts prompts/lrh` (macOS only; on other platforms, inspect the `exports/espanso/lrh/package.yml` and `_manifest.yml` produced by the export step above instead)
- `lrh validate`

## Open Questions

- Should `prompts/taurcode/implement.md` be retired/redirected once `:lrh-implement` exists, or left standing alongside it? Not decided — flagging rather than assuming.
