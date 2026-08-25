# NOTES.md — entry point

## Project
File-by-file modernization of Roberto Corradini's Reversi engine
(18-year-old repo). This workspace is a staging area: only files under active
work live here. Full-repo restructure: planned, not now (see notes/decisions.md).

## Inventory
| Item | Status | Note |
|---|---|---|
| src/twolm/board.py | analyzed 2026-08-25, untouched | docs/src/twolm/board.md |
| src/twolm/test/test_board.py | copied 2026-08-25 (user), not yet analyzed | — |
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

## Environment
- Venv: `.venv/` (gitignored, D-010), Python 3.12.3, created 2026-08-25.
- Dependencies — minimal set, derived from the actual imports of
  src/twolm/board.py and src/twolm/test/test_board.py (no other
  third-party imports):
  - numpy 2.5.2 — bitboards / structured dtypes (the code implicitly
    requires NumPy ≥ 2.0, see R5)
  - pydantic 2.13.4 — @validate_call validation layer
  - numba 0.67.0 — njit / prange / overload on the hot path (pulls
    llvmlite 0.49.0 as a transitive dependency)
- Test command (NOT yet run — with Roberto):
  `PYTHONPATH=./src .venv/bin/python -m unittest twolm.test.test_board`

## Where we are
- board.py fully analyzed; 5 real issues + minor ones catalogued
  (docs/src/twolm/board.md). Nothing changed in board.py yet.
- Sources now live in the `twolm` package under src/ (D-008); board unit
  tests copied into src/twolm/test/ by the user.
- Environment ready: .venv with the minimal deps (D-010). Tests NOT run
  yet.
- Collaboration memory set up: AGENTS.md (auto-injected) + this file + notes/.
  Git repo initialized (D-003).

## Next steps
1. Run the test suite (`PYTHONPATH=./src python3 -m unittest
   twolm.test.test_board`); analyze test_board.py and extend coverage of the
   fragile points in docs/src/twolm/board.md (esp. R1–R5 and the numba
   overloads).
2. Decide, issue by issue, what to fix in board.py (start with R1:
   `position_make_move` returns `None` on illegal move vs docstring).
3. Feed notes/ideas.md with Roberto's future-evolution ideas.

## Index
- docs/src/twolm/board.md — board.py analysis (distilled + full review in appendix)
- notes/decisions.md — decisions log (D-NNN)
- notes/ideas.md — future backlog (I-NNN)
- notes/log.md — session journal
