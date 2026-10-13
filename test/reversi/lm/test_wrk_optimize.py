#
# test_wrk_optimize.py
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

import hashlib
import tempfile
import unittest
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
import numpy.testing as nptest

from reversi.tools.state_machine import Verbosity, Context
from reversi.lm.logistic_model import LogisticModel
from reversi.lm.hlp_gradient import hlp_gradient_compute
from reversi.lm.hlp_optimize import hlp_optimize_load_checkpoint
from reversi.lm.wrk_optimize import wrk_optimize
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

        # And confirm L-BFGS did NOT run (no per-iteration optimizer logs): "L-BFGS - [" is the
        # actual lbfgs per-iteration marker.
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


class _MockOptimizeCtx(SimpleNamespace, Context):
    """The mock context: SimpleNamespace attribute idiom + the base Context (the Worker.up gate)."""


class TestLMWorkerOptimizeMock(unittest.TestCase):
    """
    The OPTIMIZE worker on a MOCK context (no DB, no pipeline, NORMAL tier): a SimpleNamespace ctx
    (the hlp_optimize _mock_ctx idiom, extended) with the REAL hlp_gradient_compute closure on a
    tiny 3x2 design matrix — a real, if miniature, L-BFGS run. The mock ctx subclasses the base
    Context as well: the Worker.up @validate_call gate requires it.
    """

    # The tiny synthetic problem (the 3x2 idiom): a 3-position, 2-feature-instance design matrix
    # over 3 weights, with targets off the w=0 hyperplane so the run must move the weights.
    DESIGN_MATRIX = np.array([[0, 1],
                              [1, 2],
                              [2, 0]], dtype=np.uint32)
    Z = np.array([0.8, 0.2, 0.6], dtype=np.float32)
    CHECKPOINT_FILE = "checkpoint_optimize.dat"

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE))
        self.base_dir = Path(self._tmp.name)

    def tearDown(self):
        if getattr(self, '_tmp', None) is not None:
            self._tmp.cleanup()

    def _build_ctx(self, max_iters, min_grad, events):
        """Build the mock ctx the OPTIMIZE worker reads (fresh w=zeros, empty event list)."""
        opt_cfg = SimpleNamespace(
            max_iters=max_iters,
            m=5,
            c1=1e-4,
            c2=0.9,
            min_grad=min_grad,
            min_p_fun_decrease=(1e-14, 7),
            log_every_n=0,
            save_every_n=0,
            checkpoint_file=self.CHECKPOINT_FILE)
        cfg = SimpleNamespace(
            base_dir=self.base_dir,
            optimization=opt_cfg,
            stat_model=SimpleNamespace(ridge_regularization=0.01))
        ctx = _MockOptimizeCtx(
            cfg=cfg,
            use_cache=True,
            design_matrix_checksum="dm-checksum",
            zed_checksum="zed-checksum",
            w=np.zeros(3, dtype=np.float32),
            design_matrix=self.DESIGN_MATRIX,
            z=self.Z,
            w_checksum=None,
            opt_info=None,
            log_event=lambda relevance, message: events.append((relevance, message)))
        # The REAL gradient closure (the classic vectorized variant) on the tiny problem.
        ctx.fg = hlp_gradient_compute(ctx)
        return ctx

    def test_optimization_runs_small(self):
        """
        A real tiny L-BFGS: the loss drops from w=0, the weights move, the published w_checksum is
        the SHA3-256 of the final weights, opt_info carries the 5 keys with converged=True, and the
        checkpoint file + its SHA3-256 sidecar exist in base_dir.
        """
        events = []
        ctx = self._build_ctx(max_iters=100, min_grad=(1e-6, 3), events=events)

        initial_f, _ = ctx.fg(ctx.w)

        wrk_optimize().up(ctx)

        final_f, _ = ctx.fg(ctx.w)
        self.assertLess(final_f, initial_f,
                        "The loss should decrease below the w=0 value.")
        self.assertFalse(np.all(ctx.w == 0),
                         "Weights should not be all zeros after optimization.")
        self.assertEqual(ctx.w_checksum,
                         hashlib.sha3_256(ctx.w.tobytes()).hexdigest())
        self.assertEqual(set(ctx.opt_info),
                         {"converged", "reason", "iters", "f", "g_norm"})
        self.assertTrue(ctx.opt_info["converged"])
        checkpoint = self.base_dir / self.CHECKPOINT_FILE
        self.assertTrue(checkpoint.exists(), "checkpoint file missing")
        self.assertTrue(checkpoint.with_name(
            checkpoint.name + ".SHA3-256").exists(), "SHA3-256 sidecar missing")

    def test_max_iters_treated_as_completed_small(self):
        """
        The checkpoint decision (the wrk_optimize disjunction): a checkpoint whose stored gradient
        norm is ABOVE the tolerance (status gate False) but whose iters reached max_iters (the
        second disjunct) is loaded as COMPLETED — run 2 never calls the optimizer.
        """
        # Run 1: a problem that does NOT converge in 10 iterations (min_grad 1e-12 is unreachable
        # in 10 L-BFGS steps) — it stops at MAX_ITERS_REACHED with iters==10.
        events1 = []
        ctx1 = self._build_ctx(max_iters=10, min_grad=(1e-12, 3), events=events1)
        wrk_optimize().up(ctx1)

        checkpoint = self.base_dir / self.CHECKPOINT_FILE
        cp = hlp_optimize_load_checkpoint(checkpoint)
        self.assertEqual(cp["reason"], "MAX_ITERS_REACHED")
        self.assertEqual(cp["iters"], 10)
        self.assertFalse(np.all(cp["w"] == 0),
                         "Checkpoint weights should not be all zeros after 10 iterations.")

        # Run 2: a FRESH ctx, same base dir, IDENTICAL config (the consistency gates pass, the
        # status gate is False) — the completed-checkpoint load must engage.
        events2 = []
        ctx2 = self._build_ctx(max_iters=10, min_grad=(1e-12, 3), events=events2)
        fg_calls = [0]
        inner_fg = ctx2.fg

        def fg_counted(w):
            fg_calls[0] += 1
            return inner_fg(w)

        ctx2.fg = fg_counted

        wrk_optimize().up(ctx2)

        messages = [m for _, m in events2]
        self.assertTrue(any("Checkpoint: optimization already completed." in m
                             for m in messages))
        self.assertTrue(any("Iterations" in m for m in messages))
        # No per-iteration optimizer marker ...
        self.assertNotIn("L-BFGS - [", messages)
        # ... and the STRONGEST form: the fg closure was never even called in run 2.
        self.assertEqual(fg_calls[0], 0)
        # The loaded state: the same weights, the same iters.
        nptest.assert_array_equal(ctx2.w, ctx1.w)
        self.assertEqual(ctx2.opt_info["iters"], 10)

    def test_down_clears_optimize(self):
        """_down clears fg, w_checksum and opt_info; ctx.w is kept."""
        events = []
        ctx = self._build_ctx(max_iters=100, min_grad=(1e-6, 3), events=events)

        wrk_optimize().up(ctx)
        self.assertIsNotNone(ctx.fg)
        self.assertIsNotNone(ctx.w_checksum)
        self.assertIsNotNone(ctx.opt_info)

        w_before = ctx.w.copy()
        wrk_optimize().down(ctx)
        self.assertIsNone(ctx.fg)
        self.assertIsNone(ctx.w_checksum)
        self.assertIsNone(ctx.opt_info)
        nptest.assert_array_equal(ctx.w, w_before)


if __name__ == '__main__':
    unittest.main()
