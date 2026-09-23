#
# test_hlp_random_play.py
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
#
#
# How to run the hlp_random_play module unit tests.
#
# Run from the workspace root (the directory containing .venv and src).
#
# -0- Activate the environment.
#
# $ source .venv/bin/activate
#
# -1- Run the tests.
#
# time PERF=0 python3 -m unittest test.reversi.lm.test_hlp_random_play
#

"""
The SU_ANALYSIS frequency data plane (the marginal + the
joint accumulators) NO-DB micro-suite: the ec formula pin
(the window constraint), the initial position (the 4-stone
start), the marginal + the joint accumulators (the streaming
frequency accumulation over the corpus, the play-path
corpus fed chunk-by-chunk).
"""

import unittest

import numpy as np

from reversi.board import (initial_game_position, make_position,
                           move_from_str, position_legal_moves)
from reversi.feature import Feature, FeatureSet
from reversi.lm.hlp_random_play import (
    JointAccumulator, MarginalAccumulator, ec_of, initial_position)
from reversi.mobility import Mobility, MobilitySet
from reversi.pattern import Pattern, PatternSet
from reversi.random_game import random_game_play_path
from reversi.tools.prng import MT19937


def _sq(name: str) -> int:
    return int(move_from_str(name))


def _corpus(n, ec, seed):
    """The random_game play-path corpus (the hlp_wave
    replacement, D-285): n positions at exactly ec (the
    double-pass game-over lanes are dropped, the quota filled
    by the next batch), seed-deterministic — the (mover, opp)
    arrays."""
    prng = MT19937(seed)
    igp = initial_game_position()
    m0, o0 = int(igp['mover']), int(igp['opponent'])
    harvested = 0
    ms, os_ = [], []
    while harvested < n:
        k = n - harvested
        batch = np.column_stack((np.full(k, m0, dtype=np.uint64),
                                 np.full(k, o0, dtype=np.uint64)))
        final, ec_arr = random_game_play_path(batch, ec, prng)
        keep = ec_arr == ec
        ms.append(final[keep]['mover'])
        os_.append(final[keep]['opponent'])
        harvested += int(keep.sum())
    return np.concatenate(ms), np.concatenate(os_)


class TestInitialPosition(unittest.TestCase):
    """The standard start (the official Othello setup): the
    E4+D5 / D4+E5 2x2 center, both sides with the 4 legal moves
    (the hand-derived sets: the mover D3, C4, F5, E6; the
    opponent E3, F4, C5, D6)."""

    def test_the_start(self):
        p = initial_position()
        self.assertEqual(int(p['mover']), 0x0000000810000000)   # E4+D5
        self.assertEqual(int(p['opponent']), 0x0000001008000000)  # D4+E5
        legal = int(position_legal_moves(p))
        # The 4 legal squares, by their bit indexes (D3=19, C4=26,
        # F5=37, E6=44).
        expected = 0
        for name in ('D3', 'C4', 'F5', 'E6'):
            expected |= 1 << _sq(name)
        self.assertEqual(legal, expected)
        # The opponent side has its 4 as well (the symmetric start).
        legal_o = int(position_legal_moves(make_position(
            p['opponent'], p['mover'])))
        self.assertEqual(legal_o.bit_count(), 4)
        # The initial ec: 64 - 4 stones = 60.
        self.assertEqual(ec_of(p), 60)


class TestEcPin(unittest.TestCase):
    """The ec formula pin: ec_of = 64 - popcount(mover
    | opponent) = the count of the empty squares = the DB's
    `empty_count` (the regab extraction filters `empty_count = ec`
    — the "mele con mele" window constraint)."""

    def test_ec_formula_hand_crafted(self):
        # The pin: ec_of = 64 - the occupied squares. Hand-crafted
        # positions (the formula is position-local, no generator
        # needed).
        # The initial position: 4 stones, ec 60.
        p = initial_position()
        self.assertEqual(ec_of(p), 60)
        self.assertEqual(
            (int(p['mover']) | int(p['opponent'])).bit_count(), 4)
        # A mid-board position (24 stones, ec 40).
        p2 = make_position(np.uint64(0x0000000000ffff00),
                           np.uint64(0x00000000ff000000))
        occ2 = (int(p2['mover']) | int(p2['opponent'])).bit_count()
        self.assertEqual(ec_of(p2), 64 - occ2)
        # A full board: 64 stones, ec 0.
        p3 = make_position(np.uint64(0xffffffff00000000),
                           np.uint64(0x00000000ffffffff))
        self.assertEqual(ec_of(p3), 0)


