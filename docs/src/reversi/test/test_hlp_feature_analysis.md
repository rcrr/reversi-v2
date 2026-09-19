# reversi/test/test_hlp_feature_analysis.py
The NO-DB micro-suite of the FEATURE_ANALYSIS data module: the SU / entropy / mutual-information kernels + the
dispersion / the never-observed audit + the ANOVA kernels + the adherence kernels — the hand-computed toy tables (the
uniform / the degenerate / the binary entropies, the perfect-correlation / the independent mutual informations, the SU =
1 / 0 / the 0-denominator guard, the dispersion K_obs / H / H_norm / coverage, the never-observed + the rarity profile,
the eta² / omega² effect sizes + the guards, the KL / the TV / the chi-square merged-tail + the adherence union
alignment). 10 classes / 32 tests / no DB.

## Coverage

| class | tests | what it pins |
|---|---|---|
| `TestEntropy` | 4 | `test_uniform` (the uniform 4: H = log2 4 = 2); `test_degenerate` (the single-category: H = 0); `test_binary` (p = [0.25, 0.75]: H = 0.8112781244591328); `test_empty` (the all-zero / the empty: H = 0, the n = 0 guard) |
| `TestMutualInformation` | 3 | `test_perfect_correlation` (u == v: the marginals [2, 2], the joint [2, 0, 0, 2], I = 1 + 1 - 1 = 1); `test_independent` (the marginals [2, 2], the joint [1, 1, 1, 1], I = 1 + 1 - 2 = 0); `test_non_negative` (the floating-point clamp: I >= 0) |
| `TestSymmetricUncertainty` | 3 | `test_perfect` (I = H_u = H_v = 1: SU = 2/2 = 1); `test_independent` (I = 0: SU = 0); `test_zero_denominator` (H_u = H_v = 0: the 0/0 guard -> SU = 0) |
| `TestDispersion` | 3 | `test_hand_computed` (counts [1, 1, 2, 4], n_conf 8: K_obs 4, H 1.75, H_norm 0.875, coverage 0.5); `test_degenerate` (counts [8], n_conf 5: K_obs 1, H 0, H_norm 0 the K_obs <= 1 guard, coverage 0.2); `test_dense_zeros_filtered` (the dense form [0, 1, 0, 3, 0]: K_obs 2, coverage 0.4) |
| `TestNeverObservedAudit` | 3 | `test_hand_computed` (counts [1, 1, 2, 4], n_conf 8: never 4, the rarity {1: 0, 2: 2, 5: 4, 10: 4, 100: 4}); `test_all_observed` (the full support: never 0); `test_empty` (the empty: never = n_conf, the rarity all 0) |
| `TestAnovaEtaOmega` | 5 | `test_two_groups` (groups [0, 0, 1, 1], values [1, 3, 2, 4]: eta² 0.2, omega² -1/7 the null effect); `test_perfect_separation` (groups [0, 0, 0, 1, 1, 1], values [1, 1, 1, 4, 4, 4]: eta² = omega² = 1); `test_single_group` (the K = 1 degeneracy: eta² = omega² = 0); `test_k_gt_n` (the K > N ValueError); `test_length_mismatch` (the groups/values length ValueError) |
| `TestKLDivergence` | 3 | `test_equal` (p = q: KL = 0); `test_known` (p = [1, 0], q = [0.5, 0.5]: KL = log 2, the 0-term vanishes); `test_infinite` (p = [1, 0], q = [0, 1]: the +inf, the DB has a code the ideal never shows) |
| `TestTotalVariation` | 3 | `test_equal` (TV = 0); `test_max` (p = [1, 0], q = [0, 1]: TV = 1); `test_half` (p = [0.75, 0.25], q = [0.5, 0.5]: TV = 0.25) |
| `TestChiSquareGoodness` | 2 | `test_no_merge` (observed [10, 20, 30, 40], expected [15, 18, 27, 40]: chi2 2.222222, p the scipy ref, merged 0); `test_merged` (observed [1, 2, 3, 40], expected [1.5, 2, 2.5, 40]: the 3 E < 5 cells merged, chi2 0, p 1.0, merged 3) |
| `TestAdherence` | 3 | `test_union_alignment` (db {0: 10, 1: 20}, ideal {0: 10, 1: 30, 2: 60}: the union {0, 1, 2}, TV 0.6, KL 0.9336627322538263, chi2 47.77777777777778, merged 1, p the scipy ref); `test_infinite_kl` (the DB has a code the ideal never shows: the KL +inf, the TV / the chi-square finite); `test_empty` (the empty DB: the nan values) |

## Goldens pinned

- The hand-computed entropy values: the uniform 2.0, the binary 0.8112781244591328 (the exact -[0.25 log2 0.25 + 0.75
  log2 0.75]), the degenerate 0.0, the empty 0.0.
- The hand-computed MI values: the perfect correlation 1.0 (u == v, the joint on the diagonal), the independent 0.0 (the
  full 2 x 2 support, the marginals uniform).
- The SU guards: the perfect 1.0, the independent 0.0, the 0-denominator 0.0 (the degenerate variables — the code-0 "no
  match" single-category).
- The hand-computed dispersion: the counts [1, 1, 2, 4] (n_conf 8) -> K_obs 4, H 1.75, H_norm 0.875, coverage 0.5; the
  degenerate (counts [8], n_conf 5) -> K_obs 1, H 0, H_norm 0 (the K_obs <= 1 guard), coverage 0.2.
- The hand-computed never-observed audit: the counts [1, 1, 2, 4] (n_conf 8) -> never 4, the rarity {1: 0, 2: 2, 5: 4,
  10: 4, 100: 4}; the all-observed (never 0); the empty (never = n_conf, the rarity all 0).
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
  (the 12-place tolerance on the hand-computed values).
- The kernels (the dispersion / the ANOVA / the adherence) will extend this suite.

## Integration

- Consumed by `run_utests.sh` (section 4 — the pipeline, at the step 3 data-module position: between the FEATURES and
  the POSITIONS).
- The kernels are the SU / the entropy / the MI of the FEATURE_ANALYSIS phase 2 (the statistics, the cheap recompute on
  every run).
