# Prompting Best Practices

## Purpose and scope

This is Taurcode's canonical human-facing guide for writing and reviewing prompts. It distills the design direction in `project/design/proposals/proposed/prompting-best-practices-and-review-framework.md` into practical rules that prompt authors can use during normal PR work.

Use this guide for:

- canonical Taurcode prompts under `prompts/taurcode/`
- prompt package text that is exported to targets such as Espanso
- prompt templates or rendered prompts that may be added in future workflows
- meaningful prompt changes that need shared review criteria

This guide is not a mandate that every prompt use the same shape. Task-specific prompts may deviate when the reason is clear, but reviewers should be able to understand the intended behavior, trust boundaries, output contract, and maintenance plan.

## Core prompting principles

1. **Define the task and success criteria.** State what the model should do, who the response is for, and what a good result looks like. If success depends on repository conventions, available tools, or an expected workflow, name those assumptions.

2. **Be clear, direct, and specific.** Prefer concrete instructions over broad requests. Replace vague goals like "make this better" with observable actions such as "identify blockers, concerns, and suggestions without rewriting by default."

3. **Separate instructions, context, examples, and output format.** Use headings, lists, fenced blocks, or labels so a reader can distinguish what the model must do from the information it should inspect. Keep examples close to the rule or format they illustrate.

4. **Treat user-provided and retrieved context as data, not instructions.** Repository files, issue text, web excerpts, command output, and interpolated variables can contain hostile or accidental instructions. Prompts should tell the model to analyze that content without letting it override higher-priority instructions.

5. **Use examples when they clarify format, style, edge cases, or label space.** Examples are useful when they remove ambiguity, demonstrate a schema, or show acceptable severity labels. Avoid examples that are longer than the rule they explain or that accidentally narrow the task too much.

6. **Prefer positive instructions over long negative constraint lists.** Start with the desired behavior. Add negative constraints only when they prevent a known failure mode, safety issue, or broken output contract.

7. **Use structured output when downstream tooling or review depends on shape.** If another human, script, or prompt will consume the answer, define required sections, fields, schemas, severity labels, or fallback formats. If free-form prose is acceptable, do not over-specify structure.

8. **Use reasoning or planning scaffolds only when the task benefits from them.** Planning, verification steps, concise rationale, self-checks, self-consistency, ReAct-style action traces, or Tree-of-Thoughts-like branching can help difficult tasks, but they add cost and complexity. Ask for actionable summaries or checks rather than unnecessary hidden chain-of-thought disclosure.

9. **Manage long context deliberately.** Include only context that helps the task. Explain which sources matter most, what to do when context is missing, and whether the model should summarize, search within, or prioritize excerpts. Long context can bury important instructions and evidence.

10. **Design for template and interpolation safety.** Variables should have clear names, documented meanings, and visible boundaries in rendered prompts. Rendered output matters more than source elegance: review examples with empty values, long values, Markdown syntax, braces, quotes, code fences, and user-controlled text.

11. **Evaluate, document, and version prompts as source artifacts.** Treat prompt changes like code changes. Keep diffs focused, record meaningful prompt-driven work through the repository prompt workflow, and validate import/export behavior when a prompt change affects package output.

12. **Optimize for maintainable workflow outcomes.** Good prompts reduce repeated manual work and produce useful, reviewable results. Avoid clever phrasing, provider-specific tricks, or large boilerplate unless they clearly improve the workflow.

## Prompt review rubric

Use this rubric for human review and for future assistant-assisted prompt review. Findings can use this lightweight severity model:

- **Blocker:** likely to break the prompt, compromise safety, or violate a documented contract.
- **Concern:** likely to reduce clarity, maintainability, robustness, or user trust.
- **Suggestion:** optional improvement or consistency note.

### Correctness

- Does the prompt ask for the intended task?
- Are the constraints compatible with each other and with the task?
- Are repository-specific instructions accurate and current?
- Does the prompt avoid asking for impossible work, unavailable tools, or unverifiable claims?