class TestMarginalAccumulator(unittest.TestCase):
    """The streaming marginal accumulator: the per-sub-variable
    (the (feature, instance) column) code -> count over the corpus,
    the dense-bincount / unique-merge split, the hand-counted LMC,
    the chunk-merge."""

    @staticmethod
    def _toy_fset():
        def u(h):
            return np.uint64(int(h, 16))
        return FeatureSet(
            'toy',
            Feature.new_intercept(),
            MobilitySet('mob', [Mobility('LMC',
                                         u('FFFFFFFFFFFFFFFF'),
                                         u('0000000000000000'))]),
            PatternSet('pat', [Pattern('R2', u('000000000000FF00'))]))

    @staticmethod
    def _toy_blocks(fset):
        blocks = []
        col = 1 if (fset.intercept is not None) else 0
        for f in fset.features:
            if f.category in (0, 'intercept') or f.name == 'INTERCEPT':
                continue
            blocks.append((f.name, col, col + int(f.n_instances),
                           int(f.n_configurations),
                           int(f.n_instances)))
            col += int(f.n_instances)
        return blocks

    @staticmethod
    def _toy_corpus(n=300, ec=20, seed=7):
        return _corpus(n, ec, seed)

    def test_lmc_hand_counted(self):
        # The LMC (single-instance, the dense bincount): the code is
        # the mover's legal-move count — the oracle is
        # position_legal_moves (INDEPENDENT of compute_indexes).
        fset = self._toy_fset()
        blocks = self._toy_blocks(fset)
        M, O = self._toy_corpus()
        acc = MarginalAccumulator(fset, blocks)
        acc.add(M, O)
        res = {((name, i)): (nc, codes, counts)
               for (name, i, nc, codes, counts) in acc.result()}
        expected = {}
        for k in range(len(M)):
            p = make_position(M[k], O[k])
            code = int(position_legal_moves(p)).bit_count()
            expected[code] = expected.get(code, 0) + 1
        nc, codes, counts = res[('LMC', 0)]
        self.assertEqual(nc, 65)
        exp_codes = np.array(sorted(expected), dtype=np.uint32)
        exp_counts = np.array([expected[c] for c in sorted(expected)],
                              dtype=np.int64)
        np.testing.assert_array_equal(codes, exp_codes)
        np.testing.assert_array_equal(counts, exp_counts)
        self.assertEqual(int(counts.sum()), len(M))

    def test_pattern_cross_check(self):
        # The R2 inst0 (multi-instance feature, one column): the
        # cross-check against an independent per-position dict count
        # via compute_indexes (the oracle for the code, the manual
        # dict for the count).
        fset = self._toy_fset()
        blocks = self._toy_blocks(fset)
        M, O = self._toy_corpus()
        acc = MarginalAccumulator(fset, blocks)
        acc.add(M, O)
        pa = np.empty(len(M), dtype=np.dtype(
            [('mover', np.uint64), ('opponent', np.uint64)]))
        pa['mover'] = M
        pa['opponent'] = O
        idx = fset.compute_indexes(pa)
        r2_col = 2  # R2 inst0 (after the intercept col 0, LMC col 1)
        expected = {}
        for k in range(len(M)):
            c = int(idx[k, r2_col])
            expected[c] = expected.get(c, 0) + 1
        row = [r for r in acc.result() if r[0] == 'R2' and r[1] == 0][0]
        name, i, nc, codes, counts = row
        self.assertEqual(nc, 6561)
        exp_codes = np.array(sorted(expected), dtype=np.uint32)
        exp_counts = np.array([expected[c] for c in sorted(expected)],
                              dtype=np.int64)
        np.testing.assert_array_equal(codes, exp_codes)
        np.testing.assert_array_equal(counts, exp_counts)
        self.assertEqual(len(codes), len(expected))  # the K_obs
        self.assertLessEqual(len(codes), nc)

    def test_chunk_merge(self):
        # Feeding the corpus in ONE chunk vs TWO chunks: the same
        # marginal (the unique-merge / the dense accumulation are
        # chunk-invariant).
        fset = self._toy_fset()
        blocks = self._toy_blocks(fset)
        M, O = self._toy_corpus(n=400)
        acc1 = MarginalAccumulator(fset, blocks)
        acc1.add(M, O)
        acc2 = MarginalAccumulator(fset, blocks)
        acc2.add(M[:200], O[:200])
        acc2.add(M[200:], O[200:])
        r1, r2 = acc1.result(), acc2.result()
        self.assertEqual(len(r1), len(r2))
        for a, b in zip(r1, r2):
            self.assertEqual(a[0], b[0])
            self.assertEqual(a[1], b[1])
            np.testing.assert_array_equal(a[3], b[3])
            np.testing.assert_array_equal(a[4], b[4])


