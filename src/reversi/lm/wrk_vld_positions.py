#
# wrk_vld_positions.py
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

import numpy as np

from typing import TYPE_CHECKING

from pydantic import validate_call, ConfigDict

from reversi.tools.state_machine import Worker, Relevance
from reversi.regab import (
    regab_count_position_overlap,
    regab_load_data_set_from_file,
    regab_store_data_set_to_file
)
from reversi.tools.cache_manager import cache_manager_load_or_compute
from reversi.lm.wrk_positions import wrk_positions_extract_and_prepare, wrk_positions_is_cache_consistent

if TYPE_CHECKING:
    from reversi.lm.logistic_model import LMContext



__all__ = ['wrk_vld_positions']



def _up(ctx: "LMContext") -> None:
    """
    Run the VLD_POSITIONS level: the load-or-compute cache flow (the REUSED wrk_positions compute
    path, the validation bid/status overrides), the population stats, and the independence trace
    (log only).
    """
    ctx.log_event(Relevance.INFO, "Loading validation game positions...")

    vld_cfg = ctx.cfg.validation_data_set

    # Note: the vld query's ec is the ROOT empty_count — it no longer inherits from regab_data_set.
    # The ValidationDataSetConfig declares only bid and status; the shared ec gates both the
    # extraction and the cache consistency check.

    # Execute the abstracted pipeline.
    cache_hit, vld_rds, vld_rds_checksum = cache_manager_load_or_compute(
        cache_path  = ctx.get_cache_file_full_path_for_current_level(),
        is_allowed  = ctx.use_cache,
        load_fn     = lambda path: regab_load_data_set_from_file(path, checksum=False),
        store_fn    = regab_store_data_set_to_file,
        validate_fn = lambda cached_vld_rds: (
            wrk_positions_is_cache_consistent(ctx, cached_vld_rds, bid=vld_cfg.bid, status=vld_cfg.status)),
        compute_fn  = lambda: wrk_positions_extract_and_prepare(ctx, bid=vld_cfg.bid, status=vld_cfg.status),
        logger_fn   = ctx.log_event
    )

    if cache_hit:
        # The cached file holds the post-policy data set (the dedup is applied in the compute flow),
        # so the duplicate count is reported from the stored content.
        ctx.log_event(Relevance.INFO,
                      f"Duplicate game positions (key: mover, opponent): [TOTAL: {len(vld_rds.df_mogv):,}] — "
                      f"data set loaded from cache (regab_allow_duplicate: {ctx.cfg.regab_allow_duplicate}).")

    # Post-processing (unrelated to caching logic).
    vld_positions, vld_game_values = vld_rds.generate_positions_and_game_values()
    ctx.vld_positions = vld_positions
    ctx.vld_game_values = vld_game_values
    ctx.vld_rds_checksum = vld_rds_checksum

    ctx.log_event(Relevance.INFO, f"Regab validation data set object checksum (vld_rds_checksum): {vld_rds_checksum}.")
    ctx.log_event(Relevance.INFO, "Model attributes vld_positions, vld_game_values and vld_rds_checksum have been set.")

    count = len(vld_game_values)
    mean = np.mean(vld_game_values)
    std_dev = np.std(vld_game_values)
    variance = np.var(vld_game_values)
    ctx.log_event(Relevance.INFO,
                  f"Statistical properties of population for validation: [COUNT: {count:,}], [MEAN: {mean:.2f}], "
                  f"[STD: {std_dev:.2f}], [VARIANCE: {variance:.2f}].")

    ctx.vld_pop_stats = {
        'count': count,
        'mean': mean,
        'std_dev': std_dev,
        'variance': variance
    }

    # The validation independence check: how many validation records are also present in the
    # training data set. LOG ONLY, no action (Roberto's ruling: a threshold/quality parameter family
    # — max allowed overlap %, minimum validation size, ... — is explicitly out of scope; we keep
    # the trace).
    overlap = regab_count_position_overlap(ctx.positions, ctx.vld_positions)
    overlap_pct = 100.0 * overlap / count if count else 0.0
    ctx.log_event(Relevance.INFO,
                  f"Validation independence check: [OVERLAP: {overlap:,} of {count:,} validation records], "
                  f"[PERCENT: {overlap_pct:.2f}%] — records present in both the validation and the training "
                  f"data sets (log only, no action).")

    return


def _down(ctx: "LMContext") -> None:
    """Clear the four vld attributes (the failure recovery)."""
    ctx.log_event(Relevance.INFO,
                  "Clearing validation game positions vld_positions, vld_game_values and vld_rds_checksum "
                  "attributes.")
    ctx.vld_positions = None
    ctx.vld_game_values = None
    ctx.vld_rds_checksum = None
    ctx.vld_pop_stats = None

    return


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def wrk_vld_positions() -> Worker:
    """Return the VLD_POSITIONS worker instance."""
    return Worker("VLD_POSITIONS", _up, _down)
