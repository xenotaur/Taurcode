# Frontmatter dependency audit

Prompt ID: `PROMPT(AD_HOC:FRONTMATTER_SHIM_AUDIT)[2026-05-12T02:33:16-04:00]`

## Summary

Taurcode's local `src/frontmatter` package appears to be an accidental or obsolete compatibility shim rather than a currently justified project abstraction. The repository declares both `python-frontmatter` and `PyYAML` as runtime dependencies, but the local top-level package is named `frontmatter`, which is the same import name provided by `python-frontmatter`.

Recommended path: move prompt loading fully to the formal `python-frontmatter` dependency, then remove the top-level local shim. If Taurcode still needs an offline or compatibility fallback, move that code under a Taurcode-owned module name such as `taurcode.frontmatter_compat` so it cannot shadow the third-party package.

This PR does not remove or rewrite the shim. The safe next step is a small implementation PR with focused tests that prove Taurcode loads the same supported prompt metadata through the third-party dependency and that unsupported rich metadata is either documented or rejected consistently.

## Implementation status

Implemented by `PROMPT(AD_HOC:REMOVE_FRONTMATTER_SHIM)[2026-05-12T16:55:00-04:00]`: Taurcode now relies on the declared `python-frontmatter` dependency for prompt loading, constrains setuptools package discovery to `taurcode*`, and no longer ships a top-level `src/frontmatter` shim.

## Current behavior

### What the local shim provides

`src/frontmatter/__init__.py` provides a very small API surface:

- `Post`, a dataclass with `metadata` and `content` attributes.
- `_parse_scalar(value)`, an internal scalar parser that strips surrounding double quotes and converts exactly `[]` to an empty list.
- `loads(text)`, which normalizes newlines, recognizes only a frontmatter block delimited by exact `---` lines, parses each non-blank frontmatter line by `line.partition(":")`, and returns `Post(metadata, content)`.
- `load(path)`, which reads UTF-8 text from disk and calls `loads`.

The shim does not call `yaml.safe_load`. It is therefore not a YAML parser. It treats indentation and list item lines as independent keys, does not preserve comments, does not understand multiline YAML, and has no explicit validation for malformed key/value lines beyond missing closing delimiter handling.

### Where `frontmatter` is used

The only production import of `frontmatter` is in `src/taurcode/prompt_loader.py`. `load_prompts()` calls `frontmatter.loads(text)` and reads these metadata keys from `post.metadata`: `id`, `name`, `description`, `keyword`, and `targets`.

The standalone validator module does not parse frontmatter directly, but the `taurcode validate` CLI path still calls `prompt_loader.load_prompts()` before `validate.validate_prompts()`. Because `prompt_loader` is the production module that imports `frontmatter`, validation has the same environment-dependent parser behavior as loading and export. Prompt linting is different: `src/taurcode/prompt_lint.py` parses prompt frontmatter with `yaml.safe_load`, reports malformed YAML with line/column diagnostics, requires mapping frontmatter, and validates schema expectations. Espanso import and metadata handling also use `PyYAML` directly.

### Packaging and import interaction

`pyproject.toml` configures a `src/` layout with package discovery rooted at `src`, and declares runtime dependencies on `python-frontmatter` and `PyYAML`. Because `src/frontmatter/__init__.py` is a top-level Python package under the configured discovery root, it is expected to be included in editable and normal Taurcode installs unless packaging is narrowed in a future PR.

That means Taurcode currently ships a top-level package with the same import name as the package provided by `python-frontmatter`. In any environment where Taurcode's discovered packages take precedence on `sys.path`, `import frontmatter` resolves to Taurcode's local shim instead of the installed third-party dependency. In an uninstalled source checkout without `src` on `sys.path`, `import frontmatter` may resolve to the third-party package instead. This makes behavior environment-dependent.

Observed local import behavior during this audit:

- With the repository's `src` directory on `PYTHONPATH`, `import frontmatter` resolves to `/workspace/Taurcode/src/frontmatter/__init__.py`.
- Without `src` on `PYTHONPATH` in the pre-existing environment, `import frontmatter` resolves to the installed `python-frontmatter` package in site-packages.

