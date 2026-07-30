---
id: lrh-closeout
name: LRH Closeout
description: Land execution records, resolve work items, and close workstreams after a PR merges
keyword: ":lrh-closeout"
---


## Claude.app Closeout Request

Complete the post-execution closeout for a merged pull request: update
execution records to `landed`, resolve the work item if the PR implemented
one, and close the governing workstream or adopt the governing proposal only
when their own conditions are actually met. Assess all artifact states
before touching any files.

This step requires LRH. If `lrh` is not on PATH, install it once, globally:

    pipx install lrh

LRH is not yet published to PyPI (tracked by `PROP-TAG-PUSH-PYPI-PUBLISHING`
in the LRH repo); until it is, `pipx install <path-to-local-lrh-checkout>`
or a locally built wheel installs the same `lrh` console script.

---

### Step 1 — Verify PR state

    gh pr view <pr-url> --json state,mergeCommit --jq '{state: .state, commit: .mergeCommit.oid}'

If `state` is not `MERGED`, **abort** — do not proceed past this point.

---

### Step 2 — Assess state, build a closeout plan

Find every execution record linked to this PR:

    grep -rl "^pr: <pr-url>" project/executions/ --include='*.md'

A PR may have several: one primary (implementation or planning) plus
`_REVIEW`/`_CONFIRM` side records. For each, check `status:` —
`in_progress` → update to `landed`; `landed` → skip.

If the PR implemented a work item (not merely created one — see the WI's
own file for whether this PR's scope was the implementation), find it and
check its bucket. If in `proposed/`, resolve it: `status: resolved`, a
`resolution:` one-liner (confirmed with the user), moved to `resolved/`.
**A PR that only created a work-item planning artifact does not resolve
that item** — it stays `proposed` until a later implementation PR.

If a related workstream exists, check whether every listed work item is now
resolved (on disk or planned in this same closeout). If so, also check its
`exit_criteria:` — read them aloud and require explicit human confirmation
before closing the workstream. If any work item is unresolved, or exit
criteria aren't confirmed, skip workstream closure and say why.

Only offer to adopt a governing design proposal if its workstream is
closing in this same pass.

Present the full plan as a table before touching anything.

---

### Step 3 — Resolve session transcript

Attempt `echo $CLAUDE_CODE_HOST_SESSION_ID`, or ask the user for the browser
URL (`claude.ai/.../local_<uuid>` — strip the `local_` prefix). If neither
resolves, use `session_transcript: pending` and remind the user to update it
later.

---

### Step 4 — Confirm gate (human gate)

Show the user the full plan from Step 2 (PR state, each record's intended
action, WI/WS/proposal actions or explicit skip-reasons, the resolution
text to be written, workstream exit criteria requiring a yes/no). **Wait for
explicit confirmation before touching any files.**

---

### Step 5 — Execute confirmed actions

    lrh prompt update-execution \
      --execution-id <id> \
      --status landed \
      --pr <pr-url> \
      --commit <merge-commit-sha> \
      --session-transcript <resolved-value> \
      --project-root .

For a resolving work item: edit frontmatter (`status: resolved`,
`resolution:`), then `mv` (never `cp`) from `proposed/` to `resolved/`. For
a closing workstream: `stage: closed`, `status: resolved`, then `mv` to
`resolved/`. For an adopting proposal: `status: adopted`,
`implementation_status: implemented`, `implemented_by:`, then `mv` the
directory to `adopted/`.

---

### Step 6 — Validate

    lrh validate

Stop and report any errors before committing.

---

### Step 7 — Session reflection

Review this session's actual decisions and corrected assumptions. Draft 0-3
candidate memories worth saving (durable, non-obvious, not already
captured) — or say explicitly that nothing stands out. Ask the user before
writing anything.

---

### Step 8 — Report and commit

Commit all closeout changes directly to `main` (not a feature branch).
Report: each action taken, the commit SHA, whether memory was written, and
any offer that was made but not taken (with a one-line reason).
