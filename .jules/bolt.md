## 2024-07-07 - O(N²) Loop in Espanso Import Matching
**Learning:** During Espanso prompt imports, matching existing prompts scaled at O(N×M) because `_match_existing_prompt` performed linear list comprehensions over all existing prompts for every single imported match.
**Action:** Always pre-compute hash maps for O(1) lookups when matching items across two large collections (like merging imported data with existing files) to reduce O(N²) bottlenecks to O(N).
