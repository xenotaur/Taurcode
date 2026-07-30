---
resolution: null
blocked_reason: null
blocked: false
id: WI-TAURCODE-SHOW-COMMAND
title: Implement taurcode show CLI command
type: deliverable
status: proposed
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
  - add_cli_command
  - run_tests
  - create_pr
forbidden_actions:
  - force_push
  - delete_branch
  - merge_pr
  - implement_espanso_backport_content
  - implement_release_hardening
  - move_prompts_to_lrh_repo
acceptance:
  - taurcode show <keyword> with no --prompts prints the matching snippet body from the explicit canonical-corpus list (prompts/taurcode, prompts/lrh) to stdout, exit 0
  - taurcode show <keyword> --prompts <dir> searches only that directory, not the canonical list
  - A keyword not found (in the given corpus, or in any canonical corpus by default) prints an error to stderr and exits non-zero
  - A keyword matching more than one canonical corpus prints an error listing which corpora matched and exits non-zero, rather than silently picking one
  - The canonical-corpus list is an explicit, maintained constant — not a glob of prompts/*/ — so prompts/examples/ and prompts/imported/ (IMPORT_STAGING_DIR) are never treated as canonical
  - scripts/format --check --diff, scripts/lint, scripts/test, and lrh validate pass with 0 new failures
required_evidence:
  - lrh_validate
  - test_output
  - manual_review
artifacts_expected:
  - src/taurcode/cli.py
  - src/taurcode/prompt_loader.py
  - tests/cli_defaults_test.py
  - README.md
---

# Implement taurcode show CLI command

## Summary

Add a `taurcode show <keyword> [--prompts <dir>]` CLI command that prints a snippet's body to stdout, for non-Espanso consumption, searching an explicit list of canonical prompt corpora by default rather than a single directory.

## Problem / Context

The governing design (`project/design/proposals/proposed/lrh-backport-and-hardening/00_proposal.md`, Decision 5, merged via PR #67) settled that `taurcode show` should exist for users who don't run Espanso at all. Today's `cli.py` subcommands are `export | install | import | lint | format | roundtrip | validate` — none prints a snippet body, and `load_prompts()` (`src/taurcode/prompt_loader.py:57-61`) only ever walks the one directory it's given. The proposal's own review round (PR #67) established that resolving "all corpora" must use an explicit, maintained list — not a glob of `prompts/*/` — since that directory also contains `prompts/examples/` (non-canonical) and `prompts/imported/` (`IMPORT_STAGING_DIR`, `cli.py:18`), which appears after any `taurcode import espanso` run. Both real canonical corpora now exist (`prompts/taurcode`, `prompts/lrh`, the latter merged via PR #72), so this item is unblocked.

### Duplication search
- In-repo: No existing implementation found. No `show` subcommand or equivalent exists in `cli.py`.
- Sibling repos: None identified.
- External libraries: None identified.
- Recommendation: Proceed.

### Demand search
- Work items: None found.
- Proposals: Found: the governing proposal itself (`lrh-backport-and-hardening/00_proposal.md`) — this work item is its intended implementation, not a duplicate request.
- Backlog: No `project/design/backlog.md` exists in this repo.
- Recommendation: No action.

## Scope

- New `show` subcommand in `cli.py`.
- An explicit, maintained canonical-corpus list (`prompts/taurcode`, `prompts/lrh`) used when `--prompts` is omitted.
- `--prompts <dir>` overrides to a single directory, matching every other subcommand's existing convention.
- Not-found and ambiguous-match error handling.

## Required Changes

1. Add a `CANONICAL_PROMPT_DIRS` (or equivalently named) constant listing the canonical corpora explicitly, next to `CANONICAL_PROMPTS_DIR`/`IMPORT_STAGING_DIR` in `cli.py:17-18`.
2. Add the `show` subparser: positional `keyword`, optional `--prompts <dir>` (unset = search the canonical list).
3. Implement lookup logic: load prompts from either the explicit `--prompts` directory or every canonical corpus, match on `keyword`, print the body to stdout on a unique match.
4. Implement error handling: no match → stderr + non-zero exit; match in more than one canonical corpus → stderr listing the matching corpora + non-zero exit.
5. Add tests covering: single-corpus lookup, default multi-corpus lookup, not-found, and ambiguous-match cases.
6. Document `taurcode show` in `README.md` alongside the other subcommands.

## Non-Goals

- Does not touch `prompts/lrh/` content further or Espanso packaging — that track (`WI-LRH-ESPANSO-BACKPORT`) is already done.
- Does not perform any part of Taurcode's release hardening — a separate work item under the same workstream.
- Does not move anything to the LRH repo.

## Acceptance Criteria

See frontmatter `acceptance:` above.

## Validation

- `scripts/version tools`
- `scripts/format --check --diff`
- `scripts/lint`
- `scripts/test`
- `taurcode show :lrh-implement` (default, multi-corpus)
- `taurcode show :lrh-implement --prompts prompts/lrh` (single-corpus)
- `lrh validate`
