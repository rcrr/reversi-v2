# reversi/lm/hlp_feature_analysis.py
The FEATURE_ANALYSIS data module: the kernels over the frequency tables (the marginal / the joint counts from the
hlp_random_play accumulators). The SU / entropy / mutual-information kernels + the dispersion / the never-observed audit
+ the ANOVA kernels + the adherence kernels are in place — the full kernel set is complete. Pure math from the frequency
tables — NO DB, NO positions. The worker (wrk_feature_analysis) calls these on the accumulator output (the phase-2
recompute, cheap, on every run).

## API
- `entropy(counts) -> float` — the Shannon entropy H in bits, from the count array (the marginal or the joint). The
  0-log-0 convention (the zero counts contribute 0); the empty / the all-zero -> 0.
- `mutual_information(joint_counts, marg_u, marg_v) -> float` — I(u; v) in bits, the identity I = H(u) + H(v) - H(u, v)
  (the ratio form's 0/0 avoided; the joint entropy is the entropy of the joint counts). Clamped to >= 0 (the
  floating-point rounding of the identity can give a tiny negative).
- `symmetric_uncertainty(I, H_u, H_v) -> float` — the symmetrical uncertainty SU = 2·I / (H(u) + H(v)), in [0, 1]. The
  0-denominator guard: SU = 0 if H(u) + H(v) == 0 (the degenerate variables — the code-0 "no match" single-category, the
  ODP-4/ODP-8 close).
- `dispersion(counts, n_configurations) -> dict` — the per-sub-variable dispersion: K_obs (the distinct observed codes),
  H (the entropy in bits), H_norm = H / log2(K_obs) (else 0 — the K_obs <= 1 guard), the coverage = K_obs /
  n_configurations. Returns {'k_obs', 'h', 'h_norm', 'coverage'}.
- `never_observed_audit(counts, n_configurations, rarity_thresholds=(1, 2, 5, 10, 100)) -> dict` — the never-observed
  audit: the number of theoretical codes never seen (n_configurations
  - K_obs) + the rarity profile (the count of the observed codes below each small count threshold — the configurations
    that random play almost never reaches: the weights that can never be learned). Returns {'k_obs', 'never_observed',
    'rarity'}.
- `anova_eta_omega(groups, values) -> dict` — the one-way ANOVA effect sizes: the observed codes as the groups (K), the
  target = the continuous training game values (N). eta² = SS_eff / SS_tot; omega² = (SS_eff - (K-1) MS_err) / (SS_tot +
  MS_err), MS_err = SS_err / (N - K). Guards: K = 1 -> eta² = omega² = 0 (degenerate, by convention); K > N ->
  ValueError (unreachable); omega² may be slightly negative (the null effect) — the raw value is reported. Returns
  {'eta2', 'omega2', 'k', 'n'}.
- `kl_divergence(p, q) -> float` — the KL divergence KL(p || q) in nats, the 0-log-0 convention (the p(i) = 0 terms
  vanish); +inf if p(i) > 0 and q(i) = 0 (the DB has a code the ideal never shows).
- `total_variation(p, q) -> float` — the total variation distance TV(p, q) = 0.5 * sum |p - q|, in [0, 1] (the robust
  "how different" number, no log, no 0/0).
- `chi_square_goodness(observed, expected, min_expected=5) -> dict` — the chi-square goodness-of-fit: the statistic sum
  (O - E)^2 / E, the p-value (the scipy chi2.sf, the (k - 1) df), the merged tail (the low-expected cells, E <
  min_expected, merged into an "other" bin) + the merge count (the standard technique). Returns {'chi2', 'p', 'merged'};
  the p-value is nan if the merged result has fewer than 2 cells. The disjoint support (a cell with O > 0 but E = 0, the
  DB observes a code the ideal never shows) returns chi2 = +inf, p = 0 (the total incompatibility, aligned with the KL
  +inf — the merged tail would otherwise hide the root cause and divide by zero).
