#
# test_wrk_validate.py
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
# How to run the wrk_validate unit tests.
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
# time python3 -m unittest test.reversi.lm.test_wrk_validate
#

import math
import re
import unittest
import tempfile
from types import SimpleNamespace

import json5
import numpy as np
import pandas as pd

from unittest.mock import patch
from io import StringIO
from pathlib import Path

from reversi.tools.state_machine import Verbosity
from reversi.lm.logistic_model import LogisticModel, LMContext
from reversi.lm.wrk_validate import _down, wrk_validate
from reversi.lm.hlp_validate import LMValidate, hlp_validate_top_outliers, hlp_validate_model
from reversi.lm.hlp_gradient import sigmoid
from reversi.regab import RegabDBConnection, RegabDataSet, regab_store_data_set_to_file
from test.reversi.closecheck import assert_close
from test.reversi.paths import WORKSPACE_ROOT, CUSTOM_TMP_BASE
from test.reversi.tags import db_long_gate
from reversi.board import Position
from reversi.index import ExtendedIndex



class TestLMWorkerValidate(unittest.TestCase):
    """
    Test the VALIDATE worker integration (rlm_02.json): the 7-metric goldens, the log lines, the
    deterministic recompute (no cache file — the rlmwf_14 slot stays unused), and the _down scope.
    """

    def setUp(self):
        # The SKIP_REGAB_DB gate, as in test_regab — the worker tests need the live regab DB (the
        # setUp moves to VLD_POSITIONS, which runs the whole training chain on a fresh base dir).
        db_long_gate(self)  # the SKIP_REGAB_DB + LONG gates

        # Patch stdout to keep test output clean and capture logs
        self.patcher_stdout = patch('sys.stdout', new=StringIO())
        self.mock_stdout = self.patcher_stdout.start()

        # TemporaryDirectory created FIRST so a mid-setup failure still leaves a cleanable temp dir.
        self._tmp = tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE))
        self.tmp_dir = Path(self._tmp.name)
        self.json_config = str(WORKSPACE_ROOT / "test" / "reversi" / "data" / "rlm_02.json")

        self.rlm = LogisticModel(self.json_config,
                                 verbosity=Verbosity.HIGH,
                                 base_dir_override=self.tmp_dir)

        # Move up to VLD_POSITIONS to ensure full pipeline consistency
        self.rlm.move_to_step('VLD_POSITIONS')
        self.assertEqual(self.rlm.current_step, 13)

    def tearDown(self):
        if getattr(self, 'patcher_stdout', None) is not None:
            self.patcher_stdout.stop()
        if getattr(self, '_tmp', None) is not None:
            self._tmp.cleanup()

    def test_hlp_validate_model_goldens(self):
        """
        First run to VALIDATE on rlm_02 (bid [8] vs the bid [6,7] training model): the 7-metric dict
        + the INFO log lines, the goldens derived independently.
        """
        self.assertIsNone(self.rlm.context.vld_metrics)

        self.rlm.move_to_step('VALIDATE')
        self.assertEqual(self.rlm.current_step, 14)
        self.assertEqual(self.rlm.current_worker_name, 'VALIDATE')

        met = self.rlm.context.vld_metrics
        self.assertIsNotNone(met)
        self.assertEqual(set(met), {'vld_loss', 'vld_mse_z', 'vld_mae_z',
                                    'vld_mae_y', 'vld_mse_y', 'vld_rmse_y',
                                    'vld_samples'})
        assert_close(self, met['vld_loss'], 0.00700794393196702, 'vld_loss')
        assert_close(self, met['vld_mse_z'], 0.01401588786393404, 'vld_mse_z')
        assert_close(self, met['vld_mae_z'], 0.09311295300722122, 'vld_mae_z')
        assert_close(self, met['vld_mae_y'], 12.161691665649414, 'vld_mae_y')
        assert_close(self, met['vld_mse_y'], 239.10484313964844, 'vld_mse_y')
        assert_close(self, met['vld_rmse_y'], 15.46301555633545, 'vld_rmse_y')
        self.assertEqual(met['vld_samples'], 200)

        logs = self.mock_stdout.getvalue()
        self.assertIn("Starting model validation...", logs)
        self.assertIn("Computing indexes for validation set...", logs)
        self.assertIn("Computing predictions (forward pass) on validation set...", logs)
        self.assertIn("Validation completed. Loss (MSE/2): 7.00794393e-03", logs)
        self.assertIn("  MSE:      1.4016e-02", logs)
        self.assertIn("  MAE:      9.3113e-02", logs)
        self.assertIn("  MAE(y):   12.16", logs)
        self.assertIn("  RMSE(y):  15.46", logs)
        self.assertIn("  RMSE/MAE: 1.27", logs)

    def test_second_instance_deterministic(self):
        """
        A second instance on the same base dir recomputes identical metrics (VALIDATE has no cache
        file) while the 6 cache_manager levels hit and the DB is not re-extracted.
        """
        self.rlm.move_to_step('VALIDATE')
        met = self.rlm.context.vld_metrics
        self.assertIsNotNone(met)

        # Create a completely new instance pointing to the same base dir
        rlm2 = LogisticModel(self.json_config,
                             verbosity=Verbosity.HIGH,
                             base_dir_override=self.tmp_dir)

        # Clear the StringIO buffer to only capture logs from the second run
        self.mock_stdout.seek(0)
        self.mock_stdout.truncate(0)

        rlm2.move_to_step('VALIDATE')
        self.assertEqual(rlm2.current_step, 14)

        logs = self.mock_stdout.getvalue()
        # The 6 cache_manager levels (POSITIONS, INDEXES, WMAPS, DESIGN_MTR, GENERATE,
        # VLD_POSITIONS) hit; CONFIG and the OPTIMIZE checkpoint have their own load flows; FEATURES
        # / ZED / GRADIENT / VALIDATE have no cache file and recompute.
        self.assertEqual(logs.count("Cache successfully loaded and validated"), 6)
        self.assertNotIn("Extracted", logs,
                         "DB was queried even though a valid cache existed.")
        self.assertNotIn("established successfully", logs,
                         "DB connection was opened even though a valid cache existed.")

        # VALIDATE recomputes from the cached w_dense — deterministic.
        self.assertEqual(rlm2.context.vld_metrics, met)

    def test_down_clears_vld_metrics(self):
        """Pin the _down scope: back to VLD_POSITIONS clears vld_metrics only."""
        self.rlm.move_to_step('VALIDATE')
        self.assertIsNotNone(self.rlm.context.vld_metrics)

        self.rlm.move_to_step(13)
        self.assertEqual(self.rlm.current_step, 13)
        self.assertEqual(self.rlm.current_worker_name, 'VLD_POSITIONS')
        self.assertIsNone(self.rlm.context.vld_metrics)


