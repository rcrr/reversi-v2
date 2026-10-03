# test/reversi/closecheck.py
Tolerant float comparison for the float64 pipeline-metric goldens (the thread-count ULP study). The train/vld/pop
metric reductions run through the multi-threaded OpenBLAS ddot, whose last ULPs depend on the machine that runs
the tests.

## API

| name | contract |
|---|---|
| `assert_close(testcase, got, want, label='')` | Assert that `got` is within `REL_TOL` (relative) / `ABS_TOL` (absolute) of the golden `want`; the failure message shows the actual relative difference and the tolerances. A plain function called on the test case, not a decorator |
| `REL_TOL` | `1e-9` — the goldens must agree to ~10 significant digits (measured environment drift is <= 4e-14 relative; a genuine regression shows at >= 1e-6) |
| `ABS_TOL` | `1e-12` — the absolute floor for near-zero values (the small validation losses) |

`__all__` = [assert_close, REL_TOL, ABS_TOL]. No `@validate_call` — this is a test helper, not a domain function.

## Architecture

- `math.isclose(got, want, rel_tol=REL_TOL, abs_tol=ABS_TOL)` — the two-tolerance shape: relative for the large
  metrics, an absolute floor so the near-zero losses are not exempt.
- The failure message carries the actual relative difference: a red test says HOW MUCH it missed, not just that it
  missed.
- The bit-exact pins STAY `assertEqual` (R-810): the int/uint counts, the f32-quantized values (train_loss, g_norm,
  the tps read-back truncations), the sha3_256 file/array hashes, the EF pins, the second-instance determinism
  tests. `assert_close` is for the f64 metric reductions only.

## Verified invariants

- The ULP investigation: a 4 → 8 vCPU move shifts the goldens by up to ~4e-14 relative (2-301 ULP across the
  three A20xx/rlm chains), while every bit-exact contract of the pipeline held.
- The detection margin: a genuine pipeline regression (a wrong feature, wrong samples, a broken reduction) shows
  up at >= 1e-6 — ~5 orders of magnitude above `REL_TOL`.

## Open issues

None.

## Conventions

- Float golden tests MUST use `assert_close` (R-810): float results are not bit-reproducible across machines.
- The call shape: `assert_close(self, met['train_rmse_y'], 15.58872172931622, 'train_rmse_y')` — the label is the
  metric name; the empty default renders as `value`.

## Integration

- Imported by the pipeline metric golden suites (the hlp_analytics / hlp_validate reduction goldens) — the house
  idiom for every f64 metric golden.
