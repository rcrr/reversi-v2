# test_pattern.py — test-suite analysis for `twolm.pattern`

_Analyzed 2026-08-27 (session 5), per the deferred analysis promised in D-019.
Doc-only analysis: no source or test edits in this session — a fix campaign
awaits explicit per-item approval, same pattern as pattern.py (D-019)._

Suite status at analysis time: pattern suite **50/0/3** (3 PERF skips),
full discover **243/0/15** OK, PERF=1: pattern 50 OK. Source under test:
`src/twolm/pattern.py` (1250 lines), HEAD `3b4fee0` (post minor-sweep,
sweep code committed in `c031f8c`).

---

## 1. What this file is

- **1488 lines**, **12 TestCase classes**, **50 test methods** (3 of them
  behind `PERF=1` gates → default run is 47 executed + 3 skipped = 50/0/3).
- Mirror test suite for `src/twolm/pattern.py`: the pattern bitboard/packing
  layer (D8 transforms, pack plans, symmetry functions, base-3 configuration
  indexes, principal indexes, `Pattern`/`PatternSet`, MDP record/CSV output).
- The suite is **golden-value heavy**: it pins full output strings
  (`print`, `mdp_record`), full pack-plan triples, full principal-index dicts
  (9, 27, 81 entries), 49 first-row values of a 3×49 set pipeline, and
  per-pattern `symmetry_fs` for 29 named patterns.
- It is the natural companion of the pattern.py analysis
  (docs/src/twolm/pattern.md): where that doc describes behaviour, this file
  records what is pinned, what was independently re-derived, and what is
  missing.

## 2. Suite conventions

- **Run command** (header, L38-41): from the workspace root,
  `source .venv/bin/activate` then `time PERF=0 python3 -m unittest
  twolm.test.test_pattern`. Valid: `src/twolm/test/__init__.py` exists, so
  the dotted path resolves.
- **Shared position fixture**: `mover = bitboard_from_signed_int(
  np.int64(4611717676283199524))`, `opponent = bitboard_from_signed_int(
  np.int64(-7855295674223658936))` → `make_position(mover, opponent)` —
  the same position as the board suite; used by
  `TestPatternComputeIndexes` and `TestPatternSetComputePrincipalIndexes`.
- **Dual scalar/array API** (per project convention): every public
  compute function is tested with a scalar position, with a 1-D array of
  positions, and (where applicable) at 1 M size under the PERF gate.
- **PERF gates**: `@unittest.skipUnless(os.environ.get('PERF') == '1', ...)`
  — 3 occurrences (pack 1 M L620, `compute_indexes_on_position` 1 M L1015,
  set `compute_principal_indexes` 1 M L1469).
- **Imports**: star import `from twolm.pattern import *` (exposes `__all__`
  = Index, IndexArray, Pattern, PatternType, sample_pattern_data,
  PatternSet) plus explicit board-function imports; the 29-pattern
  `sample_pattern_data` is exercised by the Cayley-table test.
- **Module-level D8 fixtures** (L66-79): `ar` (the "test position") plus
  7 pre-transformed copies. Only `ar` is referenced (Cayley tests); the
  7 `ar_*` names are dead (see §5, T3).
- **Golden styles**: full-string goldens for `print`/`mdp_record`
  (multi-line lists joined with `\n` + trailing newline);
  `np.array` goldens for pack plans, index vectors, first-row pipeline
  values; `nptest.assert_array_equal` for arrays; per-row `subTest`
  (symmetry table); `mock_open` + `MagicMock(spec=Pattern)` to isolate the
  `mdp_csv_file` classmethod.
- **Error-path conventions**: `assertRaises` + message substring
  (`"not principal"`, `"duplicate names"`, `"duplicate masks"`), except
  `mdp_csv_file` where all three `TypeError` messages are asserted with
  exact `assertEqual`.
- **Row diversity**: the 1 M pack PERF tiles the 18 distinct setUp
  bitboards (`np.tile`), so the pack/unpack kernels *are* exercised on
  mixed rows — but the two public indexing functions (below) are only
  exercised on uniform `np.full` arrays (§5 T9).

## 3. Coverage by area

Inventory of the 12 classes (line ranges, method counts, what is pinned):

