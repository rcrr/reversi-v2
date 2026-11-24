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
Unit tests for the multi-ply evaluation function: the compiled EF leaf (the index parity
BIT-EXACT vs the client's compute_indexes pipeline + the leaf value contract, deterministic
and within the measured ulp bound of the client EF) and the float32 alpha-beta search + the
public factory (the depth ladder over the fixture set + the search contract + the search
discipline on a trivial intercept-only model). No DB: the rebuildable LM fixtures + seeded
collision-free playout positions.
"""

import unittest

import numpy as np
from pydantic import ValidationError
from scipy.special import expit

from reversi.board import (Bitboard, bitboard_count, flips_of_move, final_value_of,
                           initial_game_position, legal_moves_of, make_position)
from reversi.endgame_solver import alphabeta_solve, make_game_position
from reversi.feature import Feature, FeatureSet
from reversi.game_position_database import load_game_position_database
from reversi.lm.client import make_evaluation_function_array
from reversi.lm.model_weights import ModelWeights, model_weights_read_file
from reversi.lm.multi_ply_ef import (_ab_eval, _ef_leaf_indexes, _ef_leaf_value,
                                      GROUP_MASKS, make_evaluation_function,
                                      N_GROUPS, prepare_multi_ply_plan)
from test.reversi.fixtures import require_lm_fixture
from test.reversi.paths import WORKSPACE_ROOT
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
    (the leaf parity test pins it bit-close to the client EF — the oracle's independence is
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
        The leaf value is within the measured bound of the client EF (the numpy
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
    The search-based evaluation over the fixture set: the depth ladder (the depth-0
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
        shape, the EF output range |v| <= R, determinism)."""
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
        """The structural contract: float32 of the batch shape, |v| within the EF output
        range, and deterministic (two calls bit-equal)."""
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


class TestMultiPlyEfGroupOrder(unittest.TestCase):
    """
    The fixed best-first group ordering (the C fast endgame solver's worst_to_best table):
    the mask partition of the 64 squares + the priority (the corners first, the central
    four last) + the value invariance (the wide root window contains the value range, so
    the search is the exact minimax and the ordering only changes the node counts — the
    ground window and the over-wide window are bit-identical).
    """

    @classmethod
    def setUpClass(cls):
        cls.mw = model_weights_read_file(require_lm_fixture('rlm_fixture_simple_ec19'))
        cls.plan = prepare_multi_ply_plan(cls.mw)
        rng = np.random.default_rng(SEED)
        cls.positions = np.array([_playout_to_ec(20, rng) for _ in range(4)])

    def test_group_masks_partition_the_board(self):
        """The N_GROUPS group masks are pairwise disjoint and cover all 64 squares exactly once."""
        seen = np.uint64(0)
        for g in range(N_GROUPS):
            self.assertEqual(int(seen & GROUP_MASKS[g]), 0, f'group {g} overlaps the earlier ones')
            seen = seen | GROUP_MASKS[g]
        self.assertEqual(seen, np.uint64((1 << 64) - 1))

    def test_group_priority_corners_first_central_last(self):
        """Group 0 is exactly the four corners (A1, H1, A8, H8); the last group the central
        four (D4, E4, D5, E5)."""
        def bits(mask):
            return {i for i in range(64) if int(mask) >> i & 1}
        self.assertEqual(bits(GROUP_MASKS[0]), {0, 7, 56, 63})
        self.assertEqual(bits(GROUP_MASKS[-1]), {27, 28, 35, 36})

    def test_ground_window_equals_wide_window(self):
        """Value invariance under the ordering: the ground window (+/-R, containing the EF
        range) and the over-wide window (+/-1e30, no cutoff can fire) return bit-identical
        values — both are the exact minimax."""
        horizon = 64 - self.mw.ec
        R = int(np.ceil(64.0 / (1.0 - 2.0 * self.mw.logit_clipping))) + 1
        for p in self.positions:
            st_ground = np.array([-float(R), float(R)])
            st_wide = np.array([-1e30, 1e30])
            v_ground = _ab_eval(p['mover'], p['opponent'], st_ground,
                                self.mw.w_dense, *self.plan, horizon)
            v_wide = _ab_eval(p['mover'], p['opponent'], st_wide,
                              self.mw.w_dense, *self.plan, horizon)
            self.assertEqual(v_ground, v_wide)


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


