---
prompt_id: AD_HOC-20260515-TAURCODE-ROUNDTRIP-CLI
date: 2026-05-16
scope: AD_HOC
status: landed
---

## Summary
added Espanso roundtrip semantic comparison CLI

## Result
Execution completed.

## Validation
scripts/develop: failed due pip build dependency network tunnel 403 while fetching setuptools.
scripts/lint: passed after formatting.
scripts/format: passed.
scripts/test: passed, 147 tests.
scripts/coverage: failed because coverage module is not installed in the environment.
taurcode validate/export/roundtrip: exact taurcode command unavailable because develop install failed; PYTHONPATH=src python -m taurcode.cli fallback validate/export/roundtrip passed.

## Follow-up
None.
