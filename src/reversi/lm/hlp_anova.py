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
from scipy.stats import chi2 as _chi2

from reversi.tools.state_machine import Relevance

# The ANOVA family (the D-298 split from the shared data plane — the SU
# kernels moved to hlp_su_analysis): the 2 PURE-MATH kernels (the ANOVA
# effect sizes + the adherence trio, NO DB, NO positions) + the 2 FLOW
# functions (the wrk/hlp boundary, the D-315 move from wrk_anova: the
# compute + the report) + the private helpers (the 3 trio kernels + the
# 2 per-sub-variable line builders).
__all__ = ['anova_eta_omega', 'adherence',
           'hlp_anova_compute_analysis', 'hlp_anova_generate_report']


def anova_eta_omega(groups, values) -> dict:
    """
    The one-way ANOVA effect sizes (the ANOVA level, the design section 3.5): the observed codes as the groups (K), the
    target = the continuous training game values (N).

      SS_tot = sum (y - ybar)^2
      SS_eff = sum_g n_g (y_g - ybar)^2
      SS_err = SS_tot - SS_eff
      eta²   = SS_eff / SS_tot
      omega² = (SS_eff - (K - 1) MS_err) / (SS_tot + MS_err)
      MS_err = SS_err / (N - K)

    Guards: K = 1 -> eta² = omega² = 0 (degenerate, by convention); K > N -> ValueError (unreachable). omega² may be
    slightly negative (the null effect): the raw value is reported. eta² is the biased sample share (up with high K);
    omega² is the unbiased population estimate — the pair is reported together.

    Args:
      groups: the group assignment per observation (the observed codes; length N). Any hashable values.
      values: the continuous target values (length N).

    Returns:
      {'eta2', 'omega2', 'k', 'n'}.

    Raises:
      ValueError: K > N (unreachable) or the length mismatch.
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
    The KL divergence KL(p || q) in nats, the 0-log-0 convention (the p(i) = 0 terms vanish). +inf if p(i) > 0 and
    q(i) = 0 (the DB has a code the ideal never shows — the infinite divergence).

    Args:
      p: the DB distribution (the probabilities, sum 1).
      q: the ideal distribution (the probabilities, sum 1).
    """
    p = np.asarray(p, dtype=np.float64).ravel()
    q = np.asarray(q, dtype=np.float64).ravel()
    mask = p > 0
    if bool(np.any(mask & (q <= 0))):
        return float('inf')
    return float((p[mask] * np.log(p[mask] / q[mask])).sum())


def _total_variation(p, q) -> float:
    """
    The total variation distance TV(p, q) = 0.5 * sum |p - q|, in [0, 1] (the robust "how different" number, no log,
    no 0/0).

    Args:
      p: the DB distribution (the probabilities, sum 1).
      q: the ideal distribution (the probabilities, sum 1).
    """
    p = np.asarray(p, dtype=np.float64).ravel()
    q = np.asarray(q, dtype=np.float64).ravel()
    return float(0.5 * np.abs(p - q).sum())


def _chi_square_goodness(observed, expected, min_expected=5) -> dict:
    """
    The chi-square goodness-of-fit: the statistic sum (O - E)^2 / E, the p-value (the scipy chi2.sf, the (k - 1) df),
    the merged tail (the low-expected cells, E < min_expected, merged into an "other" bin) + the merge count (the
    standard technique).

    Args:
      observed: the DB observed counts (the O_i, one per cell).
      expected: the ideal expected counts (the E_i = the ideal frequency * N_DB, one per cell).
      min_expected: the threshold for the merged tail (the default 5, the standard).

    Returns:
      {'chi2', 'p', 'merged'} (the statistic, the p-value, the merge count). The p-value is nan if the merged result
      has fewer than 2 cells (the degenerate, df < 1).
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


def adherence(db_counts, ideal_counts) -> dict:
    """
    The adherence (c) (the ANOVA level, the design section 3.5): the DB configuration distribution (the observed
    codes of the training positions) vs the ideal distribution (the corpus frequencies, normalized). The fixed trio
    (no config whitelist): the chi-square goodness-of-fit (the p-value + the merged-tail count), the KL divergence
    (the 0-log-0), the total variation distance (the 0..1 "how different" number, robust). The two are aligned over
    the union of the observed codes (the missing side is 0).

    Args:
      db_counts: the DB observed code counts, a dict {code: count} (the training positions).
      ideal_counts: the ideal (corpus) code counts, a dict {code: count} (the corpus frequencies).

    Returns:
      {'chi2', 'p', 'merged', 'kl', 'tv'}. The values are nan if either distribution is empty.
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
    """The eta²/omega² per sub-variable (the one-way ANOVA — it does not need the corpus): the DB training set is the
    per-position raw codes (the groups) + the continuous game values (the target)."""
    anova_lines = []
    for (name, c0, c1, n_conf, n_inst) in ctx.feature_set.feature_blocks:
        for i in range(n_inst):
            groups = ctx.hlp_indexes.indexes[:, c0 + i]
            r = anova_eta_omega(groups, ctx.game_values)
            anova_lines.append((name, i, r['k'], r['n'], r['eta2'], r['omega2']))
            ctx.log_event(Relevance.INFO,
                          f"  ANOVA {name}[{i}]: eta2 {r['eta2']:.4f}, omega2 {r['omega2']:.4f} (K {r['k']})")
    return anova_lines


def _compute_adherence_lines(ctx) -> list | None:
    """The adherence per sub-variable (the DB configuration distribution vs the ideal corpus frequencies, the TV
    descending). The GRACEFUL DEGRADATION: if the SU_ANALYSIS level was disabled (no corpus in the ctx), the adherence
    is skipped with a log note (None is returned); the eta²/omega² runs (it does not need the corpus)."""
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
                a = adherence(db_counts, ideal_counts)
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
    """The ANOVA analysis (the two passes over the training set): the eta²/omega² per sub-variable + the adherence
    per sub-variable (the GRACEFUL DEGRADATION: None when the corpus is absent, the SU_ANALYSIS level disabled).

    Returns:
      (anova_lines, adherence_lines): the per-sub-variable (name, i, k, n, eta2, omega2) rows, and the
      per-sub-variable adherence rows sorted by the TV descending (or None).
    """
    anova_lines = _compute_anova_lines(ctx)
    adherence_lines = _compute_adherence_lines(ctx)
    return anova_lines, adherence_lines


def hlp_anova_generate_report(ctx, anova_lines, adherence_lines) -> Path:
    """The TXT report (dir_name under base_dir, the PlotConfig pattern): the per-sub-variable eta²/omega² + the top-N
    most deviant features (the adherence, the TV descending) + the graceful-degradation note (when the adherence is
    skipped). The optional CSV (the export_csv flag)."""
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
