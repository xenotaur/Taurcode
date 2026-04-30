---
id: codex-cloud-pr-template
name: Codex Cloud PR Prompt Template
description: Reusable prompt template for implementing a fix, opening a PR, and recording execution.
keyword: ":tc-codex-pr-template"
---

PROMPT(<WORK_ITEM_OR_AD_HOC>:<SLUG_UPPER_UNDERSCORE>)[<ISO8601_TIMESTAMP_WITH_OFFSET>]

# Codex Cloud PR Prompt

## Objective
Implement the requested fix and open a pull request with a minimal, review-friendly diff.

## Required policy and repository guidance
1. Follow `AGENTS.md` instructions applicable to every file you touch.
2. Follow `STYLE.md` for coding, testing, and change-scope consistency.
3. Follow `PROMPTS.md` for prompt IDs, execution records, rerun handling, and soft idempotence behavior.

## Prompt metadata
- Generate a fresh prompt ID for each meaningful run using the `PROMPTS.md` format:
  - `PROMPT(<WORK_ITEM_OR_AD_HOC>:<SLUG_UPPER_UNDERSCORE>)[<ISO8601_TIMESTAMP_WITH_OFFSET>]`
- If no specific work item applies, use `AD_HOC`.
- Replace all placeholders before execution.

## Workflow
1. Read context and constraints from repository docs (`AGENTS.md`, `STYLE.md`, `PROMPTS.md`, and any nested instructions in scope).
2. Before making changes, check for prior execution records for the exact generated prompt ID under `project/executions/`.
3. Apply soft idempotence rules from `PROMPTS.md`:
   - If status is `landed` or `in_progress`, stop and report unless this run is explicitly a rerun.
   - If status is `failed`, `reverted`, or `superseded`, summarize prior run and continue only as rerun/follow-up.
   - If status is ambiguous, stop and report ambiguity.
4. Implement only the requested fix with minimal unrelated churn.
5. Add/update tests as needed for behavior changes.
6. Update any `README.md` files in folders you modify when behavior, usage, or structure changes.
7. Run relevant checks (at minimum: `scripts/develop` before claiming operability, and `scripts/test` before claiming tests pass; include lint/format checks when code changes warrant).
8. Create a PR with a clear summary, validation notes, and any follow-ups.
9. After the PR is generated, create an execution record with `scripts/prompts/record-execution`, following `PROMPTS.md` and `project/executions/README.md`.
10. Keep this lightweight: execution records are expected for meaningful prompt-driven PRs, but should not block small or obvious changes. Do not modify unrelated execution records.

## Execution record requirements
After PR creation, run `scripts/prompts/record-execution` to create the execution record, and ensure the record captures:
- prompt ID (exactly as generated for this run)
- concise summary of implemented changes
- result/status (`planned`, `in_progress`, `landed`, `failed`, `reverted`, or `superseded` as appropriate)
- validation commands and outcomes

If additional metadata is needed (for example work-item linkage such as `AD_HOC`, PR/commit references, or rerun linkage), add it manually only if the current execution-record format in this repository supports it. Do not assume `scripts/prompts/record-execution` will populate unsupported fields, and note any manual follow-up needed in your handoff.

## Deliverables
- Code + tests for the fix
- Updated relevant `README.md` files in affected folders
- Pull request
- Execution record created via `scripts/prompts/record-execution`

## Constraints
- Keep changes focused and conservative.
- Do not perform unrelated refactors.
- Preserve repository conventions and deterministic behavior.
