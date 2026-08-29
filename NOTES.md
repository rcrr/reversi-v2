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
| src/twolm/pattern.py | analyzed 2026-08-27 (D-019); all real issues resolved: R1 (D-020) principal = numerically lowest orbit mask + regression test; R2-R7 doc/hygiene fixes (D-021); R8 closed as little-endian-only platform note (D-022); minor sweep complete 2026-08-27: 19/19 items (D-023, D-024, D-025 + doc/hygiene/API fixes); D-032 (2026-08-28): Burnside attributes n_invariant_configs / n_unique_configs | docs/src/twolm/pattern.md |
| src/twolm/test/test_pattern.py | analyzed 2026-08-27: 12 classes / 50 tests / 3 PERF gates; 21/21 goldens independently re-derived (0 mismatches); 16 defects T1-T16 + T17 (sqa8/sqh1 fixtures swapped names/values) documented; fix campaign CLOSED: P0 (D-026-028, 6da0803) + P1 (D-029/030/031: row independence both public indexing APIs + EDGE 6561-entry dict pin) + P2 hygiene (D-033: T1-T7, T15-T16; T19 found+fixed in T2) + P2 breadth (D-034: T11-T14 + T17), suite 64/0/3 GREEN; T18 noted-only, M1 deferred | docs/src/twolm/test/test_pattern.md |
| src/twolm/mobility.py | analyzed 2026-08-28: Mobility/MobilitySet + popcount64 SWAR + Numba kernel; feature index formula + n_configurations (distinct index values) + sorted-order columns + hash all verified vs independent ground truth (V1-V8, 200-position differential); R1-R6 fix batch applied (D-035: docstrings + column-order contract + popcount64 test-helper + dead imports + property/repr alignment + n_instances as-is); M1-M5 disposed (D-036: M1 glossary shipped, M2/M3/M5 left as-is, M4 corrected — no PERF gates in any suite); suite 23/0/1 GREEN | docs/src/twolm/mobility.md |
| src/twolm/test/test_mobility.py | analyzed 2026-08-28: 2 classes / 23 tests / 1 PERF; 13 verified facts V1-V13 (0 mismatches, incl. 31-line popcount table and [53,13,66] golden); 9 defects T1-T9 documented (dead if-False block, stale raises_assertion names, 2 hash self-comparisons, header grammar, dead imports, no multi-position test, R5 __repr__ untested, cosmetic print-on-failure); fix campaign CLOSED (D-037: T1-T9, per-item approvals, single batch commit — P0 __repr__ goldens, P1 multi-position row independence, P2 hygiene/breadth incl. pinned hash literal 2e553593...208a94); suite 23 -> 26, GREEN 26/0/1 | docs/src/twolm/test/test_mobility.md |
| src/twolm/feature.py | analyzed 2026-08-28 (session 8): Feature (blocked __new__ + factories) + FeatureSet (intercept/mset/pset composition, sorted-order features, hash over child hash hex strings); all goldens re-derived independently (V1-V8, zero mismatches: 3x10 index matrix, 13 orbit sizes, 3 pinned hashes); R1-R4 fix batch applied (D-038: sha3_256 doc fix + column-layout contract + __init__ docstring + dead imports); M1 applied (D-039), M2 applied (D-040), M3 left as-is (D-041, follow-up I-007), M4 applied (D-042) — all disposed; suite 13/0/1 GREEN | docs/src/twolm/feature.md |
| src/twolm/test/test_feature.py | analyzed 2026-08-28 (session 8): 4 classes / 14 tests / 1 PERF; 9 verified facts W1-W9 (0 mismatches, incl. 3x10 matrix and f5663932 hash literal); 9 defects T1-T9 documented (dead if-False block w/ never-imported position_print, 6 dead imports, header grammar + "environmeant" typo, no names-order assert, partial-None FeatureSet untested, Feature repr/eq untested, cosmetic import-time spaces, no full print_summary golden); fix priorities proposed (P1 = T6); T6 applied (D-043: 3 partial-None tests with 3 genuine hash literals, suite 13 -> 16 run, GREEN 16/0/1), T1 applied (D-044: dead if-False block removed), T2 applied (D-045: 6 dead imports removed), T3 applied (D-046: header grammar), T5 applied (D-047: names-order assertion), T7 applied (D-048: repr/eq/unhashable goldens, 16 -> 19 run), T9 applied (D-049: full 38-line print_summary golden); T4 pending (Roberto's call), T8 left as-is | docs/src/twolm/test/test_feature.md |
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
  Fix campaign CLOSED (per-item approvals): P0 complete
  (D-026-028, commit 6da0803), P1 complete (D-029/030/031); in
  between: D-032 (2026-08-28) — Pattern Burnside attributes
  n_invariant_configs / n_unique_configs (formulas verified 29/29
  sample patterns before implementation; goldens incl. CORE 3/21 per
  Roberto). P2 then complete the same day: hygiene batch (D-033:
  T1-T7, T15-T16, each approved one at a time; T2 became
  print-on-failure per Roberto's proposal, which exposed T19 —
  position_print never imported — fixed in the same item), then
  breadth batch (D-034: T11 hash pin, T12 PatternType, T13
  mdp_record SNAKE/CORE/DIAG8, T14 collision preconditions, plus
  T17 sqa8/sqh1 fixture fix; T12 exposed a doc "11 members"
  miscount corrected to 12). Final suite: 64 tests, GREEN 64/0/3.
  Remaining known items: T18 noted-only (no code action), M1
  deferred (stale PatternSet Raises docstring, awaiting go-ahead).
- mobility.py analyzed (2026-08-28, session 7,
  docs/src/twolm/mobility.md): feature index formula
  `popcount(lms & mask) + (a − popcount(alms & amask))`,
  n_configurations = k + a + 1 (distinct index values — brute-force
  verified), columns in the set's SORTED (mask, amask) order (live
  verified; docstring gap R2), sha3_256 hash re-implemented from
  scratch (match), 200-position random differential test of
  compute_indexes vs pure Python (0 mismatches), popcount64 vs
  int.bit_count on 200,010 values (0 mismatches). No logic defect
  found. Fix candidates R1-R6 all approved and applied the same day
  (D-035 batch: class docstrings + column-order contract + popcount64
  test-helper + dead imports + property/repr alignment + n_instances
  as-is), no behavior change. Minor notes M1-M5 disposed the same
  day (D-036): M1 glossary shipped (LMC/ALMC/DLMC expansions from
  the 2008 program), M2/M3/M5 left as-is, M4 corrected after
  Roberto's challenge (no PERF gates in any suite — all PERF tests
  are print-only; ±30% is campaign comparison discipline).
