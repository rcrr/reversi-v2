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
does NOT unlink it). The machine contract: `_up` publishes the
THREE context attributes `ctx.train_metrics` (the 7-key dict),
`ctx.train_dense_metrics` (the 4-key dense-pass dict, D-105/M2) and
`ctx.analytics_report` (the console report string); `_down` clears
all three.

## Suite status (session 29, post D-105)

- `test_lm_worker_analytics`: 4/0/0 live (2 classes — the rlm_02
  golden/determinism/_down trio + the rlm_01 mobility-table test;
  all 4 tests DB-gated — the setUp moves through VALIDATE on a fresh
  base dir, so the live regab DB is required; under `SKIP_REGAB_DB=1`
  the 4 tests skip — 4/0/4 gated).
- Full discover: 631 tests, 87 skipped under `SKIP_REGAB_DB=1`,
  GREEN (3.2 s); ungated (live DB): 631 run, 18 skipped, GREEN
  (46.8 s). The module-level `-W error` run is clean (8.0 s).

## State per Roberto

Pipeline COMPLETE (15/15 active levels post D-104). The ANALYTICS
fix campaign (D-103) is CLOSED: T1 (factory `@validate_call`
+ pydantic import — all 13 worker factories now uniform), T2 (the
dead `pathlib.Path` import removed here + the dead `sys` /
`Optional` / `List` imports removed in rlm_analytics), T4 (6 ws
lines), T5 (the dedicated test file added), T6 (rlm_01.json
`detailed_report` += "LMC" — the mobility-table branch gets
end-to-end coverage), M1 (RLMContext pre-declares `train_metrics`),
M2/M3 in rlm_analytics. T3 verified no-action (both headers already
carry their own names — unlike D-102's rlm_validate). D-105 (M2
approved by Roberto, 2026-09-03): the dense-pass 3-metric table —
this file: `_up` publishes the 4-key `train_dense_metrics` dict
(pre-declared on RLMContext L156) before the format calls, `_down`
clears it (3 fields), the data module logs one extra INFO line.

## Architecture (86 lines, post D-105)

- Imports (L28-38): `Worker, Relevance` from state_machine (L34),
  the 4 public data functions from rlm_analytics (L35-37, 3 lines
  since D-105/M2), `validate_call, ConfigDict` from pydantic (L30 —
  added in D-103 T1, replacing the dead `from pathlib import Path`
  line — T2), `RLMContext` under TYPE_CHECKING (L37-38). NO
  `twolm.cache_manager` import (by design).
