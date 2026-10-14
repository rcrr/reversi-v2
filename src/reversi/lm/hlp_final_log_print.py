#
# hlp_final_log_print.py
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

from pathlib import Path
from typing import TYPE_CHECKING

from reversi.tools.state_machine import Relevance

if TYPE_CHECKING:
    from reversi.lm.logistic_model import LMContext


__all__ = ['hlp_final_log_print_write_log']


def hlp_final_log_print_write_log(ctx: "LMContext") -> Path:
    """
    Write the run log (all buffered events from DEBUG upward — the TRACE hot-loop detail stays
    out of the file) to the FINAL_LOG_PRINT file.

    This function renders the machine's event log buffer (the LogEntry list the StateMachine fills
    on every log_event, independent of the display verbosity gate) and writes it to the configured
    file name under the context base_dir. The buffer already carries the "Starting worker
    FINAL_LOG_PRINT, UP step" line (the machine logs it before the worker call), while the
    "Completed UP step" line is logged after the return — the file is the full log up to the moment
    of the write.

    Args:
        ctx: The pipeline context (the cfg with the log_file_name + the base_dir, the injected
            format_event_log renderer, the event log).

    Returns:
        Path: The path of the written log file.
    """
    log_path = Path(ctx.cfg.base_dir) / ctx.cfg.log_file_name
    log_path.parent.mkdir(parents=True, exist_ok=True)
    text = ctx.format_event_log(Relevance.DEBUG)
    log_path.write_text(text, encoding="utf-8")
    ctx.log_event(Relevance.DEBUG,
                  f"FINAL_LOG_PRINT: log written: {log_path} ({len(text.splitlines())} lines).")
    return log_path
