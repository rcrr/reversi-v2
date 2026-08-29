# opt_lbfgs.py — analysis

Date: 2026-08-29. Module added by Roberto (2 files: opt_lbfgs.py + test_opt_lbfgs.py).

Suite: **4 tests, GREEN 4/0/0** (no PERF gates). Suite is fast (~0.040s).

Full workspace: **389 tests, GREEN, 17 skipped.**

## Architecture

`opt_lbfgs` implements the Limited-memory BFGS optimizer with strong Wolfe
line search, restart logic, convergence monitoring, warm-start capability,
logging, and checkpointing.

### Components

| Component | Role |
|---|---|
| `FG = namedtuple('FG', ['fun', 'grad'])` | Function+evaluation tuple. |
| `FixedSizeMaxList(size)` | Fixed-size sliding window that tracks the maximum pushed value. Backed by `collections.deque(maxlen=size)`. |
| `lbfgs(fg, x0, ...)` | Main optimizer. Returns `(x_opt, info_dict)`. |
| `_two_loop_recursion(g, s, y, rho)` | Computes H_k · g (L-BFGS two-loop). |
| `_strong_wolfe_line_search(fg, x, p, fgv0, c1, c2, ...)` | Strong Wolfe line search with cubic interpolation and zoom phase. |
| `_zoom(phi, alo, ahi, ...)` | Zoom phase: bisection + cubic interpolation bracketing. |
| `_hermite_cubic_interp(x0, y0, dy0, x1, y1, dy1, x)` | Cubic Hermite interpolant and its first two derivatives at x. |
| `_hermite_cubic_interp_min(x0, y0, dy0, x1, y1, dy1)` | Finds the minimum of the cubic Hermite interpolant in [x0, x1]. |
| `_display_line_search(...)` | Debug: plots phi(alpha) via matplotlib (optional, lazy-imported). |

### Algorithm

Standard L-BFGS with:
1. Input validation (x0 must be ndarray with float32/float64 dtype, fg must be callable).
2. Two-loop recursion for the search direction with gamma scaling (H = gamma · I).
3. Restart: if search direction is not a descent direction (p^T g ≥ 0), memory is cleared and direction falls back to steepest descent.
4. Strong Wolfe line search: tries α=1 first, expands with cubic interpolation up to α_max, zooms when needed.
5. Curvature condition: (y^T s) > 1e-15 required before adding a pair to the history.
6. Two convergence criteria: (a) gradient norm < threshold for N consecutive iterations, (b) fractional function decrease < threshold for N consecutive iterations.
7. Fixed-size history (m pairs, FIFO).

## Verified facts (V1–V5)

| # | Fact | Method |
|---|---|---|
| V1 | `_two_loop_recursion` with empty history returns `g` (gamma=1.0 identity) | Direct test with `[]` lists |
| V2 | `_two_loop_recursion` with 2 random pairs produces non-zero, shape-consistent result | Random s, y with y^T s > 0 |
| V3 | Quadratic function `f(x) = 0.5 x^T H x` converges to x* = 0 | 2D test: 9 iters, f=4.9e-26 |
| V4 | Rosenbrock converges from 5 random starts to [1,1] within 1e-4 | Multi-trial: all 5 OK |
| V5 | Input validation: non-ndarray → TypeError, int32 dtype → TypeError, non-callable fg → TypeError | Edge case tests |

## Defects

### T1 — `RuntimeException` typo (L56, HARD BUG)
`raise RuntimeException(...)` should be `raise RuntimeError(...)`. `RuntimeException` is not defined (would raise `NameError` at runtime). This path fires when `max()` is called on an empty `FixedSizeMaxList`.

**Severity**: Hard — crashes if deque is ever empty when `max()` is called.

### T2 — `CURVATURE_THRESHOLD` dead constant (L400)
`CURVATURE_THRESHOLD = 1.e-15` is defined but never referenced. The curvature check at L480 uses the literal `1.e-15` directly. Either the constant should be used or removed.

