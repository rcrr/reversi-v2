# reversi/test/test_lm_worker_full_chain.py
The pipeline's END-TO-END test: it runs the whole 16-level chain
(CREATED through CLIENT_CHECK) on two fixtures and pins the complete
saved-model round-trip (file + sidecar + read-back + evaluation
function). The ONLY test that exercises all 16 levels in one chain —
every per-level module test stops at its own level (the D-085-style
"move through my predecessors" setUp). Brought in by Roberto at
fe506c6 (D-104) with the three SAVE-family sources; rebuilt at D-104
T5-T6 (the D-085 idiom, the SKIP_REGAB_DB gates, the exact
`assertEqual` goldens replacing the bring-in's 3-4-digit
`assert_approx_equal`/`assertAlmostEqual` pins); re-pinned at D-105/M2
(the dense 4-key dicts, the 3-metric console rows, the two
file-report hashes); re-pinned at D-142 (the + `Config SHA3-256`
report lines in both variants, the two file-report hashes — the
masked-hash helper now masks the run-dependent config fingerprint
hex — and the new `test_config_record_sidecar`); re-pinned at
D-144 (the v2 model file: the file-level sha3 literal goldens
RETIRED — the embedded config dump carries the run's base_dir,
the bytes are run-specific — the size literal becomes a band,
the read-back gains the config provenance pins; the v1 guard
message "expected '1' or '2'"; `test_config_record_sidecar`
CONVERTED to `test_config_provenance_single_source` — the D-142
record retired — and the new no-DB `TestModelWeightsV2` micro
tier); re-pinned at D-145 (I-013: rlm_03 + rlm_04 now opt into
`high_performance_fg` — the numba fg — so BOTH full chains follow
the HP L-BFGS trajectories: A2030 71 iters (was 67), A2050 356
iters (was 397); every model-dependent golden moved by the
trajectory shift, the position-based goldens (pop statistics,
feature-set hash, iwmap offsets) are untouched; the A2050 chain
drops from ~10 min to ~1 min); re-pinned at D-148 (the 16th level,
CLIENT_CHECK: the step/worker pin 14/SAVE → 15/CLIENT_CHECK, the
A2030 log gains the "Client check passed ... max difference
0.000e+00 (tolerance 1.0e-08)" bit-identity pin, the two size bands
hold — the new client_check_tol config field's ~28 B stays inside
both).
> State: D-148 · 2026-09-10 · suite 9/0/0 (2 ungated read
  guards + 3 ungated D-144 v2 micro + 4 DB-gated (LONG); A2050
  additionally VLONG-gated, ~1 min since D-145, D-130)

## Coverage

