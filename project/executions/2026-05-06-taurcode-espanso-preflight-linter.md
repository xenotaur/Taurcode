---
prompt_id: AD_HOC-20260506-TAURCODE-ESPANSO-PREFLIGHT-LINTER
date: 2026-05-06
scope: AD_HOC
status: landed
---

## Summary
added Espanso preflight linter and rich import diagnostics

## Result
Execution completed.

## Validation
scripts/develop: warning - failed because pip build dependency download was blocked by 403 for setuptools.
scripts/lint: passed.
scripts/format: passed.
scripts/test: passed, 30 tests discovered and passed.
scripts/coverage: warning - failed because coverage is not installed after develop could not complete.
taurcode lint espanso --input <temp-good-package>: warning - taurcode entry point unavailable because develop install failed.
PYTHONPATH=src python -m taurcode.cli lint espanso --input <temp-good-package>: passed.

## Follow-up
None.
