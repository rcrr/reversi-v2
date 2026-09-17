# reversi/lm/hlp_plot.py
The PLOT level's figure builders (the styling ruling: the FIXED
axis ranges — the game-value axes always the full [-64, +64]
domain, the residual-density axis the centered [-72, +72] window,
the step-8 tick grid — and the two-line title: the plot name in
BOLD, the run description in smaller ITALIC, spaced apart; the
mean-by-EGV refinement: the y axis hugs the actual data
symmetrically, the smaller tick labels). The seven matplotlib
diagnostics of the logistic-model run. The first three are the port
of the R rglm workflow's classic plots (the residual-density
three-liner, the residual-vs-fitted cloud, the residual-vs-game-
value cloud — the R script itself is a scratch artifact and is NOT
referenced anywhere in the documentation); the last four are
extensions (the per-EGV box plot, the per-EGV mean-residual error
bars, the parity plot, the normal QQ plot). All figures are in Y
space (the [-64, +64] game-value scale — Y values are comparable
across models with different logit_clipping, Z values are distorted
per model).
matplotlib and scipy are imported LAZILY (inside the functions):
importing this module must stay cheap, because hlp_config_schemas
imports `PLOT_NAMES` from here and the config is parsed by every
run (and by the client). All randomness (the jitter, the KDE
subsample) is SEEDed — the R jitter was unseeded, these figures are
reproducible run over run, and the PNG output is byte-deterministic
under a fixed matplotlib version.

## API