| # | Class (lines) | Tests | Pins |
|---|---|---|---|
| 1 | `TestPattern` (L100–187) | 7 | constructor strictness (2 `ValidationError`, >18 squares `ValueError`), ELLE full-attribute golden (tmasks 8, cells, mask indexes, uniques, tr/at/sf, transformed + sorted cells, fingerprint, type), non-principal `ValueError` (BAD_ELLE), **R1 regression** (D-020: FOURC 4-corners constructs, `squares = [A1, A8, H1, H8]`, principal = `0x8100000000000081`, plus b1/a2/h2 edge cases) |
| 2 | `TestPatternPack` (L189–652) | 7 | setUp builds 18 bitboards (empty, full, rows 1-8, columns 1-8); `run_test_vectorized` helper (vectorized pack vs golden + unpack round-trip & mask recovery); pack-plan + scalar + vectorized goldens for **ELLE, EDGE, R2, CORNER, DIAG8, FOURC**; PERF 1 M over 5 patterns × tiled 18-board array |
| 3 | `TestPatternSymmetries` (L655–710) | 1 | 29-row table (mask, name, expected `symmetry_fs`): ELLE, SNAKE, EDGE, R2-R4, XEDGE, DIAG3-DIAG8, CORNER, 2X5COR, 2X6COR, RCT2X4, CASTLE, BARBEL, MACE, FOURC, CORE, CORED, COREA, WHIRL, TAU, DOTA1, DOTB1, TWOND; `test_pattern_invariance` asserts `p.symmetry_fs == expected` per row under `subTest` |
| 4 | `TestPatternMdpRecord` (L712–755) | 2 | full 24-column `mdp_record()` strings for ELLE (4 squares) and EDGE (8 squares) — includes tmasks, mask indexes, uniques, tr/at/sf, transformed cells, fingerprint, type columns |
| 5 | `TestTransformationsCayleyTable` (L757–866) | 4 | local 8 D8 functions in paper order (e, r, r2, r3, sv, sh, d1, d2) + `trm = [0,1,2,3,4,6,7,5]` relabel to canonical D8 slot order (D-014 note in docstring); 8×8 Cayley table as function references; `verify_cayley_table` checks `cayley[i,j](data) == trs[j](trs[i](data))` on: `ar` (the "cog"), 14 structural bitboards (full, empty, 4 corner squares, 2 rows, 2 columns, 4 halves), all 29 `sample_pattern_data` masks |
| 6 | `TestPatternPrint` (L868–895) | 1 | EDGE `print()` — full 13-line string golden (cells, tmasks, mask indexes, unique masks/indexes, tr/at/sf names, transformed + sorted cells 8×8, fingerprint, type) |
| 7 | `TestPatternMdpCsvFile` (L897–974) | 5 | classmethod isolation (`MagicMock(spec=Pattern)` + `mock_open`); 3 `TypeError` tests with exact messages (patterns not list, filename not str, element not Pattern); `writes_correct_content` (24-column header + 2 data rows); empty-list (header only) |
| 8 | `TestPatternComputeIndexes` (L976–1042) | 3 | scalar EDGE on the shared position → per-instance indexes `[1764, 5940, 1517, 81]`; array N=3 (`np.full`); PERF 1 M (tiled golden); `position_check_collisions` called before each call |
| 9 | `TestPatternSet` (L1044–1198) | 10 | init + sort order (EDGE < ELLE < SNAKE by mask value), 3 invalid-input `ValidationError` (stale "raises_assertion" names, T4), `names`/`masks` properties (property-style access per D-024), `print_summary` + `print` goldens (hash line self-referential, T11), duplicate-name `ValueError`, duplicate-mask `ValueError` |
| 10 | `TestPatternPrincipalIndex` (L1200–1231) | 1 | ELLE: shape (81,), property-based invariants (every `principal[i] <= i`, `principal[0] == 0`); no value golden (the full identity dict is pinned in class 11) |
| 11 | `TestPatternComputePrincipalIndexDict` (L1233–1328) | 6 | **SMALL** 9-entry dict + 6 unique; **CORNER** 2 spot checks; **CORE** full 81-entry dict + 21 unique; **DIAG3** full 27-entry dict + 18 unique; **ELLE** full identity dict (81); `convert_to_principal_index` CORE `[9,0,80,19] → [1,0,80,5]` |
| 12 | `TestPatternSetComputePrincipalIndexes` (L1330–1488) | 3 | 3-pattern set (ELLE, CORE, EDGE): `test_one_record` → 13 values `[420,116,1517,27 | 9,54,59,54,15,35,6,0 | 44]`; 13-pattern "50_PLUS" set: `test_large_set` pins mask-sorted order, (i, I, r0, r1) attribution for all 13, shape (3, 49), dtype, and the full 49-value first row; PERF 1 M with the same first-row golden |

