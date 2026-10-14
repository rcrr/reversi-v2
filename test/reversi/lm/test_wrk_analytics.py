#
# test_wrk_analytics.py
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
# How to run the wrk_analytics unit tests.
#
# Run from the workspace root (the directory containing .venv and src).
#
# -0- Activate the environment.
#
# $ source .venv/bin/activate
#
# -1- Run the tests (a live regab DB is required; LONG=1 for the TestLMWorkerAnalytics class;
# SKIP_REGAB_DB=1 skips the DB-gated tests as in test_regab, see test.reversi.tags).
#
# time python3 -m unittest test.reversi.lm.test_wrk_analytics
#

import hashlib
import math
import re
import tempfile
import unittest

from unittest.mock import patch
from io import StringIO
from pathlib import Path

import numpy as np

from reversi.lm.hlp_analytics import hlp_analytics_format_file_report
from reversi.lm.hlp_anova import hlp_anova_adherence
from reversi.tools.state_machine import Verbosity
from reversi.lm.logistic_model import LogisticModel
from test.reversi.closecheck import assert_close
from test.reversi.paths import WORKSPACE_ROOT, CUSTOM_TMP_BASE
from test.reversi.tags import db_gate, db_long_gate
from reversi.index import Index
from reversi.index import ExtendedIndex
from reversi.tools.state_machine import Relevance

import json5
import pandas as pd
from types import SimpleNamespace

from reversi.regab import RegabDBConnection, RegabDataSet, regab_store_data_set_to_file
from reversi.lm.hlp_analytics import (hlp_analytics_format_console_report,
                                      hlp_analytics_compute_training_dense_metrics,
                                      AnalyticsTrainingDenseResult)
from reversi.lm.hlp_gradient import sigmoid
from reversi.lm.hlp_zed import hlp_zed_fun_factory
from reversi.lm.wrk_analytics import _up as _analytics_up
from reversi.lm.wrk_analytics import _down as _analytics_down


