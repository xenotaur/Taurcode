---
prompt_id: PROMPT(PROMPTING-BEST-PRACTICES-REVIEW-PROMPT)-20260512-0002
date: 2026-05-14
scope: AD_HOC
related_work_item: AD_HOC
status: landed
---

## Summary
Added a reusable Taurcode prompt-review prompt under prompts/taurcode and documented its use from the root README.

## Result
Execution completed.

## Validation
scripts/version tools: failed because taurcode package metadata was not installed in the environment.
PYTHONPATH=src python -m taurcode.cli validate --prompts prompts/taurcode: passed.
PYTHONPATH=src python -m taurcode.cli lint prompts --prompts prompts/taurcode: passed.

## Follow-up
None.
