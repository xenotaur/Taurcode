---
id: lrh-remains
name: LRH Work Remains
description: Report what work remains this session, grounded in actual tracked repo state
keyword: ":lrh-remains"
---

## Claude.app Work-Remains Request

Answer "what work remains?" for the current session, grounded in actual
tracked repo state (git, `gh pr`, `lrh snapshot current_focus`) rather than
conversational recall. This is strictly read-only with respect to the
target repository and its git state: never create, edit, or move any file
in it, never run `lrh prompt` or any git mutation command. There is no
offer-and-write step — this ends at the report, unlike this prompt set's
action-oriented siblings (`:lrh-closeout`, `:lrh-review-response`).

This step benefits from LRH being installed, but do not install it as part
of running this prompt — installing a package is itself a write, and this
prompt's read-only guarantee should hold without exception. If `lrh` is not
on PATH, report it as unavailable and rely on the direct file-read
fallbacks each category below documents, rather than attempting
`pipx install lrh`.

No argument is required.

---

### Step 1 — Summarize session accomplishments

Review this session's actual transcript. In one paragraph, state what was
accomplished and what prompted it — grounded in what actually happened this
session, not a restatement of stated plans that weren't carried out.

---

### Step 2 — Ground each of the 18 checklist categories

Report against this fixed 18-item checklist, in order. Do not paraphrase,
reorder, merge, or drop items — report each one explicitly, including an
explicit "nothing outstanding" statement when a category has no findings. A
silently omitted category is indistinguishable from one that was checked
and found clean.

1. Incomplete work
2. Unanswered questions
3. Uncommitted files
4. Feature branches not pushed to main
5. Open PRs not yet merged
6. Unaddressed comments on PRs
7. Incomplete closeouts of PRs
8. Stray files
9. Stale branches
10. Unsaved memories
11. Untaken offers
12. Unaddressed issues
13. Control plane updates
14. Open work items
15. Unfinished workstreams
16. Documentation updates
17. Dogfooding of user-facing features
18. Other unfinished scope of work

