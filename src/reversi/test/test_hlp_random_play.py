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
# time PERF=0 python3 -m unittest reversi.test.test_hlp_random_play
#

"""
The single-game random play generator (the I-017 T4, D-162) NO-DB
micro-suite: the pick table (the ODP-9 properties), the pick
kernel (the counter walk, the no-consume pass), the initial
position (the 4-stone start), the HAND-COUNTED games (the
identity-table 3-ply trace, the pass branch from the synthetic
corner wall, the full 60-ply game) and the seeded games (the
pinned trajectories + the independent replay).
"""

import unittest

import numpy as np

from reversi.board import (make_position, move_from_str,
                           position_legal_moves, position_make_move)
from reversi.lm.hlp_random_play import (PA, RandomGame, _play_from,
                                        build_pick_table, ec_of,
                                        initial_position, pick_move,
                                        random_play)


def _identity_table() -> np.ndarray:
    """The hand-made table: table[n] = (0, 1, ..., n-1) — the
    pick is the (counter % k)-th set bit (the fully hand-
    computable regime)."""
    table = np.zeros((65, 64), dtype=np.uint8)
    for n in range(1, 65):
        table[n, :n] = np.arange(n, dtype=np.uint8)
    return table


def _sq(name: str) -> int:
    return int(move_from_str(name))


def _replay(g: RandomGame, table: np.ndarray) -> None:
    """The independent replay (the house double-check):
    recompute every ply from the rules (board.py) + the table
    walk, without the module's loop logic."""
    p = initial_position()
    counter = g.counter0
    for i, move in enumerate(g.moves):
        legal = int(position_legal_moves(p))
        if int(move) == PA:
            assert legal == 0, f"ply {i}: a pass with legal moves"
            p = make_position(p['opponent'], p['mover'])
        else:
            expected, counter = pick_move(np.uint64(legal), table, counter)
            assert int(move) == int(expected), (
                f"ply {i}: the pick deviates from the table walk")
            p2 = position_make_move(p, move)
            assert p2 is not None, f"ply {i}: an illegal move"
            p = p2
        assert g.ec_trace[i] == ec_of(p), f"ply {i}: the ec deviates"
    assert int(p['mover']) == int(g.position['mover'])
    assert int(p['opponent']) == int(g.position['opponent'])


class TestPickTable(unittest.TestCase):
    """The ODP-9 table properties (the T6 distribution test
    verifies the seeded rows statistically — here the hard
    properties)."""

    def test_valid_permutations(self):
        table = build_pick_table(42)
        self.assertEqual(table.shape, (65, 64))
        self.assertFalse(table.flags.writeable)
        for n in range(1, 65):
            row = table[n, :n]
            self.assertEqual(sorted(row.tolist()), list(range(n)),
                             f"row {n} is not a permutation of 0..{n-1}")

    def test_reproducible(self):
        a = build_pick_table(42)
        b = build_pick_table(42)
        self.assertTrue(np.array_equal(a, b))
        self.assertFalse(np.array_equal(a, build_pick_table(43)))


class TestPickMove(unittest.TestCase):
    """The pick kernel: the counter walk over the permutation,
    the no-consume pass."""

    def test_kth_set_bit_walk(self):
        table = _identity_table()
        legal = np.uint64(0b101)  # the bits 0 and 2
        # counter 0, 1, 2 -> ranks 0, 1, 0 (the 2 % 2 wrap) -> the
        # lowest, the highest, the lowest set bit.
        picks = [int(pick_move(legal, table, c)[0]) for c in (0, 1, 2)]
        self.assertEqual(picks, [0, 2, 0])

    def test_pass_no_consume(self):
        table = _identity_table()
        move, counter = pick_move(np.uint64(0), table, 5)
        self.assertEqual(int(move), PA)
        self.assertEqual(counter, 5)  # the pass consumes NO step


class TestInitialPosition(unittest.TestCase):
    """The standard start: the D4+E5 / D5+E4 2x2 center, both
    sides with the 4 legal moves (the hand-derived set: E3, F4,
    C5, D6)."""

    def test_the_start(self):
        p = initial_position()
        self.assertEqual(int(p['mover']), 0x0000001008000000)   # D4+E5
        self.assertEqual(int(p['opponent']), 0x0000000810000000)  # D5+E4
        legal = int(position_legal_moves(p))
        # The 4 legal squares, by their bit indexes (E3=20, F4=29,
        # C5=34, D6=43).
        expected = 0
        for name in ('E3', 'F4', 'C5', 'D6'):
            expected |= 1 << _sq(name)
        self.assertEqual(legal, expected)
        # The opponent side has its 4 as well (the symmetric start).
        legal_o = int(position_legal_moves(make_position(
            p['opponent'], p['mover'])))
        self.assertEqual(legal_o.bit_count(), 4)
        # The initial ec: 64 - 4 stones = 60.
        self.assertEqual(ec_of(p), 60)


