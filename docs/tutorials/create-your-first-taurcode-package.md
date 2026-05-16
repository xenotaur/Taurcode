# Create Your First Taurcode Package

This tutorial walks through the smallest useful Taurcode workflow: write a canonical prompt, validate it, export it to Espanso, and check that the Espanso package still represents the same prompt semantics.

The examples use the checked-in `prompts/taurcode/` package. For experimentation, work on a branch or copy that directory to a temporary package directory before editing.

## 1. Create a canonical prompt file

Create a Markdown file in a prompt package directory such as `prompts/taurcode/hello-world.md`:

```markdown
---
id: hello-world
name: Hello World
description: A small example prompt
keyword: ":tc-hello"
---

Say hello and explain what Taurcode prompts are in one short paragraph.
```

A canonical prompt has YAML frontmatter followed by the prompt body. The required fields are `id`, `name`, `description`, `keyword`, and a non-empty body. The `keyword` is the trigger exported to Espanso, so it must start with `:`.

## 2. Validate the prompt package

Run validation before exporting:

```bash
taurcode validate --prompts prompts/taurcode
```

Validation loads Markdown prompt files, checks required fields, and verifies unique `id` and `keyword` values.

For source-level checks before validation, run:

```bash
taurcode lint prompts --prompts prompts/taurcode
```

To check conservative formatting without rewriting files, run:

```bash
taurcode format prompts --prompts prompts/taurcode --check
```

## 3. Export the package to Espanso

Export canonical prompts into an Espanso package directory:

```bash
taurcode export espanso --prompts prompts/taurcode --output tmp/exported/taurcode
```

The generated package contains `package.yml`, `_manifest.yml`, and `README.md`. If the canonical package includes curated Espanso metadata under `prompts/taurcode/espanso/`, export copies supported metadata assets from there.

## 4. Check semantic roundtrip fidelity

After export, compare the generated Espanso package with the canonical prompt package:

```bash
taurcode roundtrip espanso --input tmp/exported/taurcode --prompts prompts/taurcode
```

A passing run reports that the semantic comparison passed. Taurcode compares prompt triggers, prompt bodies, and supported package metadata semantics rather than requiring byte-for-byte YAML equality.

## 5. Clean up experimental output

Generated package output under `tmp/` is a temporary local artifact. Keep canonical prompt edits under the prompt package directory, and keep generated output out of source control unless a task explicitly asks for it.

## Next steps

- See [Canonical prompt format](../reference/canonical-prompt-format.md) for exact field behavior.
- See [Espanso integration](../reference/espanso-integration.md) for import/export details.
- See [Check Espanso roundtrip fidelity](../how-to/check-espanso-roundtrip-fidelity.md) for a focused operational checklist.
