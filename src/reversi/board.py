#
# board.py
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

from typing import TypeAlias, Annotated, List, Any, Tuple

import numpy as np
import numpy.typing as npt

import numba as nb
from numba import types
from numba.extending import overload

import sys
import io
from typing import IO, Union

from pydantic import validate_call, ConfigDict, BeforeValidator, SkipValidation


__all__ = ['Square', 'SquareArray',
           'square_from_str', 'square_to_str', 'square_as_bitboard',
           'square_validate_range',
           'Move', 'MoveArray', 'MOVE_PA', 'MOVE_NA', 'MOVE_UN',
           'move_from_str', 'move_to_str', 'move_as_bitboard',
           'move_validate_range',
           'Bitboard', 'BitboardArray',
           'bitboard_from_signed_int', 'bitboard_to_signed_int', 'bitboard_from_hex_str',
           'bitboard_bsr', 'bitboard_count',
           'legal_moves_of', 'flips_of_move',
           'bitboard_transformations', 'bitboard_anti_transformations',  'bitboard_print',
           'bitboard_fa1h8', 'bitboard_fh1a8', 'bitboard_fhori', 'bitboard_fvert',
           'bitboard_ro000', 'bitboard_ro090', 'bitboard_ro180', 'bitboard_ro270',
           'bitboard_to_square_list', 'bitboard_to_square_array', 'bitboard_to_string_list',
           'bitboard_trans_fs', 'bitboard_anti_trans_fs',
           'bitboard_transformation_labels', 'bitboard_anti_transformation_labels',
           'Position', 'PositionField', 'PositionArray',
           'position_collisions', 'position_check_collisions', 'position_empty_count',
           'make_position', 'initial_game_position', 'position_eq',
           'position_print', 'position_empties',
           'position_legal_moves', 'legal_moves', 'position_legal_moves_count',
           'position_flips', 'position_make_move', 'position_count_difference',
           'position_final_value', 'position_has_to_pass', 'position_is_game_over',
           'position_is_move_legal', 'position_hash',
           'position_fa1h8', 'position_fh1a8', 'position_fhori', 'position_fvert',
           'position_ro000', 'position_ro090', 'position_ro180', 'position_ro270',
           'position_transformations', 'position_anti_transformations']



#: Represents a reversi board square indexed from 0 (A1) to 63 (H8) as a uint8 scalar.
Square: TypeAlias = np.uint8

def validate_square_array(v: any) -> any:
    """Validator to ensure a numpy array strictly uses uint8 dtype."""
    if isinstance(v, np.ndarray) and v.dtype != np.uint8:
        raise ValueError(f"Array dtype must be uint8, got {v.dtype}")
    return v

# A Pydantic-compatible type hint for Square (np.uint8) arrays.
SquareArray = Annotated[npt.NDArray[np.uint8], BeforeValidator(validate_square_array)]

__square_names__ = [
    'A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'H1',
    'A2', 'B2', 'C2', 'D2', 'E2', 'F2', 'G2', 'H2',
    'A3', 'B3', 'C3', 'D3', 'E3', 'F3', 'G3', 'H3',
    'A4', 'B4', 'C4', 'D4', 'E4', 'F4', 'G4', 'H4',
    'A5', 'B5', 'C5', 'D5', 'E5', 'F5', 'G5', 'H5',
    'A6', 'B6', 'C6', 'D6', 'E6', 'F6', 'G6', 'H6',
    'A7', 'B7', 'C7', 'D7', 'E7', 'F7', 'G7', 'H7',
    'A8', 'B8', 'C8', 'D8', 'E8', 'F8', 'G8', 'H8'
]

__square_max_value__ = len(__square_names__)

#: Moves are the actions during the game.
#: On top of the 64 moves corresponding to fill a corresponding square with a disk,
#: a few more are defined:
#: - PA : Pass - It is still a well defined by the game rule action
#: - NA : Not available - Used as a flag status by the program
#: - UN : Unknown - Used when for instance it is unknown the parent move of a given game position
Move: TypeAlias = np.uint8

__move_names__ = __square_names__ + ['PA', 'NA', 'UN']

__move_max_value__ = len(__move_names__)

#: The non-square move codes (the domain vocabulary): PA = pass, NA = not
#: available, UN = unknown. They sit above the square codes, in the order of
#: `__move_names__`.
MOVE_PA: Move = Move(64)
MOVE_NA: Move = Move(65)
MOVE_UN: Move = Move(66)

# A Pydantic-compatible type hint for Move (np.uint8) arrays.
MoveArray = Annotated[npt.NDArray[np.uint8], BeforeValidator(validate_square_array)]



#: A set of squares.
#: It is implemented as a bit-board of 64 bit using numpy.uint64 as alias type.
Bitboard: TypeAlias = np.uint64

def validate_bitboard_array(v: any) -> any:
    """Validator to ensure a numpy array strictly uses uint64 dtype."""
    if isinstance(v, np.ndarray) and v.dtype != np.uint64:
        raise ValueError(f"Array dtype must be uint64, got {v.dtype}")
    return v

#: A Pydantic-compatible type hint for Bitboard (np.uint64) arrays.
BitboardArray = Annotated[npt.NDArray[np.uint64], BeforeValidator(validate_bitboard_array)]



#: A game position is a structured native NumPy dtype.
#: Look into test_board, class TestPositionCreation, for more details in how to use it.
Position = np.dtype([('mover', Bitboard), ('opponent', Bitboard)])
PositionField = Annotated[np.void, SkipValidation[Any]]


def validate_position_array(v: any) -> any:
    """Validates and coerces 2D uint64 arrays into a 1D Position structured array."""
    if isinstance(v, np.ndarray) and v.dtype != Position:
        if v.dtype == np.uint64 and v.ndim == 2 and v.shape[1] == 2:
            return v.view(Position).reshape(-1)
        raise ValueError(f"Array dtype must be {Position}, got {v.dtype}")
    return v

PositionArray = Annotated[npt.NDArray[any], BeforeValidator(validate_position_array)]


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def make_position(mover: Union[Bitboard, np.ndarray, List],
                  opponent: Union[Bitboard, np.ndarray, List]
                  ) -> Union[np.void, np.ndarray]:
    """
    Creates a single Position scalar, a 1D PositionArray, or a 2D PositionArray.
    Allocates a fresh interleaved (shape, 2) buffer, copies the mover and
    opponent values into it, and returns a zero-copy view cast of that
    buffer to Position dtype. Inputs (lists or arrays) are never aliased;
    works for inputs of any dimensionality.
    """
    # ARRAY / LIST / MULTI-DIMENSIONAL CASE
    if isinstance(mover, (np.ndarray, list)) or isinstance(opponent, (np.ndarray, list)):
        # Convert to arrays to safely inspect shapes and sizes
        m_arr = np.asarray(mover, dtype=Bitboard)
        o_arr = np.asarray(opponent, dtype=Bitboard)

        # Enforce identical shape check across all dimensions
        if m_arr.shape != o_arr.shape:
            raise ValueError(
                f"Shape mismatch: 'mover' has shape {m_arr.shape}, "
                f"but 'opponent' has shape {o_arr.shape}."
            )

        # Capture the original structural shape (works for 1D, 2D, or higher)
        original_shape = m_arr.shape

        # Build the shape for the continuous memory block: append an axis of size 2 at the end
        # e.g., if original is (M, N), data_shape becomes (M, N, 2)
        data_shape = original_shape + (2,)

        # Allocate a contiguous C-memory block
        data = np.empty(data_shape, dtype=Bitboard)

        # Interleave the fields along the newly added trailing axis
        # Using ellipsis (...) dynamically handles any number of dimensions (1D, 2D, etc.)
        data[..., 0] = m_arr
        data[..., 1] = o_arr

        # Interpret the memory block as a structured array (Zero-Copy View)
        # The trailing dimension of size 2 collapses into the custom Position dtype
        return data.view(Position).reshape(original_shape)

    # SCALAR CASE
    return np.void((mover, opponent), dtype=Position)



#: Square methods.

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def square_from_str(name: str) -> Square:
    """
    Creates a new Square instance from a string representation.
    """
    try:
        index = __square_names__.index(name)
        return Square(index)
    except ValueError:
        raise ValueError(f"Invalid name: '{name}'. Must be one of {__square_names__}")

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def square_to_str(sq: Square) -> str:
    """
    Returns the string representation of the square.
    """
    return __square_names__[sq]

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def square_as_bitboard(sq: Square) -> Bitboard:
    """
    Converts the square to a bitboard containing only this square.
    """
    return Bitboard(Bitboard(1) << sq)

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def square_validate_range(sq: Square | SquareArray) -> None:
    if not isinstance(sq, np.ndarray):
        if not sq < __square_max_value__:
            raise ValueError(f"Value must be in the range [0..{__square_max_value__ - 1}].")
    else:
        if (sq >= __square_max_value__).any():
            raise ValueError(f"All values in the array must be in the range [0..{__square_max_value__ - 1}].")
    return



