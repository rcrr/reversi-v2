#
# test_lm_worker_analytics.py
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
# How to run the lm_worker_analytics unit tests.
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
# time python3 -m unittest twolm.test.test_lm_worker_analytics
#

import hashlib
import os
import re
import tempfile
import unittest

from unittest.mock import patch
from io import StringIO
from pathlib import Path

from twolm.state_machine import Verbosity
from twolm.logistic_model import LogisticModel
from twolm.test.paths import WORKSPACE_ROOT, CUSTOM_TMP_BASE


def _masked_report_hash(text):
    """sha3_256 of the report text with the Creation Date masked out.

    The file report embeds datetime.now() — every other byte is
    deterministic, so the date-masked hash is a stable golden.
    """
    masked = re.sub(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", "DATE", text)
    return hashlib.sha3_256(masked.encode("utf-8")).hexdigest()


class TestLMWorkerAnalytics(unittest.TestCase):
    """Tests the ANALYTICS worker integration and exact values using rlm_02.json.

    The ANALYTICS level is pure compute (no cache file — the rlmwf_12 slot
    stays unused), so the training metrics and the reports are recomputed on
    every run; the second-instance test pins that recomputation as
    deterministic.
    """

    def setUp(self):
        # The SKIP_REGAB_DB gate, as in test_regab — the worker tests need
        # the live regab DB (the setUp moves to VALIDATE, which runs the
        # whole 13-level chain on a fresh base dir).
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

        # Move up to VALIDATE to ensure full pipeline consistency
        self.rlm.move_to_step('VALIDATE')
        self.assertEqual(self.rlm.current_step, 12)

    def tearDown(self):
        if getattr(self, 'patcher_stdout', None) is not None:
            self.patcher_stdout.stop()
        if getattr(self, '_tmp', None) is not None:
            self._tmp.cleanup()

    def test_analytics_report_goldens(self):
        """First run to ANALYTICS: the 7-metric dict, the console report,
        the report file and the INFO log lines.

        Goldens: rlm_02 live (the bid [6,7] training model, 199952
        samples), re-derived independently by scratch/verify_analytics.py
        (tier C, 0 mismatches).
        """
        # Pre-state: the ANALYTICS blackboard fields are not set yet.
        self.assertIsNone(self.rlm.context.analytics_report)
        self.assertIsNone(self.rlm.context.train_metrics)

        self.rlm.move_to_step('ANALYTICS')
        self.assertEqual(self.rlm.current_step, 13)
        self.assertEqual(self.rlm.current_worker_name, 'ANALYTICS')

        met = self.rlm.context.train_metrics
        self.assertIsNotNone(met)
        self.assertEqual(set(met), {'train_mae_y', 'train_rmse_y', 'train_loss',
                                    'train_samples', 'pop_mae_y', 'pop_rmse_y',
                                    'pop_loss'})
        self.assertEqual(met['train_mae_y'], 12.346794566613694)
        self.assertEqual(met['train_rmse_y'], 15.58872172931622)
        self.assertEqual(met['train_loss'], 0.00712497066706419)
        self.assertEqual(met['train_samples'], 199952)
        self.assertEqual(met['pop_mae_y'], 21.729816221648974)
        self.assertEqual(met['pop_rmse_y'], 26.40637507956623)
        self.assertEqual(met['pop_loss'], 0.020437248051166534)

        # The console report (header only — no tables, no date) is stored
        # on the context and logged line by line.
        rep = self.rlm.context.analytics_report
        self.assertIsInstance(rep, str)
        self.assertIn("MODEL ANALYTICS REPORT: RGLM (Logistic) - Unit Test 02 (rlm_02.json)", rep)
        self.assertIn("  Total Parameters (W)        : 2,981", rep)
        self.assertIn("  Dense Parameters (K)        : 6,588", rep)
        self.assertIn("Generalization Gap (RMSE)   : -0.13", rep)
        self.assertNotIn("Creation Date", rep)
        self.assertNotIn("PATTERN FEATURE", rep)

        # The complete file report is written to base_dir under the
        # configured name; rlm_02 has no mobility features, so the
        # MOBILITY section is empty, EDGE prints its rows (it is in the
        # detailed_report list) and DIAG3 omits them.
        report_path = self.tmp_dir / "model_analytics_report.txt"
        self.assertTrue(report_path.exists())
        content = report_path.read_text(encoding="utf-8")
        self.assertIn("Creation Date", content)
        self.assertIn("MOBILITY FEATURES DETAILS:", content)
        self.assertNotIn("MOBILITY FEATURE:", content)
        self.assertIn("PATTERN FEATURE: EDGE (fid=0)", content)
        self.assertIn("PATTERN FEATURE: DIAG3 (fid=1)", content)
        self.assertEqual(content.count("(Table rows omitted"), 1)
        self.assertEqual(_masked_report_hash(content),
                         "9b97746c69436fc23fd4f7a06274174d66ed1d0cb8467619b78a409e7f743c66")

        logs = self.mock_stdout.getvalue()
        self.assertIn("Generating model analytics report...", logs)
        self.assertIn("Computing metrics on the training set...", logs)
        self.assertIn("Analytics report saved to ", logs)
        self.assertNotIn("PATTERN FEATURE", logs)

    def test_second_instance_deterministic(self):
        """A second instance on the same base dir recomputes identical metrics
        and reports (ANALYTICS has no cache file) while the 6 cache_manager
        levels hit and the DB is not re-extracted."""
        self.rlm.move_to_step('ANALYTICS')
        met = self.rlm.context.train_metrics
        rep = self.rlm.context.analytics_report
        self.assertIsNotNone(met)

        # Create a completely new instance pointing to the same base dir
        rlm2 = LogisticModel(self.json_config,
                             verbosity=Verbosity.HIGH,
                             base_dir_override=self.tmp_dir)

        # Clear the StringIO buffer to only capture logs from the second run
        self.mock_stdout.seek(0)
        self.mock_stdout.truncate(0)

        rlm2.move_to_step('ANALYTICS')
        self.assertEqual(rlm2.current_step, 13)

        logs = self.mock_stdout.getvalue()
        # The 6 cache_manager levels (POSITIONS, INDEXES, WMAPS, DESIGN_MTR,
        # GENERATE, VLD_POSITIONS) hit; CONFIG and the OPTIMIZE checkpoint
        # have their own load flows; FEATURES / ZED / GRADIENT / VALIDATE /
        # ANALYTICS have no cache file and recompute.
        self.assertEqual(logs.count("Cache successfully loaded and validated"), 6)
        self.assertNotIn("Extracted", logs,
                         "DB was queried even though a valid cache existed.")
        self.assertNotIn("established successfully", logs,
                         "DB connection was opened even though a valid cache existed.")

        # ANALYTICS recomputes from the cached artifacts — deterministic.
        self.assertEqual(rlm2.context.train_metrics, met)
        self.assertEqual(rlm2.context.analytics_report, rep)
        self.assertTrue((self.tmp_dir / "model_analytics_report.txt").exists())

    def test_down_clears_analytics_attributes(self):
        """Pin the _down scope: back to VALIDATE clears train_metrics and
        analytics_report (the report file itself is not removed)."""
        self.rlm.move_to_step('ANALYTICS')
        self.assertIsNotNone(self.rlm.context.train_metrics)
        self.assertIsNotNone(self.rlm.context.analytics_report)

        self.rlm.move_to_step(12)
        self.assertEqual(self.rlm.current_step, 12)
        self.assertEqual(self.rlm.current_worker_name, 'VALIDATE')
        self.assertIsNone(self.rlm.context.train_metrics)
        self.assertIsNone(self.rlm.context.analytics_report)
        # The report file is a base_dir artifact — _down does not unlink it.
        self.assertTrue((self.tmp_dir / "model_analytics_report.txt").exists())


class TestLMWorkerAnalyticsMobility(unittest.TestCase):
    """The mobility-table branch of the file report, using rlm_01.json.

    rlm_01 has the intercept + the LMC mobility feature + the DIAG3 and
    CORE patterns, and its analytics.detailed_report list is ["DIAG3",
    "LMC"] — so the LMC table (65 configuration rows) and the DIAG3 table
    print their rows while CORE omits them. This is the only fixture that
    exercises the mobility table helper end-to-end.
    """

    def setUp(self):
        # The SKIP_REGAB_DB gate, as in test_regab — the worker tests need
        # the live regab DB (the setUp moves to VALIDATE, which runs the
        # whole 13-level chain on a fresh base dir).
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

        # Move up to VALIDATE to ensure full pipeline consistency
        self.rlm.move_to_step('VALIDATE')
        self.assertEqual(self.rlm.current_step, 12)

    def tearDown(self):
        if getattr(self, 'patcher_stdout', None) is not None:
            self.patcher_stdout.stop()
        if getattr(self, '_tmp', None) is not None:
            self._tmp.cleanup()

    def test_mobility_and_pattern_tables(self):
        """First run to ANALYTICS on rlm_01: the training metrics golden,
        the mobility + pattern table structure and the file-report hash.

        Goldens: rlm_01 live (bid [7] training, 10 samples), re-derived
        independently by the campaign probe (0 mismatches).
        """
        self.rlm.move_to_step('ANALYTICS')
        self.assertEqual(self.rlm.current_step, 13)

        met = self.rlm.context.train_metrics
        self.assertIsNotNone(met)
        self.assertEqual(met['train_mae_y'], 9.874833279184258e-05)
        self.assertEqual(met['train_rmse_y'], 0.00013206900478667877)
        self.assertEqual(met['train_loss'], 4.704681197571781e-13)
        self.assertEqual(met['train_samples'], 10)
        self.assertEqual(met['pop_mae_y'], 15.6)
        self.assertEqual(met['pop_rmse_y'], 18.39565166010707)
        self.assertEqual(met['pop_loss'], 0.009125067852437496)

        report_path = self.tmp_dir / "model_analytics_report.txt"
        self.assertTrue(report_path.exists())
        content = report_path.read_text(encoding="utf-8")
        # The LMC table prints its rows (LMC is in the detailed_report
        # list), DIAG3 its rows too, CORE omits them — exactly one
        # omitted-rows line in the whole report.
        self.assertIn("MOBILITY FEATURES DETAILS:", content)
        self.assertIn("MOBILITY FEATURE: LMC (fid=1)", content)
        self.assertIn("PATTERN FEATURE: DIAG3 (fid=2)", content)
        self.assertIn("PATTERN FEATURE: CORE (fid=3)", content)
        self.assertEqual(content.count("(Table rows omitted"), 1)
        self.assertEqual(_masked_report_hash(content),
                         "77fa815ada656152b5f8f893134624d5d023ffc66e9c81e4fcda9a1ecc0c083d")

        logs = self.mock_stdout.getvalue()
        self.assertIn("Optimization Status         : CONVERGED_MIN_GRAD (16 iters)", logs)
        self.assertIn("Generalization Gap (RMSE)   : 27.22", logs)


if __name__ == '__main__':
    unittest.main()
