#
# prng.py
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

"""
The MT-19937 64-bit pseudo-random number generator.

MT-19937 (the 64-bit Mersenne Twister) is a DETERMINISTIC generator:
seeded once with an integer, it yields a reproducible stream of
64-bit values. The state is a 312-word (64-bit) array; a draw first
TWISTS the array (a linear recurrence mixing the 312 words) and then
TEMPERS the output word with a 4-operation bitwise mix. The period
is 2^19937 - 1, so a single seed defines the whole stream.

Typing: every 64-bit value in the data path is a numpy uint64 — the
type itself applies the unsigned-wraparound contract (arithmetic
overflows modulo 2^64; no unbounded Python ints, no manual masking).
Loop counters are plain ints (control flow, not data).

API (the MT19937 class, the sole STREAM interface):
  MT19937(seed)                      construct + seed the state.
  get_uint64()                       the next 64-bit value.
  get_uint64_batch(n)                the next n values, a (n,) u64 array.
  get_double_in_c0_c1 / _c0_o1 / _o0_o1
                                     random floats in [0,1], [0,1), (0,1).
  random_choice_from_finite_set(k)   a uniform integer in [0, k-1].
  shuffle_uint8 / shuffle /
  shuffle_double / shuffle_int       in-place Fisher-Yates shuffles.
  random_string_az(n)                n random lowercase letters.
  extract_from_set64(set_arr)        pick + remove a random bit (in place).
  choose_one_from_set64(set64)       pick a random bit, WITHOUT removing.

The pick-from-set technique lives ONCE in this module, shared
by the class methods and the numba contexts: pick_one_from_set64 (the
scalar kernel — the methods draw one value and delegate to it) and
pick_one_from_set64_batch (the vectorized form over an (N,) array of
sets, fed by one get_uint64_batch pre-draw).

The state (_mt / _mti) is INTERNAL: it is never exposed, and a
generator is neither saved nor re-seeded.
"""

from __future__ import annotations

import math

import numpy as np
import numba as nb

__all__ = ['MT19937', 'pick_one_from_set64', 'pick_one_from_set64_batch']

# The working-area size: 312 words (64-bit each) — the MT-19937
# state. NN is the only constant at module level (the ctor's
# np.zeros(NN, …) + the init loop use it); the twist + temper
# constants (MM / UM / LM / MAG) live inside the _get_uint64_batch
# kernel (they are its implementation details).
NN: int = 312


