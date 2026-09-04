<!-- ARCHIVED — D-106 step 9 (the docs/ rewrite, 2026-09-04): the
     complete session-22 analysis (D-079) + the D-080 fix-campaign
     narrative moved out of docs/src/twolm/lm_worker_positions.md
     per docs_rules.md §1/§4. This is a frozen historical record:
     it is never updated. Stale-in-current-context notes: (1) the
     "49 checks" (analysis) / "51 checks" (D-080 re-pin) probe
     figures predate D-106 step 3 — commit 585b2ad dropped the 7
     c groups and converted the D4/E sections to tests; the
     current probe is the 21-check probes/
     verify_lm_worker_positions.py (A1-A6, B2/B3a/B3b/B5/B6,
     C3/C4, D2/D3/D3b, E7, F1-F4); (2) "test_lm_worker_positions
     2/0/0" is pre step 3 — the D4a-g unit checks became
     TestIsCacheConsistent (7 tests, in-memory, no DB) and the
     E-section schema checks became test_rlm_config_schemas.py;
     the suite is now 9/0/0 (2 DB-gated); (3) the "498 tests /
     54 skipped" full-discover figure predates steps 3-8. -->

# twolm/lm_worker_positions.py

Analysis date: 2026-08-30 — analysis session 22 (D-079); the
probe (scratch/verify_lm_worker_positions.py, 49 checks) was
started in the interrupted tail of session 21 and completed in
session 22. Fix campaign D-080 applied 2026-08-30 (session 22,
Roberto: "correggile tutte").

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

- `test_lm_worker_positions`: 2/0/0 (Roberto's file; D-080
  applied T1-T4 — the D-065 idiom, the SKIP_REGAB_DB gate, the
  dead blocks removed, header grammar; both tests DB-gated, run
  with the live DB)
- Full discover: 498 tests, 54 skipped under `SKIP_REGAB_DB=1`
  (17 PERF + 35 regab + 2 positions), GREEN; ungated (live DB):
  498 run, 17 skipped, GREEN.

## State per Roberto

Pipeline-in-progress, 3 active levels (CREATED → CONFIG →
POSITIONS). D-080 (Roberto: "tutte le tue considerazioni sono
corrette. Correggile tutte"): R1 + M1-M4 + the cross-ref note
all FIXED — module CLOSED. The next line-by-line step is
`lm_worker_features()` + restoring the last muted test
(`_test_move_to_step_by_string` in test_logistic_model.py).

## Architecture (179 lines)

- `lm_worker_positions() -> Worker` (L180-182): factory returning
  `Worker("POSITIONS", _up, _down)`; D-080 M1: now
  `@validate_call(config=ConfigDict(arbitrary_types_allowed=True))`
  (L179, the D-068 M11 / D-078 M4 pattern).
- `_up` (L54-90):
  - INFO "Loading training game positions...".
  - `cache_manager_load_or_compute(...)` (L58-66) — the D-072
    standard flow, wired as:
    `cache_path  = ctx.get_cache_file_full_path_for_current_level()`
    (the injected machine closure — D-078 verbatim concatenation →
    flat `base_dir/rlmwf_02_POSITIONS.dat`),
    `is_allowed  = ctx.use_cache` (the CONFIG worker's switch,
    consumed here — F4),
    `load_fn     = lambda path: regab_load_data_set_from_file(
    path, checksum=False)` (D-080 M4 — the sidecar was already
    verified by cache_manager's step 3),
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
  (L155-176): D-080 R1 — `RegabDBConnection(dbname, user, host,
  str(conn_params.port), conn_params.password)` (the 5-arg call
  passes ALL the schema's connection params — the old 3-arg call
  dropped port + password) → `regab_extract_data_set_from_db(rc,
  bid, status, ec)` → DEBUG "Extracted {n:,} positions from the
  database." (the connection log now includes the port, never
  the password) → `finally: rc.close()` + close log.

## Verified facts (D-079 probe, re-pinned D-080 — 51 checks, 0 mismatches)

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

## Issues — resolved (D-080)

- **R1 — FIXED (D-080).** `load_from_db` now passes ALL the
  schema's connection params — `RegabDBConnection(dbname, user,
  host, str(conn_params.port), conn_params.password)` — so a
  non-default configured port is no longer silently ignored and
  a configured password reaches the connection string (regab
  carries `password=...` when one is passed). The DEBUG
  connection log now includes the port (never the password). The
  fixture (no port/password set) connects exactly as before
  (default 5432, no password). Re-pinned by probe F1.

## Minor notes — resolved (D-080)

- M1 (A4): FIXED — `@validate_call(config=ConfigDict
  (arbitrary_types_allowed=True))` on the public factory (the
  D-068 M11 / D-078 M4 pattern; Worker.__init__ is already gated
  behind it).
- M2 (A5): FIXED — the dead `from pathlib import Path` removed.
- M3 (A6): FIXED — the D-079-flagged trailing-whitespace lines
  (L73/L89/L92 at analysis) cleaned. Scope as in D-078 M3: the
  remaining original-file trailing whitespace (license header,
  import block, is_cache_consistent body) stays, as in
  lm_worker_config post-campaign.
- M4 (F2): FIXED — `load_fn` now passes `checksum=False` (a
  lambda), so the load does not re-verify the sidecar that
  cache_manager's step 3 already checked (the redundant double
  file-checksum on every cache hit is gone).
- Cross-ref note (F3): RESOLVED — the
  `regab_store_data_set_to_file` docstring no longer promises the
  checksum calculation (in the pipeline flow cache_manager writes
  the sidecar, D-072); docs/src/twolm/regab.md's API-table row
  corrected in the same batch. Re-pinned by probe F3.

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

183 lines, as of D-080.

- L28-47: imports (numpy L30, pydantic L34 [M1], regab L37-43,
  cache_manager L44, TYPE_CHECKING RLMContext L46-47)
- L51: `__all__`
- L55-91: `_up` (cache call L59-67, post-processing L69-89)
- L94-101: `_down`
- L104-153: `is_cache_consistent`
- L155-176: `load_from_db` (R1 5-arg connection call L158-160)
- L179-182: `lm_worker_positions()` (M1 @validate_call L179)
