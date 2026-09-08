# twolm/lm_worker_validate.py
The VALIDATE worker — the 13th active level (the 12th step). The
THIRD non-cache worker (after FEATURES, ZED, GRADIENT): no
`cache_manager` wiring at all — no load-or-compute cycle, no
`is_allowed` switch, no rlmwf_12* file (the level is recomputed
on every up-move: a pure forward pass over the validation
positions with the optimized `ctx.w_dense`, so the rlmwf_12 slot
stays unused — the flat-file numbering skips 12 like it skipped
03/07/08). The machine contract: `_up` publishes the ONE context
attribute `ctx.vld_metrics` (the 7-key metrics dict), `_down`
clears it.
> State: D-102 · b98edaa · 2026-09-02 · suite 3/0/0 (3 DB-gated)

## API

| name | contract |
|---|---|
| `lm_worker_validate()` | the factory — `@validate_call(config=ConfigDict(arbitrary_types_allowed=True))` (D-102 T1, all 12 active worker factories now share the pattern) returning `Worker("VALIDATE", _up, _down)` |

## Architecture

- Imports (L28-38): `pydantic` (L30 — the D-102 T1/T2 shape: the
  dead `numpy as np` import replaced by the pydantic line),
  `Worker, Relevance` (L34), `validate_model` (L35),
  `RLMContext` under TYPE_CHECKING (L37-38). NO
  `reversi.tools.cache_manager` import (by design).
- `_up` (L46-62): `log_event(INFO, "Starting model
  validation...")` (L47); `metrics = validate_model(ctx)` (L49);
  publishes `ctx.vld_metrics = metrics` (L50); then 7 INFO log
  lines (L52-60): the completion line ("Validation completed.
  Loss (MSE/2): ...", .8e format), MSE/MAE (.4e), MAE(y)/RMSE(y)
  (.2f), and the RMSE/MAE ratio (.2f) — the last one
  ZERO-GUARDED since D-102 M1 (L57-60): a perfect Y-space fit
  (`vld_mae_y == 0`) logs the "n/a (vld_mae_y is 0 — perfect
  Y-space fit)" line instead of dividing by zero (pre-campaign
  the same case raised ZeroDivisionError in the `_up` log line).
- `_down` (L65-69): logs "Clearing validation attributes..."
  then clears the ONE attribute to None (L67) — the scope is
  complete: `_up` sets exactly `vld_metrics` (pinned by probe
  A9 + `test_down_clears_vld_metrics`).
- `lm_worker_validate()` (L72-75): the factory,
  `@validate_call`-decorated since D-102 T1.

## Verified invariants

Pinned by the `probes/verify_validate.py` A + C tiers + the
3-test worker suite.

- Worker source shape (probe A-tier, with the module tier): the
  75-line file, `__all__ = ['lm_worker_validate']`, the factory
  WITH `@validate_call` + the pydantic import (T1), NO numpy
  import (T2), `validate_model` the single data name, NO
  cache_manager import, `_up` sets the 1 ctx attribute, `_down`
  clears it, `Worker("VALIDATE", ...)`, 0 non-comment trailing-
  ws lines.
- The live rlm_02 flow (probe C-tier + the worker suite): the
  full pipeline through VALIDATE (step 12, no crash — unlike
  D-097/D-099 there is no cache-path trap this time); the 7
  metric goldens are pinned in test_lm_worker_validate
  (vld_loss 0.00700794393196702, vld_mse_z
  0.01401588786393404, vld_mae_z 0.09311295300722122,
  vld_mae_y 12.161691665649414, vld_mse_y 239.10484313964844,
  vld_rmse_y 15.46301555633545, vld_samples 200 — bid [8]
  validation vs the bid [6,7] training model); the 7 INFO log
  lines (incl. "RMSE/MAE: 1.27" — the docstring normal-
  distribution indicator is 1.253); the NO rlmwf_12* file
  (probe C5); the second instance: identical metrics
  (deterministic recompute) + no DB re-extraction + exactly 6
  "Cache successfully loaded and validated" hits (the 6
  cache_manager levels — CONFIG and the OPTIMIZE checkpoint have
  their own load flows).
- The M1 zero-guard branch is unit-tested DB-free (the D-106
  step-3 conversion of probe D3 →
  `TestValidateModelUnit::test_rmse_mae_line_is_zero_guarded`, a
  REAL RLMContext — `Worker.up` is `@validate_call`-gated with
  `context: Context`, state_machine L87-90, so a SimpleNamespace
  is rejected).

## Open issues

None.

## Conventions

- The no-cache design is the third deviation from the uniform
  7-kwargs `cache_manager` wiring — intentional and confirmed by
  Roberto (the D-101 bring-in analysis asked whether it was by
  design; confirmed: the rlmwf_12 slot stays unused).
- The no-cache twin of the cache workers: where the cache levels
  pin "hit + no recompute", the second-instance test pins
  "recompute + identical result + the 6 sibling cache hits"
  (VALIDATE has no cache file to hit, so determinism is the pin).

## Integration

- Pipeline ordering: VALIDATE is the 12th step; its inputs come
  from VLD_POSITIONS (`ctx.vld_positions`,
  `ctx.vld_game_values`), FEATURES (`ctx.feature_set`), WMAPS
  (`ctx.iwmap_feature_offset`), GENERATE (`ctx.w_dense`), ZED
  (`ctx.y2z` / `ctx.z2y`) — the SM half-open interval semantics
  guarantee every up-move to step 12 passes through all five.
  The test setUp moves through VLD_POSITIONS (step 11) first, so
  the full 13-level chain is exercised end-to-end on the live
  DB.
- Downstream: ANALYTICS consumes `ctx.vld_metrics` (the
  `ctx.analytics_report` blackboard field is pre-declared,
  logistic_model L155).
- No `use_cache` interaction: with `ctx.use_cache=False` the
  other levels still warm their cache files; VALIDATE has
  nothing to warm — identical behavior either way.
