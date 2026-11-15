# test/reversi/lm/test_hlp_analytics.py

The `hlp_analytics` unit suite — 2 classes / 8 tests, no DB, < 0.2 s. The pure kernels of the analytics report:
the SU sample-consistency verdict bands and the 'SU Sample Consistency' header line in all four of its forms.

## Coverage

| class | tests | what it pins |
|---|---|---|
| `TestSuVerdict` | 3 | the TV bands: `<= 0.01` CONSISTENT, `<= 0.05` MARGINAL, above DEVIATING — the boundaries are inclusive (the 0.01 / 0.05 pins) |
| `TestSuHeaderLine` | 5 | the header line: None when the SU_ANALYSIS level was disabled; the `N/A (too small)` note with the corpus / training counts; the ok form carrying the TV + chi2 + verdict; the `N/A (degenerate)` form on a NaN TV; the `chi2 inf` / `p nan` rendering |

## Goldens pinned

The band thresholds (0.01 / 0.05, inclusive) and the four header-line forms are the pins. (No hash goldens.)

## Conventions

- the header-line tests build the `stats` dict inline (the shape `_su_sample_stats` returns) — no ctx, no feature
  set, no corpus.
- the verdict tests pin the boundary VALUES, not just the band membership, so a threshold drift is a failure.

## Integration

Mirrors the private SU kernels of `src/reversi/lm/hlp_analytics.py`. The report-level consumers
(`hlp_analytics_format_file_report`, the feature tables) need a full ctx and stay covered by `test_wrk_analytics`
(the long pipeline suite); this module pins the pure decision logic underneath them at < 0.2 s cost.
