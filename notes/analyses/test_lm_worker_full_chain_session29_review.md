<!-- ARCHIVED — D-106 step 21 (the docs/ rewrite, 2026-09-04): the SAVE family (the worker doc + this test doc) moved out of docs/src/twolm/test/ into the snapshot schema per docs_rules.md §1/§4. This is a frozen historical record: it is never updated. Stale-in-current-context notes: (1) the "32 checks" probe figure — the current probes/verify_save.py (the 4091e72 move) has 17 surviving check calls: A1-A15 (static, no DB), the C5 a-portion (the live f/g_norm floats), the D0 LONG placeholder. The D-106 step-3 deletions (all class c): B1-B2 the read guards → this file's TestModelWeightsReadGuards, C1-C14 (except the C5 f/g_norm a-portion) the rlm_04 live-chain goldens → this file's TestFullChainA2030, D1-D10 the whole rlm_03 LONG tier → this file's TestFullChainA2050. (2) the "631 tests / 87 skipped" full-discover figure predates the D-106 steps 3-20 (current: 664/87 gated). (3) the Architecture section's line ranges (L72-215 / L218-330 / L333-367) are the PRE-D-105 numbers — the D-105 re-pin grew the classes to L72-266 / L269-433 / L436-464 (the Appendix had the post-D-105 numbers). (4) the D-104/D-105 campaign narrative is frozen history. -->

# twolm/test/test_lm_worker_full_chain.py

Analysis date: 2026-09-02 — analysis session 29 (D-104, the SAVE
bring-in, Roberto's commit fe506c6, which brought in this test module
together with the three SAVE-family source files); fix campaign D-104
(T5 gates/idiom/stray-comment + T2 dead imports + T4 ws + T6 exact
goldens + O4 vld EF pin) approved by Roberto and applied in the same
session. The module is the pipeline's END-TO-END test: it runs the
whole 15-level chain (CREATED through SAVE) on two fixtures and pins
the complete saved-model round-trip.

## Suite status (session 29, post D-105)

- 5 tests total: 2 in `TestFullChainA2030` (both DB-gated), 1 in
  `TestFullChainA2050` (DB- AND LONG-gated), 2 in
  `TestModelWeightsReadGuards` (ungated, no DB).
- Live: A2030 pair ~6 s (two full rlm_04 chains + a third for the
  determinism test), guards ~0 s; A2050 ~10 min (1999179 training
  samples, 397 lbfgs iters) only with `LONG=1` (705 s measured on
  the D-105 re-pin run).
- `SKIP_REGAB_DB=1`: 3 skips (A2030 ×2 + A2050) + 2 guard runs, ~0 s.
  Pre-campaign the bring-in's A2030 had NO gate and ran (and would
  error without a DB) in "gated" mode: `SKIP_REGAB_DB` is a test-side
  convention only — no production code reads it.
- Full discover post-campaign: 631 tests, 87 skipped gated (3.2 s);
  ungated 631 run, 18 skipped, GREEN (46.8 s).

## Architecture (467 lines, post D-105)

- L28-33 the "How to run" block (added by T5 — the bring-in had no
  such block; house pattern, mentions SKIP_REGAB_DB and LONG).
- L39-63 imports: unittest/os/tempfile/shutil/hashlib/re; numpy;
  skipUnless/patch/StringIO/Path; Verbosity; LogisticModel;
  `BinaryWriter` + `verify_sha3_256_sidecar` from binio;
  `model_weights_read_file` + `MODEL_WEIGHTS_FILE_HEADER_STR`;
  `make_evaluation_function`; `sigmoid`; `WORKSPACE_ROOT` /
  `CUSTOM_TMP_BASE` from `twolm.test.paths` (the D-085 idiom). The
  bring-in's dead `numpy.testing as nptest` and its CWD-relative
  config/tmp paths are gone (T2/T5).
- L66-69 `_masked_report_hash(text)`: masks the file report's embedded
  `datetime.now()` (`\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}` → "DATE")
  before sha3_256 — the D-103 pattern for date-embedded reports.
