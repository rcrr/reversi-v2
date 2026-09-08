# reversi/test/test_feature.py
The unit suite of the first pipeline-integration module (the
`feature.py` mirror): the `Feature` factory methods + the blocked
direct construction, `FeatureSet` construction (ordering,
n_instances, hash, the intercept category check, print_summary)
and `FeatureSet.compute_indexes` (the 3×10 golden, the N=0/I=0
edges, strict typing, the 1M-position PERF). 4 classes / 20 tests
(19 run + 1 PERF skip) / no DB.
> State: D-050 · a5db33b · 2026-08-29 · suite 19/0/1

## Coverage

| class | tests | what it pins |
|---|---|---|
| `TestFeature` | 8 | `test_init_raises_runtime_error` (direct `Feature(...)` → RuntimeError); the 3 factories (all 5 fields asserted each, ref equality via dataclass `__eq__`); `test_new_from_pattern_invalid_type` (str arg → pydantic ValidationError); the `__repr__` golden (no `ref`); the field-wise `__eq__`; the unhashable instance |
| `TestFeatureSet` | 6 | `test_init` (name, the 3 object refs, `n_instances` 53, the 17-value per-feature list, the name-order golden, the pinned hash); the partial-None trio (`test_init_intercept_only` / `_mobility_only` / `_pattern_only`); `test_print_summary` (the full output golden, 3 pinned hashes); `test_init_invalid_intercept_category_raises_value_error` (a MOBILITY-category feature as intercept → ValueError) |
| `TestFeatureSetComputeIndexes` | 5 | `test_compute_indexes` (the 3×10 literal golden via assertArrayEqual); the empty edges (empty positions (0,10), empty features (3,0), both (0,0) + dtype); `test_compute_indexes_wrong_argument_type` (None / list / str / int64 ndarray → ValidationError, subTest loop) |
| `TestFeatureSetComputeIndexesPerf` | 1 | `test_performance_1m` (PERF=1: 1M positions, 51 instances, warmup, throughput print, N/I asserts only) |

## Goldens pinned

- The feature-level hash `f5663932…b74167` (pinned in two tests:
  test_init + test_print_summary) on top of the child modules'
  pinned constants — the mset `2e553593…08a94` (the same literal
  test_mobility pins) and the pset `ff97ce55…040ea`.
- The 3×10 index matrix (the EDGE 0x00000000000000FF + DIAG4
  0x0000000001020408 set + LMC + intercept, 3 real positions) —
  every cell a literal.
- The per-feature `n_instances` list (17 values, 13 patterns +
  3 mobilities + intercept, the feature ORDER pinned implicitly)
  and the name-order golden (the insertion order deliberately
  differs from the child sets' sorted storage order — the
  ordering contract exercised for free).
- The 51-instance figure of the PERF build.

## Conventions

- How to run (header): from the workspace root,
  `time PERF=0 python3 -m unittest reversi.test.test_feature` —
  `PERF=1` enables the 1M-position test (print-only, no gate —
  consistent with the whole repo).
- Strict-typing tests assert `pydantic.ValidationError` (1 in
  TestFeature, 4 wrong argument types in the subTest loop).
- No hash self-comparisons: the literals are real goldens,
  independently re-derived from the public API (the W
  re-derivations are frozen in the archived review).

## Integration

- In-memory only: no DB, no files, no pipeline — the child sets
  are built in setUp from literal mask data.
- The sibling of the other three base-module suites
  (test_board / test_mobility / test_pattern) — the same idiom
  family, the shared pinned constants.
