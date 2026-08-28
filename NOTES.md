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
| src/twolm/pattern.py | analyzed 2026-08-27 (D-019); all real issues resolved: R1 (D-020) principal = numerically lowest orbit mask + regression test; R2-R7 doc/hygiene fixes (D-021); R8 closed as little-endian-only platform note (D-022); minor sweep complete 2026-08-27: 19/19 items (D-023, D-024, D-025 + doc/hygiene/API fixes) | docs/src/twolm/pattern.md |
| src/twolm/test/test_pattern.py | analyzed 2026-08-27: 12 classes / 50 tests / 3 PERF gates; 21/21 goldens independently re-derived (0 mismatches); 16 defects T1-T16 documented; fix campaign in progress: P0 complete (D-026/D-027/D-028: #16 repr golden + #17 empty PatternSet + #18 empty mask), suite 53/0/3 | docs/src/twolm/test/test_pattern.md |
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
- D8 slot order is fixed and load-bearing (D-014): anti-transform slot s
  = T_s^{-1}; in pattern.py instance 0 = the ro000 image, and
  trans_fs/anti_trans_fs are indexed by instance (length = n_instances),
  not by slot.
- Pattern config indexes are base-3 uint32 over ≤ 18 squares (S ≤ 18);
  packed bit k ↔ the k-th square of `Pattern.squares` (ascending board
  order); principal index = min over the induced-stabilizer orbit.

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
  decisions: notes/decisions.md (D-001…D-019).
- pattern.py analyzed (2026-08-27, docs/src/twolm/pattern.md). All real
  issues resolved the same day: R1 (D-020) principal mask = numerically
  lowest orbit mask (unique representative; the 4-corners corner case),
  regression test in test_pattern.py; R2-R7 (D-021) docstring/hygiene
  fixes, code behavior untouched (approved one at a time); R8 (D-022)
  closed by decision — the set-hash endianness stays native, and both
  module docs now state the engine is tested on little-endian only.
  Minor sweep COMPLETE the same day (19/19 items, each approved one at
  a time): D-023 (#6 strict @validate_call constructor — TypeError →
  ValidationError), D-024 (#15 names/masks → @property; legacy
  .names()/.masks() call sites tracked as I-006 for migration), D-025
  (#19 collision precondition stays on the caller, documented), plus
  fail-fast checks (#17 empty PatternSet, #18 empty mask), constant
  rename (#12), type-table cross-check (#11), and doc/hygiene/API
  consistency fixes (#2-#5, #7-#10, #13, #14, #16). test_pattern.py:
  suite GREEN 50/0/3 (run only, analysis deferred).
- test_pattern.py analyzed (2026-08-27,
  docs/src/twolm/test/test_pattern.md): 12 classes, 50 tests, 3 PERF
  gates. Verification: 21/21 golden values independently re-derived
  (twolm.board + pure arithmetic only, no twolm.pattern import) — zero
  value mismatches. 16 test-file defects documented (T1-T16); the
  material gaps are the three shipped-but-untested minor-sweep paths
  (#16 __repr__, #17 empty PatternSet, #18 empty mask) and the
  uniform-np.full-only array tests of the public indexing pipeline.
  Fix campaign proposed (P0/P1/P2), awaiting per-item approval.
- R4/R5 remain doc-status only (no code action agreed).
- Sources live in the `twolm` package under src/ (D-008); board unit
  tests in src/twolm/test/. Environment: .venv with the minimal deps
  (D-010), twolm installed editable (D-011). Git repo on master (D-003).
- Collaboration memory: AGENTS.md (auto-injected) + this file + notes/.

## Next steps
- test_pattern.py fix campaign (per-item approval, D-019 pattern) —
  priorities in docs/src/twolm/test/test_pattern.md section 7.5:
  P0 = tests for the 3 untested minor-sweep paths (#16 __repr__,
  #17 empty PatternSet, #18 empty mask); P1 = multi-position
  row-independence array tests + direct EDGE 6561-entry principal dict;
  P2 = hygiene (T1-T7, T15-T16) + breadth (hash pin, PatternType,
  mdp_record SNAKE/CORE/DIAG8) + deferred M1 stale Raises docstring.
- Then: next module of Roberto's plan (game-loop module — board.py is a
  proven complete game kernel, 2026-08-26 — or the next source file of
  the original repo). R4/R5 remain doc-status only, parked.
- Feed notes/ideas.md with Roberto's future-evolution ideas.

## Index
- docs/src/twolm/board.md — board.py analysis (distilled + full review in appendix)
- docs/src/twolm/pattern.md — pattern.py analysis (R1-R8 resolved: D-020,
  D-021, D-022; little-endian-only platform note; minor sweep complete:
  19/19 items, D-023/D-024/D-025 + hygiene/API fixes)
- docs/src/twolm/test/test_board.md — test_board.py analysis (coverage by area,
  verified values, 11 defects, completeness verdict + priorities)
- docs/src/twolm/test/test_pattern.md — test_pattern.py analysis (coverage by
  area, 21 verified facts, 16 defects T1-T16, completeness verdict +
  P0/P1/P2 priorities)
- notes/naming.md — canonical board naming convention (row/column, D-013)
- notes/decisions.md — decisions log (D-NNN)
- notes/ideas.md — future backlog (I-NNN)
- notes/log.md — session journal
