---
id: WI-DOCUMENT-LIFECYCLE-SNIPPETS
title: Document the :execute, :land, and :assess prompt snippets
type: deliverable
status: resolved
priority: medium
related_focus:
  - FOCUS-BOOTSTRAP
related_workstreams:
  - WS-PROMPT-LIFECYCLE-TOOLKIT
blocked: false
blocked_reason: ""
resolution: "Documented :execute, :land, and :assess in README.md, implemented and merged in PR #65 (commit 09cbc6f)."
---

# Work Item: Document the :execute, :land, and :assess prompt snippets

## Objective
Make the prompt-lifecycle snippets discoverable from the repository's
documentation. `README.md` and `docs/` currently name only `:prompt-review` and
`:lrh-template-review`; the newer `:execute`, `:land`, and `:assess` snippets are
undocumented and discoverable only by reading the corpus.

## Scope
- Document `:execute` (full work-item-to-closeout chain), `:land` (post-PR tail),
  and `:assess` (PR go/no-go evaluator) in `README.md` and/or the appropriate
  `docs/` page.
- Note the two hard-won contracts they encode: the single human merge gate and
  the review-landed timing rule.
- Mention the CHAIN-NOTE evidence line and the find-or-backfill execution-record
  behavior at closeout.

## Out of scope
- Any change to the snippet content itself (this is documentation only).
- Removing the manual `<SESSION_URL>` step in `:execute` / `:land` (tracked
  separately as a future follow-up on WS-PROMPT-LIFECYCLE-TOOLKIT).

## Exit criteria
- A reader of `README.md` / `docs/` can find and understand when to use
  `:execute`, `:land`, and `:assess` without reading `prompts/taurcode/`.
