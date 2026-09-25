# reversi/lm/hlp_zed.py
The ZED domain module of the LM pipeline: the `LMZed` data object (the z (N,) float32 vector — the affine image of the
per-position game values — + the two affine transformation closures `y2z` / `z2y`) + `zed_fun_factory` (the pure math) +
`hlp_zed_compute` + the duck-typed `compute_sha3_256_hash`. The data object of the 9th active level (CREATED sentinel →
CONFIG → FEATURES → SU_ANALYSIS → POSITIONS → INDEXES → ANOVA → WMAPS → DESIGN_MTR → ZED) and a non-cache level,
like CONFIG / FEATURES / ANOVA (no store / load / is_cache_consistent, no cache_manager wiring, no rlmwf_09*
file — see the worker doc).

## API

| name | contract |
|---|---|
| `LMZed` | plain class — 3 fields, assigned BY REFERENCE: `y2z` (int8 → float32), `z2y` (float32 → float32), `z: NDArray[float32]` |
| `zed_fun_factory(logit_clipping)` | `@validate_call` — returns the two affine closures |
| `hlp_zed_compute(ctx)` | builds the object from `ctx.game_values` + the clipping (NO `@validate_call` — see Conventions) |

## Architecture

- `LMZed.__init__` is `@validate_call(arbitrary_types_allowed)`; `compute_sha3_256_hash` (validated) = sha3_256 over
  `z.tobytes()` ONLY (the single data vector — the duck-typed data-checksum hook; the closures are NOT covered, see
  Conventions).
- `zed_fun_factory(logit_clipping)` (validated): `a = float32(0.5)`, `b = float32((1 − 2c)/128)`; `y_to_z(y)`: `y` cast
  to float32, `z = a + y·b` — maps the int8 range [−64, +64] onto [c, 1−c] (c = logit_clipping). `z_to_y(z)`: the EXACT
  inverse, `a1 = float32(−64/(1 − 2c))`, `b1 = float32(128/(1 − 2c))`, `y = a1 + z·b1`.
- `hlp_zed_compute`: NO `@validate_call` (the no-validation note — the hlp_indexes class). Body:
  `alpha = ctx.cfg.stat_model.logit_clipping`; `y2z, z2y = zed_fun_factory(alpha)`; `y = ctx.game_values`; `z = y2z(y)`;
  returns the object.
- NO store / load / is_cache_consistent functions — a non-cache level by design, like CONFIG / FEATURES / ANOVA
  (vectorized math, "very fast" per the worker comment; no rlmwf_09* file ever materializes).

## Verified invariants

Pinned by the 51-call `probes/verify_zed.py` + `test_hlp_zed.py` (10 tests, no DB) + `test_wrk_zed.py` (3 tests, 2
DB-gated).

- Source shape (probe A1-A12): 103 lines, the 3-name `__all__`, exactly 3 `@validate_call` (init, hash, factory — NOT
  compute, with the no-validation note), the affine constants pinned, the compute body, no cache API, 0 non-header
  trailing-whitespace lines.
- The worker file shape (probe B1-B8): 73 lines, the factory WITH `@validate_call` + the pydantic import, NO
  cache_manager import (the by-design comment pinned), `_up` sets the 4 ctx attributes, `_down` clears ALL FOUR,
  `Worker("ZED", ...)`.
- The live-DB golden re-derivation (probe D1/D5-D11): the pre-state (all 4 ctx attrs None); z == the independent float32
  recompute `0.5 + y·(1−2c)/128` (EXACT) == the float64 reference (allclose); `zed_checksum == sha3_256(z.tobytes())`;
  both closures callables; live endpoints `y2z(−64) ≈ c`, `y2z(0) == 0.5`, `y2z(64) ≈ 1−c`; live round-trip
  `z2y(y2z(y)) == float32(y)`; the base dir holds EXACTLY the 8 flat files (4 `.dat` + 4 sidecars) of the 4 cache levels
  reached (no rlmwf_09*).
- The cross-module facts (probe F1/F4/F5): LMContext's 4 zed fields pre-declared; the dedicated test exists (10 tests,
  no DB wiring); the mirror docs exist.
- The unit suite (10 tests, no DB): the factory math (both branches + 2-clippling endpoints), the mock compute (the
  exact (4,) golden + the hash identity), the init validation (2 ValidationError pins + by-reference).
- The live golden (DB-gated, `test_wrk_zed.py`): the (10,) y/z literals — the single source of truth.

## Open issues

None.

## Conventions

- The duck-typed hash covers `z` ONLY (informational): the closures are pure functions of
  `cfg.stat_model.logit_clipping` (not stored on the object). Same game_values + different clipping → different z →
  different hash, so no collision risk today; a future cache would need the clipping in the checksum.
- The flat-file numbering skips 09 (FEATURES skips 02): the 09/10/11 slots stay unused — GRADIENT and OPTIMIZE are
  non-cache levels (OPTIMIZE writes a config-named checkpoint instead); the next cache level is GENERATE (step 12).
- z's dtype contract is float32 (pinned in the worker test + 3× in the dedicated test): the values live in [c, 1−c] ⊂
  (0, 1); the float32 arithmetic is exact for the round-trip within the pinned allclose tolerances (1e-6/1e-7).
- No `@validate_call` on `hlp_zed_compute` — the TYPE_CHECKING circular-import constraint (the note).

## Integration

- Pipeline ordering: `ctx.game_values` (POSITIONS — the (N,) int8 vector, values in [−64, +64]) +
  `ctx.cfg.stat_model. logit_clipping` (CONFIG) must be set before `hlp_zed_compute` runs — the SM half-open interval
  semantics guarantee every up-move to step 9 passes through both. No other upstream dependency (the
  FEATURES/INDEXES/WMAPS/DESIGN_MTR outputs are NOT consumed by ZED).
- The worker recomputes on EVERY up-move (no cache file, no `is_allowed` switch — the uniform 7-kwargs cache_manager
  wiring is absent by design: ZED is a non-cache level, like CONFIG / FEATURES / ANOVA).
- `zed_checksum` is a pure data checksum (sha3_256 over `z.tobytes()`) with no sidecar (nothing to sidecar — no file);
  it is logged by the worker and stored on the context for the next level (GRADIENT) to consume.