class TestJointAccumulator(unittest.TestCase):
    """The streaming joint accumulator: the per-requested-pair
    instance×instance (code_i, code_j) -> count, the cross-feature
    + the same-feature (the diagonal is the SU = 1 lock, the
    off-diagonal the anisotropy), the chunk-merge."""

    def _fset(self):
        return TestMarginalAccumulator._toy_fset()

    def _blocks(self):
        return TestMarginalAccumulator._toy_blocks(self._fset())

    def _corpus(self, n=200, ec=20, seed=7):
        return TestMarginalAccumulator._toy_corpus(n, ec, seed)

    @staticmethod
    def _oracle_joint(fset, M, O, ci_col, cj_col):
        """The independent per-position joint oracle (the manual
        dict, the compute_indexes for the codes)."""
        pa = np.empty(len(M), dtype=np.dtype(
            [('mover', np.uint64), ('opponent', np.uint64)]))
        pa['mover'] = M
        pa['opponent'] = O
        idx = fset.compute_indexes(pa)
        od = {}
        for k in range(len(M)):
            key = (int(idx[k, ci_col]), int(idx[k, cj_col]))
            od[key] = od.get(key, 0) + 1
        return od

    def test_cross_feature_joint(self):
        # (LMC, R2): the 4 instance-pairs (0, j), the joint
        # (code_lmc, code_r2_j) -> count vs the independent oracle.
        fset = self._fset()
        blocks = self._blocks()
        M, O = self._corpus()
        ja = JointAccumulator(fset, blocks, [('LMC', 'R2')])
        ja.add(M, O)
        ni, nj, pd = ja.result()[0]
        self.assertEqual((ni, nj), ('LMC', 'R2'))
        self.assertEqual(sorted(pd.keys()),
                         [(0, 0), (0, 1), (0, 2), (0, 3)])
        bi = [b for b in blocks if b[0] == 'LMC'][0]
        bj = [b for b in blocks if b[0] == 'R2'][0]
        for (ii, jj) in pd:
            od = self._oracle_joint(fset, M, O, bi[1] + ii, bj[1] + jj)
            codes_i, codes_j, cnt = pd[(ii, jj)]
            self.assertEqual(int(cnt.sum()), len(M))
            got = {}
            for a, b, c in zip(codes_i, codes_j, cnt):
                got[(int(a), int(b))] = int(c)
            self.assertEqual(got, od)

    def test_same_feature_diagonal(self):
        # (R2, R2): the 16 instance-pairs (4 x 4). The diagonal
        # (ii, ii) is the variable with itself — ZERO off-diagonal
        # entries (code_i == code_j always); the off-diagonal is the
        # anisotropy measure.
        fset = self._fset()
        blocks = self._blocks()
        M, O = self._corpus()
        ja = JointAccumulator(fset, blocks, [('R2', 'R2')])
        ja.add(M, O)
        ni, nj, pd = ja.result()[0]
        self.assertEqual((ni, nj), ('R2', 'R2'))
        self.assertEqual(len(pd), 16)
        for (ii, jj) in pd:
            codes_i, codes_j, cnt = pd[(ii, jj)]
            self.assertEqual(int(cnt.sum()), len(M))
            if ii == jj:
                self.assertEqual(
                    sum(1 for a, b in zip(codes_i, codes_j)
                        if a != b), 0)

    def test_chunk_merge(self):
        # One chunk == two half-chunks (the unique-merge is chunk-
        # invariant, the marginals and the joints alike).
        fset = self._fset()
        blocks = self._blocks()
        M, O = self._corpus(n=300)
        pairs = [('LMC', 'R2'), ('R2', 'R2')]
        ja1 = JointAccumulator(fset, blocks, pairs)
        ja1.add(M, O)
        ja2 = JointAccumulator(fset, blocks, pairs)
        ja2.add(M[:150], O[:150])
        ja2.add(M[150:], O[150:])
        r1, r2 = ja1.result(), ja2.result()
        self.assertEqual(len(r1), len(r2))
        for (ni1, nj1, pd1), (ni2, nj2, pd2) in zip(r1, r2):
            self.assertEqual((ni1, nj1), (ni2, nj2))
            self.assertEqual(set(pd1.keys()), set(pd2.keys()))
            for key in pd1:
                ci1, cj1, cn1 = pd1[key]
                ci2, cj2, cn2 = pd2[key]
                np.testing.assert_array_equal(ci1, ci2)
                np.testing.assert_array_equal(cj1, cj2)
                np.testing.assert_array_equal(cn1, cn2)


