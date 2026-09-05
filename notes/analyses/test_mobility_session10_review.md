<!-- ARCHIVED — D-106 step 24 (the docs/ rewrite, 2026-09-04): the MOBILITY family (the module doc + this test doc) moved out of docs/src/twolm/test/ into the snapshot schema per docs_rules.md §1/§4. This is a frozen historical record: it is never updated. Stale-in-current-context notes: (1) the class-map appendix is the PRE-D-037 426-line state — the current file is 453 lines (T1 dead block removed + real assertions, T2 the 3 renames to *_raises_validation_error, T8 +2 __repr__ goldens, T7 +1 multi-position test, T6 dead imports removed); the post-campaign class lines are in the new doc. (2) the "23/0/1" baseline predates the campaign (current: 26/0/1). (3) the T1-T9 campaign narrative (D-037) is frozen history. -->

# test_mobility.py — test-suite analysis for `twolm.mobility`

_Analyzed 2026-08-28 (session 10). File: 426 lines at analysis, added
2026-08-28 (commit 62748ca), then touched by the R5 batch (property
call-sites, commit 304cb2a) and the T1-T9 campaign (D-037). Suite
baseline at analysis: 23/0/1 GREEN; final state after the campaign:
26/0/1 GREEN (T8 +2 repr tests, T7 +1 multi-position test). 2
classes, 1 PERF test._

## 1. What this file is

The unit suite for the mobility feature module (see
`docs/src/twolm/mobility.md`): construction and strict typing of
`Mobility`, the duplicate-key/sorting/hash contract of `MobilitySet`,
the `compute_indexes` Numba pipeline (golden, underflow boundary,
empty inputs, 1M-position PERF), and the standalone `popcount64`
helper (31-line golden table + vectorized check). The suite is a
faithful sibling of test_pattern.py — same conventions, same idiom
choices (and, as section 5 shows, the same known idiom warts:
dead `if False:` block, "raises_assertion" names, hash
self-comparisons).

## 2. Suite conventions

- **How to run** (header L29-39): from the workspace root,
  `time PERF=0 python3 -m unittest twolm.test.test_mobility`;
  `PERF=1` enables the 1M-position performance test (print-only,
  no gate — consistent with the whole repo, see mobility.md M4).
- **Strict-typing tests** assert `pydantic.ValidationError` for
  non-conforming arguments (3 in TestMobility, 2 in TestMobilitySet).
- **Goldens** are literal strings / arrays / hashes where present —
  except the two hash self-comparisons (T3, T4 below).
- **Shared fixture** (`setUp`, L117-124): the standard triple
  LMC/ALMC/DLMC (all-64 / zero masks) + the `mlf` builder lambda.
- `popcount64` is imported by name (L62-63) — unaffected by the R3
  removal from `__all__` (D-035).

## 3. Coverage by area

| area | tests | notes |
|------|-------|-------|
| Mobility construction | test_init (L69) | real assertions (name/mask/amask/n_configurations), 3 cases LMC/ALMC/DLMC |
| Mobility strict typing | 3 tests (L88-98) | arg 1/2/3 wrong type → ValidationError |
| Mobility.print | test_print (L100) | exact golden string (incl. `:8s` name padding) |
| Mobility.n_configurations | test_n_configurations_calculation (L108) | k=2, a=3 → 6 (the "+1 zero-state" documented) |
| Set construction + collisions | test_init (L126), dup name (L136), dup key (L146) | dup checks assert the messages; test_init itself is a dead block (T1) |
| Set hash | hash equivalence (L156), hash calculation (L174) | order-insensitivity tested; formula check is a self-comparison (T3) |
| Set sorting | test_mobility_sorting_order (L188) | explicit 3-name ordering by (mask, amask) |
| Set strict typing | invalid list element (L207), invalid name (L217) | ValidationError both |
| Set accessors | test_names (L225), test_masks (L232) | golden list + (3,2) uint64 array; R5 property form |
| Set.print_summary | test_print_summary (L241) | full golden lines; hash part self-computed (T4) |
| compute_indexes | golden (L260), PERF (L275), underflow (L365), empty positions (L414) | single-position golden [53,13,66]; no multi-position test (T7) |
| popcount64 | test_popcount64 (L294) | 31-line scalar golden table + shape/dtype/array vectorized check |
| empty set | test_init_empty_list (L397) | name/length/names/masks (0,2)/sha3_256(b'') hash |

