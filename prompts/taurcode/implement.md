---
id: implement
name: Claude Implement Design
description: Claude Implements Design in Target Repository
keyword: ":implement"
---


## Claude.app Implementation Request

Implement the design you just restated as a pull request in the target
repository. The restated design is the authoritative specification —
do not re-derive or re-analyze it.

---

### Step 1 — Label this execution

Generate a prompt ID that reflects the design topic. Choose a slug that
names what you are implementing (e.g., `review-response-protocol-fix`).

Preferred (when LRH is installed):

    lrh prompt label --slug <descriptive-slug>

Fallback:

    scripts/prompts/label-prompt --slug <descriptive-slug>

**State the generated prompt ID prominently at the top of your response.**
This is the execution ID for this session. You will use it in the PR and
the execution record.

---

### Step 2 — Idempotence check

    lrh prompt check-execution --prompt-id "<prompt-id>" --project-root .

If a prior `landed` or `in_progress` record exists, stop and report.
Do not proceed unless this is an explicit rerun.

---

### Step 3 — Confirm plan (human gate)

Before creating any branch or touching any files, show the user:

- A one-paragraph summary of what will be implemented, based on the
  restated design at the top of this prompt
- The prompt ID minted in Step 1
- The branch name to be created (see Step 4)
- A high-level list of expected file changes
- The validation commands that will be run (see Step 6)

**Wait for explicit confirmation.** If the user redirects, adjust and
re-show. Do not proceed past this gate without approval — a restated
design is not the same as an approved plan, and this step is what
prevents an under-specified restatement from turning into an unreviewed
branch and PR.

---

### Step 4 — Branch

Confirm you are on a feature branch, not `main`. Create one if needed,
following the repository's branch naming convention:

    git checkout -b <branch-name>

---

### Step 5 — Implement

Follow the restated design exactly. Respect:

- `AGENTS.md` — repository conventions and task guidance
- `STYLE.md` — code and documentation style
- `PROMPTS.md` — prompt IDs, execution records, and rerun handling

Keep any `README.md` files in affected directories current.
Do not broaden scope, refactor, or clean up beyond what the design specifies.

---

### Step 6 — Validate

Identify and run the repository's canonical validation commands.
When available, use them in this order:

    scripts/version tools        # verify tool versions first, if present
    scripts/format --check --diff
    scripts/lint
    scripts/test

If any script is absent, identify the equivalent from `README.md` or CI
configuration. Report which commands were unavailable and what equivalent
was used instead. If a command fails with a missing-install or
missing-import error, report it as a missing environment dependency —
not a code regression — and stop.

---

### Step 7 — PR

Create a pull request. Include in the PR body:
- the prompt ID generated in Step 1
- a brief summary of what changed
- what was explicitly left out of scope

---

### Step 8 — Execution record

After the PR is created, record the execution. Preferred (when LRH is
installed):

    lrh prompt record-execution \
      --prompt-id "<prompt-id>" \
      --slug <slug> \
      --status landed \
      --project-root .

Fallback:

    scripts/prompts/record-execution \
      --prompt-id "<prompt-id>" \
      --slug <slug> \
      --status landed

Include the PR URL as the primary artifact. Record only for this prompt —
do not modify execution records for other prompts.

---

### Output

When complete, report:
- the prompt ID used
- the PR URL
- what was implemented
- what was skipped and why
- the execution record path
