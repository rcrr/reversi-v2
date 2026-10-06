#
# hlp_validate.py
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

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from reversi.lm.hlp_gradient import sigmoid
from reversi.tools.state_machine import Relevance

if TYPE_CHECKING:
    from reversi.lm.logistic_model import LMContext


__all__ = ['ValidationResult', 'validate_model', 'top_outliers']


@dataclass
class ValidationResult:
    """
    Carry the VALIDATE level's output: the 7-metric validation dict (the v2 model-file contract,
    unchanged) plus the two per-position series it is computed from.
    """
    metrics: dict[str, Any]     # the 7-key dict (the v2 model-file contract)
    y_pred: np.ndarray          # (N_VLD,) f64 — the fitted values in Y (the f64 view of the EF output)
    rn_y: np.ndarray            # (N_VLD,) f64 — the residuals in Y (the f64 view) — the series PLOT
                                # renders and CLIENT_CHECK compares against the saved-model file


def top_outliers(rn: np.ndarray, k: int = 20) -> np.ndarray:
    """
    Return the indices of the k largest |residual| values, in descending order.

    The STABLE argsort makes the selection deterministic: a tie keeps the lower index first.

    Args:
        rn: the residual series (the per-position values to rank).
        k: the number of outliers to select (default 20).

    Returns:
        np.ndarray: the k selected indices (descending |residual|).
    """
    return np.argsort(-np.abs(rn), kind='stable')[:k]


def validate_model(ctx: "LMContext") -> ValidationResult:
    """
    Run the validation forward pass and compute the validation metrics.

    The model is evaluated on the validation positions (the same feature_set as training, the dense
    weights from GENERATE): the discrete game values Y (the ordinal scale, [-64, +64] in steps of 2)
    are affinely mapped to the continuous target Z in [0, 1], and the metrics are pure geometric
    distance indicators in Z space — how well the continuous logistic curve aligns with the discrete targets.

    The metrics: MAE = (1 / n) * sum(|z_i - z_hat_i|), MSE = (1 / n) * sum((z_i - z_hat_i)^2), RMSE
    = sqrt(MSE); the ratio RMSE / MAE = sqrt(pi/2) = 1.253... marks a normal residual distribution.

    Args:
        ctx: the LMContext (the validation positions + game values, the feature_set, the w_dense
            weights, the y2z / z2y maps).

    Returns:
        ValidationResult: the 7-metric dict (vld_loss, vld_mse_z, vld_mae_z, vld_mae_y, vld_mse_y,
            vld_rmse_y, vld_samples) + the two f64 per-position series (y_pred, rn_y).
    """
    vld_positions = ctx.vld_positions
    vld_game_values = ctx.vld_game_values

    # The validation indexes, from the SAME feature_set as training.
    ctx.log_event(Relevance.INFO, "Computing indexes for validation set...")
    vld_indexes = ctx.feature_set.compute_indexes(vld_positions)
    vld_M, _ = vld_indexes.shape

    # The dense mapping: the per-instance column offsets point the raw indexes directly into w_dense.
    n_instances_per_feature = [f.n_instances for f in ctx.feature_set.features]
    col_offsets = np.repeat(ctx.iwmap_feature_offset[:-1], n_instances_per_feature)
    dense_indices = vld_indexes + col_offsets

    # The forward pass: the predictions in Z space [0, 1].
    ctx.log_event(Relevance.INFO, "Computing predictions (forward pass) on validation set...")
    linear_predictor = np.sum(ctx.w_dense[dense_indices], axis=1)
    z_pred = sigmoid(linear_predictor)
    vld_z = ctx.y2z(vld_game_values)

    # The metrics in Z space.
    rn_z = z_pred - vld_z
    norm_rn_z = np.dot(rn_z, rn_z)
    vld_loss = 0.5 * (norm_rn_z / vld_M)
    mse_z = norm_rn_z / vld_M
    mae_z = np.mean(np.abs(rn_z))

    # The metrics in Y space (the original game-points scale): the ORIGINAL f32 arithmetic (the f32
    # prediction minus the int8 game value, the sum in f32) — the goldens are pinned and embedded in
    # the v2 model file, so this split must not move them.
    y_pred = ctx.z2y(z_pred)
    rn_y = y_pred - vld_game_values
    mae_y = np.mean(np.abs(rn_y))
    mse_y = np.dot(rn_y, rn_y) / vld_M
    rmse_y = np.sqrt(mse_y)

    # The published per-position series in the f64 views (the PlotData / the CLIENT_CHECK reference
    # contract: the f32 prediction and the int8 game value upcast exactly — no rounding noise
    # enters, and the series stay bit-identical to what PLOT and CLIENT_CHECK consume).
    y_pred_f64 = y_pred.astype(np.float64)
    rn_y_f64 = y_pred_f64 - vld_game_values.astype(np.float64)

    return ValidationResult(
        metrics={
            'vld_loss': float(vld_loss),
            'vld_mse_z': float(mse_z),
            'vld_mae_z': float(mae_z),
            'vld_mae_y': float(mae_y),
            'vld_mse_y': float(mse_y),
            'vld_rmse_y': float(rmse_y),
            'vld_samples': int(vld_M)
        },
        y_pred=y_pred_f64,
        rn_y=rn_y_f64)
