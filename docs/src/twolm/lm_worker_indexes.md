# twolm/lm_worker_indexes.py

Analysis date: 2026-08-31 — analysis session 23 (D-083); fix campaign
D-084 approved by Roberto ("Sì fai tutto") and applied in the same
session. Brought in by Roberto together with rlm_indexes in a323e0f
(2026-08-31, the 5th active level of the pipeline — the import L44 +
worker-list entry in logistic_model.py were the only 2 lines the
commit touched there). Probe (scratch/verify_rlm_indexes.py, tiers C
+ D, re-pinned in D-084 to the post-campaign state): 0 mismatches.

The INDEXES worker of the RLM pipeline — the 5th active level
(CREATED sentinel → CONFIG → POSITIONS → FEATURES → INDEXES). Like
POSITIONS it is a CACHE-CONSUMING level: the 4-step
load-or-compute over the rlm_indexes object (the flat
`rlmwf_04_INDEXES.dat` + binio-format sidecar + the duck-typed data
checksum), the SECOND cache_manager consumer in the pipeline after
POSITIONS (D-079) — unlike FEATURES, the flat cache files DO
materialize (probe C2).

## Suite status (session 23, post D-084)

- `test_lm_worker_indexes`: 2/0/0 (1 class / 2 tests — the
  end-to-end cache round-trip pin: first run DB hit through
  POSITIONS + flat files + "Executing heavy computation"; second
  instance on the same base dir: "Cache successfully loaded and
  validated", no heavy computation. The setUp moves to FEATURES on
  a fresh base dir, so a live DB is required; DB-gated since
  D-084 T2, as in the other worker test files).
- Full discover: 516 tests, 58 skipped under `SKIP_REGAB_DB=1`
  (17 PERF + 35 regab + 2 positions + 2 features + 2 indexes),
  GREEN; ungated (live DB): 516 run, 17 skipped (PERF only), GREEN.

## State per Roberto

Pipeline-in-progress, 5 active levels, enabled line-by-line by
Roberto in a323e0f. INDEXES worker fix campaign (D-084) CLOSED:
M1-M3 fixed. The next line-by-line step is `lm_worker_wmaps` (the
next commented entry, logistic_model.py L45).

## Architecture (80 lines, post D-084)

- `lm_worker_indexes() -> Worker` (L77-80): factory returning
  `Worker("INDEXES", _up, _down)`; `@validate_call
  (config=ConfigDict(arbitrary_types_allowed=True))` since D-084 M1
  (the D-080 M1 / D-082 M1 pattern applied to the other workers).
- `_up(ctx)` (L51-68): INFO "Computing indexes for the feature
  set..." → `cache_manager_load_or_compute` with the full
  7-kwargs wiring (probe D5): `cache_path =
  ctx.get_cache_file_full_path_for_current_level()` (the injected
  D-078 machine-level closure — flat
  `rlmwf_04_INDEXES.dat`), `is_allowed = ctx.use_cache` (the
  CONFIG switch, D-071 R1 semantics), `load_fn =
  lambda path: rlm_indexes_load_from_file(path, checksum=False)`
  (D-084 M3 — as in the other cache workers post D-080 M4: the
  `checksum=True` default would re-verify the sidecar cache_manager
  already checked in step 2),
  `store_fn = rlm_indexes_store_to_file`, `validate_fn =
  lambda cached: rlm_indexes_is_cache_consistent(ctx, cached)`
  (the 2-field metadata compare), `compute_fn =
  lambda: rlm_indexes_compute(ctx)`, `logger_fn = ctx.log_event`.
  Then: INFO "Model attribute rlm_indexes has been set." →
  `ctx.rlm_indexes = rlm_indexes` → INFO
  "Indexes checksum (rlm_indexes_checksum): ..." →
  `ctx.rlm_indexes_checksum = rlm_indexes_checksum`.
- `_down(ctx)` (L71-74): INFO "Clearing rlm_indexes..." →
  `ctx.rlm_indexes = None` AND `ctx.rlm_indexes_checksum = None`
  (both cleared, probe C7).

## Verified facts (D-084 probe — 0 mismatches)

- V1 (C1, live DB): after `move_to_step("INDEXES")` — step 4,
  worker "INDEXES"; the 5-worker list is
  `[CREATED, CONFIG, POSITIONS, FEATURES, INDEXES]` (the
  logistic_model probe V3c, re-pinned D-083).