#: Move methods.

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def move_from_str(name: str) -> Move:
    """
    Creates a new Move instance from a string representation.
    """
    try:
        index = __move_names__.index(name)
        return Move(index)
    except ValueError:
        raise ValueError(f"Invalid name: '{name}'. Must be one of {__move_names__}")

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def move_to_str(mo: Move) -> str:
    """
    Returns the string representation of the move.
    """
    return __move_names__[mo]

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def move_as_bitboard(mo: Move) -> Bitboard:
    """
    Converts the move to a bitboard containing only the square indicated by the move.
    """
    # NumPy defines integer shifts by an amount >= the bit width as 0
    # (documented NumPy semantics; verified on NumPy 2.5.2), so the
    # non-square codes (MOVE_PA / MOVE_NA / MOVE_UN) wrap to the empty
    # bitboard.
    return Bitboard(Bitboard(1) << mo)

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def move_validate_range(mo: Move | MoveArray) -> None:
    if not isinstance(mo, np.ndarray):
        if not mo < __move_max_value__:
            raise ValueError(f"Value must be in the range [0..{__move_max_value__ - 1}].")
    else:
        if (mo >= __move_max_value__).any():
            raise ValueError(f"All values in the array must be in the range [0..{__move_max_value__ - 1}].")
    return



#: Bitboard methods.

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def bitboard_from_signed_int(i: np.int64 | npt.NDArray[np.int64]) -> Bitboard | BitboardArray:
    """
    Returns the Bitboard (uint64) representation of a numpy.int64 value,
    by reinterpreting its bits. Works on scalar and array inputs of any
    shape (the output keeps the input shape).
    For array input the result is a zero-copy view: it shares the input's
    data buffer (mutations on either side are visible on the other).
    """
    if not isinstance(i, np.ndarray):
        return i.view(Bitboard)[()]

    if i.dtype != np.int64:
        raise ValueError(f"Array dtype must be int64, got {i.dtype}")

    return i.view(Bitboard)

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def bitboard_to_signed_int(bb: Bitboard | BitboardArray) -> np.int64 | npt.NDArray[np.int64]:
    """
    Returns the signed int 64 bit long representation of the bitboard.
    It is useful to store and retrieve the value from PostgreSQL databases.
    Works on scalar and 1D array inputs.
    """

    # Standardize input by checking if it came in as a scalar or an array
    is_scalar = not isinstance(bb, np.ndarray)
    bb_arr = np.atleast_1d(bb)

    # Check layout constraints (Pydantic validates types, but we handle dimensions)
    if bb_arr.ndim != 1:
        raise ValueError(f"When the argument bb is an array, it must be 1D, got shape {bb_arr.shape}")

    # Adapt output representation to match original scalar or matrix input context
    if is_scalar:
        return bb.view(np.int64)[()]

    if bb_arr.dtype != np.uint64:
        raise ValueError(f"Array dtype must be uint64, got {bb.dtype}")

    return bb.view(np.int64)

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def bitboard_from_hex_str(h: str | npt.NDArray[str]) -> Bitboard | BitboardArray:
    """
    Returns a new Bitboard object from the hexadecimal string given as argument.
    The h string must be 16 character long having values in the range [0..F].
    Characters could be uppercase or lowercase.
    Note that the argument string is not prefixed with '0x'.
    Works on scalar and 1D array inputs.
    """

    # Standardize input by checking if it came in as a scalar or an array
    is_scalar = not isinstance(h, np.ndarray)
    h_arr = np.atleast_1d(h)

    # Check layout constraints (Pydantic validates types, but we handle dimensions)
    if h_arr.ndim != 1:
        raise ValueError(f"When the argument h is an array, it must be 1D, got shape {h_arr.shape}")

    # SCALAR CASE
    if is_scalar:
        if len(h) != 16:
            raise ValueError('Argument h must be a string of length 16')
        return Bitboard(int(h, 16))

    # ARRAY CASE
    # 1. Vectorized string length check using NumPy's character operations
    # This ensures every string in the array is exactly 16 characters long
    if not np.all(np.char.str_len(h_arr) == 16):
        raise ValueError("All hex strings in the array must be exactly 16 characters long")

    # 2. Vectorize the 'int(x, 16)' base conversion function
    # np.frompyfunc wraps the Python callable in a ufunc that applies it
    # element-wise (one Python call per element, not a C-level loop)
    # Arguments: (function, number_of_inputs, number_of_outputs)
    vectorized_hex_parser = np.frompyfunc(lambda x: int(x, 16), 1, 1)

    # 3. Apply the vectorized parser and cast the resulting object array to pure uint64
    result_array: BitboardArray = vectorized_hex_parser(h_arr).astype(np.uint64)

    return result_array

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def bitboard_bsr(bb: Bitboard) -> int:
    """
    Bit Scan Reverse.
    Returns the index of the MOST significant set bit.
    """
    n = int(bb)
    if n == 0: return -1
    return n.bit_length() - 1

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def bitboard_count(bb: Bitboard | BitboardArray) -> np.uint8 | npt.NDArray[np.uint8]:
    """
    Returns the number of squares in the set.
    Works on scalar and 1D array inputs; the output keeps the input
    shape (a scalar uint8 or an array of uint8).
    """
    bit_count = np.bitwise_count(bb)
    return bit_count

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def bitboard_print(bb: Bitboard, output: Union[IO, io.StringIO] = sys.stdout) -> None:
    """
    Prints a 2D representation of the bitboard to the given output.
    """
    sq = Bitboard(1)
    print('  a b c d e f g h', file=output)
    for row in range(0,8):
        print(row + 1, end = '', file=output)
        for col in range(0,8):
            if sq & bb != 0:
                c = 'x'
            else:
                c = '.'
            print(' ' + c, end = '', file=output)
            sq <<= 1
        print(file=output)
    return

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def bitboard_transformations(bb: Bitboard | BitboardArray) -> BitboardArray:
    """
    Applies the eight D8 transformations on the input bitboards.

     - 0 -> 0 : ro000
     - 0 -> 1 : ro090
     - 0 -> 2 : ro180
     - 0 -> 3 : ro270
     - 0 -> 4 : fvert
     - 0 -> 5 : fh1a8
     - 0 -> 6 : fhori
     - 0 -> 7 : fa1h8

    When input is a scalar Bitboard output is an array of Bitboards having shape (8,).
    When input is an array of Bitboards of length N, the output has shape (N, 8).
    """
    # Standardize input by checking if it came in as a scalar or an array
    is_scalar = not isinstance(bb, np.ndarray)
    bb_arr = np.atleast_1d(bb)

    # Check layout constraints (Pydantic validates types, but we handle dimensions)
    if bb_arr.ndim != 1:
        raise ValueError(f"When the argument bb is an array, it must be 1D, got shape {bb_arr.shape}")

    ts = _numba_bitboard_transformations(bb_arr)

    # Adapt output representation to match original scalar or matrix input context
    if is_scalar:
        return ts.flatten().view(Bitboard)

    return ts.view(Bitboard)

@nb.njit(parallel=True, cache=True)
def _numba_bitboard_transformations(bb_arr: BitboardArray) -> BitboardArray:

    # Allocate memory for output transformations matrix
    n = bb_arr.shape[0]
    ts = np.empty((n, 8), dtype=Bitboard)

    for i in nb.prange(n):

        value = bb_arr[i]
        fh = _numba_fhori_scalar_impl(value)

        ts[i, 0] = value
        ts[i, 1] = _numba_fa1h8_scalar_impl(fh)
        ts[i, 2] = _numba_fvert_scalar_impl(fh)
        ts[i, 3] = _numba_fh1a8_scalar_impl(fh)
        ts[i, 4] = _numba_fvert_scalar_impl(value)
        ts[i, 5] = _numba_fh1a8_scalar_impl(value)
        ts[i, 6] = fh
        ts[i, 7] = _numba_fa1h8_scalar_impl(value)

    return ts

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def bitboard_anti_transformations(bb: Bitboard | BitboardArray) -> BitboardArray:
    """
    Applies the eight D8 anti-transformations on the input bitboards.

     - 0 -> 0 : ro000
     - 0 -> 1 : ro270
     - 0 -> 2 : ro180
     - 0 -> 3 : ro090
     - 0 -> 4 : fvert
     - 0 -> 5 : fh1a8
     - 0 -> 6 : fhori
     - 0 -> 7 : fa1h8

    When input is a scalar Bitboard output is an array of Bitboards having shape (8,).
    When input is an array of Bitboards of length N, the output has shape (N, 8).

    Applies the anti-transformations by reversing index 1 and 3 of bitboard_transformations.
    Operates in-place on the generated matrix for maximum efficiency.
    """
    # Standardize input by checking if it came in as a scalar or an array
    is_scalar = not isinstance(bb, np.ndarray)
    bb_arr = np.atleast_1d(bb)

    # Check layout constraints (Pydantic validates types, but we handle dimensions)
    if bb_arr.ndim != 1:
        raise ValueError(f"When the argument bb is an array, it must be 1D, got shape {bb_arr.shape}")

    ts = _numba_bitboard_anti_transformations(bb_arr)

    # Adapt output representation to match original scalar or matrix input context
    if is_scalar:
        return ts.flatten().view(Bitboard)

    return ts.view(Bitboard)

