---
id: semantic-roundtrip-regression-design
type: design_proposal
status: proposed
title: Semantic Roundtrip and Regression Suite Design
---

# Semantic Roundtrip and Regression Suite Design Proposal

## Status

Proposed. Semantic normalization and the `taurcode roundtrip espanso` CLI have been
implemented as part of the Espanso roundtrip foundation. The broader regression suite
and future construct coverage described here remain proposed follow-up work.

## Summary

Taurcode is evolving from a small Espanso import/export helper into canonical prompt
infrastructure. That shift changes the roundtrip target from byte-for-byte
Espanso YAML reproduction to semantic fidelity: Taurcode should preserve the
meaning of supported prompts, metadata, and package assets across import,
validation, export, and re-import cycles, while explicitly isolating unsupported
constructs that cannot yet be modeled safely.

This proposal defines the long-term architecture for semantic roundtrip
guarantees, normalization semantics, and regression testing infrastructure. It
builds on the Espanso metadata round-trip proposal by treating `package.yml`,
`_manifest.yml`, `README.md`, `LICENSE`, Markdown frontmatter, and raw fallback
blocks as parts of a semantic prompt package rather than as unrelated files.

The proposal is design-only. It does not add CLI behavior, implement a
comparison engine, create a fixture corpus, or change importer/exporter output.

## Problem Statement

Taurcode already has empirical evidence that simple import/export flows can work
for useful Espanso packages. Empirical success is not enough for a canonical
prompt system because silent fidelity drift can appear after unrelated changes to
parsing, validation, formatting, metadata handling, or YAML emission.

The main engineering risks are:

- **Importer/exporter mismatches.** The importer may accept fields that the
  exporter cannot reproduce, or the exporter may emit defaults that the importer
  later treats as user-authored data.
- **Metadata loss.** Espanso package assets, Taurcode frontmatter, and
  prompt-level annotations can be dropped if the model only remembers
  `trigger` and `replace`.
- **YAML emitter normalization differences.** YAML libraries may change quoting,
  field ordering, scalar style, indentation, or list formatting without changing
  the represented data.
- **Unsupported construct degradation.** Variables, forms, regex triggers,
  scripts, or additional Espanso fields can be silently simplified if Taurcode
  tries to coerce them into a simple static replacement model.
- **Semantic drift hidden by formatting changes.** Large formatting diffs can
  hide real behavior changes, while byte-level comparisons can report harmless
  emitter differences as failures.

The right long-term guardrail is a regression suite that compares normalized
semantic meaning, not raw YAML text, and that separately asserts exact
preservation for data Taurcode intentionally keeps as raw fallback.

## Relationship to Espanso Metadata Roundtrip Work

The Espanso metadata round-trip proposal expands Taurcode's responsibilities
from simple prompt import/export to package-level preservation. It establishes
that Taurcode should preserve or generate Espanso metadata assets such as:

```text
prompts/<package>/espanso/_manifest.yml
prompts/<package>/espanso/README.md
prompts/<package>/espanso/LICENSE
```

and that generated Espanso packages should include complete basic package
outputs under:

```text
build/espanso/<package>/
```

That work changes the roundtrip architecture from:

```text
trigger + replace body
```

to:

```text
semantic prompt object + package metadata + target-specific preservation data
```

Roundtrip testing therefore needs to validate more than prompt bodies. It should
verify:

- package metadata preservation when source assets exist;
- conservative generated defaults when metadata assets do not exist;
- preservation of Taurcode-curated frontmatter during merge import;
- update semantics for Espanso-derived fields such as `keyword` and body;
- supported Espanso metadata fields represented in canonical metadata;
- unsupported or unknown metadata retained in an explicit preservation channel;
- unsupported match blocks saved as raw fallback without lossy rewriting.

The metadata proposal also introduces field ownership during merge import. This
proposal depends on that concept: semantic equivalence should compare fields
according to their owner and preservation contract, rather than assuming every
file is fully owned by the YAML emitter.

