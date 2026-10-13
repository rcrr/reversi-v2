# test/reversi/lm/test_wrk_validate.py
The VALIDATE worker integration suite — 4 classes / 12 tests: the DB-gated `TestLMWorkerValidate` (3 tests, live regab
DB) + the DB-free `TestValidateModelUnit` (7 tests: the unit metric math, the f64 series, the outlier kernel, the
outlier report, the full `_up` log contract) + the two UNGATED small classes (`TestValidateSecondInstanceSmall` +
`TestValidateDownScope`, 1 test each).

## Coverage

| class | tests | what it pins |
|---|---|---|
| `TestLMWorkerValidate` (setUp: the db_long_gate FIRST (the SKIP_REGAB_DB + LONG gates) with the why-comment — the setUp moves through VLD_POSITIONS on a fresh base dir, so the live regab DB is required; the idiom (TemporaryDirectory FIRST under CUSTOM_TMP_BASE, the WORKSPACE_ROOT-anchored rlm_02.json); defensive tearDown) | 3 | `test_hlp_validate_model_goldens`: the first run to VALIDATE (step 14, worker name pinned) — the pre-state `vld_metrics is None`; the 7-key dict pinned (the six float metrics via assert_close; vld_samples exact — rlm_02 live, bid [8] validation vs the bid [6,7] training model — the goldens below); the 9 INFO log lines pinned ("Starting model validation...", "Computing indexes...", "Computing predictions (forward pass)...", "Validation completed. Loss (MSE/2): 7.00794393e-03", MSE 1.4016e-02, MAE 9.3113e-02, MAE(y) 12.16, RMSE(y) 15.46, RMSE/MAE 1.27). `test_second_instance_deterministic`: a 2nd instance on the same base dir moved to VALIDATE (the buffer-truncation idiom isolates the second run) — exactly 6 "Cache successfully loaded and validated" hits (the 6 cache_manager levels; CONFIG + the OPTIMIZE checkpoint have their own load flows; FEATURES / ZED / GRADIENT / VALIDATE have no cache file), NO "Extracted", NO "established successfully" (the DB is not touched), `vld_metrics` IDENTICAL to the first run (VALIDATE has no cache file to hit, so determinism is the pin). `test_down_clears_vld_metrics`: back to step 13 (VLD_POSITIONS, name pinned) `vld_metrics` is None again (the test pins that field only — the `_down` clears all four published fields) |
| `TestValidateModelUnit` (DB-free; a `_fake_ctx` SimpleNamespace builder whose `y2z`/`z2y` lambdas mirror the zed factory — the float32 CAST before the affine, so the int8 `vld_game_values` never overflow) | 7 | `test_full_metric_math_on_hand_computed_case` (the probe D1 check): 1 feature / 2 instances, 2 positions — `vld_indexes [[0,1],[1,0]]` + `col_offsets [0,0]` → `dense_indices [[0,1],[1,0]]`; `w_dense [0.5, −0.5]` → `linear_predictor [0,0]` → `z_pred [0.5, 0.5]`; `y2z(y) = (y+64)/128`: game [0, 64] → `vld_z [0.5, 1.0]`; `rn_z [0, −0.5]` → norm 0.25, loss 0.0625, mse_z 0.125, mae_z 0.25; `z2y(z) = 128z−64`: `y_pred [0, 0]`, `rn_y [0, −64]` → mae_y 32.0, mse_y 2048.0, rmse_y sqrt(2048), samples 2 (every value EXACT). `test_rmse_mae_line_is_zero_guarded` (the probe D3 check): the zero-guard branch — a perfect Y-space fit (game [0,0], `w_dense [0,0]` → mae_y 0.0, rmse_y 0.0) must log the "RMSE/MAE: n/a" line and NOT raise; a REAL LMContext (a bare SimpleNamespace is rejected by the `Worker.up` `@validate_call` gate, state_machine); `test_validation_result_carries_the_f64_series` (the `LMValidate`: the 7 metrics + the f64 `y_pred` / `rn_y` series); `test_hlp_validate_top_outliers_ranking_and_ties` + `test_hlp_validate_top_outliers_default_is_twenty` (the `hlp_validate_top_outliers` kernel: the stable argsort, the tie order, the default 20); `test_up_outlier_report` (the top-20 extreme-outlier report — the header + exactly 20 "vld position" lines in descending \|residual\| order, the 20 records published in `ctx.vld_outliers` in the same order). `test_up_publishes_metrics_and_full_log_contract` (the full `wrk_validate().up` contract on ~50 synthetic positions — a REAL `LMContext`, `Worker.up` is `@validate_call`-gated; 1 feature / 2 instances / 2 configurations, the raw indexes index `w_dense` directly): the published `vld_metrics` is the 7-key dict with every value re-derived INDEPENDENTLY from the synthetic inputs (the `hlp_validate_model` arithmetic mirrored — the `z_pred` gather + sigmoid, the `rn_z` / `rn_y`, the mse / mae / rmse / loss, via assert_close) and the log block is EXACT — the 10-line ordered block (the 4 Starting/Computing/completed lines + the five indented metric lines with the source's EXACT spacing + the outlier-report header) asserted with `assertEqual(logs[:10], expected)`, the non-degenerate ratio branch (NOT the "RMSE/MAE: n/a" zero-guard), and exactly 20 "vld position" lines after the header |
| `TestValidateSecondInstanceSmall` (UNGATED — DB-free, the NORMAL-tier pin of the LONG-tier `test_second_instance_deterministic`; a FRESH base dir pre-seeded with the two cache files — `rlmwf_04_POSITIONS.dat` + `rlmwf_13_VLD_POSITIONS.dat`, built no-DB from in-memory `RegabDataSets` via the `TestIsCacheConsistent` idiom + the real `regab_store_data_set_to_file` — then TWO real `LogisticModel` instances on a SMALL rlm_00-derived config (shrunk `optimization.max_iters = 20` + `su_analysis.total_positions = 200`) moved to VALIDATE) | 1 | `test_second_instance_deterministic_small`: both instances move to VALIDATE (step 14); the seeded files hit the cache, the four in-between cache levels (INDEXES / WMAPS / DESIGN_MTR / GENERATE) compute from the loaded data, and VALIDATE — which has no cache file — recomputes from the cached `w_dense`: NO "Extracted", NO "established successfully" (the DB is never touched, in EITHER run), the two "Cache successfully loaded and validated from '<...>rlmwf_04_POSITIONS.dat'/'...rlmwf_13_VLD_POSITIONS.dat'." lines present, and the second instance's `vld_metrics` is bit-identical (assertEqual) to the first's |
| `TestValidateDownScope` (UNGATED — DB-free; a `SimpleNamespace` ctx with sentinel values) | 1 | `test_down_clears_all_vld_attributes`: `wrk_validate._down` clears ALL FOUR validation attributes — `vld_metrics` / `vld_y_pred` / `vld_rn` / `vld_outliers` → None (strictly stronger than the LONG-tier pin, which exercises only `vld_metrics` through the state machine) + the "Clearing validation attributes..." log line |

## Goldens pinned

- The rlm_02 7-metric goldens: `vld_loss 0.00700794393196702`, `vld_mse_z 0.01401588786393404`,
  `vld_mae_z 0.09311295300722122`, `vld_mae_y 12.161691665649414`, `vld_mse_y 239.10484313964844`,
  `vld_rmse_y 15.46301555633545`, `vld_samples 200` (bid [8] validation vs the bid [6,7] training model); the six float
  metrics are compared with assert_close (test/reversi/closecheck.py, rel 1e-9 / abs 1e-12) — the np.dot reductions run
  through the multi-threaded OpenBLAS ddot, whose last ULPs depend on the thread count x the CPU kernel; vld_samples
  stays an exact int, and the hand-computed 2-position case (TestValidateModelUnit) keeps its bit-exact pins (2-sample
  sums, no BLAS).
- The hand-computed 2-position case (the TestValidateModelUnit derivation, also the probe D1 source).
- The full `_up` log block (the `test_up_publishes_metrics_and_full_log_contract` pin): the 10-line ordered sequence —
  the 4 Starting/Computing/completed lines, the five indented metric lines with the source's EXACT spacing
  ("  MSE:      " / "  MAE:      " / "  MAE(y):   " / "  RMSE(y):  " / "  RMSE/MAE: "), and the outlier-report header —
  asserted with `assertEqual` (the log-line contract), plus the exactly-20 "vld position" outlier lines.

## Conventions

- The setUp moves to VLD_POSITIONS (step 13) BEFORE the tests, so every worker test exercises the full 13-level chain
  end-to-end on the live DB (the test_wrk_zed pattern: setUp at the level before the one under test).
- The 2nd-instance test is the no-cache twin of the cache round-trip tests (test_wrk_positions et al.): where they pin
  "cache hit + no recompute", this one pins "recompute + identical result + 6 sibling cache hits".
- The NO-DB classes (`TestValidateModelUnit` + the two UNGATED small classes) run under SKIP_REGAB_DB=1 — the unit
  facts and the small determinism / down-scope pins stay testable without the live regab DB (the second-instance class
  pre-seeds the two DB cache slots in memory, the `TestIsCacheConsistent` idiom, so no DB is ever touched).

## Integration

- This file owns C1 (bootstrap step 14), C2 (the 7-key dict + exact goldens), the log-line pins, C6 (2nd-instance
  determinism + the 6 cache hits) + C7 (the _down scope), plus the D1/D3 checks — the probe (probes/verify_validate.py)
  retains only C4 (the internal consistency invariants) + C5 (no rlmwf_14* file) for the live-DB tier.
