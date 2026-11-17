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
"""

from dataclasses import dataclass

import numpy as np
from pydantic import ConfigDict, validate_call

from reversi.board import (MOVE_PA, GamePosition, Move, Player, PositionField,
                           make_game_position, make_position, position_final_value,
                           position_legal_moves, position_make_move)


__all__ = ['SolverResult', 'minimax_solve']


@dataclass(frozen=True)
class SolverResult:
    """
    The result of an endgame solve: the game value seen from the point of view of the player to
    move at the root, the terminal game position of the best line, and the search counters.
    """
    game_value: np.int8
    final_game_position: np.void
    nodes: int
    leafs: int


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def minimax_solve(gp: GamePosition) -> SolverResult:
    """
    Solve the endgame exactly with a depth-first minimax (see the module docstring for the search
    contract) and return the game value, the final game position of the best line, and the node /
    leaf counts.

    Args:
        gp: the game position to solve (scalar only).

    Returns:
        The SolverResult of the search.
    """
    nodes = 0
    leafs = 0

    def search(p: PositionField, player: Player):
        # p: the position (the mover / opponent fields), player: the absolute player to move.
        nonlocal nodes, leafs
        nodes += 1
        legal = position_legal_moves(p)
        passing = False
        if not legal:
            # The mover has no legal move: is the game over, or does the turn pass?
            p_pass = position_make_move(p, MOVE_PA)
            legal_pass = position_legal_moves(p_pass)
            if not legal_pass:
                # A leaf: neither player has a legal move (one node, no pass).
                leafs += 1
                return (position_final_value(p),
                        make_game_position(p['mover'], p['opponent'], player))
            # The pass: a further node (the same board, the other player to move), and the value
            # comes back negated, as at every ply.
            p, player = p_pass, 1 - player
            nodes += 1
            legal = legal_pass
            passing = True
        best_value = None
        best_final = None
        for sq in range(64):
            if (legal >> sq) & 1:
                value, final = search(position_make_move(p, Move(sq)), 1 - player)
                value = -value
                if best_value is None or value > best_value:
                    best_value, best_final = value, final
        return (-best_value if passing else best_value), best_final

    value, final = search(make_position(gp['mover'], gp['opponent']), gp['player'])
    return SolverResult(game_value=np.int8(value), final_game_position=final,
                        nodes=nodes, leafs=leafs)
