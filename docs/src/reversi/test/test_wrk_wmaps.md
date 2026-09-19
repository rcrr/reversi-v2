# reversi/test/test_wrk_wmaps.py
The suite of the WMAPS worker. 2 classes / 3 tests / no PERF — ALL DB-DEPENDENT (the setUp moves through INDEXES on a
fresh base dir, which runs POSITIONS).

## Coverage

| class | what it pins |
|---|---|
| `TestLMWorkerWmaps` (2, rlm_00.json from `WORKSPACE_ROOT`, stdout patched to a StringIO, base dir under `CUSTOM_TMP_BASE`) | `test_compute_and_populate_cache`: `move_to_step("WMAPS")` (step 7 pinned) — the FLAT `rlmwf_07_WMAPS.dat` + `rlmwf_07_WMAPS.dat.SHA3-256` on disk (the machine-level naming pinned end-to-end), "Forcing computation" in the logs (the cache_manager first-run string), all 6 ctx arrays non-None + `len(ctx.w) > 0`, `verbosity=Verbosity.HIGH` (the house pattern). `test_read_cache_on_new_instance`: the second instance on the SAME base dir moves to INDEXES first (the 5 workers CONFIG → FEATURES → SU_ANALYSIS → POSITIONS → INDEXES are exercised), then WMAPS HITS the cache: "Cache successfully loaded and validated" in the logs, "Forcing computation" NOT in the logs (the negative pin), the 6 ctx arrays non-None again |
| `TestLMWorkerWmapsExactValues` (1, rlm_01.json, cut_off=2) | `test_compute_wmaps_exact_values`: the GOLDEN CONTENT pin — before WMAPS: all 6 ctx arrays None (the half-open interval guarantee); after: `expected_fwr` (4,3) = [[−1,0,0],[1,1,4],[5,5,15],[16,16,20]] int64 (per-feature [fallback, w_min, w_max]); `expected_iwmap_feature_offset` = [0,1,66,93,174] uint32 (F+1 cumulative); `expected_iwmap` (174,) int64 (mostly −1 — the unseen configurations); `expected_wmap` (21,3); `expected_wmap_fallback` (10,3) all freq 1 (f1: 6,11,15; f2: 3,5,10,11,20,23; f3: 40); `w` = 21 float32 zeros. The probe's surviving E-tier check (E9) re-derives the per-feature wmap row contiguity |

The shared setUp: the `db_long_gate` FIRST (the SKIP_REGAB_DB + LONG gates) + the paths idiom (the shared
`CUSTOM_TMP_BASE` from `reversi.test.paths`, `setUpClass` mkdir, `TemporaryDirectory` first in setUp, the
`WORKSPACE_ROOT`-anchored json_config, defensive tearDowns).

## Goldens pinned

- The flat cache file names: `rlmwf_07_WMAPS.dat` + `rlmwf_07_WMAPS.dat.SHA3-256`.
- The witness log lines: "Forcing computation" (compute run) + "Cache successfully loaded and validated" (cache hit)
  with the NEGATIVE pin.
- The full rlm_01 golden: the 6 array literals above (K=174, W=21, F=4, cut_off=2) — the single source of truth for the
  E-tier re-derivation after step 3.

## Conventions

- The paths idiom: the shared `CUSTOM_TMP_BASE` + the `WORKSPACE_ROOT` anchoring (both classes).
- The `SKIP_REGAB_DB` gate at the top of both setUps (3/0/3 under the gate).
- The `verbosity=Verbosity.HIGH` house pattern of the worker tests.

## Integration

- The end-to-end cache round-trip pin (both directions, the flat file names) + the golden content pin (all 6 arrays), as
  in the other worker test files.
- The per-feature contiguity fact (wmap row count == `w_max − w_min + 1`) is probe-side (E9) — the single E-tier
  survivor.
