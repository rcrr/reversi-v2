#
# test_lm_worker_full_chain.py
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
# How to run the full worker chain unit tests.
#
# Run from the workspace root (the directory containing .venv and src).
#
# -0- Activate the environment.
#
# $ source .venv/bin/activate
#
# -1- Run the tests (a live regab DB + LONG=1 is required;
#     SKIP_REGAB_DB=1 skips the DB-gated tests, as in test_regab.
#     VLONG=1 enables the ~10-min A2050 chain on rlm_03 and
#     implies LONG).
#
# time python3 -m unittest test.reversi.lm.test_lm_worker_full_chain
#

import unittest
import os
import tempfile
import shutil
import hashlib
import json

import json5
import re
from types import SimpleNamespace

import numpy as np

from unittest import skipUnless
from unittest.mock import patch
from io import StringIO
from pathlib import Path

from reversi.tools.state_machine import Verbosity
from reversi.lm.logistic_model import LogisticModel
from reversi.tools.binio import BinaryWriter, verify_sha3_256_sidecar
from reversi.lm.model_weights import (model_weights_read_file,
                                      model_weights_write_file,
                                      MODEL_WEIGHTS_FILE_HEADER_STR,
                                      MODEL_WEIGHTS_FILE_HEADER_VER)
from reversi.feature import FeatureSet
from reversi.lm.client import (make_evaluation_function,
                               make_evaluation_function_array)
from reversi.lm.hlp_gradient import sigmoid
from test.reversi.closecheck import assert_close
from test.reversi.paths import WORKSPACE_ROOT, CUSTOM_TMP_BASE
from test.reversi.tags import db_long_gate, tier_vvlong
from reversi.index import Index