@nb.njit(parallel=True, cache=True)
def _numba_bitboard_anti_transformations(bb_arr: BitboardArray) -> BitboardArray:

    # Allocate memory for output transformations matrix
    n = bb_arr.shape[0]
    ts = np.empty((n, 8), dtype=Bitboard)

    for i in nb.prange(n):

        value = bb_arr[i]
        fh = _numba_fhori_scalar_impl(value)

        ts[i, 0] = value
        ts[i, 1] = _numba_fh1a8_scalar_impl(fh)
        ts[i, 2] = _numba_fvert_scalar_impl(fh)
        ts[i, 3] = _numba_fa1h8_scalar_impl(fh)
        ts[i, 4] = _numba_fvert_scalar_impl(value)
        ts[i, 5] = _numba_fh1a8_scalar_impl(value)
        ts[i, 6] = fh
        ts[i, 7] = _numba_fa1h8_scalar_impl(value)

    return ts

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def bitboard_fa1h8(bb: Bitboard | BitboardArray) -> Bitboard | BitboardArray:
    """
    Reflects a bitboard, or an array of bitboards, on the diagonal a1-h8.
    Square h1 is mapped to a8 and vice versa.

    .    ---- input ----    ---- output ---
    .
    .    a b c d e f g h    a b c d e f g h
    .
    . 1  . 1 1 1 1 . . .    . . . . . . . .
    . 2  . 1 . . . 1 . .    1 1 1 1 1 1 1 1
    . 3  . 1 . . . 1 . .    1 . . . 1 . . .
    . 4  . 1 . . 1 . . .    1 . . . 1 1 . .
    . 5  . 1 1 1 . . . .    1 . . 1 . . 1 .
    . 6  . 1 . 1 . . . .    . 1 1 . . . . 1
    . 7  . 1 . . 1 . . .    . . . . . . . .
    . 8  . 1 . . . 1 . .    . . . . . . . .

    """
    if isinstance(bb, np.ndarray):
        return _numba_fa1h8_array_impl(bb)
    else:
        return Bitboard(_numba_fa1h8_scalar_impl(bb))

@overload(bitboard_fa1h8)
def _numba_ol_bitboard_fa1h8(bb):
    if isinstance(bb, types.Array):
        return lambda bb: _numba_fa1h8_array_impl(bb)
    else:
        return lambda bb: _numba_fa1h8_scalar_impl(bb)

@nb.njit(inline='always')
def _numba_fa1h8_scalar_impl(s):
    k1 = Bitboard(0x5500550055005500)
    k2 = Bitboard(0x3333000033330000)
    k4 = Bitboard(0x0f0f0f0f00000000)
    t =      k4 & (s ^ (s << 28))
    s = s ^       (t ^ (t >> 28))
    t =      k2 & (s ^ (s << 14))
    s = s ^       (t ^ (t >> 14))
    t =      k1 & (s ^ (s << 7))
    s = s ^       (t ^ (t >> 7))
    return s

@nb.njit(parallel=True, cache=True)
def _numba_fa1h8_array_impl(arr):
    N = arr.shape[0]
    out = np.empty(N, dtype=Bitboard)
    for i in nb.prange(N):
        out[i] = _numba_fa1h8_scalar_impl(arr[i])
    return out

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def bitboard_fh1a8(bb: Bitboard | BitboardArray) -> Bitboard | BitboardArray:
    """
    Reflects a bitboard, or an array of bitboards, on the diagonal h1-a8.
    Square a1 is mapped to h8 and vice versa.

    .    ---- input ----    ---- output ---
    .
    .    a b c d e f g h    a b c d e f g h
    .
    . 1  . 1 1 1 1 . . .    . . . . . . . .
    . 2  . 1 . . . 1 . .    . . . . . . . .
    . 3  . 1 . . . 1 . .    1 . . . . 1 1 .
    . 4  . 1 . . 1 . . .    . 1 . . 1 . . 1
    . 5  . 1 1 1 . . . .    . . 1 1 . . . 1
    . 6  . 1 . 1 . . . .    . . . 1 . . . 1
    . 7  . 1 . . 1 . . .    1 1 1 1 1 1 1 1
    . 8  . 1 . . . 1 . .    . . . . . . . .

    """
    if isinstance(bb, np.ndarray):
        return _numba_fh1a8_array_impl(bb)
    else:
        return Bitboard(_numba_fh1a8_scalar_impl(bb))

@overload(bitboard_fh1a8)
def _numba_ol_bitboard_fh1a8(bb):
    if isinstance(bb, types.Array):
        return lambda bb: _numba_fh1a8_array_impl(bb)
    else:
        return lambda bb: _numba_fh1a8_scalar_impl(bb)

@nb.njit(inline='always')
def _numba_fh1a8_scalar_impl(s):
    k1 = Bitboard(0xaa00aa00aa00aa00)
    k2 = Bitboard(0xcccc0000cccc0000)
    k4 = Bitboard(0xf0f0f0f00f0f0f0f)
    t =            s ^ (s << 36)
    s = s ^ (k4 & (t ^ (s >> 36)))
    t =      k2 & (s ^ (s << 18))
    s = s ^       (t ^ (t >> 18))
    t =      k1 & (s ^ (s << 9))
    s = s ^       (t ^ (t >> 9))
    return s

@nb.njit(parallel=True, cache=True)
def _numba_fh1a8_array_impl(arr):
    N = arr.shape[0]
    out = np.empty(N, dtype=Bitboard)
    for i in nb.prange(N):
        out[i] = _numba_fh1a8_scalar_impl(arr[i])
    return out

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def bitboard_fhori(bb: Bitboard | BitboardArray) -> Bitboard | BitboardArray:
    """
    Reflects the bitboard, or the array of bitboards, horizontally (on the horizontal axis).
    Row 1 is mapped to row 8 and vice versa.

    .    ---- input ----    ---- output ---
    .
    .    a b c d e f g h    a b c d e f g h
    .
    . 1  . 1 1 1 1 . . .    . 1 . . . 1 . .
    . 2  . 1 . . . 1 . .    . 1 . . 1 . . .
    . 3  . 1 . . . 1 . .    . 1 . 1 . . . .
    . 4  . 1 . . 1 . . .    . 1 1 1 . . . .
    . 5  . 1 1 1 . . . .    . 1 . . 1 . . .
    . 6  . 1 . 1 . . . .    . 1 . . . 1 . .
    . 7  . 1 . . 1 . . .    . 1 . . . 1 . .
    . 8  . 1 . . . 1 . .    . 1 1 1 1 . . .

    """
    if isinstance(bb, np.ndarray):
        return _numba_fhori_array_impl(bb)
    else:
        return Bitboard(_numba_fhori_scalar_impl(bb))

@overload(bitboard_fhori)
def _numba_ol_bitboard_fhori(bb):
    if isinstance(bb, types.Array):
        return lambda bb: _numba_fhori_array_impl(bb)
    else:
        return lambda bb: _numba_fhori_scalar_impl(bb)

@nb.njit(inline='always')
def _numba_fhori_scalar_impl(s):
    mask56 = Bitboard(0xFF00000000000000)
    mask48 = Bitboard(0x00FF000000000000)
    mask40 = Bitboard(0x0000FF0000000000)
    mask32 = Bitboard(0x000000FF00000000)
    mask24 = Bitboard(0x00000000FF000000)
    mask16 = Bitboard(0x0000000000FF0000)
    mask08 = Bitboard(0x000000000000FF00)
    mask00 = Bitboard(0x00000000000000FF)
    s = (((s << 56) & mask56) |
         ((s << 40) & mask48) |
         ((s << 24) & mask40) |
         ((s <<  8) & mask32) |
         ((s >>  8) & mask24) |
         ((s >> 24) & mask16) |
         ((s >> 40) & mask08) |
         ((s >> 56) & mask00))
    return s

@nb.njit(parallel=True, cache=True)
def _numba_fhori_array_impl(arr):
    N = arr.shape[0]
    out = np.empty(N, dtype=Bitboard)
    for i in nb.prange(N):
        out[i] = _numba_fhori_scalar_impl(arr[i])
    return out

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def bitboard_fvert(bb: Bitboard | BitboardArray) -> Bitboard | BitboardArray:
    """
    Reflects the bitboard, or the array of bitboards, vertically (on the vertical axis).
    Column a is mapped to column h and vice versa.

    .    ---- input ----    ---- output ---
    .
    .    a b c d e f g h    a b c d e f g h
    .
    . 1  . 1 1 1 1 . . .    . . . 1 1 1 1 .
    . 2  . 1 . . . 1 . .    . . 1 . . . 1 .
    . 3  . 1 . . . 1 . .    . . 1 . . . 1 .
    . 4  . 1 . . 1 . . .    . . . 1 . . 1 .
    . 5  . 1 1 1 . . . .    . . . . 1 1 1 .
    . 6  . 1 . 1 . . . .    . . . . 1 . 1 .
    . 7  . 1 . . 1 . . .    . . . 1 . . 1 .
    . 8  . 1 . . . 1 . .    . . 1 . . . 1 .

    """
    if isinstance(bb, np.ndarray):
        return _numba_fvert_array_impl(bb)
    else:
        return Bitboard(_numba_fvert_scalar_impl(bb))

@overload(bitboard_fvert)
def _numba_ol_bitboard_fvert(bb):
    if isinstance(bb, types.Array):
        return lambda bb: _numba_fvert_array_impl(bb)
    else:
        return lambda bb: _numba_fvert_scalar_impl(bb)

