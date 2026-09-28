#
# test_hlp_plot.py
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
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; or the implied warranty of
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
# How to run the hlp_plot unit tests.
#
# Run from the workspace root (the directory containing .venv and src).
#
# -0- Activate the environment.
#
# $ source .venv/bin/activate
#
# -1- Run the tests (no DB needed — the pure helpers of the PLOT
#     level: the vocabulary, the R-semantic jitter, the EGV bins,
#     the guarded KDE).
#
# time python3 -m unittest test.reversi.lm.test_hlp_plot
#

import unittest

import numpy as np

from reversi.lm.hlp_plot import (PLOT_NAMES, PLOT_BUILDERS, PLOT_TITLES,
                                  jitter, egv_bins, _kde_curve, PlotStyle)


class TestHlpPlotVocabulary(unittest.TestCase):
    """The plot vocabulary: the seven canonical names, the
    titles, and the name -> builder registry (the single source of
    truth the PlotConfig schema validates against)."""

    def test_names_seven_distinct(self):
        self.assertEqual(len(PLOT_NAMES), 7)
        self.assertEqual(len(set(PLOT_NAMES)), 7)

    def test_builders_cover_names_exactly(self):
        """Every canonical name has exactly one builder, and the
        registry holds no stray name."""
        self.assertEqual(set(PLOT_BUILDERS), set(PLOT_NAMES))

    def test_titles_cover_names_exactly(self):
        self.assertEqual(set(PLOT_TITLES), set(PLOT_NAMES))


class TestHlpPlotJitter(unittest.TestCase):
    """The R jitter semantics: uniform noise in
    [-amount*range/2, +amount*range/2], amount a fraction of the
    data range."""

    def test_bounds_and_spread(self):
        rng = np.random.default_rng(42)
        x = np.linspace(-10.0, 10.0, 1000)
        out = jitter(rng, x, 0.5)
        bound = 0.5 * (x.max() - x.min()) / 2
        self.assertLessEqual(float(np.max(np.abs(out - x))), bound)
        # It actually jitters (a spread of noise values).
        self.assertGreater(np.unique(out - x).size, 100)

    def test_zero_range_is_identity(self):
        rng = np.random.default_rng(42)
        x = np.full(50, 7.0)
        out = jitter(rng, x, 0.7)
        np.testing.assert_array_equal(out, x)


class TestHlpPlotEgvBins(unittest.TestCase):
    """The evaluated-game-value bins (the R round_gv): the fitted
    values rounded to the even step-2 grid."""

    def test_even_grid_and_coverage(self):
        rng = np.random.default_rng(42)
        y_pred = rng.standard_normal(5000) * 20
        unique, inv = egv_bins(y_pred)
        self.assertTrue(np.all(unique % 2 == 0))
        # Every point lands in exactly one bin, near its fitted value.
        self.assertEqual(inv.size, y_pred.size)
        self.assertTrue(np.all(np.abs(unique[inv] - y_pred) <= 1.0))

    def test_known_values(self):
        y_pred = np.array([-0.4, 0.6, 3.2, -2.9, 64.0], dtype=np.float64)
        unique, inv = egv_bins(y_pred)
        self.assertEqual([int(unique[k]) for k in inv],
                         [0, 0, 4, -2, 64])


class TestHlpPlotAxes(unittest.TestCase):
    """The symmetric residual-axis limit: the max absolute
    value rounded UP to the tick step (the "reasonable value"),
    at least one step."""

    def test_rounds_up_to_the_step(self):
        from reversi.lm.hlp_plot import _sym_limit
        self.assertEqual(_sym_limit(np.array([-5.3, 5.3])), 8.0)
        self.assertEqual(_sym_limit(np.array([-16.0, 16.0])), 16.0)
        self.assertEqual(_sym_limit(np.array([-16.1])), 24.0)

    def test_degenerate_inputs(self):
        from reversi.lm.hlp_plot import _sym_limit
        self.assertEqual(_sym_limit(np.zeros(10)), 8.0)
        self.assertEqual(_sym_limit(np.array([np.nan, 3.0])), 8.0)


class TestHlpPlotKde(unittest.TestCase):
    """The guarded Gaussian-kernel density helper."""

    def test_zero_variance_is_flat_zero(self):
        grid = np.linspace(-1.0, 1.0, 64)
        curve = _kde_curve(np.full(100, 3.0), grid, PlotStyle())
        np.testing.assert_array_equal(curve, 0.0)

    def test_curve_shape_and_peak(self):
        rng = np.random.default_rng(42)
        x = rng.standard_normal(2000) * 2
        grid = np.linspace(x.min(), x.max(), 256)
        curve = _kde_curve(x, grid, PlotStyle())
        self.assertEqual(curve.shape, grid.shape)
        self.assertTrue(np.all(np.isfinite(curve)))
        self.assertTrue(np.all(curve >= 0.0))
        # The peak sits near the mean of a symmetric cloud.
        peak_x = float(grid[int(curve.argmax())])
        self.assertLess(abs(peak_x - float(x.mean())), 0.5)


if __name__ == '__main__':
    unittest.main()
