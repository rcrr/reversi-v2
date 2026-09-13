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
The concurrent WAVE generator (the I-017 T5, D-170) NO-DB
micro-suite: the pick kernel vs the T4 pick (K1), the
CROSS-VALIDATION against the T4 single-game reference
(LAW-1: the bit-exact harvest positions over 63 games at
three ec targets; LAW-2: the phase invariance — same slot,
any lane, any W -> the same trajectory; the W=1 trajectory
incl. a pass-carrying game), the PASS FOLD (LAW-3: the
synthetic corner wall — the pass + the real move in ONE
step, the counter walks once), the DOUBLE-PASS DISCARD
(LAW-4: the constructed non-full deadlock — the lane
coasts, the counter freezes, it respawns at the boundary),
and the run integrity (the quota, the slot uniqueness).
"""

import os
import time
import unittest

import numpy as np

from reversi.board import (make_position, position_legal_moves,
                           position_make_move)
from reversi.lm.hlp_random_play import (PA, build_pick_table,
                                        pick_move, random_play)
from reversi.lm.hlp_wave import (BufferSink, INITIAL_MOVER, INITIAL_OPP,
                                 MAX_EC, _NN, _mt19937_batch,
                                 _mt19937_init, _pick_wave, make_wave,
                                 run_wave, run_wave_g0, step_wave,
                                 step_wave_g0)
from reversi.lm.hlp_wave import _harvest_and_respawn
from reversi.tools.prng import MT19937

TABLE_SEED = 42


def _identity_table() -> np.ndarray:
    """The hand-made table: table[n] = (0, 1, ..., n-1) — the
    pick is the (counter % k)-th set bit (the fully hand-
    computable regime)."""
    table = np.zeros((65, 64), dtype=np.uint8)
    for n in range(1, 65):
        table[n, :n] = np.arange(n, dtype=np.uint8)
    return table


class TestPickKernel(unittest.TestCase):
    """K1: the vectorized ODP-9 pick vs the T4 pick_move —
    the bit-exact kernel equivalence (the wave's semantic
    core)."""

    def test_random_sources_vs_t4(self):
        table = build_pick_table(TABLE_SEED)
        prng = MT19937(9)
        n = 2000
        src = np.array([int(prng.get_uint64()) for _ in range(n)],
                       dtype=np.uint64)
        cnt = np.array(
            [int(prng.random_choice_from_finite_set(100000))
             for _ in range(n)], dtype=np.int64)
        move, step = _pick_wave(src, cnt, table)
        for i in range(n):
            expected, counter2 = pick_move(src[i], table, int(cnt[i]))
            self.assertEqual(int(move[i]), int(expected),
                             f"lane {i}: the pick deviates")
            self.assertEqual(bool(step[i]), counter2 > int(cnt[i]),
                             f"lane {i}: the step flag deviates")

    def test_zero_src_is_pass_no_step(self):
        table = build_pick_table(TABLE_SEED)
        src = np.array([0, 0x5, 0, 1], dtype=np.uint64)
        cnt = np.array([7, 0, 9, 3], dtype=np.int64)
        move, step = _pick_wave(src, cnt, table)
        self.assertEqual([int(x) for x in move], [PA, 0, PA, 0])
        self.assertEqual([bool(x) for x in step], [False, True,
                                                   False, True])

    def test_hand_computed_identity(self):
        # The identity table: the pick is the (counter % k)-th
        # set bit of 0b101 (squares 0 and 2).
        table = _identity_table()
        src = np.array([0b101, 0b101, 0b101], dtype=np.uint64)
        cnt = np.array([0, 1, 2], dtype=np.int64)
        move, _ = _pick_wave(src, cnt, table)
        self.assertEqual([int(x) for x in move], [0, 2, 0])


class TestCrossValidation(unittest.TestCase):
    """LAW-1/2: the wave replays the SAME per-slot logic as
    the T4 — the bit-exact harvest equivalence and the phase
    invariance."""

    def _t4_position(self, slot: int, ec: int):
        g = random_play(seed=TABLE_SEED, ec_target=ec, counter0=slot)
        return (int(g.position['mover']), int(g.position['opponent']))

    def test_law1_wave_positions_equal_t4(self):
        # 63 games (9 waves of 7) at three ec targets: every
        # harvested (mover, opp) is bit-identical to the T4
        # random_play at the same slot (the dead lanes' slots
        # are simply absent from the sink).
        table = build_pick_table(TABLE_SEED)
        for ec in (55, 40, 20):
            sink = BufferSink()
            run_wave(63, ec, table, 7, sink)
            self.assertEqual(sink.count, 63,
                             f"ec {ec}: the quota is not met")
            M, O, S = sink.flatten()
            self.assertEqual(len(np.unique(S)), 63,
                             f"ec {ec}: the slots are not unique")
            for i in range(63):
                em, eo = self._t4_position(int(S[i]), ec)
                self.assertEqual(int(M[i]), em,
                                 f"ec {ec} slot {int(S[i])}: "
                                 "the mover deviates from the T4")
                self.assertEqual(int(O[i]), eo,
                                 f"ec {ec} slot {int(S[i])}: "
                                 "the opponent deviates from the T4")

    def test_law2_phase_invariance(self):
        # Same slot, any lane index, any W -> the same
        # trajectory (the lanes/threads never enter the
        # semantics): slot 1234 harvested from a W=1 wave and
        # from a W=100 wave (lane 34) is the same position.
        table = build_pick_table(TABLE_SEED)
        sink1 = BufferSink()
        run_wave(1, 20, table, 1, sink1, slot_base=1234)
        sink100 = BufferSink()
        run_wave(100, 20, table, 100, sink100, slot_base=1200)
        M1, O1, S1 = sink1.flatten()
        M100, O100, S100 = sink100.flatten()
        i = int(np.nonzero(S100 == 1234)[0][0])
        self.assertEqual(int(S1[0]), 1234)
        self.assertEqual(int(M100[i]), int(M1[0]),
                         "the W=100 lane 34 deviates from the W=1 "
                         "lane 0 (the phase is not invariant)")
        self.assertEqual(int(O100[i]), int(O1[0]))

    def test_w1_trajectory_with_pass(self):
        # The W=1 trajectory record (the PA is recorded, then
        # the folded real move) equals the T4 move list for a
        # pass-carrying game: the pinned slot 712 (the first
        # pass carrier of the seed-42 scan — passes are
        # ~0.05% of the games) at ec=20: 42 plies (40 real +
        # 2 passes at plies 31 and 33, not consecutive).
        table = build_pick_table(TABLE_SEED)
        pass_slot = 712
        state = make_wave(1, slot_base=pass_slot)
        seq = []
        for _ in range(60 - 20):
            move, pass_mask, dead = step_wave(state, table)
            self.assertFalse(bool(dead[0]),
                             "the pinned slot died (a regression)")
            if bool(pass_mask[0]):
                seq.append(PA)
            seq.append(int(move[0]))
        ref = random_play(seed=TABLE_SEED, ec_target=20,
                          counter0=pass_slot)
        self.assertEqual(seq, [int(x) for x in ref.moves],
                         f"slot {pass_slot}: the wave trajectory "
                         "deviates from the T4 move list")
        self.assertEqual(int(state.mover[0]),
                         int(ref.position['mover']))
        self.assertEqual(int(state.opp[0]),
                         int(ref.position['opponent']))
        # The pinned literals (the pin doubles as the
        # regression guard for the T4 reference).
        self.assertEqual(len(seq), 42)
        self.assertEqual([i for i, x in enumerate(seq)
                          if x == PA], [31, 33])
        self.assertEqual(seq[:6], [29, 21, 34, 42, 20, 37])
        self.assertEqual(int(state.mover[0]), 0x9880a7808080a0f0)
        self.assertEqual(int(state.opp[0]), 0x607d587c7c780800)


class TestPassFoldAndDiscard(unittest.TestCase):
    """LAW-3/4: the pass FOLDS into the step (the counter
    walks once for the folded pass+move pair) and the double
    pass DISCARDS the lane (the coast, the frozen counter,
    the boundary respawn)."""

    def test_law3_pass_wall_folds_in_one_step(self):
        # The T4 synthetic corner wall (the A1+C3 mover corner,
        # the 17-stone opponent wall): the mover has no legal
        # move; after the pass the opponent's legal set is
        # {D3, C4, D4}. The wave lane (identity table,
        # counter 0) does BOTH in one step: the recorded PA +
        # the real move D3 (rank 0), and the counter walks
        # exactly ONCE (the pass does not consume a step).
        table = _identity_table()
        m = np.uint64(0x0000000000040001)
        o = np.uint64(0x01010101010307fe)
        state = make_wave(1, slot_base=0)
        state.mover[0] = m
        state.opp[0] = o
        self.assertEqual(int(position_legal_moves(
            make_position(m, o))), 0)
        move, pass_mask, dead = step_wave(state, table)
        self.assertFalse(bool(dead[0]))
        self.assertTrue(bool(pass_mask[0]))
        self.assertEqual(int(move[0]), 19)  # D3 = bit 19
        self.assertEqual(int(state.counter[0]), 1)
        # The applied position is the T4 [PA, D3] outcome.
        from reversi.lm.hlp_random_play import _play_from
        ref = _play_from(make_position(m, o), table, 0, 44, 0)
        self.assertEqual([int(x) for x in ref.moves][:2],
                         [PA, 19])
        self.assertEqual(int(state.mover[0]),
                         int(ref.position['mover']))
        self.assertEqual(int(state.opp[0]),
                         int(ref.position['opponent']))

    def test_law4_double_pass_discards_and_respawns(self):
        # The constructed non-full deadlock (61 stones, 3 empty
        # — E4, F4, G4; the 57-stone field walled around the
        # empty run, the 4-stone A2..B3 block — NEITHER side
        # has a legal move): the lane DIES on the first step
        # (the coast: the stale state rides the documented
        # PA swap, the frozen counter), is NOT harvested at the
        # boundary, and the wave respawns it with the next
        # slot (the fresh initial position).
        table = build_pick_table(TABLE_SEED)
        m = np.uint64(0xffffffff8ffcfcff)
        o = np.uint64(0x0000000000030300)
        state = make_wave(1, slot_base=0)
        state.mover[0] = m
        state.opp[0] = o
        move, pass_mask, dead = step_wave(state, table)
        self.assertTrue(bool(dead[0]))
        self.assertEqual(int(move[0]), PA)  # the documented swap
        self.assertFalse(bool(state.alive[0]))
        # The stale state is uncorrupted: the occupied squares
        # are invariant; the fields are swapped (the documented
        # PA behaviour on a discarded lane).
        self.assertEqual(int(state.mover[0]) | int(state.opp[0]),
                         int(m) | int(o))
        self.assertEqual(int(state.mover[0]), int(o))
        self.assertEqual(int(state.opp[0]), int(m))
        self.assertEqual(int(state.counter[0]), 0)  # frozen
        self.assertEqual(int(state.dead_total), 1)
        # The coast: the dead lane stays dead, frozen; the
        # second swap brings the fields back.
        move, pass_mask, dead = step_wave(state, table)
        self.assertTrue(bool(dead[0]))
        self.assertEqual(int(state.mover[0]), int(m))
        self.assertEqual(int(state.counter[0]), 0)
        # The boundary: the dead lane is not harvested; the
        # wave respawns it with slot 1 at the initial position.
        sink = BufferSink()
        n = _harvest_and_respawn(state, sink, total=1)
        self.assertEqual(n, 0)
        self.assertEqual(sink.count, 0)
        self.assertEqual(int(state.slot[0]), 1)
        self.assertEqual(int(state.counter[0]), 1)
        self.assertEqual(int(state.mover[0]), int(INITIAL_MOVER))
        self.assertTrue(bool(state.alive[0]))


class TestRunIntegrity(unittest.TestCase):
    """The run-level invariants (the quota, the slot
    provenance, the ec domain)."""

    def test_quota_and_slots(self):
        table = build_pick_table(TABLE_SEED)
        sink = BufferSink()
        info = run_wave(1000, 20, table, 250, sink)
        self.assertEqual(info['harvested'], 1000)
        self.assertEqual(sink.count, 1000)
        M, O, S = sink.flatten()
        self.assertEqual(len(np.unique(S)), 1000,
                         "the slot provenance is not unique")
        self.assertEqual(int(S.min()), 0,
                         "the slot ids do not start at slot_base")
        self.assertLessEqual(int(S.max()), 1000 + info['dead'],
                             "a slot id ran past the consumed slots")
        # Every harvested position is at ec 20 (the lockstep
        # boundary invariant).
        for i in range(1000):
            ec = 64 - int(M[i] | O[i]).bit_count()
            self.assertEqual(ec, 20,
                             f"position {i} is at ec {ec}, not 20")

    def test_ec_target_domain(self):
        table = build_pick_table(TABLE_SEED)
        sink = BufferSink()
        for bad in (-1, 61):
            with self.assertRaises(ValueError):
                run_wave(1, bad, table, 1, sink)
        # ec_target = 60: the initial position IS the arrest
        # (0 steps per wave).
        sink = BufferSink()
        info = run_wave(4, 60, table, 2, sink)
        self.assertEqual(info['waves'], 2)
        M, O, S = sink.flatten()
        self.assertTrue((M == np.uint64(int(INITIAL_MOVER))).all())
        self.assertTrue((O == np.uint64(int(INITIAL_OPP))).all())
        self.assertEqual([int(x) for x in S], [0, 1, 2, 3])


class TestG0Engine(unittest.TestCase):
    """The G0 uniform engine (D-174 — the I-017 corpus
    generator, the D-173 gate verdict's design call)."""

    def test_batch_matches_reference(self):
        # The numba batch-draw kernel vs the golden-pinned
        # reference PRNG (bit-exact — 2000 draws + the twist
        # across the 312-word boundary + the continuation).
        mt = np.zeros(_NN, dtype=np.uint64)
        mti = _mt19937_init(mt, 7)
        ref = MT19937(7)
        draws, mti = _mt19937_batch(mt, mti, 2000)
        for i in range(2000):
            self.assertEqual(int(draws[i]), int(ref.get_uint64()),
                             f"draw {i} deviates from the "
                             "golden-pinned reference")
        draws2, _ = _mt19937_batch(mt, mti, 100)
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
        # the G0 wave (W=1, the same seed, the same ec).
        state = make_wave(1, 0)
        mt = np.zeros(_NN, dtype=np.uint64)
        mti = _mt19937_init(mt, seed)
        wave_seq = []
        for _ in range(S):
            move, _, dead, mti = step_wave_g0(state, mt, mti)
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

    def test_1e6_wall_clock(self):
        table = build_pick_table(TABLE_SEED)
        sink = BufferSink()
        t0 = time.time()
        info = run_wave(1_000_000, 20, table, 1_000_000, sink)
        dt = time.time() - t0
        print(f"\n[benchmark] 1e6 games (W=1e6, ec=20): "
              f"{dt:.1f}s — {1e6 / dt:.0f} games/s — "
              f"waves={info['waves']} dead={info['dead']} "
              f"harvested={info['harvested']}")
        self.assertLess(dt, 600.0,
                        "the 1e6 run exceeded the 10-min guard")

    def test_1e6_g0_wall_clock(self):
        # The G0 corpus engine (D-174) at the gate scale:
        # the same target (the PRNG batch-draw is the only
        # difference from the G1 hot step).
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