class TestValidateModelUnit(unittest.TestCase):
    """
    Pin the DB-free unit facts for the VALIDATE metric math.

    The checks pin the metric math directly: the hand-computed 2-position case and the zero-guard
    branch. Runs under SKIP_REGAB_DB=1 (no DB).
    """

    def _fake_ctx(self, game_values, indexes, offsets, w_dense):
        # The y2z/z2y lambdas mirror the zed factory (hlp_zed L80-83/L87-89): the float32 CAST
        # BEFORE the affine (the real y2z does NOT overflow on int8 64 — a raw (y + 64) on int8
        # would wrap to -128).
        return SimpleNamespace(
            vld_positions=np.zeros(len(game_values), dtype=np.uint64),
            vld_game_values=np.asarray(game_values, dtype=np.int8),
            feature_set=SimpleNamespace(
                compute_indexes=lambda p: np.asarray(indexes, dtype=ExtendedIndex),
                features=[SimpleNamespace(n_instances=len(offsets) - 1)]),
            iwmap_feature_offset=np.asarray(offsets, dtype=np.int64),
            w_dense=np.asarray(w_dense, dtype=np.float64),
            y2z=lambda y: (np.float32(y) + 64) / 128,
            z2y=lambda z: 128 * z - 64,
            log_event=lambda rel, msg: None)

    def test_full_metric_math_on_hand_computed_case(self):
        """
        The full metric math on the hand-computed 2-position case, every value EXACT (the full
        derivation in the mirror doc).
        """
        d = hlp_validate_model(self._fake_ctx([0, 64], [[0, 1], [1, 0]],
                                          [0, 2], [0.5, -0.5])).metrics
        self.assertEqual(d["vld_loss"], 0.0625)
        self.assertEqual(d["vld_mse_z"], 0.125)
        self.assertEqual(d["vld_mae_z"], 0.25)
        self.assertEqual(d["vld_mae_y"], 32.0)
        self.assertEqual(d["vld_mse_y"], 2048.0)
        self.assertEqual(d["vld_rmse_y"], math.sqrt(2048.0))
        self.assertEqual(d["vld_samples"], 2)

    def test_validation_result_carries_the_f64_series(self):
        """
        hlp_validate_model returns the per-position series PLOT and CLIENT_CHECK consume, as f64
        views: y_pred [0, 0] and rn_y [0, -64] on the hand-computed case.
        """
        r = hlp_validate_model(self._fake_ctx([0, 64], [[0, 1], [1, 0]],
                                          [0, 2], [0.5, -0.5]))
        self.assertIsInstance(r, LMValidate)
        self.assertEqual(r.y_pred.dtype, np.float64)
        self.assertEqual(r.rn_y.dtype, np.float64)
        np.testing.assert_array_equal(r.y_pred, np.array([0.0, 0.0]))
        np.testing.assert_array_equal(r.rn_y, np.array([0.0, -64.0]))
        # the metrics are the SAME dict the file contract pins
        self.assertEqual(r.metrics["vld_samples"], 2)

    def test_hlp_validate_top_outliers_ranking_and_ties(self):
        """
        The k largest |residual|, descending, with the STABLE tie-break (the lower index first) —
        the report's determinism rests on this.
        """
        rn = np.array([1.0, -3.0, 2.0, -3.0, 0.5])
        np.testing.assert_array_equal(hlp_validate_top_outliers(rn, k=3),
                                      np.array([1, 3, 2]))
        # the tie at |3| keeps the lower index first
        self.assertEqual(list(hlp_validate_top_outliers(rn, k=2)), [1, 3])
        # k larger than the array: the whole permutation
        self.assertEqual(len(hlp_validate_top_outliers(rn, k=99)), 5)

    def test_hlp_validate_top_outliers_default_is_twenty(self):
        """The default k is the report's 20."""
        rn = np.arange(100, dtype=np.float64) - 50.0
        out = hlp_validate_top_outliers(rn)
        self.assertEqual(len(out), 20)
        # |-50| first, then the |49| tie: the STABLE argsort keeps the lower index (1) before 99,
        # then |48| at 2
        self.assertEqual([int(x) for x in out[:4]], [0, 1, 99, 2])

    def test_up_outlier_report(self):
        """
        The top-20 extreme-outlier report: the header + exactly 20 "vld position" lines, descending
        |residual|, the 20 records in ctx.vld_outliers; ties resolved by the STABLE argsort.
        """
        n = 50
        ctx = LMContext(config_file_path=Path("dummy.json"))
        ctx.vld_positions = np.zeros(n, dtype=Position)
        ctx.vld_game_values = np.arange(-25, 25, dtype=np.int8)
        ctx.feature_set = SimpleNamespace(
            compute_indexes=lambda p: np.zeros((n, 1), dtype=ExtendedIndex),
            features=[SimpleNamespace(n_instances=1)])
        ctx.iwmap_feature_offset = np.asarray([0, 1], dtype=np.int64)
        ctx.w_dense = np.asarray([0.0], dtype=np.float64)
        ctx.y2z = lambda y: (np.float32(y) + 64) / 128
        ctx.z2y = lambda z: 128 * z - 64
        logs = []
        ctx.log_event = lambda rel, msg: logs.append(msg)

        wrk_validate().up(ctx)

        self.assertIn(
            "Top 20 extreme validation residuals (outlier report):", logs)
        lines = [m for m in logs if "vld position" in m and "residual" in m]
        self.assertEqual(len(lines), 20)
        self.assertIn("  1.", lines[0])
        self.assertIn("  20.", lines[-1])
        values = [float(re.search(r"residual ([+\-][\d.]+)$", m).group(1))
                  for m in lines]
        self.assertTrue(all(abs(a) >= abs(b)
                            for a, b in zip(values, values[1:])))
        # the published records: the same order, the raw values
        self.assertEqual([r['index'] for r in ctx.vld_outliers],
                         [0, 1, 49, 2, 48, 3, 47, 4, 46, 5,
                          45, 6, 44, 7, 43, 8, 42, 9, 41, 10])
        self.assertEqual(ctx.vld_outliers[0]['residual'], 25.0)
        self.assertEqual(ctx.vld_outliers[0]['game_value'], -25.0)
        self.assertEqual(ctx.vld_outliers[0]['fitted'], 0.0)
        self.assertEqual(ctx.vld_outliers[0]['mover'], 0)
        self.assertEqual(ctx.vld_outliers[0]['opponent'], 0)

    def test_rmse_mae_line_is_zero_guarded(self):
        """
        A perfect Y-space fit (mae_y == 0) takes the zero-guard branch — the n/a ratio line, no
        ZeroDivisionError (a REAL LMContext: Worker.up is @validate_call-gated).
        """
        ctx = LMContext(config_file_path=Path("dummy.json"))
        ctx.vld_positions = np.zeros(2, dtype=Position)
        ctx.vld_game_values = np.asarray([0, 0], dtype=np.int8)
        ctx.feature_set = SimpleNamespace(
            compute_indexes=lambda p: np.asarray([[0, 1], [1, 0]], dtype=ExtendedIndex),
            features=[SimpleNamespace(n_instances=2)])
        ctx.iwmap_feature_offset = np.asarray([0, 2], dtype=np.int64)
        ctx.w_dense = np.asarray([0.0, 0.0], dtype=np.float64)
        ctx.y2z = lambda y: (np.float32(y) + 64) / 128
        ctx.z2y = lambda z: 128 * z - 64
        logs = []
        ctx.log_event = lambda rel, msg: logs.append(msg)
        wrk_validate().up(ctx)
        self.assertTrue(any("RMSE/MAE: n/a" in m for m in logs),
                        f"logs={logs}")

    def test_up_publishes_metrics_and_full_log_contract(self):
        """
        The full _up contract on ~50 synthetic positions (a REAL LMContext — Worker.up is
        @validate_call-gated): the published vld_metrics is the 7-key dict with every value
        re-derived INDEPENDENTLY here from the synthetic inputs (not copied from the worker's
        output), and the log block is exact: the 4 Starting/Computing/completed lines, the five
        indented metric lines with the source's EXACT spacing, and the RMSE/MAE ratio line
        (non-degenerate values: the ratio branch, not the zero-guard).
        """
        n = 50
        rng = np.random.default_rng(2026)
        mover = rng.integers(0, 2**64, n, dtype=np.uint64)
        full = rng.integers(0, 2**64, n, dtype=np.uint64)
        opponent = full & ~mover  # disjoint bitboards: valid game positions
        game_values = (rng.integers(-32, 33, n) * 2).astype(np.int8)  # even, in [-64, 64]
        # 1 feature, 2 instances, 2 configurations each: the raw indexes index w_dense directly.
        indexes = rng.integers(0, 2, size=(n, 2)).astype(ExtendedIndex)
        w_dense = np.asarray([0.4, -0.7], dtype=np.float64)
        offsets = np.asarray([0, 2], dtype=np.int64)

        ctx = LMContext(config_file_path=Path("dummy.json"))
        ctx.vld_positions = np.empty(n, dtype=Position)
        ctx.vld_positions['mover'] = mover
        ctx.vld_positions['opponent'] = opponent
        ctx.vld_game_values = game_values
        ctx.feature_set = SimpleNamespace(
            compute_indexes=lambda p: indexes,
            features=[SimpleNamespace(n_instances=2)])
        ctx.iwmap_feature_offset = offsets
        ctx.w_dense = w_dense
        ctx.y2z = lambda y: (np.float32(y) + 64) / 128
        ctx.z2y = lambda z: 128 * z - 64
        logs = []
        ctx.log_event = lambda rel, msg: logs.append(msg)

        wrk_validate().up(ctx)

        met = ctx.vld_metrics
        self.assertEqual(set(met), {'vld_loss', 'vld_mse_z', 'vld_mae_z',
                                    'vld_mae_y', 'vld_mse_y', 'vld_rmse_y',
                                    'vld_samples'})
        self.assertEqual(met['vld_samples'], n)

        # Independent re-derivation: the hlp_validate_model arithmetic mirrored from the
        # synthetic inputs (the same operations, the same order).
        col_offsets = np.repeat(offsets[:-1], 2)
        z_pred = sigmoid(np.sum(w_dense[indexes + col_offsets], axis=1))
        vld_z = (np.float32(game_values) + 64) / 128
        rn_z = z_pred - vld_z
        my_mse_z = float(np.dot(rn_z, rn_z) / n)
        y_pred = 128 * z_pred - 64
        rn_y = y_pred - game_values
        my_mse_y = float(np.dot(rn_y, rn_y) / n)
        assert_close(self, met['vld_loss'], 0.5 * my_mse_z, 'vld_loss')
        assert_close(self, met['vld_mse_z'], my_mse_z, 'vld_mse_z')
        assert_close(self, met['vld_mae_z'], float(np.mean(np.abs(rn_z))), 'vld_mae_z')
        assert_close(self, met['vld_mae_y'], float(np.mean(np.abs(rn_y))), 'vld_mae_y')
        assert_close(self, met['vld_mse_y'], my_mse_y, 'vld_mse_y')
        assert_close(self, met['vld_rmse_y'], math.sqrt(my_mse_y), 'vld_rmse_y')

        # The non-degenerate branch: the ratio line is emitted, the zero-guard is not.
        self.assertGreater(met['vld_mae_y'], 0.0)
        self.assertFalse(any("RMSE/MAE: n/a" in m for m in logs))

        # The full log block, in order, with the source's exact spacing (the per-line formats of
        # wrk_validate._up + hlp_validate_model).
        expected = [
            "Starting model validation...",
            "Computing indexes for validation set...",
            "Computing predictions (forward pass) on validation set...",
            f"Validation completed. Loss (MSE/2): {met['vld_loss']:.8e}",
            f"  MSE:      {met['vld_mse_z']:.4e}",
            f"  MAE:      {met['vld_mae_z']:.4e}",
            f"  MAE(y):   {met['vld_mae_y']:.2f}",
            f"  RMSE(y):  {met['vld_rmse_y']:.2f}",
            f"  RMSE/MAE: {met['vld_rmse_y'] / met['vld_mae_y']:.2f}",
            "Top 20 extreme validation residuals (outlier report):",
        ]
        self.assertEqual(logs[:10], expected)
        # The outlier report: exactly 20 "vld position" lines after the header.
        self.assertEqual(sum("vld position" in m for m in logs[10:]), 20)


