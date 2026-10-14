#
# wrk_final_log_print.py
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
from reversi.lm.hlp_final_log_print import hlp_final_log_print_write_log

if TYPE_CHECKING:
    from reversi.lm.logistic_model import LMContext


__all__ = ['wrk_final_log_print']


def _up(ctx: "LMContext") -> None:
    """
    Run the FINAL_LOG_PRINT level: write the run log from DEBUG upward (via the hlp writer) — the
    absent log_file_name is a clean no-op (the file is NOT generated).
    """
    if ctx.cfg.log_file_name is None:
        ctx.log_event(Relevance.INFO, "FINAL_LOG_PRINT skipped: no log_file_name.")
        return
    hlp_final_log_print_write_log(ctx)


def _down(ctx: "LMContext") -> None:
    """No-op down: the worker publishes nothing on the context (the file is NOT unlinked)."""
    ctx.log_event(Relevance.INFO, "FINAL_LOG_PRINT down (no-op).")


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def wrk_final_log_print() -> Worker:
    """Return the FINAL_LOG_PRINT worker instance."""
    return Worker("FINAL_LOG_PRINT", _up, _down)