Method total: 7+7+1+2+4+1+5+3+10+1+6+3 = **50** ✓.

Notes on the large-set goldens (L1344–1406): the 13 patterns are
R2, R3, R4, XEDGE, DIAG4…DIAG8, CORNER, 2X5COR, RCT2X4, CORE; the expected
order (mask-sorted) is
2X5COR, XEDGE, R2, CORNER, R3, DIAG4, R4, DIAG5, CORE, RCT2X4,
DIAG6, DIAG7, DIAG8; J = 49; the per-pattern column blocks are
`(i, I, r0, r1)`: 2X5COR (0, 8, 0, 7), XEDGE (1, 4, 8, 11), R2 (2, 4, 12, 15),
CORNER (3, 4, 16, 19), R3 (4, 4, 20, 23), DIAG4 (5, 4, 24, 27),
R4 (6, 4, 28, 31), DIAG5 (7, 4, 32, 35), CORE (8, 1, 36, 36),
RCT2X4 (9, 2, 37, 38), DIAG6 (10, 4, 39, 42), DIAG7 (11, 4, 43, 46),
DIAG8 (12, 2, 47, 48). The one-record width 13 = 4 (EDGE) + 8 (ELLE) +
1 (CORE) = Σ n_instances of the 3-pattern set.

## 4. Verified facts (independently re-derived — no value mismatches)

Method: two scratch scripts using **only `twolm.board`** (itself
campaign-verified) **plus pure arithmetic** — no `twolm.pattern` import, so
the checks are non-circular — plus hand derivations:

- `scratch/verify_pattern_tests2.py` — 10/10 PASS
- `scratch/verify_pidx.py` — 5/5 PASS
- pack-plan checks below — 6/6 PASS (this session)

**A. Orbit structure (29 symmetry-table masks)**
1. All 29 masks are the **numerical minimum of their D8 orbit** (the R1
   rule, D-020) — consistent with the strict constructor (D-023) accepting
   every one of them.
2. Orbit size divides 8 for all 29 (|Orb| · |Stab| = 8).

**B. Pack plans (6/6)**
3. ELLE `[0x7, 0x100] / [0x7, 0x8] / [0, 5]`
4. EDGE `[0xff] / [0xff] / [0]`
5. R2 `[0xff00] / [0xff] / [8]`
6. CORNER `[0x7, 0x700, 0x70000] / [0x7, 0x38, 0x1c0] / [0, 5, 10]`
7. DIAG8 `[0x80, 0x4000, …, 0x0100000000000000] / [1..128] / [7, 13, …, 49]`
8. FOURC `[0x1, 0x80, 1<<56, 1<<63] / [0x1, 0x2, 0x4, 0x8] / [0, 6, 54, 60]`

   all match the documented run-length algorithm (maximal runs of
   consecutive set bits; `pack_mask` = run at its source location,
   `unpack_mask` = destination block, `shift = start_source − dest_pos`).

**C. Transformed masks**
9. ELLE `tmasks` (8 orbit masks, canonical D8 slot order) recomputed from
   board.py transforms — exact match (the same values are re-pinned by the
   set-print golden L1151 and the mdp golden).

**D. Principal-index dicts** (digit order = ascending board-bit order of
`Pattern.squares`; images minimized over `[ro000] + symmetry_fs` slots)
10. SMALL (0x18, 2 squares): 9-entry dict `[0,1,2,1,4,5,2,5,8]`, 6 unique.
11. CORE (2×2 block, full D8): 81-entry dict, 21 unique principals.
12. DIAG3 (3-square corner diagonal, `[ro000, fa1h8]`): 27-entry dict,
    18 unique.
13. ELLE (no symmetry): identity dict `range(81)`.

**E. Group theory**
14. D8 closure on `ar`: for all (j, k), `TRS[k] ∘ TRS[j](ar)` is one of the
    8 images.
