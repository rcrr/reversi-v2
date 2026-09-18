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

from typing import Tuple, Annotated
from pydantic import validate_call, ConfigDict, Field

from reversi.tools.prng import MT19937, pick_one_from_set64_batch
from reversi.board import (Bitboard, BitboardArray, Move, MoveArray,
                           PositionField, PositionArray, bitboard_bsr,
                           position_flips, position_legal_moves,
                           position_empty_count)



__all__ = ['random_game_choose_move',
           'random_game_make_move',
           'random_game_play_path']



@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def random_game_choose_move(p: PositionField | PositionArray,
                            prng: MT19937) -> Bitboard | BitboardArray:
    """
    Returns a bitboard having one or zero bits set, chosen at random
    from the set of legal moves for the position.

    Dual scalar/array (D-219, the house D-140 pattern): a scalar
    PositionField gives a scalar Bitboard; a 1-D PositionArray gives
    a 1-D BitboardArray of the same length (the 2-D (N, 2) uint64
    input is coerced by the PositionArray validator).

    The PRNG stream contract: the elements consume their draws from
    the ONE injected stream in element order, exactly like a scalar
    loop — one draw per element with a non-empty legal-move set, no
    draw for a pass (an empty set). The array call is bit-identical
    to the sequential scalar processing of the same positions with
    the same stream (the needs are computed before any draw; one
    get_uint64_batch call feeds the prng batch pick
    pick_one_from_set64_batch — the single source of the pick
    technique, D-221).
    """
    if isinstance(p, np.ndarray):
        # D-219: the standard 1-D guard (house pattern, as position_flips)
        if p.ndim != 1:
            raise ValueError(f"When the argument p is an array, it must be 1D, got shape {p.shape}")
        lms = position_legal_moves(p)
        needs = (lms != np.uint64(0))
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
    swapped position (the players inverted) — never None.

    Dual scalar/array (D-220, the house D-140 pattern): a scalar
    PositionField gives the (PositionField, Move) pair; a 1-D
    PositionArray gives the (PositionArray, MoveArray) pair of the same
    length (the 2-D (N, 2) uint64 input is coerced by the PositionArray
    validator). The PRNG stream contract of random_game_choose_move is
    inherited verbatim: the array call is bit-identical to the
    sequential scalar processing of the same positions with the same
    stream (one draw per non-empty legal set, no draw for a pass).
    The array path composes the verified dual functions — the D-219
    batch pick + the D-140 position_flips (a zero element swaps the
    players, a legal element flips) — and the move codes come from
    popcount(move - 1): the bit index of a single-bit move, and the
    wrap-around of an empty move gives 64 = PA.
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

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def random_game_play_path(p: PositionField,
                          target_ec: TargetEcInt,
                          prng: MT19937) -> Tuple[PositionField, int]:
    """
    Apply a sequence of random legal moves to the game position to transition
    the game state from the given position to one with a number of empty cells
    equal to target_ec.

    Returns:
        tuple: A tuple containing the target position and the number of empty
        cells of this position.

        If a game-over position is encountered during the random path, it is
        returned along with its number of empty cells, which in this case will
        be greater than target_ec.

        If the initial game position already has a number of empty cells less
        than or equal to target_ec, the position is returned as the result
        along with its own number of empty cells.
    """
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
