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
from reversi.tools.binio import write_sha3_256_sidecar
from reversi.lm.model_weights import model_weights_write_file

if TYPE_CHECKING:
    from reversi.lm.logistic_model import LMContext



__all__ = ['wrk_save']



def _up(ctx: "LMContext") -> None:
    ctx.log_event(Relevance.INFO, "Saving model weights to disk...")

    output_path = ctx.cfg.base_dir / ctx.cfg.output

    model_weights_write_file(ctx, output_path, compressed=True)
    ctx.log_event(Relevance.INFO, f"Model weights saved to {output_path}")

    _store_config_record(ctx, output_path)

def _store_config_record(ctx: "LMContext", output_path) -> None:
    # The model's configuration provenance record (D-142): the
    # normalized dump (the effective configuration of the run, the
    # base_dir override included) + the sha3_256 checksum sidecar,
    # written next to the model file so the record travels with the
    # shipped artifact.
    config_json = ctx.cfg.model_dump_json(indent=4)
    config_path = output_path.with_suffix(".config.json")
    config_path.write_text(config_json, encoding="utf-8")
    write_sha3_256_sidecar(config_path)
    ctx.log_event(Relevance.INFO, f"Configuration record saved to {config_path}")

def _down(ctx: "LMContext") -> None:
    ctx.log_event(Relevance.INFO, "Clearing save attributes...")
    # Nothing to clear from context, as we just read from it.

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def wrk_save() -> Worker:
    """Factory function that returns the SAVE worker instance."""
    return Worker("SAVE", _up, _down)
