#
# hlp_anova.py
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
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA
# or visit the site <http://www.gnu.org/licenses/>.
#

import csv
from pathlib import Path

import numpy as np
import numpy.typing as npt
from pydantic import validate_call, ConfigDict
from scipy.stats import chi2 as _chi2

from reversi.tools.state_machine import Relevance

__all__ = ['hlp_anova_eta_omega', 'hlp_anova_adherence',
           'hlp_anova_compute_analysis', 'hlp_anova_generate_report']


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def hlp_anova_eta_omega(groups: npt.ArrayLike, values: npt.ArrayLike) -> dict:
    """
    Calculate the one-way ANOVA effect sizes (the eta-squared and the omega-squared) for the observations grouped
    by their observed codes.

    This function partitions the observations into groups by their observed codes and measures how much of the
    total variance of the target values is explained by the group membership. It returns the eta-squared (the
    biased sample share of the explained variance, growing with high K) together with the omega-squared (the
    unbiased population estimate): the pair is reported as the discrimination metrics of the group assignment.

        SS_tot = sum (y - ybar)^2
        SS_eff = sum_g n_g (y_g - ybar)^2
        SS_err = SS_tot - SS_eff
        eta²   = SS_eff / SS_tot
        omega² = (SS_eff - (K - 1) MS_err) / (SS_tot + MS_err)
        MS_err = SS_err / (N - K)

    Args:
        groups (npt.ArrayLike): The group assignment of the observations, one element per observation (the observed
            codes). Any hashable values are accepted.
        values (npt.ArrayLike): The continuous target values, one element per observation, aligned with `groups`
            (the continuous game values).

    Returns:
        dict[str, float | int]: A dictionary containing the following keys:
            - 'eta2': The eta-squared effect size, in the 0.0 to 1.0 range.
            - 'omega2': The omega-squared effect size. It may be slightly negative for the null effect; the raw
                value is reported.
            - 'k': The number of observed groups (the distinct codes).
            - 'n': The number of observations.

        The degenerate inputs (the single group, K = 1; the zero variance) return 0.0 for both effect sizes.

    Raises:
        ValueError: When the number of groups exceeds the number of observations (the K > N case, unreachable) or
            when `groups` and `values` have different lengths.
    """
    g = np.asarray(groups)
    y = np.asarray(values, dtype=np.float64).ravel()
    n = int(y.shape[0])
    if g.shape[0] != n:
        raise ValueError(f"groups ({g.shape[0]}) and values ({n}) length mismatch")
    unique, inv = np.unique(g, return_inverse=True)
    k = int(unique.shape[0])
    if k > n:
        raise ValueError(f"K > N (the {k} groups exceed the {n} observations) — unreachable")
    if k == 1:
        # The degenerate (the single group): by convention.
        return {'eta2': 0.0, 'omega2': 0.0, 'k': k, 'n': n}
    ybar = float(y.mean())
    ss_tot = float(((y - ybar) ** 2).sum())
    group_sums = np.bincount(inv, weights=y)
    group_counts = np.bincount(inv)
    group_means = group_sums / group_counts
    ss_eff = float((group_counts * (group_means - ybar) ** 2).sum())
    ss_err = ss_tot - ss_eff
    eta2 = (ss_eff / ss_tot) if ss_tot > 0 else 0.0
    ms_err = (ss_err / (n - k)) if n > k else 0.0
    denom = ss_tot + ms_err
    omega2 = ((ss_eff - (k - 1) * ms_err) / denom if denom > 0 else 0.0)
    return {'eta2': float(eta2), 'omega2': float(omega2), 'k': k, 'n': n}


def _kl_divergence(p, q) -> float:
    """
    Calculate the Kullback-Leibler divergence KL(p || q) between two categorical distributions.

    This function measures how much information is lost when the ideal distribution approximates the DB
    distribution, in nats. The 0-log-0 convention applies: the terms where p(i) = 0 vanish.

    Args:
        p (npt.ArrayLike): The DB distribution (the probabilities, summing to 1), one element per category.
        q (npt.ArrayLike): The ideal distribution (the probabilities, summing to 1), one element per category.

    Returns:
        float: The divergence in nats. It is 0.0 when the two distributions are equal, and float('inf') when `p`
            has support where `q` is zero (the DB has a code the ideal never shows — the infinite divergence).
    """
    p = np.asarray(p, dtype=np.float64).ravel()
    q = np.asarray(q, dtype=np.float64).ravel()
    mask = p > 0
    if bool(np.any(mask & (q <= 0))):
        return float('inf')
    return float((p[mask] * np.log(p[mask] / q[mask])).sum())


