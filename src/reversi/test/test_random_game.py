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

from pydantic import ValidationError

from reversi.tools.prng import MT19937
from reversi.board import (Move, square_to_str, move_to_str,
                           Bitboard, Position, PositionField,
                           bitboard_to_square_list, bitboard_from_signed_int,
                           bitboard_to_signed_int,
                           bitboard_to_string_list, bitboard_print,
                           bitboard_count, bitboard_bsr,
                           make_position, position_flips, position_print,
                           position_legal_moves_count, position_empty_count,
                           position_hash, initial_game_position)

from reversi.random_game import (random_game_choose_move,
                                 random_game_make_move,
                                 random_game_play_path)



class TestRandomGameChooseMoveArray(unittest.TestCase):
    """
    random_game_choose_move, the array case (D-219): the batch pick
    over a 1-D PositionArray with the ONE injected prng stream —
    bit-identical to the sequential scalar processing (one draw per
    non-empty legal set, no draw for a pass). The fixtures are the
    six EC20 positions (three standard, two pass, one game over) +
    the initial position: a mixed batch with 13/0/0/9/0/13/4 legal
    options.
    """

    def setUp(self):
        PRNG_SEED = 93
        self.seed = PRNG_SEED
        data = np.array([
            ( 4611717676283199524, -7855295674223658936),
            (  787631300868060734, -9223372036837537535),
            (    5646387823048732,  -222663607811309568),
            (   73548482186484752, -1670215300554932092),
            (      17592186044415,                    0),
            (-7305726066363072511,  6944590345852188420),
        ], dtype=np.int64)
        self.positions = [make_position(bitboard_from_signed_int(im),
                                        bitboard_from_signed_int(io))
                          for im, io in data]
        self.positions.append(initial_game_position())
        self.movers = np.array([int(bitboard_to_signed_int(q['mover']))
                                for q in self.positions], dtype=np.int64)
        self.opponents = np.array([int(bitboard_to_signed_int(q['opponent']))
                                   for q in self.positions], dtype=np.int64)

    def _batch(self):
        return make_position(bitboard_from_signed_int(self.movers),
                             bitboard_from_signed_int(self.opponents))

    def test_array_matches_sequential_scalar(self):
        # The regina: the array call on a fresh stream (seed 93) is
        # bit-identical to the sequential scalar processing of the
        # same positions on a fresh stream with the same seed — and
        # the two streams stay aligned afterwards (the pass elements
        # consumed no draw; one get_uint64_batch fed the kernel).
        prng_seq = MT19937(self.seed)
        seq = [random_game_choose_move(q, prng_seq) for q in self.positions]
        prng_arr = MT19937(self.seed)
        arr = random_game_choose_move(self._batch(), prng_arr)
        self.assertIsInstance(arr, np.ndarray)
        self.assertEqual(arr.dtype, np.uint64)
        self.assertEqual(arr.shape, (len(self.positions),))
        for i in range(len(self.positions)):
            self.assertEqual(arr[i], seq[i])
        self.assertEqual(int(prng_seq.get_uint64()),
                         int(prng_arr.get_uint64()))

    def test_scalar_types(self):
        # The scalar path is unchanged: a Bitboard out.
        h = random_game_choose_move(self.positions[0], MT19937(self.seed))
        self.assertIsInstance(h, Bitboard)

    def test_2d_coercion(self):
        # A (n, 2) uint64 array is coerced to a 1D PositionArray.
        raw_2d = np.array([[int(q['mover']), int(q['opponent'])]
                           for q in self.positions[:2]], dtype=np.uint64)
        computed = random_game_choose_move(raw_2d, MT19937(self.seed))
        expected = random_game_choose_move(self._batch()[:2],
                                           MT19937(self.seed))
        self.assertEqual(computed.shape, (2,))
        self.assertEqual(computed.dtype, np.uint64)
        nptest.assert_array_equal(computed, expected)

    def test_1d_guard(self):
        arr = self._batch()
        with self.assertRaises(ValueError):
            random_game_choose_move(arr.reshape(2, 4), MT19937(self.seed))

    def test_empty_array(self):
        out = random_game_choose_move(np.zeros(0, dtype=Position),
                                      MT19937(self.seed))
        self.assertEqual(out.shape, (0,))
        self.assertEqual(out.dtype, np.uint64)

    def test_wrong_input_rejected(self):
        # Bare Python types are rejected (pydantic, as for the whole
        # dual API).
        with self.assertRaises(ValidationError):
            random_game_choose_move(0, MT19937(self.seed))
        with self.assertRaises(ValidationError):
            random_game_choose_move([0, 0], MT19937(self.seed))


