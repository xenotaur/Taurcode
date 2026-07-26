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

Each work item Markdown file must include YAML frontmatter at minimum:

```yaml
---
id: WI-EXAMPLE
status: proposed
---
```

## Required metadata

In addition to `id` and `status`, work items must include:

- `blocked` (`true` or `false`)
- `blocked_reason` (non-empty when `blocked: true`; `null`/empty otherwise)
- `resolution` (non-empty when `status` is terminal — `resolved` or `abandoned`;
  `null`/empty otherwise)

`lrh validate` enforces these fields.

The frontmatter `status` field is authoritative. Bucket directories provide
human-friendly organization and should match frontmatter status.
