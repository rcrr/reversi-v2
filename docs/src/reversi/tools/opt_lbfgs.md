# reversi/tools/opt_lbfgs.py
The Limited-memory BFGS optimizer — the standalone numerical engine the OPTIMIZE level runs. Implements L-BFGS with
strong Wolfe line search (cubic interpolation + zoom phase), restart logic, dual convergence monitoring, warm-start
capability, logging and checkpointing via callback hooks. Self-contained: no LMContext, no pipeline imports, no DB.

## API

| name | contract |
|---|---|
| `FG` | `namedtuple('FG', ['fun', 'grad'])` — the function + evaluation tuple |
| `FixedSizeMaxList(size)` | fixed-size sliding window tracking the maximum pushed value (deque-backed); `max()` raises `RuntimeError` on empty (pinned) |
| `lbfgs(fg, x0, ...)` | the main optimizer — 16 parameters (fg, x0 + 14 defaulted: the 8 config scalars, the `logger`/`save_fn` hooks, the 4 warm-start kwargs initial_sl/initial_yl/initial_rho/initial_iter); `TypeError` when x0 is not a float32/float64 ndarray or fg is not callable, `ValueError` on inconsistent iteration bounds (max_iters < 1 or initial_iter >= max_iters); returns `(x_opt, info_dict)` with the 9 keys w/converged/reason/iters/f/g_norm/sl/yl/rho (reason: CONVERGED_MIN_GRAD / CONVERGED_LOW_PROGRESS / MAX_ITERS_REACHED) |
| `_two_loop_recursion(g, s, y, rho)` | the L-BFGS two-loop H_k·g (private) |
| `_strong_wolfe_line_search(...)` / `_zoom(...)` | the line search + its zoom phase (private) |
| `_hermite_cubic_interp(...)` / `_hermite_cubic_interp_min(...)` | the cubic Hermite interpolant + its interval minimum (private) |
| `_display_line_search(...)` | debug plot via matplotlib (private, lazy soft dependency) |

## Architecture

- Algorithm: (1) input validation (x0 must be an ndarray with float32/float64 dtype, fg callable — `TypeError`
  otherwise; inconsistent iteration bounds — max_iters < 1 or initial_iter >= max_iters — raise `ValueError`);
  (2) two-loop recursion for the search direction with gamma scaling (H = gamma·I) — the per-op product buffer is
  pre-allocated ONCE per call (f64, `prod`) and the two per-op products are written with `np.multiply(...,
  out=prod)` + `np.subtract/np.add(..., out=delta/r)` — it replicates the classic per-op temporaries' dtype
  semantics BIT-FOR-BIT (the f64 product, the f32 in-place downcast), so the L-BFGS trajectory is unchanged (the
  bit-identity test pins it); the numba two-loop variant was measured and NOT adopted (memory-bandwidth bound +
  the serial two-loop recurrence resists prange — D-146); (3) restart — if the direction is not a descent
  direction (pᵀg ≥ 0), the memory is cleared and the direction falls back to steepest descent; (4) strong Wolfe
  line search: tries α=1 first, expands with cubic interpolation up to α_max, zooms when needed; (5) curvature
  condition — (yᵀs) > CURVATURE_THRESHOLD (1e-15) required before adding a pair to the history; (6) two
  convergence criteria: (a) gradient norm < threshold for N consecutive iterations, (b) fractional function
  decrease < threshold for N consecutive iterations; (7) fixed-size history (m pairs, FIFO).
- `save_fn` signature (7 params): `save_fn(x, sl, yl, rho, k, f, g_norm)` — the worker's intermediate-checkpoint hook.

## Verified invariants

Pinned by `test_opt_lbfgs.py` (24 tests, 9 classes, no DB, no PERF gate) + `probes/verify_optimize.py` (E5-E7 pin
this module's signature, the info-dict literals and the x0.copy() contract). No dedicated probe file exists for the
module (the suite is the verification apparatus).

- `_two_loop_recursion` with empty history returns `g` (the gamma=1.0 identity); with random pairs (yᵀs > 0)
  produces a non-zero, shape-consistent result; the out= form is BIT-IDENTICAL to the original per-op-temporary
  algorithm (the reference embedded verbatim in the test, three seeded histories: f32 n=50/m=5, f32 n=500/m=9,
  f64 n=64/m=7 — `test_out_equals_original_bit_identical`).
- The `info` dict: exactly the 9 keys; `info['w']` IS the returned x; `f` / `g_norm` agree with a fresh `fg(x)`
  evaluation; `iters` within (0, max_iters]; sl/yl/rho co-length and the history capped at m
  (`TestLBFGSInfoContract`).
- Input validation: non-ndarray x0, int32 dtype, non-callable fg raise `TypeError`; max_iters < 1 and
  initial_iter >= max_iters raise `ValueError` (`TestLBFGSInputValidation`).
- The stop reasons pinned at runtime: `CONVERGED_MIN_GRAD` (a quadratic), `MAX_ITERS_REACHED` (Rosenbrock, 2
  iters, `iters == 2`), `CONVERGED_LOW_PROGRESS` (a near-flat function) (`TestLBFGSStopReasons`).
- x0 is never mutated (the `x0.copy()` contract); a float32 x0 stays float32 end-to-end (x, the sl/yl vectors,
  g_norm); the `logger` hook receives the log lines (`TestLBFGSInfoContract`).
- The handcrafted quadratic (known minimum [−1.0, 1.5]) converges within 1e-3 (`TestLBFGSBaseFunction`); Rosenbrock
  from [−1.0, −1.0] to [1, 1] within 1e-4, 1000 iters (`TestLBFGSRosenbrockFunction`); the 20D Zakharov converges
  to the origin (seed 42, 1000 iters, within 1e-5) (`TestLBFGSZakharovFunction`).
- Warm-start: 100 continuous iterations vs 50+50 with save/resume — final positions match within 1e-4
  (`TestLBFGSWarmStart`).
- `FixedSizeMaxList`: `max()` on the empty window raises `RuntimeError`; the push/max/len/eviction behavior is
  pinned (`TestFixedSizeMaxList`).

## Open issues

None. (The remaining coverage gaps — the restart branch, the curvature skip, the Hermite + line-search internals,
integration-only — are tracked in the test doc's Integration section.)

## Conventions

- The float32 contract: `x0` float32 stays float32 end-to-end (`x0.copy()`) — what the OPTIMIZE level relies on (the
  `NDArray[np.float32]` gate of `hlp_optimize_weights_compute_hash` never rejects a live weight vector).
- `matplotlib` is imported lazily in `_display_line_search` with try/except — the display helper is optional at call
  time (matplotlib IS a declared project dependency).
- `FixedSizeMaxList.max()` is O(n) per call — fine for the small `min_grad_count` convergence-history usage (3 by
  default).
- `min_p_fun_decrease` is a FRACTION, not a percentage.
- Warm-start does NOT preserve the convergence counters (`fgv_fun_prev`, `low_progress_count_*` reinitialized) — partial
  state, not a bug.

## Integration

- Consumed ONLY by the OPTIMIZE level (wrk_optimize step 3): the worker call passes 16 kwargs — fg, x0, the 8 config
  scalars (c1, c2, min_grad, min_p_fun_decrease, max_iters, m, log_every_n, save_every_n) + logger + save_fn + the 4
  warm-start kwargs (initial_sl/initial_yl/initial_rho/initial_iter).
- The `info` dict returned at the end carries the 9 keys `hlp_optimize_info_dict` projects to the context.
