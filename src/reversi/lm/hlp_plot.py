#
# hlp_plot.py
#
# This file is part of the reversi program
# http://github.com/rcrr/reversi
#
# Author Roberto Corradini mailto:rob_corradini@yahoo.it
# Copyright 2026 Roberto Corradini. All rights reserved.
#
# License
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 3, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; or the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA
# or visit the site <http://www.gnu.org/licenses/>.
#
#
# The PLOT level's figure builders: the seven matplotlib diagnostics of
# the logistic-model run (the three classic plots ported from the R rglm
# workflow plus four extensions).
#
# matplotlib and scipy are imported LAZILY (inside the functions):
# importing this module must stay cheap, because hlp_config_schemas
# imports PLOT_NAMES from here and the config is parsed by every
# pipeline — and by the client — run.
#
# Space: Y (the [-64, +64] game-value scale) — Y values are comparable
# across models with different logit_clipping, Z values are distorted per
# model.
#
# Determinism: every randomness (the jitter, the KDE subsample) is
# driven by SEEDed numpy generators, so these figures are reproducible
# run over run, and the PNG output is byte-deterministic under a fixed
# matplotlib version.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable

import numpy as np


if TYPE_CHECKING:
    from matplotlib.figure import Figure
    from reversi.lm.logistic_model import LMContext


__all__ = ['PLOT_NAMES', 'PLOT_TITLES', 'PLOT_BUILDERS',
           'PlotData', 'PlotStyle', 'collect_plot_data', 'save_figure',
           'close_figure', 'jitter', 'egv_bins']

#: The seven canonical plot names: the PLOT whitelist vocabulary
#: (validated by the PlotConfig schema). A name listed in the
#: config's plot section is generated, an unlisted one is skipped.
PLOT_NAMES = (
    "residual_density",
    "resid_vs_fitted",
    "resid_vs_gv",
    "gv_by_egv_box",
    "resid_mean_by_egv",
    "parity",
    "resid_qq",
)

#: The figure titles (the subtitle line carries the run name).
PLOT_TITLES = {
    "residual_density": "LM Residuals Distribution",
    "resid_vs_fitted": "LM Residuals vs Evaluated Game Value",
    "resid_vs_gv": "LM Residuals vs Game Values",
    "gv_by_egv_box": "LM Game Values by Evaluated Game Value",
    "resid_mean_by_egv": "LM Mean Residual by Evaluated Game Value",
    "parity": "LM Parity: Evaluated vs Game Value",
    "resid_qq": "LM Residuals: Normal QQ Plot",
}

#: The binned-axis note: the binning carries an ITALIC mathtext
#: parenthetical (this matplotlib build has no mathtext size
#: commands, so it stays at the axis font size — the accepted
#: fallback). An empty string disables the note.

#: Seeded generators: the jitter and the KDE subsample are
#: deterministic (the R jitter was not — see the header).

#: The KDE is evaluated on a capped subsample: scipy's gaussian_kde
#: density evaluation is O(n*m), so at full A2050 scale the cap keeps
#: the figure time flat without changing the curve (100k of ~2M
#: points is statistically indistinguishable).

#: The jitter amounts, as a FRACTION of the data range (the R
#: jitter semantics: uniform noise in
#: [-amount*range/2, +amount*range/2]): the fitted-values and
#: residual axes get 0.005 (a fine scatter spread), the game-value
#: axis gets 0.7 (the full horizontal "cloud" smearing over the
#: integer grid).

#: The KDE evaluation grid size.

#: The FIXED axis ranges (the axes do not follow the data — the
#: game-value axes are always the full [-64, +64] domain, the
#: residual-density axis the reasonable centered [-72, +72] window
#: (a residual beyond that is a broken model — the outlier report is
#: where they show up), the tick step 8 (the 0, 8, 16, ... labels).

#: The plot-1 series-label placement (data-coordinate fractions: x a
#: fraction of the axis span from the left, y a fraction of the
#: curve maximum). The Reference label sits high (it overlapped its
#: line at the lower position); the Training label sits at ~x = 25 in
#: data units (the span is [-72, +72]: (25 - (-72)) / 144 ~ 0.674),
#: so it clears the residual peak it used to cover.


