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
                           make_position, position_flips, position_print)

from reversi.random_game import (initial_game_position, choose_random_move,
                                 game_position_make_random_move)



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

    def test_choose_random_move_ec20_equidistributed(self):
        # Two facts, over N random moves drawn for EACH of the six
        # positions:
        #
        # (1) every drawn move is VALIDATED: a single legal move when
        #     the position has options, or the pass (an empty move)
        #     when it has none;
        #
        # (2) the frequencies accumulated over the AVAILABLE options
        #     are REASONABLY FLAT — the choices are well spread and
        #     equidistributed. For each option-bearing position the
        #     per-option counts are checked with a chi-square over the
        #     k options (df = k - 1), kept far below the 4-sigma
        #     threshold (the expected chi-square is df, its spread
        #     sqrt(2*df)).
        N = 1000
        for i, p in enumerate(self.positions):
            lms = self.legal_moves_sets[i]
            if lms == 0:
                # No option: every draw must be the pass (an empty
                # move). The condition is validated N times.
                for _ in range(N):
                    self.assertEqual(choose_random_move(p, self.prng),
                                     Bitboard(0))
                continue
            # The available options: the positions of the legal move
            # set's bits.
            avail = [int(sq) for sq in bitboard_to_square_list(lms)]
            freq = {o: 0 for o in avail}
            for _ in range(N):
                m = choose_random_move(p, self.prng)
                # (1) the draw is validated: a single legal move.
                self.assertEqual(int(bitboard_count(m)), 1)
                self.assertTrue((m & lms) != 0)
                freq[int(bitboard_bsr(m))] += 1
            # (2) the per-option counts are reasonably flat.
            k = len(avail)
            expected = N / k
            chi2 = sum((freq[o] - expected) ** 2 for o in avail) / expected
            df = k - 1
            self.assertLess(chi2, df + 4 * (2 * df) ** 0.5,
                            f"position {i}: the per-option distribution "
                            f"is not reasonably flat (chi2={chi2:.1f})")


class TestGamePositionMakeRandomMove(unittest.TestCase):
    """
    game_position_make_random_move: it asks choose_random_move for the move
    to play, executes it on the position via position_flips, and returns the
    resulting position together with the move that was played. The random
    generation is covered by the choose_random_move tests; here the returned
    position is checked for correctness and for consistency with the chosen
    move.

    The fixture is a 20-empty-square position (ec = 20) with exactly two
    legal moves, G1 (bit 6) and G2 (bit 14) — the legal-move set is the
    bitboard 16448; the two resulting boards (the position_flips outputs,
    the next player's view) are the only possible outcomes.
    """

    def setUp(self):
        PRNG_SEED = 93
        self.prng = MT19937(PRNG_SEED)

        # The fixture position (ec = 20).
        self.position = make_position(
            bitboard_from_signed_int(np.int64(4338364875232513536)),
            bitboard_from_signed_int(np.int64(2260734154649662)))
        # The two legal moves (single-bit bitboards) and, for each, the
        # resulting board (the position_flips output).
        self.legal_moves = {
            "G1": bitboard_from_signed_int(np.int64(1) << np.int64(6)),
            "G2": bitboard_from_signed_int(np.int64(1) << np.int64(14)),
        }
        self.expected_board = {}
        for name, bb in self.legal_moves.items():
            _, updated = position_flips(self.position, bb)
            self.expected_board[name] = updated
        # The legal-move set is exactly the two moves (the bitboard 16448).
        self.assertEqual(int(bitboard_to_signed_int(
            self.legal_moves["G1"] | self.legal_moves["G2"])), 16448)

    @staticmethod
    def _board_key(p):
        # A comparable (mover, opponent) signed-int key for a position.
        return (int(bitboard_to_signed_int(p['mover'])),
                int(bitboard_to_signed_int(p['opponent'])))

    def test_n_simulations_give_only_the_two_boards(self):
        # N = 12 random moves from the fixture (seed 93): both legal moves
        # — hence both resulting boards — come out, and ONLY these two
        # boards.
        N = 12
        boards = []
        moves = set()
        for _ in range(N):
            new_p, mv = game_position_make_random_move(self.position, self.prng)
            # The move is one of the two legal moves.
            self.assertIn(int(mv), (6, 14))
            moves.add(int(mv))
            boards.append(new_p)
        # Both moves appear (with N = 12, seed 93: 6 of each).
        self.assertEqual(moves, {6, 14})
        # Only the two resulting boards come out.
        expected = {self._board_key(b) for b in self.expected_board.values()}
        self.assertEqual({self._board_key(b) for b in boards}, expected)

    def test_the_returned_position_is_consistent_with_the_move(self):
        # For every drawn move, the returned position is exactly the board
        # position_flips produces for that move on the fixture — the
        # position and the move are consistent.
        name_of = {6: "G1", 14: "G2"}
        N = 12
        for _ in range(N):
            new_p, mv = game_position_make_random_move(self.position, self.prng)
            exp = self.expected_board[name_of[int(mv)]]
            self.assertEqual(self._board_key(new_p), self._board_key(exp))

    def test_the_returned_position_is_one_move_ahead(self):
        # Each returned position is the fixture with exactly one more stone
        # placed (the move square): the total stone count grows by one and
        # the empty count drops from 20 to 19.
        fixture_stones = int(bitboard_count(
            self.position['mover'] | self.position['opponent']))
        N = 12
        for _ in range(N):
            new_p, mv = game_position_make_random_move(self.position, self.prng)
            stones = new_p['mover'] | new_p['opponent']
            self.assertEqual(int(bitboard_count(stones)), fixture_stones + 1)
            self.assertEqual(int(bitboard_count(~stones)), 19)
