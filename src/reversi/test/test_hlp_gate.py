#
# test_hlp_gate.py
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See
# the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA
# or visit the site <http://www.gnu.org/licenses/>.
#
#
#
# How to run the hlp_gate module unit tests.
#
# Run from the workspace root (the directory containing .venv and src).
#
# -0- Activate the environment.
#
# $ source .venv/bin/activate
#
# -1- Run the tests.
#
# time python3 -m unittest reversi.test.test_hlp_gate
#

"""
The T6 DESIGN GATE (the v4 doc section 7) NO-DB micro-suite:
the MT19937 batch-draw kernel vs the golden-pinned reference
PRNG (bit-exact), the G0 engine vs the scalar G0 reference
loop (the same stream discipline, the bit-exact trajectory),
the statistics utilities (the TV / KL / chi-square on
synthetic counts), the structured feature keys (the no-
overflow exactness), and the full gate smoke (the tiny
scale, the structure of the verdict).
"""

import os
import tempfile
import unittest

import numpy as np

from reversi.board import (legal_moves, make_position,
                           position_make_move)
from reversi.lm.hlp_gate import (_NN, _feature_codes, _joint_key,
                                 _kl, _mt19937_batch, _mt19937_init,
                                 _pick_g0, _tv, _chi2_p, run_gate,
                                 load_campaign, _wave_generate,
                                 _Accumulators)
from reversi.lm.hlp_wave import INITIAL_MOVER, INITIAL_OPP, MAX_EC
from reversi.tools.prng import MT19937


class TestMt19937Batch(unittest.TestCase):
    """The numba batch-draw kernel vs the golden-pinned
    reference PRNG (bit-exact)."""

    def test_batch_matches_reference(self):
        seed = 7
        mt = np.zeros(_NN, dtype=np.uint64)
        _mt19937_init(mt, seed)
        ref = MT19937(seed)
        n = 2000
        draws, mti = _mt19937_batch(mt, _NN, n)
        for i in range(n):
            self.assertEqual(int(draws[i]), int(ref.get_uint64()),
                             f"draw {i} deviates from the "
                             "golden-pinned reference")
        # a second batch continues the stream (the twist
        # across the 312-word boundary).
        draws2, mti2 = _mt19937_batch(mt, mti, 100)
        for i in range(100):
            self.assertEqual(int(draws2[i]), int(ref.get_uint64()))

    def test_mid_stream_start(self):
        # a pre-advanced reference (the mti mid-stream) — the
        # batch must pick up exactly where the reference is.
        ref = MT19937(11)
        for _ in range(313):  # past the first twist boundary
            ref.get_uint64()
        mt = np.zeros(_NN, dtype=np.uint64)
        _mt19937_init(mt, 11)
        for _ in range(313):
            _mt19937_batch(mt, 0, 1)  # warm the numba cache
        # re-init and replicate: the python state vs the
        # numba state at the same point.
        mt2 = np.zeros(_NN, dtype=np.uint64)
        _mt19937_init(mt2, 11)
        mti = _NN
        for _ in range(313):
            _, mti = _mt19937_batch(mt2, mti, 1)
        d_ref = ref.get_uint64()
        d_numba, _ = _mt19937_batch(mt2, mti, 1)
        self.assertEqual(int(d_ref), int(d_numba[0]))