15. `trm = [0,1,2,3,4,6,7,5]` is a permutation of 0..7 — a valid relabel
    between the paper order (e, r, r2, r3, sv, sh, d1, d2) and the
    canonical D8 slot order (D-014).

**F. Large set (13 patterns)**
16. Mask-sorted order of the 13 patterns matches the test's
    `expected_large_set_pattern_order`.
17. Per-pattern `n_instances` (first principles), J = 49, and all 13
    attribution tuples (i, I, r0, r1) match the goldens.

**G. Hand derivations**
18. **`symmetry_fs` semantics** (pattern.py L419–441): the set of stabilizer
    elements that induce **distinct non-identity** permutations on the
    compact pattern squares, first representative per permutation in D8 slot
    order. Hand check on DIAG8: stabilizer = {ro000, ro180, fh1a8, fa1h8};
    ro180 and fh1a8 induce the *same* permutation on the 8 diagonal
    squares, fa1h8 induces the identity *on the set* → `symmetry_fs =
    [ro180]` ✓ (test L682). Notably this is **not** "stabilizer minus
    identity" (which would give 3 elements) — the dedup-on-induced-
    permutation is what makes the table's DIAG8 entry correct.
19. One-record width 13 = Σ n_instances over the 3-pattern set (4 + 8 + 1).
20. SNAKE mask `0x0000000C30000000` = bits {28, 29, 34, 35} = {E4, F4, C5,
    D5} (checked via `bitboard_to_string_list`) — matches the set-print
    golden cells; the S-tetromino's ro180 self-symmetry is consistent with
    its `symmetry_fs = [ro180]` entry and `n_stabilizers = 2`.

**Result: zero value mismatches across all 21 checks.**

## 5. Defects in the test file itself

Numbered for the fix campaign (T = test-file defect; none is a value
mismatch):

- **T1. Tautological assertions** (L104, L107): `assertEqual(p, p)` asserts
  nothing; `test_init` effectively only constructs. (Minor.)
- **T2. Dead `if False:` debug block** (L1417–1432) in `test_one_record`:
  references `position_print`, which is **not imported** → NameError
  landmine if re-enabled.
- **T3. Dead module-level fixtures** (L73–79): `ar_reflection_h/v/h1a8/a1h8`,
  `ar_rotate_180/90c/90a` — never referenced (only `ar` is used).
- **T4. Stale test names ×5**: "raises_assertion" for tests that assert
  `ValidationError`, not `AssertionError` (L109, L113, L1071, L1078,
  L1085) — stale since the D-023 strict constructor.
- **T5. Header nits** (L30, L34): "How to use the unit tests pattern
  module." (grammar); "environmeant" (typo).
- **T6. `TestCase` shadowing** (L665): `TestCase = namedtuple('TestCase',
  …)` inside `TestPatternSymmetries` shadows `unittest.TestCase` in that
  class body — cosmetic, but confusing for future edits.
- **T7. Weak empty-list CSV test** (L968–974): only
  `write.call_count == 1`; does not assert the header line's content.
