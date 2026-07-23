---
id: espanso-match-force-clipboard
type: design_proposal
title: Per-Match `force_clipboard` Opt-In for Espanso Export
status: proposed
created_on: 2026-07-18
updated_on: 2026-07-18
implementation_status: not_started
implemented_by: []
supersedes: []
superseded_by: null
related_design:
  - project/design/proposals/adopted/espanso_metadata_roundtrip.md
  - docs/reference/canonical-prompt-format.md
  - docs/reference/espanso-integration.md
---

# Per-Match `force_clipboard` Opt-In for Espanso Export

## Summary

This proposal adds an optional per-prompt frontmatter field,
`targets.espanso.force_clipboard`, that the Espanso exporter translates into
Espanso's native `force_clipboard: true` match property, paired with a new
`taurcode lint prompts` warning that flags short prompt bodies missing the
flag. Together they let individual short prompts opt out of Espanso's
Inject-backend delivery without changing default behavior for every other
match.

## Background / Motivation

Espanso's `Auto` backend (the default) delivers a match via simulated
keypresses (`Inject`) when its replacement text is shorter than
`clipboard_threshold` (default 100 characters), and via clipboard paste
(`Clipboard`) at or above that threshold. Under `Inject`, a trailing `\n` in
the replacement text is sent as an actual simulated Return keypress, not
inserted as text. In a chat UI bound to "Enter submits" — including
Claude Code's own input — that synthetic keypress submits the turn
prematurely.

This was discovered via the `:dashes` prompt (`prompts/taurcode/dashes.md`):
at 74 characters it falls under the threshold and is delivered via `Inject`,
so its trailing separator newline submits the chat turn. `:think` (260
chars) and `:debug` (249 chars) are long enough to be delivered via
`Clipboard` and do not exhibit the bug. The failure is not a defect in the
prompt content or in the exporter's existing behavior — the exporter
(`src/taurcode/espanso_export.py:62-67`) faithfully emits `trigger` and
`replace` for every match, exactly as documented in
`docs/reference/canonical-prompt-format.md`. The gap is that Espanso's
package format supports a third, per-match key (`force_clipboard`) that
Taurcode's canonical prompt format and exporter have no way to express yet.

