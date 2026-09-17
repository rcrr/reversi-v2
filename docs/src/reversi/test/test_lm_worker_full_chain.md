# reversi/test/test_lm_worker_full_chain.py
The pipeline's END-TO-END test: it runs the whole 18-level chain
(CREATED through PLOT) on two fixtures and pins the complete
saved-model round-trip (file + sidecar + read-back + evaluation
function). The ONLY test that exercises all 18 levels in one chain —
every per-level module test stops at its own level (the "move through
my predecessors" setUp). Both fixtures (rlm_03 and rlm_04) opt into
`high_performance_fg` (the numba fg), so both full chains follow the
HP L-BFGS trajectories (A2030 71 iters, A2050 356 iters). The 16th
level is CLIENT_CHECK and the 17th is PLOT; the rlm_03.json +
rlm_04.json `plot` sections whitelist all seven plot names, so both
chains exercise plot generation. The saved model is the v2 file
format: the embedded config dump carries the run's base_dir, so the
file bytes are run-specific and the pinned file size is a band
rather than a literal.

## Coverage

| class | tests | what it pins |
|---|---|---|
| `TestFullChainA2030` (rlm_04 = "Short-Long Test 04": EDGE + LMC + intercept, bid [6] train 199932 / bid [5] vld 20000, cut 10, ec 20, `high_performance_fg: true`; setUp: the SKIP_REGAB_DB gate FIRST, stdout suppressed, `mkdtemp` under `CUSTOM_TMP_BASE`, the WORKSPACE_ROOT-anchored rlm_04.json, the model at `base_dir_override`) | 3 | `test_full_worker_chain`: `move_to_last()` + step/worker pin (18 / PLOT), then the goldens — the f64 metrics via assert_close, the f32-quantized + hash pins exact — vld 7-key (loss 0.005758139304816723, rmse_y 14.01651382446289, mae_y 11.048270225524902, mse_y 196.462646484375, mse_z 0.011516278609633446, mae_z 0.08458831906318665, samples 20000), train 7 + the dense 4-key dict (cut 10, 1923/199932 positions touch IC: dense rmse 13.8332856021253, dense loss 0.0056085786782205105), pop 4, opt (CONVERGED_MIN_GRAD, 71 iters), the v2 model file (the 23183-23283 B size band + sidecar verify — the v1 sha3 literal retired, the embedded config dump carries the run's base_dir; the band widened by ~42 B for the new config field + the HP w bytes; the band re-centered on the real test base dir — 12 runs measured 22798-22802 B, the earlier 22800-22900 sample had come from a single run with a different path prefix (22811 B) and clipped the real distribution; re-centered again for the plot config section in the embedded dump — 2 runs measured 22990/22994 B) + version 2 on the read-back, the FULL read-back (the tps f32 truncations pinned as DISTINCT values, opt 4 keys, vld 4 keys — f32 == ctx f64 exactly, `feature_set.hash` `ec4f15374a00b729629d62ee0eb4354cbf163950672b7a9db9f81375e40559ef`, `iwmap_feature_offset` [0,1,66,6627] u32, `w_dense` (6627,) f32 sha3 `90ca05a3625775903d0a6e09c37d0f5827c3815738ddcd1af8d12e113b34ea75` + array equality), the embedded config provenance (mw.config_dump == the live normalized dump, mw.config_checksum == ctx.config_checksum), the log pins (VALIDATE "Validation completed. Loss (MSE/2): 5.75813930e-03" + the 2 SAVE lines + the CLIENT_CHECK line "Client check passed: 20000 validation residuals, max difference 0.000e+00 (tolerance 1.0e-08)." + the PLOT lines — "Plot 'residual_density' saved:" (one per name) + "PLOT done: 7 plot(s) written to {base_dir}/plots." — and the seven PNG magic checks in `base_dir/plots` (the rlm_04.json `plot` whitelist, png, the relative dir_name default)), the console pins (title, "Loss (MSE/2) | 5.6081e-03 | 5.6086e-03 | 5.7581e-03" (3-metric row), "Population (baseline) : RMSE 26.41 MAE 21.73 Loss 2.0438e-02", "Generalization Gap (RMSE) : 0.18" (now dense-vs-dense), "Substitution Delta (RMSE) : 0.01", the `Config SHA3-256` line), the file-report pins (Creation Date, the masked hash `a9642167344d4247be7821137b1f4352e4d37e8cb23ddd365ba728d6c3430a29`), the 6 EF training-position pins (bit-exact, the HP values: 0: −37.28886413574219, 1: −28.242984771728516, 7: 45.49725341796875, 123: 40.28820037841797, 999: 16.244956970214844, last: 23.315696716308594), the vld[42] scalar + array EF pins (11.917137145996094 both — the w_dense substitution path), `test_config_provenance_single_source`, `test_second_instance_deterministic` (the in-run byte-identity + 6 cache hits — passes on the HP path: the K3 kernel is run-deterministic) |
| `TestFullChainA2050` (rlm_03 = "Long Test 03": the 11-pattern "A2050" set + LMC + intercept, bid [3] train 1999179 / bid [6] vld 199932, cut 1, ec 20 — the legacy production naming; `@skipUnless(LONG == '1')` + the same DB gate; stdout NOT suppressed — the ~1-min run narrates itself) | 1 | `test_full_worker_chain`: vld 7 EXACT (loss 0.0015777380904182792, rmse_y 7.3369646072387695, mae_y 5.6421332359313965, mse_y 53.831050872802734, mse_z 0.0031554761808365583, mae_z 0.04319758340716362, samples 199932), train 7 (loss 0.0014453826006501913, samples 1999179), the dense 4-key dict (cut 1: the dense values equal the compressed ones up to the f32 `w_dense` rounding, the Substitution Delta renders "0.00" (the sign of the f32 residual flipped)), pop 4, opt (CONVERGED_MIN_GRAD, 356 iters), the console pins (title, "Loss (MSE/2) | 1.4454e-03 | 1.4435e-03 | 1.5777e-03", "Population (baseline) : RMSE 26.42 MAE 21.76 Loss 2.0453e-02", "Generalization Gap (RMSE) : 0.32" (unchanged — cut 1 makes the gap dense-vs-dense without moving it), "Substitution Delta (RMSE) : 0.00", NOT-in: FEATURE SET SUMMARY / MOBILITY FEATURES DETAILS), the file-report pins (Creation Date, PATTERN FEATURE: XEDGE, masked hash `695c151bdaf2208e175d9092f9f2a092836d64a4d5029a9dda3eef3de14b9bce`), the v2 model file (the 516692-516892 B size band + sidecar — the v1 sha3 literal retired, as in A2030; the band widened 100 B lower for the HP w bytes; re-centered for the plot config section — 1 run measured 516551 B) + the seven PNG magic checks in `base_dir/plots` (the rlm_03.json `plot` whitelist — the 200k-point scale), the read-back (fs hash `2c8bb32b40eff2c1e22b992e56b8d60fb51c17afb81d48f9414aef46c349e43d`, the 14-entry boundary array, w_dense (167331,) f32 sha3 `82b329dd31c5ac0d2b6b5c23a15734e0f4a7f18b6fbc609ef8c445c43035cccc`), the embedded config provenance (mw.config_dump == the live normalized dump, mw.config_checksum == ctx.config_checksum), and the EF bit-exact on 6 training positions (cut 1: dense ≡ compressed there; the HP values: 0: 6.911094665527344, 5: −32.91969299316406, 123: 40.503456115722656, 555: 24.345985412597656, 9999: −19.517921447753906, last: 57.769447326660156). NO second-instance test: it would double the chain cost for the same property (the write path is fixture-independent) |
| `TestModelWeightsReadGuards` (ungated — no DB, no model file needed) | 2 | the two `ValueError` guards of `model_weights_read_file`, built with `BinaryWriter`: wrong description → "File header mismatch, expected 'RGLM_BINARY_WEIGHTS', found 'WRONG_DESC'."; wrong version → "File header version, expected '1' or '2', found '99'." (the reader accepts v1 AND v2) |

| `TestModelWeightsV2` (ungated — no DB, the hand-crafted + SimpleNamespace idiom) | 3 | the v2 format micro tier: (1) the hand-crafted v1 file (no config section) loads with `config_dump`/`config_checksum` None (the backward-compat reader); (2) the synthetic-ctx v2 ROUND-TRIP — `model_weights_write_file` on the SimpleNamespace ctx (the fixed-string `model_dump_json`), read back: every field + the embedded dump + the fingerprint match; (3) the v2 CORRUPTION sentinel — a stored checksum that does not cover the embedded dump → `ValueError` "Config section checksum mismatch, expected '<stored>', recomputed '<sha3>'." |
## Goldens pinned

- The two file-report masks (the `_masked_report_hash` helper masks the
  embedded `datetime.now()` AND the `Config SHA3-256` hex — the
  fingerprint embeds the run's base_dir — before sha3_256): rlm_04
  `a9642167344d4247be7821137b1f4352e4d37e8cb23ddd365ba728d6c3430a29`
  + rlm_03 `695c151bdaf2208e175d9092f9f2a092836d64a4d5029a9dda3eef3de14b9bce`
  (the HP trajectories changed the report content).
- rlm_04 gap 0.18 = 14.01651382446289 − 13.8332856021253 (dense
  vld minus dense train) + Substitution Delta 0.01 =
  13.8332856021253 − 13.825076853665676 (the 1923 IC-touching
  positions); rlm_03 gap 0.32 (the A2050 production model
  generalizes well: 1.99M train samples) + Delta 0.00 (cut 1: the
  residual is the f32 `w_dense` rounding — the sign flipped with
  the HP weights).

## Conventions

- The A2030 class ↔ rlm_04 mismatch is the legacy production naming
  above, not a copy-paste defect — no rename.
- The probe checks split here: the rlm_04 live chain → TestFullChainA2030,
  the rlm_03 LONG tier → TestFullChainA2050, the B1-B2 read guards →
  TestModelWeightsReadGuards; the probe now keeps A1-A15 static + the
  C5 a-portion + the D0 placeholder + the A6b (the config section leads
  the body, the v1|v2 guard, the corruption sentinel) (18 checks).
- LONG gating keeps the A2050 chain out of normal discover runs
  (the suite stays ~3 s gated; the A2050 chain is ~1 min, so the live
  suite cost is dominated by the A2030 chain).
- The float64 metric goldens (the vld / train / dense dicts + the pop
  statistics) are compared with assert_close (reversi/test/closecheck.py,
  rel 1e-9 / abs 1e-12) — the last ULPs of the OpenBLAS ddot depend on
  the thread count x the CPU kernel. Still bit-exact assertEqual: the
  f32-quantized values (train_loss = float(opt f32), g_norm, the tps +
  vld read-back truncations), the EF pins, the sha3 hashes, and the int
  counts; the second-instance-determinism test stays exact (the in-run
  bit-identity contract).
- The position-based goldens did NOT move when the HP weights changed
  (the
  training_pop_stats f64 values, the f32-truncated tps read-back, the
  feature-set hash, the iwmap offsets, the pop console row) — only the
  model-dependent ones (the metric dicts, the opt iters/f/g_norm, the
  w_dense sha3, the EF values, the report hashes, the console metric
  rows).

## Integration

- `reversi.test.paths` (WORKSPACE_ROOT / CUSTOM_TMP_BASE) makes the
  module runnable from any CWD.
- A2050 has no second-instance test and its goldens are pinned from
  the same live-run family as A2030 (determinism is a property of the
  chain, demonstrated on rlm_04).
