# twolm/lm_worker_indexes.py
The INDEXES worker of the RLM pipeline — the 5th active level
(CREATED → CONFIG → POSITIONS → FEATURES → INDEXES), enabled
line-by-line by Roberto in a323e0f. Like POSITIONS it is a
CACHE-CONSUMING level: the 4-step load-or-compute over the
rlm_indexes object — the SECOND cache_manager consumer in the
pipeline (after POSITIONS), and unlike FEATURES the flat
`rlmwf_04_INDEXES.dat` + binio sidecar DO materialize.
> State: D-084 · 297e531 · 2026-08-31 · suite 2/0/0 (2 DB-gated)

## API

| name | contract |
|---|---|
| `lm_worker_indexes()` | the factory — `@validate_call(config=ConfigDict(arbitrary_types_allowed=True))` returning `Worker("INDEXES", _up, _down)` |

## Architecture

- `_up`: INFO "Computing indexes for the feature set..." →
  `cache_manager_load_or_compute(...)` with the full 7-kwargs
  wiring: `cache_path =
  ctx.get_cache_file_full_path_for_current_level()` (the injected
  machine closure — flat `rlmwf_04_INDEXES.dat`), `is_allowed =
  ctx.use_cache` (the CONFIG switch, the D-071 R1 semantics),
  `load_fn = lambda path: rlm_indexes_load_from_file(path,
  checksum=False)` (the D-084 M3 shape — the sidecar was already
  verified by cache_manager, no redundant re-check), `store_fn =
  rlm_indexes_store_to_file`, `validate_fn = lambda cached:
  rlm_indexes_is_cache_consistent(ctx, cached)` (the 2-field
  metadata compare), `compute_fn = lambda: rlm_indexes_compute
  (ctx)`, `logger_fn = ctx.log_event`. Then the INFO "Model
  attribute rlm_indexes has been set." + `ctx.rlm_indexes =
  rlm_indexes` + the INFO checksum line + `ctx.rlm_indexes_
  checksum = rlm_indexes_checksum` (the cache_manager 3rd return
  element — the DATA checksum).
- `_down`: INFO "Clearing rlm_indexes..." → BOTH
  `ctx.rlm_indexes` and `ctx.rlm_indexes_checksum` set to None.

## Verified invariants

Pinned by the `probes/verify_rlm_indexes.py` D tier + the 2-test
suite.

- Source shape: the 80-line file, `__all__ =
  ['lm_worker_indexes']`, the factory name "INDEXES" WITH
  `@validate_call` (the D-084 M1 house convention), the RLMContext
  import under TYPE_CHECKING (the circular-import guard), the full
  7-kwargs cache wiring with the `checksum=False` load_fn, the
  double-clear `_down`, 0 non-comment trailing-whitespace lines —
  probe D1-D6.
- The level boundary (live DB, probe C tier): the flat file set
  is exactly CONFIG + POSITIONS + INDEXES (no `rlmwf_03_FEATURES*`
  — the pure-compute level writes nothing); the data-checksum
  identity; the sidecar is the flat `sha3_256sum` line (FILE
  checksum); the `(N, 16)` shape + independent recompute; the
  cross-run cache hit + identical object; the `_down` clearing of
  BOTH attributes.
- The end-to-end round-trip (DB-gated): `test_compute_and_
  populate_cache` (move to INDEXES = step 4 pinned, the FLAT
  `rlmwf_04_INDEXES.dat` + `.SHA3-256` on disk, "Executing heavy
  computation", non-None `rlm_indexes`) and `test_read_cache_on_
  new_instance` (the second instance: the "Cache successfully
  loaded and validated" + the NEGATIVE "Executing heavy
  computation" pin) — `test_lm_worker_indexes.py` (2 tests,
  `SKIP_REGAB_DB` gated).

## Open issues

None.

## Conventions

- The worker carries NO naming code — the flat
  `rlmwf_04_INDEXES.dat` comes from the injected full-path
  closure (the D-078 machine-level fix for ALL cache-consuming
  workers).
- `is_allowed = ctx.use_cache`: with `use_cache=False` the level
  always recomputes but still warms the cache file (the D-071 R1
  semantics, visible as in POSITIONS).
- `validate_fn` is a returning validator (a business mismatch
  deletes + recomputes; this one returns False — the D-071 R2
  shape).
- Test artifacts: the D-065 idiom + the D-085 WORKSPACE_ROOT /
  CUSTOM_TMP_BASE anchoring; the DB tests sit behind the
  `SKIP_REGAB_DB` gate.

## Integration

- The 5th RLM level (the 5-worker list `[CREATED, CONFIG,
  POSITIONS, FEATURES, INDEXES]`); the facade
  (`logistic_model.py`) instantiates the machine + `Worker`.
- Consumes the `rlm_indexes` module (all 5 public names) +
  `cache_manager`; publishes `ctx.rlm_indexes` /
  `ctx.rlm_indexes_checksum` for the WMAPS level onward.
