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
# The PLOT level's figure builders (D-149): the seven matplotlib
# diagnostics of the logistic-model run, ported from the R rglm
# workflow's three classic plots plus four extensions (the R script
# itself is NOT referenced anywhere in the documentation — it is a
# scratch artifact slated for deletion).
#
# matplotlib and scipy are imported LAZILY (inside the functions):
# importing this module must stay cheap, because hlp_config_schemas
# imports PLOT_NAMES from here and the config is parsed by every
# pipeline — and by the client — run.
#
# Space: Y (the [-64, +64] game-value scale), per the D-148 ruling —
# Y values are comparable across models with different
# logit_clipping, Z values are distorted per model.
#
# Determinism: every randomness (the jitter, the KDE subsample) is
# driven by SEEDed numpy generators (the R jitter was unseeded —
# these figures are reproducible run over run, and the PNG output is
# byte-deterministic under a fixed matplotlib version).

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable

import numpy as np

from reversi.lm.hlp_gradient import sigmoid

if TYPE_CHECKING:
    from matplotlib.figure import Figure
    from reversi.lm.logistic_model import LMContext


__all__ = ['PLOT_NAMES', 'PLOT_TITLES', 'PLOT_BUILDERS',
           'PlotData', 'collect_plot_data', 'save_figure', 'close_figure',
           'jitter', 'egv_bins']

#: The seven canonical plot names: the PLOT whitelist vocabulary
#: (D-149, validated by the PlotConfig schema). A name listed in the
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
    "resid_vs_fitted": "LM Residuals vs Fitted Values",
    "resid_vs_gv": "LM Residuals vs Game Values",
    "gv_by_egv_box": "LM Game Values by Evaluated Game Value",
    "resid_mean_by_egv": "LM Mean Residual by Evaluated Game Value",
    "parity": "LM Parity: Fitted vs Game Value",
    "resid_qq": "LM Residuals: Normal QQ Plot",
}

#: Seeded generators: the jitter and the KDE subsample are
#: deterministic (the R jitter was not — see the header).
_JITTER_SEED = 42
_KDE_SEED = 43

#: The KDE is evaluated on a capped subsample: scipy's gaussian_kde
#: density evaluation is O(n*m), so at full A2050 scale the cap keeps
#: the figure time flat without changing the curve (100k of ~2M
#: points is statistically indistinguishable).
_KDE_MAX_POINTS = 100_000

#: The jitter amounts, as a FRACTION of the data range (the R
#: jitter semantics: uniform noise in
#: [-amount*range/2, +amount*range/2]), ported from the R script:
#: the fitted-values and residual axes get 0.005 (a fine scatter
#: spread), the game-value axis gets 0.7 (the full horizontal
#: "cloud" smearing over the integer grid).
_JIT_FITTED_X = 0.005
_JIT_Y = 0.005
_JIT_GV_X = 0.7

#: The KDE evaluation grid size.
_KDE_GRID = 512

#: The FIXED axis ranges (Roberto's D-150 ruling: the axes do not
#: follow the data — the game-value axes are always the full
#: [-64, +64] domain, the residual-density axis the reasonable
#: centered [-72, +72] window (a residual beyond that is a broken
#: model — the outlier report is where they show up), the tick
#: step 8 (the 0, 8, 16, ... labels).
_AXIS_GV = 64.0
_AXIS_DENSITY = 72.0
_TICK_STEP = 8.0


