# test/reversi/lm/test_wrk_vld_positions.py
The VLD_POSITIONS worker integration suite — 4 classes / 15 tests: `TestLMWorkerVldPositions`, the DB-free
`TestIsCacheConsistentOverride` class (the probe's D2-D7 checks, probe_rules.md §4), the DB-gated
`TestVldIndependenceCheck` class, and the UNGATED `TestVldWorkerDbFree` class (the DB-free worker-level `_up` / `_down`
+ the independence-trace pins).

## Coverage

| class | tests | what it pins |
|---|---|---|
| `TestLMWorkerVldPositions` (setUp: the db_long_gate FIRST (the SKIP_REGAB_DB + LONG gates) — the setUp moves to GENERATE (step 12) on a fresh base dir, which runs the whole 13-level chain, so a live regab DB is required; the TemporaryDirectory-FIRST idiom (under CUSTOM_TMP_BASE, the WORKSPACE_ROOT-anchored rlm_02.json with the validation block {bid [8], status CMS+CMR}); defensive tearDown) | 3 | `test_compute_and_populate_cache`: pre-state — all four vld fields None; `move_to_step('VLD_POSITIONS')` → step 13, worker name VLD_POSITIONS; the flat files `rlmwf_13_VLD_POSITIONS.dat` + `.SHA3-256` exist + `binio.verify_sha3_256_sidecar` True; the log carries "Executing heavy computation"; the rlm_02 validation golden pinned: `len(vld_positions) == 200`, the structured dtype names `("mover", "opponent")`, `vld_game_values` 1-D with 200 entries, `vld_rds_checksum == e8087903437d9d42d64499626f5b4426505d3b9538539e19fb8f45dc9c9f4c48`, `vld_pop_stats["count"] == 200`, `["mean"] == 3.64`. `test_read_cache_on_new_instance`: instance 1 populates; a 2nd `LogisticModel` on the same base dir moves to GENERATE (the StringIO buffer cleared) then to VLD_POSITIONS — "Cache successfully loaded and validated" present, "Executing heavy computation" ABSENT (no re-extraction), `nptest.assert_array_equal` on the positions + checksums equal. `test_down_clears_vld_positions_attributes`: up to VLD_POSITIONS (all four fields not None), then `move_to_step(12)` back to GENERATE — `_down` ran: all four fields None again (the scope pin) |
| `TestIsCacheConsistentOverride` (DB-free — runs under SKIP_REGAB_DB=1; SimpleNamespace stand-ins for the context + the cached rds, rlm_02-shaped: training bid [6, 7] / ["CMR", "CMS"], validation bid [8] / ["CMS", "CMR"], shared ec 20, tst_regab @ localhost:5432) | 6 | `test_full_match_is_consistent`: the explicit bid/status override → True. `test_bid_mismatch_is_inconsistent`: a training-bid rds → False. `test_status_mismatch_is_inconsistent`: a partial status → False. `test_ec_mismatch_is_inconsistent`: the shared root `empty_count` is the gate (ec 22 rds → False). `test_connection_mismatch_is_inconsistent`: a different host → False. `test_no_override_uses_training_cfg`: NO override → the TRAINING cfg params are used (they differ from the vld rds → False) — the worker must pass bid/status explicitly |
| `TestVldIndependenceCheck` (`db_gate` gated — the D-532 default tier; `test_zero_overlap_is_traced` (1.7 s) self-gates
  on `tier_long()` FIRST in the method body; the `_machine(fixture)` helper builds a `LogisticModel` on the named fixture with a fresh tmp base dir and moves it to GENERATE (step 12) so the whole train chain populates `ctx.positions`; the test then moves one step to VLD_POSITIONS) | 2 | the validation-independence trace (LOG ONLY, no action). `test_zero_overlap_is_traced`: rlm_02 (train bid 6,7 / vld bid 8 — disjoint) → `len(vld_positions) == 200` + the "[OVERLAP: 0 of 200 validation records], [PERCENT: 0.00%]" log + NO raise. `test_full_overlap_is_traced_not_raised`: rlm_00 (train = vld = bid 8 — the deliberate mirror fixture) → `len(vld_positions) == 200` + the "[OVERLAP: 200 of 200 …], [PERCENT: 100.00%]" log + NO raise (the 100%-overlapping vld is traced, the worker completes) |
| `TestVldWorkerDbFree` (UNGATED — no DB, runs under SKIP_REGAB_DB=1; a REAL `LMContext` stand-in — `Worker.up` / `down` are `@validate_call`-gated — with the rlm_02-shaped cfg + the REAL cache flow against real files (`regab_store_data_set_to_file` / `regab_load_data_set_from_file`, pure file I/O); the compute path and the cache-hit shortcut are exercised with stubbed `wrk_positions_extract_and_prepare` / `cache_manager_load_or_compute`, so no DB is ever opened) | 4 | `test_read_cache_hit_db_free`: a pre-seeded cache (a REAL `RegabDataSet` stored via the real `regab_store_data_set_to_file`) is loaded + validated — "Cache successfully loaded and validated" present, "Executing heavy computation" ABSENT, the 10 synthetic rows land on `ctx.vld_positions` (array-equal to the rds's) and `vld_rds_checksum` is published (== the rds's sha3_256). `test_compute_path_db_free`: empty cache dir → the compute path runs with a STUBBED extract — the VLD-specific override `bid=[8]` / `status=["CMS", "CMR"]` is passed to the extract (not the training ones), the `rlmwf_13_VLD_POSITIONS.dat` + `.SHA3-256` sidecar land on disk and verify, the 50 rows + the population stats (`vld_pop_stats["count"] == 50`) are published, and the "Statistical properties of population for validation" line is logged. `test_down_clears_all_vld_attributes`: `down` (a real `LMContext`) clears all FOUR vld attributes (`vld_positions` / `vld_game_values` / `vld_rds_checksum` / `vld_pop_stats` → None) + the "Clearing validation game positions" line. `test_independence_trace_both_lines`: the independence trace DB-free, BOTH endpoints — the cache load stubbed to a HIT with a synthetic 10-record `RegabDataSet`, then `up()` run twice: disjoint training positions → the exact "[OVERLAP: 0 of 10 validation records], [PERCENT: 0.00%]" line, full overlap (training == vld) → the exact "[OVERLAP: 10 of 10 validation records], [PERCENT: 100.00%]" line (log only, no action). |

## Goldens pinned

- The rlm_02 validation set: 200 positions (the (200,2) u64 structured array), the checksum golden
  `e8087903437d9d42d64499626f5b4426505d3b9538539e19fb8f45dc9c9f4c48` (bid [8], status CMS+CMR, shared ec 20),
  `vld_pop_stats` count 200 / mean 3.64.
- The independence-trace line (the `test_independence_trace_both_lines` pin): the exact f-string in BOTH endpoints —
  "[OVERLAP: 0 of 10 validation records], [PERCENT: 0.00%]" (disjoint) and "[OVERLAP: 10 of 10 validation records],
  [PERCENT: 100.00%]" (full overlap), with the "records present in both … (log only, no action)" tail.

## Conventions

- The setUp moves to GENERATE (step 12) BEFORE the tests — the level BEFORE VLD_POSITIONS (step 12), the test_wrk_zed
  pattern; the full 13-level chain is exercised end-to-end on the live DB.
- The 2nd-instance test is the cache round-trip pin: "cache hit + no re-extraction + array-equal" — the mirror of the
  no-cache determinism pin in test_wrk_validate.
- The TestIsCacheConsistentOverride class keeps the 6 override-semantic branches testable without the live regab DB.
- The `TestVldWorkerDbFree` class keeps the worker-level `_up` / `_down` + the independence trace testable without the
  live regab DB: a REAL `LMContext` (the `Worker.up` `@validate_call` gate) + the real cache file I/O, with the extract
  / cache-load stubbed so no DB is opened.

## Integration

- This file owns the probe's C1 (bootstrap), C2 (structural facts), C5 (both flat files), C6 (cache hit + no
  re-extraction) + C7 (_down scope), plus the D2-D7 — the probe retains only C3a-C3d + C4 for the live-DB tier (the
  pop-stats re-derivation + the live goldens + the vld-vs-training checksum difference).
- The `TestVldWorkerDbFree` class is the no-DB unittest twin of C5 (both flat files) + C6 (cache hit + no re-extraction)
  + C7 (_down scope) + the independence trace — it covers them in the default tier over a real `LMContext` stand-in
  (the stubbed extract / cache-load keeps the DB out).
