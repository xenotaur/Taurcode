---
id: AUDIT-DOCS-2026-08-25
audit_type: docs
schema_version: 1
status: proposed
repo_root: .
project_root: project
docs_root: docs
control_root: project
package_roots:
  - src/taurcode
framework: diataxis
recommended_next_prompt: organize_docs
recommended_phase: scaffold
---

# Taurcode Documentation Audit

## Summary

This audit inspected Taurcode's human documentation, prompt packages,
generated Espanso package documentation, repo-local Claude/LRH skills, source
docstrings, and LRH project-control-plane artifacts.

The human-facing `docs/` tree is already organized into a Diataxis-inspired
structure with tutorial, how-to, reference, and explanation sections. The main
documentation risks are now narrower: `README.md` has become a broad mixed
document that duplicates more focused docs, the `taurcode show` command is not
surfaced from the docs index, the repo-local docs-audit skill references a
missing artifact convention document, and most public Python modules do not
provide docstrings for API-reference readers.

Discovery and evidence commands:

- `rg --files -g '*.md' -g '*.rst' -g '*.txt' -g '*.ipynb' -g '!*__pycache__*' -g '!build/**' -g '!dist/**' -g '!*.egg-info/**'`
- `find . -maxdepth 3 -type d | sort`
- `find docs doc documentation wiki pages examples notebooks tutorials demos -maxdepth 3 -type f 2>/dev/null | sort`
- `taurcode --help` and subcommand `--help` output for all current CLI commands
- Markdown internal-link scan with pure fragments skipped, fragments stripped,
  and targets resolved relative to containing files
- Python AST docstring survey for `src/taurcode/*.py`

Counts:

- Markdown files discovered: 277
- Tutorial: 1
- How-to: 5
- Reference: 38
- Explanation: 2
- Mixed: 58
- Meta/control-plane: 173
- True stale internal links: 0
- Ambiguous/example links: 2
- Evidence-backed gap findings: 4

## Scope and roots inspected

Repository root:

- `.`

Human docs root:

- `docs/`

Package/code roots:

- `src/taurcode/`
- `tests/`
- `scripts/`
- `pyproject.toml`

Prompt package roots and generated package docs:

- `prompts/taurcode/`
- `prompts/lrh/`
- `prompts/examples/`
- `exports/espanso/taurcode/`
- `exports/espanso/lrh/`
- `tests/fixtures/roundtrip/`

Project control plane:

- `project/`

Repo-local skill documentation:

- `.claude/skills/`

Top-level documentation and meta files:

- `README.md`
- `AGENTS.md`
- `PROMPTS.md`
- `STYLE.md`
- `.jules/bolt.md`
- `constraints-dev.txt`

Directories checked and absent:

- `doc/`
- `documentation/`
- `wiki/`
- `pages/`
- `examples/`
- `notebooks/`
- `tutorials/`
- `demos/`

## Current documentation inventory

Human-facing docs under `docs/`:

- `docs/README.md`
- `docs/tutorials/create-your-first-taurcode-package.md`
- `docs/how-to/import-an-espanso-package.md`
- `docs/how-to/check-espanso-roundtrip-fidelity.md`
- `docs/how-to/debug-espanso-import-errors.md`
- `docs/how-to/publish-a-taurcode-release.md`
- `docs/how-to/best-practices/prompting-best-practices.md`
- `docs/how-to/best-practices/reliable-ai-editing.md`
- `docs/reference/canonical-prompt-format.md`
- `docs/reference/espanso-integration.md`
- `docs/explanations/canonical-prompts-vs-espanso.md`
- `docs/explanations/semantic-vs-textual-fidelity.md`

Top-level repo documentation:

- `README.md`
- `AGENTS.md`
- `PROMPTS.md`
- `STYLE.md`

Prompt and package documentation:

- `prompts/taurcode/*.md`
- `prompts/taurcode/espanso/README.md`
- `prompts/lrh/*.md`
- `prompts/lrh/espanso/README.md`
- `prompts/examples/*.md`
- `exports/espanso/taurcode/README.md`
- `exports/espanso/lrh/README.md`

Control-plane documentation:

- `project/*/README.md` files for goal, roadmap, memory, workstreams, work
  items, focus, status, audits, executions, design proposals, and decisions