## Canonical Semantic Model Layer

Taurcode should introduce a conceptual semantic model layer between concrete
file formats and target exporters. The exact implementation can evolve, but the
model should make ownership, normalization, and unsupported data explicit.

A possible conceptual shape is:

```python
class Prompt:
    id: str
    name: str
    description: str
    keyword: str
    body: str

    metadata: dict
    espanso: EspansoMetadata | None

    unsupported_fields: dict
```

A package-level shape may also be needed:

```python
class PromptPackage:
    name: str
    prompts: list[Prompt]
    metadata_assets: PackageMetadataAssets
    raw_fallbacks: list[RawFallbackBlock]
```

These examples are guidance, not a final API requirement. The important design
requirement is that the model distinguish between:

- **normalized canonical fields** such as `id`, `name`, `description`,
  `keyword`, and prompt body;
- **general metadata** that Taurcode understands and validates;
- **target-specific metadata** such as Espanso manifest data or match fields;
- **preserved unknown fields** that Taurcode should carry forward but not
  interpret yet;
- **unsupported raw fallback** content that should remain byte-preserved unless
  a future migration explicitly claims support.

Semantic equivalence should operate on this model, not directly on emitted YAML
text. Supported constructs can be normalized into canonical fields. Unknown but
structured fields can be preserved and compared as parsed data when safe.
Unsupported raw blocks should keep a stricter preservation contract because
Taurcode does not understand them well enough to safely re-emit equivalent YAML
from a normalized structure.

## Normalization and Equivalence

This proposal distinguishes two fidelity concepts:

- **Text fidelity** means preserving the exact bytes or exact source formatting
  of a file.
- **Semantic fidelity** means preserving the represented prompt, metadata, and
  target behavior after parsing and normalization.

Taurcode should prefer semantic fidelity for supported constructs because YAML is
a data serialization format with multiple valid textual representations.
Byte-for-byte comparison is too brittle as the main abstraction boundary: it
would fail on harmless YAML emitter changes while still missing cases where two
similar-looking files behave differently.

Acceptable normalized equivalence should include:

- quoting differences such as plain, single-quoted, or double-quoted scalar
  output when the parsed string is the same;
- field ordering differences where maps represent the same key/value pairs;
- folded versus literal scalar representation where the parsed string and
  prompt behavior match;
- normalized list formatting such as flow style versus block style where the
  parsed sequence is identical;
- generated final-newline normalization for Taurcode-owned Markdown prompt
  files, as long as prompt body semantics are preserved.

Semantic normalization should not erase meaningful whitespace inside prompt
bodies. It should also avoid pretending that all YAML style differences are
irrelevant. For example, folded and literal scalars are only equivalent when the
parsed value and replacement behavior match.

Exact preservation remains desirable for unsupported/raw fallback blocks. If
Taurcode cannot model an Espanso construct, it should avoid reparsing and
re-emitting it as though it were understood. The raw fallback channel should
prioritize byte preservation or a clearly documented near-byte preservation rule
so users can trust that unsupported content was not silently degraded.

## Roundtrip Invariant Definition

The core invariant for supported constructs should be:

```text
SemanticNormalize(Export(Import(X)))
    ==
SemanticNormalize(X)
```

For a canonical Taurcode package exported to Espanso and imported back, the
corresponding invariant is:

```text
SemanticNormalize(Import(Export(P)))
    ==
SemanticNormalize(P)
```

These formulas are conceptual. The actual comparison should define the input
domain and preservation guarantees for each construct class.

### Supported constructs

For supported constructs, Taurcode should guarantee semantic equivalence after a
roundtrip. Examples include static Espanso matches where `trigger` maps to
canonical `keyword` and `replace` maps to the prompt body. Package metadata that
Taurcode explicitly models should also roundtrip semantically.

