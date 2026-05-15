---
prompt_id: AD_HOC-20260515-TAURCODE-ESPANSO-METADATA-ROUNDTRIP-MVP
date: 2026-05-15
scope: AD_HOC
status: landed
---

## Summary
implemented Espanso metadata roundtrip MVP

## Result
Execution completed.

## Validation
scripts/develop: failed because pip build dependency download hit Tunnel connection failed: 403 Forbidden for setuptools>=64.
scripts/lint: passed.
scripts/format: passed.
scripts/test: passed, 124 tests.
scripts/coverage: failed because coverage is not installed in the environment.
taurcode validate --prompts prompts/taurcode: failed because taurcode command is not installed after scripts/develop failed.
taurcode export espanso --prompts prompts/taurcode --output build/espanso/taurcode: failed because taurcode command is not installed after scripts/develop failed.
PYTHONPATH=src python -m unittest tests.espanso_import_test tests.espanso_export_test: passed, 40 tests.

## Follow-up
None.
