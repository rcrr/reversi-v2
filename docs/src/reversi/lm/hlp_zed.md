# reversi/lm/hlp_zed.py
The ZED domain module of the RLM pipeline: the
`ReversiLogisticModelZed` data object (the z (N,) float32 vector —
the affine image of the per-position game values — + the two affine
transformation closures `y2z` / `z2y`) + `zed_fun_factory` (the
pure math) + `hlp_zed_compute` + the duck-typed
`compute_sha3_256_hash`. The data object of the 8th active level
(CREATED sentinel → CONFIG → POSITIONS → FEATURES → INDEXES →
WMAPS → DESIGN_MTR → ZED) and the FIRST non-cache level in the
pipeline (no store / load / is_cache_consistent, no cache_manager
wiring, no rlmwf_07* file — see the worker doc).
> State: D-092 · 17a5f95 · 2026-09-01 · suite 10/0/0

## API

| name | contract |
|---|---|
| `ReversiLogisticModelZed` | plain class — 3 fields, assigned BY REFERENCE: `y2z` (int8 → float32), `z2y` (float32 → float32), `z: NDArray[float32]` |
| `zed_fun_factory(logit_clipping)` | `@validate_call` — returns the two affine closures |
| `hlp_zed_compute(ctx)` | builds the object from `ctx.game_values` + the clipping (NO `@validate_call` — see Conventions) |

## Architecture

- `ReversiLogisticModelZed.__init__` is
  `@validate_call(arbitrary_types_allowed)`;
  `compute_sha3_256_hash` (validated) = sha3_256 over
  `z.tobytes()` ONLY (the single data vector — the duck-typed
  data-checksum hook; the closures are NOT covered, see
  Conventions).
- `zed_fun_factory(logit_clipping)` (validated — the D-092 T7
  fix, the only exported public function that was missing it):
  `a = float32(0.5)`, `b = float32((1 − 2c)/128)`;
  `y_to_z(y)`: `y` cast to float32, `z = a + y·b` — maps the int8
  range [−64, +64] onto [c, 1−c] (c = logit_clipping).
  `z_to_y(z)`: the EXACT inverse, `a1 = float32(−64/(1 − 2c))`,
  `b1 = float32(128/(1 − 2c))`, `y = a1 + z·b1`.
- `hlp_zed_compute`: NO `@validate_call` (the L94 no-validation
  note — the hlp_indexes L166 class, the D-092 T6 fix). Body:
  `alpha = ctx.cfg.stat_model.logit_clipping`; `y2z, z2y =
  zed_fun_factory(alpha)`; `y = ctx.game_values`; `z = y2z(y)`;
  returns the object.
- NO store / load / is_cache_consistent functions — the first
  non-cache level by design (vectorized math, "very fast" per the
  worker comment; no rlmwf_07* file ever materializes — probe
  D11).

## Verified invariants

Pinned by the 51-call `probes/verify_zed.py` + `test_hlp_zed.py`
(10 tests, no DB) + `test_wrk_zed.py` (3 tests, 2
DB-gated).

- Source shape (probe A1-A12): 103 lines, the 3-name `__all__`,
  exactly 4 `@validate_call` (init, hash, factory [T7] — NOT
  compute, with the L94 no-validation note [T6]), the affine
  constants pinned (L78-79, L85-86), the compute body (L99-102),
  no cache API, 0 non-header trailing-whitespace lines (T8).
- The worker file shape (probe B1-B8): 73 lines, the factory WITH
  `@validate_call` + the pydantic import (T2), NO cache_manager
  import (the L49 by-design comment pinned), `_up` sets the 4 ctx
  attributes, `_down` clears ALL FOUR, `Worker("ZED", ...)`.
- The live-DB golden re-derivation (probe D1/D5-D11, rlm_01):
  the pre-state (all 4 ctx attrs None); z == the independent
  float32 recompute `0.5 + y·(1−2c)/128` (EXACT) == the float64
  reference (allclose); `zed_checksum == sha3_256(z.tobytes())`;
  both closures callables; live endpoints `y2z(−64) ≈ c`,
  `y2z(0) == 0.5`, `y2z(64) ≈ 1−c`; live round-trip
  `z2y(y2z(y)) == float32(y)`; the base dir holds EXACTLY the 5
  flat files + 5 sidecars of the 5 cache levels (no rlmwf_07*).
- The cross-module facts (probe F1/F4/F5): RLMContext's 4 zed
  fields pre-declared (L129-132), untouched by the commit; the
  dedicated test exists (10 tests, no DB wiring); the 4 D-007
  mirror docs exist.
- The unit suite (10 tests, no DB): the factory math (both
  branches + 2-clippling endpoints), the mock compute (the exact
  (4,) golden + the hash identity), the init validation (2
  ValidationError pins + by-reference).
- The live golden (DB-gated, `test_wrk_zed.py`): the
  rlm_01 (10,) y/z literals — the single source of truth after
  the step-3 class c deletions (A13-A15 to the factory tests,
  D2-D4 + D12 to the worker tests).

## Open issues

None.

## Conventions

- The duck-typed hash covers `z` ONLY (the old M1,
  informational): the closures are pure functions of
  `cfg.stat_model.logit_clipping` (not stored on the object).
  Same game_values + different clipping → different z →
  different hash, so no collision risk today; a future cache
  would need the clipping in the checksum.
- The flat-file numbering skips 07 (FEATURES skipped 03): the
  next cache level (GRADIENT) takes rlmwf_08.
- z's dtype contract is float32 (pinned in the worker test + 3×
  in the dedicated test): the values live in [c, 1−c] ⊂ (0, 1);
  the float32 arithmetic is exact for the round-trip within the
  pinned allclose tolerances (1e-6/1e-7).
- No `@validate_call` on `hlp_zed_compute` — the TYPE_CHECKING
  circular-import constraint (the L94 note).

## Integration

- Pipeline ordering: `ctx.game_values` (POSITIONS — the (N,) int8
  vector, values in [−64, +64]) + `ctx.cfg.stat_model.
  logit_clipping` (CONFIG) must be set before `hlp_zed_compute`
  runs — the SM half-open interval semantics guarantee every
  up-move to step 7 passes through both. No other upstream
  dependency (the FEATURES/INDEXES/WMAPS/DESIGN_MTR outputs are
  NOT consumed by ZED).
- The worker recomputes on EVERY up-move (no cache file, no
  `is_allowed` switch — the uniform 7-kwargs cache_manager
  wiring is absent by design, the first deviation from the house
  pattern).
- `zed_checksum` is a pure data checksum (sha3_256 over
  `z.tobytes()`) with no sidecar (nothing to sidecar — no file);
  it is logged by the worker and stored on the context for the
  next level (GRADIENT) to consume.
