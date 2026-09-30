# notes/decisions.md — format rules (rigid)

Applies to the open log notes/decisions.md and the closed volumes decisions_NNN.md (R-004 in notes/rules.md). The prose
is wrapped to ~120 chars/line.

## Entries

- One entry per decision (including "leave as-is for now"); the log is append-only; a blank line before every entry.
- The entry header: `D-NNN | YYYY-MM-DD | the rationale`, one line; the continuation lines are indented exactly 9
  spaces; no other indentation.
- The D-numbers are global, monotonically increasing, never reused or renumbered — across the open log and every closed
  volume.
- Code spans for the paths and the function / file names; backslash-escaped asterisks and underscores (the math
  multiplications, the snake\_case identifiers), so the Markdown renders without stray italics (D-209, extended
  at D-365).

## Volumes and rotation

- The open volume keeps the name decisions.md; past 1000 lines (the D-118 cap, amended at D-333) it closes at a session
  boundary as decisions_NNN.md (zero-padded) and a new decisions.md is opened.
- A volume jump never cuts an entry; the closed volumes are the closed history.
