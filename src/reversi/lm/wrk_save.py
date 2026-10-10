#
# wrk_save.py
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

from pydantic import validate_call, ConfigDict

from typing import TYPE_CHECKING

from reversi.tools.state_machine import Worker, Relevance
from reversi.lm.model_weights import model_weights_write_file

if TYPE_CHECKING:
    from reversi.lm.logistic_model import LMContext



__all__ = ['wrk_save']



def _up(ctx: "LMContext") -> None:
    """
    Run the SAVE level: write the lz4-compressed model weights file (the self-describing v2 artifact
    with the embedded configuration provenance) to the configured output path.
    """
    ctx.log_event(Relevance.INFO, "Saving model weights to disk...")

    output_path = ctx.cfg.base_dir / ctx.cfg.output

    # The model file embeds the configuration provenance (the normalized dump + the fingerprint, the
    # LEADING body section) — it is the single source of the run's configuration. The sidecar record
    # (<output>.config.json) is RETIRED (Roberto's ruling: the record is eliminated, the model file
    # stands alone).
    model_weights_write_file(ctx, output_path, compressed=True)
    ctx.log_event(Relevance.INFO, f"Model weights saved to {output_path}")


def _down(ctx: "LMContext") -> None:
    """Log the clearing no-op (the worker is stateless — nothing on the context)."""
    ctx.log_event(Relevance.INFO, "Clearing save attributes...")
    # Nothing to clear from context, as we just read from it.


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def wrk_save() -> Worker:
    """Return the SAVE worker instance."""
    return Worker("SAVE", _up, _down)