- `project/design/*.md` and `project/design/proposals/**/*.md`
- `project/work_items/**/*.md`
- `project/workstreams/**/*.md`
- `project/evidence/*.md`
- `project/executions/**/*.md`
- `project/context/*.md`
- `project/guardrails/*.md`

Repo-local skill docs:

- `.claude/skills/*/SKILL.md`
- `.claude/skills/*/references/*.md`

CLI documentation surface observed from help output:

- `taurcode export espanso [--prompts PROMPTS] [--output OUTPUT]`
- `taurcode import espanso --input INPUT [--output OUTPUT] [--merge]`
- `taurcode lint prompts [--prompts PROMPTS]`
- `taurcode lint espanso --input INPUT`
- `taurcode format prompts [--prompts PROMPTS] [--check]`
- `taurcode roundtrip espanso --input INPUT [--prompts PROMPTS]`
- `taurcode install espanso [--prompts PROMPTS] [--packages-dir PACKAGES_DIR] [--restart]`
- `taurcode validate [--prompts PROMPTS]`
- `taurcode show [--prompts PROMPTS] keyword`

## Current project and package layout

Taurcode follows the expected source layout:

- Tool code lives under `src/taurcode/`.
- Tests live under `tests/`.
- Canonical prompt packages live under `prompts/taurcode/` and `prompts/lrh/`.
- Espanso package exports live under `exports/espanso/`.
- Human docs live under `docs/`.
- LRH project-control-plane files live under `project/`.

`pyproject.toml` exposes the console script:

```toml
[project.scripts]
taurcode = "taurcode.cli:main"
```

The package does not expose `python -m taurcode`; `python -m taurcode` fails
because there is no `taurcode.__main__`. The implemented module invocation is
`python -m taurcode.cli`, and the installed console script is `taurcode`.

Current project status says the canonical prompt and Espanso roundtrip
foundation is complete and that Diataxis-style documentation exists. Current
focus says future work should preserve the completed foundation and keep
project-plane cleanup separate from runtime feature work.

## Diataxis classification

Tutorial:

- `docs/tutorials/create-your-first-taurcode-package.md` - clear beginner
  walkthrough that creates a prompt, validates, exports, roundtrips, and cleans
  up.

How-to:

- `docs/how-to/import-an-espanso-package.md`
- `docs/how-to/check-espanso-roundtrip-fidelity.md`
- `docs/how-to/debug-espanso-import-errors.md`
- `docs/how-to/publish-a-taurcode-release.md`
- `docs/how-to/best-practices/prompting-best-practices.md`

Reference:

- `docs/reference/canonical-prompt-format.md`
- `docs/reference/espanso-integration.md`
- Prompt source files under `prompts/taurcode/` and `prompts/lrh/`, treated as
  source/reference artifacts for expansion triggers.
- `prompts/*/espanso/README.md` and `exports/espanso/*/README.md`, treated as
  package reference/readme artifacts.
- Roundtrip fixture prompt files under `tests/fixtures/roundtrip/`.

Explanation:

- `docs/explanations/canonical-prompts-vs-espanso.md`
- `docs/explanations/semantic-vs-textual-fidelity.md`

Mixed:

- `README.md` mixes overview, tutorial snippets, how-to procedures, reference
  behavior, release instructions, and design pointers.
- `docs/how-to/best-practices/reliable-ai-editing.md` is mostly explanatory but
  also contains reusable templates, workflow steps, checklists, and examples.
- `.claude/skills/*/SKILL.md` and `.claude/skills/*/references/*.md` mix
  reference, procedural how-to, workflow policy, and examples for Claude/LRH
  users.

Meta:

- `docs/README.md` is a navigation index.
- `AGENTS.md`, `PROMPTS.md`, `STYLE.md`, `.jules/bolt.md`, and
  `constraints-dev.txt` are contributor/process/tooling meta documents.
- All `project/` files are LRH project-control-plane artifacts and should not
  be forced into the four human-doc quadrants.

## Navigation findings

The main `docs/README.md` index links the current tutorial, how-to, reference,
and explanation docs, but it does not link a dedicated CLI reference because no
such page currently exists.

`README.md` now points to the docs index and to some specific docs, but it also
contains detailed content that overlaps with more focused pages:

