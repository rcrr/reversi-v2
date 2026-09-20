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
# time PERF=0 python3 -m unittest test.reversi.lm.test_hlp_feature_analysis
#

"""
The analysis-kernels data module (the SHARED kernels of the
SU_ANALYSIS and EFFECT_SIZE levels) NO-DB micro-suite — the
SU / entropy / mutual-information kernels: the hand-computed
toy tables (the uniform / the degenerate / the binary
entropies, the perfect-correlation / the independent mutual
informations, the SU = 1 / 0 / the 0-denominator guard).
"""

import math
import unittest

import numpy as np

from scipy.stats import chi2 as _chi2

from reversi.lm.hlp_feature_analysis import (
    adherence, anova_eta_omega, chi_square_goodness, dispersion,
    entropy, kl_divergence, mutual_information,
    never_observed_audit, symmetric_uncertainty, total_variation)


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
        # The degenerate variables (H_u = H_v = 0): the 0/0
        # guard -> SU = 0.
        self.assertEqual(symmetric_uncertainty(0.0, 0.0, 0.0), 0.0)


class TestDispersion(unittest.TestCase):
    """The per-sub-variable dispersion: K_obs, H,
    H_norm = H / log2(K_obs) (the K_obs <= 1 guard), the
    coverage = K_obs / n_configurations."""

    def test_hand_computed(self):
        # counts = [1, 1, 2, 4] (4 observed, total 8),
        # n_configurations = 8: K_obs = 4, H = 1.75, H_norm =
        # 1.75 / log2 4 = 0.875, coverage = 4 / 8 = 0.5.
        d = dispersion([1, 1, 2, 4], 8)
        self.assertEqual(d['k_obs'], 4)
        self.assertAlmostEqual(d['h'], 1.75, places=12)
        self.assertAlmostEqual(d['h_norm'], 0.875, places=12)
        self.assertAlmostEqual(d['coverage'], 0.5, places=12)

    def test_degenerate(self):
        # counts = [8] (1 observed), n_configurations = 5: K_obs
        # = 1, H = 0, H_norm = 0 (the K_obs <= 1 guard), coverage
        # = 1 / 5 = 0.2.
        d = dispersion([8], 5)
        self.assertEqual(d['k_obs'], 1)
        self.assertAlmostEqual(d['h'], 0.0, places=12)
        self.assertAlmostEqual(d['h_norm'], 0.0, places=12)
        self.assertAlmostEqual(d['coverage'], 0.2, places=12)

    def test_dense_zeros_filtered(self):
        # The dense form (the zero entries are the never-
        # observed within the array): the zeros are filtered.
        d = dispersion([0, 1, 0, 3, 0], 5)
        self.assertEqual(d['k_obs'], 2)
        self.assertAlmostEqual(d['coverage'], 0.4, places=12)


class TestNeverObservedAudit(unittest.TestCase):
    """The never-observed audit: the n_configurations - K_obs
    + the rarity
    profile (the observed codes below each small threshold)."""

    def test_hand_computed(self):
        # counts = [1, 1, 2, 4] (K_obs = 4), n_configurations =
        # 8: never = 4; the rarity (the observed codes below
        # each threshold): t=1 -> 0, t=2 -> 2 (the two 1s),
        # t=5 -> 4 (all), t=10 -> 4, t=100 -> 4.
        a = never_observed_audit([1, 1, 2, 4], 8)
        self.assertEqual(a['k_obs'], 4)
        self.assertEqual(a['never_observed'], 4)
        self.assertEqual(a['rarity'], {1: 0, 2: 2, 5: 4, 10: 4,
                                       100: 4})

    def test_all_observed(self):
        # The full support (K_obs = n_configurations): never = 0.
        a = never_observed_audit([1, 1, 1, 1], 4)
        self.assertEqual(a['never_observed'], 0)

    def test_empty(self):
        # The empty (K_obs = 0): never = n_configurations, the
        # rarity all 0.
        a = never_observed_audit([], 10)
        self.assertEqual(a['k_obs'], 0)
        self.assertEqual(a['never_observed'], 10)
        self.assertEqual(a['rarity'], {1: 0, 2: 0, 5: 0, 10: 0,
                                       100: 0})