def _masked_report_hash(text):
    """
    sha3_256 of the report text with the Creation Date and the config fingerprint hex masked out —
    the report embeds datetime.now() and the run's base_dir, so the masked hash is the stable golden.
    """
    masked = re.sub(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", "DATE", text)
    masked = re.sub(r"(Config SHA3-256\s*:\s*)[0-9a-f]{64}", r"\1HASH", masked)
    return hashlib.sha3_256(masked.encode("utf-8")).hexdigest()


class TestLMWorkerAnalytics(unittest.TestCase):
    """
    The ANALYTICS worker integration + the exact rlm_02 goldens. The level is pure compute (no cache
    file — the rlmwf_15 slot stays unused), so the second-instance test pins the recomputation as
    deterministic. DB-gated (the setUp runs the 14-level chain to VALIDATE).
    """

    def setUp(self):
        # The SKIP_REGAB_DB gate, as in test_regab — the worker tests need the live regab DB (the
        # setUp moves to VALIDATE, which runs the whole 14-level chain on a fresh base dir).
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

        # Move up to VALIDATE to ensure full pipeline consistency
        self.rlm.move_to_step('VALIDATE')
        self.assertEqual(self.rlm.current_step, 14)

    def tearDown(self):
        if getattr(self, 'patcher_stdout', None) is not None:
            self.patcher_stdout.stop()
        if getattr(self, '_tmp', None) is not None:
            self._tmp.cleanup()

    def test_analytics_report_goldens(self):
        """
        First run to ANALYTICS on rlm_02 (the bid [6,7] training model, 199952 samples): the
        7-metric + 4-key dense dicts, the console report, the report file and the INFO log lines.
        """
        # Pre-state: the ANALYTICS blackboard fields are not set yet.
        self.assertIsNone(self.rlm.context.analytics_report)
        self.assertIsNone(self.rlm.context.train_metrics)
        self.assertIsNone(self.rlm.context.train_dense_metrics)

        self.rlm.move_to_step('ANALYTICS')
        self.assertEqual(self.rlm.current_step, 15)
        self.assertEqual(self.rlm.current_worker_name, 'ANALYTICS')

        met = self.rlm.context.train_metrics
        self.assertIsNotNone(met)
        self.assertEqual(set(met), {'train_mae_y', 'train_rmse_y', 'train_loss',
                                    'train_samples', 'pop_mae_y', 'pop_rmse_y',
                                    'pop_loss'})
        assert_close(self, met['train_mae_y'], 12.346794566613694, 'train_mae_y')
        assert_close(self, met['train_rmse_y'], 15.58872172931622, 'train_rmse_y')
        # f32-quantized (the OPTIMIZE objective f) — bit-exact
        self.assertEqual(met['train_loss'], 0.00712497066706419)
        self.assertEqual(met['train_samples'], 199952)
        assert_close(self, met['pop_mae_y'], 21.729816221648974, 'pop_mae_y')
        assert_close(self, met['pop_rmse_y'], 26.40637507956623, 'pop_rmse_y')
        assert_close(self, met['pop_loss'], 0.020437248051166534, 'pop_loss')

        # The dense-pass dict: the shipped inference rules (w_dense) on the training data. rlm_02
        # has frequency_cut_off=1, so the dense values match the compressed ones up to the f32
        # rounding of w_dense.
        dmet = self.rlm.context.train_dense_metrics
        self.assertIsNotNone(dmet)
        self.assertEqual(set(dmet), {'train_dense_mae_y', 'train_dense_rmse_y',
                                     'train_dense_loss', 'train_dense_samples'})
        assert_close(self, dmet['train_dense_mae_y'], 12.346794548249868, 'train_dense_mae_y')
        assert_close(self, dmet['train_dense_rmse_y'], 15.58872171282352, 'train_dense_rmse_y')
        assert_close(self, dmet['train_dense_loss'], 0.00712234852835536, 'train_dense_loss')
        self.assertEqual(dmet['train_dense_samples'], 199952)

        # The console report (header only — no tables, no date) is stored on the context and logged
        # line by line.
        rep = self.rlm.context.analytics_report
        self.assertIsInstance(rep, str)
        self.assertIn("MODEL ANALYTICS REPORT: RGLM (Logistic) - Unit Test 02 (rlm_02.json)", rep)
        self.assertIn("  Total Parameters (W)        : 2,981", rep)
        self.assertIn("  Dense Parameters (K)        : 6,588", rep)
        self.assertIn("Loss (MSE/2)    | 7.1250e-03     | 7.1223e-03     | 7.0079e-03", rep)
        self.assertIn("Population (baseline)  : RMSE 26.41  MAE 21.73  Loss 2.0437e-02", rep)
        self.assertIn("Generalization Gap (RMSE)   : -0.13", rep)
        self.assertIn("Substitution Delta (RMSE)   : -0.00", rep)
        self.assertNotIn("Creation Date", rep)
        self.assertNotIn("PATTERN FEATURE", rep)

        # The complete file report is written to base_dir under the configured name; rlm_02 has no
        # mobility features, so the MOBILITY section is empty, EDGE prints its rows (it is in the
        # detailed_report list) and DIAG3 omits them.
        report_path = self.tmp_dir / "model_analytics_report.txt"
        self.assertTrue(report_path.exists())
        content = report_path.read_text(encoding="utf-8")
        self.assertIn("Creation Date", content)
        self.assertIn("MOBILITY FEATURES DETAILS:", content)
        self.assertNotIn("MOBILITY FEATURE:", content)
        self.assertIn("PATTERN FEATURE: EDGE (fid=0)", content)
        self.assertIn("PATTERN FEATURE: DIAG3 (fid=1)", content)
        self.assertEqual(content.count("(Table rows omitted"), 1)
        # rlm_02 has no su_analysis section (the default FALSE): the report is unchanged — no SU
        # columns, no consistency line.
        self.assertNotIn("PROBABILITY", content)
        self.assertNotIn("SU Sample Consistency", content)
        # rlm_02 has NO intercept (EDGE is fid 0): no INTERCEPT section.
        self.assertNotIn("INTERCEPT:", content)
        self.assertEqual(_masked_report_hash(content),
                         "e0d3d22ab116b3381e79802bafdfdb418da84e72bd14cb3e79550d2a25b4a6f6")

        logs = self.mock_stdout.getvalue()
        self.assertIn("Generating model analytics report...", logs)
        self.assertIn("Computing metrics on the training set...", logs)
        self.assertIn("Analytics report saved to ", logs)
        self.assertNotIn("PATTERN FEATURE", logs)

    def test_train_dense_rn_series(self):
        """
        The published dense residual series: mean(|rn|) re-derives the dense MAE golden from the
        series itself (the independent cross-check).
        """
        self.rlm.move_to_step('ANALYTICS')
        dmet = self.rlm.context.train_dense_metrics
        rn = self.rlm.context.train_dense_rn
        self.assertIsInstance(rn, np.ndarray)
        self.assertEqual(rn.shape, (dmet['train_dense_samples'],))
        self.assertEqual(float(np.mean(np.abs(rn))), dmet['train_dense_mae_y'])

    def test_second_instance_deterministic(self):
        """
        A second instance on the same base dir recomputes identical metrics and reports (no cache
        file) while the 6 cache levels hit and the DB is not re-extracted.
        """
        self.rlm.move_to_step('ANALYTICS')
        met = self.rlm.context.train_metrics
        dmet = self.rlm.context.train_dense_metrics
        rep = self.rlm.context.analytics_report
        self.assertIsNotNone(met)

        # Create a completely new instance pointing to the same base dir
        rlm2 = LogisticModel(self.json_config,
                             verbosity=Verbosity.HIGH,
                             base_dir_override=self.tmp_dir)

        # Clear the StringIO buffer to only capture logs from the second run
        self.mock_stdout.seek(0)
        self.mock_stdout.truncate(0)

        rlm2.move_to_step('ANALYTICS')
        self.assertEqual(rlm2.current_step, 15)

        logs = self.mock_stdout.getvalue()
        # The 6 cache_manager levels (POSITIONS, INDEXES, WMAPS, DESIGN_MTR, GENERATE,
        # VLD_POSITIONS) hit; CONFIG and the OPTIMIZE checkpoint have their own load flows; FEATURES
        # / ZED / GRADIENT / VALIDATE / ANALYTICS have no cache file and recompute.
        self.assertEqual(logs.count("Cache successfully loaded and validated"), 6)
        self.assertNotIn("Extracted", logs,
                         "DB was queried even though a valid cache existed.")
        self.assertNotIn("established successfully", logs,
                         "DB connection was opened even though a valid cache existed.")

        # ANALYTICS recomputes from the cached artifacts — deterministic.
        self.assertEqual(rlm2.context.train_metrics, met)
        self.assertEqual(rlm2.context.train_dense_metrics, dmet)
        self.assertEqual(rlm2.context.analytics_report, rep)
        self.assertTrue((self.tmp_dir / "model_analytics_report.txt").exists())

    def test_down_clears_analytics_attributes(self):
        """
        Pin the _down scope: back to VALIDATE clears all four context attributes (the report file
        itself is not removed).
        """
        self.rlm.move_to_step('ANALYTICS')
        self.assertIsNotNone(self.rlm.context.train_metrics)
        self.assertIsNotNone(self.rlm.context.train_dense_metrics)
        self.assertIsNotNone(self.rlm.context.analytics_report)
        self.assertIsNotNone(self.rlm.context.train_dense_rn)

        self.rlm.move_to_step(14)
        self.assertEqual(self.rlm.current_step, 14)
        self.assertEqual(self.rlm.current_worker_name, 'VALIDATE')
        self.assertIsNone(self.rlm.context.train_metrics)
        self.assertIsNone(self.rlm.context.train_dense_metrics)
        self.assertIsNone(self.rlm.context.analytics_report)
        self.assertIsNone(self.rlm.context.train_dense_rn)
        # The report file is a base_dir artifact — _down does not unlink it.
        self.assertTrue((self.tmp_dir / "model_analytics_report.txt").exists())


class TestLMWorkerAnalyticsMobility(unittest.TestCase):
    """
    The mobility-table branch of the file report, using rlm_01.json — the only fixture that
    exercises the mobility table helper end-to-end: the LMC table (65 rows) + DIAG3 print their
    rows, CORE omits them (detailed_report ["DIAG3", "LMC"]).
    """

    def setUp(self):
        # The SKIP_REGAB_DB gate, as in test_regab — the worker tests need the live regab DB (the
        # setUp moves to VALIDATE, which runs the whole 14-level chain on a fresh base dir).
        db_gate(self)  # the SKIP_REGAB_DB gate

        # Patch stdout to keep test output clean and capture logs
        self.patcher_stdout = patch('sys.stdout', new=StringIO())
        self.mock_stdout = self.patcher_stdout.start()

        # TemporaryDirectory created FIRST so a mid-setup failure still leaves a cleanable temp dir.
        self._tmp = tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE))
        self.tmp_dir = Path(self._tmp.name)
        self.json_config = str(WORKSPACE_ROOT / "test" / "reversi" / "data" / "rlm_01.json")

        self.rlm = LogisticModel(self.json_config,
                                 verbosity=Verbosity.HIGH,
                                 base_dir_override=self.tmp_dir)

        # Move up to VALIDATE to ensure full pipeline consistency
        self.rlm.move_to_step('VALIDATE')
        self.assertEqual(self.rlm.current_step, 14)

    def tearDown(self):
        if getattr(self, 'patcher_stdout', None) is not None:
            self.patcher_stdout.stop()
        if getattr(self, '_tmp', None) is not None:
            self._tmp.cleanup()

    def test_mobility_and_pattern_tables(self):
        """
        First run to ANALYTICS on rlm_01 (frequency_cut_off=2 — 5/10 training positions touch IC
        slots): the 7-metric + 4-key dense goldens + the mobility/pattern tables + the file-report hash.
        """
        self.rlm.move_to_step('ANALYTICS')
        self.assertEqual(self.rlm.current_step, 15)

        met = self.rlm.context.train_metrics
        self.assertIsNotNone(met)
        assert_close(self, met['train_mae_y'], 9.874833279184258e-05, 'train_mae_y')
        assert_close(self, met['train_rmse_y'], 0.00013206900478667877, 'train_rmse_y')
        # f32-quantized (the OPTIMIZE objective f) — bit-exact
        self.assertEqual(met['train_loss'], 4.704681197571781e-13)
        self.assertEqual(met['train_samples'], 10)
        assert_close(self, met['pop_mae_y'], 15.6, 'pop_mae_y')
        assert_close(self, met['pop_rmse_y'], 18.39565166010707, 'pop_rmse_y')
        assert_close(self, met['pop_loss'], 0.009125067852437496, 'pop_loss')

        # The dense pass on the same 10 positions: the compressed fit is exact (rmse 0.00) but the
        # shipped model substitutes 5 below-cutoff configurations — the Substitution Delta row reads 3.36.
        dmet = self.rlm.context.train_dense_metrics
        assert_close(self, dmet['train_dense_mae_y'], 1.854193878173828, 'train_dense_mae_y')
        assert_close(self, dmet['train_dense_rmse_y'], 3.3556084739848866, 'train_dense_rmse_y')
        assert_close(self, dmet['train_dense_loss'], 0.0003036324051208794, 'train_dense_loss')
        self.assertEqual(dmet['train_dense_samples'], 10)

        report_path = self.tmp_dir / "model_analytics_report.txt"
        self.assertTrue(report_path.exists())
        content = report_path.read_text(encoding="utf-8")
        # The LMC table prints its rows (LMC is in the detailed_report list), DIAG3 its rows too,
        # CORE omits them — exactly one omitted-rows line in the whole report.
        self.assertIn("MOBILITY FEATURES DETAILS:", content)
        self.assertIn("MOBILITY FEATURE: LMC (fid=1)", content)
        self.assertIn("PATTERN FEATURE: DIAG3 (fid=2)", content)
        self.assertIn("PATTERN FEATURE: CORE (fid=3)", content)
        self.assertEqual(content.count("(Table rows omitted"), 1)
        # rlm_01 has no su_analysis section (the default FALSE): the report is unchanged — no SU
        # columns, no consistency line.
        self.assertNotIn("PROBABILITY", content)
        self.assertNotIn("SU Sample Consistency", content)
        self.assertEqual(_masked_report_hash(content),
                         "a246cf9df0240258d44ebe0ac21cac4b533f0b89cbbe6f954823f32fc9a632ff")

        logs = self.mock_stdout.getvalue()
        self.assertIn("Optimization Status         : CONVERGED_MIN_GRAD (16 iters)", logs)
        self.assertIn("Generalization Gap (RMSE)   : 23.87", logs)
        self.assertIn("Substitution Delta (RMSE)   : 3.36", logs)


