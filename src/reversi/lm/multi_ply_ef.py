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
The multi-ply evaluation function: the compiled EF leaf kernel + the per-model index plan
(the bit-exact pieces) and the float32 alpha-beta search + the public
`make_evaluation_function` factory.

The design: a search-based evaluation over a ModelWeights `mw`. The search descends from the
position's empty count A to the model's empty count B = `mw.ec` (the horizon; A < B is a
contract `ValueError`, A == B is the pure EF — the factory delegates to the client EF, so the
depth-0 anchor is bit-exact by construction). A horizon leaf value is the EF of that position
computed by the COMPILED leaf of this module: the same njit index pipeline the client EF uses
(bit-exact indexes) + the f32 gather + the sequential f32 sum + the piecewise f32 expit (the
scipy form) + the z2y affine. The leaf is deterministic and within the measured ulp bound of
the client EF (the numpy pairwise sum vs the sequential sum: measured <= 409 ulp on the
linear predictor).

The leaf is a SERIAL transcription of the client's kernels (the no-drift principle of
client.md, the single-position form): the batch `parallel=True` kernels cannot be called
from the search's parallel region (nested parallel calls are forbidden — and the old
worker-pool threads crashed them with the LLVM `allocate_sched` bug), so the leaf inlines
the kernel BODIES — the anti-transformation scalar impls of board.py, the mobility loop
of mobility.py, the pack/base-3/coset-min pipeline of pattern.py — and the client's own
`_prepare_weights` for the dense offsets. The index-parity test pins the bit-exact
agreement with the client's `compute_indexes`.