`scripts/develop` could not complete in this environment because pip could not fetch build dependencies through the configured network tunnel, so this audit did not produce a fresh editable-install import trace. The packaging configuration is still sufficient evidence that the local top-level package is discoverable and can shadow the dependency once installed.

## Behavior comparison against prompt metadata needs

| Metadata or parsing need | Local shim behavior | `python-frontmatter`/PyYAML expectation | Taurcode usage today |
| --- | --- | --- | --- |
| Simple scalar fields | Works for simple `key: value`; strips surrounding double quotes only. | Works through YAML parsing with typed values and standard quoting. | Required for `id`, `name`, `description`, and `keyword`. |
| Lists | Only converts exactly `[]` to an empty list. YAML list blocks are misread as separate keys. | Supports inline and block lists. | Not required for core fields, but relevant to future richer metadata. |
| Nested dictionaries | Not supported; nested lines become flattened accidental keys. | Supported. | `Prompt.targets` expects a dictionary, and design docs show nested `targets`. |
| Comments | Non-blank comment lines are parsed as keys with empty values. | YAML comments are ignored when loading. | Prompt formatter/import preservation cares about human-authored comments in frontmatter text, but prompt loading should not treat comments as metadata. |
| Quoted strings | Removes surrounding double quotes; does not implement YAML escape semantics or single quotes. | Supports YAML quoting. | Important for preferred quoted `keyword` values. |
| Multiline YAML | Not supported; block scalar markers and indented content become accidental keys. | Supported. | Long descriptions are currently linted for generic dumper wrapping, but richer metadata should not be considered supported until tested. |
| `targets` metadata | `targets:` becomes an empty string, so `post.metadata.get("targets", {}) or {}` silently discards nested target settings. | Nested target dictionaries load correctly. | Design docs define `targets.espanso.enabled` and `targets.espanso.package`, but current loader cannot consume nested targets through the shim. |
| Malformed frontmatter | Missing closing delimiter raises `ValueError("Invalid frontmatter block")`; malformed YAML-like content is otherwise accepted as arbitrary keys. | YAML parser errors are available for malformed YAML. | Linting catches malformed YAML, but direct loading/export can be more permissive if the shim is active. |

## Risk assessment

### Risks of keeping the shim

- It shadows the formal `python-frontmatter` dependency in installed contexts, making the declared dependency misleading.
- It creates environment-dependent behavior: source checkouts that import site-packages may differ from editable or installed Taurcode environments.
- It silently discards or corrupts richer YAML metadata such as nested `targets`, lists, comments, and multiline fields.
- It weakens confidence in round-trip behavior because import, lint, and metadata tools use `PyYAML`, while prompt loading may use the shim.
- It makes future contributor expectations unclear: files can appear valid under lint but load differently during export if the shim is active.

### Risks of removing the shim

- If any workflow relies on Taurcode being usable without network-installed dependencies, removing the shim eliminates that fallback.
- Third-party `python-frontmatter` may raise different exceptions or load edge cases differently, so direct CLI export/validate behavior should be covered by tests before removal.
- Existing tests may pass today without proving which `frontmatter` implementation is used, so a removal PR needs an import-resolution or behavior test to prevent accidental regressions.
- If package installation currently depends on the accidental local package satisfying `import frontmatter`, removal must be paired with dependency installation validation.

### Compatibility risks for existing prompts and tests

Current prompt examples and tests primarily use simple scalar metadata, so they are unlikely to depend on shim-specific parsing intentionally. The main compatibility risk is accidental: a prompt with invalid YAML that the shim currently accepts could start failing when loaded by `python-frontmatter`. That is probably desirable, but it should be documented as aligning direct load behavior with the existing linter's YAML expectations.

The existing `targets` field is a stronger reason to move away from the shim. `Prompt.targets` is typed as a dictionary, and the design documentation describes nested target metadata. The shim cannot load that shape correctly.

## Recommendation

Prefer moving Taurcode fully to the formal `python-frontmatter` dependency and eliminating `src/frontmatter` as a top-level package.

Recommended migration path:

