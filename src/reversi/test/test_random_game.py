#
# test_random_game.py
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
# How to run the random_game module unit tests.
#
# Run from the workspace root (the directory containing .venv and src).
#
# -0- Activate the environment.
#
# $ source .venv/bin/activate
#
# -1- Run the tests.
#
# time PERF=0 python3 -m unittest reversi.test.test_random_game
#

import unittest

import numpy as np
import numpy.testing as nptest

from reversi.tools.prng import MT19937
from reversi.board import (Move, square_to_str, move_to_str,
                           Bitboard, Position, PositionField,
                           bitboard_to_square_list, bitboard_from_signed_int,
                           bitboard_to_signed_int,
                           bitboard_to_string_list, bitboard_print,
                           bitboard_count, bitboard_bsr,
                           make_position, position_print)

from reversi.random_game import (initial_game_position, choose_random_move)



class TestInitialGame(unittest.TestCase):

    def test_initial_game_position(self):

        expected_mover_squares    = ['E4', 'D5']
        expected_opponent_squares = ['D4', 'E5']

        igp = initial_game_position()

        self.assertIsInstance(igp, np.void)
        expected_dtype = Position
        self.assertEqual(igp.dtype, expected_dtype)

        m = igp['mover']
        o = igp['opponent']

        self.assertIsInstance(m, Bitboard)
        self.assertIsInstance(o, Bitboard)

        get_squares = lambda x: [square_to_str(sq) for sq in bitboard_to_square_list(x)][::-1]

        mover_squares = get_squares(m)
        opponent_squares = get_squares(o)

        self.assertEqual(mover_squares, expected_mover_squares)
        self.assertEqual(opponent_squares, expected_opponent_squares)


class TestChooseRandomMove(unittest.TestCase):

    def setUp(self):
        PRNG_SEED = 93
        self.prng = MT19937(PRNG_SEED)

    def test_choose_random_move(self):

        I = 1_000

        expected_value_options = [
            0x0000000000080000, # D3
            0x0000000004000000, # C4
            0x0000002000000000, # F5
            0x0000100000000000, # E6
        ]

        expected_freqs = np.array([258, 229, 249, 264], dtype=np.uint64)

        igp = initial_game_position()

        freqs = np.zeros(len(expected_value_options), dtype=np.uint64)

        for i in range(I):
            move = choose_random_move(igp, self.prng)
            self.assertIsInstance(move, Bitboard)
            self.assertIn(move, expected_value_options)

            idx = expected_value_options.index(move)
            freqs[idx] += 1

        nptest.assert_array_equal(freqs, expected_freqs)


