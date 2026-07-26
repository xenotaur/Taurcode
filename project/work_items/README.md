---
id: WORK-ITEMS-README
title: Work items layout and metadata
status: active
---

# Work Items

Work items are organized by status bucket directories:

- `project/work_items/proposed/`
- `project/work_items/active/`
- `project/work_items/resolved/`
- `project/work_items/abandoned/`

Each work item Markdown file must include YAML frontmatter at minimum:

```yaml
---
id: WI-EXAMPLE
title: Example work item
type: deliverable
status: proposed
---
```

## Required metadata

Work item frontmatter must include:

- `id`
- `title`
- `type`: one of `deliverable`, `investigation`, `evaluation`, `operation`
- `status`: one of `proposed`, `active`, `resolved`, `abandoned`
- `blocked`: `true` or `false`
- `blocked_reason`: a non-empty string when `blocked: true`; `null` or `""`
  when `blocked: false` (unvalidated in that case)
- `resolution`: a non-empty string when `status` is a terminal status
  (`resolved` or `abandoned`); must be exactly `null` (not `""`) when
  `status` is non-terminal (`proposed` or `active`)

`lrh validate` enforces these fields (missing `id`/`title`/`type`/`status`
fails with `MISSING_REQUIRED_FIELD`; the `blocked`/`blocked_reason`/
`resolution` rules above fail with their own dedicated error codes).

The frontmatter `status` field is authoritative. Bucket directories provide
human-friendly organization and should match frontmatter status.
