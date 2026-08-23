# Design Backlog

Lightweight list of deferred ideas that are not yet ready for a formal
proposal or work item. Each entry should record what was noted, why it was
deferred, and where it came from so a future reader can act on it without
re-deriving context.

---

## Sync Espanso `:land`/`:execute` prose with LRH's updated skill guidance

**Noted:** 2026-08-23, while updating this repo's `.claude/skills/` LRH
mirror (adding the `.agents`/Codex and Antigravity mirrors and refreshing
several stale skills — `lrh-closeout`, `lrh-codex-export`, `lrh-execute`,
`lrh-implement`, `lrh-land` — from a fresh LRH install) and creating this
backlog file for the first time.

**Idea:** `exports/espanso/taurcode/package.yml`'s `:land` and `:execute`
triggers (and, to a lesser extent, `exports/espanso/lrh/package.yml`)
independently reimplement the same gate/chain-authorization/REVIEW-LANDED
logic LRH's own `lrh-land`/`lrh-execute`/`lrh-confirm-fixes` skills carry —
several hundred lines of hand-written prose per trigger, not generated
from the skill source. LRH's skills have moved since these were last
synced: a platform-enforced recursion guard was added to `lrh-self-review`
(`disallowed-tools: Skill`, see `DEC-SELF-REVIEW-RECURSION-GUARD` in the
LRH repo), a confirm-before-write gate pattern was added to
`lrh-codex-export`, and `disable-model-invocation` was removed from all of
`lrh-self-review`/`lrh-confirm-fixes`/`lrh-land`/`lrh-execute` in favor of
`when_to_use` guidance plus explicit in-skill gates. None of that has been
reflected in the Espanso prose, which still documents the older flag-based
posture.

Audit `exports/espanso/taurcode/package.yml`'s `:land`/`:execute` (and
`:implement`) triggers against the current `.claude/skills/lrh-land/`,
`.claude/skills/lrh-execute/`, and `.claude/skills/lrh-self-review/`
mirrors in this repo (now current as of this backlog entry), and update
the Espanso text to match wherever the two have drifted — particularly
the recursion-guard and confirm-gate mechanics, which the Espanso prose
predates entirely.

**Status:** Tracked, not yet designed. Do not block routine skill-mirror
refreshes on this — the Espanso sync is a separate, larger prose-reconciliation
effort.

**Related:** `exports/espanso/taurcode/package.yml`; `exports/espanso/lrh/package.yml`;
LRH repo `DEC-SELF-REVIEW-RECURSION-GUARD`; LRH repo
`WI-CODEX-EXPORT-INVOCATION-FLAG-REMOVAL`.
