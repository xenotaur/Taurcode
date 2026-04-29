---
prompt_id: AD_HOC-20260429-TAURCODE-ESPANSO-IMPORTER
date: 2026-04-29
scope: Implement Espanso importer to canonical prompts with raw fallback and CLI integration.
related_work_item: AD_HOC
---

## Summary of changes
- Added `taurcode import espanso` CLI subcommand with `--input` and `--output` options.
- Implemented Espanso importer for simple `trigger` + `replace` matches to canonical Markdown.
- Added raw YAML fallback output for unsupported matches into `prompts/imported_raw/`.
- Added tests for supported conversion, unsupported fallback, mixed imports, duplicate triggers, and invalid YAML.
- Updated README migration workflow for import → validate → export.

## Notes
- `scripts/prompts/record-execution` is not present in this repository snapshot, so this execution record was added manually per `project/executions/README.md` guidance.
- Applied soft idempotence by creating a record only for this prompt ID and leaving unrelated records untouched.
