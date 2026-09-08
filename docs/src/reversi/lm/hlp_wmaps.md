# reversi/lm/hlp_wmaps.py
The WMAPS domain module of the RLM pipeline: the
`ReversiLogisticModelWMaps` data object (the 6 weight-map arrays
+ the 2 metadata scalars) + 4 public functions (store / load /
compute / is_cache_consistent) + the duck-typed
`compute_sha3_256_hash` — the 6th active level's data object
(CREATED → CONFIG → POSITIONS → FEATURES → INDEXES → WMAPS), the
THIRD cache_manager consumer after POSITIONS and INDEXES.
> State: D-087 · ded27eb · 2026-08-31 · suite 13/0/0

## API

| name | contract |
|---|---|
| `ReversiLogisticModelWMaps` | plain class — 8 fields, assigned BY REFERENCE: `hlp_indexes_checksum: str`, `cut_off: int`, `feature_w_ranges` (F,3) int64 [fallback, w_min, w_max], `iwmap_feature_offset` (F+1,) uint32, `iwmap` (K,) int64 (−1 = unseen configuration), `wmap` (W,3) int64 [fid, config_id_or_−1, freq], `wmap_fallback` (F_cut,3) int64, `w` (W,) float32 zeros |
| `hlp_wmaps_store_to_file(wmaps, filename)` | binio write: header + the checksum string + the i32 cut_off + the 6 arrays in declaration order; NO sidecar (cache_manager writes it) |
| `hlp_wmaps_load_from_file(filename, checksum=True)` | sidecar verify (when enabled) + header gate (description + version) + read back a fresh object |
| `hlp_wmaps_compute(ctx)` | builds a fresh object from the ctx pindexes (NO `@validate_call` — see Conventions) |
| `hlp_wmaps_is_cache_consistent(ctx, wmaps)` | the pure 2-field metadata compare (NO `@validate_call`) |

## Architecture

- `ReversiLogisticModelWMaps.__init__` is
  `@validate_call(arbitrary_types_allowed)` — plain
  `np.ndarray` annotations (no IndexArray alias here);
  `compute_sha3_256_hash` (validated): sha3_256 over the tobytes
  of the 6 ARRAYS in declaration order (NOT the 2 scalars) — the
  duck-typed data-checksum hook cache_manager invokes (its 3rd
  return element).
- `hlp_wmaps_store_to_file` (validated): `filename: str | Path` →
  Path; `binio.BinaryWriter` — `write_header
  ("ReversiLogisticModelWMaps binary data file", 1)`,
  `write_string(hlp_indexes_checksum)`, `write_i32(cut_off)`,
  `write_array` ×6 in declaration order (the write order is
  pinned). Plain docstring — no sidecar promise (the pipeline-flow
  sidecar is written by cache_manager, the D-072 machine).
- `hlp_wmaps_load_from_file` (validated): `checksum=True` →
  `binio.verify_sha3_256_sidecar(filename)` first (mismatch →
  RuntimeError); then the header gate — wrong description →
  RuntimeError "The file is not a proper ...", wrong version →
  "File version mismatch: found ..., expected 1" (the DIFFERENT
  wording vs hlp_indexes); then `read_string` + `read_i32` +
  `read_array` ×6 → a fresh object.
- `hlp_wmaps_compute`: `cut_off =
  ctx.cfg.stat_model.frequency_cut_off`; per feature: the pindexes
  column slice (cols from col_offset), `np.unique(...,
  return_counts=True)`, `mask = counts < cut_off` — below-cutoff
  configs share the feature's single fallback weight (config_id
  −1 in the wmap, the fallback row first with the summed freq),
  above-cutoff configs get contiguous `next_w` indices; the
  `f_iwmap[stats[:,0]] = stats[:,2]` scatter; wmap rows
  `[fid, config_id_or_−1, freq]` (−1 rows = the fallbacks);
  `wmap_fallback` = the excluded rows; `w = zeros(next_w, float32)`.
- `hlp_wmaps_is_cache_consistent` (PURE 2-field compare, no DB
  params, no recompute — the cache_manager `validate_fn`):
  `cached.hlp_indexes_checksum == ctx.hlp_indexes_checksum AND
  cached.cut_off == ctx.cfg.stat_model.frequency_cut_off`.

## Verified invariants

Pinned by the 53-call `probes/verify_wmaps.py` + `test_hlp_wmaps.py` (13 tests, no DB) + `test_lm_worker_wmaps.py` (3 DB-gated tests).

- Source shape (probe A1-A12 + B1-B9): module 316 lines, the
  5-name `__all__`, exactly 4 `@validate_call` (NOT on compute /
  is_cache_consistent — the L181 no-validation comment), the
  store write order, the 3 load RuntimeError messages, the 2-field
  compare, 0 non-comment trailing-whitespace lines; worker 91
  lines, the factory WITH `@validate_call`, the 7-kwargs cache
  wiring with the `checksum=False` load_fn, `_down` clears all 7
  INCLUDING `ctx.wmaps_obj_checksum`.
- The pipeline integration (live DB, probe C1-C15): after
  `move_to_step("WMAPS")` (step 5) the base dir holds ONLY the
  flat CONFIG + POSITIONS + INDEXES + WMAPS `.dat` + `.SHA3-256`
  pairs (no `rlmwf_03_FEATURES*`); the cross-run cache hit +
  identical data; E9 — the per-feature wmap row count == `w_max −
  w_min + 1` (contiguous ranges).
- The unit suite (`test_hlp_wmaps.py`, 13 tests, no DB): the
  compute semantics (both branches — a handcrafted 4×3 mock
  pindexes: cut_off=2 → the single fallback weight per feature;
  cut_off=0 → no fallback, the mock-only branch), the 3
  consistency branches (both single-field diffs), the full
  store/load contract (the 8-field cycle, the golden hash, the 3
  load error paths, both checksum flags), the init validation.
- The end-to-end round-trip + the golden content (DB-gated,
  `test_lm_worker_wmaps.py`): the compute + store run, the
  second-instance cache hit, and the rlm_01 golden (cut_off 2,
  F=4, K=174, W=21 — all 6 arrays vs the test literals, the
  single source of truth; the former probe E tier moved here at
  step 3).

## Open issues

None.

## Conventions

- R1 (by Roberto's contract, documented in the `hlp_wmaps_compute`
  docstring): the input pindexes matrix is DENSE — every cell
  holds a valid configuration index in 0..n_configurations − 1
  (the indexes are unsigned, never −1); the −1 'unseen
  configuration' sentinel can only appear in the OUTPUT iwmap. NO
  input guard is added (resolved as no-guard).
- No `@validate_call` on `hlp_wmaps_compute` /
  `hlp_wmaps_is_cache_consistent` — the same TYPE_CHECKING
  circular-import constraint as hlp_indexes (the L181 note).
- The two checksums are distinct (as in INDEXES):
  `wmaps_obj_checksum` = the DATA checksum (sha3_256 over the 6
  raw array tobytes); the `.SHA3-256` sidecar = the FILE checksum
  (binio `sha3_256sum` format over the serialized `.dat`).

## Integration

- The 6th RLM level; the worker (lm_worker_wmaps.py) carries the
  cache wiring, this module the data object + the 4 functions.
- Consumes `ctx.hlp_indexes_checksum` (INDEXES) +
  `ctx.cfg.stat_model.frequency_cut_off` (CONFIG) + the pindexes
  layout (POSITIONS/FEATURES) — the SM half-open interval
  semantics guarantee all are set before `compute` runs.
- Publishes the 6 ctx arrays + `ctx.wmaps_obj_checksum` for the
  DESIGN_MTR level onward.
