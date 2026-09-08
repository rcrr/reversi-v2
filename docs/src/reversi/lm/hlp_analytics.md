# reversi/lm/hlp_analytics.py
The ANALYTICS data module — the 14th active level (the 13th step), the 2nd
function-only data module of a non-cache level (like hlp_gradient /
hlp_validate): 4 public functions + 3 private helpers, NO data class, NO
store/load, NO cache_manager. Computes the training-side metrics (the
COMPRESSED forward pass over `ctx.w`, what the optimizer trained, and the
DENSE one over `ctx.w_dense`, D-105/M2) and formats the two report variants
(17-line console header; complete file report with the per-feature tables).
> State: D-105 · 8cdf20b · 2026-09-03 · suite 4/0/0 (via test_lm_worker_analytics, all DB-gated)

## API
| name | contract |
|---|---|
| `compute_training_metrics(ctx)` | the COMPRESSED forward pass → the 7-key train/pop dict (`Dict[str, float \| int]`, D-103 M2); ONE INFO log line |
| `compute_training_dense_metrics(ctx)` | the DENSE forward pass → the 4-key `train_dense_{mae_y, rmse_y, loss, samples}` dict (D-105/M2); the loss is the PURE 0.5·mean(rn_z²) (the ridge lives on the compressed side); ONE INFO log line |
| `format_console_report(ctx)` | the 17-line header report, no date, no tables |
| `format_file_report(ctx)` | the complete report: detailed header + FEATURE SET SUMMARY + the MOBILITY / PATTERN FEATURES DETAILS sections |

## Architecture
522 lines (453 at D-103; D-105/M2 added the dense fn + 3-metric header):
- `_format_mobility_feature_table` (L49-167): the per-configuration ASCII
  table for one mobility feature — header: the fallback line
  (`feature_w_ranges[fid,0]` + `wmap_fallback` frequency), the
  frequency-weighted mean, the Instances/Cols + Config Counts (C/IA/IC)
  lines, the Eta-Squared statistic (SS_between/SS_total via `np.bincount`);
  rows (`print_rows`-gated) with the per-configuration weights — STATUS: IC
  (below the cut-off — fallback bucket), C (confirmed — its own trained
  `ctx.w` weight), IA (absent — the dense interpolated `ctx.w_dense`
  weight).
- `_format_pattern_feature_table` (L170-307): the same table for one
  pattern feature, plus the Max/Min Weight (w) lines, the PRINCIPAL_IDX
  column (D8 orbit representatives via
  `feature.ref.convert_to_principal_index`), and STATUS CL (collapsed to
  fallback) / C / AB (absent — dense orbit-mean weight per D-098 R2).
- `_format_header` (L310-401): `MODEL ANALYTICS REPORT: <name>` + Total
  Parameters (W) + Dense Parameters (K) + the Optimization Status (from
  `ctx.opt_info`), then the 3-metric table (D-105/M2): TRAINING from
  `ctx.train_metrics` ("Loss (MSE/2)" = `opt_info['f']`), TRAINING-DENSE
  from `ctx.train_dense_metrics` (pure forward-pass cells), VALIDATION from
  `ctx.vld_metrics` (N/A triple + gaps 0.0 when None); then the Population
  (baseline) line, the Generalization Gap (vld_rmse − train_dense_rmse —
  DENSE vs DENSE post D-105) and the Substitution Delta (train_dense_rmse −
  train_rmse — 0 at cut=1 up to f32 rounding, "-0.00" on rlm_02/rlm_03).
- `format_file_report` (L410-441): the per-table `print_rows` = the feature
  name is in `ctx.cfg.analytics.detailed_report` (D-103 M3: non-optional
  field with a `default_factory`); `col_offset` accumulates over ALL
  features (intercept included) to line the column slices up with
  `ctx.hlp_indexes.indexes`.
- `compute_training_metrics` (L443-481): the compressed forward pass —
  `np.sum(ctx.w[ctx.design_matrix].astype(np.float64), axis=1)` → `sigmoid`
  (reused) → `ctx.z2y`; `y_pred` vs `ctx.game_values`: `train_mae_y` /
  `train_rmse_y`; the population baseline: `pop_mae_y` / `pop_rmse_y` /
  `pop_loss` (0.5·mean squared z residuals via `ctx.y2z`); `train_loss =
  opt_info['f']` (0.0 when `opt_info` is None).
