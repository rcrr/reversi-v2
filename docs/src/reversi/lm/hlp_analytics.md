# reversi/lm/hlp_analytics.py
The ANALYTICS data module — the 15th step, the 3rd data module of a non-cache level (like hlp_gradient / hlp_validate):
5 public names (4 functions + the `TrainingDenseResult` dataclass) + 3 private helpers, NO store/load, NO cache_manager.
Computes the training-side metrics (the COMPRESSED forward pass over `ctx.w`, what the optimizer trained, and the DENSE
one over `ctx.w_dense`) and formats the two report variants (18-line console header — with the Config SHA3-256
fingerprint line; complete file report with the per-feature tables).

## API
| name | contract |
|---|---|
| `compute_training_metrics(ctx)` | the COMPRESSED forward pass → the 7-key train/pop dict (`Dict[str, float \| int]`); ONE INFO log line |
| `compute_training_dense_metrics(ctx)` | the DENSE forward pass → a `TrainingDenseResult` (the 4-key metrics dict + the f64 `rn_y` series) — the 4 keys are `train_dense_{mae_y, rmse_y, loss, samples}` dict; the loss is the PURE 0.5·mean(rn_z²) (the ridge lives on the compressed side); ONE INFO log line |
| `format_console_report(ctx)` | the 18-line header report, no date, no tables (the `Config SHA3-256` line, the `ctx.config_checksum` fingerprint) |
| `format_file_report(ctx)` | the complete report: detailed header (same 18-line common block) + FEATURE SET SUMMARY + the MOBILITY / PATTERN FEATURES DETAILS sections |

## Architecture
544 lines:
- `_format_mobility_feature_table`: the per-configuration ASCII table for one mobility feature — header: the fallback
  line (`feature_w_ranges[fid,0]` + `wmap_fallback` frequency), the frequency-weighted mean, the Instances/Cols + Config
  Counts (C/IA/IC) lines, the Eta-Squared statistic (SS_between/SS_total via `np.bincount`); rows (`print_rows`-gated)
  with the per-configuration weights — STATUS: IC (below the cut-off — fallback bucket), C (confirmed — its own trained
  `ctx.w` weight), IA (absent — the dense interpolated `ctx.w_dense` weight).
- `_format_pattern_feature_table`: the same table for one pattern feature, plus the Max/Min Weight (w) lines, the
  PRINCIPAL_IDX column (D8 orbit representatives via `feature.ref.convert_to_principal_index`), and STATUS CL (collapsed
  to fallback) / C / AB (absent — dense orbit-mean weight).
