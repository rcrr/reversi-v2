# twolm/lm_worker_positions.py

Analysis date: 2026-08-30 — analysis session 22 (D-079); the
probe (scratch/verify_lm_worker_positions.py, 49 checks) was
started in the interrupted tail of session 21 and completed in
session 22.

The POSITIONS worker of the RLM pipeline — the FIRST domain worker
that consumes cache_manager. It loads (or computes from the regab
DB) the training data set through the 4-step load-or-compute
pipeline, then derives the positions / game_values arrays and the
training population stats, exposing them on the context for the
workers that follow. Roberto enabled it line-by-line in 601de87
(3rd active level: CREATED sentinel → CONFIG → POSITIONS) and copied
the related test from the original repo; the D-078 machine-level
prefix fix kept the cache files FLAT (rlmwf_02_POSITIONS.dat) —
the latent `rlmwf_/` subdirectory + no-mkdir trap never
materialized (probe B4, re-verified).

## Suite status (session 22, D-079)

- `test_lm_worker_positions`: 2/0/0 (Roberto's file, as-copied,
  green on first run)
- Full discover: 498 tests, 52 skipped under `SKIP_REGAB_DB=1`,
  GREEN. Note: both tests need the LIVE regab DB (see the test
  doc, T2).

## State per Roberto

Pipeline-in-progress, 3 active levels (CREATED → CONFIG →
POSITIONS). The next line-by-line step is
`lm_worker_features()` + restoring the last muted test
(`_test_move_to_step_by_string` in test_logistic_model.py).

## Architecture (179 lines)

- `lm_worker_positions() -> Worker` (L176-178): factory returning
  `Worker("POSITIONS", _up, _down)`. No `@validate_call` (M1).
- `_up` (L54-90):
  - INFO "Loading training game positions...".
  - `cache_manager_load_or_compute(...)` (L58-66) — the D-072
    standard flow, wired as:
    `cache_path  = ctx.get_cache_file_full_path_for_current_level()`
    (the injected machine closure — D-078 verbatim concatenation →
    flat `base_dir/rlmwf_02_POSITIONS.dat`),
    `is_allowed  = ctx.use_cache` (the CONFIG worker's switch,
    consumed here — F4),
    `load_fn     = regab_load_data_set_from_file` (bare function,
    `checksum=True` default — M4),
    `store_fn    = regab_store_data_set_to_file`,
    `validate_fn = lambda cached_rds: is_cache_consistent(ctx,
    cached_rds)`,
    `compute_fn  = lambda: load_from_db(ctx)`,
    `logger_fn   = ctx.log_event`.
  - Post-processing (unrelated to caching, L68-88):
    `rds.generate_positions_and_game_values()` →
    `ctx.positions` / `ctx.game_values`; `ctx.rds_checksum =
    rds_checksum` (the 3rd return element — the duck-typed DATA
    checksum); INFO logs (checksum, attributes-set); population
    stats via numpy over `game_values` → `ctx.training_pop_stats
    = {'count', 'mean', 'std_dev', 'variance'}`.
- `_down` (L93-100): INFO "Clearing training game positions,
  game_values and rds_checksum attributes." → the 4 context
  attributes (`positions`, `game_values`, `rds_checksum`,
  `training_pop_stats`) set to None.
- `is_cache_consistent(ctx, rds, *, bid=None, status=None) -> bool`
  (L103-152): PURE metadata compare — no DB, no file access.
  (1) connection tuple `(dbname, user, host, port)` — the cached
  side is `int(cache_conn.port)` (regab stores port as str, the
  schema as int; normalization pinned by D4g); (2) query tuple
  `(bid, status, ec)` — the keyword overrides win over the cfg.
  DEBUG log always prints the bool; the per-field mismatch detail
  is built only on inconsistency.
- `load_from_db(ctx, *, bid=None, status=None) -> RegabDataSet`
  (L154-173): `RegabDBConnection(dbname, user, host)` — the 3-arg
  call DROPS port + password (R1) → `regab_extract_data_set_from_
  db(rc, bid, status, ec)` → DEBUG "Extracted {n:,} positions
  from the database." → `finally: rc.close()` + close log.

## Verified facts (D-079 probe, 49 checks, 0 mismatches)

- V1 (B1): after `move_to_step("POSITIONS")` — step 2, worker
  "POSITIONS".
- V2 (B2): context populated — `positions` / `game_values` arrays,
  `rds_checksum` a 64-hex string.
- V3 (B3a/B3b): `training_pop_stats` keys + values match an
  INDEPENDENT numpy recompute over the loaded `game_values`
  (fixture bid 8, ec 20, CMS+CMR: count 200).
- V4 (B4/B5): FLAT cache files `rlmwf_02_POSITIONS.dat` +
  `rlmwf_02_POSITIONS.dat.SHA3-256`, no `rlmwf_/` subdirectory;
  the sidecar is in the binio `<hex>  <basename>` format (the
  D-072 standard — unlike the CONFIG worker's ad-hoc bare-hex
  sidecar, per the D-078 R1 ruling).
