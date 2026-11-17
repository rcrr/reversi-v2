#
# game_position_database.py
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

"""
game_position_database - read a database of game positions from a text file (the gpdb format).

The v2 port of the legacy C game_position_db module: the same record format, the same six syntax-
error classes, the same loader policy flags — the entries are GamePosition scalars (the v2
relative view: mover / opponent / player) instead of the C GamePositionX (the absolute view).

The record format (one line per record, the fields separated by ';'):

    id;board;player;description;

- id: the entry's unique key (case sensitive).
- board: 64 characters, '.' empty, 'b' black, 'w' white (character i is square i, A1..H8).
- player: one character, 'b' or 'w'.
- description: free text; the record's own terminating ';' ends the line — anything after it is
  ignored.

A line that carries no character other than ';' (before a '#') is a comment. The board+player
fields form the 65-character GamePosition string of board.py (game_position_from_str).
"""

import os
from dataclasses import dataclass
from enum import Enum
from typing import Iterator, List, Optional, Tuple, Union

import numpy as np

from reversi.board import (GamePosition, PLAYER_BLACK, PLAYER_WHITE,
                           game_position_from_str)


__all__ = ['GpdbErrorType', 'GpdbSyntaxError', 'GpdbEntry', 'GamePositionDatabase',
           'load_game_position_database']


class GpdbErrorType(Enum):
    """The classification of the syntax errors found while parsing a database file (the C
    gpdb_syntax_err_type_t)."""
    INCOMPLETE_ENTRY = 'the line has fewer than four fields'
    BOARD_SIZE_IS_NOT_64 = 'the board field is not 64 characters long'
    SQUARE_CHAR_IS_INVALID = 'a board character is outside the set [bw.]'
    PLAYER_IS_NOT_ONE_CHAR = 'the player field is not one character long'
    PLAYER_CHAR_IS_INVALID = 'the player character is outside the set [bw]'
    DUPLICATE_ENTRY_KEY = 'the entry key is already in the database'


class GpdbSyntaxError(ValueError):
    """A syntax error in a game position database file (the C gpdb_syntax_err_t)."""

    def __init__(self, file_name: str, line_number: int, line: str,
                 error_type: GpdbErrorType, message: str):
        super().__init__(message)
        self.file_name = file_name
        self.line_number = line_number
        self.line = line
        self.error_type = error_type
        self.message = message

    def __str__(self) -> str:
        return f"{self.file_name}:{self.line_number}: {self.error_type.name}: {self.message}"


@dataclass(frozen=True)
class GpdbEntry:
    """A database entry: the unique id, the description, and the game position (a scalar)."""
    id: str
    description: str
    position: np.void  # a GamePosition scalar


class GamePositionDatabase:
    """A database of game position entries, keyed by the entry id (insertion order kept)."""

    def __init__(self, description: str = ''):
        self.description = description
        self._entries: dict = {}

    def __len__(self) -> int:
        return len(self._entries)

    def __iter__(self) -> Iterator[GpdbEntry]:
        return iter(self._entries.values())

    def find(self, entry_id: str) -> Optional[GpdbEntry]:
        """
        Return the entry with the given id, or None when absent (the C gpdb_dictionary_find_entry).

        Args:
            entry_id: the key to look up.
        """
        return self._entries.get(entry_id)

    def add_or_replace(self, entry: GpdbEntry) -> Optional[GpdbEntry]:
        """
        Insert the entry, replacing any entry with the same id (the C
        gpdb_dictionary_add_or_replace_entry).

        The replaced entry keeps its original position in the iteration order.

        Args:
            entry: the entry to insert.

        Returns:
            The replaced entry, or None when the id was new.
        """
        replaced = self._entries.get(entry.id)
        self._entries[entry.id] = entry
        return replaced

    @property
    def positions(self):
        """The entries' game positions stacked into a 1-D GamePositionArray (insertion order)."""
        return np.array([e.position for e in self._entries.values()], dtype=GamePosition)