def _total_variation(p, q) -> float:
    """
    Calculate the total variation distance TV(p, q) between two categorical distributions.

    This function measures how different the two distributions are on the robust 0.0 to 1.0 scale: no logarithm,
    no 0/0 degenerate term.

    Args:
        p (npt.ArrayLike): The DB distribution (the probabilities, summing to 1), one element per category.
        q (npt.ArrayLike): The ideal distribution (the probabilities, summing to 1), one element per category.

    Returns:
        float: The total variation distance (0.5 * the sum of the absolute differences), in the 0.0 to 1.0 range.
    """
    p = np.asarray(p, dtype=np.float64).ravel()
    q = np.asarray(q, dtype=np.float64).ravel()
    return float(0.5 * np.abs(p - q).sum())


def _chi_square_goodness(observed, expected, min_expected=5) -> dict:
    """
    Run the chi-square goodness-of-fit test between the observed and the expected category counts.

    This function computes the chi-square statistic, its p-value, and the merged-tail count: the cells whose
    expected count falls below the `min_expected` threshold are merged into a single "other" bin before the test
    (the standard technique for the low-expected cells).

    Args:
        observed (npt.ArrayLike): The DB observed counts (the O_i), one element per cell.
        expected (npt.ArrayLike): The ideal expected counts (the E_i = the ideal frequency * N_DB), one element
            per cell.
        min_expected (float): The threshold for the merged tail (the default 5, the standard).

    Returns:
        dict[str, float | int]: A dictionary containing the following keys:
            - 'chi2': The chi-square test statistic.
            - 'p': The p-value (the scipy chi2.sf over the k - 1 degrees of freedom).
            - 'merged': The count of the cells merged into the "other" bin.

        The p-value is nan when the merged result has fewer than 2 cells (the degenerate, df < 1). When a cell
        shows O > 0 with E = 0 (the DB observes a code the ideal never shows), the statistic is +inf and the
        p-value is 0.0 — the total incompatibility, the merged tail would otherwise hide the root cause.
    """
    o = np.asarray(observed, dtype=np.float64).ravel()
    e = np.asarray(expected, dtype=np.float64).ravel()
    if o.shape[0] < 2:
        return {'chi2': 0.0, 'p': float('nan'), 'merged': 0}
    # The merged tail: the cells with E < min_expected are merged into the "other" bin (the sum).
    mask = e < min_expected
    n_merge = int(mask.sum())
    # The disjoint support: a cell with O > 0 but E = 0 (the DB observes a code the ideal never shows — the total
    # incompatibility, the chi-square is +inf, the p is 0, the KL is +inf — the three are aligned, the merged tail
    # would otherwise hide the root cause and divide by zero).
    if bool(np.any((o > 0) & (e == 0))):
        return {'chi2': float('inf'), 'p': 0.0, 'merged': n_merge}
    if n_merge > 0:
        other_o = float(o[mask].sum())
        other_e = float(e[mask].sum())
        keep = ~mask
        o = np.concatenate([o[keep], [other_o]])
        e = np.concatenate([e[keep], [other_e]])
    k = int(o.shape[0])
    chi2_stat = float(((o - e) ** 2 / e).sum())
    df = k - 1
    if df < 1:
        p_val = float('nan')
    else:
        p_val = float(_chi2.sf(chi2_stat, df))
    return {'chi2': chi2_stat, 'p': p_val, 'merged': n_merge}


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def hlp_anova_adherence(db_counts: dict[str | int, int | float],
                        ideal_counts: dict[str | int, int | float]) -> dict:
    """
    Calculate statistical adherence between the observed DB distribution and an ideal distribution.

    This function measures how closely the empirical data configuration aligns with a theoretical baseline by
    aligning both distributions over the union of their observed categories. It computes a fixed trio of
    statistical distances and goodness-of-fit metrics: Chi-square, Kullback-Leibler (KL) divergence, and Total
    Variation (TV) distance.

    Args:
        db_counts (dict[str | int, int | float]): The observed configuration counts from the database (e.g.,
            training positions), mapping codes to frequencies.
        ideal_counts (dict[str | int, int | float]): The target or corpus ideal distribution counts, mapping
            codes to standard frequencies.

    Returns:
        dict[str, float]: A dictionary containing the following keys:
            - 'chi2': The Chi-square goodness-of-fit test statistic.
            - 'p': The p-value resulting from the Chi-square test.
            - 'merged': The count of tail categories merged during the test.
            - 'kl': The Kullback-Leibler divergence (0-log-0 handled).
            - 'tv': The Total Variation distance (robust scale from 0.0 to 1.0).

            All values return float('nan') (except 'merged' which returns 0) if either input distribution is
            empty.
    """
    codes = sorted(set(db_counts) | set(ideal_counts))
    db = np.array([db_counts.get(c, 0) for c in codes], dtype=np.float64)
    ideal = np.array([ideal_counts.get(c, 0) for c in codes], dtype=np.float64)
    n_db = float(db.sum())
    n_ideal = float(ideal.sum())
    if n_db == 0 or n_ideal == 0:
        return {'chi2': float('nan'), 'p': float('nan'), 'merged': 0, 'kl': float('nan'), 'tv': float('nan')}
    p_db = db / n_db
    p_ideal = ideal / n_ideal
    tv = _total_variation(p_db, p_ideal)
    kl = _kl_divergence(p_db, p_ideal)
    expected = p_ideal * n_db
    g = _chi_square_goodness(db, expected)
    return {'chi2': g['chi2'], 'p': g['p'], 'merged': g['merged'], 'kl': kl, 'tv': tv}


