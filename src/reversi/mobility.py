#
# mobility.py
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

from __future__ import annotations

from typing import List, Literal, Union, IO

from reversi.board import (Bitboard, BitboardArray,
                           PositionArray,
                           bitboard_count,
                           legal_moves)

from reversi.index import (Index, IndexArray)

import sys
import io
import hashlib

import numpy as np
import numba as nb

from pydantic import validate_call, ConfigDict



__all__ = ['Mobility',
           'MobilitySet']


class Mobility:
    """
    The Mobility class is a measure of the available moves for ONE player, counted over a defined
    set of squares (the mask) and selected by a side flag. With side = 'mover' it counts the
    mover's legal moves in the mask (the standard "LMC", Legal Move Count, uses the full-board
    mask); with side = 'opponent' it counts the opponent's legal moves in the same mask (the
    standard "ALMC", Anti Legal Move Count, uses the full-board mask).

    On a position with the mover's legal moves lms and the opponent's legal moves alms, the
    feature index is:

        index = popcount(lms & mask)    if side = 'mover'
        index = popcount(alms & mask)   if side = 'opponent'

    For popcount(mask) = k, the index ranges over 0..k, so n_configurations = k + 1 is the count
    of the DISTINCT index values (the feature-table size), not the number of (lms, alms) pairs.
    Mobility features have no symmetry instances: n_instances = 1, the (mask, side) pair defines
    the feature directly.
    """

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def __init__(self, name: str, mask: Bitboard, side: Literal['mover', 'opponent']):
        """
        Initializes a new Mobility feature with the given name, mask, and side. The mask is the
        set of squares over which the moves are counted. The side selects whose moves are
        counted: 'mover' or 'opponent'.

        Args:
            name: The human-readable label for the mobility (e.g., "LMC", "ALMC").
            mask: The 64-bit mask defining the squares counted for this mobility feature.
            side: The player whose legal moves are counted over the mask ('mover' or 'opponent').
        """

        self.name = name
        self.mask = mask
        self.side = side

        self.n_configurations = bitboard_count(mask) + 1
        self.n_instances = 1

    def __repr__(self) -> str:
        """A concise one-line summary (same info as the first line of print())."""
        return (f"Mobility(name={self.name!r}, mask=0x{self.mask:016x}, "
                f"side={self.side!r})")

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def print(self, output: Union[IO, io.StringIO] = sys.stdout) -> None:
        """Prints the mobility to stdout as default, or any other IO."""
        prt = lambda msg: print(msg, file=output)
        prt(f"[Mobility: name = {self.name:8s}, mask = 0x{self.mask:016x}, side = {self.side}]")


#: ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###