**Not covered at all:** `Mobility.__repr__` / `MobilitySet.__repr__`
(shipped by R5/D-035, zero tests — T8); multi-position row
independence of `compute_indexes` (T7).

## 4. Verified facts (independently re-derived — no value mismatches)

Ground truth: pure-Python `int.bit_count()` + the verified module
behaviour (mobility.md V1–V8). Live session 10, all match:

| # | fact | result |
|---|------|--------|
| V1 | `test_print` golden string (exact, incl. `LMC` + 5-space padding) | matches live output |
| V2 | `test_names` golden `['ALMC', 'LMC', 'DLMC']` | matches sorted storage |
| V3 | `test_masks` golden (3,2) array | matches |
| V4 | `print_summary` 4 golden lines; standard-set hash `2e5535935d46d82a941ef87d43d22562735db9b6bf41db51d6eb6a8f21208a94` | all match |
| V5 | sorting-order expectation (LowMaskLowAmask, LowMaskHighAmask, HighMask) | matches |
| V6 | duplicate messages ('duplicate names', 'duplicate (mask, amask) pairs') | both match |
| V7 | `n_configurations` 2+3+1 = 6 | matches |
| V8 | `compute_indexes` golden `[53, 13, 66]`: golden position (mover `0x40001ccaeb400024`, 17 stones; opponent `0x92fc6234143c7848`, 27 stones) has lms = `0x2c03810000820690` (13), alms = `0x2002810100838012` (11); columns are the set's SORTED order ALMC = 64−11 = 53, LMC = 13, DLMC = 13+53 = 66 | matches (cross-ref mobility.md V5) |
| V9 | underflow test position: mask = amask = 0xF, mover 0x10 (E1), opponent 0xE0 (F1,G1,H1) → lms = 0, alms = 0x8 (D1) → 0 + (4−1) = 3 | matches; comment's board story verified |
| V10 | popcount64 31-line table (lines 0-30, incl. 0xFF…, 0x1484211821822141 → 16) | 31/31 == `int.bit_count()` |
| V11 | empty set: hash = `sha3_256(b'')`, `names == []`, `masks().shape == (0, 2)` | matches |
| V12 | empty positions: output shape `(0, 3)`, dtype uint32 | matches |
| V13 | NEW (untested) `__repr__` goldens: `Mobility(name='LMC', mask=0xffffffffffffffff, amask=0x0000000000000000)`; `MobilitySet(name='Test', length=3, hash=2e5535935d46d82a941ef87d43d22562735db9b6bf41db51d6eb6a8f21208a94)` | captured live, ready for T8 |

## 5. Defects in the test file itself

_Numbering is local to this file (fresh T series; the pattern suite
has its own, already closed)._

- **T1 — `TestMobilitySet.test_init` (L126-134): dead `if False:`
  block, zero live assertions.** The test builds the set and then
  contains only a 6-line unreachable debug print. As it stands it
  verifies nothing but "construction does not raise" (which the
  other 15 set tests already do). Pattern-suite precedent: T1+T2
  (D-033). Fix: remove the dead block; add real assertions (name,
  `len(mobilities)`, `names == ['ALMC', 'LMC', 'DLMC']`).
- **T2 — three stale "raises_assertion" names (L88, L92, L96).**
  `test_init_invalid_type_arg_{1,2,3}_raises_assertion` — the
  constructor raises `ValidationError`, not AssertionError (strict
  `@validate_call`). Pattern-suite precedent: T4 rename
  (D-033). Fix: rename to `..._raises_validation_error`.
