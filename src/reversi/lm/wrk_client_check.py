#
# wrk_client_check.py
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
from reversi.lm.client import make_evaluation_function_array
from reversi.lm.model_weights import model_weights_read_file

if TYPE_CHECKING:
    from reversi.lm.logistic_model import LMContext



__all__ = ['wrk_client_check']



def _up(ctx: "LMContext") -> None:
    """
    Run the CLIENT_CHECK level: re-read the saved model file, recompute the validation residuals in
    Y space with the client's vectorized Evaluation Function, and compare them against the
    VALIDATE-published series within client_check_tol — a RuntimeError on a breach.
    """
    ctx.log_event(Relevance.INFO, "Starting client check...")

    # 1. Re-read the saved model file (the SAVE artifact — the single source of the run's weights +
    # configuration). The v2 reader re-verifies the embedded config checksum on the way.
    output_path = ctx.cfg.base_dir / ctx.cfg.output
    mw = model_weights_read_file(output_path, compressed=True)

    # 2. Build the client's vectorized Evaluation Function on the FILE weights and recompute the
    # validation residuals in Y space (the rounded-lossless f64 view, as the reference).
    ef = make_evaluation_function_array(mw)
    y_pred_file = ef(ctx.vld_positions)
    rn_file = (y_pred_file.astype(np.float64)
               - ctx.vld_game_values.astype(np.float64))

    # 3. The reference: the VALIDATE residuals published on the context — the validation's OWN
    # series, computed once by the level that owns the forward pass. Nothing mutates the vld
    # artifacts between the levels 14 and 17, so the published array IS the in-memory reference the
    # check compares against.
    rn_ref = ctx.vld_rn

    diff = np.abs(rn_file - rn_ref)
    max_diff = float(diff.max())
    first_bad = int(diff.argmax())
    tol = ctx.cfg.client_check_tol

    if max_diff >= tol:
        ctx.log_event(Relevance.ERROR,
                      f"Client check FAILED: max residual difference "
                      f"{max_diff:.3e} (first at position {first_bad}) "
                      f">= tolerance {tol:.1e}.")
        raise RuntimeError(
            f"CLIENT_CHECK failed: the validation residuals "
            f"recomputed from the saved model file differ from the "
            f"in-memory validation residuals by {max_diff:.3e} "
            f"(first at position {first_bad}), above the tolerance "
            f"{tol:.1e}. The model file, the client, or the "
            f"validation forward pass has diverged.")

    ctx.log_event(Relevance.INFO,
                  f"Client check passed: {diff.size} validation "
                  f"residuals, max difference {max_diff:.3e} "
                  f"(tolerance {tol:.1e}).")


def _down(ctx: "LMContext") -> None:
    """
    No-op (the worker publishes nothing on the ctx — it re-reads the file on every up-move, as SAVE).
    """
    ctx.log_event(Relevance.INFO, "Clearing client check attributes...")


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def wrk_client_check() -> Worker:
    """Return the CLIENT_CHECK worker instance."""
    return Worker("CLIENT_CHECK", _up, _down)