def _masked_report_hash(report_text):
    # The file report embeds datetime.now(); mask the date so the hash is stable. The config
    # fingerprint embeds the run's base_dir (a tmp dir); mask the hex the same way.
    text = re.sub(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", "DATE", report_text)
    text = re.sub(r"(Config SHA3-256\s*:\s*)[0-9a-f]{64}", r"\1HASH", text)
    return hashlib.sha3_256(text.encode()).hexdigest()


class TestFullChainA2030(unittest.TestCase):
    """
    Tests the full Reversi Logistic Model chain on the A2030 configuration.

    Every test runs the full chain up to the last level: the end-to-end test with the plots ENABLED
    (it asserts them), the provenance and the determinism tests with `plot.enable = False` — they
    assert nothing about the figures, and rendering them costs ~5.1 s of matplotlib on the A2030
    validation set. The override lives in a CONFIG FILE (a copy of rlm_04.json written in the test's
    temp dir): mutating `ctx.cfg` AFTER the CONFIG step would desync `ctx.config_checksum` from the
    cfg's own dump (the provenance test pins exactly that identity).
    """

    suppress_stdout_io = True

    def setUp(self):
        # The SKIP_REGAB_DB gate, as in test_regab — the full chain reads training and validation
        # positions from the regab database.
        db_long_gate(self)  # the SKIP_REGAB_DB + LONG gates

        if self.suppress_stdout_io:
            self.patcher_stdout = patch('sys.stdout', new=StringIO())
            self.mock_stdout = self.patcher_stdout.start()

        self.tmp_dir = tempfile.mkdtemp(dir=str(CUSTOM_TMP_BASE))
        self.json_config = str(WORKSPACE_ROOT / "test" / "reversi" / "data" / "rlm_04.json")

        self.rlm = LogisticModel(self.json_config,
                                 verbosity=Verbosity.HIGH,
                                 base_dir_override=self.tmp_dir)

    def _config_without_plots(self):
        """
        The rlm_04 config with `plot.enable = False`, written in the test's temp dir: the chain
        still runs all levels, the PLOT worker just skips the rendering.
        """
        raw = json5.loads(
            (WORKSPACE_ROOT / "test" / "reversi" / "data" /
             "rlm_04.json").read_text())
        raw.setdefault("plot", {})["enable"] = False
        path = Path(self.tmp_dir) / "rlm_04_noplot.json"
        path.write_text(json.dumps(raw))
        return str(path)

    def _model(self, plots=True):
        """A fresh LogisticModel on the test's temp dir, with or without the plot rendering."""
        return LogisticModel(self.json_config if plots
                             else self._config_without_plots(),
                             verbosity=Verbosity.HIGH,
                             base_dir_override=self.tmp_dir)

    def tearDown(self):
        if self.suppress_stdout_io:
            self.patcher_stdout.stop()
        shutil.rmtree(self.tmp_dir)

    def test_full_worker_chain(self):
        """Run the full chain up to last level on rlm_04."""
        ctx = self.rlm.context

        # Run the model chain.
        self.rlm.move_to_last()
        self.assertEqual(self.rlm.current_step, 19)
        self.assertEqual(self.rlm.current_worker_name, 'FINAL_LOG_PRINT')

        # --- Validation metrics (assert_close goldens; bid [5] vld, 20000 samples) ---
        m = ctx.vld_metrics
        self.assertEqual(m['vld_samples'], 20000)
        assert_close(self, m['vld_loss'], 0.005758139304816723, 'vld_loss')
        assert_close(self, m['vld_mse_z'], 0.011516278609633446, 'vld_mse_z')
        assert_close(self, m['vld_mae_z'], 0.08458831906318665, 'vld_mae_z')
        assert_close(self, m['vld_mae_y'], 11.048270225524902, 'vld_mae_y')
        assert_close(self, m['vld_mse_y'], 196.462646484375, 'vld_mse_y')
        assert_close(self, m['vld_rmse_y'], 14.01651382446289, 'vld_rmse_y')
        # The top-20 extreme-outlier report: the 20 records + the two f64 series published on the
        # context, the records ordered by absolute residual.
        self.assertEqual(len(ctx.vld_outliers), 20)
        self.assertEqual(len(ctx.vld_rn), 20000)
        self.assertEqual(ctx.vld_rn.dtype, np.float64)
        self.assertEqual([r['index'] for r in ctx.vld_outliers],
                         sorted((r['index'] for r in ctx.vld_outliers),
                                key=lambda i: -abs(ctx.vld_rn[i])))

        # --- Training metrics (assert_close goldens; bid [6], 199932 samples) ---
        t = ctx.train_metrics
        self.assertEqual(t['train_samples'], 199932)
        assert_close(self, t['train_mae_y'], 10.899691755852983, 'train_mae_y')
        assert_close(self, t['train_rmse_y'], 13.825076853665676, 'train_rmse_y')
        # f32-quantized (the OPTIMIZE objective f) — bit-exact
        self.assertEqual(t['train_loss'], 0.005608053877949715)
        assert_close(self, t['pop_mae_y'], 21.73034518830014, 'pop_mae_y')
        assert_close(self, t['pop_rmse_y'], 26.406980394267364, 'pop_rmse_y')
        assert_close(self, t['pop_loss'], 0.020438173785805702, 'pop_loss')

        # --- Dense training metrics (assert_close; the w_dense forward pass — the shipped inference
        # rules — on the training data; differs from the compressed pass on the 1923 positions
        # touching below-cutoff (IC) configurations) ---
        td = ctx.train_dense_metrics
        self.assertEqual(td['train_dense_samples'], 199932)
        assert_close(self, td['train_dense_mae_y'], 10.905434791589059, 'train_dense_mae_y')
        assert_close(self, td['train_dense_rmse_y'], 13.8332856021253, 'train_dense_rmse_y')
        assert_close(self, td['train_dense_loss'], 0.0056085786782205105, 'train_dense_loss')

        # --- Training population statistics (assert_close) ---
        p = ctx.training_pop_stats
        self.assertEqual(p['count'], 199932)
        assert_close(self, p['mean'], -1.3912930396334753, 'pop mean')
        assert_close(self, p['std_dev'], 26.40698039426738, 'pop std_dev')
        assert_close(self, p['variance'], 697.3286135432216, 'pop variance')

        # --- Optimization info (5-key dict) ---
        self.assertTrue(ctx.opt_info['converged'])
        self.assertEqual(ctx.opt_info['reason'], 'CONVERGED_MIN_GRAD')
        self.assertEqual(ctx.opt_info['iters'], 71)

        # --- Saved model file: exists, size band, sidecar --- The v2 file EMBEDS the run's
        # configuration: the normalized dump carries the run's base_dir (a random mkdtemp path in
        # this test), so the file BYTES are legitimately run-specific — no sha3 literal golden, and
        # the size literal is a BAND: the 8 random base_dir chars change LZ4's match structure by a
        # few bytes (measured: the same raw content compresses to 516459 or 516455 depending on the
        # random name). The determinism guarantee is carried by test_second_instance_deterministic
        # (same base dir → byte-identical file) + the read-back provenance pins below.
        output_path = ctx.cfg.base_dir / ctx.cfg.output
        self.assertTrue(output_path.exists(), f"Output file not found at {output_path}")
        st_size = output_path.stat().st_size
        self.assertTrue(23512 < st_size < 23612,
                        f"v2 model file size {st_size} outside the 23512-23612 band")
        self.assertTrue(verify_sha3_256_sidecar(output_path), "Checksum verification failed for saved model")

        # --- Read the file back using the client's read function ---
        mw = model_weights_read_file(output_path, compressed=True)

        # Metadata
        self.assertEqual(mw.version, 2)
        self.assertEqual(mw.name, ctx.cfg.name)
        self.assertEqual(mw.ec, ctx.cfg.empty_count)
        self.assertAlmostEqual(mw.logit_clipping, ctx.cfg.stat_model.logit_clipping, places=5)

        # Training population statistics (float32 truncation by the file format)
        self.assertEqual(mw.training_pop_stats['count'], np.uint64(199932))
        self.assertEqual(float(mw.training_pop_stats['mean']), -1.3912930488586426)
        self.assertEqual(float(mw.training_pop_stats['std_dev']), 26.406980514526367)
        self.assertEqual(float(mw.training_pop_stats['variance']), 697.32861328125)

        # Optimization info (4 of the 5 context keys persisted; 'converged' is derivable from 'reason')
        self.assertEqual(mw.opt_info['reason'], 'CONVERGED_MIN_GRAD')
        self.assertEqual(mw.opt_info['iters'], np.uint32(71))
        self.assertEqual(float(mw.opt_info['f']), 0.005608053877949715)
        self.assertEqual(float(mw.opt_info['g_norm']), 6.098220910644159e-05)

        # Validation metrics (4 of the 7 context metrics persisted)
        self.assertEqual(mw.vld_metrics['vld_samples'], np.uint32(20000))
        self.assertEqual(float(mw.vld_metrics['vld_rmse_y']), 14.01651382446289)
        self.assertEqual(float(mw.vld_metrics['vld_mae_y']), 11.048270225524902)
        self.assertEqual(float(mw.vld_metrics['vld_loss']), 0.005758139304816723)

        # FeatureSet (the hash is a definitive structural check: names + sorted mask contents,
        # transitive over mset/pset)
        self.assertEqual(mw.feature_set.hash, 'e9cda2ac3c14c5542bc9ebac648c340af7885757fa2f7801c27645caa58c7f69')
        self.assertEqual(mw.feature_set.hash, ctx.feature_set.hash)

        # Core inference arrays
        np.testing.assert_array_equal(mw.iwmap_feature_offset, np.array([0, 1, 66, 6627], dtype=Index))
        self.assertEqual(mw.w_dense.shape, (6627,))
        self.assertEqual(mw.w_dense.dtype, np.float32)
        self.assertEqual(
            hashlib.sha3_256(mw.w_dense.tobytes()).hexdigest(),
            '90ca05a3625775903d0a6e09c37d0f5827c3815738ddcd1af8d12e113b34ea75')
        np.testing.assert_array_equal(mw.w_dense, ctx.w_dense)

        # The configuration provenance EMBEDDED in the v2 file (the leading body section) — the
        # single source of the run's configuration: the dump is the normalized dump (the effective
        # config, the base_dir override included) and the checksum is the CONFIG-level fingerprint.
        self.assertEqual(mw.config_dump, ctx.cfg.model_dump_json(indent=4))
        self.assertEqual(mw.config_checksum, ctx.config_checksum)
        self.assertEqual(
            mw.config_checksum,
            hashlib.sha3_256(
                ctx.cfg.model_dump_json(indent=4).encode()
            ).hexdigest())

        # --- Log lines (captured stdout) ---
        logs = self.mock_stdout.getvalue()
        self.assertIn("Validation completed. Loss (MSE/2): 5.75813930e-03", logs)
        self.assertIn("Saving model weights to disk...", logs)
        self.assertIn("Model weights saved to", logs)
        # The CLIENT_CHECK level re-reads the saved file, rebuilds the client's EF and reproduces
        # the validation residuals bit-exactly (max difference 0.0 < the 1e-8 tolerance).
        self.assertIn(
            "Client check passed: 20000 validation residuals, "
            "max difference 0.000e+00 (tolerance 1.0e-08).", logs)
        # The PLOT level writes the seven rlm_04-whitelisted plots (png, the relative 'plots'
        # dir_name default) to base_dir/plots.
        plot_dir = ctx.cfg.base_dir / "plots"
        for name in ("residual_density", "resid_vs_fitted",
                     "resid_vs_gv", "gv_by_egv_box",
                     "resid_mean_by_egv", "parity", "resid_qq"):
            p = plot_dir / f"{name}.png"
            self.assertTrue(p.exists(), f"plot missing: {p}")
            self.assertEqual(p.read_bytes()[:4], b"\x89PNG")
        self.assertIn("Plot 'residual_density' saved:", logs)
        self.assertIn(f"PLOT done: 7 plot(s) written to {plot_dir}.",
                      logs)
        # The top-20 report: exactly 20 'vld position' lines in the log (the VALIDATE level emits
        # them; PLOT renders the figures only).
        self.assertEqual(logs.count("vld position"), 20)

        # --- Analytics console report (exact pins) ---
        report = ctx.analytics_report
        self.assertIn("MODEL ANALYTICS REPORT: RGLM (Logistic) - Short-Long Test 04 (rlm_04.json)", report)
        self.assertIn("Loss (MSE/2)    | 5.6081e-03     | 5.6086e-03     | 5.7581e-03", report)
        self.assertIn("Population (baseline)  : RMSE 26.41  MAE 21.73  Loss 2.0438e-02", report)
        self.assertIn("Generalization Gap (RMSE)   : 0.18", report)
        self.assertIn("Substitution Delta (RMSE)   : 0.01", report)
        # The config fingerprint (in the common header — both reports; computed from the live ctx,
        # not a literal).
        self.assertIn(f"Config SHA3-256             : {ctx.config_checksum}", report)

        # --- Analytics file report (detailed_report: EDGE + LMC) ---
        report_path = ctx.cfg.base_dir / ctx.cfg.analytics.report_file_name
        self.assertTrue(report_path.exists(), f"Analytics report file not found at {report_path}")
        file_report = report_path.read_text(encoding='utf-8')
        self.assertIn("Creation Date               :", file_report)
        self.assertIn("PATTERN FEATURE: EDGE (fid=2)", file_report)
        self.assertIn("MOBILITY FEATURE: LMC (fid=1)", file_report)
        # The config fingerprint line (the masked-hash golden masks the run-dependent hex value).
        self.assertIn(f"Config SHA3-256             : {ctx.config_checksum}", file_report)
        self.assertEqual(_masked_report_hash(file_report),
                         '42a095cac995dcf3edb2d9a65fe6706fdbbafbdfb04deecee9b3fb10bcd99c33')

        # --- The client's Evaluation Function: bit-exact on 6 pinned training positions (rlm_04 has
        # frequency_cut_off=10, so training positions touching below-cutoff configurations exercise
        # the w_dense substitution slots) ---
        ef = make_evaluation_function(mw)
        expected_ef = {
            0: -37.28886413574219,
            1: -28.242984771728516,
            7: 45.49725341796875,
            123: 40.28820037841797,
            999: 16.244956970214844,
            len(ctx.positions) - 1: 23.315696716308594,
        }
        for i, y_expected in expected_ef.items():
            self.assertEqual(ef(ctx.positions[i]), y_expected, msg=f"EF mismatch at training position {i}")

        # The same EF on a validation position: rlm_04 validation (bid [5]) contains EDGE
        # configurations unseen in training, so this pins the w_dense substitution path (orbit
        # weighted mean) end-to-end.
        self.assertEqual(ef(ctx.vld_positions[42]), 11.917137145996094)

        # --- The vectorized EF: bit-exact on the same 6 pinned training positions, one batch call
        # over the full training set + the vld pin on the validation batch ---
        ef_arr = make_evaluation_function_array(mw)
        y_arr = ef_arr(ctx.positions)
        self.assertEqual(y_arr.dtype, np.float32)
        self.assertEqual(y_arr.shape, (len(ctx.positions),))
        for i, y_expected in expected_ef.items():
            self.assertEqual(float(y_arr[i]), y_expected,
                             msg=f"array EF mismatch at training position {i}")
        self.assertEqual(float(ef_arr(ctx.vld_positions)[42]),
                         11.917137145996094)

    def test_config_provenance_single_source(self):
        """
        The model file is the SINGLE source of the run's configuration: no <output>.config.json
        sidecar — the provenance lives INSIDE the model file (pinned in test_full_worker_chain).
        """
        # The full chain with the plots disabled — this test asserts the FILE's provenance (the
        # record absence, the sidecar, the fingerprint) and nothing about the figures.
        rlm = self._model(plots=False)
        rlm.move_to_last()
        ctx = rlm.context
        output_path = ctx.cfg.base_dir / ctx.cfg.output
        config_path = output_path.with_suffix(".config.json")

        # No config record: the shipped artifact is the model file (+ its sidecar) alone.
        self.assertFalse(config_path.exists(),
                         f"Config record must not exist, found at {config_path}")
        self.assertFalse(
            (output_path.parent /
             (output_path.name + ".config.json.SHA3-256")).exists(),
            "The record sidecar must be gone with the record")
        # The model file's sidecar verifies (it covers the v2 content, config section included).
        self.assertTrue(verify_sha3_256_sidecar(output_path),
                        "Checksum verification failed for saved model")
        # The fingerprint semantics: config_checksum == sha3_256 of the normalized dump, on the
        # embedded provenance.
        self.assertEqual(ctx.config_checksum,
                         hashlib.sha3_256(
                             ctx.cfg.model_dump_json(indent=4).encode()
                         ).hexdigest())

    def test_second_instance_deterministic(self):
        """
        A second full run in the same base dir: byte-identical model file, 6 cache hits (the 6
        rlmwf_ cache files all hit; the 7th file, the OPTIMIZE checkpoint, has its own read-back).
        """
        # The full chain with the plots disabled (this test asserts the model file's byte-identity +
        # the cache hits, not the figures) — the same config file in both runs, so the embedded
        # provenance matches too.
        rlm = self._model(plots=False)
        rlm.move_to_last()
        output_path = rlm.context.cfg.base_dir / rlm.context.cfg.output
        first_hash = hashlib.sha3_256(output_path.read_bytes()).hexdigest()

        rlm2 = self._model(plots=False)
        with patch('sys.stdout', new=StringIO()) as out2:
            rlm2.move_to_last()
        logs2 = out2.getvalue()

        second_hash = hashlib.sha3_256(output_path.read_bytes()).hexdigest()
        self.assertEqual(second_hash, first_hash)
        self.assertEqual(logs2.count("Cache successfully loaded and validated"), 6)
        self.assertNotIn("Extracted", logs2)
        self.assertNotIn("established successfully", logs2)


@skipUnless(tier_vvlong(), "Skipping the very-long A2050 chain (set VVLONG=1 to run)")
class TestFullChainA2050(unittest.TestCase):
    """
    Tests the full Reversi Logistic Model chain on the A2050 configuration (the production
    endgame-solver model family: A2 + ec*10; A2050 = ec 20).
    """

    suppress_stdout_io = False

    def setUp(self):
        # The SKIP_REGAB_DB gate, as in test_regab — the full chain reads training and validation
        # positions from the regab database.
        db_long_gate(self)  # the SKIP_REGAB_DB + LONG gates

        if self.suppress_stdout_io:
            self.patcher_stdout = patch('sys.stdout', new=StringIO())
            self.mock_stdout = self.patcher_stdout.start()

        self.tmp_dir = tempfile.mkdtemp(dir=str(CUSTOM_TMP_BASE))
        self.json_config = str(WORKSPACE_ROOT / "test" / "reversi" / "data" / "rlm_03.json")

        self.rlm = LogisticModel(self.json_config,
                                 verbosity=Verbosity.HIGH,
                                 base_dir_override=self.tmp_dir)

    def tearDown(self):
        if self.suppress_stdout_io:
            self.patcher_stdout.stop()
        shutil.rmtree(self.tmp_dir)

    def test_full_worker_chain(self):
        """
        Run the full chain up to last level on rlm_03. Long-running: ~1 minute (1999179 training
        samples, 356 lbfgs iters).
        """
        ctx = self.rlm.context

        # Run the model chain.
        self.rlm.move_to_last()
        self.assertEqual(self.rlm.current_step, 19)
        self.assertEqual(self.rlm.current_worker_name, 'FINAL_LOG_PRINT')

        # --- Validation metrics (assert_close goldens; bid [6] vld, 199932 samples) ---
        m = ctx.vld_metrics
        self.assertEqual(m['vld_samples'], 199932)
        assert_close(self, m['vld_loss'], 0.0015777380904182792, 'vld_loss')
        assert_close(self, m['vld_mse_z'], 0.0031554761808365583, 'vld_mse_z')
        assert_close(self, m['vld_mae_z'], 0.04319758340716362, 'vld_mae_z')
        assert_close(self, m['vld_mae_y'], 5.6421332359313965, 'vld_mae_y')
        assert_close(self, m['vld_mse_y'], 53.831050872802734, 'vld_mse_y')
        assert_close(self, m['vld_rmse_y'], 7.3369646072387695, 'vld_rmse_y')

        # --- Training metrics (assert_close goldens; bid [3], 1999179 samples) ---
        t = ctx.train_metrics
        self.assertEqual(t['train_samples'], 1999179)
        assert_close(self, t['train_mae_y'], 5.398311036121195, 'train_mae_y')
        assert_close(self, t['train_rmse_y'], 7.017904345215441, 'train_rmse_y')
        # f32-quantized (the OPTIMIZE objective f) — bit-exact
        self.assertEqual(t['train_loss'], 0.0014453826006501913)
        assert_close(self, t['pop_mae_y'], 21.758215006979484, 'pop_mae_y')
        assert_close(self, t['pop_rmse_y'], 26.417003454424307, 'pop_rmse_y')
        assert_close(self, t['pop_loss'], 0.020453333854675293, 'pop_loss')

        # --- Dense training metrics (assert_close; rlm_03 has frequency_cut_off=1, so the dense
        # pass matches the compressed one up to the f32 rounding of w_dense — delta "0.00") ---
        td = ctx.train_dense_metrics
        self.assertEqual(td['train_dense_samples'], 1999179)
        assert_close(self, td['train_dense_mae_y'], 5.398311040100617, 'train_dense_mae_y')
        assert_close(self, td['train_dense_rmse_y'], 7.017904346461752, 'train_dense_rmse_y')
        assert_close(self, td['train_dense_loss'], 0.0014434857293963432, 'train_dense_loss')

        # --- Training population statistics (assert_close) ---
        p = ctx.training_pop_stats
        self.assertEqual(p['count'], 1999179)
        assert_close(self, p['mean'], -1.3259453005458741, 'pop mean')
        assert_close(self, p['std_dev'], 26.417003454424318, 'pop std_dev')
        assert_close(self, p['variance'], 697.8580715110664, 'pop variance')

        # --- Optimization info (5-key dict) ---
        self.assertTrue(ctx.opt_info['converged'])
        self.assertEqual(ctx.opt_info['reason'], 'CONVERGED_MIN_GRAD')
        self.assertEqual(ctx.opt_info['iters'], 356)

        # --- Analytics console report (exact pins; no detailed tables) ---
        console_report = ctx.analytics_report
        self.assertIn("MODEL ANALYTICS REPORT: RGLM (Logistic) - Long Test 03 (rlm_03.json)", console_report)
        self.assertIn("Loss (MSE/2)    | 1.4454e-03     | 1.4435e-03     | 1.5777e-03", console_report)
        self.assertIn("Population (baseline)  : RMSE 26.42  MAE 21.76  Loss 2.0453e-02", console_report)
        self.assertIn("Generalization Gap (RMSE)   : 0.32", console_report)
        self.assertIn("Substitution Delta (RMSE)   : 0.00", console_report)
        self.assertNotIn("FEATURE SET SUMMARY:", console_report)
        self.assertNotIn("MOBILITY FEATURES DETAILS:", console_report)

        # The PLOT level writes the seven rlm_03-whitelisted plots (png, the relative 'plots'
        # dir_name default) to base_dir/plots — the 200k-point scale of the production model family.
        plot_dir = ctx.cfg.base_dir / "plots"
        for name in ("residual_density", "resid_vs_fitted",
                     "resid_vs_gv", "gv_by_egv_box",
                     "resid_mean_by_egv", "parity", "resid_qq"):
            p = plot_dir / f"{name}.png"
            self.assertTrue(p.exists(), f"plot missing: {p}")
            self.assertEqual(p.read_bytes()[:4], b"\x89PNG")

        # --- Analytics file report (detailed_report: XEDGE) ---
        report_path = ctx.cfg.base_dir / ctx.cfg.analytics.report_file_name
        self.assertTrue(report_path.exists(), f"Analytics report file not found at {report_path}")
        file_report = report_path.read_text(encoding='utf-8')
        self.assertIn("Creation Date               :", file_report)
        self.assertIn("PATTERN FEATURE: XEDGE", file_report)
        self.assertEqual(_masked_report_hash(file_report),
                         '8d609b5b5d656bc47f9e35744e7ac066d2674f689cf183632b6a7b7daa41fd82')

        # --- Saved model file: exists, size band, sidecar --- As in A2030 — the embedded dump
        # carries the run's base_dir (a random mkdtemp path), so no sha3 literal golden and the size
        # literal is a band (the 8 random base_dir chars change LZ4's match structure by a few
        # bytes). Determinism is pinned by the read-back provenance + the same-base-dir byte identity.
        output_path = ctx.cfg.base_dir / ctx.cfg.output
        self.assertTrue(output_path.exists(), f"Output file not found at {output_path}")
        st_size = output_path.stat().st_size
        self.assertTrue(516991 < st_size < 517091,
                        f"v2 model file size {st_size} outside the 516991-517091 band")
        self.assertTrue(verify_sha3_256_sidecar(output_path), "Checksum verification failed for saved model")

        # --- Read the file back using the client's read function ---
        mw = model_weights_read_file(output_path, compressed=True)

        # Metadata
        self.assertEqual(mw.version, 2)
        self.assertEqual(mw.name, ctx.cfg.name)
        self.assertEqual(mw.ec, ctx.cfg.empty_count)
        self.assertAlmostEqual(mw.logit_clipping, ctx.cfg.stat_model.logit_clipping, places=5)

        # Training population statistics (float32 truncation by the file format)
        self.assertEqual(mw.training_pop_stats['count'], np.uint64(1999179))
        self.assertEqual(float(mw.training_pop_stats['mean']), -1.325945258140564)
        self.assertEqual(float(mw.training_pop_stats['std_dev']), 26.417003631591797)
        self.assertEqual(float(mw.training_pop_stats['variance']), 697.8580932617188)

        # Optimization info (4 of the 5 context keys persisted; 'converged' is derivable from 'reason')
        self.assertEqual(mw.opt_info['reason'], 'CONVERGED_MIN_GRAD')
        self.assertEqual(mw.opt_info['iters'], np.uint32(356))
        self.assertEqual(float(mw.opt_info['f']), 0.0014453826006501913)
        self.assertEqual(float(mw.opt_info['g_norm']), 7.973910214786883e-06)

        # Validation metrics (4 of the 7 context metrics persisted)
        self.assertEqual(mw.vld_metrics['vld_samples'], np.uint32(199932))
        self.assertEqual(float(mw.vld_metrics['vld_rmse_y']), 7.3369646072387695)
        self.assertEqual(float(mw.vld_metrics['vld_mae_y']), 5.6421332359313965)
        self.assertEqual(float(mw.vld_metrics['vld_loss']), 0.0015777380904182792)

        # FeatureSet (13 features: intercept + LMC + 11 patterns)
        self.assertEqual(mw.feature_set.hash, 'f34ee4097831978dc038c481e7fdf6b25b11365dccc44271a739afef2bdd337d')
        self.assertEqual(mw.feature_set.hash, ctx.feature_set.hash)

        # Core inference arrays (14 boundary entries for the 13 features)
        np.testing.assert_array_equal(
            mw.iwmap_feature_offset,
            np.array([0, 1, 66, 59115, 118164, 124725, 144408, 150969, 151050,
                      157611, 157854, 158583, 160770, 167331], dtype=Index))
        self.assertEqual(mw.w_dense.shape, (167331,))
        self.assertEqual(mw.w_dense.dtype, np.float32)
        self.assertEqual(
            hashlib.sha3_256(mw.w_dense.tobytes()).hexdigest(),
            '82b329dd31c5ac0d2b6b5c23a15734e0f4a7f18b6fbc609ef8c445c43035cccc')
        np.testing.assert_array_equal(mw.w_dense, ctx.w_dense)

        # The embedded configuration provenance (the v2 leading body section) — the single source of
        # the run's configuration.
        self.assertEqual(mw.config_dump, ctx.cfg.model_dump_json(indent=4))
        self.assertEqual(mw.config_checksum, ctx.config_checksum)

        # --- The client's Evaluation Function: bit-exact on 6 pinned training positions (rlm_03 has
        # frequency_cut_off=1, so every training configuration is confirmed: dense == compressed) ---
        ef = make_evaluation_function(mw)
        expected_ef = {
            0: 6.911094665527344,
            5: -32.91969299316406,
            123: 40.503456115722656,
            555: 24.345985412597656,
            9999: -19.517921447753906,
            len(ctx.positions) - 1: 57.769447326660156,
        }
        for i, y_expected in expected_ef.items():
            self.assertEqual(ef(ctx.positions[i]), y_expected, msg=f"EF mismatch at training position {i}")


class TestModelWeightsReadGuards(unittest.TestCase):
    """The read guards in model_weights_read_file (no DB needed)."""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(dir=str(CUSTOM_TMP_BASE))

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)

    def test_wrong_description_raises(self):
        path = Path(self.tmp_dir) / 'bad_description.dat'
        with BinaryWriter(path, compressed=False) as w:
            w.write_header('WRONG_DESC', version=1)
            w.write_string('x')
        with self.assertRaisesRegex(
                ValueError,
                r"File header mismatch, expected 'RGLM_BINARY_WEIGHTS', found 'WRONG_DESC'\."):
            model_weights_read_file(path, compressed=False)

    def test_wrong_version_raises(self):
        path = Path(self.tmp_dir) / 'bad_version.dat'
        with BinaryWriter(path, compressed=False) as w:
            w.write_header(MODEL_WEIGHTS_FILE_HEADER_STR, version=99)
            w.write_string('x')
        with self.assertRaisesRegex(
                ValueError,
                r"File header version, expected '1' or '2', found '99'\."):
            model_weights_read_file(path, compressed=False)


