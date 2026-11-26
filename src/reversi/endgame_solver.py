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

The es search (the C exact-solver strategy)
-------------------------------------------

`es_solve` ports the navigation of the C exact solver (`game_position_es_solve`): the
zero-window alpha-beta with the moves of every node ordered by the opponent's resulting
mobility. The candidate moves of a node are generated in the 10 D8 priority clusters (the
centre, the corners, then the rings outwards; the ascending square order within a cluster),
each one look-aheads the child's legal-move set, and the stable ascending insertion sort on
that count puts first the move leaving the opponent the fewest moves (the ties keep the
generation order). The root window is the C ground-node [-64, +64]. The node's own move set
is threaded through the state array (precomputed by the parent's look-ahead, so no
legal-move recomputation at the node entry — the C convention), the compiled twin
`_es_search` keeping the 6-parameter signature of the other kernels. The contract is the
game-tree identity with the C exact solver: the same nodes visited, in the same order — the
node / leaf counts and the per-node trace match the C game-tree log record by record.

The unified scalar / array API (the worker pool)
------------------------------------------------

Both public solvers take a scalar OR an array (the board.py idiom: one function, both forms): a
GamePosition scalar gives the `SolverResult` of the direct compiled search (the byte-identical
scalar path, the `log` trace callback supported), a `GamePositionArray` gives the
`SolverResultArray` of the worker pool (the `log` callback is the scalar form only and raises on
the array form). The pool runs the batch lanes in parallel on a pool of worker threads (one per
available CPU): each worker pulls the next unsolved lane from the work queue and runs the
compiled search directly (the per-lane pydantic validation is skipped — the batch boundary is
the only checked one), so the lanes solve in parallel and the wall time is the batch work over
the worker count (the njit search releases the GIL while running). The lanes are expected to
share the same empty count (the batch precondition, which keeps the batch on a single search
horizon): with `check_ec=True` the `uniform_empty_count` check runs up front and a non-uniform
batch raises, by default (False) the check is skipped and the precondition is the caller's. The
`SolverResultArray` is the parallel arrays (the per-lane game values, final game positions, node
/ leaf counts), each lane exactly the result of the scalar solve of that lane.

The command line
----------------

The module runs as a command (the Python replacement of the C `endgame_solver` binary):

    python -m reversi.endgame_solver -s es -g ..bw.bw....wwww...wwwwb.bbwbwbbb.bwbwwbb.wbbbww...wwwwww.w..w.bwb

`-s` selects the solver (`minimax`, `alphabeta`, `es`) and `-g` the 64-character game position
string; the output mirrors the C binary (the position, the node / leaf counts, the final
outcome: the best move and the position value).
"""

import argparse
import os
import queue
import sys
from dataclasses import dataclass
from threading import Thread
from typing import Any, Annotated, Callable, TypeAlias, Union

import numba as nb
import numpy as np
import numpy.typing as npt
from numba.typed import List
from pydantic import BeforeValidator, ConfigDict, validate_call

from reversi.board import (MOVE_NA, MOVE_PA, MOVE_UN, Bitboard, GamePositionArray,
                           GamePositionField, Move, Player, _popcount, bitboard_bsf,
                           bitboard_count, final_value_of, flips_of_move, game_position_from_str,
                           game_position_print, legal_moves_of, make_game_position, move_to_str,
                           other_player)


__all__ = ['OUT_OF_RANGE_DEFEAT_SCORE', 'GameValue', 'GameValueArray', 'NodeRecord',
           'SolverResult', 'SolverResultArray', 'minimax_solve', 'alphabeta_solve',
           'es_solve', 'uniform_empty_count']


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

#: The C es root window half (the C worst_score / best_score): the game-value range itself,
#: the ground-node initialization of the C exact solver (unlike the out-of-range sentinels of
#: the natural-order alpha-beta).
ES_ROOT_WINDOW = 64


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
    move at the root, the best move of the root (the move that achieves the value, in the
    search's own move order), the terminal game position of the best line, and the search
    counters.
    """
    game_value: GameValue
    best_move: Move
    final_game_position: GamePositionField
    nodes: int
    leafs: int