class TestPrngIntegration(unittest.TestCase):
    """The PRNG integration test: the full generator with the
    MT19937 seed — the corpus reproducibility (same seed -> the
    same frequency tables, the different seed -> different) + the
    small end-to-end corpus on a 2-feature set (the LMC + the R2),
    the marginals hand-checked against the independent oracle."""

    def _fset(self):
        return TestMarginalAccumulator._toy_fset()

    def _blocks(self):
        return TestMarginalAccumulator._toy_blocks(self._fset())

    def _gen_and_accum(self, n, ec, seed):
        fset = self._fset()
        blocks = self._blocks()
        acc = MarginalAccumulator(fset, blocks)
        M, O = _corpus(n, ec, seed)
        acc.add(M, O)
        return acc.result()

    def test_corpus_reproducibility(self):
        # Same seed -> the SAME frequency tables (bit-exact); the
        # different seed -> different. The play-path generator
        # re-initializes the golden-pinned MT19937 per call (the
        # seed is the corpus seed).
        r1 = self._gen_and_accum(5000, 20, 42)
        r2 = self._gen_and_accum(5000, 20, 42)
        r3 = self._gen_and_accum(5000, 20, 43)
        for a, b in zip(r1, r2):
            np.testing.assert_array_equal(a[3], b[3])  # the codes
            np.testing.assert_array_equal(a[4], b[4])  # the counts
        same_as_43 = all(
            np.array_equal(a[3], b[3]) and np.array_equal(a[4], b[4])
            for a, b in zip(r1, r3))
        self.assertFalse(same_as_43)

    def test_small_end_to_end_marginals(self):
        # The small end-to-end corpus (the play-path corpus ->
        # the accumulator): every sub-variable's sum == N, K_obs <=
        # n_conf, and the LMC marginal hand-checked against the
        # INDEPENDENT oracle (position_legal_moves, NOT
        # compute_indexes).
        n, ec, seed = 2000, 20, 42
        fset = self._fset()
        blocks = self._blocks()
        M, O = _corpus(n, ec, seed)
        acc = MarginalAccumulator(fset, blocks)
        acc.add(M, O)
        res = {((nm, i)): (nc, codes, counts)
               for (nm, i, nc, codes, counts) in acc.result()}
        for (nm, i), (nc, codes, counts) in res.items():
            self.assertEqual(int(counts.sum()), n)
            self.assertLessEqual(len(codes), nc)
        expected = {}
        for k in range(n):
            p = make_position(M[k], O[k])
            code = int(position_legal_moves(p)).bit_count()
            expected[code] = expected.get(code, 0) + 1
        nc, codes, counts = res[('LMC', 0)]
        exp_codes = np.array(sorted(expected), dtype=np.uint32)
        exp_counts = np.array([expected[c] for c in sorted(expected)],
                              dtype=np.int64)
        np.testing.assert_array_equal(codes, exp_codes)
        np.testing.assert_array_equal(counts, exp_counts)


if __name__ == '__main__':
    unittest.main()
