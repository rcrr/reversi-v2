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

from reversi.board import (Bitboard, PositionField, make_position)



__all__ = ['initial_game_position']



def initial_game_position() -> PositionField:
    """
    Returns the initial game position.

    A Reversi game starts with four discs placed in the center four squares
    of an 8×8 board (D4, E4, D5, and E5), with two black discs and two white
    discs arranged diagonally.
    Black, the mover, occupies squares E4 and D5. Otherwise White D4 and E5.
    """
    return make_position(Bitboard(0x0000000810000000),
                         Bitboard(0x0000001008000000))
