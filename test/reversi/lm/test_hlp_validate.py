#
# test_hlp_validate.py
#
# This file is part of the reversi program
# http://github.com/rcrr/reversi-v2
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

# How to run the hlp_validate unit tests.
#
# Run from the workspace root (the directory containing .venv and src).
#
# -0- Activate the environment.
#
# $ source .venv/bin/activate
#
# -1- Run the tests.
#
# time PERF=0 python3 -m unittest test.reversi.lm.test_hlp_validate
#

import unittest
from types import SimpleNamespace

import numpy as np

from reversi.lm.hlp_gradient import sigmoid
from reversi.lm.hlp_validate import LMValidate, hlp_validate_model, hlp_validate_top_outliers


class TestTopOutliers(unittest.TestCase):
    """The k-largest-|residual| index selection (the stable tie keeps the lower index)."""

    def test_descending_magnitude(self):
        rn = np.array([1.0, -5.0, 3.0, -5.0, 0.5])
        self.assertEqual(hlp_validate_top_outliers(rn, 2).tolist(), [1, 3])

    def test_stable_tie_break(self):
        rn = np.array([2.0, 2.0, 1.0])
        self.assertEqual(hlp_validate_top_outliers(rn, 2).tolist(), [0, 1])

    def test_k_larger_than_n_returns_all(self):
        rn = np.array([1.0, 3.0, 2.0])
        self.assertEqual(hlp_validate_top_outliers(rn, 10).tolist(), [1, 2, 0])


class TestValidateModel(unittest.TestCase):
    """The NO-DB mock-ctx idiom: a hand-computed 2-position forward pass (1 feature, 2 instances)."""

    def setUp(self):
        self.indexes = np.array([[1, 4], [2, 5]], dtype=np.uint32)
        self.w_dense = np.array([0.0, 0.1, 0.2, 0.0, 0.3, 0.4], dtype=np.float32)
        y2z = lambda y: (y + 64) / 128.0
        z2y = lambda z: z * 128.0 - 64.0
        self.ctx = SimpleNamespace(
            vld_positions=np.zeros((2, 2), dtype=np.uint64),  # the value is irrelevant: the mock indexes
            vld_game_values=np.array([10, 20], dtype=np.int8),
            feature_set=SimpleNamespace(
                features=[SimpleNamespace(n_instances=2)],
                compute_indexes=lambda pos: self.indexes),
            iwmap_feature_offset=np.array([0, 2], dtype=np.uint32),
            w_dense=self.w_dense,
            y2z=y2z,
            z2y=z2y,
            log_event=lambda rel, msg: None,
        )

    def _hand_computed(self):
        # The f32 forward pass, re-derived in f64 (the 0.1+0.3 / 0.2+0.4 sums, the sigmoid).
        z_pred = np.array([sigmoid(0.1 + 0.3), sigmoid(0.2 + 0.4)])
        vld_z = np.array([(10 + 64) / 128.0, (20 + 64) / 128.0])
        rn_z = z_pred - vld_z
        y_pred = z_pred * 128.0 - 64.0
        rn_y = y_pred - np.array([10.0, 20.0])
        return z_pred, vld_z, rn_z, y_pred, rn_y

    def test_result_type_and_seven_keys(self):
        r = hlp_validate_model(self.ctx)
        self.assertIsInstance(r, LMValidate)
        self.assertEqual(set(r.metrics), {'vld_loss', 'vld_mse_z', 'vld_mae_z', 'vld_mae_y',
                                           'vld_mse_y', 'vld_rmse_y', 'vld_samples'})
        self.assertEqual(r.metrics['vld_samples'], 2)

    def test_z_space_metrics_hand_computed(self):
        r = hlp_validate_model(self.ctx)
        _, _, rn_z, _, _ = self._hand_computed()
        self.assertAlmostEqual(r.metrics['vld_loss'], float(0.5 * np.dot(rn_z, rn_z) / 2), places=5)
        self.assertAlmostEqual(r.metrics['vld_mse_z'], float(np.dot(rn_z, rn_z) / 2), places=5)
        self.assertAlmostEqual(r.metrics['vld_mae_z'], float(np.mean(np.abs(rn_z))), places=5)

    def test_y_space_metrics_hand_computed(self):
        r = hlp_validate_model(self.ctx)
        _, _, _, _, rn_y = self._hand_computed()
        self.assertAlmostEqual(r.metrics['vld_mae_y'], float(np.mean(np.abs(rn_y))), places=5)
        self.assertAlmostEqual(r.metrics['vld_mse_y'], float(np.dot(rn_y, rn_y) / 2), places=5)
        self.assertAlmostEqual(r.metrics['vld_rmse_y'], float(np.sqrt(np.dot(rn_y, rn_y) / 2)), places=5)

    def test_published_series_are_f64(self):
        r = hlp_validate_model(self.ctx)
        self.assertEqual(r.y_pred.dtype, np.float64)
        self.assertEqual(r.rn_y.dtype, np.float64)
        self.assertEqual(r.y_pred.shape, (2,))
        self.assertEqual(r.rn_y.shape, (2,))


if __name__ == "__main__":
    unittest.main()
