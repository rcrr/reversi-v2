# test_lm_worker_vld_positions.py — analysis

Date: 2026-09-02. File ADDED by the D-100 fix campaign
(session 28, T5, per Roberto's "T1 - T5: OK" — the bring-in
ede2efe shipped zero tests, the D-097 T5 pattern repeated).
1 class / 3 tests, **all DB-gated** (the setUp moves to
GENERATE, which runs the whole 11-level chain on a fresh base
dir, so a live regab DB is required — the SKIP_REGAB_DB gate
at the top of setUp, as in test_regab). The D-085 idiom
applied: CUSTOM_TMP_BASE via twolm.test.paths, setUpClass
mkdir, TemporaryDirectory created FIRST in setUp, defensive
tearDown, rlm_02.json fixture.

## TestLMWorkerVldPositions (3 tests)

setUp: gate first (L73-74), stdout patched to a StringIO
(log capture), rlm_02.json (the validation block {bid [8],
status CMS+CMR}), instance 1 → `move_to_step('GENERATE')`
(step 10) — the step BEFORE VLD_POSITIONS (step 11).

1. `test_compute_and_populate_cache` (L109-143): pre-state —
   all four vld fields None; `move_to_step('VLD_POSITIONS')`
   → step 11, worker name VLD_POSITIONS; the flat files
   `rlmwf_11_VLD_POSITIONS.dat` + `.SHA3-256` exist +
   `binio.verify_sha3_256_sidecar` True; the log carries
   "Executing heavy computation"; the rlm_02 validation
   golden pinned: `len(vld_positions) == 200`, the structured
   dtype names `("mover", "opponent")`, `vld_game_values`
   1-D with 200 entries, `vld_rds_checksum ==
   e8087903437d9d42d64499626f5b4426505d3b9538539e19fb8f45dc9c9f4c48`,
   `vld_pop_stats["count"] == 200`, `["mean"] == 3.64`.
2. `test_read_cache_on_new_instance` (L145-183): instance 1
   populates; a 2nd `LogisticModel` on the same base dir
   moves to GENERATE, the StringIO buffer is cleared, then to
   VLD_POSITIONS — "Cache successfully loaded and validated"
   present, "Executing heavy computation" ABSENT (no
   re-extraction), `nptest.assert_array_equal` on the
   positions + checksums equal.
3. `test_down_clears_vld_positions_attributes` (L185-200):
   up to VLD_POSITIONS (all four fields not None), then
   `move_to_step(10)` back to GENERATE — `_down` ran: all
   four fields None again (the D-100 M3 scope pin).

## Suite status

- **3/0/0 GREEN** (live DB, 8.5 s; run:
  `time python3 -m unittest twolm.test.test_lm_worker_vld_
  positions`).
- **3/0/3** under `SKIP_REGAB_DB=1` (all three tests
  skip-gated).
- Full discover with this file: 618 tests — 618/0/77 gated,
  618 run / 17 skipped ungated (23.6 s), −W error clean
  (23.8 s).

## Appendix: line-number reference (file 195 lines)

- header + run instructions: L28-42 (the SKIP_REGAB_DB note
  L38-39, the run command L41)
- imports: L44-58 (unittest/os/tempfile L44-46 · numpy +
  nptest L48-49 · mock + StringIO + Path L51-53 · binio /
  Verbosity / LogisticModel / paths L55-58)
- `TestLMWorkerVldPositions`: L61
- `setUpClass`: L65-67 (CUSTOM_TMP_BASE mkdir)
- `setUp`: L68-97 (the gate L72-74, the stdout patch
  L76-77, the FIRST TemporaryDirectory L81-82, rlm_02 L83,
  instance 1 L86-88, the pre-state asserts L90-92, the move
  to GENERATE L95-97)
- `tearDown`: L99-102
- the 3 tests: L105-139 / L141-175 / L177-191
- `__main__`: L194-195