def _parse_record(line: str, file_name: str, line_number: int
                  ) -> Union[Tuple[str, str, str, str], None]:
    """
    Parse one file line into (id, board, player, description), or None for a comment line.

    Mirrors the C gpdb_parse_line: the line is cut at the first '#' and at the line end; it is a
    record only when it carries a character other than ';'; a record needs its four fields (four
    ';'); the board and player fields are range-checked. The description runs from the third ';'
    to the fourth one; everything after the fourth ';' is ignored. Line numbers are 0-based (the
    C convention).

    Args:
        line: the raw file line.
        file_name: the source file name (carried into any error).
        line_number: the 0-based line number (carried into any error).

    Returns:
        The (id, board, player, description) tuple, or None for a comment line.

    Raises:
        GpdbSyntaxError: the line is a record with a syntax error (one of the six classes).
    """
    cut = line.find('#')
    if cut != -1:
        line = line[:cut]
    line = line.rstrip('\r\n')

    if not any(c != ';' for c in line):
        return None  # a comment (or separators-only) line

    separators = [i for i, c in enumerate(line) if c == ';']
    if len(separators) < 4:
        raise GpdbSyntaxError(file_name, line_number, line, GpdbErrorType.INCOMPLETE_ENTRY,
                              f"The line has an incomplete record. The number of fields is "
                              f"{len(separators)}.")

    entry_id = line[:separators[0]]
    board = line[separators[0] + 1:separators[1]]
    player = line[separators[1] + 1:separators[2]]
    description = line[separators[2] + 1:separators[3]]

    if len(board) != 64:
        raise GpdbSyntaxError(file_name, line_number, line, GpdbErrorType.BOARD_SIZE_IS_NOT_64,
                              f"The board field has {len(board)} squares, length must be 64.")
    for c in board:
        if c not in '.bw':
            raise GpdbSyntaxError(file_name, line_number, line,
                                  GpdbErrorType.SQUARE_CHAR_IS_INVALID,
                                  f"Board pieces must be in the character set [bw.]. Found {c!r}.")
    if len(player) != 1:
        raise GpdbSyntaxError(file_name, line_number, line, GpdbErrorType.PLAYER_IS_NOT_ONE_CHAR,
                              f"The player field has {len(player)} characters, length must be 1.")
    if player not in 'bw':
        raise GpdbSyntaxError(file_name, line_number, line, GpdbErrorType.PLAYER_CHAR_IS_INVALID,
                              f"Player must be in the character set [bw]. Found {player!r}.")

    return entry_id, board, player, description


def load_game_position_database(file_name: str,
                                duplicates_are_errors: bool = True,
                                replace_duplicates: bool = False,
                                stop_on_error: bool = False
                                ) -> Tuple[GamePositionDatabase, List[GpdbSyntaxError]]:
    """
    Load a game position database from a text file (the C gpdb_dictionary_load).

    The file is read line by line: the comment lines are skipped, the well-formed records are
    inserted into a fresh database (the description is the file name), and the syntax errors are
    collected in the returned log (in line order). A missing file gives an empty database and an
    empty log (the C behaviour).

    Args:
        file_name: the database file to load.
        duplicates_are_errors: a duplicate key is logged as an error and the record is discarded.
        replace_duplicates: when duplicates are not errors, the new record replaces the loaded one.
        stop_on_error: the loading stops at the first error.

    Returns:
        (database, error log) — the loaded GamePositionDatabase and the list of GpdbSyntaxError.
    """
    db = GamePositionDatabase(description=file_name)
    errors: List[GpdbSyntaxError] = []

    if not os.path.exists(file_name):
        return db, errors

    with open(file_name, 'r') as f:
        for line_number, line in enumerate(f):
            try:
                parsed = _parse_record(line, file_name, line_number)
            except GpdbSyntaxError as err:
                errors.append(err)
                if stop_on_error:
                    break
                continue
            if parsed is None:
                continue
            entry_id, board, player, description = parsed
            entry = GpdbEntry(entry_id, description, game_position_from_str(board + player))
            if db.find(entry_id) is not None:
                if duplicates_are_errors:
                    errors.append(GpdbSyntaxError(
                        file_name, line_number, line, GpdbErrorType.DUPLICATE_ENTRY_KEY,
                        f'The line has a duplicate key, duplications are considered as errors. '
                        f'Key is: "{entry_id}"'))
                    if stop_on_error:
                        break
                    continue
                if replace_duplicates:
                    db.add_or_replace(entry)
                # A tolerated duplicate without replacement: the record is discarded (the C
                # behaviour).
            else:
                db.add_or_replace(entry)
    return db, errors
