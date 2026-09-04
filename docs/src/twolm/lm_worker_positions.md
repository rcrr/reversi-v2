# twolm/lm_worker_positions.py
The POSITIONS worker of the RLM pipeline — the FIRST domain
worker that consumes cache_manager: the training data set comes
from the regab DB through the standard 4-step load-or-compute
flow, then positions / game_values arrays + the training
population stats are derived for the workers that follow.
> State: D-080 · cfb55fa · 2026-08-31 · suite 9/0/0 (2 DB-gated)

## API

| name | contract |
|---|---|
| `lm_worker_positions()` | the factory — `@validate_call` returning `Worker("POSITIONS", _up, _down)` |
| `load_from_db(ctx, *, bid=None, status=None)` | the compute half: extract the data set from the regab DB into a fresh `RegabDataSet` |
| `is_cache_consistent(ctx, rds, *, bid=None, status=None)` | the validate half: a PURE metadata compare (no DB, no file access) between the cached data set and the current config |

## Architecture- `_up`: INFO "Loading training game positions..." →
  `cache_manager_load_or_compute(...)` wired as:
  `cache_path = ctx.get_cache_file_full_path_for_current_level()`
  (the injected machine closure — the verbatim-prefix
  concatenation makes the file FLAT:
  `base_dir/rlmwf_02_POSITIONS.dat`), `is_allowed = ctx.use_cache`
  (the CONFIG worker's switch, consumed here), `load_fn =
  regab_load_data_set_from_file(path, checksum=False)` (the
  sidecar was already verified by cache_manager's step 3 — no
  redundant re-check), `store_fn = regab_store_data_set_to_file`,
  `validate_fn = is_cache_consistent`, `compute_fn = load_from_db`,
  `logger_fn = ctx.log_event`. Then the post-processing
  (unrelated to caching):
  `rds.generate_positions_and_game_values()` →
  `ctx.positions` / `ctx.game_values`; `ctx.rds_checksum` = the
  duck-typed DATA checksum (the 3rd return element); INFO logs;
  the population stats with numpy over `game_values` →
  `ctx.training_pop_stats = {'count', 'mean', 'std_dev',
  'variance'}`.
- `_down`: INFO "Clearing training game positions, game_values
  and rds_checksum attributes." → the 4 context attributes
  (`positions`, `game_values`, `rds_checksum`,
  `training_pop_stats`) set to None.
- `is_cache_consistent`: compares (1) the connection tuple
  `(dbname, user, host, port)` — the cached side is
  `int(cache_conn.port)` (regab stores the port as str, the
  schema as int; the normalization is load-bearing) and (2) the
  query tuple `(bid, status, ec)` — the `bid=`/`status=` keyword
  overrides win over the cfg. The DEBUG log always prints the
  bool; the per-field detail only on inconsistency.
- `load_from_db`: `RegabDBConnection(dbname, user, host,
  str(port), password)` — ALL five schema connection params (a
  configured port is no longer silently ignored, a configured
  password reaches the connection string) →
  `regab_extract_data_set_from_db(rc, bid, status, ec)` → DEBUG
  "Extracted {n:,} positions from the database." (the connection
  log includes the port, never the password) → `finally:
  rc.close()`.

## Verified invariants

Pinned by the 21-check probe + the 9-test suite (named per bullet).

- Source shape: the `__all__` trio, the factory name "POSITIONS",
  the factory `@validate_call`, the dead pathlib import gone, the
  whitespace lines clean, the `_down` 4-attribute reset — probe
  A1-A6. The D-080 pins: the 5-arg connection call, the
  `checksum=False` load, the corrected regab_store docstring,
  `use_cache` genuinely consumed — probe F1-F4.
- The loaded state: `positions`/`game_values`/`rds_checksum`
  populated, the stats keys + the values matching an INDEPENDENT
  numpy recompute, the sidecar in the binio `<hex>  <basename>`
  format, `rds_checksum` == the independent reload's
  `compute_sha3_256_hash()` — probe B2/B3a/B3b/B5/B6.
- The repeat run: data and stats IDENTICAL across two instances
  on the same base_dir — probe C3/C4.
- The failure paths: the corrupted `.dat` → checksum WARN +
  delete + recompute; the business-inconsistent cache (warmed
  ec=20, new cfg ec=10) → "Application data validation failed" +
  delete + recompute with the NEW params — probe D2/D3/D3b.
- The cross-module import pin: the `model_validator` import in
  rlm_config_schemas is now load-bearing (the c2>c1 validator) —
  probe E7.
- The end-to-end round-trip (DB-gated): the first instance hits
  the DB ("Extracted … positions from the database.") and writes
  the FLAT `rlmwf_02_POSITIONS.dat` + `.SHA3-256`; a second
  instance loads the cache ("Cache successfully loaded and
  validated", no "Extracted", no DB log) —
  `TestLMWorkerPositions` (2 tests, `SKIP_REGAB_DB` gated).
- The metadata compare unit semantics (in-memory, no DB, no
  cache file): same cfg → True; a differing ec / bid / status /
  dbname → False; the keyword override wins; the str-port (regab)
  vs int-port (schema) compares equal — `TestIsCacheConsistent`
  (7 tests).

## Open issues

None.

## Conventions

- The D-072 cache_manager standard flow — the reference consumer
  (binio sidecar, unlike CONFIG's ad-hoc bare-hex one, D-078 R1).
- Pipeline ordering is load-bearing: `ctx.cfg` must be set
  before the cache closures are called, and
  `is_cache_consistent` reads `ctx.cfg.regab_data_set` — the
  machine's half-open interval semantics guarantee CONFIG runs
  before POSITIONS on every up-move.
- The `is_cache_consistent` keyword overrides are unused by the
  pipeline today (the validate_fn calls it bare).
- Test artifacts: the D-065 idiom + the D-085 WORKSPACE_ROOT
  anchoring; the DB tests sit behind the `SKIP_REGAB_DB` gate.

## Integration

- The 3rd RLM level (CREATED sentinel → CONFIG → POSITIONS);
  the facade (`logistic_model.py`) instantiates the machine +
  `Worker`.
- Consumes `regab` (the extract/store/load trio),
  `cache_manager` (the 4-step flow) and the
  `rlm_config_schemas` types (`RegabDBConnection`,
  `RegabDataSet`); publishes `ctx.positions` /
  `ctx.game_values` / `ctx.rds_checksum` /
  `ctx.training_pop_stats` for the FEATURES level onward.
