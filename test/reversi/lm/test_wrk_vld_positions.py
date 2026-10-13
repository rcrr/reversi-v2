#
# test_wrk_vld_positions.py
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

#
# How to run the wrk_vld_positions unit tests.
#
# Run from the workspace root (the directory containing .venv and src).
#
# -0- Activate the environment.
#
# $ source .venv/bin/activate
#
# -1- Run the tests (a live regab DB is required; LONG=1 for the TestLMWorkerVldPositions class;
# SKIP_REGAB_DB=1 skips the DB-gated tests as in test_regab, see test.reversi.tags).
#
# time python3 -m unittest test.reversi.lm.test_wrk_vld_positions
#

import unittest
import tempfile
from types import SimpleNamespace

import numpy as np
import numpy.testing as nptest
import pandas as pd

from unittest.mock import patch
from io import StringIO
from pathlib import Path

from reversi.tools import binio
from reversi.tools.state_machine import Verbosity
from reversi.lm.logistic_model import LogisticModel, LMContext
from reversi.lm.wrk_positions import wrk_positions_is_cache_consistent
from reversi.lm.wrk_vld_positions import wrk_vld_positions
from reversi.regab import (RegabDBConnection, RegabDataSet,
                           regab_store_data_set_to_file)
from reversi.board import make_position
from test.reversi.paths import CUSTOM_TMP_BASE, WORKSPACE_ROOT
from test.reversi.tags import db_gate, db_long_gate, tier_long


class TestLMWorkerVldPositions(unittest.TestCase):
    """Tests for the VLD_POSITIONS worker basic movements and cache interactions."""

    @classmethod
    def setUpClass(cls):
        CUSTOM_TMP_BASE.mkdir(parents=True, exist_ok=True)

    def setUp(self):
        # The SKIP_REGAB_DB gate, as in test_regab — all the tests need the live regab DB (the setUp
        # moves to GENERATE, which runs the whole positions chain on a fresh base dir).
        db_long_gate(self)  # the SKIP_REGAB_DB + LONG gates

        # Patch stdout to keep test output clean and capture logs
        self.patcher_stdout = patch('sys.stdout', new=StringIO())
        self.mock_stdout = self.patcher_stdout.start()

        # TemporaryDirectory created FIRST so a mid-setup failure still leaves a cleanable temp dir.
        self._tmp = tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE))
        self.tmp_dir = Path(self._tmp.name)
        self.json_config = str(WORKSPACE_ROOT / "test" / "reversi" / "data" / "rlm_02.json")

        # Instance 1: will populate the cache
        self.rlm = LogisticModel(self.json_config,
                                 verbosity=Verbosity.HIGH,
                                 base_dir_override=self.tmp_dir)

        self.assertEqual(self.rlm.current_step, 0)
        self.assertEqual(self.rlm.current_worker_name, 'CREATED')

        # Move to GENERATE first, as VLD_POSITIONS sits after it in the pipeline.
        self.rlm.move_to_step('GENERATE')
        self.assertEqual(self.rlm.current_step, 12)
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
        self.assertEqual(self.rlm.current_step, 13)
        self.assertEqual(self.rlm.current_worker_name, 'VLD_POSITIONS')

        # Verify the cache files were actually created on disk (the rlmwf_13 slot — the flat closure
        # {prefix}{level:02}_{worker_name}.dat)
        cache_file = Path(self.tmp_dir) / 'rlmwf_13_VLD_POSITIONS.dat'
        checksum_file = Path(self.tmp_dir) / 'rlmwf_13_VLD_POSITIONS.dat.SHA3-256'
        self.assertTrue(cache_file.exists(), "Cache .dat file was not created.")
        self.assertTrue(checksum_file.exists(), "Checksum file was not created.")
        self.assertTrue(binio.verify_sha3_256_sidecar(cache_file))

        # Check logs to confirm the extraction was executed
        logs = self.mock_stdout.getvalue()
        self.assertIn("Executing heavy computation", logs)

        # Verify the context was updated (the rlm_02 validation golden: bid [8], status CMS+CMR, the
        # shared ec 20 → 200 positions)
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
        self.assertEqual(self.rlm.current_step, 13)

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
        self.assertEqual(rlm2.current_step, 13)

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

        self.rlm.move_to_step(12)
        self.assertEqual(self.rlm.current_step, 12)
        self.assertEqual(self.rlm.current_worker_name, 'GENERATE')
        self.assertIsNone(self.rlm.context.vld_positions)
        self.assertIsNone(self.rlm.context.vld_game_values)
        self.assertIsNone(self.rlm.context.vld_rds_checksum)
        self.assertIsNone(self.rlm.context.vld_pop_stats)


