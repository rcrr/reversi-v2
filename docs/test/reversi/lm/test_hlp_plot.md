# test/reversi/lm/test_hlp_plot.py
The no-DB unit suite of the PLOT level's pure helpers (`reversi/lm/hlp_plot.py`): the seven-name vocabulary (the single
source of truth the `PlotConfig` schema validates against), the R-semantic jitter, the EGV bins (the R `round_gv` port),
the guarded Gaussian-kernel density, and the save-boundary guard. No figures, no ctx, no DB — the builder/rendering
behaviour lives in `test_wrk_plot` (the worker tier) and `probes/verify_plot.py` (the 19-check probe).

## Coverage

| class | tests | what it pins |
|---|---|---|
| `TestHlpPlotVocabulary` | 3 | `test_names_seven_distinct`: seven distinct canonical names. `test_builders_cover_names_exactly`: the `HLP_PLOT_BUILDERS` registry covers the names EXACTLY (no stray, no missing — a new name lands in the tuple and the registry together). `test_titles_cover_names_exactly`: the `HLP_PLOT_TITLES` map, same lock-step. |
| `TestHlpPlotAxes` | 2 | `test_rounds_up_to_the_step`: the `_sym_limit` symmetric residual-axis limit — the max absolute value rounded UP to the tick step (5.3 → 8.0, 16.0 → 16.0, 16.1 → 24.0). `test_degenerate_inputs`: a zero-variance or NaN input yields the one-step floor (8.0). |
| `TestHlpPlotJitter` | 2 | `test_bounds_and_spread`: the R jitter semantics — the output stays inside the ±amount·range/2 band AND actually spreads (>100 distinct deltas on a 1000-point axis). `test_zero_range_is_identity`: a constant input comes back untouched (the R degeneration). |
| `TestHlpPlotEgvBins` | 2 | `test_even_grid_and_coverage`: the bin values are EVEN (the step-2 grid), every point lands in exactly one bin within 1.0 of its fitted value. `test_known_values`: `[-0.4, 0.6, 3.2, -2.9, 64.0] → [0, 0, 4, -2, 64]` (the `2·rint(x/2)` banker's port of the R `round_gv`). |
| `TestHlpPlotKde` | 2 | `test_zero_variance_is_flat_zero`: the singular-kernel guard — a constant input yields a flat zero curve, no exception. `test_curve_shape_and_peak`: a symmetric cloud yields a finite, non-negative curve peaking within 0.5 of the mean. |
| `TestHlpPlotSaveFigure` | 1 | `test_unknown_format_raises`: a format outside the schema-validated pair ("svg") → the precise `ValueError` "Unknown plot format: 'svg'" (the guard that keeps the explicit-format rule honest) |

## Goldens pinned

- The EGV known-values vector `[0, 0, 4, -2, 64]` (the banker's tie-break is visible: 3.2 → 2 → 4, −2.9 → −1 → −2).
- The jitter band bound (the R ±amount·range/2 contract).
- The vocabulary lock-step (names ⇄ builders ⇄ titles) — the three collections must move together (the probe A2/A3
  twin).
- The save-boundary message: `Unknown plot format: 'svg'` (the ValueError's exact text, the explicit-format guard).

## Conventions

- The private helpers (`_kde_curve`) are tested directly — they carry the guards (the zero-variance singular kernel)
  that the figures depend on.
- No matplotlib in this file: the builders' rendering is the worker tier's territory (test_wrk_plot) — keeps this module
  import-light.

## Integration

- The module under test: `reversi/lm/hlp_plot.py` (hlp_plot.md).
- The worker tier: `test_wrk_plot` (the level end-to-end on the synthetic ctx); the probe tier: `probes/verify_plot.py`
  (the vocabulary, the lazy import, the rendering, the determinism, the PlotConfig semantics).
- The schema consumer of `HLP_PLOT_NAMES`: `test_hlp_config_schemas` (the PlotConfig section — the fail-fast unknown-name
  guard).
