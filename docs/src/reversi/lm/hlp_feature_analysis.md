# reversi/lm/hlp_feature_analysis.py
The ANOVA analysis-kernels data module (the D-298 split: the module was the SHARED data plane of the two
levels, the families proved disjoint — the SU / entropy / MI / dispersion / never-observed kernels now live in
hlp_su_analysis): the pure-math kernels over the frequency tables for the ANOVA level (the step 6 worker).
The full kernel set: the ANOVA + the adherence. Pure math from the frequency tables — NO DB, NO positions.

## API
- `anova_eta_omega(groups, values) -> dict` — the one-way ANOVA effect sizes: the observed codes as the groups (K), the
  target = the continuous training game values (N). eta² = SS_eff / SS_tot; omega² = (SS_eff - (K-1) MS_err) / (SS_tot +
  MS_err), MS_err = SS_err / (N - K). Guards: K = 1 -> eta² = omega² = 0 (degenerate, by convention); K > N ->
  ValueError (unreachable); omega² may be slightly negative (the null effect) — the raw value is reported. Returns
  {'eta2', 'omega2', 'k', 'n'}.
- `adherence(db_counts, ideal_counts) -> dict` — the adherence (c) trio: the DB configuration distribution (the observed
  codes of the training positions) vs the ideal distribution (the corpus frequencies, normalized), the fixed trio (no
  config whitelist): the chi-square (the p-value + the merged-tail count), the KL (the 0-log-0), the TV
  (the robust "how different" number). The two are aligned over the union of the observed codes (the missing side is 0).
  Returns {'chi2', 'p', 'merged', 'kl', 'tv'}; the values are nan if either distribution is empty.
- The three PRIVATE helpers of the adherence trio (the D-298: no other-module consumer, the D-290 policy — the test
  reaches them via the module import): `_kl_divergence(p, q) -> float` (the KL in nats, the 0-log-0, +inf on the
  disjoint support), `_total_variation(p, q) -> float` (the TV = 0.5 * sum |p - q|, in [0, 1]),
  `_chi_square_goodness(observed, expected, min_expected=5) -> dict` (the statistic + the scipy p-value + the
  merged tail; the disjoint support -> chi2 +inf, p 0; the p is nan if the merged result has fewer than 2 cells).

## Architecture
- The adherence is computed against the IDEAL (synthetic) frequencies: a structural property of the game geometry + the
  feature set, free of the DB sample noise (the design section 3.5). The marginal / the joint come from the
  hlp_su_analysis accumulators; this module is the from-frequency-tables math only.
- The disjoint-support alignment: a cell with O > 0 but E = 0 (the DB observes a code the ideal never shows) gives
  chi2 = +inf, p = 0, KL = +inf — the three are aligned; the merged tail would otherwise hide the root cause and
  divide by zero.

## Verified invariants
- The hand-computed toy tables (test_hlp_feature_analysis, 16 tests): the ANOVA hand-computed (the 2-group [1, 3, 2,
  4]: eta² 0.2, omega² -1/7 the null effect; the perfect separation [1, 1, 1, 4, 4, 4]: eta² = omega² = 1; the
  K = 1 degeneracy -> 0 / 0; the K > N + the length-mismatch ValueError); the adherence hand-computed (the KL = log 2
  = 0.6931471805599453 + the 0-term vanishes + the +inf the DB-has-a-code-the-ideal-never-shows; the TV = 0 / 1 /
  0.25; the chi-square no-merge 2.222222 p 0.527585 + the merged 3 -> chi2 0 p 1.0; the adherence union alignment
  TV 0.6 KL 0.9336627322538263 chi2 47.77777777777778 merged 1 + the +inf KL + the empty nan).
- The D-298 split boundary: pinned by the verify_anova F5 (the ANOVA family here, the SU kernels in
  hlp_su_analysis).

## Open issues

None.

## Conventions
- The house GNU header + the provenance docstring.
- The pure functions over the numpy count arrays; no state, no DB, no positions.
- The 0-log-0 convention (the standard KL / TV convention) throughout.

## Integration
- Consumed by the ANOVA worker (wrk_anova.py — the ANOVA on the tagged data + the adherence against the
  published `ctx.su_analysis_tables` of the hlp_su_analysis accumulators).
- Reuses: scipy.stats.chi2 (the p-values).
