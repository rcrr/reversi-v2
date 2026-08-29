# test_feature.py — test-suite analysis for `twolm.feature`

_Analyzed 2026-08-28 (session 8). File: 362 lines at analysis, added
2026-08-28 (commit b51bea6), analyzed after the R1-R4 module batch
(D-038, commit b91fef2). Suite baseline: 14 tests — 13 run + 1 PERF
skip, 0 failures, GREEN. 4 classes, 1 PERF test. Campaign in
progress one at a time: T6 (D-043), T1 (D-044), T2 (D-045),
T3 (D-046) and T5 (D-047) applied → 16 run + 1 PERF skip,
GREEN 16/0/1; T4, T7-T9 pending._

## 1. What this file is

The unit suite for the first pipeline-integration module (see
`docs/src/twolm/feature.md`): the `Feature` factory methods and the
blocked direct construction, `FeatureSet` construction (ordering,
n_instances, hash, intercept category check, print_summary), and
`FeatureSet.compute_indexes` (3×10 golden, N=0/I=0/both edges,
strict typing, 1M-position PERF). The goldens lean on the child
modules' pinned constants (mset `2e553593…`, pset `ff97ce55…`) and
add the feature-level hash `f5663932…` as a new pinned literal.
Same idiom family as the other three suites — including the known
idiom wart, the dead `if False:` debug block (T1).

## 2. Suite conventions

- **How to run** (header L28-40): from the workspace root,
  `time PERF=0 python3 -m unittest twolm.test.test_feature`;
  `PERF=1` enables the 1M-position performance test (print-only,
  no gate — consistent with the whole repo, see mobility.md M4).
- **Strict-typing tests** assert `pydantic.ValidationError`:
  1 in TestFeature (factory arg type), 1 in
  TestFeatureSetComputeIndexes (4 wrong argument types in a
  subTest loop).
- **Goldens**: feature hash literal pinned in two tests (test_init,
  test_print_summary); per-feature n_instances list; 3×10 index
  matrix; 8 `assertIn` lines of print_summary output. No hash
  self-comparisons (unlike the pre-campaign test_mobility) — the
  literals are real goldens (re-derived below).
- **Fixtures**: `TestFeatureSet.setUp` builds the full 13-pattern +
  3-mobility set in INSERTION order (R2, R3, R4, XEDGE, …, CORE);
  `TestFeatureSetComputeIndexes.setUp` a reduced EDGE + DIAG4 set
  with 3 real positions. The insertion order is deliberately
  different from the child sets' sorted storage order, so the
  ordering contract is exercised for free.

## 3. Coverage by area

| area | tests | notes |
|------|-------|-------|
| Feature direct construction | test_init_raises_runtime_error (L68) | `Feature(Category, …)` → RuntimeError |
| Feature factories | new_intercept (L72), new_from_mobility (L81), new_from_pattern (L92) | all 5 fields asserted each; ref equality via dataclass __eq__ |
| Feature factory typing | new_from_pattern_invalid_type (L103) | str arg → ValidationError; no symmetric test for new_from_mobility |
| FeatureSet construction | test_init (L137) | name, 3 object refs, n_instances 53, 17-value per-feature n_instances list (pins feature ORDER implicitly), pinned hash |
| FeatureSet print_summary | test_print_summary (L155) | 8 assertIn lines, 3 pinned hashes (feature + mset + pset); no full golden (T9) |
| FeatureSet intercept check | test_init_invalid_intercept_category (L173) | MOBILITY-category feature as intercept → ValueError "wrong category" |
| compute_indexes golden | test_compute_indexes (L219) | 3×10 matrix, assertArrayEqual vs literal; dead if-False block (T1) |
| compute_indexes edges | empty_positions (L249), empty_features (L260), both_empty (L272) | shapes (0,10), (3,0), (0,0) + dtype |
| compute_indexes typing | wrong_argument_type (L282) | None / list / str / int64 ndarray → ValidationError (subTest) |
| PERF | test_performance_1m (L299) | 1M positions, 51 instances, warmup, throughput print, N/I asserts only |

**Not covered at all:** partial-None FeatureSet constructions
(intercept-only / mset-only / pset-only: the hash chunk branches and
the single-block hstack path) (T6); `Feature.__repr__`/`__eq__`
(dataclass auto-surface) (T7); explicit names-order assertion in
test_init (T5 — currently implicit via the n_instances list).

## 4. Verified facts (independently re-derived — no value mismatches)

Ground truth: `scratch/verify_feature.py` (this session; no
`twolm.feature` import in the math — pure-Python legal moves,
orbit-min reduction, from-scratch sha3_256; `twolm.board` only for
the D8 transforms/`legal_moves`). All match:

| # | fact | result |
|---|------|--------|
| W1 | test_init hash literal `f5663932…b74167` | == from-scratch sha3_256(b'INTERCEPT' + mset hex + pset hex) |
| W2 | 17-value per-feature n_instances list `[1,1,1,1,8,4,4,4,4,4,4,4,1,2,4,4,2]` | == pure-Python orbit sizes in mask-sorted order (2X5COR 8, XEDGE/R2/CORNER/R3/DIAG4/R4/DIAG5/DIAG6/DIAG7 4, CORE 1, RCT2X4 2, DIAG8 2); sum 53 |
| W3 | 3×10 golden matrix (L209-213) | == pure-Python re-derivation, all 3 rows (col0 intercept 0, col1 LMC, cols 2-5 EDGE, cols 6-9 DIAG4 principal orbit-min columns) |
| W4 | the 3 pinned hashes in test_print_summary (f566…, 2e55…, ff97…) | all == from-scratch |
| W5 | edge shapes (0,10) / (3,0) / (0,0), dtype uint32 | == live |
| W6 | 4 wrong argument types → ValidationError | all four verified |
| W7 | factory field values (intercept 1/1/None; LMC 65/1; EDGE 3^8/4) | all == live |
| W8 | PERF `expected_index_instances = 51` | == 1 (intercept) + 1 (LMC) + 49 (the same 13 patterns) |
| W9 | suite baseline | 13/0/1 GREEN |

## 5. Defects in the test file itself

_Numbering is local to this file (fresh T series; the pattern and
mobility suites have their own, closed)._

- **T1 — `TestFeatureSetComputeIndexes.test_compute_indexes`
  (L230-245): dead `if False:` block, 16 unreachable lines. DONE
  (D-044).**
  References `position_print` (L238) — never imported (the board
  import at L45-46 is `Bitboard, make_position` only) — a latent
  NameError if the block is ever re-activated; plus the undefined
  name `indexes`. The live assertion (L247) is real. Precedents:
  test_pattern T1 (D-033),
  test_mobility T1 (D-037). Fix applied: dead block removed,
  golden assertion unchanged.
- **T2 — dead imports (L52, L53, L59, L61): `npt`, `nptest`,
  `Callable`, `TypeAlias`, `List`, bare `pydantic`. DONE
  (D-045).** Each occurs exactly once (the import line) —
  grep-verified. Precedent: test_mobility T6 (D-037). Fix applied:
  all six removed (4 import lines + 1 consequent blank line).
- **T3 — header grammar (L30). DONE (D-046).** "How to use the
  unit tests feature module." Precedent: test_mobility T5
  (D-037) fixed the same wart. Fix applied: "How to run the
  feature module unit tests."
- **T4 — header typo (L34): "Activate the environmeant."** Same
  nit as the test_board.py header (reported there, left to
  Roberto's call). Flagged for a consistent treatment across the
  repo; no separate campaign item unless Roberto wants it.
- **T5 — no explicit names-order assertion in test_init (L137).
  DONE (D-047).** The 17-value n_instances list pins the feature
  order implicitly (the 8/1/2 values sit in the sorted-order
  slots), but the column/feature order contract (feature.md
  R2/D-038) has no direct name-list assertion. Fix applied:
  explicit `expected_names` list (17 names: INTERCEPT + mobilities
  in sorted (mask, amask) order + patterns in sorted mask order)
  asserted against `[f.name for f in feature_set.features]`, in
  the same computed/expected style as the n_instances block.
- **T6 — partial-None FeatureSet untested. DONE (D-043).** Only
  the all-None set was constructed (in the edge tests). Untested
  code: the hash chunk branches for intercept-only (hash of
  `b'INTERCEPT'` alone), mset-only, pset-only; and the single-block
  hstack path of compute_indexes (intercept-only → (N,1);
  mset-only → (N,3); pset-only → (N,49) for the 13-pattern
  fixture). The only real code-coverage gap in the module (P1).
  Fix applied: three new tests in TestFeatureSet
  (test_init_intercept_only / test_init_mobility_only /
  test_init_pattern_only) reusing the setUp fixture, each pinning a
  genuine from-scratch hash literal (ab7c1b64…, 239e4df4…,
  63f0a6c8…), the names-order list, n_instances (1 / 3 / 49), the
  output shape, and block equality against the child set's own
  compute method. Suite 13 → 16 run tests.
- **T7 — `Feature.__repr__`/`__eq__` untested.** The dataclass
  auto-`__repr__` (5 fields, `ref` excluded) and field-wise
  `__eq__` (ref included) are never pinned; the suite relies on
  `__eq__` indirectly (the `assertEqual(feature_set.intercept,
  self.intercept)` style) but has no golden for either. Auto-
  generated surface (not R-shipped), so P2 rather than P0.
- **T8 — (cosmetic) `import time` trailing spaces (L56).** Same
  wart as test_mobility's `import time` (noted there, left as-is
  per Roberto). Noted, default leave-as-is.
- **T9 — `test_print_summary` (L155): 8 `assertIn` lines, no full
  golden.** The per-feature table rows (17 lines), the
  intercept-present line, and the two set lines are only spot-
  checked; a full-output golden (or at least the full feature
  table) would pin the `IntEnum`-as-int rendering and the
  `:10s`/`:10,d` formatting end to end. Optional breadth.

