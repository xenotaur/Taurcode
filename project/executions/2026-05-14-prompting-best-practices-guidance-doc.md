---
prompt_id: PROMPT(PROMPTING-BEST-PRACTICES-GUIDANCE-DOC)-20260512-0001
date: 2026-05-14
scope: AD_HOC
status: landed
---

## Summary
Added docs/prompting-best-practices.md and linked it from README documentation for canonical Taurcode prompt authoring and review guidance.

## Result
Execution completed.

## Validation
scripts/lint failed on pre-existing import ordering in src/taurcode/prompt_loader.py; scripts/test failed before editable install because taurcode was not importable; scripts/develop failed because pip could not reach setuptools due 403 network restrictions; PYTHONPATH=src scripts/test passed 121 tests.

## Follow-up
None.
