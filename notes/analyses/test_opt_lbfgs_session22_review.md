<!-- ARCHIVED — D-106 step 16 (the docs/ rewrite, 2026-09-04): the
     complete session-22 test-doc (D-053) moved out of
     docs/src/twolm/test/test_opt_lbfgs.md per docs_rules.md
     §1/§4/§6. This is a frozen historical record: it is never
     updated. NOTE: the file is UNCHANGED since 65f63be
     (2026-08-29) — 7 classes / 13 tests / 239 lines is still
     correct. The T7 fix + the 9 new tests (D-053) + the open-gap
     table (convergence/restart/curvature/Hermite/line-search
     internals) are frozen history. The "no PERF gates / 0.040s"
     figures are still accurate. -->

# test_opt_lbfgs.md — analysis

Date: 2026-08-29. One test file: `test_opt_lbfgs.py` (13 tests, 7 classes).
**T7 + 9 new tests applied (D-053): suite 4 → 13/0/0 GREEN.**

Suite: **13/0/0 GREEN, no PERF gates.** Fast (~0.040s).

## How to run

```
$ python -m unittest twolm.test.test_opt_lbfgs
```

## Coverage by area

### `TestLBFGSInputValidation` (3 tests, added D-053)
- `test_non_ndarray_x0_raises`: `x0='not_an_array'` → `TypeError`.
- `test_wrong_dtype_raises`: `x0` with `int32` dtype → `TypeError`.
- `test_non_callable_fg_raises`: `fg='not_callable'` → `TypeError`.
- **Coverage**: the input-validation paths in `lbfgs`.

### `TestFixedSizeMaxList` (4 tests, added D-053)
- `test_max_on_empty_raises`: `max()` on an empty list → `RuntimeError` (pins T1 fix).
- `test_push_and_max`: push 1/3/2, `max()==3`, `len()==3`.
- `test_eviction`: maxlen=2, push 5/1/3 → 5 evicted, `max()==3`.
- `test_len_zero_initially`: fresh list has `len()==0`.
- **Coverage**: the `FixedSizeMaxList` helper, including the T1 bug.

### `TestTwoLoopRecursion` (2 tests, added D-053)
- `test_empty_history_returns_identity`: `[]` history returns `g` unchanged.
- `test_random_pairs_shape_and_descent`: 3 random s/y pairs → correct shape, non-zero output.
- **Coverage**: the two-loop recursion in isolation.

### `TestLBFGSBaseFunction` (1 test)
- `test_a_optimization`: quadratic f(x) = x[0] - x[1] + 2*x[0]*x[1] + 2*x[0]^2 + x[1]^2, known minimum at [-1.0, 1.5]. Asserts x_opt within 1e-3.
- **Coverage**: basic convergence on a convex quadratic.

### `TestLBFGSRosenbrockFunction` (1 test)
- `test_a_optimization`: Rosenbrock function, known minimum at [1.0, 1.0], f*=0. Starts from [-1, -1], 1000 iterations, asserts within 1e-4.
- **Coverage**: non-convex, narrow curved valley — stress test for L-BFGS.

### `TestLBFGSZakharovFunction` (1 test)
- `test_a_optimization`: 20D Zakharov function, minimum at origin. Random start with seed(42), 1000 iterations, asserts within 1e-5.
- **Coverage**: moderate-dimensional (20D) convex function.

### `TestLBFGSWarmStart` (1 test)
- `test_resume_optimization`: runs Rosenbrock for 100 iters continuous vs 50+50 with save/resume. Asserts final positions match within 1e-4.
- **Coverage**: warm-start / checkpointing path.

## Defects (test file only)

### T7 — Test method with unused parameter (D-053, FIXED)
`test_a_optimization(self, d=20)` → `test_a_optimization(self)` with `d = 20` moved into the body.

### Test gaps (no code defects, but missing coverage)

The suite has excellent integration-level coverage (4 different test functions) plus, after D-053, unit-level tests for the main internal components. The following remain **open**:

| Gap | Description | Priority |
|---|---|---|
| **Convergence criteria** | min_grad stopping (gradient < threshold for N iters), min_p_fun_decrease stopping (low progress for N iters) | Medium |
| **Restart logic** | when direction is not descent (p^T g ≥ 0), memory is cleared and steepest descent used | Medium |
| **Curvature skip** | when y^T s ≤ 1e-15, the pair is not added to history | Low |
| **`_hermite_cubic_interp`** | known interpolation against manually computed values | Low |
| **`_strong_wolfe_line_search`** | step satisfies Wolfe conditions by construction | Low (covered via integration) |

Resolved in D-053:
- **Input validation** — `TestLBFGSInputValidation` (3 tests).
- **`FixedSizeMaxList`** — `TestFixedSizeMaxList` (4 tests), including the T1 bug.
- **`_two_loop_recursion`** — `TestTwoLoopRecursion` (2 tests).

## Observations

- **No PERF gates**: the suite runs in 0.040s. The 1000-iteration tests (Rosenbrock, Zakharov) are the slowest; if more test functions are added, a PERF gate could be added.
- **`np.double` vs `np.float64`**: test uses `np.double` (alias) while source uses `np.float64`. Style inconsistency only.
- **No `unittest.main` guard needed**: the `if __name__ == "__main__"` block is standard.

## Completeness verdict

**Integration coverage is good** (4 diverse test functions + warm-start), and D-053 added unit coverage for the main internal components (`FixedSizeMaxList`, `_two_loop_recursion`, input validation), including a regression test for the T1 bug. Remaining gaps are the convergence/restart/curvature branches and the Hermite/line-search internals (all low/medium priority).

**Verdict**: 13/0/0 GREEN. T7 fixed and the major unit-coverage gaps closed (D-053).

## Appendix: class map (2026-08-29, post T7 + new tests)

| Line | Class | Tests |
|---|---|---|
| 50 | `TestLBFGSInputValidation` | 3 |
| 71 | `TestFixedSizeMaxList` | 4 |
| 100 | `TestTwoLoopRecursion` | 2 |
| 125 | `TestLBFGSBaseFunction` | 1 |
| 144 | `TestLBFGSRosenbrockFunction` | 1 |
| 164 | `TestLBFGSZakharovFunction` | 1 |
| 195 | `TestLBFGSWarmStart` | 1 |