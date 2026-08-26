# NOTES.md — entry point

## Project
File-by-file modernization of Roberto Corradini's Reversi engine
(18-year-old repo). This workspace is a staging area: only files under active
work live here. Full-repo restructure: planned, not now (see notes/decisions.md).

## Inventory
| Item | Status | Note |
|---|---|---|
| src/twolm/board.py | analyzed 2026-08-25, untouched | docs/src/twolm/board.md |
| src/twolm/test/test_board.py | analyzed 2026-08-25, untouched; suite GREEN 2026-08-25 | docs/src/twolm/test/test_board.md |
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
- Packaging: `pyproject.toml` (setuptools, src layout) with twolm installed
  editable in .venv (`pip install -e .`, D-011) — `import twolm` works
  without PYTHONPATH, resolving to src/.
- Dependencies — minimal set, derived from the actual imports of
  src/twolm/board.py and src/twolm/test/test_board.py (no other
  third-party imports):
  - numpy 2.5.2 — bitboards / structured dtypes (the code implicitly
    requires NumPy ≥ 2.0, see R5)
  - pydantic 2.13.4 — @validate_call validation layer
  - numba 0.67.0 — njit / prange / overload on the hot path (pulls
    llvmlite 0.49.0 as a transitive dependency)
- Test command: `.venv/bin/python -m unittest twolm.test.test_board`
  (the old `PYTHONPATH=./src` prefix still works as a fallback)
- Suite status (2026-08-25): GREEN — 157 tests, 0 failures, 12 skipped
  (all 12 are PERF=1 performance gates). Warm run ≈ 1.2 s wall
  (numba cache warm in src/twolm/__pycache__/).

## Where we are
- board.py fully analyzed; 5 real issues + minor ones catalogued
  (docs/src/twolm/board.md). Nothing changed in board.py yet.
- test_board.py fully analyzed; 11 test-file defects + 10 systemic
  gaps catalogued, R1–R5 status mapped, completeness verdict written
  (docs/src/twolm/test/test_board.md). Nothing changed in the test
  file yet (D-012).
- Sources now live in the `twolm` package under src/ (D-008); board unit
  tests copied into src/twolm/test/ by the user.
- Environment ready: .venv with the minimal deps (D-010), twolm installed
  editable in it (D-011). Suite GREEN (157 tests, 12 PERF skips).
- Collaboration memory set up: AGENTS.md (auto-injected) + this file + notes/.
  Git repo initialized (D-003).

## Next steps
1. Decide, issue by issue, what to fix in board.py (start with R1:
   `position_make_move` returns `None` on illegal move vs docstring —
   note: the suite pins the current None behaviour
   (test_position_make_move_illegal_returns_none), so the decision is
   code-vs-docstring and the test must follow).
2. Decide on the test suite: fix the catalogued defects (P0: broken
   2-D test, 2 NameError landmines, dead assertion) and/or expand
   coverage (P1 fragile pins, P2 expansion) — source/test edits only
   on explicit request (D-004).
3. Feed notes/ideas.md with Roberto's future-evolution ideas.

## Index
- docs/src/twolm/board.md — board.py analysis (distilled + full review in appendix)
- docs/src/twolm/test/test_board.md — test_board.py analysis (coverage by area,
  verified values, 11 defects, completeness verdict + priorities)
- notes/decisions.md — decisions log (D-NNN)
- notes/ideas.md — future backlog (I-NNN)
- notes/log.md — session journal
