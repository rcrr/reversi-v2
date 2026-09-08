#
# test_hlp_zed.py
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
# How to run the hlp_zed unit tests.
#
# Run from the workspace root (the directory containing .venv and src).
#
# -0- Activate the environment.
#
# $ source .venv/bin/activate
#
# -1- Run the tests (no live regab DB required — the compute test
#     uses a handcrafted mock context, as in test_hlp_design_matrix).
#
# time python3 -m unittest reversi.test.test_hlp_zed
#

import unittest
import hashlib
from types import SimpleNamespace

import numpy as np
import numpy.testing as nptest

from pydantic import ValidationError

from reversi.lm.hlp_zed import (LMZed,
                           hlp_zed_compute,
                           zed_fun_factory)



class TestZedFunFactory(unittest.TestCase):
    """Tests the zed_fun_factory math in isolation (no DB)."""

    def test_y2z_golden(self):
        y2z, z2y = zed_fun_factory(0.02)
        values = np.array([-64, 0, 6, 64], dtype=np.int8)
        transformed = y2z(values)
        expected = np.array([0.02, 0.5, 0.545, 0.98], dtype=np.float32)
        self.assertEqual(transformed.dtype, np.float32)
        nptest.assert_allclose(expected, transformed, rtol=1e-6, atol=1e-7)

    def test_z2y_inverse(self):
        y2z, z2y = zed_fun_factory(0.02)
        z = np.array([0.02, 0.5, 0.545, 0.98], dtype=np.float32)
        expected_y = np.array([-64, 0, 6, 64], dtype=np.float32)
        nptest.assert_allclose(expected_y, z2y(z), rtol=1e-6, atol=1e-7)

    def test_round_trip(self):
        y2z, z2y = zed_fun_factory(0.03)
        values = np.array([-64, -22, 0, 18, 63, 64], dtype=np.int8)
        nptest.assert_allclose(z2y(y2z(values)), values.astype(np.float32),
                               rtol=1e-6, atol=1e-7)

    def test_endpoints_for_two_clipplings(self):
        for alpha, lo, hi in ((0.02, 0.02, 0.98), (0.03, 0.03, 0.97)):
            y2z, z2y = zed_fun_factory(alpha)
            self.assertAlmostEqual(float(y2z(np.int8(-64))), lo, places=6)
            self.assertAlmostEqual(float(y2z(np.int8(0))), 0.5, places=6)
            self.assertAlmostEqual(float(y2z(np.int8(64))), hi, places=6)


class TestHlpZedCompute(unittest.TestCase):
    """Tests hlp_zed_compute on a handcrafted mock context (no DB)."""

    def _mock_ctx(self, clipping, values):
        return SimpleNamespace(
            cfg=SimpleNamespace(stat_model=SimpleNamespace(logit_clipping=clipping)),
            game_values=np.array(values, dtype=np.int8))

    def test_compute_golden(self):
        ctx = self._mock_ctx(0.03, [10, 36, -22, 20])
        zed = hlp_zed_compute(ctx)
        self.assertIsInstance(zed, LMZed)
        self.assertTrue(callable(zed.y2z))
        self.assertTrue(callable(zed.z2y))
        # Hand-derived: z = 0.5 + y * (1 - 2*0.03) / 128 — the same
        # float32 literals the rlm_01 pipeline golden pins exactly.
        expected = np.array([0.5734375, 0.764375, 0.3384375, 0.646875],
                            dtype=np.float32)
        self.assertEqual(zed.z.dtype, np.float32)
        self.assertEqual(zed.z.shape, (4,))
        nptest.assert_array_equal(expected, zed.z)

    def test_compute_hash(self):
        ctx = self._mock_ctx(0.03, [10, 36, -22, 20])
        zed = hlp_zed_compute(ctx)
        self.assertEqual(zed.compute_sha3_256_hash(),
                         hashlib.sha3_256(zed.z.tobytes()).hexdigest())


class TestLMZed(unittest.TestCase):
    """Tests the data-object init validation and the hash golden."""

    def _closures(self):
        return zed_fun_factory(0.03)

    def test_init_stores_by_reference(self):
        y2z, z2y = self._closures()
        z = np.array([0.5, 0.51], dtype=np.float32)
        zed = LMZed(y2z=y2z, z2y=z2y, z=z)
        self.assertIs(zed.y2z, y2z)
        self.assertIs(zed.z2y, z2y)
        self.assertIs(zed.z, z)

    def test_init_rejects_invalid_z(self):
        y2z, z2y = self._closures()
        with self.assertRaises(ValidationError):
            LMZed(y2z=y2z, z2y=z2y, z="not_an_array")

    def test_init_rejects_non_callable(self):
        y2z, z2y = self._closures()
        with self.assertRaises(ValidationError):
            LMZed(y2z="not_callable", z2y=z2y,
                                    z=np.array([0.5], dtype=np.float32))

    def test_hash_golden(self):
        # The rlm_01 live golden z (10,) float32 — the pipeline
        # checksum is the sha3_256 of z.tobytes() only.
        z = np.array([0.5734375, 0.764375, 0.3384375, 0.6321875, 0.3825,
                      0.6028125, 0.3384375, 0.646875, 0.5, 0.5146875],
                     dtype=np.float32)
        y2z, z2y = self._closures()
        zed = LMZed(y2z=y2z, z2y=z2y, z=z)
        self.assertEqual(zed.compute_sha3_256_hash(),
                         '3d49fd5d56ced2f7bb70e5c24c8100b3318a7e66e7c990de53ed2f16f365d9b2')


if __name__ == '__main__':
    unittest.main()
