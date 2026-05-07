# Prompting Best Practices and Prompt Review Framework Proposal

## Status

Proposed.

## Summary

This proposal defines a lightweight design direction for improving Taurcode prompt quality through a shared prompting guidance document, a reusable prompt review rubric, reusable prompt-review prompts, and optional future automation hooks.

The framework should help Taurcode keep its prompt corpus readable, reviewable, safe, and maintainable without turning prompt authoring into a heavyweight governance process. It is intentionally architectural and implementation-oriented, but it should be rolled out in small PRs so the project can learn from real prompt reviews before standardizing too much.

## Context

Taurcode stores canonical prompts as Markdown files with frontmatter under `prompts/taurcode/` and exports those prompts to target packages such as Espanso. The prompt corpus is therefore both user-facing product content and source code-like project material: small prompt changes can alter model behavior, formatting, safety posture, and downstream generated packages.

The current canonical prompt format gives Taurcode a stable storage boundary. The next maintainability step is to define how prompts should be written, reviewed, and iterated.

## Problem Statement

Prompt quality and maintainability matter because Taurcode prompts are intended to be reused across repositories, agents, and coding workflows. A vague or inconsistent prompt can produce noisy output once; a vague or inconsistent canonical prompt can produce noisy output every time it is expanded.

Ad hoc prompt growth creates several problems:

- **Model drift:** prompts that worked for one model or model generation may become brittle as model behavior changes.
- **Formatting inconsistency:** prompts that mix instructions, examples, context, and output requirements without clear boundaries are harder for humans and models to interpret.
- **Hidden assumptions:** prompts often depend on unstated repository layout, tool availability, safety posture, or expected response shape.
- **Prompt injection risk:** prompts that include user-supplied or repository-supplied content without clear trust boundaries can let untrusted text override intended instructions.
- **Maintainability concerns:** repeated review logic scattered across many prompts makes improvement expensive and inconsistent.
- **Template hazards:** interpolation variables, escaping rules, and rendered formatting can subtly change prompt meaning.
- **Operational ambiguity:** reviewers need a shared way to decide whether a prompt is clear enough, safe enough, and easy enough to evolve.

Without a reusable framework, prompt improvements tend to be local, subjective, and difficult to apply consistently across the corpus.

## Goals

The framework should support these goals:

1. **Reusable prompting principles:** define a compact, project-approved principle set that can guide prompt authors and reviewers.
2. **Reusable prompt review guidance:** provide a rubric/checklist for human review and automated assistant-assisted review.
3. **Maintainable prompt corpora:** make prompts easier to read, diff, test, update, and export.
4. **Human and automated review compatibility:** support both normal PR review and reusable prompts that ask an AI assistant to review another prompt.
5. **Template compatibility:** account for prompt templates, variable interpolation, escaping, and rendered prompt behavior.
6. **Reduced duplicate review logic:** centralize review criteria so individual prompts do not need to restate the entire framework.
7. **Lightweight operational workflow:** add useful review structure without creating mandatory bureaucracy for every small edit.
8. **Model portability:** keep guidance mostly model-agnostic while allowing documented model-specific notes when necessary.
9. **Safety and trust boundaries:** make prompt injection awareness part of normal prompt review.
10. **Iterative evolution:** allow the framework to improve as Taurcode learns from real reviews and exports.

## Non-Goals

This proposal does not require:

- An immediate automatic prompt rewriting system.
- A mandatory prompt linting engine.
- Model-specific hardcoding in the canonical prompt format.
- A heavyweight approval board or governance bureaucracy.
- A universal prompt style that forbids task-specific variation.
- Full prompt evaluation infrastructure before guidance can exist.
- Migration of all LRH request templates in the first implementation pass.
- Runtime enforcement of every rubric item in the Taurcode CLI.

## Proposed Architecture

The proposed architecture has four near-term pieces and several optional future hooks.

### 1. Canonical prompting guidance document

Create a human-readable guidance document, likely:

```text
docs/prompting-best-practices.md
```

This document should be the canonical source for Taurcode prompting principles. It should explain:

- principle definitions
- examples of good prompt structure
- when to use structured output contracts
- how to handle context and examples
- how to treat user/repository-provided text as data rather than instructions
- how to reason about templates and interpolation variables
- how to iterate prompts safely

This document should be concise enough for prompt authors to actually read, but detailed enough to reduce subjective review debates.

### 2. Prompt review rubric/checklist

Add a review rubric as either a section of the guidance document or a separate document if it grows, likely one of:

```text
docs/prompting-best-practices.md
# or
docs/prompt-review-rubric.md
```

The rubric should define review dimensions, example questions, and severity guidance. It should be usable by humans in PR review and by AI assistants when asked to review prompt changes.

A lightweight severity model is enough:

- **Blocker:** likely to break the prompt, compromise safety, or violate a documented contract.
- **Concern:** likely to reduce clarity, maintainability, or robustness.
- **Suggestion:** optional improvement or style consistency note.

### 3. Reusable prompt-review prompts

Add one or more canonical review prompts, likely:

```text
prompts/taurcode/prompt-review.md
```

A first review prompt should ask an assistant to review a proposed prompt against the canonical guidance and rubric. It should produce structured findings rather than rewrite the prompt by default.

Possible output contract:

```markdown
## Summary

## Blockers

## Concerns

## Suggestions

## Template and Variable Notes

## Safety and Injection Notes

## Recommended Follow-up
```

The first version should focus on review, not automatic rewriting. A future companion prompt could support proposed rewrites once reviewers trust the rubric.

### 4. Repository integration points

Integrate the framework into existing Taurcode workflows without changing the canonical prompt format immediately:

- `prompts/taurcode/*.md`: prompt authors use the guidance when editing canonical prompts.
- `src/taurcode/`: future validators may optionally check metadata or structure that can be validated deterministically.
- `tests/`: future tests may render templated prompts, validate fixture prompts, or snapshot exported package behavior.
- `project/design/proposals/`: design proposals capture architectural direction before implementation.
- `project/work_items/`: follow-up implementation work items can be created from the rollout plan.
- `project/executions/`: prompt-driven changes record execution history when meaningful.

### 5. Optional future automation hooks

Future automation should be additive, not required for the first rollout:

- `taurcode prompt review`: run an assistant-assisted review prompt against a prompt file.
- `taurcode validate --strict-prompts`: deterministic checks for metadata, duplicate variables, or missing output contract sections.
- `tests/fixtures/prompts/`: representative prompt fixtures for review and rendering tests.
- `docs/prompt-review-rubric.md`: split rubric into a dedicated document if it becomes too large.
- `prompts/taurcode/prompt-rewrite.md`: optional rewrite assistant prompt once review-only behavior is established.
- `project/templates/` or LRH-owned locations: optional extension for LRH request templates.

## Prompting Principles

The first guidance document should crystallize roughly 8-12 principles. Proposed v1 principles:

1. **Clarity and specificity:** state the task, constraints, and success criteria directly.
2. **Separation of concerns:** separate instructions, context, examples, variables, and output format where practical.
3. **Explicit output contracts:** specify expected structure when downstream humans or tools depend on the response shape.
4. **Positive instructions first:** prefer clear desired behavior over long lists of prohibitions; use constraints where they materially reduce risk.
5. **Right-sized reasoning scaffolds:** ask for planning, checks, or concise rationale only when it improves task quality; avoid unnecessary hidden or verbose reasoning requirements.
6. **Context as data:** mark user-provided, repository-provided, or generated content as data to inspect, not instructions to obey.
7. **Template awareness:** design prompts so interpolation variables, escaping, and rendered formatting preserve meaning.
8. **Maintainability:** make prompts easy to diff, review, and update; avoid repeated boilerplate when a reusable reference can work.
9. **Evaluation and iteration:** treat prompt design as iterative; prefer small changes with observable validation.
10. **Safety and injection awareness:** identify trust boundaries and make instruction precedence explicit when prompts include untrusted text.
11. **Model robustness:** avoid relying on provider-specific quirks unless documented; expect model behavior to drift over time.
12. **Operational usefulness:** optimize prompts for real workflow outcomes, not aesthetic prompt cleverness.

## Prompt Review Rubric

The review rubric should evaluate prompts across the following dimensions.

### Correctness

- Does the prompt ask for the intended task?
- Are constraints compatible with the task?
- Are repository-specific requirements accurate?
- Does the prompt avoid asking the model to do impossible or unavailable work?

### Ambiguity

- Are key terms defined or inferable from context?
- Does the prompt make clear who the audience is?
- Are optional and mandatory behaviors distinguishable?
- Could a reasonable model follow the prompt in multiple incompatible ways?

### Maintainability

- Is the prompt readable as Markdown?
- Are sections organized predictably?
- Is duplicated boilerplate necessary?
- Can future reviewers update one concern without rewriting the whole prompt?

### Formatting consistency

- Does the prompt follow repository conventions for frontmatter and Markdown body structure?
- Are headings, lists, examples, and code fences used consistently?
- Will export targets preserve the intended formatting?

### Output contract clarity

- Does the prompt define expected sections, formats, or schemas when needed?
- Are failure modes or warning formats specified where useful?
- Does the output contract match how users will consume the response?

### Variable safety

- Are variables named clearly?
- Are variable trust levels apparent?
- Are interpolation boundaries visible in the rendered prompt?
- Could a variable value accidentally terminate a section, code fence, or instruction boundary?

### Injection resistance