For each category, run the command(s) listed below and report only what the
tool output actually shows — never substitute conversational recall for a
command that could answer the question. If a command isn't applicable (e.g.
`gh` unavailable, `lrh` not on PATH, not a git repository), say so explicitly
for that category rather than skipping it silently — fall back to the next
available signal listed for that category where one exists (e.g. direct
`project/` reads when `lrh snapshot` isn't available).

1. **Incomplete work** — no single command; review this session's own
   transcript against what was actually completed vs. stated as a plan.
2. **Unanswered questions** — review this session's transcript for questions
   posed (by either party) that were never resolved.
3. **Uncommitted files** — `git status --short`
4. **Feature branches not pushed to main** — `git status -sb` (current
   branch ahead/behind) catches the truly-unpushed-anywhere case. **This
   alone misses a branch that's fully pushed to its remote but not yet
   merged into the default branch** — `git log --branches --not --remotes`
   excludes any commit reachable from a remote-tracking ref, so a pushed
   branch's commits are excluded from that diff even though they're not
   merged. **Do not hard-code `main`** — the target repo's default branch
   may be `master`, `develop`, or something else; resolve it first, without
   hard-coding the remote name `origin` either:
   `gh repo view --json defaultBranchRef --jq .defaultBranchRef.name` (or,
   if `gh` is unavailable, resolve the remote name with `git remote` first —
   there is normally exactly one — then run
   `git symbolic-ref refs/remotes/<remote>/HEAD` against that name rather
   than assuming `origin`), then use that value in
   `git branch --no-merged <default-branch>` to find local branches not
   merged into it, regardless of push state. For each such branch, **don't
   just check whether a remote copy exists, and don't hard-code the remote
   name `origin`** — the repo's remote may be named differently, or a local
   branch may track a differently-named remote branch, in which case an
   `origin/<branch>` comparison fails or checks the wrong ref even when the
   branch is fully pushed, falsely reporting it as unpushed. Compare each
   branch against its own configured upstream instead:
   `git rev-parse <branch>` vs. `git rev-parse <branch>@{upstream}` (or
   `git rev-list --left-right --count <branch>@{upstream}...<branch>` for an
   ahead/behind count). If a branch has no configured upstream at all, treat
   that as its own distinct case (never pushed) rather than folding it into
   either the pushed or unpushed bucket silently.
5. **Open PRs not yet merged** — `gh pr list --author @me --state open`; for
   the current branch specifically, `gh pr view --json state,url`
6. **Unaddressed comments on PRs** — for the authoritative live count, pull
   the raw review-thread state for the PR (e.g. via the GitHub API or `gh`)
   and filter to unresolved threads.
7. **Incomplete closeouts of PRs** — start from `grep -rl '^status:
   in_progress' project/executions/ --include='*.md'` as a first pass, but
   **do not stop there** — that grep only sees what's checked out locally,
   and a record already `landed` in the local checkout can be `in_progress`
   on the remote default branch (or vice versa), or a record can exist
   remotely with no local copy at all. Enumerate the candidate set from the
   remote default branch too:
   `gh api repos/<owner>/<repo>/git/trees/<default-branch>?recursive=true --jq '.tree[] | select(.path | test("^project/executions/.*\\.md$")) | .path'`
   (resolve `<default-branch>` the same way category 4 does), and treat the
   union of the local grep's matches and this remote listing as the
   candidate set — not just the local grep's output. Then cross-check each
   candidate's `pr:` field against `gh pr view <pr-url> --json
   state,mergeCommit` — a `MERGED` PR with an `in_progress` record is an
   incomplete closeout.
   **Read this against fresh remote state, not a stale local checkout or a
   prior session's own closeout report** — a record correctly landed by an
   earlier PR can be silently reverted back to `in_progress` by a later,
   unrelated merge with no conflict and no warning. **Use a read-only
   remote query, never `git pull`** — this check never mutates git state,
   and `git pull` fetches *and* integrates changes into the current branch,
   modifying refs and the working tree, which is exactly the kind of side
   effect to avoid, especially at session end with local work present. Read
   the file's actual content on the remote default branch directly instead:
   `gh api -H "Accept: application/vnd.github.raw" repos/<owner>/<repo>/contents/<path>?ref=<default-branch>`
   (resolve `<default-branch>` the same way category 4 does) — **the
   Contents API returns JSON with the file body base64-encoded in
   `.content` by default**; the raw media-type header above returns the
   plain-text body directly instead — without it, the frontmatter `status:`
   value isn't actually readable from the response, defeating the point of
   this check. Before trusting a record's `status:` field, verify it this
   way rather than assuming a status reported earlier in this same session,
   or in a prior closeout, still holds.
8. **Stray files** — `git status --short` (untracked files outside expected
   output paths), and check the session's own scratchpad directory for
   leftover files that should have been cleaned up or delivered
9. **Stale branches** — `git branch -a --sort=-committerdate`, cross-checked
   against `gh pr list --state all --limit 1000 --json headRefName,state` —
   **`gh pr list` defaults to `--limit 30`**; in a repo with more than 30
   historical PRs, the default silently misses older merged/closed PRs,
   making their branches look like they have no associated PR and falsely
   reporting them as stale. Always pass an explicit high `--limit` (or
   paginate) here. **Check `gh api repos/<owner>/<repo> --jq
   .delete_branch_on_merge` first** — if `false`, a branch whose PR already
   merged or closed is the *expected*, low-value case, not a signal — do
   not flag it. The real signal is a branch with **no** merged or closed PR
   associated with it at all (never had one, or its PR is still open but
   the branch has had no commits in a long while) — that is what "stale"
   means here. Flagging every merged-but-undeleted branch buries the one
   abandoned in-progress branch under expected repo-wide noise.
10. **Unsaved memories** — manual eyeball of this session's actual decisions
    and corrected assumptions against `MEMORY.md`
    (`~/.claude/projects/<project-slug>/memory/MEMORY.md`, outside the
    target repo) — not an automated keyword search. Apply the standing bar
    for what's memory-worthy: surprising, non-obvious, durable, and not
    already captured by an existing memory or derivable by reading the
    current project state. **State the exact directory path checked** (the
    `<project-slug>` actually used), not just "memory was checked" — a
    forked or relocated session can end up writing to a *different*
    project-slug directory than its predecessor without either session
    noticing, silently splitting one session's memories across two
    namespaces.
11. **Untaken offers** — review this session's transcript for offers made
    ("want me to also...", "should I...") that were never confirmed or
    declined. **Also cross-check any prompt or skill invoked this session
    against its own mandatory-offer steps** — e.g. `:lrh-closeout`'s final
    step requires offering `/export`; if that ran this session, confirm the
    offer was actually made, not just that *some* offer was made somewhere.
    A freeform transcript scan alone can miss a specific offer another
    workflow's own checklist requires.
12. **Unaddressed issues** — `gh issue list --assignee @me --state open` if
    the repo uses GitHub issues; otherwise note that no issue tracker is in
    use for this check
13. **Control plane updates** — `lrh validate` (report errors and warnings
    verbatim, don't summarize away a warning)
14. **Open work items** — **always inspect session-touched work-item files
    directly**: `grep -l '^status: proposed' project/work_items/proposed/*.md`
    and `grep -l '^status: active' project/work_items/active/*.md`, scoped
    to items touched or created this session. Do not rely on
    `lrh snapshot current_focus --stdout` for this, even when `lrh` is
    installed — its "Relevant Work Items" section filters to work items
    whose `related_focus` list contains the current focus id, and only
    falls back to "include all" if *zero* work items repo-wide match that
    focus id. A session-touched WI with an unrelated or empty
    `related_focus` can be silently excluded from that output while other,
    unrelated WIs still satisfy the fallback condition —
    `lrh snapshot` is a useful cross-check, not a substitute for reading
    the files directly.
15. **Unfinished workstreams** — **always** read
    `project/workstreams/active/*.md` frontmatter (`work_items:`,
    `exit_criteria:`) directly and cross-check each listed WI's status. Do
    not rely on `lrh snapshot current_focus --stdout` for this even when
    `lrh` is installed — its `current_focus` scope has no `## Workstreams`
    section at all (that section only exists in the separate `work_item`
    scope, a different command). Calling
    `lrh snapshot current_focus --stdout` for workstream data will always
    return nothing on this point, regardless of whether `lrh` is installed
    or what state the workstreams are actually in — it is not a
    fallback-only limitation.
16. **Documentation updates** — check whether files this session touched
    have corresponding doc references (e.g. `CLAUDE.md`, a skill or
    prompt's own index entry, a README) that still need updating to
    reflect the change
17. **Dogfooding of user-facing features** — if this session built or
    changed a user-facing feature (a skill, a CLI command, a prompt, a UI),
    check whether it was actually invoked/exercised this session or only
    written. **Also check the inverse case:** did this session discover
    mid-session that a relevant skill or prompt *already existed*, then
    manually re-derive its documented pattern by hand (e.g. raw tool calls
    replicating what it would have done) instead of actually invoking it?
    Look for a documented pattern appearing in the transcript without a
    corresponding invocation of it.
18. **Other unfinished scope of work** — catch-all; anything raised in
    conversation that doesn't fit categories 1–17 but is still open

---

### Step 3 — Flag cross-session ownership candidates

For any branch, PR, or work item surfaced in Step 2 that this session's own
transcript never touched, do not report it as this session's own unfinished
work and do not silently exclude it either — surface it separately and ask
the user to confirm whether it belongs to this session or is already owned
by a different one.

No single signal is reliable alone — cross-reference multiple sources before
concluding an item is (or isn't) already claimed:

- The candidate WI's own `assigned_agents:`/`blocked:` frontmatter fields
- `gh pr list --state open`, checked by **actual file list**
  (`gh pr view <n> --json files`), not just by title — two open PRs with
  generic-sounding titles can still turn out to overlap or not overlap only
  once their touched files are compared
- `git worktree list` across all active local worktrees, to see if another
  worktree already has the candidate's branch checked out
- Remote branch names via `gh api repos/<owner>/<repo>/branches`, in case a
  branch exists remotely that no local worktree has fetched yet
- `project/focus/current_focus.md` and
  `project/focus/development_agenda.md` for a stated current owner or
  priority

Report which of these were actually checked, not just the conclusion.

---

### Step 4 — State the next step

If Step 2 surfaced any category with real outstanding work, state the single
most logical next step to address it. If everything is clean, say so
plainly — do not manufacture a next step where none exists.

---

### Step 5 — Report

Present the Step 1 summary, the full per-category results from Step 2 (all
18 items, including explicit "nothing outstanding" lines), the Step 3
ownership flags (if any), and the Step 4 next step. This is the end of the
job — do not offer to act on any finding; if the user wants to act on one,
that is a separate, explicit invocation of whichever prompt or skill fits.
No file is written, no `lrh prompt` or git mutation command is run.
