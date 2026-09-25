# test/reversi/lm/test_hlp_feature_analysis.py
The NO-DB micro-suite of the ANOVA analysis-kernels data module (the D-298 split: the SU / entropy / MI /
dispersion / never-observed micro-suite moved to test_hlp_su_analysis): the hand-computed toy tables for the ANOVA
kernels + the adherence kernels (the eta² / omega² effect sizes + the guards, the KL / the TV / the chi-square
merged-tail + the adherence union alignment — the three private helpers called via the module import, the D-290
policy). 5 classes / 16 tests / no DB.

## Coverage

| class | tests | what it pins |
|---|---|---|
| `TestAnovaEtaOmega` | 5 | `test_two_groups` (groups [0, 0, 1, 1], values [1, 3, 2, 4]: eta² 0.2, omega² -1/7 the null effect); `test_perfect_separation` (groups [0, 0, 0, 1, 1, 1], values [1, 1, 1, 4, 4, 4]: eta² = omega² = 1); `test_single_group` (the K = 1 degeneracy: eta² = omega² = 0); `test_k_gt_n` (the K > N ValueError); `test_length_mismatch` (the groups/values length ValueError) |
| `TestKLDivergence` | 3 | `test_equal` (p = q: KL = 0); `test_known` (p = [1, 0], q = [0.5, 0.5]: KL = log 2, the 0-term vanishes); `test_infinite` (p = [1, 0], q = [0, 1]: the +inf, the DB has a code the ideal never shows) |
| `TestTotalVariation` | 3 | `test_equal` (TV = 0); `test_max` (p = [1, 0], q = [0, 1]: TV = 1); `test_half` (p = [0.75, 0.25], q = [0.5, 0.5]: TV = 0.25) |
| `TestChiSquareGoodness` | 2 | `test_no_merge` (observed [10, 20, 30, 40], expected [15, 18, 27, 40]: chi2 2.222222, p the scipy ref, merged 0); `test_merged` (observed [1, 2, 3, 40], expected [1.5, 2, 2.5, 40]: the 3 E < 5 cells merged, chi2 0, p 1.0, merged 3) |
| `TestAdherence` | 3 | `test_union_alignment` (db {0: 10, 1: 20}, ideal {0: 10, 1: 30, 2: 60}: the union {0, 1, 2}, TV 0.6, KL 0.9336627322538263, chi2 47.77777777777778, merged 1, p the scipy ref); `test_infinite_kl` (the DB has a code the ideal never shows: the KL + the chi-square +inf, p 0, the TV finite < 1); `test_empty` (the empty DB: the nan values) |

## Goldens pinned

- The hand-computed ANOVA: the 2-group (groups [0, 0, 1, 1], values [1, 3, 2, 4]) -> eta² 0.2, omega² -1/7 (the null
  effect — the raw value reported); the perfect separation (groups [0, 0, 0, 1, 1, 1], values [1, 1, 1, 4, 4, 4]) ->
  eta² = omega² = 1; the K = 1 degeneracy -> 0 / 0; the K > N + the length-mismatch ValueError.
- The hand-computed adherence: the KL = log 2 = 0.6931471805599453 (the 0-term vanishes) + the +inf (the DB has a code
  the ideal never shows); the TV = 0 / 1 / 0.25; the chi-square no-merge 2.222222 (the p the scipy reference 0.527585) +
  the merged 3 (the E < 5 cells into the "other" bin -> chi2 0, p 1.0); the adherence union alignment (db {0: 10, 1:
  20}, ideal {0: 10, 1: 30, 2: 60}) -> TV 0.6, KL 0.9336627322538263, chi2 47.77777777777778, merged 1; the +inf KL; the
  empty nan.

## Conventions

- The house test header (the "How to run" block).
- The pure-function micro-suite: the hand-computed toy count arrays (the marginal / the joint), the assertAlmostEqual
  (the 12-place tolerance on the hand-computed values, 10 places for the adherence KL/chi-square/p-value).
- The three private helpers (the kl / the TV / the chi-square) are called via the module import `hlp_fa._*` (the
  D-290 / D-298).

## Integration

- Consumed by `run_utests.sh` (section 4 — the pipeline, at the step 3 data-module position: between the FEATURES and
  the POSITIONS).
- The companion suites: test_hlp_su_analysis (the D-298 SU kernel micro-suite + the accumulators) and
  test_wrk_anova (the worker orchestration).