class TestIsCacheConsistentOverride(unittest.TestCase):
    """
    Unit semantics of the VLD_POSITIONS wrk_positions_is_cache_consistent override (no DB — runs
    under SKIP_REGAB_DB=1): the 6 branches of the probe's D2-D7. SimpleNamespace stand-ins for the
    context and the cached rds. The worker must pass the validation bid/status explicitly (a bare
    call compares against the TRAINING params).
    """

    def _ctx(self):
        """
        An rlm_02-shaped context: training bid [6, 7] / ["CMR", "CMS"], validation bid [8] / ["CMS",
        "CMR"], shared ec 20, tst_regab @ localhost:5432.
        """
        conn = SimpleNamespace(dbname="tst_regab", user="tst_regab",
                               host="localhost", port=5432, password="x")
        vld = SimpleNamespace(bid=[8], status=["CMS", "CMR"])
        regab = SimpleNamespace(regab_db_connection=conn, bid=[6, 7],
                                status=["CMR", "CMS"], ec=20)
        cfg = SimpleNamespace(regab_data_set=regab, validation_data_set=vld,
                              empty_count=20)
        return SimpleNamespace(cfg=cfg, log_event=lambda rel, msg: None)

    def _rds(self, bid=[8], status=["CMS", "CMR"], ec=20, host="localhost"):
        conn = SimpleNamespace(dbname="tst_regab", user="tst_regab",
                               host=host, port="5432", password="x")
        return SimpleNamespace(rc=conn, bid=bid, status=status, ec=ec)

    def test_full_match_is_consistent(self):
        self.assertIs(wrk_positions_is_cache_consistent(self._ctx(), self._rds(),
                                          bid=[8], status=["CMS", "CMR"]), True)

    def test_bid_mismatch_is_inconsistent(self):
        self.assertIs(wrk_positions_is_cache_consistent(self._ctx(), self._rds(),
                                          bid=[6, 7], status=["CMS", "CMR"]), False)

    def test_status_mismatch_is_inconsistent(self):
        self.assertIs(wrk_positions_is_cache_consistent(self._ctx(), self._rds(),
                                          bid=[8], status=["CMS"]), False)

    def test_ec_mismatch_is_inconsistent(self):
        """The shared ec (the root empty_count) is the gate."""
        self.assertIs(wrk_positions_is_cache_consistent(self._ctx(), self._rds(ec=22),
                                          bid=[8], status=["CMS", "CMR"]), False)

    def test_connection_mismatch_is_inconsistent(self):
        self.assertIs(wrk_positions_is_cache_consistent(self._ctx(), self._rds(host="otherhost"),
                                          bid=[8], status=["CMS", "CMR"]), False)

    def test_no_override_uses_training_cfg(self):
        """
        No override -> the TRAINING cfg params are used (they differ from the vld rds -> False): the
        worker must pass bid/status explicitly.
        """
        self.assertIs(wrk_positions_is_cache_consistent(self._ctx(), self._rds()), False)


