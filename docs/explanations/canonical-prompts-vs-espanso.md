# Canonical Prompts vs Espanso

Taurcode separates canonical prompt authoring from target package output.

## Canonical prompts are the source of truth

The canonical Taurcode prompt package is a set of human-editable Markdown files under `prompts/taurcode/`. These files carry prompt text plus human-facing metadata such as `id`, `name`, `description`, and `keyword`.

This format is optimized for review:

- each prompt can be edited as a small Markdown source file
- frontmatter provides machine-readable fields
- Git diffs stay focused on author intent
- validation can catch missing fields and duplicate triggers before export

## Espanso is an output target

Espanso packages are generated views of canonical prompts. Taurcode exports prompt `keyword` values to Espanso `trigger` values and prompt bodies to Espanso `replace` values.

This boundary keeps Espanso-specific package concerns out of canonical prompt authoring while still allowing Taurcode prompts to be used through Espanso.

## Why not use Espanso as the only source?

Plain Espanso `package.yml` does not represent every Taurcode prompt annotation. For example, curated prompt names and descriptions are useful in a source package but do not have a direct place in a simple Espanso match.

Keeping Markdown prompts canonical lets Taurcode preserve authoring metadata without pretending that Espanso can roundtrip fields it does not model.

## Where package metadata belongs

Espanso package-level metadata is still source-controlled when it matters. Taurcode stores curated Espanso metadata assets under `prompts/<package>/espanso/`, separate from prompt Markdown files. Export copies supported assets into generated package output.

This keeps prompt content, prompt metadata, and target package metadata in predictable locations.
