#
# test_rlm_gradient.py
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
# How to run the rlm_gradient unit tests.
#
# Run from the workspace root (the directory containing .venv and src).
#
# -0- Activate the environment.
#
# $ source .venv/bin/activate
#
# -1- Run the tests (no live regab DB required — the compute test
#     uses a handcrafted mock context, as in test_hlp_zed).
#
# time python3 -m unittest twolm.test.test_rlm_gradient
#

import unittest
from types import SimpleNamespace

import numpy as np
import numpy.testing as nptest

from twolm.rlm_gradient import rlm_gradient_compute, sigmoid



class TestSigmoid(unittest.TestCase):
    """Tests the sigmoid wrapper in isolation (no DB)."""

    def test_sigmoid_golden(self):
        # sigmoid(x) = 1 / (1 + exp(-x)), re-derived in float64
        # directly (independent of the scipy expit path).
        x = np.array([-1.0, 0.0, 1.0], dtype=np.float32)
        x64 = x.astype(np.float64)
        expected = 1.0 / (1.0 + np.exp(-x64))
        nptest.assert_allclose(sigmoid(x), expected, rtol=1e-6, atol=1e-7)

    def test_sigmoid_symmetry(self):
        # sigmoid(x) + sigmoid(-x) == 1
        x = np.array([-2.0, -0.5, 0.5, 2.0], dtype=np.float32)
        nptest.assert_allclose(sigmoid(x) + sigmoid(-x), 1.0, rtol=1e-6, atol=1e-7)


class TestRLMGradientCompute(unittest.TestCase):
    """Tests rlm_gradient_compute on a handcrafted mock context (no DB)."""

    def _mock_ctx(self, ridge, w, X, z):
        return SimpleNamespace(
            cfg=SimpleNamespace(stat_model=SimpleNamespace(ridge_regularization=ridge)),
            w=np.array(w, dtype=np.float32),
            design_matrix=np.array(X, dtype=np.uint32),
            z=np.array(z, dtype=np.float32))

    def _reference(self, ctx, w):
        # Independent float64 re-derivation of f and g: the hand-rolled
        # sigmoid, the per-row w-INDEX sum, and np.add.at (a different
        # accumulation than the closure's broadcast bincount).
        M, P = ctx.design_matrix.shape
        alpha = ctx.cfg.stat_model.ridge_regularization / M
        w64 = w.astype(np.float64)
        lp = np.sum(w64[ctx.design_matrix], axis=1)
        zh = 1.0 / (1.0 + np.exp(-lp))
        rn = zh - ctx.z.astype(np.float64)
        f_ref = 0.5 * (float(np.dot(rn, rn)) / M + alpha * float(np.dot(w64, w64)))
        dzh_rn = zh * (1.0 - zh) * rn
        g0 = np.zeros(len(ctx.w), dtype=np.float64)
        np.add.at(g0, ctx.design_matrix.ravel(), np.repeat(dzh_rn, P))
        g_ref = g0 / M + alpha * w64
        return f_ref, g_ref

    def test_compute_zero_weights_golden(self):
        # X (M=3, P=2), w (N=3) all zeros, ridge 0:
        # f = 0.5 * mean((0.5 - z)^2) = 0.5 * (0.16 + 0.16 + 0) / 3 = 4/75
        # g = [1/30, 0, -1/30] — each row spreads 0.25 * (0.5 - z[m])
        # over its two cells, divided by M.
        ctx = self._mock_ctx(0.0, [0.0, 0.0, 0.0],
                             [[0, 1], [1, 2], [0, 2]], [0.1, 0.9, 0.5])
        fg = rlm_gradient_compute(ctx)
        f, g = fg(ctx.w)
        nptest.assert_allclose(f, 4 / 75, rtol=1e-6, atol=1e-8)
        nptest.assert_allclose(g, [1 / 30, 0.0, -1 / 30], rtol=1e-6, atol=1e-8)

    def test_compute_nonzero_weights(self):
        # The full math (sigmoid + residual + ridge) at w != 0 against
        # the independent float64 re-derivation.
        ctx = self._mock_ctx(0.03, [0.1, -0.2, 0.05],
                             [[0, 1], [1, 2], [0, 2]], [0.1, 0.9, 0.5])
        fg = rlm_gradient_compute(ctx)
        f, g = fg(ctx.w)
        f_ref, g_ref = self._reference(ctx, ctx.w)
        nptest.assert_allclose(f, f_ref, rtol=1e-5, atol=1e-7)
        nptest.assert_allclose(g, g_ref, rtol=1e-5, atol=1e-7)

    def test_ridge_scaling(self):
        # g(ridge_b) - g(ridge_a) == (b - a) / M * w and
        # f(ridge_b) - f(ridge_a) == 0.5 * (b - a) / M * ||w||^2
        # (the leading 0.5 of the loss) — pins the per-position /M
        # normalization of the ridge term.
        X = [[0, 1], [1, 2], [0, 2]]
        z = [0.1, 0.9, 0.5]
        w = np.array([0.1, -0.2, 0.05], dtype=np.float32)
        f_a, g_a = rlm_gradient_compute(self._mock_ctx(0.01, [0.1, -0.2, 0.05], X, z))(w)
        f_b, g_b = rlm_gradient_compute(self._mock_ctx(0.50, [0.1, -0.2, 0.05], X, z))(w)
        dw = w.astype(np.float64)
        nptest.assert_allclose(g_b - g_a, (0.50 - 0.01) / 3 * dw, rtol=1e-6, atol=1e-9)
        nptest.assert_allclose(f_b - f_a, 0.5 * (0.50 - 0.01) / 3 * float(np.dot(dw, dw)),
                               rtol=1e-6, atol=1e-9)

    def test_minlength_empty_bucket(self):
        # Bucket 2 has no cell: g[2] is the pure ridge term
        # alpha * w[2] = (0.03 / 2) * 0.3 = 0.0045, and g keeps the
        # full (N,) shape regardless of the cell coverage.
        ctx = self._mock_ctx(0.03, [0.1, 0.2, 0.3], [[0, 0], [1, 1]], [0.3, 0.7])
        fg = rlm_gradient_compute(ctx)
        f, g = fg(ctx.w)
        self.assertEqual(g.shape, (3,))
        nptest.assert_allclose(g[2], 0.015 * 0.3, rtol=1e-6, atol=1e-9)

    def test_output_dtypes(self):
        # R1 (D-093): the closure returns (np.float32, NDArray[float32]).
        ctx = self._mock_ctx(0.03, [0.1, -0.2, 0.05],
                             [[0, 1], [1, 2], [0, 2]], [0.1, 0.9, 0.5])
        fg = rlm_gradient_compute(ctx)
        f, g = fg(ctx.w)
        self.assertEqual(f.dtype, np.float32)
        self.assertEqual(g.dtype, np.float32)
        self.assertEqual(g.shape, (3,))

    def test_closure_stateless(self):
        # Two evaluations of the same w must be identical (the
        # pre-allocated buffers must not leak state between calls).
        ctx = self._mock_ctx(0.03, [0.1, -0.2, 0.05],
                             [[0, 1], [1, 2], [0, 2]], [0.1, 0.9, 0.5])
        fg = rlm_gradient_compute(ctx)
        f1, g1 = fg(ctx.w)
        f2, g2 = fg(ctx.w)
        self.assertEqual(f1, f2)
        nptest.assert_array_equal(g1, g2)


if __name__ == '__main__':
    unittest.main()
