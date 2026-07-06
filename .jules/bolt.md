## 2024-07-06 - Frontmatter vs String Operations in prompt loading
**Learning:** `python-frontmatter` uses `pyyaml` under the hood. While loading, we replaced using `frontmatter.loads()` completely with a naive `.split("\n")` which iterates lines. The codebase had optimized the `.split("\n")` to a highly efficient string `.find("\n---\n")` search because the body extraction executes for every single file. Wait, in `extract_prompt_body`, the current code is already split-based.

## 2024-07-06 - O(N*M) lookup in Espanso Import
**Learning:** The `_merge_simple_matches` function in `espanso_import.py` loops over all `entries` (new matches) and calls `_match_existing_prompt`, which does list comprehensions over `existing_prompts` twice for every single match entry. This creates an O(N*M) performance bottleneck when importing a large espanso package (like one with 10k triggers).
**Action:** Pre-compute dictionaries mapping keywords and file stems to their corresponding `ExistingPrompt` objects to achieve O(1) lookups and O(N+M) total complexity.