class _MockCtx:
    """
    The NO-DB mock context for the SU sample columns: the real rlm_00 cfg + feature_set (the facade
    run to FEATURES) + the SYNTHETIC wmap / indexes / game values / corpus marginal.
    """

    def __init__(self, cfg, feature_set, indexes, game_values, tables,
                 n_features, n_dense, iwmap_feature_offset):
        self.cfg = cfg
        self.feature_set = feature_set
        self.hlp_indexes = type('I', (), {'indexes': indexes})()
        self.game_values = game_values
        self.su_analysis_tables = tables
        self.wmap = np.zeros((n_dense, 3), dtype=ExtendedIndex)
        name_to_fid = {f.name: i
                       for i, f in enumerate(feature_set.features)}
        self.wmap[0, :] = (0, 0, 1)  # the intercept slot
        for (name, _c0, _c1, nc, _ni) in feature_set.feature_blocks:
            fid = name_to_fid[name]
            for c in range(nc):
                self.wmap[iwmap_feature_offset[fid] + c, :] = (
                    fid, c, 1)
        self.wmap_fallback = None
        self.iwmap = np.arange(n_dense, dtype=ExtendedIndex)
        self.w = 0.001 * (np.arange(n_dense, dtype=np.float64) + 1.0)
        self.w_dense = self.w.copy()
        self.iwmap_feature_offset = iwmap_feature_offset
        self.feature_w_ranges = np.full((n_features, 2), -1,
                                        dtype=ExtendedIndex)
        self.config_checksum = "ab" * 32
        self.train_metrics = {}
        self.train_dense_metrics = {}
        self.vld_metrics = {}
        self.opt_info = {}


def _make_su_ctx(tmp, total_positions, corpus_kind='match'):
    """
    The mock ctx over the real rlm_00 campaign (the facade runs to FEATURES, the idiom): 100
    synthetic training positions (the 2-code concentration — code 0 the first 50, code 1 the rest,
    every sub-variable), the complete synthetic wmap (freq 1 — every row STATUS C), and the
    synthetic corpus marginal: 'match' (3x the training counts, the TV 0.0 match), 'marginal' (the
    9-count 0 -> 1 LMC shift, the TV 0.03), 'deviating' (the one-point LMC mass, the chi-square inf,
    the TV 0.5).
    """
    rlm = LogisticModel(str(WORKSPACE_ROOT / "test" / "reversi" /
                            "data" / "rlm_00.json"),
                        verbosity=Verbosity.NONE,
                        base_dir_override=tmp)
    rlm.run("FEATURES")
    cfg = rlm.context.cfg
    fset = rlm.context.feature_set
    blocks = fset.feature_blocks
    n_positions = 100
    max_col = max(c1 for (_n, c0, c1, _nc, _ni) in blocks)
    indexes = np.zeros((n_positions, max_col), dtype=Index)
    sub_counts = {}
    for (name, c0, c1, n_conf, n_inst) in blocks:
        for i in range(n_inst):
            # The 2-code concentration: 50 positions per code.
            indexes[:, c0 + i] = (
                np.arange(n_positions) >= 50).astype(Index)
            sub_counts[(name, i)] = {0: 50, 1: 50}
    marginal = []
    for (name, c0, c1, n_conf, n_inst) in blocks:
        for i in range(n_inst):
            base = {c: 3 * n
                    for c, n in sub_counts[(name, i)].items()}
            if name == 'LMC' and i == 0 and corpus_kind == 'marginal':
                base[0] -= 9
                base[1] = base.get(1, 0) + 9
            if name == 'LMC' and i == 0 and corpus_kind == 'deviating':
                base = {c: 0 for c in base}
                base[0] = total_positions
            base = {c: n for c, n in base.items() if n > 0}
            codes = np.array(sorted(base), dtype=Index)
            counts = np.array([base[c] for c in sorted(base)],
                              dtype=np.int64)
            marginal.append((name, i, n_conf, codes, counts))
    game_values = (np.arange(n_positions) % 7) / 7.0 - 0.5
    # The dense layout: the intercept slot + the non-intercept configurations (the real
    # iwmap_feature_offset construction).
    n_dense = 1 + sum(nc for (_n, _c0, _c1, nc, _ni) in blocks)
    iwmap_feature_offset = np.zeros(
        len(fset.features) + 1, dtype=np.int64)
    iwmap_feature_offset[1:] = np.cumsum(
        [ft.n_configurations for ft in fset.features])
    tables = {
        'signature': {'total_positions': total_positions},
        'marginal': marginal, 'joint': None,
    }
    return _MockCtx(cfg, fset, indexes, game_values, tables,
                    len(fset.features), n_dense, iwmap_feature_offset), \
        blocks