- V2 (C2, live DB): flat cache files — the base dir holds ONLY
  `rlmwf_01_CONFIG.dat` + `.SHA3-256`, `rlmwf_02_POSITIONS.dat` +
  `.SHA3-256`, `rlmwf_04_INDEXES.dat` + `.SHA3-256` (no
  `rlmwf_03_FEATURES*` — the pure-compute level writes nothing).
  The D-078 machine-level naming: no `rlmwf_/` subdirectory.
- V3 (C3, live DB): `ctx.rlm_indexes` set;
  `ctx.rlm_indexes_checksum` = `sha3_256(indexes.tobytes())`
  (independently recomputed — the DATA checksum, the
  cache_manager 3rd return element).
- V4 (C4, live DB): the on-disk sidecar = the flat
  `sha3_256sum` line over the `.dat` (the FILE checksum — different
  from the data checksum).
- V5 (C5, live DB): `indexes` shape (N, 16) uint32 (N = the
  training position count; 16 = the fixture n_instances sum),
  identical to the independent
  `feature_set.compute_indexes(feature_set positions)` recompute.
- V6 (C6a-c, live DB): cross-run — a second instance on the same
  base_dir: "Cache successfully loaded and validated", no
  "Executing heavy computation", `rlm_indexes` IDENTICAL (checksum
  + matrix).
- V7 (C7, live DB): `_down` (down to FEATURES, step 3) clears BOTH
  `ctx.rlm_indexes` and `ctx.rlm_indexes_checksum`.
- V8 (D1-D6): structure — 80 lines; `__all__ =
  ['lm_worker_indexes']`; factory + `Worker("INDEXES", _up, _down)`
  WITH `@validate_call` (D3, D-084 M1); the RLMContext import under
  TYPE_CHECKING (D4, the circular-import guard); the full 7-kwargs
  cache wiring with the `load_fn =
  lambda path: rlm_indexes_load_from_file(path, checksum=False)`
  shape (D5, D-084 M3); `_down` clears both + 0 non-comment
  trailing-whitespace lines (D6, D-084 M2).

## Minor notes — RESOLVED (D-084)

- **M1 FIXED**: `@validate_call
  (config=ConfigDict(arbitrary_types_allowed=True))` on the public
  factory (L77) + the `from pydantic import validate_call,
  ConfigDict` import (L32) — the house convention, the same fix as
  D-080 M1 (lm_worker_positions) / D-082 M1 (lm_worker_features).
- **M2 FIXED**: the 2 non-comment trailing-whitespace lines (L62
  after the cache_manager call, L68 between `_up` and `_down`
  pre-fix) stripped; scope as in D-078 M3: the license-header `# `
  lines stay.
- **M3 FIXED**: `load_fn =
  lambda path: rlm_indexes_load_from_file(path, checksum=False)`
  (L57) — the redundant sidecar re-verification is gone, the same
  shape as POSITIONS' D-080 M4 fix.

## Integration notes

- Pipeline ordering: `ctx.rds_checksum` (POSITIONS) and
  `ctx.feature_set` (FEATURES) must both be set before `compute`
  runs — the SM half-open interval semantics guarantee every up-
  move to step 4 passes through both levels (and FEATURES is pure
  compute, so it always re-derives the FeatureSet).
- The worker carries NO naming code — the flat
  `rlmwf_04_INDEXES.dat` comes from the injected full-path closure
  (the D-078 machine-level fix for ALL cache-consuming workers).
- `is_allowed = ctx.use_cache`: with `use_cache=False` the level
  always recomputes but still warms the cache file (D-071 R1 —
  visible here as in POSITIONS).
- `validate_fn` is the 2-field metadata compare (no DB access, no
  recompute) — a business mismatch deletes + recomputes (D-071
  R2: a raising validator would too; this one returns False).

## Appendix — line reference

80 lines, as of D-084 (77 at a323e0f arrival).

- L28-43: imports (pydantic L32 [M1], state_machine L34,
  rlm_indexes L35-39, cache_manager L40, TYPE_CHECKING RLMContext
  L42-43)
- L47: `__all__`
- L51-68: `_up` (cache wiring L54-62, M3 at L57, 0 non-comment
  trailing-whitespace lines [M2])
- L71-74: `_down`
- L77-80: `lm_worker_indexes()` (M1: `@validate_call` at L77)
