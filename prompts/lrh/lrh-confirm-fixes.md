---
id: lrh-confirm-fixes
name: LRH Confirm Fixes
description: Pre-merge, independent verification that pushed review fixes actually resolved reviewers' comments
keyword: ":lrh-confirm-fixes"
---


## Claude.app Confirm-Fixes Request

Independently verify that a PR's pushed review fixes actually resolved the
reviewers' comments, resolve the threads the current diff plainly satisfies,
and surface everything else. This does not merge the PR. Run after the last
review-response round, before the human merge click.

Verification reads the live diff, never a prior round's claims about what
was fixed.

This step requires LRH. If `lrh` is not on PATH, install it once, globally:

    pipx install lrh

LRH is not yet published to PyPI (tracked by `PROP-TAG-PUSH-PYPI-PUBLISHING`
in the LRH repo); until it is, `pipx install <path-to-local-lrh-checkout>`
or a locally built wheel installs the same `lrh` console script.

---

### Step 1 — Detect PR and verify branch

    gh pr view <pr-url> --json headRefName,state --jq '{branch: .headRefName, state: .state}'

Verify the current branch matches. If `state` is not `OPEN`, stop and
report.

---

### Step 2 — Gather state

    lrh request review_response <pr-url>
    lrh github threads <pr-url> --mode raw --state all

Filter the threads output client-side to `isResolved == false` — this is
the authoritative list, broader than `review_response`'s own narrower
"unresolved" notion (which also excludes outdated-but-unresolved threads).
Correlate each thread to its comment data via the thread's *latest* comment
URL.

Then check CI:

    gh pr checks <pr-url> --required --json name,state,bucket

If this errors with "no required checks reported", distinguish a
no-protection repo from a timing race before falling back:

    gh api "repos/<owner>/<repo>/rules/branches/<base>" --jq '[.[] | select(.type=="required_status_checks")] | length'

`0` → no protection, safe to fall back to `gh pr checks <pr-url> --json
name,state,bucket`. `>0` → required checks likely haven't posted yet; treat
CI as pending, do not fall back.

---

### Step 3 — Fresh-eyes verification

For each unresolved thread, read its comment against the current `HEAD`
diff (`gh pr diff <pr-url>`) — never against a prior round's report.
Classify:

- **Clear-satisfied** — diff plainly resolves it → eligible for resolution
- **Unaddressed** — not acted on → surface; offer `:lrh-review-response`
- **Partial** — some instances fixed, others missed → surface, do not resolve
- **Ambiguous** — diff doesn't decide it → surface, do not resolve
- **Problematic resolution** — a fix is present but wrong/incomplete → surface as a finding
- **Problematic comment** — the reviewer's comment is itself wrong or conflicts with a documented design decision → surface with skip-rationale

**Never mark a thread Clear-satisfied unless the diff plainly resolves it.**
When uncertain, use Ambiguous.

Mint a prompt ID (slug from the branch, `-confirm` suffix). A prior
`_CONFIRM` record on this branch is not a blocker — warn and proceed.

---

### Step 4 — Confirm gate (human gate)

Show the user, as a single batch: the Clear-satisfied threads (author +
excerpt), the surfaced exceptions grouped by bucket with a one-line
rationale each, provisional CI status, and the minted prompt ID. **Wait for
explicit confirmation** before resolving anything.

---

### Step 5 — Resolve confirmed threads

For each confirmed Clear-satisfied thread:

    gh api graphql -f query='
    mutation {
      resolveReviewThread(input:{threadId:"<thread-id>"}) {
        thread { id isResolved }
      }
    }'

Skip threads already resolved. For Unaddressed threads, offer
`:lrh-review-response` — do not auto-invoke.

---

### Step 6 — Execution record

    lrh prompt record-execution \
      --prompt-id "<id>" \
      --work-item AD_HOC \
      --slug <slug> \
      --status in_progress \
      --project-root .

Populate `pr:` (the PR URL — required for `:lrh-closeout` to discover this
record later; it greps `^pr: <pr-url>` across `project/executions/`),
`agent`, `instruction_source`, `session_transcript: pending`, and
`rerun_of:` (the primary record for this branch, excluding both `_REVIEW.md`
and `_CONFIRM.md`). Run `lrh validate`, then commit and push as an
additional commit — this is the commit that will actually be merged.

---

### Step 7 — Readiness report

Re-fetch CI against the post-push `HEAD` SHA (repeat the Step 2 CI check).
The final verdict is the thread-resolution state **and** this re-checked CI:

- **Green** — all threads resolved, CI green → report
  `gh pr merge <pr-url> --squash --match-head-commit <sha>`
- **CI pending / failing** — report plainly, do not claim ready
- **Threads outstanding** — report which ones and why, do not claim ready

---

### Output

Report: the final verdict and the SHA it was checked against, what was
resolved vs. surfaced, the merge one-liner (only if green), and a reminder
that after merging, closeout should land the execution record.
