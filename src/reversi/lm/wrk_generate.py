#
# wrk_generate.py
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
from reversi.lm.hlp_generate import (compute_w_dense,
                                hlp_generate_store_to_file,
                                hlp_generate_load_from_file,
                                hlp_generate_is_cache_consistent)
from reversi.tools.cache_manager import cache_manager_load_or_compute

if TYPE_CHECKING:
    from reversi.lm.logistic_model import LMContext



__all__ = ['wrk_generate']



def _up(ctx: "LMContext") -> None:
    """
    Run the GENERATE level: the 7-kwargs cache load-or-compute for the dense weight vector, and
    publish it on the context (w_dense + its data checksum).
    """
    ctx.log_event(Relevance.INFO, "Generating dense weight vector (w_dense) for inference...")

    cache_hit, dense_obj, dense_w_checksum = cache_manager_load_or_compute(
        cache_path  = ctx.get_cache_file_full_path_for_current_level(),
        is_allowed  = ctx.use_cache,
        load_fn     = hlp_generate_load_from_file,
        store_fn    = hlp_generate_store_to_file,
        validate_fn = lambda cached_dw: hlp_generate_is_cache_consistent(ctx, cached_dw),
        compute_fn  = lambda: compute_w_dense(ctx),
        logger_fn   = ctx.log_event
    )

    ctx.w_dense = dense_obj.w_dense
    ctx.log_event(Relevance.INFO,
                  f"Dense weight vector generated/loaded. Shape: {ctx.w_dense.shape}")

    ctx.log_event(Relevance.INFO, f"Dense weight vector (dense_w_checksum): {dense_w_checksum}.")
    ctx.dense_w_checksum = dense_w_checksum


def _down(ctx: "LMContext") -> None:
    """Clear both context attributes (the dense weight vector + the data checksum)."""
    ctx.log_event(Relevance.INFO, "Clearing dense weight vector...")
    ctx.w_dense = None
    ctx.dense_w_checksum = None


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def wrk_generate() -> Worker:
    """Return the GENERATE worker instance."""
    return Worker("GENERATE", _up, _down)
