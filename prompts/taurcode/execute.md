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

Run this nearly autonomously. Responding to review is autonomous — you do **not**
need my approval to apply review fixes. **One hard human gate** and one timing
rule bound that autonomy:

- **MERGE GATE (human approval)** — Never merge without my explicit in-session
  go (see Step 6). This is the one point that always stops for me.
- **REVIEW-LANDED rule** — Do not act on review until it has *actually landed*;
  an empty thread list right after pushing is not a clean review (see Step 3).

Throughout: if a major issue arises, an assumption is violated, a repository
convention is unclear, review comments cannot be resolved, or validation fails,
**stop and report — do not guess past it.**

---

### Step 1 — Implement

Run `/lrh-implement` for this work item. Follow its own plan-confirmation gate;
do not skip it. Respect `AGENTS.md`, `STYLE.md`, and `PROMPTS.md`, and keep any
`README.md` in affected directories current.

### Step 2 — Confirm the PR and execution record

`/lrh-implement` already opens the pull request, pushes the branch, and records
the execution as `in_progress` (see `prompts/taurcode/implement.md`, Steps 7–8).
Do **not** open a second PR. Verify those outputs exist, then state the PR URL
and the prompt/execution ID prominently. If `/lrh-implement` stopped before
opening a PR (for example at its plan gate), stop and report rather than opening
one here.

### Step 3 — Wait for review to ACTUALLY land

Automated reviewers post minutes after the PR opens or is pushed, so an empty
thread list immediately after pushing is **not** proof of a clean review — it
usually just means the review has not run yet. Wait until the review has
actually completed (its comments and checks have reported back), then:

- completed **with** comments → address them (Step 4);
- completed **with no findings** → that is a clean review; proceed to the merge
  gate (Step 6).

If the review has not reported after a reasonable wait, stop and ask me how to
proceed rather than looping.

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

### Step 8 — Land the execution record (find-or-backfill)

Locate this PR's execution record — first any created by an earlier step
(`/lrh-implement`, or `/lrh-review-response` / `/lrh-confirm-fixes` on a
reviewed PR), searching by the PR's `pr:` URL. Then:

- **If a record exists:** set its `status` to `landed` and push to `main`.
- **If no record exists** (a PR authored outside the skill chain that also drew
  no review activity): create an honest BACKFILL `AD_HOC` record from available
  PR data — `pr` (this PR's URL), `commit`, `status`, `agent`, and
  `instruction_source` describing the PR/session — via `lrh prompt label` +
  `lrh prompt record-execution`. Mark it in the body as a post-hoc backfill
  reconstructed at land time, **not** a fabricated instruction-phase record.
  Surface the reconstructed record to me before pushing — never write it
  silently — then set `status: landed` and push.

Update only this PR's record; do not touch unrelated execution records.

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
