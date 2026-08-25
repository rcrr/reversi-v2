# NOTES.md — entry point

## Project
File-by-file modernization of Roberto Corradini's Reversi engine
(18-year-old repo). This workspace is a staging area: only files under active
work live here. Full-repo restructure: planned, not now (see notes/decisions.md).

## Inventory
| Item | Status | Note |
|---|---|---|
| board.py | analyzed 2026-08-25, untouched | notes/board.md |
| test_board.py | NOT YET COPIED (user has tests in the original repo) | pending |
| logistello-papers/ | reference material, read-only | user's papers |

## Conventions in the code (respect them in any new work)
- Dual scalar/array API: public functions accept scalar OR 1-D array, return
  the input kind. Same validation pattern everywhere
  (is_scalar → atleast_1d → ndim check → dispatch → reshape back).
- `@validate_call` (pydantic, arbitrary_types_allowed) on all public functions.
- Numba `njit(cache=True)` + `prange` for hot loops; numba overloads for the
  four D8 primitives (fa1h8, fh1a8, fhori, fvert).
- Position = numpy structured dtype `[('mover', u64), ('opponent', u64)]`.
- Move codes: 0..63 = squares, 64 = PA (pass), 65 = NA, 66 = UN.

## Where we are
- board.py fully analyzed; 5 real issues + minor ones catalogued
  (notes/board.md). Nothing changed in board.py yet.
- Collaboration memory set up: AGENTS.md (auto-injected) + this file + notes/.
  Git repo initialized (D-003).

## Next steps
1. Copy test_board.py here; analyze it, run it, extend coverage of the
   fragile points in notes/board.md (esp. R1–R5 and the numba overloads).
2. Decide, issue by issue, what to fix in board.py (start with R1:
   `position_make_move` returns `None` on illegal move vs docstring).
3. Feed notes/ideas.md with Roberto's future-evolution ideas.

## Index
- notes/board.md — board.py analysis (distilled + full review in appendix)
- notes/decisions.md — decisions log (D-NNN)
- notes/ideas.md — future backlog (I-NNN)
- notes/log.md — session journal
