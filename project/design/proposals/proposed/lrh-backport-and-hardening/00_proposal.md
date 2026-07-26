---
id: lrh-backport-and-hardening
type: design_proposal
title: LRH Prompt Backport (Espanso) and Taurcode PyPI Release Hardening
status: proposed
created_on: 2026-07-26
updated_on: 2026-07-26
implementation_status: not_started
implemented_by: []
supersedes: []
superseded_by: null
related_design:
  - project/design/proposals/adopted/espanso-match-force-clipboard/00_proposal.md
  - project/work_items/resolved/WI-DOCUMENT-LIFECYCLE-SNIPPETS.md
  - prompts/taurcode/implement.md
  - prompts/taurcode/lrh-template-review.md
---

# LRH Prompt Backport (Espanso) and Taurcode PyPI Release Hardening

## Summary

This proposal backports proven LRH slash-command skills into short, paste-able
`:lrh-` Espanso trigger snippets, shipped as a new package (`lrh`) separate
from the existing `taurcode` package, sourced for now from `prompts/lrh/`
inside this repo. In parallel, it hardens Taurcode's own release tooling to
the point of an actual PyPI release, using LRH's own already-proven release
pipeline as the concrete template.

## Background / Motivation

`prompts/taurcode/implement.md` is a hand-authored backport of `/lrh-implement`
as `:implement` — the only LRH slash-command skill with a short-trigger,
paste-able form today. Other proven LRH skills (`/lrh-review-response`,
`/lrh-confirm-fixes`, `/lrh-closeout`, and others as judged valuable) have no
equivalent. `:lrh-template-review` (`prompts/taurcode/lrh-template-review.md`)
already establishes that LRH-adjacent content can live in Taurcode's own
corpus, and that an `lrh-` prefix is the established disambiguation
convention for it — this proposal generalizes that precedent rather than
introducing a new one.

Reaching parity requires answering where the source files live, how they're
packaged for Espanso, and what happens to the existing `taurcode` package's
namespace as a result. Espanso's package manager only supports
`install | list | uninstall | update` (confirmed via `espanso package
--help`) — there is no `enable`/`disable` — so package granularity is a real
constraint, not a stylistic choice.

Separately, actually publishing Taurcode to PyPI is a longstanding, explicit
precondition: `scripts/publish` still unconditionally exits 1 with "Publishing
not yet supported until taurcode is more heavily tested / fleshed out"
(`scripts/publish:10`). This has been true since the script was written, with
no defined completion criteria. LRH has already built and exercised a working
release pipeline; Taurworks and Prosoc carry the *identical* unresolved
`scripts/publish` stub. Hardening Taurcode's pipeline to LRH's proven shape is
both the blocker for eventually moving `prompts/lrh/` into LRH's own repo as
a real dependency, and a reusable template for the sibling fleet.

## Prior Art Check

### Duplication search
- In-repo: No existing implementation found. Related: `project/design/proposals/adopted/espanso-match-force-clipboard/00_proposal.md` (a prior, narrower Espanso-export feature — not overlapping in scope).
- Sibling repos: LRH has no Espanso tooling of any kind. Taurworks and Prosoc share the identical unresolved `scripts/publish` stub text as Taurcode; LCATS is more bespoke (real runtime deps, an existing `git+https`-pinned dependency, NLP extras).
- External libraries: None identified as a wholesale replacement — this proposal composes existing tools (Espanso, setuptools-scm, `pypa/gh-action-pypi-publish`) rather than adopting a single library in their place.
- Recommendation: Proceed.

### Demand search
- Work items: None found proposing this exact scope. Tangential: `project/work_items/resolved/WI-DOCUMENT-LIFECYCLE-SNIPPETS.md` documents `:lrh-template-review` but doesn't propose a package or backport.
- Proposals: None found.
- Backlog: No `project/design/backlog.md` exists in this repo.
- Recommendation: No action.

## Design Decisions

### Decision 1: Trigger naming
Options considered:
- Bare triggers (`:review-response`, `:confirm-fixes`) — risks future collisions with personal `taurcode` triggers or other installed packages.
- `:lrh-`-prefixed triggers — namespaces by origin.

**Chosen: `:lrh-` prefix** (`:lrh-implement`, `:lrh-review-response`,
`:lrh-confirm-fixes`, `:lrh-closeout`, …), matching the existing
`:lrh-template-review` precedent already shipped in
`prompts/taurcode/lrh-template-review.md`.

### Decision 2: Package separation
Options considered:
- Fold `:lrh-` triggers into the existing `taurcode` package.
- Ship a separate `lrh` Espanso package.

