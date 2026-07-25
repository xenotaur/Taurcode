## 2025-07-20 - Avoid split().join() for string parsing
**Learning:** In Python, doing `text.split("\n")` followed by `"\n".join()` on very large strings is a performance bottleneck because it allocates many strings and intermediate lists. Doing `find("\n---\n")` and slicing `text[index:]` performs all operations at the C level and is ~4x faster on large prompts.
**Action:** Always prefer `str.find()` + slicing or regex over `split().join()` when manipulating large strings if the condition allows it.