class MT19937:
    """
    The 64-bit MT-19937 generator: a seeded, deterministic stream of
    64-bit values.

    Construction takes the seed (REQUIRED) and initializes the state;
    the object is always initialized and cannot be re-seeded. The
    state (_mt / _mti) is INTERNAL — it is never exposed (a
    generator is not saved or re-seeded).

    Attributes (internal):
      _mt:  np.ndarray, shape (NN,), dtype uint64 — the working area.
      _mti: int — the position within the working area.
    """

    def __init__(self, seed: int) -> None:
        # Seed the 312-word working area (the MT-19937 init). The
        # working index is left at NN, so the FIRST get_uint64
        # twists the just-initialized array before its first draw.
        # The arithmetic wraps modulo 2^64 by design (unsigned); the
        # numpy overflow warnings are silenced locally.
        self._mt = np.zeros(NN, dtype=np.uint64)
        self._mt[0] = np.uint64(seed)
        with np.errstate(over="ignore", invalid="ignore"):
            for mti in range(1, NN):
                prev = self._mt[mti - 1]
                # 6364136223846793005 — the 64-bit MT init multiplier.
                self._mt[mti] = (
                    np.uint64(6364136223846793005) * (prev ^ (prev >> 62))
                    + np.uint64(mti))
        self._mti = NN

    # -- the generators -------------------------------------------------

    def get_uint64(self) -> np.uint64:
        """
        The next 64-bit value of the sequence. Delegates to
        get_uint64_batch (n = 1): the twist + the 4-op temper live
        in the numba kernel _get_uint64_batch (the single source),
        so the scalar and batch paths share one implementation.
        """
        return self.get_uint64_batch(1)[0]

    def get_uint64_batch(self, n: int) -> np.ndarray:
        """
        The n successive values of the sequence as a (n,) uint64
        array. Runs the numba kernel _get_uint64_batch on this
        state (the _mt working area + the _mti index, mutated in
        place); it is bit-identical to get_uint64 called n times.
        """
        draws, self._mti = _get_uint64_batch(self._mt, self._mti, n)
        return draws

    def get_double_in_c0_c1(self) -> np.float64:
        """
        A random float in the [0, 1] interval (both ends included).
        Takes the top 53 bits of a uint64 (53 = the float64 mantissa
        bits) and scales to the unit interval.
        """
        return np.float64(
            int(self.get_uint64() >> 11) * (1.0 / 9007199254740991.0))

    def get_double_in_c0_o1(self) -> np.float64:
        """
        A random float in the [0, 1) interval (0 included, 1
        excluded). Top 53 bits of a uint64 scaled to the unit
        interval.
        """
        return np.float64(
            int(self.get_uint64() >> 11) * (1.0 / 9007199254740992.0))

    def get_double_in_o0_o1(self) -> np.float64:
        """
        A random float in the (0, 1) interval (open at both ends).
        Top 52 bits of a uint64, offset by half a step, scaled to
        the unit interval so neither endpoint is reachable.
        """
        return np.float64(
            (int(self.get_uint64() >> 12) + 0.5)
            * (1.0 / 4503599627370496.0))

    def random_choice_from_finite_set(self, k: int) -> np.uint64:
        """
        A random integer uniformly distributed in the [0, k-1]
        interval (k must not be 0).

        k == 1 returns 0 WITHOUT consuming a value from the sequence
        (a single-element choice is deterministic); otherwise one
        value is consumed.
        """
        k = int(k)
        if k == 0:
            raise ValueError("k cannot be 0")
        if k == 1:
            return np.uint64(0)
        r = self.get_double_in_c0_o1()
        c = int(math.floor(float(r) * k))
        return np.uint64(c)

    # -- the shuffles (Fisher-Yates, in place) --------------------------

    def shuffle_uint8(self, array: np.ndarray, n: int) -> None:
        """
        Arranges in place the n first elements of a uint8 array in
        random order (Fisher-Yates). n == 0 or n == 1 consumes no
        random value.
        """
        if array.dtype != np.uint8:
            raise ValueError("shuffle_uint8: the array must be uint8")
        if n > 1:
            for i in range(n - 1, 0, -1):
                j = int(self.random_choice_from_finite_set(i + 1))
                t = array[j]
                array[j] = array[i]
                array[i] = t

    def shuffle(self, array: np.ndarray, n: int) -> None:
        """
        The generic shuffle: any 1-D numpy array, in place
        (Fisher-Yates). n == 0 or n == 1 consumes no random value.
        """
        if array.ndim != 1:
            raise ValueError("shuffle: the array must be 1-D")
        if n > 1:
            for i in range(n - 1, 0, -1):
                j = int(self.random_choice_from_finite_set(i + 1))
                t = array[j]
                array[j] = array[i]
                array[i] = t

    def shuffle_double(self, array: np.ndarray, n: int) -> None:
        """
        The float64 array shuffle, in place (Fisher-Yates). n == 0
        or n == 1 consumes no random value.
        """
        if array.dtype != np.float64:
            raise ValueError("shuffle_double: the array must be float64")
        if n > 1:
            for i in range(n - 1, 0, -1):
                j = int(self.random_choice_from_finite_set(i + 1))
                t = array[j]
                array[j] = array[i]
                array[i] = t

    def shuffle_int(self, array: np.ndarray, n: int) -> None:
        """
        The integer array shuffle, in place (Fisher-Yates; accepts
        any integer dtype — the shuffle is a dtype-agnostic slot
        swap). n == 0 or n == 1 consumes no random value.
        """
        if not np.issubdtype(array.dtype, np.integer):
            raise ValueError("shuffle_int: the array must be an integer")
        if n > 1:
            for i in range(n - 1, 0, -1):
                j = int(self.random_choice_from_finite_set(i + 1))
                t = array[j]
                array[j] = array[i]
                array[i] = t

    # -- the string + the set extraction --------------------------------

    def random_string_az(self, n: int) -> str:
        """
        A string of n random characters in the [a..z] range.
        """
        n = int(n)
        a = ord('a')
        z = ord('z')
        range_az = z - a + 1  # 26 (the letters a..z)
        return "".join(
            chr(a + int(self.random_choice_from_finite_set(range_az)))
            for _ in range(n))

    def extract_from_set64(self, set_arr: np.ndarray) -> np.uint8:
        """
        Picks + REMOVES a random bit from the 64-bit set and returns
        its 0-based position.

        `set_arr` is a uint64 ndarray whose element 0 holds the set
        bitmask, updated IN PLACE (note: the picked bit is cleared
        from the ORIGINAL set, so the skipped-lowest bits survive).

        How it works: one get_uint64 draw; the pick delegated to the
        numba kernel pick_one_from_set64 (the single source of the
        pick technique); the picked bit is then cleared from
        the ORIGINAL set.
        """
        if set_arr.dtype != np.uint64:
            raise ValueError("extract_from_set64: the set must be uint64")
        s = set_arr[0]
        if s == np.uint64(0):
            raise ValueError("the set must not be empty")
        _bb, p = pick_one_from_set64(np.uint64(s), self.get_uint64())
        # Clear the picked bit from the ORIGINAL set (the numpy ~
        # wraps at 64 bits).
        set_arr[0] = set_arr[0] & ~(np.uint64(1) << np.uint64(p))
        return np.uint8(p)

    def choose_one_from_set64(self, set64: np.uint64) -> (np.uint64, np.uint8):
        """
        Picks a random bit from the 64-bit set WITHOUT removing it
        (unlike extract_from_set64, the set is read, never mutated):
        one get_uint64 draw, the pick delegated to the numba kernel
        pick_one_from_set64 (the single source of the pick technique
        — the single source of the pick technique). k = the popcount, the c-th set bit (skipping the c
        lowest) is picked. Returns (1 << p, p). The empty set
        returns the (0, 64) sentinel (64 = no bit) WITHOUT consuming
        a draw.
        """
        s = np.uint64(set64)
        if s == np.uint64(0):
            return np.uint64(0x0000000000000000), np.uint8(64)
        # The numba scalar-return idiom: the kernel values come back
        # as Python ints at the Python boundary — re-wrap to the
        # numpy dtypes (the method's historical contract).
        bb, p = pick_one_from_set64(s, self.get_uint64())
        return np.uint64(bb), np.uint8(p)


