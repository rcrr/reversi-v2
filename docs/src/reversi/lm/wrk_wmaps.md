# reversi/lm/wrk_wmaps.py
The WMAPS worker of the RLM pipeline — the 6th active level
(CREATED → CONFIG → POSITIONS → FEATURES → INDEXES → WMAPS),
enabled line-by-line by Roberto in 73b4342. Like POSITIONS and
INDEXES it is a CACHE-CONSUMING level: the 4-step load-or-compute
over the hlp_wmaps object — the THIRD cache_manager consumer in
the pipeline (the flat `rlmwf_05_WMAPS.dat` + binio sidecar DO
materialize).
> State: D-087 · ded27eb · 2026-08-31 · suite 3/0/0 (3 DB-gated)

## API

| name | contract |
|---|---|
| `wrk_wmaps()` | the factory — `@validate_call(config=ConfigDict(arbitrary_types_allowed=True))` returning `Worker("WMAPS", _up, _down)` |

## Architecture

- `_up`: INFO "Computing weight maps (WMAPS) for the feature
  set..." → `cache_manager_load_or_compute(...)` with the full
  7-kwargs wiring: `cache_path =
  ctx.get_cache_file_full_path_for_current_level()` (the injected
  machine closure — flat `rlmwf_05_WMAPS.dat`), `is_allowed =
  ctx.use_cache` (the CONFIG switch, the D-071 R1 semantics),
  `load_fn = lambda path: hlp_wmaps_load_from_file(path,
  checksum=False)` (the house shape — the sidecar was already
  verified by cache_manager), `store_fn = hlp_wmaps_store_to_file`,
  `validate_fn = lambda cached: hlp_wmaps_is_cache_consistent
  (ctx, cached)` (the 2-field metadata compare), `compute_fn =
  lambda: hlp_wmaps_compute(ctx)`, `logger_fn = ctx.log_event`.
  Then the 6 separate context attributes are populated
  (feature_w_ranges, iwmap_feature_offset, iwmap, wmap,
  wmap_fallback, w) + the INFO "Total weights (W)" line +
  `ctx.wmaps_obj_checksum = wmaps_obj_checksum` (the 7th
  attribute, the DATA checksum — the cache_manager 3rd return
  element).
- `_down`: INFO "Clearing WMAPS and W attributes..." → all 7
  attributes to None — the 6 arrays AND `ctx.wmaps_obj_checksum`
  (the house shape clears object + checksum).

## Verified invariants

Pinned by the `probes/verify_wmaps.py` B tier + the 3-test suite.

- Source shape: the 91-line file, `__all__ = ['wrk_wmaps']`,
  the factory name "WMAPS" WITH `@validate_call` + the pydantic
  import, the RLMContext import under TYPE_CHECKING (the
  circular-import guard), the full 7-kwargs cache wiring with the
  `checksum=False` load_fn, `_up` sets the 6 ctx arrays +
  `wmaps_obj_checksum` (7 attributes), `_down` clears all 7, 0
  non-comment trailing-whitespace lines — probe B1-B9.
- The level boundary (live DB, probe C tier): the flat file set is
  exactly CONFIG + POSITIONS + INDEXES + WMAPS (no
  `rlmwf_03_FEATURES*`); the cross-run cache hit + identical data;
  E9 — the per-feature wmap row count == `w_max − w_min + 1`
  (contiguous ranges).
- The end-to-end round-trip + the golden content (DB-gated):
  `test_compute_and_populate_cache` (step 5 pinned, the FLAT
  `rlmwf_05_WMAPS.dat` + `.SHA3-256` on disk, "Forcing
  computation", the 6 arrays non-None + `len(ctx.w) > 0`),
  `test_read_cache_on_new_instance` (the second instance moves to
  INDEXES first, then WMAPS: "Cache successfully loaded and
  validated", no "Forcing computation", the data identical), and
  `test_compute_wmaps_exact_values` (the rlm_01 golden — all 6
  arrays vs the test literals) — `test_wrk_wmaps.py` (3
  tests, `SKIP_REGAB_DB` gated).

## Open issues

None.

## Conventions

- The worker carries NO naming code — the flat
  `rlmwf_05_WMAPS.dat` comes from the injected full-path closure
  (the D-078 machine-level fix for ALL cache-consuming workers).
- `is_allowed = ctx.use_cache`: with `use_cache=False` the level
  always recomputes but still warms the cache file (the D-071 R1
  semantics).
- `validate_fn` is the 2-field metadata compare (no DB access, no
  recompute) — a business mismatch deletes + recomputes (the D-071
  R2 shape).
- The only worker that spreads ONE data object across separate
  context attributes (6 arrays + the checksum, as in INDEXES:
  object + checksum).

## Integration

- The 6th RLM level (the 6-worker list `[CREATED, CONFIG,
  POSITIONS, FEATURES, INDEXES, WMAPS]`); the facade
  (`logistic_model.py`) instantiates the machine + `Worker`.
- Consumes the `hlp_wmaps` module (all 5 public names) +
  `cache_manager`; publishes the 6 ctx arrays +
  `ctx.wmaps_obj_checksum` for the DESIGN_MTR level onward.
