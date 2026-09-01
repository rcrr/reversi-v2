#
# test_lm_worker_zed.py
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
# How to run the lm_worker_zed unit tests.
#
# Run from the workspace root (the directory containing .venv and src).
#
# -0- Activate the environment.
#
# $ source .venv/bin/activate
#
# -1- Run the tests (a live regab DB is required; SKIP_REGAB_DB=1
#     skips the DB-gated tests, as in test_regab).
#
# time python3 -m unittest twolm.test.test_lm_worker_zed
#

import unittest
import os
import tempfile

import numpy as np
import numpy.testing as nptest

from unittest.mock import patch
from io import StringIO
from pathlib import Path

from twolm.state_machine import Verbosity
from twolm.logistic_model import LogisticModel
from twolm.rlm_zed import zed_fun_factory
from twolm.test.paths import WORKSPACE_ROOT, CUSTOM_TMP_BASE



class TestZedFunFactory(unittest.TestCase):
    """Tests the mathematical zed_fun_factory in isolation."""

    def test_zed_fun_factory(self):
        alpha = 0.02
        y2z, z2y = zed_fun_factory(alpha)

        values = np.array([-64, 0, 6, +64], dtype=np.int8)
        transformed_values = y2z(values)
        expected_transformed_values = np.array([0.02, 0.5, 0.545, 0.98], dtype=np.float32)
        nptest.assert_allclose(expected_transformed_values, transformed_values, rtol=1e-6, atol=1e-7)

        re_transformed_values = z2y(transformed_values)
        nptest.assert_allclose(np.float32(values), re_transformed_values, rtol=1e-6, atol=1e-7)


class TestLMWorkerZed(unittest.TestCase):
    """Tests the ZED worker integration and exact values using rlm_01.json."""

    def setUp(self):
        # T1 (D-091): the SKIP_REGAB_DB gate, as in test_regab —
        # the worker tests need the live regab DB (the setUp moves to
        # DESIGN_MTR, which runs the positions chain on a fresh base dir).
        if os.getenv('SKIP_REGAB_DB', '0') == '1':
            self.skipTest('SKIP_REGAB_DB=1: database tests skipped')

        # Patch stdout to keep test output clean and capture logs
        self.patcher_stdout = patch('sys.stdout', new=StringIO())
        self.mock_stdout = self.patcher_stdout.start()

        # TemporaryDirectory created FIRST so a mid-setup failure
        # still leaves a cleanable temp dir.
        self._tmp = tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE))
        self.tmp_dir = Path(self._tmp.name)
        self.json_config = str(WORKSPACE_ROOT / "src" / "twolm" / "test" / "data" / "rlm_01.json")

        self.rlm = LogisticModel(self.json_config,
                                 verbosity=Verbosity.HIGH,
                                 base_dir_override=self.tmp_dir)

        # Move up to DESIGN_MTR to ensure full pipeline consistency
        self.rlm.move_to_step('DESIGN_MTR')
        self.assertEqual(self.rlm.current_step, 6)

    def tearDown(self):
        if getattr(self, 'patcher_stdout', None) is not None:
            self.patcher_stdout.stop()
        if getattr(self, '_tmp', None) is not None:
            self._tmp.cleanup()

    def test_compute_zed(self):
        self.assertIsNone(self.rlm.context.y2z)
        self.assertIsNone(self.rlm.context.z)

        expected_logit_clipping = 0.03
        logit_clipping = self.rlm.context.cfg.stat_model.logit_clipping
        self.assertEqual(expected_logit_clipping, logit_clipping)

        expected_y = np.array([10, 36, -22, 18, -16, 14, -22, 20, 0, 2], dtype=np.int8)

        # In the new design, game_values is already a numpy array in the context
        y = np.asarray(self.rlm.context.game_values, dtype=np.int8)
        nptest.assert_array_equal(expected_y, y)

        self.rlm.move_to_step('ZED')
        self.assertEqual(self.rlm.current_step, 7)

        self.assertIsNotNone(self.rlm.context.y2z)
        self.assertIsNotNone(self.rlm.context.z)

        self.assertEqual(type(self.rlm.context.z), np.ndarray)
        self.assertEqual(self.rlm.context.z.dtype, np.float32)
        self.assertEqual(self.rlm.context.z.shape, (10,))

        expected_z = np.array([0.5734375,
                               0.764375,
                               0.3384375,
                               0.6321875,
                               0.3825,
                               0.6028125,
                               0.3384375,
                               0.646875,
                               0.5,
                               0.5146875], dtype=np.float32)

        nptest.assert_array_equal(expected_z, self.rlm.context.z)

    def test_down_clears_zed_attributes(self):
        # T5 (D-091): pin the _down clearing (live-verified, probe D12).
        self.rlm.move_to_step('ZED')
        self.assertIsNotNone(self.rlm.context.z)

        self.rlm.move_to_step(6)
        self.assertEqual(self.rlm.current_step, 6)
        self.assertEqual(self.rlm.current_worker_name, 'DESIGN_MTR')
        self.assertIsNone(self.rlm.context.y2z)
        self.assertIsNone(self.rlm.context.z2y)
        self.assertIsNone(self.rlm.context.z)
        self.assertIsNone(self.rlm.context.zed_checksum)


if __name__ == '__main__':
    unittest.main()
