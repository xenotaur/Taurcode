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

The frontmatter `status` field is authoritative. Bucket directories provide
human-friendly organization and should match frontmatter status.
