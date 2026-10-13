#
# wrk_wmaps.py
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
from reversi.lm.hlp_wmaps import (hlp_wmaps_load_from_file,
                             hlp_wmaps_store_to_file,
                             hlp_wmaps_compute,
                             hlp_wmaps_is_cache_consistent)
from reversi.tools.cache_manager import cache_manager_load_or_compute

if TYPE_CHECKING:
    from reversi.lm.logistic_model import LMContext



__all__ = ['wrk_wmaps']



def _up(ctx: "LMContext") -> None:
    """
    Run the WMAPS level: the 4-step load-or-compute of the hlp_wmaps object, spread across the 6
    context arrays (feature_w_ranges, iwmap_feature_offset, iwmap, wmap, wmap_fallback, w) + the
    data checksum.
    """
    ctx.log_event(Relevance.INFO, "Computing weight maps (WMAPS) for the feature set...")

    cache_hit, wmaps_obj, wmaps_obj_checksum = cache_manager_load_or_compute(
        cache_path  = ctx.get_cache_file_full_path_for_current_level(),
        is_allowed  = ctx.use_cache,
        load_fn     = lambda path: hlp_wmaps_load_from_file(path, checksum=False),
        store_fn    = hlp_wmaps_store_to_file,
        validate_fn = lambda cached_wmaps: hlp_wmaps_is_cache_consistent(ctx, cached_wmaps),
        compute_fn  = lambda: hlp_wmaps_compute(ctx),
        logger_fn   = ctx.log_event
    )

    # Populate the 6 separate attributes in the context
    ctx.feature_w_ranges = wmaps_obj.feature_w_ranges
    ctx.iwmap_feature_offset = wmaps_obj.iwmap_feature_offset
    ctx.iwmap = wmaps_obj.iwmap
    ctx.wmap = wmaps_obj.wmap
    ctx.wmap_fallback = wmaps_obj.wmap_fallback
    ctx.w = wmaps_obj.w
    ctx.log_event(Relevance.INFO,
                  "Model attributes feature_w_ranges, iwmap_feature_offset, iwmap, wmap, "
                  "wmap_fallback, w have been set.")
    ctx.log_event(Relevance.INFO, f"WMAPS computed/loaded. Total weights (W): {len(ctx.w)}")

    ctx.log_event(Relevance.INFO, f"Wmaps object checksum (wmaps_obj_checksum): {wmaps_obj_checksum}.")
    ctx.wmaps_obj_checksum = wmaps_obj_checksum


def _down(ctx: "LMContext") -> None:
    """Clear all 7 WMAPS context attributes to None (the 6 arrays + the data checksum)."""
    ctx.log_event(Relevance.INFO, "Clearing WMAPS and W attributes...")
    ctx.feature_w_ranges = None
    ctx.iwmap_feature_offset = None
    ctx.iwmap = None
    ctx.wmap = None
    ctx.wmap_fallback = None
    ctx.w = None
    ctx.wmaps_obj_checksum = None


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def wrk_wmaps() -> Worker:
    """Return the WMAPS worker instance."""
    return Worker("WMAPS", _up, _down)
