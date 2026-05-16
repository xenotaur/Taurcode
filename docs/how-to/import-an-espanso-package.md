# Import an Espanso Package

Use this guide when you have an Espanso package and want to convert it into Taurcode Markdown prompt files.

## Import into a staging directory

For a first import, write into a staging directory instead of directly overwriting curated prompts:

```bash
taurcode import espanso --input path/to/package.yml --output prompts/imported
```

`--input` may point at a direct `package.yml` file or at a package directory containing `package.yml`.

When importing from a package directory, Taurcode also copies supported package metadata assets into `<output>/espanso/` when they exist:

- `_manifest.yml`
- `README.md`
- `LICENSE`

Review the staged Markdown files before treating them as canonical prompt sources.

## Import from a local Espanso package directory

Run the preflight linter before importing a local package:

```bash
taurcode lint espanso --input ~/Library/Application\ Support/espanso/match/packages/taurcode/
taurcode import espanso --input ~/Library/Application\ Support/espanso/match/packages/taurcode/ --output prompts/imported
```

The linter reports malformed YAML, invisible parser-sensitive line separators, missing package files, and metadata issues before import attempts to convert matches.

## Merge updates into curated prompts

Use `--merge` only when you intentionally want to update an existing curated prompt directory from an Espanso package:

```bash
taurcode import espanso --input build/espanso/taurcode --output prompts/taurcode --merge
```

Merge import matches existing prompts by `keyword` first, then by the generated filename stem. It preserves curated frontmatter such as `name`, `description`, `id`, comments, field order, and unknown fields where practical, while updating Espanso-derived trigger/body data.

## After importing

Validate and review the result:

```bash
taurcode validate --prompts prompts/imported
taurcode lint prompts --prompts prompts/imported
taurcode format prompts --prompts prompts/imported --check
```

If you merged into `prompts/taurcode`, run the same commands against `prompts/taurcode` and review the Git diff before exporting.
