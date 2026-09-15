#
# test_prng.py
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
# How to run the prng module unit tests.
#
# Run from the workspace root (the directory containing .venv and src).
#
# -0- Activate the environment.
#
# $ source .venv/bin/activate
#
# -1- Run the tests.
#
# time PERF=0 python3 -m unittest reversi.test.test_prng
#

"""
The MT19937 (the 64-bit MT-19937 PRNG port, the I-017 T2,
D-159) suite:

- the SMOKE micro-suite (the T2): the determinism, the strict
  typing (the numpy uint64 / float64 dtypes of the state and of
  every output), the range / wrap contracts, the no-consume
  contracts (k == 1, the n <= 1 shuffles), and the
  extract_from_set64 semantics;
- the C-ORACLE golden suite (the T3, D-161): the exact
  bit-sequence vs Roberto's C build (the committed
  prng_golden.txt — the C library is the ONLY valid oracle: his
  variant, the 64-bit constants; numpy RandomState is NOT) + the
  seed-init contract (the whole 312-word mt state, verbatim) +
  the equi-distribution on the first 100k.
"""

import unittest

import numpy as np

from reversi.test.paths import WORKSPACE_ROOT
from reversi.tools.prng import MT19937, NN, MM, UM, LM, MAG01


#: The committed C-oracle golden (the D-161 artifact).
GOLDEN_PATH = (WORKSPACE_ROOT / "src" / "reversi" / "test" / "data"
               / "prng_golden.txt")


def _load_golden() -> "dict[str, list[str]]":
    """Parses the golden file: the [section] markers group the
    lines (the # header is skipped)."""
    sections: "dict[str, list[str]]" = {}
    current = None
    with open(GOLDEN_PATH) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("[") and line.endswith("]"):
                current = line[1:-1]
                sections[current] = []
            elif current is not None:
                sections[current].append(line)
    return sections


class TestPrng(unittest.TestCase):
    """The port contract: the determinism, the typing, the wraps,
    the no-consume rules, the set extraction."""

    def test_constants_are_the_c_ones(self):
        # The C static constants (prng.c L154-158), verbatim.
        self.assertEqual(NN, 312)
        self.assertEqual(MM, 156)
        self.assertEqual(int(UM), 0xFFFFFFFF80000000)
        self.assertEqual(int(LM), 0x000000007FFFFFFF)
        self.assertEqual(int(MAG01[1]), 0xB5026F5AA96619E9)

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

    def test_get_uint64_wrap_64bit(self):
        # The full 64-bit domain: the max seed exercises the wrap
        # arithmetic without any overflow error (the numpy
        # errstate silences the by-design wraps).
        g = MT19937(np.uint64(0xFFFFFFFFFFFFFFFF))
        for _ in range(100):
            v = g.get_uint64()
            self.assertIsInstance(v, np.uint64)

    def test_get_uint64_batch_matches_scalar(self):
        # The numba batch draw (get_uint64_batch, the D-195 class
        # interface) is bit-exact vs get_uint64 called n times
        # (the same twist + the same 4-op temper, the single
        # source); 500 draws cross the 312-word twist boundary.
        g = MT19937(1234)
        ref = MT19937(1234)
        n = 500
        batch = g.get_uint64_batch(n)
        self.assertEqual(batch.dtype, np.uint64)
        self.assertEqual(batch.shape, (n,))
        for i in range(n):
            self.assertEqual(int(batch[i]), int(ref.get_uint64()),
                             f"batch draw {i} deviates from the "
                             "scalar reference")

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