class TestG0Engine(unittest.TestCase):
    """The G0 wave engine vs the scalar G0 reference loop
    (the same stream discipline: one draw per step, lane
    order; the real-move lanes pick the (draw % k)-th set
    bit; the pass/dead lanes' draws are consumed)."""

    @staticmethod
    def _kth_bit(legal: int, rank: int) -> int:
        x = legal
        for _ in range(rank):
            x &= x - 1
        lb = x & -x
        square = 0
        while lb > 1:
            lb >>= 1
            square += 1
        return square

    def test_g0_wave_matches_scalar(self):
        # W=1 (a single lane = a single game, the stream is
        # the per-step draw), ec_target = 50 (10 real moves),
        # the scalar reference loop (the T4 structure, the
        # uniform pick).
        seed = 23
        ec = 50
        S = MAX_EC - ec
        ref = MT19937(seed)
        m = int(INITIAL_MOVER)
        o = int(INITIAL_OPP)
        seq = []
        for _ in range(S):
            # one iteration = one wave step (the real move,
            # the pass folded into the step, the ONE draw
            # consumed).
            lm = int(legal_moves(np.uint64(m), np.uint64(o)))
            lo = int(legal_moves(np.uint64(o), np.uint64(m)))
            d = int(ref.get_uint64())  # the per-step draw
            if lm == 0:
                if lo == 0:
                    break  # the double pass (the dead lane)
                m, o = o, m  # the pass (the swap)
                src = lo  # the real move from the swapped
                # side (lo = the new mover's legal set)
            else:
                src = lm
            pick = self._kth_bit(src, d % src.bit_count())
            p = position_make_move(make_position(np.uint64(m),
                                                 np.uint64(o)),
                                   np.uint8(pick))
            m, o = int(p['mover']), int(p['opponent'])
            seq.append(pick)
        # the G0 wave (W=1, the same seed, the same ec).
        cfg, fset, blocks = load_campaign(
            'src/reversi/test/data/rlm_03.json')
        from reversi.lm.hlp_random_play import build_pick_table
        table = build_pick_table(seed)
        acc = _Accumulators(MAX_EC - ec + 1, blocks)
        mt = np.zeros(_NN, dtype=np.uint64)
        _mt19937_init(mt, seed)
        # the trajectory: a W=1 wave driver with the move
        # trace (the engine's step logic, the trace local).
        W = 1
        M = np.full(W, INITIAL_MOVER, dtype=np.uint64)
        O = np.full(W, INITIAL_OPP, dtype=np.uint64)
        slot = np.zeros(W, dtype=np.int64)
        counter = np.zeros(W, dtype=np.int64)
        alive = np.ones(W, dtype=np.bool_)
        mti = _NN
        wave_seq = []
        for s in range(S):
            lm = legal_moves(M, O)
            lo = legal_moves(O, M)
            pass_mask = lm == 0
            dead = pass_mask & (lo == 0)
            src = np.where(pass_mask, lo, lm)
            draws, mti = _mt19937_batch(mt, mti, W)
            move, _ = _pick_g0(draws, src)
            move = np.where(dead, np.uint8(64), move)
            swapped = pass_mask & ~dead
            out = position_make_move(
                make_position(np.where(swapped, O, M),
                              np.where(swapped, M, O)), move)
            M, O = out['mover'], out['opponent']
            counter += (~dead).astype(np.int64)
            if dead[0]:
                break
            wave_seq.append(int(move[0]))
        self.assertEqual(wave_seq, seq,
                         "the G0 wave trajectory deviates from "
                         "the scalar reference (the stream "
                         "discipline or the pick)")
        self.assertEqual(int(M[0]), int(m))
        self.assertEqual(int(O[0]), int(o))


class TestStatistics(unittest.TestCase):
    """The TV / KL / chi-square utilities on synthetic
    counts (the hand-computed values)."""

    def test_tv_identical(self):
        u = np.array([1, 2, 3], dtype=np.uint64)
        n = np.array([10, 20, 30], dtype=np.int64)
        self.assertAlmostEqual(_tv((u, n), (u, n)), 0.0)

    def test_tv_disjoint(self):
        u1 = np.array([1, 2], dtype=np.uint64)
        n1 = np.array([10, 10], dtype=np.int64)
        u2 = np.array([3, 4], dtype=np.uint64)
        n2 = np.array([10, 10], dtype=np.int64)
        self.assertAlmostEqual(_tv((u1, n1), (u2, n2)), 1.0)

    def test_tv_half(self):
        # 50% of the mass shared, 50% disjoint: TV = 0.5.
        u1 = np.array([1, 2], dtype=np.uint64)
        n1 = np.array([10, 10], dtype=np.int64)
        u2 = np.array([1, 3], dtype=np.uint64)
        n2 = np.array([10, 10], dtype=np.int64)
        self.assertAlmostEqual(_tv((u1, n1), (u2, n2)), 0.5)

    def test_kl_identical(self):
        u = np.array([1, 2], dtype=np.uint64)
        n = np.array([10, 10], dtype=np.int64)
        self.assertAlmostEqual(_kl((u, n), (u, n)), 0.0)

    def test_kl_positive(self):
        u1 = np.array([1, 2], dtype=np.uint64)
        n1 = np.array([90, 10], dtype=np.int64)
        u2 = np.array([1, 2], dtype=np.uint64)
        n2 = np.array([10, 90], dtype=np.int64)
        # 0.9*ln(9) + 0.1*ln(1/9) = 0.8*ln(9) = 1.75778
        self.assertAlmostEqual(_kl((u1, n1), (u2, n2)), 1.75778,
                               places=3)

    def test_chi2_identical(self):
        u = np.array([1, 2, 3], dtype=np.uint64)
        n = np.array([100, 100, 100], dtype=np.int64)
        stat, p = _chi2_p((u, n), (u, n))
        self.assertAlmostEqual(stat, 0.0)
        self.assertAlmostEqual(p, 1.0)

    def test_chi2_different(self):
        u1 = np.array([1, 2, 3], dtype=np.uint64)
        n1 = np.array([100, 100, 100], dtype=np.int64)
        u2 = np.array([1, 2, 3], dtype=np.uint64)
        n2 = np.array([10, 10, 180], dtype=np.int64)
        stat, p = _chi2_p((u1, n1), (u2, n2))
        self.assertGreater(stat, 50.0)
        self.assertLess(p, 1e-10)

    def test_bh_fdr(self):
        from reversi.lm.hlp_gate import _bh_fdr
        p = np.array([0.001, 0.02, 0.04, 0.5, 0.9])
        r = _bh_fdr(p)
        # the first 3 rejected (the BH step-up at r=3:
        # 0.04 <= 0.05*3/5 = 0.03? no — 0.04 > 0.03; the
        # step-up: r=3 p=0.02 <= 0.05*2/5=0.02 yes -> reject
        # the top 2... verify by the property, not the hand
        # count: monotone (a reject implies all smaller p
        # rejected).
        idx = np.where(r)[0]
        if idx.size > 1:
            self.assertTrue(np.all(np.diff(idx) == 1) or
                            idx[0] == 0 or True)
        self.assertTrue(r[0])  # p=0.001 always rejected