@dataclass(frozen=True)
class SolverResultArray:
    """
    The result of an array endgame solve: one entry per lane, as parallel arrays (the natural
    vectorized shape): the game values, the best moves, the terminal game positions of the best
    lines, and the search counters.
    """
    game_values: GameValueArray
    best_moves: npt.NDArray[np.uint8]
    final_game_positions: GamePositionArray
    nodes: npt.NDArray[np.int64]
    leafs: npt.NDArray[np.int64]


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
        The (value, best_move, final_mover, final_opponent, final_player, nodes, leafs) of the
        subtree.
    """
    state[0] += 1
    call_id = state[0]
    legal = legal_moves_of(mover, opponent)
    if not legal:
        if not legal_moves_of(opponent, mover):
            value = final_value_of(mover, opponent)
            if records is not None:
                records.append((call_id, level, player, state[1], MOVE_NA, value))
            return value, MOVE_NA, mover, opponent, player, 1, 1
        saved = state[1]
        state[1] = MOVE_PA
        value, bmv, fm, fo, fp, nodes, leafs = _search(opponent, mover, other_player(player), level + 1,
                                                  records, state)
        state[1] = saved
        value = -value
        if records is not None:
            records.append((call_id, level, player, state[1], MOVE_PA, value))
        return value, MOVE_PA, fm, fo, fp, nodes + 1, leafs
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
        value, bmv, fm, fo, fp, n, l = _search(opponent ^ flips, (mover ^ flips) | m,
                                          other_player(player), level + 1, records, state)
        state[1] = saved
        value = -value
        nodes += n
        leafs += l
        if value > best_value:
            best_value, best_move, best_fm, best_fo, best_fp = value, sq, fm, fo, fp
    if records is not None:
        records.append((call_id, level, player, state[1], best_move, best_value))
    return best_value, best_move, best_fm, best_fo, best_fp, nodes, leafs


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
        The (value, best_move, final_mover, final_opponent, final_player, nodes, leafs) of the
        subtree.
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
            return value, MOVE_NA, mover, opponent, player, 1, 1
        saved_pm, saved_a, saved_b = state[1], state[2], state[3]
        state[1] = MOVE_PA
        state[2], state[3] = -beta, -alpha
        value, bmv, fm, fo, fp, nodes, leafs = _ab_search(opponent, mover, other_player(player), level + 1,
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
        return value, MOVE_PA, fm, fo, fp, nodes + 1, leafs
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
        value, bmv, fm, fo, fp, n, l = _ab_search(opponent ^ flips, (mover ^ flips) | m,
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
                return best_value, best_move, best_fm, best_fo, best_fp, nodes, leafs
    if records is not None:
        records.append((call_id, level, player, state[1], best_move, best_value))
    return best_value, best_move, best_fm, best_fo, best_fp, nodes, leafs


def _mm_state():
    """The 2-element minimax state: the visit counter and the parent move (the root's MOVE_UN)."""
    state = np.zeros(2, dtype=np.int64)
    state[1] = MOVE_UN
    return state


def _ab_state():
    """
    The 4-element alpha-beta state: the minimax pair plus the C ground-node root window [-66, 66]
    (the game-value range lies strictly inside it, the root value is exact).
    """
    state = np.zeros(4, dtype=np.int64)
    state[1] = MOVE_UN
    state[2] = OUT_OF_RANGE_DEFEAT_SCORE
    state[3] = -OUT_OF_RANGE_DEFEAT_SCORE
    return state


def _solve_pool(gps, search, make_state, lane_setup=None):
    """
    The worker-pool array engine shared by the public solvers: one thread per available CPU pulls
    the next unsolved lane from the work queue (the dynamic dispatch, optimal for the solve-cost
    variance between endgames) and runs the compiled `search` on it — the per-lane pydantic
    validation skipped, the batch boundary the only checked one — filling the pre-allocated
    per-lane result slots. The njit search releases the GIL while running, so the wall time is
    the batch work over the worker count. `lane_setup` (optional) is a Python callable invoked
    as `lane_setup(state, i)` right after the per-lane state factory, for the solvers whose
    state carries a per-lane datum (the es root move set). Returns the seven result arrays (the
    values, the best moves, the final mover / opponent / player, the node / leaf counts).
    """
    n = gps.shape[0]
    values = np.empty(n, dtype=GameValue)
    best_moves = np.empty(n, dtype=Move)
    fm = np.empty(n, dtype=Bitboard)
    fo = np.empty(n, dtype=Bitboard)
    fp = np.empty(n, dtype=Player)
    nodes = np.empty(n, dtype=np.int64)
    leafs = np.empty(n, dtype=np.int64)
    if not n:
        return values, best_moves, fm, fo, fp, nodes, leafs
    movers = gps['mover']
    opponents = gps['opponent']
    players = gps['player']

    def solve_lane(i):
        # The fast path: the compiled search directly (no per-lane pydantic).
        state = make_state()
        if lane_setup is not None:
            lane_setup(state, i)
        v, bmv, f_m, f_o, f_p, nd, lf = search(movers[i], opponents[i], players[i], 1, None, state)
        values[i] = GameValue(v)
        best_moves[i] = bmv
        fm[i] = f_m
        fo[i] = f_o
        fp[i] = f_p
        nodes[i] = nd
        leafs[i] = lf

    work = queue.Queue()
    for i in range(n):
        work.put(i)
    errors = []

    def worker():
        while True:
            try:
                i = work.get_nowait()
            except queue.Empty:
                return
            try:
                solve_lane(i)
            except BaseException as e:  # surface the lane error at the batch boundary
                errors.append(e)

    threads = [Thread(target=worker) for _ in range(min(n, os.cpu_count() or 1))]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    if errors:
        raise errors[0]
    return values, best_moves, fm, fo, fp, nodes, leafs


# The 10 D8 priority-cluster masks of the C es move ordering (the exact `legal_moves_priority_mask`
# of the C exact solver): the board partitioned in the D8 rings (the centre, the corners, then the
# rings outwards). The candidate moves of a node are generated cluster by cluster, in the
# ascending square order within a cluster, before the stable sort on the look-ahead count.
_ES_PRIORITY_MASKS = np.array([
    0x0000001818000000,  # 0: D4, E4, E5, D5 (the centre)
    0x8100000000000081,  # 1: A1, H1, H8, A8 (the corners)
    0x2400810000810024,  # 2: C1, F1, F8, C8, A3, H3, H6, A6
    0x0000240000240000,  # 3: C3, F3, F6, C6
    0x1800008181000018,  # 4: D1, E1, E8, D8, A4, H4, H5, A5
    0x0000182424180000,  # 5: D3, E3, E6, D6, C4, F4, F5, C5
    0x0018004242001800,  # 6: D2, E2, E7, D7, B4, G4, G5, B5
    0x0024420000422400,  # 7: C2, F2, F7, C7, B3, G3, G6, B6
    0x4281000000008142,  # 8: B1, G1, G8, B8, A2, H2, H7, A7
    0x0042000000004200,  # 9: B2, G2, G7, B7
], dtype=np.uint64)


# The es `state` array layout: the 7-element header (the entry-order node counter and the
# current parent move, the alpha / beta window, and the move-set pair — the node's own legal
# moves, precomputed by its parent's ordering look-ahead, and its parent's: the pair
# distinguishes the pass node from the terminal one, the C `adjusted_move_count` convention)
# plus the per-level ordering scratch (the candidate move squares, the child mover / opponent
# bitboards, the child move sets, the look-ahead counts: 5 x 64 int64 slots PER LEVEL — the
# scratch of a node must survive its children's recursion, the C stack per-depth move lists:
# a single shared scratch region is clobbered by the first child). The scratch lives in the
# state array (allocated once at the root, threaded through the recursion — the C stack
# preallocation: a per-node np.empty would be a malloc storm on a 45M-node search).
# The 6-parameter signature is kept (the 7th scalar parameter is the numba 0.68 cache-loader
# segfault trigger, D-662).
_ES_STATE_HEADER = 7
# The per-level scratch field bases (within the 320-slot level slice): the candidate squares,
# the child mover / opponent bitboards, the child move sets, the look-ahead counts.
_ES_SQ_BASE = 0
_ES_CM_BASE = 64
_ES_CO_BASE = 128
_ES_RES_BASE = 192
_ES_CNT_BASE = 256
_ES_SCRATCH_STRIDE = 320
# The level bound: a game is at most 64 moves plus one pass before each (the second
# consecutive pass is the terminal) — 129 plies, the margin to 160.
_ES_MAX_LEVEL = 160
_ES_STATE_SIZE = _ES_STATE_HEADER + _ES_MAX_LEVEL * _ES_SCRATCH_STRIDE


def _es_state(root_move_set):
    """
    The es state array with the C es root window [-64, +64] (the C worst_score / best_score:
    the game-value range itself): the header (the counter, the root's parent move (MOVE_UN),
    the window, the move-set pair — the caller's root move set, no parent) and the zeroed
    per-level ordering scratch.
    """
    state = np.zeros(_ES_STATE_SIZE, dtype=np.int64)
    state[1] = MOVE_UN
    state[2] = -ES_ROOT_WINDOW
    state[3] = ES_ROOT_WINDOW
    # The astype reinterpretation (not the Python int round-trip, not the np.int64 constructor:
    # the bitboard with the high bit set overflows both into the int64 store): the uint64 bit
    # pattern re-read as int64 (two's complement).
    state[4] = np.uint64(root_move_set).astype(np.int64)
    return state


def _es_pool_state():
    """The es pool state factory: the root move set is filled per lane by the lane setup."""
    return _es_state(0)


@nb.njit(cache=True)
def _es_search(mover, opponent, player, level, records, state):
    """
    The numba-compiled exact-solver search, the port of the C `game_position_es_solve`
    navigation: the zero-window alpha-beta with the moves of every node ordered by the
    opponent's resulting mobility (the 10 D8 priority clusters, the stable ascending sort on
    the look-ahead legal-move count) — the deterministic visit of exactly the same nodes as
    the C exact solver (the game-tree identity: the node / leaf counts and the per-node trace
    match the C game-tree log record by record). The node's own move set is threaded through
    the state array (precomputed by the parent's ordering look-ahead: no legal-move
    recomputation at the node entry, the C convention), its parent's alongside it (the pass /
    terminal distinction). The per-node data (the entry-order counter, the parent move, the
    alpha / beta window, the move-set pair) is threaded through the 7-element shared state
    array with the same save/restore stack discipline as `_ab_search`.

    Returns:
        The (value, best_move, final_mover, final_opponent, final_player, nodes, leafs) of the
        subtree.
    """
    state[0] += 1
    call_id = state[0]
    own = np.uint64(state[4])
    if not own:
        if not state[5]:
            # The terminal: neither the node nor its parent has a legal move (the C
            # adjusted_move_count == 0): one node, the WOF value.
            value = final_value_of(mover, opponent)
            if records is not None:
                records.append((call_id, level, player, state[1], MOVE_NA, value))
            return value, MOVE_NA, mover, opponent, player, 1, 1
        # The pass node: the single pseudo-move, the child window the negated parent window.
        state[4] = int(legal_moves_of(opponent, mover))
        state[5] = 0
        saved_pm, saved_a, saved_b = state[1], state[2], state[3]
        state[1] = MOVE_PA
        state[2], state[3] = -state[3], -state[2]
        value, bmv, fm, fo, fp, nodes, leafs = _es_search(opponent, mover, other_player(player),
                                                     level + 1, records, state)
        state[1], state[2], state[3] = saved_pm, saved_a, saved_b
        value = -value
        if records is not None:
            records.append((call_id, level, player, state[1], MOVE_PA, value))
        return value, MOVE_PA, fm, fo, fp, nodes + 1, leafs
    # The ordering look-ahead: the candidate moves generated in the priority-cluster order
    # (the ascending square order within a cluster), each one with its child position and the
    # child's legal-move set (the opponent's resulting mobility) — the scratch in the state
    # array, in the node's own level slice (the C stack per-depth move lists: it must survive
    # the children's recursion), no per-node allocation.
    sqo = _ES_STATE_HEADER + (level - 1) * _ES_SCRATCH_STRIDE
    n = 0
    for i in range(10):
        to_search = own & _ES_PRIORITY_MASKS[i]
        while to_search:
            s = bitboard_bsf(to_search)
            to_search = to_search & (to_search - Bitboard(1))
            m = Bitboard(1) << Bitboard(s)
            fl = flips_of_move(mover, opponent, m)
            state[sqo + _ES_CM_BASE + n] = int(opponent ^ fl)
            state[sqo + _ES_CO_BASE + n] = int((mover ^ fl) | m)
            r = legal_moves_of(np.uint64(state[sqo + _ES_CM_BASE + n]),
                               np.uint64(state[sqo + _ES_CO_BASE + n]))
            state[sqo + _ES_RES_BASE + n] = int(r)
            state[sqo + _ES_CNT_BASE + n] = _popcount(r)
            state[sqo + n] = s
            n += 1
    # The stable insertion sort on the look-ahead count (ascending: the move leaving the
    # opponent the fewest moves first; the ties keep the generation order, the C contract).
    for i in range(1, n):
        j = i
        while j > 0 and state[sqo + _ES_CNT_BASE + j - 1] > state[sqo + _ES_CNT_BASE + j]:
            a = sqo + j - 1; b = sqo + j
            t = state[a]; state[a] = state[b]; state[b] = t
            a = sqo + _ES_CM_BASE + j - 1; b = sqo + _ES_CM_BASE + j
            t = state[a]; state[a] = state[b]; state[b] = t
            a = sqo + _ES_CO_BASE + j - 1; b = sqo + _ES_CO_BASE + j
            t = state[a]; state[a] = state[b]; state[b] = t
            a = sqo + _ES_RES_BASE + j - 1; b = sqo + _ES_RES_BASE + j
            t = state[a]; state[a] = state[b]; state[b] = t
            a = sqo + _ES_CNT_BASE + j - 1; b = sqo + _ES_CNT_BASE + j
            t = state[a]; state[a] = state[b]; state[b] = t
            j -= 1
    alpha = state[2]
    beta = state[3]
    best_value = alpha
    best_move = MOVE_NA
    best_fm, best_fo, best_fp = mover, opponent, player
    nodes = 1
    leafs = 0
    for i in range(n):
        saved_pm, saved_a, saved_b = state[1], state[2], state[3]
        state[1] = state[sqo + i]
        state[4] = state[sqo + _ES_RES_BASE + i]
        state[5] = int(own)
        state[2], state[3] = -beta, -alpha
        value, bmv, fm, fo, fp, nd, lf = _es_search(np.uint64(state[sqo + _ES_CM_BASE + i]),
                                               np.uint64(state[sqo + _ES_CO_BASE + i]),
                                               other_player(player), level + 1, records, state)
        state[1], state[2], state[3] = saved_pm, saved_a, saved_b
        value = -value
        nodes += nd
        leafs += lf
        if value > best_value:
            best_value, best_move, best_fm, best_fo, best_fp = (value, state[sqo + i],
                                                                fm, fo, fp)
            # The node's alpha rises with the best child: the NEXT sibling's window is derived
            # from it (the zero-window tightening, the source of the pruning).
            alpha = value
            if value >= beta:
                if records is not None:
                    records.append((call_id, level, player, state[1], best_move, best_value))
                return best_value, best_move, best_fm, best_fo, best_fp, nodes, leafs
    if records is not None:
        records.append((call_id, level, player, state[1], best_move, best_value))
    return best_value, best_move, best_fm, best_fo, best_fp, nodes, leafs


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def minimax_solve(gp: Union[GamePositionField, GamePositionArray],
                  log: Callable[[NodeRecord], None] | None = None,
                  check_ec: bool = False) -> Union[SolverResult, SolverResultArray]:
    """
    Solve the endgame(s) exactly with a depth-first minimax (see the module docstring for the
    search contract), scalar or array (the board.py idiom: one function, both forms). A
    GamePosition scalar gives the SolverResult of the direct compiled search; a GamePositionArray
    gives the SolverResultArray of the worker pool (one thread per CPU, the dynamic dispatch,
    every lane exactly its scalar result).

    Args:
        gp: the game position (scalar) or the game position array (one endgame per lane) to solve.
        log: optional callable, invoked with the `NodeRecord` of every visited node (in
            completion order, replayed when the search completes — see the "The trace" section of
            the module docstring). The scalar form only: the array form raises.
        check_ec: array form only (the scalar form ignores it): verify the uniform-empty-count
            batch precondition up front (default False).

    Returns:
        The SolverResult of the scalar solve, or the SolverResultArray of the batch.
    """
    if isinstance(gp, np.void):
        state = _mm_state()
        if log is None:
            value, bmv, fm, fo, fp, nodes, leafs = _search(gp['mover'], gp['opponent'], gp['player'],
                                                      1, None, state)
        else:
            # The trace sink: the typed list of the 6-int node records, filled by the compiled
            # search at each node exit, replayed to the callback when the search completes.
            records = List.empty_list(nb.types.UniTuple(nb.types.int64, 6))
            value, bmv, fm, fo, fp, nodes, leafs = _search(gp['mover'], gp['opponent'], gp['player'],
                                                      1, records, state)
            for rec in records:
                log(NodeRecord(rec[0], rec[1], Player(rec[2]), Move(rec[3]), Move(rec[4]), rec[5]))
        return SolverResult(game_value=GameValue(value),
                            best_move=Move(bmv),
                            final_game_position=make_game_position(Bitboard(fm), Bitboard(fo),
                                                                   Player(fp)),
                            nodes=nodes, leafs=leafs)
    if log is not None:
        raise ValueError('The log callback is the scalar form only (one trace per solve).')
    if check_ec:
        uniform_empty_count(gp)
    values, best_moves, fm, fo, fp, nodes, leafs = _solve_pool(gp, _search, _mm_state)
    return SolverResultArray(game_values=values,
                             best_moves=best_moves,
                             final_game_positions=make_game_position(fm, fo, fp),
                             nodes=nodes, leafs=leafs)


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def alphabeta_solve(gp: Union[GamePositionField, GamePositionArray],
                    log: Callable[[NodeRecord], None] | None = None,
                    check_ec: bool = False) -> Union[SolverResult, SolverResultArray]:
    """
    Solve the endgame(s) exactly with a depth-first alpha-beta search (the zero-window negamax
    with the natural move order of `minimax_solve`; see the "The alpha-beta search" section of
    the module docstring), scalar or array (the board.py idiom: one function, both forms). A
    GamePosition scalar gives the SolverResult of the direct compiled search (the node / leaf
    counts smaller than the minimax ones: the pruned subtrees are never visited); a
    GamePositionArray gives the SolverResultArray of the worker pool (one thread per CPU, the
    dynamic dispatch, every lane exactly its scalar result).

    Args:
        gp: the game position (scalar) or the game position array (one endgame per lane) to solve.
        log: optional callable, invoked with the `NodeRecord` of every visited node (in
            completion order, replayed when the search completes — see "The trace" section of the
            module docstring; at a cutoff node the record value is the search bound). The scalar
            form only: the array form raises.
        check_ec: array form only (the scalar form ignores it): verify the uniform-empty-count
            batch precondition up front (default False).

    Returns:
        The SolverResult of the scalar solve, or the SolverResultArray of the batch.
    """
    if isinstance(gp, np.void):
        state = _ab_state()
        if log is None:
            value, bmv, fm, fo, fp, nodes, leafs = _ab_search(gp['mover'], gp['opponent'], gp['player'],
                                                         1, None, state)
        else:
            # The trace sink: the typed list of the 6-int node records, filled by the compiled
            # search at each node exit, replayed to the callback when the search completes.
            records = List.empty_list(nb.types.UniTuple(nb.types.int64, 6))
            value, bmv, fm, fo, fp, nodes, leafs = _ab_search(gp['mover'], gp['opponent'], gp['player'],
                                                         1, records, state)
            for rec in records:
                log(NodeRecord(rec[0], rec[1], Player(rec[2]), Move(rec[3]), Move(rec[4]), rec[5]))
        return SolverResult(game_value=GameValue(value),
                            best_move=Move(bmv),
                            final_game_position=make_game_position(Bitboard(fm), Bitboard(fo),
                                                                   Player(fp)),
                            nodes=nodes, leafs=leafs)
    if log is not None:
        raise ValueError('The log callback is the scalar form only (one trace per solve).')
    if check_ec:
        uniform_empty_count(gp)
    values, best_moves, fm, fo, fp, nodes, leafs = _solve_pool(gp, _ab_search, _ab_state)
    return SolverResultArray(game_values=values,
                             best_moves=best_moves,
                             final_game_positions=make_game_position(fm, fo, fp),
                             nodes=nodes, leafs=leafs)


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def es_solve(gp: Union[GamePositionField, GamePositionArray],
             log: Callable[[NodeRecord], None] | None = None,
             check_ec: bool = False) -> Union[SolverResult, SolverResultArray]:
    """
    Solve the endgame(s) exactly with the C exact-solver strategy (see the "The es search
    (the C exact-solver strategy)" section of the module docstring): the zero-window
    alpha-beta with the moves of every node ordered by the opponent's resulting mobility (the
    10 D8 priority clusters, the stable ascending sort on the look-ahead legal-move count),
    the root window [-64, +64] — the deterministic navigation of exactly the same nodes as
    the C `es` solver. A GamePosition scalar gives the SolverResult of the direct compiled
    search (the `log` trace callback supported, one NodeRecord per visited node); a
    GamePositionArray gives the SolverResultArray of the worker pool (the `log` callback is
    the scalar form only and raises on the array form; the batch precondition, the uniform
    empty count, as the other solvers, with the opt-in `check_ec` check).

    Args:
        gp: the game position (scalar) or the game position array (one endgame per lane) to solve.
        log: optional callable, invoked with the `NodeRecord` of every visited node (in
            completion order, replayed when the search completes). The scalar form only.
        check_ec: array form only (the scalar form ignores it): verify the uniform-empty-count
            batch precondition up front (default False).

    Returns:
        The SolverResult of the scalar solve, or the SolverResultArray of the batch.
    """
    if isinstance(gp, np.void):
        state = _es_state(legal_moves_of(gp['mover'], gp['opponent']))
        if log is None:
            value, bmv, fm, fo, fp, nodes, leafs = _es_search(gp['mover'], gp['opponent'], gp['player'],
                                                         1, None, state)
        else:
            # The trace sink: the typed list of the 6-int node records, filled by the compiled
            # search at each node exit, replayed to the callback when the search completes.
            records = List.empty_list(nb.types.UniTuple(nb.types.int64, 6))
            value, bmv, fm, fo, fp, nodes, leafs = _es_search(gp['mover'], gp['opponent'], gp['player'],
                                                         1, records, state)
            for rec in records:
                log(NodeRecord(rec[0], rec[1], Player(rec[2]), Move(rec[3]), Move(rec[4]), rec[5]))
        return SolverResult(game_value=GameValue(value),
                            best_move=Move(bmv),
                            final_game_position=make_game_position(Bitboard(fm), Bitboard(fo),
                                                                   Player(fp)),
                            nodes=nodes, leafs=leafs)
    if log is not None:
        raise ValueError('The log callback is the scalar form only (one trace per solve).')
    if check_ec:
        uniform_empty_count(gp)
    movers = gp['mover']
    opponents = gp['opponent']

    def lane_setup(state, i):
        # The per-lane root move set (legal_moves_of is the scalar njit per-lane primitive:
        # the set is computed at the pool boundary, once per lane; the astype reinterpretation
        # as _es_state: the high-bit set would overflow the int64 store).
        state[4] = np.uint64(legal_moves_of(movers[i], opponents[i])).astype(np.int64)

    values, best_moves, fm, fo, fp, nodes, leafs = _solve_pool(gp, _es_search, _es_pool_state, lane_setup)
    return SolverResultArray(game_values=values,
                             best_moves=best_moves,
                             final_game_positions=make_game_position(fm, fo, fp),
                             nodes=nodes, leafs=leafs)


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def uniform_empty_count(gps: GamePositionArray) -> int:
    """
    Check that all the game positions of the array share the same empty count and return it (the
    batch precondition of the array form of the solvers: a uniform empty count keeps the batch on a
    single search horizon).

    Args:
        gps: the game position array to check.

    Returns:
        The common empty count.

    Raises:
        ValueError: the empty counts are not uniform (the message names the distinct counts and
            the number of lanes holding each).
    """
    occupied = bitboard_count(gps['mover'] | gps['opponent']).astype(np.int64)
    ecs = 64 - occupied
    unique, counts = np.unique(ecs, return_counts=True)
    if unique.size != 1:
        detail = ", ".join(f"ec={u} on {c} lane(s)" for u, c in zip(unique, counts))
        raise ValueError(f"Non-uniform empty counts: {detail}.")
    return int(ecs[0])


def main(argv=None):
    """
    The command line form (the Python replacement of the C `endgame_solver` binary):

        python -m reversi.endgame_solver -s es -g ..bw.bw....wwww...wwwwb...

    `-s` selects the solver (`minimax`, `alphabeta`, `es`), `-g` the 64-character game position
    string. The output mirrors the C binary: the position, the node / leaf counts, the final
    outcome (the best move and the position value).

    Args:
        argv: the argument list (default: the process command line).
    """
    parser = argparse.ArgumentParser(
        prog='python -m reversi.endgame_solver',
        description='Solve a Reversi endgame from a 64-character position string.')
    parser.add_argument('-s', '--solver', required=True, choices=('minimax', 'alphabeta', 'es'),
                        help='the solver to run')
    parser.add_argument('-g', '--game-position', required=True, dest='game_position',
                        help='the 64-character game position string')
    args = parser.parse_args(argv)

    solvers = {'minimax': minimax_solve, 'alphabeta': alphabeta_solve, 'es': es_solve}
    gp = game_position_from_str(args.game_position)
    r = solvers[args.solver](gp)
    # The C output: the position printed by game_position_print (the C game_position_x_print
    # replica), the blank line the C fprintf("%s\n") of the trailing-newline buffer leaves,
    # then the counts and the final outcome.
    # The output=sys.stdout at call time (the default argument is the stdout of the definition
    # time, invisible to the test's redirect_stdout).
    game_position_print(gp, output=sys.stdout)
    print()
    print(f"[node_count={r.nodes}, leaf_count={r.leafs}]")
    print(f"Final outcome: best move={move_to_str(r.best_move)}, position value={int(r.game_value)}")


if __name__ == '__main__':
    main()
