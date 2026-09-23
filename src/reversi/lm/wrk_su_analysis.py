#
# wrk_su_analysis.py
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
The SU_ANALYSIS worker (the SU level, step 3) — the level
ORCHESTRATION skeleton (D-289, the wrk_design_matrix minimalism):
the enable no-op, the CACHED corpus (phase 1, the expensive part —
the hlp_su_analysis compute, the binio cache flow D-288, the
consistency signature with the feature_set hash INSTEAD of the
rds_checksum), the statistics (phase 2: the dispersion + the
never-observed audit + the SU pairs, cheap, recomputed on EVERY run
including the cache hit — the hlp), and the ctx publication (the
corpus frequency tables for the EFFECT_SIZE level, the adherence,
step 6). ALL the analysis logic lives in
reversi.lm.hlp_su_analysis. The D-060 semantics: the generation
error fails the level, the machine re-raises, the _down clears the
ctx artifacts.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import validate_call, ConfigDict

from reversi.tools.state_machine import Worker, Relevance
from reversi.lm.hlp_su_analysis import (
    hlp_su_analysis_load_from_file,
    hlp_su_analysis_store_to_file,
    hlp_su_analysis_compute,
    hlp_su_analysis_is_cache_consistent,
    hlp_su_analysis_statistics)
from reversi.tools.cache_manager import cache_manager_load_or_compute

if TYPE_CHECKING:
    from reversi.lm.logistic_model import LMContext


__all__ = ['wrk_su_analysis']


def _up(ctx: "LMContext") -> None:
    cfg_fa = ctx.cfg.su_analysis
    if not cfg_fa.enable:
        ctx.log_event(Relevance.INFO,
                      "SU_ANALYSIS disabled (enable: false) — no-op.")
        ctx.su_analysis_tables = None
        return
    # Phase 1 — the corpus (the expensive part, CACHED).
    cache_hit, tables, _checksum = cache_manager_load_or_compute(
        cache_path  = ctx.get_cache_file_full_path_for_current_level(),
        is_allowed  = ctx.use_cache,
        load_fn     = lambda path: hlp_su_analysis_load_from_file(
            path, checksum=False),
        store_fn    = hlp_su_analysis_store_to_file,
        validate_fn = lambda cached: hlp_su_analysis_is_cache_consistent(
            ctx, cached),
        compute_fn  = lambda: hlp_su_analysis_compute(ctx),
        logger_fn   = ctx.log_event,
    )
    ctx.log_event(Relevance.INFO,
                  f"SU_ANALYSIS corpus: "
                  f"{'loaded from cache' if cache_hit else 'computed'}.")
    # Phase 2 — the statistics (cheap, recomputed on EVERY run).
    hlp_su_analysis_statistics(ctx, tables)
    # Publish the tables on the ctx (for the EFFECT_SIZE level).
    ctx.su_analysis_tables = tables
    ctx.log_event(Relevance.INFO,
                  "su_analysis_tables published on the ctx.")


def _down(ctx: "LMContext") -> None:
    ctx.log_event(Relevance.INFO,
                  "Clearing the su_analysis_tables attribute.")
    ctx.su_analysis_tables = None


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def wrk_su_analysis() -> Worker:
    """Factory function that returns the SU_ANALYSIS worker
    instance."""
    return Worker("SU_ANALYSIS", _up, _down)
