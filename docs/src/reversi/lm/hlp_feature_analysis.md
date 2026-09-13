# reversi/lm/hlp_feature_analysis.py
The FEATURE_ANALYSIS data module (the I-017, the step 3 data
plane): the kernels over the frequency tables (the marginal /
the joint counts from the accumulators, the T7-T8 in
hlp_random_play). The SU / entropy / mutual-information
kernels (T11, D-181) are landed; the dispersion + the never-
observed audit (T12), the ANOVA kernels (T13) and the
adherence kernels (T14) follow. Pure math from the frequency
tables — NO DB, NO positions. The worker (wrk_feature_analysis,
T16) calls these on the accumulator output (the phase-2
recompute, cheap, on every run).
> State: D-181 (T11: the SU/entropy/MI kernels) · 2026-09-13 ·
suite 10/0/0

## API
- `entropy(counts) -> float` — the Shannon entropy H in bits,
  from the count array (the marginal or the joint). The 0-log-0
  convention (the zero counts contribute 0); the empty / the
  all-zero -> 0.
- `mutual_information(joint_counts, marg_u, marg_v) -> float` —
  I(u; v) in bits, the identity I = H(u) + H(v) - H(u, v) (the
  ratio form's 0/0 avoided; the joint entropy is the entropy of
  the joint counts). Clamped to >= 0 (the floating-point
  rounding of the identity can give a tiny negative).
- `symmetric_uncertainty(I, H_u, H_v) -> float` — the
  symmetrical uncertainty SU = 2·I / (H(u) + H(v)), in [0, 1].
  The 0-denominator guard: SU = 0 if H(u) + H(v) == 0 (the
  degenerate variables — the code-0 "no match" single-category,
  the ODP-4/ODP-8 close).

## Architecture
- The SU is computed from the IDEAL (synthetic) frequencies: a
  structural property of the game geometry + the feature set,
  free of the DB sample noise (the design section 3.3 phase 2).
  The marginal / the joint come from the T7-T8 accumulators
  (hlp_random_play); this module is the from-frequency-tables
  math only.
- The MI identity I = H(u) + H(v) - H(u, v) (vs the ratio form
  p(u,v) log(p(u,v)/(p(u)p(v)))): the 0/0 of the ratio (the
  cell with p(u,v) = 0, or p(u) = 0) is avoided; the joint
  entropy is the entropy of the joint counts (the observed
  cells). The clamp to >= 0 guards the floating-point rounding.
- The SU 0-denominator guard (the design: "SU = 0 if the
  denominator is 0"): the degenerate sub-variable (the single
  observed category — the code-0 "no match" when the pattern
  never matches) has H = 0; the pair (u, v) with H(u) + H(v) =
  0 is the 0/0, guarded to 0 (not a measurement — the ODP-4/
  ODP-8 close: the 1s and the 0/0 are locks, not signals).

## Verified invariants
- The hand-computed toy tables (test_hlp_feature_analysis,
  10 tests): the uniform 4 (H = 2), the degenerate (H = 0),
  the binary p = [0.25, 0.75] (H = 0.8112781244591328), the
  empty (H = 0, the n = 0 guard); the perfect-correlation MI
  (u == v: I = 1), the independent MI (I = 0), the non-negative
  clamp; the SU = 1 (the perfect), the SU = 0 (the
  independent), the SU = 0 (the 0-denominator guard).

## Open issues
- The T12 dispersion + the never-observed audit (the K_obs /
  H / H_norm / coverage per sub-variable + the n_configurations
  - K_obs + the rarity profile) — PENDING.
- The T13 ANOVA kernels (the eta² / the omega² per sub-variable,
  the K = 1 degeneracy + the K > N ValueError guards) —
  PENDING.
- The T14 adherence kernels (the chi-square merged-tail, the
  KL, the TV 0-log-0) — PENDING.
- The T16 worker (wrk_feature_analysis) wires these into the
  pipeline (the cache flow + the phase-2 recompute + the
  reports) — PENDING.

## Conventions
- The house GNU header + the provenance docstring (the doc
  sections, the D-number).
- The pure functions over the numpy count arrays (the marginal
  / the joint from the accumulators); no state, no DB, no
  positions.
- The 0-log-0 convention (the standard entropy / KL / TV
  convention) throughout.

## Integration
- Consumes the T7-T8 accumulators' output (the marginal / the
  joint counts) — the hlp_random_play data plane.
- Future consumer: the FEATURE_ANALYSIS worker (T16,
  wrk_feature_analysis.py) — the phase-2 recompute (the
  statistics on every run, including the cache hit) + the
  reports (the console + the TXT + the optional CSV).