@dataclass
class PlotStyle:
    """
    The appearance and determinism knobs of the figure builders (the config's plot
    section carries the same values, so the plot config is the single tuning point):
    the binned-axis note, the jitter/KDE seeds, the jitter amounts, the KDE grid +
    subsample cap, the fixed axis domains + the tick step, and the plot-1
    series-label placement.
    """
    binned_note: str = r" $(binned\ every\ 2)$"
    jitter_seed: int = 42
    kde_seed: int = 43
    kde_max_points: int = 100_000
    jitter_fitted_x: float = 0.005
    jitter_y: float = 0.005
    jitter_gv_x: float = 0.7
    kde_grid: int = 512
    axis_gv: float = 64.0
    axis_density: float = 72.0
    tick_step: float = 8.0
    series_label_x: dict[str, float] = field(default_factory=lambda: {
        "Validation": 0.04, "Training": 0.674, "Reference": 0.75})
    series_label_y: dict[str, float] = field(default_factory=lambda: {
        "Validation": 0.80, "Training": 0.96, "Reference": 0.98})


@dataclass
class PlotData:
    """
    Carry the PLOT level's inputs, all rounded-lossless f64 views (the f32
    predictions and the int8 game values upcast exactly — no f32
    rounding noise enters the figures):

    trn_y_true: the training game values (the Y scale).
    trn_rn: the TRAINING residuals in Y, the w_dense forward pass
        (the shipped inference rules — the same pass as the
        TRAINING-DENSE analytics column and the CLIENT_CHECK
        reference).
    vld_y_pred: the validation fitted values (the Y scale, the EF output).
    vld_rn: the validation residuals (the Y scale) — the VALIDATE /
        CLIENT_CHECK residuals.
    vld_gv: the validation game values (the Y scale).
    """
    trn_y_true: np.ndarray
    trn_rn: np.ndarray
    vld_y_pred: np.ndarray
    vld_rn: np.ndarray
    vld_gv: np.ndarray


def _mpl():
    """
    Import matplotlib lazily (the Agg backend, headless).

    Returns:
        module: the matplotlib.pyplot module (the lazy import keeps this
            module cheap — hlp_config_schemas imports PLOT_NAMES from
            here, and the config is parsed by every run).
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    return plt


def collect_plot_data(ctx: "LMContext") -> PlotData:
    """
    Assemble the PlotData from the series the pipeline already
    computed — the dense training residuals published by ANALYTICS
    (`ctx.train_dense_rn`) and the validation series published by
    VALIDATE (`ctx.vld_y_pred` / `ctx.vld_rn`), with the game values
    from POSITIONS / VLD_POSITIONS. No forward pass runs here: the
    figures render what the pipeline measured, they do not
    re-measure it.

    Args:
        ctx ("LMContext"): the pipeline context (the published series).

    Returns:
        PlotData: the five f64 series the builders draw.
    """
    return PlotData(
        trn_y_true=ctx.game_values.astype(np.float64),
        trn_rn=ctx.train_dense_rn,
        vld_y_pred=ctx.vld_y_pred,
        vld_rn=ctx.vld_rn,
        vld_gv=ctx.vld_game_values.astype(np.float64))


def jitter(rng: np.random.Generator, x: np.ndarray, amount: float) -> np.ndarray:
    """
    Jitter x with the R jitter semantics: uniform noise in
    [-amount*range(x)/2, +amount*range/2], amount a FRACTION of the
    data range. A zero-range input comes back untouched (the R
    degenerates the same way).

    Args:
        rng (np.random.Generator): the seeded generator (the callers pass one
            built from the style jitter seed).
        x (np.ndarray): the values to jitter.
        amount (float): the jitter amount as a fraction of the data range.

    Returns:
        np.ndarray: the jittered values.
    """
    r = float(x.max() - x.min())
    if r <= 0.0:
        return x
    return x + (rng.uniform(-1.0, 1.0, x.size) * amount * r) / 2.0


def egv_bins(y_pred: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    Bin the fitted values to the even step-2 grid (the R round_gv:
    2 * round(y_pred/2)). np.rint is banker's rounding against R's
    round-half-away-from-zero, but y_pred is a continuous f64 so the
    half-tie is a measure-zero event.

    Args:
        y_pred (np.ndarray): the fitted values to bin.

    Returns:
        tuple: (unique_egv_values, group_index_per_point).
    """
    egv = (2 * np.rint(y_pred / 2.0)).astype(np.int64)
    return np.unique(egv, return_inverse=True)


