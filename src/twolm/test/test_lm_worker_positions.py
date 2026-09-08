#
# test_lm_worker_positions.py
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
# How to run the lm_worker_positions unit tests.
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
# time python3 -m unittest twolm.test.test_lm_worker_positions
#

import unittest
import os
import tempfile

import json5
import numpy as np
import pandas as pd

from unittest.mock import patch
from io import StringIO
from pathlib import Path

from twolm.state_machine import Verbosity
from twolm.logistic_model import LogisticModel, RLMContext
from twolm.rlm_config_schemas import ReversiLogisticModelConfig
from twolm.regab import RegabDBConnection, RegabDataSet
from twolm.lm_worker_positions import is_cache_consistent
from twolm.test.paths import CUSTOM_TMP_BASE, WORKSPACE_ROOT
from twolm.test.tags import db_long_gate


class TestLMWorkerPositions(unittest.TestCase):
    """Tests for the POSITIONS worker basic movements and DB/Cache interactions."""

    @classmethod
    def setUpClass(cls):
        CUSTOM_TMP_BASE.mkdir(parents=True, exist_ok=True)

    def setUp(self):
        # T2 (D-080): the SKIP_REGAB_DB gate, as in test_regab —
        # both tests need the live regab DB.
        db_long_gate(self)  # the SKIP_REGAB_DB + LONG gates (D-130)

        # Patch stdout to keep test output clean and capture logs
        self.patcher_stdout = patch('sys.stdout', new=StringIO())
        self.mock_stdout = self.patcher_stdout.start()

        # TemporaryDirectory created FIRST so a mid-setup failure
        # still leaves a cleanable temp dir.
        self._tmp = tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE))
        self.tmp_dir = Path(self._tmp.name)
        self.json_config = str(WORKSPACE_ROOT / "src" / "twolm" / "test" / "data" / "rlm_00.json")

        # Instance 1: Will populate the cache
        self.rlm = LogisticModel(self.json_config,
                                 verbosity=Verbosity.HIGH,
                                 base_dir_override=self.tmp_dir)

        self.assertEqual(self.rlm.current_step, 0)
        self.assertEqual(self.rlm.current_worker_name, 'CREATED')
        self.rlm.move_to_step('CONFIG')
        self.assertEqual(self.rlm.current_step, 1)

    def tearDown(self):
        if getattr(self, 'patcher_stdout', None) is not None:
            self.patcher_stdout.stop()
        if getattr(self, '_tmp', None) is not None:
            self._tmp.cleanup()

    def test_read_db_and_populate_cache(self):
        """First run should hit the DB, extract data, and create the cache file."""
        self.rlm.move_to_step('POSITIONS')
        self.assertEqual(self.rlm.current_step, 2)
        self.assertEqual(self.rlm.current_worker_name, 'POSITIONS')

        # Verify cache files were actually created on disk
        cache_file = self.tmp_dir / 'rlmwf_02_POSITIONS.dat'
        checksum_file = self.tmp_dir / 'rlmwf_02_POSITIONS.dat.SHA3-256'
        self.assertTrue(cache_file.exists(), "Cache .dat file was not created.")
        self.assertTrue(checksum_file.exists(), "Checksum file was not created.")

        # Check logs to confirm DB was hit
        logs = self.mock_stdout.getvalue()
        self.assertIn("Extracted", logs)
        self.assertIn("positions from the database.", logs)

    def test_read_cache_on_new_instance(self):
        """A second instance should read from the cache and NOT hit the DB."""

        # 1. Run the first instance to populate the cache
        self.rlm.move_to_step('POSITIONS')
        self.assertEqual(self.rlm.current_step, 2)

        # 2. Create a completely new instance pointing to the same cache directory
        rlm2 = LogisticModel(self.json_config,
                             verbosity=Verbosity.HIGH,
                             base_dir_override=self.tmp_dir)
        rlm2.move_to_step('CONFIG')  # Reach the step before POSITIONS

        # Clear the StringIO buffer to only capture logs from the second run
        self.mock_stdout.seek(0)
        self.mock_stdout.truncate(0)

        # 3. Move to POSITIONS in the second instance
        rlm2.move_to_step('POSITIONS')
        self.assertEqual(rlm2.current_step, 2)

        # Check logs to confirm Cache was hit successfully
        logs = self.mock_stdout.getvalue()
        self.assertIn("Cache successfully loaded and validated", logs)

        # And confirm DB was NOT hit
        self.assertNotIn("Extracted", logs, "DB was queried even though a valid cache existed.")
        self.assertNotIn("established successfully", logs, "DB connection was opened even though a valid cache existed.")