def _compute_anova_lines(ctx) -> list:
    """
    Compute the per-sub-variable ANOVA report lines (the eta-squared / omega-squared section of the ANOVA report).

    This function runs the one-way ANOVA over every sub-variable of the feature set (the feature x instance
    pairs): the DB training set provides the per-position raw codes (the groups) and the continuous game values
    (the target) — the corpus is not needed. One INFO log line is emitted per sub-variable.

    Args:
        ctx (LMContext): The pipeline context (the feature set, the indexes, the game values, the event log).

    Returns:
        list: One row per sub-variable: (name, i, k, n, eta2, omega2), where name is the feature name, i the
            instance index, k the observed groups, n the observations, eta2 / omega2 the effect sizes.
    """
    anova_lines = []
    for (name, c0, c1, n_conf, n_inst) in ctx.feature_set.feature_blocks:
        for i in range(n_inst):
            groups = ctx.hlp_indexes.indexes[:, c0 + i]
            r = hlp_anova_eta_omega(groups, ctx.game_values)
            anova_lines.append((name, i, r['k'], r['n'], r['eta2'], r['omega2']))
            ctx.log_event(Relevance.INFO,
                          f"  ANOVA {name}[{i}]: eta2 {r['eta2']:.4f}, omega2 {r['omega2']:.4f} (K {r['k']})")
    return anova_lines


def _compute_adherence_lines(ctx) -> list | None:
    """
    Compute the per-sub-variable adherence report lines (the TV-descending adherence section of the ANOVA report).

    This function measures the adherence of every sub-variable: the DB configuration distribution (the observed
    codes of the training positions) vs the ideal corpus frequencies (the SU_ANALYSIS tables), sorted by the
    total variation distance descending, the top-N logged.

    The GRACEFUL DEGRADATION: when the SU_ANALYSIS level was disabled (no corpus in the context), the adherence
    is skipped with a log note and None is returned — the eta-squared / omega-squared runs (it does not need the
    corpus).

    Args:
        ctx (LMContext): The pipeline context (the feature set, the indexes, the su_analysis tables, the anova
            config, the event log).

    Returns:
        list | None: One row per sub-variable: (name, i, chi2, p, merged, kl, tv), sorted by the TV descending.
            None when the SU_ANALYSIS level was disabled (the graceful degradation).
    """
    tables = ctx.su_analysis_tables
    if tables is not None:
        cfg_anova = ctx.cfg.anova
        marginal = tables['marginal']
        ideal_lookup = {(nm, ii): dict(zip(cd.tolist(), ct.tolist())) for (nm, ii, _nc, cd, ct) in marginal}
        adherence_lines = []
        for (name, c0, c1, n_conf, n_inst) in ctx.feature_set.feature_blocks:
            for i in range(n_inst):
                groups = ctx.hlp_indexes.indexes[:, c0 + i]
                uniq, cnt = np.unique(groups, return_counts=True)
                db_counts = dict(zip(uniq.tolist(), cnt.tolist()))
                ideal_counts = ideal_lookup.get((name, i), {})
                a = hlp_anova_adherence(db_counts, ideal_counts)
                adherence_lines.append((name, i, a['chi2'], a['p'], a['merged'], a['kl'], a['tv']))
        adherence_lines.sort(key=lambda x: x[6], reverse=True)
        for (name, i, chi2, p, merged, kl, tv) in adherence_lines[:cfg_anova.top_k_adherence]:
            ctx.log_event(Relevance.INFO,
                          f"  Adherence {name}[{i}]: TV {tv:.4f}, KL {kl:.4f}, chi2 {chi2:.2f} "
                          f"(p {p:.2e}, merged {merged})")
        return adherence_lines
    ctx.log_event(Relevance.INFO, "  Adherence SKIPPED (the SU_ANALYSIS level was disabled — no corpus in the ctx).")
    return None


