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
from reversi.endgame_solver import _validate_game_value_array
from reversi.game_position_database import load_game_position_database

from test.reversi.paths import WORKSPACE_ROOT
from test.reversi.tags import tier_long


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


class TestGameValueArrayValidator(unittest.TestCase):
    """
    The int8-dtype contract of the GameValueArray validator.
    """

    def test_int8_array_passes(self):
        a = np.array([4, -6], dtype=np.int8)
        self.assertIs(_validate_game_value_array(a), a)

    def test_non_int8_array_raises(self):
        with self.assertRaises(ValueError):
            _validate_game_value_array(np.array([4, 6]))

    def test_non_array_passes(self):
        self.assertEqual(_validate_game_value_array([4, 6]), [4, 6])


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
    minimax_solve on the ffo-01-simplified series of the gpdb-sample-games.txt corpus (loaded with
    the gpdb module): each case reproduces the C reference exactly (the value, the node / leaf
    counts, the final position), and the search trace reproduces the C game-tree log record by
    record.
    """

    DB_FILE = WORKSPACE_ROOT / 'test' / 'reversi' / 'data' / 'gpdb-sample-games.txt'
    LOG_DIR = WORKSPACE_ROOT / 'test' / 'reversi' / 'data'

    # The case -> the expected result: the game value, the node count, the leaf count, the final
    # position string, the solution line.
    CASES = {
        0: (18, 18055194, 5316151,
            'bwbbbbbbbwwwwwwbbwbwbwwbbwwbwbbbbbwwbwbbbbbwwbwbbbbwwwbbbbbbbbbb' + 'b',
            ('A8', 'A6', 'A4', 'A7', 'B6', 'A2', 'H8', 'A3', 'A1', 'B1', 'H1', 'G2')),
        1: (-18, 1111408, 322891,
            'bwbbbbbbbwwwwwwbbwbwbwwbbwwbwbbbbbwwbwbbbbbwwbwbbbbwwwbbbbbbbbbb' + 'b',
            ('A6', 'A4', 'A7', 'B6', 'A2', 'H8', 'A3', 'A1', 'B1', 'H1', 'G2')),
        2: (18, 261482, 78435,
            'bwbbbbbbbwwwwwwbbwbwbwwbbwwbwbbbbbwwbwbbbbbwwbwbbbbwwwbbbbbbbbbb' + 'b',
            ('A4', 'A7', 'B6', 'A2', 'H8', 'A3', 'A1', 'B1', 'H1', 'G2')),
        3: (-18, 105203, 32174,
            'bwbbbbbbbwwwwwwbbwbwbwwbbwwbwbbbbbwwbwbbbbbwwbwbbbbwwwbbbbbbbbbb' + 'b',
            ('A7', 'B6', 'A2', 'H8', 'A3', 'A1', 'B1', 'H1', 'G2')),
        4: (18, 20040, 6201,
            'bwbbbbbbbwwwwwwbbwbwbwwbbwwbwbbbbbwwbwbbbbbwwbwbbbbwwwbbbbbbbbbb' + 'b',
            ('B6', 'A2', 'H8', 'A3', 'A1', 'B1', 'H1', 'G2')),
        5: (-18, 2256, 644,
            'bwbbbbbbbwwwwwwbbwbwbwwbbwwbwbbbbbwwbwbbbbbwwbwbbbbwwwbbbbbbbbbb' + 'b',
            ('A2', 'H8', 'A3', 'A1', 'B1', 'H1', 'G2')),
        6: (18, 519, 153,
            'bwbbbbbbbwwwwwwbbwbwbwwbbwwbwbbbbbwwbwbbbbbwwbwbbbbwwwbbbbbbbbbb' + 'b',
            ('H8', 'A3', 'A1', 'B1', 'H1', 'G2')),
        7: (-18, 142, 44,
            'bwbbbbbbbwwwwwwbbwbwbwwbbwwbwbbbbbwwbwbbbbbwwbwbbbbwwwbbbbbbbbbb' + 'b',
            ('A3', 'A1', 'B1', 'H1', 'G2')),
        8: (18, 46, 15,
            'bwbbbbbbbwwwwwwbbwbwbwwbbwwbwbbbbbwwbwbbbbbwwbwbbbbwwwbbbbbbbbbb' + 'b',
            ('A1', 'B1', 'H1', 'G2')),
    }

    @classmethod
    def setUpClass(cls):
        cls.db, _ = load_game_position_database(cls.DB_FILE)

    def _solve_case(self, n):
        value, nodes, leafs, final, line = self.CASES[n]
        name = 'ffo-01-simplified' if n == 0 else f'ffo-01-simplified-{n}'
        entry = self.db.find(name)
        self.assertIsNotNone(entry)
        r = minimax_solve(entry.position)
        self.assertEqual(int(r.game_value), value)
        self.assertEqual(r.nodes, nodes)
        self.assertEqual(r.leafs, leafs)
        self.assertEqual(game_position_to_str(r.final_game_position), final)
        # Playing the solution line from the starting position arrives at the final position.
        p = entry.position
        for name in line:
            p = game_position_make_move(p, Move(square_from_str(name)))
        self.assertEqual(game_position_to_str(p), final)

    def _trace_case(self, n):
        # The trace of the search (one NodeRecord per visited node, emitted when the node's
        # search completes) reproduces the C game-tree log record by record, on the six
        # comparable columns (the call id, the level, the player, the parent move, the best
        # move, the value).
        entry = self.db.find(f'ffo-01-simplified-{n}')
        self.assertIsNotNone(entry)
        records = []
        minimax_solve(entry.position, log=records.append)
        records.sort(key=lambda r: r.call_id)

        log_file = self.LOG_DIR / f'es_log_ffo-01-simplified-{n}.csv'
        lines = [l for l in log_file.read_text().splitlines() if l.strip()]
        col = {name: i for i, name in enumerate(lines[0].split(';'))}
        c_rows = sorted((l.split(';') for l in lines[1:]), key=lambda r: int(r[col['CALL_ID']]))

        self.assertEqual(len(records), len(c_rows))
        for rec, row in zip(records, c_rows):
            got = (rec.call_id, rec.level, int(rec.player),
                   '--' if rec.parent_move == MOVE_PA else move_to_str(rec.parent_move),
                   '--' if rec.best_move == MOVE_PA else move_to_str(rec.best_move),
                   rec.value)
            exp = (int(row[col['CALL_ID']]), int(row[col['CALL_LEVEL']]), int(row[col['PLAYER']]),
                   row[col['PARENT_MOVE']], row[col['T_BEST_MOVE']], int(row[col['T_ALPHA']]))
            self.assertEqual(got, exp, f"node {rec.call_id}")

    @unittest.skipUnless(tier_long(), "Skipping the LONG-tier test (set LONG=1 to run)")
    def test_ffo_01_simplified(self):
        self._solve_case(0)

    def test_ffo_01_simplified_1(self):
        self._solve_case(1)

    def test_ffo_01_simplified_2(self):
        self._solve_case(2)

    def test_ffo_01_simplified_3(self):
        self._solve_case(3)

    def test_ffo_01_simplified_4(self):
        self._solve_case(4)

    def test_ffo_01_simplified_4_trace(self):
        self._trace_case(4)

    def test_ffo_01_simplified_5(self):
        self._solve_case(5)

    def test_ffo_01_simplified_5_trace(self):
        self._trace_case(5)

    def test_ffo_01_simplified_6(self):
        self._solve_case(6)

    def test_ffo_01_simplified_6_trace(self):
        self._trace_case(6)

    def test_ffo_01_simplified_7(self):
        self._solve_case(7)

    def test_ffo_01_simplified_7_trace(self):
        self._trace_case(7)

    def test_ffo_01_simplified_8(self):
        self._solve_case(8)

    def test_ffo_01_simplified_8_trace(self):
        self._trace_case(8)