- feature.py analyzed (2026-08-28, session 8,
  docs/src/twolm/feature.md): the first integration module —
  Feature (blocked __new__ + 3 factories, Category IntEnum) +
  FeatureSet (intercept + MobilitySet + PatternSet -> features
  list in child sorted order, n_instances sum 53, sha3_256 hash
  over b'INTERCEPT' + child hash hex strings, compute_indexes
  (N, I) hstack with (N, I) edge returns). All goldens re-derived
  independently (V1-V8, zero mismatches: 3x10 index matrix in
  pure Python, 13 orbit sizes, 3 pinned hashes). R1-R4 applied
  (D-038, single batch: sha3_256 doc fix, column-layout contract,
  __init__ docstring, dead imports) — no behavior change; M1
  applied (D-039), M2 applied (D-040), M3 left as-is (D-041,
  I-007), M4 applied (D-042) — all disposed. Suite 13/0/1 GREEN. test_feature.py analyzed
  the same day (docs/src/twolm/test/test_feature.md): 14 tests / 1
  PERF, 9 verified facts W1-W9 (0 mismatches), 9 defects T1-T9
  documented (dead if-False block referencing never-imported
  position_print, 6 dead imports, header grammar + "environmeant"
  typo, no names-order assert, partial-None FeatureSet untested
  (P1), Feature repr/eq untested, no full print_summary golden);
  campaign in progress one at a time: T6 (P1) applied (D-043,
  suite 16/0/1), T1 applied (D-044), T2 applied (D-045),
  T3 applied (D-046), T5 applied (D-047), T7 applied (D-048),
  T9 applied (D-049, suite 19/0/1); T4 pending (Roberto's call),
  T8 left as-is.
- R4/R5 remain doc-status only (no code action agreed).
- Sources live in the `twolm` package under src/ (D-008); board unit
  tests in src/twolm/test/. Environment: .venv with the minimal deps
  (D-010), twolm installed editable (D-011). Git repo on master (D-003).
- Collaboration memory: AGENTS.md (auto-injected) + this file + notes/.

## Next steps
- test_pattern.py fix campaign — **CLOSED** (all P0/P1/P2 items
  approved and done; D-026…D-034; suite 64/0/3, GREEN). Remaining
  known items (out of scope of the closed campaign): T18 noted-only
  (np.uint8 `3**n_squares` overflow, no code action); M1 deferred
  (stale PatternSet Raises docstring, awaiting go-ahead);
  test_board.py header nits (reported, out of scope).
- mobility.py: analysis DONE (2026-08-28, docs/src/twolm/mobility.md).
  R1-R6 fix batch DONE (D-035); M1-M5 disposed (D-036).
  test_mobility.py analyzed + fix campaign CLOSED the same day
  (D-037, defects T1-T9, per-item approvals; suite 23 -> 26,
  GREEN 26/0/1). Mobility module fully done: analysis + R1-R6
  (D-035) + M1-M5 (D-036) + test campaign (D-037).
- The plan (confirmed by Roberto, 2026-08-28, session close): port
  the ENTIRE pipeline — the original repo brought in module by
  module, this staging workspace's work — with VERIFIED code and
  COMPLETE tests as the goal: a solid base before further
  evolution (Roberto has a list of future changes in mind, out of
  scope for the port). Done so far: board.py (2026-08-26, proven
  complete game kernel), pattern.py, mobility.py. The game-loop
  module is NOT in the plan (I-005 resolved). Now: feature.py —
  analysis done (e9adf7b) + R1-R4 (D-038) + test analysis
  (T6 applied D-043, T1 applied D-044, T2 applied D-045,
  T3 applied D-046, T5 applied D-047, T7 applied D-048,
  T9 applied D-049, T4 pending Roberto's call, T8 left
  as-is). M1 applied (D-039), M2 applied (D-040), M3 left
  as-is (D-041, I-007), M4 applied (D-042) — all disposed.
  Pattern R4/R5 remain doc-status only, parked.
- Feed notes/ideas.md with Roberto's future-evolution ideas.

## Index
- docs/src/twolm/board.md — board.py analysis (distilled + full review in appendix)
- docs/src/twolm/pattern.md — pattern.py analysis (R1-R8 resolved: D-020,
  D-021, D-022; little-endian-only platform note; minor sweep complete:
  19/19 items, D-023/D-024/D-025 + hygiene/API fixes)
- docs/src/twolm/test/test_board.md — test_board.py analysis (coverage by area,
  verified values, 11 defects, completeness verdict + priorities)
- docs/src/twolm/test/test_pattern.md — test_pattern.py analysis (coverage by
  area, 21 verified facts, defects T1-T19 (T17/T19 found during the
  campaign), completeness verdict +
  P0/P1/P2 priorities)
- docs/src/twolm/mobility.md — mobility.py analysis (feature index formula,
  n_configurations semantics, sorted-order columns, verified V1-V8,
  R1-R6 applied D-035, minor M1-M5 disposed D-036)
- docs/src/twolm/test/test_mobility.md — test_mobility.py analysis (coverage by
  area, 13 verified facts, defects T1-T9, completeness verdict +
  P0/P1/P2 priorities)
- docs/src/twolm/feature.md — feature.py analysis (first pipeline
  integration module: Feature factories + blocked __new__, FeatureSet
  composition/hash/column layout, verified V1-V8, R1-R4 applied D-038,
  minor M1 D-039, M2 D-040, M3 left as-is D-041/I-007, M4 D-042 — all disposed)
- docs/src/twolm/test/test_feature.md — test_feature.py analysis
  (coverage by area, 9 verified facts W1-W9, defects T1-T9,
  completeness verdict + P1/P2 priorities; T6 applied D-043,
  rest pending)
- notes/naming.md — canonical board naming convention (row/column, D-013)
- notes/decisions.md — decisions log (D-NNN)
- notes/ideas.md — future backlog (I-NNN)
- notes/log.md — session journal
