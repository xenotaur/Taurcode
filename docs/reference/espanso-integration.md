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

## Install command

```bash
taurcode install espanso --prompts prompts/taurcode
```

macOS only for now. Install re-exports the canonical prompt corpus straight
into Espanso's local match-packages directory
(`~/Library/Application Support/espanso/match/packages/<name>/`), so a merged
exporter or prompt change can be made live in one step instead of the manual
re-export-and-copy dance below. On any non-macOS platform the command prints an
unsupported-platform message and exits non-zero rather than guessing a path;
export the package with `taurcode export espanso` and copy it into place
manually there.

The installed directory `<name>` is derived from the curated
`_manifest.yml` `name:` field (defaulting to `taurcode`), so the installed
directory name and the manifest name always agree. There is no `--name` flag,
and install never rewrites curated metadata: the installed package is
byte-identical to what `taurcode export espanso` produces.

Options:

- `--packages-dir <dir>` — install into a non-default macOS match-packages
  directory (find yours with `espanso path packages`). Overrides are still
  macOS-only.
- `--restart` — run `espanso restart` after installing so the change takes
  effect immediately. Off by default: without it, install is pure file I/O and
  prints the `espanso restart` command for you to run. With it, a missing
  `espanso` binary on `PATH` is a clear error, not a crash.

Install exports into a staging directory first and replaces the live package
only after the export and its build lint both succeed, so a failed export
leaves an existing installed package byte-identical to its previous state.

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

On macOS, Taurcode installs generated packages into the local Espanso
configuration via `taurcode install espanso` (see "Install command" above).
Taurcode does not install on non-macOS platforms, continuously sync with
Espanso, validate network homepages, or support arbitrary advanced Espanso
match behavior as canonical prompt semantics.

### Keeping an installed package in sync

On macOS, `taurcode install espanso --restart` is the preferred way to keep an
installed package current: it re-exports the canonical corpus into Espanso's
match-packages directory and restarts Espanso in one step. Run it after merging
any change to `prompts/taurcode/` or the exporter. Without an install or sync
step, a package sitting in Espanso's match directory is a plain, one-time
snapshot — nothing detects or re-generates it when the repository changes, so
an installed copy can silently go stale with no error or warning.

If the change is to exporter behavior itself (not just prompt content), first
make sure the `taurcode` command on your `PATH` actually reflects the current
checkout — a stale or non-editable install will silently keep running the old
exporter and reproduce the same drift this section exists to prevent. Run
`scripts/develop` (per the "Operability guardrails" in `AGENTS.md`) to install
in editable mode, or invoke Taurcode directly from the checkout with
`python -m taurcode.cli` instead of the bare `taurcode` command.

The equivalent manual steps, which `taurcode install espanso` automates, are a
re-export into the match directory followed by a restart:

```bash
python -m taurcode.cli export espanso --prompts prompts/taurcode --output "$HOME/Library/Application Support/espanso/match/packages/taurcode"
espanso restart
```

(Adjust the output path for the actual directory name if you installed
Taurcode's package under a different one, and for your platform's Espanso match
directory on non-macOS systems, where the install command does not run.)
