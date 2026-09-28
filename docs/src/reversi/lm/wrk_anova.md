# reversi/lm/wrk_anova.py
The ANOVA worker (the eta²/omega² + the adherence, step 6): the one-way ANOVA effect sizes (the eta²/omega² per
sub-variable) + the adherence (the fixed trio — the chi-square + the KL + the TV — the DB configuration distribution vs
the ideal corpus frequencies). NO cache (a diagnostic; the recompute is seconds). The GRACEFUL DEGRADATION: if the
SU_ANALYSIS level was disabled (no corpus in the ctx), the adherence is skipped with a log note; the eta²/omega² runs
(it does not need the corpus). The down is a no-op — the worker publishes nothing on the ctx.

## API
- `wrk_anova() -> Worker` — the factory: the `Worker("ANOVA", _up, _down)` (the house worker pattern).
- `_up(ctx)`: the thin orchestrator (the D-310 split, extended at D-315) — (1) the enable check — `anova.enable`
  false makes the level a no-op (opt-in); (2) `anova_lines, adherence_lines = hlp_anova_compute_analysis(ctx)`;
  (3) `hlp_anova_generate_report(ctx, anova_lines, adherence_lines)`.
- `_down(ctx)`: a no-op (recovery is trivially satisfied — the worker publishes nothing on the ctx).
- The analysis + the outputs live in hlp_anova (mirror: docs/src/reversi/lm/hlp_anova.md): `hlp_anova_compute_analysis`
  (the eta²/omega² per sub-variable + the adherence per sub-variable, the graceful-degradation None branch) +
  `hlp_anova_generate_report` (the TXT report + the optional CSV) — the D-315 move from this worker.

## Architecture
- **The inputs** (read by hlp_anova, the D-315 move) — the `ctx.hlp_indexes.indexes` (the per-position raw codes, the
  group assignment — the `feature_set.compute_indexes` of the INDEXES level) + the `ctx.game_values` (the continuous
  training game values, the target) + the `ctx.su_analysis_tables` (the corpus frequency tables, the cross-level
  blackboard from the SU_ANALYSIS level).
- **The ANOVA** — the `hlp_anova_eta_omega(groups, values)`: the one-way ANOVA, the observed raw codes as the groups
  (K),
  the game values as the target (N). The per-sub-variable raw code is `indexes[:, c0 + i]` (the block layout, the
  `fset.feature_blocks` property). eta² is the biased sample share; omega² is the unbiased population estimate — the
  pair is reported together (omega² may be slightly negative, the null effect — the raw value is reported).
- **The adherence** — the `adherence(db_counts, ideal_counts)`: the DB distribution (the `np.unique` counts of the
  training raw codes) vs the ideal distribution (the corpus marginal, the su_analysis_tables). The fixed trio (the
  chi-square merged-tail p + the KL + the TV) — no config whitelist. The top-N (the `top_k_adherence`,
  default 20) most deviant features (the TV descending) are reported. The GRACEFUL DEGRADATION: the adherence is skipped
  (the log note) when the corpus is absent (the SU_ANALYSIS disabled); the ANOVA runs (it does not need the corpus).
- **NO cache** — a diagnostic (the recompute is seconds); the generation error -> the level fails, the machine
  re-raises.

## Verified invariants
- Pinned by `test_wrk_anova.py` (7 tests, the NO-DB mock-ctx suite, the rlm_00 fixture's feature set, the
  synthetic raw codes + the game values): the factory (the ANOVA name); the enable no-op (opt-in); the ANOVA (the
  log has one line per sub-variable); the graceful degradation (the tables None -> the adherence SKIPPED, the ANOVA
  runs); the adherence computed (the tables set -> the log has the Adherence lines, the top-N); the report (the TXT is
  written); the down (a no-op).
- Pinned by the 41-check `probes/verify_anova.py`: the no-cache discipline; the independent math (the ANOVA vs the
  F identity + scipy's f_oneway + the eta² >= omega² invariant; the adherence trio vs pure-python formulas + the Pinsker
  bound); the CSV path (no test covers it); a live A2050 tier with NO DB — the cached 1e7 area symlinked under
  build/tmp, every ANOVA line and every adherence row recomputed from the caches.

## Open issues
- The report's adherence section header says "top {top_k_adherence}" while the body lists EVERY sub-variable: the
  `top_k_adherence` bound is applied to the CONSOLE lines only (`adherence_lines[:top_k]` in the log), the report
  receives the full list. A wording defect of the header (the console/report split is deliberate) — pinned by
  `probes/verify_anova.py` (C6/D7), left as-is pending Roberto's call (a source change). None.

## Conventions
- The house worker pattern: the `wrk_X() -> Worker` factory + the `_up`/`_down`.
- The raw codes (the group assignment) come from the `ctx.hlp_indexes.indexes` (the per-position, per-column code index,
  the `feature_set.compute_indexes`).
- The ANOVA / the adherence are the hlp_anova kernels — the from-frequency-tables math. `hlp_anova_eta_omega`
  is SHARED (the D-311): the ANALYTICS pooled eta² (the "Eta-Squared (Discrimination)" line of both feature tables)
  calls the same kernel — the single-instance features' ANALYTICS value == this level's value (pinned by
  `TestEtaSquaredCrossLevel` in test_wrk_analytics).

## Integration
- The worker consumes the `ctx.cfg` (the anova config, the enable guard); the analysis inputs — the
  `ctx.feature_set` (the FEATURES level, step 2) + the `ctx.hlp_indexes` (the INDEXES level, step 5) + the
  `ctx.game_values` (the POSITIONS level, step 4) + the `ctx.su_analysis_tables` (the SU_ANALYSIS level, step 3, the
  cross-level blackboard) — are read by hlp_anova (the D-315 move).
- The full wiring registers the worker at step 6 (after INDEXES, before WMAPS).