- `compute_training_dense_metrics` (L483-521, D-105/M2): the DENSE forward
  pass — the hlp_validate expanded-offsets idiom (`col_offsets =
  np.repeat(...)`, `dense_indices = ctx.hlp_indexes.indexes + col_offsets`)
  → `sigmoid` → `ctx.z2y`.

## Verified invariants
Pinned by `probes/verify_analytics.py` (36 checks) + the 4-test worker
suite (all DB-gated).
- Structure (probe A1-A13, 14): 522 lines; `__all__` = the 4 public names;
  0 non-comment trailing-ws lines (D-103 T4); typing line `TYPE_CHECKING,
  Dict` (T2); NO `@validate_call`; `train_dense_metrics` pre-declared
  (A13).
- The live rlm_02 goldens (probe C-tier + the worker suite; the dense 4
  values: test doc): the 7-metric training goldens (bid [6,7]):
  `train_mae_y 12.346794566613694`, `train_rmse_y 15.58872172931622`,
  `train_loss 0.00712497066706419` (= `opt_info['f']`), `train_samples
  199952`, `pop_mae_y 21.729816221648974`, `pop_rmse_y 26.40637507956623`,
  `pop_loss 0.020437248051166534` (C10 float64 re-derivation: 0 mismatch);
  the rlm_02 file report byte-deterministic (date-masked sha3_256
  `94a4af7e5ca554e6f8b219cf5ed820e45e102489dacdc25e15d2b263158120b0` —
  C5a/C5b, recompute-identical).
- The rlm_01 goldens (probe C-tier + the Mobility test class, exact values
  in the test doc): the 10-sample model (bid [7]) converges to
  interpolation (CONVERGED_MIN_GRAD, 16 iters); the dense dict (cut 2 —
  5/10 positions touch IC configs) differs from compressed; the file report
  mask `f6b54954a3c54d13a9a3b3e65face75a5bd709899050c0b77b236a8955cf4c8c`;
  gap dense-vs-dense: 23.87 (was 27.22 pre D-105) + Substitution Delta 3.36
  (the true compressed-vs-dense cost).
- The unit math (probe D1-D4, no DB): the hand-computed 2-position case
  (predictor 0 → z_pred 0.5 → y_pred 0: mae_y/rmse_y 10.0, train_loss 0.123
  = `opt_info['f']`, samples 2, pop 10.0/10.0, pop_loss 0.0030517578125);
  `opt_info` None → train_loss 0.0; console N/A branch (6 "N/A" cells, gaps
  0.00, 17 lines); dense-pass case (mae_y/rmse_y 10.0, loss
  0.0030517578125, samples 2).

## Open issues
None.

## Conventions
- NO `@validate_call` on the 4 public data functions and no no-validation
  note — consistent with hlp_validate, approved in D-102 without one.
- The `sigmoid` is REUSED from hlp_gradient (L36) — no local copy.
- Report-only: the TRAINING "Loss (MSE/2)" cell is `opt_info['f']`
  (ridge-inclusive) while the TRAINING-DENSE / VALIDATION / Population
  cells are pure 0.5·mean(rn²) — intentional (the objective the optimizer
  minimized); the dense pass reads the f32 `w_dense` copy, the compressed
  pass the float64 `w` — even at cut=1 the two columns differ by the f32
  rounding (rlm_02: −1.6e-08 in rmse).

## Integration
- Consumers: ONLY the ANALYTICS worker — the 4 public functions are the
  module's whole API (`__all__`).
- Inputs: CONFIG (`ctx.cfg`), FEATURES (`ctx.feature_set` + `feature.ref`),
  INDEXES (`ctx.hlp_indexes.indexes`), POSITIONS (`ctx.game_values`), WMAPS
  (`ctx.w` + offsets/ranges/fallback), DESIGN_MTR (`ctx.design_matrix`),
  ZED (`ctx.y2z` / `ctx.z2y`), OPTIMIZE (`ctx.opt_info`), GENERATE
  (`ctx.w_dense`), VALIDATE (`ctx.vld_metrics` — the header's VALIDATION
  column), plus the worker's same-_up outputs (`ctx.train_metrics` /
  `ctx.train_dense_metrics`, computed in `_up` before the format calls).
- No cache file: the reports are derived artifacts — the file report is
  (re)written to `base_dir` on every ANALYTICS up-move; the rlmwf_12 slot
  stays unused.
