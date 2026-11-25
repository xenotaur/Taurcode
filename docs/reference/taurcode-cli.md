# Taurcode CLI Reference

The console command is `taurcode`. The equivalent Python module invocation is
`python -m taurcode.cli`. Run `taurcode --help` to list commands, or append
`--help` to a command or subcommand for its usage.

Relative paths are resolved from the working directory. Examples and default
paths below assume you run the command from the Taurcode checkout root.
For every command except `show`, `--prompts DIR` defaults to
`prompts/taurcode` where that option is accepted.

## Commands

| Invocation | Behavior |
| --- | --- |
| `taurcode export espanso [--prompts DIR] [--output DIR]` | Validates canonical prompts and writes an Espanso package. The output directory defaults to `build/espanso/taurcode`, even when `--prompts` points to another corpus. |
| `taurcode import espanso --input PATH [--output DIR] [--merge]` | Imports an Espanso package into Markdown. The output directory defaults to `prompts/imported`. `--merge` updates an existing prompt directory and preserves curated metadata where possible. |
| `taurcode lint espanso --input PATH` | Checks Espanso parser safety and package metadata. Errors fail the command. Warnings alone do not. |
| `taurcode lint prompts [--prompts DIR]` | Checks canonical Markdown prompt sources. Errors fail the command. Warnings alone do not. |
| `taurcode format prompts [--prompts DIR] [--check]` | Applies conservative prompt formatting. `--check` makes no writes and exits with status `1` if any file would change. |
| `taurcode roundtrip espanso --input PATH [--prompts DIR]` | Compares the Espanso package with canonical prompt semantics. Exit status `0` indicates equivalence and `1` indicates differences or a processing error. |
| `taurcode install espanso [--prompts DIR] [--packages-dir DIR] [--restart]` | Exports and installs the package into the local Espanso configuration on macOS. See [Install](#install) for defaults and restart behavior. |
| `taurcode validate [--prompts DIR]` | Loads and validates a canonical prompt package, including required fields and unique IDs and keywords. |
| `taurcode show [--prompts DIR] KEYWORD` | Prints the body of an exact keyword match. See [Show](#show) for the `all` value and search behavior. |

For Espanso import, lint, and roundtrip, `--input PATH` accepts an Espanso
package directory or a direct `package.yml` path. For Espanso export, the
basename of `--output DIR` must match the package name in a curated
`_manifest.yml`, if present. See the
[Espanso integration reference](espanso-integration.md) for package metadata,
supported match shapes, and comparison behavior. See the
[canonical prompt format](canonical-prompt-format.md) for prompt fields,
validation, and formatting rules.

## Install

`install espanso` supports macOS. `--packages-dir` defaults to
`~/Library/Application Support/espanso/match/packages/`. The command exports
to a staging directory, then replaces the installed package after export and
build lint succeed. `--restart` runs `espanso restart` after installation and
requires `espanso` on `PATH`. With the default options, Taurcode prints the
restart command for you to run. Continuous sync is out of scope. For the
package naming rules and the manual workflow on other platforms, see the
[Espanso install reference](espanso-integration.md#install-command).

## Show

`show` matches `KEYWORD` exactly against prompt frontmatter, including the
leading `:` used by canonical keywords. It writes the matching prompt body to
stdout. Zero or multiple matches produce a diagnostic on stderr and exit status
`1`.

Omitting `--prompts` or passing `--prompts all` searches the explicit canonical
corpus list, currently `prompts/taurcode` and `prompts/lrh`. Example and staging
directories are excluded from that list. Passing a directory searches only
that directory.

```bash
taurcode show :lrh-implement
taurcode show :lrh-implement --prompts all
taurcode show :lrh-implement --prompts prompts/lrh
```
