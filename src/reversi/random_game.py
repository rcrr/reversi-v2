# random_game.py
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

from __future__ import annotations

import numpy as np
import numpy.typing as npt

from typing import Tuple, Annotated
from pydantic import validate_call, ConfigDict, Field

from reversi.tools.prng import MT19937, pick_one_from_set64_batch
from reversi.board import (Bitboard, BitboardArray, Move, MoveArray,
                           PositionField, PositionArray, bitboard_bsr,
                           make_position, position_flips,
                           position_legal_moves, position_empty_count)



__all__ = ['random_game_choose_move',
           'random_game_make_move',
           'random_game_play_path']



#: The empty move set: the pass signal of the pick domain (the
#: (0, 64) sentinel bitboard).
_EMPTY_MOVE_SET: Bitboard = Bitboard(0)



@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def random_game_choose_move(p: PositionField | PositionArray,
                            prng: MT19937) -> Bitboard | BitboardArray:
    """
    Returns a bitboard having one or zero bits set, chosen at random
    from the set of legal moves for the position.

    Dual scalar/array: a scalar
    PositionField gives a scalar Bitboard; a 1-D PositionArray gives
    a 1-D BitboardArray of the same length (the 2-D (N, 2) uint64
    input is coerced by the PositionArray validator).

    The PRNG stream contract: the elements consume their draws from
    the ONE injected stream in element order, exactly like a scalar
    loop — one draw per element with a non-empty legal-move set, no
    draw for a pass (an empty set). The array call is bit-identical
    to the sequential scalar processing of the same positions with
    the same stream.
    """
    if isinstance(p, np.ndarray):
        # D-219: the standard 1-D guard (house pattern, as position_flips)
        if p.ndim != 1:
            raise ValueError(f"When the argument p is an array, it must be 1D, got shape {p.shape}")
        lms = position_legal_moves(p)
        needs = (lms != _EMPTY_MOVE_SET)
        draws = prng.get_uint64_batch(int(np.count_nonzero(needs)))
        slots = np.cumsum(needs, dtype=np.int64) - needs.astype(np.int64)
        return pick_one_from_set64_batch(lms, draws, slots)
    if isinstance(p, np.void):
        moves: Bitboard = position_legal_moves(p)
        move, _ = prng.choose_one_from_set64(moves)
        return move
    raise TypeError("Input must be a Position scalar or a Position array.")

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def random_game_make_move(p: PositionField | PositionArray,
                          prng: MT19937) -> Tuple[PositionField | PositionArray,
                                                  Move | MoveArray]:
    """
    Executes a random legal move on the position.

    Asks random_game_choose_move for the move to play, executes it on p via
    position_flips, and returns the resulting position together with the
    move that was played. The returned position is the one position_flips
    produces (the next player's view: the mover / opponent fields are
    swapped with respect to the input). When the position has no legal
    move the move is the pass (PA) and the returned position is the
    swapped position (the players inverted).

    Dual scalar/array: a scalar
    PositionField gives the (PositionField, Move) pair; a 1-D
    PositionArray gives the (PositionArray, MoveArray) pair of the same
    length (the 2-D (N, 2) uint64 input is coerced by the PositionArray
    validator) — the per-element semantics is the scalar one (a zero
    move swaps the players, a legal move flips). The PRNG stream
    contract of random_game_choose_move is inherited: the array call
    is bit-identical to the sequential scalar processing of the same
    positions with the same stream.
    """
    if isinstance(p, np.ndarray):
        # D-220: the standard 1-D guard (house pattern, as position_flips)
        if p.ndim != 1:
            raise ValueError(f"When the argument p is an array, it must be 1D, got shape {p.shape}")
        moves = random_game_choose_move(p, prng)
        _, new_p = position_flips(p, moves)
        move_codes = np.bitwise_count(moves - np.uint64(1)).astype(np.uint8)
        return new_p, move_codes
    if isinstance(p, np.void):
        move_bb: Bitboard = random_game_choose_move(p, prng)
        _, new_p = position_flips(p, move_bb)
        idx: int = bitboard_bsr(move_bb)
        move: Move = Move(64) if idx == -1 else Move(idx)
        return new_p, move
    raise TypeError("Input must be a Position scalar or a Position array.")

TargetEcInt = Annotated[int, Field(ge=0, le=60)]

#: Internal use function.
def _apply_picked_moves(movers: np.ndarray, opponents: np.ndarray,
                        lane_mask: np.ndarray, moves: np.ndarray,
                        swapped_view: bool):
    """
    Applies the picked single-bit moves to the masked lanes and
    returns the updated (movers, opponents) arrays (fresh copies —
    the input arrays are never mutated).

    The moves are executed by the D-140 position_flips on the lane
    subset: the CURRENT view (mover first), or the SWAPPED
    (opponent-first) view for the pass-and-reply lanes.
    position_flips returns the NEXT player's view, which — after the
    opponent's move — is the original mover's frame again, so the
    write-back maps the fields directly in both cases.
    """
    idx = np.flatnonzero(lane_mask)
    if idx.size == 0:
        return movers, opponents
    if swapped_view:
        view = make_position(opponents[idx], movers[idx])
    else:
        view = make_position(movers[idx], opponents[idx])
    _, updated = position_flips(view, moves[idx])
    movers = movers.copy()
    opponents = opponents.copy()
    movers[idx] = updated['mover']
    opponents[idx] = updated['opponent']
    return movers, opponents

