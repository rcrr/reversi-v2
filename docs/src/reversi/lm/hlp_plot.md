# reversi/lm/hlp_plot.py
The PLOT level's figure builders: the seven matplotlib diagnostics of the logistic-model run, all in Y space (the [-64,
+64] game-value scale — Y values are comparable across models with different logit_clipping, Z values are not). Three
are the port of the R rglm workflow's classic plots (the residual-density three-liner, the residual-vs-fitted cloud, the
residual-vs-game-value cloud); four are extensions (the per-EGV box plot, the per-EGV mean-residual error bars, the
parity plot, the normal QQ plot). The axes follow fixed rulings — the game-value axes always the full [-64, +64] domain,
the residual-density axis the centered [-72, +72] window, the step-8 tick grid — and the title is two lines (the plot
name in bold, the run description in italic). Every random element (the jitter, the KDE subsample) is SEEDed, so a
figure is reproducible run over run and the PNG is byte-deterministic under a fixed matplotlib version. matplotlib and
scipy are imported LAZILY: the import must stay cheap, because `hlp_config_schemas` imports `PLOT_NAMES` from here and
the config is parsed by every run (and by the client).

## API

| name | contract |
|---|---|
| `PLOT_NAMES` | the seven canonical plot names (the whitelist vocabulary the `PlotConfig` schema validates against): `residual_density`, `resid_vs_fitted`, `resid_vs_gv`, `gv_by_egv_box`, `resid_mean_by_egv`, `parity`, `resid_qq` |
| `PLOT_TITLES` | the name → title map (the figure's second title line carries the run name) |
| `PlotData` | the dataclass: `trn_y_true`, `trn_rn`, `vld_y_pred`, `vld_rn`, `vld_gv` — all rounded-lossless f64 views |
| `collect_plot_data(ctx) -> PlotData` | the ASSEMBLY of the published series (I-018): `ctx.train_dense_rn` (ANALYTICS) + `ctx.vld_y_pred` / `ctx.vld_rn` (VALIDATE) + the game values from POSITIONS / VLD_POSITIONS — no forward pass runs here |
| `jitter(rng, x, amount) -> (N,) f64` | the R jitter semantics: uniform noise in ±amount·range(x)/2; a zero-range input comes back untouched |
| `egv_bins(y_pred) -> (unique, inv)` | the evaluated-game-value bins: `y_pred` rounded to the even step-2 grid (`2·rint(y_pred/2)`) + `np.unique(..., return_inverse=True)` |
| `_sym_limit(values, step=8) -> float` | private — the symmetric residual-axis limit: the max absolute value rounded UP to the tick step, at least one step |
| `plot_<name>(d, run_name) -> Figure` | the seven builders (see Architecture); each takes the PlotData + the run name and returns the Figure |
| `PLOT_BUILDERS` | the name → builder registry (the worker dispatches on it) |
| `save_figure(fig, path, fmt, dpi=150)` | saves in the given format (png at dpi, pdf vector); the format is passed EXPLICITLY (matplotlib otherwise sniffs the file suffix) and an unknown format raises `ValueError` |
| `close_figure(fig)` | releases the figure (the worker calls it after every save round) |

## Architecture

- Imports: `dataclass`, typing, numpy, the numpy surface only (the same scipy-expit the VALIDATE / CLIENT_CHECK passes
  use), `LMContext` + `Figure` under TYPE_CHECKING. NO top-level matplotlib / scipy import.
- Constants: `PLOT_NAMES`, `PLOT_TITLES`, the seeds `_JITTER_SEED=42` / `_KDE_SEED=43`, `_KDE_MAX_POINTS=100_000` (the
  O(n·m) cap), the jitter amounts `_JIT_FITTED_X=0.005`, `_JIT_Y=0.005`, `_JIT_GV_X=0.7` (the R fractions),
  `_KDE_GRID=512`, and the axis constants `_AXIS_GV=64.0`, `_AXIS_DENSITY=72.0`, `_TICK_STEP=8.0`.
- `collect_plot_data`: a PURE ASSEMBLY (I-018) — the training game values (`ctx.game_values`) + the dense training
  residuals (`ctx.train_dense_rn`, published by ANALYTICS) + the validation fitted / residual series (`ctx.vld_y_pred` /
  `ctx.vld_rn`, published by VALIDATE) + the validation game values. NO forward pass runs here: the figures render what
  the pipeline measured.
- The helpers: `jitter` (the R band + the zero-range guard); `egv_bins` (the step-2 binning); `_sym_limit`
  (`step * ceil(max|values| / step)`, the non-finite / zero guard returns one step); `_kde_curve` (the lazy
  `scipy.stats.gaussian_kde`, Scott's rule bandwidth — the R `density()` uses Silverman's, below plot resolution — the
  seeded 100k subsample cap and the zero-variance guard: a flat zero curve, the degenerate kernel is singular).
- `_fig` (the shared layout): a fresh (9,6) figure, the light theme (grid alpha 0.3); the title is TWO lines — the plot
  name in bold (fontsize 13, `pad=26` lifts it) and the run name in smaller italic (fontsize 10, just above the axis).
  The axis labels are per-builder ("Evaluated game value", "Game value", "Game value residual", the quantile pair), and
  the binned axes carry the italic mathtext note `$(binned\ every\ 2)$` at the axis font size (this matplotlib build has
  no mathtext size commands).
- The builders:
  - `plot_residual_density` (the R p0): three KDE curves on a shared axis — Reference (the training game values centered
    on their mean: the "population" series of the analytics report, slategray), Training (firebrick), Validation
    (black); the margin labels carry the sd (the validation one also mean/min/max); the dashed vline at the TRAINING
    residual mean; the density axis on the centered [-72, +72] window; NO legend (the margin labels identify the
    curves).
  - `plot_resid_vs_fitted` (the R p1): the validation residual cloud vs the fitted values, the seeded 0.005-fraction
    jitter on both axes, black dots alpha 0.04; x the full [-64, +64] domain, y symmetric on a `_sym_limit`.
  - `plot_resid_vs_gv` (the R p2): the validation residual cloud vs the actual game values; the x jitter is the
    large 0.7-range fraction (the horizontal smearing over the integer grid), the y jitter the fine 0.005 one,
    alpha 0.02; x the full [-64, +64] domain (a data-driven axis would let the jitter smear the auto-range far past it —
    the out-of-domain points are clipped), y as in `resid_vs_fitted`.
  - `plot_gv_by_egv_box` (the R boxplot helper): the validation game values as a box plot per EGV bin; BOTH axes the
    full [-64, +64] domain regardless of the data, the ticks on the step-8 grid; the tick labels are set EXPLICITLY
    (`set_xticks(ticks, labels=...)`) — `boxplot()` leaves its own categorical bin labels on the axis.
  - `plot_resid_mean_by_egv`: the validation residual MEAN ± sd error bars per EGV bin against the zero line (the
    systematic-bias-per-level view: a miscalibrated region drifts away from zero); single-point bins get a zero bar (the
    ddof=1 sd is undefined at n=1); x the full [-64, +64], y hugs the ACTUAL data (the |mean|+sd extent rounded up to
    the step-8 grid, kept symmetric, the ticks 0, 8, 16, ... within the limit), the tick labels in the smaller font
    (labelsize 8).
  - `plot_parity`: the validation game values vs the fitted values, the 45° line, both axes the full [-64, +64], equal
    aspect.
  - `plot_resid_qq`: the sorted sample quantiles of the validation residuals against the standard normal theoretical
    quantiles (the lazy `scipy.special.ndtri`), the dashed `y = sd·x` scale line (residuals that are normal with mean
    zero sit ON the line); y the full [-64, +64], x data-driven (the normal tail, about ±3.3).
- `PLOT_BUILDERS` is the registry; `save_figure` / `close_figure` are the save boundary.

## Verified invariants

Pinned by the 11-test `test_hlp_plot` suite (no DB) + the 17-check `probes/verify_plot.py` probe (no DB) + the
worker/chain suites.

- The vocabulary: seven distinct names; the builder registry and the titles cover the names EXACTLY (no stray, no
  missing) (`test_builders_cover_names_exactly`, `test_titles_cover_names_exactly`; probe A2/A3). The schema validates
  against the same vocabulary (probe A4).
- The jitter: the output stays inside the ±amount·range/2 band and actually spreads (>100 distinct deltas); the
  zero-range input is the identity (`test_bounds_and_spread`, `test_zero_range_is_identity`; probe B4).
- The EGV bins: the grid is even and every point lands in a bin within 1.0 of its fitted value; the known-values case
  `[-0.4, 0.6, 3.2, -2.9, 64.0] → [0, 0, 4, -2, 64]` (`test_even_grid_and_coverage`, `test_known_values`; probe B6).
- The KDE guard: a zero-variance input yields a flat zero curve (no singular-kernel exception); a symmetric cloud yields
  a finite, non-negative curve peaking within 0.5 of the mean (`test_zero_variance_is_flat_zero`,
  `test_curve_shape_and_peak`; probe B5).
- The lazy import: no top-level matplotlib (probe A5) — importing this module (via the schema) stays cheap for every run
  and the client.
- The rendering: every builder renders a non-trivial PNG on a synthetic PlotData (probe B1); the 'pdf,png' pair writes
  both magics (probe B2); a second render hashes EQUAL — the byte determinism of the seeded pipeline (probe B3; the
  worker-level twin in `test_wrk_plot`, the chain-level twin in the A2030/A2050 file pins).

## Open issues

None.

## Conventions

- The R fidelity: the classic plots mirror the R rglm workflow (the KDE three-liner with the sd/mean/min/max margin
  labels + the training-mean vline; the two gray-cloud scatters with the R jitter fractions; the per-EGV box plot), with
  the documented differences: Y space instead of the [0,1] target space, Scott's instead of Silverman's KDE bandwidth,
  SEEDed instead of unseeded jitter (determinism). The 100k KDE cap keeps the figure time flat at the A2050 scale.
- The builders are PURE: they take the PlotData + the run name and return the Figure; all ctx access is in
  `collect_plot_data` (the worker boundary), and the worker closes every figure after the save round (no Figure leaks
  across levels).

## Integration

- Consumed by `wrk_plot` (the 18th level): `collect_plot_data` once per up-move, the `PLOT_BUILDERS` dispatch,
  `save_figure` / `close_figure` per save.
- `PLOT_NAMES` is imported by `hlp_config_schemas` (the `PlotConfig` validator) — the single source of truth for the
  plot vocabulary: a new plot name lands here first, then in the builders + the titles (the probe pins keep the three in
  lock-step).
- The series arrive from the levels that own the passes (ANALYTICS and VALIDATE, I-018): do NOT reintroduce a local
  forward pass — the single derivation is the point, and the figures are byte-pinned by the rendering golden.
- The figures read the PUBLISHED series (the f64 residuals), so no model math is re-derived here — the plotted fitted
  values are what the saved model computes.
