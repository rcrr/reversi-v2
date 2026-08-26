# NOTES.md — entry point

## Project
File-by-file modernization of Roberto Corradini's Reversi engine
(18-year-old repo). This workspace is a staging area: only files under active
work live here. Full-repo restructure: planned, not now (see notes/decisions.md).

## Inventory
| Item | Status | Note |
|---|---|---|
| src/twolm/board.py | analyzed 2026-08-25; modified by fix campaign (T22, T25, T36, T37, T38) | docs/src/twolm/board.md |
| src/twolm/test/test_board.py | analyzed 2026-08-25; fix campaign completed 2026-08-26, suite GREEN 193/0/12 | docs/src/twolm/test/test_board.md |
| logistello-papers/ | reference material, read-only | user's papers |

## Conventions in the code (respect them in any new work)
- Board vocabulary is canonical: **row** (1–8, top→bottom) and **column**
  (A–H, left→right) — never file/rank (chess). A1 = top-left (N-W) = bit 0;
  H8 = bottom-right (S-E) = bit 63. row_1 = [A1..H1]; column_a = [A1..A8].
  Full text: notes/naming.md (D-013).
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
- Suite status (2026-08-26, post-campaign): GREEN — 193 tests, 0
  failures, 12 skipped (all 12 are PERF=1 performance gates). Warm run
  ≈ 0.5 s wall (numba cache warm in src/twolm/__pycache__/).

## Where we are
- board.py fully analyzed (docs/src/twolm/board.md); test_board.py fully
  analyzed (docs/src/twolm/test/test_board.md).
- Fix campaign COMPLETE (2026-08-26): all P0 + P1 items, R1 (T36/T37,
  D-017), R3 (T38, D-018), and the full P2 batch (T26–T35, one commit,
  Roberto's explicit "Facciamoli tutti, un solo commit"). Suite grew
  157 → 193 tests, stayed GREEN throughout. Journal: notes/log.md;
  decisions: notes/decisions.md (D-001…D-018).
- R4/R5 remain doc-status only (no code action agreed).
- Sources live in the `twolm` package under src/ (D-008); board unit
  tests in src/twolm/test/. Environment: .venv with the minimal deps
  (D-010), twolm installed editable (D-011). Git repo on master (D-003).
- Collaboration memory: AGENTS.md (auto-injected) + this file + notes/.

## Next steps
- Campaign closed (suite GREEN 193/0/12). Next session: start a NEW
  module (Roberto's plan; I-005) — module to be chosen with Roberto:
  game-loop module (board.py is proven a complete game kernel, 2026-08-26)
  or the next source file of the original repo. R4/R5 remain doc-status
  only, parked.
- Feed notes/ideas.md with Roberto's future-evolution ideas.

## Index
- docs/src/twolm/board.md — board.py analysis (distilled + full review in appendix)
- docs/src/twolm/test/test_board.md — test_board.py analysis (coverage by area,
  verified values, 11 defects, completeness verdict + priorities)
- notes/naming.md — canonical board naming convention (row/column, D-013)
- notes/decisions.md — decisions log (D-NNN)
- notes/ideas.md — future backlog (I-NNN)
- notes/log.md — session journal