- **T3 — `test_hash_calculation_verification` (L174-186): hash
  self-comparison.** The "expected" hash is recomputed with the
  very formula under test (sorted keys + `tobytes()` + sha3_256) —
  a wrong-but-self-consistent implementation would pass. No pinned
  golden. Pattern-suite precedent: T11 (D-034). Fix: pin the literal
  `2e5535935d46d82a941ef87d43d22562735db9b6bf41db51d6eb6a8f21208a94`
  (independently verified twice — this session and mobility.md V6).
- **T4 — `test_print_summary` (L244): `expected_hash = ms.hash`.**
  The hash part of the expected output is taken from the object
  under test (self-comparison); the rest of the golden is real.
  Fix: pin the same literal in the format string.
- **T5 — header grammar (L29).** "How to use the unit tests mobility
  module." Pattern-suite precedent: T5 (D-033) fixed the same wart
  to "How to run the pattern module unit tests." Fix: "How to run
  the mobility module unit tests."
- **T6 — dead imports (L45-47, L60): `shutil`, `tempfile`,
  `legal_moves`.** Each occurs exactly once (the import line) —
  verified. Pattern-suite precedent: T3 (D-033). Fix: remove.
- **T7 — no multi-position row-independence test for
  `compute_indexes`.** The only functional test (L260) uses exactly
  one position (`np.full(1, ...)`); the kernel's N-row loop
  (row-independence of output rows) is untested. Pattern-suite
  precedent: T9 (D-029/D-030). Fix: ≥2 distinct positions with
  per-row expected values (pure-Python ground truth).
- **T8 — `__repr__` shipped (R5/D-035) with zero coverage.** Both
  new `__repr__` methods are untested — "shipped code with zero
  coverage", the pattern-suite P0 category (T8/D-026, where the
  `__repr__` golden test was the P0 item). Fix: golden tests with
  the live-captured strings (V13 above).
- **T9 — (cosmetic) `test_popcount64` print-on-failure idiom
  (L334-341).** On mismatch it prints and then
  `assertTrue(False)`; a native `assertEqual` would report the
  offending line directly. The idiom is accepted in this workspace
  (pattern T2 fix adopted print-on-failure), so: noted, optional.

## 6. Docstring/behaviour mismatches (cross-check findings)

- The `test_popcount64` table comment "line 30" marks the last of
  **31** lines (0-30); the file's own header says nothing about
  the count — no mismatch, just precision for future readers.
- `test_init` (set) docstring absence vs. the real dead block — the
  test name promises "init works" and delivers a no-op (T1).
- No mismatch between the R5 property form and the tests: all four
  call-sites updated in 304cb2a; suite GREEN.
