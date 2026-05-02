---
prompt_id: PROMPT(AD_HOC:REPAIR_WORK_ITEM_FRONTMATTER_AND_BUCKETS)[2026-05-02T15:18:00-04:00]
date: 2026-05-02
scope: AD_HOC
status: landed
---

## Summary
Repaired LRH work-item organization by aligning statuses to `active`/`proposed`/`resolved`, moving flat work-item files into status buckets, and updating references plus work-items layout documentation.

## Result
- Moved `WI-BOOTSTRAP-0001` to `project/work_items/resolved/` and normalized frontmatter status from `done` to `resolved`.
- Moved `WI-CANONICAL-PROMPTS-0002` to `project/work_items/active/` and normalized frontmatter status from `todo` to `active`.
- Updated status document evidence path to new active work-item location.
- Added `project/work_items/README.md` documenting bucket layout and frontmatter expectations.

## Validation
- `lrh validate` failed in environment (`lrh: command not found`).
- `scripts/test` passed (20 tests).

## Follow-up
Optionally run `lrh validate` in an environment where the `lrh` CLI is installed.
