# reversi/lm/wrk_vld_positions.py
The VLD_POSITIONS worker — the 12th active level (the 11th step). The
POSITIONS TWIN over the validation data set: the 6th `cache_manager`
consumer and the only worker that REUSES another level's data module —
`extract_and_prepare` + `is_cache_consistent` imported from
`wrk_positions` (L43), the keyword `bid`/`status` overrides
selecting the validation query. After the population stats,
the worker runs the validation-independence check — how many
validation records are ALSO present in the training set — LOG ONLY,
no action. The flat file is
`rlmwf_11_VLD_POSITIONS.dat` + `.SHA3-256`.

## API

| name | contract |
|---|---|
| `wrk_vld_positions()` | the factory — `@validate_call(config=ConfigDict(arbitrary_types_allowed=True))` returning `Worker("VLD_POSITIONS", _up, _down)` |

## Architecture

- `_up` (L54-114):
  - `vld_cfg = ctx.cfg.validation_data_set` (L57) —
    `ValidationDataSetConfig` declares ONLY `bid:
    List[NonNegativeInt]` + `status: List[StatusString]`. The
    M1 note (L59-62): the query INHERITS `ec` from
    `ctx.cfg.regab_data_set` (the training block) — the shared
    `ec` (20 in rlm_02) gates BOTH the extraction
    (wrk_positions L171) and the cache consistency check
    (L122 there); the validation block cannot override `ec`.
  - The uniform 7-kwargs `cache_manager_load_or_compute`
    (L65-73): `cache_path = ctx.get_cache_file_full_path_for_
    current_level()` (L66), `is_allowed = ctx.use_cache`,
    `load_fn = lambda path: regab_load_data_set_from_file(path,
    checksum=False)` (L68: the `checksum=True` default re-verified
    the sidecar cache_manager step 3 already checked), `store_fn =
    regab_store_data_set_to_file`, `validate_fn = lambda
    cached_vld_rds: is_cache_consistent(ctx, cached_vld_rds,
    bid=vld_cfg.bid, status=vld_cfg.status)` (L70 — the
    override is LOAD-BEARING: without it the TRAINING cfg
    params are used and the vld rds would always mismatch),
    `compute_fn = lambda: extract_and_prepare(ctx,
    bid=vld_cfg.bid, status=vld_cfg.status)` (L71 — the
    shared wrk_positions compute path, extract → dedup policy →
    log; the cache file stores the POST-policy data set, so a
    flag flip changes the stored content + the vld rds_checksum,
    cascading through the checksum lineage), `logger_fn =
    ctx.log_event`.
  - The cache-hit log (L75-80): on a hit the post-policy
    total is logged from the stored content ("Duplicate game
    positions (key: mover, opponent): [TOTAL: N] — data set
    loaded from cache (regab_allow_duplicate: …)"); on the
    compute path the full line is logged inside
    `extract_and_prepare` before the store.
  - Post-processing (L82-102): `vld_positions, vld_game_values
    = vld_rds.generate_positions_and_game_values()` (L83 — the
    board.py `Position` structured dtype, mover/opponent u64);
    the 3 rds-derived fields set (L84-86 — `vld_rds_checksum` is
    the duck-typed `RegabDataSet.compute_sha3_256_hash` over
    `df_mogv`); population stats logged (L91-95) + stored in
    `ctx.vld_pop_stats` (L97-102: count int + mean/std_dev/
    variance np.float64 over the int8 game values).
  - The validation-independence check (L104-112):
    `overlap = regab_count_position_overlap(ctx.positions,
    ctx.vld_positions)` — the number of vld records whose
    (mover, opponent) key is also in the training set (a pandas
    inner-merge over the two key columns; the train side is
    deduped first) — then one INFO log ("Validation
    independence check: [OVERLAP: X of N validation records],
    [PERCENT: P%] — … (log only, no action)"). LOG ONLY:
    NO raise, no threshold parameter, no
    quality gate (a max-overlap% / min-validation-size family
    is explicitly out of scope).
- `_down` (L117-124): clears ALL FOUR fields (L119-122) — the
  house shape, no gap.
- The factory (L127-130): `@validate_call`-gated with
  `arbitrary_types_allowed=True`.

## Verified invariants

Pinned by the 17-check `probes/verify_vld_positions.py` +
`test_wrk_vld_positions.py` (11 tests: 5 DB-gated + 6 DB-free).

- Source shape (probe A1-A8): the REUSED wrk_positions
  pair — A7 pins the import
  (`extract_and_prepare, is_cache_consistent`), A8 pins the
  vld `bid`/`status` overrides on BOTH the compute
  (`extract_and_prepare`) and the validate fns (D8 with the
  live-factory check D1, the reuse-identity pin now includes
  `extract_and_prepare.__module__`), the `_for_current_level`
  name, the `checksum=False` load_fn, the bid/status
  overrides, the factory gate, no numpy / Path / regab-extract
  imports, the 4-field `_down`.
- The context facts (probe B4/B5): the 4 pre-declared `vld_*`
  blackboard fields + the worker-list entry.
- The live rlm_02 invariants (probe C3a-C3d + C4 + the worker
  suite): bid [8] / status [CMS, CMR] / shared ec 20 → **200
  positions** (the (200,2) u64 structured array), int8 game
  values in [−58, 56]; `vld_pop_stats` count 200, mean
  `np.float64(3.64)`, std `np.float64(23.809880302093077)`,
  variance `np.float64(566.9104)`; `vld_rds_checksum` golden
  `e8087903437d9d42d64499626f5b4426505d3b9538539e19fb8f45dc9c9f4c48`;
  the vld checksum DIFFERS from the training rds checksum
  (`32da0ed3ff34c196d714ab1a5224206ece3792e05168e22005eb2d85758d55b3`);
  the 2nd instance on the same base dir: "Cache successfully
  loaded and validated" with NO "Executing heavy computation"
  (no re-extraction), identical positions + checksum; the cache
  gate compares (connection tuple, bid, status, shared ec) —
  a training-bid change does NOT invalidate the vld cache
  (independent data set), an `ec` change does.
- The independence trace (DB-gated, `TestVldIndependenceCheck`
  2 tests): rlm_02 (train bid 6,7 / vld bid 8 — disjoint) →
  "[OVERLAP: 0 of 200 validation records], [PERCENT: 0.00%]" +
  the chain continues; rlm_00 (train = vld = bid 8 — the
  deliberate mirror fixture) → "[OVERLAP: 200 of 200 …],
  [PERCENT: 100.00%]" + NO raise (the
  100%-overlapping vld is traced, the worker completes).
- The reused-override semantics (the DB-free
  TestIsCacheConsistentOverride class, 6 tests — probe D2-D7):
  full match → True; bid /
  status / ec / connection mismatch → False; NO override → the
  TRAINING cfg params are used → False (the worker must pass
  bid/status explicitly).

## Open issues

None.

## Conventions

- The unpacked `cache_hit` is now CONSUMED (the
  cache-hit duplicate line, L75-80) — the wrk_positions twin
  changed the same way.
- The `load_fn` `checksum=False`: the sidecar was verified by
  cache_manager step 3.
- The import-block trailing ws (L39) stays, as in
  wrk_positions.

## Integration

- Reuses `wrk_positions.extract_and_prepare` +
  `is_cache_consistent` — the twin relationship: same
  extraction machinery (and the same duplicate policy),
  different `bid`/`status` (validation bid [8] vs training bid
  [6,7] in rlm_02). The flat files are distinct:
  `rlmwf_03_POSITIONS.dat` (training) vs
  `rlmwf_11_VLD_POSITIONS.dat` (validation).
- The independence check reads `ctx.positions` (the
  training set, level 2) — the SM half-open interval semantics
  guarantee POSITIONS ran before VLD_POSITIONS on every up-move.
- Downstream: VALIDATE consumes `ctx.vld_positions` /
  `ctx.vld_game_values`; ANALYTICS consumes
  `ctx.vld_pop_stats`; the SM half-open interval semantics
  guarantee every up-move past step 11 passes through
  VLD_POSITIONS.
