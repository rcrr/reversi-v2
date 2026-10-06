#
# wrk_anova.py
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

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import validate_call, ConfigDict

from reversi.tools.state_machine import Worker, Relevance
from reversi.lm.hlp_anova import hlp_anova_compute_analysis, hlp_anova_generate_report

if TYPE_CHECKING:
    from reversi.lm.logistic_model import LMContext


__all__ = ['wrk_anova']


def _up(ctx: "LMContext") -> None:
    """
    Run the ANOVA level: the per-sub-variable effect sizes (eta²/omega²) + the adherence (the
    graceful-degradation skip when the SU_ANALYSIS corpus is absent) and the report — a no-op with
    the opt-in log when anova.enable is false.
    """
    if not ctx.cfg.anova.enable:
        ctx.log_event(Relevance.INFO, "ANOVA disabled (enable: false) — no-op.")
        return
    anova_lines, adherence_lines = hlp_anova_compute_analysis(ctx)
    hlp_anova_generate_report(ctx, anova_lines, adherence_lines)


def _down(ctx: "LMContext") -> None:
    """No-op (the ANOVA worker publishes nothing on the ctx)."""
    ctx.log_event(Relevance.INFO, "ANOVA down (no-op).")


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def wrk_anova() -> Worker:
    """Return the ANOVA worker instance."""
    return Worker("ANOVA", _up, _down)
