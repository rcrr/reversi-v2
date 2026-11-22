#
# multi_ply_ef.py
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

"""
The multi-ply evaluation function (D-674: the compiled EF leaf kernel + the per-model index
plan — the bit-exact pieces; D-675 adds the alpha-beta search + the public factory).

The design: a search-based evaluation over a ModelWeights `mw`. The search descends from the
position's empty count A to the model's empty count B = `mw.ec` (the horizon; A < B is a
contract `ValueError`, A == B is the pure EF — the factory delegates to the client EF, so the
depth-0 anchor is bit-exact by construction). A horizon leaf value is the EF of that position
computed by the COMPILED leaf of this module: the same njit index pipeline the client EF uses
(bit-exact indexes) + the f32 gather + the sequential f32 sum + the piecewise f32 expit (the
scipy form) + the z2y affine. The leaf is deterministic and within the measured ulp bound of
the client EF (the numpy pairwise sum vs the sequential sum: D-674 measurement, <= 409 ulp
on the linear predictor).

The compiled leaf reuses the pipeline's own njit kernels (the no-drift principle of
client.md): the anti-transformations + the principal-indexes kernel of pattern.py, the
indexes kernel of mobility.py, the legal-moves vector kernel of board.py, and the client's
own `_prepare_weights` for the dense offsets.
"""

import numba as nb
import numpy as np
import numpy.typing as npt
from pydantic import ConfigDict, validate_call

from reversi.board import (_numba_bitboard_anti_transformations, _vectorized_legal_moves)
from reversi.lm.client import _prepare_weights
from reversi.lm.model_weights import ModelWeights
from reversi.mobility import _numba_compute_indexes_kernel
from reversi.pattern import _numba_compute_principal_indexes_kernel

__all__ = ['prepare_multi_ply_plan']


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def prepare_multi_ply_plan(mw: ModelWeights) -> tuple:
    """
    The per-model prepared data of the compiled EF leaf (computed ONCE, closed over by the
    factory): a 17-tuple —

        0  expanded_offsets   (I,) u32   the per-instance w_dense start offsets (the client's)
        1  a1                 f32 scalar the z2y affine offset (the hlp_zed formula, bit-identical)
        2  b1                 f32 scalar the z2y affine slope
        3  has_intercept      bool       the intercept column (constant 0)
        4  mob_masks          (L,) u64   the mobility masks (the set's sorted (mask, side) order)
        5  mob_sides          (L,) u8    0 = mover, 1 = opponent
        6  n_squares_arr      (P,) u32   the pattern square counts
        7  bit_shifts_matrix  (P, S) u32 the per-pattern bit shifts
        8  powers_3           (S,) u32   the base-3 powers
        9  n_groups_arr       (P,) u32   the per-pattern distinct-mask group counts
        10 group_size_arr    (P,) u32   the 8 // n_groups coset sizes
        11 idx_sort_matrix   (P, 8) u32 the per-pattern mask-index sort orders
        12 current_col       int        the total pattern columns
        13 col_offsets       (P,) u32   the per-pattern column offsets
        14 num_planes_arr    (P,) u32   the per-pattern pack plane counts
        15 pack_masks_3d     (P, Q) u64 the per-pattern pack masks
        16 pack_shifts_3d    (P, Q) u64 the per-pattern pack shifts

    The pattern block MIRRORS the Python preparation of `PatternSet.compute_principal_indexes`
    (pattern.py) — the parity test pins the agreement, so a drift in one of the two
    preparations turns the suite red.
    """
    expanded_offsets, _ = _prepare_weights(mw)

    # The z2y affine constants: the EXACT hlp_zed_fun_factory formula (f64 division, then the
    # f32 cast) — bit-identical to the client's z2y closure.
    a1 = np.float32(-64. / (1. - 2. * mw.logit_clipping))
    b1 = np.float32(128. / (1. - 2. * mw.logit_clipping))

    fs = mw.feature_set
    has_intercept = bool(fs.intercept)

    # The mobility block (the MobilitySet.compute_indexes preparation, mobility.py).
    if fs.mset is not None:
        mob_masks = np.array([mo.mask for mo in fs.mset.mobilities], dtype=np.uint64)
        mob_sides = np.array([0 if mo.side == 'mover' else 1 for mo in fs.mset.mobilities],
                             dtype=np.uint8)
    else:
        mob_masks = np.empty(0, dtype=np.uint64)
        mob_sides = np.empty(0, dtype=np.uint8)

    # The pattern block (the PatternSet.compute_principal_indexes preparation, pattern.py).
    if fs.pset is not None and len(fs.pset.patterns) > 0:
        pats = fs.pset.patterns
        P = len(pats)
        S_max = max(p.n_squares for p in pats)
        Q_max = max(p.pack_plan[0].shape[0] for p in pats)
        powers_3 = np.array([3**j for j in range(S_max)], dtype=np.uint32)
        n_squares_arr = np.array([p.n_squares for p in pats], dtype=np.uint32)
        num_planes_arr = np.empty(P, dtype=np.uint32)
        bit_shifts_matrix = np.zeros((P, S_max), dtype=np.uint32)
        idx_sort_matrix = np.zeros((P, 8), dtype=np.uint32)
        n_groups_arr = np.empty(P, dtype=np.uint32)
        group_size_arr = np.empty(P, dtype=np.uint32)
        col_offsets = np.empty(P, dtype=np.uint32)
        pack_masks_3d = np.zeros((P, Q_max), dtype=np.uint64)
        pack_shifts_3d = np.zeros((P, Q_max), dtype=np.uint64)
        current_col = 0
        for i, p in enumerate(pats):
            bit_shifts_matrix[i, :p.n_squares] = p.bit_shifts
            mi = p.mask_indexes
            n_groups = len(np.unique(mi))
            n_groups_arr[i] = n_groups
            group_size_arr[i] = 8 // n_groups
            idx_sort_matrix[i, :] = np.argsort(mi)
            col_offsets[i] = current_col
            p_masks, _, p_shifts = p.pack_plan
            num_planes_arr[i] = p_masks.shape[0]
            pack_masks_3d[i, :p_masks.shape[0]] = p_masks
            pack_shifts_3d[i, :p_shifts.shape[0]] = p_shifts
            current_col += n_groups
    else:
        S_max = 0
        powers_3 = np.empty(0, dtype=np.uint32)
        n_squares_arr = np.empty(0, dtype=np.uint32)
        num_planes_arr = np.empty(0, dtype=np.uint32)
        bit_shifts_matrix = np.zeros((0, S_max), dtype=np.uint32)
        idx_sort_matrix = np.zeros((0, 8), dtype=np.uint32)
        n_groups_arr = np.empty(0, dtype=np.uint32)
        group_size_arr = np.empty(0, dtype=np.uint32)
        col_offsets = np.empty(0, dtype=np.uint32)
        pack_masks_3d = np.zeros((0, 0), dtype=np.uint64)
        pack_shifts_3d = np.zeros((0, 0), dtype=np.uint64)
        current_col = 0

    return (expanded_offsets, a1, b1, has_intercept, mob_masks, mob_sides,
            n_squares_arr, bit_shifts_matrix, powers_3, n_groups_arr, group_size_arr,
            idx_sort_matrix, current_col, col_offsets, num_planes_arr,
            pack_masks_3d, pack_shifts_3d)


