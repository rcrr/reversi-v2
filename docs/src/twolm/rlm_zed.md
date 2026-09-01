# twolm/rlm_zed.py

Analysis date: 2026-08-31 — analysis session 24 (D-091); fix
campaign D-092 approved by Roberto ("T1-T8: OK") and applied in the
same session. Brought in by Roberto (commit 439c966 — the 8th active
level of the pipeline — the import + worker-list entry in
logistic_model.py were his; RLMContext already carried the `z` +
`y2z` + `z2y` + `zed_checksum` blackboard fields from first import).
Probe (scratch/verify_zed.py, 60 checks, tiers A–G, re-pinned in
D-092 to the post-campaign state): 0 mismatches.

The ZED domain module of the RLM pipeline: the
`ReversiLogisticModelZed` data object (the z (N,) float32 vector —
the affine image of the per-position game values — + the two
affine transformation closures `y2z` / `z2y`) + `zed_fun_factory`
(the pure math) + `rlm_zed_compute` + the duck-typed
`compute_sha3_256_hash`. The data object of the 8th active level
(CREATED sentinel → CONFIG → POSITIONS → FEATURES → INDEXES → WMAPS
→ DESIGN_MTR → ZED) and the FIRST non-cache level in the pipeline
(no store / load / is_cache_consistent, no cache_manager wiring, no
rlmwf_07* file — the on-the-fly choice, see the worker doc).

## Suite status (session 24, post D-092)

- `test_rlm_zed`: 10/0/0 (3 classes; no DB, no gate — the factory
  math pins (goldens, inverse, round-trip, 2-clippling endpoints),
  the handcrafted-mock compute (exact (4,) golden + hash identity),
  the init validation (2 ValidationError pins + by-reference), the
  rlm_01 hash golden) — NEW in D-092 T3.
- `test_lm_worker_zed`: 3/0/0 live (2 classes; 1 DB-free factory
  test + 2 DB-gated worker tests since D-092 T1 — the setUp moves
  through DESIGN_MTR on a fresh base dir, so a live DB is required).
- Full discover: 563 tests, 66 skipped under `SKIP_REGAB_DB=1`
  (17 PERF + 35 regab + 2 positions + 2 features + 2 indexes + 3
  wmaps + 3 design_matrix + 2 zed), GREEN; ungated (live DB): 563
  run, 17 skipped (PERF only), GREEN. The full `-W error` discover
  is clean.

## State per Roberto

Pipeline-in-progress, 8 active levels, enabled by Roberto's
2026-08-31 bring-in (commit 439c966: the two modules + the test,
uncommented the `lm_worker_zed` import + worker-list entry).
The next line-by-line step is `lm_worker_gradient` (the next
commented entry). ZED fix campaign (D-092) CLOSED: rlm_zed
T6 (the no-validation note) + T7 (the factory `@validate_call`) +
T8 (2 ws lines) fixed; lm_worker_zed T2 + T8 fixed; the worker test
T1/T4/T5/T8 fixed; the dedicated `test_rlm_zed.py` added (T3).

## Architecture (103 lines, post D-092)

- `ReversiLogisticModelZed` (L48-67): plain class. `__init__`
  (L53-60, `@validate_call
  (config=ConfigDict(arbitrary_types_allowed=True))`) with 3
  fields — `y2z: Callable[[NDArray[int8]], NDArray[float32]]`,
  `z2y: Callable[[NDArray[float32]], NDArray[float32]]`, `z:
  NDArray[float32]` — assigned by reference (no copy).
  `compute_sha3_256_hash` (L62-67, `@validate_call`): `sha3_256`
  over `z.tobytes()` ONLY (the single data vector — the duck-typed
  data-checksum hook; M1 below: the closures are not covered).
- `zed_fun_factory(logit_clipping: float)` (L70-90, `@validate_call`
  since D-092 T7 — the only exported public function in the pipeline
  that was missing it): returns the two affine closures. `y_to_z`
  (L80-83): `a = float32(0.5)`, `b = float32((1 − 2c)/128)`
  (L78-79), `z = a + y·b` with `y` cast to float32 — maps the int8
  range [−64, +64] onto [c, 1−c] (c = logit_clipping). `z_to_y`
  (L87-89): the exact inverse, `a1 = float32(−64/(1 − 2c))`,
  `b1 = float32(128/(1 − 2c))` (L85-86), `y = a1 + z·b1`.
- `rlm_zed_compute` (L94-103): NO `@validate_call` — the source
  documents why (L94: "Here validation is not possible, it brings
  in a convoluted issue with circular imports" — the rlm_indexes
  L166 note class, added in D-092 T6). Body: `alpha = ctx.
  cfg.stat_model.logit_clipping`; `y2z, z2y = zed_fun_factory
  (alpha)`; `y = ctx.game_values`; `z = y2z(y)`; returns
  `ReversiLogisticModelZed(y2z, z2y, z)`.
