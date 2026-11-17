#
# test_endgame_solver.py
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
#
# How to run the endgame_solver module unit tests.
#
# Run from the workspace root (the directory containing .venv and src).
#
# -0- Activate the environment.
#
# $ source .venv/bin/activate
#
# -1- Run the tests.
#
# time PERF=0 python3 -m unittest test.reversi.test_endgame_solver
#

import dataclasses
import unittest

import numpy as np

from reversi.board import *
from reversi.endgame_solver import *
from reversi.game_position_database import load_game_position_database

from test.reversi.paths import WORKSPACE_ROOT


class TestSolverResult(unittest.TestCase):
    """
    The SolverResult dataclass: the fields and the frozen behaviour.
    """

    def test_fields(self):
        gp = game_position_from_str('b' * 64 + 'b')
        r = SolverResult(game_value=np.int8(3), final_game_position=gp, nodes=10, leafs=3)
        self.assertIsInstance(r.game_value, np.int8)
        self.assertEqual(int(r.game_value), 3)
        self.assertEqual(r.nodes, 10)
        self.assertEqual(r.leafs, 3)
        self.assertEqual(game_position_to_str(r.final_game_position), game_position_to_str(gp))

    def test_frozen(self):
        r = SolverResult(game_value=np.int8(0), final_game_position=game_position_from_str('b' * 64 + 'b'),
                         nodes=1, leafs=1)
        with self.assertRaises(dataclasses.FrozenInstanceError):
            r.nodes = 2


class TestMinimaxSolveMicro(unittest.TestCase):
    """
    minimax_solve on small hand-built endgames: the game value, the final position, and the
    node / leaf counts, all pinned.
    """

    def test_full_board_black_to_move(self):
        r = minimax_solve(game_position_from_str('bbbbbbbb' * 5 + 'wwwwwwww' * 3 + 'b'))
        self.assertEqual(int(r.game_value), 16)
        self.assertEqual(r.nodes, 1)
        self.assertEqual(r.leafs, 1)
        self.assertEqual(game_position_to_str(r.final_game_position), 'bbbbbbbb' * 5 + 'wwwwwwww' * 3 + 'b')

    def test_full_board_white_to_move(self):
        r = minimax_solve(game_position_from_str('bbbbbbbb' * 5 + 'wwwwwwww' * 3 + 'w'))
        self.assertEqual(int(r.game_value), -16)
        self.assertEqual(r.nodes, 1)
        self.assertEqual(r.leafs, 1)

    def test_full_board_draw(self):
        r = minimax_solve(game_position_from_str('bbbbbbbb' * 4 + 'wwwwwwww' * 4 + 'b'))
        self.assertEqual(int(r.game_value), 0)
        self.assertEqual(r.nodes, 1)
        self.assertEqual(r.leafs, 1)

    def test_draw_with_empties_is_zero(self):
        # The WOF scoring: a draw is 0, with or without empty squares.
        r = minimax_solve(game_position_from_str('bbbbbbbb' + '.' * 48 + 'wwwwwwww' + 'b'))
        self.assertEqual(int(r.game_value), 0)
        self.assertEqual(r.nodes, 1)
        self.assertEqual(r.leafs, 1)

    def test_single_empty_forced(self):
        r = minimax_solve(game_position_from_str(
            '.wbbbbbb' + 'bbbbbbbb' * 3 + 'bbwwwwww' + 'wwwwwwww' * 3 + 'b'))
        self.assertEqual(int(r.game_value), 4)
        self.assertEqual(r.nodes, 2)
        self.assertEqual(r.leafs, 1)
        self.assertEqual(game_position_to_str(r.final_game_position),
                         'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb' + 'wwwwwwwwwwwwwwwwwwwwwwwwwwwwww' + 'w')

    def test_tie_keeps_the_first_static_move(self):
        # Two lines of equal value: the first in the static A1..H8 order is kept (the A1 line,
        # whose final position differs from the H1 line's).
        r = minimax_solve(game_position_from_str(
            '.wbbwbw.' + 'bbbbbbbb' * 3 + 'bwwwwwww' + 'wwwwwwww' * 2 + 'bwwwwwww' + 'b'))
        self.assertEqual(int(r.game_value), -14)
        self.assertEqual(r.nodes, 5)
        self.assertEqual(r.leafs, 2)
        self.assertEqual(game_position_to_str(r.final_game_position),
                         'bbbbwbwwbbbbbbwwbbbbbwbwbbbbwbbwbwwwwwwwwwwwwwwwwwwwwwwwbwwwwwwwb')

    def test_pass_at_root(self):
        # The mover has no legal move: the turn passes (a further node), the opponent plays the
        # single legal move, the board fills up.
        r = minimax_solve(game_position_from_str(
            'bbbbbbbb' + 'bbbbbbbb' + '.bbbwwww' + 'bbwwwwww' + 'bbbbbbbb' + 'wbbbbbbb'
            + 'bbbbbbbb' + 'wwwwwwbb' + 'b'))
        self.assertEqual(int(r.game_value), 10)
        self.assertEqual(r.nodes, 3)
        self.assertEqual(r.leafs, 1)
        self.assertEqual(game_position_to_str(r.final_game_position),
                         'bbbbbbbbbbbbbbbbwwwwwwwwwwwwwwwwwbwbbbbbwbbwbbbbbbbbwbbbwwwwwwbbb')


class TestMinimaxSolveFixture(unittest.TestCase):
    """
    minimax_solve on the gpdb-sample-games.txt corpus (loaded with the gpdb module): the
    solution reproduces the reference exactly (the value, the final position, the node / leaf
    counts).
    """

    DB_FILE = WORKSPACE_ROOT / 'test' / 'reversi' / 'data' / 'gpdb-sample-games.txt'

    @classmethod
    def setUpClass(cls):
        cls.db, _ = load_game_position_database(cls.DB_FILE)

    def test_ffo_01_simplified_8(self):
        entry = self.db.find('ffo-01-simplified-8')
        self.assertIsNotNone(entry)
        r = minimax_solve(entry.position)
        self.assertEqual(int(r.game_value), 18)
        self.assertEqual(r.nodes, 46)
        self.assertEqual(r.leafs, 15)
        self.assertEqual(game_position_to_str(r.final_game_position),
                         'bwbbbbbbbwwwwwwbbwbwbwwbbwwbwbbbbbwwbwbbbbbwwbwbbbbwwwbbbbbbbbbb' + 'b')
        # The solution line (A1, B1, H1, G2) ends at the final position.
        p = entry.position
        for name in ('A1', 'B1', 'H1', 'G2'):
            p = make_game_position_from_position(
                position_make_move(p, square_from_str(name)), np.uint8(1 - int(p['player'])))
        self.assertEqual(game_position_to_str(p), game_position_to_str(r.final_game_position))