def _kde_curve(values: np.ndarray, grid: np.ndarray, style: PlotStyle) -> np.ndarray:
    """
    Compute the Gaussian-kernel density of values on the grid (scipy's
    gaussian_kde, Scott's rule bandwidth — the R density() uses
    Silverman's; the difference is below the plot resolution). Large
    inputs are subsampled to the style cap (seeded). A zero-variance
    input yields a flat zero curve (the degenerate kernel is
    singular).

    Args:
        values (np.ndarray): the series to smooth.
        grid (np.ndarray): the evaluation grid.
        style (PlotStyle): the knobs (the subsample seed + cap).

    Returns:
        np.ndarray: the density on the grid.
    """
    from scipy.stats import gaussian_kde
    v = values
    if v.size > style.kde_max_points:
        v = np.random.default_rng(style.kde_seed).choice(v, style.kde_max_points,
                                                         replace=False)
    if float(v.std()) <= 0.0:
        return np.zeros(grid.shape)
    return gaussian_kde(v)(grid)


def _sym_limit(values: np.ndarray, step: float = 8.0) -> float:
    """
    Compute the symmetric residual-axis limit: the max absolute value
    rounded UP to the tick step (the "reasonable value"), at least one
    step.

    Args:
        values (np.ndarray): the series whose spread sets the limit.
        step (float): the tick step to round up to (the style tick step).

    Returns:
        float: the symmetric limit (the axis is [-limit, +limit]).
    """
    m = float(np.abs(values).max())
    if not np.isfinite(m) or m <= 0.0:
        return step
    return float(step * np.ceil(m / step))


def _fig(title: str, run_name: str, xlabel: str, ylabel: str):
    """
    Build a fresh figure in the light-theme look (the grid on, the
    R theme_light equivalent). The title is two lines: the plot name
    in BOLD, the run description in ITALIC with a smaller font,
    spaced apart (the name sits high via the pad, the description just
    above the axis).

    Args:
        title (str): the figure title (the plot name).
        run_name (str): the run name (the config name, the italic subtitle).
        xlabel (str): the x axis label.
        ylabel (str): the y axis label.

    Returns:
        tuple: (fig, ax) — the fresh figure + its axis.
    """
    plt = _mpl()
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.grid(True, alpha=0.3)
    ax.set_title(title, fontsize=13, fontweight="bold", pad=26)
    ax.text(0.5, 1.005, run_name, transform=ax.transAxes, ha="center",
            va="bottom", style="italic", fontsize=10)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    return fig, ax


# --- The seven figure builders ------------------------------------------
# Each takes the PlotData + the run name (the config name, the R
# runcode's place in the title) + the PlotStyle, and returns the
# matplotlib Figure (the worker saves it in every configured format,
# then closes it).

def plot_residual_density(d: PlotData, run_name: str,
                          style: PlotStyle) -> "Figure":
    """
    Build the plot-1 figure: probability density vs game value
    residual, three curves — Reference (the training game values
    centered on their mean: the "population" series of the analytics
    report), Training (the training residuals) and Validation (the
    validation residuals). The dashed vline marks the training
    residual mean; the margin labels carry the sd (the validation
    one also the mean/min/max).

    Args:
        d (PlotData): the PLOT inputs (the training + validation series).
        run_name (str): the run name (the config name, the subtitle line).
        style (PlotStyle): the knobs (the window, the KDE grid/seed/cap, the
            label placement).

    Returns:
        Figure: the built figure (the worker saves it, then closes it).
    """
    ref = d.trn_y_true - d.trn_y_true.mean()
    series = (("Reference", ref, "slategray"),
              ("Training", d.trn_rn, "firebrick"),
              ("Validation", d.vld_rn, "black"))

    # The FIXED centered window (always centered on zero, the
    # reasonable [-72, +72] — a residual beyond it means a broken
    # model, and the outlier report is where those show up; in
    # theory the residual can reach +/-128).
    lo, hi = -style.axis_density, style.axis_density
    span = float(hi - lo)
    grid = np.linspace(lo, hi, style.kde_grid)

    fig, ax = _fig(PLOT_TITLES["residual_density"], run_name,
                   "Game value residual", "Probability density")
    max_y = 0.0
    for label, vals, color in series:
        curve = _kde_curve(vals, grid, style)
        max_y = max(max_y, float(curve.max()))
        ax.plot(grid, curve, color=color, lw=1.4)
        ax.text(lo + style.series_label_x[label] * span,
                style.series_label_y[label] * max_y,
                _series_label(label, vals), ha="left", va="top",
                fontsize=9, color=color)
    ax.axvline(float(d.trn_rn.mean()), color="black", ls="--", lw=0.8)
    ax.set_xlim(lo, hi)
    ax.set_ylim(0.0, max_y * 1.15)
    # No legend: the margin labels identify the curves.
    return fig