The batch search is a SINGLE njit call over the lanes on numba's workqueue (`prange`):
the per-lane search is independent, the workqueue balances the lane-cost tail at the C
level, and the whole call runs with the GIL released. (The earlier Python worker pool —
a lane-index queue pulled by one thread per core — plateaued at ~2 cores in this numba x
CPython environment: the GIL is released per call, but 8 Python threads over njit calls
do not scale past ~2; numba's own threadpool does.)
"""

from typing import Callable

import numba as nb
import numpy as np
import numpy.typing as npt
from pydantic import ConfigDict, validate_call

from reversi.board import (Bitboard, PositionArray, _bsr,
                           _numba_fa1h8_scalar_impl,
                           _numba_fh1a8_scalar_impl, _numba_fhori_scalar_impl,
                           _numba_fvert_scalar_impl, _popcount, bitboard_count,
                           final_value_of, flips_of_move, legal_moves_of)
from reversi.lm.client import _prepare_weights, make_evaluation_function_array
from reversi.lm.model_weights import ModelWeights

__all__ = ['prepare_multi_ply_plan', 'make_evaluation_function']

# The fixed best-first square grouping of the search move loop, ported from the C fast
# endgame solver's worst_to_best table: the corner rings first (the four corners in the
# first group), the outer rings in, the X-squares last, the central four appended after
# them. Each group is one bitmask; `legal` is masked with the groups in this order and
# each group's legal bits are scanned BSR-first. The central four ARE searched (unlike
# the C, which skips them), so the value stays the exact minimax — the ordering only
# changes the node counts, never the values (the wide root window contains the range).
GROUP_MASKS = np.array([
    0x8100000000000081,   # the four corners (A1, H1, A8, H8)
    0x2400810000810024,
    0x240000240000,
    0x1800008181000018,
    0x182424180000,
    0x18004242001800,
    0x24420000422400,
    0x4281000000008142,
    0x42000000004200,
    0x1818000000,         # the central four (E5, D5, E4, D4)
], dtype=np.uint64)
N_GROUPS = 10


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
    The compiled index pipeline of a SINGLE position — the SERIAL transcription of the client's
    njit kernels (the batch `parallel=True` forms cannot be called from the search's parallel
    region — nested parallel calls, and the old worker-pool threads, crash with the LLVM
    `allocate_sched` bug): the same per-element math, bit-exact with
    `FeatureSet.compute_indexes`.

    Returns:
        The (I,) uint32 index row (the intercept column, then the mobility block, then the
        pattern block — the FeatureSet column contract).
    """
    n_mob = mob_masks.shape[0]
    I = (1 if has_intercept else 0) + n_mob + current_col
    out = np.empty(I, dtype=np.uint32)
    k = 0
    if has_intercept:
        out[0] = 0
        k = 1
    if n_mob > 0:
        # The mobility kernel body (mobility.py), the single-position form:
        lm_m = legal_moves_of(mover, opponent)
        lm_o = legal_moves_of(opponent, mover)
        for j in range(n_mob):
            src = lm_m if mob_sides[j] == 0 else lm_o
            out[k + j] = _popcount(src & mob_masks[j])
        k += n_mob
    if current_col > 0:
        # The anti-transformations (the board.py kernel body, the 8 scalar images):
        m_atrxs = np.empty(8, dtype=np.uint64)
        o_atrxs = np.empty(8, dtype=np.uint64)
        for v, ts in ((mover, m_atrxs), (opponent, o_atrxs)):
            fh = _numba_fhori_scalar_impl(v)
            ts[0] = v
            ts[1] = _numba_fh1a8_scalar_impl(fh)
            ts[2] = _numba_fvert_scalar_impl(fh)
            ts[3] = _numba_fa1h8_scalar_impl(fh)
            ts[4] = _numba_fvert_scalar_impl(v)
            ts[5] = _numba_fh1a8_scalar_impl(v)
            ts[6] = fh
            ts[7] = _numba_fa1h8_scalar_impl(v)
        # The principal-indexes kernel body (pattern.py), the single-position form:
        L = n_squares_arr.shape[0]
        local = np.empty(8, dtype=np.uint32)
        for i in range(L):
            S = n_squares_arr[i]
            n_groups = n_groups_arr[i]
            group_size = group_size_arr[i]
            col_offset = col_offsets[i]
            num_planes = num_planes_arr[i]
            for s in range(8):
                val_m = m_atrxs[s]
                val_o = o_atrxs[s]
                packed_m = Bitboard(0)
                packed_o = Bitboard(0)
                for p in range(num_planes):
                    mask = pack_masks_3d[i, p]
                    shift = pack_shifts_3d[i, p]
                    packed_m |= (val_m & mask) >> shift
                    packed_o |= (val_o & mask) >> shift
                idx_m = np.uint32(0)
                idx_o = np.uint32(0)
                for b in range(S):
                    shift_val = bit_shifts_matrix[i, b]
                    p3 = powers_3[b]
                    bit_m = (packed_m >> shift_val) & Bitboard(1)
                    bit_o = (packed_o >> shift_val) & Bitboard(1)
                    idx_m += np.uint32(bit_m) * p3
                    idx_o += np.uint32(bit_o) * p3
                local[s] = (np.uint32(2) * idx_o) + idx_m
            for g in range(n_groups):
                min_val = np.uint32(4294967295)  # UINT32_MAX
                start_idx = g * group_size
                for t in range(group_size):
                    sorted_s = idx_sort_matrix[i, start_idx + t]
                    val = local[sorted_s]
                    if val < min_val:
                        min_val = val
                out[k + col_offset + g] = min_val
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
    client EF (the numpy pairwise sum vs the sequential sum — measured <= 409 ulp on the
    linear predictor).

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


@nb.njit(cache=True)
def _ab_eval(mover, opponent, state,
             w_dense, expanded_offsets, a1, b1,
             has_intercept,
             mob_masks, mob_sides,
             n_squares_arr, bit_shifts_matrix, powers_3,
             n_groups_arr, group_size_arr, idx_sort_matrix,
             current_col, col_offsets,
             num_planes_arr, pack_masks_3d, pack_shifts_3d,
             horizon_stones, verify_end_game):
    """
    The float32 alpha-beta of the multi-ply EF (the endgame-solver discipline, the value-only
    variant): the node value is seen from the point of view of the mover at that node (the
    child values are negated at each ply); the horizon node is the EF leaf (the contract: at
    the horizon, the value is the EF — no pass-through); the terminal node is the exact WOF
    (`final_value_of`, the mover's point of view) cast to f32; a no-move node above the
    horizon passes (the sides swap, the value is negated). The move loop is the fixed
    best-first group order (the `GROUP_MASKS` table: `legal` masked with the groups in
    priority order, each group's legal bits scanned BSR-first), the zero-window
    propagation (the child window is the negated parent window), the cutoff at value >=
    beta, and the strict > alpha rise. `state` is the 2-element shared
    array: state[0] / state[1] the node's (alpha, beta) window (the numba 0.68 state-array
    idiom).

    `verify_end_game` (the factory parameter, default False): when True, a horizon-or-above
    node is first tested for the double pass (no legal move for EITHER side — the game over)
    and returns the exact WOF instead of the EF leaf estimate; with the model's horizon at
    the 64-stone board (ec0) every leaf is then a true terminal and the search value is the
    exact endgame value (the model is never consulted). The cost: the two `legal_moves_of`
    calls per horizon leaf, paid only when the flag is on.

    Returns:
        The f32 value of the position, from the mover's point of view.
    """
    # The horizon: the EF leaf (the stones only grow, so >= is the exact horizon test).
    # `_popcount` is the njit kernel (the bitboard_count public wrapper is Python).
    if _popcount(mover | opponent) >= horizon_stones:
        if verify_end_game and not legal_moves_of(mover, opponent) \
                and not legal_moves_of(opponent, mover):
            # The terminal at/above the horizon: the exact WOF (the verify_end_game
            # contract — the horizon check no longer shadows the double pass).
            return np.float32(final_value_of(mover, opponent))
        return _ef_leaf_value(mover, opponent, w_dense, expanded_offsets, a1, b1,
                              has_intercept,
                              mob_masks, mob_sides,
                              n_squares_arr, bit_shifts_matrix, powers_3,
                              n_groups_arr, group_size_arr, idx_sort_matrix,
                              current_col, col_offsets,
                              num_planes_arr, pack_masks_3d, pack_shifts_3d)
    legal = legal_moves_of(mover, opponent)
    if not legal:
        if not legal_moves_of(opponent, mover):
            # The terminal: the exact WOF (the mover's point of view), as f32.
            return np.float32(final_value_of(mover, opponent))
        # The pass: the sides swap, the window negates (the zero-window propagation).
        saved_a, saved_b = state[0], state[1]
        state[0], state[1] = -state[1], -state[0]
        value = _ab_eval(opponent, mover, state,
                         w_dense, expanded_offsets, a1, b1,
                         has_intercept,
                         mob_masks, mob_sides,
                         n_squares_arr, bit_shifts_matrix, powers_3,
                         n_groups_arr, group_size_arr, idx_sort_matrix,
                         current_col, col_offsets,
                         num_planes_arr, pack_masks_3d, pack_shifts_3d,
                         horizon_stones, verify_end_game)
        state[0], state[1] = saved_a, saved_b
        return -value
    alpha = state[0]
    beta = state[1]
    best = alpha
    for g in range(N_GROUPS):
        gm = legal & GROUP_MASKS[g]
        while gm:
            sq = _bsr(gm)
            m = Bitboard(1) << Bitboard(sq)
            gm = gm & ~m
            flips = flips_of_move(mover, opponent, m)
            saved_a, saved_b = state[0], state[1]
            state[0], state[1] = -beta, -alpha
            value = _ab_eval(opponent ^ flips, (mover ^ flips) | m, state,
                             w_dense, expanded_offsets, a1, b1,
                             has_intercept,
                             mob_masks, mob_sides,
                             n_squares_arr, bit_shifts_matrix, powers_3,
                             n_groups_arr, group_size_arr, idx_sort_matrix,
                             current_col, col_offsets,
                             num_planes_arr, pack_masks_3d, pack_shifts_3d,
                             horizon_stones, verify_end_game)
            state[0], state[1] = saved_a, saved_b
            value = -value
            if value > best:
                best = value
                # The node's alpha rises with the best child: the NEXT sibling's window is
                # derived from it (the zero-window tightening, the source of the pruning).
                alpha = value
                if value >= beta:
                    return best
    return best


@nb.njit(parallel=True, cache=True)
def _search_prange(movers, opponents, out,
                   w_dense, expanded_offsets, a1, b1,
                   has_intercept,
                   mob_masks, mob_sides,
                   n_squares_arr, bit_shifts_matrix, powers_3,
                   n_groups_arr, group_size_arr, idx_sort_matrix,
                   current_col, col_offsets,
                   num_planes_arr, pack_masks_3d, pack_shifts_3d,
                   horizon_stones, window, verify_end_game):
    """
    The batch search over the lanes STRICTLY ABOVE the horizon, as a single njit call: the
    lanes loop on numba's workqueue (`prange` — the C-level dynamic dispatch that balances
    the lane-cost tail), each lane the compiled `_ab_eval` with the root window [-R, +R].
    The per-lane values are bit-exact with the former worker-pool form (the search is
    per-lane independent; the window state is F64 — the f32 values are exact in it, where
    an f32 window stored in int64 would TRUNCATE and break the zero-window tightening).
    `verify_end_game` is passed through to `_ab_eval` (the horizon terminal check).
    """
    n = movers.shape[0]
    for i in nb.prange(n):
        st = np.zeros(2, dtype=np.float64)
        st[0], st[1] = -window, window  # the root window [-R, +R] (alpha, beta)
        out[i] = _ab_eval(movers[i], opponents[i], st,
                          w_dense, expanded_offsets, a1, b1,
                          has_intercept,
                          mob_masks, mob_sides,
                          n_squares_arr, bit_shifts_matrix, powers_3,
                          n_groups_arr, group_size_arr, idx_sort_matrix,
                          current_col, col_offsets,
                          num_planes_arr, pack_masks_3d, pack_shifts_3d,
                          horizon_stones, verify_end_game)
    return out


def _search_pool(positions, ecs, mw, plan, window, horizon_stones,
                 verify_end_game=False):
    """
    The batch search over the lanes strictly above the horizon (the A == B lanes are
    evaluated by the factory in a single batched client-EF call): one njit call, the lanes
    on numba's workqueue (the `_search_prange` above) — the GIL is released for the whole
    call, the per-lane values are the individual ones. `verify_end_game` is the factory's
    horizon terminal check (default False: the horizon leaf is always the EF estimate).

    Returns:
        The (positions.shape,) float32 value array.
    """
    n = positions.shape[0]
    out = np.empty(n, dtype=np.float32)
    if n == 0:
        return out
    (expanded_offsets, a1, b1, has_intercept,
     mob_masks, mob_sides,
     n_squares_arr, bit_shifts_matrix, powers_3,
     n_groups_arr, group_size_arr, idx_sort_matrix,
     current_col, col_offsets,
     num_planes_arr, pack_masks_3d, pack_shifts_3d) = plan
    return _search_prange(positions['mover'], positions['opponent'], out,
                          mw.w_dense, expanded_offsets, a1, b1,
                          has_intercept,
                          mob_masks, mob_sides,
                          n_squares_arr, bit_shifts_matrix, powers_3,
                          n_groups_arr, group_size_arr, idx_sort_matrix,
                          current_col, col_offsets,
                          num_planes_arr, pack_masks_3d, pack_shifts_3d,
                          horizon_stones, window, verify_end_game)


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def make_evaluation_function(mw: ModelWeights,
                             verify_end_game: bool = False
                             ) -> Callable[[npt.NDArray], npt.NDArray[np.float32]]:
    """
    The multi-ply evaluation-function factory: the search-based evaluation over the model.

    The returned `ef` is STRICT ARRAY (the client array-EF contract): it accepts a structured
    PositionArray of any shape (a (N, 2) uint64 array is coerced to 1-D by the PositionArray
    validator) and returns a same-shape float32 array (C-order element order). A scalar
    Position or bare lists raise the Pydantic `ValidationError`.

    The search contract: every position's empty count A must be >= the model's horizon
    B = `mw.ec` (a `ValueError` naming the offending count otherwise). The batch is split
    first: the A == B lanes (the bit-exact depth-0 anchor) go to the CLIENT EF itself in a
    SINGLE batched call (the EF is per-position, so the batched values are the individual
    ones); only the A > B lanes run the float32 alpha-beta — a single njit call over the
    lanes on numba's workqueue (the fixed best-first group order, the zero window, down to
    the horizon, where the leaf value is the compiled EF).

    The Y output range contract applies: NO clip anywhere; the root window is
    derived from the clipping: R = ceil(64/(1-2c)) + 1 (67 for c = 0.01 — it strictly
    contains the EF range +/-64/(1-2c) = +/-65.31, as the C ground window +/-66 contains the
    game-value range).

    Args:
        mw: the model weights (the feature set + the weights + the ec horizon).
        verify_end_game: when True, a horizon-or-above node with NO legal move for either
            side (the game over) returns the exact WOF value instead of the EF leaf
            estimate (the horizon check no longer shadows the double pass). With the model's
            horizon at the 64-stone board (ec0) every leaf is then a true terminal and the
            search value is the exact endgame value (the model is never consulted): the EF
            coincides with the exact endgame solver. The cost is the two `legal_moves_of`
            calls per horizon leaf, paid only when the flag is on. Default False: the
            horizon leaf is always the EF estimate (the original contract).
    """
    plan = prepare_multi_ply_plan(mw)
    horizon_stones = 64 - mw.ec
    window = int(np.ceil(64.0 / (1.0 - 2.0 * mw.logit_clipping))) + 1
    client_ef = make_evaluation_function_array(mw)

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def ef(positions: PositionArray) -> npt.NDArray[np.float32]:
        # The A >= B contract (the per-lane empty counts).
        ecs = 64 - bitboard_count(positions['mover'] | positions['opponent'])
        if ecs.size and int(ecs.min()) < mw.ec:
            bad = int(ecs.min())
            raise ValueError(
                f'every position empty count must be >= the model empty count '
                f'{mw.ec} (the search horizon): found {bad}')
        flat = positions.ravel()
        ecs_flat = ecs.ravel()
        out = np.empty(flat.shape, dtype=np.float32)
        horizon = ecs_flat == mw.ec
        if horizon.any():
            # The depth-0 lanes: the client EF itself, one batched call (the bit-exact anchor).
            out[horizon] = client_ef(flat[horizon])
        above = ~horizon
        if above.any():
            out[above] = _search_pool(flat[above], ecs_flat[above], mw, plan,
                                       window, horizon_stones, verify_end_game)
        return out.reshape(positions.shape)

    return ef
