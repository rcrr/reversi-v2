# reversi/test/test_lm_worker_full_chain.py
The pipeline's END-TO-END test: it runs the whole 15-level chain
(CREATED through SAVE) on two fixtures and pins the complete
saved-model round-trip (file + sidecar + read-back + evaluation
function). The ONLY test that exercises all 15 levels in one chain —
every per-level module test stops at its own level (the D-085-style
"move through my predecessors" setUp). Brought in by Roberto at
fe506c6 (D-104) with the three SAVE-family sources; rebuilt at D-104
T5-T6 (the D-085 idiom, the SKIP_REGAB_DB gates, the exact
`assertEqual` goldens replacing the bring-in's 3-4-digit
`assert_approx_equal`/`assertAlmostEqual` pins); re-pinned at D-105/M2
(the dense 4-key dicts, the 3-metric console rows, the two
file-report hashes).
> State: D-141 · 8c20bab · 2026-09-09 · suite 5/0/0 (2 ungated +
  3 DB-gated (LONG); A2050 additionally VLONG-gated, ~10 min,
  D-130)

## Coverage

| class | tests | what it pins |
|---|---|---|
| `TestFullChainA2030` (rlm_04 = "Short-Long Test 04": EDGE + LMC + intercept, bid [6] train 199932 / bid [5] vld 20000, cut 10, ec 20; setUp: the SKIP_REGAB_DB gate FIRST (T5a), stdout suppressed, `mkdtemp` under `CUSTOM_TMP_BASE`, the WORKSPACE_ROOT-anchored rlm_04.json, the model at `base_dir_override`) | 2 | `test_full_worker_chain`: `move_to_last()` + step/worker pin (14 / SAVE), then the goldens — the f64 metrics via assert_close (D-127), the f32-quantized + hash pins exact — vld 7-key (loss 0.00575742032378912, rmse_y 14.015637397766113, mae_y 11.048789978027344, mse_y 196.43809509277344, mse_z 0.01151484064757824, mae_z 0.0845922976732254, samples 20000), train 7 + the dense 4-key dict (D-105/M2 — cut 10, 1923/199932 positions touch IC: dense rmse 13.831248070093375, dense loss 0.005606927908957004), pop 4, opt (CONVERGED_MIN_GRAD, 67 iters), the model file (21603 B, sha3 `bcf8d918979aaddba52ed2c9a80571f4fdc939a985ff4f3705510fa4f8010abb` + sidecar verify), the FULL read-back (the tps f32 truncations pinned as DISTINCT values, opt 4 keys, vld 4 keys — f32 == ctx f64 exactly, `feature_set.hash` `ec4f15374a00b729629d62ee0eb4354cbf163950672b7a9db9f81375e40559ef`, `iwmap_feature_offset` [0,1,66,6627] u32, `w_dense` (6627,) f32 sha3 `7ecdeba66d9f34b9396e199dd4a5933196131db497ff88fce726bcd75f1f4f37` + array equality), the log pins (VALIDATE "Validation completed. Loss (MSE/2): 5.75742032e-03" + the 2 SAVE lines), the console pins (title, "Loss (MSE/2) \| 5.6064e-03 \| 5.6069e-03 \| 5.7574e-03" (D-105/M2 3-metric row), "Population (baseline) : RMSE 26.41 MAE 21.73 Loss 2.0438e-02", "Generalization Gap (RMSE) : 0.18" (D-105/M2 — now dense-vs-dense, was 0.19 mixed), "Substitution Delta (RMSE) : 0.01"), the file-report pins (Creation Date, the EDGE/LMC detail sections, masked hash `d44557a8efd007f4634c2949a0cf9eca60d7b38f790c2bbd1e058245a4045a2e` (D-105/M2 re-pin)), and the EF pins (6 training positions bit-exact + `ef(vld_positions[42])` = 11.932792663574219 — the O4 substitution-path pin: cut 10 + bid [5] validation make that position exercise the w_dense substitution end-to-end) + the D-141 array-EF batch pin (the vectorized EF bit-exact on the SAME 6 pinned training positions via one batch call over the full 199932-position set, dtype/shape (199932,) f32, + the vld[42] pin on the validation batch). `test_second_instance_deterministic` (T6): a third chain in the same base dir — byte-identical model file, exactly 6 "Cache successfully loaded and validated" hits (7 cache files: CONFIG re-stores its snapshot — a 'stored' line, not a 'hit'), no "Extracted", no "established successfully" |
| `TestFullChainA2050` (rlm_03 = "Long Test 03": the 11-pattern "A2050" set + LMC + intercept, bid [3] train 1999179 / bid [6] vld 199932, cut 1, ec 20 — the legacy production naming; `@skipUnless(LONG == '1')` + the same DB gate; stdout NOT suppressed — the ~10-min run narrates itself) | 1 | `test_full_worker_chain`: vld 7 EXACT (loss 0.001578879076987505, rmse_y 7.339616775512695, mae_y 5.644496440887451, mse_y 53.86997604370117, mse_z 0.00315775815397501, mae_z 0.04321568086743355, samples 199932), train 7 (loss 0.001444403431378305, samples 1999179), the dense 4-key dict (D-105/M2 — cut 1: the dense values equal the compressed ones up to the f32 `w_dense` rounding, the Substitution Delta renders "-0.00"), pop 4, opt (CONVERGED_MIN_GRAD, 397 iters), the console pins (title, "Loss (MSE/2) \| 1.4444e-03 \| 1.4424e-03 \| 1.5789e-03", "Population (baseline) : RMSE 26.42 MAE 21.76 Loss 2.0453e-02", "Generalization Gap (RMSE) : 0.32" (unchanged — cut 1 makes the gap dense-vs-dense without moving it), "Substitution Delta (RMSE) : -0.00", NOT-in: FEATURE SET SUMMARY / MOBILITY FEATURES DETAILS), the file-report pins (Creation Date, PATTERN FEATURE: XEDGE, masked hash `57f9766b7e5115903319f3387b192e490c71674eebc2e2c199040579b5fad83a` (D-105/M2 re-pin)), the model file (515042 B, sha3 `3ad1805815c536e4506b0804b5be9e8662de53402c37fc3268c8dbbbb6847ff4` + sidecar), the read-back (fs hash `2c8bb32b40eff2c1e22b992e56b8d60fb51c17afb81d48f9414aef46c349e43d`, the 14-entry boundary array, w_dense (167331,) f32 sha3 `a012689f70ef8a492ce0fbf374a49e79e62f758a83fce94540a459bd28b527fc`), and the EF bit-exact on 6 training positions (cut 1: dense ≡ compressed there). NO second-instance test: it would double the ~10-min cost for the same property (the write path is fixture-independent) |
| `TestModelWeightsReadGuards` (ungated — no DB, no model file needed) | 2 | the two `ValueError` guards of `model_weights_read_file`, built with `BinaryWriter`: wrong description → "File header mismatch, expected 'RGLM_BINARY_WEIGHTS', found 'WRONG_DESC'."; wrong version → "File header version, expected '1', found '99'." (the D-106 step-3 class-c home of the probe B1-B2 read guards) |

