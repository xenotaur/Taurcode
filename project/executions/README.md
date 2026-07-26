# Executions

This directory stores prompt execution records when automation scripts are unavailable in-repo.

## Naming
- `YYYY-MM-DD-<PROMPT_ID>.md`

## Minimum fields
- Prompt ID
- Date
- Scope
- Summary of changes
- Related work item (or `AD_HOC`)

## Important rules

- Prompts should only manipulate execution records related to them; leave
  unrelated execution records alone.
- A record's narrative body (its summary/result/validation/follow-up
  content) is immutable once merged to `main` — even where it has since gone
  stale. Annotate a correction in a later, separate record rather than
  rewriting it.
- The exception is limited frontmatter backfills and corrections to a
  record's own provenance metadata (for example a closeout populating
  `status`, `pr`, or `commit`) — these are allowed because they record what
  actually happened, and are normal closeout workflow.
- Editing a record's own body across pushes on the PR that originally
  authored it (before that PR merges) is normal iteration, not a rewrite —
  the record isn't yet historical. Once merged, treat it as immutable.