- `_up` (L48-73): `log_event(INFO, "Generating model analytics
  report...")` (L49); `ctx.train_metrics = compute_training_metrics
  (ctx)` (L54 — the field is pre-declared on RLMContext L155 since
  D-103 M1); `ctx.train_dense_metrics =
  compute_training_dense_metrics(ctx)` (L55 — pre-declared on
  RLMContext L156 since D-105/M2); `console_report =
  format_console_report(ctx)` (L58); the 17 header lines logged
  line by line (L61-62 — "so it shows up in the StateMachine
  logs", per the comment); `file_report = format_file_report(ctx)`
  (L65) written to `ctx.cfg.base_dir / ctx.cfg.analytics.
  report_file_name` (L66-69); `log_event(INFO, f"Analytics report
  saved to ...")` (L71); publishes `ctx.analytics_report =
  console_report` (L73, "Store in context if needed by the SAVE
  worker later").
- `_down` (L75-79): `log_event(INFO, "Clearing analytics
  attributes...")` then clears the THREE attributes to None
  (L77-79) — the scope is complete: `_up` sets exactly
  `analytics_report` + `train_metrics` + `train_dense_metrics`
  (pinned by probe A8 and test_down_clears_analytics_attributes).
- `lm_worker_analytics()` (L82-85): the factory — `@validate_call
  (config=ConfigDict(arbitrary_types_allowed=True))` since D-103
  T1 (all 14 sibling worker factories share the pattern) — returns
  `Worker("ANALYTICS", _up, _down)` (L85).

## Verified facts (D-105 probe — 41 checks, 0 mismatches)

scratch/verify_analytics.py, tiers A (structure, 14), B (pipeline
state, 5), C (live golden re-derivation, 18 incl. sub-checks, gated
on SKIP_REGAB_DB), D (unit math, no DB, 4). Pre D-103 the probe
reported exactly the 7 worklist mismatches (A2, A3, A4, A6a, A6b,
A11, A12); post D-103 all 33 pass; D-105 re-pinned (A1, A8, A10,
B2, B3, C2, C6, C6a, C8, C9, C11, D3) and added A13, C4b, C11b,
D4 — post D-105 all 41 pass.

- V1 (A-tier): structure — 86 lines; `__all__ =
  ['lm_worker_analytics']` (L44); the factory WITH `@validate_call`
  + the pydantic import (D-103 T1); NO pathlib import (T2); NO
  cache_manager import (A9); `_up` sets the 3 ctx attributes (L54,
  L55, L73); `_down` clears all three (L77-79);
  `Worker("ANALYTICS", ...)` (L85); 0 non-comment
  trailing-whitespace lines (D-103 T4 — 6 pre).
- V2 (B-tier): the import L53 + worker-list entry L220 uncommented
  (D-103); 0 commented worker imports remain (D-104 made the
  pipeline complete); 15 active levels (CREATED sentinel + 14
  factory calls); the schema `AnalyticsConfig` (default factory)
  makes `ctx.cfg.analytics` always exist — the worker's L65 direct
  access is safe (B5).
- V3 (C-tier, live DB, rlm_02): the full pipeline through ANALYTICS
  (step 13, no crash) with the 7-metric training goldens:
  `train_mae_y 12.346794566613694`, `train_rmse_y
  15.58872172931622`, `train_loss 0.00712497066706419` (=
  `opt_info['f']`, the OPTIMIZE final objective), `train_samples
  199952`, `pop_mae_y 21.729816221648974`, `pop_rmse_y
  26.40637507956623`, `pop_loss 0.020437248051166534` (the bid [6,7]
  training model, 199952 samples) + the 4-key dense goldens
  (D-105/M2, C4b): `train_dense_mae_y 12.346794548249868`,
  `train_dense_rmse_y 15.58872171282352`, `train_dense_loss
  0.00712234852835536`, `train_dense_samples 199952` (cut 1 — the
  residual vs compressed is the f32 rounding of `w_dense`). The
  step-13 log span from "Generating model analytics report..." to
  "Analytics report saved to ..." is exactly 21 lines (1
  Generating + 1 "Computing metrics on the training set..." + 1
  "Computing dense-pass metrics on the training set..." (D-105/M2)
  + 17 header lines + 1 saved). NO rlmwf_12* file and the rlmwf_*
  set unchanged (C7/C7b). Second instance: identical train_metrics
  + identical train_dense_metrics + identical console report
  (deterministic recompute) + no DB re-extraction + exactly 6
  "Cache successfully loaded and validated" hits (C8). The `_down`
  clearing of all 3 attributes (C9). Independent float64
  re-derivation of the training metrics: 0 mismatch (C10). The
  header's Generalization Gap = vld_rmse_y − train_dense_rmse_y
  (dense-vs-dense, C11) and Substitution Delta = train_dense_rmse_y
  − train_rmse_y ("−0.00" at rlm_02's cut 1, C11b).
- V4 (C-tier, live DB, rlm_02 file report): the file exists at
  `base_dir/model_analytics_report.txt`; structure = header
  (detailed — with the Creation Date) + FEATURE SET SUMMARY +
  MOBILITY FEATURES DETAILS (empty — no mobility features) + PATTERN
  details (EDGE rows printed — in `detailed_report`; DIAG3 rows
  omitted; ELLE/LMC absent from the fixture); date-masked
  sha3_256 golden `94a4af7e5ca554e6f8b219cf5ed820e45e102489dacdc25e
  15d2b263158120b0` (C5/C5a/C5b — deterministic, recompute-identical;
  re-pinned D-105 for the 3-metric header).
- V5 (D-tier, no DB): the full training-metric math on a hand-
  computed 2-position case (predictor 0 → z_pred 0.5 → y_pred 0:
  mae_y 10.0, rmse_y 10.0, train_loss 0.123 = `opt_info['f']`,
  samples 2, pop_mae_y 10.0, pop_rmse_y 10.0, pop_loss
  0.0030517578125) (D1); the `opt_info` None branch → train_loss
  0.0 (D2); the console-report N/A branch (train_dense_metrics +
  vld_metrics both None → 6 "N/A" cells, Population line, both gaps
  0.00, 17 lines) (D3); the dense-pass metric math on the same
  hand-computed case (mae_y 10.0, rmse_y 10.0, loss
  0.0030517578125, samples 2) (D4, D-105/M2).

## Minor notes

- **T3 (verified, no action)** — both file headers already carry
  their own names (unlike D-102's rlm_validate, which carried
  `# rlm_config_schemas.py`).
- **M1 (FIXED, D-103, logistic_model)** — `train_metrics` was set by
  the worker as an ad-hoc dataclass attribute: it works (no
  `__slots__`), but every other blackboard field is pre-declared on
  RLMContext (the D-099 idiom), and the worker's own comment says
  the SAVE worker will consume it later. Now declared (L155); the
  same idiom was applied to `train_dense_metrics` (L156) in
  D-105/M2.
- **M2 (FIXED, D-103, rlm_analytics)** — the `Dict[str, float]`
  return annotation on compute_training_metrics while
  `train_samples` is an int → `Dict[str, float | int]`.
- **M3 (FIXED, D-103, rlm_analytics)** — the `hasattr(ctx.cfg,
  'analytics')` guard in format_file_report was dead code: the
  schema field is non-optional with a `default_factory`, so the
  attribute always exists and is never None → direct access.
- **RESOLVED (D-105/M2) — the mixed-representation Generalization
  Gap (O1):** pre D-105 the TRAINING column was the COMPRESSED
  forward pass (`ctx.w` over `ctx.design_matrix` — exactly what the
  optimizer trained) and the VALIDATION column the DENSE forward
  pass (`ctx.w_dense` — the GENERATE materialization, the shipped
  inference rules). The two training representations differ only
  for positions that touch configurations whose orbit was unseen in
  training (dense: orbit frequency-weighted mean / mobility
  np.interp — D-098 R2; compressed: the trained fallback weight).
  Roberto's correction (D-104, the O1 answer) — "dense ≡ compressed
  only when nothing is below the frequency_cut_off" — was verified
  empirically: rlm_04 (cut 10) 1923/199932 training positions
  differ, rlm_01 (cut 2) 5/10, rlm_02/rlm_03 (cut 1) identical up
  to the f32 `w_dense` copy. D-105 made the table explicit: the
  3-metric header now carries BOTH training representations
  (TRAINING + TRAINING-DENSE), the Generalization Gap is dense-vs-
  dense (pure), and the Substitution Delta row quantifies the
  compressed-vs-dense cost (0.00 at cut=1, 0.01 on rlm_04, 3.36 on
  rlm_01).
- Report-only: the data module logs TWO INFO lines
  (compute_training_metrics + compute_training_dense_metrics,
  D-105/M2) — consistent with rlm_validate (3 such lines in
  validate_model).
- Report-only: the 4 public data functions carry NO `@validate_call`
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

- Pipeline ordering: ANALYTICS is the 14th level of 15 (the
  pipeline is COMPLETE post D-104); its inputs come
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
- Downstream: SAVE (level 15, active post D-104) consumes
  `ctx.vld_metrics` + `ctx.training_pop_stats` + `ctx.opt_info` for
  the model_weights file (the worker's "Store in context if needed
  by the SAVE worker later" comment).

## Appendix — line reference

86 lines, as of D-105 (80 at D-103; D-105/M2: +2 import lines
[the 3-line import], +3 comment lines in `_up` step 1, +1 the
dense publish line, +1 the dense None clear in `_down`).

- L28-38: imports (pydantic L30 [T1], state_machine L34,
  rlm_analytics L35-37 [4 names, D-105/M2], TYPE_CHECKING L37-38)
- L44: `__all__`
- L48-73: `_up` (L49 the start log, L54 the train_metrics publish,
  L55 the train_dense_metrics publish [D-105/M2], L58 the console
  report, L61-62 the line-by-line log loop, L65-69 the file report
  write, L71 the saved log, L73 the analytics_report publish)
- L75-79: `_down` (L77-79 the three None clears)
- L82-85: `lm_worker_analytics` (L82 decorator [T1], L85 the Worker)
