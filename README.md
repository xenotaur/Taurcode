# Taurcode
Taurcode is a set of prompts for AI-generated coding with tools to format them for various injection systems like Espanso.

## Canonical prompts
Canonical prompts are authored in Markdown files under `prompts/*.md` with YAML frontmatter metadata.

Example prompt:

```markdown
---
id: test-prompt
name: Test Prompt
description: A test prompt
keyword: ":tc-test"
---

This is a test prompt body.
```

## Export to Espanso
Use the CLI to export canonical prompts to an Espanso package:

```bash
PYTHONPATH=src python -m taurcode.cli export espanso --prompts prompts --output build/espanso/taurcode
```

Generated output:

- `build/espanso/taurcode/package.yml`
- `build/espanso/taurcode/_manifest.yml`

Note: installation into a local Espanso configuration is currently manual.