def hlp_anova_compute_analysis(ctx) -> tuple:
    """
    Run the ANOVA analysis over the training set and return the per-sub-variable results.

    This function executes the two analysis passes: the eta-squared / omega-squared per sub-variable and the
    adherence per sub-variable.

    The GRACEFUL DEGRADATION: the adherence lines are None when the corpus is absent (the SU_ANALYSIS level
    disabled) — the eta-squared / omega-squared runs.

    Args:
        ctx (LMContext): The pipeline context (the feature set, the indexes, the game values, the su_analysis
            tables, the event log).

    Returns:
        tuple: The (anova_lines, adherence_lines) pair: the per-sub-variable (name, i, k, n, eta2, omega2) rows,
            and the per-sub-variable adherence rows sorted by the TV descending (or None).
    """
    anova_lines = _compute_anova_lines(ctx)
    adherence_lines = _compute_adherence_lines(ctx)
    return anova_lines, adherence_lines


def hlp_anova_generate_report(ctx, anova_lines, adherence_lines) -> Path:
    """
    Generate the ANOVA report (the TXT file, the optional CSV) and return the report path.

    This function writes the per-sub-variable eta-squared / omega-squared section, the top-N most deviant
    features (the adherence, the TV descending), and the graceful-degradation note (when the adherence is
    skipped). The report is written to the anova dir_name under the context base_dir.

    Args:
        ctx (LMContext): The pipeline context (the base_dir, the anova config, the event log).
        anova_lines (list): The per-sub-variable (name, i, k, n, eta2, omega2) rows (the compute pass output).
        adherence_lines (list | None): The per-sub-variable adherence rows sorted by the TV descending, or None
            (the graceful degradation).

    Returns:
        Path: The path of the written TXT report. When the anova export_csv flag is set, the CSV (the anova.csv
            with the eta / omega + the adherence columns) is written beside it.
    """
    cfg_anova = ctx.cfg.anova
    lines = ["ANOVA REPORT", "=" * 40]
    lines.append(f"Sub-variables (the eta-squared / omega-squared): {len(anova_lines)}")
    for (name, i, k, n, eta2, omega2) in anova_lines:
        lines.append(f"  ANOVA {name} inst {i}: eta2 {eta2:.4f}, omega2 {omega2:.4f} (K {k}, N {n})")
    if adherence_lines is None:
        lines.append("Adherence: SKIPPED (the SU_ANALYSIS level was disabled — no corpus in the ctx).")
    else:
        lines.append(f"Top adherence (the TV descending, top {cfg_anova.top_k_adherence}):")
        for (name, i, chi2, p, merged, kl, tv) in adherence_lines:
            lines.append(f"  Adherence {name} inst {i}: TV {tv:.4f}, KL {kl:.4f}, chi2 {chi2:.2f} "
                         f"(p {p:.2e}, merged {merged})")
    report_path = Path(ctx.cfg.base_dir) / cfg_anova.dir_name / cfg_anova.report_file_name
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    ctx.log_event(Relevance.INFO, f"ANOVA report written: {report_path}.")
    if cfg_anova.export_csv:
        csv_path = report_path.parent / "anova.csv"
        with open(csv_path, 'w', newline='', encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(['type', 'feature', 'inst', 'eta2', 'omega2', 'k', 'tv', 'kl', 'chi2', 'p', 'merged'])
            for (name, i, k, n, eta2, omega2) in anova_lines:
                w.writerow(['anova', name, i, f"{eta2:.6f}", f"{omega2:.6f}", k, '', '', '', '', ''])
            if adherence_lines is not None:
                for (name, i, chi2, p, merged, kl, tv) in adherence_lines:
                    w.writerow(['adherence', name, i, '', '', '', f"{tv:.6f}", f"{kl:.6f}", f"{chi2:.6f}",
                                f"{p:.6e}", merged])
        ctx.log_event(Relevance.INFO, f"ANOVA CSV written: {csv_path}.")
    return report_path