- L72-215 `TestFullChainA2030` (rlm_04 = "Short-Long Test 04": EDGE +
  LMC + intercept, bid [6] train 199932 samples / bid [5] vld 20000,
  frequency_cut_off 10, ec 20):
  - L80-97 setUp: the SKIP_REGAB_DB gate FIRST (T5a, D-085 idiom),
    stdout suppression, `mkdtemp(dir=str(CUSTOM_TMP_BASE))`, the
    WORKSPACE_ROOT-anchored rlm_04.json, the model at
    `base_dir_override`.
  - L104-194 `test_full_worker_chain`: `move_to_last()` + step/worker
    pin (14 / SAVE), then the exact goldens — vld 7-key dict, train
    7-key dict, the dense 4-key dict (D-105/M2 — rlm_04 cut 10,
    1923 training positions touch IC configs: train_dense_mae_y
    10.905119078281873, train_dense_rmse_y 13.831248070093375,
    train_dense_loss 0.0056069279089570045, train_dense_samples
    199932), pop 4-key dict, opt (converged/reason/iters), the
    model file (21603 B, sha3 `bcf8d918979aaddba52ed2c9a80571f4fdc939a985ff4f3705510fa4f8010abb`,
    sidecar), the full read-back (metadata, tps f32 truncations, opt 4
    keys, vld 4 keys, `feature_set.hash`
    `ec4f15374a00b729629d62ee0eb4354cbf163950672b7a9db9f81375e40559ef`,
    `iwmap_feature_offset` `[0,1,66,6627]` u32, `w_dense` (6627,) f32
    sha3 `7ecdeba66d9f34b9396e199dd4a5933196131db497ff88fce726bcd75f1f4f37`
    + array equality), the log-line pins (VALIDATE "Validation
    completed. Loss (MSE/2): 5.75742032e-03", the 2 SAVE lines), the
    console-report pins (title, "Loss (MSE/2)    | 5.6064e-03     |
    5.6069e-03     | 5.7574e-03" (D-105/M2 — the 3-metric row),
    "Population (baseline)  : RMSE 26.41  MAE 21.73  Loss
    2.0438e-02", "Generalization Gap (RMSE)   : 0.18" (D-105/M2 —
    now dense-vs-dense, was 0.19 mixed), "Substitution Delta
    (RMSE)   : 0.01" (D-105/M2)), the file-report pins (Creation
    Date, the EDGE/LMC detail sections, masked hash
    `d44557a8efd007f4634c2949a0cf9eca60d7b38f790c2bbd1e058245a4045a2e`
    (D-105/M2 re-pin)),
    and the EF pins (6 training positions bit-exact + `vld_positions[42]`
    → 11.932792663574219, the O4 substitution-path pin).
  - L196-215 `test_second_instance_deterministic` (added by T6): a
    third chain in the same base dir — byte-identical model file, 6
    "Cache successfully loaded and validated" hits (7 cache files;
    CONFIG re-stores its snapshot, so a 'stored' line, not a hit), no
    "Extracted", no "established successfully".
- L218-330 `TestFullChainA2050` (rlm_03 = "Long Test 03": 11 patterns
  (the "A2050" set) + LMC + intercept, bid [3] train 1999179 samples /
  bid [6] vld 199932, frequency_cut_off 1, ec 20; the legacy
  production naming, see below): `@skipUnless(LONG == '1')` + the
  same DB gate in setUp (T5a); stdout NOT suppressed (the ~10-min run
  narrates itself). `test_full_worker_chain` pins: vld 7 exact
  (loss 0.001578879076987505, rmse_y 7.339616775512695, mae_y
  5.644496440887451, mse_y 53.86997604370117, mse_z
  0.00315775815397501, mae_z 0.04321568086743355, samples 199932),
  train 7 exact (loss 0.001444403431378305, rmse_y 7.015377800787937,
  mae_y 5.396253447071691, samples 1999179, pop_mae_y
  21.758215006979484, pop_rmse_y 26.417003454424307, pop_loss
  0.020453333854675293), the dense 4-key dict (D-105/M2 — rlm_03
  cut 1: the dense values equal the compressed ones up to the f32
  `w_dense` rounding, the Substitution Delta renders "-0.00":
  train_dense_mae_y 5.396253444189108, train_dense_rmse_y
  7.015377798958687, train_dense_loss 0.0014424461405724287,
  train_dense_samples 1999179), pop 4 exact, opt (CONVERGED_MIN_GRAD, 397
  iters), the console pins (title, "Loss (MSE/2)    | 1.4444e-03     |
  1.4424e-03     | 1.5789e-03" (D-105/M2 — the 3-metric row),
  "Population (baseline)  : RMSE 26.42  MAE 21.76  Loss
  2.0453e-02", "Generalization Gap (RMSE)   : 0.32" (unchanged —
  cut 1 makes the gap dense-vs-dense without moving it),
  "Substitution Delta (RMSE)   : -0.00" (D-105/M2),
  NOT-in: FEATURE SET SUMMARY / MOBILITY FEATURES DETAILS), the
  file-report pins (Creation Date, PATTERN FEATURE: XEDGE, masked hash
  `57f9766b7e5115903319f3387b192e490c71674eebc2e2c199040579b5fad83a`
  (D-105/M2 re-pin)),
  the model file (515042 B, sha3
  `3ad1805815c536e4506b0804b5be9e8662de53402c37fc3268c8dbbbb6847ff4`,
  sidecar), the read-back (fs hash `2c8bb32b40eff2c1e22b992e56b8d60fb51c17afb81d48f9414aef46c349e43d`,
  the 14-entry boundary array, w_dense (167331,) f32 sha3
  `a012689f70ef8a492ce0fbf374a49e79e62f758a83fce94540a459bd28b527fc`),
  and the EF bit-exact on 6 training positions (cut 1: dense ≡
  compressed there).