class TestModelWeightsV2(unittest.TestCase):
    """
    The v2 model file (the configuration provenance is EMBEDDED — the normalized dump + the
    fingerprint, the leading body section) + the v1 backward-compat reader + the v2 corruption
    guard. No DB: the round-trip runs on a synthetic context (the SimpleNamespace idiom), the v1/v2
    bodies are hand-crafted with BinaryWriter.
    """

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(dir=str(CUSTOM_TMP_BASE))

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)

    @staticmethod
    def _v1_body(w):
        # A minimal v1 body (no config section).
        w.write_string("V1_NAME")
        w.write_u32(20)
        w.write_f32(0.05)
        w.write_u64(100)
        w.write_f32(0.5)
        w.write_f32(1.5)
        w.write_f32(2.25)
        w.write_string("CONVERGED_MIN_GRAD")
        w.write_u32(7)
        w.write_f32(0.01)
        w.write_f32(1e-6)
        w.write_u32(10)
        w.write_f32(1.0)
        w.write_f32(0.5)
        w.write_f32(0.0025)
        w.write_string("V1_FS")
        w.write_u8(0)  # no intercept
        w.write_u8(0)  # no mobility set
        w.write_u8(0)  # no pattern set
        w.write_array(np.array([0, 1, 2], dtype=np.uint32))
        w.write_array(np.array([0.1, 0.2, 0.3], dtype=np.float32))

    def test_v1_file_loads_without_config(self):
        """
        The backward-compat reader: a v1 file loads fine and the config provenance fields stay None.
        """
        path = Path(self.tmp_dir) / 'v1_model.dat'
        with BinaryWriter(path, compressed=False) as w:
            w.write_header(MODEL_WEIGHTS_FILE_HEADER_STR, version=1)
            self._v1_body(w)
        mw = model_weights_read_file(path, compressed=False)
        self.assertEqual(mw.version, 1)
        self.assertEqual(mw.name, "V1_NAME")
        self.assertEqual(mw.config_dump, None)
        self.assertEqual(mw.config_checksum, None)

    def _synthetic_ctx(self):
        # The writer touches only these attributes (a SimpleNamespace stand-in for the LMContext;
        # the cfg's model_dump_json is a fixed string so the test is deterministic).
        dump = '{"name": "SYNTH_C2", "marker": "SYNTH"}'
        cfg = SimpleNamespace(
            name="SYNTH_C2",
            empty_count=20,
            stat_model=SimpleNamespace(logit_clipping=0.05),
            model_dump_json=lambda indent=4: dump,
        )
        return SimpleNamespace(
            cfg=cfg,
            config_checksum=hashlib.sha3_256(dump.encode()).hexdigest(),
            training_pop_stats={'count': 100, 'mean': 0.5,
                                'std_dev': 1.5, 'variance': 2.25},
            opt_info={'reason': 'CONVERGED_MIN_GRAD', 'iters': 7,
                      'f': 0.01, 'g_norm': 1e-6},
            vld_metrics={'vld_samples': 10, 'vld_rmse_y': 1.0,
                         'vld_mae_y': 0.5, 'vld_loss': 0.0025},
            feature_set=FeatureSet("SYNTH_FS", None, None, None),
            iwmap_feature_offset=np.array([0, 1, 2], dtype=Index),
            w_dense=np.array([0.1, 0.2, 0.3], dtype=np.float32),
        ), dump

    def test_v2_roundtrip_synthetic_ctx(self):
        """
        Write v2 from the synthetic context, read it back: every field matches, the embedded config
        provenance round-trips.
        """
        ctx, dump = self._synthetic_ctx()
        path = Path(self.tmp_dir) / 'v2_model.dat'
        model_weights_write_file(ctx, path, compressed=False)
        mw = model_weights_read_file(path, compressed=False)
        self.assertEqual(mw.version, MODEL_WEIGHTS_FILE_HEADER_VER)
        self.assertEqual(mw.version, 2)
        self.assertEqual(mw.name, "SYNTH_C2")
        self.assertEqual(mw.ec, 20)
        self.assertEqual(mw.opt_info['reason'], 'CONVERGED_MIN_GRAD')
        self.assertEqual(mw.training_pop_stats['count'], 100)
        self.assertEqual(mw.vld_metrics['vld_samples'], 10)
        self.assertEqual(mw.feature_set.name, "SYNTH_FS")
        np.testing.assert_array_equal(mw.iwmap_feature_offset,
                                      ctx.iwmap_feature_offset)
        np.testing.assert_array_equal(mw.w_dense, ctx.w_dense)
        # The single source: the embedded dump + the fingerprint.
        self.assertEqual(mw.config_dump, dump)
        self.assertEqual(mw.config_checksum, ctx.config_checksum)

    def test_v2_write_emits_no_config_sidecar(self):
        """
        The v2 write emits NO <output>.config.json sidecar (the provenance is EMBEDDED in the model
        file): the shipped artifact is the model file + its own .SHA3-256 sidecar, and the
        fingerprint covers the normalized dump.
        """
        ctx, dump = self._synthetic_ctx()
        path = Path(self.tmp_dir) / 'v2_no_sidecar.dat'
        model_weights_write_file(ctx, path, compressed=True)

        config_path = path.with_suffix(".config.json")
        self.assertFalse(config_path.exists(),
                         f"Config record must not exist, found at {config_path}")
        self.assertFalse(
            (path.parent / (path.name + ".config.json.SHA3-256")).exists(),
            "The record sidecar must be gone with the record")
        # The model file's own sidecar verifies (it covers the v2 content, config section included).
        self.assertTrue(verify_sha3_256_sidecar(path),
                        "Checksum verification failed for saved model")
        # The fingerprint semantics: config_checksum == sha3_256 of the normalized dump (the
        # writer's own normalization: the utf-8-encoded dump).
        self.assertEqual(ctx.config_checksum,
                         hashlib.sha3_256(
                             ctx.cfg.model_dump_json(indent=4).encode()
                         ).hexdigest())

    def test_v2_config_checksum_mismatch_raises(self):
        """
        A v2 file whose stored checksum does not cover the embedded dump is corrupted: the sentinel raises.
        """
        path = Path(self.tmp_dir) / 'v2_bad_checksum.dat'
        with BinaryWriter(path, compressed=False) as w:
            w.write_header(MODEL_WEIGHTS_FILE_HEADER_STR, version=2)
            w.write_string("deadbeef" * 8)  # a sentinel that covers NOTHING
            w.write_string('{"name": "SYNTH_C2"}')
        with self.assertRaisesRegex(
                ValueError,
                r"Config section checksum mismatch, expected 'deadbeef.*', "
                r"recomputed '[0-9a-f]{64}'\."):
            model_weights_read_file(path, compressed=False)


if __name__ == '__main__':
    unittest.main()