class TestChooseRandomMoveEC20(unittest.TestCase):
    """
    The fixtures are:
     - prng                      : An MT-19937 pseudo random number generator.
     - test_data_string          : A human readable documentation string.
     - positions                 : Six valid game positions having 20 square empty.
                                   Three are standard, two are pass ones, one is game over.
     - legal_moves_sets          : The legal move set that the mover has as options.
     - opponent_legal_moves_sets : The legal move set offered to the opponent after a pass.
    """

    def setUp(self):
        PRNG_SEED = 93
        self.prng = MT19937(PRNG_SEED)

        self.test_data_string = \
        """
        .   a b c d e f g h
        . 1 . . @ O . @ O .
        . 2 . . . O O O O .
        . 3 . . O O O O @ .
        . 4 @ @ O @ O @ @ @
        . 5 . @ O @ O O @ @
        . 6 . O @ @ @ O O .
        . 7 . . O O O O O O
        . 8 . O . . O . @ O
        legal_moves = ['E1', 'H1', 'B2', 'C2', 'B3', 'H3', 'A6', 'H6', 'A7', 'B7', 'C8', 'D8', 'F8']
        opponent_legal_moves = []

        .   a b c d e f g h
        . 1 O @ @ @ @ @ . .
        . 2 O @ @ O @ @ . .
        . 3 O O O @ @ @ . .
        . 4 O @ @ @ @ @ . @
        . 5 . @ @ @ @ @ @ .
        . 6 . @ . @ @ @ . .
        . 7 . @ @ @ . @ @ @
        . 8 . @ . @ . . . O
        legal_moves = []
        opponent_legal_moves = ['G1', 'G2', 'G3', 'G4', 'A5', 'C6', 'H6', 'E7', 'G8']

        .   a b c d e f g h
        . 1 . . @ @ @ . . .
        . 2 . . . @ @ @ @ @
        . 3 . . @ . @ @ @ .
        . 4 . . @ @ @ O O O
        . 5 . . @ @ @ O @ O
        . 6 @ @ @ @ O O O O
        . 7 . . @ O @ O O O
        . 8 . . O O O O O O
        legal_moves = []
        opponent_legal_moves = ['F1', 'G1', 'B2', 'C2', 'B3', 'D3', 'B4', 'A5', 'B5', 'B7', 'B8']

        .   a b c d e f g h
        . 1 . . O . @ . . O
        . 2 . . @ @ @ . O @
        . 3 . @ @ @ @ @ @ .
        . 4 . @ . O @ @ @ O
        . 5 . . @ O @ @ @ @
        . 6 @ @ O @ O O @ .
        . 7 @ O @ . O . O O
        . 8 @ . . O . O O O
        legal_moves = ['G1', 'F2', 'H3', 'C4', 'D7', 'F7', 'B8', 'C8', 'E8']
        opponent_legal_moves = []

        .   a b c d e f g h
        . 1 @ @ @ @ @ @ @ @
        . 2 @ @ @ @ @ @ @ @
        . 3 @ @ @ @ @ @ @ @
        . 4 @ @ @ @ @ @ @ @
        . 5 @ @ @ @ @ @ @ @
        . 6 @ @ @ @ . . . .
        . 7 . . . . . . . .
        . 8 . . . . . . . .
        legal_moves = []
        opponent_legal_moves = []

        .   a b c d e f g h
        . 1 @ . O . . . . .
        . 2 O O O . O O O .
        . 3 . @ @ @ @ O . .
        . 4 O O @ @ @ O . @
        . 5 @ . . @ @ O @ @
        . 6 . . O @ @ O @ @
        . 7 . . @ @ @ O O @
        . 8 . @ . @ @ O O @
        legal_moves = ['B1', 'D1', 'E1', 'F1', 'G1', 'H1', 'A3', 'G3', 'G4', 'B5', 'C5', 'B6', 'B7']
        opponent_legal_moves = []
        """
        data = np.array([
            ( 4611717676283199524, -7855295674223658936, 3171520399607465616,                   0),
            (  787631300868060734, -9223372036837537535,                   0, 4616334758962544704),
            (    5646387823048732,  -222663607811309568,                   0,  144678150948390496),
            (   73548482186484752, -1670215300554932092, 1596526067978346560,                   0),
            (      17592186044415,                    0,                   0,                   0),
            (-7305726066363072511,  6944590345852188420,     565175824482554,                   0),
        ], dtype=np.int64)

        self.positions = [make_position(bitboard_from_signed_int(im),
                                        bitboard_from_signed_int(io)) for im, io, _, _ in data]

        self.legal_moves_sets = [bitboard_from_signed_int(ilms) for _, _, ilms, _ in data]
        self.opponent_legal_moves_sets = [bitboard_from_signed_int(iolms) for _, _, _, iolms, in data]

        def _pr(i: int) -> None:
            p = self.positions[i]
            lms = self.legal_moves_sets[i]
            legal_moves = bitboard_to_string_list(lms)
            legal_moves.reverse()
            olms = self.opponent_legal_moves_sets[i]
            opponent_legal_moves = bitboard_to_string_list(olms)
            opponent_legal_moves.reverse()
            print()
            print(f"Record n.: {i}")
            position_print(p)
            print(f"legal_moves = {legal_moves}")
            print(f"opponent_legal_moves = {opponent_legal_moves}")

        self.print_record = _pr

    def test_choose_random_move_ec20(self):

        for i, p in enumerate(self.positions):
            expected_move_options = []

            try:
                move_as_bitboard = choose_random_move(p, self.prng)
                self.assertIsInstance(move_as_bitboard, Bitboard)

                lms = self.legal_moves_sets[i]

                n_options = bitboard_count(move_as_bitboard)
                self.assertIn(n_options, [0, 1])

                idx: int = bitboard_bsr(move_as_bitboard)
                if idx == -1:
                    move = Move(64) # Pass move
                else:
                    move = Move(idx)
                move_as_str = move_to_str(move)

                if lms != 0:
                    #: The selected move must be part of the legal move set.
                    self.assertTrue(move_as_bitboard & lms != 0)
                else:
                    #: The only option is pass
                    self.assertTrue(move_as_bitboard == Bitboard(0))

            except AssertionError as e:
                print()
                print(f"Intercepted error: {e}")
                self.print_record(i)
                print(f"Selected move: {move_as_str} (integer value: {move:d})")

                raise
