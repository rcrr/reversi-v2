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

With a `log` given, `minimax_solve` collects one `NodeRecord` per visited node, in the order the
search of the nodes completes (the C game-tree log works the same way: the `CALL_ID` is assigned
at the node entry, the row is written at its exit), and replays them to the callback when the
search completes. The `NodeRecord` carries the six fields of the first trace version, each one
matching a column of the C log:

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

The alpha-beta search
---------------------

`alphabeta_solve` is the alpha-beta twin of `minimax_solve`: the same depth-first search, the
same natural (static square) move order, the same tie-break (the strict comparison keeps the
first move in the order), plus the zero-window propagation (the child window is the negated
parent window) and the cutoff (a child value that reaches the node's beta ends the move loop;
the node then exits with its alpha — a bound at a cutoff node, exact otherwise). The root
window is the C ground-node initialization (the out-of-range sentinels, [-66, 66]): the
game-value range lies strictly inside it, the root value is exact, and the returned best line
is the same line the minimax returns; the node / leaf counts are smaller, the pruned subtrees
never being visited. The compiled twin is `_ab_search`, the per-node data (the entry-order counter, the
parent move, the alpha / beta window) threaded through the 4-element shared state array with the
same save/restore stack discipline as `_search`.

A trace note: in the C reference log the `T_BEST_MOVE` of a non-improving node (a fail-low node
that exits with its window alpha) is not defined by the search — the C node struct never
initializes `best_move` there, so the log carries the stale value of the previous occupant of the
stack slot. The v2 trace records `MOVE_NA` at such nodes, the only value consistent with the
search; a node-by-node comparison against the C log therefore skips `best_move` where the v2
record is `MOVE_NA`.
"""

from dataclasses import dataclass
from typing import Any, Annotated, Callable, TypeAlias

import numba as nb
import numpy as np
import numpy.typing as npt
from numba.typed import List
from pydantic import BeforeValidator, ConfigDict, validate_call

from reversi.board import (MOVE_NA, MOVE_PA, MOVE_UN, Bitboard, GamePositionField,
                           Move, Player, bitboard_bsf, final_value_of, flips_of_move,
                           legal_moves_of, make_game_position, other_player)


__all__ = ['OUT_OF_RANGE_DEFEAT_SCORE', 'GameValue', 'GameValueArray', 'NodeRecord',
           'SolverResult', 'minimax_solve', 'alphabeta_solve']


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


# The 2-element `state` array (not a 7th scalar parameter): numba 0.68 SEGFAULTS when a fresh
# process loads the cache of this function WITH a parent_move scalar parameter (bisected in
# scratch: the identical body caches and reloads fine with 6 parameters, the 7-parameter form
# crashes the loader). state[0] is the entry-order node counter, state[1] the current
# parent_move, saved/restored around each recursive call (stack discipline).
@nb.njit(cache=True)
def _search(mover, opponent, player, level, records, state):
    """
    The numba-compiled recursive search, the single implementation of the search contract of
    `minimax_solve`: the position passed as the three field scalars (numba cannot build the
    structured GamePosition scalar), the public per-lane bitboard primitives of board.py inlined
    by the compiler. `records` is the trace sink (one 6-int tuple per node, appended at the node
    exit; None disables the trace, the untraced specialization drops the guards); `state` is the
    2-element shared array: state[0] the entry-order node counter (the call_id of a node is its
    value at the node entry, the C convention), state[1] the current parent_move.

    Returns:
        The (value, final_mover, final_opponent, final_player, nodes, leafs) of the subtree.
    """
    state[0] += 1
    call_id = state[0]
    legal = legal_moves_of(mover, opponent)
    if not legal:
        if not legal_moves_of(opponent, mover):
            value = final_value_of(mover, opponent)
            if records is not None:
                records.append((call_id, level, player, state[1], MOVE_NA, value))
            return value, mover, opponent, player, 1, 1
        saved = state[1]
        state[1] = MOVE_PA
        value, fm, fo, fp, nodes, leafs = _search(opponent, mover, other_player(player), level + 1,
                                                  records, state)
        state[1] = saved
        value = -value
        if records is not None:
            records.append((call_id, level, player, state[1], MOVE_PA, value))
        return value, fm, fo, fp, nodes + 1, leafs
    best_value = OUT_OF_RANGE_DEFEAT_SCORE
    best_move = MOVE_NA
    best_fm, best_fo, best_fp = mover, opponent, player
    nodes = 1
    leafs = 0
    moves = legal
    while moves:
        sq = bitboard_bsf(moves)
        moves = moves & (moves - Bitboard(1))
        m = Bitboard(1) << Bitboard(sq)
        flips = flips_of_move(mover, opponent, m)
        saved = state[1]
        state[1] = sq
        value, fm, fo, fp, n, l = _search(opponent ^ flips, (mover ^ flips) | m,
                                          other_player(player), level + 1, records, state)
        state[1] = saved
        value = -value
        nodes += n
        leafs += l
        if value > best_value:
            best_value, best_move, best_fm, best_fo, best_fp = value, sq, fm, fo, fp
    if records is not None:
        records.append((call_id, level, player, state[1], best_move, best_value))
    return best_value, best_fm, best_fo, best_fp, nodes, leafs


# The 4-element `state` array: state[0] the entry-order node counter, state[1] the current
# parent_move, state[2] / state[3] the node's (alpha, beta) window — every per-node datum is
# threaded through the shared array with save/restore around each recursive call (stack
# discipline), keeping the 6-parameter signature (a 7th scalar parameter is the numba 0.68
# cache-loader segfault trigger, D-662).
@nb.njit(cache=True)
def _ab_search(mover, opponent, player, level, records, state):
    """
    The numba-compiled recursive alpha-beta search, the compiled twin of `_search`: the same
    position / sink / state convention, plus the zero-window propagation (the child window is the
    negated parent window) and the cutoff (a child value that reaches the node's beta ends the
    move loop). The node's best value starts at its window alpha: a fail-low node exits with its
    window alpha and `MOVE_NA`, a cutoff node with the bound that triggered it.

    Returns:
        The (value, final_mover, final_opponent, final_player, nodes, leafs) of the subtree.
    """
    state[0] += 1
    call_id = state[0]
    alpha = state[2]
    beta = state[3]
    legal = legal_moves_of(mover, opponent)
    if not legal:
        if not legal_moves_of(opponent, mover):
            value = final_value_of(mover, opponent)
            if records is not None:
                records.append((call_id, level, player, state[1], MOVE_NA, value))
            return value, mover, opponent, player, 1, 1
        saved_pm, saved_a, saved_b = state[1], state[2], state[3]
        state[1] = MOVE_PA
        state[2], state[3] = -beta, -alpha
        value, fm, fo, fp, nodes, leafs = _ab_search(opponent, mover, other_player(player), level + 1,
                                                     records, state)
        state[1], state[2], state[3] = saved_pm, saved_a, saved_b
        value = -value
        if value <= alpha:
            # Fail-low: the C pass node exits with its window alpha and best_move NA (the pass is
            # recorded only when it improves the window alpha).
            value, fm, fo, fp = alpha, mover, opponent, player
            best = MOVE_NA
        else:
            best = MOVE_PA
        if records is not None:
            records.append((call_id, level, player, state[1], best, value))
        return value, fm, fo, fp, nodes + 1, leafs
    best_value = alpha
    best_move = MOVE_NA
    best_fm, best_fo, best_fp = mover, opponent, player
    nodes = 1
    leafs = 0
    moves = legal
    while moves:
        sq = bitboard_bsf(moves)
        moves = moves & (moves - Bitboard(1))
        m = Bitboard(1) << Bitboard(sq)
        flips = flips_of_move(mover, opponent, m)
        saved_pm, saved_a, saved_b = state[1], state[2], state[3]
        state[1] = sq
        state[2], state[3] = -beta, -alpha
        value, fm, fo, fp, n, l = _ab_search(opponent ^ flips, (mover ^ flips) | m,
                                             other_player(player), level + 1, records, state)
        state[1], state[2], state[3] = saved_pm, saved_a, saved_b
        value = -value
        nodes += n
        leafs += l
        if value > best_value:
            best_value, best_move, best_fm, best_fo, best_fp = value, sq, fm, fo, fp
            # The node's alpha rises with the best child: the NEXT sibling's window is derived
            # from it (the zero-window tightening, the source of the pruning).
            alpha = value
            if value >= beta:
                if records is not None:
                    records.append((call_id, level, player, state[1], best_move, best_value))
                return best_value, best_fm, best_fo, best_fp, nodes, leafs
    if records is not None:
        records.append((call_id, level, player, state[1], best_move, best_value))
    return best_value, best_fm, best_fo, best_fp, nodes, leafs


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def minimax_solve(gp: GamePositionField, log: Callable[[NodeRecord], None] | None = None) -> SolverResult:
    """
    Solve the endgame exactly with a depth-first minimax (see the module docstring for the search
    contract) and return the game value, the final game position of the best line, and the node /
    leaf counts.

    Args:
        gp: the game position to solve (scalar only).
        log: optional callable, invoked with the `NodeRecord` of every visited node (in
            completion order, replayed when the search completes — see the "The trace" section of
            the module docstring).

    Returns:
        The SolverResult of the search.
    """
    state = np.zeros(2, dtype=np.int64)
    state[1] = MOVE_UN
    if log is None:
        value, fm, fo, fp, nodes, leafs = _search(gp['mover'], gp['opponent'], gp['player'],
                                                  1, None, state)
    else:
        # The trace sink: the typed list of the 6-int node records, filled by the compiled
        # search at each node exit, replayed to the callback when the search completes.
        records = List.empty_list(nb.types.UniTuple(nb.types.int64, 6))
        value, fm, fo, fp, nodes, leafs = _search(gp['mover'], gp['opponent'], gp['player'],
                                                  1, records, state)
        for rec in records:
            log(NodeRecord(rec[0], rec[1], Player(rec[2]), Move(rec[3]), Move(rec[4]), rec[5]))
    return SolverResult(game_value=GameValue(value),
                        final_game_position=make_game_position(Bitboard(fm), Bitboard(fo),
                                                               Player(fp)),
                        nodes=nodes, leafs=leafs)


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def alphabeta_solve(gp: GamePositionField, log: Callable[[NodeRecord], None] | None = None) -> SolverResult:
    """
    Solve the endgame exactly with a depth-first alpha-beta search (the zero-window negamax with
    the natural move order of `minimax_solve`; see the "The alpha-beta search" section of the
    module docstring) and return the game value, the final game position of the best line, and
    the node / leaf counts (smaller than the minimax ones: the pruned subtrees are never
    visited).

    Args:
        gp: the game position to solve (scalar only).
        log: optional callable, invoked with the `NodeRecord` of every visited node (in
            completion order, replayed when the search completes — see "The trace" section of the
            module docstring; at a cutoff node the record value is the search bound).

    Returns:
        The SolverResult of the search.
    """
    state = np.zeros(4, dtype=np.int64)
    state[1] = MOVE_UN
    # The C game-tree stack ground node is initialized with the out-of-range sentinels on both
    # sides, so the root window is [-66, 66]: the game-value range lies strictly inside it and
    # the root value is exact.
    state[2] = OUT_OF_RANGE_DEFEAT_SCORE
    state[3] = -OUT_OF_RANGE_DEFEAT_SCORE
    if log is None:
        value, fm, fo, fp, nodes, leafs = _ab_search(gp['mover'], gp['opponent'], gp['player'],
                                                     1, None, state)
    else:
        # The trace sink: the typed list of the 6-int node records, filled by the compiled
        # search at each node exit, replayed to the callback when the search completes.
        records = List.empty_list(nb.types.UniTuple(nb.types.int64, 6))
        value, fm, fo, fp, nodes, leafs = _ab_search(gp['mover'], gp['opponent'], gp['player'],
                                                     1, records, state)
        for rec in records:
            log(NodeRecord(rec[0], rec[1], Player(rec[2]), Move(rec[3]), Move(rec[4]), rec[5]))
    return SolverResult(game_value=GameValue(value),
                        final_game_position=make_game_position(Bitboard(fm), Bitboard(fo),
                                                               Player(fp)),
                        nodes=nodes, leafs=leafs)
