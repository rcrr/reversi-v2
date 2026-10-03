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
# time PERF=0 python3 -m unittest test.reversi.tools.test_prng
#

"""
The MT19937 (the 64-bit MT-19937 PRNG) suite:

- the SMOKE micro-suite: the determinism, the strict typing
  (the numpy uint64 / float64 dtypes of every output), the range /
  wrap contracts, the no-consume contracts (k == 1, the n <= 1
  shuffles), and the extract_from_set64 semantics;
- the bit-exact golden suite: the exact sequence vs the committed
  reference (data/prng_golden.txt) + the equi-distribution on the
  first 100k.
"""

import unittest

import numpy as np

from test.reversi.paths import WORKSPACE_ROOT
from reversi.tools.prng import MT19937, pick_one_from_set64, pick_one_from_set64_batch


#: The committed reference golden.
GOLDEN_PATH = (WORKSPACE_ROOT / "test" / "reversi" / "data"
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
    """The smoke contracts: the determinism, the typing, the
    wraps, the no-consume rules, the set extraction."""

    def test_get_uint64_wrap_64bit(self):
        # The full 64-bit domain: the max seed exercises the wrap
        # arithmetic without any overflow error (the numpy
        # errstate silences the by-design wraps).
        g = MT19937(np.uint64(0xFFFFFFFFFFFFFFFF))
        for _ in range(100):
            v = g.get_uint64()
            self.assertIsInstance(v, np.uint64)

    def test_get_uint64_batch_matches_scalar(self):
        # The batch draw (get_uint64_batch) is bit-exact vs
        # get_uint64 called n times (the same twist + the same
        # 4-op temper, the single source); 500 draws cross the
        # 312-word twist boundary.
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
        # k == 0: raises.
        g = MT19937(1)
        with self.assertRaises(ValueError):
            g.random_choice_from_finite_set(0)
        # k == 1: returns 0 WITHOUT consuming a value.
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
        # n <= 1: no random number is consumed.
        a = MT19937(3)
        one = np.array([7], dtype=np.uint8)
        a.shuffle_uint8(one, 1)
        b = MT19937(3)
        self.assertEqual(a.get_uint64(), b.get_uint64())
        # The dtype pins.
        with self.assertRaises(ValueError):
            a.shuffle_uint8(np.arange(4, dtype=np.int64), 4)
        with self.assertRaises(ValueError):
            a.shuffle_double(np.arange(4, dtype=np.uint8), 4)
        with self.assertRaises(ValueError):
            a.shuffle_int(np.arange(4, dtype=np.float64), 4)
        # The generic shuffle works on any 1-D array.
        arr = np.array([3.0, 1.0, 2.0])
        a.shuffle(arr, 3)
        self.assertEqual(sorted(arr.tolist()), [1.0, 2.0, 3.0])
        # shuffle_double is a PERMUTATION of a float64 array.
        d0 = np.arange(16, dtype=np.float64)
        d = d0.copy()
        a.shuffle_double(d, 16)
        self.assertEqual(sorted(d.tolist()), d0.tolist())
        # shuffle_int is a PERMUTATION of an integer array.
        i0 = np.arange(16, dtype=np.int64)
        i = i0.copy()
        a.shuffle_int(i, 16)
        self.assertEqual(sorted(i.tolist()), i0.tolist())

    def test_shuffle_nd_corder_parity(self):
        # The N-D C-order parity (D-421): shuffling an N-D array in
        # place (the n first elements, C-order) with seed S equals
        # shuffling the 1-D C-order ravel with the same seed S — the
        # draw sequence is shape-agnostic.
        seed = 42
        for shape in ((4, 6), (2, 3, 4)):
            base = np.arange(24, dtype=np.uint8).reshape(shape)
            nd = base.copy()
            MT19937(seed).shuffle_uint8(nd, 24)
            flat1 = base.copy().ravel()
            MT19937(seed).shuffle_uint8(flat1, 24)
            self.assertEqual(nd.ravel().tolist(), flat1.tolist())
        # F-order: the C-order element sequence is addressed through
        # .flat (no copy) — the parity target is still the C-order
        # ravel.
        fbase = np.arange(24, dtype=np.uint8).reshape(4, 6, order='F')
        fnd = fbase.copy()
        MT19937(seed).shuffle_uint8(fnd, 24)
        flat1 = fbase.ravel()
        MT19937(seed).shuffle_uint8(flat1, 24)
        self.assertEqual(fnd.ravel().tolist(), flat1.tolist())

    def test_shuffle_nd_all_methods_parity(self):
        # The C-order parity for the four methods (same seed, same
        # data): the N-D result equals the 1-D C-order ravel result.
        cases = (('shuffle_uint8', np.uint8),
                 ('shuffle_double', np.float64),
                 ('shuffle_int', np.int64),
                 ('shuffle', np.float64))
        for meth, dt in cases:
            base = np.arange(12, dtype=dt).reshape(3, 4)
            nd = base.copy()
            g = MT19937(55)
            getattr(g, meth)(nd, 12)
            flat1 = base.copy().ravel()
            h = MT19937(55)
            getattr(h, meth)(flat1, 12)
            self.assertEqual(nd.ravel().tolist(), flat1.tolist())

    def test_shuffle_nd_permutation_and_element_n(self):
        # A shuffled N-D array is a permutation of its elements.
        base = np.arange(12, dtype=np.float64).reshape(3, 4)
        shuffled = base.copy()
        MT19937(7).shuffle_double(shuffled, 12)
        self.assertEqual(sorted(shuffled.ravel().tolist()),
                         base.ravel().tolist())
        # n counts ELEMENTS in C-order: n = 4 touches only the first
        # row of a (3, 4).
        a = base.copy()
        MT19937(7).shuffle_double(a, 4)
        self.assertEqual(a[1:].tolist(), base[1:].tolist())
        self.assertEqual(sorted(a[0].tolist()), base[0].tolist())
        # n <= 1 on N-D consumes nothing.
        g = MT19937(7)
        one = base.copy()
        g.shuffle_double(one, 1)
        h = MT19937(7)
        self.assertEqual(g.get_uint64(), h.get_uint64())
        # The generic shuffle works on any shape (the D-417
        # follow-up).
        arr2 = np.array([[3.0, 1.0], [2.0, 4.0]])
        MT19937(13).shuffle(arr2, 4)
        self.assertEqual(sorted(arr2.ravel().tolist()),
                         [1.0, 2.0, 3.0, 4.0])

    def test_shuffle_strided_views(self):
        # A strided 1-D view is shuffled in place (no ravel copy — the
        # D-417 regression class): the unviewed base slots survive.
        base = np.arange(16, dtype=np.uint8)
        even = base[::2]
        even0 = even.copy()
        MT19937(11).shuffle_uint8(even, 8)
        self.assertEqual(sorted(even.tolist()), even0.tolist())
        expected = np.arange(16, dtype=np.uint8)
        expected[::2] = even
        self.assertEqual(base.tolist(), expected.tolist())
        # A strided N-D view: the C-order element sequence is
        # shuffled, the rest of the base survives.
        big = np.arange(36, dtype=np.int64).reshape(6, 6)
        sub = big[::2, ::2]
        sub0 = sub.copy()
        MT19937(12).shuffle_int(sub, 9)
        self.assertEqual(sorted(sub.ravel().tolist()), sub0.ravel().tolist())
        expected = np.arange(36, dtype=np.int64).reshape(6, 6)
        expected[::2, ::2] = sub
        self.assertEqual(big.tolist(), expected.tolist())

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
        # The empty set: raises.
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
        # the picked bit is cleared from the ORIGINAL set (the
        # skipped-lowest bits survive).
        h = MT19937(11)
        for _ in range(200):
            s2 = np.array([np.uint64(0x5555555555555555)], dtype=np.uint64)
            p = int(h.extract_from_set64(s2))
            self.assertTrue(0x5555555555555555 & (1 << p))
            self.assertFalse(int(s2[0]) & (1 << p))


class TestPrngGolden(unittest.TestCase):
    """
    The bit-exact golden: the committed reference sequences
    (data/prng_golden.txt). Each section is mirrored with a
    FRESH instance of MT19937 (seed 42).
    """

    @classmethod
    def setUpClass(cls):
        cls.g = _load_golden()

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
        # the set empties exactly at the end (the picked bit is
        # cleared from the ORIGINAL set).
        g = MT19937(42)
        s = np.array([np.uint64(0xFFFFFFFFFFFFFFFF)], dtype=np.uint64)
        picks = [int(g.extract_from_set64(s)) for _ in range(64)]
        self.assertEqual([str(p) for p in picks], self.g["extract_full"])
        self.assertEqual(sorted(picks), list(range(64)))
        self.assertEqual(int(s[0]), 0)


class TestPrngEquidistribution(unittest.TestCase):
    """
    The statistical properties of the sequence itself: the
    per-bit balance, the chi-square on the top-bit bins, and the
    choice-64 uniformity (deterministic, the fixed seed 42).
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


class TestChooseOneFromSet64(unittest.TestCase):
    """
    choose_one_from_set64: the uniform NO-REMOVAL pick from a 64-bit
    set. It returns (1 << p, p) for a random set bit p; it never
    mutates the set; the empty set is the (0, 64) sentinel (no draw
    is consumed).
    """

    # At least 3 distinct seeds (robust against a seed-specific fluke).
    SEEDS = [42, 7, 93]

    # The 7 golden cases: (section, seed, set, the set's bit count).
    # One full set + three distinct 2-bit sets + three distinct
    # 3-bit sets.
    CASES = [
        ("choose_full",   42, 0xFFFFFFFFFFFFFFFF, 64),
        ("choose_2bit_a", 42, (1 << 0) | (1 << 63),        2),
        ("choose_2bit_b",  7, (1 << 3) | (1 << 7),         2),
        ("choose_2bit_c", 93, (1 << 16) | (1 << 48),       2),
        ("choose_3bit_d", 42, (1 << 0) | (1 << 1) | (1 << 63),   3),
        ("choose_3bit_e",  7, (1 << 5) | (1 << 10) | (1 << 20),  3),
        ("choose_3bit_f", 93, (1 << 7) | (1 << 32) | (1 << 55),  3),
    ]

    @classmethod
    def setUpClass(cls):
        cls.g = _load_golden()

    @staticmethod
    def _bits(set64):
        # The sorted positions of the set bits of set64.
        return sorted(i for i in range(64) if (int(set64) >> i) & 1)

    # -- the empty set: the (0, 64) sentinel, no draw consumed --------

    def test_empty_set_is_the_sentinel_and_consumes_nothing(self):
        # The empty set returns the (0, 64) sentinel and the stream
        # position is untouched: the next value equals a fresh
        # instance's first value. Checked over 3 seeds.
        for seed in self.SEEDS:
            g = MT19937(seed)
            h = MT19937(seed)
            val, p = g.choose_one_from_set64(np.uint64(0))
            self.assertEqual(int(val), 0)
            self.assertEqual(int(p), 64)
            self.assertEqual(g.get_uint64(), h.get_uint64())

    # -- the return shape: (1 << p, p), p a set bit --------------------

    def test_the_return_is_the_single_bit_at_position_p(self):
        # For a non-empty set the returned value is exactly the single
        # bit at the returned position p, and p is a set bit of the
        # input. 3 seeds x 4 sets x 20 picks.
        sets = [
            0xFFFFFFFFFFFFFFFF,
            (1 << 0) | (1 << 63),
            (1 << 3) | (1 << 7),
            (1 << 5) | (1 << 10) | (1 << 20),
        ]
        for seed in self.SEEDS:
            g = MT19937(seed)
            for s in sets:
                for _ in range(20):
                    val, p = g.choose_one_from_set64(np.uint64(s))
                    self.assertEqual(int(val), 1 << int(p))
                    self.assertTrue(s & (1 << int(p)))

    # -- the no-removal contract --------------------------------------

    def test_the_set_is_never_mutated(self):
        # Unlike extract_from_set64, the set is only READ: after many
        # picks it still holds all its bits (it is never drained) and
        # every pick is one of them. 3 seeds x 100 picks.
        s = 0x5555555555555555  # 32 set bits
        for seed in self.SEEDS:
            g = MT19937(seed)
            for _ in range(100):
                val, p = g.choose_one_from_set64(np.uint64(s))
                self.assertTrue(s & (1 << int(p)))
            self.assertEqual(int(s).bit_count(), 32)

    # -- the 1000-pick golden + the expected frequencies --------------

    def test_the_1000_pick_golden_and_expected_frequencies(self):
        # Each of the 7 cases (the full set + the 3 two-bit + the 3
        # three-bit sets) is replayed for 1000 picks: the exact
        # position sequence matches the committed golden, and the
        # observed frequencies match the golden's expected
        # frequencies (the uniform spread over the set's bits).
        for section, seed, set64, nbits in self.CASES:
            g = MT19937(seed)
            positions = [
                int(g.choose_one_from_set64(np.uint64(set64))[1])
                for _ in range(1000)
            ]
            # (a) The exact 1000-pick sequence is the golden.
            self.assertEqual([str(p) for p in positions], self.g[section])
            # (b) The observed frequencies are the golden's expected
            #     ones, and they cover exactly the set's bits.
            freq = {}
            for p in positions:
                freq[p] = freq.get(p, 0) + 1
            expected = {}
            for tok in self.g[section + "_freqs"][0].split():
                pos, cnt = tok.split(":")
                expected[int(pos)] = int(cnt)
            self.assertEqual(freq, expected)
            self.assertEqual(sorted(freq), self._bits(set64))

    # -- the full set: a reasonable equi-distribution ------------------

    def test_the_full_set_is_reasonably_equidistributed(self):
        # A large sample (200k picks) from the full 64-bit set: the
        # 64 positions are each hit ~3125 times (200k / 64), and the
        # chi-square over the 64 bins stays far below the ~3.7-sigma
        # threshold for df = 63 — the pick is uniform over the set.
        N = 200000
        g = MT19937(42)
        obs = np.zeros(64, dtype=np.int64)
        for _ in range(N):
            _, p = g.choose_one_from_set64(np.uint64(0xFFFFFFFFFFFFFFFF))
            obs[int(p)] += 1
        expected = N / 64.0
        chi2 = float(np.sum((obs - expected) ** 2 / expected))
        self.assertLess(chi2, 150.0)


class TestPickOneFromSet64(unittest.TestCase):
    """
    The numba pick kernels: pick_one_from_set64 (the scalar
    kernel — the single source of the pick technique, shared by
    choose_one_from_set64 / extract_from_set64) and
    pick_one_from_set64_batch (the vectorized form). The identity
    pin: on identical streams the kernels and the class methods
    agree draw-for-draw.
    """

    SETS = [0x1, 0x3, 0xF0, 0xFFFF,
            0x8000000000000001, 0xFFFFFFFFFFFFFFFF,
            0x1248842104812448]

    def test_scalar_kernel_matches_the_method(self):
        # For every set and 100 draws: two identical streams — the
        # method consumes one draw, the kernel gets the same value
        # explicitly; the (bitboard, index) results agree
        # bit-for-bit.
        for s in self.SETS:
            m = MT19937(93)
            k = MT19937(93)
            for _ in range(100):
                d = k.get_uint64()
                bb_k, p_k = pick_one_from_set64(np.uint64(s), d)
                bb_m, p_m = m.choose_one_from_set64(np.uint64(s))
                self.assertEqual(int(bb_k), int(bb_m))
                self.assertEqual(int(p_k), int(p_m))

    def test_batch_kernel_matches_the_method(self):
        # A mixed batch (with empty sets): the batch kernel on a
        # fresh stream is bit-identical to the sequential method
        # loop — and the streams stay aligned afterwards.
        sets = np.array([0x1, 0, 0xF0, 0xFFFF, 0,
                         0xFFFFFFFFFFFFFFFF, 0x1248842104812448],
                        dtype=np.uint64)
        needs = sets != 0
        slots = np.cumsum(needs, dtype=np.int64) - needs.astype(np.int64)
        m = MT19937(93)
        seq = [m.choose_one_from_set64(np.uint64(s)) for s in sets]
        k = MT19937(93)
        draws = k.get_uint64_batch(int(np.count_nonzero(needs)))
        out = pick_one_from_set64_batch(sets, draws, slots)
        for i in range(len(sets)):
            self.assertEqual(int(out[i]), int(seq[i][0]))
        self.assertEqual(int(m.get_uint64()), int(k.get_uint64()))

    def test_batch_all_empty_sets(self):
        # All-empty sets: every element is the pass signal (0) and
        # no draw is consumed (the draws array is empty; the stream
        # stays aligned with a fresh generator's first draw).
        sets = np.zeros(5, dtype=np.uint64)
        slots = np.zeros(5, dtype=np.int64)
        k = MT19937(93)
        out = pick_one_from_set64_batch(sets, k.get_uint64_batch(0),
                                        slots)
        self.assertTrue(np.array_equal(out, np.zeros(5, dtype=np.uint64)))
        m = MT19937(93)
        self.assertEqual(int(k.get_uint64()), int(m.get_uint64()))


if __name__ == '__main__':
    unittest.main()
