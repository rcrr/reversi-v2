#
# test_wrk_gradient.py
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
# How to run the wrk_gradient unit tests.
#
# Run from the workspace root (the directory containing .venv and src).
#
# -0- Activate the environment.
#
# $ source .venv/bin/activate
#
# -1- Run the tests (a live regab DB + LONG=1 is required;
#     SKIP_REGAB_DB=1 skips the DB-gated tests as in test_regab;
#     VLONG=1 implies LONG, see test.reversi.tags).
#
# time python3 -m unittest test.reversi.lm.test_wrk_gradient
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

from reversi.tools.state_machine import Verbosity
from reversi.lm.logistic_model import LogisticModel
from reversi.lm.wrk_gradient import wrk_gradient
from test.reversi.paths import WORKSPACE_ROOT, CUSTOM_TMP_BASE
from test.reversi.tags import db_long_gate



class TestLMWorkerGradient(unittest.TestCase):
    """Tests the GRADIENT worker integration and exact values using rlm_02.json."""

    def setUp(self):
        # The SKIP_REGAB_DB gate, as in test_regab —
        # the worker test needs the live regab DB (the setUp moves to
        # ZED, which runs the positions chain on a fresh base dir).
        db_long_gate(self)  # the SKIP_REGAB_DB + LONG gates

        # Patch stdout to keep test output clean, especially for large datasets
        self.patcher_stdout = patch('sys.stdout', new=StringIO())
        self.mock_stdout = self.patcher_stdout.start()

        # TemporaryDirectory created FIRST so a mid-setup failure
        # still leaves a cleanable temp dir.
        self._tmp = tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE))
        self.tmp_dir = Path(self._tmp.name)
        self.json_config = str(WORKSPACE_ROOT / "test" / "reversi" / "data" / "rlm_02.json")

        self.rlm = LogisticModel(self.json_config,
                                 verbosity=Verbosity.LOW,
                                 base_dir_override=self.tmp_dir)

        # Move up to ZED to prepare the full state for GRADIENT
        self.rlm.move_to_step('ZED')
        self.assertEqual(self.rlm.current_step, 9)

    def tearDown(self):
        if getattr(self, 'patcher_stdout', None) is not None:
            self.patcher_stdout.stop()
        if getattr(self, '_tmp', None) is not None:
            self._tmp.cleanup()

    def test_generate_gradient(self):
        ctx = self.rlm.context

        # Before moving to GRADIENT, fg should be None
        self.assertIsNone(ctx.fg)

        # Verify prerequisites are correctly populated by previous steps
        self.assertEqual(ctx.design_matrix.shape, (199952, 8))
        self.assertEqual(len(ctx.w), 2981)

        # Move to GRADIENT
        self.rlm.move_to_step('GRADIENT')
        self.assertEqual(self.rlm.current_step, 10)

        self.assertIsNotNone(ctx.fg)
        self.assertTrue(callable(ctx.fg), "The attribute fg should be callable")

        # Evaluate the function at the initial weights (all zeros)
        f, g = ctx.fg(ctx.w)

        # Assertions on outputs
        expected_f = np.float32(0.02049378)
        nptest.assert_allclose(f, expected_f, rtol=1e-6, atol=1e-7)

        expected_g_0000 = np.float32(3.558e-4)
        nptest.assert_allclose(g[0], expected_g_0000, rtol=1e-4, atol=1e-7)

        expected_g_0001 = np.float32(-2.395e-4)
        nptest.assert_allclose(g[1], expected_g_0001, rtol=1e-4, atol=1e-7)

        expected_g_2980 = np.float32(1.101e-3)
        nptest.assert_allclose(g[2980], expected_g_2980, rtol=1e-4, atol=1e-7)

    def test_down_clears_gradient(self):
        # The _down clearing: from GRADIENT back to ZED, the worker
        # must clear ctx.fg.
        self.rlm.move_to_step('GRADIENT')
        self.assertEqual(self.rlm.current_step, 10)
        self.assertIsNotNone(self.rlm.context.fg)

        self.rlm.move_to_step(9)
        self.assertEqual(self.rlm.current_step, 9)
        self.assertEqual(self.rlm.current_worker_name, 'ZED')
        self.assertIsNone(self.rlm.context.fg)


class TestGradientFlagWiring(unittest.TestCase):
    """The high_performance_fg config flag wiring: the
    GRADIENT worker reads optimization.high_performance_fg and builds
    the matching fg variant. Mock context (no DB)."""

    def _mock_ctx(self, high_performance):
        from reversi.tools.state_machine import Context
        ctx = Context()
        ctx.cfg = SimpleNamespace(
            optimization=SimpleNamespace(high_performance_fg=high_performance),
            stat_model=SimpleNamespace(ridge_regularization=0.01))
        ctx.w = np.zeros(3, dtype=np.float32)
        ctx.design_matrix = np.array([[0, 1], [1, 2], [0, 2]], dtype=np.uint32)
        ctx.z = np.array([0.1, 0.9, 0.5], dtype=np.float32)
        ctx.log_event = lambda *args: None
        ctx.fg = None
        return ctx

    def _up(self, ctx):
        wrk_gradient().up(ctx)

    def test_up_flag_true_builds_hp_variant(self):
        ctx = self._mock_ctx(True)
        self._up(ctx)
        self.assertIsNotNone(ctx.fg)
        self.assertTrue(ctx.fg.high_performance)
        f, g = ctx.fg(ctx.w)
        self.assertEqual(f.dtype, np.float32)
        self.assertEqual(g.dtype, np.float32)

    def test_up_flag_false_builds_classic_variant(self):
        ctx = self._mock_ctx(False)
        self._up(ctx)
        self.assertIsNotNone(ctx.fg)
        self.assertFalse(ctx.fg.high_performance)


if __name__ == '__main__':
    unittest.main()