def _mpl():
    """The lazy matplotlib import (the Agg backend, headless)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    return plt


@dataclass
class PlotData:
    """
    The PLOT level's inputs, all rounded-lossless f64 views (the f32
    predictions and the int8 game values upcast exactly — no f32
    rounding noise enters the figures):

    trn_y_true: the training game values (Y).
    trn_rn: the TRAINING residuals in Y, the w_dense forward pass
        (the shipped inference rules — the same pass as the
        TRAINING-DENSE analytics column and the CLIENT_CHECK
        reference).
    vld_y_pred: the validation fitted values (Y, the EF output).
    vld_rn: the validation residuals (Y) — the VALIDATE /
        CLIENT_CHECK residuals.
    vld_gv: the validation game values (Y).
    """
    trn_y_true: np.ndarray
    trn_rn: np.ndarray
    vld_y_pred: np.ndarray
    vld_rn: np.ndarray
    vld_gv: np.ndarray


def collect_plot_data(ctx: "LMContext") -> PlotData:
    """
    Builds the PlotData from the pipeline context: the training
    w_dense forward pass over ctx.hlp_indexes.indexes (the same
    gather + row sum as hlp_analytics.compute_training_dense_metrics)
    and the validation forward pass (the same formula as
    hlp_validate.validate_model — the CLIENT_CHECK reference).
    Stateless: nothing is stored on the context.
    """
    n_instances_per_feature = [f.n_instances for f in ctx.feature_set.features]
    col_offsets = np.repeat(ctx.iwmap_feature_offset[:-1], n_instances_per_feature)

    # Training: the dense pass (what the saved model actually computes).
    dense_indices = ctx.hlp_indexes.indexes + col_offsets
    linear_predictor = np.sum(ctx.w_dense[dense_indices], axis=1)
    y_pred_trn = ctx.z2y(sigmoid(linear_predictor))
    y_true = ctx.game_values.astype(np.float64)
    trn_rn = y_pred_trn.astype(np.float64) - y_true

    # Validation: the VALIDATE forward pass (the in-memory reference).
    vld_indexes = ctx.feature_set.compute_indexes(ctx.vld_positions)
    dense_indices_v = vld_indexes + col_offsets
    linear_predictor_v = np.sum(ctx.w_dense[dense_indices_v], axis=1)
    vld_y_pred = ctx.z2y(sigmoid(linear_predictor_v)).astype(np.float64)
    vld_gv = ctx.vld_game_values.astype(np.float64)
    vld_rn = vld_y_pred - vld_gv

    return PlotData(trn_y_true=y_true, trn_rn=trn_rn,
                    vld_y_pred=vld_y_pred, vld_rn=vld_rn, vld_gv=vld_gv)


def jitter(rng: np.random.Generator, x: np.ndarray, amount: float) -> np.ndarray:
    """
    The R jitter semantics: uniform noise in
    [-amount*range(x)/2, +amount*range/2], amount a FRACTION of the
    data range. A zero-range input comes back untouched (the R
    degenerates the same way).
    """
    r = float(x.max() - x.min())
    if r <= 0.0:
        return x
    return x + (rng.uniform(-1.0, 1.0, x.size) * amount * r) / 2.0


def egv_bins(y_pred: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    The evaluated-game-value bins (the R round_gv): y_pred rounded
    to the even step-2 grid (2 * round(y_pred/2)). np.rint is
    banker's rounding against R's round-half-away-from-zero, but
    y_pred is a continuous f64 so the half-tie is a measure-zero
    event. Returns (unique_egv_values, group_index_per_point).
    """
    egv = (2 * np.rint(y_pred / 2.0)).astype(np.int64)
    return np.unique(egv, return_inverse=True)


def _kde_curve(values: np.ndarray, grid: np.ndarray) -> np.ndarray:
    """
    The Gaussian-kernel density of values on the grid (scipy's
    gaussian_kde, Scott's rule bandwidth — the R density() uses
    Silverman's; the difference is below the plot resolution).
    Large inputs are subsampled to _KDE_MAX_POINTS (seeded). A
    zero-variance input yields a flat zero curve (the degenerate
    kernel is singular).
    """
    from scipy.stats import gaussian_kde
    v = values
    if v.size > _KDE_MAX_POINTS:
        v = np.random.default_rng(_KDE_SEED).choice(v, _KDE_MAX_POINTS,
                                                    replace=False)
    if float(v.std()) <= 0.0:
        return np.zeros(grid.shape)
    return gaussian_kde(v)(grid)


