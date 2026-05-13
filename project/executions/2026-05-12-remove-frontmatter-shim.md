---
prompt_id: PROMPT(AD_HOC:REMOVE_FRONTMATTER_SHIM)[2026-05-12T16:55:00-04:00]
date: 2026-05-12
scope: AD_HOC
related_work_item: AD_HOC
status: in_progress
---

## Summary
Removed the local top-level src/frontmatter shim so import frontmatter resolves to the declared python-frontmatter dependency; constrained setuptools discovery to taurcode*; added prompt_loader tests for scalar YAML metadata, quoted strings, comments, nested targets, malformed YAML errors, body normalization, and shim removal; updated README and proposal status. No prior execution record for this exact prompt ID was found before work began. Branch: work. Divergence: scripts/develop could not complete because pip build-dependency resolution hit the configured network tunnel, so tests were run with PYTHONPATH=src.

## Result
Execution generated a PR on branch `work` and remains in review until merge.

## Validation
scripts/develop: failed before install due pip tunnel 403 while fetching setuptools build dependencies. scripts/lint: passed. scripts/format --check: passed. scripts/test: failed without an installed package because taurcode was not importable after scripts/develop failed. PYTHONPATH=src scripts/test: passed, 119 tests. PYTHONPATH=src python -m unittest discover -s tests -p '*_test.py': passed, 119 tests. PYTHONPATH=src python -m unittest discover tests: discovered zero tests because repository tests use *_test.py naming. PYTHONPATH=src python - <<'PY' import frontmatter check: resolved frontmatter to site-packages, not src/frontmatter. Review follow-up: scripts/version tools failed because taurcode package metadata is not installed, which is a setup/bootstrap mismatch for canonical tool-version validation. PYTHONPATH=src python -m unittest tests.prompt_loader_test tests.prompt_validation_test passed, 13 tests.

## Follow-up
Addressed review feedback to report malformed prompt YAML as clean CLI errors and to align execution-record metadata.
