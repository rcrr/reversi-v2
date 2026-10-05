# reversi/lm/hlp_anova.py
The ANOVA family module: the pure-math kernels over the frequency tables + the two FLOW functions (the wrk/hlp
boundary). NO DB, NO positions. The ANALYTICS pooled eta² (the "Eta-Squared (Discrimination)" line of both feature
tables) is the SAME `hlp_anova_eta_omega` call: the kernel serves TWO consumers (the ANOVA level + the ANALYTICS
tables).

## API
- `hlp_anova_eta_omega(groups: npt.ArrayLike, values: npt.ArrayLike) -> dict` — the one-way ANOVA effect sizes: the
  observed codes as the groups (K), the target = the continuous training game values (N). eta² = SS_eff / SS_tot;
  omega² = (SS_eff - (K-1) MS_err) / (SS_tot + MS_err), MS_err = SS_err / (N - K). Guards: K = 1 -> eta² = omega² = 0
  (degenerate, by convention); K > N -> ValueError (unreachable); omega² may be slightly negative (the null effect) —
  the raw value is reported. Returns {'eta2', 'omega2', 'k', 'n'}.
- `hlp_anova_adherence(db_counts: dict[str | int, int | float], ideal_counts: dict[str | int, int | float]) -> dict` —
  the adherence trio: the DB configuration distribution (the observed codes of the training positions) vs the ideal
  distribution (the corpus frequencies, normalized), the fixed trio (no config whitelist): the chi-square (the p-value
  + the merged-tail count), the KL (the 0-log-0), the TV (the robust "how different" number). The two are aligned over
  the union of the observed codes (the missing side is 0). Returns {'chi2', 'p', 'merged', 'kl', 'tv'}; the values are
  nan if either distribution is empty.
- `hlp_anova_compute_analysis(ctx) -> tuple` — the ANOVA analysis (the two passes over the training set): the
  eta²/omega² per sub-variable + the adherence per sub-variable (None when the corpus is absent — the graceful
  degradation, the SU_ANALYSIS level disabled). Returns (anova_lines, adherence_lines).
- `hlp_anova_generate_report(ctx, anova_lines, adherence_lines) -> Path` — the ANOVA outputs: the TXT report
  (dir_name under base_dir, the per-sub-variable rows + the top-N most deviant features + the graceful-degradation
  note) + the optional CSV (the export_csv flag).
- The three PRIVATE helpers of the adherence trio (no other-module consumer — the test reaches them via the module
  import): `_kl_divergence(p, q) -> float` (the KL in nats, the 0-log-0, +inf on the
  disjoint support), `_total_variation(p, q) -> float` (the TV = 0.5 * sum |p - q|, in [0, 1]),
  `_chi_square_goodness(observed, expected, min_expected=5) -> dict` (the statistic + the scipy p-value + the
  merged tail; the disjoint support -> chi2 +inf, p 0; the p is nan if the merged result has fewer than 2 cells).
- The two PRIVATE per-sub-variable line builders: `_compute_anova_lines(ctx) -> list`
  (the eta²/omega² per sub-variable, one log line per row) + `_compute_adherence_lines(ctx) -> list | None` (the
  adherence per sub-variable, the TV descending, the top-N logged; the graceful-degradation None branch with the
  SKIPPED log note).

## Architecture
- The wrk/hlp split: the worker owns the LEVEL (the enable guard + the two FLOW calls);
  this module owns the analysis + the outputs. The worker no longer imports the kernels — the boundary is exactly
  the two FLOW functions.
- The adherence is computed against the IDEAL (synthetic) frequencies: a structural property of the game geometry + the
  feature set, free of the DB sample noise. The marginal / the joint come from the
  hlp_su_analysis accumulators; this module is the from-frequency-tables math only.
- The disjoint-support alignment: a cell with O > 0 but E = 0 (the DB observes a code the ideal never shows) gives
  chi2 = +inf, p = 0, KL = +inf — the three are aligned; the merged tail would otherwise hide the root cause and
  divide by zero.
- NO cache (a diagnostic, the recompute is seconds): the two passes are cheap and run on EVERY up-move.

## Verified invariants
- The hand-computed toy tables (test_hlp_anova, 18 tests): the ANOVA hand-computed (the 2-group [1, 3, 2,
  4]: eta² 0.2, omega² -1/7 the null effect; the perfect separation [1, 1, 1, 4, 4, 4]: eta² = omega² = 1; the
  K = 1 + the zero-variance degeneracies -> 0 / 0; the K > N + the length-mismatch ValueError); the adherence
  hand-computed (the KL = log 2 = 0.6931471805599453 + the 0-term vanishes + the +inf the DB-has-a-code-the-ideal-
  never-shows; the TV = 0 / 1 / 0.25; the chi-square no-merge 2.222222 p 0.527585 + the merged 3 -> chi2 0 p 1.0 +
  the degenerate tail -> p nan; the adherence union alignment TV 0.6 KL 0.9336627322538263 chi2 47.77777777777778
  merged 1 + the +inf KL + the empty nan).
- The module boundary (the ANOVA family — the kernels + the compute / report methods — here, the SU kernels in
  hlp_su_analysis): pinned by the verify_anova F5.
- The graceful-degradation branch: pinned by the verify_anova A5 (the None branch + the SKIPPED log, in this
  module).

## Open issues

None.

## Conventions
- The house GNU header; no module docstring (the mirror is the module's documentation).
- The 2 PURE-MATH kernels are the @validate_call Pydantic boundary (the typed ArrayLike / dict parameters, the
  ConfigDict arbitrary_types_allowed); the 2 FLOW functions stay undecorated (the ctx idiom — the hlp_design_matrix
  precedent).
- The pure functions over the numpy count arrays; no state, no DB, no positions.
- The 0-log-0 convention (the standard KL / TV convention) throughout.

## Integration
- Consumed by the ANOVA worker (wrk_anova.py): `_up` = the enable guard + `hlp_anova_compute_analysis` +
  `hlp_anova_generate_report`; the cross-level input `ctx.su_analysis_tables` (the SU_ANALYSIS level, step 3) is read
  in `_compute_adherence_lines`.
- Also consumed by the ANALYTICS data module (hlp_analytics): the pooled eta² + the adherence trio
  (the "SU Sample Consistency" line).
- Reuses: scipy.stats.chi2 (the p-values).
