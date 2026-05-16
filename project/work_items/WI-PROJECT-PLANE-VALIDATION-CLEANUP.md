---
id: WI-PROJECT-PLANE-VALIDATION-CLEANUP
title: Clean up Taurcode project-plane validation issues
type: work_item
status: proposed
priority: medium
owner: TBD
related_focus: []
related_workstreams: []
blocked: false
blocked_reason: ""
resolution: ""
---

# Work Item: Clean up Taurcode project-plane validation issues

## Objective

Resolve the known `lrh validate` project-plane metadata failures in Taurcode so the repository's project/control-plane metadata validates cleanly without weakening LRH validation rules.

This work item is intentionally scoped to project-plane hygiene. It should not change Taurcode runtime behavior, prompt import/export semantics, lint/toolchain configuration, or Espanso round-trip behavior except where documentation references need to remain consistent.

## Background

After the lint/toolchain drift fix landed, the Taurcode code validation passed:

- `scripts/lint` passed.
- `scripts/test` passed with 121 tests.
- `scripts/version tools` reported the expected pinned tool versions.

However, `lrh validate` still reported known project-plane metadata issues. These are pre-existing or adjacent control-plane hygiene issues, not regressions in the lint/toolchain workstream.

Representative validation output:

```text
Validation completed: 14 error(s), 1 warning(s)

Errors:
- [MISSING_REQUIRED_FIELD] work_items/active/WI-CANONICAL-PROMPTS-0002.md: missing required field 'type'
- [WORK_ITEM_LIST_FIELD_INVALID] work_items/active/WI-CANONICAL-PROMPTS-0002.md: related_focus must be a list
- [MISSING_REQUIRED_FIELD] work_items/active/WI-CANONICAL-PROMPTS-0002.md: missing required field 'blocked'
- [MISSING_REQUIRED_FIELD] work_items/active/WI-CANONICAL-PROMPTS-0002.md: missing required field 'blocked_reason'
- [MISSING_REQUIRED_FIELD] work_items/active/WI-CANONICAL-PROMPTS-0002.md: missing required field 'resolution'
- [MISSING_REQUIRED_FIELD] work_items/resolved/WI-BOOTSTRAP-0001.md: missing required field 'type'
- [WORK_ITEM_LIST_FIELD_INVALID] work_items/resolved/WI-BOOTSTRAP-0001.md: related_focus must be a list
- [MISSING_REQUIRED_FIELD] work_items/resolved/WI-BOOTSTRAP-0001.md: missing required field 'blocked'
- [MISSING_REQUIRED_FIELD] work_items/resolved/WI-BOOTSTRAP-0001.md: missing required field 'blocked_reason'
- [MISSING_REQUIRED_FIELD] work_items/resolved/WI-BOOTSTRAP-0001.md: missing required field 'resolution'
- [WORK_ITEM_RESOLUTION_REQUIRED] work_items/resolved/WI-BOOTSTRAP-0001.md: terminal statuses require a non-empty resolution
- [MISSING_FRONTMATTER] contributors/contributors.md: markdown file must begin with YAML frontmatter
- [UNKNOWN_OWNER] work_items/active/WI-CANONICAL-PROMPTS-0002.md: owner references unknown contributor 'TBD'
- [UNKNOWN_OWNER] work_items/resolved/WI-BOOTSTRAP-0001.md: owner references unknown contributor 'TBD'

Warnings:
- [PLANNING_ORPHANED_ACTIVE_WORK_ITEM] work_items/active/WI-CANONICAL-PROMPTS-0002.md: active work item 'WI-CANONICAL-PROMPTS-0002' is not attached to a planning parent
```

## Scope

### Status update

The Espanso roundtrip closeout resolved `WI-CANONICAL-PROMPTS-0002` and moved it to
`project/work_items/resolved/` with schema-shaped frontmatter and closeout evidence.
This cleanup item should now treat any remaining canonical-prompt work item validation
issues as verification rather than as active implementation work.

