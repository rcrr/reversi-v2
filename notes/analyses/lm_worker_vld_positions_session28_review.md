<!-- ARCHIVED — D-106 step 19 (the docs/ rewrite, 2026-09-04): the
     complete session-28 analysis (D-099) + the D-100
     fix-campaign narrative moved out of
     docs/src/twolm/lm_worker_vld_positions.md per docs_rules.md
     §1/§4. This is a frozen historical record: it is never
     updated. Stale-in-current-context notes: (1) the "31-check
     probe" figure — the current
     probes/verify_vld_positions.py (the 4091e72 move) has 17
     surviving check calls: A1-A8 (source shape: the REUSED
     lm_worker_positions pair, the R1 rename, the T3 checksum=
     False load_fn, the bid/status overrides, the factory gate,
     no numpy / no Path / no regab extract import, the 4-field
     _down), B4 + B5 (context facts), C3a-C3d + C4 (live-DB
     structural + cache-hit + _down invariants), D1 + D8 (the
     reused-override semantics, no DB). The D-106 step-3
     deletions/conversions: B1-B3 pipeline-state pins → the hub
     verify_logistic_model.py; C1 (bootstrap) + C2 (structural
     facts) + C5 (both flat files) + C6 (cache hit + no
     re-extraction) + C7 (_down scope) → test_lm_worker_vld_
     positions (class c); D2-D7 (the 6 override-semantic
     branches) → TestIsCacheConsistentOverride in the same file
     (class a §4 conversion — the suite grew 3 → 9 tests at
     14a0827). (2) the "618 tests / 77 skipped" full-discover
     figure predates steps 3-18 (current: 664/87 gated); (3)
     the D-099/D-100 campaign narrative (R1 the 2nd D-074 R1
     trap, T1-T5, M1-M3) is frozen history. -->

# lm_worker_vld_positions.py — analysis

Date: 2026-09-02. Module brought in by Roberto (ede2efe,
session 28 — the VLD_POSITIONS bring-in, 12th pipeline level:
the import L51 + worker-list entry L217 in logistic_model.py
uncommented; RLMContext's 4 `vld_*` fields pre-declared at
L146-149). **Analysis session 28 (D-099); fix campaign D-100
CLOSED (Roberto: "T1 - T5: OK, M1 - M3: OK, Procedi"): R1
RESOLVED (the one-line rename to
`get_cache_file_full_path_for_current_level()` — the 2nd
occurrence of the D-074 R1 trap, the 1st in lm_worker_generate
D-097 R1), T1 (factory `@validate_call` + pydantic import — all
11 worker factories now uniform), T2 (5 dead imports removed:
`Path`, `RegabDataSet`, `RegabDBConnection`,
`regab_extract_data_set_from_db`), T3 (load_fn `checksum=False`
lambda — the D-080 M4 shape), T4 (3 ws-only lines stripped —
the import-block trailing ws L38 stays, the D-078 M3 / D-080 M3
house scope, as in lm_worker_positions), T5 (test_lm_worker_
vld_positions.py ADDED — 1 class / 3 tests, all DB-gated),
M1 (the inherited-`ec` fact documented in the _up comment
L58-61), M2 (the unpacked `cache_hit` unused — the identical
lm_worker_positions L59 shape, keep, reported-only), M3
(positive — the `_down` scope clears all four fields, no gap,
contrast D-096 R4); 31-check probe re-pinned to the post-
campaign state, 0 mismatches.**

## Architecture

The **VLD_POSITIONS worker** (level 11, `rlmwf_11` cache slot)
is the **POSITIONS TWIN over the validation data set**. It is
the 6th `cache_manager` consumer and the only worker that
REUSES the data module of another level: `load_from_db` +
`is_cache_consistent` are imported from `lm_worker_positions`
(L42), not re-implemented — the keyword `bid`/`status`
overrides select the validation query.

`_up` (L53-96):

1. Reads `vld_cfg = ctx.cfg.validation_data_set` (L56) —
   `ValidationDataSetConfig` declares only `bid:
   List[NonNegativeInt]` + `status: List[StatusString]`.
   **M1 (D-100, documented L58-61):** the query inherits `ec`
   from `ctx.cfg.regab_data_set` (the training block) — the
   shared `ec` (20 in rlm_02) gates BOTH the extraction
   (`load_from_db` L171 of lm_worker_positions) and the cache
   consistency check (L122 there) — consistent across the two
   call sites, but the validation block cannot override `ec`.
2. The uniform 7-kwargs `cache_manager_load_or_compute` call
   (L64-72): `cache_path =
   ctx.get_cache_file_full_path_for_current_level()` (L65 —
   the D-074 house name post D-100 R1; the bring-in called the
   nonexistent `..._for_next_level()`, the 2nd occurrence of
   the D-074 R1 trap, empirically demonstrated: the rlm_02
   pipeline died at [11][VLD_POSITIONS] with the
   AttributeError; the alias simulation proved the level
   otherwise works end-to-end), `is_allowed = ctx.use_cache`,
   `load_fn = lambda path: regab_load_data_set_from_file(path,
   checksum=False)` (L67 — the D-080 M4 shape post D-100 T3:
   the raw function's `checksum=True` default re-verified the
   sidecar that cache_manager step 3 already checked),
   `store_fn = regab_store_data_set_to_file`,
   `validate_fn = lambda cached_vld_rds:
   is_cache_consistent(ctx, cached_vld_rds, bid=vld_cfg.bid,
   status=vld_cfg.status)` (L69 — the override is load-bearing:
   with no override the TRAINING cfg params are used and the
   vld rds would always mismatch), `compute_fn = lambda:
   load_from_db(ctx, bid=vld_cfg.bid, status=vld_cfg.status)`
   (L70), `logger_fn = ctx.log_event`.
