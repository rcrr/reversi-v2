#
# test_lm_worker_validate.py
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
# How to run the lm_worker_validate unit tests.
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
# time python3 -m unittest twolm.test.test_lm_worker_validate
#

import unittest
import os
import tempfile

from unittest.mock import patch
from io import StringIO
from pathlib import Path

from twolm.state_machine import Verbosity
from twolm.logistic_model import LogisticModel
from twolm.test.paths import WORKSPACE_ROOT, CUSTOM_TMP_BASE



class TestLMWorkerValidate(unittest.TestCase):
    """Tests the VALIDATE worker integration and exact values using rlm_02.json.

    The VALIDATE level is pure compute (no cache file — the rlmwf_12 slot
    stays unused), so the metrics are recomputed on every run; the
    second-instance test pins that recomputation as deterministic.
    """

    def setUp(self):
        # The SKIP_REGAB_DB gate, as in test_regab — the worker tests need
        # the live regab DB (the setUp moves to VLD_POSITIONS, which runs
        # the whole training chain on a fresh base dir).
        if os.getenv('SKIP_REGAB_DB', '0') == '1':
            self.skipTest('SKIP_REGAB_DB=1: database tests skipped')

        # Patch stdout to keep test output clean and capture logs
        self.patcher_stdout = patch('sys.stdout', new=StringIO())
        self.mock_stdout = self.patcher_stdout.start()

        # TemporaryDirectory created FIRST so a mid-setup failure
        # still leaves a cleanable temp dir.
        self._tmp = tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE))
        self.tmp_dir = Path(self._tmp.name)
        self.json_config = str(WORKSPACE_ROOT / "src" / "twolm" / "test" / "data" / "rlm_02.json")

        self.rlm = LogisticModel(self.json_config,
                                 verbosity=Verbosity.HIGH,
                                 base_dir_override=self.tmp_dir)

        # Move up to VLD_POSITIONS to ensure full pipeline consistency
        self.rlm.move_to_step('VLD_POSITIONS')
        self.assertEqual(self.rlm.current_step, 11)

    def tearDown(self):
        if getattr(self, 'patcher_stdout', None) is not None:
            self.patcher_stdout.stop()
        if getattr(self, '_tmp', None) is not None:
            self._tmp.cleanup()

    def test_validate_model_goldens(self):
        """First run to VALIDATE: the 7-metric dict + the INFO log lines.

        Goldens: rlm_02 live (bid [8] validation vs the bid [6,7] training
        model), re-derived independently by scratch/verify_validate.py
        (tier C, 0 mismatches).
        """
        self.assertIsNone(self.rlm.context.vld_metrics)

        self.rlm.move_to_step('VALIDATE')
        self.assertEqual(self.rlm.current_step, 12)
        self.assertEqual(self.rlm.current_worker_name, 'VALIDATE')

        met = self.rlm.context.vld_metrics
        self.assertIsNotNone(met)
        self.assertEqual(set(met), {'vld_loss', 'vld_mse_z', 'vld_mae_z',
                                    'vld_mae_y', 'vld_mse_y', 'vld_rmse_y',
                                    'vld_samples'})
        self.assertEqual(met['vld_loss'], 0.00700794393196702)
        self.assertEqual(met['vld_mse_z'], 0.01401588786393404)
        self.assertEqual(met['vld_mae_z'], 0.09311295300722122)
        self.assertEqual(met['vld_mae_y'], 12.161691665649414)
        self.assertEqual(met['vld_mse_y'], 239.10484313964844)
        self.assertEqual(met['vld_rmse_y'], 15.46301555633545)
        self.assertEqual(met['vld_samples'], 200)

        logs = self.mock_stdout.getvalue()
        self.assertIn("Starting model validation...", logs)
        self.assertIn("Computing indexes for validation set...", logs)
        self.assertIn("Computing predictions (forward pass) on validation set...", logs)
        self.assertIn("Validation completed. Loss (MSE/2): 7.00794393e-03", logs)
        self.assertIn("  MSE:      1.4016e-02", logs)
        self.assertIn("  MAE:      9.3113e-02", logs)
        self.assertIn("  MAE(y):   12.16", logs)
        self.assertIn("  RMSE(y):  15.46", logs)
        self.assertIn("  RMSE/MAE: 1.27", logs)

    def test_second_instance_deterministic(self):
        """A second instance on the same base dir recomputes identical metrics
        (VALIDATE has no cache file) while the 6 cache_manager levels hit and
        the DB is not re-extracted."""
        self.rlm.move_to_step('VALIDATE')
        met = self.rlm.context.vld_metrics
        self.assertIsNotNone(met)

        # Create a completely new instance pointing to the same base dir
        rlm2 = LogisticModel(self.json_config,
                             verbosity=Verbosity.HIGH,
                             base_dir_override=self.tmp_dir)

        # Clear the StringIO buffer to only capture logs from the second run
        self.mock_stdout.seek(0)
        self.mock_stdout.truncate(0)

        rlm2.move_to_step('VALIDATE')
        self.assertEqual(rlm2.current_step, 12)

        logs = self.mock_stdout.getvalue()
        # The 6 cache_manager levels (POSITIONS, INDEXES, WMAPS, DESIGN_MTR,
        # GENERATE, VLD_POSITIONS) hit; CONFIG and the OPTIMIZE checkpoint
        # have their own load flows; FEATURES / ZED / GRADIENT / VALIDATE
        # have no cache file and recompute.
        self.assertEqual(logs.count("Cache successfully loaded and validated"), 6)
        self.assertNotIn("Extracted", logs,
                         "DB was queried even though a valid cache existed.")
        self.assertNotIn("established successfully", logs,
                         "DB connection was opened even though a valid cache existed.")

        # VALIDATE recomputes from the cached w_dense — deterministic.
        self.assertEqual(rlm2.context.vld_metrics, met)

    def test_down_clears_vld_metrics(self):
        """Pin the _down scope: back to VLD_POSITIONS clears vld_metrics only."""
        self.rlm.move_to_step('VALIDATE')
        self.assertIsNotNone(self.rlm.context.vld_metrics)

        self.rlm.move_to_step(11)
        self.assertEqual(self.rlm.current_step, 11)
        self.assertEqual(self.rlm.current_worker_name, 'VLD_POSITIONS')
        self.assertIsNone(self.rlm.context.vld_metrics)


if __name__ == '__main__':
    unittest.main()
