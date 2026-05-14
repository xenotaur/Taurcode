---
prompt_id: PROMPT(PROMPTING-BEST-PRACTICES-LRH-TEMPLATE-FOLLOWUP)-20260512-0004
date: 2026-05-14
scope: AD_HOC
status: landed
---

## Summary
Added Taurcode guidance and a reusable prompt for guidance-only reviews of Logical Robotics Harness request templates; no LRH template files were available in this checkout, so direct LRH edits were deferred.

## Result
Execution completed.

## Validation
scripts/develop: failed because pip build dependency fetch was blocked by a 403 Forbidden proxy response. scripts/lint: passed after correcting import ordering in src/taurcode/prompt_loader.py. scripts/test: failed because taurcode was not installed after scripts/develop failed. PYTHONPATH=src python -m unittest discover -b -s tests -p '*_test.py': passed, 121 tests. PYTHONPATH=src python -m taurcode.cli validate --prompts prompts/taurcode: passed, 18 prompts. PYTHONPATH=src python -m taurcode.cli lint prompts --prompts prompts/taurcode: passed. PYTHONPATH=src python -m taurcode.cli format prompts --prompts prompts/taurcode --check: passed.

## Follow-up
None.