class TestAnovaEtaOmega(unittest.TestCase):
    """The one-way ANOVA effect sizes: eta² =
    SS_eff / SS_tot, omega² = (SS_eff - (K-1) MS_err) / (SS_tot
    + MS_err), the K = 1 degeneracy + the K > N ValueError."""

    def test_two_groups(self):
        # groups = [0, 0, 1, 1], values = [1, 3, 2, 4]: ybar
        # 2.5, SS_tot 5.0, SS_eff 1.0, SS_err 4.0. eta² = 0.2,
        # MS_err 2.0, omega² = (1.0 - 1.0) / 7.0 = -0.142857
        # (the null effect — the raw value is reported).
        r = anova_eta_omega([0, 0, 1, 1], [1, 3, 2, 4])
        self.assertEqual(r['k'], 2)
        self.assertEqual(r['n'], 4)
        self.assertAlmostEqual(r['eta2'], 0.2, places=12)
        self.assertAlmostEqual(r['omega2'], -1.0 / 7.0, places=12)

    def test_perfect_separation(self):
        # groups = [0, 0, 0, 1, 1, 1], values = [1, 1, 1, 4, 4,
        # 4]: SS_tot = SS_eff = 13.5, SS_err 0. eta² = 1.0,
        # omega² = 1.0 (the perfect separation).
        r = anova_eta_omega([0, 0, 0, 1, 1, 1],
                           [1, 1, 1, 4, 4, 4])
        self.assertEqual(r['k'], 2)
        self.assertAlmostEqual(r['eta2'], 1.0, places=12)
        self.assertAlmostEqual(r['omega2'], 1.0, places=12)

    def test_single_group(self):
        # The K = 1 degeneracy: by convention eta² = omega² = 0.
        r = anova_eta_omega([0, 0, 0], [1, 2, 3])
        self.assertEqual(r['k'], 1)
        self.assertEqual(r['eta2'], 0.0)
        self.assertEqual(r['omega2'], 0.0)

    def test_k_gt_n(self):
        # The K > N guard: the ValueError (unreachable).
        with self.assertRaises(ValueError):
            anova_eta_omega([0, 1, 2], [1, 2])

    def test_length_mismatch(self):
        # The groups / the values length mismatch: the
        # ValueError.
        with self.assertRaises(ValueError):
            anova_eta_omega([0, 1], [1, 2, 3])


class TestKLDivergence(unittest.TestCase):
    """The KL divergence: in nats, the 0-log-0
    convention, +inf if p(i) > 0 and q(i) = 0."""

    def test_equal(self):
        # p = q: KL = 0.
        self.assertAlmostEqual(kl_divergence([0.5, 0.5],
                                             [0.5, 0.5]), 0.0,
                               places=12)

    def test_known(self):
        # p = [1, 0], q = [0.5, 0.5]: KL = log(1 / 0.5) =
        # log(2) (the 0-term vanishes).
        self.assertAlmostEqual(kl_divergence([1, 0], [0.5, 0.5]),
                               0.6931471805599453, places=12)

    def test_infinite(self):
        # p = [1, 0], q = [0, 1]: p(0) > 0, q(0) = 0 -> +inf
        # (the DB has a code the ideal never shows).
        self.assertEqual(kl_divergence([1, 0], [0, 1]), float('inf'))


class TestTotalVariation(unittest.TestCase):
    """The total variation: 0.5 * sum |p - q|,
    in [0, 1], the robust "how different" number."""

    def test_equal(self):
        # p = q: TV = 0.
        self.assertAlmostEqual(total_variation([0.5, 0.5],
                                              [0.5, 0.5]), 0.0,
                               places=12)

    def test_max(self):
        # p = [1, 0], q = [0, 1]: TV = 0.5 * (1 + 1) = 1.
        self.assertAlmostEqual(total_variation([1, 0],
                                              [0, 1]), 1.0,
                               places=12)

    def test_half(self):
        # p = [0.75, 0.25], q = [0.5, 0.5]: TV = 0.5 * (0.25 +
        # 0.25) = 0.25.
        self.assertAlmostEqual(total_variation([0.75, 0.25],
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
        g = chi_square_goodness([10, 20, 30, 40],
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
        g = chi_square_goodness([1, 2, 3, 40],
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
        r = adherence({0: 10, 1: 20}, {0: 10, 1: 30, 2: 60})
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
        r = adherence({0: 50, 1: 50}, {0: 50, 2: 50})
        self.assertEqual(r['kl'], float('inf'))
        self.assertEqual(r['chi2'], float('inf'))
        self.assertEqual(r['p'], 0.0)
        self.assertLess(r['tv'], 1.0)

    def test_empty(self):
        # The empty DB (or the empty ideal): the nan values.
        r = adherence({}, {0: 10, 1: 10})
        self.assertTrue(math.isnan(r['chi2']))
        self.assertTrue(math.isnan(r['kl']))
        self.assertTrue(math.isnan(r['tv']))


if __name__ == '__main__':
    unittest.main()
