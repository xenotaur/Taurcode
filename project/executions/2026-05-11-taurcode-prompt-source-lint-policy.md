---
prompt_id: PROMPT(TAURCODE-PROMPT-SOURCE-LINT-POLICY)[2026-05-11T01:50:00-04:00]
date: 2026-05-11
scope: AD_HOC
related_work_item: AD_HOC
status: landed
---

## Summary
Added prompt-source lint checks, CLI integration, documentation, and tests for Taurcode Markdown prompt packages.

## Result
Execution completed.

## Validation
scripts/develop (failed: pip build dependency fetch blocked by 403 Forbidden); scripts/test; scripts/lint; scripts/format --check --diff; PYTHONPATH=src python -m taurcode.cli lint prompts --prompts prompts/taurcode

## Follow-up
None.
