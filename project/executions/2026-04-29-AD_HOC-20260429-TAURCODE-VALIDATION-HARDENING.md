---
prompt_id: AD_HOC-20260429-TAURCODE-VALIDATION-HARDENING
date: 2026-04-29
scope: project/
related_work_item: AD_HOC
status: landed
---

# Execution Record

## Summary
Prompt validation hardening for directory loading, deterministic validation/export flow, CLI validation command, tests, and docs.

## Changes
- Extended prompt loading to recursively load markdown files and sort deterministically.
- Added stronger validation for required fields, keyword format, duplicate IDs, and duplicate keywords with source-aware errors.
- Added `taurcode validate --prompts <dir>` CLI command.
- Added unittest coverage for deterministic behavior and invalid data paths.
- Updated README with validation command and rules.

## Related work item
- AD_HOC