def _sym_limit(values: np.ndarray, step: float = _TICK_STEP) -> float:
    """The symmetric residual-axis limit: the max absolute value
    rounded UP to the tick step (the "reasonable value" Roberto
    asks for), at least one step."""
    m = float(np.abs(values).max())
    if not np.isfinite(m) or m <= 0.0:
        return step
    return float(step * np.ceil(m / step))


def _fig(title: str, run_name: str, xlabel: str, ylabel: str):
    """A fresh figure in the light-theme look (the grid on, the
    R theme_light equivalent). The title is two lines (D-150):
    the plot name in BOLD, the run description in ITALIC with a
    smaller font, spaced apart (the name sits high via the pad,
    the description just above the axis)."""
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
# runcode's place in the title) and returns the matplotlib Figure
# (the worker saves it in every configured format, then closes it).

def plot_residual_density(d: PlotData, run_name: str) -> "Figure":
    """
    Plot 1 (the R p0): probability density vs game value residual,
    three curves — Reference (the training game values centered on
    their mean: the "population" series of the analytics report),
    Training (the training residuals) and Validation (the
    validation residuals). The dashed vline marks the training
    residual mean; the margin labels carry the sd (the validation
    one also the mean/min/max).
    """
    ref = d.trn_y_true - d.trn_y_true.mean()
    series = (("Reference", ref, "slategray"),
              ("Training", d.trn_rn, "firebrick"),
              ("Validation", d.vld_rn, "black"))

    # The FIXED centered window (the D-150 ruling: always centered
    # on zero, the reasonable [-72, +72] — a residual beyond it
    # means a broken model, and the outlier report is where those
    # show up; in theory the residual can reach +/-128).
    lo, hi = -_AXIS_DENSITY, _AXIS_DENSITY
    span = float(hi - lo)
    grid = np.linspace(lo, hi, _KDE_GRID)

    fig, ax = _fig(PLOT_TITLES["residual_density"], run_name,
                   "Game value residual (Y)", "Probability density")
    max_y = 0.0
    for label, vals, color in series:
        curve = _kde_curve(vals, grid)
        max_y = max(max_y, float(curve.max()))
        ax.plot(grid, curve, color=color, lw=1.4)
        ax.text(lo + _TXT_X[label] * span, _TXT_Y[label] * max_y,
                _series_label(label, vals), ha="left", va="top",
                fontsize=9, color=color)
    ax.axvline(float(d.trn_rn.mean()), color="black", ls="--", lw=0.8)
    ax.set_xlim(lo, hi)
    ax.set_ylim(0.0, max_y * 1.15)
    # No legend (the R original had legend.position = "None" —
    # the margin labels identify the curves).
    return fig


#: The annotation placement of plot 1 (data-coordinate fractions:
#: x as a fraction of the axis span from the left, y as a fraction
#: of the curve maximum). The Reference label sits HIGH (D-150:
#: it overlapped its line at the lower position).
_TXT_X = {"Validation": 0.04, "Training": 0.40, "Reference": 0.75}
_TXT_Y = {"Validation": 0.80, "Training": 0.96, "Reference": 0.98}


def _series_label(label: str, vals: np.ndarray) -> str:
    sd = f"{float(vals.std()):6.4f}"
    if label == "Validation":
        return (f"Validation:\nsd = {sd}\nmean = {float(vals.mean()):6.4f}"
                f"\nmin = {float(vals.min()):6.4f}"
                f"\nmax = {float(vals.max()):6.4f}")
    return f"{label}:\nsd = {sd}"


def plot_resid_vs_fitted(d: PlotData, run_name: str) -> "Figure":
    """
    Plot 2 (the R p1): the validation residual cloud vs the fitted
    values (the EF output), the gray-dot scatter with the seeded
    R-semantic jitter on both axes.
    """
    rng = np.random.default_rng(_JITTER_SEED)
    x = jitter(rng, d.vld_y_pred, _JIT_FITTED_X)
    y = jitter(rng, d.vld_rn, _JIT_Y)
    fig, ax = _fig(PLOT_TITLES["resid_vs_fitted"], run_name,
                   "Fitted (Y)", "Game value residual (Y)")
    ax.scatter(x, y, s=4, c="black", alpha=0.04)
    # The D-150 axes: x always the full [-64, +64] domain (the
    # fitted values live in it by construction), y symmetric on a
    # reasonable (tick-step-rounded) limit.
    lim = _sym_limit(y)
    ax.set_xlim(-_AXIS_GV, _AXIS_GV)
    ax.set_ylim(-lim, lim)
    return fig


