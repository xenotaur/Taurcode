---
prompt_id: PROMPT(TAURCODE-ROUNDTRIP-MERGE-NEWLINE-DESIGN)[2026-05-10T00:40:00-04:00]
date: 2026-05-10
scope: AD_HOC
related_work_item: AD_HOC
status: in_progress
---

## Summary
Updated the existing Espanso metadata round-trip design proposal with merge import and newline normalization semantics for curated Taurcode prompt packages.

## Result
Review feedback addressed; PR remains in review until merge.

## Validation
Initial PR validation: scripts/develop: warning - failed because pip build dependency download was blocked by 403 for setuptools. scripts/lint: passed. scripts/format: passed. scripts/test: passed, 59 tests discovered and passed.

Review feedback validation: scripts/version tools: warning - failed because the `taurcode` distribution metadata is not installed in this environment. Per review protocol, format, lint, and test were not rerun after this setup/bootstrap mismatch.

## Follow-up
None.