class TestRandomGameMakeMoveArray(unittest.TestCase):
    """
    random_game_make_move, the array case (D-220): the batch
    pick-and-execute over a 1-D PositionArray — the D-219 batch pick
    (the stream contract) composed with the D-140 position_flips
    (a zero element swaps the players, a legal element flips), the
    move codes from popcount(move - 1) (the bit index, and the
    wrap-around of an empty move gives 64 = PA). The fixtures are
    the same mixed batch of TestRandomGameChooseMoveArray.
    """

    def setUp(self):
        PRNG_SEED = 93
        self.seed = PRNG_SEED
        data = np.array([
            ( 4611717676283199524, -7855295674223658936),
            (  787631300868060734, -9223372036837537535),
            (    5646387823048732,  -222663607811309568),
            (   73548482186484752, -1670215300554932092),
            (      17592186044415,                    0),
            (-7305726066363072511,  6944590345852188420),
        ], dtype=np.int64)
        self.positions = [make_position(bitboard_from_signed_int(im),
                                        bitboard_from_signed_int(io))
                          for im, io in data]
        self.positions.append(initial_game_position())
        self.movers = np.array([int(bitboard_to_signed_int(q['mover']))
                                for q in self.positions], dtype=np.int64)
        self.opponents = np.array([int(bitboard_to_signed_int(q['opponent']))
                                   for q in self.positions], dtype=np.int64)

    def _batch(self):
        return make_position(bitboard_from_signed_int(self.movers),
                             bitboard_from_signed_int(self.opponents))

    def test_array_matches_sequential_scalar(self):
        # The regina: the array (positions, codes) on a fresh stream
        # is bit-identical to the sequential scalar processing with
        # the same seed — and the streams stay aligned afterwards.
        prng_seq = MT19937(self.seed)
        seq = [random_game_make_move(q, prng_seq) for q in self.positions]
        prng_arr = MT19937(self.seed)
        arr_p, arr_m = random_game_make_move(self._batch(), prng_arr)
        self.assertIsInstance(arr_p, np.ndarray)
        self.assertEqual(arr_p.dtype, Position)
        self.assertEqual(arr_p.shape, (len(self.positions),))
        self.assertIsInstance(arr_m, np.ndarray)
        self.assertEqual(arr_m.dtype, np.uint8)
        for i in range(len(self.positions)):
            self.assertEqual(int(arr_m[i]), int(seq[i][1]))
            self.assertEqual(int(arr_p[i]['mover']),
                             int(seq[i][0]['mover']))
            self.assertEqual(int(arr_p[i]['opponent']),
                             int(seq[i][0]['opponent']))
        self.assertEqual(int(prng_seq.get_uint64()),
                         int(prng_arr.get_uint64()))

    def test_returned_positions_consistent_with_the_codes(self):
        # For every element, the returned position is exactly the
        # scalar position_flips output for the drawn code (the cross
        # -check through the scalar path; the pass code 64 swaps the
        # players).
        arr_p, arr_m = random_game_make_move(self._batch(),
                                             MT19937(self.seed))
        for i, q in enumerate(self.positions):
            code = int(arr_m[i])
            mv = Bitboard(0) if code == 64 else Bitboard(1) << np.uint64(code)
            _, expected = position_flips(q, mv)
            self.assertEqual(int(arr_p[i]['mover']),
                             int(expected['mover']))
            self.assertEqual(int(arr_p[i]['opponent']),
                             int(expected['opponent']))

    def test_initial_position_code_in_the_legal_set(self):
        # The initial-position element: the drawn code is one of the
        # four legal squares {D3, C4, F5, E6} (19, 26, 37, 44).
        arr_p, arr_m = random_game_make_move(self._batch(),
                                             MT19937(self.seed))
        self.assertIn(int(arr_m[-1]), (19, 26, 37, 44))

    def test_2d_coercion(self):
        raw_2d = np.array([[int(q['mover']), int(q['opponent'])]
                           for q in self.positions[:2]], dtype=np.uint64)
        arr_p, arr_m = random_game_make_move(raw_2d, MT19937(self.seed))
        exp_p, exp_m = random_game_make_move(self._batch()[:2],
                                             MT19937(self.seed))
        self.assertEqual(arr_p.shape, (2,))
        self.assertEqual(arr_m.shape, (2,))
        nptest.assert_array_equal(arr_p, exp_p)
        nptest.assert_array_equal(arr_m, exp_m)

    def test_1d_guard(self):
        arr = self._batch()
        with self.assertRaises(ValueError):
            random_game_make_move(arr.reshape(2, 4), MT19937(self.seed))

    def test_empty_array(self):
        arr_p, arr_m = random_game_make_move(np.zeros(0, dtype=Position),
                                             MT19937(self.seed))
        self.assertEqual(arr_p.shape, (0,))
        self.assertEqual(arr_m.shape, (0,))
        self.assertEqual(arr_m.dtype, np.uint8)

    def test_wrong_input_rejected(self):
        with self.assertRaises(ValidationError):
            random_game_make_move(0, MT19937(self.seed))
        with self.assertRaises(ValidationError):
            random_game_make_move([0, 0], MT19937(self.seed))



