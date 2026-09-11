# reversi/lm/wrk_positions.py
The POSITIONS worker of the LM pipeline — the FIRST domain
worker that consumes cache_manager: the training data set comes
from the regab DB through the standard 4-step load-or-compute
flow, then positions / game_values arrays + the training
population stats are derived for the workers that follow.
> State: D-157 · 2026-09-11 · suite 12/0/0 (5 DB-gated; the D-143
  regab_allow_duplicate policy tier)

## API

| name | contract |
|---|---|
| `wrk_positions()` | the factory — `@validate_call` returning `Worker("POSITIONS", _up, _down)` |
| `load_from_db(ctx, *, bid=None, status=None)` | the compute half: extract the data set from the regab DB into a fresh `RegabDataSet` |
| `extract_and_prepare(ctx, *, bid=None, status=None)` | D-143: the SHARED compute path used as `_up`'s `compute_fn` (and reused by VLD_POSITIONS) — `load_from_db` → `regab_dedup_mogv` per `ctx.cfg.regab_allow_duplicate` (True = keep every row and log the FOUND count; False = swap in the deduplicated frame and log the REMOVED count) → the post-policy `RegabDataSet`. The cache file stores the POST-policy data set, so a flag flip changes the stored content + the `rds_checksum`, cascading through the downstream checksum lineage (no format change) |
| `is_cache_consistent(ctx, rds, *, bid=None, status=None)` | the validate half: a PURE metadata compare (no DB, no file access) between the cached data set and the current config |

## Architecture- `_up`: INFO "Loading training game positions..." →
  `cache_manager_load_or_compute(...)` wired as:
  `cache_path = ctx.get_cache_file_full_path_for_current_level()`
  (the injected machine closure — the verbatim-prefix
  concatenation makes the file FLAT:
  `base_dir/rlmwf_03_POSITIONS.dat`), `is_allowed = ctx.use_cache`
  (the CONFIG worker's switch, consumed here), `load_fn =
  regab_load_data_set_from_file(path, checksum=False)` (the
  sidecar was already verified by cache_manager's step 3 — no
  redundant re-check), `store_fn = regab_store_data_set_to_file`,
  `validate_fn = is_cache_consistent`, `compute_fn =
  extract_and_prepare` (D-143 — the shared compute path, see API),
  `logger_fn = ctx.log_event`. On a CACHE HIT, the post-policy
  total is logged from the stored content ("Duplicate game positions
  (key: mover, opponent): [TOTAL: N] — data set loaded from cache
  (regab_allow_duplicate: …)"); on the COMPUTE path the full line
  ([TOTAL] + [FOUND]/[REMOVED] + [PERCENT]) is logged inside
  `extract_and_prepare` before the store. Then the post-processing
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
- `extract_and_prepare` (D-143): `load_from_db(ctx, bid=bid,
  status=status)` (so the VLD call site passes its own bid/status
  overrides) → `regab_dedup_mogv(rds.df_mogv)` → the
  `regab_allow_duplicate` branch (True: keep + "kept" log; False:
  `rds.df_mogv = deduped` + "removed" log) → returns the
  post-policy rds. The dedup is a single hash-based
  `drop_duplicates` pass (O(n), order-preserving — NO sort: a global
  sort would reorder EVERY row and perturb the goldens far beyond
  the removed rows); keep='first' is unambiguous because the
  extraction is `ORDER BY seq` and the duplicate rows carry identical
  attributes (the CMS/CMR double-recording structure, measured: 0
  multi-game_value / 0 multi-player duplicate groups).

## Verified invariants

Pinned by the 21-check probe + the 12-test suite (named per bullet).

- Source shape: the `__all__` quadruple (D-143: `extract_and_prepare`
  added), the factory name "POSITIONS",
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
  hlp_config_schemas is now load-bearing (the c2>c1 validator) —
  probe E7.
- The end-to-end round-trip (DB-gated): the first instance hits
  the DB ("Extracted … positions from the database.") and writes
  the FLAT `rlmwf_03_POSITIONS.dat` + `.SHA3-256` (D-157: slot
  03 — the file-less FEATURES takes 02); a second
  instance loads the cache ("Cache successfully loaded and
  validated", no "Extracted", no DB log) —
  `TestLMWorkerPositions` (2 tests, `SKIP_REGAB_DB` gated).
- The metadata compare unit semantics (in-memory, no DB, no
  cache file): same cfg → True; a differing ec / bid / status /
  dbname → False; the keyword override wins; the str-port (regab)
  vs int-port (schema) compares equal — `TestIsCacheConsistent`
  (7 tests).
- The D-143 duplicate policy (DB-gated, fixture bid 8: 200 records,
  11 duplicate keys, 189 distinct): `regab_allow_duplicate: false`
  → 189 positions + the "[TOTAL: 200], [REMOVED: 11], [PERCENT:
  5.50%] — removed" log; `true` → 200 positions + the "[FOUND: 11]
  — kept" log; and the cache file holds the POST-policy content (a
  flag-false file reloads 189 records + the cache-hit log line) —
  `TestLMWorkerPositionsDuplicates` (3 tests, `db_long_gate` gated).

## Open issues

None.

## Conventions

- The D-072 cache_manager standard flow — the reference consumer
  (binio sidecar, unlike CONFIG's ad-hoc bare-hex one, D-078 R1).
- Pipeline ordering is load-bearing: `ctx.cfg` must be set
  before the cache closures are called, and
  `is_cache_consistent` reads `ctx.cfg.regab_data_set` — the
  machine's half-open interval semantics guarantee CONFIG (and
  FEATURES, D-157) run before POSITIONS on every up-move.
- The `is_cache_consistent` keyword overrides: unused by the
  POSITIONS `validate_fn` (it calls bare), but load-bearing for the
  VLD level, which passes its own `bid=`/`status=` (the A8 pin).
- Test artifacts: the D-065 idiom + the D-085 WORKSPACE_ROOT
  anchoring; the DB tests sit behind the `SKIP_REGAB_DB` gate.

## Integration

- The 4th active level (CREATED sentinel → CONFIG → FEATURES →
  POSITIONS), step 3 (D-157: the I-012 transposition — the
  file-less FEATURES took step 2, this level's slot 02 → 03);
  the facade (`logistic_model.py`) instantiates the machine +
  `Worker`.
- Consumes `regab` (the extract/store/load trio),
  `cache_manager` (the 4-step flow) and the
  `hlp_config_schemas` types (`RegabDBConnection`,
  `RegabDataSet`); publishes `ctx.positions` /
  `ctx.game_values` / `ctx.rds_checksum` /
  `ctx.training_pop_stats` for the INDEXES level onward (D-157:
  FEATURES precedes POSITIONS).
- D-143: `extract_and_prepare` + `is_cache_consistent` are REUSED
  by the VLD level (`wrk_vld_positions`) — the vld compute path is
  this same function called with the vld `bid=`/`status=` overrides
  (the A7/D8 reuse-identity pins).