## Goldens pinned

- The two file-report masks (the `_masked_report_hash` helper masks the
  embedded `datetime.now()` before sha3_256 — the D-103 pattern):
  rlm_04 `d44557a8efd007f4634c2949a0cf9eca60d7b38f790c2bbd1e058245a4045a2e`
  + rlm_03 `57f9766b7e5115903319f3387b192e490c71674eebc2e2c199040579b5fad83a`
  (both D-105/M2 re-pins).
- rlm_04 gap 0.18 = 14.015637397766113 − 13.831248070093375 (dense
  vld minus dense train; was 0.19 mixed with the compressed train
  13.822995683195872) + Substitution Delta 0.01 =
  13.831248070093375 − 13.822995683195872 (the 1923 IC-touching
  positions); rlm_03 gap 0.32 (the A2050 production model
  generalizes well: 1.99M train samples) + Delta -0.00 (cut 1: the
  residual is the f32 `w_dense` rounding, −1.7e-07).

## Conventions

- The A2030 class ↔ rlm_04 mismatch is the legacy production naming
  above, not a copy-paste defect — no rename (accepted, O3).
- The D-106 step-3 class-c deletions landed HERE: probe C1-C14 (the
  rlm_04 live chain) → TestFullChainA2030, D1-D10 (the whole rlm_03
  LONG tier) → TestFullChainA2050, B1-B2 → TestModelWeightsReadGuards;
  the probe now keeps A1-A15 static + the C5 a-portion + the D0
  placeholder (17 checks).
- LONG gating keeps the ~10-min chain out of normal discover runs
  (the suite stays ~3 s gated / ~40 s live).
- D-127: the float64 metric goldens (the vld / train / dense
  dicts + the pop statistics) are compared with assert_close
  (reversi/test/closecheck.py, rel 1e-9 / abs 1e-12) — the
  last ULPs of the OpenBLAS ddot depend on the thread count
  x the CPU kernel. Still bit-exact assertEqual: the
  f32-quantized values (train_loss = float(opt f32), g_norm,
  the tps + vld read-back truncations), the EF pins, the
  sha3 hashes, and the int counts; the
  second-instance-determinism test stays exact (the in-run
  bit-identity contract).

## Integration

- `reversi.test.paths` (WORKSPACE_ROOT / CUSTOM_TMP_BASE) makes the
  module runnable from any CWD (the bring-in's `'./build/tmp'` +
  relative json paths were CWD-locked, T5).
- A2050 has no second-instance test and its goldens are pinned from
  the same live-run family as A2030 (determinism is a property of the
  chain, demonstrated on rlm_04).
