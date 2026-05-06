---
prompt_id: AD_HOC-20260506-TAURCODE-CANONICAL-CORPUS-LOCATION
date: 2026-05-06
scope: AD_HOC
status: landed
---

## Summary
finalized canonical Taurcode prompt corpus location under prompts/taurcode/

## Result
Execution completed.

## Validation
scripts/develop: failed due to network/build dependency restrictions (pip tunnel 403 while fetching setuptools>=64).
scripts/lint: passed.
scripts/format: passed.
scripts/test: passed (23 tests).
scripts/coverage: failed because coverage module is unavailable after develop could not install test dependencies.
taurcode validate --prompts prompts/taurcode: could not run because taurcode console script was not installed after scripts/develop failed.
taurcode export espanso --prompts prompts/taurcode --output build/espanso/taurcode: could not run because taurcode console script was not installed after scripts/develop failed.
PYTHONPATH=src python -m taurcode.cli validate --prompts prompts/taurcode: passed (9 prompts).
PYTHONPATH=src python -m taurcode.cli export espanso --prompts prompts/taurcode --output build/espanso/taurcode: passed.

## Follow-up
None.
