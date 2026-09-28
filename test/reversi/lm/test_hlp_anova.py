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
# How to run the hlp_anova module unit tests.
#
# Run from the workspace root (the directory containing .venv and src).
#
# -0- Activate the environment.
#
# $ source .venv/bin/activate
#
# -1- Run the tests.
#
# time PERF=0 python3 -m unittest test.reversi.lm.test_hlp_anova
#

"""
The ANOVA analysis-kernels data module (the D-298 split:
the SU / entropy / MI / dispersion / never-observed micro-suite
moved to test_hlp_su_analysis) NO-DB micro-suite — the hand-
computed toy tables for the ANOVA effect sizes (the two-groups
eta²/omega², the perfect separation, the K = 1 degeneracy, the
guards) + the adherence trio (the chi-square goodness-of-fit
with the merged tail, the KL 0-log-0 + the +inf disjoint
support, the total variation — the three PRIVATE helpers
called via the module import, the D-290 policy).
"""

import math
import unittest

import numpy as np

from scipy.stats import chi2 as _chi2

from reversi.lm import hlp_anova as hlp_an
from reversi.lm.hlp_anova import hlp_anova_adherence, hlp_anova_eta_omega


class TestAnovaEtaOmega(unittest.TestCase):
    """The one-way ANOVA effect sizes: eta² =
    SS_eff / SS_tot, omega² = (SS_eff - (K-1) MS_err) / (SS_tot
    + MS_err), the K = 1 degeneracy + the K > N ValueError."""

    def test_two_groups(self):
        # groups = [0, 0, 1, 1], values = [1, 3, 2, 4]: ybar
        # 2.5, SS_tot 5.0, SS_eff 1.0, SS_err 4.0. eta² = 0.2,
        # MS_err 2.0, omega² = (1.0 - 1.0) / 7.0 = -0.142857
        # (the null effect — the raw value is reported).
        r = hlp_anova_eta_omega([0, 0, 1, 1], [1, 3, 2, 4])
        self.assertEqual(r['k'], 2)
        self.assertEqual(r['n'], 4)
        self.assertAlmostEqual(r['eta2'], 0.2, places=12)
        self.assertAlmostEqual(r['omega2'], -1.0 / 7.0, places=12)

    def test_perfect_separation(self):
        # groups = [0, 0, 0, 1, 1, 1], values = [1, 1, 1, 4, 4,
        # 4]: SS_tot = SS_eff = 13.5, SS_err 0. eta² = 1.0,
        # omega² = 1.0 (the perfect separation).
        r = hlp_anova_eta_omega([0, 0, 0, 1, 1, 1],
                           [1, 1, 1, 4, 4, 4])
        self.assertEqual(r['k'], 2)
        self.assertAlmostEqual(r['eta2'], 1.0, places=12)
        self.assertAlmostEqual(r['omega2'], 1.0, places=12)

    def test_single_group(self):
        # The K = 1 degeneracy: by convention eta² = omega² = 0.
        r = hlp_anova_eta_omega([0, 0, 0], [1, 2, 3])
        self.assertEqual(r['k'], 1)
        self.assertEqual(r['eta2'], 0.0)
        self.assertEqual(r['omega2'], 0.0)

    def test_k_gt_n(self):
        # The K > N guard: the ValueError (unreachable).
        with self.assertRaises(ValueError):
            hlp_anova_eta_omega([0, 1, 2], [1, 2])

    def test_length_mismatch(self):
        # The groups / the values length mismatch: the
        # ValueError.
        with self.assertRaises(ValueError):
            hlp_anova_eta_omega([0, 1], [1, 2, 3])


class TestKLDivergence(unittest.TestCase):
    """The KL divergence: in nats, the 0-log-0
    convention, +inf if p(i) > 0 and q(i) = 0."""

    def test_equal(self):
        # p = q: KL = 0.
        self.assertAlmostEqual(hlp_an._kl_divergence([0.5, 0.5],
                                             [0.5, 0.5]), 0.0,
                               places=12)

    def test_known(self):
        # p = [1, 0], q = [0.5, 0.5]: KL = log(1 / 0.5) =
        # log(2) (the 0-term vanishes).
        self.assertAlmostEqual(hlp_an._kl_divergence([1, 0], [0.5, 0.5]),
                               0.6931471805599453, places=12)

    def test_infinite(self):
        # p = [1, 0], q = [0, 1]: p(0) > 0, q(0) = 0 -> +inf
        # (the DB has a code the ideal never shows).
        self.assertEqual(hlp_an._kl_divergence([1, 0], [0, 1]), float('inf'))


