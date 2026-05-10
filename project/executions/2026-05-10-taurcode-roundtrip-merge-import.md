---
prompt_id: PROMPT(TAURCODE-ROUNDTRIP-MERGE-IMPORT)[2026-05-10T00:45:00-04:00]
date: 2026-05-10
scope: AD_HOC
status: landed
---

## Summary
Implemented explicit Espanso merge import semantics that preserve curated Markdown frontmatter, update Espanso-derived keyword/body content, create new prompts, warn on orphans, fail on ambiguous matches, and ignore espanso/ package metadata during matching.

## Result
Execution completed.

## Validation
scripts/develop (failed: pip build dependency install blocked by 403 to package index); scripts/lint (passed); scripts/test (passed, 67 tests).

## Follow-up
None.
