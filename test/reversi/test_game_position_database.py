#
# test_game_position_database.py
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
#
# How to run the game_position_database module unit tests.
#
# Run from the workspace root (the directory containing .venv and src).
#
# -0- Activate the environment.
#
# $ source .venv/bin/activate
#
# -1- Run the tests.
#
# time PERF=0 python3 -m unittest test.reversi.test_game_position_database
#

import unittest

import numpy as np

from reversi.board import (Bitboard, GamePosition, PLAYER_BLACK, PLAYER_WHITE,
                           game_position_from_str, game_position_to_str)
from reversi.game_position_database import (GpdbEntry, GpdbErrorType, GpdbSyntaxError,
                                            GamePositionDatabase, _parse_record,
                                            load_game_position_database)
from test.reversi.paths import CUSTOM_TMP_BASE, WORKSPACE_ROOT



class TestParseRecord(unittest.TestCase):
    """
    _parse_record: the C gpdb_parse_line mirror — the comment classification, the four-field
    split, the trailing-garbage / inline-comment rules, and the five field-level error classes.
    """

    BOARD = "." * 64

    def test_comment_line_is_none(self):
        self.assertIsNone(_parse_record("# a comment", "f", 0))

    def test_separators_only_line_is_none(self):
        self.assertIsNone(_parse_record(";;;", "f", 0))

    def test_well_formed_record(self):
        rec = f"one;{self.BOARD};b;A test record;"
        self.assertEqual(_parse_record(rec, "f", 3), ("one", self.BOARD, "b", "A test record"))

    def test_trailing_garbage_ignored(self):
        rec = f"two;{self.BOARD};w;desc; junk after the fourth separator"
        self.assertEqual(_parse_record(rec, "f", 4), ("two", self.BOARD, "w", "desc"))

    def test_inline_comment_cut(self):
        rec = f"three;{self.BOARD};w;desc; # an inline comment"
        self.assertEqual(_parse_record(rec, "f", 5), ("three", self.BOARD, "w", "desc"))

    def test_incomplete_entry(self):
        # Zero, one, two and three separators are all incomplete records.
        for n_sep in range(4):
            line = "x" + (";" + "." * 10) * n_sep
            with self.assertRaises(GpdbSyntaxError) as cm:
                _parse_record(line, "f", 1)
            self.assertEqual(cm.exception.error_type, GpdbErrorType.INCOMPLETE_ENTRY)

    def test_board_size_error(self):
        with self.assertRaises(GpdbSyntaxError) as cm:
            _parse_record(f"b;{'.' * 60};b;d;", "f", 2)
        self.assertEqual(cm.exception.error_type, GpdbErrorType.BOARD_SIZE_IS_NOT_64)

    def test_square_char_error(self):
        with self.assertRaises(GpdbSyntaxError) as cm:
            _parse_record(f"c;{'b' * 63}x;b;d;", "f", 3)
        self.assertEqual(cm.exception.error_type, GpdbErrorType.SQUARE_CHAR_IS_INVALID)

    def test_player_size_error(self):
        with self.assertRaises(GpdbSyntaxError) as cm:
            _parse_record(f"d;{self.BOARD};bw;d;", "f", 4)
        self.assertEqual(cm.exception.error_type, GpdbErrorType.PLAYER_IS_NOT_ONE_CHAR)

    def test_player_char_error(self):
        with self.assertRaises(GpdbSyntaxError) as cm:
            _parse_record(f"e;{self.BOARD};c;d;", "f", 5)
        self.assertEqual(cm.exception.error_type, GpdbErrorType.PLAYER_CHAR_IS_INVALID)


