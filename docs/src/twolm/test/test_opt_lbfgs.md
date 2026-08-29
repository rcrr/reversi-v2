# test_opt_lbfgs.md — analysis

Date: 2026-08-29. One test file: `test_opt_lbfgs.py` (4 tests, 4 classes).

Suite: **4/0/0 GREEN, no PERF gates.** Fast (~0.040s).

## How to run

```
$ python -m unittest twolm.test.test_opt_lbfgs
```

## Coverage by area

### `TestLBFGSBaseFunction` (1 test)
- `test_a_optimization`: quadratic f(x) = x[0] - x[1] + 2*x[0]*x[1] + 2*x[0]^2 + x[1]^2, known minimum at [-1.0, 1.5]. Asserts x_opt within 1e-3.
- **Coverage**: basic convergence on a convex quadratic.

### `TestLBFGSRosenbrockFunction` (1 test)
- `test_a_optimization`: Rosenbrock function, known minimum at [1.0, 1.0], f*=0. Starts from [-1, -1], 1000 iterations, asserts within 1e-4.
- **Coverage**: non-convex, narrow curved valley — stress test for L-BFGS.

### `TestLBFGSZakharovFunction` (1 test)
- `test_a_optimization(d=20)`: 20D Zakharov function, minimum at origin. Random start with seed(42), 1000 iterations, asserts within 1e-5.
- **Coverage**: moderate-dimensional (20D) convex function.

### `TestLBFGSWarmStart` (1 test)
- `test_resume_optimization`: runs Rosenbrock for 100 iters continuous vs 50+50 with save/resume. Asserts final positions match within 1e-4.
- **Coverage**: warm-start / checkpointing path.

## Defects (test file only)

### T7 — Test method with unused parameter (L110)
`test_a_optimization(self, d=20)` — test method has a parameter `d`. `unittest` calls it without arguments, so the default is used. The parameter suggests the test was designed for subTest/different d values but wasn't converted. Works by accident.

**Severity**: Cosmetic — non-idiomatic.

### Test gaps (no code defects, but missing coverage)

The suite has excellent integration-level coverage (4 different test functions) but no unit-level tests for the internal components. The following are **proposed additions**:

| Gap | Description | Priority |
|---|---|---|
| **Input validation** | `lbfgs` raises `TypeError` for non-ndarray x0, wrong dtype, non-callable fg — these paths exist but have no test | High |
| **`FixedSizeMaxList`** | max on empty deque (triggers T1 bug), push/len/max behavior, deque maxlen eviction | High (catches T1) |
| **`_two_loop_recursion`** | empty history → identity, random pairs → shape-correct output, known s/y → verified result | Medium |
| **Convergence criteria** | min_grad stopping (gradient < threshold for N iters), min_p_fun_decrease stopping (low progress for N iters) | Medium |
| **Restart logic** | when direction is not descent (p^T g ≥ 0), memory is cleared and steepest descent used | Medium |
| **Curvature skip** | when y^T s ≤ 1e-15, the pair is not added to history | Low |
| **`_hermite_cubic_interp`** | known interpolation against manually computed values | Low |
| **`_strong_wolfe_line_search`** | step satisfies Wolfe conditions by construction | Low (covered via integration) |

## Observations

- **No PERF gates**: the suite runs in 0.040s. The 1000-iteration tests (Rosenbrock, Zakharov) are the slowest; if more test functions are added, a PERF gate could be added.
- **`np.double` vs `np.float64`**: test uses `np.double` (alias) while source uses `np.float64`. Style inconsistency only.
- **No `unittest.main` guard needed**: the `if __name__ == "__main__"` block at L162 is standard.

## Proposed new tests

If Roberto approves, the following tests would fill the major gaps:

1. **`TestLBFGSInputValidation`**: 3 tests — non-ndarray x0 → TypeError, int32 dtype → TypeError, non-callable fg → TypeError.
2. **`TestFixedSizeMaxList`**: 4 tests — max on empty deque → RuntimeError (pins T1 fix), push+max, len after pushes, eviction at maxlen.
3. **`TestTwoLoopRecursion`**: 2 tests — empty history returns identity, random pairs produce correct shape and non-zero output.
4. **`TestLBFGSConvergenceCriteria`**: 2 tests — min_grad stopping (quadratic with very tight threshold), min_p_fun_decrease stopping (flat function).

## Completeness verdict

**Integration coverage is good** (4 diverse test functions + warm-start), but **unit coverage is minimal** and the input validation paths are untested. The `FixedSizeMaxList` is completely uncovered — this is the class that contains T1 (the `RuntimeException` bug).

**Verdict**: 4/0/0 GREEN. Acceptable for a first port, but strongly recommend adding unit tests for the internal components (especially `FixedSizeMaxList` and input validation) before the module is considered "done."

## Appendix: class map (2026-08-29)

| Line | Class | Tests |
|---|---|---|
| 50 | `TestLBFGSBaseFunction` | 1 |
| 69 | `TestLBFGSRosenbrockFunction` | 1 |
| 89 | `TestLBFGSZakharovFunction` | 1 |
| 119 | `TestLBFGSWarmStart` | 1 |