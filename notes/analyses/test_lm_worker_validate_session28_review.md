<!-- ARCHIVED — D-106 step 18 (the docs/ rewrite, 2026-09-04): the
     complete D-102 T5 session-28 narrative moved out of
     docs/src/twolm/test/test_lm_worker_validate.md per
     docs_rules.md §1/§4. This is a frozen historical record:
     it is never updated. Stale-in-current-context notes: (1)
     the "28 checks" probe figure — see the sibling
     rlm_validate_session28_review.md header (C1/C2/C3/C6/C7
     were deleted at D-106 step 3 class c because this file
     pins them); (2) the file grew 179 → 258 lines at D-106
     step 3 (7964b96): the probe D1 + D3 were CONVERTED here
     into the new TestValidateModelUnit class (2 DB-free tests:
     the hand-computed 2-position metric math + the M1 zero-
     guard branch) — the "3 tests" figure is now 5; (3) the
     "622 tests / 80 skipped" full-discover figure predates
     steps 3-17 (current: 664/87 gated); (4) the D-102 T5
     "close the bring-in coverage gap" narrative is frozen
     history. -->

# twolm/test/test_lm_worker_validate.py

Created: 2026-09-02 (session 28, D-102 T5 — the dedicated worker
suite closing the bring-in coverage gap, per Roberto's approved
proposal: 1 class / 3 tests, all DB-gated, the D-085 idiom).

The VALIDATE worker integration suite: 1 class (`TestLMWorkerValidate`)
/ 3 tests / no PERF, ALL DB-gated (the setUp moves through
VLD_POSITIONS on a fresh base dir — the live regab DB is required).
The D-085 idiom from day one: TemporaryDirectory under the shared
`CUSTOM_TMP_BASE` created first, `WORKSPACE_ROOT`-anchored json
(rlm_02.json), defensive tearDown, the `twolm.test.paths` import.
Header grammar per house style (the SKIP_REGAB_DB note is true:
under the gate 3/0/3).

## Suite status (session 28, post D-102)

- 3/0/0 live (30.6 s full-discover context); under `SKIP_REGAB_DB=1`
  the 3 tests skip — 3/0/3 gated.
- Green on first run; no fixes needed.

## Tests

- `test_validate_model_goldens` — the first run to VALIDATE (step
  12, worker name pinned): the pre-state `vld_metrics is None`; the
  7-key dict pinned EXACTLY (rlm_02 live, bid [8] validation vs the
  bid [6,7] training model): `vld_loss 0.00700794393196702`,
  `vld_mse_z 0.01401588786393404`, `vld_mae_z
  0.09311295300722122`, `vld_mae_y 12.161691665649414`,
  `vld_mse_y 239.10484313964844`, `vld_rmse_y
  15.46301555633545`, `vld_samples 200` (the float() casts make the
  values exact Python floats — deterministic pipeline); the 7 INFO
  log lines pinned (the "Starting model validation..." / "Computing
  indexes..." / "Computing predictions (forward pass)..." /
  "Validation completed. Loss (MSE/2): 7.00794393e-03" / MSE
  1.4016e-02 / MAE 9.3113e-02 / MAE(y) 12.16 / RMSE(y) 15.46 /
  RMSE/MAE 1.27). Goldens re-derived independently by
  scratch/verify_validate.py tier C (0 mismatches).
- `test_second_instance_deterministic` — a second LogisticModel on
  the same base dir moved to VALIDATE: the buffer-truncation idiom
  (test_lm_worker_positions) isolates the second run; exactly 6
  "Cache successfully loaded and validated" hits (the 6
  cache_manager levels — CONFIG and the OPTIMIZE checkpoint have
  their own load flows; FEATURES / ZED / GRADIENT / VALIDATE have no
  cache file); NO "Extracted", NO "established successfully" (the DB
  is not touched); `vld_metrics` IDENTICAL to the first run (the
  VALIDATE recompute is deterministic — it has no cache file to hit,
  so determinism is the pin, probe C6).
- `test_down_clears_vld_metrics` — the `_down` scope: back to step
  11 (VLD_POSITIONS, name pinned) `vld_metrics is None` (the single
  field `_up` sets, the house shape).

## Integration notes

- The setUp moves to VLD_POSITIONS (step 11) BEFORE the tests, so
  every test exercises the full 13-level chain end-to-end on the
  live DB (the test_lm_worker_zed pattern: setUp at the level before
  the one under test).
- The second-instance test is the no-cache twin of the cache
  round-trip tests (test_lm_worker_positions et al.): where they pin
  "cache hit + no recompute", this one pins "recompute + identical
  result + 6 sibling cache hits".