@nb.njit(inline='always')
def _numba_fvert_scalar_impl(s):
    k1 = Bitboard(0x5555555555555555)
    k2 = Bitboard(0x3333333333333333)
    k4 = Bitboard(0x0f0f0f0f0f0f0f0f)
    s = ((s >> 1) & k1) | ((s & k1) << 1)
    s = ((s >> 2) & k2) | ((s & k2) << 2)
    s = ((s >> 4) & k4) | ((s & k4) << 4)
    return s

@nb.njit(parallel=True, cache=True)
def _numba_fvert_array_impl(arr):
    N = arr.shape[0]
    out = np.empty(N, dtype=Bitboard)
    for i in nb.prange(N):
        out[i] = _numba_fvert_scalar_impl(arr[i])
    return out

#: -------------------------------------

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def bitboard_ro000(bb: Bitboard | BitboardArray) -> Bitboard | BitboardArray:
    """
    Returns the bitboard, or the array of bitboards, unchanged
    (rotated by zero degree).
    Conceptually it applies a rotation of zero degrees.
    It is the identity transformation: like the other seven D8
    functions, the result is a fresh copy of the input (no aliasing),
    so the identity contract is the same at the bitboard and the
    position layers (position_ro000).

    .    ---- input ----    ---- output ---
    .
    .    a b c d e f g h    a b c d e f g h
    .
    . 1  . 1 1 1 1 . . .    . 1 1 1 1 . . .
    . 2  . 1 . . . 1 . .    . 1 . . . 1 . .
    . 3  . 1 . . . 1 . .    . 1 . . . 1 . .
    . 4  . 1 . . 1 . . .    . 1 . . 1 . . .
    . 5  . 1 1 1 . . . .    . 1 1 1 . . . .
    . 6  . 1 . 1 . . . .    . 1 . 1 . . . .
    . 7  . 1 . . 1 . . .    . 1 . . 1 . . .
    . 8  . 1 . . . 1 . .    . 1 . . . 1 . .

    """
    if isinstance(bb, np.ndarray):
        return bb.copy()
    return Bitboard(bb)

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def bitboard_ro090(bb: Bitboard | BitboardArray) -> Bitboard | BitboardArray:
    """
    Rotates the bitboard, or the array of bitboards, by 90 degrees clockwise.
    Square a1 is mapped to h1, and b1 is mapped to h2.

    .    ---- input ----    ---- output ---
    .
    .    a b c d e f g h    a b c d e f g h
    .
    . 1  . 1 1 1 1 . . .    . . . . . . . .
    . 2  . 1 . . . 1 . .    1 1 1 1 1 1 1 1
    . 3  . 1 . . . 1 . .    . . . 1 . . . 1
    . 4  . 1 . . 1 . . .    . . 1 1 . . . 1
    . 5  . 1 1 1 . . . .    . 1 . . 1 . . 1
    . 6  . 1 . 1 . . . .    1 . . . . 1 1 .
    . 7  . 1 . . 1 . . .    . . . . . . . .
    . 8  . 1 . . . 1 . .    . . . . . . . .

    """

    return bitboard_fhori(bitboard_fh1a8(bb))

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def bitboard_ro180(bb: Bitboard | BitboardArray) -> Bitboard | BitboardArray:
    """
    Rotates the bitboard, or the array of bitboards, by 180 degrees.
    Square a1 is mapped to h8, and b1 is mapped to g8.

    .    ---- input ----    ---- output ---
    .
    .    a b c d e f g h    a b c d e f g h
    .
    . 1  . 1 1 1 1 . . .    . . 1 . . . 1 .
    . 2  . 1 . . . 1 . .    . . . 1 . . 1 .
    . 3  . 1 . . . 1 . .    . . . . 1 . 1 .
    . 4  . 1 . . 1 . . .    . . . . 1 1 1 .
    . 5  . 1 1 1 . . . .    . . . 1 . . 1 .
    . 6  . 1 . 1 . . . .    . . 1 . . . 1 .
    . 7  . 1 . . 1 . . .    . . 1 . . . 1 .
    . 8  . 1 . . . 1 . .    . . . 1 1 1 1 .

    """

    return bitboard_fh1a8(bitboard_fa1h8(bb))

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def bitboard_ro270(bb: Bitboard | BitboardArray) -> Bitboard | BitboardArray:
    """
    Rotates the bitboard, or the array of bitboards, by 270 degrees clockwise.
    Square a1 is mapped to a8, and b1 is mapped to a7.

    .    ---- input ----    ---- output ---
    .
    .    a b c d e f g h    a b c d e f g h
    .
    . 1  . 1 1 1 1 . . .    . . . . . . . .
    . 2  . 1 . . . 1 . .    . . . . . . . .
    . 3  . 1 . . . 1 . .    . 1 1 . . . . 1
    . 4  . 1 . . 1 . . .    1 . . 1 . . 1 .
    . 5  . 1 1 1 . . . .    1 . . . 1 1 . .
    . 6  . 1 . 1 . . . .    1 . . . 1 . . .
    . 7  . 1 . . 1 . . .    1 1 1 1 1 1 1 1
    . 8  . 1 . . . 1 . .    . . . . . . . .

    """

    return bitboard_fh1a8(bitboard_fhori(bb))

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def bitboard_to_square_list(bb: Bitboard) -> List[Square]:
    """
    Returns the bitboard represented as a list of squares.
    Squares are ordered from larger (H8) to smaller (A1).
    """

    squares = []

    if not bb == 0:
        while bb:
            sq = bitboard_bsr(bb)
            squares.append(Square(sq))
            bb = Bitboard(bb ^ (Bitboard(1) << sq))

    return squares

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def bitboard_to_square_array(bb: Bitboard) -> SquareArray:
    """
    Returns the square set as a numpy array of squares.
    """
    return np.array(bitboard_to_square_list(bb), dtype=Square)

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def bitboard_to_string_list(bb: Bitboard) -> List[str]:
    """
    Returns the bitboard as a list of strings.
    """
    squares = bitboard_to_square_list(bb)
    return [square_to_str(sq) for sq in squares]

#: Transformation Functions
#:   bitboard_trans_fs (list): The set of functions used to transform the bitboard.
#:   bitboard_anti_trans_fs (list): The inverse functions used to map back to the original configuration.
bitboard_trans_fs = [
    bitboard_ro000,
    bitboard_ro090,
    bitboard_ro180,
    bitboard_ro270,
    bitboard_fvert,
    bitboard_fh1a8,
    bitboard_fhori,
    bitboard_fa1h8,
]

#: Anti Transformation Functions
#:   bitboard_anti_trans_fs (list): The inverse functions used to map back to the original configuration.
bitboard_anti_trans_fs = [
    bitboard_ro000,
    bitboard_ro270,
    bitboard_ro180,
    bitboard_ro090,
    bitboard_fvert,
    bitboard_fh1a8,
    bitboard_fhori,
    bitboard_fa1h8,
]

#: Transformation Labels
#:   bitboard_transformation_labels: The set of labels describing the transformations of the bitboard.
bitboard_transformation_labels = [
    'ro000',
    'ro090',
    'ro180',
    'ro270',
    'fvert',
    'fh1a8',
    'fhori',
    'fa1h8',
]

#: Anti Transformation Labels
#:   bitboard_anti_transformation_labels: The set of labels describing the inverse transformations of the bitboard.
bitboard_anti_transformation_labels = [
    'ro000',
    'ro270',
    'ro180',
    'ro090',
    'fvert',
    'fh1a8',
    'fhori',
    'fa1h8',
]



#: Position methods.

