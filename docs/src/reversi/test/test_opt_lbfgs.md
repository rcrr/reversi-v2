# reversi/test/test_opt_lbfgs.py
The opt_lbfgs unit suite: integration-level coverage (4 diverse test functions + warm-start) plus unit-level tests for
the main internal components (input validation, `FixedSizeMaxList` incl. the hard-bug regression, the two-loop
recursion). 7 classes / 13 tests, no DB, no PERF gate (~0.040s).

## Coverage

| class | tests | what it pins |
|---|---|---|
| `TestLBFGSInputValidation` | 3 | non-ndarray x0 → `TypeError`; int32 dtype → `TypeError`; non-callable fg → `TypeError` (the input-validation paths in `lbfgs`) |
| `TestFixedSizeMaxList` | 4 | `test_max_on_empty_raises` (pins the `RuntimeError` fix); push 1/3/2 → `max()==3`, `len()==3`; eviction at maxlen=2 (5/1/3 → 5 evicted, `max()==3`); fresh list `len()==0` |
| `TestTwoLoopRecursion` | 2 | empty history → `g` unchanged (the identity); 3 random s/y pairs (yᵀs > 0) → correct shape, non-zero output |
| `TestLBFGSBaseFunction` | 1 | the handcrafted quadratic `x[0] − x[1] + 2·x[0]·x[1] + 2·x[0]² + x[1]²`, known minimum [−1.0, 1.5], within 1e-3 (basic convergence on a convex quadratic) |
| `TestLBFGSRosenbrockFunction` | 1 | Rosenbrock from [−1, −1], known minimum [1.0, 1.0] (f*=0), 1000 iters, within 1e-4 (non-convex narrow curved valley — the L-BFGS stress test) |
| `TestLBFGSZakharovFunction` | 1 | 20D Zakharov, minimum at the origin, random start seed(42), 1000 iters, within 1e-5 (moderate-dimensional convex) |
| `TestLBFGSWarmStart` | 1 | 100 continuous iterations vs 50+50 with save/resume — final positions match within 1e-4 (the warm-start / checkpointing path) |

## Goldens pinned

- The known minima: [−1.0, 1.5] (quadratic), [1.0, 1.0] (Rosenbrock), the origin (Zakharov) — with the per-function
  tolerances (1e-3 / 1e-4 / 1e-5).
- The hard-bug regression: `max()` on an empty `FixedSizeMaxList` raises `RuntimeError`.

## Conventions

- No PERF gates: the suite runs in ~0.040s; the 1000-iteration tests (Rosenbrock, Zakharov) are the slowest — a PERF
  gate could be added if more test functions are introduced.
- The test uses `np.double` (an alias) where the source uses `np.float64` — style inconsistency only, not a bug.
- `test_a_optimization(self)` with `d = 20` defined in the body (the unused-parameter smell is avoided).

## Integration

- Independent of the pipeline: the standalone verification of the numerical engine the OPTIMIZE level runs (no
  LMContext, no DB, no fixtures).
- Known open gaps (low/medium priority): the min_grad / min_p_fun_decrease stopping branches, the restart branch (pᵀg ≥
  0), the curvature skip (yᵀs ≤ 1e-15), the Hermite + line-search internals — covered via integration only.