**Chosen: separate `lrh` package.** Espanso's package manager (`espanso
package --help`: `install | list | uninstall | update`, no `enable`/`disable`)
makes install/uninstall the only real opt-in/opt-out unit. A user who wants
personal `taurcode` triggers but not the `lrh` set (or vice versa) can only
get that by installing/uninstalling separate packages — folding both into
one package would make that impossible. Mechanically this costs nothing new:
`export_espanso()`'s package name is `output.name` (`espanso_export.py:56`),
and `load_prompts()` already walks whatever directory it's given
(`prompt_loader.py:52-53`).

### Decision 3: Manifest curation
Options considered:
- Rely on `espanso_metadata.generate_default_manifest()`'s generated default.
- Hand-write `prompts/lrh/espanso/_manifest.yml` up front.

**Chosen: hand-write the manifest up front.**
`generate_default_manifest()` hardcodes `homepage =
"https://github.com/xenotaur/Taurcode"` (`espanso_metadata.py:5`) — left
unaddressed, a generated `lrh` package would silently claim Taurcode's own
homepage for content describing LRH. `export_espanso_metadata_assets()`
already copies a curated `_manifest.yml`/`README.md`/`LICENSE` from
`<source_dir>/espanso/` when present (`espanso_export.py:23-38`), so this is
a content decision, not a code change — write `prompts/lrh/espanso/
{_manifest.yml,README.md,LICENSE}` as a real package (matching
`prompts/taurcode/espanso/`'s shape) rather than leaving it to the default.

### Decision 4: Source location (for now)
Options considered:
- Author `prompts/lrh/` inside Taurcode's own repo.
- Author the source directly in LRH's repo, with Taurcode as a pip/pipx
  dependency (via a local checkout, a pinned `git+https` install — a live
  pattern already in use elsewhere in this fleet, see LCATS's
  `gutenbergpy @ git+https://github.com/xenotaur/gutenbergpy.git@LCATS/TitleFix`
  dependency — or a real PyPI dependency once published).

**Chosen: `prompts/lrh/` inside Taurcode's own repo, for now.** The current
user of this backport is its sole author, so this unblocks dogfooding
immediately with zero cross-repo dependency mechanics. It extends an existing
pattern rather than inventing one: `:lrh-template-review` already
demonstrates LRH-adjacent content living in Taurcode's corpus, and
`AGENTS.md:37-41` documents that Taurcode is itself managed by LRH's own
control-plane tooling — this is not a foreign graft onto an unrelated
project.

### Decision 5: `taurcode show` CLI feature
Options considered:
- No non-Espanso consumption path (source-control browsing only).
- Add a CLI command to print a snippet body to stdout.

**Chosen: add `taurcode show <keyword> --prompts <dir|all>`.** Today's
`cli.py` subcommands are `export | install | import | lint | format |
roundtrip | validate` (`cli.py:24-89`) — none prints a snippet body. This
serves users who don't run Espanso at all. `--prompts` follows the existing
convention used by every other subcommand (a directory path,
e.g. `cli.py:26-33`); unset or `--prompts=all` is new behavior — it requires
enumerating every top-level `prompts/*/` directory and merging results, since
`load_prompts()` today only ever walks the one directory it's given
(`prompt_loader.py:52-53`).

### Decision 6: Sequencing and gate
Options considered:
- Gate all `:lrh-` prompt authoring on Taurcode's release hardening.
- Let dogfooding continue independently, with hardening as a parallel,
  separately-scoped effort.

**Chosen: run them in parallel, not as a strict pipeline.** Dogfooding and
adding new `:lrh-` prompt files to `prompts/lrh/` continues freely and is not
gated on the hardening work. Separately, Taurcode is hardened for an actual
PyPI release, using LRH's own proven pipeline as the concrete target shape:

| Piece | Taurcode today | LRH (target shape) |
|---|---|---|
| Versioning | Static `version = "0.1.0"` (`pyproject.toml`) | `dynamic = ["version"]` + setuptools-scm from git tags |
| `scripts/version` | `""` / `tools` only (`scripts/version`) | + `verify <tag>` subcommand |
| Smoke test | Plain `unittest discover` (`scripts/smoke`) | `scripts/release-smoke <tag> --strict-isolation` — isolated venv build/install/invoke + `.pth`/editable-leak check |
| CI workflows | `coverage.yml, lint.yml, meta.yml, smoke.yml, tests.yml` | + `release.yml` (tag-triggered) and `testpypi-rehearsal.yml` (`workflow_dispatch`) |
| PyPI auth | N/A — `scripts/publish` exits 1 (`scripts/publish:10`) | Trusted Publishing (OIDC), no stored token |
| Publish gate | N/A | Required-reviewer gate on the `pypi` GitHub Environment; `testpypi` left open |

