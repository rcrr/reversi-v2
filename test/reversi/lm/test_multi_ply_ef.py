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
Unit tests for the multi-ply evaluation function (D-674: the compiled EF leaf — the index
parity BIT-EXACT vs the client's compute_indexes pipeline + the leaf value contract,
deterministic and within the measured ulp bound of the client EF; D-675: the float32
alpha-beta search + the public factory — the depth ladder over the fixture set + the search
contract + the search discipline on a trivial intercept-only model). No DB: the rebuildable
LM fixtures (D-671/672) + seeded collision-free playout positions.
"""

import unittest

import numpy as np
from pydantic import ValidationError
from scipy.special import expit

from reversi.board import (Bitboard, bitboard_count, flips_of_move, final_value_of,
                           initial_game_position, legal_moves_of, make_position)
from reversi.lm.client import make_evaluation_function_array
from reversi.lm.model_weights import ModelWeights, model_weights_read_file
from reversi.lm.multi_ply_ef import (_ef_leaf_indexes, _ef_leaf_value,
                                      make_evaluation_function, prepare_multi_ply_plan)
from reversi.feature import Feature, FeatureSet
from test.reversi.fixtures import require_lm_fixture
from test.reversi.tags import tier_long

FIXTURE = 'rlm_fixture_simple_ec16'
# The fast-tier scale (the 0.2-0.4 s suite budget): the playout generation + the pure-Python
# oracle are the cost drivers, the compiled search is milliseconds. The full 100-position
# scale lives in the LONG-tier tests.
N_LEAF = 10
N_POS = 20
SEED = 42

# The discipline-test pass position (a scanned playout constant): at ec28 the mover has NO
# legal move, the opponent has 16 — the pass-node scenario of the search discipline.
PASS_MOVER = Bitboard(0x80746AD8BC668500)
PASS_OPPONENT = Bitboard(0x1C0810204080000E)
PASS_EC = 28


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


def _play_moves(p, k, rng):
    """Advance the position by k random legal moves (the playout step, reused)."""
    m, o = p['mover'], p['opponent']
    for _ in range(k):
        legal = legal_moves_of(m, o)
        if not legal:
            m, o = o, m
            continue
        bits = [i for i in range(64) if (legal >> i) & 1]
        sq = bits[int(rng.integers(len(bits)))]
        mv = Bitboard(1) << Bitboard(sq)
        fl = flips_of_move(m, o, mv)
        m, o = o ^ fl, (m ^ fl) | mv
    return make_position(m, o)


def _minimax_oracle(mw, p, plan):
    """
    The INDEPENDENT full-width minimax oracle (pure Python, NO pruning, its own move
    enumeration, the exact WOF at the terminals, the pass negated): the reference the
    alpha-beta SEARCH logic is checked against. The horizon leaves use the compiled EF leaf
    (the D-674 parity test pins it bit-close to the client EF — the oracle's independence is
    in the search logic, the leaf correctness is a separate pinned concern) — 100x cheaper
    than a per-leaf client-EF pydantic call.
    """
    def value(m, o):
        if 64 - int(m | o).bit_count() == mw.ec:
            return float(_ef_leaf_value(m, o, mw.w_dense, *plan))
        legal = legal_moves_of(m, o)
        if not legal:
            if not legal_moves_of(o, m):
                return float(final_value_of(m, o))
            return -value(o, m)
        best = None
        mm = legal
        while mm:
            sq = (int(mm) & -int(mm)).bit_length() - 1  # int ops: no u64 overflow warning
            mv = Bitboard(1) << Bitboard(sq)
            fl = flips_of_move(m, o, mv)
            v = -value(o ^ fl, (m ^ fl) | mv)
            best = v if best is None else max(best, v)
            mm &= mm - Bitboard(1)
        return best

    return value(p['mover'], p['opponent'])


class TestMultiPlyEfLeaf(unittest.TestCase):
    """The compiled EF leaf vs the client EF, on the fixture ec16 model."""

    @classmethod
    def setUpClass(cls):
        cls.mw = model_weights_read_file(require_lm_fixture(FIXTURE))
        cls.plan = prepare_multi_ply_plan(cls.mw)
        rng = np.random.default_rng(SEED)
        cls.positions = np.array([_playout_to_ec(cls.mw.ec, rng) for _ in range(N_LEAF)])

    def test_index_parity_bit_exact(self):
        """
        The compiled index pipeline is the client's: every row bit-exact vs
        feature_set.compute_indexes (the serial transcription, the same prepared data).
        """
        ref = self.mw.feature_set.compute_indexes(self.positions)
        for i in range(N_LEAF):
            p = self.positions[i]
            got = _ef_leaf_indexes(p['mover'], p['opponent'], *self.plan[3:])
            np.testing.assert_array_equal(got, ref[i])

    @unittest.skipUnless(tier_long(), 'Skipping the LONG-tier test (set LONG=1 to run)')
    def test_index_parity_bit_exact_full_scale(self):
        """LONG: the 100-position index parity scale."""
        rng = np.random.default_rng(SEED + 7)
        positions = np.array([_playout_to_ec(self.mw.ec, rng) for _ in range(100)])
        ref = self.mw.feature_set.compute_indexes(positions)
        for i in range(100):
            p = positions[i]
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
        for i in range(N_LEAF):
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


class TestMultiPlyEfSearch(unittest.TestCase):
    """
    The search-based evaluation over the fixture set (D-675): the depth ladder (the depth-0
    anchor bit-exact by delegation, the depths 1-2 vs the independent minimax oracle, the
    depths 3-4 structural in the LONG tier) + the search contract.
    """

    @classmethod
    def setUpClass(cls):
        rng = np.random.default_rng(SEED)
        cls.positions = np.array([_playout_to_ec(20, rng) for _ in range(N_POS)])
        cls.models = {B: model_weights_read_file(require_lm_fixture(f'rlm_fixture_simple_ec{B}'))
                      for B in (20, 19, 18)}

    # --- the depth ladder (the fast scale) ---

    def test_depth0_anchor_bit_exact(self):
        """A == B: the factory delegates to the client EF — bit-exact on all 100 positions."""
        mw = self.models[20]
        got = make_evaluation_function(mw)(self.positions)
        ref = make_evaluation_function_array(mw)(self.positions)
        np.testing.assert_array_equal(got, ref)

    def test_depth1_vs_minimax_oracle(self):
        """A = B+1: 40 positions vs the independent full-width minimax — the pruning
        correctness at one ply (the oracle is pure Python with a pydantic call per node: the
        fast scale is kept small, the full 100 lives in the LONG tier)."""
        mw = self.models[19]
        plan = prepare_multi_ply_plan(mw)
        got = make_evaluation_function(mw)(self.positions[:10])
        ref = np.array([_minimax_oracle(mw, p, plan) for p in self.positions[:10]])
        np.testing.assert_allclose(got, ref, rtol=1e-3, atol=1e-3)

    def test_depth2_vs_minimax_oracle(self):
        """A = B+2: 5 positions vs the oracle (the pruning correctness at two plies)."""
        mw = self.models[18]
        plan = prepare_multi_ply_plan(mw)
        got = make_evaluation_function(mw)(self.positions[:2])
        ref = np.array([_minimax_oracle(mw, p, plan) for p in self.positions[:2]])
        np.testing.assert_allclose(got, ref, rtol=1e-3, atol=1e-3)

    @unittest.skipUnless(tier_long(), 'Skipping the LONG-tier test (set LONG=1 to run)')
    def test_depth12_full_scale_oracle(self):
        """LONG: the full 100-position oracle scale at depths 1 and 2."""
        for B in (19, 18):
            mw = self.models[B]
            plan = prepare_multi_ply_plan(mw)
            got = make_evaluation_function(mw)(self.positions)
            ref = np.array([_minimax_oracle(mw, p, plan) for p in self.positions])
            np.testing.assert_allclose(got, ref, rtol=1e-3, atol=1e-3)

    def test_depth34_structural(self):
        """A = B+3 / B+4: 10 positions each — the structural contract (float32, the batch
        shape, the D-670 range |v| <= R, determinism)."""
        for B in (17, 16):
            with self.subTest(B=B):
                mw = model_weights_read_file(require_lm_fixture(f'rlm_fixture_simple_ec{B}'))
                ef = make_evaluation_function(mw)
                got1 = ef(self.positions[:10])
                got2 = ef(self.positions[:10])
                R = 64.0 / (1.0 - 2.0 * mw.logit_clipping)
                self.assertEqual(got1.dtype, np.float32)
                self.assertEqual(got1.shape, (10,))
                self.assertTrue(np.all(np.abs(got1) <= R + 1e-3))
                np.testing.assert_array_equal(got1, got2)

    @unittest.skipUnless(tier_long(), 'Skipping the LONG-tier test (set LONG=1 to run)')
    def test_depth34_full_scale_structural(self):
        """LONG: the full 100-position structural scale at depths 3 and 4."""
        for B in (17, 16):
            with self.subTest(B=B):
                mw = model_weights_read_file(require_lm_fixture(f'rlm_fixture_simple_ec{B}'))
                ef = make_evaluation_function(mw)
                positions = np.array([_playout_to_ec(20,
                                                      np.random.default_rng(SEED + B))
                                       for _ in range(100)])
                got = ef(positions)
                R = 64.0 / (1.0 - 2.0 * mw.logit_clipping)
                self.assertEqual(got.shape, (100,))
                self.assertTrue(np.all(np.abs(got) <= R + 1e-3))

    # --- the structural contract (the fast scale) ---

    def test_output_range_and_determinism(self):
        """The structural contract: float32 of the batch shape, |v| within the D-670 range,
        and deterministic (two calls bit-equal)."""
        for B in (19, 18):
            with self.subTest(B=B):
                mw = self.models[B]
                ef = make_evaluation_function(mw)
                got1 = ef(self.positions[:4])
                got2 = ef(self.positions[:4])
                self.assertEqual(got1.dtype, np.float32)
                self.assertEqual(got1.shape, (4,))
                R = 64.0 / (1.0 - 2.0 * mw.logit_clipping)
                self.assertTrue(np.all(np.abs(got1) <= R + 1e-3))
                np.testing.assert_array_equal(got1, got2)

    # --- the search contract ---

    def test_below_horizon_raises(self):
        """A position below the model horizon (A < B) is a contract ValueError."""
        mw = self.models[19]
        ef = make_evaluation_function(mw)
        rng = np.random.default_rng(SEED + 1)
        p = _playout_to_ec(20, rng)
        # Play until strictly below the horizon (a pass step would not lower the ec).
        for _ in range(20):
            if bitboard_count(p['mover'] | p['opponent']) < 64 - 18:
                p = _play_moves(p, 1, rng)
            else:
                break
        self.assertLess(64 - int(p['mover'] | p['opponent']).bit_count(), 19)
        with self.assertRaises(ValueError):
            ef(np.array([p]))

    def test_scalar_position_rejected(self):
        """The strict array contract: a scalar Position raises the Pydantic ValidationError."""
        ef = make_evaluation_function(self.models[20])
        with self.assertRaises(ValidationError):
            ef(self.positions[0])

    def test_bare_list_rejected(self):
        """The strict array contract: bare lists raise the Pydantic ValidationError."""
        ef = make_evaluation_function(self.models[20])
        with self.assertRaises(ValidationError):
            ef([[1, 2], [3, 4]])

    def test_empty_batch(self):
        """The empty batch: the empty float32 array."""
        ef = make_evaluation_function(self.models[20])
        empty = np.zeros((0,), dtype=self.positions.dtype)
        out = ef(empty)
        self.assertEqual(out.shape, (0,))
        self.assertEqual(out.dtype, np.float32)


class TestMultiPlyEfDiscipline(unittest.TestCase):
    """
    The search discipline on a trivial INTERCEPT-ONLY model (the hand-computable values):
    every horizon leaf is the constant y0, so a normal depth-1 root is -y0 (the mover's
    children are all y0) and a PASS root is +y0 (the sign flip through the pass) — the
    negamax sign convention and the pass handling, pinned exactly.
    """

    @classmethod
    def setUpClass(cls):
        # The trivial model: intercept only, B = PASS_EC - 1 (the horizon just below the pass).
        fs = FeatureSet('TRIVIAL', Feature.new_intercept(), None, None)
        offsets = np.array([0, 1], dtype=np.uint32)
        w0 = np.float32(np.log(3.0))
        cls.mw = ModelWeights(
            version=1, name='TRIVIAL', ec=PASS_EC - 1, logit_clipping=0.01,
            opt_info={}, training_pop_stats={}, vld_metrics={},
            feature_set=fs, iwmap_feature_offset=offsets, w_dense=np.array([w0],
                                                                           dtype=np.float32))
        # The expected constant leaf (the independent path: the scipy expit + the hlp_zed
        # affine formula):
        a1 = np.float32(-64. / (1. - 2. * cls.mw.logit_clipping))
        b1 = np.float32(128. / (1. - 2. * cls.mw.logit_clipping))
        cls.y0 = float(a1 + expit(np.float32(w0)) * b1)
        rng = np.random.default_rng(SEED)
        cls.normal = _playout_to_ec(PASS_EC, rng)

    def test_normal_root_is_minus_y0(self):
        """A normal depth-1 root: the mover's children are all the constant leaf y0 -> -y0.
        (The factory called per test: a function stored as a class attribute would bind as a
        method and swallow `self`.)"""
        got = float(make_evaluation_function(self.mw)(np.array([self.normal]))[0])
        self.assertAlmostEqual(got, -self.y0, delta=1e-4)

    def test_pass_root_is_plus_y0(self):
        """The pass root: the mover has no move, the pass flips the sign -> +y0."""
        self.assertEqual(legal_moves_of(PASS_MOVER, PASS_OPPONENT), 0)
        lane = np.array([[int(PASS_MOVER), int(PASS_OPPONENT)]], dtype=np.uint64)
        got = float(make_evaluation_function(self.mw)(lane)[0])
        self.assertAlmostEqual(got, self.y0, delta=1e-4)


if __name__ == '__main__':
    unittest.main()