class TestPrngGolden(unittest.TestCase):
    """
    The C-oracle bit-exact golden (the I-017 T3, D-161): the
    committed sequences generated by the C build of Roberto's
    prng.c (the file header records the provenance). Each
    section is mirrored with a FRESH instance (the golden
    generator's contract).
    """

    @classmethod
    def setUpClass(cls):
        cls.g = _load_golden()

    def test_seed42_init_state(self):
        # The seed-init contract: the whole 312-word working area
        # after init_by_seed(42) — the C state, verbatim.
        g = MT19937(42)
        state = [f"{int(w):016x}" for w in g.mt]
        self.assertEqual(state, self.g["mt_seed42"])

    def test_seed42_sequence(self):
        g = MT19937(42)
        seq = [f"{int(g.get_uint64()):016x}" for _ in range(10000)]
        self.assertEqual(seq, self.g["seq_seed42"])

    def test_doubles(self):
        for name, method in [
            ("doubles_c0_c1", "get_double_in_c0_c1"),
            ("doubles_c0_o1", "get_double_in_c0_o1"),
            ("doubles_o0_o1", "get_double_in_o0_o1"),
        ]:
            g = MT19937(42)
            draw = getattr(g, method)
            with self.subTest(kind=name):
                seq = [f"{draw():.17g}" for _ in range(100)]
                self.assertEqual(seq, self.g[name])

    def test_choice_sequence(self):
        g = MT19937(42)
        seq = [str(int(g.random_choice_from_finite_set(5)))
               for _ in range(1000)]
        self.assertEqual(seq, self.g["choice5"])

    def test_extract_full_sequence(self):
        # 64 picks exhaust the full set: a permutation of 0..63,
        # the set empties exactly at the end (the C in-place
        # contract: the picked bit is cleared from the ORIGINAL
        # set).
        g = MT19937(42)
        s = np.array([np.uint64(0xFFFFFFFFFFFFFFFF)], dtype=np.uint64)
        picks = [int(g.extract_from_set64(s)) for _ in range(64)]
        self.assertEqual([str(p) for p in picks], self.g["extract_full"])
        self.assertEqual(sorted(picks), list(range(64)))
        self.assertEqual(int(s[0]), 0)


class TestPrngEquidistribution(unittest.TestCase):
    """
    The statistical properties (the doc spec: 'the equi-
    distribution on the first 100k'): the per-bit balance, the
    chi-square on the top-bit bins, and the choice-64 uniformity.
    Python-side (no C golden needed — the property is of the
    sequence itself) and deterministic (the fixed seed 42).
    """

    N = 100000

    def _draw(self, n: int) -> np.ndarray:
        g = MT19937(42)
        return np.array([int(g.get_uint64()) for _ in range(n)],
                        dtype=np.uint64)

    def test_first_100k_bit_balance(self):
        # Every one of the 64 bit positions is set ~50% of the
        # time (the per-bit sigma is ~158 at n = 100k; the 2%
        # band is a ~12.6-sigma tolerance — generous and flake-
        # proof, and still catches a stuck / shifted bit).
        xs = self._draw(self.N)
        frac = np.array(
            [float(np.count_nonzero(xs & np.uint64(1) << b))
             for b in range(64)]) / self.N
        self.assertTrue(np.all(frac > 0.48))
        self.assertTrue(np.all(frac < 0.52))

    def test_first_100k_top_bits_chi_square(self):
        # The 100k draws binned by the top 7 bits (128 bins, the
        # expected 781.25 per bin): the chi-square statistic stays
        # far below the conservative 250 threshold (the df=127
        # 3.7-sigma critical is ~172).
        xs = self._draw(self.N)
        obs = np.bincount((xs >> 57).astype(np.int64), minlength=128)
        expected = self.N / 128
        chi2 = float(np.sum((obs - expected) ** 2 / expected))
        self.assertLess(chi2, 250.0)

    def test_choice_64_uniform(self):
        # 100k random_choice_from_finite_set(64) draws: 64 bins,
        # the expected 1562.5 — the conservative 130 threshold
        # (the df=63 3.7-sigma critical is ~108).
        g = MT19937(42)
        draws = [int(g.random_choice_from_finite_set(64))
                 for _ in range(self.N)]
        obs = np.bincount(draws, minlength=64)
        expected = self.N / 64
        chi2 = float(np.sum((obs - expected) ** 2 / expected))
        self.assertLess(chi2, 130.0)


if __name__ == '__main__':
    unittest.main()