- `adherence(db_counts, ideal_counts) -> dict` — the adherence (c) trio: the DB configuration distribution (the observed
  codes of the training positions) vs the ideal distribution (the corpus frequencies, normalized), the fixed trio (the
  ODP-5 close, no config whitelist): the chi-square (the p-value + the merged-tail count), the KL (the 0-log-0), the TV
  (the robust "how different" number). The two are aligned over the union of the observed codes (the missing side is 0).
  Returns {'chi2', 'p', 'merged', 'kl', 'tv'}; the values are nan if either distribution is empty.

## Architecture
- The SU is computed from the IDEAL (synthetic) frequencies: a structural property of the game geometry + the feature
  set, free of the DB sample noise (the design section 3.3 phase 2). The marginal / the joint come from the
  hlp_random_play accumulators; this module is the from-frequency-tables math only.
- The MI identity I = H(u) + H(v) - H(u, v) (vs the ratio form p(u,v) log(p(u,v)/(p(u)p(v)))): the 0/0 of the ratio (the
  cell with p(u,v) = 0, or p(u) = 0) is avoided; the joint entropy is the entropy of the joint counts (the observed
  cells). The clamp to >= 0 guards the floating-point rounding.
- The SU 0-denominator guard (the design: "SU = 0 if the denominator is 0"): the degenerate sub-variable (the single
  observed category — the code-0 "no match" when the pattern never matches) has H = 0; the pair (u, v) with H(u) + H(v)
  = 0 is the 0/0, guarded to 0 (not a measurement — the ODP-4/ODP-8 close: the 1s and the 0/0 are locks, not signals).

## Verified invariants
- The hand-computed toy tables (test_hlp_feature_analysis, 32 tests): the uniform 4 (H = 2), the degenerate (H = 0), the
  binary p = [0.25, 0.75] (H = 0.8112781244591328), the empty (H = 0, the n = 0 guard); the perfect-correlation MI (u ==
  v: I = 1), the independent MI (I = 0), the non-negative clamp; the SU = 1 (the perfect), the SU = 0 (the independent),
  the SU = 0 (the 0-denominator guard); the dispersion hand-computed (counts [1, 1, 2, 4], n_conf 8: K_obs 4, H 1.75,
  H_norm 0.875, coverage 0.5) + the degenerate (K_obs 1, H_norm 0 the guard) + the dense-zeros filter; the
  never-observed audit hand-computed (never 4, the rarity {1: 0, 2: 2, 5: 4, 10: 4, 100: 4}) + the all-observed (never
  0) + the empty (never = n_conf, the rarity all 0); the ANOVA hand-computed (the 2-group [1, 3, 2, 4]: eta² 0.2,
  omega² -1/7 the null effect; the perfect separation [1, 1, 1, 4, 4, 4]: eta² = omega² = 1; the K = 1 degeneracy -> 0 /
  0; the K > N + the length-mismatch ValueError; the adherence hand-computed (the KL = log 2 = 0.6931471805599453 + the
  0-term vanishes + the +inf the DB-has-a-code-the-ideal-never-shows; the TV = 0 / 1 / 0.25; the chi-square
  no-merge 2.222222 p 0.527585 + the merged 3 -> chi2 0 p 1.0; the adherence union alignment TV 0.6
  KL 0.9336627322538263 chi2 47.77777777777778 merged 1 + the +inf KL + the empty nan).

## Open issues
- The worker (wrk_feature_analysis) wires these into the pipeline (the cache flow + the phase-2 recompute + the reports)
  — PENDING.

## Conventions
- The house GNU header + the provenance docstring.
- The pure functions over the numpy count arrays (the marginal / the joint from the accumulators); no state, no DB, no
  positions.
- The 0-log-0 convention (the standard entropy / KL / TV convention) throughout.

## Integration
- Consumes the hlp_random_play accumulators' output (the marginal / the joint counts) — the data plane.
- Future consumer: the FEATURE_ANALYSIS worker (wrk_feature_analysis.py) — the phase-2 recompute (the statistics on
  every run, including the cache hit) + the reports (the console + the TXT + the optional CSV).