class TestVldIndependenceCheck(unittest.TestCase):
    """
    The validation independence check (log-only): how many validation records are also in the
    training set. No threshold, no quality gate, no raise (0% and 100% both traced).
    """

    @classmethod
    def setUpClass(cls):
        CUSTOM_TMP_BASE.mkdir(parents=True, exist_ok=True)

    def setUp(self):
        # The SKIP_REGAB_DB gate — the train chain runs on the live regab DB (the vld extraction too).
        db_gate(self)  # the SKIP_REGAB_DB gate

        self.patcher_stdout = patch('sys.stdout', new=StringIO())
        self.mock_stdout = self.patcher_stdout.start()

        # TemporaryDirectory created FIRST so a mid-setup failure still leaves a cleanable temp dir.
        self._tmp = tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE))
        self.tmp_dir = Path(self._tmp.name)

    def _machine(self, fixture: str) -> LogisticModel:
        rlm = LogisticModel(str(WORKSPACE_ROOT / "test" / "reversi" / "data" /
                                fixture),
                            verbosity=Verbosity.HIGH,
                            base_dir_override=self.tmp_dir)
        # VLD_POSITIONS sits after GENERATE in the pipeline: the whole train chain must have
        # populated ctx.positions.
        rlm.move_to_step('GENERATE')
        self.assertEqual(rlm.current_step, 12)
        return rlm

    def tearDown(self):
        if getattr(self, 'patcher_stdout', None) is not None:
            self.patcher_stdout.stop()
        if getattr(self, '_tmp', None) is not None:
            self._tmp.cleanup()

    def test_zero_overlap_is_traced(self):
        """
        rlm_02: train bid 6,7 / vld bid 8 — the production fixtures are disjoint: 0 of 200, no
        action (the chain continues).
        """
        if not tier_long():
            self.skipTest('LONG tier: LONG=1 required (D-532: the slow sibling stays tiered)')
        rlm = self._machine('rlm_02.json')
        rlm.move_to_step('VLD_POSITIONS')
        self.assertEqual(len(rlm.context.vld_positions), 200)
        logs = self.mock_stdout.getvalue()
        self.assertIn(
            "Validation independence check: [OVERLAP: 0 of 200 validation records], [PERCENT: 0.00%] — "
            "records present in both the validation and the training data sets (log only, no action).", logs)

    def test_full_overlap_is_traced_not_raised(self):
        """
        rlm_00: train and vld are the same bid 8 extraction — 100% overlap is TRACED, not raised
        (the check is log-only).
        """
        rlm = self._machine('rlm_00.json')
        rlm.move_to_step('VLD_POSITIONS')
        self.assertEqual(len(rlm.context.vld_positions), 200)
        logs = self.mock_stdout.getvalue()
        self.assertIn(
            "Validation independence check: [OVERLAP: 200 of 200 validation records], [PERCENT: 100.00%] — "
            "records present in both the validation and the training data sets (log only, no action).", logs)


