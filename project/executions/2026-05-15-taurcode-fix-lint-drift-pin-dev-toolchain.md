---
prompt_id: PROMPT(TAURCODE-FIX-LINT-DRIFT-PIN-DEV-TOOLCHAIN)[2026-05-15T00:20:00-04:00]
date: 2026-05-15
scope: AD_HOC
status: landed
---

## Summary
Fixed Ruff import-order drift in prompt_loader, pinned development tools in constraints-dev.txt, routed scripts/develop and CI through constrained dev installs, documented reproducible toolchain usage, and added explicit Ruff isort import classification.

## Result
Execution completed.

## Validation
scripts/develop: warning - failed because pip build dependency fetch was blocked by a 403 Forbidden tunnel response for setuptools.
scripts/format: passed.
scripts/lint: passed.
scripts/test: passed, 121 tests.
lrh validate: unavailable because lrh was not installed in the Codex environment.
scripts/version tools: warning - failed because editable install did not complete, so taurcode package metadata was unavailable.
scripts/check-workflows: passed.
python --version / pip / black / ruff / coverage fallback: warning - Python 3.12.13, pip 26.1, black 26.3.1, ruff 0.15.12; coverage module unavailable after scripts/develop failed.

## Follow-up
None.
