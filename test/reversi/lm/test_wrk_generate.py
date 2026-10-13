#
# test_wrk_generate.py
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
# How to run the wrk_generate unit tests.
#
# Run from the workspace root (the directory containing .venv and src).
#
# -0- Activate the environment.
#
# $ source .venv/bin/activate
#
# -1- Run the tests (a live regab DB + LONG=1 is required; SKIP_REGAB_DB=1 skips the DB-gated tests
# as in test_regab; VLONG=1 implies LONG, see test.reversi.tags).
#
# time python3 -m unittest test.reversi.lm.test_wrk_generate
#

import unittest
import tempfile
import hashlib

import numpy as np
import numpy.testing as nptest

from unittest.mock import patch
from io import StringIO
from pathlib import Path
from types import SimpleNamespace

from reversi.tools import binio
from reversi.tools.state_machine import Verbosity
from reversi.lm.logistic_model import LogisticModel
from reversi.lm.wrk_generate import wrk_generate
from reversi.index import ExtendedIndex, Index
from test.reversi.paths import CUSTOM_TMP_BASE, WORKSPACE_ROOT
from test.reversi.tags import db_long_gate


class TestLMWorkerGenerate(unittest.TestCase):
    """Tests for the GENERATE worker basic movements and cache interactions."""

    @classmethod
    def setUpClass(cls):
        CUSTOM_TMP_BASE.mkdir(parents=True, exist_ok=True)

    def setUp(self):
        # The SKIP_REGAB_DB gate, as in test_regab — all the tests need the live regab DB (the setUp
        # moves to OPTIMIZE, which runs the whole positions chain on a fresh base dir).
        db_long_gate(self)  # the SKIP_REGAB_DB + LONG gates

        # Patch stdout to keep test output clean and capture logs
        self.patcher_stdout = patch('sys.stdout', new=StringIO())
        self.mock_stdout = self.patcher_stdout.start()

        # TemporaryDirectory created FIRST so a mid-setup failure still leaves a cleanable temp dir.
        self._tmp = tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE))
        self.tmp_dir = Path(self._tmp.name)
        self.json_config = str(WORKSPACE_ROOT / "test" / "reversi" / "data" / "rlm_02.json")

        # Instance 1: Will populate the cache
        self.rlm = LogisticModel(self.json_config,
                                 verbosity=Verbosity.HIGH,
                                 base_dir_override=self.tmp_dir)

        self.assertEqual(self.rlm.current_step, 0)
        self.assertEqual(self.rlm.current_worker_name, 'CREATED')

        # Move to OPTIMIZE first, as GENERATE depends on the optimized weights (w + w_checksum)
        # produced there
        self.rlm.move_to_step('OPTIMIZE')
        self.assertEqual(self.rlm.current_step, 11)
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
        self.assertEqual(self.rlm.current_step, 12)
        self.assertEqual(self.rlm.current_worker_name, 'GENERATE')

        # Verify cache files were actually created on disk
        cache_file = Path(self.tmp_dir) / 'rlmwf_12_GENERATE.dat'
        checksum_file = Path(self.tmp_dir) / 'rlmwf_12_GENERATE.dat.SHA3-256'
        self.assertTrue(cache_file.exists(), "Cache .dat file was not created.")
        self.assertTrue(checksum_file.exists(), "Checksum file was not created.")
        self.assertTrue(binio.verify_sha3_256_sidecar(cache_file))

        # Check logs to confirm computation was executed
        logs = self.mock_stdout.getvalue()
        self.assertIn("Executing heavy computation", logs)

        # Verify the context was updated (the rlm_02 golden: K = 6588 = 1 (intercept) + 6561 (EDGE)
        # + 27 (DIAG3))
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
        self.assertEqual(self.rlm.current_step, 12)

        # 2. Create a completely new instance pointing to the same cache directory
        rlm2 = LogisticModel(self.json_config,
                             verbosity=Verbosity.HIGH,
                             base_dir_override=self.tmp_dir)
        rlm2.move_to_step('OPTIMIZE')  # Reach the step before GENERATE

        # Clear the StringIO buffer to only capture logs from the second run
        self.mock_stdout.seek(0)
        self.mock_stdout.truncate(0)

        # 3. Move to GENERATE in the second instance
        rlm2.move_to_step('GENERATE')
        self.assertEqual(rlm2.current_step, 12)

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

        self.rlm.move_to_step(11)
        self.assertEqual(self.rlm.current_step, 11)
        self.assertEqual(self.rlm.current_worker_name, 'OPTIMIZE')
        self.assertIsNone(self.rlm.context.w_dense)
        self.assertIsNone(self.rlm.context.dense_w_checksum)


