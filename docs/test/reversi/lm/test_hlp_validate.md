# test/reversi/lm/test_hlp_validate.py

The `hlp_validate` unit suite — 2 classes / 7 tests, no DB, < 0.2 s. The outlier selection (the stable
descending-|residual| ranking) and the validation forward pass with its 7-metric dict, on a hand-computed
2-position mock ctx.

## Coverage

| class | tests | what it pins |
|---|---|---|
| `TestTopOutliers` | 3 | the k-largest-\|residual\| selection: the descending magnitude order, the STABLE tie break (the lower index first on equal magnitude), k larger than N (all indices, ranked) |
| `TestValidateModel` | 4 | the `LMValidate` result: the exact 7 metric keys + `vld_samples`; the Z-space metrics (loss / mse / mae) against the hand-computed forward pass; the Y-space metrics (mae / mse / rmse) the same way; the published `y_pred` / `rn_y` series in the f64 views with the right shapes |

## Goldens pinned

The 7 metric keys, the metric formulas (re-derived independently in the test from the same tiny weights), and the
f64 series contract are the pins. (No hash goldens — the hand computation stands in for them.)

## Conventions

- the NO-DB mock-ctx idiom: a `SimpleNamespace` ctx with a 1-feature / 2-instance mock feature set (a
  `compute_indexes` lambda returning a fixed 2x2 index array), a 6-weight `w_dense`, the affine `y2z` / `z2y`
  maps, and a no-op `log_event`.
- the hand computation re-derives the f32 forward pass in f64; the assertions use `places=5` so the f32 sum
  noise (0.1 + 0.3 vs 0.4) cannot bite.

## Integration

Mirrors `src/reversi/lm/hlp_validate.py` (the `LMValidate` carrier, the outlier kernel, the validation forward
pass). The VALIDATE level in the full pipeline (the real validation positions from the DB) stays covered by
`test_wrk_validate` and the end-to-end chain; this module pins the metric logic itself at < 0.2 s cost.
