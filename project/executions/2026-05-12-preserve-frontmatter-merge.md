---
prompt_id: PROMPT(TAURCODE-PRESERVE-FRONTMATTER-MERGE)[2026-05-11T02:00:00-04:00]
date: 2026-05-12
scope: AD_HOC
related_work_item: AD_HOC
status: landed
---

## Summary
Preserved existing Markdown prompt frontmatter text during Espanso merge import when keyword semantics are unchanged; added targeted keyword edits for filename matches, regression tests for quoted keyword/long description/order/unknown formatting/body updates/idempotence, and documented diff-friendly merge behavior.

## Result
Execution completed.

## Validation
scripts/version tools (failed: taurcode package metadata is not installed in this environment, setup/bootstrap mismatch); PYTHONPATH=src python -m unittest discover -b -s tests -p "*_test.py" (passed, 115 tests); python -m ruff check src tests (passed); python -m black --check src tests (passed). Prior scripts/develop/scripts/test failures were due the same editable-install/bootstrap limitation.

## Follow-up
None.