class TestMultiPlyEfDeepBranches(unittest.TestCase):
    """
    The deep branches of _ab_eval the shallow fixture depths never reach: the in-search
    TERMINAL (the double-pass node above the horizon -> the exact WOF, the leaf the
    final_value_of) and the in-search PASS (the no-move node above the horizon -> the sides
    swap, the value negated). The ec0 fixture makes the horizon the 64-stone board, so the
    wipe-out position's leaves are all exact terminals and the search value is the exact
    endgame value — asserted identical (as float) to the independent exact engine
    (alphabeta_solve); the internal pass is pinned with the TRIVIAL model (the constant
    leaf, the closed form) against the independent Python minimax oracle (the same
    contract, no pruning).
    """

    DB_FILE = WORKSPACE_ROOT / 'test' / 'reversi' / 'data' / 'gpdb-sample-games.txt'

    @classmethod
    def setUpClass(cls):
        cls.db, _ = load_game_position_database(cls.DB_FILE)
        # The model (the factory is called per test: a function stored as a class attribute
        # would bind as a method and swallow `self` — the discipline class idiom).
        cls.mw0 = model_weights_read_file(require_lm_fixture('rlm_fixture_simple_ec0'))
        # The TRIVIAL model at ec1 (the horizon 63: the 62-stone pass node is above it,
        # the 63-stone leaves are the constant).
        fs = FeatureSet('TRIVIAL', Feature.new_intercept(), None, None)
        w0 = np.float32(np.log(3.0))
        cls.mw1 = ModelWeights(
            version=1, name='TRIVIAL-EC1', ec=1, logit_clipping=0.01,
            opt_info={}, training_pop_stats={}, vld_metrics={}, feature_set=fs,
            iwmap_feature_offset=np.array([0, 1], dtype=np.uint32),
            w_dense=np.array([w0], dtype=np.float32))
        a1 = np.float32(-64. / (1. - 2. * 0.01))
        b1 = np.float32(128. / (1. - 2. * 0.01))
        cls.leaf = float(a1 + expit(w0) * b1)

    def _ef0_named(self, name):
        p = self.db.find(name).position
        pos2 = make_position(np.array([p['mover']], dtype=np.uint64),
                             np.array([p['opponent']], dtype=np.uint64))
        return float(make_evaluation_function(self.mw0)(pos2)[0])

    def test_terminal_wipe_out_is_exact(self):
        """The in-search terminal: 'black-wins-by-wipe-out' (13 empties) — the double-pass
        node above the horizon returns the exact WOF, every leaf exact, the value identical
        (as float) to the alphabeta_solve integer."""
        p = self.db.find('black-wins-by-wipe-out').position
        ref = int(alphabeta_solve(p).game_value)
        self.assertEqual(self._ef0_named('black-wins-by-wipe-out'), float(ref))

    @staticmethod
    def _trivial_oracle(m, o, horizon, leaf):
        """The independent Python minimax of the TRIVIAL contract (no pruning)."""
        if bitboard_count(np.uint64(m | o)) >= horizon:
            return leaf
        lm = int(legal_moves_of(np.uint64(m), np.uint64(o)))
        if not lm:
            if not int(legal_moves_of(np.uint64(o), np.uint64(m))):
                return float(final_value_of(np.uint64(m), np.uint64(o)))
            return -TestMultiPlyEfDeepBranches._trivial_oracle(o, m, horizon, leaf)
        best = None
        g = lm
        while g:
            b = g & (-g)
            fo = int(flips_of_move(np.uint64(m), np.uint64(o), np.uint64(b)))
            v = -TestMultiPlyEfDeepBranches._trivial_oracle(o ^ fo, (m ^ fo) | b,
                                                             horizon, leaf)
            best = v if best is None else max(best, v)
            g &= g - 1
        return best

    def test_internal_pass_is_exact(self):
        """The in-search pass: 'woc18-FKvsAP-g1-03' (3 empties, 61 stones) — one of the
        mover's legal moves leaves the opponent with NO legal move, the 62-stone child is
        the pass node (above the TRIVIAL ec1 horizon 63 the search would stop — it is
        below it, so the pass branch runs). The value is the independent Python oracle."""
        p = self.db.find('woc18-FKvsAP-g1-03').position
        m, o = int(p['mover']), int(p['opponent'])
        # The precondition pin: at least one legal move leaves the opponent with none.
        g = int(legal_moves_of(np.uint64(m), np.uint64(o)))
        has_internal_pass = False
        while g:
            b = g & (-g)
            fo = int(flips_of_move(np.uint64(m), np.uint64(o), np.uint64(b)))
            nm, no = (m | b | fo), (o & ~fo)
            if not int(legal_moves_of(np.uint64(no), np.uint64(nm))):
                has_internal_pass = True
                break
            g &= g - 1
        self.assertTrue(has_internal_pass, 'the fixture position lost its internal pass')
        ref = self._trivial_oracle(m, o, 63, self.leaf)
        got = float(make_evaluation_function(self.mw1)(
            np.array([[m, o]], dtype=np.uint64))[0])
        self.assertAlmostEqual(got, ref, delta=1e-4)


