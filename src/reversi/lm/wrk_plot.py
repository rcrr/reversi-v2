#
# wrk_plot.py
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
# The PLOT level (D-149): the 17th level, after CLIENT_CHECK. It
# writes the run's matplotlib diagnostic figures (hlp_plot) to the
# configured plots directory.
#
# Pilot (Roberto's ruling, D-149): the WHITELIST of plot names in
# the config's plot section decides what is generated — a listed
# name is written, an unlisted name is skipped, an empty list makes
# the level a no-op. The plot.enable master switch dominates: false
# means "do nothing" even when names are listed.
#
# No cache file (the 8th non-cache level, as CLIENT_CHECK — the
# rlmwf_16 slot stays unused): the figures are derived artifacts,
# regenerated on every up-move (an idempotent overwrite).

from __future__ import annotations

from pathlib import Path

from pydantic import validate_call, ConfigDict

from typing import TYPE_CHECKING

from reversi.tools.state_machine import Worker, Relevance
from reversi.lm.hlp_plot import (PLOT_BUILDERS, collect_plot_data,
                                  save_figure, close_figure)

if TYPE_CHECKING:
    from reversi.lm.logistic_model import LMContext



__all__ = ['wrk_plot']



def _up(ctx: "LMContext") -> None:
    plot_cfg = ctx.cfg.plot

    # 1. The pilot (D-149): the master switch first, then the
    #    whitelist. Either empty path is a clean no-op (log only).
    if not plot_cfg.enable:
        ctx.log_event(Relevance.INFO,
                      "PLOT skipped: plot.enable is false.")
        return
    if not plot_cfg.plots:
        ctx.log_event(Relevance.INFO,
                      "PLOT skipped: no plot names requested.")
        return

    ctx.log_event(Relevance.INFO,
                  f"Generating {len(plot_cfg.plots)} plot(s)...")

    # 2. The figures' data (the training w_dense pass + the
    #    validation forward pass, hlp_plot.collect_plot_data).
    data = collect_plot_data(ctx)

    # 3. The plots directory: an ABSOLUTE dir_name is used as-is (it
    #    may live outside base_dir), a relative one resolves under
    #    base_dir (the "plots" default).
    dir_name = Path(plot_cfg.dir_name)
    plot_dir = dir_name if dir_name.is_absolute() else (ctx.cfg.base_dir / dir_name)
    plot_dir.mkdir(parents=True, exist_ok=True)

    formats = tuple(f.strip() for f in plot_cfg.format.split(","))

    # 4. One figure per whitelisted name, saved in every configured
    #    format (the "pdf,png" pair writes both).
    for name in plot_cfg.plots:
        fig = PLOT_BUILDERS[name](data, ctx.cfg.name)
        paths = []
        for fmt in formats:
            p = plot_dir / f"{name}.{fmt}"
            save_figure(fig, p, fmt, plot_cfg.dpi)
            paths.append(str(p))
        close_figure(fig)
        ctx.log_event(Relevance.INFO,
                      f"Plot '{name}' saved: {', '.join(paths)}")

    ctx.log_event(Relevance.INFO,
                  f"PLOT done: {len(plot_cfg.plots)} plot(s) "
                  f"written to {plot_dir}.")


def _down(ctx: "LMContext") -> None:
    ctx.log_event(Relevance.INFO, "Clearing plot attributes...")
    # Nothing to clear from context: the worker is stateless (the
    # figures are built and closed locally on every up-move, as the
    # SAVE and CLIENT_CHECK workers).


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def wrk_plot() -> Worker:
    """Factory function that returns the PLOT worker instance."""
    return Worker("PLOT", _up, _down)
