<!-- ARCHIVED — D-106 step 15 (the docs/ rewrite, 2026-09-04): the
     complete session-25 test-doc (D-094 M1) moved out of
     docs/src/twolm/test/test_rlm_gradient.md per
     docs_rules.md §1/§4/§6. This is a frozen historical record:
     it is never updated. NOTE: the file is UNCHANGED since its
     creation at D-094 (34442b2, 2026-09-01) — 2 classes / 8
     tests / 169 lines is still correct (no step-3 conversion
     touched it — its G-tier pins survived in the probe). The
     "573 tests / 68 skipped" full-discover figure predates steps
     3-10 (current: 664/87 gated). -->

# twolm/test/test_rlm_gradient.py

Analysis date: 2026-09-01 — CREATED in the D-094 fix campaign
(session 25, D-094 M1 — the coverage gap found by the D-093
analysis: at bring-in the fg math was only tested through the full
8-level pipeline run on the 199952-position dataset). Probe
(scratch/verify_gradient.py, 61 checks, tier G): 0 mismatches.

## Suite status (session 25)

- `test_rlm_gradient`: 8/0/0 (2 classes; no DB, no gate, no
  artifacts — the handcrafted-mock pattern, as in test_rlm_zed).

## State per Roberto

NEW in D-094 (M1: Roberto "OK"). No further campaign — the file is
clean from day one (no ws lines, no dead imports, the no-DB header
claim true from the first line).

## Architecture (169 lines)

- 2 classes:
- `TestSigmoid` (L54-69): `test_sigmoid_golden` (L57-63) —
  sigmoid([−1, 0, 1]) vs the hand-rolled float64
  `1/(1+exp(−x))` (independent of the scipy expit path);
  `test_sigmoid_symmetry` (L65-69) — `sigmoid(x) + sigmoid(−x)
  == 1`.
- `TestRLMGradientCompute` (L71-165): `_mock_ctx` (L74-79) — the
  SimpleNamespace chain (`cfg.stat_model.ridge_regularization`,
  `w`, `design_matrix` uint32, `z` float32); `_reference` (L81-96)
  — the independent float64 re-derivation (hand-rolled sigmoid,
  the per-row `w[X]` w-INDEX sum, np.add.at — a different
  accumulation than the closure's broadcast bincount);
  `test_compute_zero_weights_golden` (L98-108) — the exact
  goldens on the (3, 2) handcrafted matrix: f = 4/75, g =
  [1/30, 0, −1/30] (w = 0, ridge 0); `test_compute_nonzero_weights`
  (L110-119) — the full math (sigmoid + residual + ridge) at w ≠ 0
  vs the `_reference`; `test_ridge_scaling` (L121-133) —
  g(b)−g(a) = (b−a)/M·w and f(b)−f(a) = 0.5·(b−a)/M·‖w‖² (the
  per-position /M normalization pinned directly);
  `test_minlength_empty_bucket` (L136-143) — an uncovered w-index
  still gets the pure ridge term (g[2] = 0.015·0.3) and g keeps
  the full (N,) shape; `test_output_dtypes` (L146-153) — the R1
  (D-093) pin: f dtype float32, g dtype float32, g shape (N,);
  `test_closure_stateless` (L156-163) — two evaluations of the
  same w are identical (the pre-allocated buffers do not leak).

## Verified facts

- 8/0/0 without any DB / gate / temp artifact (the tier-G probe
  pins the no-DB wiring: no `from twolm.logistic_model`, no
  SKIP_REGAB_DB, no twolm.test.paths, no `import os`).
- The goldens are exact by construction: with w = 0 and ridge 0,
  f = 0.5·mean((0.5−z)²) = 4/75 and g[k] = 0.25·Σ_{m: X[m,*]=k}
  (0.5−z[m])/M = [1/30, 0, −1/30] on the handcrafted
  X = [[0,1],[1,2],[0,2]], z = [0.1, 0.9, 0.5].
- The nonzero-weights case agrees with the independent float64
  re-derivation at rtol 1e-5 (the float32 pipeline vs the
  float64 reference).
- The R1 dtype pins (f + g float32) hold post-D-094-cast.

## Minor notes

- The mock context needs only the 4 attributes
  `rlm_gradient_compute` reads (`ctx.w`, `ctx.design_matrix`,
  `ctx.z`, `ctx.cfg.stat_model.ridge_regularization`) — the
  SimpleNamespace chain is the minimal mock, the zed pattern.
- No init-validation tests: rlm_gradient is a function-only
  module (no data class to validate) — unlike test_rlm_zed.

## Appendix — line reference

169 lines (created at D-094).

- L45-51: imports (SimpleNamespace L46, numpy L48-49, the 2
  domain names L51)
- L54-69: `TestSigmoid` (golden L57-63, symmetry L65-69)
- L71-165: `TestRLMGradientCompute` (mock L74-79, reference
  L81-96, 6 tests L98-163)