### Required changes

- Verify `project/work_items/resolved/WI-CANONICAL-PROMPTS-0002.md` remains compatible with the current LRH work item schema.
- Update `project/work_items/resolved/WI-BOOTSTRAP-0001.md` so its frontmatter conforms to the current LRH work item schema.
- Convert `related_focus` fields from scalar values to lists where required.
- Add required work item fields:
  - `type`
  - `blocked`
  - `blocked_reason`
  - `resolution`
- For resolved work items, provide a meaningful non-empty `resolution`.
- Resolve `owner: TBD` issues by either:
  - replacing `TBD` with a valid contributor ID, or
  - adding an appropriate contributor record/frontmatter for the placeholder only if that is consistent with Taurcode conventions.
- Add required YAML frontmatter to `project/contributors/contributors.md`, or restructure contributor metadata according to current Taurcode/LRH conventions.
- Address the orphaned active work item warning for `WI-CANONICAL-PROMPTS-0002` by attaching it to the appropriate planning parent, workstream, focus, or documented interim parent relationship.

### Out of scope

- Do not weaken, bypass, or special-case LRH validation to make these issues disappear.
- Do not make Taurcode runtime code changes unless needed only for documentation or validation wiring.
- Do not rework unrelated design proposals, evidence records, or execution records.
- Do not reopen `WI-CANONICAL-PROMPTS-0002` unless validation shows the closeout evidence is materially incorrect.
- Do not invent major new lifecycle conventions if LRH already defines the required schema.

## Suggested implementation approach

1. Inspect current LRH/Taurcode schema expectations:
   - `project/work_items/README.md`
   - `project/contributors/README.md`, if present
   - `project/design/proposals/README.md`
   - current `lrh validate` output
   - known-good work item examples in LRH, if needed

2. Update work item frontmatter conservatively:
   - preserve existing IDs, titles, status, and intent
   - add missing required fields
   - convert scalar list fields to YAML lists
   - use `blocked: false` and `blocked_reason: ""` only where truthful

3. Resolve contributor ownership:
   - prefer a real known contributor ID if Taurcode has one
   - otherwise create or repair contributor metadata so ownership references validate
   - avoid leaving `owner: TBD` if validation treats it as an unknown contributor

4. Add a valid resolution to `WI-BOOTSTRAP-0001.md`:
   - summarize that repository bootstrap/project-plane scaffolding was completed
   - cite existing evidence or execution records if appropriate

5. Verify resolved `WI-CANONICAL-PROMPTS-0002` closeout state:
   - confirm the resolved work item path and evidence references are valid
   - avoid reopening the work item unless its acceptance criteria are demonstrably incomplete

## Acceptance criteria

- `lrh validate` reports no errors for:
  - `work_items/resolved/WI-CANONICAL-PROMPTS-0002.md`
  - `work_items/resolved/WI-BOOTSTRAP-0001.md`
  - `contributors/contributors.md`
- `lrh validate` no longer reports `UNKNOWN_OWNER` for `owner: TBD`.
- `lrh validate` no longer reports `WORK_ITEM_RESOLUTION_REQUIRED` for `WI-BOOTSTRAP-0001.md`.
- The orphaned active work item warning is resolved or explicitly documented as deferred with a clear reason.
- `scripts/lint` passes.
- `scripts/test` passes.
- No unrelated project-plane files are changed.
- Any execution record created for this cleanup follows `PROMPTS.md` and `project/executions/README.md`.

## Validation commands

Run:

```bash
lrh validate
scripts/lint
scripts/test
```

Optionally also run:

```bash
scripts/version tools
```

## Notes for a later automated cleanup pass

This work item exists partly to give a future LRH-assisted project-plane cleanup tool a concrete target. Prefer deterministic schema repairs and avoid semantic reinterpretation unless the repository evidence clearly supports it.
