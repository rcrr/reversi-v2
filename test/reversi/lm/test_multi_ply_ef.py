#
# test_multi_ply_ef.py
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
Unit tests for the multi-ply EF compiled leaf (D-674): the index parity (BIT-EXACT vs the
client's compute_indexes pipeline) + the leaf value contract (deterministic, within the
measured ulp bound of the client EF — the numpy pairwise sum vs the sequential f32 sum).
No DB: the fixture model ec16 (the rebuildable LM fixture, D-671/672) + 100 seeded
collision-free positions playout-generated to ec16.
"""

import unittest

import numpy as np

from reversi.board import (Bitboard, bitboard_count, flips_of_move, initial_game_position,
                           legal_moves_of, make_position)
from reversi.lm.client import make_evaluation_function_array
from reversi.lm.model_weights import model_weights_read_file
from reversi.lm.multi_ply_ef import (_ef_leaf_indexes, _ef_leaf_value,
                                      prepare_multi_ply_plan)
from test.reversi.fixtures import require_lm_fixture

FIXTURE = 'rlm_fixture_simple_ec16'
N_POS = 100
SEED = 42


def _playout_to_ec(target_ec, rng):
    """
    A random playout from the initial position to the target empty count (the positions are
    collision-free by construction).
    """
    pos = initial_game_position()
    m, o = pos['mover'], pos['opponent']
    while bitboard_count(m | o) < 64 - target_ec:
        legal = legal_moves_of(m, o)
        if not legal:
            m, o = o, m  # the pass
            continue
        bits = [i for i in range(64) if (legal >> i) & 1]
        sq = bits[int(rng.integers(len(bits)))]
        mv = Bitboard(1) << Bitboard(sq)
        fl = flips_of_move(m, o, mv)
        m, o = o ^ fl, (m ^ fl) | mv
    return make_position(m, o)


class TestMultiPlyEfLeaf(unittest.TestCase):
    """The compiled EF leaf vs the client EF, on the fixture ec16 model."""

    @classmethod
    def setUpClass(cls):
        cls.mw = model_weights_read_file(require_lm_fixture(FIXTURE))
        cls.plan = prepare_multi_ply_plan(cls.mw)
        rng = np.random.default_rng(SEED)
        cls.positions = np.array([_playout_to_ec(cls.mw.ec, rng) for _ in range(N_POS)])

    def test_index_parity_bit_exact(self):
        """
        The compiled index pipeline is the client's: every row bit-exact vs
        feature_set.compute_indexes (the same njit kernels, the same prepared data).
        """
        ref = self.mw.feature_set.compute_indexes(self.positions)
        for i in range(N_POS):
            p = self.positions[i]
            got = _ef_leaf_indexes(p['mover'], p['opponent'], *self.plan[3:])
            np.testing.assert_array_equal(got, ref[i])

    def test_leaf_value_within_measured_bound(self):
        """
        The leaf value is within the D-674 measured bound of the client EF (the numpy
        pairwise sum vs the sequential f32 sum: <= 409 ulp on the linear predictor,
        compressed further by the expit + the affine — 0.05 in Y is a wide safety margin).
        """
        # The factory called directly (a function stored as a class attribute would bind as a
        # method and swallow `self` — the pydantic strict array gate catches it).
        ref = make_evaluation_function_array(self.mw)(self.positions)
        for i in range(N_POS):
            p = self.positions[i]
            got = _ef_leaf_value(p['mover'], p['opponent'], self.mw.w_dense, *self.plan)
            self.assertLessEqual(abs(float(got) - float(ref[i])), 0.05)

    def test_leaf_value_deterministic(self):
        """The compiled leaf is deterministic: two calls return the same f32 bits."""
        p = self.positions[0]
        v1 = _ef_leaf_value(p['mover'], p['opponent'], self.mw.w_dense, *self.plan)
        v2 = _ef_leaf_value(p['mover'], p['opponent'], self.mw.w_dense, *self.plan)
        self.assertEqual(v1, v2)

    def test_plan_dtypes(self):
        """The plan carries the house dtypes (u32 indexes, u64 bitboards, f32 affine)."""
        expanded_offsets, a1, b1, has_intercept, mob_masks, mob_sides, *rest = self.plan
        self.assertEqual(expanded_offsets.dtype, np.uint32)
        self.assertIsInstance(a1, np.float32)
        self.assertIsInstance(b1, np.float32)
        self.assertTrue(has_intercept)
        self.assertEqual(mob_masks.dtype, np.uint64)
        self.assertEqual(mob_sides.dtype, np.uint8)
        for arr in rest[:6]:  # the u32 pattern block (before the int current_col + the u64 3-D)
            self.assertEqual(arr.dtype, np.uint32)
        self.assertEqual(self.plan[-1].dtype, np.uint64)
        self.assertEqual(self.plan[-2].dtype, np.uint64)


if __name__ == '__main__':
    unittest.main()