def _pooled_adherence(ctx, name, blocks):
    """
    The independent oracle: the pooled adherence of one feature (the synthetic indexes vs the
    synthetic corpus marginal).
    """
    m = next(bl for bl in blocks if bl[0] == name)
    c0, c1, _nc, n_inst = m[1], m[2], m[3], m[4]
    flat = ctx.hlp_indexes.indexes[:, c0:c0 + n_inst].ravel()
    uniq, cnt = np.unique(flat, return_counts=True)
    db = dict(zip(uniq.tolist(), cnt.tolist()))
    pool = {}
    for (nm, ii, _n, codes, counts) in ctx.su_analysis_tables['marginal']:
        if nm != name:
            continue
        for code, cc in zip(codes.tolist(), counts.tolist()):
            pool[code] = pool.get(code, 0) + cc
    return hlp_anova_adherence(db, pool)


def _expected_su_line(ctx, name, blocks):
    """
    The independent oracle of the 'SU Sample Consistency' line: re-derives the pooled adherence from
    the ctx and renders the contract string.
    """
    a = _pooled_adherence(ctx, name, blocks)
    tv = a['tv']
    chi2 = "inf" if math.isinf(a['chi2']) else f"{a['chi2']:.1f}"
    p = "nan" if math.isnan(a['p']) else f"{a['p']:.2e}"
    verdict = ('CONSISTENT' if tv <= 0.01
               else 'MARGINAL' if tv <= 0.05 else 'DEVIATING')
    return (f"  SU Sample Consistency       : TV {tv:.4f}  chi2 {chi2} "
            f"(p {p}, merged {a['merged']})  ->  {verdict}")


class TestSuSampleColumns(unittest.TestCase):
    """
    The SU sample columns (PROBABILITY / SU_PROBABILITY) + the 'SU Sample Consistency' header line:
    the NO-DB suite over the mock ctx. Four modes: SU off (the unchanged table), consistent /
    marginal / deviating (the columns + the verdict line), too small (the N/A note, no columns).
    """

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_su_off_unchanged(self):
        # The SU_ANALYSIS level disabled (the tables None): the report is unchanged — no columns, no
        # header line.
        ctx, _ = _make_su_ctx(self.tmp, 300)
        ctx.su_analysis_tables = None
        rep = hlp_analytics_format_file_report(ctx)
        self.assertNotIn("PROBABILITY", rep)
        self.assertNotIn("SU Sample Consistency", rep)

    def test_ok_consistent(self):
        # The corpus = 3x the training counts (the TV 0.0 match, the hand-computed chi2 0.0 / p
        # 1.0): the columns + the 5 CONSISTENT lines (the 2-code mock makes all 5 identical).
        ctx, blocks = _make_su_ctx(self.tmp, 300, 'match')
        rep = hlp_analytics_format_file_report(ctx)
        self.assertIn("| PROBABILITY | SU_PROBABILITY |", rep)
        self.assertIn(_expected_su_line(ctx, 'LMC', blocks), rep)
        self.assertEqual(
            rep.count("TV 0.0000  chi2 0.0 (p 1.00e+00, merged 0)"), 4)
        self.assertEqual(rep.count("->  CONSISTENT"), 4)

    def test_ok_marginal(self):
        # The 9-count 0 -> 1 LMC shift (the hand-computed TV 0.03, the chi2 9/47 + 9/53 = 0.3613):
        # the LMC line is MARGINAL, the other 3 features stay CONSISTENT.
        ctx, blocks = _make_su_ctx(self.tmp, 300, 'marginal')
        rep = hlp_analytics_format_file_report(ctx)
        self.assertIn(_expected_su_line(ctx, 'LMC', blocks), rep)
        self.assertIn(
            "TV 0.0300  chi2 0.4 (p 5.48e-01, merged 0)  ->  MARGINAL",
            rep)
        self.assertEqual(rep.count("->  MARGINAL"), 1)
        self.assertEqual(rep.count("->  CONSISTENT"), 3)

    def test_ok_deviating_inf_chi2(self):
        # The one-point LMC corpus mass: the DB observes codes the corpus never shows (the
        # chi-square inf, the p 0) + the hand-computed TV 0.5 -> DEVIATING.
        ctx, blocks = _make_su_ctx(self.tmp, 300, 'deviating')
        rep = hlp_analytics_format_file_report(ctx)
        self.assertIn(_expected_su_line(ctx, 'LMC', blocks), rep)
        self.assertIn(
            "TV 0.5000  chi2 inf (p 0.00e+00, merged 1)  ->  DEVIATING",
            rep)
        self.assertEqual(rep.count("->  DEVIATING"), 1)
        self.assertEqual(rep.count("->  CONSISTENT"), 3)

    def test_too_small(self):
        # The corpus under 2x the training size (3 < 200): the N/A header note, no columns, the 135 separator.
        ctx, _ = _make_su_ctx(self.tmp, 3, 'match')
        rep = hlp_analytics_format_file_report(ctx)
        self.assertIn(
            "  SU Sample Consistency       : N/A (SU corpus too small: "
            "3 < 2x training 100)", rep)
        self.assertNotIn("PROBABILITY", rep)
        self.assertNotIn("->  ", rep)

    def test_probability_values(self):
        # The column values, re-derived from the synthetic data: the PROBABILITY column sums to 100%
        # (the total_freq invariant) and the SU_PROBABILITY is the pooled corpus share (the 3x
        # corpus -> 3x the uniform training share).
        ctx, blocks = _make_su_ctx(self.tmp, 300, 'match')
        lmc = next(b for b in blocks if b[0] == 'LMC')
        c0, c1, n_conf, n_inst = lmc[1], lmc[2], lmc[3], lmc[4]
        pool = {}
        for (nm, ii, _n, codes, counts) in \
                ctx.su_analysis_tables['marginal']:
            if nm == 'LMC':
                for code, cc in zip(codes.tolist(), counts.tolist()):
                    pool[code] = pool.get(code, 0) + cc
        corpus_total = sum(pool.values())
        # The synthetic wmap freq is 1 per configuration (every row is STATUS C): the row
        # PROBABILITY is 100/n_conf, the SU_PROBABILITY 300/n_conf (the 3x corpus).
        prob = 100.0 * 1 / n_conf
        su_p = 100.0 * pool[0] / corpus_total
        rep = hlp_analytics_format_file_report(ctx)
        # The LMC table's column-header line (the mobility layout).
        self.assertIn("| PROBABILITY | SU_PROBABILITY |", rep)
        # The exact probability cells (49 rows share them).
        self.assertIn(f"{prob:.3f}%", rep)
        self.assertIn(f"{su_p:.3f}%", rep)
        # The PROBABILITY column sums to 100% over the LMC rows (the 3-decimal rounding leaves the
        # n_conf x 0.0005 band: 0.0325 at 65 rows).
        lmc0 = rep.index("MOBILITY FEATURE: LMC")
        lmc1 = rep.index("\n\n", lmc0)
        rows = [l for l in rep[lmc0:lmc1].splitlines()
                if re.match(r"\s+\d+\s+\| [CIC]", l)]
        self.assertEqual(len(rows), n_conf)
        probs = [float(re.search(r"\|\s+([\d.]+)% \|", r).group(1))
                 for r in rows]
        self.assertAlmostEqual(sum(probs), 100.0, delta=0.05)

    def test_intercept_section_present(self):
        # The rlm_00 feature set has an intercept: the report carries the INTERCEPT section (before
        # the MOBILITY details) with the single Weight line (4 decimals, re-derived from the ctx).
        ctx, _ = _make_su_ctx(self.tmp, 300, 'match')
        self.assertIsNotNone(ctx.feature_set.intercept)
        fid = ctx.feature_set.features.index(ctx.feature_set.intercept)
        w_idx = int(ctx.iwmap[int(ctx.iwmap_feature_offset[fid])])
        expected = f"  {'Weight (w)':<28}: {float(ctx.w[w_idx]):+.4f}"
        rep = hlp_analytics_format_file_report(ctx)
        self.assertIn("INTERCEPT:", rep)
        self.assertIn(expected, rep)
        # The section precedes the MOBILITY details.
        self.assertLess(rep.index("INTERCEPT:"),
                        rep.index("MOBILITY FEATURES DETAILS:"))

    def test_intercept_section_absent(self):
        # The no-intercept branch (fset.intercept None — the rlm_02 shape, exercised NO-DB): no
        # INTERCEPT section.
        ctx, _ = _make_su_ctx(self.tmp, 300, 'match')
        ctx.feature_set.intercept = None
        rep = hlp_analytics_format_file_report(ctx)
        self.assertNotIn("INTERCEPT:", rep)


