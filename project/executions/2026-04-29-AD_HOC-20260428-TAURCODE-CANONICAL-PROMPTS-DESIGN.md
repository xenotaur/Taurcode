---
prompt_id: AD_HOC-20260428-TAURCODE-CANONICAL-PROMPTS-DESIGN
date: 2026-04-29
scope: project/
related_work_item: WI-CANONICAL-PROMPTS-0002
status: completed
---

# Execution Record

## Summary
Updated project control-plane artifacts to record canonical Markdown/frontmatter prompts as the intended source of truth and Espanso as a generated export target.

## Design points recorded
- Canonical prompt authoring should use `prompts/*.md` with YAML frontmatter plus plain Markdown body.
- Espanso is an export target (not canonical source).
- Generated Espanso package outputs should be emitted to `build/espanso/<package>/`.
- v1 should not auto-install generated output into local Espanso locations.

## Notes
- Attempted to use `scripts/prompts/record-execution`, but the script is not present in this repository snapshot.
