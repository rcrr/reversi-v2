# reversi/test/test_wrk_analytics.py
The ANALYTICS worker integration suite — the dedicated suite for the ANALYTICS level, the first suite to cover TWO
non-cache levels' downstream data (the 5th non-cache level itself + the rlm_01 mobility-table branch of the file
report). 2 classes / 4 tests, all DB-gated.

## Coverage

| class | tests | what it pins |
|---|---|---|
| `TestLMWorkerAnalytics` (rlm_02; setUp: the SKIP_REGAB_DB gate FIRST (idiom — the setUp moves through the whole 14-level chain to VALIDATE on a fresh base dir, so the live regab DB is required); the stdout patcher; `TemporaryDirectory` created FIRST; the `WORKSPACE_ROOT`-anchored rlm_02.json; `move_to_step('VALIDATE')` → step 14; defensive tearDown) | 3 | `test_analytics_report_goldens`: pre-state — `analytics_report` + `train_metrics` + `train_dense_metrics` all None (pre-declared on LMContext but unset); `move_to_step('ANALYTICS')` → step 15 / worker "ANALYTICS"; the 7-key dict pinned (5 float metrics via assert_close; the f32-quantized train_loss and train_samples exact; rlm_02, bid [6,7], 199952 samples — the goldens in the module doc) + the 4-key dense dict pinned (assert_close; the ints exact; dense == compressed up to the f32 `w_dense` rounding); the console report: the title, "Total Parameters (W) : 2,981", "Dense Parameters (K) : 6,588", the 3 data rows "Loss (MSE/2) \| 7.1250e-03 \| 7.1223e-03 \| 7.0079e-03", the Population line "RMSE 26.41 MAE 21.73 Loss 2.0437e-02", "Generalization Gap (RMSE) : -0.13", "Substitution Delta (RMSE) : -0.00" (f32 rounding, not substitution), NO "Creation Date", NO "PATTERN FEATURE" (header-only); the file report: exists at `base_dir/model_analytics_report.txt`, the Creation Date + the empty MOBILITY section, the EDGE (fid=0) + DIAG3 (fid=1) pattern headers, exactly ONE "(Table rows omitted" line (DIAG3 — EDGE is in the fixture's `detailed_report`), the date-masked sha3_256 golden `3b4a5bebdf8b39add5a942132efdecd65dbeadcd84b4bc78ada464050a662e7b` (the `Config SHA3-256` line too, the hex masked in the golden); the captured logs: "Generating model analytics report...", "Computing metrics on the training set...", "Computing metrics on the training set...", "Analytics report saved to ", NO "PATTERN FEATURE". `test_second_instance_deterministic`: a 2nd `LogisticModel` on the SAME base dir moved to ANALYTICS: exactly 6 "Cache successfully loaded and validated" hits (the 6 cache_manager levels — the CONFIG level writes no cache file, so ALL 6 hits are cache_manager; the 7th cache file, the OPTIMIZE checkpoint (`checkpoint_optimize.dat`, not an rlmwf_ file), has its own read-back; FEATURES/ZED/GRADIENT/VALIDATE/ANALYTICS recompute), no "Extracted", no "established successfully"; the recomputed `train_metrics` dict, the `train_dense_metrics` dict and the `analytics_report` string IDENTICAL to the first instance (the no-cache determinism pin). `test_down_clears_analytics_attributes`: back to VALIDATE (step 14) clears the 3 blackboard fields the test pins (`train_metrics`, `train_dense_metrics`, `analytics_report`) to None — the worker also clears the 4th (`train_dense_rn`, probe A8), unpinned by this suite — while the report file REMAINS on disk (the artifact semantics — `_down` does not unlink, like the OPTIMIZE checkpoint) |
| `TestLMWorkerAnalyticsMobility` (rlm_01 — the ONLY fixture that exercises the mobility table helper end-to-end; `analytics.detailed_report = ["DIAG3", "LMC"]`) | 1 | `test_mobility_and_pattern_tables`: first run to ANALYTICS; the rlm_01 7-metric goldens (bid [7], 10 samples — the 10-sample model converges to interpolation, CONVERGED_MIN_GRAD, 16 iters) + the 4-key dense dict pinned (the 3 floats via assert_close, the int train_dense_samples exact) (cut 2, 5/10 training positions touch IC configs: train_dense_mae_y 1.854193878173828, train_dense_rmse_y 3.3556084739848866, train_dense_loss 0.0003036324051208794, train_dense_samples 10); the file report: "MOBILITY FEATURE: LMC (fid=1)" (the 65-row table), "PATTERN FEATURE: DIAG3 (fid=2)", "PATTERN FEATURE: CORE (fid=3)", exactly ONE omitted-rows line (CORE); the rlm_01 date-masked sha3_256 golden `15c71c7ea1608b14bd45a826c76e18b3193ccc10a3c55e008c491bc3457de5f5` (the `Config SHA3-256` line too, the hex masked in the golden); the logs: "Optimization Status : CONVERGED_MIN_GRAD (16 iters)" + "Generalization Gap (RMSE) : 23.87" (dense-vs-dense: vld_rmse 27.22 − train_dense_rmse 3.36) + "Substitution Delta (RMSE) : 3.36" (the true compressed-vs-dense cost: 3.36 vs the compressed 0.00) |

## Goldens pinned

- The two file-report masks: rlm_02 `3b4a5bebdf8b39add5a942132efdecd65dbeadcd84b4bc78ada464050a662e7b` + rlm_01
  `15c71c7ea1608b14bd45a826c76e18b3193ccc10a3c55e008c491bc3457de5f5` (the `_masked_report_hash` helper: the file embeds
  `datetime.now()` — the Creation Date line — and a `Config SHA3-256` fingerprint that embeds the run's `base_dir`, so
  the golden is the sha3_256 of the text with the date regex-masked to "DATE" and the config hex to "HASH"; every other
  byte is deterministic).
- The rlm_02 7-metric + 4-key dense goldens and the rlm_01 7-metric + 4-key dense goldens (the module doc's live
  invariants).

## Conventions

- The db_long_gate idiom (the SKIP_REGAB_DB + LONG tier gates) is FIRST in setUp (before the stdout patch / tmp dir).
- The float64 metric goldens are compared with assert_close (reversi/test/closecheck.py, rel 1e-9 / abs 1e-12): the
  np.dot reductions over up to ~2M f64 terms run through the multi-threaded OpenBLAS ddot (scipy 0.3.34, DYNAMIC_ARCH
  NO_AFFINITY) — the last ULPs depend on the thread count x the CPU kernel (the 4 -> 8 vCPU VM move shifted them up to
  88 ULP on rlm_02). Still bit-exact (assertEqual): the f32-quantized train_loss (float of the f32 OPTIMIZE objective),
  the int counts, the report hashes, and the second-instance-determinism contract (every upstream artifact stays pinned
  by the rlmwf checksum + sha3 flows).
- The 6-hit cache count mirrors the VALIDATE suite's count — ANALYTICS adds no cache file (the rlmwf_15 slot stays
  unused).

## Integration

- The `detailed_report` fixture (`rlm_01.json` `["DIAG3", "LMC"]`) is consumed by the ANALYTICS level only, so it moves
  no other golden.
- The dense-metric goldens and the report pins are pinned by this file: 14 positive line pins (7 console-report, 4
  rlm_02 file-report, 3 rlm_01 file-report), the 2 exactly-ONE "(Table rows omitted" counts, the 2 date-masked
  file-report hashes, and 4 negative assertNotIn pins (console: no Creation Date, no PATTERN FEATURE; rlm_02 file:
  no MOBILITY FEATURE:; rlm_02 logs: no PATTERN FEATURE).
