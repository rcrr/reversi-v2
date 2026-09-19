# reversi/lm/wrk_indexes.py
The INDEXES worker of the LM pipeline — the 6th active level (CREATED → CONFIG → FEATURES → SU_ANALYSIS → POSITIONS →
INDEXES). Like POSITIONS it is a CACHE-CONSUMING level: the 4-step load-or-compute over the hlp_indexes object — the
SECOND cache_manager consumer in the pipeline (after POSITIONS), and unlike FEATURES the flat `rlmwf_05_INDEXES.dat` +
binio sidecar DO materialize.

## API

| name | contract |
|---|---|
| `wrk_indexes()` | the factory — `@validate_call(config=ConfigDict(arbitrary_types_allowed=True))` returning `Worker("INDEXES", _up, _down)` |

## Architecture

- `_up`: INFO "Computing indexes for the feature set..." → `cache_manager_load_or_compute(...)` with the full 7-kwargs
  wiring: `cache_path = ctx.get_cache_file_full_path_for_current_level()` (the injected machine closure — flat
  `rlmwf_05_INDEXES.dat`), `is_allowed = ctx.use_cache` (the CONFIG switch),
  `load_fn = lambda path: hlp_indexes_load_from_file(path, checksum=False)` (the sidecar was already verified by
  cache_manager, no redundant re-check), `store_fn = hlp_indexes_store_to_file`,
  `validate_fn = lambda cached: hlp_indexes_is_cache_consistent(ctx, cached)` (the 2-field metadata compare),
  `compute_fn = lambda: hlp_indexes_compute (ctx)`, `logger_fn = ctx.log_event`. Then the INFO "Model attribute
  hlp_indexes has been set." + `ctx.hlp_indexes = hlp_indexes` + the INFO checksum line +
  `ctx.hlp_indexes_checksum = hlp_indexes_checksum` (the cache_manager 3rd return element — the DATA checksum).
- `_down`: INFO "Clearing hlp_indexes..." → BOTH `ctx.hlp_indexes` and `ctx.hlp_indexes_checksum` set to None.

## Verified invariants

Pinned by the `probes/verify_hlp_indexes.py` D tier + the 2-test suite.

- Source shape: the 80-line file, `__all__ = ['wrk_indexes']`, the factory name "INDEXES" WITH `@validate_call`, the
  LMContext import under TYPE_CHECKING (the circular-import guard), the full 7-kwargs cache wiring with the
  `checksum=False` load_fn, the double-clear `_down`, 0 non-comment trailing-whitespace lines — probe D1-D6.
- The level boundary (live DB, probe C tier): the flat file set is exactly SU_ANALYSIS + POSITIONS + INDEXES (no
  `rlmwf_01_CONFIG*` — CONFIG writes nothing; no `rlmwf_02_FEATURES*`); the data-checksum identity; the sidecar is the
  flat `sha3_256sum` line (FILE checksum); the `(N, 16)` shape + independent recompute; the cross-run cache hit +
  identical object; the `_down` clearing of BOTH attributes.
- The end-to-end round-trip (DB-gated): `test_compute_and_populate_cache` (move to INDEXES = step 5 pinned, the FLAT
  `rlmwf_05_INDEXES.dat` + `.SHA3-256` on disk, "Executing heavy computation", non-None `hlp_indexes`) and
  `test_read_cache_on_new_instance` (the second instance: the "Cache successfully loaded and validated" + the NEGATIVE
  "Executing heavy computation" pin) — `test_wrk_indexes.py` (2 tests, `SKIP_REGAB_DB` gated).

## Open issues

None.

## Conventions

- The worker carries NO naming code — the flat `rlmwf_05_INDEXES.dat` comes from the injected full-path closure.
- `is_allowed = ctx.use_cache`: with `use_cache=False` the level always recomputes but still warms the cache file
  (visible as in POSITIONS).
- `validate_fn` is a returning validator (a business mismatch deletes + recomputes; this one returns False).
- Test artifacts: the WORKSPACE_ROOT / CUSTOM_TMP_BASE anchoring idiom; the DB tests sit behind the `SKIP_REGAB_DB`
  gate.

## Integration

- The 6th LM level (the 6-worker prefix `[CREATED, CONFIG, FEATURES, SU_ANALYSIS, POSITIONS, INDEXES]`); the facade
  (`logistic_model.py`) instantiates the machine + `Worker`.
- Consumes the `hlp_indexes` module (all 5 public names) + `cache_manager`; publishes `ctx.hlp_indexes` /
  `ctx.hlp_indexes_checksum` for the WMAPS level onward.