def _series_label(label: str, vals: np.ndarray) -> str:
    """
    Format the plot-1 series margin label (the name + the sd, the
    Validation one also the mean/min/max).

    Args:
        label (str): the series name ("Reference" / "Training" / "Validation").
        vals (np.ndarray): the series values (the sd/mean/min/max source).

    Returns:
        str: the formatted label.
    """
    sd = f"{float(vals.std()):6.4f}"
    if label == "Validation":
        return (f"Validation:\nsd = {sd}\nmean = {float(vals.mean()):6.4f}"
                f"\nmin = {float(vals.min()):6.4f}"
                f"\nmax = {float(vals.max()):6.4f}")
    return f"{label}:\nsd = {sd}"


def plot_resid_vs_fitted(d: PlotData, run_name: str,
                         style: PlotStyle) -> "Figure":
    """
    Build the plot-2 figure: the validation residual cloud vs the
    fitted values (the EF output), the gray-dot scatter with the
    seeded R-semantic jitter on both axes.

    Args:
        d (PlotData): the PLOT inputs (the validation series).
        run_name (str): the run name (the config name, the subtitle line).
        style (PlotStyle): the knobs (the jitter seed + amounts, the x domain,
            the tick step).

    Returns:
        Figure: the built figure (the worker saves it, then closes it).
    """
    rng = np.random.default_rng(style.jitter_seed)
    x = jitter(rng, d.vld_y_pred, style.jitter_fitted_x)
    y = jitter(rng, d.vld_rn, style.jitter_y)
    fig, ax = _fig(PLOT_TITLES["resid_vs_fitted"], run_name,
                   "Evaluated game value", "Game value residual")
    ax.scatter(x, y, s=4, c="black", alpha=0.04)
    # The FIXED axes: x always the full domain (the fitted values
    # live in it by construction), y symmetric on a reasonable
    # (tick-step-rounded) limit.
    lim = _sym_limit(y, style.tick_step)
    ax.set_xlim(-style.axis_gv, style.axis_gv)
    ax.set_ylim(-lim, lim)
    return fig


def plot_resid_vs_gv(d: PlotData, run_name: str,
                     style: PlotStyle) -> "Figure":
    """
    Build the plot-3 figure: the validation residual cloud vs the
    actual game values, the gray-dot scatter; the x jitter is the
    large 0.7-range fraction (the "cloud" smearing over the integer
    grid), the y jitter the fine one.

    Args:
        d (PlotData): the PLOT inputs (the validation series).
        run_name (str): the run name (the config name, the subtitle line).
        style (PlotStyle): the knobs (the jitter seed + amounts, the x domain,
            the tick step).

    Returns:
        Figure: the built figure (the worker saves it, then closes it).
    """
    rng = np.random.default_rng(style.jitter_seed)
    x = jitter(rng, d.vld_gv, style.jitter_gv_x)
    y = jitter(rng, d.vld_rn, style.jitter_y)
    fig, ax = _fig(PLOT_TITLES["resid_vs_gv"], run_name,
                   "Game value", "Game value residual")
    ax.scatter(x, y, s=4, c="black", alpha=0.02)
    # The FIXED axes: x always the full game-value domain — the
    # previous data-driven axis let the 0.7 "cloud" jitter smear the
    # auto-range to +/-108; the jittered points beyond the domain are
    # clipped by the axis, the labels are NOT swapped. y as in
    # resid_vs_fitted.
    lim = _sym_limit(y, style.tick_step)
    ax.set_xlim(-style.axis_gv, style.axis_gv)
    ax.set_ylim(-lim, lim)
    return fig


