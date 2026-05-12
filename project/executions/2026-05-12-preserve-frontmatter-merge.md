---
prompt_id: PROMPT(TAURCODE-PRESERVE-FRONTMATTER-MERGE)[2026-05-11T02:00:00-04:00]
date: 2026-05-12
scope: AD_HOC
status: landed
---

## Summary
Preserved existing Markdown prompt frontmatter text during Espanso merge import when keyword semantics are unchanged; added targeted keyword edits for filename matches, regression tests for quoted keyword/long description/order/unknown formatting/body updates/idempotence, and documented diff-friendly merge behavior.

## Result
Execution completed.

## Validation
scripts/develop (failed: package build dependencies could not be fetched because pip access to setuptools was blocked by 403); scripts/test (failed because editable install could not complete, leaving taurcode unavailable on sys.path); PYTHONPATH=src python -m unittest discover -b -s tests -p "*_test.py" (passed, 112 tests); scripts/lint (passed); PYTHONPATH=src scripts/smoke (no smoke tests discovered).

## Follow-up
None.