**Severity**: Cosmetic.

### T3 — `low_progres_count` misspelling (L409-458)
`low_progres_count_f` and `low_progres_count_g` should be `low_progress_count_*` (missing 's'). Internal variable names only — user-facing log message at L458 correctly says "progress".

**Severity**: Cosmetic.

### T4 — `_hermite_cubic_interp_min` fallthrough to non-minimum (L149-152)
When `stationary_point_0[3] <= 0` (not a minimum), the code returns `stationary_point_1` unconditionally. But if `stationary_point_1[3] <= 0` as well, it should return `None` (no valid minimum in the interval), per the docstring. The current code returns a maximum/inflection point instead.

**Severity**: Medium — could select a non-minimum step in the line search, degrading convergence.

### T5 — `save_fn` type hint / docstring mismatch (L345, L380)
- Type hint: `Callable[..., int], None]` → 5 parameters `(x, sl, yl, rho, k)`.
- Docstring: `save_fn(x, sl, yl, rho, k)` → 5 parameters.
- Actual call at L501: `save_fn(x, sl, yl, rho, k, fgv.fun, g_norm_history.max())` → **7 parameters**.

The code and the test agree on 7 parameters. The type hint and docstring are wrong.

**Severity**: Medium — type-checkers (mypy) would flag the mismatch; docstring misleads users.

### T6 — `min_p_fun_decrease` docstring: "percentage" vs "fraction" (L366)
The parameter is documented as "Minimum percentage acceptable loss decrease" but the code computes a fractional (not percentage) relative decrease: `p_diff = diff / np.fabs(fgv.fun)`. The default `1e-14` is a fraction, not a percentage.

**Severity**: Minor — docstring only.

## Observations (not defects)

- **Warm-start doesn't preserve convergence counters**: `fgv_fun_prev` and `low_progres_count_*` are reinitialized when resuming. Not a bug, but partial state.
- **`matplotlib` is a soft dependency**: imported lazily in `_display_line_search` with a try/except. Not in `pyproject.toml` — acceptable since it's debug-only.
- **No `np.double` vs `np.float64` consistency**: source uses `np.float32`/`np.float64`; test uses `np.double` (alias for `np.float64`). Not a bug.
- **`FixedSizeMaxList.max()` is O(n) per call**: uses `max(self._buffer)` which scans all elements. With `m=10` (the lbfgs default history size), the convergence-history usage `min_grad_count` is small, so this is fine.

## Suite status

```
$ python -m unittest twolm.test.test_opt_lbfgs
....
--------------------------------------------------------------
Ran 4 tests in 0.040s
OK
```

| Class | Tests | Coverage |
|---|---|---|
| `TestLBFGSBaseFunction` | 1 | Simple quadratic convergence |
| `TestLBFGSRosenbrockFunction` | 1 | Rosenbrock convergence (1000 iters) |
| `TestLBFGSZakharovFunction` | 1 | Zakharov 20D convergence (1000 iters) |
| `TestLBFGSWarmStart` | 1 | Save/resume across two 50-iter runs |

## Appendix: line-number reference (2026-08-29)

- `FG`: L38
- `FixedSizeMaxList`: L47
- `FixedSizeMaxList.push`: L51
- `FixedSizeMaxList.max`: L54
- `_display_line_search`: L63
- `_hermite_cubic_interp_min`: L119
- `_hermite_cubic_interp`: L155
- `_two_loop_recursion`: L188
- `_strong_wolfe_line_search`: L232
- `_zoom`: L289
- `lbfgs`: L334
- `CURVATURE_THRESHOLD`: L400
- `min_grad` convergence: L432-443
- `min_p_fun_decrease` convergence: L445-461
- `Two-loop direction`: L464
- `Restart logic`: L466-472
- `Line search call`: L474
- `Curvature condition`: L480-487
- `History update`: L481-487
- `Logging`: L493-497