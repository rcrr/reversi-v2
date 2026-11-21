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

import numba as nb
import numpy as np
import numpy.typing as npt
from pydantic import BeforeValidator, ConfigDict, validate_call

from reversi.board import (MOVE_NA, MOVE_PA, MOVE_UN, Bitboard, GamePosition, GamePositionField,
                           Move, Player, bitboard_bsf, final_value_of, flips_of_move,
                           legal_moves_of, game_position_final_value, game_position_legal_moves,
                           game_position_make_move, make_game_position)


__all__ = ['OUT_OF_RANGE_DEFEAT_SCORE', 'GameValue', 'GameValueArray', 'NodeRecord',
           'SolverResult', 'minimax_solve']


#: Represents a reversi game value from -64 to +64 as an numpy.int8 scalar.
GameValue: TypeAlias = np.int8

def _validate_game_value_array(v: Any) -> Any:
    """Validator to ensure a numpy array strictly uses int8 dtype."""
    if isinstance(v, np.ndarray) and v.dtype != np.int8:
        raise ValueError(f"Array dtype must be int8, got {v.dtype}")
    return v

# A Pydantic-compatible type hint for GameValue (np.int8) arrays.
GameValueArray = Annotated[npt.NDArray[GameValue], BeforeValidator(_validate_game_value_array)]

#: The out-of-range sentinel of the best-value accumulation (the C out_of_range_defeat_score): just
#: outside the game-value range [-64, 64], so the first child value always wins the strict
#: comparison and the no-move-yet state needs no test.
OUT_OF_RANGE_DEFEAT_SCORE = -66


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


@nb.njit(cache=True)
def _search(mover, opponent, player, level):
    """
    The numba-compiled recursive search (the nopython twin of the Python `search` closure of
    `minimax_solve`): the same contract, the position passed as the three field scalars (numba
    cannot build the structured GamePosition scalar), the public per-lane bitboard primitives of
    board.py inlined by the compiler.

    Returns:
        The (value, final_mover, final_opponent, final_player, nodes, leafs) of the subtree.
    """
    legal = legal_moves_of(mover, opponent)
    if not legal:
        if not legal_moves_of(opponent, mover):
            return final_value_of(mover, opponent), mover, opponent, player, 1, 1
        value, fm, fo, fp, nodes, leafs = _search(opponent, mover, 1 - player, level + 1)
        return -value, fm, fo, fp, nodes + 1, leafs
    best_value = OUT_OF_RANGE_DEFEAT_SCORE
    best_fm, best_fo, best_fp = mover, opponent, player
    nodes = 1
    leafs = 0
    moves = legal
    while moves:
        sq = bitboard_bsf(moves)
        moves = moves & (moves - Bitboard(1))
        m = Bitboard(1) << Bitboard(sq)
        flips = flips_of_move(mover, opponent, m)
        value, fm, fo, fp, n, l = _search(opponent ^ flips, (mover ^ flips) | m,
                                          1 - player, level + 1)
        value = -value
        nodes += n
        leafs += l
        if value > best_value:
            best_value, best_fm, best_fo, best_fp = value, fm, fo, fp
    return best_value, best_fm, best_fo, best_fp, nodes, leafs


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
    if log is None:
        value, fm, fo, fp, nodes, leafs = _search(gp['mover'], gp['opponent'],
                                                  int(gp['player']), 1)
        return SolverResult(game_value=GameValue(value),
                            final_game_position=make_game_position(np.uint64(fm), np.uint64(fo),
                                                                   np.uint8(fp)),
                            nodes=nodes, leafs=leafs)

    nodes = 0
    leafs = 0

    def search(gp: GamePosition, level: int, parent_move: Move) -> tuple[int, GamePositionField]:
        level += 1
        nonlocal nodes, leafs
        nodes += 1
        call_id = nodes
        legal = game_position_legal_moves(gp)
        if not legal:
            gp_pass = game_position_make_move(gp, MOVE_PA)
            if not game_position_legal_moves(gp_pass):
                leafs += 1
                value = game_position_final_value(gp)
                if log is not None:
                    log(NodeRecord(call_id, level, gp['player'], parent_move, MOVE_NA, value))
                return value, gp
            value, final = search(gp_pass, level, MOVE_PA)
            value = -value
            if log is not None:
                log(NodeRecord(call_id, level, gp['player'], parent_move, MOVE_PA, value))
            return value, final
        best_value = OUT_OF_RANGE_DEFEAT_SCORE
        best_move = MOVE_NA
        best_final = gp
        moves = legal
        while moves:
            sq = bitboard_bsf(moves)
            moves &= moves - 1
            value, final = search(game_position_make_move(gp, Move(sq)), level, Move(sq))
            value = -value
            if value > best_value:
                best_value, best_move, best_final = value, Move(sq), final
        if log is not None:
            log(NodeRecord(call_id, level, gp['player'], parent_move, best_move, best_value))
        return best_value, best_final

    value, final = search(gp, 0, MOVE_UN)
    return SolverResult(game_value=GameValue(value), final_game_position=final,
                        nodes=nodes, leafs=leafs)
