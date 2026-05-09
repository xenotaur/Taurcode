---
id: prompt
name: Prompt
description: Provide a structured prompt to generate a PR to accomplish this task
keyword: ":prompt"
---

Provide a structured prompt to generate a PR to accomplish this task:

Before writing the prompt, generate a prompt ID using the conventions
in `PROMPTS.md`. Include that prompt ID at the top of the generated
prompt.

After the PR is generated, the agent should create an execution record
for the prompt using `scripts/prompts/record-execution`, following the
conventions in `PROMPTS.md` and `project/executions/README.md`.

In that prompt, ask the agent to:

- follow AGENTS.md
- follow STYLE.md for consistency
- follow PROMPTS.md for prompt IDs, execution records, and rerun handling
- update any README.md’s in affected folders
- add or update an execution record for the prompt (using AD_HOC if no work item applies)
- check for prior execution records for the same prompt ID and apply soft idempotence rules before proceeding

Keep the workflow lightweight: execution records are expected for
meaningful prompt-driven PRs, but should not block small or obvious
changes. Do not update execution records unrelated to this task.

Target the prompt to Codex Cloud and provide it as both a downloadable
file AND a copy-and-paste block inline within the chat. Please present
the downloadable file first, as prompts in copy-and-paste blocks
sometimes interfere with the rendering of the chat. The copy-and-paste
block should be a 1-1 copy of the prompt; NEVER present a copy and paste
block that does not exactly correspond to the exact contents of the
downloadable file.