## 6. Docstring/behaviour mismatches (cross-check findings)

- No mismatch between the post-R1/R3 docstrings (D-038) and the
  tests: the hash construction and the features-building order the
  docstrings now describe are exactly what the goldens pin (W1,
  W2).
- The `test_new_from_pattern` golden `n_instances = 4` for EDGE and
  `n_configurations = 3**8` are consistent with the Pattern
  campaign's verified values (pattern.md).
- No "raises_assertion"-style stale names (this file was written
  after that pattern was identified).
- `test_compute_indexes` name vs. its dead block: the test is
  fully live (the golden assert is the test); the dead block is an
  artifact, not a promise gap (contrast mobility T1).

## 7. Completeness analysis

### 7.1 What is well covered

Factories (all 3, full field asserts, blocked construction), the
intercept category guard, the 17-value ordering-sensitive
n_instances list, two pinned feature-level hash literals, a genuine
3×10 multi-position golden (re-derived W3), all three empty edges
with dtype checks, strict typing on both the factory and the
compute path, and a standard print-only PERF. The fixture's
insertion-order ≠ sorted-order choice means the ordering contract
is exercised by every golden.

### 7.2 Status of known issues

Module side: R1-R4 applied (D-038); M1-M4 disposition pending.
The suite does not pin `Feature.__repr__` (T7), the partial-None
construction (T6), or an explicit names order (T5).

### 7.3 Systematic gaps

1. **Partial-None construction** (T6) — the `__init__` hash chunk
   branches and the single-block hstack path are untested code;
   every other branch has coverage.
2. **Auto-surface `__repr__`/`__eq__`** (T7) — relied upon, never
   pinned.
3. **Hygiene** (T1-T3, T5, T9) — the familiar idiom warts (dead
   block, dead imports, header grammar) plus one explicit-order
   and one full-golden breadth item.

### 7.4 Verdict

A **good** suite for the pipeline's first integration module:
13/0/1 GREEN, real pinned goldens everywhere it matters (the new
feature-level hash, the ordering-sensitive n_instances list, the
3×10 matrix), and honest edge/typing coverage. The gaps are one
genuine coverage hole (partial-None, T6), one auto-surface pin
(T7), and the standard hygiene set (T1-T3, T5, T9) — none of them
indicates a module defect; every golden re-derived in this session
matched (W1-W8).

### 7.5 Fix priorities (campaign pending)

_Per-item approval (D-019 pattern). Status 2026-08-28: proposed,
awaiting Roberto's approvals._

- **P0** (shipped code with zero coverage): none — the R1-R4 batch
  was doc/hygiene-only, and its behaviour (hash, column order) is
  already pinned by existing goldens.
- **P1** (coverage of existing behaviour):
  1. T6 — partial-None `FeatureSet` tests: intercept-only /
     mset-only / pset-only constructions (hash chunk branches
     pinned against from-scratch values) + single-block
     `compute_indexes` shapes. **DONE (D-043).**
- **P2** (hygiene + breadth):
  2. T1 — dead `if False:` block removed. **DONE (D-044).**
  3. T2 — 6 dead imports removed. **DONE (D-045).**
  4. T3 — header grammar. **DONE (D-046).**
  5. T5 — explicit names-order assertion in test_init. **DONE (D-047).**
  6. T7 — `Feature.__repr__`/`__eq__` golden tests.
  7. T9 — full print_summary golden (or at least the full 17-row
     feature table).
  8. T4 — "environmeant" typo (repo-consistency call, Roberto's).
  9. T8 — `import time` trailing spaces (default leave-as-is, per
     test_mobility precedent).

---

## Appendix — class map

```
TestFeature (L66)                              5 tests
├── test_init_raises_runtime_error (L68)
├── test_new_intercept (L72)
├── test_new_from_mobility (L81)
├── test_new_from_pattern (L92)
└── test_new_from_pattern_invalid_type (L103)

TestFeatureSet (L108)                          3 tests
├── setUp (L110): 13-pattern + 3-mobility fixtures, insertion order
├── test_init (L137)                                        [T5 gap]
├── test_print_summary (L155)                               [T9]
└── test_init_invalid_intercept_category_raises_value_error (L173)

TestFeatureSetComputeIndexes (L184)             5 tests
├── setUp (L186): EDGE + DIAG4 set, LMC, intercept, 3 positions,
│                 10-column golden (verified W3)
├── test_compute_indexes (L219)                           [T1 dead block]
├── test_compute_indexes_empty_positions (L249)
├── test_compute_indexes_empty_features (L260)
├── test_compute_indexes_both_empty (L272)
└── test_compute_indexes_wrong_argument_type (L282)

TestFeatureSetComputeIndexesPerf (L296)          1 test
└── test_performance_1m (L299) PERF, print-only   [W8: 51 instances]
```