def initial_game_position() -> PositionField:
    """
    Returns the initial game position.

    A Reversi game starts with four discs placed in the center four squares
    of an 8×8 board (D4, E4, D5, and E5), with two black discs and two white
    discs arranged diagonally.
    Black, the starting player (the mover), occupies squares E4 and D5,
    while White occupies D4 and E5.
    .
    .        C   D   E   F
    .      +---+---+---+---+
    .    3 |   |   |   |   |
    .      +---+---+---+---+
    .    4 |   | W | B |   |  (W = White, B = Black)
    .      +---+---+---+---+
    .    5 |   | B | W |   |
    .      +---+---+---+---+
    .    6 |   |   |   |   |
    .      +---+---+---+---+
    .
    """
    return make_position(Bitboard(0x0000000810000000),
                         Bitboard(0x0000001008000000))

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def position_eq(pos_a: PositionField | PositionArray, pos_b: PositionField | PositionArray) -> bool:
    return np.array_equal(pos_a, pos_b)

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def position_print(p: PositionField, output: Union[IO, io.StringIO] = sys.stdout) -> None:
    """
    Prints a 2D representation of the position to the given output.
    """
    sq = Bitboard(1)
    print('  a b c d e f g h', file=output)
    for row in range(0,8):
        print(row + 1, end = '', file=output)
        for col in range(0,8):
            if sq & p['mover'] != 0:
                c = '@'
            elif sq & p['opponent'] != 0:
                c = 'O'
            else:
                c = '.'
            print(' ' + c, end = '', file=output)
            sq <<= 1
        print(file=output)
    return

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def position_empties(p: PositionField | PositionArray) -> Bitboard | BitboardArray:
    """
    Returns the set of empty squares in the game position.
    Works on scalar and array inputs of any shape (output keeps the input shape).
    """
    return ~(p['mover'] | p['opponent'])

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def position_empty_count(p: PositionField | PositionArray) -> np.uint8 | npt.NDArray[np.uint8]:
    """
    Returns the count of empty squares in the game position.
    Works on scalar and array inputs of any shape (the output keeps the
    input shape: a scalar uint8 or an array of uint8).
    """
    return bitboard_count(~(p['mover'] | p['opponent']))

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def position_collisions(p: PositionField | PositionArray) -> Bitboard | BitboardArray:
    """
    Returns the set of overlapping squares between mover and opponent.
    Given the observation that squares cannot be taken by both players,
    it is an invariant that must be always zero (the empty set).
    Works on scalar and array inputs of any shape (output keeps the input shape).
    """
    return p['mover'] & p['opponent']

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def position_check_collisions(p: PositionField | PositionArray) -> None:
    """
    Checks for overlapping squares between mover and opponent.
    Given the observation that squares cannot be taken by both players,
    it is an invariant that must be always zero (the empty set).
    When a collision is found raises a ValueError.
    Works on scalar and array inputs of any shape.
    """
    collisions = position_collisions(p)
    if np.any(collisions):
        # Convert to 1D safely to support both scalar and array inputs without IndexError
        collisions_1d = np.atleast_1d(collisions)

        total_size = collisions_1d.size
        nonzero_indices = np.nonzero(collisions_1d)[0]
        num_collisions = nonzero_indices.size  # Faster than len() on numpy arrays
        first_collision_idx = nonzero_indices[0]

        error_message = (
            f"Validation Failed: Detected {num_collisions} collision(s) "
            f"out of {total_size} total elements. "
            f"First collision occurred at index: {first_collision_idx}."
        )
        raise ValueError(error_message)

#: legal_moves code starts here.

#: Constants for bitboard manipulation
_all_squares                 = Bitboard(0xFFFFFFFFFFFFFFFF)
_all_squares_except_column_a = Bitboard(0xFEFEFEFEFEFEFEFE)
_all_squares_except_column_h = Bitboard(0x7F7F7F7F7F7F7F7F)

#: Pre-calculating masks and slides to avoid overhead inside the JIT function
_mask_l = np.array([
    _all_squares_except_column_a,
    _all_squares_except_column_h,
    _all_squares,
    _all_squares_except_column_a
], dtype=Bitboard)
_mask_r = np.array([
    _all_squares_except_column_h,
    _all_squares_except_column_a,
    _all_squares,
    _all_squares_except_column_h
], dtype=Bitboard)
_slide_1 = np.array([1, 7, 8, 9], dtype=np.uint8)
_slide_2 = _slide_1 * 2
_slide_4 = _slide_1 * 4

#: Internal use function.
@nb.njit(inline='always')
def _kogge_stone_lms(generator: Bitboard, propagator: Bitboard,
                     blocker: Bitboard) -> Bitboard:
    """
    The Kogge-Stone legal-move-set primitive (the historical name,
    resurrected): the sliding moves of the generator through the
    propagator, stopped by the blocker (the empties). The private
    core, shared by the vectorized kernel and `legal_moves_of` — the
    same encapsulation pattern as `_kogge_stone_mm` /
    `flips_of_move`.
    """
    legal_result = Bitboard(0)

    # Iterate through the 4 main directions (each handles both sides: Left/Right, Up/Down, etc.)
    for d in range(4):
        # --- Directional Forward Shift (Left-style) ---
        g = generator
        p = propagator & _mask_l[d]

        g |= p & (g << _slide_1[d])
        p &= p << _slide_1[d]
        g |= p & (g << _slide_2[d])
        p &= p << _slide_2[d]
        g |= p & (g << _slide_4[d])

        # Resulting moves must be in an empty square and not be the generator itself
        g_final = blocker & _mask_l[d] & ((g & ~generator) << _slide_1[d])
        legal_result |= g_final

        # --- Directional Backward Shift (Right-style) ---
        g = generator
        p = propagator & _mask_r[d]

        g |= p & (g >> _slide_1[d])
        p &= p >> _slide_1[d]
        g |= p & (g >> _slide_2[d])
        p &= p >> _slide_2[d]
        g |= p & (g >> _slide_4[d])

        g_final = blocker & _mask_r[d] & ((g & ~generator) >> _slide_1[d])
        legal_result |= g_final

    return legal_result

#: The PUBLIC numba primitives: the per-lane legal-move set and the
#: flip set of a single-bit move — the single sources of the two
#: geometries, shared by the vectorized kernels of this module and by
#: the numba compositions of the other modules (random_game's fused
#: play-path engine). njit + inline='always': the compiler embeds the
#: machine code at the call sites; the source exists once.
@nb.njit(inline='always', cache=True)
def legal_moves_of(mover: Bitboard, opponent: Bitboard) -> Bitboard:
    """
    The legal-move set of ONE position (the per-lane numba
    primitive): the Kogge-Stone computation over the 4 directions x
    2 senses, delegated to the private core `_kogge_stone_lms` (the
    same encapsulation pattern as `flips_of_move` /
    `_kogge_stone_mm`). The single source shared by legal_moves /
    _vectorized_legal_moves (which call it per lane) and by the
    numba compositions.
    """
    return _kogge_stone_lms(mover, opponent, Bitboard(~(mover | opponent)))

#: Internal use function.
@nb.njit(parallel=True, cache=True)
def _vectorized_legal_moves(movers: np.ndarray, opponents: np.ndarray) -> np.ndarray:
    """
    Vectorized calculation of Reversi legal moves using Kogge-Stone algorithm.
    Optimized for large arrays (10M+ elements) using Numba JIT and multi-threading.
    """
    n = movers.shape[0]
    results = np.empty(n, dtype=Bitboard)

    # Parallel loop across all board instances
    for i in nb.prange(n):
        results[i] = legal_moves_of(Bitboard(movers[i]), Bitboard(opponents[i]))

    return results

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def legal_moves(mover: Bitboard | BitboardArray,
                opponent: Bitboard | BitboardArray) -> Bitboard | BitboardArray:
    """
    Calculate Reversi legal moves for a single or multiple board configurations.

    When input is a scalar Bitboard the output is a Bitboard.
    When input is a 1-D array of Bitboards (both arguments, same
    shape), the output is an array with shape (N,). Bare Python ints
    and lists are rejected (Pydantic) as for the rest of the dual API.
    """
    # Check if inputs are scalars
    if isinstance(mover, Bitboard) and isinstance(opponent, Bitboard):
        # Wrap the scalar inputs into numpy arrays
        movers = np.array([mover], dtype=Bitboard)
        opponents = np.array([opponent], dtype=Bitboard)

        # Call the vectorized function
        result = _vectorized_legal_moves(movers, opponents)

        # Return the result as a scalar
        return result[0]
    elif isinstance(mover, np.ndarray) and isinstance(opponent, np.ndarray):
        # D-111 M5: the standard 1-D guard (house pattern) — a 2-D
        # array used to crash deep in the numba kernel with a
        # TypingError instead of a clean ValueError.
        if mover.ndim != 1:
            raise ValueError(f"When the argument mover is an array, it must be 1D, got shape {mover.shape}")
        if opponent.ndim != 1:
            raise ValueError(f"When the argument opponent is an array, it must be 1D, got shape {opponent.shape}")

        # Ensure the arrays have the same shape
        if mover.shape != opponent.shape:
            raise ValueError("The shapes of mover and opponent arrays must be the same.")

        # Call the vectorized function directly
        return _vectorized_legal_moves(mover, opponent)
    else:
        raise TypeError("Inputs must be either both Bitboard or both npt.NDArray[Bitboard].")

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def position_legal_moves(p: PositionField | PositionArray) -> Bitboard | BitboardArray:
    return legal_moves(p['mover'], p['opponent'])

#: legal_move code ends here.

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def position_legal_moves_count(p: PositionField) -> int:
    """
    Returns the count of legal moves for the game position.
    """
    lms = position_legal_moves(p)
    lmc = bitboard_count(lms)
    return lmc

#: make_move code starts here.
#:
#: flips and make_move are dual scalar/array (D-140), the same
#: technique as legal_moves (D-111): a numba prange kernel over the
#: N-board batch (_vectorized_flips / _vectorized_make_move), the
#: per-element _kogge_stone_mm under njit(inline), the standard 1-D /
#: shape guards, the output re-assembled with make_position (the fresh
#: interleaved buffer, zero-copy view). The scalar path keeps its
#: pre-vectorization behaviour bit-for-bit; the former banner note
#: ("PASS as a special case") is resolved per-element inside the
#: make_move kernel (move == MOVE_PA -> the player swap, no filter needed).

_mm_mask = np.array([
    _all_squares_except_column_a,
    _all_squares_except_column_h,
    _all_squares,
    _all_squares_except_column_a,
    _all_squares_except_column_h,
    _all_squares_except_column_a,
    _all_squares,
    _all_squares_except_column_h,
], dtype=Bitboard)

