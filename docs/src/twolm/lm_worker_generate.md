# twolm/lm_worker_generate.py

Analysis date: 2026-09-02 — analysis session 27 (D-097); fix
campaign D-098 approved by Roberto and applied in the same session.
Brought in by Roberto (commit e31c061 — the 11th active level of
the pipeline). Probe (scratch/verify_generate.py, 43 checks, tiers
A–F, re-pinned to the post-campaign state): 0 mismatches.

The GENERATE worker of the RLM pipeline: `_up` runs the
cache_manager_load_or_compute flow to materialize the dense weight
vector (`ctx.w_dense` + `ctx.dense_w_checksum`) and `_down` clears
both. The 5th cache_manager consumer with the uniform 7-kwargs
wiring (config, positions, indexes, wmaps, design_matrix — D-072
machine): the flat file `rlmwf_10_GENERATE.dat` + `.SHA3-256`
(machine closure `{prefix}{level:02}_{worker_name}.dat`, step 10).
After OPTIMIZE's config-driven checkpoint name (D-096 M8), GENERATE
is the last cache level before the future VLD_POSITIONS (rlmwf_11).

## Suite status (session 27, post D-098)

- `test_lm_worker_generate`: 3/0/0 live (1 class; 3 DB-gated —
  the setUp moves through OPTIMIZE on a fresh base dir, so a live
  DB is required; 3/0/3 under `SKIP_REGAB_DB=1`) — NEW in D-098
  T5 (the bring-in had NO worker test at all).
- `test_rlm_generate` (the domain module): 14/0/0 (4 classes, no
  DB).
- Full discover: 615 tests, 74 skipped under `SKIP_REGAB_DB=1`,
  GREEN; ungated (live DB): 615 run, 17 skipped (PERF only),
  GREEN. The full `-W error` discover is clean.

## State per Roberto

Pipeline-in-progress, 11 active levels. GENERATE fix campaign
(D-098) CLOSED: R1 (the `_for_next_level` call — the D-074 R1 trap
re-introduced, the one-line rename, see rlm_generate.md R1),
T3 (the factory `@validate_call` + the pydantic import), T7 (4 ws
lines) applied. The triple blank lines L43-45 / L47-49 are the
canonical pattern of all 10 worker files (house style, D-094 M4).

## Architecture (78 lines, post D-098)

- `_up` (L50-67): logs "Generating dense weight vector (w_dense)
  for inference..." (L51), the uniform 7-kwargs
  `cache_manager_load_or_compute` (L53-61): `cache_path =
  ctx.get_cache_file_full_path_for_current_level()` (L54 — post
  D-098 R1; the bring-in called the nonexistent
  `..._for_next_level()`, the D-074 R1 trap re-introduced),
  `is_allowed = ctx.use_cache`, `load_fn = rlm_generate_load_from_
  file`, `store_fn = rlm_generate_store_to_file`, `validate_fn` =
  the is_cache_consistent closure, `compute_fn` = the
  compute_w_dense closure, `logger_fn = ctx.log_event`. Sets
  `ctx.w_dense = dense_obj.w_dense` (L63) + the shape log (L64),
  logs the dense_w_checksum (L66) and sets `ctx.dense_w_checksum`
  (L67).
- `_down` (L70-73): logs "Clearing dense weight vector..." (L71),
  `ctx.w_dense = None` (L72), `ctx.dense_w_checksum = None`
  (L73) — the scope pinned by the worker test
  test_down_clears_generate_attributes (D-098 T5).
- `lm_worker_generate()` (L76-78, `@validate_call
  (config=ConfigDict(arbitrary_types_allowed=True))` since D-098
  T3 — like all 10 worker factories): returns
  `Worker("GENERATE", _up, _down)`.

## Verified facts

- The worker list is the 11 active entries (probe F3): CREATED
  sentinel + CONFIG + POSITIONS + FEATURES + INDEXES + WMAPS +
  DESIGN_MTR + ZED + GRADIENT + OPTIMIZE + GENERATE.
- Live (rlm_02, probe E tier + the worker suite): the full
  pipeline to GENERATE writes `rlmwf_10_GENERATE.dat` +
  `.SHA3-256` (sidecar verifies); `ctx.w_dense` (6588,) float32,
  `ctx.dense_w_checksum` = the hash golden
  `ec9d65453bb112bf277c79f96a86edfa9468bb01f42a2763cd82d69c5b2b15b4`
  (= sha3_256 of the dense bytes, the duck-typed hash); the
  second instance on the same base dir gets the GENERATE cache hit
  ("Cache successfully loaded and validated", no recompute,
  `w_dense` array-equal); `move_to_step(9)` back to OPTIMIZE
  clears BOTH fields (worker test).
- The `w_dense: Any = None` + `dense_w_checksum: str | None =
  None` blackboard fields were pre-declared in RLMContext
  (logistic_model.py L142-143) at first import (probe F1) — the
  D-094 fg pattern, no change to this module's context.

## Minor notes

- **M1** (informational, by design): the flat-file numbering takes
  rlmwf_10 — the next cache level (VLD_POSITIONS, if brought in)
  takes rlmwf_11.
