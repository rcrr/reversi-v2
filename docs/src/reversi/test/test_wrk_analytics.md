# reversi/test/test_wrk_analytics.py
The ANALYTICS worker integration suite — added by the D-103
campaign (T5, Roberto-approved: "T5: OK. Procedi!"), the
dedicated suite for the ANALYTICS level — the first suite to
cover TWO non-cache levels' downstream data (the 5th non-cache
level itself + the rlm_01 mobility-table branch of the file
report). 2 classes / 4 tests, all DB-gated. Re-pinned at
D-105/M2 (the dense-metrics pins, the 3-metric header lines,
the new INFO log line, the two file-report hashes, the rlm_01
gap 27.22 → 23.87).
> State: D-105 · 8cdf20b · 2026-09-03 · suite 4/0/0 (4 DB-gated)

## Coverage

| class | tests | what it pins |
|---|---|---|
| `TestLMWorkerAnalytics` (rlm_02; setUp: the SKIP_REGAB_DB gate FIRST (D-085 idiom — the setUp moves through the whole 13-level chain to VALIDATE on a fresh base dir, so the live regab DB is required); the stdout patcher; `TemporaryDirectory` created FIRST; the `WORKSPACE_ROOT`-anchored rlm_02.json; `move_to_step('VALIDATE')` → step 12; defensive tearDown) | 3 | `test_analytics_report_goldens`: pre-state — `analytics_report` + `train_metrics` + `train_dense_metrics` all None (pre-declared on RLMContext since D-103 M1 / D-105 M2 but unset); `move_to_step('ANALYTICS')` → step 13 / worker "ANALYTICS"; the 7-key dict pinned (the six float metrics via
assert_close, D-127; the f32-quantized train_loss and
train_samples exact; rlm_02, bid [6,7], 199952 samples —
the goldens in the module doc) + the 4-key dense dict
pinned (assert_close, D-127; the ints exact; D-105/M2 — cut
1: dense == compressed up to the f32 `w_dense` rounding); the console report: the title, "Total Parameters (W) : 2,981", "Dense Parameters (K) : 6,588", the 3 data rows "Loss (MSE/2) \| 7.1250e-03 \| 7.1223e-03 \| 7.0079e-03" (D-105/M2), the Population line "RMSE 26.41 MAE 21.73 Loss 2.0437e-02", "Generalization Gap (RMSE) : -0.13", "Substitution Delta (RMSE) : -0.00" (cut 1: f32 rounding, not substitution), NO "Creation Date", NO "PATTERN FEATURE" (header-only); the file report: exists at `base_dir/model_analytics_report.txt`, the Creation Date + the empty MOBILITY section, the EDGE (fid=0) + DIAG3 (fid=1) pattern headers, exactly ONE "(Table rows omitted" line (DIAG3 — EDGE is in the fixture's `detailed_report`), the date-masked sha3_256 golden `94a4af7e5ca554e6f8b219cf5ed820e45e102489dacdc25e15d2b263158120b0` (D-105/M2 re-pin); the captured logs: "Generating model analytics report...", "Computing metrics on the training set...", "Computing dense-pass metrics on the training set..." (D-105/M2), "Analytics report saved to ", NO "PATTERN FEATURE". `test_second_instance_deterministic`: a 2nd `LogisticModel` on the SAME base dir moved to ANALYTICS: exactly 6 "Cache successfully loaded and validated" hits (the 6 cache_manager levels — CONFIG + the OPTIMIZE checkpoint have their own load flows; FEATURES/ZED/GRADIENT/VALIDATE/ANALYTICS recompute), no "Extracted", no "established successfully"; the recomputed `train_metrics` dict, the `train_dense_metrics` dict (D-105/M2) and the `analytics_report` string IDENTICAL to the first instance (the no-cache determinism pin). `test_down_clears_analytics_attributes`: back to VALIDATE (step 12) clears ALL THREE blackboard fields to None (D-105/M2 added `train_dense_metrics`) while the report file REMAINS on disk (the artifact semantics — `_down` does not unlink, like the OPTIMIZE checkpoint) |
| `TestLMWorkerAnalyticsMobility` (rlm_01 — the ONLY fixture that exercises the mobility table helper end-to-end; `analytics.detailed_report = ["DIAG3", "LMC"]` post D-103 T6) | 1 | `test_mobility_and_pattern_tables`: first run to ANALYTICS; the rlm_01 7-metric goldens (bid [7], 10 samples — the 10-sample model converges to interpolation, CONVERGED_MIN_GRAD, 16 iters) + the 4-key dense dict pinned EXACTLY (D-105/M2 — cut 2, 5/10 training positions touch IC configs: train_dense_mae_y 1.854193878173828, train_dense_rmse_y 3.3556084739848866, train_dense_loss 0.0003036324051208794, train_dense_samples 10); the file report: "MOBILITY FEATURE: LMC (fid=1)" (the 65-row table), "PATTERN FEATURE: DIAG3 (fid=2)", "PATTERN FEATURE: CORE (fid=3)", exactly ONE omitted-rows line (CORE); the rlm_01 date-masked sha3_256 golden `f6b54954a3c54d13a9a3b3e65face75a5bd709899050c0b77b236a8955cf4c8c` (D-105/M2 re-pin); the logs: "Optimization Status : CONVERGED_MIN_GRAD (16 iters)" + "Generalization Gap (RMSE) : 23.87" (D-105/M2 — now dense-vs-dense: vld_rmse 27.22 − train_dense_rmse 3.36; was 27.22 as 27.22 − 0.00 compressed) + "Substitution Delta (RMSE) : 3.36" (the true compressed-vs-dense cost: 3.36 vs the compressed 0.00) |

## Goldens pinned

- The two file-report masks: rlm_02
  `94a4af7e5ca554e6f8b219cf5ed820e45e102489dacdc25e15d2b263158120b0`
  + rlm_01 `f6b54954a3c54d13a9a3b3e65face75a5bd709899050c0b77b236a8955cf4c8c`
  (the `_masked_report_hash` helper: the file embeds
  `datetime.now()` — the Creation Date line — so the golden is
  the sha3_256 of the text with the date regex-masked to "DATE";
  every other byte is deterministic).
- The rlm_02 7-metric + 4-key dense goldens and the rlm_01 7-
  metric + 4-key dense goldens (the module doc's live invariants).

## Conventions

- D-085 idiom: the db_long_gate (the SKIP_REGAB_DB + LONG tier
  gates, D-130) is FIRST in setUp (before the stdout patch / tmp
  dir).
- The float64 metric goldens are compared with assert_close
  (reversi/test/closecheck.py, rel 1e-9 / abs 1e-12) since
  D-127: the np.dot reductions over up to ~2M f64 terms run
  through the multi-threaded OpenBLAS ddot (scipy 0.3.34,
  DYNAMIC_ARCH NO_AFFINITY) — the last ULPs depend on the
  thread count x the CPU kernel (the 4 -> 8 vCPU VM move
  shifted them up to 88 ULP on rlm_02). Still bit-exact
  (assertEqual): the f32-quantized train_loss (float of the
  f32 OPTIMIZE objective), the int counts, the report
  hashes, and the second-instance-determinism contract
  (every upstream artifact stays pinned by the rlmwf
  checksum + sha3 flows).
- The 6-hit cache count mirrors the VALIDATE suite's count —
  the 5th non-cache level adds no cache file (the rlmwf_12 slot
  stays unused; the flat-file numbering skips 12 like 03/07/08).

## Integration

- The `detailed_report` fixture change (T6: rlm_01.json
  `["DIAG3"]` → `["DIAG3", "LMC"]`) is the only fixture edit of
  the D-103 campaign — the analytics block is consumed by the
  ANALYTICS level only, so no other golden moved (the rlm_01
  hash above is the post-T6 value).
- The D-106 step-3 class c deletions (probe C4b the dense
  goldens + C6 the 17 header lines / 21-line span) were deleted
  because this file pins them.
