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
- `_format_header(ctx, detailed=False)` (L309-371): the common
  header — `MODEL ANALYTICS REPORT: <name>`, Total Parameters (W)
  = len(ctx.w), Dense Parameters (K) = len(ctx.w_dense), the
  Optimization Status (reason + iters from `ctx.opt_info`), then the
  4-column metric table (TRAINING from `ctx.train_metrics` —
  TRAINING column "Loss (MSE/2)" is `opt_info['f']`, the ridge-
  inclusive final objective, while the VALIDATION/POPULATION losses
  are pure 0.5·mean(rn²) — the intentional asymmetry of the
  training-side objective), VALIDATION from `ctx.vld_metrics` (the
  N/A triple + gen_gap 0.0 when None), POPULATION from the
  train-metrics population baseline, and the Generalization Gap
  (vld_rmse − train_rmse, see the lm_worker_analytics doc O1 note).
  `detailed=True` adds the Creation Date + the stat_model lines
  (frequency cut-off, logit clipping, ridge).
- `format_console_report(ctx)` (L374-378): `_format_header
  (detailed=False)` — the 15-line report, no date, no tables.
- `format_file_report(ctx)` (L381-411): the complete report —
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
- `compute_training_metrics(ctx)` (L414-453) → `Dict[str, float |
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

## Verified facts (D-103 probe — 33 checks, 0 mismatches)

scratch/verify_analytics.py, tiers A (structure, 12), B (pipeline
state, 5), C (live golden re-derivation, 11, gated), D (unit math,
no DB, 3). Pre-campaign the probe reported exactly the 7 worklist
mismatches; post D-103 all 33 pass.

- V1 (A-tier): structure — 453 lines; `__all__` = the 3 public
  names (L44); 0 non-comment trailing-whitespace lines (D-103 T4 —
  39 pre); the typing line is `TYPE_CHECKING, Dict` (T2); NO
  `@validate_call` anywhere (the rlm_indexes-L166 TYPE_CHECKING
  class — consistent with rlm_validate, report-only).
- V2 (C-tier, live DB, rlm_02): the 7-metric training goldens
  (rlm_02, bid [6,7], 199952 samples): `train_mae_y
  12.346794566613694`, `train_rmse_y 15.58872172931622`,
  `train_loss 0.00712497066706419` (= `opt_info['f']`),
  `train_samples 199952`, `pop_mae_y 21.729816221648974`,
  `pop_rmse_y 26.40637507956623`, `pop_loss
  0.020437248051166534`; independent float64 re-derivation: 0
  mismatch (C10).
- V3 (C-tier, live DB, file reports): the rlm_02 file report
  (EDGE rows printed — in the fixture's `detailed_report`; DIAG3
  omitted; the MOBILITY section empty — no mobility features) is
  byte-deterministic: date-masked sha3_256
  `9b97746c69436fc23fd4f7a06274174d66ed1d0cb8467619b78a409e7f743c66`
  (C5a/C5b, recompute-identical). The rlm_01 file report (LMC +
  DIAG3 rows printed post D-103 T6, CORE omitted — exactly one
  "(Table rows omitted" line; the LMC table's 65 rows exercise the
  mobility helper end-to-end) is pinned by the same mask:
  `77fa815ada656152b5f8f893134624d5d023ffc66e9c81e4fcda9a1ecc0c083d`.
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
  0.0 (D2); the console-report N/A branch (vld_metrics None → 3
  "N/A" strings, gen_gap 0.00, 15 lines) (D3).

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
- Report-only — the mixed-representation Generalization Gap: the
  TRAINING column is the compressed forward pass, the VALIDATION
  column the dense one; on rlm_02 all 1600 validation instances sit
  on seen orbits (0 unseen — measured), so the gap is a clean
  data difference there (full note in the lm_worker_analytics doc,
  O1).
- Report-only: the TRAINING "Loss (MSE/2)" cell is `opt_info['f']`
  — the ridge-inclusive final objective — while the other two
  columns are pure 0.5·mean(rn²); intentional (the training-side
  objective is what the optimizer minimized), documented here.
- Report-only: the ONE INFO log line comes from the data module
  (compute_training_metrics) — consistent with rlm_validate.
- Report-only: rlm_02's `detailed_report` lists ELLE/LMC (absent
  from that fixture) — harmless, the block looks copied (the
  fixture is Roberto's).

## Integration notes

- Consumers: ONLY the ANALYTICS worker (lm_worker_analytics.py) —
  the 3 public functions are the module's whole API (`__all__`).
- Inputs: CONFIG (`ctx.cfg` — name, base_dir, analytics,
  stat_model), FEATURES (`ctx.feature_set` + `feature.ref` for the
  pattern principals), INDEXES (`ctx.rlm_indexes.indexes`),
  POSITIONS (`ctx.game_values`), WMAPS (`ctx.w`, `ctx.iwmap`,
  `ctx.iwmap_feature_offset`, `ctx.feature_w_ranges`, `ctx.wmap`,
  `ctx.wmap_fallback`), DESIGN_MTR (`ctx.design_matrix` — the raw
  X array), ZED (`ctx.y2z` / `ctx.z2y`), OPTIMIZE (`ctx.opt_info`),
  GENERATE (`ctx.w_dense`), VALIDATE (`ctx.vld_metrics` for the
  header's VALIDATION column).
- The `sigmoid` is REUSED from rlm_gradient (defined + exported
  there) — no local copy (L36).
- No cache file: the reports are derived artifacts — the file
  report is (re)written to `base_dir` on every ANALYTICS up-move;
  the rlmwf_12 slot stays unused.

## Appendix — line reference

453 lines, as of D-103 (456 at the 96dacb5 bring-in; D-103: −1
`import sys` line [T2], −2 net on the M3 guard, 39 ws lines
emptied in place [T4]).

- L28-37: imports (L33 typing [T2], L36 the rlm_gradient sigmoid)
- L44: `__all__`
- L48-166: `_format_mobility_feature_table` (L113-122 the header,
  L124-125 the print_rows gate, L127-164 the rows)
- L169-306: `_format_pattern_feature_table` (L204-215 the
  max/min lines, L217-218 the principals, L250-261 the header,
  L263-264 the print_rows gate, L266-304 the rows)
- L309-371: `_format_header` (L347-355 the detailed lines,
  L357-370 the metric table)
- L374-378: `format_console_report`
- L381-411: `format_file_report` (L392-393 the M3 direct access,
  L395-401 the mobility section, L403-408 the pattern section)
- L414-453: `compute_training_metrics` (L417 the M2 annotation,
  L425 the compressed forward pass, L446-454 the 7-key dict)
