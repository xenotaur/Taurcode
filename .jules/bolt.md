## 2025-07-20 - Avoid split().join() for string parsing
**Learning:** In Python, doing `text.split("\n")` followed by `"\n".join()` on very large strings is a performance bottleneck because it allocates many strings and intermediate lists. Doing `find("\n---\n")` and slicing `text[index:]` performs all operations at the C level and is ~4x faster on large prompts.
**Action:** Always prefer `str.find()` + slicing or regex over `split().join()` when manipulating large strings if the condition allows it.

## 2025-07-20 - Avoid splitlines() on large text files
**Learning:** In Python, calling `splitlines(keepends=True)` or `split("\n")` on large string content allocates an array of strings in memory. If only a small portion of the text is required (such as frontmatter at the top of a file), this is highly inefficient.
**Action:** Replace `splitlines()` on the entire document with a string search (such as `.find("\n---\n")` or `re.search`) to identify the section to be split, slice out the section, and then `splitlines()` on the smaller slice.