class TestRandomGameChooseMove(unittest.TestCase):

    def setUp(self):
        PRNG_SEED = 93
        self.prng = MT19937(PRNG_SEED)

    def test_random_game_choose_move(self):

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
            move = random_game_choose_move(igp, self.prng)
            self.assertIsInstance(move, Bitboard)
            self.assertIn(move, expected_value_options)

            idx = expected_value_options.index(move)
            freqs[idx] += 1

        nptest.assert_array_equal(freqs, expected_freqs)


class TestRandomGameChooseMoveEC20(unittest.TestCase):
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

    def test_random_game_choose_move_ec20(self):

        for i, p in enumerate(self.positions):
            expected_move_options = []

            try:
                move_as_bitboard = random_game_choose_move(p, self.prng)
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

    def test_random_game_choose_move_ec20_equidistributed(self):
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
                    self.assertEqual(random_game_choose_move(p, self.prng),
                                     Bitboard(0))
                continue
            # The available options: the positions of the legal move
            # set's bits.
            avail = [int(sq) for sq in bitboard_to_square_list(lms)]
            freq = {o: 0 for o in avail}
            for _ in range(N):
                m = random_game_choose_move(p, self.prng)
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


class TestRandomGameMakeMove(unittest.TestCase):
    """
    random_game_make_move: it asks random_game_choose_move for the move
    to play, executes it on the position via position_flips, and returns the
    resulting position together with the move that was played. The random
    generation is covered by the random_game_choose_move tests; here the returned
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
            new_p, mv = random_game_make_move(self.position, self.prng)
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
            new_p, mv = random_game_make_move(self.position, self.prng)
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
            new_p, mv = random_game_make_move(self.position, self.prng)
            stones = new_p['mover'] | new_p['opponent']
            self.assertEqual(int(bitboard_count(stones)), fixture_stones + 1)
            self.assertEqual(int(bitboard_count(~stones)), 19)

    def test_no_legal_move_is_a_pass_with_the_swapped_position(self):
        # A position with no legal move: the move is the pass (PA) and the
        # returned position is the swapped position (the players inverted)
        # — never None.
        p = make_position(Bitboard(0x0000000000000001),
                          Bitboard(0x0000000000010000))
        self.assertEqual(int(position_legal_moves_count(p)), 0)
        new_p, mv = random_game_make_move(p, self.prng)
        self.assertEqual(int(mv), 64)
        self.assertIsNotNone(new_p)
        # The players are inverted.
        self.assertEqual(int(bitboard_to_signed_int(new_p['mover'])), 0x10000)
        self.assertEqual(int(bitboard_to_signed_int(new_p['opponent'])), 0x1)


class TestRandomGamePlayPath(unittest.TestCase):

    def setUp(self):
        PRNG_SEED = 141
        self.prng = MT19937(PRNG_SEED)
        self.position = make_position(bitboard_from_signed_int(np.int64(4611717676283199524)),
                                      bitboard_from_signed_int(np.int64(-7855295674223658936)))

    def test_random_game_play_path(self):
        target_ec = 10
        ec0 = position_empty_count(self.position)
        self.assertEqual(ec0, 20)
        rp, ec = random_game_play_path(self.position, target_ec, self.prng)
        self.assertLessEqual(ec, ec0)
        self.assertGreaterEqual(ec, target_ec)

    def test_random_game_play_path_multi_generation(self):
        # N = 10 independent paths played from the same start position
        # (the prng stream advances across the calls — one MT-19937
        # stream, no reseed). Two facts:
        #
        # (1) every path lands EXACTLY on the target (6 real moves
        #     from ec = 20; the game-over cut-off is out of reach this
        #     early — the ec decreases by one per placed disc, the
        #     pass swaps the players without touching it);
        #
        # (2) the N final positions are pairwise DISTINCT — the
        #     position_hash duplicate check (D-213): the hash is a
        #     pure function of the (mover, opponent) pair and it is
        #     view-dependent, so an equal hash means an equal
        #     position with the same player to move.
        NG = 10
        target_ec = 14
        gen = lambda : random_game_play_path(self.position, target_ec, self.prng)
        position_list = [gen() for i in range(NG)]
        for rp, ec in position_list:
            self.assertEqual(ec, target_ec)
        set_of_hash = {position_hash(rp) for rp, _ in position_list}
        self.assertEqual(NG, len(set_of_hash), "Duplicate positions found!")

    def test_random_game_play_path_double_pass_game_over(self):
        # A game-over position (both players moveless, ec = 20 > the
        # target): the double-pass break must stop the loop. The pass
        # is PA = 64 since D-208 — the stale pre-D-208 sentinel
        # (Move(66) = UN) never matched and the loop span forever
        # (the D-218 fix). The two consecutive passes swap the view
        # twice: the returned position is the input one, with its own
        # empty count.
        p = make_position(bitboard_from_signed_int(np.int64(0x00000FFFFFFFFFFF)),
                          Bitboard(0))
        self.assertEqual(int(position_empty_count(p)), 20)
        self.assertEqual(int(position_legal_moves_count(p)), 0)
        rp, ec = random_game_play_path(p, 10, self.prng)
        self.assertEqual(int(ec), 20)
        self.assertEqual(int(bitboard_to_signed_int(rp['mover'])),
                         0x00000FFFFFFFFFFF)
        self.assertEqual(int(bitboard_to_signed_int(rp['opponent'])), 0)

    def test_random_game_play_path_single_pass_continues(self):
        # The mover has no legal move, the opponent has nine: the
        # pass swaps the view and the game continues with the
        # opponent's random moves (the single-pass continuation) —
        # the path terminates at the target ec (deterministic,
        # seed 141).
        p = make_position(bitboard_from_signed_int(np.int64(787631300868060734)),
                          bitboard_from_signed_int(np.int64(-9223372036837537535)))
        self.assertEqual(int(position_legal_moves_count(p)), 0)
        rp, ec = random_game_play_path(p, 10, self.prng)
        self.assertEqual(int(ec), 10)
