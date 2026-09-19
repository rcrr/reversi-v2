# reversi/lm/hlp_design_matrix.py
The DESIGN_MTR domain module of the LM pipeline: the `LMDesignMatrix` data object (the (N,I) uint32 X — the w-index of
each (position, feature-instance) cell — + the `wmaps_obj_checksum` metadata) + 4 public functions + the duck-typed
`compute_sha3_256_hash` — the 7th active level's data object (CREATED → CONFIG → FEATURES → POSITIONS → INDEXES → WMAPS
→ DESIGN_MTR), the FOURTH cache_manager consumer in the pipeline.

## API

| name | contract |
|---|---|
| `LMDesignMatrix` | plain class — 2 fields, assigned BY REFERENCE: `wmaps_obj_checksum: str`, `X: np.ndarray` (N,I) uint32 (N = training positions, I = total feature instances) |
| `hlp_design_matrix_store_to_file(dm, filename, compressed=True)` | binio write: header + the checksum string + X; LZ4 whole-file frame by default; the sidecar is written by the binio writer |
| `hlp_design_matrix_load_from_file(filename, checksum=True, compressed=True)` | LZ4 guard + decompress, then the sidecar verify (when enabled) + the header gate (description + version) + read back a fresh object |
| `hlp_design_matrix_compute(ctx)` | builds X from the pindexes + the WMAPS arrays (NO `@validate_call` — see Conventions) |
| `hlp_design_matrix_is_cache_consistent(ctx, dm)` | the pure 1-field metadata compare (NO `@validate_call`) |

## Architecture

- `LMDesignMatrix.__init__` is `@validate_call(arbitrary_types_allowed)`; `compute_sha3_256_hash` (validated) = sha3_256
  over `X.tobytes()` ONLY (the single data array — the duck-typed data-checksum hook).
- `hlp_design_matrix_store_to_file` (validated): `filename: str | Path` → Path; `binio.BinaryWriter` —
  `write_header ("LMDesignMatrix binary data file", 1)`, `write_string(dm.wmaps_obj_checksum)`, `write_array(dm.X)`. The
  writer runs with `compressed=True` by default (as in model_weights) — the LZ4 whole-file frame; the sidecar is written
  by the binio writer (cache_manager re-writes it idempotently in the pipeline flow).
- `hlp_design_matrix_load_from_file` (validated): `compressed=True` → the LZ4 frame guard + decompress (a non-frame file
  → the binio BinaryFormatError — the self-healing delete+recompute path); `checksum=True` →
  `binio.verify_sha3_256_sidecar` first (mismatch → RuntimeError "The checksum file signature doesn't match..."); the
  header gate (wrong description / wrong version → the 2 RuntimeError messages); `read_string` + `read_array` → a fresh
  object.
- `hlp_design_matrix_compute`: `pindexes = ctx.hlp_indexes.indexes`;
  `col_offsets = np.repeat (ctx.iwmap_feature_offset[:-1], n_instances_per_feature)`;
  `pindexes_with_offsets = pindexes + col_offsets`; the SINGLE guard — `np.any(ctx.iwmap[pindexes_with_offsets] == -1)`
  → ValueError "It should never happen, pindexes is referring an invalid value."; `X = np.empty(pindexes.shape, uint32)`
  filled by `np.take(ctx.iwmap.astype(np.uint32), pindexes_with_offsets, out=X)` — the explicit source cast (the
  L125-128 note, see Conventions). Returns the object with `ctx.wmaps_obj_checksum`.
- `hlp_design_matrix_is_cache_consistent`: `dm. wmaps_obj_checksum == ctx.wmaps_obj_checksum` — a PURE 1-field compare
  (no DB params, no independent model params: X is a pure function of the WMAPS outputs + pindexes, unlike WMAPS's 2
  fields and INDEXES's 3).

## Verified invariants

Pinned by the 54-call `probes/verify_design_matrix.py` + `test_hlp_design_matrix.py` (14 tests, no DB) +
`test_wrk_design_matrix.py` (3 DB-gated tests).

- Source shape (probe A1-A15): 139 lines, the 5-name `__all__`, exactly 4 `@validate_call` (NOT on compute /
  is_cache_consistent — the L113 note), the store write order, the 3 load RuntimeError messages, the 1-field compare,
  the explicit cast + single guard pinned (L125-128 / L122-123).
- Worker file shape (probe B1-B9): 80 lines, the factory WITH `@validate_call`, the 7-kwargs cache wiring (the
  `checksum=False` load_fn), `_down` clears BOTH attributes.
- The live-DB golden re-derivation (probe D5-D10, rlm_01): X == the independent recompute
  `iwmap[pindexes + col_offsets]`, every value a valid w index (< W=21), per-feature columns within their iwmap regions,
  intercept column all 0, the DATA checksum identity.
- Cross-fixture facts (probe F1/F4/F5): LMContext has both fields; rlm_01 stat_model {cut_off 2, logit 0.03, ridge 0.0},
  layout n_instances [1,1,4,1] (sum 7) / n_configurations [1,65,27,81] (K=174). The unit suite (14 tests, no DB): the
  compute math (both branches — a handcrafted mock mirroring the WMAPS one), the consistency compare, the store/load
  contract (cycle + golden hash + the 3 error paths), the init validation. The end-to-end round-trip + the (10,7) golden
  (DB-gated, `test_wrk_design_matrix.py`) is the single source of truth.

## Open issues

None.

## Conventions

- The explicit-cast note (L125-128): `astype(np.uint32)` is REQUIRED — the implicit int64 → uint32 output cast in
  `np.take(..., out=X)` is deprecated in NumPy 2.5 (future hard error), FATAL under `-W error` (X keeps the `np.empty`
  garbage).
- The single guard is a defensive re-check of the WMAPS R1 contract (pindexes dense, unsigned — a referenced −1 slot is
  a data bug, hence "It should never happen"); the guarded invariant: iwmap values are −1 or ≥ 0.
- No `@validate_call` on `hlp_design_matrix_compute` / `hlp_design_matrix_is_cache_consistent` — the TYPE_CHECKING
  circular-import constraint (the L113 note).
- The two checksums are distinct (as in WMAPS/INDEXES): `design_matrix_checksum` = the DATA checksum (sha3_256 over
  `X.tobytes()`); the `.SHA3-256` sidecar = the FILE checksum (binio `sha3_256sum` over the `.dat`). X is uint32,
  matching the pindexes/offset dtypes (no upcast on the addition).

## Integration

- The 7th LM level; the worker (wrk_design_matrix.py) carries the cache wiring, this module the data object + the 4
  functions. Consumes `ctx.hlp_indexes` (INDEXES) + `ctx.iwmap` + `ctx.iwmap_feature_offset` + `ctx.wmaps_obj_checksum`
  (WMAPS) + the per-feature `n_instances` (FEATURES) — the SM half-open interval semantics guarantee all are set before
  `compute` runs.
- Publishes the BARE ndarray `ctx.design_matrix` (= `dm_obj.X`, NOT the data object) + `ctx.design_matrix_checksum` —
  the later level (ZED) consumes the array directly; the hash method is duck-typed on the object only inside this
  level's store/load.