_mm_slide_up_1 = np.array([1,  7,  8,  9,  0,  0,  0,  0], dtype=np.uint8)
_mm_slide_dw_1 = np.array([0,  0,  0,  0,  1,  7,  8,  9], dtype=np.uint8)
_mm_slide_up_2 = np.array([2, 14, 16, 18,  0,  0,  0,  0], dtype=np.uint8)
_mm_slide_dw_2 = np.array([0,  0,  0,  0,  2, 14, 16, 18], dtype=np.uint8)
_mm_slide_up_4 = np.array([4, 28, 32, 36,  0,  0,  0,  0], dtype=np.uint8)
_mm_slide_dw_4 = np.array([0,  0,  0,  0,  4, 28, 32, 36], dtype=np.uint8)

@nb.njit(inline='always')
def _kogge_stone_mm(generator: Bitboard,
                    propagator: Bitboard,
                    blocker: Bitboard) -> Bitboard:
    g: Bitboard
    p: Bitboard
    gt: Bitboard
    accumulator: Bitboard

    accumulator = Bitboard(0)

    for i in range(8):
        g = generator
        p = propagator & _mm_mask[i]

        g |= p & ((g << _mm_slide_up_1[i]) >> _mm_slide_dw_1[i])
        p &=     ((p << _mm_slide_up_1[i]) >> _mm_slide_dw_1[i])

        g |= p & ((g << _mm_slide_up_2[i]) >> _mm_slide_dw_2[i])
        p &=     ((p << _mm_slide_up_2[i]) >> _mm_slide_dw_2[i])

        # Flipped disks plus move, but only if this direction really flips.
        g |= p & ((g << _mm_slide_up_4[i]) >> _mm_slide_dw_4[i])

        # Flip blocker. It is the bracketing square belonging to mover.
        gt = blocker & _mm_mask[i] & ((g << _mm_slide_up_1[i]) >> _mm_slide_dw_1[i])

        # Accumulates flipped disks only if there is a blocker (true flipping direction).
        # In C: (g & -(gt > 0))
        if gt > 0:
            accumulator |= g

    return Bitboard(accumulator & ~generator)

@nb.njit(inline='always', cache=True)
def flips_of_move(mover: Bitboard, opponent: Bitboard, move: Bitboard) -> Bitboard:
    """
    The flip set when the single-bit `move` is played by `mover`
    against `opponent`: the Kogge-Stone flip primitive (the single
    source of the flip geometry for the numba compositions —
    random_game's fused play-path engine calls it per lane).
    """
    return _kogge_stone_mm(move, opponent, mover)

#: Internal use function.
@nb.njit(parallel=True, cache=True)
def _vectorized_flips(movers: np.ndarray, opponents: np.ndarray, moves: np.ndarray) -> tuple:
    """
    Vectorized flip-set calculation over an N-board batch (D-140).
    A zero (PASS) move swaps the players and gets a 0 flip set; for a
    non-single-bit move the element keeps the input position and gets a
    0 flip set; for a legal move the flipped opponent discs change side
    and the mover places the disc.
    """
    n = movers.shape[0]
    flips = np.empty(n, dtype=Bitboard)
    out_movers = np.empty(n, dtype=Bitboard)
    out_opponents = np.empty(n, dtype=Bitboard)

    # Parallel loop across all board instances
    for i in nb.prange(n):
        mover = Bitboard(movers[i])
        opponent = Bitboard(opponents[i])
        move = Bitboard(moves[i])
        if move == 0:
            # PASS: the players swap, no flip.
            flips[i] = Bitboard(0)
            out_movers[i] = opponent
            out_opponents[i] = mover
        elif (move & (move - 1)) != 0:
            # A non-single-bit move: no flip, position unchanged.
            flips[i] = Bitboard(0)
            out_movers[i] = mover
            out_opponents[i] = opponent
        else:
            f = _kogge_stone_mm(move, opponent, mover)
            flips[i] = f
            if f != 0:
                out_movers[i] = opponent & ~f
                out_opponents[i] = mover | f | move
            else:
                out_movers[i] = mover
                out_opponents[i] = opponent

    return flips, out_movers, out_opponents

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def position_flips(p: PositionField | PositionArray,
                   move: Bitboard | BitboardArray) -> Tuple[Bitboard | BitboardArray,
                                                            PositionField | PositionArray | None]:
    """
    Computes the flip set.
    Return flips as well as the updated game position.
    The moving player places a disc in the square identified by the move
    parameter. The flipped squares are returned.
    When the move is 0ULL (PASS) the players are swapped and the updated
    board is the swapped position (no flip).
    When the move is not legal (a single bit without a flipping ray, or a
    non-single-bit bitboard) the empty flip set is returned and the
    updated board is None (the scalar case).
    The updated board is returned as the second element of the tuple when
    the move is legal or a PASS, None otherwise.

    Dual scalar/array (D-140, as legal_moves): when input is a scalar
    the output is scalar; when p is a 1-D PositionArray and move a 1-D
    Bitboard array of the same shape, the output is a Bitboard array
    and a PositionArray. In the array case a zero (PASS) element swaps
    the players, a legal element flips, and an illegal (or non-single-
    bit) element i gets flips[i] = 0 and updated[i] left as the input
    position (no per-element None). Bare Python ints and lists are
    rejected (Pydantic) as for the rest of the dual API.
    """
    if isinstance(p, np.ndarray) and isinstance(move, np.ndarray):
        # D-140: the standard 1-D guard (house pattern, as legal_moves)
        if p.ndim != 1:
            raise ValueError(f"When the argument p is an array, it must be 1D, got shape {p.shape}")
        if move.ndim != 1:
            raise ValueError(f"When the argument move is an array, it must be 1D, got shape {move.shape}")
        if p.shape != move.shape:
            raise ValueError("The shapes of p and move arrays must be the same.")
        flips, out_movers, out_opponents = _vectorized_flips(p['mover'], p['opponent'], move)
        return flips, make_position(out_movers, out_opponents)
    if isinstance(p, np.void) and isinstance(move, Bitboard):
        m = p['mover']
        o = p['opponent']
        if move == 0x0000000000000000:
            # PASS: the players swap, no flip.
            return Bitboard(0x0000000000000000), make_position(o, m)
        if bitboard_count(move) != 1:
            # A non-single-bit move is not a move: no flip, no position.
            return Bitboard(0x0000000000000000), None
        # The njit primitive returns a Python int at the Python boundary
        # (numba scalar-return idiom) — re-wrap to Bitboard.
        flips = Bitboard(_kogge_stone_mm(move, o, m))
        if flips != 0x0000000000000000:
            updated = make_position(o & ~flips, m | flips | move)
        else:
            updated = None
        return flips, updated
    raise TypeError("Inputs must be either both scalar or both 1-D arrays.")

#: Internal use function.
@nb.njit(parallel=True, cache=True)
def _vectorized_make_move(movers: np.ndarray, opponents: np.ndarray, moves: np.ndarray) -> tuple:
    """
    Vectorized game-move execution over an N-board batch (D-140).
    moves is a 1-D uint8 array with values in [0..64]: 64 (PA) swaps
    the player and opponent bitboards of the element (it is not
    verified that pass is the only legal move); a legal square flips
    as in _vectorized_flips; an illegal square leaves the input
    position unchanged. The flips output mirrors the flip set (0 for
    PA and for illegal squares).
    A move on a square OCCUPIED by the mover or the opponent stones
    is UNEXPECTED BEHAVIOR (the caller's responsibility to avoid —
    pass only legal moves or PA): the flip ray is computed anyway
    and, when non-zero, is APPLIED — on an own-stone square the
    result is a well-formed but UNREACHABLE position (the placed
    stone adds nothing: the total count is short by one), on an
    opponent-stone square the result is CORRUPT (the square ends up
    in BOTH bitboards). "Illegal -> unchanged" holds only for EMPTY
    squares without a flipping ray. (D-171: documented as
    caller's responsibility; the kernel is not modified.)
    """
    n = movers.shape[0]
    flips = np.empty(n, dtype=Bitboard)
    out_movers = np.empty(n, dtype=Bitboard)
    out_opponents = np.empty(n, dtype=Bitboard)

    # Parallel loop across all board instances
    for i in nb.prange(n):
        mover = Bitboard(movers[i])
        opponent = Bitboard(opponents[i])
        move = moves[i]
        if move == MOVE_PA:
            # PASS: swap the players.
            flips[i] = Bitboard(0)
            out_movers[i] = opponent
            out_opponents[i] = mover
        else:
            move_bb = Bitboard(1) << move
            f = _kogge_stone_mm(move_bb, opponent, mover)
            flips[i] = f
            if f != 0:
                out_movers[i] = opponent & ~f
                out_opponents[i] = mover | f | move_bb
            else:
                out_movers[i] = mover
                out_opponents[i] = opponent

    return flips, out_movers, out_opponents

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def position_make_move(p: PositionField | PositionArray,
                       move: Move | MoveArray) -> PositionField | PositionArray | None:
    """
    Executes a game move.
    The move must be in the range A1, ... H8, PA. [0..64].
    When 64 (PA) is passed the player and opponent bitboards are swapped
    (it is not verified that pass is the only legal move) — PA never
    returns None.
    When an illegal move (an EMPTY square without a flipping ray) is
    passed and the input is a scalar, None is returned — the only case
    that yields None (the array case keeps the input position).
    A move on a square OCCUPIED by the mover or the opponent
    stones is UNEXPECTED BEHAVIOR (the caller's responsibility to
    avoid — pass only legal moves or PA): the flip ray is
    computed anyway and, when non-zero, is APPLIED — on an
    own-stone square the result is a well-formed but UNREACHABLE
    position (the total stone count is short by one), on an
    opponent-stone square the result is CORRUPT (the square ends
    up in BOTH bitboards). (D-171: documented as caller's
    responsibility; the kernel is not modified.)

    Dual scalar/array (D-140, as legal_moves): when input is a scalar
    the output is scalar (the pre-vectorization behaviour, including the
    PASS swap
    and the out-of-range ValueError); when p is a 1-D PositionArray
    and move a 1-D uint8 MoveArray of the same shape, the output is a
    PositionArray. In the array case PA elements swap the players, a
    legal square updates the position, and an illegal square leaves
    the input position unchanged (no per-element None). Any value
    above 64 in the array raises ValueError before the kernel.
    """
    if isinstance(p, np.ndarray) and isinstance(move, np.ndarray):
        # D-140: the standard 1-D guard (house pattern, as legal_moves)
        if p.ndim != 1:
            raise ValueError(f"When the argument p is an array, it must be 1D, got shape {p.shape}")
        if move.ndim != 1:
            raise ValueError(f"When the argument move is an array, it must be 1D, got shape {move.shape}")
        if p.shape != move.shape:
            raise ValueError("The shapes of p and move arrays must be the same.")
        if (move > MOVE_PA).any():
            raise ValueError(f"All moves in the array must be in the range [0..{int(MOVE_PA)}].")
        _, out_movers, out_opponents = _vectorized_make_move(p['mover'], p['opponent'], move)
        return make_position(out_movers, out_opponents)
    if isinstance(p, np.void) and isinstance(move, np.uint8):
        # Scalar path: the pre-vectorization behaviour, unchanged.
        if move == MOVE_PA: # PASS
            return make_position(p['opponent'], p['mover'])
        if move > MOVE_PA:
            raise ValueError(f"Argument move {int(move)} is out of range [0..{int(MOVE_PA)}]")
        m = move_as_bitboard(move)
        _, updated = position_flips(p, m)
        return updated
    raise TypeError("Inputs must be either both scalar or both 1-D arrays.")

