# reversi/lm/hlp_gradient.py
The GRADIENT domain module of the LM pipeline — the function-only module: NO data class, NO store / load /
is_cache_consistent, NO init validation, NO hash (like hlp_validate and hlp_analytics). Two public names: `sigmoid` (the
scipy `expit` wrapper) + `hlp_gradient_compute` (the closure builder: captures X, z and
`alpha = ridge_regularization / M`; the returned `fg(w)` evaluates the normalized loss and gradient). TWO fg variants:
the classic vectorized-numpy closure (the default) and the high-performance numba single-pass kernel (K3, selected by
the `high_performance` flag; its row-block count T is the `hi_perf_blocks` config field, default 8). A NON-cache level
(like FEATURES, ANOVA, ZED): no cache_manager wiring, no rlmwf_09* / rlmwf_10* file ever.

## API

| name | contract |
|---|---|
| `sigmoid(x)` | the scipy `expit` wrapper — NO `@validate_call` (the hot-loop call) |
| `hlp_gradient_compute(ctx, high_performance=False, hi_perf_blocks=8)` | builds the `fg(w)` closure (NO `@validate_call` — see Conventions); returns a callable `(w float32 (N,)) -> (f float32, g float32 (N,))`. `high_performance=False` (default) → the classic closure; `True` → the numba kernel closure with `hi_perf_blocks` row-blocks (the config field, default 8; used only on the HP path). The returned closure carries a `high_performance` bool attribute identifying the variant. |

## Architecture

- `sigmoid(x)`: `return expit(x)` (the scipy import). NO `@validate_call` (it is called in the optimization hot loop).
  Docstring: expit's stability advantage is at extreme x, where the naive `1 / (1 + exp(−x))` overflows.
- `hlp_gradient_compute`: NO `@validate_call` (the no-validation note, as in hlp_indexes). Captures: `N = len(ctx.w)`,
  `X = ctx.design_matrix`, `M, P = X.shape`, `z = ctx.z`, `alpha = ctx.cfg.stat_model.ridge_regularization / M`.

### The classic variant (the default)

  - Pre-allocated buffers (the performance shape): `bincount_weights_buffer = np.empty(M*P, float32)` + the `(M, P)`
    view.
  - The `fg(w)` closure body: `linear_predictor = np.sum(w[X], axis=1)` (the w-INDEX sum — NOT `X @ w`);
    `zh = sigmoid(linear_predictor)`; `dzh = zh·(1 − zh)`; `rn = zh − z`; the normalized loss
    `f = 0.5·(‖rn‖²/M + alpha·‖w‖²)` (MSE + ridge, /M-normalized for dataset-size-independent convergence criteria); the
    normalized gradient `g = bincount(X_flat, weights = dzh·rn broadcast, minlength=N)/M + alpha·w`;
    `return np.float32(f), g.astype(np.float32, copy=False)` — the R1 cast: the return type says float32, so both
    outputs are float32.
  - The default variant: proven and readable.

### The high-performance variant (K3)

  - `_hp_fg_kernel` (`@njit(parallel=True, cache=True)`): ONE streaming pass over the design matrix rows, `prange` over
    the `T = hi_perf_blocks` row-blocks (config field, default 8). Per row: the f32 w-INDEX sum `acc` (gather);
    `zhv = 1/(1+exp(−acc))` (f32, the same sigmoid math), `rn = zhv − z[i]`, `vv = zhv·(1−zhv)·rn`; the row's `vv` is
    scattered into the block's PRIVATE f64 gradient buffer `g_blocks[b]`, and `rn²` into the block's f64 partial norm
    `norm_blocks[b]`.
  - No M×P temporary is ever materialized (the classic path allocates two ~384 MB temporaries per call at A2050 scale:
    the gather result + the bincount weight buffer). X is read once, row-contiguous (L2-friendly); w (311 KB at A2050)
    and the T×N f64 buffers (~5 MB at A2050) are L2-resident.
  - `fg_hp(w)`: clears the two private buffers, one kernel call, then the fixed-order final reduction in numpy:
    `f = 0.5·(Σ_b norm_blocks[b]/M + alpha·w·w)` (f64) → float32; `g = (Σ_b g_blocks[b])/M + alpha·w` (f64) → float32.
  - RACE-FREE without atomics: numba 0.67 has NO CPU atomics (CUDA-only) — each prange block writes only to its own
    private buffer; the cross-block reduction happens in numpy after the kernel.
  - RUN-DETERMINISTIC by construction: the block split is fixed (T is config-fixed, regardless of the thread count) and
    the final accumulation order is fixed (block order 0..T−1), so the result is bit-identical across runs and machines
    — the 2nd-instance byte-identity contract holds (the `test_hp_deterministic` test + the full-chain determinism tests
    pin it). The float32 rounding ORDER differs from the classic path (a few ulps on f and g), so a run with the HP
    variant follows a slightly different — but equivalent — L-BFGS trajectory (A2050: 356 iters / f = 1.4453826e-03 vs
    the classic 397 / f = 1.4444034e-03 — Δrel 0.07%, both converged, both g_norm < 1e-05).
  - M < T edge: empty blocks (i0 = i1) — exercised by design in the unit tests (M = 3 mock).
  - First call compiles the kernel (~1-3 s, `cache=True` → `__pycache__`).

## Verified invariants

Pinned by the `probes/verify_gradient.py` probe + `test_hlp_gradient.py` (15 tests, no DB, 3 classes) +
`test_wrk_gradient.py` (2 DB-gated tests + 2 no-DB flag-wiring tests).