3. Post-processing (L75-94): `vld_positions, vld_game_values =
   vld_rds.generate_positions_and_game_values()` (the board.py
   `Position` structured dtype, mover/opponent u64), the 4
   context fields set (L76-78: `vld_positions`,
   `vld_game_values`, `vld_rds_checksum` — the duck-typed
   `RegabDataSet.compute_sha3_256_hash` over `df_mogv`), the
   population stats logged + stored in `ctx.vld_pop_stats`
   (L89-94: count int + mean/std_dev/variance np.float64 over
   the int8 game values).

`_down` (L99-106): clears **all four** fields (L101-104) —
the house shape, no gap (M3, contrast D-096 R4: the OPTIMIZE
bring-in's `_down` missed `w_checksum` + `opt_info` pre-fix).

The factory (L109-112) is `@validate_call`-gated with
`arbitrary_types_allowed=True` (D-100 T1) — all 11 worker
factories now share the pattern (D-080 M4 / D-082 M1 / D-084
M1 / D-090 T2 / D-092 T2 / D-094 T2 / D-096 T10 / D-098 T3 /
D-100 T1).

## The flat cache file

`rlmwf_11_VLD_POSITIONS.dat` + `.SHA3-256` — the uniform
`{prefix}{level:02}_{worker_name}.dat` closure (D-078), step
11; the slot predicted in D-097/D-098 ("the next cache level
takes rlmwf_11"). Distinct from the training
`rlmwf_02_POSITIONS.dat` — two distinct data sets (training
bid [6,7] vs validation bid [8]), two distinct cache files,
two distinct checksums (rlm_02 live: training
`32da0ed3ff34c196d714ab1a5224206ece3792e05168e22005eb2d85758d55b3`
vs validation `e8087903437d9d42d64499626f5b4426505d3b9538539e19fb8f45dc9c9f4c48`).
The consistency gate compares (connection tuple, bid, status,
shared ec) — a training-bid change does NOT invalidate the vld
cache (correct: independent data set), but an `ec` change
does (correct: the vld extraction uses the shared ec).

## Verified invariants (live rlm_02 golden, D-099/D-100)

- Validation set: bid [8], status [CMS, CMR], shared ec 20 →
  **200 positions** (the (200,2) u64 structured array), int8
  game values in [−58, 56].
- `vld_pop_stats`: count 200, mean `np.float64(3.64)`, std
  `np.float64(23.809880302093077)`, variance
  `np.float64(566.9104)`.
- `vld_rds_checksum` golden
  `e8087903437d9d42d64499626f5b4426505d3b9538539e19fb8f45dc9c9f4c48`
  (the duck-typed `RegabDataSet.compute_sha3_256_hash` over
  `df_mogv`).
- 2nd instance on the same base dir: "Cache successfully
  loaded and validated" with NO "Executing heavy computation"
  (no re-extraction), identical positions + checksum.
- `_down` clears all four fields.
- The reused-override semantics (no DB): full match → True;
  bid / status / ec / connection mismatch → False; no override
  → the TRAINING cfg params are used → False (probe D tier).

## Suite status

- test_lm_worker_vld_positions.py: **3/0/0 GREEN** (live DB,
  8.5 s) — 3/0/3 gated (SKIP_REGAB_DB). See
  docs/src/twolm/test/test_lm_worker_vld_positions.md.
- Full discover: **618/0/77** gated (2.6 s) + 618 run / 17
  skipped ungated (23.6 s), −W error full discover clean
  (23.8 s), build/tmp clean — the baseline 599 → 615 → 618
  (the +3 are this suite's gated tests).

## Appendix: line-number reference (post D-100, file 112 lines)

- imports: L28-42 (numpy L30 · typing TYPE_CHECKING L32 ·
  pydantic L34 (D-100 T1) · state_machine L36 · regab L37-40
  (2 names post D-100 T2 — the import-block trailing ws L38
  stays, house scope) · cache_manager L41 · the REUSED
  lm_worker_positions pair L42 (D-099 design) · TYPE_CHECKING
  block L44-45)
- `__all__`: L49
- `_up`: L53-96 (the vld_cfg read L56, the M1 inherited-`ec`
  note L58-61, the 7-kwargs call L64-72 — R1 fixed L65, T3
  fixed L69-70, the post-processing L75-94, `vld_pop_stats`
  L89-94)
- `_down`: L99-106 (all four fields L101-104)
- `lm_worker_vld_positions`: L109-112 (`@validate_call` L109,
  D-100 T1)
