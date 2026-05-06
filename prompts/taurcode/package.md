---
id: package
name: Package
description: Imported from Espanso
keyword: ":package"
---

Provide a package of prompts

Please provide a package of structured prompts to generate
a sequence of PRs to implement your proposed work item.

For each prompt, generate a prompt ID using the conventions
in `PROMPTS.md`. Include that prompt ID at the top of each
generated prompt.

After each PR is generated, the agent should create an
execution record for the prompt using
`scripts/prompts/record-execution`, following the
conventions in `PROMPTS.md` and `project/executions/README.md`.

In each prompt, ask the agent to:

- follow AGENTS.md
- follow STYLE.md for consistency
- follow PROMPTS.md for prompt IDs, execution records, and rerun handling
- update any README.md’s in affected folders
- add or update an execution record for the prompt (using AD_HOC if no work item applies)
- check for prior execution records for the same prompt ID and apply soft idempotence rules before proceeding

Target the prompts to Codex Cloud. Please provide a downloadable zip file.
Also provide the entire text of each prompt as a separate copy-and-paste
blocks inline within the chat. Please present the downloadable zip file
first, because prompts in copy-and-paste blocks sometimes interfere with
the rendering of the chat. The copy-and-paste block should be a 1-1 copy
of each prompt; NEVER present a copy and paste block that does not exactly
correspond to the exact contents of a downloadable file.
