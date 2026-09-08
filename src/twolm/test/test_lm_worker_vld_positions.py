#
# test_lm_worker_vld_positions.py
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
# How to run the lm_worker_vld_positions unit tests.
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
# time python3 -m unittest twolm.test.test_lm_worker_vld_positions
#

import unittest
import os
import tempfile
from types import SimpleNamespace

import numpy as np
import numpy.testing as nptest

from unittest.mock import patch
from io import StringIO
from pathlib import Path

from reversi.tools import binio
from reversi.tools.state_machine import Verbosity
from twolm.logistic_model import LogisticModel
from twolm.lm_worker_positions import is_cache_consistent
from reversi.test.paths import CUSTOM_TMP_BASE, WORKSPACE_ROOT
from reversi.test.tags import db_long_gate


class TestLMWorkerVldPositions(unittest.TestCase):
    """Tests for the VLD_POSITIONS worker basic movements and cache interactions."""

    @classmethod
    def setUpClass(cls):
        CUSTOM_TMP_BASE.mkdir(parents=True, exist_ok=True)

    def setUp(self):
        # The SKIP_REGAB_DB gate, as in test_regab — all the tests need the
        # live regab DB (the setUp moves to GENERATE, which runs the whole
        # positions chain on a fresh base dir).
        db_long_gate(self)  # the SKIP_REGAB_DB + LONG gates (D-130)

        # Patch stdout to keep test output clean and capture logs
        self.patcher_stdout = patch('sys.stdout', new=StringIO())
        self.mock_stdout = self.patcher_stdout.start()

        # TemporaryDirectory created FIRST so a mid-setup failure
        # still leaves a cleanable temp dir.
        self._tmp = tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE))
        self.tmp_dir = Path(self._tmp.name)
        self.json_config = str(WORKSPACE_ROOT / "src" / "reversi" / "test" / "data" / "rlm_02.json")

        # Instance 1: will populate the cache
        self.rlm = LogisticModel(self.json_config,
                                 verbosity=Verbosity.HIGH,
                                 base_dir_override=self.tmp_dir)

        self.assertEqual(self.rlm.current_step, 0)
        self.assertEqual(self.rlm.current_worker_name, 'CREATED')

        # Move to GENERATE first, as VLD_POSITIONS sits after it in the
        # pipeline (the 11th level, step 11)
        self.rlm.move_to_step('GENERATE')
        self.assertEqual(self.rlm.current_step, 10)
        self.assertEqual(self.rlm.current_worker_name, 'GENERATE')

    def tearDown(self):
        if getattr(self, 'patcher_stdout', None) is not None:
            self.patcher_stdout.stop()
        if getattr(self, '_tmp', None) is not None:
            self._tmp.cleanup()

    def test_compute_and_populate_cache(self):
        """First run should extract the validation data set and create the cache file."""
        self.assertIsNone(self.rlm.context.vld_positions)
        self.assertIsNone(self.rlm.context.vld_game_values)
        self.assertIsNone(self.rlm.context.vld_rds_checksum)
        self.assertIsNone(self.rlm.context.vld_pop_stats)

        self.rlm.move_to_step('VLD_POSITIONS')
        self.assertEqual(self.rlm.current_step, 11)
        self.assertEqual(self.rlm.current_worker_name, 'VLD_POSITIONS')

        # Verify the cache files were actually created on disk (the rlmwf_11
        # slot — the flat closure {prefix}{level:02}_{worker_name}.dat)
        cache_file = Path(self.tmp_dir) / 'rlmwf_11_VLD_POSITIONS.dat'
        checksum_file = Path(self.tmp_dir) / 'rlmwf_11_VLD_POSITIONS.dat.SHA3-256'
        self.assertTrue(cache_file.exists(), "Cache .dat file was not created.")
        self.assertTrue(checksum_file.exists(), "Checksum file was not created.")
        self.assertTrue(binio.verify_sha3_256_sidecar(cache_file))

        # Check logs to confirm the extraction was executed
        logs = self.mock_stdout.getvalue()
        self.assertIn("Executing heavy computation", logs)

        # Verify the context was updated (the rlm_02 validation golden:
        # bid [8], status CMS+CMR, the shared ec 20 → 200 positions)
        self.assertEqual(len(self.rlm.context.vld_positions), 200)
        self.assertEqual(self.rlm.context.vld_positions.dtype.names,
                         ("mover", "opponent"))
        self.assertEqual(self.rlm.context.vld_game_values.ndim, 1)
        self.assertEqual(len(self.rlm.context.vld_game_values), 200)
        self.assertEqual(
            self.rlm.context.vld_rds_checksum,
            "e8087903437d9d42d64499626f5b4426505d3b9538539e19fb8f45dc9c9f4c48")
        self.assertEqual(self.rlm.context.vld_pop_stats["count"], 200)
        self.assertEqual(self.rlm.context.vld_pop_stats["mean"], 3.64)

    def test_read_cache_on_new_instance(self):
        """A second instance should read from the cache and NOT re-extract."""

        # 1. Run the first instance to populate the cache
        self.rlm.move_to_step('VLD_POSITIONS')
        self.assertEqual(self.rlm.current_step, 11)

        # 2. Create a completely new instance pointing to the same cache directory
        rlm2 = LogisticModel(self.json_config,
                             verbosity=Verbosity.HIGH,
                             base_dir_override=self.tmp_dir)
        rlm2.move_to_step('GENERATE')  # Reach the step before VLD_POSITIONS

        # Clear the StringIO buffer to only capture logs from the second run
        self.mock_stdout.seek(0)
        self.mock_stdout.truncate(0)

        # 3. Move to VLD_POSITIONS in the second instance
        rlm2.move_to_step('VLD_POSITIONS')
        self.assertEqual(rlm2.current_step, 11)

        # Check logs to confirm the cache was hit successfully
        logs = self.mock_stdout.getvalue()
        self.assertIn("Cache successfully loaded and validated", logs)

        # And confirm the extraction was NOT executed again
        self.assertNotIn("Executing heavy computation", logs,
                         "The validation data set was re-extracted even though "
                         "a valid cache existed.")

        # Verify the context was updated with the cached data
        nptest.assert_array_equal(rlm2.context.vld_positions,
                                  self.rlm.context.vld_positions)
        self.assertEqual(rlm2.context.vld_rds_checksum,
                         self.rlm.context.vld_rds_checksum)

    def test_down_clears_vld_positions_attributes(self):
        """The _down worker clears all four VLD_POSITIONS context attributes."""
        self.rlm.move_to_step('VLD_POSITIONS')
        self.assertIsNotNone(self.rlm.context.vld_positions)
        self.assertIsNotNone(self.rlm.context.vld_game_values)
        self.assertIsNotNone(self.rlm.context.vld_rds_checksum)
        self.assertIsNotNone(self.rlm.context.vld_pop_stats)

        self.rlm.move_to_step(10)
        self.assertEqual(self.rlm.current_step, 10)
        self.assertEqual(self.rlm.current_worker_name, 'GENERATE')
        self.assertIsNone(self.rlm.context.vld_positions)
        self.assertIsNone(self.rlm.context.vld_game_values)
        self.assertIsNone(self.rlm.context.vld_rds_checksum)
        self.assertIsNone(self.rlm.context.vld_pop_stats)