class MobilitySet:
    """
    The MobilitySet class represents a collection of Mobility objects. It uses the tuple (mask,
    side) as a unique key — the SAME mask with the two different sides is a valid pair of
    features (the standard LMC + ALMC). Mobilities are stored in ascending sorted order based on
    their unique key (lexicographically: first by mask, then by side); names, masks and the
    compute_indexes() output columns all follow this sorted order.
    """

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def __init__(self, name: str, mobilities: List[Mobility]):
        """
        Initializes a MobilitySet instance with the given name and list of mobilities.

        Args:
            name: The name of the set.
            mobilities: The list of Mobility objects in the set.

        Raises:
            ValueError: If there are duplicate names in the mobilities.
            ValueError: If there are duplicate (mask, side) pairs in the mobilities.
        """
        # Extract and check for duplicate names
        names = [m.name for m in mobilities]
        if len(names) != len(set(names)):
            raise ValueError('Mobilities list contains duplicate names')

        # Extract composite keys as tuples and check for duplicates. Tuples are naturally
        # hashable and comparable in Python.
        keys = [(m.mask, m.side) for m in mobilities]
        if len(keys) != len(set(keys)):
            raise ValueError('Mobilities list contains duplicate (mask, side) pairs')

        # Sort mobilities by composite key value. Python sorts tuples lexicographically: first
        # by mask, then by side ('mover' < 'opponent').
        self.mobilities = sorted(mobilities, key=lambda m: (m.mask, m.side))

        # Create hash of sorted composite keys. Concatenate the mask bytes and the one-byte side
        # code (0 = mover, 1 = opponent) sequentially for each element.
        hash_input = b''.join(
            m.mask.tobytes() + np.uint8(0 if m.side == 'mover' else 1).tobytes()
            for m in self.mobilities
        )
        self.hash = hashlib.sha3_256(hash_input).hexdigest()

        self.name = name

    def __repr__(self) -> str:
        """A concise one-line summary (same info as the first line of print_summary())."""
        return (f"MobilitySet(name={self.name!r}, length={len(self.mobilities)}, "
                f"hash={self.hash})")

    @property
    def names(self) -> List[str]:
        """
        Returns a list of the names of the mobilities in the set.

        Returns:
            List[str]: The list of mobility names.
        """
        return [mobility.name for mobility in self.mobilities]

    @property
    def masks(self) -> np.ndarray:
        """
        Returns a 2D numpy array (shape = (N, 2)) of the (mask, side-code) pairs of the
        mobilities in the set. Column 0 is the mask, column 1 the one-byte side code
        (0 = mover, 1 = opponent).

        Returns:
            np.ndarray: The array of (mask, side-code) pairs.
        """
        arr = np.array([[m.mask, 0 if m.side == 'mover' else 1] for m in self.mobilities],
                       dtype=Bitboard)
        # Force the array to be strictly 2-dimensional (N, 2). If N=0, this correctly transforms
        # shape (0,) into shape (0, 2).
        return arr.reshape(-1, 2)

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def print_summary(self, output: Union[IO, io.StringIO] = sys.stdout) -> None:
        """
        Prints a summary representation of the mobility set.

        The summary includes the set name, hash, and one line per mobility (name, mask, side).
        """
        prt = lambda msg: print(msg, file=output)
        prt(f"MobilitySet: name = {self.name}, length = {len(self.mobilities)}, hash = {self.hash}")
        for m in self.mobilities:
            prt(f"  Mobility: name = {m.name:8s}, mask = 0x{m.mask:016x}, side = {m.side}")

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def compute_indexes(self, positions: PositionArray) -> IndexArray:
        """
        Computes the mobility indexes for an array of positions via the high-performance Numba
        kernel.

        For each position i and each mobility j, the returned index is:

            popcount(lms[i]  & mask_j)   if side_j = 'mover'
            popcount(alms[i] & mask_j)   if side_j = 'opponent'

        where lms[i] / alms[i] are the legal moves of the mover / opponent.

        Column contract: the L output columns follow the set's sorted (mask, side) order (the
        same order returned by names and masks), NOT the caller's insertion order. Label columns
        with ms.names to stay consistent.

        Args:
            positions: The input positions, of any shape.

        Returns:
            IndexArray: The index matrix of shape positions.shape + (L,).
        """

        L = len(self.mobilities)

        m = positions['mover']
        o = positions['opponent']

        lms = legal_moves(m, o)
        alms = legal_moves(o, m)

        # 1D configurations for efficient Numba sequential access
        masks = np.array([mo.mask for mo in self.mobilities], dtype=Bitboard)
        sides = np.array([0 if mo.side == 'mover' else 1 for mo in self.mobilities],
                          dtype=np.uint8)

        # Call the JIT-compiled function
        if lms.ndim == 1:
            # The 1-D fast path: the legal-move arrays go straight to the kernel.
            return _numba_compute_indexes_kernel(lms, alms, masks, sides)
        # The N-D contract: the 1-D kernel over the flattened C-order arrays, the output reshaped
        # to the positions shape + (L,).
        return _numba_compute_indexes_kernel(
            lms.ravel(), alms.ravel(), masks, sides).reshape(positions.shape + (L,))

#: End of MobilitySet class.

#: ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def popcount64(b: Bitboard | BitboardArray) -> Index | IndexArray:
    """
    Scalar/vectorized 64-bit population count, used to test the Numba popcount kernel. Not part
    of the public API.
    """
    return _numba_popcount64_kernel(b)


@nb.vectorize([nb.uint32(nb.uint64)], cache=True)
def _numba_popcount64_kernel(x):
    """
    High-performance 64-bit bitwise population count optimized for Numba. LLVM often replaces
    this implementation with native CPU popcnt instructions. Processes one uint64 but expands
    automatically to arrays via NumPy UFuncs.
    """
    x -= (x >> np.uint64(1)) & np.uint64(0x5555555555555555)
    x = (x & np.uint64(0x3333333333333333)) + ((x >> np.uint64(2)) & np.uint64(0x3333333333333333))
    x = (x + (x >> np.uint64(4))) & np.uint64(0x0F0F0F0F0F0F0F0F)
    x += x >> np.uint64(8)
    x += x >> np.uint64(16)
    x += x >> np.uint64(32)
    return np.uint32(x & np.uint64(0x7F))

@nb.njit(cache=True)
def _numba_compute_indexes_kernel(lms: np.ndarray, alms: np.ndarray,
                                  masks: np.ndarray, sides: np.ndarray) -> np.ndarray:
    """
    Optimized Numba kernel to process indexes loop-by-loop without temporary memory
    allocations. For each (position, mobility) pair it counts the legal moves of the side
    selected by the one-byte side code (0 = mover, 1 = opponent) over the mobility mask.
    """
    N = lms.shape[0]
    L = masks.shape[0]

    # Pre-allocate only the final output matrix to optimize memory.
    indexes = np.empty((N, L), dtype=Index)

    for i in range(N):
        for j in range(L):
            # Select the legal-move bitboard of the side this mobility counts.
            src = lms[i] if sides[j] == 0 else alms[i]
            indexes[i, j] = _numba_popcount64_kernel(src & masks[j])

    return indexes
