PROMPT(AD_HOC:GENERATE_PR_FOR_FIX_WITH_EXECUTION_RECORD)[2026-04-30T00:22:33+00:00]

# Codex Cloud PR Prompt

## Objective
Implement the requested fix and open a pull request with a minimal, review-friendly diff.

## Required policy and repository guidance
1. Follow `AGENTS.md` instructions applicable to every file you touch.
2. Follow `STYLE.md` for coding, testing, and change-scope consistency.
3. Follow `PROMPTS.md` for prompt IDs, execution records, rerun handling, and soft idempotence behavior.

## Prompt metadata
- Prompt ID: `PROMPT(AD_HOC:GENERATE_PR_FOR_FIX_WITH_EXECUTION_RECORD)[2026-04-30T00:22:33+00:00]`
- Work item linkage: `AD_HOC` (use this unless a concrete work item is explicitly identified during implementation).

## Workflow
1. Read context and constraints from repository docs (`AGENTS.md`, `STYLE.md`, `PROMPTS.md`, and any nested instructions in scope).
2. Before making changes, check for prior execution records for this exact prompt ID under `project/executions/`.
3. Apply soft idempotence rules from `PROMPTS.md`:
   - If status is `landed` or `in_progress`, stop and report unless this run is explicitly a rerun.
   - If status is `failed`, `reverted`, or `superseded`, summarize prior run and continue only as rerun/follow-up.
   - If status is ambiguous, stop and report ambiguity.
4. Implement only the requested fix with minimal unrelated churn.
5. Add/update tests as needed for behavior changes.
6. Update any `README.md` files in folders you modify when behavior, usage, or structure changes.
7. Run relevant checks (at minimum: `scripts/develop` before claiming operability, and `scripts/test` before claiming tests pass; include lint/format checks when code changes warrant).
8. Create a PR with a clear summary, validation notes, and any follow-ups.
9. After the PR is generated, create or update the execution record with `scripts/prompts/record-execution`, following `PROMPTS.md` and `project/executions/README.md`.
10. Keep this lightweight: execution records are expected for meaningful prompt-driven PRs, but should not block small or obvious changes. Do not modify unrelated execution records.

## Execution record requirements
After PR creation, run `scripts/prompts/record-execution` and include:
- prompt ID (exactly as above)
- related work item (`AD_HOC` if no work item applies)
- concise summary of implemented changes
- result/status (`planned`, `in_progress`, `landed`, `failed`, `reverted`, or `superseded` as appropriate)
- validation commands and outcomes
- links/references to PR and commit(s) if available
- rerun linkage (`rerun_of`) when applicable

## Deliverables
- Code + tests for the fix
- Updated relevant `README.md` files in affected folders
- Pull request
- Execution record created via `scripts/prompts/record-execution`

## Constraints
- Keep changes focused and conservative.
- Do not perform unrelated refactors.
- Preserve repository conventions and deterministic behavior.
