# reversi/lm/hlp_validate.py
The VALIDATE domain module of the LM pipeline — the 14th step. Like hlp_zed and hlp_gradient it is PURE COMPUTE: no
store / load / is_cache_consistent trio, no checksum, no cache file (the rlmwf_14 slot stays unused). It runs the
forward pass of the trained model on the validation positions (the same `ctx.feature_set` as training, the dense weights
`ctx.w_dense` from GENERATE) and returns a `LMValidate`: the 7-metric validation dict (the v2 model-file contract)
plus the two per-position series it is computed from — the fitted values and the residuals in Y, the SINGLE derivation
PLOT renders and CLIENT_CHECK compares against the saved file.

## API

| name | contract |
|---|---|
| `LMValidate` | the dataclass: `metrics` (the 7-key dict), `y_pred` (the fitted values in Y, f64), `rn_y` (the residuals in Y, f64) |
| `hlp_validate_model(ctx) -> LMValidate` | the forward pass + the metrics + the two series; NO `@validate_call` (the function-only shape over an already-validated context) |
| `hlp_validate_top_outliers(rn, k=20) -> ndarray` | the indices of the k largest `\|residual\|`, descending; the STABLE argsort makes a tie keep the LOWER index first |

## Architecture

- The metric semantics (the docstring, condensed): the Z-space MAE / MSE / RMSE over the
  affine-mapped targets + the three formulas + the RMSE/MAE = sqrt(π/2) = 1.253 normal-distribution
  indicator. MAE is the mean absolute deviation — on the bounded [0, 1] scale an MAE of 0.04 reads as
  a 4% average deviation — and it weighs every error linearly (the "typical" accuracy baseline). MSE
  is the residual variance (the sqrt brings it back to Z units as the RMSE, the prediction-error
  standard deviation) and it penalizes large deviations aggressively (a 0.1 miss costs 0.01, a 0.5
  miss 0.25): the alarm for the logistic shape — the curve flattens to horizontal asymptotes at 0 / 1
  around a steep central inflection, and if the data does not flatten at the same rate the boundary
  errors blow up, so a rising MSE flags a fundamentally bad fit in those regions.
- The body: `vld_indexes = ctx.feature_set.compute_indexes(vld_positions)` (the SAME feature_set as training), the dense
  mapping (`col_offsets = np.repeat(ctx.iwmap_feature_offset[:-1], n_instances_per_feature)`, then
  `dense_indices = vld_indexes + col_offsets` and `linear_predictor = np.sum(ctx.w_dense[dense_indices], axis=1)`), the
  forward pass (`z_pred = sigmoid(linear_predictor)` — the hlp_gradient reuse) and `vld_z = ctx.y2z(vld_game_values)`:
  `y2z` casts to float32 BEFORE the affine, so the int8 game values never overflow.
- TWO arithmetic paths, deliberately: the METRICS keep the original f32 arithmetic (`y_pred = ctx.z2y(z_pred)`,
  `rn_y = y_pred - vld_game_values`), because their goldens are pinned and embedded in the v2 model file; the PUBLISHED
  series are the f64 views (`astype(np.float64)`), bit-identical to what PLOT and CLIENT_CHECK computed before — so the
  publication moves no number.
- The 7-key dict: `vld_loss = 0.5·‖rn_z‖²/M`, `vld_mse_z = 2·vld_loss`, `vld_mae_z`, `vld_mae_y`, `vld_mse_y`,
  `vld_rmse_y`, `vld_samples` — every value `float(...)`-cast except `vld_samples` (`int`).
- `hlp_validate_top_outliers` is the outlier report's kernel: one stable argsort, no state.
- Imports: `Any` in the typing line, NO regab import (the data comes from `ctx.vld_positions` / `ctx.vld_game_values`,
  never a DB call).

## Verified invariants

Pinned by the `probes/verify_validate.py` sweep + `test_wrk_validate.py`.

- The module shape (probe A1-A13): the 3-name `__all__`, NO regab import, the `sigmoid` reuse, NO cache_manager import,
  the 7-key metrics dict, the underscore unpack, no dead numpy import in the worker.
- The f64 series: `LMValidate.y_pred` / `rn_y` are f64 and carry the hand-computed values of the
  2-position case (y_pred [0, 0], rn_y [0, −64]) — `test_validation_result_carries_the_f64_series`.
- The outlier kernel: the ranking, the tie-break (a |49| tie keeps the lower index first) and the default k = 20
  — `test_top_outliers_ranking_and_ties`, `test_top_outliers_default_is_twenty`.
- The live rlm_02 invariants (probe C4/C5): the internal consistency (mse_z == 2·vld_loss, rmse_y² == mse_y) and NO
  rlmwf_14* file in the base dir.
- The live rlm_02 goldens (the worker suite, the first run to VALIDATE): `vld_loss 0.00700794393196702`,
  `vld_mse_z 0.01401588786393404`, `vld_mae_z 0.09311295300722122`, `vld_mae_y 12.161691665649414`,
  `vld_mse_y 239.10484313964844`, `vld_rmse_y 15.46301555633545`, `vld_samples 200` — the validation loss stays close to
  the training final loss (no overfitting signal).
- The unit metric math (`TestValidateModelUnit`, DB-free; the python-float typing is probe D2): the hand-computed
  2-position case (1 feature / 2 instances, `w_dense [0.5, −0.5]`, game values [0, 64] → loss 0.0625, mse_z 0.125,
  mae_z 0.25, mae_y 32.0, mse_y 2048.0, rmse_y sqrt(2048), samples 2), every metric a PYTHON float, `vld_samples` an
  int, and the M1 zero-guard branch.

## Open issues

None.

## Conventions

- No init validation, no `@validate_call`: a single function over an already-validated context — the `ctx: "LMContext"`
  string annotation + the TYPE_CHECKING import is the house pattern for the circular constraint.
- The dense-mapping idiom (`np.repeat` + fancy indexing + `np.sum`) differs from hlp_generate's per-feature start/end
  loop — both valid, left as is.
- The metric arithmetic is f32 and the published series are f64: do NOT unify them — the goldens and the model file
  depend on the first, the HlpPlotData / CLIENT_CHECK contract on the second.

## Integration

- Upstream inputs: VLD_POSITIONS (`ctx.vld_positions`, `ctx.vld_game_values`), FEATURES (`ctx.feature_set`), WMAPS
  (`ctx.iwmap_feature_offset`), GENERATE (`ctx.w_dense`), ZED (`ctx.y2z` / `ctx.z2y`).
- Downstream: ANALYTICS consumes `ctx.vld_metrics`; SAVE embeds it in the v2 model file; PLOT renders `ctx.vld_y_pred` /
  `ctx.vld_rn`; CLIENT_CHECK compares the saved-file residuals against `ctx.vld_rn`.
- No `use_cache` interaction: the level writes nothing, so the CONFIG cache switch is irrelevant here.
