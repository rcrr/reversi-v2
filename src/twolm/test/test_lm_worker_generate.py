#
# test_lm_worker_generate.py
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
# How to run the lm_worker_generate unit tests.
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
# time python3 -m unittest twolm.test.test_lm_worker_generate
#

import unittest
import os
import tempfile
import hashlib

import numpy as np
import numpy.testing as nptest

from unittest.mock import patch
from io import StringIO
from pathlib import Path

from twolm import binio
from twolm.state_machine import Verbosity
from twolm.logistic_model import LogisticModel
from twolm.test.paths import CUSTOM_TMP_BASE, WORKSPACE_ROOT


class TestLMWorkerGenerate(unittest.TestCase):
    """Tests for the GENERATE worker basic movements and cache interactions."""

    @classmethod
    def setUpClass(cls):
        CUSTOM_TMP_BASE.mkdir(parents=True, exist_ok=True)

    def setUp(self):
        # The SKIP_REGAB_DB gate, as in test_regab — all the tests need the
        # live regab DB (the setUp moves to OPTIMIZE, which runs the whole
        # positions chain on a fresh base dir).
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

        # Instance 1: Will populate the cache
        self.rlm = LogisticModel(self.json_config,
                                 verbosity=Verbosity.HIGH,
                                 base_dir_override=self.tmp_dir)

        self.assertEqual(self.rlm.current_step, 0)
        self.assertEqual(self.rlm.current_worker_name, 'CREATED')

        # Move to OPTIMIZE first, as GENERATE depends on the optimized
        # weights (w + w_checksum) produced there
        self.rlm.move_to_step('OPTIMIZE')
        self.assertEqual(self.rlm.current_step, 9)
        self.assertEqual(self.rlm.current_worker_name, 'OPTIMIZE')

    def tearDown(self):
        if getattr(self, 'patcher_stdout', None) is not None:
            self.patcher_stdout.stop()
        if getattr(self, '_tmp', None) is not None:
            self._tmp.cleanup()

    def test_compute_and_populate_cache(self):
        """First run should compute the dense weights and create the cache file."""
        self.assertIsNone(self.rlm.context.w_dense)
        self.assertIsNone(self.rlm.context.dense_w_checksum)

        self.rlm.move_to_step('GENERATE')
        self.assertEqual(self.rlm.current_step, 10)
        self.assertEqual(self.rlm.current_worker_name, 'GENERATE')

        # Verify cache files were actually created on disk
        cache_file = Path(self.tmp_dir) / 'rlmwf_10_GENERATE.dat'
        checksum_file = Path(self.tmp_dir) / 'rlmwf_10_GENERATE.dat.SHA3-256'
        self.assertTrue(cache_file.exists(), "Cache .dat file was not created.")
        self.assertTrue(checksum_file.exists(), "Checksum file was not created.")
        self.assertTrue(binio.verify_sha3_256_sidecar(cache_file))

        # Check logs to confirm computation was executed
        logs = self.mock_stdout.getvalue()
        self.assertIn("Executing heavy computation", logs)

        # Verify the context was updated (the rlm_02 golden:
        # K = 6588 = 1 (intercept) + 6561 (EDGE) + 27 (DIAG3))
        self.assertEqual(self.rlm.context.w_dense.shape, (6588,))
        self.assertEqual(self.rlm.context.w_dense.dtype, np.float32)
        self.assertEqual(
            self.rlm.context.dense_w_checksum,
            "ec9d65453bb112bf277c79f96a86edfa9468bb01f42a2763cd82d69c5b2b15b4")
        # The duck-typed data checksum is the sha3_256 of the dense bytes
        self.assertEqual(
            hashlib.sha3_256(self.rlm.context.w_dense.tobytes()).hexdigest(),
            self.rlm.context.dense_w_checksum)

    def test_read_cache_on_new_instance(self):
        """A second instance should read from the cache and NOT recompute."""

        # 1. Run the first instance to populate the cache
        self.rlm.move_to_step('GENERATE')
        self.assertEqual(self.rlm.current_step, 10)

        # 2. Create a completely new instance pointing to the same cache directory
        rlm2 = LogisticModel(self.json_config,
                             verbosity=Verbosity.HIGH,
                             base_dir_override=self.tmp_dir)
        rlm2.move_to_step('OPTIMIZE') # Reach the step before GENERATE

        # Clear the StringIO buffer to only capture logs from the second run
        self.mock_stdout.seek(0)
        self.mock_stdout.truncate(0)

        # 3. Move to GENERATE in the second instance
        rlm2.move_to_step('GENERATE')
        self.assertEqual(rlm2.current_step, 10)

        # Check logs to confirm the cache was hit successfully
        logs = self.mock_stdout.getvalue()
        self.assertIn("Cache successfully loaded and validated", logs)

        # And confirm heavy computation was NOT executed
        self.assertNotIn("Executing heavy computation", logs,
                         "The dense weights were recomputed even though a valid cache existed.")

        # Verify the context was updated with the cached data
        nptest.assert_array_equal(rlm2.context.w_dense, self.rlm.context.w_dense)
        self.assertEqual(rlm2.context.dense_w_checksum, self.rlm.context.dense_w_checksum)

    def test_down_clears_generate_attributes(self):
        """The _down worker clears both GENERATE context attributes."""
        self.rlm.move_to_step('GENERATE')
        self.assertIsNotNone(self.rlm.context.w_dense)
        self.assertIsNotNone(self.rlm.context.dense_w_checksum)

        self.rlm.move_to_step(9)
        self.assertEqual(self.rlm.current_step, 9)
        self.assertEqual(self.rlm.current_worker_name, 'OPTIMIZE')
        self.assertIsNone(self.rlm.context.w_dense)
        self.assertIsNone(self.rlm.context.dense_w_checksum)


if __name__ == '__main__':
    unittest.main()
