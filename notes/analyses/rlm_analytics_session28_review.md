<!-- ARCHIVED — D-106 step 20 (the docs/ rewrite, 2026-09-04):
     the complete session-28 analysis (D-103) + the D-105/M2
     re-pin narrative moved out of
     docs/src/twolm/rlm_analytics.md per docs_rules.md
     §1/§4. This is a frozen historical record: it is never
     updated. Stale-in-current-context notes: (1) the "41 checks,
     0 mismatches" figure — the current
     probes/verify_analytics.py (the 4091e72 move) has 36
     surviving check calls: A1-A13 (structure, 14 — incl. A6a/
     A6b), B4 + B5 (context facts), C1-C11b (live golden re-
     derivation, 16 — incl. C4a, C5a/C5b, C6a, C7b, C11b), D1-D4
     (unit math, no DB). The D-106 step-3 deletions: B1-B3
     pipeline-state pins → the hub verify_logistic_model.py;
     C4b (the train_dense_ goldens) + C6 (the 17 header lines +
     21-line span) deleted class c — the worker's integration
     test pins them. (2) the "626 tests / 84 skipped" full-
     discover figure predates steps 3-19 (current: 664/87
     gated); (3) the D-103/D-105 campaign narrative (T1-T6 +
     M1-M3, the O1 mixed-representation gap resolution, the
     3-metric header) is frozen history. -->

# twolm/rlm_analytics.py