class TestLoadFixture(unittest.TestCase):
    """
    The load on the legacy fixture (test/reversi/data/gpdb-test-db.txt, the C db/gpdb-test-db.txt
    verbatim): the entry population, the error log (the C line numbering, 0-based), and the
    string round trip against the file's own records.
    """

    FIXTURE = WORKSPACE_ROOT / "test" / "reversi" / "data" / "gpdb-test-db.txt"

    def test_load_counts(self):
        db, errors = load_game_position_database(str(self.FIXTURE))
        self.assertEqual(len(db), 6)
        self.assertEqual(len(errors), 11)

    def test_error_log_types_and_lines(self):
        db, errors = load_game_position_database(str(self.FIXTURE))
        self.assertEqual([(e.line_number, e.error_type) for e in errors], [
            (35, GpdbErrorType.PLAYER_CHAR_IS_INVALID),
            (40, GpdbErrorType.DUPLICATE_ENTRY_KEY),
            (50, GpdbErrorType.INCOMPLETE_ENTRY),
            (51, GpdbErrorType.INCOMPLETE_ENTRY),
            (52, GpdbErrorType.INCOMPLETE_ENTRY),
            (53, GpdbErrorType.INCOMPLETE_ENTRY),
            (57, GpdbErrorType.BOARD_SIZE_IS_NOT_64),
            (61, GpdbErrorType.SQUARE_CHAR_IS_INVALID),
            (65, GpdbErrorType.PLAYER_CHAR_IS_INVALID),
            (66, GpdbErrorType.PLAYER_IS_NOT_ONE_CHAR),
            (67, GpdbErrorType.PLAYER_IS_NOT_ONE_CHAR),
        ])

    def test_loaded_entries(self):
        db, _ = load_game_position_database(str(self.FIXTURE))
        self.assertEqual(db.description, str(self.FIXTURE))
        e = db.find("all-black")
        self.assertEqual(e.position['mover'], Bitboard(0xFFFFFFFFFFFFFFFF))
        self.assertEqual(e.position['opponent'], Bitboard(0))
        self.assertEqual(e.position['player'], PLAYER_BLACK)
        e = db.find("all-white")
        self.assertEqual(e.position['mover'], Bitboard(0xFFFFFFFFFFFFFFFF))
        self.assertEqual(e.position['player'], PLAYER_WHITE)
        e = db.find("all-empty")
        self.assertEqual(e.position['mover'], Bitboard(0))
        self.assertEqual(e.position['opponent'], Bitboard(0))
        self.assertEqual(e.position['player'], PLAYER_BLACK)
        e = db.find("duplicate-entry")
        self.assertEqual(e.description, "Test inserting a position twice: first time")
        self.assertEqual(e.position['player'], PLAYER_WHITE)
        self.assertIsNone(db.find("test-wrong"))

    def test_same_board_opposite_players(self):
        # test-one / test-two share the board: black to move -> mover = blacks, white to move
        # -> mover = whites.
        db, _ = load_game_position_database(str(self.FIXTURE))
        one, two = db.find("test-one"), db.find("test-two")
        self.assertEqual(one.position['mover'], two.position['opponent'])
        self.assertEqual(one.position['opponent'], two.position['mover'])

    def test_string_round_trip_against_file(self):
        # For every loaded entry: game_position_to_str(entry.position) reproduces the file's own
        # board+player fields of the entry's record.
        db, _ = load_game_position_database(str(self.FIXTURE))
        # The first occurrence of each key wins (the db keeps the first loaded record — the
        # fixture's duplicate-entry pair).
        lines = {}
        for ln in self.FIXTURE.read_text().splitlines():
            if ln and not ln.startswith('#'):
                lines.setdefault(ln.split(';')[0], ln)
        for entry in db:
            parts = lines[entry.id].split(';')
            self.assertEqual(game_position_to_str(entry.position), parts[1] + parts[2])

    def test_positions_property(self):
        db, _ = load_game_position_database(str(self.FIXTURE))
        gps = db.positions
        self.assertEqual(gps.dtype, GamePosition)
        self.assertEqual(gps.shape, (6,))
        self.assertEqual(gps[0]['player'], PLAYER_BLACK)  # insertion order: test-one first


class TestLoadPolicies(unittest.TestCase):
    """
    The loader policy flags (the C gpdb_dictionary_load trio) and the missing-file behaviour, on
    synthetic files under the shared build/tmp base.
    """

    BOARD = "." * 64
    TMP_FILES = []

    def tearDown(self):
        for name in self.TMP_FILES:
            path = CUSTOM_TMP_BASE / name
            if path.exists():
                path.unlink()
        self.TMP_FILES = []

    def _write(self, name, content):
        path = CUSTOM_TMP_BASE / name
        path.write_text(content)
        self.TMP_FILES.append(name)
        return str(path)

    def test_duplicate_replacement(self):
        f = self._write("gpdb_dup.txt",
                        f"a;{self.BOARD};b;first;\nb;{self.BOARD};w;second;\n"
                        f"a;{self.BOARD};w;third;")
        db, errors = load_game_position_database(f, duplicates_are_errors=False,
                                                 replace_duplicates=True)
        self.assertEqual(len(db), 2)
        self.assertEqual(db.find("a").description, "third")
        self.assertEqual(errors, [])

    def test_duplicate_kept_first(self):
        f = self._write("gpdb_dup2.txt",
                        f"a;{self.BOARD};b;first;\na;{self.BOARD};w;second;")
        db, errors = load_game_position_database(f, duplicates_are_errors=False,
                                                 replace_duplicates=False)
        self.assertEqual(len(db), 1)
        self.assertEqual(db.find("a").description, "first")
        self.assertEqual(errors, [])

    def test_stop_on_error(self):
        f = self._write("gpdb_stop.txt",
                        f"bad;{self.BOARD};c;d;\ngood;{self.BOARD};b;d;")
        db, errors = load_game_position_database(f, stop_on_error=True)
        self.assertEqual(len(db), 0)
        self.assertEqual(len(errors), 1)

    def test_missing_file(self):
        db, errors = load_game_position_database(str(CUSTOM_TMP_BASE / "no_such_file.txt"))
        self.assertEqual(len(db), 0)
        self.assertEqual(errors, [])


class TestDatabaseClass(unittest.TestCase):
    """
    The GamePositionDatabase container: the add / find / replace / len / iteration contract.
    """

    def _entry(self, id, player=PLAYER_BLACK):
        return GpdbEntry(id, f"desc-{id}", game_position_from_str("." * 64 + player_to_char(player)))

    def test_add_find_len_iter(self):
        db = GamePositionDatabase("test db")
        self.assertEqual(len(db), 0)
        db.add_or_replace(self._entry("a"))
        db.add_or_replace(self._entry("b"))
        self.assertEqual(len(db), 2)
        self.assertEqual(db.find("a").description, "desc-a")
        self.assertIsNone(db.find("z"))
        self.assertEqual([e.id for e in db], ["a", "b"])

    def test_add_or_replace_returns_replaced(self):
        db = GamePositionDatabase()
        first = self._entry("a", PLAYER_BLACK)
        second = self._entry("a", PLAYER_WHITE)
        self.assertIsNone(db.add_or_replace(first))
        replaced = db.add_or_replace(second)
        self.assertIs(replaced, first)
        self.assertEqual(db.find("a").position['player'], PLAYER_WHITE)
        self.assertEqual(len(db), 1)


def player_to_char(player) -> str:
    """The one-character form of a player constant."""
    return 'b' if player == PLAYER_BLACK else 'w'