class TestSuSampleEndToEnd(unittest.TestCase):
    """
    The SU sample columns end-to-end on the REAL rlm_00 pipeline (the 10,000-position corpus, the
    200 training positions): the structure + the independently re-derived 'SU Sample Consistency'
    lines. DB-gated (the rlm_00 DB extraction).
    """

    def setUp(self):
        db_gate(self)
        self.patcher_stdout = patch('sys.stdout', new=StringIO())
        self.mock_stdout = self.patcher_stdout.start()
        self._tmp = tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE))
        self.tmp_dir = Path(self._tmp.name)
        self.json_config = str(WORKSPACE_ROOT / "test" / "reversi" /
                               "data" / "rlm_00.json")
        self.rlm = LogisticModel(self.json_config,
                                 verbosity=Verbosity.HIGH,
                                 base_dir_override=self.tmp_dir)
        self.rlm.move_to_step('VALIDATE')
        self.assertEqual(self.rlm.current_step, 14)

    def tearDown(self):
        if getattr(self, 'patcher_stdout', None) is not None:
            self.patcher_stdout.stop()
        if getattr(self, '_tmp', None) is not None:
            self._tmp.cleanup()

    def test_su_columns_real_corpus(self):
        """
        The 10,000-position corpus vs the 200 training positions: the two SU columns + the 4
        consistency lines in the file report, each re-derived from the ctx.
        """
        self.rlm.move_to_step('ANALYTICS')
        self.assertEqual(self.rlm.current_step, 15)
        content = (self.tmp_dir / "model_analytics_report.txt").read_text(
            encoding="utf-8")
        self.assertIn("PROBABILITY", content)
        self.assertIn("SU_PROBABILITY", content)
        self.assertEqual(content.count("SU Sample Consistency"), 4)
        ctx = self.rlm.context
        blocks = ctx.feature_set.feature_blocks
        for (name, c0, c1, _nc, n_inst) in blocks:
            flat = ctx.hlp_indexes.indexes[:, c0:c0 + n_inst].ravel()
            db = dict(zip(*[x.tolist() for x in
                            np.unique(flat, return_counts=True)]))
            pool = {}
            for (nm, ii, _n, codes, counts) in \
                    ctx.su_analysis_tables['marginal']:
                if nm != name:
                    continue
                for code, cc in zip(codes.tolist(), counts.tolist()):
                    pool[code] = pool.get(code, 0) + cc
            a = hlp_anova_adherence(db, pool)
            tv = a['tv']
            chi2 = "inf" if math.isinf(a['chi2']) else f"{a['chi2']:.1f}"
            p = "nan" if math.isnan(a['p']) else f"{a['p']:.2e}"
            verdict = ('CONSISTENT' if tv <= 0.01
                       else 'MARGINAL' if tv <= 0.05 else 'DEVIATING')
            expected = (f"  SU Sample Consistency       : TV {tv:.4f}  "
                         f"chi2 {chi2} (p {p}, merged {a['merged']})  ->  "
                         f"{verdict}")
            self.assertIn(expected, content, name)
        # The rlm_00 feature set has an intercept: the INTERCEPT section (before the MOBILITY
        # details) with the single Weight line (4 decimals), re-derived from the ctx.
        self.assertIn("INTERCEPT:", content)
        self.assertLess(content.index("INTERCEPT:"),
                        content.index("MOBILITY FEATURES DETAILS:"))
        intercept = ctx.feature_set.intercept
        self.assertIsNotNone(intercept)
        fid = ctx.feature_set.features.index(intercept)
        w_idx = int(ctx.iwmap[int(ctx.iwmap_feature_offset[fid])])
        self.assertIn(
            f"  {'Weight (w)':<28}: {float(ctx.w[w_idx]):+.4f}", content)


class TestEtaSquaredCrossLevel(unittest.TestCase):
    """
    The cross-level eta2 invariant, end-to-end on the REAL rlm_00 pipeline (the 200 training
    positions, the ANOVA level force-enabled after CONFIG): for the single-instance features (n_inst
    == 1) the ANALYTICS pooled grouping (all the instances of the feature) coincides with the ANOVA
    per-sub-variable grouping, so the 'Eta-Squared (Discrimination)' line and the 'ANOVA <name> inst
    0: eta2 ...' line must agree. DB-gated.
    """

    def setUp(self):
        db_gate(self)
        self.patcher_stdout = patch('sys.stdout', new=StringIO())
        self.mock_stdout = self.patcher_stdout.start()
        self._tmp = tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE))
        self.tmp_dir = Path(self._tmp.name)
        self.json_config = str(WORKSPACE_ROOT / "test" / "reversi" /
                               "data" / "rlm_00.json")
        self.rlm = LogisticModel(self.json_config,
                                 verbosity=Verbosity.HIGH,
                                 base_dir_override=self.tmp_dir)
        # Force-enable the ANOVA level after CONFIG (the rlm_00 fixture keeps it opt-in FALSE) so
        # the chain to ANALYTICS produces BOTH reports.
        self.rlm.move_to_step("CONFIG")
        self.rlm.context.cfg.anova.enable = True
        self.rlm.move_to_step("ANALYTICS")
        self.assertEqual(self.rlm.current_step, 15)

    def tearDown(self):
        if getattr(self, 'patcher_stdout', None) is not None:
            self.patcher_stdout.stop()
        if getattr(self, '_tmp', None) is not None:
            self._tmp.cleanup()

    def test_single_instance_eta2_agreement(self):
        """
        The two reports, both re-parsed line by line: the 3 single-instance features carry the same
        eta² in the ANALYTICS details table and in the ANOVA report (the printed 4 decimals).
        """
        ctx = self.rlm.context
        single = [name for (name, _c0, _c1, _nc, n_inst)
                  in ctx.feature_set.feature_blocks
                  if n_inst == 1]
        self.assertTrue(single,
                        "no single-instance feature in the fixture")

        content = (self.tmp_dir / "model_analytics_report.txt").read_text(
            encoding="utf-8")
        hdr_rx = re.compile(r"^(?:MOBILITY|PATTERN) FEATURE: (\w+) ")
        eta_rx = re.compile(
            r"^  Eta-Squared \(Discrimination\): ([0-9.]+)")
        analytics_eta = {}
        current = None
        for line in content.splitlines():
            m = hdr_rx.match(line)
            if m:
                current = m.group(1)
                continue
            m = eta_rx.match(line)
            if m and current is not None:
                analytics_eta[current] = float(m.group(1))
                current = None
        self.assertEqual(len(analytics_eta),
                         len(ctx.feature_set.feature_blocks))

        anova_content = (self.tmp_dir / "anova" /
                         "anova_report.txt").read_text(encoding="utf-8")
        anova_rx = re.compile(
            r"^  ANOVA (\w+) inst (\d+): eta2 ([0-9.]+), ")
        anova_eta = {}
        for line in anova_content.splitlines():
            m = anova_rx.match(line)
            if m:
                anova_eta[(m.group(1), int(m.group(2)))] = float(m.group(3))

        for name in single:
            self.assertIn(name, analytics_eta)
            self.assertIn((name, 0), anova_eta)
            self.assertAlmostEqual(anova_eta[(name, 0)],
                                   analytics_eta[name], places=4,
                                   msg=name)