class TestIsCacheConsistent(unittest.TestCase):
    """Unit semantics of lm_worker_positions.is_cache_consistent.

    D-106 step 3 (probe_rules.md §4): converted from the
    verify_lm_worker_positions.py D4a-g probe. The probe warmed a
    real cache file through the live pipeline and compared against
    it; the test builds the same rds metadata in memory (fixture
    rlm_00 values: bid [8], status ["CMS", "CMR"], ec 20,
    tst_regab @ localhost:5432) — no DB, no cache file."""

    def setUp(self):
        self.json_path = (WORKSPACE_ROOT / "src" / "twolm" / "test" /
                          "data" / "rlm_00.json")
        self.rc = RegabDBConnection("tst_regab", "tst_regab", "localhost",
                                    "5432", activate_conn=False)
        self.df = pd.DataFrame({
            'mover': [1, 2],
            'opponent': [3, 4],
            'game_value': [4, 6]
        }).astype({'mover': 'int64', 'opponent': 'int64', 'game_value': 'int8'})
        self.rds = RegabDataSet(self.rc, [8], ["CMS", "CMR"], 20, self.df)

    def _ctx(self, mutate=None) -> RLMContext:
        d = json5.loads(self.json_path.read_text())
        if mutate:
            mutate(d)
        cx = RLMContext(config_file_path=Path("rlm_00.json"))
        cx.cfg = ReversiLogisticModelConfig(**d)
        return cx

    def test_same_cfg_is_consistent(self):
        self.assertIs(is_cache_consistent(self._ctx(), self.rds), True)

    def test_different_ec_is_inconsistent(self):
        def _ec19(d):
            d["regab_data_set"]["ec"] = 19
        self.assertIs(is_cache_consistent(self._ctx(_ec19), self.rds), False)

    def test_different_bid_is_inconsistent(self):
        def _bid9(d):
            d["regab_data_set"]["bid"] = [9]
        self.assertIs(is_cache_consistent(self._ctx(_bid9), self.rds), False)

    def test_different_status_is_inconsistent(self):
        def _st_cms(d):
            d["regab_data_set"]["status"] = ["CMS"]
        self.assertIs(is_cache_consistent(self._ctx(_st_cms), self.rds), False)

    def test_different_dbname_is_inconsistent(self):
        def _dbname(d):
            d["regab_data_set"]["regab_db_connection"]["dbname"] = "other_db"
        self.assertIs(is_cache_consistent(self._ctx(_dbname), self.rds), False)

    def test_keyword_override_wins(self):
        """The bid/status keyword args override the cfg values."""
        self.assertIs(is_cache_consistent(self._ctx(), self.rds,
                                          bid=[9]), False)
        self.assertIs(is_cache_consistent(self._ctx(), self.rds,
                                          bid=[8],
                                          status=["CMS", "CMR"]), True)

    def test_str_port_vs_int_port_compares_equal(self):
        """rds.rc.port is a str ('5432'), the schema port an int:
        the comparison still passes (int coercion on the cache side)."""
        self.assertEqual(self.rds.rc.port, "5432")
        self.assertIs(is_cache_consistent(self._ctx(), self.rds), True)


if __name__ == '__main__':
    unittest.main()
