# reversi/test/test_hlp_feature_analysis.py
The NO-DB micro-suite of the FEATURE_ANALYSIS data module (the
I-017): the T11 SU / entropy / mutual-information kernels
(D-181) — the hand-computed toy tables (the uniform / the
degenerate / the binary entropies, the perfect-correlation /
the independent mutual informations, the SU = 1 / 0 / the 0-
denominator guard). 3 classes / 10 tests / no DB.
> State: D-181 (T11) · 2026-09-13 · suite 10/0/0

## Coverage

| class | tests | what it pins |
|---|---|---|
| `TestEntropy` | 4 | `test_uniform` (the uniform 4: H = log2 4 = 2); `test_degenerate` (the single-category: H = 0); `test_binary` (p = [0.25, 0.75]: H = 0.8112781244591328); `test_empty` (the all-zero / the empty: H = 0, the n = 0 guard) |
| `TestMutualInformation` | 3 | `test_perfect_correlation` (u == v: the marginals [2, 2], the joint [2, 0, 0, 2], I = 1 + 1 - 1 = 1); `test_independent` (the marginals [2, 2], the joint [1, 1, 1, 1], I = 1 + 1 - 2 = 0); `test_non_negative` (the floating-point clamp: I >= 0) |
| `TestSymmetricUncertainty` | 3 | `test_perfect` (I = H_u = H_v = 1: SU = 2/2 = 1); `test_independent` (I = 0: SU = 0); `test_zero_denominator` (H_u = H_v = 0: the 0/0 guard -> SU = 0, the ODP-4/ODP-8 close) |

## Goldens pinned

- The hand-computed entropy values: the uniform 2.0, the
  binary 0.8112781244591328 (the exact -[0.25 log2 0.25 +
  0.75 log2 0.75]), the degenerate 0.0, the empty 0.0.
- The hand-computed MI values: the perfect correlation 1.0
  (u == v, the joint on the diagonal), the independent 0.0
  (the full 2 x 2 support, the marginals uniform).
- The SU guards: the perfect 1.0, the independent 0.0, the 0-
  denominator 0.0 (the degenerate variables — the code-0 "no
  match" single-category).

## Conventions

- The house test header (the "How to run" block).
- The pure-function micro-suite: the hand-computed toy count
  arrays (the marginal / the joint), the assertAlmostEqual
  (the 12-place tolerance on the hand-computed values).
- The T12-T14 kernels (the dispersion / the ANOVA / the
  adherence) will extend this suite as they land.

## Integration

- Consumed by `run_utests.sh` (section 4 — the pipeline, at the
  step 3 data-module position: between the FEATURES and the
  POSITIONS; the worker wrk_feature_analysis lands in T16).
- The T11 kernels are the SU / the entropy / the MI of the
  FEATURE_ANALYSIS phase 2 (the statistics, the cheap recompute
  on every run).
