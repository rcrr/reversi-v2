#
# test_feature_prng.py
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
#
#
# How to run the feature_prng module unit tests.
#
# Run from the workspace root (the directory containing .venv and src).
#
# -0- Activate the environment.
#
# $ source .venv/bin/activate
#
# -1- Run the tests.
#
# time PERF=0 python3 -m unittest reversi.test.test_feature_prng
#

"""
The MT19937 (the 64-bit MT-19937 PRNG port, the I-017 T2, D-159)
SMOKE micro-suite: the determinism, the strict typing (the numpy
uint64 / float64 dtypes of the state and of every output), the
range / wrap contracts, the no-consume contracts (k == 1, the
n <= 1 shuffles), and the extract_from_set64 semantics.

The BIT-EXACT golden suite (the exact bit-sequence vs Roberto's C
build + the published vectors + the equi-distribution property)
is the NEXT task (the I-017 T3, test_feature_prng.py extended) —
this suite only pins the contract so an accidental refactor
cannot slip in silently.
"""

import unittest

import numpy as np

from reversi.feature_prng import MT19937, NN, MM, UM, LM, MAG01


class TestFeaturePrngContract(unittest.TestCase):
    """The port contract: the determinism, the typing, the wraps,
    the no-consume rules, the set extraction."""

    def test_constants_are_the_c_ones(self):
        # The C static constants (prng.c L154-158), verbatim.
        self.assertEqual(NN, 312)
        self.assertEqual(MM, 156)
        self.assertEqual(int(UM), 0xFFFFFFFF80000000)
        self.assertEqual(int(LM), 0x000000007FFFFFFF)
        self.assertEqual(int(MAG01[1]), 0xB5026F5AA96619E9)

    def test_ctor_fails_fast(self):
        # Exactly one of seed / init_key (the fused C new + init).
        with self.assertRaises(ValueError):
            MT19937()
        with self.assertRaises(ValueError):
            MT19937(42, init_key=[1])
        # The empty key: the C out-of-bounds read becomes a
        # fail-fast ValueError (documented deviation).
        with self.assertRaises(ValueError):
            MT19937(init_key=[])

    def test_seed_determinism_and_typing(self):
        a = MT19937(42)
        b = MT19937(42)
        for _ in range(50):
            va, vb = a.get_uint64(), b.get_uint64()
            self.assertIsInstance(va, np.uint64)
            self.assertEqual(va, vb)
        c = MT19937(43)
        self.assertNotEqual(c.get_uint64(), a.get_uint64())
        # The state is the C working area: a uint64 ndarray.
        self.assertEqual(a.mt.dtype, np.uint64)
        self.assertEqual(a.mt.shape, (NN,))

    def test_array_init_determinism(self):
        key = np.array([1, 2, 3, 4], dtype=np.uint64)
        a = MT19937(init_key=key)
        b = MT19937(init_key=[1, 2, 3, 4])
        for _ in range(50):
            self.assertEqual(a.get_uint64(), b.get_uint64())
        c = MT19937(init_key=[1, 2, 3, 5])
        self.assertNotEqual(c.get_uint64(), a.get_uint64())
        # The C final touch: the MSB of mt[0] is 1 (the non-zero
        # initial array assurance) — a FRESH instance (the draws
        # twist the working area, including mt[0]).
        m = MT19937(init_key=key)
        self.assertEqual(int(m.mt[0]) >> 63, 1)

    def test_get_uint64_wrap_64bit(self):
        # The full 64-bit domain: the max seed exercises the wrap
        # arithmetic without any overflow error (the numpy
        # errstate silences the by-design wraps).
        g = MT19937(np.uint64(0xFFFFFFFFFFFFFFFF))
        for _ in range(100):
            v = g.get_uint64()
            self.assertIsInstance(v, np.uint64)

    def test_double_ranges_and_typing(self):
        g = MT19937(7)
        for _ in range(1000):
            c01 = g.get_double_in_c0_c1()
            self.assertIsInstance(c01, np.float64)
            self.assertGreaterEqual(float(c01), 0.0)
            self.assertLessEqual(float(c01), 1.0)
            co1 = g.get_double_in_c0_o1()
            self.assertGreaterEqual(float(co1), 0.0)
            self.assertLess(float(co1), 1.0)
            o01 = g.get_double_in_o0_o1()
            self.assertGreater(float(o01), 0.0)
            self.assertLess(float(o01), 1.0)

    def test_random_choice_contracts(self):
        # k == 0: the C assert becomes a ValueError.
        g = MT19937(1)
        with self.assertRaises(ValueError):
            g.random_choice_from_finite_set(0)
        # k == 1: returns 0 WITHOUT consuming (the C contract).
        h = MT19937(1)
        self.assertEqual(int(h.random_choice_from_finite_set(1)), 0)
        i = MT19937(1)
        self.assertEqual(h.get_uint64(), i.get_uint64())
        # k == 5: every value in [0, 4].
        g = MT19937(2)
        for _ in range(1000):
            c = g.random_choice_from_finite_set(5)
            self.assertIsInstance(c, np.uint64)
            self.assertGreaterEqual(int(c), 0)
            self.assertLess(int(c), 5)

    def test_shuffle_contracts(self):
        # A shuffled array is a PERMUTATION of the input.
        base = np.arange(16, dtype=np.uint8)
        g = MT19937(3)
        shuffled = base.copy()
        g.shuffle_uint8(shuffled, 16)
        self.assertEqual(sorted(shuffled.tolist()), base.tolist())
        # n <= 1: no random number is consumed (the C contract).
        a = MT19937(3)
        one = np.array([7], dtype=np.uint8)
        a.shuffle_uint8(one, 1)
        b = MT19937(3)
        self.assertEqual(a.get_uint64(), b.get_uint64())
        # The dtype pins (the strict-typing ruling).
        with self.assertRaises(ValueError):
            a.shuffle_uint8(np.arange(4, dtype=np.int64), 4)
        with self.assertRaises(ValueError):
            a.shuffle_double(np.arange(4, dtype=np.uint8), 4)
        with self.assertRaises(ValueError):
            a.shuffle_int(np.arange(4, dtype=np.float64), 4)
        # The generic (the C _p face) works on any 1-D array.
        arr = np.array([3.0, 1.0, 2.0])
        a.shuffle(arr, 3)
        self.assertEqual(sorted(arr.tolist()), [1.0, 2.0, 3.0])

    def test_random_string_az(self):
        g = MT19937(5)
        s = g.random_string_az(100)
        self.assertEqual(len(s), 100)
        self.assertTrue(all("a" <= ch <= "z" for ch in s))
        # Determinism: the same seed, the same string (two fresh
        # instances — the draws advance the sequence position).
        self.assertEqual(MT19937(5).random_string_az(10),
                         MT19937(5).random_string_az(10))
        # The empty string (n == 0).
        self.assertEqual(g.random_string_az(0), "")

    def test_extract_from_set64(self):
        # The single-bit set: always that bit, the set empties.
        g = MT19937(9)
        s = np.array([np.uint64(1) << 40], dtype=np.uint64)
        self.assertEqual(int(g.extract_from_set64(s)), 40)
        self.assertEqual(int(s[0]), 0)
        # The empty set: the C assert becomes a ValueError.
        with self.assertRaises(ValueError):
            g.extract_from_set64(np.array([np.uint64(0)], dtype=np.uint64))
        # The full 64-bit set: 64 distinct bits come out, and the
        # set empties exactly when the last one is picked.
        f = MT19937(10)
        full = np.array([np.uint64(0xFFFFFFFFFFFFFFFF)], dtype=np.uint64)
        seen = set()
        for _ in range(64):
            p = int(f.extract_from_set64(full))
            self.assertNotIn(p, seen)
            seen.add(p)
        self.assertEqual(int(full[0]), 0)
        self.assertEqual(len(seen), 64)
        # The returned position was a set bit BEFORE the call, and
        # the picked bit is cleared from the ORIGINAL set (the C
        # pointer semantics: the skipped-lowest bits survive).
        h = MT19937(11)
        for _ in range(200):
            s2 = np.array([np.uint64(0x5555555555555555)], dtype=np.uint64)
            p = int(h.extract_from_set64(s2))
            self.assertTrue(0x5555555555555555 & (1 << p))
            self.assertFalse(int(s2[0]) & (1 << p))


if __name__ == '__main__':
    unittest.main()