- `_format_header`: `MODEL ANALYTICS REPORT: <name>` + Total Parameters (W) + Dense Parameters (K) + the Optimization
  Status (from `ctx.opt_info`) + the Config SHA3-256 line (the `ctx.config_checksum` fingerprint — in the COMMON block,
  so BOTH the console and the file report carry it), then the 3-metric table: TRAINING from `ctx.train_metrics` ("Loss
  (MSE/2)" = `opt_info['f']`), TRAINING-DENSE from `ctx.train_dense_metrics` (pure forward-pass cells), VALIDATION from
  `ctx.vld_metrics` (N/A triple + gaps 0.0 when None); then the Population (baseline) line, the Generalization Gap
  (vld_rmse − train_dense_rmse — DENSE vs DENSE) and the Substitution Delta (train_dense_rmse − train_rmse — 0 at cut=1
  up to f32 rounding, "-0.00" on rlm_02/rlm_03).
- `format_file_report`: the per-table `print_rows` = the feature name is in `ctx.cfg.analytics.detailed_report`
  (non-optional field with a `default_factory`); `col_offset` accumulates over ALL features (intercept included) to line
  the column slices up with `ctx.hlp_indexes.indexes`.
- `compute_training_metrics`: the compressed forward pass —
  `np.sum(ctx.w[ctx.design_matrix].astype(np.float64), axis=1)` → `sigmoid` (reused) → `ctx.z2y`; `y_pred` vs
  `ctx.game_values`: `train_mae_y` / `train_rmse_y`; the population baseline: `pop_mae_y` / `pop_rmse_y` / `pop_loss`
  (0.5·mean squared z residuals via `ctx.y2z`); `train_loss = opt_info['f']` (0.0 when `opt_info` is None).
- `compute_training_dense_metrics`: the DENSE forward pass — the hlp_validate expanded-offsets idiom
  (`col_offsets = np.repeat(...)`, `dense_indices = ctx.hlp_indexes.indexes + col_offsets`) → `sigmoid` → `ctx.z2y`.

## Verified invariants
Pinned by `probes/verify_analytics.py` (36 checks) + the 4-test worker suite (all DB-gated).
- Structure (probe A1-A13, 14): 544 lines; `__all__` = the 5 public names (the 4 functions + `TrainingDenseResult`); 0
  non-comment trailing-ws lines; typing line `TYPE_CHECKING, Dict`; NO `@validate_call`; `train_dense_metrics`
  pre-declared (A13).
- The live rlm_02 goldens (probe C-tier + the worker suite; the dense 4 values: test doc): the 7-metric training goldens
  (bid [6,7]): `train_mae_y 12.346794566613694`, `train_rmse_y 15.58872172931622`, `train_loss 0.00712497066706419` (=
  `opt_info['f']`), `train_samples 199952`, `pop_mae_y 21.729816221648974`, `pop_rmse_y 26.40637507956623`,
  `pop_loss 0.020437248051166534` (C10 float64 re-derivation: 0 mismatch); the rlm_02 file report byte-deterministic
  (date-masked sha3_256 `3b4a5bebdf8b39add5a942132efdecd65dbeadcd84b4bc78ada464050a662e7b` — C5a/C5b,
  recompute-identical; + the Config SHA3-256 line, the hex value masked in the golden).
- The rlm_01 goldens (probe C-tier + the Mobility test class, exact values in the test doc): the 10-sample model (bid
  [7]) converges to interpolation (CONVERGED_MIN_GRAD, 16 iters); the dense dict (cut 2 — 5/10 positions touch IC
  configs) differs from compressed; the file report mask
  `15c71c7ea1608b14bd45a826c76e18b3193ccc10a3c55e008c491bc3457de5f5`; gap dense-vs-dense: 23.87 + Substitution
  Delta 3.36 (the true compressed-vs-dense cost).
- The unit math (probe D1-D4, no DB): the hand-computed 2-position case (predictor 0 → z_pred 0.5 → y_pred 0:
  mae_y/rmse_y 10.0, train_loss 0.123 = `opt_info['f']`, samples 2, pop 10.0/10.0, pop_loss 0.0030517578125); `opt_info`
  None → train_loss 0.0; console N/A branch (6 "N/A" cells, gaps 0.00, 18 lines — + the Config SHA3-256 line);
  dense-pass case (mae_y/rmse_y 10.0, loss 0.0030517578125, samples 2).

## Open issues
None.

## Conventions
- NO `@validate_call` on the 4 public data functions and no no-validation note — consistent with hlp_validate.
- The `sigmoid` is REUSED from hlp_gradient — no local copy.
- Report-only: the TRAINING "Loss (MSE/2)" cell is `opt_info['f']` (ridge-inclusive) while the TRAINING-DENSE /
  VALIDATION / Population cells are pure 0.5·mean(rn²) — intentional (the objective the optimizer minimized); the dense
  pass reads the f32 `w_dense` copy, the compressed pass the float64 `w` — even at cut=1 the two columns differ by the
  f32 rounding (rlm_02: −1.6e-08 in rmse).

## Integration
- Consumers: the ANALYTICS worker (the 4 functions + `TrainingDenseResult` are the module's whole API, `__all__`);
  `test_wrk_plot` imports `compute_training_dense_metrics` for its synthetic ctx, and `hlp_plot` consumes the published
  `ctx.train_dense_rn` series (never this module directly).
- Inputs: CONFIG (`ctx.cfg` + `ctx.config_checksum`), FEATURES (`ctx.feature_set` + `feature.ref`), INDEXES
  (`ctx.hlp_indexes.indexes`), POSITIONS (`ctx.game_values`), WMAPS (`ctx.w` + offsets/ranges/fallback), DESIGN_MTR
  (`ctx.design_matrix`), ZED (`ctx.y2z` / `ctx.z2y`), OPTIMIZE (`ctx.opt_info`), GENERATE (`ctx.w_dense`), VALIDATE
  (`ctx.vld_metrics` — the header's VALIDATION column), plus the worker's same-_up outputs (`ctx.train_metrics` /
  `ctx.train_dense_metrics` / `ctx.train_dense_rn` — the f64 residual series PLOT consumes — computed in `_up`
  before the format calls).
- No cache file: the reports are derived artifacts — the file report is (re)written to `base_dir` on every ANALYTICS
  up-move; the rlmwf_15 slot stays unused.