class TestTotalVariation(unittest.TestCase):
    """The total variation: 0.5 * sum |p - q|,
    in [0, 1], the robust "how different" number."""

    def test_equal(self):
        # p = q: TV = 0.
        self.assertAlmostEqual(hlp_an._total_variation([0.5, 0.5],
                                              [0.5, 0.5]), 0.0,
                               places=12)

    def test_max(self):
        # p = [1, 0], q = [0, 1]: TV = 0.5 * (1 + 1) = 1.
        self.assertAlmostEqual(hlp_an._total_variation([1, 0],
                                              [0, 1]), 1.0,
                               places=12)

    def test_half(self):
        # p = [0.75, 0.25], q = [0.5, 0.5]: TV = 0.5 * (0.25 +
        # 0.25) = 0.25.
        self.assertAlmostEqual(hlp_an._total_variation([0.75, 0.25],
                                              [0.5, 0.5]), 0.25,
                               places=12)


class TestChiSquareGoodness(unittest.TestCase):
    """The chi-square goodness-of-fit: the
    statistic sum (O - E)^2 / E, the p-value (the scipy
    chi2.sf), the merged tail (the E < 5 cells into the "other"
    bin) + the merge count."""

    def test_no_merge(self):
        # observed = [10, 20, 30, 40], expected = [15, 18, 27,
        # 40] (all E >= 5, no merge): chi2 = 25/15 + 4/18 +
        # 9/27 + 0 = 2.222222, df 3, p = 0.527585, merged 0.
        g = hlp_an._chi_square_goodness([10, 20, 30, 40],
                                [15, 18, 27, 40])
        self.assertEqual(g['merged'], 0)
        self.assertAlmostEqual(g['chi2'], 2.2222222222222223,
                               places=12)
        self.assertAlmostEqual(g['p'],
                               float(_chi2.sf(2.2222222222222223,
                                              3)), places=12)

    def test_merged(self):
        # observed = [1, 2, 3, 40], expected = [1.5, 2, 2.5,
        # 40]: the 3 cells with E < 5 are merged into the
        # "other" bin (O 6, E 6); the remaining [40, 6] / [40,
        # 6]: chi2 = 0, df 1, p = 1.0, merged 3.
        g = hlp_an._chi_square_goodness([1, 2, 3, 40],
                                [1.5, 2.0, 2.5, 40])
        self.assertEqual(g['merged'], 3)
        self.assertAlmostEqual(g['chi2'], 0.0, places=12)
        self.assertAlmostEqual(g['p'], 1.0, places=12)


class TestAdherence(unittest.TestCase):
    """The adherence (c) trio: the chi-square
    (the p-value + the merged-tail count), the KL (the 0-log-0),
    the TV (the robust "how different" number)."""

    def test_union_alignment(self):
        # db = {0: 10, 1: 20}, ideal = {0: 10, 1: 30, 2: 60}
        # (the union {0, 1, 2}, the DB missing code 2 -> 0):
        # TV = 0.6, KL = 0.933663 (nats), the chi-square 47.7778
        # (the merged tail: code 0's E = 3 < 5 -> merged 1), the
        # p-value the scipy reference.
        r = hlp_anova_adherence({0: 10, 1: 20}, {0: 10, 1: 30, 2: 60})
        self.assertAlmostEqual(r['tv'], 0.6, places=12)
        self.assertAlmostEqual(r['kl'], 0.9336627322538263,
                               places=10)
        self.assertAlmostEqual(r['chi2'], 47.77777777777778,
                               places=10)
        self.assertEqual(r['merged'], 1)
        self.assertAlmostEqual(r['p'],
                               float(_chi2.sf(47.77777777777778,
                                              2)), places=10)

    def test_infinite_kl(self):
        # The DB has a code the ideal never shows (the ideal
        # missing that code -> 0): the disjoint support. The KL
        # is +inf (the infinite divergence), the chi-square is
        # +inf (the total incompatibility, the p is 0) — the
        # three are aligned, the TV is finite (the robust
        # "how different" number).
        r = hlp_anova_adherence({0: 50, 1: 50}, {0: 50, 2: 50})
        self.assertEqual(r['kl'], float('inf'))
        self.assertEqual(r['chi2'], float('inf'))
        self.assertEqual(r['p'], 0.0)
        self.assertLess(r['tv'], 1.0)

    def test_empty(self):
        # The empty DB (or the empty ideal): the nan values.
        r = hlp_anova_adherence({}, {0: 10, 1: 10})
        self.assertTrue(math.isnan(r['chi2']))
        self.assertTrue(math.isnan(r['kl']))
        self.assertTrue(math.isnan(r['tv']))


if __name__ == '__main__':
    unittest.main()
