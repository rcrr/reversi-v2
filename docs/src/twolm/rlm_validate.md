# twolm/rlm_validate.py
The VALIDATE domain module of the RLM pipeline — the 13th active
level (the 12th step). Unlike every other rlm_* level except
hlp_zed / rlm_gradient, this one is PURE COMPUTE: no data class,
no store / load / is_cache_consistent trio, no checksum, no
rlmwf_12 file (the slot stays unused, as 03/07/08). The single
public function `validate_model(ctx) -> Dict[str, Any]` runs the
forward pass of the trained model on the validation positions
(the same `ctx.feature_set` as training, the dense weights
`ctx.w_dense` from GENERATE) and returns the 7-metric
validation dict: the Z-space metrics (`vld_loss = 0.5·‖rn_z‖²/M`,
`vld_mse_z = ‖rn_z‖²/M = 2·loss`, `vld_mae_z = mean|rn_z|`) and
the Y-space metrics (`vld_mae_y`, `vld_mse_y`, `vld_rmse_y` —
the predictions mapped back with `ctx.z2y`), plus
`vld_samples = M`.
> State: D-102 · b98edaa · 2026-09-02 · suite 5/0/0 (via test_lm_worker_validate, 3 DB-gated)

## API

| name | contract |
|---|---|
| `validate_model(ctx)` | the single public function — the forward pass + the 7-metric dict; NO `@validate_call` (the rlm_gradient function-only shape over an already-validated context) |

## Architecture

- `validate_model` (L46-152): the long docstring (L47-104)
  explains the Z-space metric semantics (MAE / MSE / RMSE; the
  RMSE/MAE = sqrt(π/2) = 1.253 normal-distribution indicator —
  the rlm_02 live ratio is 1.27). The body:
  - `vld_indexes = ctx.feature_set.compute_indexes(vld_positions)`
    (L110, the SAME feature_set as training) + `vld_M, _ =
    vld_indexes.shape` (L111 — the D-102 M2 underscore unpack).
  - The dense mapping (L115-119): `col_offsets =
    np.repeat(ctx.iwmap_feature_offset[:-1],
    n_instances_per_feature)` then `dense_indices = vld_indexes +
    col_offsets` (the fancy-index idiom — contrast
    rlm_generate's per-feature loop, both valid) and
    `linear_predictor = np.sum(ctx.w_dense[dense_indices],
    axis=1)` (L123).
  - The forward pass (L124-127): `z_pred = sigmoid(linear_
    predictor)` (the rlm_gradient sigmoid REUSE, L34) +
    `vld_z = ctx.y2z(vld_game_values)` (L127 — `y2z` does
    `y = np.float32(y)` BEFORE the affine, so the int8
    `vld_game_values` never overflow).
  - The Z metrics (L130-134) + the Y metrics (L138-142,
    `y_pred = ctx.z2y(z_pred)`) + the 7-key return (L144-152) —
    every value `float(...)`-cast except `vld_samples`
    (`int(M)`); `vld_mse_y` is the 6th metric since D-102 M3
    (between `vld_mae_y` and `vld_rmse_y`).
- Imports (L28-38): `Any` in the typing line (the D-102 R1
  fix — the unimported `Any` was a PEP-563-masked latent
  NameError under `typing.get_type_hints`; NO live crash, nothing
  calls it), NO regab import (D-102 T2 — the data comes from
  `ctx.vld_positions` / `ctx.vld_game_values`, never a DB call),
  the file header carries its OWN name (the D-102 T3 fix — the
  bring-in said `rlm_config_schemas.py`, copy-paste).

## Verified invariants

Pinned by the 18-check `probes/verify_validate.py` +
`test_lm_worker_validate.py` (5 tests: 2 DB-free + 3 DB-gated).

- Module + worker source shape (probe A1-A13, 14 checks): the
  single-name `__all__`, the header name, the `Any` import, NO
  regab import, the `sigmoid` reuse, NO cache_manager import,
  the 7-key dict, the underscore unpack, 0 non-comment trailing-
  ws lines.
- The live rlm_02 invariants (probe C4/C5): the internal
  consistency (mse_z == 2·vld_loss, rmse_y² == mse_y) and the
  NO rlmwf_12* file in the base dir.
- The live rlm_02 goldens (the worker suite, first run to
  VALIDATE, step 12; bid [8] validation vs the bid [6,7]
  training model): `vld_loss 0.00700794393196702`,
  `vld_mse_z 0.01401588786393404`, `vld_mae_z
  0.09311295300722122`, `vld_mae_y 12.161691665649414`,
  `vld_mse_y 239.10484313964844`, `vld_rmse_y
  15.46301555633545`, `vld_samples 200`; the validation loss ≈
  the training final loss (7.1250e-03 — no overfitting signal).
- The unit metric math (TestValidateModelUnit, the D-106 step-3
  conversion of probe D1/D3, DB-free): the hand-computed 2-
  position case (1 feature / 2 instances, `w_dense [0.5, −0.5]`,
  game values [0, 64]) → loss 0.0625, mse_z 0.125, mae_z 0.25,
  mae_y 32.0, mse_y 2048.0, rmse_y sqrt(2048), samples 2; every
  metric a PYTHON float (the float() casts) + `vld_samples` an
  int (probe D2).

## Open issues

None.

## Conventions

- No init validation, no `@validate_call`: single function over
  an already-validated context — the `ctx: "RLMContext"` string
  annotation + TYPE_CHECKING import is the house pattern for the
  circular constraint.
- The dense-mapping idiom (`np.repeat` + fancy indexing +
  `np.sum`) differs from rlm_generate's per-feature start/end
  loop — both valid, left as is (report-only, no number).
- The `y2z` float32 cast before the affine is what keeps the
  int8 `vld_game_values` overflow-free (a raw `int8 + 64` at y=64
  would wrap to −128) — the test fakes mirror the cast.

## Integration

- Upstream inputs (guaranteed by the SM half-open interval
  semantics on an up-move to step 12): VLD_POSITIONS
  (`ctx.vld_positions` (200, uint64), `ctx.vld_game_values`
  (200,) int8, `ctx.vld_rds_checksum`), FEATURES
  (`ctx.feature_set`), WMAPS (`ctx.iwmap_feature_offset`),
  GENERATE (`ctx.w_dense` (6588,) float32), ZED (`ctx.y2z` /
  `ctx.z2y`).
- Downstream: ANALYTICS consumes `ctx.vld_metrics` (the
  `ctx.analytics_report` blackboard field is pre-declared,
  logistic_model L155).
- No `use_cache` interaction: the level writes nothing, so the
  CONFIG cache switch is irrelevant here.
