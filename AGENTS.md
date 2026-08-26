# AGENTS.md — reversi staging workspace

## What this is
Staging workspace for the modernization of Roberto Corradini's Reversi engine
(18-year-old repo; see board.py header). Source files are copied in one at a
time and developed here. A full-repo restructure is planned later — do not
propose repo-wide reorganization now.

## Standing rules
1. Before working: read NOTES.md (state, next steps, index).
2. Notes are autonomous: after each milestone and at the end of a work
   session, update NOTES.md and the relevant notes/ files without being asked.
3. Source files (*.py and any code): modify ONLY on explicit user request.
   logistello-papers/ is read-only reference material.
4. Notes and comments in this workspace: English. Replies to the user: Italian.
5. Every source file src/X.py gets its doc at docs/src/X.md (mirror rule,
   D-007): architecture, verified invariants, issues, conventions.
6. Every decision (including "leave as-is for now") goes to notes/decisions.md
   with date and rationale. Session summary goes to notes/log.md.

## Naming convention (canonical — full text: notes/naming.md)
This is Reversi, NOT chess: the board vocabulary is **column** (A–H,
left→right) and **row** (1–8, top→bottom) — never "file"/"rank". Square
name: column letter then row number. A1 = top-left (N-W) = bit 0 (LSB);
H8 = bottom-right (S-E) = bit 63 (MSB). row_1 = [A1..H1];
column_a = [A1..A8]. (Set 2026-08-26, D-013: the code follows this
convention; do not "fix" names toward chess vocabulary.) The eight D8
board symmetries (names, fixed slot order, anti-transformations, corner
mappings) are canonized in notes/naming.md (D-014): the order is
arbitrary but fixed — do not reorder or rename. Board diagrams always
read row 1 on top, column a on the left.

## Layout
- AGENTS.md — this file; standing instructions only, keep it small
- NOTES.md — entry point: state, next steps, index (read first)
- src/ — all Python sources (D-006), package `twolm` (D-008):
  src/twolm/board.py, unit tests in src/twolm/test/
- docs/ — code documentation, mirrors src/ (D-007); docs/src/twolm/board.md
- notes/ — collaboration only: decisions.md · ideas.md · log.md
- logistello-papers/ — user's reference papers (read-only)