| name | contract |
|---|---|
| `PLOT_NAMES` | the seven canonical plot names (the PLOT whitelist vocabulary — the single source of truth the `PlotConfig` schema validates against): `residual_density`, `resid_vs_fitted`, `resid_vs_gv`, `gv_by_egv_box`, `resid_mean_by_egv`, `parity`, `resid_qq` |
| `PLOT_TITLES` | the name → title map (the figure's subtitle line carries the run name) |
| `PlotData` | the dataclass: `trn_y_true`, `trn_rn`, `vld_y_pred`, `vld_rn`, `vld_gv` — all rounded-lossless f64 views |
| `collect_plot_data(ctx) -> PlotData` | the training w_dense forward pass over `ctx.hlp_indexes.indexes` (the same gather + row sum as `hlp_analytics.compute_training_dense_metrics`) + the validation forward pass (the same formula as `hlp_validate.validate_model` — the CLIENT_CHECK reference) |
| `jitter(rng, x, amount) -> (N,) f64` | the R jitter semantics: uniform noise in [-amount·range(x)/2, +amount·range/2], amount a fraction of the data range; a zero-range input comes back untouched |
| `egv_bins(y_pred) -> (unique, inv)` | the evaluated-game-value bins (the R `round_gv`): y_pred rounded to the even step-2 grid (`2·rint(y_pred/2)` — `np.rint` is banker's rounding against R's round-half-away-from-zero, but y_pred is a continuous f64 so the half-tie is measure-zero) |
| `_sym_limit(values, step=8) -> float` | private — the symmetric residual-axis limit: the max absolute value rounded UP to the tick step (the "reasonable value"), at least one step |
| `plot_<name>(d, run_name) -> Figure` | the seven builders (see Architecture) — each takes the PlotData + the run name (the config name) and returns the matplotlib Figure |
| `PLOT_BUILDERS` | the name → builder registry (the worker dispatches on it) |
| `save_figure(fig, path, fmt, dpi=150)` | saves in the given format (png at dpi, pdf vector) — the format is passed EXPLICITLY (the `format=` kwarg; matplotlib otherwise sniffs the file suffix, the "png2" trap) |
| `close_figure(fig)` | releases the figure (the worker calls it after every save round) |

## Architecture

- Header block (L28-41): the note — the lazy-matplotlib
  rationale, the Y-space ruling, the determinism contract.
- Imports (L44-55): `dataclass`, typing, numpy (L48),
  `sigmoid` from hlp_gradient (L51 — the SAME scipy-expit the
  VALIDATE / CLIENT_CHECK passes use), `LMContext` + `Figure` under
  TYPE_CHECKING. NO top-level matplotlib/scipy import (verified by
  the probe A5).
- Constants (L69-112): `PLOT_NAMES` (L69-77), `PLOT_TITLES`
  (L80-88), the seeds `_JITTER_SEED=42` / `_KDE_SEED=43` (L92-93),
  `_KDE_MAX_POINTS=100_000` (L99 — the O(n·m) cap), the jitter
  amounts `_JIT_FITTED_X=0.005`, `_JIT_Y=0.005`, `_JIT_GV_X=0.7`
  (L107-109 — the R fractions, unit-agnostic), `_KDE_GRID=512`
  (L112), the fixed-axis constants `_AXIS_GV=64.0`,
  `_AXIS_DENSITY=72.0`, `_TICK_STEP=8.0` (the game-value axes
  always the full [-64, +64] domain, the residual-density axis
  the centered [-72, +72] window — a residual beyond it means a
  broken model, the outlier report is where they show up — the
  step-8 tick grid).
- `PlotData` (L124-145): the five f64 arrays (the docstring
  documents the provenance of each).
- `collect_plot_data` (L147-176): the per-instance `col_offsets`
  (L156-157, the same `np.repeat(offsets[:-1], n_instances)`
  construction) → the TRAINING dense pass over
  `ctx.hlp_indexes.indexes` (L159-162) → the VALIDATION forward
  pass via `feature_set.compute_indexes` (L165-168) → the f64-view
  residuals (L163, L169-171). Stateless (nothing stored on the
  context).
- `jitter` (L178-189): the R semantics (the ±amount·range/2 uniform
  band, the zero-range guard).
- `egv_bins` (L191-201): `2·rint(y_pred/2)` → int64 →
  `np.unique(..., return_inverse=True)`.
- `_kde_curve` (L203-220): the lazy `scipy.stats.gaussian_kde`
  (Scott's rule bandwidth — the R `density()` uses Silverman's,
  below plot resolution), the seeded 100k subsample cap, the
  zero-variance guard (a flat zero curve — the degenerate kernel
  is singular), evaluated on the caller's grid.
- `_sym_limit`: `step * ceil(max|values| / step)`,
  the non-finite / zero guard returns one step.
- `_fig` (the title layout): the fresh (9,6) figure, the
  light-theme look (grid alpha 0.3, the R `theme_light`
  equivalent); the title is TWO lines — the plot name in BOLD
  (fontsize 13, `pad=26` lifts it) and the run name in smaller
  ITALIC (fontsize 10, just above the axis).
- The label standardization: every axis label and title
  says "Evaluated game value" (the two "Fitted" titles
  renamed); the bare "(Y)" is gone from every label (the
  PlotData docstrings say "the Y scale"); the two binned axes
  carry the italic mathtext note ` $(binned\ every\ 2)$` (the
  `_BINNED_NOTE` constant) at the axis font size — this
  matplotlib 3.11 build has no mathtext size commands
  (\small and \itshape are rejected), so the note stays at the
  axis font size (a smaller note is not renderable).
- The builders:
  - `plot_residual_density` (plot 1 / the R p0): three KDE curves
    on a shared axis — Reference (the training game values
    centered on their mean: the "population" series of the
    analytics report, slategray), Training (firebrick), Validation
    (black); the margin labels carry the sd (the validation one
    also mean/min/max — the `_series_label` helper; the placement
    fractions `_TXT_X`/`_TXT_Y` — the Reference label sits HIGH
    (it overlapped its line at the lower position); the Training
    label sits at ~x = 25 in data units (the fraction 0.674), so
    it clears the residual peak it used to cover); the
    dashed vline at the TRAINING residual mean; the axis FIXED on
    the centered [-72, +72] window; NO legend (the R
    original had `legend.position = "None"` — the margin labels
    identify the curves).
  - `plot_resid_vs_fitted` (plot 2 / the R p1): the validation
    residual cloud vs the fitted values, the seeded
    0.005-fraction jitter on both axes, black dots alpha 0.04;
    the axes: x always the full [-64, +64] domain, y
    symmetric on a `_sym_limit` (tick-step-rounded) limit.
  - `plot_resid_vs_gv` (plot 3 / the R p2): the validation
    residual cloud vs the actual game values; the x jitter is the
    large 0.7-range fraction (the horizontal "cloud" smearing
    over the integer grid), the y jitter the fine 0.005 one,
    alpha 0.02; the axes: x always the full [-64, +64]
    game-value domain (a data-driven axis would let the
    0.7 jitter smear the auto-range to ±108 — the labels were
    NOT swapped, the jittered points beyond the domain are
    clipped by the axis), y as in
    resid_vs_fitted.
  - `plot_gv_by_egv_box` (plot 4 / the R boxplot helper): the
    validation game values as a box plot per EGV bin (the fitted
    Y rounded to the step-2 grid); the axes: BOTH x and y
    always the full [-64, +64] domain, regardless of the data,
    the ticks on the step-8 grid; the mandatory EXPLICIT
    labels (`set_xticks(ticks, labels=...)`): boxplot() leaves
    the 62 categorical bin labels on the axis, and a
    positions-only set_xticks prints the first 17 of them under
    the step-8 positions (the stale-label bug); the x
    label: "Evaluated game value" + the italic binned note.
  - `plot_resid_mean_by_egv` (plot 5, new): the validation
    residual MEAN ± sd error bars per EGV bin against the zero
    line — the systematic-bias-per-level view (a miscalibrated
    region drifts away from zero); single-point bins get a zero bar (the
    ddof=1 sd is undefined at n=1); the axes: x
    always the full [-64, +64] domain, y
    hugs the ACTUAL data (the |mean|+sd extent rounded UP to the
    step-8 grid, kept symmetric — the min/max extent of the
    actual data; the tick grid stays 0, 8, 16, ...
    within the limit), the tick labels in the smaller font
    (labelsize 8); the x label: "Evaluated game
    value" + the same italic binned note.
  - `plot_parity` (plot 6, new): the validation game values vs
    the fitted values, the 45° line, both axes on the full
    [-64, +64] scale, equal
    aspect.
  - `plot_resid_qq` (plot 7, new): the sorted sample quantiles
    of the validation residuals against the standard normal
    theoretical quantiles (the lazy `scipy.special.ndtri`), the
    dashed `y = sd·x` scale line (residuals that are normal with
    mean zero sit ON the line; the R script computed the
    skewness/kurtosis numerically — this shows them); the
    axis: y (the sample quantiles) always the full [-64, +64], x
    (the theoretical quantiles) stays data-driven (the normal
    tail, about ±3.3).
- `PLOT_BUILDERS` (L410-418): the registry.
- `save_figure` (L421-433): the explicit-`format` save (the png2
  trap comment) + the unknown-format `ValueError` guard.
- `close_figure` (L435-438).

## Verified invariants

Pinned by the 9-test `test_hlp_plot` suite (no DB) + the 16-check
`probes/verify_plot.py` probe (no DB) + the worker/chain suites.

- The vocabulary: seven distinct names; the builder registry and
  the titles cover the names EXACTLY (no stray, no missing)
  (`test_builders_cover_names_exactly`, `test_titles_cover_names_
  exactly`; probe A2/A3). The schema validates against the same
  vocabulary (probe A4).
- The jitter: the output stays inside the ±amount·range/2 band and
  actually spreads (>100 distinct deltas); the zero-range input is
  the identity (`test_bounds_and_spread`, `test_zero_range_is_
  identity`; probe B4).
- The EGV bins: the grid is even, every point lands in a bin within
  1.0 of its fitted value; the known-values case
  `[-0.4, 0.6, 3.2, -2.9, 64.0] → [0, 0, 4, -2, 64]`
  (`test_even_grid_and_coverage`, `test_known_values`; probe B6).
- The KDE guard: a zero-variance input yields a flat zero curve
  (no singular-kernel exception); a symmetric cloud yields a
  finite, non-negative curve peaking within 0.5 of the mean
  (`test_zero_variance_is_flat_zero`, `test_curve_shape_and_peak`;
  probe B5).
- The lazy import: no top-level matplotlib (probe A5) — importing
  hlp_plot (via the schema) stays cheap for every run and the
  client.
- The rendering: every builder renders a non-trivial PNG on a
  synthetic PlotData (probe B1); the 'pdf,png' pair writes both
  magics (probe B2); a second render hashes EQUAL — the byte
  determinism of the seeded pipeline (probe B3; the worker-level
  twin in test_wrk_plot, the chain-level twin in the A2030/A2050
  file pins).

## Open issues

None.

## Conventions

- The R fidelity: the three classic plots mirror the R rglm
  workflow (the three KDE lines with the sd/mean/min/max margin
  labels + the training-mean vline; the two gray-cloud scatters
  with the R jitter fractions 0.005/0.005/0.7 as a fraction of the
  data range; the per-EGV box plot). The differences are
  documented: Y space instead of the transformed [0,1] target
  space (the cross-model comparability ruling), Scott's instead of Silverman's KDE
  bandwidth (below plot resolution), SEEDed instead of unseeded
  jitter (determinism), and the box-plot helper that the R script
  defined but never returned.
- The KDE cap (100k): the density is statistically indistinguishable
  and the figure time stays flat at the A2050 scale (~2M training
  points).
- The builders are pure: they take the PlotData + the run name and
  return the Figure; all ctx access is in `collect_plot_data` (the
  worker boundary). The figures are closed by the worker after the
  save round (no Figure leaks across levels).

## Integration

- Consumed by wrk_plot (the 17th level): `collect_plot_data`
  (once per up-move), the `PLOT_BUILDERS` dispatch, `save_figure` /
  `close_figure` per save.
- `PLOT_NAMES` is imported by hlp_config_schemas (the PlotConfig
  `plots` validator) — the single source of truth for the plot
  vocabulary; a new plot name lands here first, then in the
  builders + titles (the probe A2/A3 pins keep the three in lock-
  step).
- The training pass is a FORMULA COPY of hlp_analytics' dense
  metrics and the validation pass of hlp_validate (the A1a
  pattern): if those formulas change, these copies must follow.
- The `sigmoid` import ties the figures to the exact model math
  (the scipy-expit, the f32 pipeline) — the plotted fitted values
  are what the saved model computes.