def plot_gv_by_egv_box(d: PlotData, run_name: str,
                       style: PlotStyle) -> "Figure":
    """
    Build the plot-4 figure: the validation game values as a box
    plot per evaluated game value (the fitted Y rounded to the
    step-2 grid), both axes fixed to the full scale.

    Args:
        d (PlotData): the PLOT inputs (the validation fitted + true game values).
        run_name (str): the run name (the config name, the subtitle line).
        style (PlotStyle): the knobs (the binned note, the axis domain, the
            tick step).

    Returns:
        Figure: the built figure (the worker saves it, then closes it).
    """
    unique, inv = egv_bins(d.vld_y_pred)
    groups = [d.vld_gv[inv == k] for k in range(unique.size)]
    fig, ax = _fig(PLOT_TITLES["gv_by_egv_box"], run_name,
                   "Evaluated game value" + style.binned_note, "Game value")
    ax.boxplot(groups, positions=unique, widths=0.7,
               flierprops=dict(markersize=1.0, alpha=0.4))
    # The FIXED axes: BOTH always the full domain, regardless of the
    # data; the ticks on the tick-step grid.
    ticks = np.arange(-style.axis_gv, style.axis_gv + 1, style.tick_step)
    ax.set_xlim(-style.axis_gv, style.axis_gv)
    ax.set_ylim(-style.axis_gv, style.axis_gv)
    # The EXPLICIT labels are mandatory (the stale-label bug):
    # boxplot() leaves the N categorical bin labels on the axis, and
    # a positions-only set_xticks keeps those stale labels — the
    # first 17 bins (-62..-30) would be printed under the 17
    # tick-step positions.
    ax.set_xticks(ticks, labels=[str(int(t)) for t in ticks])
    return fig


def plot_resid_mean_by_egv(d: PlotData, run_name: str,
                           style: PlotStyle) -> "Figure":
    """
    Build the plot-5 figure: the validation residual MEAN with the
    +/- sd error bars per evaluated game value, against the zero
    line — the systematic-bias-per-level view (a miscalibrated
    region of the evaluation scale shows up as a drift away from
    zero). Single-point bins have a zero bar.

    Args:
        d (PlotData): the PLOT inputs (the validation series).
        run_name (str): the run name (the config name, the subtitle line).
        style (PlotStyle): the knobs (the binned note, the axis domain, the
            tick step).

    Returns:
        Figure: the built figure (the worker saves it, then closes it).
    """
    unique, inv = egv_bins(d.vld_y_pred)
    means, sds, counts = [], [], []
    for k in range(unique.size):
        g = d.vld_rn[inv == k]
        means.append(float(g.mean()))
        sds.append(float(g.std(ddof=1)) if g.size > 1 else 0.0)
        counts.append(int(g.size))
    fig, ax = _fig(PLOT_TITLES["resid_mean_by_egv"], run_name,
                   "Evaluated game value" + style.binned_note,
                   "Residual, mean +/- sd")
    ax.errorbar(unique, means, yerr=sds, fmt="o", ms=4, color="firebrick",
                ecolor="firebrick", elinewidth=0.8, capsize=3)
    ax.axhline(0.0, color="black", ls="--", lw=0.8)
    # The FIXED axes: x always the full domain; y hugs the ACTUAL
    # data — the full |mean| + sd extent rounded UP to the tick-step
    # grid, kept SYMMETRIC (a value in range stays in range); the
    # tick labels in the smaller font.
    extent = np.abs(np.array(means)) + np.array(sds)
    lim = _sym_limit(extent, style.tick_step)
    ax.set_xlim(-style.axis_gv, style.axis_gv)
    ax.set_ylim(-lim, lim)
    ax.set_xticks(np.arange(-style.axis_gv, style.axis_gv + 1, style.tick_step))
    ax.set_yticks(np.arange(-lim, lim + 1, style.tick_step))
    ax.tick_params(axis="both", labelsize=8)
    return fig