#: make_move code ends here.

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def position_count_difference(p: PositionField) -> int:
    """
    Returns the disk difference between the player and her opponent.
    """
    mc = bitboard_count(p['mover'])
    oc = bitboard_count(p['opponent'])
    return int(mc) - int(oc)

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def position_final_value(p: PositionField) -> int:
    """
    Used for the score at the end of the game.
    Returns the disk difference between the player and her opponent,
    assigning the empty squares to the player having most discs.

    From the web site of the World Othello Federation,
    World Othello Championship Rules, scoring:
    "At the end of the game, if both players have completed their moves in
    the allowed time, the winner is the player with the greater number of
    discs of his colour on the board at the end. The official score of the
    game will be determined by counting up the discs of each colour on the
    board, counting empty squares for the winner. In the event of a draw,
    the score will always be 32-32".
    """
    mc = bitboard_count(p['mover'])
    oc = bitboard_count(p['opponent'])
    diff = int(mc) - int(oc)
    if diff == 0: return 0
    ec = __square_max_value__ - int(mc + oc)
    if diff > 0:
        delta = diff + ec
    else:
        delta = diff - ec
    return delta

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def position_has_to_pass(p: PositionField) -> bool:
    """
    Returns true if the mover player doesn't have any legal move.
    """
    lmc = position_legal_moves_count(p)
    if lmc == 0:
        return True
    else:
        return False

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def position_is_game_over(p: PositionField) -> bool:
    """
    Returns true if the game is over.
    """
    lmc = position_legal_moves_count(p)
    if lmc > 0: return False
    next_board = position_make_move(p, move_from_str('PA'))
    next_lmc = position_legal_moves_count(next_board)
    if next_lmc > 0: return False
    return True

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def position_is_move_legal(p: PositionField, move: Move) -> bool:
    """
    Returns true if the move is legal.
    """
    if move > MOVE_PA: return False
    lms = position_legal_moves(p)
    if move == MOVE_PA: # Pass move
        if lms == 0x0000000000000000:
            return True
        else:
            return False
    mbb = move_as_bitboard(move)
    if (mbb & lms) == mbb:
        return True
    return False


#: The Zobrist bitstrings of the legacy C engine (D-213): the 128
#: URANDOM-generated constants of board.c `zobrist_bitstrings[]` —
#: entries 0..63 are the legacy blacks slots, 64..127 the legacy whites
#: ones. The table is canon: the SHA-3-256 test pin + the position
#: goldens protect it, and it makes the hash values legacy-comparable
#: (the position_hash docstring).
_zobrist_bitstrings = np.array([
           0x4EC764D9D2FC995C, 0x4689879C5E2B6C8D, 0x7B8509672627BDE6, 0x5EC9EED7E83A1070,
           0x8C61E367C148A670, 0x12BF65D47CB500F3, 0x2D128CD312314B15, 0xEC8FFA579C3FF006,
           0x1B772E0C17A8637D, 0xFEA5D5093AE4F127, 0x3F6223B7D74731E8, 0x9BF6F10BF080F403,
           0xCE03618789AACB66, 0x29264F46A5C844E3, 0xD4BD485D4B88FC6E, 0xAAC3C81799DAE8F5,
           0x46B256D2079DA270, 0x5765CB86D7BE25B4, 0x7754057541AAAF9E, 0xB9E9E765C5214D6D,
           0x957833AE886E5003, 0x59BEDBE41933BEB6, 0xD5D328EC1AE90B22, 0x26FA194CD5A4CC9A,
           0x34790BFC50B7571E, 0xE91BC0D61C9FA3C5, 0x8FB89136550EFB06, 0x36701B34D43E30CD,
           0xAAFD6ACF34BB27C1, 0x401DD1B2B7A72AB4, 0x6F5903B64BBD50D7, 0x9067F2A3CB7EBB34,
           0x2C7807F6E28CD962, 0x42B2DB1AED17AFD5, 0xF42857186A09F927, 0x258AB4C5E9986E0C,
           0x8F8BA0BC0571B0F6, 0xCB7AC29208905214, 0x89914660AA38896A, 0x380CAC8536886A07,
           0x7B7F399C6EC9563D, 0xB9CBFBEEE95F05B1, 0x46AAAFC2159C8F19, 0xDCE680A0882BCCEF,
           0x347DDA36E42E2D99, 0x48EAF8CB224BCBB6, 0x1EACE389084B2674, 0x261BC842C735974D,
           0xF334875975FD986B, 0xF6B436CC3615018C, 0x6658B92BCD930893, 0x4B6BF5B88078852E,
           0x30461B28416207E1, 0xA2EE71D448670786, 0x0C8CD31138E8A683, 0x5FF41A78E0014DD0,
           0xA57DE5B0A848A8E0, 0x71D68A3A9600F975, 0xEBB35D1E75B69FFB, 0xFCC1D327A771464B,
           0xB6C1F45DB043CF56, 0x92EF77063313F3CE, 0x5F48E97C72B167E2, 0x5806342E75C7BB6B,
           0x056C0070CF70F8DD, 0x81AD4662EE05E75A, 0x1C10E0B05C7B3C49, 0xC684C383E396972A,
           0x35747D859FC1A7E1, 0xFDDCF0169427CEE5, 0x3952CBE313B377E2, 0xDA1B5C1E5BCCB131,
           0x10B747061AF1559C, 0x8388EDE0F8EDCBFC, 0x4873A84B8ABF0FA8, 0xB30E990FE793A807,
           0x6B8C5C09C78D0A9F, 0x7A488BC144D344AA, 0xC04C26EC10A73AE9, 0x9278CDFF5EBA539E,
           0xFF3A1C4370FB8703, 0x70D16AE16E34B5B5, 0x2732FCB913E2E5C3, 0xC59EE008F48EB1FA,
           0x38C7DB9E584C3680, 0x16F9194953701E88, 0x2E4C5FAC8051C8FD, 0x27DD41B7B5D864FA,
           0xECA6A65750A55AEA, 0x5EBECF093FF380E7, 0xAA4B94B2F0585B82, 0xC88047DA71E83C4D,
           0xB55C0550FE29B255, 0x2A1F8CB7ECEB6200, 0x7B841E8CB0945F2D, 0x6E5D5D9ED39B4961,
           0x67222624CF379C81, 0x0CC24C31A8BA7F90, 0x4B54A89AF4A4DF4C, 0x91A6E548CAC3E417,
           0x83DEB6121EA84F96, 0x9F951DD98DBB9DF5, 0x25584291FF15CB27, 0x3371E38504F0CB1F,
           0x0EB9B65B5DE9637D, 0x2D292615860C0AE9, 0x8DAFEA0E2F5DD418, 0x5E30A0DFD3A6BA54,
           0x5C442D0B47BF7364, 0x7C2EEBB8C8734B16, 0x440AF7B361B686A6, 0xBC6C2CB56CE41EDD,
           0x2DF7B73E01F1DB6C, 0xD76592C6235F3FFE, 0x2139DC845CE8D2B0, 0x42168DFAFC8BF871,
           0xB0E6598E3C707763, 0xD7C55A777BF74808, 0x04C0175493D0C6EC, 0x78B2B49BF53DD1A5,
           0xC6020A48A9F0B2CD, 0x08CA89D2EA10FEB4, 0x07DE9D1304C3B2BD, 0x769EF9C4E120BC5F,
           0xEEBD5772D344846F, 0x1E972C3F168BBF7F, 0x0C72560FAD1EC422, 0xD85B15F5DBCD19B9
], dtype=np.uint64)

