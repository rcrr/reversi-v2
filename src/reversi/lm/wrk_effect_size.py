#
# wrk_effect_size.py
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

"""
The EFFECT_SIZE worker (the I-017, the eta²/omega² + the
adherence, step 6, D-187): the one-way ANOVA effect sizes (the
eta²/omega² per sub-variable, the T13 kernel) + the adherence
(the fixed trio — the chi-square + the KL + the TV, the T14
kernel — the DB configuration distribution vs the ideal corpus
frequencies). NO cache (a diagnostic; the recompute is seconds).
The GRACEFUL DEGRADATION: if the SU_ANALYSIS level was
disabled (no corpus in the ctx), the adherence is skipped with
a log note; the eta²/omega² runs (it does not need the corpus).
The D-060 semantics.
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

from typing import TYPE_CHECKING

from pydantic import validate_call, ConfigDict

from reversi.tools.state_machine import Worker, Relevance
from reversi.lm.hlp_feature_analysis import (
    adherence, anova_eta_omega)

if TYPE_CHECKING:
    from reversi.lm.logistic_model import LMContext


__all__ = ['wrk_effect_size']


def _feature_blocks(fset):
    """The per-feature column blocks (the fset.features order —
    the documented column layout: the intercept, then the
    mobilities, then the patterns): (name, col_start, col_end,
    n_conf, n_inst) over the non-intercept features."""
    blocks = []
    col = 1 if (fset.intercept is not None) else 0
    for f in fset.features:
        if f.category in (0, 'intercept') or f.name == 'INTERCEPT':
            continue
        blocks.append((f.name, col, col + int(f.n_instances),
                       int(f.n_configurations), int(f.n_instances)))
        col += int(f.n_instances)
    return blocks


def _write_report(ctx, anova_lines, adherence_lines) -> Path:
    """The TXT report (dir_name under base_dir, the PlotConfig
    pattern): the per-sub-variable eta²/omega² + the top-N most
    deviant features (the adherence, the TV descending) + the
    graceful-degradation note (when the adherence is skipped).
    The optional CSV (the export_csv flag)."""
    cfg_es = ctx.cfg.effect_size
    lines = ["EFFECT_SIZE REPORT", "=" * 40]
    lines.append(f"Sub-variables (the eta-squared / omega-squared): "
                 f"{len(anova_lines)}")
    for (name, i, k, n, eta2, omega2) in anova_lines:
        lines.append(f"  ANOVA {name} inst {i}: eta2 {eta2:.4f}, "
                     f"omega2 {omega2:.4f} (K {k}, N {n})")
    if adherence_lines is None:
        lines.append("Adherence: SKIPPED (the SU_ANALYSIS "
                     "level was disabled — no corpus in the ctx).")
    else:
        lines.append(f"Top adherence (the TV descending, "
                     f"top {cfg_es.top_k_adherence}):")
        for (name, i, chi2, p, merged, kl, tv) in adherence_lines:
            lines.append(f"  Adherence {name} inst {i}: TV {tv:.4f}, "
                         f"KL {kl:.4f}, chi2 {chi2:.2f} "
                         f"(p {p:.2e}, merged {merged})")
    report_path = Path(ctx.cfg.base_dir) / cfg_es.dir_name / \
        cfg_es.report_file_name
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    ctx.log_event(Relevance.INFO,
                  f"EFFECT_SIZE report written: {report_path}.")
    if cfg_es.export_csv:
        csv_path = report_path.parent / "effect_size.csv"
        with open(csv_path, 'w', newline='', encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(['type', 'feature', 'inst', 'eta2', 'omega2',
                        'k', 'tv', 'kl', 'chi2', 'p', 'merged'])
            for (name, i, k, n, eta2, omega2) in anova_lines:
                w.writerow(['anova', name, i, f"{eta2:.6f}",
                            f"{omega2:.6f}", k, '', '', '', '', ''])
            if adherence_lines is not None:
                for (name, i, chi2, p, merged, kl, tv) in adherence_lines:
                    w.writerow(['adherence', name, i, '', '', '',
                                f"{tv:.6f}", f"{kl:.6f}",
                                f"{chi2:.6f}", f"{p:.6e}", merged])
        ctx.log_event(Relevance.INFO,
                      f"EFFECT_SIZE CSV written: {csv_path}.")
    return report_path


def _up(ctx: "LMContext") -> None:
    cfg_es = ctx.cfg.effect_size
    if not cfg_es.enable:
        ctx.log_event(Relevance.INFO,
                      "EFFECT_SIZE disabled (enable: false) — no-op.")
        return
    fset = ctx.feature_set
    blocks = _feature_blocks(fset)
    # The DB training set: the per-position raw codes (the groups)
    # + the continuous game values (the target).
    X = ctx.hlp_indexes.indexes
    y = ctx.game_values
    # The eta²/omega² per sub-variable (the one-way ANOVA, the
    # T13 kernel — it does not need the corpus).
    anova_lines = []
    for (name, c0, c1, n_conf, n_inst) in blocks:
        for i in range(n_inst):
            groups = X[:, c0 + i]
            r = anova_eta_omega(groups, y)
            anova_lines.append((name, i, r['k'], r['n'],
                                r['eta2'], r['omega2']))
            ctx.log_event(Relevance.INFO,
                          f"  ANOVA {name}[{i}]: eta2 {r['eta2']:.4f}, "
                          f"omega2 {r['omega2']:.4f} (K {r['k']})")
    # The adherence (c) per sub-variable (the T14 kernel) — the
    # GRACEFUL DEGRADATION: if the SU_ANALYSIS level was
    # disabled (no corpus in the ctx), the adherence is skipped
    # with a log note; the eta²/omega² runs.
    tables = ctx.su_analysis_tables
    adherence_lines = None
    if tables is not None:
        marginal = tables['marginal']
        ideal_lookup = {(nm, ii): dict(zip(cd.tolist(), ct.tolist()))
                        for (nm, ii, _nc, cd, ct) in marginal}
        adherence_lines = []
        for (name, c0, c1, n_conf, n_inst) in blocks:
            for i in range(n_inst):
                groups = X[:, c0 + i]
                uniq, cnt = np.unique(groups, return_counts=True)
                db_counts = dict(zip(uniq.tolist(), cnt.tolist()))
                ideal_counts = ideal_lookup.get((name, i), {})
                a = adherence(db_counts, ideal_counts)
                adherence_lines.append((name, i, a['chi2'], a['p'],
                                        a['merged'], a['kl'], a['tv']))
        adherence_lines.sort(key=lambda x: x[6], reverse=True)
        for (name, i, chi2, p, merged, kl, tv) in \
                adherence_lines[:cfg_es.top_k_adherence]:
            ctx.log_event(Relevance.INFO,
                          f"  Adherence {name}[{i}]: TV {tv:.4f}, "
                          f"KL {kl:.4f}, chi2 {chi2:.2f} "
                          f"(p {p:.2e}, merged {merged})")
    else:
        ctx.log_event(Relevance.INFO,
                      "  Adherence SKIPPED (the SU_ANALYSIS "
                      "level was disabled — no corpus in the ctx).")
    _write_report(ctx, anova_lines, adherence_lines)


def _down(ctx: "LMContext") -> None:
    # The EFFECT_SIZE worker publishes nothing on the ctx (a
    # diagnostic); the down is a no-op (the D-060 recovery is
    # trivially satisfied).
    ctx.log_event(Relevance.INFO, "EFFECT_SIZE down (no-op).")


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def wrk_effect_size() -> Worker:
    """Factory function that returns the EFFECT_SIZE worker
    instance."""
    return Worker("EFFECT_SIZE", _up, _down)