- Does the prompt distinguish trusted instructions from untrusted input?
- Does it tell the model how to handle conflicting instructions inside quoted content, repository files, or user-provided text?
- Are tool-use or execution instructions guarded against untrusted content?

### Context handling

- Does the prompt ask for enough context without assuming unavailable files or tools?
- Does it avoid overloading the model with irrelevant context?
- Does it tell the model what to do when context is missing?

### Reasoning appropriateness

- Does the prompt request planning, concise rationale, or verification only where useful?
- Does it avoid demanding unnecessary chain-of-thought disclosure?
- Does it prefer actionable summaries and checks over verbose internal reasoning?

### Model robustness

- Is the prompt likely to work across multiple current models?
- Does it avoid brittle phrasing that depends on a single provider's behavior?
- Are model-specific assumptions documented as notes rather than hidden requirements?

### Operational usability

- Can a user paste or expand the prompt and understand what to provide next?
- Does the prompt minimize repetitive manual work?
- Does it fit Taurcode's CLI/export workflow and Espanso package constraints?

## Suggested Review Workflow

A lightweight prompt review workflow should be enough for v1:

1. **Author or modify a prompt** in the canonical corpus or a related template location.
2. **Self-check against the guidance** for obvious clarity, formatting, variable, and safety issues.
3. **Run normal repository checks** when prompt changes affect export, import, validation, or packaging behavior.
4. **Optionally run the reusable prompt-review prompt** for meaningful prompt changes.
5. **Address blockers and high-value concerns**; record suggestions as follow-up if they would broaden the PR.
6. **Avoid process expansion** for tiny wording fixes unless traceability is useful.

For meaningful prompt-driven changes, continue using the existing execution-record workflow from `PROMPTS.md`.

## Reusable Prompt-Review Prompt Design

The first reusable review prompt should be a canonical Taurcode prompt. It should:

- summarize the prompt under review
- evaluate against the canonical principles and rubric
- classify findings by severity
- avoid rewriting by default
- call out template and variable risks separately
- call out injection and trust-boundary risks separately
- identify whether follow-up should be immediate or can be deferred

The prompt should accept at least:

- the prompt text under review
- optional rendered output if the prompt is templated
- optional repository context or intended use case
- optional known model/provider target if relevant

The review prompt should not require live internet access. It can reference the checked-in guidance as its source of review criteria.

## Templated Prompt Considerations

Taurcode prompts are currently Markdown/frontmatter files, but future prompt tooling and LRH request templates may include interpolation. The framework should account for templated prompts before adding strict automation.

### LRH request templates

LRH request templates may combine project control-plane content, work-item data, generated prompt IDs, and user-provided request text. Review should verify:

- which variables are trusted project metadata and which are user-controlled
- whether rendered prompts preserve instruction hierarchy
- whether missing variables fail clearly or render with visible placeholders
- whether template defaults are documented
- whether repeated template sections stay readable after rendering

### Interpolation variables

Variables should have clear names and intended types. Where possible, template documentation should distinguish:

- trusted internal values
- user-authored values
- repository file excerpts
- generated or model-produced values
- optional values that may be empty

### Escaping and boundary preservation

Rendered prompts should not let variable values accidentally break prompt structure. Reviewers should consider:

- code fence collisions
- Markdown heading injection
- YAML/frontmatter delimiter collisions
- braces or placeholder syntax inside variable values
- indentation changes that alter block semantics
- target-specific escaping for Espanso or other package formats

### Rendering behavior

Prompt review should inspect rendered examples, not only source templates, when rendering behavior can change meaning. Future tests can include golden rendered prompts for representative variable values.

### Formatting semantics

Formatting is part of the prompt contract. Exporters and template renderers should preserve meaningful line breaks, bullets, code fences, and quoted data boundaries. If a target cannot preserve formatting, the limitation should be documented rather than hidden.

### Compatibility with existing tooling

The first rollout should not require changing Taurcode's canonical prompt schema. Future schema additions, such as optional `variables` metadata, should be proposed separately and validated against import/export needs.

## Optional LRH Request Template Extension

The framework can later extend to LRH request templates if it proves useful for Taurcode prompts. A staged extension could:

1. inventory LRH request templates and identify variable patterns
2. document LRH-specific trust boundaries
3. add rendered-template review examples
4. create a reusable LRH-template review prompt
5. consider deterministic checks for missing variables or unsafe placeholder rendering

This should remain optional until Taurcode's own prompt corpus review process is useful and stable.

## Recommended Rollout Plan

Roll out the framework in staged PRs:

1. **Design proposal:** add this proposal under `project/design/proposals/` and document the proposal area.
2. **Guidance document:** add `docs/prompting-best-practices.md` with principles, examples, and the initial rubric.
3. **Review prompt:** add `prompts/taurcode/prompt-review.md` as a canonical reusable review prompt.
4. **Taurcode prompt review pass:** use the review prompt to audit existing `prompts/taurcode/*.md`; make narrow updates where the review identifies high-value improvements.
5. **Template follow-up:** evaluate whether LRH request templates need the same rubric or a specialized variant.
6. **Optional automation:** after manual review experience, consider deterministic validation checks or a CLI review command.
7. **Roadmap/work-item planning:** convert accepted follow-up stages into LRH work items as needed.

## Risks and Tradeoffs

### Over-standardization

A single style can improve consistency, but too much standardization can make prompts worse for specialized tasks. The guidance should describe defaults, not ban justified variation.

### Prompt bureaucracy

Review rubrics can slow work if every tiny wording change requires extensive ceremony. The workflow should reserve deeper review for meaningful prompt changes.

### Stale guidance

Prompting guidance can drift as models and best practices change. The guidance document should include a review date or changelog once it exists.

### Model-specific behavior drift

Model-specific tips can be useful, but hardcoding them into general Taurcode guidance can make prompts brittle. Prefer model-agnostic principles plus clearly labeled provider/model notes.

### Consistency vs flexibility

Reusable review logic reduces duplication, but individual prompts may still need task-specific structure. The framework should let prompt owners explain deviations.

### False confidence from review prompts

An AI-assisted review prompt can catch issues, but it is not proof of prompt quality. Human review, rendered examples, and real workflow outcomes remain important.

### Automation cost

Deterministic linting can catch obvious issues, but prompt semantics are hard to validate mechanically. Automation should begin with low-risk checks before claiming semantic review capability.

## Open Questions

1. Which guidance belongs in a single canonical document versus separate rubric and examples files?
2. Should canonical prompt frontmatter eventually include optional prompt metadata such as `variables`, `audience`, `review_status`, or `last_reviewed`?
3. How should Taurcode represent model-specific prompting differences without fragmenting the corpus?
4. What prompt evaluation metrics are practical for a small prompt toolkit?
5. Should prompt review become a CLI feature, a reusable prompt only, or both?
6. Which rendered-template cases should become regression tests?
7. How should review findings be recorded when they do not produce immediate code changes?
8. Should LRH request templates share the exact Taurcode rubric or use an LRH-specific supplement?
9. What safety checks can be deterministic without overpromising injection resistance?
10. How should prompt review integrate with future package targets beyond Espanso?

## References and Further Reading

These references should inform the future guidance document without being copied wholesale into Taurcode rules:

- [OpenAI: Prompt engineering best practices for ChatGPT](https://help.openai.com/en/articles/10032626-prompt-engineering-best-practices-for-chatgpt)
- [OpenAI API: Prompt engineering / prompting guidance](https://platform.openai.com/docs/guides/prompt-engineering)
- [OpenAI API: Reasoning best practices](https://platform.openai.com/docs/guides/reasoning-best-practices)
- [Google Cloud Vertex AI: Overview of prompting strategies](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/learn/prompts/prompt-design-strategies)
- [Google Cloud Vertex AI: Prompt iteration strategies](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/prompts/prompt-iteration)
- [Google Cloud Vertex AI: Use prompt templates](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/learn/prompts/prompt-templates)
- [Anthropic: Prompt engineering overview](https://docs.anthropic.com/en/docs/prompt-engineering)
- [Anthropic: Claude prompt engineering best practices](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices)
- [Wei et al., 2022: Chain-of-Thought Prompting Elicits Reasoning in Large Language Models](https://arxiv.org/abs/2201.11903)
- [Yao et al., 2022: ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)
- [Wang et al., 2022: Self-Consistency Improves Chain of Thought Reasoning in Language Models](https://arxiv.org/abs/2203.11171)
- [Yao et al., 2023: Tree of Thoughts: Deliberate Problem Solving with Large Language Models](https://arxiv.org/abs/2305.10601)
- [Liu et al., 2023: Lost in the Middle: How Language Models Use Long Contexts](https://arxiv.org/abs/2307.03172)
- [Wallace et al., 2024: The Instruction Hierarchy: Training LLMs to Prioritize Privileged Instructions](https://arxiv.org/abs/2404.13208)
- [The Prompt Report: A Systematic Survey of Prompting Techniques](https://arxiv.org/abs/2406.06608)

## Acceptance Criteria for Follow-Up Implementation

A follow-up implementation should be considered successful when:

- Taurcode has a checked-in canonical prompting guidance document.
- The guidance includes a compact principle set and practical review rubric.
- Taurcode has at least one reusable prompt-review prompt in the canonical prompt corpus.
- Existing prompt validation and export workflows continue to pass.
- Any template-specific guidance preserves compatibility with current canonical prompt loading and Espanso export behavior.
- Future automation hooks are documented as optional rather than implied requirements.
