# reversi/lm/wrk_effect_size.py
The EFFECT_SIZE worker (the eta²/omega² + the adherence, step 6): the one-way ANOVA effect sizes (the eta²/omega² per
sub-variable) + the adherence (the fixed trio — the chi-square + the KL + the TV — the DB configuration distribution vs
the ideal corpus frequencies). NO cache (a diagnostic; the recompute is seconds). The GRACEFUL DEGRADATION: if the
SU_ANALYSIS level was disabled (no corpus in the ctx), the adherence is skipped with a log note; the eta²/omega² runs
(it does not need the corpus). The down is a no-op — the worker publishes nothing on the ctx.

## API
- `wrk_effect_size() -> Worker` — the factory: the `Worker("EFFECT_SIZE", _up, _down)` (the house worker pattern).
- `_up(ctx)`: (1) the enable check — `effect_size.enable` false makes the level a no-op (opt-in); (2) the ANOVA — the
  eta²/omega² per sub-variable (the one-way ANOVA, the observed raw codes as the groups, the continuous game values as
  the target — it does NOT need the corpus); (3) the adherence (the c metric) — per sub-variable, the DB configuration
  distribution (the observed raw codes of the training positions (`np.unique`)) vs the ideal distribution (the corpus
  frequencies from the `ctx.su_analysis_tables`, normalized), the fixed trio (the `adherence` kernel); the GRACEFUL
  DEGRADATION: if the `ctx.su_analysis_tables` is None (the SU_ANALYSIS level was disabled), the adherence is SKIPPED
  with a log note (the ANOVA runs); (4) the outputs — the console (the ANOVA per sub-variable + the top-N most deviant
  features, the TV descending) + the TXT report (dir_name under base_dir) + the optional CSV (the export_csv flag).
- `_down(ctx)`: a no-op (recovery is trivially satisfied — the worker publishes nothing on the ctx).

## Architecture
- **The inputs** — the `ctx.hlp_indexes.indexes` (the per-position raw codes, the group assignment — the
  `feature_set.compute_indexes` of the INDEXES level) + the `ctx.game_values` (the continuous training game values, the
  target) + the `ctx.su_analysis_tables` (the corpus frequency tables, the cross-level blackboard from the SU_ANALYSIS
  level).
- **The ANOVA** — the `anova_eta_omega(groups, values)`: the one-way ANOVA, the observed raw codes as the groups (K),
  the game values as the target (N). The per-sub-variable raw code is `indexes[:, c0 + i]` (the block layout, the
  `_feature_blocks`). eta² is the biased sample share; omega² is the unbiased population estimate — the pair is reported
  together (omega² may be slightly negative, the null effect — the raw value is reported).
- **The adherence** — the `adherence(db_counts, ideal_counts)`: the DB distribution (the `np.unique` counts of the
  training raw codes) vs the ideal distribution (the corpus marginal, the su_analysis_tables). The fixed trio (the
  chi-square merged-tail p + the KL + the TV) — the ODP-5 close, no config whitelist. The top-N (the `top_k_adherence`,
  default 20) most deviant features (the TV descending) are reported. The GRACEFUL DEGRADATION: the adherence is skipped
  (the log note) when the corpus is absent (the SU_ANALYSIS disabled); the ANOVA runs (it does not need the corpus).
- **NO cache** — a diagnostic (the recompute is seconds); the generation error -> the level fails, the machine
  re-raises.

## Verified invariants
- Pinned by `test_wrk_effect_size.py` (7 tests, the NO-DB mock-ctx suite, the rlm_00 fixture's feature set, the
  synthetic raw codes + the game values): the factory (the EFFECT_SIZE name); the enable no-op (opt-in); the ANOVA (the
  log has one line per sub-variable); the graceful degradation (the tables None -> the adherence SKIPPED, the ANOVA
  runs); the adherence computed (the tables set -> the log has the Adherence lines, the top-N); the report (the TXT is
  written); the down (a no-op).
- Pinned by the 41-check `probes/verify_effect_size.py`: the no-cache discipline; the independent math (the ANOVA vs the
  F identity + scipy's f_oneway + the eta² >= omega² invariant; the adherence trio vs pure-python formulas + the Pinsker
  bound); the CSV path (no test covers it); a live A2050 tier with NO DB — the cached 1e7 area symlinked under
  build/tmp, every ANOVA line and every adherence row recomputed from the caches.

## Open issues
- The report's adherence section header says "top {top_k_adherence}" while the body lists EVERY sub-variable: the
  `top_k_adherence` bound is applied to the CONSOLE lines only (`adherence_lines[:top_k]` in the log), the report
  receives the full list. A wording defect of the header (the console/report split is deliberate) — pinned by
  `probes/verify_effect_size.py` (C6/D7), left as-is pending Roberto's call (a source change). None.

## Conventions
- The house worker pattern: the `wrk_X() -> Worker` factory + the `_up`/`_down`.
- The raw codes (the group assignment) come from the `ctx.hlp_indexes.indexes` (the per-position, per-column code index,
  the `feature_set.compute_indexes`).
- The ANOVA / the adherence are the hlp_feature_analysis kernels — the from-frequency-tables math.

## Integration
- Consumes the `ctx.cfg` (the effect_size config) + the `ctx.feature_set` (the FEATURES level, step 2) + the
  `ctx.hlp_indexes` (the INDEXES level, step 5) + the `ctx.game_values` (the POSITIONS level, step 4) + the
  `ctx.su_analysis_tables` (the SU_ANALYSIS level, step 3, the cross-level blackboard).
- The full wiring registers the worker at step 6 (after INDEXES, before WMAPS).
