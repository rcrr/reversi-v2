# reversi/test/test_wrk_vld_positions.py
The VLD_POSITIONS worker integration suite — ADDED by the D-100
T5 campaign (the bring-in ede2efe shipped zero tests, the
D-097 T5 pattern repeated; per Roberto's "T1 - T5: OK"), then
EXTENDED at D-106 step 3: the probe D2-D7 were converted here
(probe_rules.md §4) into the new DB-free
`TestIsCacheConsistentOverride` class — 2 classes / 9 tests
today.
> State: D-106 · 14a0827 · 2026-09-04 · suite 9/0/0 (3 DB-gated)

## Coverage

| class | tests | what it pins |
|---|---|---|
| `TestLMWorkerVldPositions` (setUp: the db_long_gate FIRST (L72-74, the SKIP_REGAB_DB + LONG gates, D-130) — the setUp moves to GENERATE (step 10) on a fresh base dir, which runs the whole 11-level chain, so a live regab DB is required; the D-085 idiom (TemporaryDirectory FIRST under CUSTOM_TMP_BASE, the WORKSPACE_ROOT-anchored rlm_02.json with the validation block {bid [8], status CMS+CMR}); defensive tearDown) | 3 | `test_compute_and_populate_cache`: pre-state — all four vld fields None; `move_to_step('VLD_POSITIONS')` → step 11, worker name VLD_POSITIONS; the flat files `rlmwf_11_VLD_POSITIONS.dat` + `.SHA3-256` exist + `binio.verify_sha3_256_sidecar` True; the log carries "Executing heavy computation"; the rlm_02 validation golden pinned: `len(vld_positions) == 200`, the structured dtype names `("mover", "opponent")`, `vld_game_values` 1-D with 200 entries, `vld_rds_checksum == e8087903437d9d42d64499626f5b4426505d3b9538539e19fb8f45dc9c9f4c48`, `vld_pop_stats["count"] == 200`, `["mean"] == 3.64`. `test_read_cache_on_new_instance`: instance 1 populates; a 2nd `LogisticModel` on the same base dir moves to GENERATE (the StringIO buffer cleared) then to VLD_POSITIONS — "Cache successfully loaded and validated" present, "Executing heavy computation" ABSENT (no re-extraction), `nptest.assert_array_equal` on the positions + checksums equal. `test_down_clears_vld_positions_attributes`: up to VLD_POSITIONS (all four fields not None), then `move_to_step(10)` back to GENERATE — `_down` ran: all four fields None again (the D-100 M3 scope pin) |
| `TestIsCacheConsistentOverride` (DB-free — runs under SKIP_REGAB_DB=1; SimpleNamespace stand-ins for the context + the cached rds, rlm_02-shaped: training bid [6, 7] / ["CMR", "CMS"], validation bid [8] / ["CMS", "CMR"], shared ec 20, tst_regab @ localhost:5432) | 6 | `test_full_match_is_consistent`: the explicit bid/status override → True. `test_bid_mismatch_is_inconsistent`: a training-bid rds → False. `test_status_mismatch_is_inconsistent`: a partial status → False. `test_ec_mismatch_is_inconsistent`: the shared `regab_data_set.ec` is the gate (ec 22 rds → False). `test_connection_mismatch_is_inconsistent`: a different host → False. `test_no_override_uses_training_cfg`: NO override → the TRAINING cfg params are used (they differ from the vld rds → False) — the worker must pass bid/status explicitly |

## Goldens pinned

- The rlm_02 validation set: 200 positions (the (200,2) u64
  structured array), the checksum golden
  `e8087903437d9d42d64499626f5b4426505d3b9538539e19fb8f45dc9c9f
  4c48` (bid [8], status CMS+CMR, shared ec 20), `vld_pop_stats`
  count 200 / mean 3.64.

## Conventions

- The setUp moves to GENERATE (step 10) BEFORE the tests — the
  level BEFORE VLD_POSITIONS (step 11), the test_wrk_zed
  pattern; the full 11-level chain is exercised end-to-end on
  the live DB.
- The 2nd-instance test is the cache round-trip pin: "cache hit
  + no re-extraction + array-equal" — the mirror of the no-
  cache determinism pin in test_wrk_validate.
- The TestIsCacheConsistentOverride class keeps the 6 override-
  semantic branches testable without the live regab DB (the §4
  conversion).

## Integration

- After the D-106 step-3 class c deletions this file owns the
  probe's former C1 (bootstrap), C2 (structural facts), C5
  (both flat files), C6 (cache hit + no re-extraction) + C7
  (_down scope), plus the converted D2-D7 — the probe retains
  only C3a-C3d + C4 for the live-DB tier (the pop-stats re-
  derivation + the live goldens + the vld-vs-training checksum
  difference).