class TestVldWorkerDbFree(unittest.TestCase):
    """
    DB-free worker-level pins for the VLD_POSITIONS _up/_down (no DB — runs under
    SKIP_REGAB_DB=1): a REAL LMContext stand-in (Worker.up is @validate_call-gated) with an
    rlm_02-shaped cfg (the TestIsCacheConsistentOverride._ctx shape) and the REAL cache flow
    against real files (regab_store_data_set_to_file / regab_load_data_set_from_file — pure file
    I/O). The compute path and the cache-hit shortcut are exercised with stubbed
    wrk_positions_extract_and_prepare / cache_manager_load_or_compute, so no DB is ever opened.
    """

    @classmethod
    def setUpClass(cls):
        CUSTOM_TMP_BASE.mkdir(parents=True, exist_ok=True)

    def setUp(self):
        # TemporaryDirectory created FIRST so a mid-setup failure still leaves a cleanable temp dir.
        self._tmp = tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE))
        self.tmp_dir = Path(self._tmp.name)
        self.events = []

    def tearDown(self):
        if getattr(self, '_tmp', None) is not None:
            self._tmp.cleanup()

    def _ctx(self, positions) -> LMContext:
        """
        The shared stand-in: the rlm_02 shape (training bid [6, 7] / ["CMR", "CMS"], validation
        bid [8] / ["CMS", "CMR"], shared ec 20, tst_regab @ localhost:5432), use_cache True, the
        cache path pinned to the rlmwf_13 slot, ~10 synthetic training positions, a capturing
        log_event.
        """
        conn = SimpleNamespace(dbname="tst_regab", user="tst_regab",
                               host="localhost", port=5432, password="x")
        vld = SimpleNamespace(bid=[8], status=["CMS", "CMR"])
        regab = SimpleNamespace(regab_db_connection=conn, bid=[6, 7],
                                status=["CMR", "CMS"], ec=20)
        ctx = LMContext(config_file_path=Path("dummy.json"))
        ctx.cfg = SimpleNamespace(regab_data_set=regab, validation_data_set=vld,
                                  empty_count=20, regab_allow_duplicate=True)
        ctx.use_cache = True
        ctx.get_cache_file_full_path_for_current_level = (
            lambda: self.tmp_dir / "rlmwf_13_VLD_POSITIONS.dat")
        ctx.positions = positions
        ctx.log_event = lambda rel, msg: self.events.append(msg)
        return ctx

    @staticmethod
    def _rds(n: int, seed: int) -> RegabDataSet:
        """
        A REAL no-DB RegabDataSet (the TestIsCacheConsistent idiom): the cfg-matching connection
        (activate_conn=False) + n synthetic rows with disjoint bitboards and even game values.
        """
        rng = np.random.default_rng(seed)
        mover = rng.integers(0, 2**64, n, dtype=np.uint64)
        full = rng.integers(0, 2**64, n, dtype=np.uint64)
        opponent = full & ~mover
        game_values = (rng.integers(-32, 33, n) * 2).astype(np.int8)
        df = pd.DataFrame({
            'mover': mover.astype(np.int64),
            'opponent': opponent.astype(np.int64),
            'game_value': game_values
        })
        rc = RegabDBConnection("tst_regab", "tst_regab", "localhost", "5432",
                               activate_conn=False)
        return RegabDataSet(rc, [8], ["CMS", "CMR"], 20, df)

    @staticmethod
    def _positions(n: int, seed: int):
        """n synthetic training positions (the make_position rows, disjoint bitboards)."""
        rng = np.random.default_rng(seed)
        mover = rng.integers(0, 2**64, n, dtype=np.uint64)
        full = rng.integers(0, 2**64, n, dtype=np.uint64)
        opponent = full & ~mover
        return make_position(mover, opponent)

    def test_read_cache_hit_db_free(self):
        """
        A pre-seeded cache (a REAL RegabDataSet stored via the real regab_store_data_set_to_file)
        is loaded and validated: no heavy computation, the 10 synthetic rows land on the context,
        the data checksum is published.
        """
        rds = self._rds(10, 1)
        regab_store_data_set_to_file(rds, self.tmp_dir / "rlmwf_13_VLD_POSITIONS.dat")

        ctx = self._ctx(self._positions(10, 99))
        wrk_vld_positions().up(ctx)

        self.assertTrue(any("Cache successfully loaded and validated" in m for m in self.events))
        self.assertFalse(any("Executing heavy computation" in m for m in self.events))
        expected = make_position(rds.df_mogv['mover'].to_numpy(),
                                 rds.df_mogv['opponent'].to_numpy())
        nptest.assert_array_equal(ctx.vld_positions, expected)
        self.assertEqual(len(ctx.vld_positions), 10)
        self.assertEqual(ctx.vld_rds_checksum, rds.compute_sha3_256_hash())

    def test_compute_path_db_free(self):
        """
        Empty cache dir: the compute path runs with a STUBBED extract (the real cache flow does
        the store) — the VLD-specific bid/status override is passed to the extract, the .dat +
        the .SHA3-256 sidecar land on disk and verify, the 50 rows + the population stats are
        published, the population-stats line is logged.
        """
        rds50 = self._rds(50, 2)
        calls = []

        def stub(ctx_arg, *, bid=None, status=None):
            calls.append({'bid': bid, 'status': status})
            return rds50

        ctx = self._ctx(self._positions(10, 99))
        with patch('reversi.lm.wrk_vld_positions.wrk_positions_extract_and_prepare', stub):
            wrk_vld_positions().up(ctx)

        # The VLD-specific override: the validation bid/status, not the training ones.
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]['bid'], [8])
        self.assertEqual(calls[0]['status'], ["CMS", "CMR"])

        self.assertTrue(any("Executing heavy computation" in m for m in self.events))

        cache_file = self.tmp_dir / "rlmwf_13_VLD_POSITIONS.dat"
        checksum_file = self.tmp_dir / "rlmwf_13_VLD_POSITIONS.dat.SHA3-256"
        self.assertTrue(cache_file.exists())
        self.assertTrue(checksum_file.exists())
        self.assertTrue(binio.verify_sha3_256_sidecar(cache_file))

        self.assertEqual(len(ctx.vld_positions), 50)
        self.assertEqual(ctx.vld_pop_stats["count"], 50)
        self.assertTrue(any("Statistical properties of population for validation" in m
                            for m in self.events))

    def test_down_clears_all_vld_attributes(self):
        """
        The _down scope: all FOUR vld attributes are cleared and the "Clearing validation game
        positions" line is emitted (a real LMContext — Worker.down is @validate_call-gated).
        """
        sentinel = object()
        ctx = LMContext(config_file_path=Path("dummy.json"))
        ctx.vld_positions = sentinel
        ctx.vld_game_values = sentinel
        ctx.vld_rds_checksum = sentinel
        ctx.vld_pop_stats = sentinel
        ctx.log_event = lambda rel, msg: self.events.append(msg)

        wrk_vld_positions().down(ctx)

        self.assertIsNone(ctx.vld_positions)
        self.assertIsNone(ctx.vld_game_values)
        self.assertIsNone(ctx.vld_rds_checksum)
        self.assertIsNone(ctx.vld_pop_stats)
        self.assertIn("Clearing validation game positions", "\n".join(self.events))

    def test_independence_trace_both_lines(self):
        """
        The independence trace, DB-free, BOTH endpoints: the cache load is stubbed to a HIT with
        a synthetic 10-record RegabDataSet, then up() is run twice — once with training positions
        DISJOINT from the vld ones (0 of 10 / 0.00%), once with FULL overlap (10 of 10 /
        100.00%) — pinning the exact f-string of the trace line in both cases.
        """
        rds10 = self._rds(10, 3)
        checksum = rds10.compute_sha3_256_hash()

        def stub(**kwargs):
            return True, rds10, checksum

        # Case 1: disjoint training positions → 0 of 10, 0.00%.
        ctx = self._ctx(self._positions(10, 77))
        with patch('reversi.lm.wrk_vld_positions.cache_manager_load_or_compute', stub):
            wrk_vld_positions().up(ctx)
        self.assertIn(
            "Validation independence check: [OVERLAP: 0 of 10 validation records], "
            "[PERCENT: 0.00%] — records present in both the validation and the training "
            "data sets (log only, no action).",
            self.events)

        # Case 2: the training positions ARE the vld positions → 10 of 10, 100.00%.
        vld_positions, _ = rds10.generate_positions_and_game_values()
        self.events.clear()
        ctx = self._ctx(vld_positions)
        with patch('reversi.lm.wrk_vld_positions.cache_manager_load_or_compute', stub):
            wrk_vld_positions().up(ctx)
        self.assertIn(
            "Validation independence check: [OVERLAP: 10 of 10 validation records], "
            "[PERCENT: 100.00%] — records present in both the validation and the training "
            "data sets (log only, no action).",
            self.events)


if __name__ == '__main__':
    unittest.main()
