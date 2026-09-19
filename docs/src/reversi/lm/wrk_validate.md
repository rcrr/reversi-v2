# reversi/lm/wrk_validate.py
The VALIDATE worker — the 14th step. A non-cache worker (like FEATURES, EFFECT_SIZE, ZED, GRADIENT): no `cache_manager`
wiring at all — no load-or-compute cycle, no `is_allowed` switch, no cache file (the level is recomputed on every
up-move, so the rlmwf_14 slot stays unused). The machine contract: `_up` publishes the validation outputs — the 7-key
metrics dict plus the I-018 series and records — and logs the metric block and the top-20 extreme-residual report;
`_down` clears the four attributes.

## API

| name | contract |
|---|---|
| `wrk_validate()` | the factory — `@validate_call(config=ConfigDict(arbitrary_types_allowed=True))` (the uniform worker-factory gate) returning `Worker("VALIDATE", _up, _down)` |

## Architecture

- `_up`: logs "Starting model validation...", calls `validate_model(ctx)` once and publishes
  `ctx.vld_metrics = result.metrics`, `ctx.vld_y_pred = result.y_pred`, `ctx.vld_rn = result.rn_y` and
  `ctx.vld_outliers = _outlier_records(...)`; then the 6 metric INFO lines (the completion line at .8e, MSE/MAE at .4e,
  MAE(y)/RMSE(y) at .2f, and the RMSE/MAE ratio at .2f — the last one ZERO-GUARDED: a perfect Y-space fit logs "n/a
  (vld_mae_y is 0 — perfect Y-space fit)" instead of dividing by zero).
- The top-20 extreme-residual report (the I-018 design — it belongs to the level that COMPUTES the residuals): the
  header line + 20 lines carrying the rank, the validation index, the position's bitboards, the game value, the fitted
  value and the residual. The order is `hlp_validate.top_outliers`, so it is deterministic.
- `_outlier_records`: the 20 records as raw values (index, mover, opponent, game_value, fitted, residual) — the data
  behind the report, published for the levels that consume it.
- `_down`: logs "Clearing validation attributes..." and clears the four attributes.
- Imports: `pydantic`, `Worker` / `Relevance`, the hlp_validate names, `LMContext` under TYPE_CHECKING. NO
  `reversi.tools.cache_manager` import and NO numpy import (the worker does no numerics — the series arrive typed from
  the data module).

## Verified invariants

Pinned by the `probes/verify_validate.py` sweep + `test_wrk_validate.py`.

- The worker shape (probe A1-A13): `__all__ = ['wrk_validate']`, the factory WITH `@validate_call` + the pydantic
  import, NO numpy import, NO cache_manager import, `_up` publishing the four attributes, `_down` clearing exactly them,
  `Worker("VALIDATE", _up, _down)`, no non-comment trailing-whitespace lines.
- The live rlm_02 flow (probe C-tier + the worker suite): the full pipeline through VALIDATE (no crash), the 7 metric
  goldens, the log lines (incl. "RMSE/MAE: 1.27" — the docstring indicator is 1.253), NO rlmwf_14* file (probe C5), and
  the second instance: identical metrics (a deterministic recompute) + no DB re-extraction + exactly 6 "Cache
  successfully loaded and validated" hits (the 6 cache_manager levels).
- The report (I-018): the header + exactly 20 "vld position" lines, the |residual| non-increasing down the list, and the
  published records in the same order (the stable tie-break: a |24| tie keeps the lower index first) —
  `test_up_outlier_report`.
- The `_down` scope: back to VLD_POSITIONS clears the four attributes (the test pins `vld_metrics`; the code clears all
  four).
- The zero-guard branch is unit-tested DB-free on a REAL LMContext (`Worker.up` is `@validate_call`-gated with
  `context: Context`, so a SimpleNamespace is rejected) — `test_rmse_mae_line_is_zero_guarded`.

## Open issues

None.

## Conventions

- The no-cache design is a deviation from the uniform `cache_manager` wiring — intentional: the rlmwf_14 slot stays
  unused.
- The worker does no numerics: the series arrive from `hlp_validate` and the worker only publishes, records and logs
  (hence no numpy import).
- Where the cache levels pin "hit + no recompute", the second-instance test pins "recompute + identical result + the 6
  sibling cache hits".

## Integration

- Pipeline ordering: VALIDATE is the 14th step; its inputs come from VLD_POSITIONS (`ctx.vld_positions`,
  `ctx.vld_game_values`), FEATURES (`ctx.feature_set`), WMAPS (`ctx.iwmap_feature_offset`), GENERATE (`ctx.w_dense`) and
  ZED (`ctx.y2z` / `ctx.z2y`).
- Downstream: ANALYTICS consumes `ctx.vld_metrics`; PLOT consumes `ctx.vld_y_pred` / `ctx.vld_rn` (the figures) and
  CLIENT_CHECK `ctx.vld_rn` (the in-memory reference) — I-018.
- No `use_cache` interaction: with `ctx.use_cache=False` the other levels still warm their cache files; VALIDATE has
  nothing to warm.
