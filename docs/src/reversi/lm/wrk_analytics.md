# reversi/lm/wrk_analytics.py
The ANALYTICS worker — the 15th step. A non-cache worker — no `cache_manager` wiring at all (no load-or-compute cycle,
no rlmwf_15* file, confirmed live). Pure compute on every up-move: it recomputes the training metrics (compressed +
dense passes), logs the console report line by line, and writes the complete file report to
`base_dir/<cfg.analytics.report_file_name>` (plain text, overwritten every run — the OPTIMIZE-checkpoint artifact
semantics; `_down` does NOT unlink it). The machine contract: `_up` publishes the FOUR context attributes
`ctx.train_metrics` (the 7-key dict), `ctx.train_dense_metrics` (the 4-key dense-pass dict), `ctx.train_dense_rn`
(the dense residual series) and `ctx.analytics_report` (the console report string); `_down` clears all four.

## API

| name | contract |
|---|---|
| `wrk_analytics()` | the factory — `@validate_call(config=ConfigDict(arbitrary_types_allowed=True))` (all 17 sibling worker factories share the pattern) returning `Worker("ANALYTICS", _up, _down)` |

## Architecture

89 lines.

- Imports: pydantic, `Worker, Relevance`, the 4 public data functions from hlp_analytics, `LMContext` under
  TYPE_CHECKING. NO `reversi.tools.cache_manager` import (by design).
- `_up`: `log_event(INFO, "Generating model analytics report...")`; `ctx.train_metrics = compute_training_metrics(ctx)`
  (pre-declared on LMContext); `dense = compute_training_dense_metrics(ctx)` → `ctx.train_dense_metrics = dense.metrics`
  + `ctx.train_dense_rn = dense.rn_y` (both pre-declared on LMContext); `console_report = format_console_report(ctx)`;
  the 18 header lines logged line by line; `file_report = format_file_report(ctx)` written to
  `ctx.cfg.base_dir / ctx.cfg.analytics.report_file_name`; `log_event(INFO, "Analytics report saved to ...")`;
  publishes `ctx.analytics_report = console_report` ("Store in context if needed by the SAVE worker later").
- `_down`: logs "Clearing analytics attributes..." then clears the FOUR attributes to None — the scope is complete:
  `_up` sets exactly `analytics_report` + `train_metrics` + `train_dense_metrics` + `train_dense_rn` (pinned by probe
  A8 + `test_down_clears_analytics_attributes`).
- `wrk_analytics()`: the factory, `@validate_call`-decorated.

## Verified invariants

Pinned by the 36-check `probes/verify_analytics.py` + the 4-test worker suite (2 classes, all DB-gated).

- Source shape (probe A-tier): the 89-line file, `__all__ = ['wrk_analytics']`, the factory WITH `@validate_call` + the
  pydantic import, NO pathlib import, NO cache_manager import (A9), `_up` sets the 4 ctx attributes, `_down` clears all
  four, `Worker("ANALYTICS", ...)`, 0 non-comment trailing-ws lines.
- The live rlm_02 flow (probe C-tier + the suite): the full pipeline through ANALYTICS (step 15, no crash) with the
  22-line log span (the 2 worker INFO lines as endpoints, the 2 data-module INFO lines + 18 header lines between
  them); the 7-metric + 4-key
  dense goldens (the module doc's live invariants); the file report at `base_dir/model_analytics_report.txt`
  byte-deterministic (date-masked sha3_256 `94a4af7e5ca554e6f8b219cf5ed820e45e102489dacdc25e15d2b263158120b0` —
  C5a/C5b); NO rlmwf_15* file and the rlmwf_* set unchanged (C7/C7b); the 2nd instance: identical 3 attributes
  (deterministic recompute; C8 compares the 3 — the 4th, `train_dense_rn`, is not compared) + no DB re-extraction +
  exactly 6 "Cache successfully loaded and validated" hits (the 6 cache_manager levels; CONFIG + the OPTIMIZE
  checkpoint have their own load flows) (C8); the `_down` clearing of all 4 attributes (C9 pins the 3 — `train_dense_rn`
  is A8's source-level pin); the header's Generalization Gap = vld_rmse_y − train_dense_rmse_y (dense-vs-dense, C11) and
  Substitution Delta = train_dense_rmse_y − train_rmse_y ("−0.00" at rlm_02's cut 1, C11b).
- The rlm_01 mobility table (the Mobility test class): the `MOBILITY FEATURE: LMC (fid=1)` table exercises the helper
  end-to-end (65 rows — the only fixture that does), the gap 23.87 + the Substitution Delta 3.36 (the true
  compressed-vs-dense cost at cut 2), the file-report mask
  `f6b54954a3c54d13a9a3b3e65face75a5bd709899050c0b77b236a8955cf4c8c`.

## Open issues

None.

## Conventions

- The no-cache design is a deviation from the uniform 7-kwargs `cache_manager` wiring — intentional (the rlmwf_15 slot
  stays unused like 02/09/10).
- The 2 data-module INFO lines come from hlp_analytics (compute_training_metrics + compute_training_dense_metrics) —
  consistent with hlp_validate.
- `Worker.up` is `@validate_call`-gated with `context: Context` (state_machine): a bare SimpleNamespace is rejected (the
  D-tier probe fakes use it only for the data functions).

## Integration

- Pipeline ordering: ANALYTICS is step 15 of 18; its inputs come from every upstream level (the field list in the
  hlp_analytics doc) — the SM half-open interval semantics guarantee every up-move to step 15 passes through all of
  them. The test setUp moves through VALIDATE (step 14) first, so the full 15-level chain is exercised end-to-end on the
  live DB.
- Downstream: SAVE (step 16) consumes `ctx.vld_metrics` + `ctx.training_pop_stats` + `ctx.opt_info` for the
  model_weights file (the worker's "Store in context if needed by the SAVE worker later" comment).
