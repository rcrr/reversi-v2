#
# test_hlp_feature_analysis.py
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
# How to run the hlp_feature_analysis module unit tests.
#
# Run from the workspace root (the directory containing .venv and src).
#
# -0- Activate the environment.
#
# $ source .venv/bin/activate
#
# -1- Run the tests.
#
# time PERF=0 python3 -m unittest reversi.test.test_hlp_feature_analysis
#

"""
The FEATURE_ANALYSIS data module (the I-017) NO-DB micro-suite —
the T11 SU / entropy / mutual-information kernels (D-181): the
hand-computed toy tables (the uniform / the degenerate / the
binary entropies, the perfect-correlation / the independent
mutual informations, the SU = 1 / 0 / the 0-denominator guard).
"""

import unittest

import numpy as np

from reversi.lm.hlp_feature_analysis import (
    entropy, mutual_information, symmetric_uncertainty)


class TestEntropy(unittest.TestCase):
    """The Shannon entropy H in bits, the 0-log-0 convention."""

    def test_uniform(self):
        # The uniform 4: H = log2(4) = 2.
        self.assertAlmostEqual(entropy([1, 1, 1, 1]), 2.0, places=12)

    def test_degenerate(self):
        # The single-category (the rest zero): H = 0.
        self.assertAlmostEqual(entropy([4, 0, 0, 0]), 0.0, places=12)

    def test_binary(self):
        # p = [0.25, 0.75]: H = -(0.25 log2 0.25 + 0.75 log2
        # 0.75) = 0.8112781244591328.
        self.assertAlmostEqual(entropy([1, 3]),
                               0.8112781244591328, places=12)

    def test_empty(self):
        # The all-zero / the empty: H = 0 (the n = 0 guard).
        self.assertEqual(entropy([0, 0, 0]), 0.0)
        self.assertEqual(entropy([]), 0.0)


class TestMutualInformation(unittest.TestCase):
    """I(u; v) in bits, the identity I = H(u) + H(v) - H(u, v)."""

    def test_perfect_correlation(self):
        # u == v, 4 positions (u = [0, 0, 1, 1]): the marginals
        # [2, 2] (H = 1 each), the joint (the 2 x 2 grid)
        # [2, 0, 0, 2] (H(u, v) = 1). I = 1 + 1 - 1 = 1.
        I = mutual_information([2, 0, 0, 2], [2, 2], [2, 2])
        self.assertAlmostEqual(I, 1.0, places=12)

    def test_independent(self):
        # u = [0, 0, 1, 1], v = [0, 1, 0, 1] (independent): the
        # marginals [2, 2] (H = 1 each), the joint [1, 1, 1, 1]
        # (H(u, v) = 2). I = 1 + 1 - 2 = 0.
        I = mutual_information([1, 1, 1, 1], [2, 2], [2, 2])
        self.assertAlmostEqual(I, 0.0, places=12)

    def test_non_negative(self):
        # The floating-point rounding of the identity can give a
        # tiny negative — the clamp keeps I >= 0.
        I = mutual_information([2, 0, 0, 2], [2, 2], [2, 2])
        self.assertGreaterEqual(I, 0.0)


class TestSymmetricUncertainty(unittest.TestCase):
    """SU = 2I / (H_u + H_v), in [0, 1], the 0-denominator guard."""

    def test_perfect(self):
        # I = H_u = H_v = 1 (the perfect correlation): SU = 2/2 = 1.
        self.assertAlmostEqual(
            symmetric_uncertainty(1.0, 1.0, 1.0), 1.0, places=12)

    def test_independent(self):
        # I = 0 (the independent): SU = 0.
        self.assertAlmostEqual(
            symmetric_uncertainty(0.0, 1.0, 1.0), 0.0, places=12)

    def test_zero_denominator(self):
        # The degenerate variables (H_u = H_v = 0): the 0/0 guard
        # -> SU = 0 (the ODP-4/ODP-8 close).
        self.assertEqual(symmetric_uncertainty(0.0, 0.0, 0.0), 0.0)


if __name__ == '__main__':
    unittest.main()
