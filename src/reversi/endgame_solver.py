#
# endgame_solver.py
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
endgame_solver - the scalar exact endgame solver.

`minimax_solve` searches the whole game tree of an endgame with a depth-first minimax:

- the legal moves of each position are explored in the static square order (A1, A2, ..., H8);
- a position where neither player has a legal move is a leaf, valued by `position_final_value`
  (the WOF scoring: the empty squares are assigned to the winner, a draw is 0);
- the value of a child is negated at each ply, so every result is seen from the point of view
  of the player to move at that position, and the returned game value is seen from the point of
  view of the player to move at the root;
- a player with no legal move passes: the turn is handed to the opponent as a further node, and
  the value comes back negated; a position where neither player has a legal move is a leaf
  (one node, no pass);
- in a tie of equal values, the first move in the static order is kept.

`nodes` counts every position visited (the root and the leaves included); `leafs` counts the
terminal positions evaluated.

The trace
---------

With a `log` given, `minimax_solve` calls it once per visited node, when the search of the node
completes (the C game-tree log works the same way: the `CALL_ID` is assigned at the node entry,
the row is written at its exit). The `NodeRecord` carries the six fields of the first trace
version, each one matching a column of the C log:

- `call_id` (the C `CALL_ID`): the node number, 1-based, assigned at entry - it aligns the v2
  records with the C log one to one;
- `level` (the C `CALL_LEVEL`): the search depth (1 = the root) - the shape of the tree;
- `player` (the C `PLAYER`): the absolute player to move at the node - the anchor of the
  sign-flip semantics;
- `parent_move` (the C `PARENT_MOVE`): the move by which the parent reached this node
  (`MOVE_UN` at the root, `MOVE_PA` at the child of a pass) - it reconstructs the path from
  the root;
- `best_move` (the C `T_BEST_MOVE`): the move chosen by the node (`MOVE_PA` at a pass node,
  `MOVE_NA` at a leaf) - the decision of the node;
- `value` (the C `T_ALPHA`): the final value of the node, seen from the point of view of the
  player to move there (at the root, the game value).

The C-internal columns (the Zobrist `HASH`, the absolute `BLACKS` / `WHITES` bitboards) are not
part of the record: they depend on the C hash constants and are not reproducible in v2.
"""

from dataclasses import dataclass
from typing import Any, Annotated, Callable, TypeAlias

import numpy as np
import numpy.typing as npt
from pydantic import BeforeValidator, ConfigDict, validate_call

from reversi.board import (MOVE_NA, MOVE_PA, MOVE_UN, GamePosition, GamePositionField, Move,
                           Player, PositionField, make_game_position, make_position,
                           position_final_value, position_legal_moves, position_make_move)


__all__ = ['GameValue', 'GameValueArray', 'NodeRecord', 'SolverResult', 'minimax_solve']


#: Represents a reversi game value from -64 to +64 as an numpy.int8 scalar.
GameValue: TypeAlias = np.int8

def _validate_game_value_array(v: Any) -> Any:
    """Validator to ensure a numpy array strictly uses int8 dtype."""
    if isinstance(v, np.ndarray) and v.dtype != np.int8:
        raise ValueError(f"Array dtype must be int8, got {v.dtype}")
    return v

# A Pydantic-compatible type hint for GameValue (np.int8) arrays.
GameValueArray = Annotated[npt.NDArray[GameValue], BeforeValidator(_validate_game_value_array)]


@dataclass(frozen=True)
class NodeRecord:
    """
    One visited node of the search, as emitted to the `log` callback of `minimax_solve` (see the
    "The trace" section of the module docstring for the role of each field). The move fields are
    never `None`: the domain sentinel codes express the absences (`MOVE_UN` at the root parent,
    `MOVE_NA` at a leaf best, `MOVE_PA` at a pass).
    """
    call_id: int
    level: int
    player: Player
    parent_move: Move
    best_move: Move
    value: int


@dataclass(frozen=True)
class SolverResult:
    """
    The result of an endgame solve: the game value seen from the point of view of the player to
    move at the root, the terminal game position of the best line, and the search counters.
    """
    game_value: GameValue
    final_game_position: GamePositionField
    nodes: int
    leafs: int


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def minimax_solve(gp: GamePosition, log: Callable[[NodeRecord], None] | None = None) -> SolverResult:
    """
    Solve the endgame exactly with a depth-first minimax (see the module docstring for the search
    contract) and return the game value, the final game position of the best line, and the node /
    leaf counts.

    Args:
        gp: the game position to solve (scalar only).
        log: optional callable, invoked once per visited node with the `NodeRecord` of the node,
            when the search of the node completes (see the "The trace" section of the module
            docstring).

    Returns:
        The SolverResult of the search.
    """
    nodes = 0
    leafs = 0
    call_count = 0

    def search(p: PositionField, player: Player, level: int, parent_move: Move):
        # p: the position (the mover / opponent fields), player: the absolute player to move.
        nonlocal nodes, leafs, call_count
        nodes += 1
        call_count += 1
        call_id = call_count
        legal = position_legal_moves(p)
        if not legal:
            # The mover has no legal move: is the game over, or does the turn pass?
            p_pass = position_make_move(p, MOVE_PA)
            legal_pass = position_legal_moves(p_pass)
            if not legal_pass:
                # A leaf: neither player has a legal move (one node, no pass).
                leafs += 1
                value = position_final_value(p)
                if log is not None:
                    log(NodeRecord(call_id, level, player, parent_move, MOVE_NA, int(value)))
                return value, make_game_position(p['mover'], p['opponent'], player)
            # The pass: a further node (the same board, the other player to move), searched as a
            # node of its own; the value comes back negated, as at every ply.
            value, final = search(p_pass, 1 - player, level + 1, MOVE_PA)
            value = -value
            if log is not None:
                log(NodeRecord(call_id, level, player, parent_move, MOVE_PA, value))
            return value, final
        best_value = None
        best_move = None
        best_final = None
        for sq in range(64):
            if (legal >> sq) & 1:
                value, final = search(position_make_move(p, Move(sq)), 1 - player,
                                      level + 1, Move(sq))
                value = -value
                if best_value is None or value > best_value:
                    best_value, best_move, best_final = value, Move(sq), final
        if log is not None:
            log(NodeRecord(call_id, level, player, parent_move, best_move, best_value))
        return best_value, best_final

    value, final = search(make_position(gp['mover'], gp['opponent']), gp['player'], 1, MOVE_UN)
    return SolverResult(game_value=GameValue(value), final_game_position=final,
                        nodes=nodes, leafs=leafs)