1. Add focused tests that lock current intended prompt-loading behavior for simple scalar fields, quoted strings, nested `targets`, comments, malformed frontmatter, and multiline YAML decisions.
2. Adjust packaging or source layout so Taurcode no longer installs a top-level `frontmatter` package.
3. Update `src/taurcode/prompt_loader.py` to import the third-party dependency unambiguously once the local package is gone.
4. Run the standard validation commands and confirm `scripts/develop` can install dependencies in a network-capable environment.
5. Update user-facing docs to state that prompt frontmatter is YAML parsed by `python-frontmatter`/`PyYAML`, and to distinguish supported metadata from tolerated-but-not-guaranteed formatting.

If an offline fallback is still required, keep it only under a Taurcode-owned name such as `taurcode.frontmatter_compat`. That compatibility module should be explicitly selected by Taurcode code and tested against a documented minimal metadata subset. It should not be named `frontmatter`.

## Implementation plan

### PR 1: Lock intended prompt-loading behavior

- Add unit tests under `tests/` for `prompt_loader.load_prompts()` covering:
  - simple scalar frontmatter fields,
  - quoted `keyword` values,
  - comments in frontmatter,
  - nested `targets`,
  - malformed YAML frontmatter,
  - the current decision for multiline YAML fields.
- Cover both direct `prompt_loader.load_prompts()` callers and CLI paths that load prompts before acting, especially `taurcode validate` and `taurcode export espanso`.
- Add a small import-shadowing test or packaging assertion that fails if Taurcode still ships top-level `frontmatter` after the migration PR.
- Keep the local shim unchanged in this PR if the tests are intended to document current failure modes.

### PR 2: Remove top-level shim shadowing

- Delete `src/frontmatter/__init__.py`, or exclude `frontmatter` from package discovery if a temporary source copy must remain for comparison.
- Ensure `python-frontmatter` remains a runtime dependency and consider pinning a compatible minimum version once behavior is tested.
- Run `scripts/develop` in a network-capable environment to confirm the formal dependency installs and resolves.
- Verify `import frontmatter` resolves to site-packages after installation.

### PR 3: Document supported frontmatter semantics

- Update `README.md` and any prompt-format docs to state which metadata fields are required and which rich YAML features are supported.
- Document whether `targets` is supported during export or reserved for future target exporters.
- Document malformed frontmatter behavior for load/export versus lint.

### Rollback and compatibility notes

If the removal causes unexpected installation failures, restore functionality by adding a Taurcode-owned `taurcode.frontmatter_compat` module and importing it explicitly only when a dependency check fails. Do not restore a top-level `frontmatter` package because that recreates the shadowing problem.

## Decision criteria

### Evidence that would justify eliminating the shim now

- Tests pass when prompt loading uses third-party `python-frontmatter` for simple scalar prompts and existing fixtures.
- Nested `targets` load as dictionaries in `Prompt.targets`.
- Malformed YAML behavior is consistent with prompt linting or intentionally documented.
- `scripts/develop` proves the runtime dependency installs in a normal development environment.
- Packaging inspection shows Taurcode no longer installs a top-level `frontmatter` package.

### Evidence that would justify keeping a compatibility layer temporarily

- A documented, tested requirement exists for offline operation without installed dependencies.
- The compatibility layer is moved under `taurcode.frontmatter_compat` and cannot shadow third-party packages.
- The supported subset is explicitly limited to simple scalar frontmatter needed by current exports.
- CLI behavior detects and explains unsupported rich YAML instead of silently corrupting metadata.

### Preconditions before treating rich YAML metadata as supported

- `prompt_loader` tests cover lists, nested dictionaries, comments, quoted strings, multiline scalars, and malformed YAML diagnostics.
- The README states which rich metadata fields affect behavior and which are preserved only for humans or future exporters.
- Round-trip tests prove that import/export either preserves rich metadata text or intentionally normalizes it.
- `targets` semantics are implemented consistently across loader, validator, exporter, and documentation.

## Follow-up work

- Add a prompt-loading test suite focused on YAML frontmatter semantics and import resolution.
- Remove or rename `src/frontmatter` so Taurcode stops shadowing `python-frontmatter`.
- Decide whether `targets` is currently supported behavior or reserved design metadata, then update README and validation accordingly.
- Add a packaging check that confirms installed top-level packages are only Taurcode-owned names.
- Consider pinning `python-frontmatter>=1.1.0` after behavior is validated against the supported prompt corpus.