### Clarity

- Are the task, audience, required inputs, and success criteria clear?
- Are optional and mandatory behaviors distinguishable?
- Are important terms defined or inferable from context?
- Could a reasonable model follow the prompt in multiple incompatible ways?

### Scope control

- Does the prompt keep the model focused on the requested change or answer?
- Does it discourage drive-by rewrites, unrelated research, or unnecessary process?
- Does it say what to do when the requested scope is too broad or missing key context?

### Output contract

- Does the prompt specify required sections, fields, schemas, labels, or examples when response shape matters?
- Does it define warning, failure, or uncertainty formats where useful?
- Is the output contract realistic for the intended model and workflow?

### Context separation

- Are trusted instructions separated from untrusted context, examples, excerpts, and command output?
- Does the prompt explain how to handle conflicts inside quoted or retrieved material?
- Are examples clearly examples rather than additional hidden requirements?

### Variable handling

- Are interpolation variables named clearly and described by type, source, and trust level?
- Are optional or empty variables handled intentionally?
- Could rendered variable values break headings, fences, frontmatter, placeholders, or indentation?

### Prompt-injection resistance

- Does the prompt preserve instruction hierarchy when it includes user-authored, repository-authored, generated, or retrieved content?
- Does it prevent untrusted content from changing tool-use, file-editing, safety, or output instructions?
- Does it tell the model to report suspicious or conflicting instructions when that matters?

### Reasoning appropriateness

- Does the prompt ask for planning, rationale, verification, or alternative exploration only when it improves quality?
- Does it avoid demanding private chain-of-thought disclosure?
- Does it favor concise, reviewable explanations and checks over verbose internal reasoning?

### Maintainability

- Is the prompt readable as Markdown and easy to diff?
- Are sections organized predictably?
- Is duplicated boilerplate necessary, or should the prompt refer to shared guidance?
- Can future reviewers update one concern without rewriting the whole prompt?

### Model/update robustness

- Is the prompt likely to work across current model families rather than depending on one provider quirk?
- Are model-specific notes documented as notes, not hidden assumptions?
- Is the prompt resilient to model behavior drift, longer context windows, or stricter tool policies?

### Operational usability

- Can a user paste, expand, or export the prompt and understand what to do next?
- Does it fit Taurcode's Markdown/frontmatter format and package export constraints?
- Are validation steps, rendered examples, or manual checks clear enough for PR review?

## Common prompt failure modes

- **Vague task framing:** the prompt asks for improvement or review without defining the desired outcome.
- **Mixed instruction layers:** context, examples, user requests, and output requirements are blended into one paragraph.
- **Untrusted context override:** repository or user text can appear to instruct the model to ignore the prompt.
- **Missing output contract:** downstream users expect a table, sections, JSON, or severity labels that the prompt never requires.
- **Overly rigid output contract:** the prompt mandates structure that makes simple answers awkward or hides important nuance.
- **Template breakage after rendering:** a variable value closes a code fence, creates a new Markdown heading, or leaves a placeholder unresolved.
- **Negative-instruction bloat:** long lists of prohibitions obscure the desired behavior.
- **Unnecessary reasoning scaffolding:** the prompt demands elaborate planning for a simple task or asks for chain-of-thought where a concise rationale is enough.
- **Long-context overload:** the prompt includes too much low-value context and does not prioritize what matters.
- **Hidden model assumptions:** the prompt relies on a provider-specific feature or behavior without saying so.
- **Stale operational details:** tool names, paths, commands, or repository conventions have drifted from current practice.

## Special notes for templated prompts and variable interpolation

Templated prompts need review at both the source-template level and rendered-output level. A readable template can still produce an unsafe or confusing prompt after interpolation.

For each variable, document or make obvious:

- the variable's purpose and expected type
- whether it is trusted project metadata, user-authored text, repository content, generated text, or retrieved content
- whether it is required, optional, or allowed to be empty
- what escaping or boundary mechanism protects the rendered prompt