### Preserved unknown structured data

For unknown but structured metadata that Taurcode chooses to preserve, the
invariant should be data equivalence after parsing, not necessarily identical
text. Taurcode may normalize ordering or style if the preservation policy says
that the parsed data is the contract.

### Unsupported raw fallback

For unsupported match constructs, Taurcode should not claim full semantic
support. The invariant should instead be:

```text
RawFallback(Import(X)) preserves UnsupportedBlocks(X)
```

The comparison should assert that unsupported blocks are present, associated
with clear warnings or diagnostics, and not silently converted into incomplete
prompts. Where feasible, the raw bytes should be preserved exactly.

### Equivalence boundaries

The normalization boundary should be explicit in tests and documentation:

- canonical prompt fields are compared by normalized semantic value;
- prompt body content is compared by exact string value after documented newline
  normalization;
- Taurcode-owned frontmatter is compared as normalized parsed metadata;
- Espanso metadata assets are compared according to their ownership rule;
- raw fallback blocks are compared using the strict preservation rule for the
  raw channel.

## Regression Suite Architecture

Taurcode should add a regression framework for real corpus roundtrip testing
after the semantic model and normalization rules are documented enough to test.
A possible fixture layout is:

```text
tests/fixtures/real_corpus/
  espanso/
    simple_static_package/
    metadata_rich_package/
    unsupported_constructs_package/
  taurcode/
    curated_prompt_package/
    merge_import_package/
```

A complementary semantic fixture layout could store expected normalized model
snapshots:

```text
tests/fixtures/semantic_roundtrip/
  simple_static_package.expected.yml
  metadata_rich_package.expected.yml
  unsupported_constructs_package.expected.yml
```

The suite should cover:

- import validation for corpus-derived Espanso packages;
- export validation for canonical Taurcode prompt packages;
- import/export/import and export/import/export roundtrip paths;
- normalization-based comparisons for supported constructs;
- assertions that unsupported constructs are reported and stored in raw fallback
  files;
- metadata preservation assertions for `_manifest.yml`, `README.md`, `LICENSE`,
  and future supported metadata;
- merge-import assertions for human-authored frontmatter preservation;
- regression cases for known fidelity bugs, including newline, block scalar,
  frontmatter, and metadata drift.

Real corpus fixtures should be curated and small enough to review. The goal is
not to vendor every user package, but to preserve representative examples that
exercise known fidelity boundaries. Fixtures derived from real packages should
be sanitized where necessary and documented so future contributors understand
what behavior each case protects.

## Proposed CLI and Tooling

A future roundtrip command could expose the regression workflow for local
packages and CI diagnostics:

```bash
taurcode roundtrip espanso --input <package>
```

The expected workflow would be:

```text
1. import
2. validate
3. export
4. normalize
5. compare
6. report semantic differences
```

The report should focus on semantic differences, not raw textual diffs, while
still linking to file-level context when helpful. For unsupported constructs, the
report should state that Taurcode preserved raw fallback content instead of
claiming full support.

Possible future tooling pieces include:

- a semantic normalizer that emits stable comparison snapshots;
- a diff reporter that groups differences by prompt, package metadata, and raw
  fallback content;
- a fixture update command that intentionally refreshes expected snapshots after
  a documented normalization change;
- CI checks that run the curated roundtrip corpus.

This proposal does not implement any of those commands.

## Recommended Implementation Sequencing

Recommended sequencing is:

1. **Complete metadata roundtrip implementation.** Package asset and merge-import
   semantics should be reliable before broad roundtrip assertions depend on
   them.
2. **Stabilize the canonical semantic model.** Define what fields and ownership
   categories are represented before writing a comparison engine.
3. **Specify normalization and equivalence.** Document which differences are
   semantic, which are formatting-only, and which require exact preservation.
4. **Build the roundtrip harness.** Implement import/export/normalize/compare as
   a reusable test helper before exposing it as CLI behavior.