class TestLMWorkerGenerateMock(unittest.TestCase):
    """
    The GENERATE worker exercised directly on a mock context (no DB, no pipeline): the
    load-or-compute cache machinery over the small 3-feature fixture (the 9-dim w_dense, the
    test_hlp_generate shape). UNGATED: it runs in the simple default run.
    """

    @classmethod
    def setUpClass(cls):
        CUSTOM_TMP_BASE.mkdir(parents=True, exist_ok=True)

    def setUp(self):
        # TemporaryDirectory created FIRST so a mid-setup failure still leaves a cleanable temp dir.
        self._tmp = tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE))
        self.tmp_dir = Path(self._tmp.name)

    def tearDown(self):
        if getattr(self, '_tmp', None) is not None:
            self._tmp.cleanup()

    def _mock_ctx(self, events):
        """
        The mock context: a real Context (Worker.up is @validate_call on the base Context type, so
        a SimpleNamespace would be rejected) with the 3-feature fixture, the cache machinery pinned
        at level 12 (GENERATE), and a capturing log_event.
        """
        from reversi.tools.state_machine import Context
        ctx = Context()

        # The cache machinery: the StateMachine cache-path closure, pinned at level 12 (GENERATE).
        ctx.cfg = SimpleNamespace(base_dir=self.tmp_dir, cache_files_prefix='rlmwf_')
        ctx.get_cache_file_full_path_for_current_level = (
            lambda: ctx.cfg.base_dir / Path(f"{ctx.cfg.cache_files_prefix}12_GENERATE.dat"))
        ctx.use_cache = True

        # The 3-feature fixture (the test_hlp_generate shape): Intercept, Pattern (the identity
        # principal map), Mobility -> the 9-dim w_dense.
        ctx.feature_set = SimpleNamespace(
            hash="abc",
            features=[
                SimpleNamespace(name="INT", category=0, n_instances=1, n_configurations=1),
                SimpleNamespace(name="PAT", category=2, n_instances=1, n_configurations=3,
                                ref=SimpleNamespace(convert_to_principal_index=lambda x: x)),
                SimpleNamespace(name="MOB", category=1, n_instances=1, n_configurations=5)
            ])
        ctx.iwmap_feature_offset = np.array([0, 1, 4, 9], dtype=Index)
        ctx.iwmap = np.array([0, -1, 1, 0, -1, 2, -1, 3, -1], dtype=ExtendedIndex)
        ctx.feature_w_ranges = np.array([[-1, 0, 0], [0, 0, 1], [-1, 2, 3]], dtype=ExtendedIndex)
        ctx.wmap = np.array([[1, -1, 3], [1, 1, 10], [2, 1, 5], [2, 3, 5]], dtype=ExtendedIndex)
        ctx.w = np.array([0.5, -0.2, 1.0, 3.0], dtype=np.float32)
        ctx.w_checksum = "abc654"

        # The worker-published attributes.
        ctx.w_dense = None
        ctx.dense_w_checksum = None

        # The capturing log sink: (relevance, message) tuples.
        ctx.log_event = lambda rel, msg: events.append((rel, msg))
        return ctx

    def test_compute_and_populate_cache(self):
        """Empty cache dir: the worker runs the real compute and populates the cache + sidecar."""
        events = []
        ctx = self._mock_ctx(events)
        wrk_generate().up(ctx)

        # The compute path was taken.
        self.assertTrue(any("Executing heavy computation" in msg
                            for _rel, msg in events))

        # The cache files were created on disk and the sidecar verifies.
        cache_file = self.tmp_dir / 'rlmwf_12_GENERATE.dat'
        checksum_file = self.tmp_dir / 'rlmwf_12_GENERATE.dat.SHA3-256'
        self.assertTrue(cache_file.exists(), "Cache .dat file was not created.")
        self.assertTrue(checksum_file.exists(), "Checksum sidecar file was not created.")
        self.assertTrue(binio.verify_sha3_256_sidecar(cache_file))

        # The context was updated with the computed dense weights (the 3-feature fixture: 9-dim).
        self.assertEqual(ctx.w_dense.dtype, np.float32)
        self.assertEqual(ctx.w_dense.shape, (9,))
        # The duck-typed data checksum is the sha3_256 of the dense bytes.
        self.assertEqual(ctx.dense_w_checksum,
                         hashlib.sha3_256(ctx.w_dense.tobytes()).hexdigest())

    def test_read_cache_on_new_instance(self):
        """A fresh ctx over the same cache path + same fixture reads the cache (no recompute)."""
        # 1. The first instance populates the cache.
        events1 = []
        ctx1 = self._mock_ctx(events1)
        wrk_generate().up(ctx1)

        # 2. A fresh instance over the same cache path and the same fixture.
        events2 = []
        ctx2 = self._mock_ctx(events2)
        wrk_generate().up(ctx2)

        # The cache path was taken: validated and loaded, not recomputed.
        self.assertTrue(any("Cache successfully loaded and validated" in msg
                            for _rel, msg in events2))
        self.assertFalse(any("Executing heavy computation" in msg
                              for _rel, msg in events2),
                         "The dense weights were recomputed even though a valid cache existed.")

        # The loaded data matches the first instance's.
        nptest.assert_array_equal(ctx2.w_dense, ctx1.w_dense)
        self.assertEqual(ctx2.dense_w_checksum, ctx1.dense_w_checksum)

    def test_down_clears_generate_attributes(self):
        """The _down worker clears both GENERATE context attributes."""
        events = []
        ctx = self._mock_ctx(events)
        wrk_generate().up(ctx)
        self.assertIsNotNone(ctx.w_dense)
        self.assertIsNotNone(ctx.dense_w_checksum)

        wrk_generate().down(ctx)
        self.assertIsNone(ctx.w_dense)
        self.assertIsNone(ctx.dense_w_checksum)


if __name__ == '__main__':
    unittest.main()
