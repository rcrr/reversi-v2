# test/reversi/lm/test_hlp_gradient.py
The dedicated data-object suite of the hlp_gradient module. 3 classes / 14 tests / no DB, no gate, no artifacts — the
handcrafted-mock pattern, as in test_hlp_zed.

## Coverage

| class | tests | what it pins |
|---|---|---|
| `TestSigmoid` (no DB) | 2 | `test_sigmoid_golden`: `sigmoid([−1, 0, 1])` vs the hand-rolled float64 `1/(1+exp(−x))` (independent of the scipy expit path). `test_sigmoid_symmetry`: `sigmoid(x) + sigmoid(−x) == 1` |
| `TestHlpGradientCompute` (a `SimpleNamespace` mock ctx: `cfg.stat_model.ridge_regularization`, `w`, `design_matrix` uint32, `z` float32 — the 4 attributes `hlp_gradient_compute` reads; the `_reference` helper = the independent float64 re-derivation: hand-rolled sigmoid, the per-row `w[X]` w-INDEX sum via `np.add.at` — a different accumulation than the closure's broadcast bincount) | 6 | `test_compute_zero_weights_golden`: the EXACT goldens on the handcrafted (3, 2) matrix X = `[[0,1],[1,2],[0,2]]`, z = `[0.1, 0.9, 0.5]`, w = 0, ridge 0: f = 4/75, g = `[1/30, 0, −1/30]`. `test_compute_nonzero_weights`: the full math (sigmoid + residual + ridge) at w ≠ 0 vs the `_reference` (rtol 1e-5 — float32 pipeline vs float64 reference). `test_ridge_scaling`: `g(b)−g(a) = (b−a)/M·w` and `f(b)−f(a) = 0.5·(b−a)/M·‖w‖²` (the per-position /M normalization pinned directly). `test_minlength_empty_bucket`: an uncovered w-index still gets the pure ridge term (the `minlength=N` pin) and g keeps the full (N,) shape. `test_output_dtypes`: the R1 pin — f dtype float32, g dtype float32, g shape (N,). `test_closure_stateless`: two evaluations of the same w are identical (the pre-allocated buffers do not leak) |
| `TestHighPerformanceFg` (the same mock-ctx pattern on `high_performance=True`) | 6 | `test_hp_zero_weights_golden`: the SAME exact goldens (f = 4/75, g = `[1/30, 0, −1/30]`) through the numba kernel — M = 3 < T = 8, so the empty-block edge is exercised by design. `test_hp_nonzero_weights`: the full math on a seeded M = 5000 design matrix vs the independent float64 re-derivation (the f64 per-block accumulators track the reference to ~1e-9). `test_hp_matches_classic`: the two variants agree at rtol 1e-5 (the measured max relative delta ~1e-7 — the f32 sum order differs). `test_hp_output_dtypes`: the R1 float32 contract holds for the HP variant. `test_hp_deterministic`: two evaluations are BIT-identical (the fixed block split + fixed accumulation order — the 2nd-instance byte-identity guarantee). `test_hp_variant_markers`: the default build carries `high_performance=False`, the flagged one `True` |

## Goldens pinned

- The exact zero-weights goldens: f = 4/75, g = `[1/30, 0, −1/30]` — by construction (w = 0, ridge 0 → f
  = 0.5·mean((0.5−z)²), g[k] = 0.25·Σ_{m: X[m,*]=k}(0.5−z[m])/M).
- The hand-rolled sigmoid reference (independent of scipy).

## Conventions

- DB-free BY CONSTRUCTION (the module has no file I/O) — hence no SKIP_REGAB_DB gate and no `test.reversi.paths` import.
- NO init-validation tests: hlp_gradient is a function-only module (no data class to validate) — unlike test_hlp_zed.
- No ws lines, no dead imports, the no-DB header claim true from the first line.

## Integration

- Independent of the pipeline: the per-function pin that would catch a signature change to `hlp_gradient` (the worker
  test only exercises the end-to-end path on the live 199952-position rlm_02 dataset).
- The LIVE goldens (the 4 pinned values at w=0) live in test_wrk_gradient.py — the single source of truth for them.