#
# The SMALL-scale NO-DB additions: the shared random seed + the synthetic data sizes for the
# seeded cache files and the synthetic contexts below.
#

_SMALL_SEED = 42
_SMALL_TRAIN_POSITIONS = 200
_SMALL_VLD_POSITIONS = 50


class TestAnalyticsSecondInstanceSmall(unittest.TestCase):
    """
    The second-instance determinism of the ANALYTICS level at SMALL scale, NO-DB: two real
    LogisticModel instances on a fresh base dir whose two DB-extracting cache files (POSITIONS /
    VLD_POSITIONS) are pre-seeded in memory (the TestIsCacheConsistent idiom: a RegabDBConnection
    with activate_conn=False + a tiny DataFrame, stored via regab_store_data_set_to_file which
    writes the .SHA3-256 sidecar the pipeline does). The small config is derived from the rlm_00
    fixture with the SU_ANALYSIS level disabled. The second instance must hit the cache at every
    cacheable level (no DB extraction, no connection) and recompute the ANALYTICS blackboard
    deterministically from the cached inputs (ANALYTICS has no cache file).
    """

    @classmethod
    def setUpClass(cls):
        CUSTOM_TMP_BASE.mkdir(parents=True, exist_ok=True)

    def setUp(self):
        # UNGATED: no DB gate — this class runs in the default (no-DB) tier.
        self.patcher_stdout = patch('sys.stdout', new=StringIO())
        self.mock_stdout = self.patcher_stdout.start()

        self._tmp = tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE))
        self.tmp_dir = Path(self._tmp.name)
        self.cfg_path = self._write_small_config()
        self._seed_db_cache_files()

    def tearDown(self):
        if getattr(self, 'patcher_stdout', None) is not None:
            self.patcher_stdout.stop()
        if getattr(self, '_tmp', None) is not None:
            self._tmp.cleanup()

    def _write_small_config(self) -> Path:
        # The rlm_00 fixture with the SU_ANALYSIS level disabled (its corpus is the third DB
        # extraction and has no cache seed here): the two remaining DB levels are the seeded ones.
        d = json5.loads((WORKSPACE_ROOT / "test" / "reversi" / "data" /
                         "rlm_00.json").read_text())
        d["su_analysis"]["enable"] = False
        cfg_path = self.tmp_dir / "rlm_00_small.json"
        with open(cfg_path, "w") as f:
            json5.dump(d, f, indent=4)
        return cfg_path

    def _seed_db_cache_files(self):
        # Pre-populate the two DB-extracting cache slots in memory: the fixture metadata of the
        # rlm_00 config (tst_regab @ localhost:5432, bid [8], status CMS/CMR, ec 20), so the
        # wrk_positions_is_cache_consistent check accepts them.
        rng = np.random.default_rng(_SMALL_SEED)
        rc = RegabDBConnection("tst_regab", "tst_regab", "localhost", "5432",
                               activate_conn=False)
        for slot, n in (("rlmwf_04_POSITIONS.dat", _SMALL_TRAIN_POSITIONS),
                        ("rlmwf_13_VLD_POSITIONS.dat", _SMALL_VLD_POSITIONS)):
            m = rng.integers(0, 2**63, size=n).astype(np.int64)
            o = rng.integers(0, 2**63, size=n).astype(np.int64)
            o &= ~m
            gv = (rng.integers(-32, 33, size=n) * 2).astype(np.int8)
            df = pd.DataFrame({'mover': m, 'opponent': o, 'game_value': gv})
            rds = RegabDataSet(rc, [8], ["CMS", "CMR"], 20, df)
            regab_store_data_set_to_file(rds, self.tmp_dir / slot)

    def test_second_instance_deterministic_small(self):
        # Instance 1: the 15-level chain on the seeded base dir (cache hits on the two seeded
        # slots, the other cache levels computed and stored, no DB anywhere).
        rlm1 = LogisticModel(str(self.cfg_path),
                             verbosity=Verbosity.HIGH,
                             base_dir_override=self.tmp_dir)
        rlm1.move_to_step('ANALYTICS')
        self.assertEqual(rlm1.current_step, 15)
        met1 = rlm1.context.train_metrics
        dmet1 = rlm1.context.train_dense_metrics
        rep1 = rlm1.context.analytics_report
        self.assertIsNotNone(met1)
        self.assertIsNotNone(dmet1)
        self.assertIsNotNone(rep1)

        # Instance 2: a completely new instance on the same base dir.
        self.mock_stdout.seek(0)
        self.mock_stdout.truncate(0)
        rlm2 = LogisticModel(str(self.cfg_path),
                             verbosity=Verbosity.HIGH,
                             base_dir_override=self.tmp_dir)
        rlm2.move_to_step('ANALYTICS')
        self.assertEqual(rlm2.current_step, 15)

        logs = self.mock_stdout.getvalue()
        # No DB at all: no extraction, no connection.
        self.assertNotIn("Extracted", logs,
                         "DB was queried even though a valid cache existed.")
        self.assertNotIn("established successfully", logs,
                         "DB connection was opened even though a valid cache existed.")
        # The 6 cache_manager levels (POSITIONS, INDEXES, WMAPS, DESIGN_MTR, GENERATE,
        # VLD_POSITIONS) all hit — including the two seeded DB-extracting files.
        hits = [l for l in logs.splitlines()
                if "Cache successfully loaded and validated" in l]
        self.assertEqual(len(hits), 6)
        hit_paths = " ".join(hits)
        self.assertIn("rlmwf_04_POSITIONS.dat", hit_paths)
        self.assertIn("rlmwf_13_VLD_POSITIONS.dat", hit_paths)

        # ANALYTICS has no cache file: the blackboard is recomputed from the cached inputs —
        # deterministically.
        self.assertEqual(rlm2.context.train_metrics, met1)
        self.assertEqual(rlm2.context.train_dense_metrics, dmet1)
        self.assertEqual(rlm2.context.analytics_report, rep1)
        self.assertTrue((self.tmp_dir / "model_analytics_report.txt").exists())