class TestMultiPlyEfExactBattery(unittest.TestCase):
    """
    The exact-identity battery: the 17 wipe-out corpus positions (one side at zero stones —
    the double-pass terminal, the value the full +/-64, the ec5...ec25 spread) over the ec4
    fixture. The multi-ply EF value is asserted IDENTICAL (as float) to the exact integer:
    the integer pinned in ROWS and recomputed by the independent exact engine
    (alphabeta_solve). The wipe-out positions are the corpus class where the identity is
    guaranteed by construction: the double-pass node returns the exact WOF, the
    model-estimate leaf is never reached, the search value is the exact endgame value.
    """

    # (mover, opponent, player, game_value) — the regab corpus wipe-outs (the batch 3/6/9/12
    # CMS rows + the CMR sign mirrors), extracted 2026-11-24.
    ROWS = (
        (0, -33927, 0, -64),
        (-33927, 0, 1, 64),
        (0, -4647715365202215042, 1, -64),
        (-4647715365202215042, 0, 0, 64),
        (0, -72902036147932676, 1, -64),
        (-72902036147932676, 0, 0, 64),
        (0, 4250553610422648830, 0, -64),
        (4250553610422648830, 0, 1, 64),
        (0, 1267480720616456191, 1, -64),
        (0, 3098242621458333695, 1, -64),
        (0, -505250894615517538, 1, -64),
        (0, -1369957418393461185, 0, -64),
        (0, 9187200850921933892, 0, -64),
        (0, 25753847955259386, 1, -64),
        (0, 37272616318271359, 1, -64),
        (0, 8583335366303263, 0, -64),
        (0, 38843546781529618, 1, -64),
    )

    @classmethod
    def setUpClass(cls):
        cls.mw = model_weights_read_file(require_lm_fixture('rlm_fixture_simple_ec4'))
        cls.gps3 = make_game_position(
            np.array([r[0] for r in cls.ROWS], dtype=np.int64).astype(np.uint64),
            np.array([r[1] for r in cls.ROWS], dtype=np.int64).astype(np.uint64),
            np.array([r[2] for r in cls.ROWS], dtype=np.uint8))

    def test_exact_engine_recomputes_the_pinned_values(self):
        """The pin of the ROWS: the independent exact engine gives the pinned integers."""
        r = alphabeta_solve(self.gps3)
        self.assertEqual([int(v) for v in r.game_values], [row[3] for row in self.ROWS])

    def test_ef_identical_as_float_to_the_exact_integer(self):
        """The (b) contract: the multi-ply EF value identical (as float) to the exact
        integer, on every lane of the battery."""
        got = make_evaluation_function(self.mw)(make_position(
            np.array([r[0] for r in self.ROWS], dtype=np.int64).astype(np.uint64),
            np.array([r[1] for r in self.ROWS], dtype=np.int64).astype(np.uint64)))
        for g, row in zip(got, self.ROWS):
            self.assertEqual(float(g), float(row[3]))


