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
import os
import time
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
        12: (18, 1, 1,
            'bwbbbbbbbwwwwwwbbwbwbwwbbwwbwbbbbbwwbwbbbbbwwbwbbbbwwwbbbbbbbbbb' + 'b',
            ()),
    }

    # The corner cases: the named corpus entries with the search-contract edge shapes (the forced
    # first pass, the wipe-out win before ec=0).
    CASES_CORNER = {
        'black-has-to-pass': (-52, 196030, 55778,
            'wwwwwwwbwwwwwwbwwwwwwbwwwwwwwwwwwwwbwwwwwwwwbwwwwwwwwwwwwwwwwwbwb',
            ('--', 'H7', '--', 'G1', 'H1', 'E1', '--', 'C1', '--', 'A6', 'A5', 'A3', 'A7', 'A4')),
        'black-wins-by-wipe-out': (-64, 4900474, 1367719,
            'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbw',
            ('F6', 'H2', '--', 'H4', '--', 'A6', '--', 'G8', 'G6', 'A7', '--', 'H8', 'H7',
             'H6', '--', 'F8', '--', 'B7', '--', 'A8')),
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

    def _solve_named(self, name):
        value, nodes, leafs, final, line = self.CASES_CORNER[name]
        entry = self.db.find(name)
        self.assertIsNotNone(entry)
        r = minimax_solve(entry.position)
        self.assertEqual(int(r.game_value), value)
        self.assertEqual(r.nodes, nodes)
        self.assertEqual(r.leafs, leafs)
        self.assertEqual(game_position_to_str(r.final_game_position), final)
        # Playing the solution line from the starting position arrives at the final position (a
        # line entry of '--' is a pass: the player swap, the board untouched).
        p = entry.position
        for mv in line:
            p = game_position_make_move(p, Move(MOVE_PA) if mv == '--' else square_from_str(mv))
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

    @unittest.skipUnless(os.environ.get('PERF') == '1', "Skipping performance test (set PERF=1 to run)")
    def test_performance_ffo_01_simplified_1(self):
        # The 1.1M-node case 1: the untraced throughput of the compiled search (the printout is the
        # measurement; no assertion on the rate — the machine dependent number of the run).
        name = 'ffo-01-simplified-1'
        entry = self.db.find(name)
        self.assertIsNotNone(entry)
        minimax_solve(entry.position)  # warm-up (the njit compile)
        start = time.perf_counter()
        r = minimax_solve(entry.position)
        duration = time.perf_counter() - start
        print(f"\n[PERF minimax_solve {name}] Solved {r.nodes:,} nodes in "
              f"{duration:.4f}s ({r.nodes / duration / 1e6:.2f} M nodes/s)")

    def test_ffo_01_simplified_8_trace(self):
        self._trace_case(8)

    def test_ffo_01_simplified_12(self):
        # The already-finished game of the series: a single leaf (the terminal check precedes any
        # search), the value the WOF of the full board.
        self._solve_case(12)

    def test_black_has_to_pass(self):
        # The forced first pass: the mover has no legal move, the search starts with the pass
        # node (the solution line opens with '--').
        self._solve_named('black-has-to-pass')

    def test_black_wins_by_wipe_out(self):
        # The wipe-out win before ec=0: one side has no stone left, the WOF assigns every empty
        # square to the winner (the value the full +/-64, the final board one colour).
        self._solve_named('black-wins-by-wipe-out')


class TestAlphaBetaSolveFixture(unittest.TestCase):
    """
    alphabeta_solve on the ffo-01-simplified series of the gpdb-sample-games.txt corpus (loaded
    with the gpdb module): each case reproduces the C alpha-beta reference exactly (the value, the
    node / leaf counts, the final position, the solution line — the same line the minimax
    returns), and the search trace reproduces the C alpha-beta game-tree log record by record.

    Trace note: the C log `T_BEST_MOVE` of a non-improving (fail-low) node is not part of the
    search contract — the C node struct never initializes `best_move` there, so the log carries
    the stale value of the previous occupant of the stack slot (a C logging artifact). The v2
    record is `MOVE_NA` at such nodes, and the comparison skips the best-move column when the v2
    record has no real best move.
    """

    DB_FILE = WORKSPACE_ROOT / 'test' / 'reversi' / 'data' / 'gpdb-sample-games.txt'
    LOG_DIR = WORKSPACE_ROOT / 'test' / 'reversi' / 'data'

    # The case -> the expected result: the game value, the node count, the leaf count, the final
    # position string, the solution line (identical to the minimax one: the same natural move
    # order and the same strict tie-break).
    FINAL = 'bwbbbbbbbwwwwwwbbwbwbwwbbwwbwbbbbbwwbwbbbbbwwbwbbbbwwwbbbbbbbbbb' + 'b'
    CASES = {
        0: (18, 1700428, 420214, FINAL,
            ('A8', 'A6', 'A4', 'A7', 'B6', 'A2', 'H8', 'A3', 'A1', 'B1', 'H1', 'G2')),
        1: (-18, 43846, 10037, FINAL,
            ('A6', 'A4', 'A7', 'B6', 'A2', 'H8', 'A3', 'A1', 'B1', 'H1', 'G2')),
        2: (18, 15638, 3640, FINAL,
            ('A4', 'A7', 'B6', 'A2', 'H8', 'A3', 'A1', 'B1', 'H1', 'G2')),
        3: (-18, 7881, 1947, FINAL,
            ('A7', 'B6', 'A2', 'H8', 'A3', 'A1', 'B1', 'H1', 'G2')),
        4: (18, 2029, 538, FINAL,
            ('B6', 'A2', 'H8', 'A3', 'A1', 'B1', 'H1', 'G2')),
        5: (-18, 427, 108, FINAL,
            ('A2', 'H8', 'A3', 'A1', 'B1', 'H1', 'G2')),
        6: (18, 232, 64, FINAL,
            ('H8', 'A3', 'A1', 'B1', 'H1', 'G2')),
        7: (-18, 107, 33, FINAL,
            ('A3', 'A1', 'B1', 'H1', 'G2')),
        8: (18, 40, 13, FINAL,
            ('A1', 'B1', 'H1', 'G2')),
        12: (18, 1, 1, FINAL, ()),
    }

    # The corner cases: the named corpus entries with the search-contract edge shapes (the forced
    # first pass, the wipe-out win before ec=0). The solution line is the minimax one (the full
    # best line): the alpha-beta recorded best-move chain stops at the first fail-low tie, while
    # the value / final / line are the same game properties.
    CASES_CORNER = {
        'black-has-to-pass': (-52, 23977, 5963,
            'wwwwwwwbwwwwwwbwwwwwwbwwwwwwwwwwwwwbwwwwwwwwbwwwwwwwwwwwwwwwwwbwb',
            ('--', 'H7', '--', 'G1', 'H1', 'E1', '--', 'C1', '--', 'A6', 'A5', 'A3', 'A7', 'A4')),
        'black-wins-by-wipe-out': (-64, 310082, 74388,
            'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbw',
            ('F6', 'H2', '--', 'H4', '--', 'A6', '--', 'G8', 'G6', 'A7', '--', 'H8', 'H7',
             'H6', '--', 'F8', '--', 'B7', '--', 'A8')),
    }

    @classmethod
    def setUpClass(cls):
        cls.db, _ = load_game_position_database(cls.DB_FILE)

    def _solve_case(self, n):
        value, nodes, leafs, final, line = self.CASES[n]
        name = 'ffo-01-simplified' if n == 0 else f'ffo-01-simplified-{n}'
        entry = self.db.find(name)
        self.assertIsNotNone(entry)
        r = alphabeta_solve(entry.position)
        self.assertEqual(int(r.game_value), value)
        self.assertEqual(r.nodes, nodes)
        self.assertEqual(r.leafs, leafs)
        self.assertEqual(game_position_to_str(r.final_game_position), final)
        # Playing the solution line from the starting position arrives at the final position.
        p = entry.position
        for name in line:
            p = game_position_make_move(p, Move(square_from_str(name)))
        self.assertEqual(game_position_to_str(p), final)

    def _solve_named(self, name):
        value, nodes, leafs, final, line = self.CASES_CORNER[name]
        entry = self.db.find(name)
        self.assertIsNotNone(entry)
        r = alphabeta_solve(entry.position)
        self.assertEqual(int(r.game_value), value)
        self.assertEqual(r.nodes, nodes)
        self.assertEqual(r.leafs, leafs)
        self.assertEqual(game_position_to_str(r.final_game_position), final)
        # Playing the solution line from the starting position arrives at the final position (a
        # line entry of '--' is a pass: the player swap, the board untouched).
        p = entry.position
        for mv in line:
            p = game_position_make_move(p, Move(MOVE_PA) if mv == '--' else square_from_str(mv))
        self.assertEqual(game_position_to_str(p), final)

    def _trace_case(self, n):
        # The trace of the search (one NodeRecord per visited node, emitted when the node's
        # search completes) reproduces the C alpha-beta game-tree log record by record, on the
        # six comparable columns — with the documented exception of the best move at a
        # non-improving node (the C stale-value artifact, the class docstring).
        entry = self.db.find(f'ffo-01-simplified-{n}')
        self.assertIsNotNone(entry)
        records = []
        alphabeta_solve(entry.position, log=records.append)
        records.sort(key=lambda r: r.call_id)

        log_file = self.LOG_DIR / f'ab_log_ffo-01-simplified-{n}.csv'
        lines = [l for l in log_file.read_text().splitlines() if l.strip()]
        col = {name: i for i, name in enumerate(lines[0].split(';'))}
        c_rows = sorted((l.split(';') for l in lines[1:]), key=lambda r: int(r[col['CALL_ID']]))

        self.assertEqual(len(records), len(c_rows))
        for rec, row in zip(records, c_rows):
            got = (rec.call_id, rec.level, int(rec.player),
                   '--' if rec.parent_move == MOVE_PA else move_to_str(rec.parent_move),
                   rec.value)
            exp = (int(row[col['CALL_ID']]), int(row[col['CALL_LEVEL']]), int(row[col['PLAYER']]),
                   row[col['PARENT_MOVE']], int(row[col['T_ALPHA']]))
            self.assertEqual(got, exp, f"node {rec.call_id}")
            if rec.best_move != MOVE_NA:
                self.assertEqual('--' if rec.best_move == MOVE_PA else move_to_str(rec.best_move),
                                 row[col['T_BEST_MOVE']], f"node {rec.call_id} best move")

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

    def test_ab_minimax_parity(self):
        # The alpha-beta and the minimax agree on the value and the final position of every case
        # (both searches are exact: the pruning only skips the irrelevant subtrees).
        for n in (1, 2, 3, 4, 5, 6, 7, 8):
            name = f'ffo-01-simplified-{n}'
            entry = self.db.find(name)
            self.assertIsNotNone(entry)
            ab = alphabeta_solve(entry.position)
            mm = minimax_solve(entry.position)
            self.assertEqual(int(ab.game_value), int(mm.game_value), name)
            self.assertEqual(game_position_to_str(ab.final_game_position),
                             game_position_to_str(mm.final_game_position), name)

    @unittest.skipUnless(os.environ.get('PERF') == '1', "Skipping performance test (set PERF=1 to run)")
    def test_performance_ffo_01_simplified_1(self):
        # The 44k-node case 1: the untraced throughput of the compiled alpha-beta search (the
        # printout is the measurement; no assertion on the rate — the machine dependent number of
        # the run).
        name = 'ffo-01-simplified-1'
        entry = self.db.find(name)
        self.assertIsNotNone(entry)
        alphabeta_solve(entry.position)  # warm-up (the njit compile)
        start = time.perf_counter()
        r = alphabeta_solve(entry.position)
        duration = time.perf_counter() - start
        print(f"\n[PERF alphabeta_solve {name}] Solved {r.nodes:,} nodes in "
              f"{duration:.4f}s ({r.nodes / duration / 1e6:.2f} M nodes/s)")

    def test_ffo_01_simplified_12(self):
        # The already-finished game of the series: a single leaf (the terminal check precedes any
        # search), the value the WOF of the full board.
        self._solve_case(12)

    def test_black_has_to_pass(self):
        # The forced first pass: the mover has no legal move, the search starts with the pass
        # node (the solution line opens with '--').
        self._solve_named('black-has-to-pass')

    def test_black_wins_by_wipe_out(self):
        # The wipe-out win before ec=0: one side has no stone left, the WOF assigns every empty
        # square to the winner (the value the full +/-64, the final board one colour).
        self._solve_named('black-wins-by-wipe-out')


class TestAlphaBetaSolveArray(unittest.TestCase):
    """
    the array form of alphabeta_solve (the worker-pool engine): every lane is exactly the result of the
    scalar alphabeta_solve of that lane (the engine runs the same compiled search), the batch
    values are checked against the independent DB goldens, and the batch precondition (the
    uniform empty count) is enforced by the opt-in check.
    """

    DB_FILE = WORKSPACE_ROOT / 'test' / 'reversi' / 'data' / 'gpdb-sample-games.txt'

    # The ten ec=8 lanes of the regab_prng_gp batch 7 (the user's set): the (mover, opponent)
    # bitboards as the DB signed integers, the player to move, and the independent DB game value.
    ROWS_10 = (
        (292196245152202976, -941136803967009266, 0, 14),
        (137788107833069952, 8220822431822392860, 0, 22),
        (72340273019509822, -1657607341870702464, 0, 0),
        (-7277957165829819713, 6917669195627496704, 0, 2),
        (221126373199515453, -259477888540577728, 0, 8),
        (-62480787258276348, 26100142223444217, 0, -8),
        (-1989845522081987904, 1737573574205058354, 0, -6),
        (-9218550381016039559, 8711891024890314754, 0, 28),
        (5782611454622482432, 1080872728222711615, 0, -48),
        (185881781002365168, 1228230909805926159, 0, -22),
    )

    @classmethod
    def setUpClass(cls):
        cls.db, _ = load_game_position_database(cls.DB_FILE)
        cls.gps10 = make_game_position(
            np.array([r[0] for r in cls.ROWS_10], dtype=np.int64).astype(np.uint64),
            np.array([r[1] for r in cls.ROWS_10], dtype=np.int64).astype(np.uint64),
            np.array([r[2] for r in cls.ROWS_10], dtype=np.uint8))

    def test_ten_db_golden_values(self):
        # The batch values are the independent DB goldens.
        r = alphabeta_solve(self.gps10)
        self.assertEqual(r.game_values.tolist(), [row[3] for row in self.ROWS_10])

    def test_ten_parity_scalar(self):
        # Every lane is exactly the result of the scalar solve of that lane (value, final,
        # node / leaf counts).
        r = alphabeta_solve(self.gps10)
        for i in range(10):
            s = alphabeta_solve(self.gps10[i])
            self.assertEqual(int(r.game_values[i]), int(s.game_value))
            self.assertEqual(game_position_to_str(r.final_game_positions[i]),
                             game_position_to_str(s.final_game_position))
            self.assertEqual(r.nodes[i], s.nodes)
            self.assertEqual(r.leafs[i], s.leafs)

    def test_mixed_corner_batch(self):
        # A batch mixing the corner shapes (the forced first pass, the finished game, the
        # wipe-out, a plain series lane): each lane its scalar result.
        names = ('black-has-to-pass', 'ffo-01-simplified-12', 'black-wins-by-wipe-out',
                 'ffo-01-simplified-8')
        entries = [self.db.find(n) for n in names]
        gps = make_game_position(np.array([e.position['mover'] for e in entries], dtype=np.uint64),
                                 np.array([e.position['opponent'] for e in entries],
                                          dtype=np.uint64),
                                 np.array([e.position['player'] for e in entries], dtype=np.uint8))
        r = alphabeta_solve(gps)
        self.assertEqual([int(v) for v in r.game_values], [-52, 18, -64, 18])
        for i, e in enumerate(entries):
            s = alphabeta_solve(e.position)
            self.assertEqual(r.nodes[i], s.nodes)
            self.assertEqual(r.leafs[i], s.leafs)
            self.assertEqual(game_position_to_str(r.final_game_positions[i]),
                             game_position_to_str(s.final_game_position))

    def test_empty_batch(self):
        empty = make_game_position(np.array([], dtype=np.uint64), np.array([], dtype=np.uint64),
                                   np.array([], dtype=np.uint8))
        r = alphabeta_solve(empty)
        self.assertEqual(r.game_values.shape, (0,))
        self.assertEqual(r.nodes.shape, (0,))
        self.assertEqual(r.leafs.shape, (0,))

    def test_uniform_empty_count(self):
        # The ten lanes share ec=8.
        self.assertEqual(uniform_empty_count(self.gps10), 8)
        # A non-uniform batch raises, naming the distinct counts.
        p8 = self.db.find('ffo-01-simplified-8').position
        p12 = self.db.find('ffo-01-simplified-12').position
        mixed = make_game_position(np.array([p8['mover'], p12['mover']], dtype=np.uint64),
                                   np.array([p8['opponent'], p12['opponent']], dtype=np.uint64),
                                   np.array([p8['player'], p12['player']], dtype=np.uint8))
        with self.assertRaises(ValueError):
            uniform_empty_count(mixed)

    def test_check_ec_gate(self):
        # check_ec=True on a non-uniform batch raises at the boundary; the default (False) skips
        # the check and solves the lanes anyway.
        p8 = self.db.find('ffo-01-simplified-8').position
        p12 = self.db.find('ffo-01-simplified-12').position
        mixed = make_game_position(np.array([p8['mover'], p12['mover']], dtype=np.uint64),
                                   np.array([p8['opponent'], p12['opponent']], dtype=np.uint64),
                                   np.array([p8['player'], p12['player']], dtype=np.uint8))
        with self.assertRaises(ValueError):
            alphabeta_solve(mixed, check_ec=True)
        r = alphabeta_solve(mixed)
        self.assertEqual([int(v) for v in r.game_values], [18, 18])


class TestAlphaBetaSolveArrayScale(unittest.TestCase):
    """
    The worker-pool array solver at the 100 / 1000-lane scale: the regab batch sets (the ec=8
    positions of the regab_prng_gp table, pulled in seq order from the batches 8 and 9) — the
    batch values are the INDEPENDENT DB game-value goldens, the ec precondition is enforced by the
    check, and the PERF printout is the batch throughput.
    """

    B8_FILE = WORKSPACE_ROOT / 'test' / 'reversi' / 'data' / 'regab-batch8-ec8-100.tsv'
    B9_FILE = WORKSPACE_ROOT / 'test' / 'reversi' / 'data' / 'regab-batch9-ec8-1000.tsv'

    @classmethod
    def _load(cls, path):
        rows = np.genfromtxt(path, delimiter='|', dtype=np.int64)
        gps = make_game_position(rows[:, 0].astype(np.uint64), rows[:, 1].astype(np.uint64),
                                 rows[:, 2].astype(np.uint8))
        return gps, rows[:, 3]

    def test_batch8_100_db_goldens(self):
        gps, goldens = self._load(self.B8_FILE)
        self.assertEqual(uniform_empty_count(gps), 8)
        r = alphabeta_solve(gps, check_ec=True)
        self.assertTrue(np.array_equal(r.game_values, goldens.astype(np.int8)))

    def test_batch9_1000_db_goldens(self):
        gps, goldens = self._load(self.B9_FILE)
        self.assertEqual(uniform_empty_count(gps), 8)
        r = alphabeta_solve(gps, check_ec=True)
        self.assertTrue(np.array_equal(r.game_values, goldens.astype(np.int8)))

    @unittest.skipUnless(os.environ.get('PERF') == '1', "Skipping performance test (set PERF=1 to run)")
    def test_performance_batch9_1000(self):
        # The 1000-lane batch: the pool throughput (the printout is the measurement; no assertion
        # on the rate — the machine dependent number of the run).
        gps, _ = self._load(self.B9_FILE)
        alphabeta_solve(gps)  # warm-up (the njit compile)
        start = time.perf_counter()
        r = alphabeta_solve(gps)
        duration = time.perf_counter() - start
        print(f"\n[PERF alphabeta_solve batch9-ec8-1000] Solved {r.nodes.sum():,} nodes "
              f"in {duration:.4f}s ({r.nodes.sum() / duration / 1e6:.2f} M lane-nodes/s)")


class TestUnifiedSolveApi(unittest.TestCase):
    """
    The unified scalar / array API (the board.py idiom: one function, both forms): the scalar
    input gives the SolverResult of the direct compiled search, the array input the
    SolverResultArray of the worker pool, the log callback is the scalar form only, and the
    minimax array form gives the same exact values (both engines are exact).
    """

    DB_FILE = WORKSPACE_ROOT / 'test' / 'reversi' / 'data' / 'gpdb-sample-games.txt'
    ROWS_10 = TestAlphaBetaSolveArray.ROWS_10

    @classmethod
    def setUpClass(cls):
        cls.db, _ = load_game_position_database(cls.DB_FILE)
        cls.gps10 = make_game_position(
            np.array([r[0] for r in cls.ROWS_10], dtype=np.int64).astype(np.uint64),
            np.array([r[1] for r in cls.ROWS_10], dtype=np.int64).astype(np.uint64),
            np.array([r[2] for r in cls.ROWS_10], dtype=np.uint8))

    def test_scalar_form_returns_solver_result(self):
        gp = self.db.find('ffo-01-simplified-4').position
        self.assertIsInstance(alphabeta_solve(gp), SolverResult)
        self.assertIsInstance(minimax_solve(gp), SolverResult)

    def test_array_form_returns_solver_result_array(self):
        self.assertIsInstance(alphabeta_solve(self.gps10), SolverResultArray)
        self.assertIsInstance(minimax_solve(self.gps10), SolverResultArray)

    def test_array_log_raises(self):
        def log(rec):
            pass
        with self.assertRaises(ValueError):
            alphabeta_solve(self.gps10, log=log)
        with self.assertRaises(ValueError):
            minimax_solve(self.gps10, log=log)

    def test_minimax_array_db_goldens(self):
        # The minimax array form: the same exact DB values as the alpha-beta form (both engines
        # are exact).
        r = minimax_solve(self.gps10)
        self.assertEqual(r.game_values.tolist(), [row[3] for row in self.ROWS_10])

    def test_minimax_check_ec_gate(self):
        # The minimax check_ec gate (the alphabeta twin of test_check_ec_gate): the non-uniform
        # batch raises at the boundary; the default (False) skips the check and solves.
        p8 = self.db.find('ffo-01-simplified-8').position
        p12 = self.db.find('ffo-01-simplified-12').position
        mixed = make_game_position(np.array([p8['mover'], p12['mover']], dtype=np.uint64),
                                   np.array([p8['opponent'], p12['opponent']], dtype=np.uint64),
                                   np.array([p8['player'], p12['player']], dtype=np.uint8))
        with self.assertRaises(ValueError):
            minimax_solve(mixed, check_ec=True)
        r = minimax_solve(mixed)
        self.assertEqual([int(v) for v in r.game_values], [18, 18])