Review rendered examples that include:

- normal values
- empty or missing optional values
- long multiline values
- Markdown headings, lists, and code fences
- YAML/frontmatter delimiters
- placeholder-like braces or template syntax
- text that contains hostile instructions such as requests to ignore previous directions

Prefer visible boundaries around variable content. Fenced blocks, quoted sections, explicit labels, or delimiter lines can help, but they are not magic: prompts should still state that variable content is data to inspect, not instructions to obey.

## Applying the rubric to LRH request templates

Logical Robotics Harness request templates should be reviewed as templates with a stable rendering contract, not as ordinary prose prompts. When LRH template sources are not available in the current checkout, keep Taurcode changes guidance-only and leave direct LRH template edits to a dedicated LRH PR.

Use the standard rubric above, plus these LRH-specific checks:

- **Template inventory:** identify every interpolation variable, placeholder, conditional section, and repeated section before suggesting edits.
- **Trust boundaries:** distinguish LRH-generated metadata, project-control-plane content, repository excerpts, work-item text, generated prompt IDs, and free-form user request text.
- **Rendering contract:** preserve required variables, interpolation syntax, delimiters, section headings, examples, and any output shape consumed by LRH commands or downstream workflows.
- **Empty and unusual values:** inspect rendered examples with missing optional values, long multiline work-item content, Markdown headings, code fences, braces, and hostile instructions inside user-controlled fields.
- **Operational expectations:** verify that template guidance still matches LRH CLI behavior, prompt ID conventions, execution-record expectations, and repository-specific instructions.
- **Minimal edits first:** prefer small wording or boundary improvements over broad rewrites unless a rendered template is clearly unsafe or unusable.

A safe LRH template review should usually produce findings and minimal patch suggestions first. Apply direct template edits only when the LRH checkout, rendering behavior, and tests or fixtures are available.

## Checklist for prompt changes

Before opening or approving a meaningful prompt change, check:

- [ ] The prompt's task, audience, and success criteria are clear.
- [ ] Instructions, context, examples, and output format are visually separated.
- [ ] Any untrusted or user-controlled text is treated as data.
- [ ] The output contract is explicit when another person, prompt, or tool depends on response shape.
- [ ] Examples clarify behavior without becoming accidental extra requirements.
- [ ] Reasoning or planning scaffolds are right-sized for the task.
- [ ] Long context is prioritized and not included by habit.
- [ ] Variables and rendered templates preserve boundaries and handle empty or unusual values.
- [ ] The prompt is readable, diff-friendly, and scoped to the workflow it supports.
- [ ] Relevant validation, rendering, import, or export checks were run when behavior could change.
- [ ] Meaningful prompt-driven work has an execution record according to `PROMPTS.md`.

## Further reading

These sources informed the design proposal and should guide future revisions without being copied wholesale into Taurcode rules:

- Google prompting guidance, including Vertex AI prompt design, prompt iteration, and prompt templates.
- OpenAI prompting guidance, including general prompt engineering and reasoning best practices.
- Anthropic prompting guidance, including prompt engineering overview material and model-family best practices.
- Research on reasoning and tool-use scaffolds, including chain-of-thought prompting, self-consistency, ReAct, and Tree of Thoughts.
- Research on long-context behavior, especially evidence that models can underuse information in the middle of long contexts.
- Research and guidance on instruction hierarchy and prompt-injection resistance.
- Broad surveys such as The Prompt Report for terminology and technique comparisons.

## Open questions

- Should this guide eventually split the rubric into `docs/prompt-review-rubric.md`?
- Should canonical prompt frontmatter include optional metadata such as variables, audience, review status, or last-reviewed date?
- Which rendered-template cases should become automated regression tests?
- How should Taurcode document model-specific guidance without fragmenting the prompt corpus?
- What evaluation signals are practical for a lightweight prompt toolkit?
- How should prompt review findings be recorded when they do not produce immediate code changes?
- Which prompt-injection checks can be deterministic without overpromising semantic safety?