class TestAnalyticsConsoleReportAndUp(unittest.TestCase):
    """
    The ANALYTICS console-report formatter + the worker's _up, NO-DB over the file's _MockCtx
    idiom: the header structure pinned over known metric dicts, and _up exercised directly (the 3
    INFO lines, the report file, the four published attributes with the values independently
    re-derived from the synthetic arrays).
    """

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self._events = []

    def tearDown(self):
        self._tmp.cleanup()

    def test_console_report_format(self):
        ctx, _ = _make_su_ctx(self.tmp, 300)
        # The known metric dicts: the values are deliberately DISTINCT per column so each assert
        # pins the value's column placement.
        ctx.train_metrics = {'train_mae_y': 1.5, 'train_rmse_y': 2.5,
                             'train_loss': 1.0e-03, 'train_samples': 100,
                             'pop_mae_y': 10.0, 'pop_rmse_y': 12.0,
                             'pop_loss': 0.01}
        ctx.train_dense_metrics = {'train_dense_mae_y': 2.25,
                                   'train_dense_rmse_y': 3.75,
                                   'train_dense_loss': 2.5e-03,
                                   'train_dense_samples': 100}
        ctx.vld_metrics = {'vld_mae_y': 4.5, 'vld_rmse_y': 6.25,
                           'vld_loss': 7.0e-03, 'vld_samples': 50}
        ctx.opt_info = {'reason': 'CONVERGED_MIN_GRAD', 'iters': 12}

        rep = hlp_analytics_format_console_report(ctx)

        # The title line from the cfg name, inside the 135-char frame.
        self.assertIn(f"MODEL ANALYTICS REPORT: {ctx.cfg.name}", rep)
        self.assertTrue(rep.strip().startswith("=" * 135))
        # The parameter counts, re-derived from the ctx arrays.
        self.assertIn(f"  Total Parameters (W)        : {len(ctx.w):,}", rep)
        self.assertIn(f"  Dense Parameters (K)        : {len(ctx.w_dense):,}", rep)
        self.assertIn("  Optimization Status         : CONVERGED_MIN_GRAD (12 iters)", rep)
        # The 3-column metric table: the column-header line + the three rows, re-derived from
        # the ctx metric dicts.
        self.assertIn(
            f"  {'METRIC':<15} | {'TRAINING':<14} | {'TRAINING-DENSE':<14} | "
            f"{'VALIDATION':<14}", rep)
        self.assertIn(
            f"  {'RMSE (y)':<15} | {ctx.train_metrics['train_rmse_y']:<14.2f} | "
            f"{ctx.train_dense_metrics['train_dense_rmse_y']:<14.2f} | "
            f"{ctx.vld_metrics['vld_rmse_y']:<14.2f}", rep)
        self.assertIn(
            f"  {'MAE (y)':<15} | {ctx.train_metrics['train_mae_y']:<14.2f} | "
            f"{ctx.train_dense_metrics['train_dense_mae_y']:<14.2f} | "
            f"{ctx.vld_metrics['vld_mae_y']:<14.2f}", rep)
        self.assertIn(
            f"  {'Loss (MSE/2)':<15} | {ctx.train_metrics['train_loss']:<14.4e} | "
            f"{ctx.train_dense_metrics['train_dense_loss']:<14.4e} | "
            f"{ctx.vld_metrics['vld_loss']:<14.4e}", rep)
        # The Population / Generalization Gap / Substitution Delta rows, re-derived from the
        # ctx metric dicts.
        self.assertIn(
            f"  Population (baseline)  : RMSE {ctx.train_metrics['pop_rmse_y']:.2f}  "
            f"MAE {ctx.train_metrics['pop_mae_y']:.2f}  "
            f"Loss {ctx.train_metrics['pop_loss']:.4e}", rep)
        gen_gap = ctx.vld_metrics['vld_rmse_y'] - ctx.train_dense_metrics['train_dense_rmse_y']
        sub_delta = (ctx.train_dense_metrics['train_dense_rmse_y']
                     - ctx.train_metrics['train_rmse_y'])
        self.assertIn(f"  Generalization Gap (RMSE)   : {gen_gap:.2f}", rep)
        self.assertIn(f"  Substitution Delta (RMSE)   : {sub_delta:.2f}", rep)
        # The NEGATIVES: the console report (the short summary) carries no Creation Date and no
        # per-feature detail sections.
        self.assertNotIn("Creation Date", rep)
        self.assertNotIn("PATTERN FEATURE", rep)

    def test_up_publishes_and_logs(self):
        ctx, _ = _make_su_ctx(self.tmp, 300)
        # Extend the mock ctx with what wrk_analytics._up needs.
        n = len(ctx.game_values)
        rng = np.random.default_rng(_SMALL_SEED)
        ctx.design_matrix = rng.integers(0, len(ctx.w), size=(n, 4), dtype=np.int64)
        ctx.y2z, ctx.z2y = hlp_zed_fun_factory(ctx.cfg.stat_model.logit_clipping)
        ctx.opt_info = {'reason': 'CONVERGED_MIN_GRAD', 'iters': 7, 'f': 0.0123}
        ctx.log_event = lambda relevance, message: self._events.append(
            (relevance, message))

        _analytics_up(ctx)

        # The 3 INFO log lines (the console report is logged line by line in between).
        info_msgs = [m for rel, m in self._events if rel == Relevance.INFO]
        self.assertIn("Generating model analytics report...", info_msgs)
        self.assertIn("Computing metrics on the training set...", info_msgs)
        saved = [m for m in info_msgs if m.startswith("Analytics report saved to ")]
        self.assertEqual(len(saved), 1)

        # The report file is written to base_dir under the configured name.
        report_path = ctx.cfg.base_dir / ctx.cfg.analytics.report_file_name
        self.assertTrue(report_path.exists())
        self.assertEqual(saved[0], f"Analytics report saved to {report_path}")

        # The published attributes: the 7-key train metrics, the 4-key dense metrics, the dense
        # residual series, the console report.
        self.assertEqual(
            set(ctx.train_metrics),
            {'train_mae_y', 'train_rmse_y', 'train_loss', 'train_samples',
             'pop_mae_y', 'pop_rmse_y', 'pop_loss'})
        self.assertEqual(
            set(ctx.train_dense_metrics),
            {'train_dense_mae_y', 'train_dense_rmse_y', 'train_dense_loss',
             'train_dense_samples'})
        self.assertIsInstance(ctx.train_dense_rn, np.ndarray)
        self.assertEqual(ctx.train_dense_rn.shape, (n,))
        self.assertIsInstance(ctx.analytics_report, str)

        # The values, independently re-derived from the synthetic arrays — the compressed pass
        # (what lbfgs fit).
        y_true = ctx.game_values.astype(np.float64)
        rn_y = (ctx.z2y(sigmoid(np.sum(ctx.w[ctx.design_matrix].astype(
            np.float64), axis=1))) - y_true)
        self.assertEqual(ctx.train_metrics['train_mae_y'],
                         float(np.mean(np.abs(rn_y))))
        self.assertEqual(ctx.train_metrics['train_rmse_y'],
                         float(np.sqrt(np.dot(rn_y, rn_y) / len(rn_y))))
        self.assertEqual(ctx.train_metrics['train_loss'], ctx.opt_info['f'])
        self.assertEqual(ctx.train_metrics['train_samples'], n)
        rn_pop = y_true - np.mean(y_true)
        self.assertEqual(ctx.train_metrics['pop_mae_y'],
                         float(np.mean(np.abs(rn_pop))))
        self.assertEqual(ctx.train_metrics['pop_rmse_y'],
                         float(np.sqrt(np.dot(rn_pop, rn_pop) / len(rn_pop))))
        z_true = ctx.y2z(ctx.game_values)
        rn_z_pop = z_true - np.mean(z_true)
        self.assertEqual(ctx.train_metrics['pop_loss'],
                         float(0.5 * np.dot(rn_z_pop, rn_z_pop) / len(rn_z_pop)))

        # The dense pass (the shipped inference rules), re-derived the same way.
        col_offsets = np.repeat(ctx.iwmap_feature_offset[:-1],
                                [f.n_instances for f in ctx.feature_set.features])
        z_dense = sigmoid(np.sum(
            ctx.w_dense[ctx.hlp_indexes.indexes + col_offsets], axis=1))
        rn_dense = ctx.z2y(z_dense) - y_true
        self.assertEqual(ctx.train_dense_rn.tobytes(), rn_dense.tobytes())
        self.assertEqual(ctx.train_dense_metrics['train_dense_mae_y'],
                         float(np.mean(np.abs(rn_dense))))
        self.assertEqual(ctx.train_dense_metrics['train_dense_rmse_y'],
                         float(np.sqrt(np.dot(rn_dense, rn_dense) / len(rn_dense))))
        self.assertEqual(ctx.train_dense_metrics['train_dense_loss'],
                         float(0.5 * np.dot((z_dense - z_true) ** 2,
                                             np.ones_like(z_dense))
                                / len(z_dense)))
        self.assertEqual(ctx.train_dense_metrics['train_dense_samples'], n)


