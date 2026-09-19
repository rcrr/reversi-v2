# reversi/feature.py
The first pipeline-integration module: it wraps the three feature sources already in the package — the constant
intercept, `Mobility` (mobility.py) and `Pattern` (pattern.py) — into two classes: `Feature` (one evaluation feature,
factory-only) and `FeatureSet` (a named collection that builds the flat feature list and the `(N, I)` uint32 index
matrix a feature-table evaluation consumes).

## API

| name | contract |
|---|---|
| `Feature` | `@dataclass(init=False)`; `Category` IntEnum (INTERCEPT=0, MOBILITY=1, PATTERN=2); fields `category`, `name`, `n_configurations`, `n_instances`, `ref` (the source object, `repr=False`); direct construction BLOCKED; factories: `new_intercept()`, `new_from_pattern(p)`, `new_from_mobility(m)` |
| `FeatureSet` | `__init__(name, intercept, mset, pset)` (validated); `print_summary(output=sys.stdout)`; `compute_indexes(positions) -> IndexArray` |

## Architecture

- `Feature` construction: `__new__` is `@validate_call` and unconditionally raises `RuntimeError` ("Use the Factory
  Method instead") — `*args/**kwargs: Any` so pydantic passes validation through and the error propagates.
  `_create_empty()` (internal, also validated) calls `object.__new__(cls)` to bypass the block; the three strict
  `@validate_call` (arbitrary_types_allowed) factories assign every field, copying `name`, `n_configurations`,
  `n_instances` from the source object (kept in `ref`). Dataclass semantics: `__eq__` over ALL fields (including `ref`),
  auto `__repr__` without `ref`, not frozen.
- `FeatureSet.__init__` (validated): a present intercept must be `Category.INTERCEPT` (else ValueError "wrong
  category"); the `features` list is built in the order intercept, then the mobilities in the MobilitySet's sorted
  (mask, amask) order, then the patterns in the PatternSet's sorted mask order — the child sets' sorted STORAGE order,
  not the caller's insertion order; `n_instances` is the sum; the `hash` is sha3_256 over `b'INTERCEPT'` (if present) +
  the mset hash hex string (if present) + the pset hash hex string (if present) — the child HASH values (transitively
  their sorted mask contents), not raw masks; the set name is NOT part of the hash.
- `print_summary` (validated): writes to an IO object (default stdout) — header line (name, length, hash), intercept
  present/None, per-set name+hash lines, then one line per feature `{i:02d} {category} {name:10s} {n_instances}
  {n_configurations:10,d}`.
- `compute_indexes(positions) -> IndexArray` (validated): the `(N, I)` uint32 matrix, `I` = the summed `n_instances` —
  column 0 = the intercept (constant 0) if present, then the `mset.compute_indexes` block, then the
  `pset.compute_principal_indexes` block (each pattern expanded into its `n_instances` columns in its unique-mask
  first-seen D8 order), merged with a single `np.hstack`. `N=0` or `I=0` returns `np.empty((N, I), dtype=Index)`
  immediately. The `IndexArray` return annotation carries the BeforeValidator dtype check via the imported alias
  (pattern.py).

## Verified invariants

Pinned by `test_feature.py` (19 tests + 1 PERF, no DB):

- Direct construction raises RuntimeError; the three factories assert all 5 fields each (ref equality via dataclass
  `__eq__`); a str argument to a factory → pydantic ValidationError; the `__repr__` golden; the field-wise `__eq__`; the
  instance is unhashable — `TestFeature` (8).
- `FeatureSet` construction on the 13-pattern + 3-mobility fixture (built in INSERTION order, deliberately different
  from the child sets' sorted storage order): name, the 3 object refs, `n_instances` 53, the 17-value per-feature list +
  the name-order golden (the ordering contract exercised for free), the pinned hash; the partial-None trio
  (intercept-only / mobility-only / pattern-only); a MOBILITY-category feature as intercept → ValueError; the full
  print_summary golden — `TestFeatureSet` (6).
- `compute_indexes`: the 3×10 literal golden (EDGE + DIAG4 + LMC + intercept, 3 real positions); the empty edges (0,10)
  / (3,0) / (0,0) + dtype; None / list / str / int64 ndarray → ValidationError (subTest) —
  `TestFeatureSetComputeIndexes` (5).
- `test_performance_1m`: 1M positions, 51 instances, warmup, throughput print, N/I asserts only (PERF=1, print-only, no
  gate) — `TestFeatureSetComputeIndexesPerf` (1).

## Open issues

None.

## Conventions

- Factory-method encapsulation: `Feature` instances exist only through the factories (created once, then read).
- The hash is over the child sets' hash values — changing a set name never changes the hash; changing a mask does.
- The shared test idiom family of the four base-module suites (PERF=1 print-only; the goldens independently re-derived
  from the public API).

## Integration

- The composition point of `board` (PositionArray), `pattern` (Pattern/PatternSet/Index/IndexArray) and `mobility`
  (Mobility/MobilitySet) — it owns no board logic of its own.
- Consumed by the FEATURES worker (wrk_features.py) and, through `ctx.feature_set`, by the INDEXES level onward.
