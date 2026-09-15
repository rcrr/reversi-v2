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
The MT-19937 64-bit PRNG — the line-by-line Python port of Roberto's
C library (prng.c, 2017 — the 64-bit variant, NOT the 32-bit
reference), the I-017 T2 (D-159).

The strict-typing ruling (D-159, Roberto: "NUMPY e stiamo strict con
i tipi"): every 64-bit value in the DATA PATH is a numpy uint64 — the
type itself applies the C unsigned-wraparound contract (a numpy
uint64 addition/multiplication overflows modulo 2^64 exactly like the
C, no unbounded Python ints, no manual masking). Loop counters are
plain ints (control flow, not data).

Ported: the full MT family (the 15 prng_mt19937_* functions).
Skipped: the 4 prng_stdlib_* wrappers (thin over srand/rand — a
no-sense in Python) and prng_uint64_from_clock_random_seed (the
clock-based seed: non-deterministic and unused — the pipeline seed
comes from the config and is part of the cache signature).

The bit-exact verification oracles (T3): the C build of prng.c +
bit_works.c + time_utils.c and Roberto's ut_prng.c.
"""

from __future__ import annotations

import math

import numpy as np
import numba as nb

__all__ = ['MT19937', 'NN', 'MM', 'UM', 'LM', 'MAG01', 'MAG',
           'mt19937_init', 'mt19937_batch_draw']

# The C static constants (prng.c L154-158), verbatim.
NN: int = 312
MM: int = 156
UM: np.uint64 = np.uint64(0xFFFFFFFF80000000)  # Most significant 33 bits
LM: np.uint64 = np.uint64(0x000000007FFFFFFF)  # Least significant 31 bits
MAG01: np.ndarray = np.array(
    [np.uint64(0), np.uint64(0xB5026F5AA96619E9)], dtype=np.uint64)

#: The scalar MAG (the C MAG01[1] — the odd index), the constant
#: the numba batch-draw kernel switches on (the single source for
#: the G0 wave stream, the D-194 move from lm/hlp_wave.py).
MAG: np.uint64 = MAG01[1]


class MT19937:
    """
    The 64-bit MT-19937 generator state — the Python face of the C
    prng_mt19937_t struct (the `uint64_t *mt` working area + the
    `size_t mti` working index).

    Construction fuses the C `prng_mt19937_new` + one init call
    (fail-fast: exactly one of `seed` / `init_key` must be given —
    the C allows deferring the init to the first get_uint64, which
    applies its default seed 5489; the port keeps that fallback for
    a BARE state, see get_uint64).

    Attributes (internal — the C struct fields):
      _mt:  np.ndarray, shape (NN,), dtype uint64 — the working area.
      _mti: int — the working index; NN + 1 = not initialized.
    """

    def __init__(self, seed: int | None = None, *,
                 init_key: np.ndarray | list | None = None) -> None:
        if (seed is None) == (init_key is None):
            raise ValueError("exactly one of seed / init_key must be given")
        # prng_mt19937_new: the fresh working area + the sentinel.
        self._mt = np.zeros(NN, dtype=np.uint64)
        # mti == NN + 1 means that the mt array is not initialized.
        self._mti = NN + 1
        if seed is not None:
            self.init_by_seed(seed)
        else:
            self.init_by_array(init_key)

    # -- the C accessors (read-only views, for the tests) -------------

    @property
    def mt(self) -> np.ndarray:
        """The C `st->mt` working area (read-only view)."""
        return self._mt

    @property
    def mti(self) -> int:
        """The C `st->mti` working index."""
        return self._mti

    # -- init ----------------------------------------------------------

    def init_by_seed(self, seed: int) -> None:
        """
        C prng_mt19937_init_by_seed (prng.c L309), line by line.

        Note (verbatim quirk, DO NOT "fix"): the C loop leaves
        `st->mti == nn` — the FIRST get_uint64 therefore twists the
        just-initialized array immediately.
        """
        self._mt[0] = np.uint64(seed)
        # The C unsigned arithmetic wraps modulo 2^64 BY DESIGN (that
        # is the contract): the numpy overflow warnings are silenced
        # locally (errstate) — the wrap is not an error.
        with np.errstate(over="ignore", invalid="ignore"):
            for mti in range(1, NN):
                prev = self._mt[mti - 1]
                # 6364136223846793005 is HIS constant (prng.c) — it is
                # NOT the 32-bit-reference 6364136293807784493.
                self._mt[mti] = (
                    np.uint64(6364136223846793005) * (prev ^ (prev >> 62))
                    + np.uint64(mti))
        self._mti = NN  # the C for-loop leaves mti == nn

    def init_by_array(self, init_key: np.ndarray | list) -> None:
        """
        C prng_mt19937_init_by_array (prng.c L337), line by line.

        `init_key` is the uint64 array of init values. The C reads
        `init_key[j]` with j wrapping at key_length — an EMPTY key
        would be an out-of-bounds read in C (UB); the port fails
        fast with a ValueError instead.
        """
        key = np.asarray(init_key, dtype=np.uint64).ravel()
        key_length = int(key.size)
        if key_length == 0:
            raise ValueError("init_key must not be empty")

        i = 1
        j = 0
        k = NN if NN > key_length else key_length

        self.init_by_seed(19650218)

        # The C unsigned arithmetic wraps BY DESIGN (as above).
        with np.errstate(over="ignore", invalid="ignore"):
            while k:
                k -= 1
                prev = self._mt[i - 1]
                self._mt[i] = (
                    (self._mt[i] ^ (prev ^ (prev >> 62))
                     * np.uint64(3935559000370003845))
                    + key[j] + np.uint64(j))  # non linear
                i += 1
                j += 1
                if i >= NN:
                    self._mt[0] = self._mt[NN - 1]
                    i = 1
                if j >= key_length:
                    j = 0

            k = NN - 1
            while k:
                k -= 1
                prev = self._mt[i - 1]
                self._mt[i] = (
                    (self._mt[i] ^ (prev ^ (prev >> 62))
                     * np.uint64(2862933555777941757))
                    - np.uint64(i))  # non linear (the unsigned wrap)
                i += 1
                if i >= NN:
                    self._mt[0] = self._mt[NN - 1]
                    i = 1

        # MSB is 1; assuring non-zero initial array.
        self._mt[0] = np.uint64(1) << 63

    # -- the generators -------------------------------------------------

    def get_uint64(self) -> np.uint64:
        """
        C prng_mt19937_get_uint64 (prng.c L380), line by line: the
        twist (312 words at one time) + the 4-op temper. Returns the
        next pseudo-random uint64 of the sequence.
        """
        mt = self._mt
        if self._mti >= NN:
            # If init_by_seed has not been called, a default initial
            # seed is used (the C contract, kept for a bare state).
            if self._mti == NN + 1:
                self.init_by_seed(5489)

            i = 0
            while i < NN - MM:
                x = (mt[i] & UM) | (mt[i + 1] & LM)
                mt[i] = mt[i + MM] ^ (x >> 1) ^ MAG01[int(x & 1)]
                i += 1

            # The C index `i + (mm - nn)` (the unsigned wrap of
            # mm - nn) is `i - 156` in plain Python.
            while i < NN - 1:
                x = (mt[i] & UM) | (mt[i + 1] & LM)
                mt[i] = mt[i + (MM - NN)] ^ (x >> 1) ^ MAG01[int(x & 1)]
                i += 1

            x = (mt[NN - 1] & UM) | (mt[0] & LM)
            mt[NN - 1] = mt[MM - 1] ^ (x >> 1) ^ MAG01[int(x & 1)]

            self._mti = 0

        x = mt[self._mti]
        self._mti += 1

        # The temper (prng.c L411-414): the & binds tighter than ^,
        # exactly as in the C; the numpy uint64 shifts wrap at 64 bits.
        x = x ^ (x >> 29) & np.uint64(0x5555555555555555)
        x = x ^ (x << 17) & np.uint64(0x71D67FFFEDA60000)
        x = x ^ (x << 37) & np.uint64(0xFFF7EEE000000000)
        x = x ^ (x >> 43)

        return x

    def get_double_in_c0_c1(self) -> np.float64:
        """
        C prng_mt19937_get_double_in_c0_c1 (prng.c L432): a random
        number on the [0, 1] real interval (both ends included).
        """
        return np.float64(
            int(self.get_uint64() >> 11) * (1.0 / 9007199254740991.0))

    def get_double_in_c0_o1(self) -> np.float64:
        """
        C prng_mt19937_get_double_in_c0_o1 (prng.c L450): a random
        number on the [0, 1) real interval.
        """
        return np.float64(
            int(self.get_uint64() >> 11) * (1.0 / 9007199254740992.0))

    def get_double_in_o0_o1(self) -> np.float64:
        """
        C prng_mt19937_get_double_in_o0_o1 (prng.c L468): a random
        number on the (0, 1) real interval (open at both ends).
        """
        return np.float64(
            (int(self.get_uint64() >> 12) + 0.5)
            * (1.0 / 4503599627370496.0))

    def random_choice_from_finite_set(self, k: int) -> np.uint64:
        """
        C prng_mt19937_random_choice_from_finite_set (prng.c L495),
        line by line: a random integer uniformly distributed in the
        [0, k-1] integer interval (k must not be 0 — the C assert).

        k == 1 returns 0 WITHOUT consuming a value from the prng
        sequence (the C contract); otherwise the prng status is
        altered.
        """
        k = int(k)
        if k == 0:
            raise ValueError("k cannot be 0 (the C assert)")
        if k == 1:
            return np.uint64(0)
        r = self.get_double_in_c0_o1()
        c = int(math.floor(float(r) * k))
        # The numpy cast wraps modulo 2^64, exactly like the C
        # (uint64_t) cast on the floor result.
        return np.uint64(c)

    # -- the shuffles (Fisher-Yates, in place) --------------------------

    def shuffle_uint8(self, array: np.ndarray, n: int) -> None:
        """
        C prng_mt19937_shuffle_array_uint8 (prng.c L532): arranges in
        place the n elements of the uint8 array in random order.
        n == 0 or n == 1: no random number is consumed (the C
        contract).
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
        C prng_mt19937_shuffle_array_p (prng.c L573) — the GENERIC
        ("pointer") shuffle: any 1-D numpy array (the C void** face),
        in place. n == 0 or n == 1: no random number is consumed (the
        C contract).
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
        C prng_mt19937_shuffle_array_double (prng.c L616): the
        float64 array face, in place. n == 0 or n == 1: no random
        number is consumed (the C contract).
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
        C prng_mt19937_shuffle_array_int (prng.c L657): the integer
        array face, in place (the C type is the 32-bit int; the
        numpy port accepts any integer dtype — the shuffle semantics
        are dtype-agnostic slot swaps). n == 0 or n == 1: no random
        number is consumed (the C contract).
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
        C prng_mt19937_random_string_az (prng.c L693): a sequence of
        n random characters in the [a..z] range (the C fills a
        NUL-terminated buffer; the Python face returns the str).
        """
        n = int(n)
        a = ord('a')
        z = ord('z')
        range_az = z - a  # 25 (the C: the unsigned range)
        return "".join(
            chr(a + int(self.random_choice_from_finite_set(range_az)))
            for _ in range(n))

    def extract_from_set64(self, set_arr: np.ndarray) -> np.uint8:
        """
        C prng_mt19937_extract_from_set64 (prng.c L712), line by
        line: extracts (picks + removes) a random bit from the
        64-bit set and returns its 0-based position.

        `set_arr` is the C `uint64_t *set` face: a uint64 ndarray
        whose element 0 holds the set bitmask, updated IN PLACE (the
        C pointer semantics — note the C clears the picked bit from
        the ORIGINAL set, so the skipped-lowest bits survive).

        The three bitw_* C helpers (bit_works.c) are inlined here:
          bitw_bit_count_64(s)           -> popcount(s)
          bitw_reset_lowest_set_bit_64   -> (s - 1) & s (clears the
                                             lowest set bit)
          bitw_bit_scan_forward_64(s)    -> the index of the lowest
                                             set bit (the C de Bruijn
                                             table; here
                                             (s & -s).bit_length() - 1)
        """
        if set_arr.dtype != np.uint64:
            raise ValueError("extract_from_set64: the set must be uint64")
        s = set_arr[0]
        k = int(s).bit_count()
        if k == 0:
            raise ValueError("the set must not be empty (the C assert *set)")
        r = self.get_double_in_c0_o1()
        c = int(math.floor(float(r) * k))
        for _ in range(c):
            s = (s - 1) & s  # bitw_reset_lowest_set_bit_64
        low = int(s) & -int(s)
        p = low.bit_length() - 1  # bitw_bit_scan_forward_64
        # The C: *set = *set &~(1ULL << p) — the mask applies to the
        # ORIGINAL set (the numpy ~ wraps at 64 bits, like the C).
        set_arr[0] = set_arr[0] & ~(np.uint64(1) << p)
        return np.uint8(p)

    def choose_one_from_set64(self, set64: np.uint64) -> (np.uint64, np.uint8):
        s = set64
        k = int(s).bit_count()
        if k == 0:
            return np.uint64(0x0000000000000000), np.uint8(64)
        r = self.get_double_in_c0_o1()
        c = int(math.floor(float(r) * k))
        for _ in range(c):
            s = (s - 1) & s
        low = int(s) & -int(s)
        p = low.bit_length() - 1
        return np.uint64(1) << p, np.uint8(p)


# ---------------------------------------------------------------------
# The numba MT19937-64 kernels — the SINGLE SOURCE of the batch
# draw (the D-194 move from lm/hlp_wave.py, which now imports
# them): the twist + the 4-op temper, bit-exact vs the golden-
# pinned MT19937 class above (the T3 C oracle). The state is the
# caller's (the `mt` working area + the `mti` index), mutated in
# place. The G0 wave engine (hlp_wave.run_wave_g0) is the
# consumer.
# ---------------------------------------------------------------------

@nb.njit(cache=True)
def mt19937_init(mt, seed):
    """C prng_mt19937_init_by_seed, line by line (the
    verbatim quirk: the loop leaves mti == NN — the first
    draw twists the just-initialized array). Returns mti."""
    mt[0] = np.uint64(seed)
    for i in range(1, NN):
        prev = mt[i - 1]
        mt[i] = np.uint64(6364136223846793005) * (prev ^ (prev >> 62)) \
            + np.uint64(i)
    return NN


@nb.njit(cache=True)
def mt19937_batch_draw(mt, mti, n):
    """The n successive u64 draws (the twist + the 4-op
    temper, prng.c L380-414 line by line — bit-exact vs the
    golden-pinned MT19937 class above, the T3 C oracle).
    Returns (draws, mti)."""
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
