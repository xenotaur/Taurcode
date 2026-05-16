# Semantic vs Textual Fidelity

Taurcode roundtrip checks compare semantics instead of raw generated text.

## Textual fidelity

A textual comparison asks whether two files have identical bytes. That is useful for generated snapshots, but it is too strict for many YAML workflows. YAML emitters can change field ordering, quoting, indentation, block scalar style, or list style while preserving the data Espanso receives.

If Taurcode required byte-for-byte YAML equality, harmless emitter changes could look like product regressions.

## Semantic fidelity

A semantic comparison asks whether two representations mean the same thing for the supported Taurcode workflow.

For Espanso roundtrip checks, Taurcode currently compares:

- prompt trigger/keyword semantics
- prompt replacement/body text
- parsed `_manifest.yml` data
- `README.md` and `LICENSE` text with normalized line endings
- supported package metadata presence when canonical metadata assets are curated

This model catches meaningful drift while avoiding noise from formatting-only YAML differences.

## Why formatting-only changes are ignored

Espanso consumes parsed YAML data, not a preferred Taurcode emitter style. A package with the same triggers and replacements should pass even if YAML quotes or block scalar formatting differ.

Taurcode still preserves final-newline behavior for prompt bodies because a final newline can be part of the parsed replacement text. The goal is not to ignore all text differences; it is to ignore differences that do not change the represented package semantics.

## What semantic mode intentionally ignores

Espanso semantic mode does not compare canonical-only prompt annotations such as `name` and `description`, because simple Espanso package output does not contain them. Their absence in an exported package is not an export failure.

Canonical semantic comparison remains a fuller concept for prompt-source comparisons and future tooling, where Taurcode-owned annotations matter.