- Source shape (probe A1-A15): 180 lines, the 2-name `__all__`, the expit + numba imports, the no-validation note, the
  `hi_perf_blocks: int = 8` parameter, the kernel def (prange + private f64 buffers), the flag + the variant marker
  attributes, 0 non-comment trailing-whitespace lines.
- The worker file shape (probe B1-B9): 65 lines, the factory WITH `@validate_call` + the pydantic import, NO
  cache_manager import (the by-design comment pinned); `_up` reads the `high_performance_fg` flag + `hi_perf_blocks`
  from `ctx.cfg.optimization` and passes both to `hlp_gradient_compute`; `_down` clears `ctx.fg`;
  `Worker("GRADIENT", ...)`.
- The live-DB golden re-derivation (probe D0 + D5-D10 + D12, rlm_02 — 199952 positions, the rlm_02 config has NO flag →
  the classic path): the pipeline bootstrap through GRADIENT; alpha + clipping; f(w=0) + g(w=0) re-derived (independent
  float64, the float32 R1 pin); f+g at w ≠ 0 (ridge); the closure stateless (2 calls); NO rlmwf_09*/10* files; the
  feature set (8 instances).
- The cross-file facts (probe E1/E4-E8): LMContext's `fg` field pre-declared; scipy in pyproject.toml + in the venv
  (1.18.1); the StatModelConfig `ridge_regularization` field (`ge=0.00`); the rlm_02 config.
- The unit suite (15 tests, no DB): the sigmoid goldens/ symmetry; the classic mock compute (the exact zero-weights
  goldens, the nonzero full math vs the independent float64 re-derivation, the /M scaling, the minlength empty-bucket
  pin, the R1 dtype pins, the statelessness); the TestHighPerformanceFg class (7 tests): the same zero-weights goldens
  via the HP path (M = 3 < T = 8, the empty blocks), the nonzero full math vs the float64 re-derivation (M = 5000, ~1e-9
  tracking), the classic-vs-HP equivalence (rtol 1e-5), the R1 dtype contract, the bit-identical determinism, the
  variant markers, the explicit hi_perf_blocks flow (T = 2 vs the float64 reference).
- The live goldens (DB-gated, `test_wrk_gradient.py`): the 4 pinned values at w=0 on the 199952-position rlm_02 (the
  classic path — rlm_02 has no flag); the no-DB TestGradientFlagWiring class (2 tests): the worker reads the flag + the
  block count (a Context-subclass mock) and builds the matching variant (the marker pin).
- The full-chain goldens (`test_lm_worker_full_chain.py`): A2030 (rlm_04, flag true) + A2050 (rlm_03, flag true)
  re-pinned to the HP trajectories (the A2050: 356 iters, CONVERGED_MIN_GRAD, f = 1.4453826e-03, g_norm = 7.973910e-06,
  the w_dense sha3 82b329dd..., the EF pins; the A2030: 71 iters, the w_dense sha3 90ca05a3...). The second-instance
  determinism tests (the in-run byte-identity contract) pass on the HP path.

## Open issues

- The two-loop recursion in `opt_lbfgs.py` is the second cost center of the HP OPTIMIZE (~25%): the `out=` product
  buffer (O2b) is the adopted optimization; the numba two-loop was measured and rejected (memory-bandwidth bound).

## Conventions

- The R1 float32 return contract: the NEXT level (OPTIMIZE) sees both `f` and `g` as float32 — for BOTH variants.
- The linear predictor is the w-INDEX sum (each X cell is a w-index), NOT `X @ w`; the /M normalization scales both the
  MSE and the ridge term by 1/M — the optimizer's convergence criteria are dataset-size independent (the ridge_scaling
  test pins it).
- The `high_performance_fg` config flag: default FALSE (the classic path) everywhere; rlm_03/rlm_04 opt in (the
  full-chain test configs); `hi_perf_blocks` (PositiveInt, default 8, the production block count) is read with the flag
  and used only on the HP path; a mid-run switch is numerically sound (same objective).
- `sigmoid` stays a bare wrapper (no `@validate_call`) — hot-loop performance; the worker file's triple blank lines are
  the canonical house pattern.
- The scipy `expit` is the classic path's only special-function dependency (scipy in pyproject.toml); the HP path
  computes the sigmoid inline in f32 (the kernel must be self-contained for numba).
- The f64 per-block accumulators are the PRODUCTION choice: f tracks the float64 reference to ~1e-12 rel (the f32
  accumulation showed ~3.2e-06 abs) at a +4.3 ms/call cost — negligible against the classic baseline.

## Integration

- The GRADIENT level; the worker (wrk_gradient.py) is the thin glue, this module the math. Consumes `ctx.design_matrix`
  (DESIGN_MTR), `ctx.z` (ZED), `ctx.w` (WMAPS — the (W,) float32 weight vector, 2981 on live rlm_02; OPTIMIZE later
  overwrites it) + `ctx.cfg.stat_model.ridge_regularization` + `ctx.cfg.optimization.high_performance_fg` /
  `hi_perf_blocks` (all CONFIG).
- Publishes `ctx.fg` (the loss/gradient closure) for the OPTIMIZE level. The flat-file numbering stops at
  rlmwf_08_DESIGN_MTR — the next cache level is GENERATE (rlmwf_12; 09/10/11 are skipped: ZED, GRADIENT and OPTIMIZE
  write nothing).
