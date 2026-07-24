---
id: execute
name: Execute Work Item to Closeout
description: Drive a work item from implementation through the LRH closeout chain, nearly autonomously
keyword: ":execute"
---

## Execute a Work Item to Closeout

Drive this work item through the full LRH lifecycle — implement, PR, review,
merge, closeout — running as autonomously as possible and stopping only when
something genuinely needs me.

**Two hard human gates. Do not cross either without my explicit in-session go:**

- **REVIEW GATE** — Wait until review comments have *actually landed* before
  responding to them (see Step 3).
- **MERGE GATE** — Never merge without my explicit approval in this session
  (see Step 6).

Throughout: if a major issue arises, an assumption is violated, a repository
convention is unclear, review comments cannot be resolved, or validation fails,
**stop and report — do not guess past it.**

---

### Step 1 — Implement

Run `/lrh-implement` for this work item. Follow its own plan-confirmation gate;
do not skip it. Respect `AGENTS.md`, `STYLE.md`, and `PROMPTS.md`, and keep any
`README.md` in affected directories current.

### Step 2 — Open and push the PR

Create the pull request and push the branch. Record the execution as
`in_progress` with the PR URL as the primary artifact (per `/lrh-implement` /
`PROMPTS.md`). State the PR URL and the prompt/execution ID prominently.

### Step 3 — Wait for review comments to ACTUALLY land

Do **not** proceed on an empty thread list. Automated reviewers post minutes
after the PR opens or is pushed, so a clean-looking thread list immediately
after pushing is **not** proof the review is clean. Wait until review activity
has actually landed — check back until comment threads have appeared and
settled — before treating the review as ready to address.

### Step 4 — Respond to review

Run `/lrh-review-response`, then `/lrh-confirm-fixes`.

### Step 5 — Verify every issue is resolved

If any fix is unapplied, any comment is unresolved, or any raised issue remains,
**STOP and report** with specifics. Do not proceed to merge.

### Step 6 — MERGE GATE (ask first)

Only when all review comments are resolved: before asking, **summarize the PR
for me** — what it accomplishes, and how it changed over the review cycle (which
comments prompted which fixes; or state plainly that review required no
changes). Then **ask me for explicit approval to merge.** Wait for a clear yes
in this session. Never merge on your own initiative. Once I approve, merge the PR.

### Step 7 — Closeout

Run `/lrh-closeout` with the session URL:

    <SESSION_URL — paste View > Copy URL>

### Step 8 — Land the execution record

Update the execution record for this prompt to `landed` and push that change to
`main`. Update only this prompt's record; do not touch unrelated execution
records.

Before pushing, append one CHAIN-NOTE line to this execution record's body
(under its Result section), and include the same line in your final report:

    CHAIN-NOTE: cycles=<N>; stops=<N>; gates=[<gates that fired>]; friction=<one phrase or `none`>; note="<free text, or omit>"

where cycles = number of review-response→confirm-fixes rounds it took
(1 = converged in a single pass), stops = how many stop-and-report
conditions fired this run, gates = which human gates actually fired (e.g.
merge), friction = the one mechanical/boilerplate/noise point or `none`.
One line only — if it grows past one line, trim it. The value is a greppable
signal (`lrh search executions "CHAIN-NOTE"`), not a retro.

### Step 9 — Memories and follow-ups

Review what happened and propose any memories worth saving. Then suggest the
next work item in this workstream, or other reasonable follow-ups.

---

### Output

When you reach the end (or stop early), report:

- what was accomplished and where (PR URL, merge status, execution record path)
- the prompt/execution ID used
- the CHAIN-NOTE line for this run
- anything that stopped you, and what you need from me
- proposed memories and suggested next steps

---

### Additional instructions for this run (optional)

Anything below the line is extra context or overrides for this run — for
example, the session URL to pass to `/lrh-closeout`, a specific work item,
branch name, or constraints. If empty, proceed with the defaults above.

----Additional Notes Follow—————————————————————
