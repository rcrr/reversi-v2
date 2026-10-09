#
# test_wrk_optimize.py
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
# How to run the wrk_optimize unit tests.
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
# time python3 -m unittest test.reversi.lm.test_wrk_optimize
#

import tempfile
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import numpy as np
import numpy.testing as nptest

from reversi.tools.state_machine import Verbosity
from reversi.lm.logistic_model import LogisticModel
from test.reversi.paths import WORKSPACE_ROOT, CUSTOM_TMP_BASE
from test.reversi.tags import db_long_gate


class TestLMWorkerOptimize(unittest.TestCase):
    """Tests the OPTIMIZE worker integration."""

    def setUp(self):
        # The SKIP_REGAB_DB gate, as in test_regab — the worker test needs the live regab DB (the
        # setUp moves to GRADIENT, which runs the positions chain on a fresh base dir).
        db_long_gate(self)  # the SKIP_REGAB_DB + LONG gates

        # Patch stdout to keep test output clean, especially for large datasets
        self.patcher_stdout = patch('sys.stdout', new=StringIO())
        self.mock_stdout = self.patcher_stdout.start()

        # The shared temp-dir idiom: TemporaryDirectory created FIRST under the shared
        # CUSTOM_TMP_BASE, WORKSPACE_ROOT-anchored config.
        self._tmp = tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE))
        self.tmp_dir = Path(self._tmp.name)
        self.json_config = str(WORKSPACE_ROOT / "test" / "reversi" / "data" / "rlm_02.json")

        self.rlm = LogisticModel(self.json_config,
                                 verbosity=Verbosity.HIGH,
                                 base_dir_override=self.tmp_dir)

        # Move to GRADIENT first
        self.rlm.move_to_step('GRADIENT')
        self.assertEqual(self.rlm.current_step, 10)

    def tearDown(self):
        if getattr(self, 'patcher_stdout', None) is not None:
            self.patcher_stdout.stop()
        if getattr(self, '_tmp', None) is not None:
            self._tmp.cleanup()

    def test_optimization_runs(self):
        """Run optimization and verify loss decreases."""
        ctx = self.rlm.context

        # Record initial loss (at w=0)
        initial_f, _ = ctx.fg(ctx.w)

        # Run optimization
        self.rlm.move_to_step('OPTIMIZE')
        self.assertEqual(self.rlm.current_step, 11)

        # Calculate final loss
        final_f, _ = ctx.fg(ctx.w)

        # The optimization should have significantly reduced the loss
        self.assertLess(final_f, initial_f)
        self.assertGreater(np.sum(np.abs(ctx.w)), 0.0, "Weights should not be all zeros after optimization.")

    def test_max_iters_treated_as_completed(self):
        """Test that reaching max iterations is treated as a valid completion and cached."""
        ctx = self.rlm.context

        # Override config to hit max_iters quickly
        ctx.cfg.optimization.max_iters = 10
        ctx.cfg.optimization.log_every_n = 0  # Keep test output clean

        # 1. First run: should run for 10 iterations and stop at MAX_ITERS_REACHED
        self.rlm.move_to_step('OPTIMIZE')
        self.assertEqual(self.rlm.current_step, 11)

        # Weights should be updated and not all zeros
        self.assertFalse(np.all(ctx.w == 0), "Weights should not be all zeros after 10 iterations.")
        weights_from_first_run = ctx.w.copy()

        # 2. Second run: new instance, same directory, same config
        rlm2 = LogisticModel(self.json_config,
                             verbosity=Verbosity.HIGH,
                             base_dir_override=self.tmp_dir)
        rlm2.move_to_step('CONFIG')
        rlm2.context.cfg.optimization.max_iters = 10

        # Clear buffer to capture second run logs
        self.mock_stdout.seek(0)
        self.mock_stdout.truncate(0)

        # Move to OPTIMIZE
        rlm2.move_to_step('OPTIMIZE')

        # Check logs to confirm it loaded from checkpoint instead of running
        logs = self.mock_stdout.getvalue()
        self.assertIn("Checkpoint: optimization already completed.", logs)
        self.assertIn("Iterations", logs)

        # And confirm L-BFGS did NOT run (no per-iteration optimizer logs). "L-BFGS - [" is the
        # actual lbfgs marker — the old "Starting L-BFGS optimization" string was never logged (vacuous).
        self.assertNotIn("L-BFGS - [", logs)

        # Weights must be identical to the first run (loaded from checkpoint)
        nptest.assert_array_equal(rlm2.context.w, weights_from_first_run)

    def test_down_clears_optimize(self):
        """_down clears fg, w_checksum and opt_info; ctx.w is kept."""
        ctx = self.rlm.context

        self.rlm.move_to_step('OPTIMIZE')
        self.assertEqual(self.rlm.current_step, 11)
        self.assertIsNotNone(ctx.fg)
        self.assertIsNotNone(ctx.w_checksum)
        self.assertIsNotNone(ctx.opt_info)

        w_before = ctx.w.copy()
        self.rlm.move_to_step(10)
        self.assertEqual(self.rlm.current_worker_name, 'GRADIENT')
        self.assertIsNone(ctx.fg)
        self.assertIsNone(ctx.w_checksum)
        self.assertIsNone(ctx.opt_info)
        nptest.assert_array_equal(ctx.w, w_before)


if __name__ == '__main__':
    unittest.main()
