#
# wrk_positions.py
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

import numpy as np

from typing import TYPE_CHECKING

from pydantic import validate_call, ConfigDict

from reversi.tools.state_machine import Worker, Relevance
from reversi.regab import (
    RegabDataSet, 
    RegabDBConnection, 
    regab_extract_data_set_from_db,
    regab_load_data_set_from_file, 
    regab_store_data_set_to_file
)
from reversi.tools.cache_manager import cache_manager_load_or_compute

if TYPE_CHECKING:
    from reversi.lm.logistic_model import LMContext



__all__ = ['wrk_positions', 'load_from_db', 'is_cache_consistent']



def _up(ctx: "LMContext") -> None:
    ctx.log_event(Relevance.INFO, "Loading training game positions...")

    # Execute the abstracted pipeline.
    cache_hit, rds, rds_checksum = cache_manager_load_or_compute(
        cache_path  = ctx.get_cache_file_full_path_for_current_level(),
        is_allowed  = ctx.use_cache,
        load_fn     = lambda path: regab_load_data_set_from_file(path, checksum=False),
        store_fn    = regab_store_data_set_to_file,
        validate_fn = lambda cached_rds: is_cache_consistent(ctx, cached_rds),
        compute_fn  = lambda: load_from_db(ctx),
        logger_fn   = ctx.log_event
    )

    # Post-processing (unrelated to caching logic).
    positions, game_values = rds.generate_positions_and_game_values()
    ctx.positions = positions
    ctx.game_values = game_values
    ctx.rds_checksum = rds_checksum

    ctx.log_event(Relevance.INFO, f"Regab data set object checksum (rds_checksum): {rds_checksum}.")
    ctx.log_event(Relevance.INFO, "Model attributes positions, game_values and rds_checksum have been set.")

    count = len(game_values)
    mean = np.mean(game_values)
    std_dev = np.std(game_values)
    variance = np.var(game_values)
    ctx.log_event(Relevance.INFO, f"Statistical properties of population for training: [COUNT: {count:,}], [MEAN: {mean:.2f}], [STD: {std_dev:.2f}], [VARIANCE: {variance:.2f}].")

    ctx.training_pop_stats = {
        'count': count,
        'mean': mean,
        'std_dev': std_dev,
        'variance': variance
    }

    return


def _down(ctx: "LMContext") -> None:
    ctx.log_event(Relevance.INFO, "Clearing training game positions, game_values and rds_checksum attributes.")
    ctx.positions = None
    ctx.game_values = None
    ctx.rds_checksum = None
    ctx.training_pop_stats = None

    return


def is_cache_consistent(ctx: "LMContext", rds: RegabDataSet, *, bid=None, status=None) -> bool:
    """Compare live configuration with cached dataset metadata."""
    
    # 1. Check DB Connection parameters
    cfg_conn = ctx.cfg.regab_data_set.regab_db_connection
    cache_conn = rds.rc
    
    cfg_conn_data = (cfg_conn.dbname, cfg_conn.user, cfg_conn.host, cfg_conn.port)
    cache_conn_data = (cache_conn.dbname, cache_conn.user, cache_conn.host, int(cache_conn.port))
    
    is_conn_consistent = cfg_conn_data == cache_conn_data

    # 2. Check DB Query parameters
    cfg_query = ctx.cfg.regab_data_set
    if bid is None:
        bid = cfg_query.bid
    if status is None:
        status = cfg_query.status
    ec = cfg_query.ec
    cache_query = rds
    
    cfg_query_data = (bid, status, ec)
    cache_query_data = (cache_query.bid, cache_query.status, cache_query.ec)
    
    is_query_consistent = cfg_query_data == cache_query_data

    is_cache_consistent = is_conn_consistent and is_query_consistent
    ctx.log_event(Relevance.DEBUG, f"is_cache_consistent = {is_cache_consistent}.")

    # Log details only if inconsistencies are found (avoids building strings for no reason)
    if not is_conn_consistent:
        msg_conn = (
            f"DB Connection mismatch:\n"
            f"  cfg.dbname   = {repr(cfg_conn.dbname)}, cache.dbname = {repr(cache_conn.dbname)}\n"
            f"  cfg.user     = {repr(cfg_conn.user)}, cache.user = {repr(cache_conn.user)}\n"
            f"  cfg.host     = {repr(cfg_conn.host)}, cache.host = {repr(cache_conn.host)}\n"
            f"  cfg.port     = {repr(cfg_conn.port)}, cache.port = {repr(cache_conn.port)}"
        )
        ctx.log_event(Relevance.DEBUG, msg_conn)
        
    if not is_query_consistent:
        msg_query = (
            f"DB Query mismatch:\n"
            f"  cfg.bid    = {repr(bid)}, cache.bid = {repr(cache_query.bid)}\n"
            f"  cfg.status = {repr(status)}, cache.status = {repr(cache_query.status)}\n"
            f"  cfg.ec     = {repr(ec)}, cache.ec = {repr(cache_query.ec)}"
        )
        ctx.log_event(Relevance.DEBUG, msg_query)

    return is_cache_consistent

def load_from_db(ctx: "LMContext", *, bid=None, status=None) -> RegabDataSet:
    """Extract dataset from the database safely."""
    conn_params = ctx.cfg.regab_data_set.regab_db_connection
    rc = RegabDBConnection(conn_params.dbname, conn_params.user,
                           conn_params.host, str(conn_params.port),
                           conn_params.password)

    ctx.log_event(Relevance.DEBUG, f"Regab Database connection {(conn_params.dbname, conn_params.user, conn_params.host, conn_params.port)} established successfully.")

    query_params = ctx.cfg.regab_data_set
    if bid is None:
        bid = query_params.bid
    if status is None:
        status = query_params.status

    try:
        rds = regab_extract_data_set_from_db(rc, bid, status, query_params.ec)
        ctx.log_event(Relevance.DEBUG, f"Extracted {len(rds.df_mogv):,} positions from the database.")
        return rds
    finally:
        rc.close()
        ctx.log_event(Relevance.DEBUG, "Regab Database connection closed successfully.")


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def wrk_positions() -> Worker:
    """Factory function that returns the POSITIONS worker instance."""
    return Worker("POSITIONS", _up, _down)

