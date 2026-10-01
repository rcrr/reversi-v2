# notes/overview.md — format rules (rigid)

Applies to notes/overview.md (R-030 in notes/rules.md — the entry-point rule: read first, updated after each milestone
and at the end of each work session). This file is rigid: follow it when editing the overview; a format change amends
this file in the same commit as its decision. The prose is wrapped to ~120 chars/line.

## The eight sections

- Exactly the eight sections, in exactly this order: Project · Conventions in the code · Environment · Current state ·
  Next steps · Source files · Test files · Index.
- Language: English. Dates: YYYY-MM-DD.
- Reference families: D-NNN (the decisions), I-NNN (the ideas), R-NNN (a rule of the register), session N (the
  journals), T-NN (a test defect), R# (a code issue, never an R-NNN), M# (a minor note).

## Source files / Test files (the two tables)

- One table per kind, one row per tracked file, alphabetical by full path. One physical line per row; a literal `|`
  inside a cell is escaped `\|` (D-116).
- State cell: ONE line — a status word + the open/parked items (each with its governing D-pointer if any); the
  description is the mirror's job, the campaign history the decision log's (D-117, clarified D-335).
- Suite count (Test files table ONLY): `<total>/<failures>/<skipped>` under the standard pre-commit run (LONG=1, the
  live DB; total = unittest's "Ran N"); a (+N VLONG) marker for the tier-gated tests that skip in it (D-117,
  amended D-339).
- Doc cell: a markdown link to the mirror (D-117, amended D-339).

## Current state

- CURRENT STATE only, MAX 10 bullets — each a present fact NOT in the tables and NOT in the mirrors (the pipeline-wide
  state, the in-flight campaigns with their horizon, the cross-file contracts).
- NO bullet-per-campaign: the campaign lives in the journal + the decisions log, and its state leaves this section when
  the campaign ends (D-334).

## Next steps

- OPEN items only, no "Done" bullets.
- The list is NON-prioritized (Roberto picks the next item on demand) (D-117, amended D-337).

## Index

- One bullet per notes/ file, a one-line description.
- The docs/ mirrors are not listed (their paths are the Doc column of the two tables).