#: Internal use function.
def _play_path_step(cur: np.ndarray, active: np.ndarray, target: np.uint8,
                    prng: MT19937):
    """
    Advances ONE step of the engine for every active lane; returns
    the updated (cur, ec, active).

    The lane classification (all draw-independent — the legal sets
    are pure computations):
      - mover_plays: the mover has a legal move — one draw, the disc
        is placed by the mover (position_flips on the current view);
      - mover_passes_opponent_plays: the mover is moveless and the
        opponent is not — the pass consumes no draw, the opponent
        plays from the SWAPPED view (one draw);
      - double_pass_game_over: both players are moveless — the lane
        ends, no draw, the position is left unchanged (the two
        scalar swaps restore the input view).

    Every non-terminal lane consumes EXACTLY ONE draw, in element
    order (the step-interleaved stream discipline).
    """
    lms_mover = position_legal_moves(cur)
    lms_opponent = position_legal_moves(make_position(cur['opponent'],
                                                      cur['mover']))
    mover_passes = active & (lms_mover == _EMPTY_MOVE_SET)
    mover_plays = active & (lms_mover != _EMPTY_MOVE_SET)
    double_pass_game_over = mover_passes & (lms_opponent == _EMPTY_MOVE_SET)
    mover_passes_opponent_plays = (mover_passes
                                   & (lms_opponent != _EMPTY_MOVE_SET))
    needs_draw = mover_plays | mover_passes_opponent_plays
    draws = prng.get_uint64_batch(int(np.count_nonzero(needs_draw)))
    slots = np.cumsum(needs_draw, dtype=np.int64) - needs_draw.astype(np.int64)
    pick_sets = np.where(mover_plays, lms_mover,
                         np.where(mover_passes_opponent_plays, lms_opponent,
                                  _EMPTY_MOVE_SET))
    moves = pick_one_from_set64_batch(pick_sets, draws, slots)
    movers, opponents = _apply_picked_moves(cur['mover'], cur['opponent'],
                                            mover_plays, moves,
                                            swapped_view=False)
    movers, opponents = _apply_picked_moves(movers, opponents,
                                            mover_passes_opponent_plays,
                                            moves, swapped_view=True)
    new_cur = make_position(movers, opponents)
    ec = position_empty_count(new_cur)
    active = active & ~double_pass_game_over & (ec > target)
    return new_cur, ec, active

#: Internal use function.
def _play_path_engine(cur: np.ndarray, target: np.uint8, prng: MT19937):
    """
    The array play-path engine: the step loop over the batch.

    The lanes advance in LOCKSTEP: at every step the active lanes
    draw once, in element order. Two facts pin the stream contract
    down: the call is DETERMINISTIC given the seed, and with N == 1
    the lockstep stream IS the lane's sequential stream, so the
    single-lane array call is bit-identical to the scalar call.

    The termination is mathematical: every non-terminal step
    decreases a lane's ec by exactly one and the game-over step ends
    the lane — the step bound is derived from the input (a lane
    needs at most its ec surplus over the target, plus one); a stall
    would raise, never hang.
    """
    ec = position_empty_count(cur)
    active = ec > target
    # The mathematical step bound: every non-terminal step decreases
    # a lane's ec by exactly one and the game-over step ends the
    # lane — a lane needs at most (its start ec - the target) steps
    # plus one; the bound below is that maximum over the lanes,
    # computed from the input (a stall is impossible by the math: it
    # would raise, never hang).
    max_steps = int(ec.max(initial=0)) - int(target) + 1
    for _step in range(max_steps):
        if not np.any(active):
            break
        cur, ec, active = _play_path_step(cur, active, target, prng)
    if np.any(active):
        raise RuntimeError("random_game_play_path: the step bound "
                           "(70) is exceeded — an active lane did "
                           "not terminate")
    return cur, ec

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def random_game_play_path(p: PositionField | PositionArray,
                          target_ec: TargetEcInt,
                          prng: MT19937) -> Tuple[PositionField | PositionArray,
                                                  np.uint8 | npt.NDArray[np.uint8]]:
    """
    Apply a sequence of random legal moves to the game position to transition
    the game state from the given position to one with a number of empty cells
    equal to target_ec.

    Returns:
        tuple: A tuple containing the target position and the number of empty
        cells of this position (an ordinal np.uint8).

        If a game-over position is encountered during the random path, it is
        returned along with its number of empty cells, which in this case will
        be greater than target_ec.

        If the initial game position already has a number of empty cells less
        than or equal to target_ec, the position is returned as the result
        along with its own number of empty cells.

    Dual scalar/array: a scalar
    PositionField gives the (PositionField, np.uint8) pair; a 1-D
    PositionArray gives the (PositionArray, uint8-array) pair of the
    same length (the 2-D (N, 2) uint64 input is coerced by the
    PositionArray validator). The PRNG stream contract of the array
    case: the lanes advance in LOCKSTEP — at every step the ACTIVE
    lanes draw once, in element order — exactly one draw per
    non-terminal lane, no draw for the game-over lanes. Two facts
    pin the contract down: the call is DETERMINISTIC given the seed,
    and with N == 1 the array call is BIT-IDENTICAL to the scalar
    call. The target is ONE shared value for the whole batch.
    """
    if isinstance(p, np.ndarray):
        # D-222: the standard 1-D guard (house pattern, as position_flips)
        if p.ndim != 1:
            raise ValueError(f"When the argument p is an array, it must be 1D, got shape {p.shape}")
        return _play_path_engine(p, np.uint8(target_ec), prng)
    if isinstance(p, np.void):
        PASS_MOVE = Move(64)
        ec = position_empty_count(p)

        while (ec > target_ec):
            p, move = random_game_make_move(p, prng)
            ec = position_empty_count(p)
            if move == PASS_MOVE:
                p, move = random_game_make_move(p, prng)
                if move == PASS_MOVE:
                    break

        return p, ec
    raise TypeError("Input must be a Position scalar or a Position array.")