- NO `rlm_zed_store_to_file` / `_load_from_file` /
  `_is_cache_consistent` — the first non-cache level by design
  (vectorized math, "very fast" per the worker comment; no
  rlmwf_07* file ever materializes, probe D11).

## Verified facts (D-091/D-092 probe — 60 checks, 0 mismatches)

- V1 (A-tier): structure — 103 lines; `__all__` = the 3 public
  names; exactly 4 `@validate_call` decorators (init,
  compute_sha3_256_hash, zed_fun_factory [T7], NOT compute — with
  the L94 no-validation note [T6]); the affine constants pinned
  (L78-79, L85-86); the compute body (L99-102); no cache API; 0
  non-comment trailing-whitespace lines (D-092 T8).
- V2 (B-tier): the worker file — 73 lines; the factory WITH
  `@validate_call` + the pydantic import (D-092 T2); NO
  cache_manager wiring (by design); `_up` sets the 4 ctx
  attributes (L53-56); `_down` clears ALL FOUR (L64-67, the house
  shape — no gap at bring-in); 0 non-comment ws lines (D-092 T8).
- V3 (D-tier, live DB, rlm_01): the golden content re-derived
  independently — the pipeline run on rlm_01.json (logit_clipping
  0.03) compared against the pinned (10,) literals extracted from
  the test source (the single source of truth): y ==
  `[10, 36, −22, 18, −16, 14, −22, 20, 0, 2]` int8; z == the
  (10,) float32 literal == the independent float32 recompute
  `0.5 + y·(1−2c)/128` (exact) == the float64 reference
  (allclose); `ctx.zed_checksum == sha3_256(z.tobytes())`;
  endpoints `y2z(±64) = c / 1−c`, `y2z(0) = 0.5`; round-trip
  `z2y(y2z(y)) == float32(y)`; the base dir holds EXACTLY the 5
  flat files + 5 sidecars of the 5 cache levels (no rlmwf_07*);
  `_down` live: back at step 6, all 4 ctx attrs None again.
- V4 (G-tier): the dedicated test file — 157 lines; 3 classes /
  10 tests; no DB claim in the header (the file is DB-free); the
  rlm_01 hash golden `3d49fd5d56ced2f7bb70e5c24c8100b3318a7e66e7c99
  0de53ed2f16f365d9b2` pinned; the (4,) exact compute golden; the 2
  ValidationError pins; 0 ws lines.

## Minor notes

- **M1 (informational, D-091):** the duck-typed hash covers `z`
  only — the closures are pure functions of
  `cfg.stat_model.logit_clipping` (not stored on the object). Same
  game_values + different clipping → different z → different hash,
  so no collision risk today; a future cache would need the
  clipping in the checksum.
- **M2 (informational, D-091):** the flat-file numbering skips 07
  (FEATURES skipped 03): the next cache level (GRADIENT) takes
  rlmwf_08.

## Integration notes

- Pipeline ordering: `ctx.game_values` (POSITIONS — the (N,) int8
  vector, values in [−64, +64]) + `ctx.cfg.stat_model.
  logit_clipping` (CONFIG) must be set before `rlm_zed_compute`
  runs — the SM half-open interval semantics guarantee every
  up-move to step 7 passes through both. No other upstream
  dependency (the FEATURES/INDEXES/WMAPS/DESIGN_MTR outputs are
  NOT consumed by ZED).
- The worker (lm_worker_zed) recomputes on EVERY up-move (no
  cache file, no `is_allowed` switch — the uniform 7-kwargs
  cache_manager wiring is absent by design, the first deviation
  from the house pattern, documented in the worker comment).
- `zed_checksum` is a pure data checksum (sha3_256 over
  `z.tobytes()`) with no sidecar (nothing to sidecar — no file);
  it is logged by the worker and stored on the context for the
  next level (GRADIENT) to consume.
- z's dtype contract is float32 (pinned in the worker test + 3× in
  the dedicated test): the values live in [c, 1−c] ⊂ (0, 1); the
  float32 arithmetic is exact for the round-trip within the
  pinned allclose tolerances (1e-6/1e-7).

## Appendix — line reference

103 lines, as of D-092 (101 at D-091 bring-in; D-092: +1 note line
[T6], +1 decorator line [T7], 2 ws lines emptied in place [T8]).

- L29-35: imports (hashlib L31, numpy L31-32, typing L34, pydantic
  L35)
- L37-38: `RLMContext` under TYPE_CHECKING
- L42-44: `__all__` (the 3 public names)
- L48-67: `ReversiLogisticModelZed` (`__init__` L53-60,
  `compute_sha3_256_hash` L62-67)
- L70-90: `zed_fun_factory` (L70 decorator [T7]; constants
  L78-79 + L85-86; `y_to_z` L80-83, `z_to_y` L87-89, return L90)
- L94-103: `rlm_zed_compute` (L94 no-validation note [T6])
