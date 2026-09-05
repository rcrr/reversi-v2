# twolm/test/test_lm_worker_validate.py
The VALIDATE worker integration suite — CREATED in the D-102 T5
campaign (the bring-in coverage gap closed per Roberto's
approved proposal: 1 class / 3 tests, all DB-gated, the D-085
idiom from day one), then EXTENDED at D-106 step 3: the probe
D1 + D3 were converted here (probe_rules.md §4) into the new
DB-free `TestValidateModelUnit` class — 2 classes / 5 tests
today.
> State: D-106 · 7964b96 · 2026-09-04 · suite 5/0/0 (3 DB-gated)

## Coverage

| class | tests | what it pins |
|---|---|---|
| `TestLMWorkerValidate` (setUp: the SKIP_REGAB_DB gate FIRST with the why-comment — the setUp moves through VLD_POSITIONS on a fresh base dir, so the live regab DB is required; the D-085 idiom (TemporaryDirectory FIRST under CUSTOM_TMP_BASE, the WORKSPACE_ROOT-anchored rlm_02.json); defensive tearDown) | 3 | `test_validate_model_goldens`: the first run to VALIDATE (step 12, worker name pinned) — the pre-state `vld_metrics is None`; the 7-key dict pinned EXACTLY (rlm_02 live, bid [8] validation vs the bid [6,7] training model — the goldens below); the 7 INFO log lines pinned ("Starting model validation...", "Computing indexes...", "Computing predictions (forward pass)...", "Validation completed. Loss (MSE/2): 7.00794393e-03", MSE 1.4016e-02, MAE 9.3113e-02, MAE(y) 12.16, RMSE(y) 15.46, RMSE/MAE 1.27). `test_second_instance_deterministic`: a 2nd instance on the same base dir moved to VALIDATE (the buffer-truncation idiom isolates the second run) — exactly 6 "Cache successfully loaded and validated" hits (the 6 cache_manager levels; CONFIG + the OPTIMIZE checkpoint have their own load flows; FEATURES / ZED / GRADIENT / VALIDATE have no cache file), NO "Extracted", NO "established successfully" (the DB is not touched), `vld_metrics` IDENTICAL to the first run (VALIDATE has no cache file to hit, so determinism is the pin). `test_down_clears_vld_metrics`: back to step 11 (VLD_POSITIONS, name pinned) `vld_metrics is None` (the single field `_up` sets, the house shape) |
| `TestValidateModelUnit` (DB-free; a `_fake_ctx` SimpleNamespace builder whose `y2z`/`z2y` lambdas mirror the zed factory — the float32 CAST before the affine, so the int8 `vld_game_values` never overflow) | 2 | `test_full_metric_math_on_hand_computed_case` (the D-106 step-3 conversion of probe D1): 1 feature / 2 instances, 2 positions — `vld_indexes [[0,1],[1,0]]` + `col_offsets [0,0]` → `dense_indices [[0,1],[1,0]]`; `w_dense [0.5, −0.5]` → `linear_predictor [0,0]` → `z_pred [0.5, 0.5]`; `y2z(y) = (y+64)/128`: game [0, 64] → `vld_z [0.5, 1.0]`; `rn_z [0, −0.5]` → norm 0.25, loss 0.0625, mse_z 0.125, mae_z 0.25; `z2y(z) = 128z−64`: `y_pred [0, 0]`, `rn_y [0, −64]` → mae_y 32.0, mse_y 2048.0, rmse_y sqrt(2048), samples 2 (every value EXACT). `test_rmse_mae_line_is_zero_guarded` (the D-106 step-3 conversion of probe D3): the M1 (D-102) branch — a perfect Y-space fit (game [0,0], `w_dense [0,0]` → mae_y 0.0, rmse_y 0.0) must log the "RMSE/MAE: n/a" line and NOT raise (pre-campaign: ZeroDivisionError in the `_up` log line); a REAL RLMContext (a bare SimpleNamespace is rejected by the `Worker.up` `@validate_call` gate, state_machine L87-90) |

## Goldens pinned

- The rlm_02 7-metric goldens: `vld_loss
  0.00700794393196702`, `vld_mse_z 0.01401588786393404`,
  `vld_mae_z 0.09311295300722122`, `vld_mae_y
  12.161691665649414`, `vld_mse_y 239.10484313964844`,
  `vld_rmse_y 15.46301555633545`, `vld_samples 200` (the
  float() casts make the values exact Python floats —
  deterministic pipeline; bid [8] validation vs the bid [6,7]
  training model).
- The hand-computed 2-position case (the TestValidateModelUnit
  derivation, also the probe D1 source).

## Conventions

- The setUp moves to VLD_POSITIONS (step 11) BEFORE the tests,
  so every worker test exercises the full 13-level chain
  end-to-end on the live DB (the test_lm_worker_zed pattern:
  setUp at the level before the one under test).
- The 2nd-instance test is the no-cache twin of the cache
  round-trip tests (test_lm_worker_positions et al.): where they
  pin "cache hit + no recompute", this one pins "recompute +
  identical result + 6 sibling cache hits".
- The TestValidateModelUnit class runs under SKIP_REGAB_DB=1
  (no DB) — the §4 conversion kept the unit facts testable
  without the live regab DB.

## Integration

- After the D-106 step-3 class c deletions this file owns the
  probe's former C1 (bootstrap step 12), C2 (the 7-key dict +
  exact goldens), C3 (the 5 log lines), C6 (2nd-instance
  determinism + the 6 cache hits) + C7 (the _down scope), plus
  the converted D1/D3 — the probe retains only C4 (the internal
  consistency invariants) + C5 (no rlmwf_12* file) for the
  live-DB tier.