LRH's own hardening was tracked as real work items, used here as scope
precedent: `WI-RELEASE-TAG-CI`, `WI-RELEASE-SMOKE-ISOLATION-AUDIT`,
`WI-RELEASE-PUBLISH-APPROVAL-GATE`, and `WI-ASSIST-INSTALLABILITY-HARDENING`.
The last of these verifies package-data template loading post-install, which
is judged **not directly applicable** to Taurcode (it ships no runtime
package-data resources) — the port should carry over the generically-useful
core of `release_smoke.py` (isolated build → install → invoke → leak-check)
and skip the template-loading-specific checks.

Best practices this design follows, each independently verified reachable:
- [PyPI Trusted Publishers](https://docs.pypi.org/trusted-publishers/) — OIDC over stored tokens.
- [setuptools-scm usage](https://setuptools-scm.readthedocs.io/en/latest/usage/) — dynamic versioning from tags.
- [Packaging Guide: using TestPyPI](https://packaging.python.org/en/latest/guides/using-testpypi/) — rehearse before releasing.
- [semver.org](https://semver.org/) — `vMAJOR.MINOR.PATCH` tags.
- [Packaging Guide: writing pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/) — single declarative source.
- [GitHub Docs: environments for deployment](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment) — required-reviewer gate on an irreversible action.
- [Espanso: creating a package](https://espanso.org/docs/packages/creating-a-package/) — `_manifest.yml` + `package.yml` shape.

Once Taurcode ships to PyPI **and** the `:lrh-` prompts prove valuable
through dogfooding (a judgment call on usage frequency, triggered personally
by this proposal's author as part of working through releases — not an
automated signal), revisit moving `prompts/lrh/` into LRH's own repo, adding
`taurcode` as a real dependency there, and building whatever further features
that migration needs.

## Non-Goals

- Does not move `prompts/lrh/` into LRH's repo now — that is explicitly
  deferred to the gate in Decision 6.
- Does not decide the fleet-wide skill-extraction ordering — see Open
  Questions.
- Does not perform PyPI Trusted Publisher registration or GitHub Environment
  configuration — both are account-level/repo-admin actions on external
  services that the human author must perform directly; no agent can do
  this on their behalf.
- Does not harden Taurworks, LCATS, or Prosoc directly — it only establishes
  that Taurcode's hardening is a reusable template for the two (Taurworks,
  Prosoc) that share its exact blocker.
- Does not port LRH's full `release_smoke.py` (696 lines) verbatim — only
  the generically-useful isolation-check core, per Decision 6.

## Implementation Plan

This spans multiple, largely independent PRs — treated as workstream-scale
rather than a single work item:

1. `prompts/lrh/` scaffolding: curated manifest + first `:lrh-` prompt files
   (starting from `:implement`, `:lrh-review-response`, `:lrh-confirm-fixes`,
   `:lrh-closeout`).
2. `taurcode show` CLI command.
3. Taurcode release hardening: dynamic versioning migration, trimmed
   `scripts/release-smoke`, `scripts/version verify`, `release.yml` +
   `testpypi-rehearsal.yml`, then the human-performed PyPI Trusted Publisher
   + GitHub Environment configuration, then a TestPyPI rehearsal, then a
   real tagged release.

Items 1–2 have no dependency on item 3 and can land first. Suggest a
companion workstream to sequence these and hold the individual work items.

## Open Questions

- **Fleet-wide skill-extraction ordering (Decision 7, explicitly not
  decided):** should "harden a Python project for PyPI release using LRH's
  pipeline" be (a) built by hand for Taurcode first, then extracted into a
  distributable LRH skill afterward, riding on the already-adopted
  `PROP-LRH-PROJECT-LOCAL-SKILLS` infrastructure (`create-skill`, `src/lrh/
  skills/`, `lrh setup`); (b) designed as a skill first and then applied to
  Taurcode; or (c) built alongside the Taurcode port, treating Taurcode as
  the reference implementation? Deferred — Taurworks and Prosoc share the
  identical blocker, so this has real payoff beyond this proposal, but the
  ordering is a judgment call not yet made.

## Cross-References

- `prompts/taurcode/implement.md` — existing `:implement` backport (precedent).
- `prompts/taurcode/lrh-template-review.md` — existing `:lrh-` prefix precedent.
- `project/design/proposals/adopted/espanso-match-force-clipboard/00_proposal.md` — prior, narrower Espanso-export proposal.
- `project/work_items/resolved/WI-DOCUMENT-LIFECYCLE-SNIPPETS.md` — documents `:lrh-template-review`.
