<!-- ARCHIVED — D-106 step 18 (the docs/ rewrite, 2026-09-04): the
     complete session-28 analysis (D-101) + the D-102
     fix-campaign narrative moved out of
     docs/src/twolm/rlm_validate.md per docs_rules.md
     §1/§4. This is a frozen historical record: it is never
     updated. Stale-in-current-context notes: (1) the "28 checks"
     figure — the current probes/verify_validate.py (the 4091e72
     move) has 18 surviving check calls: A1-A13 (module + worker
     source shape, 14 — incl. A7a/A7b), B4 (context fact), C4 +
     C5 (live-DB invariants: the internal-consistency
     mse_z == 2·vld_loss + rmse_y² == mse_y, and the NO
     rlmwf_12* file), D2 (the float() type pins). The D-106 step-3
     deletions/conversions: B1-B3 pipeline-state pins → the hub
     verify_logistic_model.py; C1 (bootstrap step 12) + C2 (the
     7-key dict + exact goldens) + C3 (the 5 log lines) + C6
     (2nd-instance determinism + the 6 cache hits) + C7 (the
     _down scope) → test_lm_worker_validate; D1 (the hand-
     computed 2-position metric math) + D3 (the M1 zero-guard n/a
     line) → TestValidateModelUnit in the same file (class a §4
     conversion — the suite grew 3 → 5 tests at 7964b96). (2)
     the "622 tests / 80 skipped" full-discover figure predates
     steps 3-17 (current: 664/87 gated); (3) the D-101/D-102
     campaign narrative (R1 the PEP-563-masked Any, T1-T5,
     M1-M3) is frozen history. -->

# twolm/rlm_validate.py