Analysis date: 2026-09-02 — analysis session 28 (D-103, the
ANALYTICS bring-in, Roberto's commit 96dacb5); fix campaign D-103
approved by Roberto ("T1: OK, T2: OK, T4: OK, T5: OK, T6: OK,
M1-M3: OK. Procedi!") and applied in the same session. Brought in
by Roberto (96dacb5 — the 2nd dedicated data module of a
non-cache level besides the worker, function-only like
rlm_gradient / rlm_validate: 3 public functions + 3 private
helpers, NO data class, NO store/load, NO cache_manager).

The analytics report engine of the RLM pipeline: computes the
training-side metrics (the COMPRESSED forward pass — `ctx.w` over
`ctx.design_matrix`, exactly what the optimizer trained) and
formats the two report variants (the 15-line console header; the
complete file report with the per-feature configuration tables).

## Suite status (session 28, post D-103)

- No dedicated data-suite (the level's behavior is covered by
  `test_lm_worker_analytics` — the worker integration, which
  exercises all 3 public functions end-to-end — 4/0/0 live, 4/0/4
  gated).
- Full discover: 626 tests, 84 skipped under `SKIP_REGAB_DB=1`,
  GREEN (2.8 s); ungated (live DB): 626 run, 17 skipped, GREEN
  (39.1 s). The full `-W error` discover is clean (38.9 s).

## Architecture (453 lines, post D-103)

- Imports (L28-37): `io` (StringIO for the feature-set summary),
  `numpy as np`, `TYPE_CHECKING, Dict` (D-103 T2: the dead `sys`
  import + the unused `Optional`/`List` removed), `datetime`
  (the file header's Creation Date), `sigmoid` REUSED from
  rlm_gradient (L36 — no local copy), `Relevance` from
  state_machine (the ONE INFO log line in compute_training_metrics).
- `_format_mobility_feature_table(ctx, fid, indexes_col_offset,
  print_rows=True)` (L48-166): the per-configuration ASCII table
  for one mobility feature — header: the fallback line
  (`feature_w_ranges[fid,0]` + the `wmap_fallback` total frequency),
  the frequency-weighted mean of the true weights, the
  Instances/Cols line, the Config Counts (C/IA/IC) line, the
  Eta-Squared discrimination statistic (SS_between/SS_total over
  per-config game-value groups via `np.bincount`); rows (one per
  configuration, `print_rows`-gated): W_DENSE_IDX | STATUS | W_IDX
  | CONF_IDX | FREQUENCY | AVERAGE_GV | RMSE_GV | WEIGHT — STATUS
  is IC (the config's frequency is below the cut-off — counted in
  the feature's fallback bucket), C (confirmed — above cut-off, its
  own trained `ctx.w` weight) or IA (absent — never seen, the dense
  interpolated `ctx.w_dense` weight).
- `_format_pattern_feature_table(...)` (L169-306): the same table
  for one pattern feature, plus the Max/Min Weight (w) lines (with
  the configuration ids), the PRINCIPAL_IDX column
  (`feature.ref.convert_to_principal_index` over all configs — the
  D8 orbit representatives), and STATUS CL (collapsed to the
  fallback bucket) / C / AB (absent — never seen, the dense
  orbit-mean weight per D-098 R2).
- `_format_header(ctx, detailed=False)` (L310-401): the common
  header — `MODEL ANALYTICS REPORT: <name>`, Total Parameters (W)
  = len(ctx.w), Dense Parameters (K) = len(ctx.w_dense), the
  Optimization Status (reason + iters from `ctx.opt_info`), then the
  3-metric table (D-105/M2): TRAINING from `ctx.train_metrics`
  (the COMPRESSED forward pass — what lbfgs fit; its "Loss (MSE/2)"
  cell is `opt_info['f']`, the ridge-inclusive final objective),
  TRAINING-DENSE from `ctx.train_dense_metrics` (the DENSE forward
  pass over `w_dense` — the exact shipped inference rules of
  rlm_client; all 3 cells pure forward-pass metrics), VALIDATION
  from `ctx.vld_metrics` (the N/A triple + both gaps 0.0 when
  None); then the Population (baseline) line (the train-metrics
  population baseline — RMSE/MAE/Loss on one row), the
  Generalization Gap (vld_rmse − train_dense_rmse — DENSE vs
  DENSE post D-105: a pure generalization measure) and the
  Substitution Delta (train_dense_rmse − train_rmse — the
  compressed-vs-dense difference: exactly 0 for
  frequency_cut_off=1 up to the f32 rounding of `w_dense`, which
  renders "-0.00" on rlm_02/rlm_03). `detailed=True` adds the
  Creation Date + the stat_model lines (frequency cut-off, logit
  clipping, ridge).
- `format_console_report(ctx)` (L403-407): `_format_header
  (detailed=False)` — the 17-line report, no date, no tables.
- `format_file_report(ctx)` (L410-441): the complete report —
  detailed header + FEATURE SET SUMMARY (`ctx.feature_set.
  print_summary(output=buffer)`) + the MOBILITY FEATURES DETAILS
  section (one table per category-1 feature) + the PATTERN FEATURES
  DETAILS section (one table per category-2 feature); the per-table
  `print_rows` = the feature name is in
  `ctx.cfg.analytics.detailed_report` (D-103 M3: direct access —
  the field is non-optional with a `default_factory`, the old
  `hasattr` guard was dead code); `col_offset` accumulates over ALL
  features (intercept included) so each table's column slice lines
  up with `ctx.rlm_indexes.indexes` (the design-matrix column
  layout).
- `compute_training_metrics(ctx)` (L443-481) → `Dict[str, float |
  int]` (D-103 M2 annotation — `train_samples` is the int): ONE
  INFO log line ("Computing metrics on the training set..."); the
  compressed forward pass: `np.sum(ctx.w[ctx.design_matrix].astype
  (np.float64), axis=1)` → `sigmoid` (reused) → `ctx.z2y` closure
  (float32 affine over the float64 z — the zed factory's cast
  semantics); `y_pred` vs `ctx.game_values` (float64): `train_mae_y`
  / `train_rmse_y`; the population baseline (the y_true-vs-its-mean
  residuals): `pop_mae_y` / `pop_rmse_y` / `pop_loss` (0.5·mean
  squared z residuals via `ctx.y2z`); `train_loss = opt_info['f']`
  (0.0 when `opt_info` is None); `train_samples = int(len
  (y_true))`.
- `compute_training_dense_metrics(ctx)` (L483-521, D-105/M2) →
  `Dict[str, float | int]`: ONE INFO log line ("Computing
  dense-pass metrics on the training set..."); the DENSE forward
  pass — the same expanded-offsets construction as rlm_validate:
  `col_offsets = np.repeat(ctx.iwmap_feature_offset[:-1],
  n_instances_per_feature)`, `dense_indices = ctx.rlm_indexes.
  indexes + col_offsets`, `np.sum(ctx.w_dense[dense_indices],
  axis=1)` → `sigmoid` → `ctx.z2y`; the 4-key dict
  `train_dense_{mae_y, rmse_y, loss, samples}`; the loss is the
  PURE 0.5·mean(rn_z²) forward-pass loss (there is no dense
  optimizer objective — the ridge lives on the compressed side).

## Verified facts (D-105 probe — 41 checks, 0 mismatches)

scratch/verify_analytics.py, tiers A (structure, 14), B (pipeline
state, 5), C (live golden re-derivation, 18 incl. sub-checks,
gated), D (unit math, no DB, 4). Pre D-103 the probe reported
exactly the 7 worklist mismatches; post D-103 all 33 pass. D-105
re-pin: the 3 stale pre-D-104 pins (A1 the 4 `__all__` names, B2
0 commented worker imports — the pipeline is complete, B3 15
active levels), the D-105 table re-pins (A8 the 3 cleared fields,
A10 the 4 data fns, C2 the pre-state, C6/C6a the 17-line header +
21-line span, C8/C9 the dense dict in determinism/_down, C11 the
dense-vs-dense gap formula) and 4 new checks (A13 the
`train_dense_metrics` pre-declaration, C4b the dense goldens, C11b
the substitution-delta formula, D4 the dense hand-computed math).

- V1 (A-tier): structure — 522 lines; `__all__` = the 4 public
  names (L44-45, D-105/M2 added
  `compute_training_dense_metrics`); 0 non-comment
  trailing-whitespace lines (D-103 T4 — 39 pre); the typing line is
  `TYPE_CHECKING, Dict` (T2); NO `@validate_call` anywhere (the
  rlm_indexes-L166 TYPE_CHECKING class — consistent with
  rlm_validate, report-only).
- V2 (C-tier, live DB, rlm_02): the 7-metric training goldens
  (rlm_02, bid [6,7], 199952 samples): `train_mae_y
  12.346794566613694`, `train_rmse_y 15.58872172931622`,
  `train_loss 0.00712497066706419` (= `opt_info['f']`),
  `train_samples 199952`, `pop_mae_y 21.729816221648974`,
  `pop_rmse_y 26.40637507956623`, `pop_loss
  0.020437248051166534`; independent float64 re-derivation: 0
  mismatch (C10). The 4-key dense goldens (D-105/M2, C4b —
  rlm_02 has frequency_cut_off=1, so the dense values match the
  compressed ones up to the f32 rounding of `w_dense`):
  `train_dense_mae_y 12.346794548249868`, `train_dense_rmse_y
  15.58872171282352`, `train_dense_loss 0.00712234852835536`,
  `train_dense_samples 199952` (the compressed-vs-dense rmse
  residual is −1.6e-08 — the f32 copy, no substitution).
- V3 (C-tier, live DB, file reports): the rlm_02 file report
  (EDGE rows printed — in the fixture's `detailed_report`; DIAG3
  omitted; the MOBILITY section empty — no mobility features) is
  byte-deterministic: date-masked sha3_256
  `94a4af7e5ca554e6f8b219cf5ed820e45e102489dacdc25e15d2b263158120b0`
  (C5a/C5b, recompute-identical; re-pinned D-105 — the new
  3-metric header). The rlm_01 file report (LMC +
  DIAG3 rows printed post D-103 T6, CORE omitted — exactly one
  "(Table rows omitted" line; the LMC table's 65 rows exercise the
  mobility helper end-to-end) is pinned by the same mask:
  `f6b54954a3c54d13a9a3b3e65face75a5bd709899050c0b77b236a8955cf4c8c`
  (re-pinned D-105).
- V4 (C-tier, live DB, rlm_01): the 7-metric training goldens
  (bid [7], 10 samples): `train_mae_y 9.874833279184258e-05`,
  `train_rmse_y 0.00013206900478667877`, `train_loss
  4.704681197571781e-13` (the 10-sample model converges to
  interpolation — CONVERGED_MIN_GRAD, 16 iters), `train_samples
  10`, `pop_mae_y 15.6`, `pop_rmse_y 18.39565166010707`,
  `pop_loss 0.009125067852437496`.
- V5 (D-tier, no DB): the full training-metric math on a hand-
  computed 2-position case (predictor 0 → z_pred 0.5 → y_pred 0:
  mae_y 10.0, rmse_y 10.0, train_loss 0.123 = `opt_info['f']`,
  samples 2, pop_mae_y 10.0, pop_rmse_y 10.0, pop_loss
  0.0030517578125) (D1); the `opt_info` None branch → train_loss
  0.0 (D2); the console-report N/A branch (train_dense_metrics +
  vld_metrics both None → 6 "N/A" cells, Population baseline line,
  both gaps 0.00, 17 lines) (D3); the dense-pass metric math on
  the same hand-computed case (D-105/M2 — dense indices [[0,1],
  [1,0]] over `w_dense` [1,-1] → predictor 0: mae_y 10.0, rmse_y
  10.0, loss 0.0030517578125, samples 2) (D4).

## Minor notes

- **T2 (FIXED, D-103)** — dead imports: `import sys` (never used),
  `Optional` / `List` in the typing line (never referenced).
- **T4 (FIXED, D-103)** — 39 non-comment ws lines stripped
  (ws-only + trailing, across the table helpers).
- **M2 (FIXED, D-103)** — the `Dict[str, float]` annotation while
  `train_samples` is an int → `Dict[str, float | int]`.
- **M3 (FIXED, D-103)** — the `hasattr(ctx.cfg, 'analytics')` /
  `is not None` guard in format_file_report (4 lines) was dead
  code: the schema field is non-optional with a `default_factory` →
  direct `ctx.cfg.analytics.detailed_report` access.
- **RESOLVED (D-105/M2)** — the mixed-representation Generalization
  Gap: pre D-105 the TRAINING column was the compressed forward pass
  and the VALIDATION column the dense one — the gap mixed the data
  difference with the substitution effect. Now the table carries
  both training representations as two columns, the gap is dense-vs-
  dense (pure generalization) and the substitution effect has its
  own Substitution Delta row (0.00 at cut=1; 0.01 on rlm_04 with
  1923/199932 IC positions; 3.36 on rlm_01 where 5/10 training
  positions are IC).
- Report-only: the TRAINING "Loss (MSE/2)" cell is `opt_info['f']`
  — the ridge-inclusive final objective — while the TRAINING-DENSE,
  VALIDATION and Population cells are pure 0.5·mean(rn²);
  intentional (the training-side objective is what the optimizer
  minimized), documented here.
- Report-only: the dense pass reads the f32 `w_dense` copy while
  the compressed pass reads the float64 `w` — so even at
  frequency_cut_off=1 the two training columns differ by the f32
  rounding (rlm_02: −1.6e-08 in rmse; renders "-0.00" in the
  Substitution Delta row).
- Report-only: the TWO INFO log lines come from the data module
  (compute_training_metrics, compute_training_dense_metrics) —
  consistent with rlm_validate.
- Report-only: rlm_02's `detailed_report` lists ELLE/LMC (absent
  from that fixture) — harmless, the block looks copied (the
  fixture is Roberto's).

## Integration notes

- Consumers: ONLY the ANALYTICS worker (lm_worker_analytics.py) —
  the 4 public functions are the module's whole API (`__all__`).
- Inputs: CONFIG (`ctx.cfg` — name, base_dir, analytics,
  stat_model), FEATURES (`ctx.feature_set` + `feature.ref` for the
  pattern principals), INDEXES (`ctx.rlm_indexes.indexes`),
  POSITIONS (`ctx.game_values`), WMAPS (`ctx.w`, `ctx.iwmap`,
  `ctx.iwmap_feature_offset`, `ctx.feature_w_ranges`, `ctx.wmap`,
  `ctx.wmap_fallback`), DESIGN_MTR (`ctx.design_matrix` — the raw
  X array), ZED (`ctx.y2z` / `ctx.z2y`), OPTIMIZE (`ctx.opt_info`),
  GENERATE (`ctx.w_dense`), VALIDATE (`ctx.vld_metrics` for the
  header's VALIDATION column), and the worker's own same-_up
  outputs (`ctx.train_metrics`, `ctx.train_dense_metrics` —
  computed in `_up` before the format calls).
- The `sigmoid` is REUSED from rlm_gradient (defined + exported
  there) — no local copy (L36).
- No cache file: the reports are derived artifacts — the file
  report is (re)written to `base_dir` on every ANALYTICS up-move;
  the rlmwf_12 slot stays unused.

## Appendix — line reference

522 lines, as of D-105 (453 at D-103; D-105/M2: +1 `__all__` line,
+9 docstring lines on `_format_header`, +2 table lines [Population
baseline + Substitution Delta], +16 dense-metrics lines in
`_format_header`, +40 the new `compute_training_dense_metrics`).

- L28-37: imports (L33 typing [T2], L36 the rlm_gradient sigmoid)
- L44-45: `__all__` (4 names, D-105/M2)
- L49-167: `_format_mobility_feature_table` (L114-123 the header,
  L125-126 the print_rows gate, L128-165 the rows)
- L170-307: `_format_pattern_feature_table` (L205-216 the
  max/min lines, L218-219 the principals, L251-262 the header,
  L264-265 the print_rows gate, L267-305 the rows)
- L310-401: `_format_header` (L311-323 the D-105/M2 docstring,
  L352-360 the detailed lines, L362-400 the 3-metric table +
  Population line + the two gap lines)
- L403-407: `format_console_report`
- L410-441: `format_file_report` (L421-422 the M3 direct access,
  L424-430 the mobility section, L432-437 the pattern section)
- L443-481: `compute_training_metrics` (L446 the M2 annotation,
  L454 the compressed forward pass, L472-480 the 7-key dict)
- L483-521: `compute_training_dense_metrics` (D-105/M2; L494 the
  INFO line, L498-499 the per-instance offsets, L501-502 the dense
  forward pass, L514 the pure z-loss, L516-520 the 4-key dict)
