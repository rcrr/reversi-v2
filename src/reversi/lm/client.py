#
# client.py
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
import numpy.typing as npt

from typing import Callable

from pydantic import validate_call, ConfigDict

from reversi.lm.model_weights import ModelWeights
from reversi.lm.hlp_zed import hlp_zed_fun_factory
from reversi.lm.hlp_gradient import sigmoid
from reversi.board import Position, PositionArray


__all__ = ['make_evaluation_function',
           'make_evaluation_function_array']


def _prepare_weights(mw: ModelWeights) -> tuple:
    """
    Prepare the shared closure data for the scalar and the array Evaluation Function factories.

    Both factories close over the same two pre-computed artifacts: the per-instance w_dense start
    offsets and the z→y affine map. The offsets expand the feature boundary array to instance
    granularity (each feature's start repeated n_instances times, e.g. EDGE's start 4 times for its
    4 instances), so the per-instance index gathers w_dense directly; the z2y map is only the z→y
    half of the zed transform, since the client never transforms observations.

    Args:
        mw: the trained model whose weights are closed over.

    Returns:
        tuple: (expanded_offsets, z2y) — expanded_offsets: the per-instance w_dense start offsets
            (the boundary array without its last entry, each start repeated n_instances times); z2y:
            the z→y affine transform (the hlp_zed_fun_factory z→y half).
    """
    offsets = mw.iwmap_feature_offset
    _, z2y = hlp_zed_fun_factory(mw.logit_clipping)

    # Pre-compute the expanded offsets for all instances
    n_instances_per_feature = [f.n_instances for f in mw.feature_set.features]
    expanded_offsets = np.repeat(offsets[:-1], n_instances_per_feature)
    return expanded_offsets, z2y


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def make_evaluation_function(mw: ModelWeights) -> Callable[[Position], float]:
    """
    Create a scalar Evaluation Function (EF) in Y space, closed over the trained model.

    The returned EF evaluates a single position: it computes the principal index of every feature
    instance, gathers the corresponding dense weights, sums them into the linear predictor, applies
    the sigmoid (Z space) and the z→y affine map, and returns the resulting game value.

    Args:
        mw: the trained model the EF evaluates against.

    Returns:
        Callable[[Position], float]: the EF — one Position in, the Y-space game value out as a
        Python float.
    """
    expanded_offsets, z2y = _prepare_weights(mw)

    def ef(p: Position) -> float:
        # 1. Compute Principal Indexes (returns array of length total_instances)
        indexes = mw.feature_set.compute_indexes(np.array([p]))[0]

        # 2. Map directly to w_dense using expanded offsets
        w_indices = expanded_offsets + indexes
        weights = mw.w_dense[w_indices]

        # 3. Linear predictor and Sigmoid (Z space)
        linear_predictor = np.sum(weights)
        z_pred = sigmoid(linear_predictor)

        # 4. Transform back to Y space
        y_pred = z2y(np.array([z_pred], dtype=np.float32))[0]

        return float(y_pred)

    return ef


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def make_evaluation_function_array(mw: ModelWeights) -> Callable[[PositionArray], npt.NDArray[np.float32]]:
    """
    Create a vectorized Evaluation Function (EF) in Y space over a PositionArray batch.

    The returned EF evaluates a whole batch in one call with the same inference as the scalar EF,
    bit-exact per position, for any input shape: it accepts a structured PositionArray of any shape
    and returns a same-shape float32 array (the positions evaluated in C-order element order),
    without the length-1 wrap (the compute_indexes call is already a batch API; the tail is
    element-wise NumPy).

    Strict array: the EF accepts a structured PositionArray of any shape (a (N, 2) uint64 array is
    coerced to 1-D by the PositionArray validator); a scalar Position or bare lists raise the
    Pydantic ValidationError. Precondition (the compute_principal_indexes caller contract): the
    positions are collision-free (mover & opponent == 0); the client does not re-check.

    Args:
        mw: the trained model the EF evaluates against.

    Returns:
        Callable[[PositionArray], npt.NDArray[np.float32]]: the vectorized EF — one batch in, the
        same-shape float32 Y-space game values out (C-order element order; empty arrays keep their
        shape).
    """
    expanded_offsets, z2y = _prepare_weights(mw)

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def ef(p: PositionArray) -> npt.NDArray[np.float32]:
        # 1. Compute the Principal Indexes for the whole batch (p.shape + (I,))
        indexes = mw.feature_set.compute_indexes(p)

        # 2. Map to w_dense (the per-instance start offsets broadcast over the batch) and gather the
        # per-position sums over the LAST axis — the feature instances (the sum axis is
        # shape-agnostic: for a 1-D batch, axis -1 IS axis 1) — the linear predictor, f32
        weights = mw.w_dense[expanded_offsets + indexes]
        linear_predictor = weights.sum(axis=-1)

        # 3. Sigmoid (Z space) and 4. back to Y space (element-wise, f32; the output has the input shape)
        z_pred = sigmoid(linear_predictor)
        return z2y(z_pred)

    return ef