| class | tests | what it pins |
|---|---|---|
| `TestFullChainA2030` (rlm_04 = "Short-Long Test 04": EDGE + LMC + intercept, bid [6] train 199932 / bid [5] vld 20000, cut 10, ec 20, `high_performance_fg: true` (D-145); setUp: the SKIP_REGAB_DB gate FIRST (T5a), stdout suppressed, `mkdtemp` under `CUSTOM_TMP_BASE`, the WORKSPACE_ROOT-anchored rlm_04.json, the model at `base_dir_override`) | 3 | `test_full_worker_chain`: `move_to_last()` + step/worker pin (15 / CLIENT_CHECK, D-148), then the goldens — the f64 metrics via assert_close (D-127), the f32-quantized + hash pins exact — vld 7-key (loss 0.005758139304816723, rmse_y 14.01651382446289, mae_y 11.048270225524902, mse_y 196.462646484375, mse_z 0.011516278609633446, mae_z 0.08458831906318665, samples 20000), train 7 + the dense 4-key dict (D-105/M2 — cut 10, 1923/199932 positions touch IC: dense rmse 13.8332856021253, dense loss 0.0056085786782205105), pop 4, opt (CONVERGED_MIN_GRAD, 71 iters), the v2 model file (the 22750-22850 B size band + sidecar verify — D-144: the v1 sha3 literal retired, the embedded config dump carries the run's base_dir; D-145: the band widened by ~42 B for the new config field + the HP w bytes; D-147: the band re-centered on the real test base dir — 12 runs measured 22798-22802 B, the D-145 22800-22900 sample had come from a single run with a different path prefix (22811 B) and clipped the real distribution) + version 2 on the read-back, the FULL read-back (the tps f32 truncations pinned as DISTINCT values, opt 4 keys, vld 4 keys — f32 == ctx f64 exactly, `feature_set.hash` `ec4f15374a00b729629d62ee0eb4354cbf163950672b7a9db9f81375e40559ef`, `iwmap_feature_offset` [0,1,66,6627] u32, `w_dense` (6627,) f32 sha3 `90ca05a3625775903d0a6e09c37d0f5827c3815738ddcd1af8d12e113b34ea75` + array equality), the D-144 embedded config provenance (mw.config_dump == the live normalized dump, mw.config_checksum == ctx.config_checksum), the log pins (VALIDATE "Validation completed. Loss (MSE/2): 5.75813930e-03" + the 2 SAVE lines + the D-148 CLIENT_CHECK line "Client check passed: 20000 validation residuals, max difference 0.000e+00 (tolerance 1.0e-08)."), the console pins (title, "Loss (MSE/2) | 5.6081e-03 | 5.6086e-03 | 5.7581e-03" (D-105/M2 3-metric row), "Population (baseline) : RMSE 26.41 MAE 21.73 Loss 2.0438e-02", "Generalization Gap (RMSE) : 0.18" (D-105/M2 — now dense-vs-dense), "Substitution Delta (RMSE) : 0.01", the `Config SHA3-256` line (D-142)), the file-report pins (Creation Date, the masked hash `a9642167344d4247be7821137b1f4352e4d37e8cb23ddd365ba728d6c3430a29` (D-145 re-pin)), the 6 EF training-position pins (bit-exact, the D-145 HP values: 0: −37.28886413574219, 1: −28.242984771728516, 7: 45.49725341796875, 123: 40.28820037841797, 999: 16.244956970214844, last: 23.315696716308594), the vld[42] scalar + array EF pins (11.917137145996094 both — the w_dense substitution path), `test_config_provenance_single_source` (D-144), `test_second_instance_deterministic` (the in-run byte-identity + 6 cache hits — passes on the HP path: the K3 kernel is run-deterministic) |
| `TestFullChainA2050` (rlm_03 = "Long Test 03": the 11-pattern "A2050" set + LMC + intercept, bid [3] train 1999179 / bid [6] vld 199932, cut 1, ec 20 — the legacy production naming; `@skipUnless(LONG == '1')` + the same DB gate; stdout NOT suppressed — the ~1-min run (D-145) narrates itself) | 1 | `test_full_worker_chain`: vld 7 EXACT (loss 0.0015777380904182792, rmse_y 7.3369646072387695, mae_y 5.6421332359313965, mse_y 53.831050872802734, mse_z 0.0031554761808365583, mae_z 0.04319758340716362, samples 199932), train 7 (loss 0.0014453826006501913, samples 1999179), the dense 4-key dict (D-105/M2 — cut 1: the dense values equal the compressed ones up to the f32 `w_dense` rounding, the Substitution Delta renders "0.00" (D-145: the sign of the f32 residual flipped)), pop 4, opt (CONVERGED_MIN_GRAD, 356 iters), the console pins (title, "Loss (MSE/2) | 1.4454e-03 | 1.4435e-03 | 1.5777e-03", "Population (baseline) : RMSE 26.42 MAE 21.76 Loss 2.0453e-02", "Generalization Gap (RMSE) : 0.32" (unchanged — cut 1 makes the gap dense-vs-dense without moving it), "Substitution Delta (RMSE) : 0.00", NOT-in: FEATURE SET SUMMARY / MOBILITY FEATURES DETAILS), the file-report pins (Creation Date, PATTERN FEATURE: XEDGE, masked hash `695c151bdaf2208e175d9092f9f2a092836d64a4d5029a9dda3eef3de14b9bce` (D-145 re-pin)), the v2 model file (the 516300-516500 B size band + sidecar — D-144: the v1 sha3 literal retired, as in A2030; D-145: the band widened 100 B lower for the HP w bytes), the read-back (fs hash `2c8bb32b40eff2c1e22b992e56b8d60fb51c17afb81d48f9414aef46c349e43d`, the 14-entry boundary array, w_dense (167331,) f32 sha3 `82b329dd31c5ac0d2b6b5c23a15734e0f4a7f18b6fbc609ef8c445c43035cccc`), the D-144 embedded config provenance (mw.config_dump == the live normalized dump, mw.config_checksum == ctx.config_checksum), and the EF bit-exact on 6 training positions (cut 1: dense ≡ compressed there; the D-145 HP values: 0: 6.911094665527344, 5: −32.91969299316406, 123: 40.503456115722656, 555: 24.345985412597656, 9999: −19.517921447753906, last: 57.769447326660156). NO second-instance test: it would double the chain cost for the same property (the write path is fixture-independent) |
| `TestModelWeightsReadGuards` (ungated — no DB, no model file needed) | 2 | the two `ValueError` guards of `model_weights_read_file`, built with `BinaryWriter`: wrong description → "File header mismatch, expected 'RGLM_BINARY_WEIGHTS', found 'WRONG_DESC'."; wrong version → "File header version, expected '1' or '2', found '99'." (D-144: the reader accepts v1 AND v2) (the D-106 step-3 class-c home of the probe B1-B2 read guards) |

| `TestModelWeightsV2` (D-144, ungated — no DB, the hand-crafted + SimpleNamespace idiom) | 3 | the v2 format micro tier: (1) the hand-crafted v1 file (the D-143-era layout, no config section) loads with `config_dump`/`config_checksum` None (the backward-compat reader); (2) the synthetic-ctx v2 ROUND-TRIP — `model_weights_write_file` on the SimpleNamespace ctx (the fixed-string `model_dump_json`), read back: every field + the embedded dump + the fingerprint match; (3) the v2 CORRUPTION sentinel — a stored checksum that does not cover the embedded dump → `ValueError` "Config section checksum mismatch, expected '<stored>', recomputed '<sha3>'." |
## Goldens pinned

- The two file-report masks (the `_masked_report_hash` helper masks the
  embedded `datetime.now()` AND the `Config SHA3-256` hex — the
  fingerprint embeds the run's base_dir, D-142 — before sha3_256, the
  D-103 pattern): rlm_04
  `a9642167344d4247be7821137b1f4352e4d37e8cb23ddd365ba728d6c3430a29`
  + rlm_03 `695c151bdaf2208e175d9092f9f2a092836d64a4d5029a9dda3eef3de14b9bce`
  (both D-145 re-pins — the HP trajectories changed the report
  content).
- rlm_04 gap 0.18 = 14.01651382446289 − 13.8332856021253 (dense
  vld minus dense train) + Substitution Delta 0.01 =
  13.8332856021253 − 13.825076853665676 (the 1923 IC-touching
  positions); rlm_03 gap 0.32 (the A2050 production model
  generalizes well: 1.99M train samples) + Delta 0.00 (cut 1: the
  residual is the f32 `w_dense` rounding — the sign flipped with
  the D-145 HP weights).

## Conventions

- The A2030 class ↔ rlm_04 mismatch is the legacy production naming
  above, not a copy-paste defect — no rename (accepted, O3).
- The D-106 step-3 class-c deletions landed HERE: probe C1-C14 (the
  rlm_04 live chain) → TestFullChainA2030, D1-D10 (the whole rlm_03
  LONG tier) → TestFullChainA2050, B1-B2 → TestModelWeightsReadGuards;
  the probe now keeps A1-A15 static + the C5 a-portion + the D0
  placeholder + the D-144 A6b (the config section leads the body, the v1|v2 guard, the corruption sentinel) (18 checks).
- LONG gating keeps the A2050 chain out of normal discover runs
  (the suite stays ~3 s gated; since D-145 the A2050 chain is
  ~1 min, so the live suite cost is dominated by the A2030 chain).
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
- D-145 (I-013): the position-based goldens did NOT move with the
  HP re-pin (the training_pop_stats f64 values, the f32-truncated
  tps read-back, the feature-set hash, the iwmap offsets, the pop
  console row) — only the model-dependent ones (the metric dicts,
  the opt iters/f/g_norm, the w_dense sha3, the EF values, the
  report hashes, the console metric rows).

## Integration

- `reversi.test.paths` (WORKSPACE_ROOT / CUSTOM_TMP_BASE) makes the
  module runnable from any CWD (the bring-in's `'./build/tmp'` +
  relative json paths were CWD-locked, T5).
- A2050 has no second-instance test and its goldens are pinned from
  the same live-run family as A2030 (determinism is a property of the
  chain, demonstrated on rlm_04).