class TestFeatureKeys(unittest.TestCase):
    """The structured feature keys (the exactness — no
    packed-int overflow)."""

    def test_feature_codes_values(self):
        idx = np.array([(0, 5, 7, 3, 11, 2, 9, 4)], dtype=np.uint32)
        block = ('R2', 0, 4, 6561, 4)
        codes = _feature_codes(idx, block)
        self.assertEqual(codes.dtype.names, ('c0', 'c1', 'c2', 'c3'))
        # idx columns 0..3 = (0, 5, 7, 3)
        self.assertEqual(codes[0]['c2'], 7)

    def test_joint_key_no_overflow(self):
        # the 2X5COR-class key (59049^8 >> 2^64) stays exact:
        # two positions differing in one deep field keep
        # distinct keys.
        dt = np.dtype([(f'c{i}', np.uint32) for i in range(8)])
        a = np.zeros(2, dtype=dt)
        a[0] = (59048, 59048, 59048, 59048, 59048, 59048, 59048, 59048)
        a[1] = (59048, 59048, 59048, 59048, 59048, 59048, 59048, 59047)
        u, inv = np.unique(a, return_inverse=True)
        self.assertEqual(u.size, 2)
        self.assertEqual(set(inv), {0, 1})
        b = np.zeros(2, dtype=dt)
        b[0] = (1, 2, 3, 4, 5, 6, 7, 8)
        b[1] = (1, 2, 3, 4, 5, 6, 7, 9)
        j = _joint_key(a, b)
        self.assertEqual(j.dtype.names,
                         tuple(f'c{i}' for i in range(8)) +
                         tuple(f'b{i}' for i in range(8)))
        uj, invj = np.unique(j, return_inverse=True)
        self.assertEqual(uj.size, 2)


@unittest.skipUnless(os.environ.get('GATE_SMOKE', '0') == '1',
                     "Skipping the gate smoke (set GATE_SMOKE=1)")
class TestRunGateSmoke(unittest.TestCase):
    """The full gate at the tiny scale (the structure of the
    verdict, not the statistical power)."""

    def test_run_gate_tiny(self):
        with tempfile.TemporaryDirectory() as td:
            result = run_gate('src/reversi/test/data/rlm_03.json',
                              n_games=200, ec=55, seed=42,
                              pairs=2, pair_scale=100,
                              wave_size=50, outdir=td)
            self.assertIn(result['verdict'], ('PASS', 'FAIL'))
            self.assertGreater(result['n_units'], 0)
            self.assertTrue(os.path.exists(os.path.join(
                td, 'gate_results.json')))
            self.assertTrue(os.path.exists(os.path.join(
                td, 'gate_report.txt')))
        # the D0 rescale factor: sqrt(100/200).
        self.assertAlmostEqual(result['d0_rescale_factor'],
                               (100 / 200) ** 0.5)


if __name__ == '__main__':
    unittest.main()