5. **Add the regression suite.** Seed it with small corpus-derived fixtures and
   known historical fidelity bugs.
6. **Consider CLI exposure.** Add user-facing roundtrip diagnostics only after
   the harness has proven stable in tests.

Normalization semantics should stabilize before the comparison engine because
otherwise the engine will encode accidental policy decisions. A premature diff
engine can make future improvements expensive by treating arbitrary emitter
formatting as contract. The model and normalization policy should define the
contract first; tooling should implement that contract second.

## Supported and Unsupported Construct Policy

Taurcode should document support by construct category rather than by incidental
parser behavior.

### Supported initial constructs

The supported baseline should remain conservative:

- static Espanso matches with `trigger` and `replace`;
- canonical prompt frontmatter fields required by the prompt schema;
- prompt bodies represented as Markdown text;
- package metadata assets covered by the Espanso metadata roundtrip design;
- merge-import ownership rules for Espanso-derived and Taurcode-curated fields.

### Unsupported or partially supported constructs

Unsupported or partially supported constructs should include, until explicitly
implemented and tested:

- Espanso variables;
- forms;
- scripts and shell commands;
- regex triggers;
- imports or global variables;
- additional match fields not represented in the semantic model;
- metadata fields whose validation or ownership semantics are unknown.

Unsupported constructs should be detected, reported, and preserved through a raw
fallback path when possible. Taurcode should not silently drop them, generate a
simple prompt that loses behavior, or mark the roundtrip as semantically
successful.

## Risks and Tradeoffs

Semantic normalization provides several benefits:

- tests fail on meaningful behavior changes rather than harmless YAML style
  changes;
- the importer/exporter boundary is defined in terms of prompt infrastructure,
  not one emitter's formatting choices;
- metadata ownership and preservation become explicit;
- regression fixtures can protect against drift across future refactors.

The tradeoffs are real:

- semantic comparison is more complex than byte comparison;
- normalization rules can hide bugs if they are too broad;
- YAML has ambiguous presentation details, especially around multiline strings
  and whitespace-sensitive replacement bodies;
- preserving unsupported raw content complicates the model and file layout;
- fixture snapshots can become maintenance burden if they are too large or too
  tightly coupled to implementation details.

Byte-level comparison is still useful as a narrow tool, especially for raw
fallback preservation and possibly for metadata files that Taurcode copies
without ownership. It should not be the top-level roundtrip contract for
supported constructs because it would optimize for emitter stability rather than
prompt meaning.

Long-term maintainability depends on keeping the semantic model small,
documented, and explicit. Each newly supported construct should include a model
mapping, normalization rule, importer/exporter behavior, validator behavior, and
regression fixture before Taurcode claims roundtrip support for it.

## Documentation Relationships

This proposal should be read alongside:

- `project/design/design.md`, which defines canonical Markdown prompt files as
  the source of truth and Espanso as an export target;
- `project/design/proposals/adopted/espanso_metadata_roundtrip.md`, which defines
  package metadata preservation, merge-import field ownership, and metadata
  linting direction;
- future canonical prompt schema documentation, which should specify required
  and optional frontmatter fields;
- importer/exporter documentation, which should state which Espanso constructs
  are supported and which are raw fallback only;
- validator documentation, which should distinguish semantic errors from
  warnings and unsupported-construct diagnostics;
- raw fallback design documentation, if split out later, which should specify
  exact preservation guarantees and migration paths for newly supported
  constructs.

As these documents evolve, they should avoid describing YAML text formatting as
the core contract. The durable contract is semantic prompt meaning plus explicit
preservation policies for data Taurcode cannot yet interpret.

## Non-Goals

This proposal does not implement:

- a roundtrip engine;
- a regression fixture corpus;
- a new semantic model API;
- CLI commands;
- additional exporter behavior;
- automatic install or sync behavior;
- broad code refactors.