@nb.njit(cache=True)
def _ef_leaf_indexes(mover, opponent,
                    has_intercept,
                    mob_masks, mob_sides,
                    n_squares_arr, bit_shifts_matrix, powers_3,
                    n_groups_arr, group_size_arr, idx_sort_matrix,
                    current_col, col_offsets,
                    num_planes_arr, pack_masks_3d, pack_shifts_3d):
    """
    The compiled index pipeline of a SINGLE position: the same njit kernels the client EF uses
    (the `FeatureSet.compute_indexes` pydantic wrapper inlined) — bit-exact with it.

    Returns:
        The (I,) uint32 index row (the intercept column, then the mobility block, then the
        pattern block — the FeatureSet column contract).
    """
    m1 = np.array([mover], dtype=np.uint64)
    o1 = np.array([opponent], dtype=np.uint64)

    n_mob = mob_masks.shape[0]
    I = (1 if has_intercept else 0) + n_mob + current_col
    out = np.empty(I, dtype=np.uint32)
    k = 0
    if has_intercept:
        out[0] = 0
        k = 1
    if n_mob > 0:
        lms = _vectorized_legal_moves(m1, o1)
        alms = _vectorized_legal_moves(o1, m1)
        mob = _numba_compute_indexes_kernel(lms, alms, mob_masks, mob_sides)
        for j in range(n_mob):
            out[k + j] = mob[0, j]
        k += n_mob
    if current_col > 0:
        m_atrxs = _numba_bitboard_anti_transformations(m1)
        o_atrxs = _numba_bitboard_anti_transformations(o1)
        pat = _numba_compute_principal_indexes_kernel(
            m_atrxs, o_atrxs,
            n_squares_arr, bit_shifts_matrix, powers_3,
            n_groups_arr, group_size_arr, idx_sort_matrix,
            current_col, col_offsets,
            num_planes_arr, pack_masks_3d, pack_shifts_3d)
        for j in range(current_col):
            out[k + j] = pat[0, j]
    return out


@nb.njit(cache=True)
def _ef_leaf_value(mover, opponent,
                   w_dense, expanded_offsets, a1, b1,
                   has_intercept,
                   mob_masks, mob_sides,
                   n_squares_arr, bit_shifts_matrix, powers_3,
                   n_groups_arr, group_size_arr, idx_sort_matrix,
                   current_col, col_offsets,
                   num_planes_arr, pack_masks_3d, pack_shifts_3d):
    """
    The compiled EF leaf of a SINGLE position: the index row (the client's njit pipeline) +
    the f32 gather + the SEQUENTIAL f32 sum + the piecewise f32 expit (the scipy form the
    client's sigmoid is) + the z2y affine.

    Deterministic (the same f32 bits on every run); within the measured ulp bound of the
    client EF (the numpy pairwise sum vs the sequential sum — D-674: <= 409 ulp linear).

    Returns:
        The f32 Y-space value of the position.
    """
    idx = _ef_leaf_indexes(mover, opponent,
                           has_intercept,
                           mob_masks, mob_sides,
                           n_squares_arr, bit_shifts_matrix, powers_3,
                           n_groups_arr, group_size_arr, idx_sort_matrix,
                           current_col, col_offsets,
                           num_planes_arr, pack_masks_3d, pack_shifts_3d)
    linear = np.float32(0.0)
    for i in range(idx.shape[0]):
        # The u32 sum: expanded_offsets u32 + idx u32 -> u32 (the client's measured promotion).
        linear += w_dense[expanded_offsets[i] + idx[i]]
    # The scipy expit piecewise form (the f32 loop — the client's sigmoid, bit-exact shape):
    one = np.float32(1.0)
    if linear >= 0:
        z = one / (one + np.exp(-linear))
    else:
        e = np.exp(linear)
        z = e / (one + e)
    return a1 + z * b1