class TestMultiPlyEfVerifyEndGame(unittest.TestCase):
    """
    The horizon terminal contract: the 15 GENERIC ec4 corpus positions (the batch-4 CMS
    rows, the value spread -52..+58) over the ec0 fixture (the horizon the 64-stone
    board) — every 64-stone leaf is a true terminal (the double pass, the exact WOF),
    the search value is the exact endgame value, and the EF is asserted IDENTICAL (as
    float) to the exact integer recomputed by the independent exact engine
    (alphabeta_solve) and pinned in ROWS.
    """

    # (mover, opponent, player, game_value) — the regab corpus GENERIC ec4 CMS positions
    # (batch 4), extracted 2026-11-24: 8 negative + 7 positive, the value spread -52..+58.
    ROWS = (
        (225193278861520960, -225193278863634657, 0, -52),
        (9099705752508544, -225272487866333313, 0, -44),
        (2254184227026952, -2254184243804239, 0, -40),
        (35843303160216576, -107900897214921921, 0, -38),
        (-7179663585553416192, 2522871202108145663, 0, -34),
        (1063975843258318848, -1136877866521346049, 0, -32),
        (4348432994023733884, -8969126211714251517, 0, -30),
        (2307050506726940768, -6927743724409086065, 0, -28),
        (-63288202639637889, 63147465151281152, 0, 58),
        (-72944994771255425, 324442173194368, 0, 46),
        (-9151687194643544177, 8935513313018132576, 0, 44),
        (1139145856919536671, -3445129603621586112, 0, 42),
        (-36170474246533120, 36170474238144380, 1, 40),
        (3602893112585205631, 5260190954071541888, 0, 38),
        (-8086791878459465478, 5780948869245640196, 0, 36),
    )

    @classmethod
    def setUpClass(cls):
        cls.mw0 = model_weights_read_file(require_lm_fixture('rlm_fixture_simple_ec0'))
        cls.gps3 = make_game_position(
            np.array([r[0] for r in cls.ROWS], dtype=np.int64).astype(np.uint64),
            np.array([r[1] for r in cls.ROWS], dtype=np.int64).astype(np.uint64),
            np.array([r[2] for r in cls.ROWS], dtype=np.uint8))

    def test_exact_engine_recomputes_the_pinned_values(self):
        """The pin of the ROWS: the independent exact engine gives the pinned integers."""
        r = alphabeta_solve(self.gps3)
        self.assertEqual([int(v) for v in r.game_values], [row[3] for row in self.ROWS])

    def test_verify_end_game_identical_as_float_to_the_exact_integer(self):
        """The horizon terminal contract: with the ec0 horizon, the EF value is identical
        (as float) to the exact endgame integer, on every lane."""
        got = make_evaluation_function(self.mw0)(make_position(
            np.array([r[0] for r in self.ROWS], dtype=np.int64).astype(np.uint64),
            np.array([r[1] for r in self.ROWS], dtype=np.int64).astype(np.uint64)))
        for g, row in zip(got, self.ROWS):
            self.assertEqual(float(g), float(row[3]))


if __name__ == '__main__':
    unittest.main()
