#
# wrk_gradient.py
#
# This file is part of the reversi program
# http://github.com/rcrr/reversi-v2
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
from reversi.lm.hlp_gradient import hlp_gradient_compute

if TYPE_CHECKING:
    from reversi.lm.logistic_model import LMContext



__all__ = ['wrk_gradient']



def _up(ctx: "LMContext") -> None:
    """
    Run the GRADIENT level: build the loss/gradient closure via hlp_gradient_compute, and publish it
    on the context (ctx.fg), with the high_performance flag + the hi_perf_blocks count.
    """
    ctx.log_event(Relevance.INFO, "Building gradient and loss function (fg)...")

    # GRADIENT building is a closure generation, very fast. No cache needed.
    high_performance = ctx.cfg.optimization.high_performance_fg
    hi_perf_blocks = ctx.cfg.optimization.hi_perf_blocks
    ctx.fg = hlp_gradient_compute(
        ctx, high_performance=high_performance, hi_perf_blocks=hi_perf_blocks)

    ctx.log_event(Relevance.INFO,
                  f"Gradient function generated (high_performance: {high_performance}).")


def _down(ctx: "LMContext") -> None:
    """Clear the gradient/loss closure published on the context (ctx.fg)."""
    ctx.log_event(Relevance.INFO, "Clearing gradient function...")
    ctx.fg = None


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def wrk_gradient() -> Worker:
    """Return the GRADIENT worker instance."""
    return Worker("GRADIENT", _up, _down)