# ---------------------------------------------------------------------
# The numba MT19937-64 batch-draw kernel: the twist + the 4-op
# temper, the single source of the draw path. _get_uint64_batch
# is INTERNAL to the class: only MT19937.get_uint64_batch calls
# it. The state is the caller's (the `mt` working area + the
# `mti` index), mutated in place.
# ---------------------------------------------------------------------


@nb.njit(cache=True)
def _get_uint64_batch(mt, mti, n):
    """INTERNAL to the class: the n successive u64 draws (the
    twist + the 4-op temper). Only MT19937.get_uint64_batch
    calls it. Returns (draws, mti). The twist + temper
    constants (MM / UM / LM / MAG) are local to the kernel; NN
    (the working-area size) is module-level."""
    # The twist + temper constants (kernel-local).
    MM = 156  # the half-state offset (NN // 2)
    UM = np.uint64(0xFFFFFFFF80000000)  # keep the upper 33 bits
    LM = np.uint64(0x000000007FFFFFFF)  # keep the lower 31 bits
    MAG = np.uint64(0xB5026F5AA96619E9)  # the odd-parity XOR constant
    out = np.empty(n, dtype=np.uint64)
    for j in range(n):
        if mti >= NN:
            i = 0
            while i < NN - MM:
                x = (mt[i] & UM) | (mt[i + 1] & LM)
                mt[i] = mt[i + MM] ^ (x >> 1) ^ \
                    (np.uint64(0) if (x & np.uint64(1)) == 0 else MAG)
                i += 1
            while i < NN - 1:
                x = (mt[i] & UM) | (mt[i + 1] & LM)
                mt[i] = mt[i + (MM - NN)] ^ (x >> 1) ^ \
                    (np.uint64(0) if (x & np.uint64(1)) == 0 else MAG)
                i += 1
            x = (mt[NN - 1] & UM) | (mt[0] & LM)
            mt[NN - 1] = mt[MM - 1] ^ (x >> 1) ^ \
                (np.uint64(0) if (x & np.uint64(1)) == 0 else MAG)
            mti = 0
        x = mt[mti]
        mti += 1
        x = x ^ ((x >> 29) & np.uint64(0x5555555555555555))
        x = x ^ ((x << 17) & np.uint64(0x71D67FFFEDA60000))
        x = x ^ ((x << 37) & np.uint64(0xFFF7EEE000000000))
        x = x ^ (x >> 43)
        out[j] = x
    return out, mti


