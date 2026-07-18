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

**Chosen:** `taurcode validate` treats a present-but-non-boolean
`force_clipboard` value as an error, consistent with the strictness already
applied to other known optional fields. An absent or `false` value is not
an error and is not emitted.

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

Single PR, no novel architectural decisions beyond what's captured above:

1. `src/taurcode/espanso_export.py` — read `targets.espanso.force_clipboard`
   per match, emit `force_clipboard: true` when set.
2. `src/taurcode/prompt_lint.py` — add the short-body-without-flag warning
   to `_style_warnings`.
3. `docs/reference/canonical-prompt-format.md` — add `force_clipboard` to
   the Optional fields table.
4. `docs/reference/espanso-integration.md` — short note on the
   Inject/Clipboard split and why the field exists.
5. `prompts/taurcode/dashes.md` — set `targets.espanso.force_clipboard: true`,
   resolving the original bug at the source and serving as the field's
   first real usage example.
6. Tests: extend `tests/espanso_export_test.py` and
   `tests/prompt_lint_test.py`; update roundtrip fixtures under
   `tests/fixtures/roundtrip/` if the `:dashes`-equivalent fixture is
   affected.

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
