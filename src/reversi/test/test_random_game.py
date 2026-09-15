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
from reversi.board import (square_to_str,
                           Bitboard, Position, PositionField,
                           bitboard_to_square_list)

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