As a stopgap, the affected machine's Espanso installation was reconfigured
with a global `backend: Clipboard` override in
`~/Library/Application Support/espanso/config/default.yml`. That fix is
machine-local (Espanso's package format has no `config:` section, so this
setting cannot ship inside `package.yml`) and broader than necessary — it
forces every match in every installed package through `Clipboard`, which
carries independent, documented side effects unrelated to this bug
(espanso/espanso#2059, "overwrites system clipboard contents when it
contained a screenshot"; #2051, "truncates the system clipboard contents").

This proposal is the source-level fix: a mechanism scoped to exactly the
matches that need it, shipped with the package so it travels to every
installing user regardless of their own Espanso config.

## Design Decisions

### Decision: Field shape and name

Options considered:
- `targets.espanso.force_clipboard: true` (boolean) — mirrors Espanso's own
  `force_clipboard` match property directly.
- `targets.espanso.force_mode: "clipboard" | "keys"` — mirrors Espanso's
  more general `force_mode` enum, which can also force *into* `Inject`.

**Chosen: `force_clipboard: true` (boolean).** Nothing in the current prompt
corpus needs to force a match into `Inject`; only the "opt out of Inject"
direction has a real use case. Exposing `force_mode` now would be
speculative surface area for a need that doesn't exist yet (YAGNI).

### Decision: Where the exporter reads and emits the field

**Chosen:** `Prompt.targets` (`src/taurcode/prompt_model.py`) is already an
untyped `Dict[str, Any]` passthrough — no dataclass or schema migration is
needed to carry this field through parsing. The per-match loop in
`espanso_export.py:62-67` gains a check —
`prompt.targets.get("espanso", {}).get("force_clipboard")` — and appends a
third `force_clipboard: true` line to that match's block only when the
value is `true`. `trigger`/`replace` emission order and formatting are
unchanged, so every existing prompt without the field produces byte-identical
`package.yml` output; only `:dashes`' emitted block changes.

### Decision: Validation strictness

Today `taurcode validate` (`src/taurcode/validate.py`) checks only
`REQUIRED_FIELDS` presence, keyword format, and id/keyword uniqueness — it
does not type-check `targets` or any other optional/nested field. Frontmatter
`targets` reaches the pipeline completely untyped: `prompt_loader.py:61`
loads it as `post.metadata.get("targets", {}) or {}`, so a value like
`targets: true` or `targets: {espanso: true}` survives unchanged. The
exporter read sketched in the previous decision —
`prompt.targets.get("espanso", {}).get("force_clipboard")` — assumes both
`targets` and `targets.espanso` are mappings; on either of the shapes above
it raises an uncaught `AttributeError` at export time instead of a
validation error.

**Chosen:** extend `taurcode validate` to require, when present:
`targets` is a mapping; `targets.espanso`, when present, is a mapping;
`targets.espanso.force_clipboard`, when present, is a boolean. Any other
shape is a validation error, not a crash. An absent or `false`
`force_clipboard` is not an error and is not emitted. Because
`docs/reference/canonical-prompt-format.md:50` already establishes that
export runs validation before writing, this validation is a hard
precondition for the exporter's chained `.get()` reads to be safe — the
exporter itself does not need redundant defensive type-checks once this
validation lands. Add corresponding `taurcode validate` test coverage for
malformed shapes (`targets: true`, `targets: {espanso: true}`,
`force_clipboard: "yes"`).

### Decision: Lint warning trigger condition

Options considered:
- Heuristic content check (e.g., "body has no trailing sentence-like
  content") — harder to define precisely, risk of false positives/negatives.
- Reuse Espanso's own default `clipboard_threshold` (100 characters) as the
  trigger point for a new advisory warning.

**Chosen: mirror the 100-character default.** It reproduces the exact
failure condition (short enough to be delivered via `Inject`) with no
guessing about content, and is cheap to compute at lint time. Define it as
a named constant with a comment citing the Espanso default it mirrors, so
a future reconciliation is easy if Espanso ever changes its own default.

### Decision: Where the lint warning lives

Options considered:
- `src/taurcode/espanso_lint.py` — package-build-level checks.
- `src/taurcode/prompt_lint.py` — prompt-source-level checks
  (`_style_warnings`, `src/taurcode/prompt_lint.py:265`).

**Chosen: `prompt_lint.py`.** The condition (`keyword`/`body` length) is a
property of the prompt source, evaluable before any export step, and
`cli.py` already separates `lint prompts` (source) from `lint espanso`
(built package) along exactly this line. This also matches the existing
warning class described in `docs/reference/canonical-prompt-format.md:60`
("reviewable source quality issues... unquoted keywords... wrapped
descriptions") — a non-blocking warning, not a validation error.

### Decision: Importer round-trip for `force_clipboard`

The importer (`src/taurcode/espanso_import.py`) accepts exactly
`_SIMPLE_KEYS = {"trigger", "replace"}` (line 13); `is_simple_match` (lines
34-35) requires a match's keys to equal that set exactly. A match carrying
`force_clipboard` as a third key fails `is_simple_match`, so fresh import
(`import_espanso`) routes it to `imported_raw` instead of a canonical
prompt file, and merge import (`_merge_simple_matches`, lines 390-426)
skips it entirely — the existing canonical prompt is never added to
`matched_paths` and is reported as an orphan warning. Without a fix, any
prompt that opts into `force_clipboard` (starting with `:dashes` itself)
breaks Taurcode's own export-to-import round trip the moment someone runs
`taurcode import espanso --merge` against the exported package.

Options considered:
- Leave `force_clipboard` matches unsupported (raw-fallback only) and
  document that prompts using the new field are export-only.
- Extend `_SIMPLE_KEYS`/`is_simple_match` to also accept an optional
  `force_clipboard: true` key, mapping it back to
  `targets.espanso.force_clipboard: true` on both fresh and merge import.

**Chosen:** the second option. `project/design/proposals/adopted/espanso_metadata_roundtrip.md`
already establishes round-trip fidelity for Espanso package metadata as a
Taurcode design goal; treating this proposal's own new field as an
exception to that goal on day one would contradict it.

### Decision: Semantic roundtrip coverage for `force_clipboard`

`normalize_canonical_prompts` (`src/taurcode/semantic_normalize.py:89-118`)
builds each `NormalizedPrompt` from `id`, `keyword`, `name`, `description`,
and `tags` only — it never reads `targets`, so `force_clipboard` is
invisible on the canonical side of any comparison regardless of what
frontmatter sets. Separately, `_unsupported_fields_differ`
(`semantic_normalize.py:287-294`) returns `False` for
`ESPANSO_SEMANTIC_MODE` comparisons whenever the *expected* side's
`unsupported_fields` is empty, even when the *actual* side's is not. Because
the canonical side never records `force_clipboard` as anything (supported or
unsupported), `taurcode roundtrip espanso` would pass even if the exporter
silently dropped or mis-emitted `force_clipboard` — the check has no
signal to compare.

**Chosen:** capture `targets.espanso.force_clipboard` explicitly as a named
field on `NormalizedPrompt` (not as a generic unsupported field, since it
is now a modeled, supported construct), populate it in both
`normalize_canonical_prompts` and `normalize_espanso_package`, compare it
directly in `_compare_canonical_prompt_fields`, and add a regression
fixture asserting the roundtrip fails if the exporter drops or corrupts the
field.

## Non-Goals

- Does not expose Espanso's `force_mode: "keys"` (forcing `Inject`) — no
  current use case; can be proposed separately if one emerges.
- Does not change the exporter's default emission for any prompt that
  doesn't set the field — existing `package.yml` output for all prompts
  except `:dashes` is unaffected.
- Does not remove or replace the machine-local `backend: Clipboard`
  stopgap as part of this proposal's implementation; reverting it to
  `Auto` is a manual one-line follow-up once `:dashes` carries
  `force_clipboard: true`, not a Taurcode code or doc change.
- Does not add a hard validation error for short bodies missing the flag —
  the lint warning is advisory, consistent with this repo's existing
  warning-vs-error split.

## Implementation Plan

Single PR, no novel architectural decisions beyond what's captured above.
Ordered so each step's precondition lands before anything that depends on it:

1. `src/taurcode/validate.py` (and the `targets` shape reaching it via
   `prompt_loader.py:61`) — require `targets` and `targets.espanso`, when
   present, to be mappings, and `force_clipboard`, when present, to be a
   boolean. This is a precondition for step 2's exporter read to be safe.
2. `src/taurcode/espanso_export.py` — read `targets.espanso.force_clipboard`
   per match, emit `force_clipboard: true` when set.
3. `src/taurcode/espanso_import.py` — extend `_SIMPLE_KEYS`/`is_simple_match`
   to accept an optional `force_clipboard: true` key, mapping it back to
   `targets.espanso.force_clipboard: true` on both fresh import
   (`import_espanso`) and merge import (`_merge_simple_matches`).
4. `src/taurcode/semantic_normalize.py` — capture
   `targets.espanso.force_clipboard` explicitly on `NormalizedPrompt` in
   both `normalize_canonical_prompts` and `normalize_espanso_package`,
   compare it in `_compare_canonical_prompt_fields`, and add a roundtrip
   regression fixture for a dropped/corrupted field.
5. `src/taurcode/prompt_lint.py` — add the short-body-without-flag warning
   to `_style_warnings`.
6. `docs/reference/canonical-prompt-format.md` — add `force_clipboard` to
   the Optional fields table, including the shape-validation rule from
   step 1.
7. `docs/reference/espanso-integration.md` — short note on the
   Inject/Clipboard split and why the field exists.
8. `prompts/taurcode/dashes.md` — set `targets.espanso.force_clipboard: true`,
   resolving the original bug at the source and serving as the field's
   first real usage example, exercising the full round trip from steps 1-4.
9. Tests: extend `tests/prompt_validation_test.py`,
   `tests/espanso_export_test.py`, `tests/espanso_import_test.py`,
   `tests/prompt_lint_test.py`, and `tests/semantic_normalize_test.py`;
   update roundtrip fixtures under `tests/fixtures/roundtrip/` for the
   `:dashes`-equivalent fixture.

Suggested as a single `/lrh-work-item` once this proposal is accepted.

## Cross-References

- Prior art: `project/design/proposals/adopted/espanso_metadata_roundtrip.md`
  established the pattern this proposal extends — per-match Espanso
  metadata flowing from canonical prompt Markdown through the exporter.
- `docs/reference/canonical-prompt-format.md` — current Optional fields
  table and exporter scope note this proposal amends.
- Espanso match schema (`force_clipboard`, `force_mode`):
  https://raw.githubusercontent.com/espanso/espanso/dev/schemas/match.schema.json
- Espanso config schema (`clipboard_threshold`, `backend`):
  https://raw.githubusercontent.com/espanso/espanso/dev/schemas/config.schema.json
