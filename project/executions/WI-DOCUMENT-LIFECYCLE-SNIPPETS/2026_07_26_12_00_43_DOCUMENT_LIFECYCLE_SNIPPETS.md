---
execution_id: 2026_07_26_12_00_43_DOCUMENT_LIFECYCLE_SNIPPETS
prompt_id: PROMPT(WI-DOCUMENT-LIFECYCLE-SNIPPETS:DOCUMENT_LIFECYCLE_SNIPPETS)[2026-07-26T11:57:28-04:00]
work_item: WI-DOCUMENT-LIFECYCLE-SNIPPETS
status: in_progress
rerun_of: 
pr: https://github.com/xenotaur/Taurcode/pull/65
commit: 
created_at: 2026-07-26T12:00:43-04:00
agent: claude_code
instruction_source: project/work_items/proposed/WI-DOCUMENT-LIFECYCLE-SNIPPETS.md
session_transcript: https://claude.ai/epitaxy/local_ed7726e5-900b-493d-ae77-ae5b6a7194d0
---

# Summary

Implement `WI-DOCUMENT-LIFECYCLE-SNIPPETS`: make `:execute`, `:land`, and
`:assess` discoverable from `README.md`. Opened as PR #65.

# Result

Added a "Prompt lifecycle snippets" subsection to `README.md`, right after the
existing `:prompt-review` / `:lrh-template-review` paragraphs, following that
same precedent (a paragraph per snippet, no new `docs/` page). Documents:

- `:execute` — full work-item-to-closeout chain.
- `:land` — post-PR tail only.
- The two shared contracts: the **merge gate** (always stops for a human,
  with a pre-merge PR summary) and the **review-landed rule** (an empty
  comment-thread list right after pushing is not proof of a clean review).
- The **CHAIN-NOTE** evidence signal (greppable via
  `lrh search executions "CHAIN-NOTE"`) and the **find-or-backfill**
  execution-record behavior at closeout.
- `:assess` — PR go/no-go evaluator, judged on technical merit rather than
  authorship.

Diff scoped to `README.md` only (13 insertions). No change to the snippets
themselves, per the work item's stated out-of-scope.

# Validation

- `scripts/version tools` — Black had drifted to 25.11.0 vs. the
  `constraints-dev.txt` pin of 26.3.1; reinstalled via
  `pip install -e ".[dev]" -c constraints-dev.txt` to correct it before
  formatting.
- `scripts/format --check --diff` — passed, 28 files unchanged.
- `scripts/lint` — passed (ruff + black check).
- `scripts/test` — 199 tests, OK.
- `lrh validate --project-dir project` — 0 errors, 0 warnings (unchanged).

# Follow-up

None from this record. See `WS-PROMPT-LIFECYCLE-TOOLKIT` for the separately
tracked follow-up on removing the manual `<SESSION_URL>` step.
