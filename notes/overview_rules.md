# notes/overview.md — format rules (rigid)

Applies to notes/overview.md (R-030 in notes/rules.md — the entry-point rule: read first, updated after each milestone
and at the end of each work session). This file is rigid: follow it when editing the overview; a format change amends
this file in the same commit as its decision. The prose is wrapped to ~120 chars/line.

## The seven sections

- The overview opens with the pointer section (H2 `Format rules`, pointing at this file), then exactly the seven
  sections, in exactly this order: Project · Environment · Current state · Next steps · Source files · Test files ·
  Index.
- Language: English. Dates: YYYY-MM-DD.
- Reference families: D-NNN (the decisions), I-NNN (the ideas), R-NNN (a rule of the register), session N (the
  journals), T-NN (a test defect), R# (a code issue, never an R-NNN), M# (a minor note).

## Source files / Test files (the two tables)

- One table per kind, one row per tracked file, alphabetical by full path. One physical line per row; a literal `|`
  inside a cell is escaped `\|`.
- State cell: ONE line — a status word + the open/parked items (each with its governing D-pointer if any); the
  description is the mirror's job, the campaign history the decision log's.
- Suite/std\_run (Test files table ONLY): `<total>/<failures>/<skipped>/<vlong>/<vvlong>` under the standard pre-commit
  run (LONG=1, the live DB): total = unittest's "Ran N" (the skips included); the failures, the skips, and — of those —
  the VLONG- and VVLONG-gated counts.
- Doc cell: a markdown link to the mirror.

## Current state

- CURRENT STATE only, MAX 10 bullets — each a present fact NOT in the tables and NOT in the mirrors (the pipeline-wide
  state, the in-flight campaigns with their horizon, the cross-file contracts).
- NO bullet-per-campaign: the campaign lives in the journal + the decisions log, and its state leaves this section when
  the campaign ends.

## Next steps

- OPEN items only, no "Done" bullets.
- The list is NON-prioritized (the user picks the next item on demand).

## Index

- One bullet per notes/ file, a one-line description.
- The docs/ mirrors are not listed (their paths are the Doc column of the two tables).
- The description is the file's identity — no D pointers, no grammar details, no cross-references: those live in the
  files themselves.
