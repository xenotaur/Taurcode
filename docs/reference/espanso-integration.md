# Espanso Integration Reference

Taurcode treats Espanso as an import/export target for canonical Markdown prompt packages.

## Export command

```bash
taurcode export espanso --prompts prompts/taurcode --output build/espanso/taurcode
```

Export validates prompts, then writes an Espanso package. Each canonical prompt becomes a simple Espanso match with:

- `keyword` mapped to `trigger`
- prompt body mapped to `replace`

Generated package output includes:

- `package.yml`
- `_manifest.yml`
- `README.md`

`LICENSE` is copied only when a curated source license exists.

## Import command

```bash
taurcode import espanso --input path/to/package-or-package.yml --output prompts/imported
```

`--input` accepts either a package directory containing `package.yml` or a direct `package.yml` path. A fresh import writes Markdown prompts into the chosen output directory.

Use merge import only for intentional updates to existing curated prompt sources:

```bash
taurcode import espanso --input build/espanso/taurcode --output prompts/taurcode --merge
```

Merge import matches by existing prompt `keyword` first, then by generated filename stem. Ambiguous matches fail instead of silently choosing a destination.

## Supported Espanso match shape

The simple importer converts static match entries that contain only:

- `trigger`
- `replace`
- `force_clipboard: true` (optional — any other value, such as `false`, is not part of the simple shape and causes the match to fall back to raw import instead of mapping into a canonical prompt)

These map cleanly to Taurcode `keyword`, prompt body, and `targets.espanso.force_clipboard` fields respectively. More complex Espanso constructs are outside the current canonical prompt export model and should be reviewed manually if they appear in imported fallback output.

## Inject vs. Clipboard backend and `force_clipboard`

Espanso's `Auto` backend (the default) delivers a match via simulated keypresses (`Inject`) when its `replace` text is shorter than Espanso's `clipboard_threshold` default (100 characters), and via clipboard paste (`Clipboard`) at or above that threshold. Under `Inject`, a trailing `\n` in the match is sent as an actual simulated Return keypress rather than inserted text — in an application bound to "Enter submits" (a chat input, for example), that synthetic keypress can submit the input prematurely. Matches at or above the threshold are unaffected, since Clipboard-backend paste never generates a synthetic Return keydown.

A prompt can opt out of this per match by setting `targets.espanso.force_clipboard: true` in its frontmatter (see `docs/reference/canonical-prompt-format.md`). Export emits this as Espanso's native `force_clipboard: true` match property, which forces Clipboard-backend delivery for that match regardless of its length or the installing user's own `clipboard_threshold`/`backend` configuration. This is scoped to the single match that needs it — it does not change delivery for any other match in the package.

## Metadata asset layout

Canonical Taurcode packages store supported Espanso package metadata under:

```text
prompts/<package>/espanso/
```

Supported assets are:

- `_manifest.yml`
- `README.md`
- `LICENSE`

Import from a package directory copies those files into `<output>/espanso/` when present. Export copies curated metadata assets from `prompts/<package>/espanso/` into generated output. If no curated `_manifest.yml` or `README.md` exists, export writes conservative generated defaults. If no curated `LICENSE` exists, export omits `LICENSE` and removes stale generated-output license files.

## Espanso linting

Run:

```bash
taurcode lint espanso --input path/to/package-or-package.yml
```

The linter checks parser safety and package metadata. Errors return nonzero. Warnings are non-blocking by default and highlight likely metadata quality issues.

## Roundtrip command

```bash
taurcode roundtrip espanso --input tmp/exported/taurcode --prompts prompts/taurcode
```

The command compares exported Espanso package semantics against canonical prompt semantics. It returns `0` when semantics match and nonzero when differences are found.

Espanso semantic mode compares trigger/body values and supported metadata semantics. It intentionally ignores canonical-only prompt annotations such as `name` and `description`, because plain Espanso package output does not represent those fields.

## Out of scope

Taurcode does not currently install generated packages into a local Espanso configuration, sync with Espanso, validate network homepages, or support arbitrary advanced Espanso match behavior as canonical prompt semantics.

### Keeping a manually-installed package in sync

Because Taurcode has no install or sync mechanism, a package copied into Espanso's local match directory (for example `~/Library/Application Support/espanso/match/packages/<name>/` on macOS) is a plain, one-time snapshot. Nothing detects or re-generates it automatically when `prompts/taurcode/` or the exporter changes — an installed copy can silently go stale relative to the repository, with no error or warning. After merging any change that affects exported behavior, manually re-export and reinstall before assuming the change is live:

```bash
taurcode export espanso --prompts prompts/taurcode --output "$HOME/Library/Application Support/espanso/match/packages/taurcode"
espanso restart
```

(Adjust the output path for your platform's Espanso match directory.) A dedicated install command that automates this is tracked as follow-up work; until it exists, this step is manual.
