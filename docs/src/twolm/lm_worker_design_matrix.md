# twolm/lm_worker_design_matrix.py

Analysis date: 2026-08-31 — analysis session 23 (D-089); fix
campaign D-090 approved by Roberto ("Procedi su tutti i T, e R1")
and applied in the same session. Brought in by Roberto in the
UNCOMMITTED 2026-08-31 bring-in (the 7th active level of the
pipeline — the import + worker-list entry in logistic_model.py were
his). Probe (scratch/verify_design_matrix.py, tier B, re-pinned in
D-090 to the post-campaign state): 0 mismatches.

The DESIGN_MTR worker of the RLM pipeline — the 7th active level
(CREATED sentinel → CONFIG → POSITIONS → FEATURES → INDEXES →
WMAPS → DESIGN_MTR). Like POSITIONS, INDEXES and WMAPS it is a
CACHE-CONSUMING level: the 4-step load-or-compute over the
rlm_design_matrix object (the flat `rlmwf_06_DESIGN_MTR.dat` +
binio-format sidecar + the duck-typed data checksum), the FOURTH
cache_manager consumer in the pipeline — the flat cache files DO
materialize (probe V4).

## Suite status (session 23, post D-090)

- `test_lm_worker_design_matrix`: 3/0/0 (2 classes — the end-to-end
  cache round-trip pin (first run "Forcing computation" + both flat
  files; second instance on the same base dir: "Cache successfully
  loaded and validated", no recompute) + the rlm_01 golden-content
  pin (the (10,7) uint32 X vs the 10 pinned rows). The setUp moves
  through WMAPS on a fresh base dir, so a live DB is required;
  DB-gated since D-090 T1, as in the other worker test files.
- `test_rlm_design_matrix`: 12/0/0 (the dedicated data-object
  suite — no DB, no gate; D-090 T6).
- Full discover: 550 tests, 64 skipped under `SKIP_REGAB_DB=1`
  (17 PERF + 35 regab + 2 positions + 2 features + 2 indexes + 3
  wmaps + 3 design_matrix), GREEN; ungated (live DB): 550 run, 17
  skipped (PERF only), GREEN.

## State per Roberto

Pipeline-in-progress, 7 active levels, enabled by Roberto's
2026-08-31 bring-in. DESIGN_MTR worker fix campaign (D-090)
CLOSED: T2-T3 + T5 fixed. The next line-by-line step is
`lm_worker_zed` (the next commented entry in logistic_model.py).

## Architecture (80 lines, post D-090)

- `lm_worker_design_matrix() -> Worker` (L77-80): factory
  returning `Worker("DESIGN_MTR", _up, _down)`; `@validate_call
  (config=ConfigDict(arbitrary_types_allowed=True))` since D-090
  T2 (the D-080 M1 / D-082 M1 / D-084 M1 / D-087 T6 pattern applied
  to the other six workers).
- `_up(ctx)` (L50-68): INFO "Computing Design Matrix (X)..." →
  `cache_manager_load_or_compute` with the full 7-kwargs wiring:
  `cache_path =
  ctx.get_cache_file_full_path_for_current_level()` (the injected
  D-078 machine-level closure — flat `rlmwf_06_DESIGN_MTR.dat`),
  `is_allowed = ctx.use_cache` (the CONFIG switch, the D-071 R1
  semantics), `load_fn = lambda path:
  rlm_design_matrix_load_from_file(path, checksum=False)` (D-090
  T3 — the house shape as in the other cache workers post D-080 M4
  / D-084 M3 / D-087 T7: the `checksum=True` default would
  re-verify the sidecar cache_manager already checked in step 2),
  `store_fn = rlm_design_matrix_store_to_file`,
  `validate_fn = lambda cached_dm:
  rlm_design_matrix_is_cache_consistent(ctx, cached_dm)` (the
  1-field metadata compare), `compute_fn = lambda:
  rlm_design_matrix_compute(ctx)`, `logger_fn = ctx.log_event`.
  Then: `ctx.design_matrix = dm_obj.X` with the INFO "Model
  attribute design_matrix has been set." + the INFO "Design Matrix
  computed/loaded. Shape: ..." → the INFO "Design matrix checksum
  (design_matrix_checksum): ..." → `ctx.design_matrix_checksum =
  dm_checksum` (the 2nd attribute, the DATA checksum — the
  cache_manager 3rd return element).
- `_down(ctx)` (L71-74): INFO "Clearing Design Matrix
  attribute..." → both attributes to None — `ctx.design_matrix`
  AND `ctx.design_matrix_checksum` (the house shape: object +
  checksum — already correct at bring-in, no T item).

## Verified facts (D-090 probe — 0 mismatches)

- V1 (B1-B3): 80 lines; `__all__ = ['lm_worker_design_matrix']`;
  the factory WITH `@validate_call` + the pydantic import (T2).
- V2 (B4): the full 7-kwargs cache wiring with the
  `load_fn = lambda path: rlm_design_matrix_load_from_file(path,
  checksum=False)` shape (T3).
- V3 (B5-B7): `_up` sets `ctx.design_matrix` (the bare ndarray
  `dm_obj.X`, NOT the object) + `ctx.design_matrix_checksum`;
  `_down` clears both (the house shape, verified at bring-in).
- V4 (live DB, cross-run): after `move_to_step("DESIGN_MTR")` —
  step 6, worker "DESIGN_MTR"; the base dir holds ONLY the flat
  `rlmwf_01_CONFIG.dat` + `.SHA3-256`, `rlmwf_02_POSITIONS.dat` +
  `.SHA3-256`, `rlmwf_04_INDEXES.dat` + `.SHA3-256`,
  `rlmwf_05_WMAPS.dat` + `.SHA3-256`, `rlmwf_06_DESIGN_MTR.dat` +
  `.SHA3-256` (no `rlmwf_03_FEATURES*` — the pure-compute level
  writes nothing). A second instance on the same base_dir: "Cache
  successfully loaded and validated", no "Forcing computation".

## Minor notes — RESOLVED (D-090)

- **T2 FIXED**: `@validate_call
  (config=ConfigDict(arbitrary_types_allowed=True))` on the public
  factory (L77) + the `from pydantic import validate_call,
  ConfigDict` import (L32) — the house convention, the same fix as
  D-080 M1 / D-082 M1 / D-084 M1 / D-087 T6.
- **T3 FIXED**: `load_fn = lambda path:
  rlm_design_matrix_load_from_file(path, checksum=False)` (L56) —
  the redundant sidecar re-verification is gone (cache_manager
  verifies in step 2; the raw function would verify again in
  step 3), the same shape as the D-080 M4 / D-084 M3 / D-087 T7
  fixes.
- **T5 FIXED**: the 2 whitespace-only lines stripped (emptied in
  place); scope as in D-078 M3: the license-header `# ` lines stay.

## Integration notes

- Pipeline ordering: `ctx.rlm_indexes` (INDEXES) + `ctx.iwmap` +
  `ctx.iwmap_feature_offset` + `ctx.wmaps_obj_checksum` (WMAPS)
  must all be set before `compute` runs — the SM half-open
  interval semantics guarantee every up-move to step 6 passes
  through all of them.
- The worker carries NO naming code — the flat
  `rlmwf_06_DESIGN_MTR.dat` comes from the injected full-path
  closure (the D-078 machine-level fix for ALL cache-consuming
  workers).
- `is_allowed = ctx.use_cache`: with `use_cache=False` the level
  always recomputes but still warms the cache file (the D-071 R1
  pattern).
- `validate_fn` is the 1-field metadata compare (no DB access, no
  recompute) — a business mismatch deletes + recomputes (the
  D-071 R2 pattern).
- The worker stores 2 blackboard fields (the X ndarray + the
  checksum) — `ctx.design_matrix` holds the BARE ndarray
  (`dm_obj.X`), not the data object: a later level (ZED, once
  brought in) consumes the array directly, and the hash method is
  duck-typed on the object only inside this level's store/load.

## Appendix — line reference

80 lines, as of D-090 (77 at bring-in; +2 for the pydantic import
block, +1 for the decorator, 2 ws lines emptied in place).

- L28-42: imports (pydantic L32 [T2], state_machine L34,
  rlm_design_matrix L35-38, cache_manager L39, TYPE_CHECKING
  RLMContext L41-42)
- L46: `__all__`
- L50-68: `_up` (cache wiring L53-61, T3 at L56, the 2-attribute
  population L63-68)
- L71-74: `_down`
- L77-80: `lm_worker_design_matrix()` (T2: `@validate_call` at
  L77)