def plot_resid_vs_gv(d: PlotData, run_name: str) -> "Figure":
    """
    Plot 3 (the R p2): the validation residual cloud vs the actual
    game values, the gray-dot scatter; the x jitter is the large
    0.7-range fraction (the "cloud" smearing over the integer
    grid), the y jitter the fine one.
    """
    rng = np.random.default_rng(_JITTER_SEED)
    x = jitter(rng, d.vld_gv, _JIT_GV_X)
    y = jitter(rng, d.vld_rn, _JIT_Y)
    fig, ax = _fig(PLOT_TITLES["resid_vs_gv"], run_name,
                   "Game value (Y)", "Game value residual (Y)")
    ax.scatter(x, y, s=4, c="black", alpha=0.02)
    # The D-150 axes: x always the full [-64, +64] game-value
    # domain — the previous data-driven axis let the 0.7 "cloud"
    # jitter smear the auto-range to +/-108 (Roberto read it as
    # swapped labels); the jittered points beyond the domain are
    # clipped by the axis, the labels are NOT swapped. y as in
    # resid_vs_fitted.
    lim = _sym_limit(y)
    ax.set_xlim(-_AXIS_GV, _AXIS_GV)
    ax.set_ylim(-lim, lim)
    return fig


def plot_gv_by_egv_box(d: PlotData, run_name: str) -> "Figure":
    """
    Plot 4 (the R boxplot helper, never shipped in the R return
    list): the validation game values as a box plot per evaluated
    game value (the fitted Y rounded to the step-2 grid), y fixed
    to the full [-64, +64] scale.
    """
    unique, inv = egv_bins(d.vld_y_pred)
    groups = [d.vld_gv[inv == k] for k in range(unique.size)]
    fig, ax = _fig(PLOT_TITLES["gv_by_egv_box"], run_name,
                   "Evaluated game value (Y, step 2)", "Game value (Y)")
    ax.boxplot(groups, positions=unique, widths=0.7,
               flierprops=dict(markersize=1.0, alpha=0.4))
    # The D-150 axes: BOTH always the full [-64, +64] domain,
    # regardless of the data; the ticks on the step-8 grid.
    ticks = np.arange(-_AXIS_GV, _AXIS_GV + 1, _TICK_STEP)
    ax.set_xlim(-_AXIS_GV, _AXIS_GV)
    ax.set_ylim(-_AXIS_GV, _AXIS_GV)
    # The EXPLICIT labels are mandatory (the D-153 stale-label bug):
    # boxplot() leaves the N categorical bin labels on the axis, and
    # a positions-only set_xticks keeps those stale labels — the
    # first 17 bins (-62..-30) would be printed under the 17
    # step-8 positions.
    ax.set_xticks(ticks, labels=[str(int(t)) for t in ticks])
    return fig