Analysis date: 2026-09-02 — analysis session 28 (D-101, the
VALIDATE bring-in, Roberto's commit 536eadc); fix campaign D-102
approved by Roberto ("R1: OK, T1: OK, T2: OK, T3, T4: OK, T5: OK,
M1-M3: OK. Procedi") and applied in the same session. Brought in by
Roberto (536eadc) alongside lm_worker_validate — the FIRST
bring-in with a dedicated data module for a non-cache pipeline
level.

`validate_model(ctx) -> Dict[str, Any]` — the single public function
(`__all__ = ['validate_model']`, L42). It runs the forward pass of
the trained model on the validation positions (the same
`ctx.feature_set` as training, the dense weights `ctx.w_dense` from
GENERATE) and returns the 7-metric validation dict (post D-102 M3):
the Z-space metrics (`vld_loss` = 0.5·‖rn_z‖²/M, `vld_mse_z` =
‖rn_z‖²/M = 2·loss, `vld_mae_z` = mean|rn_z|) and the Y-space
metrics (`vld_mae_y`, `vld_mse_y`, `vld_rmse_y` — the predictions
mapped back with `ctx.z2y`), plus `vld_samples` = M. No store /
load / is_cache_consistent trio, no data class, no checksum: the
level is pure compute (the rlmwf_12 slot stays unused — unlike every
other rlm_* level except rlm_zed / rlm_gradient).

## Suite status (session 28, post D-102)

No dedicated data-object suite: `validate_model` is covered
end-to-end by `test_lm_worker_validate` (3/0/0 live, 3/0/3 gated)
and by the probe D-tier (the hand-computed 2-position math re-derived
independently, no DB). The contrast with rlm_zed / rlm_gradient
(which got dedicated suites in D-092/D-094) is deliberate scope:
Roberto approved exactly 1 class / 3 tests for the worker (D-102
T5), and the metric math is the D3-tier unit fact.

## State per Roberto

Pipeline-in-progress, 13 active levels. The next line-by-line step
is `lm_worker_analytics` (the next commented entry, logistic_model
L53). rlm_validate fix campaign (D-102) CLOSED: R1 (the unimported
`Any`), T2 (the 2 dead regab imports), T3 (the wrong header name),
T4 (27 ws lines), M2 (the unused `vld_P`), M3 (`vld_mse_y` added to
the dict) — all applied.

## Architecture (152 lines, post D-102)

- Imports (L28-38): `numpy as np` (L30), `TYPE_CHECKING, Any, Dict`
  (L32 — `Any` added in D-102 R1), `sigmoid` from rlm_gradient
  (L34 — REUSED, not re-implemented), `Relevance` from
  state_machine (L35), `RLMContext` under TYPE_CHECKING (L37-38).
  The dead `RegabDBConnection, regab_extract_data_set_from_db`
  import (bring-in L36) removed in D-102 T2 — the data comes from
  `ctx.vld_positions` / `ctx.vld_game_values` (set by
  VLD_POSITIONS), never from a DB call.
- `validate_model` (L46-152): the long docstring (L47-104) explains
  the Z-space metric semantics (MAE/MSE/RMSE, the
  RMSE/MAE = sqrt(π/2) = 1.253 normal-distribution indicator — the
  rlm_02 live ratio is 1.27). The body: `vld_indexes =
  ctx.feature_set.compute_indexes(vld_positions)` (L111, the SAME
  feature_set as training); `vld_M, _ = vld_indexes.shape` (L112 —
  D-102 M2); the dense mapping (L116-120): `col_offsets =
  np.repeat(ctx.iwmap_feature_offset[:-1], n_instances_per_feature)`
  then `dense_indices = vld_indexes + col_offsets` (the fancy-index
  idiom — contrast rlm_generate's per-feature loop, both valid);
  `linear_predictor = np.sum(ctx.w_dense[dense_indices], axis=1)`
  (L124); `z_pred = sigmoid(linear_predictor)` (L125);
  `vld_z = ctx.y2z(vld_game_values)` (L128); the Z metrics
  (L131-135); the Y metrics (L139-143, `y_pred = ctx.z2y(z_pred)`);
  the 7-key return (L145-152) — every value `float(...)`-cast except
  `vld_samples` (`int(M)`).
- No init validation, no `@validate_call`: single function over an
  already-validated context (the rlm_gradient function-only shape);
  the `ctx: "RLMContext"` string annotation + TYPE_CHECKING import
  is the house pattern for the TYPE_CHECKING circular constraint.

## Verified facts (D-101/D-102 probe — 28 checks, 0 mismatches)

The A-tier pins the structure: `__all__` (L42); the header carries
its OWN name `# rlm_validate.py` (L2 — the bring-in said
`rlm_config_schemas.py`, copy-paste; D-102 T3); `Any` imported
(R1); NO regab import (T2); the `sigmoid` REUSE (A10); NO
cache_manager (A11); the 7-key dict (A12 — post M3); the underscore
unpack (A13 — post M2); 0 non-comment trailing-whitespace lines
(A7b — post T4; the 27 bring-in lines were the docstring trailing
ws + the docstring ws-only lines + L107/L117). The C-tier pins the
live goldens (see lm_worker_validate V2); the D-tier re-derives the
full metric math on a hand-computed 2-position case (loss 0.0625,
mse_z 0.125, mae_z 0.25, mae_y 32.0, mse_y 2048.0, rmse_y
sqrt(2048), samples 2) + the float() type pins.

- V1 (R1 context): the unimported `Any` was a PEP 563-masked latent
  NameError under `typing.get_type_hints(validate_model)` (the
  D-074 R2 class). Unlike D-097/D-099 there was NO live crash:
  nothing in src/ calls `get_type_hints` on `validate_model`, and
  VALIDATE has no cache-path call, so the pipeline reaches step 12
  cleanly (the D-074 R1 `_for_next_level` trap does not apply).

## Minor notes

- **M2 (FIXED, D-102)** — `vld_P` (the feature-instance count) was
  unpacked from `vld_indexes.shape` but never used → underscore
  (`vld_M, _ = ...`, the D-096 M1 pattern).
- **M3 (FIXED, D-102)** — `vld_mse_y` was computed (L142) but
  omitted from the returned dict — it only fed `rmse_y`. Roberto's
  call: it belongs in the dict (the 7th key, between `vld_mae_y`
  and `vld_rmse_y`).
- **Report-only (no number):** the dense-mapping idiom
  (`np.repeat` + fancy indexing + `np.sum`) differs from
  rlm_generate's per-feature start/end loop — both valid, left as
  is.
- **Report-only (no number):** the Zed `y2z` cast — `y2z` does
  `y = np.float32(y)` BEFORE the affine, so the int8
  `vld_game_values` never overflow (a raw `int8 + 64` at y=64 would
  wrap to −128 — the probe's fake lambdas mirror the cast).

## Integration notes

- Upstream inputs (all guaranteed by the SM half-open interval
  semantics on an up-move to step 12): VLD_POSITIONS
  (`ctx.vld_positions` (200, uint64), `ctx.vld_game_values` (200,)
  int8, `ctx.vld_rds_checksum`), FEATURES (`ctx.feature_set`), WMAPS
  (`ctx.iwmap_feature_offset`), GENERATE (`ctx.w_dense` (6588,)
  float32), ZED (`ctx.y2z` / `ctx.z2y`).
- The `sigmoid` reuse from rlm_gradient keeps a single source of the
  scipy `expit` wrapper (A10).
- No `use_cache` interaction: the level writes nothing, so the
  CONFIG cache switch is irrelevant here.
- Downstream: ANALYTICS (the next commented level) will consume
  `ctx.vld_metrics` (the `ctx.analytics_report` blackboard field is
  pre-declared, logistic_model L155).

## Appendix — line reference

152 lines, as of D-102 (152 at the 536eadc bring-in; D-102: −1
import line [T2] + 1 dict line [M3], 27 ws lines stripped in place
[T4] — net 0).

- L2: the file name (T3)
- L28-38: imports (numpy L30, typing L32 [R1], rlm_gradient L34,
  state_machine L35, TYPE_CHECKING L37-38)
- L42: `__all__`
- L46-152: `validate_model` (L47-104 the metrics docstring,
  L106-107 the ctx reads, L111 the index compute, L112 the M2
  unpack, L116-120 the dense mapping, L124-128 the forward pass,
  L131-135 the Z metrics, L139-143 the Y metrics, L145-152 the
  7-key return — L149 the M3 `vld_mse_y` line)