#: The SWAR byte-fold tables of position_hash (D-213): entry [c, k, v]
#: is the XOR of the color-c bitstrings of the squares 8k .. 8k+7
#: selected by the bits of the byte v (the fast path of the legacy
#: per-bit loop: 16 table lookups per position, no per-bit iteration).
#: Generated at import time (deterministic, no RNG); 32 KB —
#: L1-resident.
_zobrist_byte_fold = np.zeros((2, 8, 256), dtype=np.uint64)
for _c in range(2):
    for _k in range(8):
        for _b in range(8):
            _z = _zobrist_bitstrings[64 * _c + 8 * _k + _b]
            for _v in range(256):
                if (_v >> _b) & 1:
                    _zobrist_byte_fold[_c, _k, _v] ^= _z

#: Internal use function.
@nb.njit(cache=True)
def _zobrist_position_fold(m, o):
    """
    The position_hash fold of one (mover, opponent) pair: 16 byte-table
    lookups, no per-bit loop (the SWAR fast path of the legacy C
    game_position_x_hash_plain). m and o are uint64 scalars; the
    return is the uint64 fold.
    """
    h = _zobrist_byte_fold[0, 0, int(m & np.uint64(0xFF))]
    h ^= _zobrist_byte_fold[0, 1, int((m >> np.uint64(8)) & np.uint64(0xFF))]
    h ^= _zobrist_byte_fold[0, 2, int((m >> np.uint64(16)) & np.uint64(0xFF))]
    h ^= _zobrist_byte_fold[0, 3, int((m >> np.uint64(24)) & np.uint64(0xFF))]
    h ^= _zobrist_byte_fold[0, 4, int((m >> np.uint64(32)) & np.uint64(0xFF))]
    h ^= _zobrist_byte_fold[0, 5, int((m >> np.uint64(40)) & np.uint64(0xFF))]
    h ^= _zobrist_byte_fold[0, 6, int((m >> np.uint64(48)) & np.uint64(0xFF))]
    h ^= _zobrist_byte_fold[0, 7, int((m >> np.uint64(56)) & np.uint64(0xFF))]
    h ^= _zobrist_byte_fold[1, 0, int(o & np.uint64(0xFF))]
    h ^= _zobrist_byte_fold[1, 1, int((o >> np.uint64(8)) & np.uint64(0xFF))]
    h ^= _zobrist_byte_fold[1, 2, int((o >> np.uint64(16)) & np.uint64(0xFF))]
    h ^= _zobrist_byte_fold[1, 3, int((o >> np.uint64(24)) & np.uint64(0xFF))]
    h ^= _zobrist_byte_fold[1, 4, int((o >> np.uint64(32)) & np.uint64(0xFF))]
    h ^= _zobrist_byte_fold[1, 5, int((o >> np.uint64(40)) & np.uint64(0xFF))]
    h ^= _zobrist_byte_fold[1, 6, int((o >> np.uint64(48)) & np.uint64(0xFF))]
    h ^= _zobrist_byte_fold[1, 7, int((o >> np.uint64(56)) & np.uint64(0xFF))]
    return h

#: Internal use function.
@nb.njit(parallel=True, cache=True)
def _vectorized_position_hash(movers: np.ndarray, opponents: np.ndarray) -> np.ndarray:
    """
    Vectorized position_hash over an N-position batch (D-213).
    movers and opponents are the 1-D uint64 fields of a Position array;
    the output is the 1-D uint64 array of the per-element Zobrist
    folds.
    """
    n = movers.shape[0]
    out = np.empty(n, dtype=np.uint64)
    for i in nb.prange(n):
        out[i] = _zobrist_position_fold(movers[i], opponents[i])
    return out

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def position_hash(p: PositionField | PositionArray) -> Bitboard | BitboardArray:
    """
    Returns the 64-bit Zobrist hash of the game position.

    The hash is the XOR-fold of the legacy C engine zobrist bitstrings
    (D-213): the mover discs select the first 64 entries (the legacy
    blacks slots), the opponent discs the last 64 ones (the legacy
    whites slots), and no complement is applied. It is exactly the
    legacy game_position_x_hash value of the position with blacks =
    mover, whites = opponent, player = BLACK_PLAYER; the C complement
    rule (`if (p) hash = ~hash`, p = WHITE_PLAYER) maps a legacy
    player = WHITE position to the one's complement:
    legacy_hash(blacks, whites, WHITE) = ~position_hash(blacks, whites).

    Works on scalar and array inputs of any shape (the output keeps
    the input kind: a scalar uint64 or an array of uint64). A pure
    function of the (mover, opponent) pair: no state, bit-stable
    across runs, and XOR-incremental (a disc flip at square i
    contributes zobrist[i] ^ zobrist[i + 64], the legacy
    zobrist_flip_bitstrings entry).
    """
    if isinstance(p, np.ndarray):
        # D-213: the standard 1-D guard (house pattern, as position_flips)
        if p.ndim != 1:
            raise ValueError(f"When the argument p is an array, it must be 1D, got shape {p.shape}")
        return _vectorized_position_hash(p['mover'], p['opponent'])
    if isinstance(p, np.void):
        # The njit primitive returns a Python int at the Python boundary
        # (numba scalar-return idiom) — re-wrap to Bitboard.
        return Bitboard(_zobrist_position_fold(p['mover'], p['opponent']))
    raise TypeError("Input must be a Position scalar or a Position array.")

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def position_fa1h8(p: PositionField) -> PositionField:
    """
    Reflects the game position on the diagonal a1-h8.
    """
    return make_position(bitboard_fa1h8(p['mover']), bitboard_fa1h8(p['opponent']))

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def position_fh1a8(p: PositionField) -> PositionField:
    """
    Reflects the game position on the diagonal h1-a8.
    """
    return make_position(bitboard_fh1a8(p['mover']), bitboard_fh1a8(p['opponent']))

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def position_fhori(p: PositionField) -> PositionField:
    """
    Reflects the game position horizontally (on the horizontal axis).
    """
    return make_position(bitboard_fhori(p['mover']), bitboard_fhori(p['opponent']))

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def position_fvert(p: PositionField) -> PositionField:
    """
    Reflects the game position vertically (on the vertical axis).
    """
    return make_position(bitboard_fvert(p['mover']), bitboard_fvert(p['opponent']))

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def position_ro000(p: PositionField) -> PositionField:
    """
    Returns the game position unchanged, as it is.
    """
    return p.copy()

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def position_ro090(p: PositionField) -> PositionField:
    """
    Rotates the game position by 90 degrees clockwise.
    """
    return make_position(bitboard_ro090(p['mover']), bitboard_ro090(p['opponent']))

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def position_ro180(p: PositionField) -> PositionField:
    """
    Rotates the game position by 180 degrees.
    """
    return make_position(bitboard_ro180(p['mover']), bitboard_ro180(p['opponent']))

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def position_ro270(p: PositionField) -> PositionField:
    """
    Rotates the game position by 270 degrees clockwise.
    """
    return make_position(bitboard_ro270(p['mover']), bitboard_ro270(p['opponent']))

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def position_transformations(p: PositionField | PositionArray) -> PositionArray:
    """
    Applies the eight D8 transformations on the input game positions.

     - 0 -> 0 : ro000
     - 0 -> 1 : ro090
     - 0 -> 2 : ro180
     - 0 -> 3 : ro270
     - 0 -> 4 : fvert
     - 0 -> 5 : fh1a8
     - 0 -> 6 : fhori
     - 0 -> 7 : fa1h8

    When input is a scalar Position output is an array of Positions having shape (8,).
    When input is an array of Positions of length N, the output has shape (N, 8).
    """
    mtrs = bitboard_transformations(p['mover'])
    otrs = bitboard_transformations(p['opponent'])
    return make_position(mtrs, otrs)

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def position_anti_transformations(p: PositionField | PositionArray) -> PositionArray:
    """
    Applies the eight D8 anti-transformations on the input game positions.

     - 0 -> 0 : ro000
     - 0 -> 1 : ro270
     - 0 -> 2 : ro180
     - 0 -> 3 : ro090
     - 0 -> 4 : fvert
     - 0 -> 5 : fh1a8
     - 0 -> 6 : fhori
     - 0 -> 7 : fa1h8

    When input is a scalar Position output is an array of Positions having shape (8,).
    When input is an array of Positions of length N, the output has shape (N, 8).
    """
    mtrs = bitboard_anti_transformations(p['mover'])
    otrs = bitboard_anti_transformations(p['opponent'])
    return make_position(mtrs, otrs)