class TestHandCountedGames(unittest.TestCase):
    """The hand-counted traces: the identity-table regime (the
    pick = the (counter % k)-th set bit, fully hand-computable),
    the pass branch, the full game."""

    def test_identity_short_game(self):
        # 3 plies, ec 60 -> 57: the first pick is hand-derived
        # (k = 4, counter 0, identity -> rank 0 -> the lowest legal
        # square = E3), the rest re-derived by the replay below.
        g = random_play(seed=0, ec_target=57, counter0=0,
                        table=_identity_table())
        self.assertEqual([int(m) for m in g.moves],
                         [_sq('E3'), _sq('F3'), _sq('C5')])
        self.assertEqual(g.ec_trace, [59, 58, 57])
        self.assertEqual(int(g.position['mover']), 0x0000000010200000)
        self.assertEqual(int(g.position['opponent']), 0x0000001c08100000)
        self.assertEqual(g.stopped_by, 'ec')
        self.assertEqual(g.plies, 3)
        _replay(g, _identity_table())

    def test_pass_from_wall_position(self):
        # The synthetic corner wall: the mover's two stones (A1,
        # C3) are fully walled in (the opponent owns row 1, column
        # A, and the B2/C2/B3 ring — verified: the mover has ZERO
        # legal moves, the opponent {D3, C4, D4} after the pass).
        # The loop must play the PA (no counter step), then pick
        # D3 (k = 3, counter 0, identity -> rank 0 -> the lowest).
        m = np.uint64(0x0000000000040001)  # A1 + C3
        o = np.uint64(0x01010101010307fe)  # the 17-stone wall
        p = make_position(m, o)
        self.assertEqual(int(position_legal_moves(p)), 0)
        g = _play_from(p, _identity_table(), 0, 44, 0)
        self.assertEqual([int(x) for x in g.moves], [PA, _sq('D3')])
        self.assertEqual(g.ec_trace, [45, 44])  # the pass keeps ec
        self.assertEqual(g.stopped_by, 'ec')
        self.assertEqual(g.plies, 2)

    def test_full_game(self):
        # Seed 3 played to ec = 0: the board fills (60 real moves
        # from the 4 stones, no pass) — the game-over check fires
        # on the full board (is_game_over: no legal move for
        # either side).
        g = random_play(seed=3, ec_target=0)
        self.assertEqual(g.plies, 60)
        self.assertEqual(g.ec, 0)
        self.assertEqual(g.stopped_by, 'game_over')
        occupied = (int(g.position['mover'])
                    | int(g.position['opponent'])).bit_count()
        self.assertEqual(occupied, 64)
        self.assertEqual(int(g.position['mover']).bit_count(), 35)
        self.assertEqual(int(g.position['opponent']).bit_count(), 29)
        _replay(g, build_pick_table(3))


class TestSeededGames(unittest.TestCase):
    """The seeded games: the pinned trajectories (the determinism
    proof), the counter0 phase shift, the ec domain."""

    def test_seed7_pinned(self):
        g = random_play(seed=7, ec_target=20)
        self.assertEqual(g.plies, 40)
        self.assertEqual(g.ec, 20)
        self.assertEqual(g.stopped_by, 'ec')
        # 40 plies = 40 stones (60 -> 20, no pass on this seed).
        self.assertEqual(len([m for m in g.moves if int(m) != PA]), 40)
        self.assertEqual(int(g.position['mover']), 0x814024f52b158800)
        self.assertEqual(int(g.position['opponent']), 0x0e864b0a544a540e)
        # The first 10 moves (the hand-counted anchor of the
        # trajectory).
        self.assertEqual([int(m) for m in g.moves[:10]],
                         [_sq(n) for n in
                          ('F4', 'D3', 'C2', 'F5', 'D6', 'C5',
                           'G6', 'G5', 'G4', 'H7')])
        _replay(g, build_pick_table(7))

    def test_seed8_differs(self):
        a = random_play(seed=7, ec_target=20)
        b = random_play(seed=8, ec_target=20)
        self.assertNotEqual([int(x) for x in a.moves],
                            [int(x) for x in b.moves])
        self.assertNotEqual(int(b.position['mover']),
                            int(a.position['mover']))
        # The seed-8 pinned tail.
        self.assertEqual(int(b.position['mover']), 0x0204f9da60dc1800)
        self.assertEqual(int(b.position['opponent']), 0x019a04241f2244bc)

    def test_counter0_phase_shifts(self):
        # The T5 slot pin: counter0 is the per-game phase — the
        # same seed, a different start phase, a different first
        # move (rank 0 vs rank 7 % 4 = 3 on the seeded row 4 —
        # distinct permutation values, guaranteed).
        a = random_play(seed=7, ec_target=59)
        b = random_play(seed=7, ec_target=59, counter0=7)
        self.assertEqual([int(x) for x in a.moves],
                         [_sq('F4')])
        self.assertNotEqual(int(b.moves[0]), int(a.moves[0]))
        self.assertEqual(len(b.moves), 1)

    def test_ec_target_domain(self):
        for bad in (-1, 61):
            with self.assertRaises(ValueError):
                random_play(seed=1, ec_target=bad)
        # ec_target >= 60: arrested before the first ply.
        g = random_play(seed=1, ec_target=60)
        self.assertEqual(g.plies, 0)
        self.assertEqual(g.ec, 60)
        self.assertEqual(g.stopped_by, 'ec')


if __name__ == '__main__':
    unittest.main()
