# reversi/lm/wrk_design_matrix.py
The DESIGN_MTR worker of the LM pipeline — the 8th active level (CREATED → CONFIG → FEATURES → SU_ANALYSIS → POSITIONS →
WMAPS → DESIGN_MTR). Like POSITIONS, INDEXES and WMAPS it is a CACHE-CONSUMING level: the 4-step load-or-compute over
the hlp_design_matrix object (the flat `rlmwf_08_DESIGN_MTR.dat` + binio sidecar + the duck-typed data checksum) — the
FIFTH cache_manager consumer in the pipeline; the flat files DO materialize (the DB test pins their existence).

## API

| name | contract |
|---|---|
| `wrk_design_matrix()` | the factory — `@validate_call(config=ConfigDict(arbitrary_types_allowed=True))` returning `Worker("DESIGN_MTR", _up, _down)` |

## Architecture

- `_up`: INFO "Computing Design Matrix (X)..." → `cache_manager_load_or_compute(...)` with the full 7-kwargs wiring:
  `cache_path = ctx.get_cache_file_full_path_for_current_level()` (the injected machine closure — flat
  `rlmwf_08_DESIGN_MTR.dat`), `is_allowed = ctx.use_cache` (the CONFIG switch),
  `load_fn = lambda path: hlp_design_matrix_load_from_file(path, checksum=False)` (the house shape — the sidecar was
  already verified by cache_manager), `store_fn = hlp_design_matrix_store_to_file`,
  `validate_fn = lambda cached_dm: hlp_design_matrix_is_cache_consistent(ctx, cached_dm)` (the 1-field metadata
  compare), `compute_fn = lambda: hlp_design_matrix_compute(ctx)`, `logger_fn = ctx.log_event`. Then
  `ctx.design_matrix = dm_obj.X` (the BARE ndarray, NOT the object) + the INFO "Design Matrix computed/loaded. Shape:.
  .." lines + `ctx. design_matrix_checksum = dm_checksum` (the 2nd attribute, the DATA checksum — the cache_manager 3rd
  return element).
- `_down`: INFO "Clearing Design Matrix attribute..." → BOTH attributes to None — `ctx.design_matrix` AND
  `ctx.design_matrix_checksum` (the house shape: object + checksum).

## Verified invariants

Pinned by the `probes/verify_design_matrix.py` B + C + D + F tiers + the 3-test suite.

- Source shape (probe B1-B9): the 80-line file, `__all__ = ['wrk_design_matrix']`, the factory name "DESIGN_MTR" WITH
  `@validate_call` + the pydantic import, the full 7-kwargs cache wiring with the `checksum=False` load_fn, `_up` sets
  `ctx.design_matrix` (the bare `dm_obj.X`) + `ctx.design_matrix_checksum`, `_down` clears both, 0 whitespace-only
  lines.
- The worker-test source shape (probe C1-C14): the gate in BOTH setUps + `import os`, the idiom (TemporaryDirectory ×2
  under CUSTOM_TMP_BASE, WORKSPACE_ROOT-anchored json ×2, the paths import, no `shutil`), all 3 `LogisticModel`
  constructions `Verbosity.HIGH`, the cache names pinned, the step pins 7 (×2) + 8 (×3).
- The level boundary + golden re-derivation (live DB, probe D5-D10 + F tier): after `move_to_step("DESIGN_MTR")` — step
  6; the base dir holds ONLY the flat CONFIG + POSITIONS + INDEXES + WMAPS + DESIGN_MTR `.dat` + `.SHA3-256` pairs (no
  `rlmwf_02_FEATURES*`); the cross-run cache hit + no recompute; X == the independent recompute
  `iwmap[pindexes + col_offsets]`, every value a valid w index (< W=21), per-feature columns within their iwmap regions,
  intercept column all 0, the DATA checksum identity.
- The end-to-end round-trip + the golden content (DB-gated): `test_compute_and_populate_cache` (step 8 pin, the FLAT
  `rlmwf_08_DESIGN_MTR.dat` + `.SHA3-256` on disk, "Forcing computation", `design_matrix` not None, shape == the
  principal-indexes shape, dtype uint32), `test_read_cache_on_new_instance` (the second instance to WMAPS, then
  DESIGN_MTR: "Cache successfully loaded and validated", no "Forcing computation", same shape + uint32), and
  `test_compute_design_matrix_exact_values` (the rlm_01 (10,7) uint32 X literal) — `test_wrk_design_matrix.py` (3 tests,
  `SKIP_REGAB_DB` gated).

## Open issues

None.

## Conventions

- The worker carries NO naming code — the flat `rlmwf_08_DESIGN_MTR.dat` comes from the injected full-path closure.
- `is_allowed = ctx.use_cache`: with `use_cache=False` the level always recomputes but still warms the cache file.
- `validate_fn` is the 1-field metadata compare (no DB access, no recompute) — a business mismatch deletes + recomputes.
- The blackboard gets the BARE ndarray (`dm_obj.X`), not the data object: the later level (ZED) consumes the array
  directly, and the hash method is duck-typed on the object only inside this level's store/load.

## Integration

- The 8th LM level (the 9-worker prefix
  `[CREATED, CONFIG, FEATURES, SU_ANALYSIS, POSITIONS, INDEXES, EFFECT_SIZE, WMAPS, DESIGN_MTR]`); the facade
  (`logistic_model.py`) instantiates the machine + `Worker`.
- Consumes the `hlp_design_matrix` module (all 5 public names) + `cache_manager`; publishes `ctx.design_matrix` (the
  (N,I) uint32 X) + `ctx.design_matrix_checksum` for the ZED level onward.
