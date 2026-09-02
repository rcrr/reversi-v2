# twolm/lm_worker_analytics.py

Analysis date: 2026-09-02 — analysis session 28 (D-103, the
ANALYTICS bring-in, Roberto's commit 96dacb5); fix campaign D-103
approved by Roberto ("T1: OK, T2: OK, T4: OK, T5: OK, T6: OK,
M1-M3: OK. Procedi!") and applied in the same session. Brought in
by Roberto (96dacb5 — the 14th active level of the pipeline, the
2nd bring-in with a dedicated data module `rlm_analytics.py` besides
the worker — function-only, no data class).

The ANALYTICS worker of the RLM pipeline: the FIFTH non-cache worker
(after FEATURES, ZED, GRADIENT, VALIDATE) — no `cache_manager`
wiring at all (no load-or-compute cycle, no rlmwf_12* file; the slot
stays unused, confirmed live — probe C7/C7b). The level is pure
compute on every up-move: it recomputes the training metrics, logs
the console report line by line, writes the complete file report to
`base_dir/<cfg.analytics.report_file_name>` (plain text, overwritten
every run — the OPTIMIZE-checkpoint artifact semantics; `_down`
does NOT unlink it). The machine contract: `_up` publishes the TWO
context attributes `ctx.train_metrics` (the 7-key dict) and
`ctx.analytics_report` (the console report string); `_down` clears
both.

## Suite status (session 28, post D-103)

- `test_lm_worker_analytics`: 4/0/0 live (2 classes — the rlm_02
  golden/determinism/_down trio + the rlm_01 mobility-table test;
  all 4 tests DB-gated — the setUp moves through VALIDATE on a fresh
  base dir, so the live regab DB is required; under `SKIP_REGAB_DB=1`
  the 4 tests skip — 4/0/4 gated).
- Full discover: 626 tests, 84 skipped under `SKIP_REGAB_DB=1`,
  GREEN (2.8 s); ungated (live DB): 626 run, 17 skipped, GREEN
  (39.1 s). The full `-W error` discover is clean (38.9 s).

## State per Roberto

Pipeline-in-progress, 14 active levels, enabled by Roberto's
2026-09-02 bring-in (96dacb5). The next line-by-line step is
`lm_worker_save` (the last commented entry, L54 / worker list L221).
ANALYTICS fix campaign (D-103) CLOSED: T1 (factory `@validate_call`
+ pydantic import — all 13 worker factories now uniform), T2 (the
dead `pathlib.Path` import removed here + the dead `sys` /
`Optional` / `List` imports removed in rlm_analytics), T4 (6 ws
lines), T5 (the dedicated test file added), T6 (rlm_01.json
`detailed_report` += "LMC" — the mobility-table branch gets
end-to-end coverage), M1 (RLMContext pre-declares `train_metrics`),
M2/M3 in rlm_analytics. T3 verified no-action (both headers already
carry their own names — unlike D-102's rlm_validate).

## Architecture (80 lines, post D-103)

- Imports (L28-38): `Worker, Relevance` from state_machine (L34),
  the 3 public data functions from rlm_analytics (L35),
  `validate_call, ConfigDict` from pydantic (L30 — added in D-103
  T1, replacing the dead `from pathlib import Path` line — T2),
  `RLMContext` under TYPE_CHECKING (L37-38). NO
  `twolm.cache_manager` import (by design).
- `_up` (L46-68): `log_event(INFO, "Generating model analytics
  report...")` (L47); `ctx.train_metrics = compute_training_metrics
  (ctx)` (L50 — the field is pre-declared on RLMContext L155 since
  D-103 M1); `console_report = format_console_report(ctx)` (L53);
  the 15 header lines logged line by line (L56-57 — "so it shows up
  in the StateMachine logs", per the comment); `file_report =
  format_file_report(ctx)` (L60) written to
  `ctx.cfg.base_dir / ctx.cfg.analytics.report_file_name` (L61-63);
  `log_event(INFO, f"Analytics report saved to ...")` (L65);
  publishes `ctx.analytics_report = console_report` (L68, "Store in
  context if needed by the SAVE worker later").
- `_down` (L70-73): `log_event(INFO, "Clearing analytics
  attributes...")` then clears the TWO attributes to None (L72-73)
  — the scope is complete: `_up` sets exactly `analytics_report` +
  `train_metrics` (pinned by probe A8 and
  test_down_clears_analytics_attributes).
- `lm_worker_analytics()` (L76-79): the factory — `@validate_call
  (config=ConfigDict(arbitrary_types_allowed=True))` since D-103
  T1 (all 13 sibling worker factories share the pattern) — returns
  `Worker("ANALYTICS", _up, _down)` (L79).

## Verified facts (D-103 probe — 33 checks, 0 mismatches)

scratch/verify_analytics.py, tiers A (structure, 12 checks), B
(pipeline state, 5), C (live golden re-derivation, 11, gated on
SKIP_REGAB_DB), D (unit math, no DB, 3). Pre-campaign the probe
reported exactly the 7 worklist mismatches (A2, A3, A4, A6a, A6b,
A11, A12); post D-103 all 33 pass.

- V1 (A-tier): structure — 80 lines; `__all__ =
  ['lm_worker_analytics']` (L42); the factory WITH `@validate_call`
  + the pydantic import (D-103 T1); NO pathlib import (T2); NO
  cache_manager import (A9); `_up` sets the 2 ctx attributes (L50,
  L68); `_down` clears both (L72-73); `Worker("ANALYTICS", ...)`
  (L79); 0 non-comment trailing-whitespace lines (D-103 T4 — 6 pre).
- V2 (B-tier): the import L53 + worker-list entry L220 uncommented;
  1 commented import remains (save, L54); 14 active levels (CREATED
  sentinel + 13 factory calls); the schema `AnalyticsConfig`
  (default factory) makes `ctx.cfg.analytics` always exist — the
  worker's L60 direct access is safe (B5).
- V3 (C-tier, live DB, rlm_02): the full pipeline through ANALYTICS
  (step 13, no crash) with the 7-metric training goldens:
  `train_mae_y 12.346794566613694`, `train_rmse_y
  15.58872172931622`, `train_loss 0.00712497066706419` (=
  `opt_info['f']`, the OPTIMIZE final objective), `train_samples
  199952`, `pop_mae_y 21.729816221648974`, `pop_rmse_y
  26.40637507956623`, `pop_loss 0.020437248051166534` (the bid [6,7]
  training model, 199952 samples). The step-13 log span from
  "Generating model analytics report..." to "Analytics report saved
  to ..." is exactly 18 lines (1 Generating + 1 "Computing metrics
  on the training set..." + 15 header lines + 1 saved). NO rlmwf_12*
  file and the rlmwf_* set unchanged (C7/C7b). Second instance:
  identical metrics + identical console report (deterministic
  recompute) + no DB re-extraction + exactly 6 "Cache successfully
  loaded and validated" hits (C8). The `_down` clearing (C9).
  Independent float64 re-derivation of the training metrics: 0
  mismatch (C10).
- V4 (C-tier, live DB, rlm_02 file report): the file exists at
  `base_dir/model_analytics_report.txt`; structure = header
  (detailed — with the Creation Date) + FEATURE SET SUMMARY +
  MOBILITY FEATURES DETAILS (empty — no mobility features) + PATTERN
  details (EDGE rows printed — in `detailed_report`; DIAG3 rows
  omitted; ELLE/LMC absent from the fixture); date-masked
  sha3_256 golden `9b97746c69436fc23fd4f7a06274174d66ed1d0cb8467619
  b78a409e7f743c66` (C5/C5a/C5b — deterministic, recompute-identical).
- V5 (D-tier, no DB): the full training-metric math on a hand-
  computed 2-position case (predictor 0 → z_pred 0.5 → y_pred 0:
  mae_y 10.0, rmse_y 10.0, train_loss 0.123 = `opt_info['f']`,
  samples 2, pop_mae_y 10.0, pop_rmse_y 10.0, pop_loss
  0.0030517578125); the `opt_info` None branch → train_loss 0.0;
  the console-report N/A branch (vld_metrics None → 3 "N/A" strings,
  gen_gap 0.00, 15 lines).

## Minor notes

- **T3 (verified, no action)** — both file headers already carry
  their own names (unlike D-102's rlm_validate, which carried
  `# rlm_config_schemas.py`).
- **M1 (FIXED, D-103, logistic_model)** — `train_metrics` was set by
  the worker as an ad-hoc dataclass attribute: it works (no
  `__slots__`), but every other blackboard field is pre-declared on
  RLMContext (the D-099 idiom), and the worker's own comment says
  the SAVE worker will consume it later. Now declared (L155).
- **M2 (FIXED, D-103, rlm_analytics)** — the `Dict[str, float]`
  return annotation on compute_training_metrics while
  `train_samples` is an int → `Dict[str, float | int]`.
- **M3 (FIXED, D-103, rlm_analytics)** — the `hasattr(ctx.cfg,
  'analytics')` guard in format_file_report was dead code: the
  schema field is non-optional with a `default_factory`, so the
  attribute always exists and is never None → direct access.
- **Report-only — the mixed-representation Generalization Gap
  (O1, quantified):** the TRAINING column is the COMPRESSED forward
  pass (`ctx.w` over `ctx.design_matrix` — exactly what the
  optimizer trained), the VALIDATION column the DENSE forward pass
  (`ctx.w_dense` — the GENERATE materialization). The two differ
  only for configurations whose orbit was unseen in training
  (dense: orbit frequency-weighted mean / mobility np.interp —
  D-098 R2; compressed: the feature fallback index). Measured on
  rlm_02: 0 of the 1600 validation instances (200 × 8) hit an
  unseen orbit (EDGE seen configs 2963/6561, DIAG3 18/27 cover all
  touched orbits), so the −0.13 gap is a clean train-vs-vld data
  difference there; on sparser datasets the gap would additionally
  carry the substitution delta. Left as-is (documented, not
  changed) — the dense path is the only one that can always run on
  validation data (the compressed design-matrix guard would raise
  on unseen configs).
- Report-only: `compute_training_metrics` logs ONE INFO line from
  the data module — consistent with rlm_validate (3 such lines in
  validate_model).
- Report-only: the 3 public data functions carry NO `@validate_call`
  and no no-validation note (the rlm_indexes-L166 TYPE_CHECKING
  class) — consistent with rlm_validate, approved in D-102 without
  one.
- Report-only: rlm_02's `detailed_report` lists ELLE/LMC — names
  absent from that fixture (harmless; only EDGE matches; the block
  looks copied — the fixture is Roberto's).
- The no-cache design is the fifth deviation from the uniform
  7-kwargs `cache_manager` wiring — intentional and confirmed by
  Roberto (the rlmwf_12 slot stays unused, the flat-file numbering
  will skip 12 like it skipped 03/07/08).

## Integration notes

- Pipeline ordering: ANALYTICS is the 14th level; its inputs come
  from CONFIG (`ctx.cfg` — base_dir, name, analytics, stat_model),
  FEATURES (`ctx.feature_set`), INDEXES (`ctx.rlm_indexes`), WMAPS
  (`ctx.w`, `ctx.iwmap`, `ctx.iwmap_feature_offset`,
  `ctx.feature_w_ranges`, `ctx.wmap`, `ctx.wmap_fallback`),
  DESIGN_MTR (`ctx.design_matrix` — the raw X array), ZED
  (`ctx.z2y`, `ctx.y2z`), OPTIMIZE (`ctx.opt_info`), GENERATE
  (`ctx.w_dense`), VALIDATE (`ctx.vld_metrics` for the header's
  VALIDATION column). The SM half-open interval semantics guarantee
  every up-move to step 13 passes through all of them. The test
  setUp moves through VALIDATE (step 12) first, so the full
  14-level chain is exercised end-to-end on the live DB.
- The `sigmoid` is REUSED from rlm_gradient (defined + exported
  there) — no local copy (rlm_analytics L36).
- `Worker.up` is `@validate_call`-gated with `context: Context`
  (state_machine L87-90): a bare SimpleNamespace is rejected — the
  D-tier probe fakes use SimpleNamespace only for the rlm_analytics
  data functions (which take ctx under TYPE_CHECKING).
- Downstream: SAVE (the last commented level) will consume
  `ctx.train_metrics` + `ctx.analytics_report` (the worker's "Store
  in context if needed by the SAVE worker later" comment).

## Appendix — line reference

80 lines, as of D-103 (78 at the 96dacb5 bring-in; D-103: +1
pydantic import line [T1, replacing the pathlib line — T2], +1
decorator line [T1], 6 ws lines emptied in place [T4]).

- L28-38: imports (pydantic L30 [T1], state_machine L34,
  rlm_analytics L35, TYPE_CHECKING L37-38)
- L42: `__all__`
- L46-68: `_up` (L47 start log, L50 the train_metrics publish,
  L53 the console report, L56-57 the line-by-line log loop, L60-63
  the file report write, L65 the saved log, L68 the
  analytics_report publish)
- L70-73: `_down` (L72-73 the two None clears)
- L76-79: `lm_worker_analytics` (L76 decorator [T1], L79 the Worker)