class TestAnalyticsDownScope(unittest.TestCase):
    """
    The ANALYTICS level's _down scope, NO-DB: the four context attributes are cleared (the
    failure-recovery contract) and the report file is NOT removed (it is a base_dir artifact).
    """

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp_dir = Path(self._tmp.name)
        self._events = []

    def tearDown(self):
        self._tmp.cleanup()

    def test_down_clears_attributes_and_keeps_file(self):
        report_file = self.tmp_dir / "model_analytics_report.txt"
        report_file.write_text("dummy report\n", encoding="utf-8")

        ctx = SimpleNamespace(
            train_metrics={'sentinel': 1},
            train_dense_metrics={'sentinel': 2},
            analytics_report="sentinel report",
            train_dense_rn=np.array([1.0, 2.0]),
            log_event=lambda relevance, message: self._events.append(
                (relevance, message)),
        )

        _analytics_down(ctx)

        self.assertIsNone(ctx.train_metrics)
        self.assertIsNone(ctx.train_dense_metrics)
        self.assertIsNone(ctx.analytics_report)
        self.assertIsNone(ctx.train_dense_rn)
        # The report file is a base_dir artifact: _down does not unlink it.
        self.assertTrue(report_file.exists())
        # The clearing line is logged.
        self.assertIn("Clearing analytics attributes...",
                      [m for _, m in self._events])


class TestDenseRnSeriesConsistency(unittest.TestCase):
    """
    The published dense residual series consistency, NO-DB: a direct unit test of
    hlp_analytics_compute_training_dense_metrics on a small synthetic ctx (the real rlm_00
    feature set through the FEATURES facade, 500 synthetic positions): the published MAE / RMSE
    are re-derived BIT-EXACT from the published rn_y series, and the Z-space loss is re-derived
    through an independent forward pass.
    """

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_rn_series_matches_published_mae(self):
        # The real rlm_00 feature set (the facade runs to FEATURES, no DB — the file's
        # established idiom).
        rlm = LogisticModel(
            str(WORKSPACE_ROOT / "test" / "reversi" / "data" / "rlm_00.json"),
            verbosity=Verbosity.NONE, base_dir_override=self.tmp)
        rlm.run("FEATURES")
        fset = rlm.context.feature_set
        blocks = fset.feature_blocks

        n = 500
        rng = np.random.default_rng(_SMALL_SEED)
        # The hlp_indexes.indexes layout: one column per feature instance, each holding the
        # configuration index within its feature.
        max_col = max(c1 for (_n, c0, c1, _nc, _ni) in blocks)
        indexes = np.zeros((n, max_col), dtype=Index)
        for (_name, c0, c1, nc, n_inst) in blocks:
            indexes[:, c0:c1] = rng.integers(0, nc, size=(n, n_inst),
                                              dtype=Index)
        # The real iwmap_feature_offset construction (the cumulative dense-layout boundaries).
        iwmap_feature_offset = np.zeros(len(fset.features) + 1, dtype=np.int64)
        iwmap_feature_offset[1:] = np.cumsum(
            [ft.n_configurations for ft in fset.features])
        n_dense = int(iwmap_feature_offset[-1])
        w_dense = (0.001 * (np.arange(n_dense) + 1.0)).astype(np.float32)
        game_values = (rng.integers(-32, 33, size=n) * 2).astype(np.int8)
        # The real ZED transforms (the rlm_00 logit clipping 0.05).
        y2z, z2y = hlp_zed_fun_factory(0.05)

        ctx = SimpleNamespace(
            feature_set=fset,
            hlp_indexes=SimpleNamespace(indexes=indexes),
            iwmap_feature_offset=iwmap_feature_offset,
            w_dense=w_dense,
            game_values=game_values,
            y2z=y2z,
            z2y=z2y,
            log_event=lambda *args: None,
        )

        res = hlp_analytics_compute_training_dense_metrics(ctx)
        self.assertIsInstance(res, AnalyticsTrainingDenseResult)
        rn = res.rn_y
        self.assertEqual(rn.dtype, np.float64)
        self.assertEqual(rn.shape, (n,))

        met = res.metrics
        # The MAE / RMSE re-derived BIT-EXACT from the published series itself.
        self.assertEqual(met['train_dense_mae_y'], float(np.mean(np.abs(rn))))
        self.assertEqual(met['train_dense_rmse_y'],
                         float(np.sqrt(np.dot(rn, rn) / n)))
        # The Z-space loss re-derived through the independent forward pass.
        col_offsets = np.repeat(iwmap_feature_offset[:-1],
                                [f.n_instances for f in fset.features])
        z_pred = sigmoid(np.sum(w_dense[indexes + col_offsets], axis=1))
        rn_z = z_pred - y2z(game_values)
        self.assertEqual(met['train_dense_loss'],
                         float(0.5 * np.dot(rn_z, rn_z) / n))
        self.assertEqual(met['train_dense_samples'], n)


if __name__ == '__main__':
    unittest.main()