# ---------------------------------------------------------------------
# The pick-from-set technique (D-221): the SINGLE SOURCE shared by
# MT19937.choose_one_from_set64 / extract_from_set64 (they draw one
# value and delegate) and by the numba batch callers (e.g.
# random_game_choose_move). pick_one_from_set64 is the scalar kernel:
# the pick from a NON-ZERO set given the pre-drawn value.
# pick_one_from_set64_batch is its vectorized form over an (N,) array
# of sets.
# ---------------------------------------------------------------------


@nb.njit(cache=True)
def pick_one_from_set64(s, d):
    """
    The uniform pick of one bit from the NON-ZERO 64-bit set s,
    given the pre-drawn uint64 value d: k = popcount(s),
    r = (d >> 11) * (1 / 2**53) — the get_double_in_c0_o1
    scalarization — c = floor(r * k), the c-th set bit of s
    (skipping the c lowest). Returns (1 << p, p).
    """
    v = s - ((s >> np.uint64(1)) & np.uint64(0x5555555555555555))
    v = (v & np.uint64(0x3333333333333333)) + ((v >> np.uint64(2)) & np.uint64(0x3333333333333333))
    v = (v + (v >> np.uint64(4))) & np.uint64(0x0F0F0F0F0F0F0F0F)
    k = (v * np.uint64(0x0101010101010101)) >> np.uint64(56)
    r = np.float64(d >> np.uint64(11)) * (1.0 / 9007199254740992.0)
    c = int(math.floor(r * np.float64(k)))
    t = s
    for _ in range(c):
        t = (t - np.uint64(1)) & t
    low = t & (np.uint64(0) - t)
    p = 0
    u = low
    while (u & np.uint64(1)) == np.uint64(0):
        u = u >> np.uint64(1)
        p += 1
    return low, np.uint8(p)


@nb.njit(parallel=True, cache=True)
def pick_one_from_set64_batch(sets, draws, slots):
    """
    The vectorized pick_one_from_set64 over an (N,) uint64 array of
    sets: element i with a non-empty set picks from sets[i]
    using draws[slots[i]] (slots[i] = the number of NON-EMPTY sets
    before i — the prefix count the caller computes, e.g. the cumsum
    of sets != 0); draws is the (k,) uint64 array of the pre-drawn
    values, one per non-empty set in element order. An empty set
    yields 0 (the caller's pass signal) and consumes no draw. The
    whole call is the bit-identical counterpart of calling
    MT19937.choose_one_from_set64 on the elements in order with the
    same stream.
    """
    n = sets.shape[0]
    out = np.empty(n, dtype=np.uint64)
    for i in nb.prange(n):
        s = sets[i]
        if s == np.uint64(0):
            out[i] = np.uint64(0)
        else:
            bb, _p = pick_one_from_set64(s, draws[slots[i]])
            out[i] = bb
    return out
