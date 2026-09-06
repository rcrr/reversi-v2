# twolm/opt_lbfgs.py
The Limited-memory BFGS optimizer — the standalone numerical
engine the OPTIMIZE level runs. Implements L-BFGS with strong
Wolfe line search (cubic interpolation + zoom phase), restart
logic, dual convergence monitoring, warm-start capability,
logging and checkpointing via callback hooks. Self-contained: no
RLMContext, no pipeline imports, no DB.
> State: D-053 · 65f63be · 2026-08-29 · suite 13/0/0

## API

| name | contract |
|---|---|
| `FG` | `namedtuple('FG', ['fun', 'grad'])` — the function + evaluation tuple |
| `FixedSizeMaxList(size)` | fixed-size sliding window tracking the maximum pushed value (deque-backed); `max()` raises `RuntimeError` on empty (the T1 hard-bug fix, pinned) |
| `lbfgs(fg, x0, ...)` | the main optimizer — 16 kwargs (the 5 config scalars, `logger_fn`/`save_fn` hooks, the 4 warm-start kwargs); returns `(x_opt, info_dict)` with the 9 keys w/converged/reason/iters/f/g_norm/sl/yl/rho |
| `_two_loop_recursion(g, s, y, rho)` | the L-BFGS two-loop H_k·g (private) |
| `_strong_wolfe_line_search(...)` / `_zoom(...)` | the line search + its zoom phase (private) |
| `_hermite_cubic_interp(...)` / `_hermite_cubic_interp_min(...)` | the cubic Hermite interpolant + its interval minimum (private) |
| `_display_line_search(...)` | debug plot via matplotlib (private, lazy soft dependency) |

## Architecture

- Algorithm: (1) input validation (x0 must be an ndarray with
  float32/float64 dtype, fg callable — `TypeError` otherwise);
  (2) two-loop recursion for the search direction with gamma
  scaling (H = gamma·I); (3) restart — if the direction is not
  a descent direction (pᵀg ≥ 0), the memory is cleared and the
  direction falls back to steepest descent; (4) strong Wolfe
  line search: tries α=1 first, expands with cubic interpolation
  up to α_max, zooms when needed; (5) curvature condition —
  (yᵀs) > CURVATURE_THRESHOLD (1e-15) required before adding a
  pair to the history; (6) two convergence criteria: (a)
  gradient norm < threshold for N consecutive iterations, (b)
  fractional function decrease < threshold for N consecutive
  iterations; (7) fixed-size history (m pairs, FIFO).
- `save_fn` signature (7 params, the T5 fix):
  `save_fn(x, sl, yl, rho, k, f, g_norm)` — the worker's
  intermediate-checkpoint hook.

## Verified invariants

Pinned by `test_opt_lbfgs.py` (13 tests, 7 classes, no DB, no
PERF gate — ~0.040s). No probe file exists for this module (the
suite is the verification apparatus).

- `_two_loop_recursion` with empty history returns `g` (the
  gamma=1.0 identity); with random pairs (yᵀs > 0) produces a
  non-zero, shape-consistent result.
- Quadratic `f(x) = 0.5 xᵀHx` converges to x* = 0 (2D, 9 iters,
  f ≈ 4.9e-26); the handcrafted quadratic (known minimum
  [−1.0, 1.5]) converges within 1e-3.
- Rosenbrock converges from 5 random starts to [1,1] within
  1e-4 (multi-trial); the 1000-iteration single-start run
  matches.
- Zakharov 20D converges to the origin (seed 42, 1000 iters,
  within 1e-5).
- Warm-start: 100 continuous iterations vs 50+50 with
  save/resume — final positions match within 1e-4.
- Input validation: non-ndarray x0, int32 dtype, non-callable fg
  all raise `TypeError`.

## Open issues

None.

## Conventions

- The float32 contract: `x0` float32 stays float32 end-to-end
  (`x0.copy()`) — what the OPTIMIZE level relies on (the
  `NDArray[np.float32]` gate of
  `weights_compute_sha3_256_hash` never rejects a live weight
  vector).
- `matplotlib` is a soft dependency: imported lazily in
  `_display_line_search` with try/except, NOT in
  pyproject.toml (debug-only, acceptable).
- `FixedSizeMaxList.max()` is O(n) per call — fine for the
  small `min_grad_count` convergence-history usage (m=10
  default).
- `min_p_fun_decrease` is a FRACTION, not a percentage (the T6
  docstring fix).
- Warm-start does NOT preserve the convergence counters
  (`fgv_fun_prev`, `low_progress_count_*` reinitialized) —
  partial state, not a bug.

## Integration

- Consumed ONLY by the OPTIMIZE level (lm_worker_optimize step
  3): the worker passes `fg=ctx.fg`, `x0=w_init`, the 5 config
  scalars (max_iters, m, min_grad, min_p_fun_decrease,
  alpha-scaling), the two wrapper hooks and the 4 warm-start
  kwargs (w_init, initial_sl/yl/rho, initial_iter).
- The `info` dict returned at the end carries the 9 keys
  `optimization_info_dict` projects to the context.