class TestValidateSecondInstanceSmall(unittest.TestCase):
    """
    The second-instance determinism, DB-free (the NORMAL-tier pin of the LONG-tier
    test_second_instance_deterministic): a FRESH base dir pre-seeded with the two cache files
    (rlmwf_04_POSITIONS.dat + rlmwf_13_VLD_POSITIONS.dat, built no-DB from in-memory
    RegabDataSets — the TestIsCacheConsistent idiom + the real regab_store_data_set_to_file),
    then TWO real LogisticModel instances on a SMALL rlm_00-derived config moved to VALIDATE.
    The seeded files make the POSITIONS / VLD_POSITIONS levels hit the cache, the four
    in-between cache levels (INDEXES / WMAPS / DESIGN_MTR / GENERATE) compute from the loaded
    data (no DB), and VALIDATE — which has no cache file — recomputes from the cached w_dense:
    the second instance's vld_metrics is bit-identical to the first's.
    """

    @classmethod
    def setUpClass(cls):
        CUSTOM_TMP_BASE.mkdir(parents=True, exist_ok=True)

    def setUp(self):
        # TemporaryDirectory created FIRST so a mid-setup failure still leaves a cleanable temp dir.
        self._tmp = tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE))
        self.tmp_dir = Path(self._tmp.name)

        # The SMALL config: the rlm_00 fixture re-dumped with a shrunk optimization + SU corpus
        # (the chain runs twice; the DB is never touched, so only the CPU work matters).
        d = json5.loads((WORKSPACE_ROOT / "test" / "reversi" / "data" /
                         "rlm_00.json").read_text(encoding="utf-8"))
        d["optimization"]["max_iters"] = 20
        d["su_analysis"]["total_positions"] = 200
        self.cfg_file = self.tmp_dir / "rlm_00_small.json"
        self.cfg_file.write_text(json5.dumps(d), encoding="utf-8")

        # The no-DB seed: in-memory RegabDataSets matching the cfg (tst_regab @ localhost:5432,
        # bid [8], status ["CMS", "CMR"], ec 20 — the rlm_00 values), stored via the real file I/O.
        self.rc = RegabDBConnection("tst_regab", "tst_regab", "localhost", "5432",
                                    activate_conn=False)
        regab_store_data_set_to_file(self._seed_rds(10, 1),
                                     self.tmp_dir / "rlmwf_04_POSITIONS.dat")
        regab_store_data_set_to_file(self._seed_rds(10, 2),
                                     self.tmp_dir / "rlmwf_13_VLD_POSITIONS.dat")

    def tearDown(self):
        if getattr(self, '_tmp', None) is not None:
            self._tmp.cleanup()

    @staticmethod
    def _seed_rds(n: int, seed: int) -> RegabDataSet:
        # Synthetic 10-row data set: the disjoint-bitboard idiom (random boards with overlapping
        # mover/opponent bits break the WMAPS pattern-index bounds).
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
        return RegabDataSet(RegabDBConnection("tst_regab", "tst_regab", "localhost",
                                              "5432", activate_conn=False),
                            [8], ["CMS", "CMR"], 20, df)

    def test_second_instance_deterministic_small(self):
        rlm1 = LogisticModel(str(self.cfg_file),
                             verbosity=Verbosity.NONE,
                             base_dir_override=self.tmp_dir)
        rlm1.move_to_step('VALIDATE')
        self.assertEqual(rlm1.current_step, 14)
        met1 = rlm1.context.vld_metrics
        self.assertIsNotNone(met1)

        # The whole first run is DB-free too: the seeded files hit, nothing is extracted.
        msgs1 = [e.message for e in rlm1.sm.logs]
        self.assertFalse(any("Extracted" in m for m in msgs1))
        self.assertFalse(any("established successfully" in m for m in msgs1))

        # A completely new instance on the SAME base dir: every cache level hits.
        rlm2 = LogisticModel(str(self.cfg_file),
                             verbosity=Verbosity.NONE,
                             base_dir_override=self.tmp_dir)
        rlm2.move_to_step('VALIDATE')
        self.assertEqual(rlm2.current_step, 14)

        msgs2 = [e.message for e in rlm2.sm.logs]
        self.assertFalse(any("Extracted" in m for m in msgs2),
                         "DB was queried even though a valid cache existed.")
        self.assertFalse(any("established successfully" in m for m in msgs2),
                         "DB connection was opened even though a valid cache existed.")
        self.assertIn(
            f"Cache successfully loaded and validated from '{self.tmp_dir / 'rlmwf_04_POSITIONS.dat'}'.",
            msgs2)
        self.assertIn(
            f"Cache successfully loaded and validated from '{self.tmp_dir / 'rlmwf_13_VLD_POSITIONS.dat'}'.",
            msgs2)

        # VALIDATE has no cache file — the metrics are a pure deterministic recompute from the
        # cached w_dense: bit-identical to the first instance's.
        self.assertEqual(rlm2.context.vld_metrics, met1)


class TestValidateDownScope(unittest.TestCase):
    """
    The FULL _down scope, DB-free: the failure-recovery rollback clears all FOUR validation
    attributes (vld_metrics, vld_y_pred, vld_rn, vld_outliers) — strictly stronger than the
    LONG-tier pin, which exercises only vld_metrics through the state machine.
    """

    def test_down_clears_all_vld_attributes(self):
        sentinel = object()
        logs = []
        ctx = SimpleNamespace(
            vld_metrics=sentinel,
            vld_y_pred=sentinel,
            vld_rn=sentinel,
            vld_outliers=sentinel,
            log_event=lambda rel, msg: logs.append(msg))

        _down(ctx)

        self.assertIsNone(ctx.vld_metrics)
        self.assertIsNone(ctx.vld_y_pred)
        self.assertIsNone(ctx.vld_rn)
        self.assertIsNone(ctx.vld_outliers)
        self.assertIn("Clearing validation attributes...", logs)


if __name__ == '__main__':
    unittest.main()
