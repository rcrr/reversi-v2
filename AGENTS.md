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
5. Every source file brought in gets a note notes/<file>.md: architecture,
   verified invariants, issues, conventions.
6. Every decision (including "leave as-is for now") goes to notes/decisions.md
   with date and rationale. Session summary goes to notes/log.md.

## Layout
- AGENTS.md — this file; standing instructions only, keep it small
- NOTES.md — entry point: state, next steps, index (read first)
- notes/ — board.md · decisions.md · ideas.md · log.md
- board.py — source under development (see notes/board.md)
- logistello-papers/ — user's reference papers (read-only)
