#
# test_lm_worker_full_chain.py
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
# How to run the full worker chain unit tests.
#
# Run from the workspace root (the directory containing .venv and src).
#
# -0- Activate the environment.
#
# $ source .venv/bin/activate
#
# -1- Run the tests (a live regab DB is required; SKIP_REGAB_DB=1
#     skips the DB-gated tests, as in test_regab. LONG=1 enables the
#     long-running A2050 chain on rlm_03).
#
# time python3 -m unittest twolm.test.test_lm_worker_full_chain
#

import unittest
import os
import tempfile
import shutil
import hashlib
import re

import numpy as np

from unittest import skipUnless
from unittest.mock import patch
from io import StringIO
from pathlib import Path

from twolm.state_machine import Verbosity
from twolm.logistic_model import LogisticModel
from twolm.binio import BinaryWriter, verify_sha3_256_sidecar
from twolm.model_weights import model_weights_read_file, MODEL_WEIGHTS_FILE_HEADER_STR
from twolm.rlm_client import make_evaluation_function
from twolm.rlm_gradient import sigmoid
from twolm.test.paths import WORKSPACE_ROOT, CUSTOM_TMP_BASE


def _masked_report_hash(report_text):
    # The file report embeds datetime.now(); mask the date so the hash is stable.
    text = re.sub(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", "DATE", report_text)
    return hashlib.sha3_256(text.encode()).hexdigest()


class TestFullChainA2030(unittest.TestCase):
    """Tests the full Reversi Logistic Model chain on the A2030 configuration."""

    suppress_stdout_io = True

    def setUp(self):
        # The SKIP_REGAB_DB gate, as in test_regab — the full chain reads
        # training and validation positions from the regab database.
        if os.getenv('SKIP_REGAB_DB', '0') == '1':
            self.skipTest('SKIP_REGAB_DB=1: database tests skipped')

        if self.suppress_stdout_io:
            self.patcher_stdout = patch('sys.stdout', new=StringIO())
            self.mock_stdout = self.patcher_stdout.start()

        self.tmp_dir = tempfile.mkdtemp(dir=str(CUSTOM_TMP_BASE))
        self.json_config = str(WORKSPACE_ROOT / "src" / "twolm" / "test" / "data" / "rlm_04.json")

        self.rlm = LogisticModel(self.json_config,
                                 verbosity=Verbosity.HIGH,
                                 base_dir_override=self.tmp_dir)

    def tearDown(self):
        if self.suppress_stdout_io:
            self.patcher_stdout.stop()
        shutil.rmtree(self.tmp_dir)

    def test_full_worker_chain(self):
        """Run the full 15-level chain (CREATED through SAVE) on rlm_04."""
        ctx = self.rlm.context

        # Run the model chain (CREATED is step 0, SAVE is step 14).
        self.rlm.move_to_last()
        self.assertEqual(self.rlm.current_step, 14)
        self.assertEqual(self.rlm.current_worker_name, 'SAVE')

        # --- Validation metrics (exact goldens, bid [5] vld, 20000 samples) ---
        m = ctx.vld_metrics
        self.assertEqual(m['vld_samples'], 20000)
        self.assertEqual(m['vld_loss'], 0.00575742032378912)
        self.assertEqual(m['vld_mse_z'], 0.01151484064757824)
        self.assertEqual(m['vld_mae_z'], 0.0845922976732254)
        self.assertEqual(m['vld_mae_y'], 11.048789978027344)
        self.assertEqual(m['vld_mse_y'], 196.43809509277344)
        self.assertEqual(m['vld_rmse_y'], 14.015637397766113)

        # --- Training metrics (exact goldens, bid [6], 199932 samples) ---
        t = ctx.train_metrics
        self.assertEqual(t['train_samples'], 199932)
        self.assertEqual(t['train_mae_y'], 10.899353761577668)
        self.assertEqual(t['train_rmse_y'], 13.822995683195872)
        self.assertEqual(t['train_loss'], 0.00560641149058938)
        self.assertEqual(t['pop_mae_y'], 21.73034518830014)
        self.assertEqual(t['pop_rmse_y'], 26.406980394267364)
        self.assertEqual(t['pop_loss'], 0.020438173785805702)

        # --- Dense training metrics (exact goldens, D-105/M2: the w_dense
        #     forward pass — the shipped inference rules — on the training
        #     data; differs from the compressed pass on the 1923 positions
        #     touching below-cutoff (IC) configurations) ---
        td = ctx.train_dense_metrics
        self.assertEqual(td['train_dense_samples'], 199932)
        self.assertEqual(td['train_dense_mae_y'], 10.905119078281873)
        self.assertEqual(td['train_dense_rmse_y'], 13.831248070093375)
        self.assertEqual(td['train_dense_loss'], 0.0056069279089570045)

        # --- Training population statistics (exact goldens) ---
        p = ctx.training_pop_stats
        self.assertEqual(p['count'], 199932)
        self.assertEqual(p['mean'], -1.3912930396334753)
        self.assertEqual(p['std_dev'], 26.40698039426738)
        self.assertEqual(p['variance'], 697.3286135432216)

        # --- Optimization info (5-key dict) ---
        self.assertTrue(ctx.opt_info['converged'])
        self.assertEqual(ctx.opt_info['reason'], 'CONVERGED_MIN_GRAD')
        self.assertEqual(ctx.opt_info['iters'], 67)

        # --- Saved model file: exists, size, sha3_256, sidecar ---
        output_path = ctx.cfg.base_dir / ctx.cfg.output
        self.assertTrue(output_path.exists(), f"Output file not found at {output_path}")
        self.assertEqual(output_path.stat().st_size, 21603)
        self.assertEqual(
            hashlib.sha3_256(output_path.read_bytes()).hexdigest(),
            'bcf8d918979aaddba52ed2c9a80571f4fdc939a985ff4f3705510fa4f8010abb')
        self.assertTrue(verify_sha3_256_sidecar(output_path), "Checksum verification failed for saved model")

        # --- Read the file back using the client's read function ---
        mw = model_weights_read_file(output_path, compressed=True)

        # Metadata
        self.assertEqual(mw.version, 1)
        self.assertEqual(mw.name, ctx.cfg.name)
        self.assertEqual(mw.ec, ctx.cfg.regab_data_set.ec)
        self.assertAlmostEqual(mw.logit_clipping, ctx.cfg.stat_model.logit_clipping, places=5)

        # Training population statistics (float32 truncation by the file format)
        self.assertEqual(mw.training_pop_stats['count'], np.uint64(199932))
        self.assertEqual(float(mw.training_pop_stats['mean']), -1.3912930488586426)
        self.assertEqual(float(mw.training_pop_stats['std_dev']), 26.406980514526367)
        self.assertEqual(float(mw.training_pop_stats['variance']), 697.32861328125)

        # Optimization info (4 of the 5 context keys persisted; 'converged' is
        # derivable from 'reason')
        self.assertEqual(mw.opt_info['reason'], 'CONVERGED_MIN_GRAD')
        self.assertEqual(mw.opt_info['iters'], np.uint32(67))
        self.assertEqual(float(mw.opt_info['f']), 0.00560641149058938)
        self.assertEqual(float(mw.opt_info['g_norm']), 4.3686068238457665e-05)

        # Validation metrics (4 of the 7 context metrics persisted)
        self.assertEqual(mw.vld_metrics['vld_samples'], np.uint32(20000))
        self.assertEqual(float(mw.vld_metrics['vld_rmse_y']), 14.015637397766113)
        self.assertEqual(float(mw.vld_metrics['vld_mae_y']), 11.048789978027344)
        self.assertEqual(float(mw.vld_metrics['vld_loss']), 0.00575742032378912)

        # FeatureSet (the hash is a definitive structural check: names +
        # sorted mask contents, transitive over mset/pset)
        self.assertEqual(mw.feature_set.hash, 'ec4f15374a00b729629d62ee0eb4354cbf163950672b7a9db9f81375e40559ef')
        self.assertEqual(mw.feature_set.hash, ctx.feature_set.hash)

        # Core inference arrays
        np.testing.assert_array_equal(mw.iwmap_feature_offset, np.array([0, 1, 66, 6627], dtype=np.uint32))
        self.assertEqual(mw.w_dense.shape, (6627,))
        self.assertEqual(mw.w_dense.dtype, np.float32)
        self.assertEqual(
            hashlib.sha3_256(mw.w_dense.tobytes()).hexdigest(),
            '7ecdeba66d9f34b9396e199dd4a5933196131db497ff88fce726bcd75f1f4f37')
        np.testing.assert_array_equal(mw.w_dense, ctx.w_dense)

        # --- Log lines (captured stdout) ---
        logs = self.mock_stdout.getvalue()
        self.assertIn("Validation completed. Loss (MSE/2): 5.75742032e-03", logs)
        self.assertIn("Saving model weights to disk...", logs)
        self.assertIn("Model weights saved to", logs)

        # --- Analytics console report (exact pins) ---
        report = ctx.analytics_report
        self.assertIn("MODEL ANALYTICS REPORT: RGLM (Logistic) - Short-Long Test 04 (rlm_04.json)", report)
        self.assertIn("Loss (MSE/2)    | 5.6064e-03     | 5.6069e-03     | 5.7574e-03", report)
        self.assertIn("Population (baseline)  : RMSE 26.41  MAE 21.73  Loss 2.0438e-02", report)
        self.assertIn("Generalization Gap (RMSE)   : 0.18", report)
        self.assertIn("Substitution Delta (RMSE)   : 0.01", report)

        # --- Analytics file report (detailed_report: EDGE + LMC) ---
        report_path = ctx.cfg.base_dir / ctx.cfg.analytics.report_file_name
        self.assertTrue(report_path.exists(), f"Analytics report file not found at {report_path}")
        file_report = report_path.read_text(encoding='utf-8')
        self.assertIn("Creation Date               :", file_report)
        self.assertIn("PATTERN FEATURE: EDGE (fid=2)", file_report)
        self.assertIn("MOBILITY FEATURE: LMC (fid=1)", file_report)
        self.assertEqual(_masked_report_hash(file_report),
                         'd44557a8efd007f4634c2949a0cf9eca60d7b38f790c2bbd1e058245a4045a2e')

        # --- The client's Evaluation Function: bit-exact on 6 pinned training
        #     positions (rlm_04 has frequency_cut_off=10, so training positions
        #     touching below-cutoff configurations exercise the w_dense
        #     substitution slots) ---
        ef = make_evaluation_function(mw)
        expected_ef = {
            0: -37.12018585205078,
            1: -28.228458404541016,
            7: 45.391082763671875,
            123: 40.502410888671875,
            999: 16.26209259033203,
            len(ctx.positions) - 1: 23.326324462890625,
        }
        for i, y_expected in expected_ef.items():
            self.assertEqual(ef(ctx.positions[i]), y_expected, msg=f"EF mismatch at training position {i}")

        # The same EF on a validation position: rlm_04 validation (bid [5])
        # contains EDGE configurations unseen in training, so this pins the
        # w_dense substitution path (orbit weighted mean) end-to-end.
        self.assertEqual(ef(ctx.vld_positions[42]), 11.932792663574219)

    def test_second_instance_deterministic(self):
        """A second full run in the same base dir: byte-identical model file,
        6 cache hits (7 cache files; CONFIG re-stores its snapshot, so it is a
        'stored' line, not a 'hit')."""
        self.rlm.move_to_last()
        output_path = self.rlm.context.cfg.base_dir / self.rlm.context.cfg.output
        first_hash = hashlib.sha3_256(output_path.read_bytes()).hexdigest()

        rlm2 = LogisticModel(self.json_config,
                             verbosity=Verbosity.HIGH,
                             base_dir_override=self.tmp_dir)
        with patch('sys.stdout', new=StringIO()) as out2:
            rlm2.move_to_last()
        logs2 = out2.getvalue()

        second_hash = hashlib.sha3_256(output_path.read_bytes()).hexdigest()
        self.assertEqual(second_hash, first_hash)
        self.assertEqual(logs2.count("Cache successfully loaded and validated"), 6)
        self.assertNotIn("Extracted", logs2)
        self.assertNotIn("established successfully", logs2)


@skipUnless(os.environ.get('LONG') == '1', "Skipping long-running test (set LONG=1 to run)")
class TestFullChainA2050(unittest.TestCase):
    """Tests the full Reversi Logistic Model chain on the A2050 configuration
    (the production endgame-solver model family: A2 + ec*10; A2050 = ec 20)."""

    suppress_stdout_io = False

    def setUp(self):
        # The SKIP_REGAB_DB gate, as in test_regab — the full chain reads
        # training and validation positions from the regab database.
        if os.getenv('SKIP_REGAB_DB', '0') == '1':
            self.skipTest('SKIP_REGAB_DB=1: database tests skipped')

        if self.suppress_stdout_io:
            self.patcher_stdout = patch('sys.stdout', new=StringIO())
            self.mock_stdout = self.patcher_stdout.start()

        self.tmp_dir = tempfile.mkdtemp(dir=str(CUSTOM_TMP_BASE))
        self.json_config = str(WORKSPACE_ROOT / "src" / "twolm" / "test" / "data" / "rlm_03.json")

        self.rlm = LogisticModel(self.json_config,
                                 verbosity=Verbosity.HIGH,
                                 base_dir_override=self.tmp_dir)

    def tearDown(self):
        if self.suppress_stdout_io:
            self.patcher_stdout.stop()
        shutil.rmtree(self.tmp_dir)

    def test_full_worker_chain(self):
        """Run the full 15-level chain (CREATED through SAVE) on rlm_03.
        Long-running: ~10 minutes (1999179 training samples, 397 lbfgs iters)."""
        ctx = self.rlm.context

        # Run the model chain (CREATED is step 0, SAVE is step 14).
        self.rlm.move_to_last()
        self.assertEqual(self.rlm.current_step, 14)
        self.assertEqual(self.rlm.current_worker_name, 'SAVE')

        # --- Validation metrics (exact goldens, bid [6] vld, 199932 samples) ---
        m = ctx.vld_metrics
        self.assertEqual(m['vld_samples'], 199932)
        self.assertEqual(m['vld_loss'], 0.001578879076987505)
        self.assertEqual(m['vld_mse_z'], 0.00315775815397501)
        self.assertEqual(m['vld_mae_z'], 0.04321568086743355)
        self.assertEqual(m['vld_mae_y'], 5.644496440887451)
        self.assertEqual(m['vld_mse_y'], 53.86997604370117)
        self.assertEqual(m['vld_rmse_y'], 7.339616775512695)

        # --- Training metrics (exact goldens, bid [3], 1999179 samples) ---
        t = ctx.train_metrics
        self.assertEqual(t['train_samples'], 1999179)
        self.assertEqual(t['train_mae_y'], 5.396253447071691)
        self.assertEqual(t['train_rmse_y'], 7.015377800787937)
        self.assertEqual(t['train_loss'], 0.001444403431378305)
        self.assertEqual(t['pop_mae_y'], 21.758215006979484)
        self.assertEqual(t['pop_rmse_y'], 26.417003454424307)
        self.assertEqual(t['pop_loss'], 0.020453333854675293)

        # --- Dense training metrics (exact goldens, D-105/M2: rlm_03 has
        #     frequency_cut_off=1, so the dense pass matches the compressed
        #     one up to the f32 rounding of w_dense — delta "-0.00") ---
        td = ctx.train_dense_metrics
        self.assertEqual(td['train_dense_samples'], 1999179)
        self.assertEqual(td['train_dense_mae_y'], 5.396253444189108)
        self.assertEqual(td['train_dense_rmse_y'], 7.015377798958687)
        self.assertEqual(td['train_dense_loss'], 0.0014424461405724287)

        # --- Training population statistics (exact goldens) ---
        p = ctx.training_pop_stats
        self.assertEqual(p['count'], 1999179)
        self.assertEqual(p['mean'], -1.3259453005458741)
        self.assertEqual(p['std_dev'], 26.417003454424318)
        self.assertEqual(p['variance'], 697.8580715110664)

        # --- Optimization info (5-key dict) ---
        self.assertTrue(ctx.opt_info['converged'])
        self.assertEqual(ctx.opt_info['reason'], 'CONVERGED_MIN_GRAD')
        self.assertEqual(ctx.opt_info['iters'], 397)

        # --- Analytics console report (exact pins; no detailed tables) ---
        console_report = ctx.analytics_report
        self.assertIn("MODEL ANALYTICS REPORT: RGLM (Logistic) - Long Test 03 (rlm_03.json)", console_report)
        self.assertIn("Loss (MSE/2)    | 1.4444e-03     | 1.4424e-03     | 1.5789e-03", console_report)
        self.assertIn("Population (baseline)  : RMSE 26.42  MAE 21.76  Loss 2.0453e-02", console_report)
        self.assertIn("Generalization Gap (RMSE)   : 0.32", console_report)
        self.assertIn("Substitution Delta (RMSE)   : -0.00", console_report)
        self.assertNotIn("FEATURE SET SUMMARY:", console_report)
        self.assertNotIn("MOBILITY FEATURES DETAILS:", console_report)

        # --- Analytics file report (detailed_report: XEDGE) ---
        report_path = ctx.cfg.base_dir / ctx.cfg.analytics.report_file_name
        self.assertTrue(report_path.exists(), f"Analytics report file not found at {report_path}")
        file_report = report_path.read_text(encoding='utf-8')
        self.assertIn("Creation Date               :", file_report)
        self.assertIn("PATTERN FEATURE: XEDGE", file_report)
        self.assertEqual(_masked_report_hash(file_report),
                         '57f9766b7e5115903319f3387b192e490c71674eebc2e2c199040579b5fad83a')

        # --- Saved model file: exists, size, sha3_256, sidecar ---
        output_path = ctx.cfg.base_dir / ctx.cfg.output
        self.assertTrue(output_path.exists(), f"Output file not found at {output_path}")
        self.assertEqual(output_path.stat().st_size, 515042)
        self.assertEqual(
            hashlib.sha3_256(output_path.read_bytes()).hexdigest(),
            '3ad1805815c536e4506b0804b5be9e8662de53402c37fc3268c8dbbbb6847ff4')
        self.assertTrue(verify_sha3_256_sidecar(output_path), "Checksum verification failed for saved model")

        # --- Read the file back using the client's read function ---
        mw = model_weights_read_file(output_path, compressed=True)

        # Metadata
        self.assertEqual(mw.version, 1)
        self.assertEqual(mw.name, ctx.cfg.name)
        self.assertEqual(mw.ec, ctx.cfg.regab_data_set.ec)
        self.assertAlmostEqual(mw.logit_clipping, ctx.cfg.stat_model.logit_clipping, places=5)

        # Training population statistics (float32 truncation by the file format)
        self.assertEqual(mw.training_pop_stats['count'], np.uint64(1999179))
        self.assertEqual(float(mw.training_pop_stats['mean']), -1.325945258140564)
        self.assertEqual(float(mw.training_pop_stats['std_dev']), 26.417003631591797)
        self.assertEqual(float(mw.training_pop_stats['variance']), 697.8580932617188)

        # Optimization info (4 of the 5 context keys persisted; 'converged' is
        # derivable from 'reason')
        self.assertEqual(mw.opt_info['reason'], 'CONVERGED_MIN_GRAD')
        self.assertEqual(mw.opt_info['iters'], np.uint32(397))
        self.assertEqual(float(mw.opt_info['f']), 0.001444403431378305)
        self.assertEqual(float(mw.opt_info['g_norm']), 7.43771579436725e-06)

        # Validation metrics (4 of the 7 context metrics persisted)
        self.assertEqual(mw.vld_metrics['vld_samples'], np.uint32(199932))
        self.assertEqual(float(mw.vld_metrics['vld_rmse_y']), 7.339616775512695)
        self.assertEqual(float(mw.vld_metrics['vld_mae_y']), 5.644496440887451)
        self.assertEqual(float(mw.vld_metrics['vld_loss']), 0.001578879076987505)

        # FeatureSet (13 features: intercept + LMC + 11 patterns)
        self.assertEqual(mw.feature_set.hash, '2c8bb32b40eff2c1e22b992e56b8d60fb51c17afb81d48f9414aef46c349e43d')
        self.assertEqual(mw.feature_set.hash, ctx.feature_set.hash)

        # Core inference arrays (14 boundary entries for the 13 features)
        np.testing.assert_array_equal(
            mw.iwmap_feature_offset,
            np.array([0, 1, 66, 59115, 118164, 124725, 144408, 150969, 151050,
                      157611, 157854, 158583, 160770, 167331], dtype=np.uint32))
        self.assertEqual(mw.w_dense.shape, (167331,))
        self.assertEqual(mw.w_dense.dtype, np.float32)
        self.assertEqual(
            hashlib.sha3_256(mw.w_dense.tobytes()).hexdigest(),
            'a012689f70ef8a492ce0fbf374a49e79e62f758a83fce94540a459bd28b527fc')
        np.testing.assert_array_equal(mw.w_dense, ctx.w_dense)

        # --- The client's Evaluation Function: bit-exact on 6 pinned
        #     training positions (rlm_03 has frequency_cut_off=1, so every
        #     training configuration is confirmed: dense == compressed) ---
        ef = make_evaluation_function(mw)
        expected_ef = {
            0: 7.2613525390625,
            5: -32.98143768310547,
            123: 40.5123291015625,
            555: 24.14972686767578,
            9999: -19.389434814453125,
            len(ctx.positions) - 1: 57.8465576171875,
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
                r"File header version, expected '1', found '99'\."):
            model_weights_read_file(path, compressed=False)


if __name__ == '__main__':
    unittest.main()
