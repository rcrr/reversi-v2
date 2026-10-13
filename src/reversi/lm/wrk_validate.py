#
# wrk_validate.py
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

from pydantic import validate_call, ConfigDict

from typing import TYPE_CHECKING

from reversi.tools.state_machine import Worker, Relevance
from reversi.lm.hlp_validate import hlp_validate_top_outliers, hlp_validate_model

if TYPE_CHECKING:
    from reversi.lm.logistic_model import LMContext



__all__ = ['wrk_validate']



def _outlier_records(ctx: "LMContext", rn, y_pred, k: int = 20) -> list:
    """
    The k extreme-residual records, descending by |residual| (the stable argsort,
    hlp_validate_top_outliers): the position's bitboards + the game value + the fitted value + the
    residual, as raw values — the outlier report's data.

    rn / y_pred are the f64 validation series of LMValidate.
    """
    records = []
    for i in hlp_validate_top_outliers(rn, k):
        pos = ctx.vld_positions[i]
        records.append({
            'index': int(i),
            'mover': int(pos['mover']),
            'opponent': int(pos['opponent']),
            'game_value': float(ctx.vld_game_values[i]),
            'fitted': float(y_pred[i]),
            'residual': float(rn[i]),
        })
    return records


def _up(ctx: "LMContext") -> None:
    """
    Run the VALIDATE level: the model validation (hlp_validate_model), the four published outputs,
    and the metric block + the top-20 extreme-residual report.
    """
    ctx.log_event(Relevance.INFO, "Starting model validation...")

    result = hlp_validate_model(ctx)
    metrics = result.metrics
    ctx.vld_metrics = metrics
    ctx.vld_y_pred = result.y_pred
    ctx.vld_rn = result.rn_y
    ctx.vld_outliers = _outlier_records(ctx, result.rn_y, result.y_pred)

    ctx.log_event(Relevance.INFO, f"Validation completed. Loss (MSE/2): {metrics['vld_loss']:.8e}")
    ctx.log_event(Relevance.INFO, f"  MSE:      {metrics['vld_mse_z']:.4e}")
    ctx.log_event(Relevance.INFO, f"  MAE:      {metrics['vld_mae_z']:.4e}")
    ctx.log_event(Relevance.INFO, f"  MAE(y):   {metrics['vld_mae_y']:.2f}")
    ctx.log_event(Relevance.INFO, f"  RMSE(y):  {metrics['vld_rmse_y']:.2f}")
    if metrics['vld_mae_y'] > 0.0:
        ctx.log_event(Relevance.INFO, f"  RMSE/MAE: {(metrics['vld_rmse_y']/metrics['vld_mae_y']):.2f}")
    else:
        ctx.log_event(Relevance.INFO, "  RMSE/MAE: n/a (vld_mae_y is 0 — perfect Y-space fit)")

    # The top-20 extreme-residual report: it belongs to the level that COMPUTES the residuals; the
    # 20 records are published for the levels that consume them.
    ctx.log_event(Relevance.INFO,
                  "Top 20 extreme validation residuals (outlier report):")
    for rank, rec in enumerate(ctx.vld_outliers, 1):
        ctx.log_event(Relevance.INFO,
                      f"  {rank:2d}. vld position {rec['index']:>7d} "
                      f"({rec['mover']:016X}/{rec['opponent']:016X}): "
                      f"game value {rec['game_value']:+.0f}, "
                      f"fitted {rec['fitted']:+.2f}, "
                      f"residual {rec['residual']:+.2f}")

    return


def _down(ctx: "LMContext") -> None:
    """Clear the four validation attributes (the failure recovery)."""
    ctx.log_event(Relevance.INFO, "Clearing validation attributes...")
    ctx.vld_metrics = None
    ctx.vld_y_pred = None
    ctx.vld_rn = None
    ctx.vld_outliers = None

    return


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def wrk_validate() -> Worker:
    """Return the VALIDATE worker instance."""
    return Worker("VALIDATE", _up, _down)
