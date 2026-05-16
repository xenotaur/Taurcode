# Taurcode Documentation

Taurcode documentation is organized with a lightweight Diátaxis-inspired structure:

- **Tutorials** teach a complete workflow from start to finish.
- **How-to guides** answer task-specific operational questions.
- **Reference** pages describe stable formats, commands, and behavior.
- **Explanations** describe the rationale behind Taurcode design choices.

## Tutorials

- [Create your first Taurcode package](tutorials/create-your-first-taurcode-package.md) — author a canonical prompt, validate it, export it to Espanso, and run a semantic roundtrip check.

## How-to guides

- [Import an Espanso package](how-to/import-an-espanso-package.md) — stage or merge an Espanso package into Taurcode prompt sources.
- [Check Espanso roundtrip fidelity](how-to/check-espanso-roundtrip-fidelity.md) — verify exported Espanso output against canonical prompt semantics.
- [Debug Espanso import errors](how-to/debug-espanso-import-errors.md) — use preflight linting and source fixes before importing.

### Best practices

- [Prompting best practices](how-to/best-practices/prompting-best-practices.md) — practical prompt authoring and review guidance.
- [Reliable AI editing](how-to/best-practices/reliable-ai-editing.md) — editor contracts and safe workflows for AI-assisted code updates.

## Reference

- [Canonical prompt format](reference/canonical-prompt-format.md) — required frontmatter, optional fields, prompt discovery, validation, and formatting expectations.
- [Espanso integration](reference/espanso-integration.md) — import, export, metadata assets, supported Espanso features, and roundtrip comparison behavior.

## Explanations

- [Canonical prompts vs Espanso](explanations/canonical-prompts-vs-espanso.md) — why Taurcode treats Markdown prompt files as source and Espanso as a target format.
- [Semantic vs textual fidelity](explanations/semantic-vs-textual-fidelity.md) — why roundtrip checks compare meaning instead of generated YAML bytes.