def plot_parity(d: PlotData, run_name: str,
                style: PlotStyle) -> "Figure":
    """
    Build the plot-6 figure: the parity view — the validation game
    values against the fitted values, the 45-degree line, both axes
    on the full scale (the global fit quality at a glance).

    Args:
        d (PlotData): the PLOT inputs (the validation series).
        run_name (str): the run name (the config name, the subtitle line).
        style (PlotStyle): the knobs (the frame domain).

    Returns:
        Figure: the built figure (the worker saves it, then closes it).
    """
    fig, ax = _fig(PLOT_TITLES["parity"], run_name,
                   "Evaluated game value", "Game value")
    ax.scatter(d.vld_y_pred, d.vld_gv, s=4, c="black", alpha=0.04)
    ax.plot([-style.axis_gv, style.axis_gv], [-style.axis_gv, style.axis_gv],
            color="slategray", lw=1.0)
    ax.set_xlim(-style.axis_gv, style.axis_gv)
    ax.set_ylim(-style.axis_gv, style.axis_gv)
    ax.set_aspect("equal")
    return fig


def plot_resid_qq(d: PlotData, run_name: str,
                  style: PlotStyle) -> "Figure":
    """
    Build the plot-7 figure: the normal QQ plot of the validation
    residuals — the sorted sample quantiles against the standard
    normal theoretical quantiles (scipy.ndtri), the dashed line the
    y = sd * x scale line (residuals that are normal with mean zero
    sit ON the line; tails that deviate from it are non-normality).
    The skewness/kurtosis show up as the tail deviations.

    Args:
        d (PlotData): the PLOT inputs (the validation residuals).
        run_name (str): the run name (the config name, the subtitle line).
        style (PlotStyle): the knobs (the y-frame domain).

    Returns:
        Figure: the built figure (the worker saves it, then closes it).
    """
    from scipy.special import ndtri
    rn = np.sort(d.vld_rn)
    n = rn.size
    theory = ndtri((np.arange(1, n + 1) - 0.5) / n)
    sd_rn = float(rn.std())
    fig, ax = _fig(PLOT_TITLES["resid_qq"], run_name,
                   "Theoretical quantiles (standard normal)",
                   "Sample quantiles (residual, Y)")
    ax.scatter(theory, rn, s=4, c="black", alpha=0.05)
    xs = np.array([theory.min(), theory.max()])
    ax.plot(xs, sd_rn * xs, color="firebrick", ls="--", lw=1.0)
    # The FIXED axis: y (the sample quantiles of the residual)
    # always the full domain; x (the theoretical quantiles) stays
    # data-driven (the normal tail, about +/-3.3).
    ax.set_ylim(-style.axis_gv, style.axis_gv)
    return fig


#: The name -> builder registry (the worker dispatches on it; each
#: builder takes the PlotData, the run name, and the PlotStyle).
PLOT_BUILDERS: dict[str, Callable[[PlotData, str, PlotStyle], "Figure"]] = {
    "residual_density": plot_residual_density,
    "resid_vs_fitted": plot_resid_vs_fitted,
    "resid_vs_gv": plot_resid_vs_gv,
    "gv_by_egv_box": plot_gv_by_egv_box,
    "resid_mean_by_egv": plot_resid_mean_by_egv,
    "parity": plot_parity,
    "resid_qq": plot_resid_qq,
}


def save_figure(fig: "Figure", path, fmt: str, dpi: int = 150) -> None:
    """
    Save the figure to path in the given format (png at dpi, pdf
    vector). Only the schema-validated formats reach here.

    The format is passed EXPLICITLY: the file name may carry a
    non-standard suffix, and matplotlib otherwise sniffs the
    extension (the 'png2' trap).

    Args:
        fig ("Figure"): the figure to save.
        path (Path): the destination path.
        fmt (str): the format ("png" or "pdf").
        dpi (int): the raster resolution (the png output).
    """
    if fmt == "png":
        fig.savefig(path, format="png", dpi=dpi)
    elif fmt == "pdf":
        fig.savefig(path, format="pdf")
    else:
        raise ValueError(f"Unknown plot format: {fmt!r}")


def close_figure(fig: "Figure") -> None:
    """
    Release the figure's resources (the worker calls it after every
    save round).

    Args:
        fig ("Figure"): the figure to release.
    """
    plt = _mpl()
    plt.close(fig)
