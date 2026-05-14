---
prompt_id: PROMPT(PROMPTING-BEST-PRACTICES-REVIEW-PROMPT)-20260512-0002
date: 2026-05-14
scope: AD_HOC
status: landed
---

## Summary
Added a reusable Taurcode prompt-review prompt under prompts/taurcode and documented its use from the root README.

## Result
Execution completed.

## Validation
scripts/develop: failed because pip build dependency resolution could not access setuptools (403 Forbidden).
scripts/lint: failed on pre-existing import-order issue in src/taurcode/prompt_loader.py.
scripts/test: failed because editable install was unavailable after scripts/develop failed.
PYTHONPATH=src python -m taurcode.cli validate --prompts prompts/taurcode: passed.
PYTHONPATH=src python -m taurcode.cli lint prompts --prompts prompts/taurcode: passed.
PYTHONPATH=src python -m unittest discover -b -s tests -p "*_test.py": passed, 121 tests.

## Follow-up
None.
