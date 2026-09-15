#
# test_hlp_wave.py
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
# How to run the hlp_wave module unit tests.
#
# Run from the workspace root (the directory containing .venv and src).
#
# -0- Activate the environment.
#
# $ source .venv/bin/activate
#
# -1- Run the tests.
#
# time python3 -m unittest reversi.test.test_hlp_wave
#
# -2- The LONG tier (the 1e6 benchmark).
#
# time LONG=1 python3 -m unittest reversi.test.test_hlp_wave
#

"""
The concurrent WAVE generator (the I-017 T5, the D-174
corpus generator) NO-DB micro-suite: the G0 engine (the
MT19937 batch draw vs the T3 reference, the W=1 trajectory
vs the scalar, the run integrity + determinism) + the
G0 1e6 benchmark.
"""

import os
import time
import unittest

import numpy as np

from reversi.board import (make_position, position_legal_moves,
                           position_make_move)
from reversi.lm.hlp_wave import (BufferSink, INITIAL_MOVER, INITIAL_OPP,
                                  MAX_EC, make_wave,
                                  run_wave_g0, step_wave_g0)
from reversi.tools.prng import MT19937

class TestG0Engine(unittest.TestCase):
    """The G0 uniform engine (D-174 — the I-017 corpus
    generator, the D-173 gate verdict's design call)."""

    def test_batch_matches_reference(self):
        # The numba batch-draw (the class get_uint64_batch,
        # the single source) vs the golden-pinned reference
        # PRNG (bit-exact — 2000 draws + the twist across the
        # 312-word boundary + the continuation).
        batch_gen = MT19937(7)
        ref = MT19937(7)
        draws = batch_gen.get_uint64_batch(2000)
        for i in range(2000):
            self.assertEqual(int(draws[i]), int(ref.get_uint64()),
                             f"draw {i} deviates from the "
                             "golden-pinned reference")
        draws2 = batch_gen.get_uint64_batch(100)
        for i in range(100):
            self.assertEqual(int(draws2[i]), int(ref.get_uint64()))

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

    def test_w1_trajectory_vs_scalar(self):
        # The W=1 G0 wave vs the scalar G0 reference loop
        # (the same stream discipline: one draw per step,
        # the pass folded into the step — the pass lane's
        # move from the swapped side, the dead lane's draw
        # consumed) — the moves + the final position are
        # bit-exact.
        seed = 23
        ec = 50
        S = MAX_EC - ec
        ref = MT19937(seed)
        m, o = int(INITIAL_MOVER), int(INITIAL_OPP)
        seq = []
        for _ in range(S):
            pos = make_position(np.uint64(m), np.uint64(o))
            lm = int(position_legal_moves(pos))
            lo = int(position_legal_moves(
                make_position(np.uint64(o), np.uint64(m))))
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
            p = position_make_move(pos if lm else
                                   make_position(np.uint64(m),
                                                 np.uint64(o)),
                                   np.uint8(pick))
            m, o = int(p['mover']), int(p['opponent'])
            seq.append(pick)
        # the G0 wave (W=1, the same seed, the same ec) —
        # the stream lives in the class (the D-195).
        state = make_wave(1, 0)
        prng = MT19937(seed)
        wave_seq = []
        for _ in range(S):
            move, _, dead = step_wave_g0(state, prng)
            if bool(dead[0]):
                break
            wave_seq.append(int(move[0]))
        self.assertEqual(wave_seq, seq,
                         "the W=1 G0 wave deviates from the "
                         "scalar reference (the stream "
                         "discipline or the pick)")
        self.assertEqual(int(state.mover[0]), int(m))
        self.assertEqual(int(state.opp[0]), int(o))

    def test_run_integrity_and_determinism(self):
        # 1000 games (W=250, ec=20): the quota, the unique
        # slots, the ec target (64 - popcount(mover|opp) ==
        # 20 for every harvested position), and the
        # determinism (the same seed + slot_base replays
        # bit-exactly).
        sink = BufferSink()
        info = run_wave_g0(1000, 20, 42, 250, sink)
        self.assertEqual(info['harvested'], 1000)
        M, O, slot = sink.flatten()
        self.assertEqual(slot.size, 1000)
        self.assertEqual(len(np.unique(slot)), 1000)
        occ = M | O
        for i in range(1000):
            ec_i = 64 - int(occ[i]).bit_count()
            self.assertEqual(ec_i, 20,
                             f"harvested position {i} is at "
                             f"ec {ec_i}, not 20")
        # the determinism: the second identical run
        # (same seed, same slot_base) replays bit-exactly.
        sink2 = BufferSink()
        run_wave_g0(1000, 20, 42, 250, sink2)
        M2, O2, slot2 = sink2.flatten()
        np.testing.assert_array_equal(M, M2)
        np.testing.assert_array_equal(O, O2)
        np.testing.assert_array_equal(slot, slot2)
        # a different seed changes the stream (the harvest
        # differs — the guard against a frozen generator).
        sink3 = BufferSink()
        run_wave_g0(1000, 20, 43, 250, sink3)
        M3, _, _ = sink3.flatten()
        self.assertFalse(np.array_equal(M, M3),
                         "seed 43 == seed 42 harvest: the "
                         "stream is not consumed")


@unittest.skipUnless(os.environ.get('LONG') == '1',
                     "Skipping the 1e6 benchmark (set LONG=1 to run)")
class TestBenchmark(unittest.TestCase):
    """The 1e6 benchmark (the gate scale): the target is
    well under the T4 Python rate (the doc's 20-60 min) —
    the printed wall time is the deliverable; the assertion
    is a generous order-of-magnitude guard."""

    def test_1e6_g0_wall_clock(self):
        # The G0 corpus engine (D-174) at the gate scale:
        # the 1e6 target, ec=20, seed 42.
        sink = BufferSink()
        t0 = time.time()
        info = run_wave_g0(1_000_000, 20, 42, 1_000_000, sink)
        dt = time.time() - t0
        print(f"\n[benchmark] 1e6 G0 games (W=1e6, ec=20, "
              f"seed 42): {dt:.1f}s — {1e6 / dt:.0f} games/s"
              f" — waves={info['waves']} dead={info['dead']}"
              f" harvested={info['harvested']}")
        self.assertLess(dt, 600.0,
                        "the 1e6 G0 run exceeded the 10-min "
                        "guard")


if __name__ == '__main__':
    unittest.main()