- L333-367 `TestModelWeightsReadGuards` (added by T6): the two
  `ValueError` guards of `model_weights_read_file`, built with
  `BinaryWriter` (wrong description → "File header mismatch, expected
  'RGLM_BINARY_WEIGHTS', found 'WRONG_DESC'."; wrong version → "File
  header version, expected '1', found '99'."). Ungated: no DB, no
  model file needed.

## Verified facts (D-105 probe — 32 checks, 0 mismatches)

- A2030 pair GREEN live, A2050 GREEN under `LONG=1` (705 s on the
  D-105 re-pin run) — all goldens above derived from live runs
  (scratch/o104_probe.py, o104_rlm03.py, o104_clip.py; the D-105
  dense goldens from the D-105 capture runs) before being pinned.
- rlm_04 gap 0.18 (D-105/M2 — now dense-vs-dense) =
  14.015637397766113 − 13.831248070093375 (vld slightly worse than
  the dense train — a healthy model on bid [5]); was 0.19 when the
  gap mixed in the compressed train (13.822995683195872). The new
  Substitution Delta row reads 0.01 (13.831248070093375 −
  13.822995683195872 — 1923/199932 training positions touch IC
  configs).
- rlm_03 gap 0.32 (the production A2050 model generalizes well: 1.99M
  train samples); Substitution Delta -0.00 (cut 1: the dense-vs-
  compressed residual is the f32 `w_dense` rounding, −1.7e-07).
- The bring-in's original pins (3-4 significant digits, `assert_approx_equal`
  / `assertAlmostEqual`) were replaced by exact `assertEqual` pins
  (T6, the house pattern since D-096); the 3-4-digit values all
  subsume the exact ones.
- The "A2030"/"A2050" class names: Roberto's legacy production
  naming — A2xxx is the endgame-solver model family (A2 + ec*10;
  A2050 = ec 20; production: A2050, A2150, A2250, ...). rlm_03's
  pattern set is literally named "A2050"; rlm_04's is named "EDGE"
  (the class keeps the legacy name — left as-is, accepted).

## Minor notes (D-104 observations, report-only)

- O3 (accepted): the A2030 class ↔ rlm_04 mismatch is the legacy
  naming (above), not a copy-paste defect — no rename.
- O4 (accepted, now pinned): the EF cross-check originally used
  training positions only; the `vld_positions[42]` pin adds the
  substitution path (rlm_04's freq_cut 10 + bid [5] validation = many
  unseen EDGE configurations).
- The second-instance determinism test is on A2030 only: A2050 would
  double the ~10-min cost for the same property (rlm_03 has no extra
  mechanism — the write path is fixture-independent).
- A2050 has no second-instance test and its goldens are pinned from
  the same live run family as A2030 (determinism is a property of the
  chain, demonstrated on rlm_04 and in the D-103/D-102 modules).
- T4 removed 37 ws lines (31 ws-only + 6 code-line trailing) from the
  bring-in's 291-line file; the T5 rewrite reorganized it to 444
  lines (exact goldens are verbose by design).

## Integration notes

- The module is the ONLY test that exercises all 15 levels in one
  chain: every per-level module test stops at its own level (the
  D-085-style "move through my predecessors" setUp), so this is the
  integration safety net for the SAVE bring-in.
- `twolm.test.paths` (WORKSPACE_ROOT / CUSTOM_TMP_BASE) makes the
  module runnable from any CWD (the bring-in's `'./build/tmp'` +
  `'src/twolm/test/data/rlm_04.json'` were CWD-locked).
- LONG gating keeps the 10-min chain out of normal discover runs
  (the house's existing LONG convention; the suite stays ~3 s gated /
  ~40 s live).

## Appendix — line reference (post D-105, 467 lines)

- L1-26 license header (canonical, untouched)
- L28-33 How-to-run block (T5)
- L35-63 imports (T2/T5)
- L66-69 `_masked_report_hash`
- L72-266 `TestFullChainA2030` (gate, idiom, goldens incl. the D-105
  dense 4-key dict, EF, 2nd instance)
- L269-433 `TestFullChainA2050` (LONG + DB gate, rlm_03 goldens
  incl. the D-105 dense 4-key dict)
- L436-464 `TestModelWeightsReadGuards`
- L465-467 `__main__`