- Import and merge behavior overlaps with `docs/how-to/import-an-espanso-package.md`.
- Roundtrip behavior overlaps with
  `docs/how-to/check-espanso-roundtrip-fidelity.md` and
  `docs/explanations/semantic-vs-textual-fidelity.md`.
- Prompt format, validation, lint, and formatting behavior overlap with
  `docs/reference/canonical-prompt-format.md`.
- Espanso integration, install behavior, and `force_clipboard` overlap with
  `docs/reference/espanso-integration.md`.
- Release mechanics overlap with `docs/how-to/publish-a-taurcode-release.md`.

`taurcode show` is documented in `README.md` and present in CLI help, but it is
not discoverable from `docs/README.md` and has no focused how-to or reference
page. This is a navigation gap for users who start in the docs tree.

The repo-local `.claude/skills/lrh-doc-audit/SKILL.md` says the docs audit
artifact schema is defined in `docs/reference/docs-audit-artifact-convention.md`,
but that path does not exist. This creates a navigation and reference gap for
future users of the skill inside this repository.

## Accuracy findings

The current `docs/` pages broadly match the implemented CLI surface:

- `taurcode --help` lists `export`, `lint`, `format`, `roundtrip`, `install`,
  `import`, `validate`, and `show`.
- The `docs/` tree covers export/import/roundtrip/lint/format/install and
  canonical prompt behavior.
- `README.md` covers `show`, including default `--prompts all` behavior.

Accuracy gaps and risks:

- The README's Espanso metadata section says local installation and sync are
  out of scope. Its macOS installation section documents the supported
  `taurcode install espanso` command. The Espanso reference confirms that
  installation is supported on macOS and that continuous sync is out of scope.
  See [Espanso metadata ownership](../../../README.md#espanso-metadata-ownership),
  [Install into Espanso (macOS)](../../../README.md#install-into-espanso-macos),
  and the [Espanso integration reference](../../../docs/reference/espanso-integration.md#out-of-scope).
- `python -m taurcode` is not a supported invocation in the current package.
  The supported module invocation is `python -m taurcode.cli`, and the
  installed console script is `taurcode`.
- The audit skill's reference to
  `docs/reference/docs-audit-artifact-convention.md` is inaccurate for the
  current repo because that file is absent.
- Public Python modules are not consistently documented with module or public
  symbol docstrings. An AST survey found module docstrings only in
  `src/taurcode/__init__.py` and `src/taurcode/espanso_install.py`; most public
  functions and data classes in the remaining modules lack docstrings. This is
  a reference gap only if Taurcode intends those modules as a public Python API.

## Stale or ambiguous links

The stale-link scan found no true stale internal Markdown links in human docs,
README files, prompt package docs, or project-control files.

Two ambiguous/example links were reported:

- `.claude/skills/lrh-doc-audit/SKILL.md:118` contains the literal example
  shape `[text](path)`.
- `.claude/skills/lrh-doc-audit/references/audit-requirements.md:74` contains
  the same literal example shape.

These are not broken navigation links in ordinary prose. They are examples of
Markdown link syntax and should be ignored by consumers, escaped, or fenced if a
future link checker treats them as failures.

## Project-control-plane vs human-docs boundary

The `project/` tree is dense and healthy as a control plane, but it is not the
same thing as human product documentation.

Human documentation should continue to live under `docs/` and top-level
orientation files. LRH planning, evidence, execution records, work items,
workstreams, design proposals, guardrails, status, and focus should continue to
live under `project/` and be classified as meta/control-plane content.

The docs audit should not reorganize control-plane artifacts into the Diataxis
tree. Where a design proposal or work item explains user-facing behavior, the
human docs may cite it as rationale, but the proposal itself remains part of the
project control plane.

Repo-local `.claude/skills/` files are also not primary product documentation.
They are operational instructions for Claude/LRH workflows and should be
classified as mixed workflow/reference material. The missing audit artifact
convention is still relevant because the repo-local skill points human and
agent users to a nonexistent path.

## Recommended target documentation structure

Keep the existing `docs/` layout:

```text
docs/
  README.md
  tutorials/
  how-to/
    best-practices/
  reference/
  explanations/
```

Add focused reference coverage rather than reshaping the whole tree:

```text
docs/reference/
  canonical-prompt-format.md
  espanso-integration.md
  taurcode-cli.md
  docs-audit-artifact-convention.md
```

Recommended role split:

- `README.md`: short project overview, quick install/development orientation,
  common commands, and links into `docs/`.
- `docs/README.md`: complete navigation index for tutorials, how-to guides,
  reference pages, and explanations.
- `docs/reference/taurcode-cli.md`: current CLI command and option reference
  based on `taurcode --help`.
- `docs/reference/docs-audit-artifact-convention.md`: stable schema/reference
  for LRH docs audit artifacts, satisfying the repo-local skill's documented
  expectation.
- Existing how-to pages: focused operational recipes.
- Existing explanation pages: conceptual rationale and trade-offs.

## Recommended phased PRs

Phase 1 - Reference and navigation hygiene:

- Add `docs/reference/taurcode-cli.md`.
- Add `docs/reference/docs-audit-artifact-convention.md`.
- Update `docs/README.md` to link both new reference pages.
- Lightly reduce `README.md` duplication by pointing detailed CLI behavior to
  the new CLI reference.

Phase 2 - README slimming:

- Move or remove detailed import/export/roundtrip/release material from
  `README.md` where it duplicates focused docs.
- Keep only the quickest orientation and links from `README.md` to the docs
  tree.
- Preserve any content not already represented in focused docs before removing
  it from the README.

Phase 3 - API reference decision:

- Decide whether `src/taurcode/` is intended as public Python API surface or
  only as implementation behind the CLI.
- If public, add module and public-symbol docstrings or generated API reference.
- If private, document the supported integration contract as the CLI and prompt
  file formats, and do not treat missing public docstrings as a docs gap.

Phase 4 - Skill-doc link-check polish:

- Fence or escape literal `[text](path)` examples in the repo-local docs-audit
  skill files if automated link checkers begin reporting them as failures.

## Proposed first PR scope

Create a small documentation hygiene PR with the following concrete changes:

1. Add `docs/reference/taurcode-cli.md` as a compact CLI reference covering the
   current command surface from `taurcode --help`:
   `export`, `import`, `lint`, `format`, `roundtrip`, `install`, `validate`,
   and `show`.

2. Add `docs/reference/docs-audit-artifact-convention.md` documenting the v1
   audit artifact frontmatter and required headings used by `/lrh-doc-audit`.

3. Update `docs/README.md` to link both new reference pages and to explicitly
   surface `taurcode show`.

4. Lightly edit `README.md` so it remains the project orientation page and
   points detailed CLI behavior to `docs/reference/taurcode-cli.md`, without
   changing command semantics or removing unique guidance.

5. Correct the scope statement in the README's "Espanso metadata ownership"
   section. State that `taurcode install espanso` supports local installation on
   macOS, link to "Install into Espanso (macOS)", and clarify that continuous
   sync is out of scope.

This first PR should not move files, reorganize the docs tree, alter prompt
sources, change `project/` control-plane state, or edit runtime code.

## Risks and cautions

- The README has accumulated useful details. Slimming it should happen
  carefully so unique behavior notes are preserved in focused docs before they
  are removed from the top-level file.
- Adding `docs/reference/docs-audit-artifact-convention.md` should align with
  the repo-local skill text and the v1 schema summarized in
  `.claude/skills/lrh-doc-audit/references/audit-requirements.md`.
- Do not treat `project/` as missing Diataxis documentation. It is a separate
  LRH control plane, and reorganizing it would be project-state work rather
  than docs hygiene.
- Do not treat sparse Python docstrings as blocking unless Taurcode declares a
  supported Python API beyond the console script and file formats.
- The two ambiguous `[text](path)` examples are safe inline cleanup candidates
  only if a future automated link-check job needs them escaped or fenced.

## Validation commands for follow-up PRs

Run documentation/content checks:

```bash
rg -n '\]\([^)#][^)]+\)' README.md docs project .claude/skills
```

Run Taurcode validation relevant to command examples:

```bash
scripts/develop
scripts/test
taurcode --help
taurcode validate --prompts prompts/taurcode
taurcode lint prompts --prompts prompts/taurcode
taurcode format prompts --prompts prompts/taurcode --check
taurcode export espanso --prompts prompts/taurcode --output tmp/exported/taurcode
taurcode roundtrip espanso --input tmp/exported/taurcode --prompts prompts/taurcode
```

Run LRH project-plane validation after audit or control-plane changes:

```bash
lrh validate
```