- `test_n_configurations_calculation` comment ("0 moves, 1 move,
  2 moves + 0 anti, 1 anti, 2 anti, 3 anti = 6 total states") is
  muddled (it enumerates 7 states but claims 6) — the value is
  correct (V7); the comment is the wart. Noted, cosmetic.

## 7. Completeness analysis

### 7.1 What is well covered

Construction + strict typing (5 tests), both collision checks with
message asserts, sorting order, hash order-insensitivity, real print
goldens (Mobility, print_summary structure), the underflow boundary
of the Numba kernel, empty-set and empty-positions edges, and a
solid 31-line popcount table with a vectorized shape/dtype check.
The core golden `[53, 13, 66]` is a genuine independent-value
golden (re-derived V8), not a self-comparison.

### 7.2 Status of known issues

All module-side issues are resolved (R1-R6, D-035; M1-M5, D-036).
The only module behaviour the suite does not pin is the
`__repr__` pair (T8).

### 7.3 Systematic gaps

1. **Row independence** of `compute_indexes` (T7) — the kernel is a
   (N) → (N, L) map; a single-row test cannot catch cross-row
   contamination (e.g. an accidental write to the wrong row).
2. **Shipped-but-untested `__repr__`** (T8) — new surface from the
   R5 batch, zero coverage.
3. **Two hash self-comparisons** (T3, T4) — the one structural
   constant (standard-set hash `2e553593…208a94`) is not pinned
   anywhere as a literal.

### 7.4 Verdict

A **good** suite for a small module: 23/0/1 GREEN, honest goldens
in the functionally important places, and a deliberately pinned
empty-behaviour contract (empty set, empty positions). The gaps are
the familiar pattern-suite warts (dead block, stale names, hash
self-comparisons, single-row array test) plus one fresh
shipped-untested surface (`__repr__`) — none of them indicates a
module defect; every golden re-derived in this session matched.

### 7.5 Fix priorities (campaign progress)

_Per-item approval, one at a time (D-019 pattern). Status
2026-08-28: **campaign complete — T1-T9 all approved and applied
(D-037, batch commit); suite 23 → 26 tests, GREEN 26/0/1.**_

- **P0** (shipped code with zero coverage — T8) — **DONE** (D-037):
  1. Golden tests for `Mobility.__repr__` and
     `MobilitySet.__repr__` (V13 strings; set golden also pins the
     standard-set hash literal). [D-037]
- **P1** (coverage of existing behaviour) — **DONE** (D-037):
  2. Multi-position `compute_indexes` row-independence test: 2
     distinct positions (golden + underflow), per-row expected
     values [[53,13,66],[63,0,63]] (T7). [D-037]
- **P2** (hygiene + breadth) — **DONE** (D-037):
  3. T1: `TestMobilitySet.test_init` — dead `if False:` block
     removed, real assertions added (name, length, names).
  4. T2: the 3 "raises_assertion" tests renamed to
     "raises_validation_error".
  5. T3+T4: standard-set hash literal
     `2e5535935d46d82a941ef87d43d22562735db9b6bf41db51d6eb6a8f21208a94`
     pinned in `test_hash_calculation_verification` (double assert:
     formula and object) and `test_print_summary`.
  6. T5: header grammar → "How to run the mobility module unit
     tests."
  7. T6: dead imports `shutil`, `tempfile`, `legal_moves` removed
     (the `import time` trailing space was noted, left as-is).
  8. T9 (Roberto approved): native `assertEqual` with the line
     number in the message, replacing the print-on-failure idiom in
     `test_popcount64`.

---

## Appendix — class map

```
TestMobility (L67)                          6 tests
├── test_init (L69)
├── test_init_invalid_type_arg_1_raises_assertion (L88)   [T2]
├── test_init_invalid_type_arg_2_raises_assertion (L92)   [T2]
├── test_init_invalid_type_arg_3_raises_assertion (L96)   [T2]
├── test_print (L100)
└── test_n_configurations_calculation (L108)

TestMobilitySet (L115)                     17 tests
├── setUp (L117): standard LMC/ALMC/DLMC triple + mlf lambda
├── test_init (L126)                                          [T1]
├── test_duplicate_name_collision (L136)
├── test_duplicate_key_collision (L146)
├── test_hash_equivalence_same_keys (L156)
├── test_hash_calculation_verification (L174)                 [T3]
├── test_mobility_sorting_order (L188)
├── test_invalid_mobility_type_in_list (L207)
├── test_invalid_name_argument_type (L217)
├── test_names (L225)
├── test_masks (L232)
├── test_print_summary (L241)                                 [T4]
├── test_compute_indexes (L260)                               [T7 gap]
├── test_compute_indexes_performance_1m (L275)   PERF, print-only
├── test_popcount64 (L294)                                   [T9]
├── test_compute_indexes_prevents_underflow (L365)
├── test_init_empty_list (L397)
└── test_compute_indexes_empty_positions (L414)
```