- V5 (B6): `rds_checksum` == an independent reload of the .dat's
  `rds.compute_sha3_256_hash()` (the duck-typed data checksum).
- V6 (B7): first run HITS the DB ("Extracted 200 positions from
  the database.").
- V7 (C1-C4): a SECOND instance on the same base_dir: cache hit —
  "Cache successfully loaded and validated", no "Extracted", no
  DB-connection log; positions arrays, rds_checksum and stats
  IDENTICAL across runs.
- V8 (D1a/D1b): `use_cache=False` → "Cache not allowed by
  configuration. Forcing computation." — and the cache file is
  STILL written (the D-071 R1 intentional behaviour, now visible
  in a domain worker).
- V9 (D2): corrupted .dat → "Checksum validation failed" +
  "Deleting cache and recomputing" + DB recompute; the file is
  recreated valid.
- V10 (D3/D3b): business inconsistency (cache warmed with ec 20,
  new cfg ec 10) → "Application data validation failed" + delete +
  recompute; the rewritten cache carries the NEW params (ec=10) —
  cache_manager step 4 (`validate_fn`) in action.
- V11 (D4a-D4g): `is_cache_consistent` unit behaviour — same cfg
  consistent; differing ec / bid / status / dbname inconsistent;
  the keyword overrides win; the str-port (regab) == int-port
  (schema) after the `int()` normalization.
- V12 (A1-A3): structure — `__all__ = [lm_worker_positions,
  load_from_db, is_cache_consistent]`; worker name "POSITIONS";
  `_down` resets the 4 attributes.
- V13 (F4): `is_allowed = ctx.use_cache` — the switch copied by
  the CONFIG worker is genuinely consumed here.

## Issues — OPEN (awaiting Roberto's call)

- **R1 (F1):** `load_from_db` builds
  `RegabDBConnection(dbname, user, host)` — DROPPING `port` and
  `password` although the schema has both
  (`RegabDBConnectionConfig.port: int = 5432`, `password:
  Optional[str]`). A non-default port in the config is silently
  ignored (the connection always opens on 5432); a configured
  password is silently ignored (regab's connection string carries
  `password=...` only when one is passed — L137-138).

## Minor notes — OPEN (awaiting Roberto's call)

- M1 (A4): no `@validate_call` on the public factory
  (lm_worker_config has it since D-078 M4 — house convention
  D-068 M11; Worker.__init__ is already gated, so this is a
  convention-only delta).
- M2 (A5): `from pathlib import Path` imported (L33) but unused.
- M3 (A6): trailing-whitespace lines (L73, L89, L92).
- M4 (F2): `load_fn` is the BARE `regab_load_data_set_from_file`
  with its `checksum=True` default — cache_manager's step 3
  already verified the file sidecar, and the load re-verifies the
  SAME sidecar: the file checksum is computed twice on every cache
  hit (redundant, harmless).
- Cross-ref note (F3): `regab_store_data_set_to_file`'s docstring
  promises it "calculates the SHA3-256 checksum", but it writes
  only the .dat — in this flow the sidecar is written by
  cache_manager (`write_sha3_256_sidecar`, D-072). The docstring
  is aspirational. Cross-reference on the CLOSED regab module —
  Roberto's call (regab-side doc fix, or leave).

## Integration notes

- The D-078 machine-level prefix fix is what makes this worker
  correct: the injected closure concatenates `rlmwf_` +
  `02_POSITIONS.dat` → flat file, no subdirectory to mkdir (V4).
  The "CROSSED OUT" trap noted in the NOTES inventory is hereby
  re-verified as gone.
- Pipeline ordering is load-bearing (as for the CONFIG worker,
  D-074 R1 note): `ctx.cfg` must be set before the
  `get_cache_file_*_for_current_level` closures are called, and
  `is_cache_consistent` reads `ctx.cfg.regab_data_set` — the SM
  half-open interval semantics guarantee CONFIG runs before
  POSITIONS on every up-move.
- `use_cache` lifecycle: CONFIG._up copies `cfg.use_cache` →
  context; CONFIG._down resets it to None; the only consumer in
  the pipeline so far is THIS worker (V13).
- `is_cache_consistent`'s keyword overrides (`bid=`, `status=`)
  are unused by the pipeline today (the validate_fn lambda calls
  it bare) — available for manual re-validation calls.

## Appendix — line reference

179 lines, as of 601de87.

- L28-46: imports (numpy L30, `pathlib.Path` L33 — M2, regab
  L36-42, cache_manager L43, TYPE_CHECKING RLMContext L45-46)
- L50: `__all__`
- L54-90: `_up` (cache call L58-66, post-processing L68-88)
- L93-100: `_down`
- L103-152: `is_cache_consistent`
- L154-173: `load_from_db` (R1 3-arg connection call L157)
- L176-178: `lm_worker_positions()` (M1 no @validate_call)