- **T8. Minor-sweep code with zero coverage**: `Pattern.__repr__` (#16),
  empty-`PatternSet` `ValueError` (#17), empty-mask `ValueError` (#18) —
  three shipped code paths, no tests. (This is the suite's biggest gap;
  see §7.3.)
- **T9. Uniform-array tests only**: all `np.full` — no multi-position
  row-independence test for `compute_indexes_on_position` nor
  `compute_principal_indexes` (the pack/unpack path *is* row-diverse via
  the tiled 1 M PERF, but the public indexing pipeline is not).
- **T10. EDGE 6561-config principal dict never pinned directly** (only
  through the set-pipeline goldens).
- **T11. `PatternSet.hash` never golden-pinned**: `print_summary`/`print`
  expectations build the hash line from the computed `self.pattern_set.hash`
  → self-referential; only formatting is checked.
- **T12. `PatternType` has no direct test** (`from_fingerprint`, `.data`) —
  exercised only indirectly through the fingerprint/type columns of the
  mdp/print goldens.
- **T13. `mdp_record` goldens cover 2 of 29 patterns** (ELLE, EDGE); no
  SNAKE/CORE/DIAG8 record goldens.
- **T14. Inconsistent precondition usage**: `position_check_collisions`
  called in `TestPatternComputeIndexes` (L986/L1004/L1025) but not in
  `TestPatternSetComputePrincipalIndexes` (same position).
- **T15. Misleading mock records** (L903, L906): the mocked
  `mdp_record` strings don't follow the real format ("0xff" vs
  "00000000000000FF"; "CORNER,0x0f,4,81,1,1" vs real 9/19683/4/2) —
  harmless as mocks, but they misinform.
- **T16. Cosmetic**: `TestPatternPack.tearDown` is a no-op `pass`.
- **T17. Fixture names swapped vs values** (L84-85, found during D-029):
  `sqa8 = 0x80` is actually H1 (bit 7, row 1) and `sqh1 =
  0x0100000000000000` is actually A8 (bit 56, column a). Only use is
  the identity-agnostic Cayley-table input, so nothing is wrong
  numerically — the names mislead.
- **T19. Missing import inside dead code** (found during T2): the
  `if False:` debug block in `test_one_record` referenced
  `position_print`, which was never imported — a NameError landmine
  if re-enabled. Fixed as part of T2 (print-on-failure + import).

## 6. Docstring/behaviour mismatches (cross-check findings)

- **M1 (known, deferred — not re-raising)**: `PatternSet` docstring Raises
  block (pattern.py L1002–1007) still lists `TypeError` for non-str name /
  non-Pattern elements; the D-023 strict constructor raises
  `ValidationError`. The empty-list `ValueError` line (#17) is present and
  correct. Flagged in the pattern.md campaign; Roberto deferred it.
- **M2. `mdp_csv_file` docstring**: accurate — 3 `TypeError`s, all tested
  with exact-message `assertEqual`.
- **M3. pattern.md says "11-entry" type table; `PatternType` has 12
  members** (TYPE_0…TYPE_9 + TYPE_3D DOTA1 + TYPE_7D DIAG8) — minor doc
  inconsistency in pattern.md (doc-side, not test-side).
- **M4. Header run command** (L40) is valid (package `__init__.py` exists).
- **M5. Column counts consistent**: `mdp_record` goldens (24 columns) ==
  `mdp_csv_file` header constant (L950–956).
- **Naming cross-check**: no transposition issues in this file's goldens —
  spot-checked SNAKE (fact 20); the bit↔name mapping is the campaign-
  verified board convention (D-013), not re-litigated here.

## 7. Completeness analysis

### 7.1 What is well covered
- Constructor strictness: `ValidationError` ×2, >18-squares `ValueError`,
  non-principal `ValueError`, and the **R1 regression** (D-020 corner case)
  are all pinned.
- Packing: 6 pack-plan goldens + scalar + vectorized pack/unpack round-
  trips on 18 structural bitboards + 1 M PERF.
- Symmetries: 29 named patterns with expected `symmetry_fs` (including the
  FOURC all-7 case and the rotation-only COREA/WHIRL cases).
- Group structure: Cayley table verified on `ar`, 14 structural bitboards,
  and all 29 sample masks.
- Output layer: `print` (EDGE), `mdp_record` (ELLE, EDGE), `mdp_csv_file`
  (types + content + empty), set `print`/`print_summary`.
- Indexing pipeline: scalar/array/1 M for both public functions; principal
  dicts for 5 patterns (incl. two full 81/27-entry dicts); set-level
  pipeline (one-record + 13-pattern large set with full attribution).

### 7.2 Status of known issues
- M1 (stale `PatternSet` Raises) — known, deferred (see §6).
- All golden values re-derived independently — **no mismatches found**
  (§4, 21/21).
- R1 (D-020) pinned by a dedicated regression test.
- `symmetry_fs` semantics decoded and hand-verified (fact 18) — the test
  table is internally consistent with the implementation; no test defect.

### 7.3 Systematic gaps
1. **New minor-sweep code untested** (T8): `__repr__`, empty-set
   `ValueError`, empty-mask `ValueError` — shipped paths with zero
   coverage.
2. **Array row-independence** (T9): uniform `np.full` arrays only for both
   public indexing functions; a row-mixing bug in the numba kernels would
   pass silently.
3. **EDGE 6561-entry dict** (T10) not pinned directly.
4. **`PatternSet.hash`** (T11) not golden-pinned (self-referential).
5. **`PatternType`** (T12) no direct tests.
6. **`mdp_record` breadth** (T13): 2 of 29 patterns.

### 7.4 Verdict
A **strong** suite for the pattern core (packing, symmetry, principal-index
pipeline) with unusually rich goldens, and a clean verification record
(21/21 independent re-derivations, zero mismatches). The gaps concentrate
in (i) the strict-constructor edge paths added by the minor sweep — shipped
but untested — and (ii) the array dimension of the public indexing API
(row independence). The test file's own hygiene issues (T1–T7, T15–T16)
are minor; the stale "raises_assertion" names (T4) are the only ones that
would actively mislead a future reader.

### 7.5 Fix priorities (campaign progress)
_Per-item approval, one at a time, per the D-019 pattern. Status
2026-08-28:_

- **P0** (shipped code with zero coverage — T8) — **DONE**
  (D-026/027/028, commit 6da0803):
  1. Test `Pattern.__repr__` (golden, e.g. ELLE/EDGE). [D-026]
  2. Test empty `PatternSet` → `ValueError` (message). [D-027]
  3. Test empty mask (0x0) → `ValueError` (message). [D-028]
- **P1** (coverage of existing behaviour) — **DONE**
  (D-029/030/031, commit 086ef75):
  4. Multi-position array tests (≥2 distinct positions, assert row
     independence) for `compute_indexes_on_position` and
     `compute_principal_indexes` (T9). [D-029, D-030]
  5. Direct EDGE 6561-entry principal-dict test (length, unique count
     3321, spot values) (T10). [D-031]
- **P2** (hygiene + breadth):
  6. Hygiene — **DONE** (D-033, batch commit after P1): T1 tautologies
     → real assertions; T2 dead `if False:` block → print-on-failure
     (Roberto's proposal; exposed **T19** — `position_print` was never
     imported — fixed in the same item); T3 dead `ar_*` fixtures
     removed (`ar` kept); T4 the 5 "raises_assertion" tests renamed
     to "raises_validation_error"; T5 header typo/grammar fixed; T6
     `TestCase` namedtuple renamed to `SymmetryCase`; T7 CSV header
     content asserted in the empty-list test; T15 mock records
     replaced with the real EDGE/CORNER `mdp_record()` output; T16
     no-op `tearDown` removed. T17 (sqa8/sqh1 fixture values
     corrected) is done in the breadth batch below (D-034).
     T18 (np.uint8 `3**n_squares` overflow) stays noted-only, no
     code action.
  7. Add `position_check_collisions` to the set-level indexing tests
     (T14) — **DONE** (D-034): collision precondition now asserted
     at both levels.
  8. Direct `PatternType.from_fingerprint` tests (T12) — **DONE**
     (D-034): 12-member closed-set + roundtrip, unknown fingerprint
     → None, `.data` keys + orbit-stabilizer identity (all 12),
     full-data pins for TYPE_2/TYPE_9/TYPE_3D. Also fixed the doc's
     "11 members" miscounts (actually 12).
  9. Add `mdp_record` goldens for SNAKE/CORE/DIAG8 (T13) — **DONE**
     (D-034): three golden strings mirroring the EDGE one.
  10. Golden-pin `PatternSet.hash` (T11) — **DONE** (D-034): expected
     hash `5e5abf79…9d10b` computed from the actual masks, no
     self-comparison.
  11. Fix the stale `PatternSet` Raises docstring (M1 — deferred item,
      needs Roberto's go-ahead).

---

## Appendix — class map

```
L1–41      module docstring (run command; L30/L34 nits — T5)
L43–64     imports (star import from twolm.pattern; board functions)
L66–79     fixtures: ar + 7 dead ar_* (T3)
L100–187   TestPattern                        7 tests
L189–652   TestPatternPack                    7 tests (helper + 18-board setUp)
L655–710   TestPatternSymmetries              1 test (29 subTests; T6)
L712–755   TestPatternMdpRecord               2 tests
L757–866   TestTransformationsCayleyTable     4 tests
L868–895   TestPatternPrint                   1 test
L897–974   TestPatternMdpCsvFile              5 tests (T7, T15)
L976–1042  TestPatternComputeIndexes          3 tests (T9, T14)
L1044–1198 TestPatternSet                     10 tests (T4 ×3, T11)
L1200–1231 TestPatternPrincipalIndex          1 test
L1233–1328 TestPatternComputePrincipalIndexDict  6 tests
L1330–1488 TestPatternSetComputePrincipalIndexes 3 tests (T2 dead block, T9)
```
