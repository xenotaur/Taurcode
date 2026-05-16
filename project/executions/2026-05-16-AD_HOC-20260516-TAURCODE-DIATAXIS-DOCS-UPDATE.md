---
prompt_id: AD_HOC-20260516-TAURCODE-DIATAXIS-DOCS-UPDATE
date: 2026-05-16
scope: AD_HOC
related_work_item: AD_HOC
status: landed
---

## Summary
added Diátaxis-style documentation structure and workflow docs

## Result
Execution completed.

## Validation
scripts/develop: failed due to a pip build-dependency network tunnel 403 while fetching setuptools.
scripts/lint: passed.
scripts/format: passed.
scripts/test: passed, 147 tests.
scripts/coverage: failed because coverage module is not installed in the environment.
taurcode validate --prompts prompts/taurcode: failed because taurcode console script is unavailable after develop install failed.
taurcode export espanso --prompts prompts/taurcode --output tmp/exported/taurcode: failed because taurcode console script is unavailable after develop install failed.
taurcode roundtrip espanso --input tmp/exported/taurcode --prompts prompts/taurcode: failed because taurcode console script is unavailable after develop install failed.
PYTHONPATH=src python -m taurcode.cli validate --prompts prompts/taurcode: passed.
PYTHONPATH=src python -m taurcode.cli export espanso --prompts prompts/taurcode --output tmp/exported/taurcode: passed.
PYTHONPATH=src python -m taurcode.cli roundtrip espanso --input tmp/exported/taurcode --prompts prompts/taurcode: passed.
PYTHONPATH=src python -m taurcode.cli lint prompts --prompts prompts/taurcode: passed.
PYTHONPATH=src python -m taurcode.cli format prompts --prompts prompts/taurcode --check: passed.
Markdown relative links check: passed.

## Follow-up
None.
