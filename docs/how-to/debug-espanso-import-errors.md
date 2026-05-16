# Debug Espanso Import Errors

Use this guide when `taurcode import espanso` fails or produces warnings.

## 1. Run the Espanso linter directly

```bash
taurcode lint espanso --input path/to/espanso/package
```

The same preflight diagnostics also run during import, but running the linter directly gives a smaller feedback loop while fixing source files.

## 2. Fix source package errors manually

Taurcode does not silently rewrite, normalize, or repair source Espanso files. Fix the package manually and rerun linting.

Common blocking errors include:

- an input directory with no `package.yml`
- invalid UTF-8
- malformed YAML
- parser-sensitive invisible Unicode line separators
- invalid or missing required package metadata in generated package output

## 3. Review warnings before importing

Warnings do not block import by default, but they often indicate stale or low-quality metadata. Examples include placeholder manifest values, tiny README files, README content that does not mention the package, and homepage values that are not HTTP(S) URLs.

## 4. Re-run import after lint passes

For a fresh staged import:

```bash
taurcode import espanso --input path/to/espanso/package --output prompts/imported
```

For an intentional merge into curated prompts:

```bash
taurcode import espanso --input path/to/espanso/package --output prompts/taurcode --merge
```

## 5. Validate the imported prompts

```bash
taurcode validate --prompts prompts/imported
taurcode lint prompts --prompts prompts/imported
```

If you imported into a different directory, replace `prompts/imported` with that directory.

## Notes on unsupported matches

The importer converts simple static Espanso matches with only `trigger` and `replace` into canonical Markdown prompts. More complex match entries are not converted into normal prompt files by the simple importer path; review any fallback output before curating the result.
