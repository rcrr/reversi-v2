#
# client.py
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
import numpy.typing as npt

from typing import Callable

from pydantic import validate_call, ConfigDict

from reversi.lm.model_weights import ModelWeights
from reversi.lm.hlp_zed import zed_fun_factory
from reversi.lm.hlp_gradient import sigmoid
from reversi.board import Position, PositionArray


__all__ = ['make_evaluation_function',
           'make_evaluation_function_array']


def _prepare_weights(mw: ModelWeights) -> tuple:
    """
    Shared closure setup for the scalar and the array Evaluation
    Function factories (D-141): returns (expanded_offsets, z2y).

    expanded_offsets: the per-INSTANCE w_dense start offsets — the
    boundary array iwmap_feature_offset without its last entry, each
    start repeated n_instances times for its feature (e.g. if EDGE has
    4 instances, its offset is repeated 4 times).

    z2y: only the z→y affine half of zed_fun_factory — the client never
    transforms observations.
    """
    offsets = mw.iwmap_feature_offset
    _, z2y = zed_fun_factory(mw.logit_clipping)

    # Pre-compute the expanded offsets for all instances
    n_instances_per_feature = [f.n_instances for f in mw.feature_set.features]
    expanded_offsets = np.repeat(offsets[:-1], n_instances_per_feature)
    return expanded_offsets, z2y


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def make_evaluation_function(mw: ModelWeights) -> Callable[[Position], float]:
    """
    Factory that creates a scalar Evaluation Function (EF) in Y space.
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
    Factory that creates a vectorized Evaluation Function (EF) in Y
    space over a PositionArray batch (D-141).

    Strict array: it accepts a 1-D PositionArray (or a (N, 2) uint64
    array, coerced by the PositionArray validator) and returns a (N,)
    float32 array — the same inference as the scalar EF, bit-exact per
    position, without the length-1 wrap (the compute_indexes call is
    already a batch API; the tail is element-wise NumPy).

    Precondition (the compute_principal_indexes caller contract): the
    positions are collision-free (mover & opponent == 0); the client
    does not re-check.
    """
    expanded_offsets, z2y = _prepare_weights(mw)

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def ef(p: PositionArray) -> npt.NDArray[np.float32]:
        # The PositionArray validator coerces (N, 2) uint64 but admits
        # a 2-D structured array (no ndim check there): the standard
        # 1-D guard (D-111 M5) keeps a clean ValueError out of the
        # numba kernel.
        if p.ndim != 1:
            raise ValueError(f"p must be a 1-D PositionArray, got ndim {p.ndim} (shape {p.shape})")

        # 1. Compute the Principal Indexes for the whole batch (N, I)
        indexes = mw.feature_set.compute_indexes(p)

        # 2. Map to w_dense (the per-instance start offsets broadcast
        #    over the batch) and gather the row sums (the linear
        #    predictor, f32)
        weights = mw.w_dense[expanded_offsets + indexes]
        linear_predictor = weights.sum(axis=1)

        # 3. Sigmoid (Z space) and 4. back to Y space (element-wise, f32)
        z_pred = sigmoid(linear_predictor)
        return z2y(z_pred)

    return ef