def plot_resid_mean_by_egv(d: PlotData, run_name: str) -> "Figure":
    """
    Plot 5 (new diagnostic): the validation residual MEAN with the
    +/- sd error bars per evaluated game value, against the zero
    line — the systematic-bias-per-level view (a miscalibrated
    region of the evaluation scale shows up as a drift away from
    zero). Single-point bins have a zero bar.
    """
    unique, inv = egv_bins(d.vld_y_pred)
    means, sds, counts = [], [], []
    for k in range(unique.size):
        g = d.vld_rn[inv == k]
        means.append(float(g.mean()))
        sds.append(float(g.std(ddof=1)) if g.size > 1 else 0.0)
        counts.append(int(g.size))
    fig, ax = _fig(PLOT_TITLES["resid_mean_by_egv"], run_name,
                   "Evaluated game value (Y, step 2)",
                   "Residual (Y), mean +/- sd")
    ax.errorbar(unique, means, yerr=sds, fmt="o", ms=4, color="firebrick",
                ecolor="firebrick", elinewidth=0.8, capsize=3)
    ax.axhline(0.0, color="black", ls="--", lw=0.8)
    # The D-150/D-151 axes: x always the full [-64, +64] domain
    # (Roberto: "asse x perfetto"); y hugs the ACTUAL data — the
    # full |mean| + sd extent rounded UP to the step-8 grid, kept
    # SYMMETRIC (the D-151 ruling: "i valori min e max reali del
    # grafico ... se il valore è nel range -16,+16 teniamolo in
    # questo range"); the tick labels in the smaller font (D-151:
    # "riduci la dimensione del font dei valori sugli assi").
    extent = np.abs(np.array(means)) + np.array(sds)
    lim = _sym_limit(extent)
    ax.set_xlim(-_AXIS_GV, _AXIS_GV)
    ax.set_ylim(-lim, lim)
    ax.set_xticks(np.arange(-_AXIS_GV, _AXIS_GV + 1, _TICK_STEP))
    ax.set_yticks(np.arange(-lim, lim + 1, _TICK_STEP))
    ax.tick_params(axis="both", labelsize=8)
    return fig


def plot_parity(d: PlotData, run_name: str) -> "Figure":
    """
    Plot 6 (new diagnostic): the parity view — the validation game
    values against the fitted values, the 45-degree line, both axes
    on the full [-64, +64] scale (the global fit quality at a
    glance).
    """
    fig, ax = _fig(PLOT_TITLES["parity"], run_name,
                   "Fitted (Y)", "Game value (Y)")
    ax.scatter(d.vld_y_pred, d.vld_gv, s=4, c="black", alpha=0.04)
    ax.plot([-64.0, 64.0], [-64.0, 64.0], color="slategray", lw=1.0)
    ax.set_xlim(-64.0, 64.0)
    ax.set_ylim(-64.0, 64.0)
    ax.set_aspect("equal")
    return fig


def plot_resid_qq(d: PlotData, run_name: str) -> "Figure":
    """
    Plot 7 (new diagnostic): the normal QQ plot of the validation
    residuals — the sorted sample quantiles against the standard
    normal theoretical quantiles (scipy.ndtri), the dashed line the
    y = sd * x scale line (residuals that are normal with mean zero
    sit ON the line; tails that deviate from it are non-normality).
    The R script computed the skewness/kurtosis numerically; this
    shows them.
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
    # The D-150 axis: y (the sample quantiles of the residual)
    # always the full [-64, +64]; x (the theoretical quantiles)
    # stays data-driven (the normal tail, about +/-3.3).
    ax.set_ylim(-_AXIS_GV, _AXIS_GV)
    return fig


#: The name -> builder registry (the worker dispatches on it).
PLOT_BUILDERS: dict[str, Callable[[PlotData, str], "Figure"]] = {
    "residual_density": plot_residual_density,
    "resid_vs_fitted": plot_resid_vs_fitted,
    "resid_vs_gv": plot_resid_vs_gv,
    "gv_by_egv_box": plot_gv_by_egv_box,
    "resid_mean_by_egv": plot_resid_mean_by_egv,
    "parity": plot_parity,
    "resid_qq": plot_resid_qq,
}


def save_figure(fig: "Figure", path, fmt: str, dpi: int = 150) -> None:
    """Saves the figure to path in the given format (png at dpi, pdf
    vector). Only the schema-validated formats reach here."""
    # The format is passed EXPLICITLY: the file name may carry a
    # non-standard suffix, and matplotlib otherwise sniffs the
    # extension (the 'png2' trap).
    if fmt == "png":
        fig.savefig(path, format="png", dpi=dpi)
    elif fmt == "pdf":
        fig.savefig(path, format="pdf")
    else:
        raise ValueError(f"Unknown plot format: {fmt!r}")


def close_figure(fig: "Figure") -> None:
    """Releases the figure's resources (the worker calls it after
    every save round)."""
    plt = _mpl()
    plt.close(fig)
