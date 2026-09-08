# reversi/lm/hlp_indexes.py
The INDEXES domain module of the RLM pipeline: the
`ReversiLogisticModelIndexes` data object (the 2-D uint32 index
matrix + its two metadata hashes) + 4 public functions (store /
load / compute / is_cache_consistent) — the data object of the
5th active level (CREATED → CONFIG → POSITIONS → FEATURES →
INDEXES), the SECOND cache_manager consumer after POSITIONS.
> State: D-084 · 297e531 · 2026-08-31 · suite 14/0/0

## API

| name | contract |
|---|---|
| `ReversiLogisticModelIndexes` | plain class — 3 fields `rds_checksum: str`, `feature_set_hash: str`, `indexes: IndexArray`, assigned BY REFERENCE (no copy); `compute_sha3_256_hash()` = the duck-typed data checksum; one-line `__repr__` |
| `rlm_indexes_store_to_file(rlm_indexes, filename)` | binio write: header + the 2 strings + the array; NO sidecar (cache_manager writes it) |
| `rlm_indexes_load_from_file(filename, checksum=True)` | sidecar verify (when enabled) + header gate (description + version) + read back a fresh object |
| `rlm_indexes_compute(ctx)` | builds a fresh object from `ctx` (NO `@validate_call` — see Conventions) |
| `rlm_indexes_is_cache_consistent(ctx, rlm_indexes)` | the pure 2-field metadata compare (NO `@validate_call`) |

## Architecture

- `ReversiLogisticModelIndexes.__init__` is
  `@validate_call(arbitrary_types_allowed)` — `IndexArray`
  (pattern.py L74: `Annotated[npt.NDArray[np.uint32],
  BeforeValidator(validate_index_array)]`) is what coerces the
  array. `compute_sha3_256_hash` (validated):
  `sha3_256(self.indexes.tobytes()).hexdigest()` — the hook
  cache_manager invokes (its 3rd return element); `__repr__` is
  validated (house style) — a one-line summary.
- `rlm_indexes_store_to_file` (validated): `filename: str | Path`
  → Path; `binio.BinaryWriter` — header
  ("ReversiLogisticModelIndexes binary data file", version 1),
  the 2 strings (rds_checksum, feature_set_hash), the array
  (write order pinned, probe A5). Docstring Note: no sidecar is
  written here — in the pipeline flow the sidecar is written by
  cache_manager (as in regab).
- `rlm_indexes_load_from_file` (validated): `checksum=True` →
  `binio.verify_sha3_256_sidecar(filename)` first (mismatch →
  RuntimeError); then the header gate — wrong description →
  RuntimeError "The file is not a proper ...", wrong version →
  RuntimeError "The file version is not consistent, found ...,
  expected 1"; then `read_string` ×2 + `read_array` → a fresh
  object.
- `rlm_indexes_compute`: `rds_checksum = ctx.rds_checksum`,
  `feature_set_hash = ctx.feature_set.hash`, `indexes =
  ctx.feature_set.compute_indexes(ctx.positions)` (public
  FeatureSet API) → fresh object.
- `rlm_indexes_is_cache_consistent`: `cached_feature_set_hash ==
  ctx.feature_set.hash AND cached_rds_checksum == ctx.rds_checksum`
  — a PURE compare (no DB params, no recompute); the
  cache_manager `validate_fn` (a mismatch deletes + recomputes).

## Verified invariants

Pinned by the 52-call `probes/verify_hlp_indexes.py` + the two test files (14 unit tests, all mocked; 2 DB-gated end-to-end).

- Source shape (probe A1-A11): 190 lines, the 5-name `__all__`,
  exactly 5 `@validate_call` (NOT on compute / is_cache_consistent
  — the no-validation comment), the store write order, the 3
  load RuntimeError messages, the 2-field compare, the D-084
  fixes.
- The object behaviour (pure, no DB, probe B2-B8): the data
  checksum (independent recompute) and the 3 load error paths
  (corrupted file, wrong description, wrong version); the
  compute identity (probe B12-B13) — a real fixture FeatureSet +
  a fabricated 2-position array: the (2, 16) uint32 matrix
  identical to `FeatureSet.compute_indexes` called directly, the
  checksums from the ctx.
- The pipeline integration (live DB, probe C2-C7): after
  `move_to_step("INDEXES")` the base dir holds ONLY the flat
  CONFIG + POSITIONS + INDEXES `.dat` + `.SHA3-256` pairs (no
  `rlmwf_03_FEATURES*`); `ctx.rlm_indexes` set,
  `ctx.rlm_indexes_checksum` = the DATA checksum; the sidecar is
  the flat `sha3_256sum` line (FILE checksum ≠ data checksum);
  the `(N, 16)` shape identical to the independent recompute;
  the cross-run identical object; `_down` clears BOTH.
- The unit suite (`test_rlm_indexes.py`, 14 tests, no DB): the
  3-field init (by-reference `assertIs`, the two precise
  `ValidationError` rejections), the store call sequence (both
  `assert_has_calls(any_order=False)` and the full
  `method_calls ==`), the 5 load paths (both checksum flags, the
  3 RuntimeError messages), the compute with a MagicMock ctx,
  the 3 `is_cache_consistent` single-field-diff branches.
- The end-to-end round-trip (DB-gated,
  `test_lm_worker_indexes.py`, 2 `SKIP_REGAB_DB`-gated tests):
  the compute + store run ("Executing heavy computation", the
  flat files on disk) and the second-instance cache hit ("Cache
  successfully loaded and validated", no heavy computation).

## Open issues

None.

## Conventions

- M5 (by design, source L166): NO `@validate_call` on
  `rlm_indexes_compute` / `rlm_indexes_is_cache_consistent` —
  the `ctx: RLMContext` annotation cannot be resolved by
  pydantic without a real import, so it stays under
  TYPE_CHECKING (the circular-import guard).
- The two checksums are distinct: `rlm_indexes_checksum` = the
  DATA checksum (sha3_256 over the raw uint32 bytes); the
  `.SHA3-256` sidecar = the FILE checksum (binio `sha3_256sum`
  format over the serialized `.dat`).
- The store writes NO sidecar — cache_manager owns it in the
  pipeline flow (the D-072/D-080 pattern).

## Integration

- The 5th RLM level; the worker (lm_worker_indexes.py) carries
  the cache wiring, this module the data object + the 4
  functions. Consumes `ctx.rds_checksum` (POSITIONS) and
  `ctx.feature_set` (FEATURES) — both must be set before
  `compute` runs (the SM half-open interval semantics guarantee
  it).
- Publishes `ctx.rlm_indexes` + `ctx.rlm_indexes_checksum` for
  the WMAPS level onward.