class TestIsCacheConsistentOverride(unittest.TestCase):
    """Unit semantics of the VLD_POSITIONS is_cache_consistent override.

    The worker reuses lm_worker_positions.is_cache_consistent and
    must pass the validation_data_set bid/status explicitly (the
    no-override call would compare against the TRAINING
    regab_data_set params). SimpleNamespace stand-ins for the
    context and the cached rds — no DB, so this class runs under
    SKIP_REGAB_DB=1 too.

    D-106 step 3 (probe_rules.md §4): converted from the
    verify_vld_positions.py D2-D7 probe."""

    def _ctx(self):
        """An rlm_02-shaped context: training bid [6, 7] /
        ["CMR", "CMS"], validation bid [8] / ["CMS", "CMR"], shared
        ec 20, tst_regab @ localhost:5432."""
        conn = SimpleNamespace(dbname="tst_regab", user="tst_regab",
                               host="localhost", port=5432, password="x")
        vld = SimpleNamespace(bid=[8], status=["CMS", "CMR"])
        regab = SimpleNamespace(regab_db_connection=conn, bid=[6, 7],
                                status=["CMR", "CMS"], ec=20)
        cfg = SimpleNamespace(regab_data_set=regab, validation_data_set=vld)
        return SimpleNamespace(cfg=cfg, log_event=lambda rel, msg: None)

    def _rds(self, bid=[8], status=["CMS", "CMR"], ec=20, host="localhost"):
        conn = SimpleNamespace(dbname="tst_regab", user="tst_regab",
                               host=host, port="5432", password="x")
        return SimpleNamespace(rc=conn, bid=bid, status=status, ec=ec)

    def test_full_match_is_consistent(self):
        self.assertIs(is_cache_consistent(self._ctx(), self._rds(),
                                          bid=[8], status=["CMS", "CMR"]), True)

    def test_bid_mismatch_is_inconsistent(self):
        self.assertIs(is_cache_consistent(self._ctx(), self._rds(),
                                          bid=[6, 7], status=["CMS", "CMR"]), False)

    def test_status_mismatch_is_inconsistent(self):
        self.assertIs(is_cache_consistent(self._ctx(), self._rds(),
                                          bid=[8], status=["CMS"]), False)

    def test_ec_mismatch_is_inconsistent(self):
        """The shared regab_data_set.ec is the gate."""
        self.assertIs(is_cache_consistent(self._ctx(), self._rds(ec=22),
                                          bid=[8], status=["CMS", "CMR"]), False)

    def test_connection_mismatch_is_inconsistent(self):
        self.assertIs(is_cache_consistent(self._ctx(), self._rds(host="otherhost"),
                                          bid=[8], status=["CMS", "CMR"]), False)

    def test_no_override_uses_training_cfg(self):
        """No override -> the TRAINING cfg params are used (they differ
        from the vld rds -> False): the worker must pass bid/status
        explicitly."""
        self.assertIs(is_cache_consistent(self._ctx(), self._rds()), False)


if __name__ == '__main__':
    unittest.main()
