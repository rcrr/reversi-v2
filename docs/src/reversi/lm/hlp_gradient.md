# reversi/lm/hlp_gradient.py
The GRADIENT domain module of the RLM pipeline — the function-only
module: NO data class, NO store / load / is_cache_consistent, NO
init validation, NO hash (unlike every other rlm_* level). Two
public names: `sigmoid` (the scipy `expit` wrapper) +
`hlp_gradient_compute` (the closure builder: captures X, z and
`alpha = ridge_regularization / M`; the returned `fg(w)` evaluates
the normalized loss and gradient). The 9th active level (CREATED
sentinel → CONFIG → POSITIONS → FEATURES → INDEXES → WMAPS →
DESIGN_MTR → ZED → GRADIENT) and the SECOND non-cache level (after
ZED): no cache_manager wiring, no rlmwf_07* / rlmwf_08* file ever.
> State: D-094 · 34442b2 · 2026-09-01 · suite 8/0/0

## API

| name | contract |
|---|---|
| `sigmoid(x)` | the scipy `expit` wrapper — NO `@validate_call` (the hot-loop call, left as-is by Roberto) |
| `hlp_gradient_compute(ctx)` | builds the `fg(w)` closure (NO `@validate_call` — see Conventions); returns a callable `(w float32 (N,)) -> (f float32, g float32 (N,))` |

## Architecture

- `sigmoid(x)`: `return expit(x)` (the scipy import). NO
  `@validate_call` (M2, left as-is by Roberto's call — it is
  called in the optimization hot loop). Docstring: the naive
  `1 / (1 + exp(−x))` is what it replaced; expit's stability
  advantage is at extreme x (where the naive `np.exp(−x)`
  overflows).
- `hlp_gradient_compute`: NO `@validate_call` (the L52
  no-validation note — the hlp_indexes L166 class, the D-094 T3
  fix). Captures: `N = len(ctx.w)`, `X = ctx.design_matrix`,
  `M, P = X.shape` (M = positions), `X_flat = X.ravel()`,
  `z = ctx.z`, `alpha = ctx.cfg.stat_model.ridge_regularization
  / M`. Pre-allocated buffers (the D-094 perf shape):
  `bincount_weights_buffer = np.empty(M*P, float32)` + the
  `(M, P)` view.
- The `fg(w)` closure body: `linear_predictor = np.sum(w[X],
  axis=1)` (the w-INDEX sum — NOT `X @ w`); `zh =
  sigmoid(linear_predictor)`; `dzh = zh·(1 − zh)`; `rn = zh − z`;
  the normalized loss `f = 0.5·(‖rn‖²/M + alpha·‖w‖²)` (MSE +
  ridge, /M-normalized for dataset-size-independent convergence
  criteria); the normalized gradient `g = bincount(X_flat,
  weights = dzh·rn broadcast, minlength=N)/M + alpha·w`;
  `return np.float32(f), g.astype(np.float32, copy=False)` — the
  R1 (D-093, fixed in D-094) cast: the return type says float32,
  so both outputs are float32 (the behaviour change Roberto
  chose).

## Verified invariants

Pinned by the 54-call `probes/verify_gradient.py` +
`test_hlp_gradient.py` (8 tests, no DB) +
`test_lm_worker_gradient.py` (2 DB-gated tests).

- Source shape (probe A1-A13): 91 lines, the 2-name `__all__`,
  the expit import, the no-validation note (L52), the captures
  (L60-65), the buffers (L68-69), the fg body (L71-89), the R1
  return (L89), 0 non-comment trailing-whitespace lines.
- The worker file shape (probe B1-B9): 62 lines, the factory WITH
  `@validate_call` + the pydantic import (T2), NO cache_manager
  import (the L48 by-design comment pinned), `_up` sets `ctx.fg`,
  `_down` clears it, `Worker("GRADIENT", ...)`.
- The live-DB golden re-derivation (probe D0 + D5-D10 + D12,
  rlm_02 — 199952 positions): the pipeline bootstrap through
  GRADIENT; alpha + clipping; f(w=0) + g(w=0) re-derived
  (independent float64, the float32 R1 pin); f+g at w ≠ 0
  (ridge); the closure stateless (2 calls); NO rlmwf_07*/08*
  files; the feature set (8 instances).
- The cross-file facts (probe E1/E4-E8): RLMContext's `fg` field
  pre-declared; scipy in pyproject.toml (T1) + in the venv
  (1.18.1); the StatModelConfig `ridge_regularization` field
  (`ge=0.00`); the rlm_02 config.
- The unit suite (8 tests, no DB): the sigmoid goldens/symmetry;
  the mock compute (the exact zero-weights goldens, the nonzero
  full math vs the independent float64 re-derivation, the /M
  scaling, the minlength empty-bucket pin, the R1 dtype pins, the
  statelessness).
- The live goldens (DB-gated, `test_lm_worker_gradient.py`): the
  4 pinned values at w=0 on the 199952-position rlm_02 — the
  single source of truth after the step-3 class c deletions (D1-
  D4 + D11 to the worker test, E2/E3 to the hub).

## Open issues

None.

## Conventions

- The R1 float32 return contract (D-093 → D-094): the NEXT level
  (OPTIMIZE) sees both `f` and `g` as float32.
- The linear predictor is `np.sum(w[X], axis=1)` — the w-INDEX
  sum (each X cell is a w-index), NOT `X @ w`.
- The /M normalization: both the MSE and the ridge terms are
  scaled by 1/M — the optimizer's convergence criteria are
  dataset-size independent (pinned directly by the ridge_scaling
  test).
- M2 (left as-is): `sigmoid` stays a bare wrapper (no
  `@validate_call`) — hot-loop performance.
- M4 (left as-is, the worker file): the triple blank lines are
  the canonical pattern of all 8 worker files (house style).
- The scipy `expit` is the only special-function dependency of
  the pipeline (scipy in pyproject.toml since D-094 T1).

## Integration

- The 9th RLM level; the worker (lm_worker_gradient.py) is the
  thin glue, this module the math. Consumes `ctx.design_matrix`
  (DESIGN_MTR), `ctx.z` (ZED), `ctx.w` (WMAPS — the (W,) float32
  weight vector, W = total weights; 2981 on live rlm_02; the
  OPTIMIZE level later overwrites it with the optimized values)
  + `ctx.cfg.stat_model.ridge_regularization` (CONFIG).
- Publishes `ctx.fg` (the loss/gradient closure) for the OPTIMIZE
  level. The flat-file numbering stops at rlmwf_06_DESIGN_MTR —
  the next cache level (OPTIMIZE) takes rlmwf_08 (07 is skipped,
  as 03 was at FEATURES).
