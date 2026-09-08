#
# test_lm_worker_indexes.py
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
# How to run the lm_worker_indexes unit tests.
#
# Run from the workspace root (the directory containing .venv and src).
#
# -0- Activate the environment.
#
# $ source .venv/bin/activate
#
# -1- Run the tests (a live regab DB + LONG=1 is required;
#     SKIP_REGAB_DB=1 skips the DB-gated tests as in test_regab;
#     VLONG=1 implies LONG, D-130).
#
# time python3 -m unittest reversi.test.test_wrk_indexes
#

import unittest
import os
import tempfile

from unittest.mock import patch
from io import StringIO
from pathlib import Path

from reversi.tools.state_machine import Verbosity
from twolm.logistic_model import LogisticModel
from reversi.test.paths import CUSTOM_TMP_BASE, WORKSPACE_ROOT
from reversi.test.tags import db_long_gate


class TestLMWorkerIndexes(unittest.TestCase):
    """Tests for the INDEXES worker basic movements and cache interactions."""

    @classmethod
    def setUpClass(cls):
        CUSTOM_TMP_BASE.mkdir(parents=True, exist_ok=True)

    def setUp(self):
        # T2 (D-084): the SKIP_REGAB_DB gate, as in test_regab —
        # both tests need the live regab DB (the setUp moves to
        # FEATURES, which runs POSITIONS on a fresh base dir).
        db_long_gate(self)  # the SKIP_REGAB_DB + LONG gates (D-130)

        # Patch stdout to keep test output clean and capture logs
        self.patcher_stdout = patch('sys.stdout', new=StringIO())
        self.mock_stdout = self.patcher_stdout.start()

        # TemporaryDirectory created FIRST so a mid-setup failure
        # still leaves a cleanable temp dir.
        self._tmp = tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE))
        self.tmp_dir = Path(self._tmp.name)
        self.json_config = str(WORKSPACE_ROOT / "src" / "reversi" / "test" / "data" / "rlm_00.json")

        # Instance 1: Will populate the cache
        self.rlm = LogisticModel(self.json_config,
                                 verbosity=Verbosity.HIGH,
                                 base_dir_override=self.tmp_dir)

        self.assertEqual(self.rlm.current_step, 0)
        self.assertEqual(self.rlm.current_worker_name, 'CREATED')

        # Move to FEATURES first, as INDEXES depends on the feature_set loaded there
        self.rlm.move_to_step('FEATURES')
        self.assertEqual(self.rlm.current_step, 3)
        self.assertEqual(self.rlm.current_worker_name, 'FEATURES')

    def tearDown(self):
        if getattr(self, 'patcher_stdout', None) is not None:
            self.patcher_stdout.stop()
        if getattr(self, '_tmp', None) is not None:
            self._tmp.cleanup()

    def test_compute_and_populate_cache(self):
        """First run should compute indexes and create the cache file."""
        self.rlm.move_to_step('INDEXES')
        self.assertEqual(self.rlm.current_step, 4)
        self.assertEqual(self.rlm.current_worker_name, 'INDEXES')

        # Verify cache files were actually created on disk
        cache_file = Path(self.tmp_dir) / 'rlmwf_04_INDEXES.dat'
        checksum_file = Path(self.tmp_dir) / 'rlmwf_04_INDEXES.dat.SHA3-256'
        self.assertTrue(cache_file.exists(), "Cache .dat file was not created.")
        self.assertTrue(checksum_file.exists(), "Checksum file was not created.")

        # Check logs to confirm computation was executed
        logs = self.mock_stdout.getvalue()
        self.assertIn("Executing heavy computation", logs)

        # Verify context was updated
        self.assertIsNotNone(self.rlm.context.hlp_indexes)

    def test_read_cache_on_new_instance(self):
        """A second instance should read from the cache and NOT recompute."""

        # 1. Run the first instance to populate the cache
        self.rlm.move_to_step('INDEXES')
        self.assertEqual(self.rlm.current_step, 4)

        # 2. Create a completely new instance pointing to the same cache directory
        rlm2 = LogisticModel(self.json_config,
                             verbosity=Verbosity.HIGH,
                             base_dir_override=self.tmp_dir)
        rlm2.move_to_step('FEATURES') # Reach the step before INDEXES

        # Clear the StringIO buffer to only capture logs from the second run
        self.mock_stdout.seek(0)
        self.mock_stdout.truncate(0)

        # 3. Move to INDEXES in the second instance
        rlm2.move_to_step('INDEXES')
        self.assertEqual(rlm2.current_step, 4)

        # Check logs to confirm Cache was hit successfully
        logs = self.mock_stdout.getvalue()
        self.assertIn("Cache successfully loaded and validated", logs)

        # And confirm heavy computation was NOT executed
        self.assertNotIn("Executing heavy computation", logs, "Indexes were recomputed even though a valid cache existed.")

        # Verify context was updated with cached data
        self.assertIsNotNone(rlm2.context.hlp_indexes)


if __name__ == '__main__':
    unittest.main()

