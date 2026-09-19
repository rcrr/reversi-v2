# reversi/lm/wrk_analytics.py
The ANALYTICS worker — the 15th step. The FIFTH non-cache worker (after FEATURES, ZED, GRADIENT, VALIDATE) — no
`cache_manager` wiring at all (no load-or-compute cycle, no rlmwf_15* file, confirmed live). Pure compute on every
up-move: it recomputes the training metrics (compressed + dense passes), logs the console report line by line, and
writes the complete file report to `base_dir/<cfg.analytics.report_file_name>` (plain text, overwritten every run — the
OPTIMIZE-checkpoint artifact semantics; `_down` does NOT unlink it). The machine contract: `_up` publishes the THREE
context attributes `ctx.train_metrics` (the 7-key dict), `ctx.train_dense_metrics` (the 4-key dense-pass dict) and
`ctx.analytics_report` (the console report string); `_down` clears all three.

## API

| name | contract |
|---|---|
| `wrk_analytics()` | the factory — `@validate_call(config=ConfigDict(arbitrary_types_allowed=True))` (all 14 sibling worker factories share the pattern) returning `Worker("ANALYTICS", _up, _down)` |

## Architecture

86 lines.

- Imports (L28-38): pydantic (L30), `Worker, Relevance` (L34), the 4 public data functions from hlp_analytics (L35-37),
  `LMContext` under TYPE_CHECKING (L37-38). NO `reversi.tools.cache_manager` import (by design).
- `_up` (L48-73): `log_event(INFO, "Generating model analytics report...")` (L49);
  `ctx.train_metrics = compute_training_metrics(ctx)` (L54 — pre-declared on LMContext L155);
  `ctx.train_dense_metrics = compute_training_dense_metrics(ctx)` (L55 — pre-declared on LMContext L156);
  `console_report = format_console_report(ctx)` (L58); the 17 header lines logged line by line (L61-62);
  `file_report = format_file_report(ctx)` (L65) written to `ctx.cfg.base_dir / ctx.cfg.analytics.report_file_name`
  (L66-69); `log_event(INFO, "Analytics report saved to ...")` (L71); publishes `ctx.analytics_report = console_report`
  (L73, "Store in context if needed by the SAVE worker later").
- `_down` (L75-79): logs "Clearing analytics attributes..." then clears the THREE attributes to None (L77-79) — the
  scope is complete: `_up` sets exactly `analytics_report` + `train_metrics` + `train_dense_metrics` (pinned by probe A8
  + `test_down_clears_analytics_attributes`).
- `wrk_analytics()` (L82-85): the factory, `@validate_call`-decorated.

## Verified invariants

Pinned by the 36-check `probes/verify_analytics.py` + the 4-test worker suite (2 classes, all DB-gated).

- Source shape (probe A-tier): the 86-line file, `__all__ = ['wrk_analytics']`, the factory WITH `@validate_call` + the
  pydantic import, NO pathlib import, NO cache_manager import (A9), `_up` sets the 3 ctx attributes, `_down` clears all
  three, `Worker("ANALYTICS", ...)`, 0 non-comment trailing-ws lines.
- The live rlm_02 flow (probe C-tier + the suite): the full pipeline through ANALYTICS (step 15, no crash) with the
  21-line log span (2 data-module INFO lines + 17 header lines between the two worker INFO lines); the 7-metric + 4-key
  dense goldens (the module doc's live invariants); the file report at `base_dir/model_analytics_report.txt`
  byte-deterministic (date-masked sha3_256 `94a4af7e5ca554e6f8b219cf5ed820e45e102489dacdc25e15d2b263158120b0` —
  C5a/C5b); NO rlmwf_15* file and the rlmwf_* set unchanged (C7/C7b); the 2nd instance: identical 3 attributes
  (deterministic recompute) + no DB re-extraction + exactly 6 "Cache successfully loaded and validated" hits (the 6
  cache_manager levels; CONFIG + the OPTIMIZE checkpoint have their own load flows) (C8); the `_down` clearing of all 3
  attributes (C9); the header's Generalization Gap = vld_rmse_y − train_dense_rmse_y (dense-vs-dense, C11) and
  Substitution Delta = train_dense_rmse_y − train_rmse_y ("−0.00" at rlm_02's cut 1, C11b).
- The rlm_01 mobility table (the Mobility test class): the `MOBILITY FEATURE: LMC (fid=1)` table exercises the helper
  end-to-end (65 rows — the only fixture that does), the gap 23.87 + the Substitution Delta 3.36 (the true
  compressed-vs-dense cost at cut 2), the file-report mask
  `f6b54954a3c54d13a9a3b3e65face75a5bd709899050c0b77b236a8955cf4c8c`.

## Open issues

None.

## Conventions

- The no-cache design is the fifth deviation from the uniform 7-kwargs `cache_manager` wiring — intentional (the
  rlmwf_15 slot stays unused like 02/09/10).
- The 2 data-module INFO lines come from hlp_analytics (compute_training_metrics + compute_training_dense_metrics) —
  consistent with hlp_validate.
- `Worker.up` is `@validate_call`-gated with `context: Context` (state_machine L87-90): a bare SimpleNamespace is
  rejected (the D-tier probe fakes use it only for the data functions).

## Integration

- Pipeline ordering: ANALYTICS is level 14 of 15 (COMPLETE); its inputs come from every upstream level (the field list
  in the hlp_analytics doc) — the SM half-open interval semantics guarantee every up-move to step 15 passes through all
  of them. The test setUp moves through VALIDATE (step 14) first, so the full 15-level chain is exercised end-to-end on
  the live DB.
- Downstream: SAVE (level 15, active) consumes `ctx.vld_metrics` + `ctx.training_pop_stats` + `ctx.opt_info` for the
  model_weights file (the worker's "Store in context if needed by the SAVE worker later" comment).
