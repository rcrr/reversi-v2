#
# test_wrk_analytics.py
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
# How to run the wrk_analytics unit tests.
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
# time python3 -m unittest test.reversi.lm.test_wrk_analytics
#

import hashlib
import math
import os
import re
import tempfile
import unittest

from unittest.mock import patch
from io import StringIO
from pathlib import Path

import numpy as np

from reversi.lm.hlp_analytics import format_file_report
from reversi.lm.hlp_anova import adherence
from reversi.tools.state_machine import Verbosity
from reversi.lm.logistic_model import LogisticModel
from test.reversi.closecheck import assert_close
from test.reversi.paths import WORKSPACE_ROOT, CUSTOM_TMP_BASE
from test.reversi.tags import db_long_gate


def _masked_report_hash(text):
    """sha3_256 of the report text with the Creation Date masked out.

    The file report embeds datetime.now() — every other byte is
    deterministic, so the date-masked hash is a stable golden. The
    config fingerprint embeds the run's base_dir (a tmp dir); mask
    the hex the same way.
    """
    masked = re.sub(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", "DATE", text)
    masked = re.sub(r"(Config SHA3-256\s*:\s*)[0-9a-f]{64}", r"\1HASH", masked)
    return hashlib.sha3_256(masked.encode("utf-8")).hexdigest()


class TestLMWorkerAnalytics(unittest.TestCase):
    """Tests the ANALYTICS worker integration and exact values using rlm_02.json.

    The ANALYTICS level is pure compute (no cache file — the rlmwf_15 slot
    stays unused), so the training metrics and the reports are recomputed on
    every run; the second-instance test pins that recomputation as
    deterministic.
    """

    def setUp(self):
        # The SKIP_REGAB_DB gate, as in test_regab — the worker tests need
        # the live regab DB (the setUp moves to VALIDATE, which runs the
        # whole 15-level chain on a fresh base dir).
        db_long_gate(self)  # the SKIP_REGAB_DB + LONG gates

        # Patch stdout to keep test output clean and capture logs
        self.patcher_stdout = patch('sys.stdout', new=StringIO())
        self.mock_stdout = self.patcher_stdout.start()

        # TemporaryDirectory created FIRST so a mid-setup failure
        # still leaves a cleanable temp dir.
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
        """First run to ANALYTICS: the 7-metric dict, the 4-key dense dict,
        the console report, the report file and the INFO log lines.

        Goldens: rlm_02 live (the bid [6,7] training model, 199952
        samples), derived independently, not read back from the
        worker output.
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

        # The dense-pass dict: the shipped inference rules (w_dense)
        # on the training data. rlm_02 has frequency_cut_off=1, so the dense
        # values match the compressed ones up to the f32 rounding of w_dense.
        dmet = self.rlm.context.train_dense_metrics
        self.assertIsNotNone(dmet)
        self.assertEqual(set(dmet), {'train_dense_mae_y', 'train_dense_rmse_y',
                                     'train_dense_loss', 'train_dense_samples'})
        assert_close(self, dmet['train_dense_mae_y'], 12.346794548249868, 'train_dense_mae_y')
        assert_close(self, dmet['train_dense_rmse_y'], 15.58872171282352, 'train_dense_rmse_y')
        assert_close(self, dmet['train_dense_loss'], 0.00712234852835536, 'train_dense_loss')
        self.assertEqual(dmet['train_dense_samples'], 199952)

        # The console report (header only — no tables, no date) is stored
        # on the context and logged line by line.
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

        # The complete file report is written to base_dir under the
        # configured name; rlm_02 has no mobility features, so the
        # MOBILITY section is empty, EDGE prints its rows (it is in the
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
        # rlm_02 has no su_analysis section (the default FALSE): the
        # report is unchanged — no SU columns, no consistency line.
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

    def test_second_instance_deterministic(self):
        """A second instance on the same base dir recomputes identical metrics
        and reports (ANALYTICS has no cache file) while the 6 cache_manager
        levels hit and the DB is not re-extracted."""
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
        # The 6 cache_manager levels (POSITIONS, INDEXES, WMAPS, DESIGN_MTR,
        # GENERATE, VLD_POSITIONS) hit; CONFIG and the OPTIMIZE checkpoint
        # have their own load flows; FEATURES / ZED / GRADIENT / VALIDATE /
        # ANALYTICS have no cache file and recompute.
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
        """Pin the _down scope: back to VALIDATE clears train_metrics,
        train_dense_metrics and analytics_report (the report file itself is
        not removed)."""
        self.rlm.move_to_step('ANALYTICS')
        self.assertIsNotNone(self.rlm.context.train_metrics)
        self.assertIsNotNone(self.rlm.context.train_dense_metrics)
        self.assertIsNotNone(self.rlm.context.analytics_report)

        self.rlm.move_to_step(14)
        self.assertEqual(self.rlm.current_step, 14)
        self.assertEqual(self.rlm.current_worker_name, 'VALIDATE')
        self.assertIsNone(self.rlm.context.train_metrics)
        self.assertIsNone(self.rlm.context.train_dense_metrics)
        self.assertIsNone(self.rlm.context.analytics_report)
        # The report file is a base_dir artifact — _down does not unlink it.
        self.assertTrue((self.tmp_dir / "model_analytics_report.txt").exists())


class TestLMWorkerAnalyticsMobility(unittest.TestCase):
    """The mobility-table branch of the file report, using rlm_01.json.

    rlm_01 has the intercept + the LMC mobility feature + the DIAG3 and
    CORE patterns, and its analytics.detailed_report list is ["DIAG3",
    "LMC"] — so the LMC table (65 configuration rows) and the DIAG3 table
    print their rows while CORE omits them. This is the only fixture that
    exercises the mobility table helper end-to-end.
    """

    def setUp(self):
        # The SKIP_REGAB_DB gate, as in test_regab — the worker tests need
        # the live regab DB (the setUp moves to VALIDATE, which runs the
        # whole 15-level chain on a fresh base dir).
        db_long_gate(self)  # the SKIP_REGAB_DB + LONG gates

        # Patch stdout to keep test output clean and capture logs
        self.patcher_stdout = patch('sys.stdout', new=StringIO())
        self.mock_stdout = self.patcher_stdout.start()

        # TemporaryDirectory created FIRST so a mid-setup failure
        # still leaves a cleanable temp dir.
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
        """First run to ANALYTICS on rlm_01: the training metrics golden,
        the dense-pass golden (rlm_01 has frequency_cut_off=2, so 5 of its
        10 training positions touch IC slots — the substitution delta is
        3.36, the clearest demonstration of the substitution table), the
        mobility + pattern table structure and the file-report hash.

        Goldens: rlm_01 live (bid [7] training, 10 samples),
        derived independently, not read back from the worker output.
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

        # The dense pass on the same 10 positions: the compressed fit is
        # exact (rmse 0.00) but the shipped model substitutes 5 below-cutoff
        # configurations — the Substitution Delta row reads 3.36.
        dmet = self.rlm.context.train_dense_metrics
        assert_close(self, dmet['train_dense_mae_y'], 1.854193878173828, 'train_dense_mae_y')
        assert_close(self, dmet['train_dense_rmse_y'], 3.3556084739848866, 'train_dense_rmse_y')
        assert_close(self, dmet['train_dense_loss'], 0.0003036324051208794, 'train_dense_loss')
        self.assertEqual(dmet['train_dense_samples'], 10)

        report_path = self.tmp_dir / "model_analytics_report.txt"
        self.assertTrue(report_path.exists())
        content = report_path.read_text(encoding="utf-8")
        # The LMC table prints its rows (LMC is in the detailed_report
        # list), DIAG3 its rows too, CORE omits them — exactly one
        # omitted-rows line in the whole report.
        self.assertIn("MOBILITY FEATURES DETAILS:", content)
        self.assertIn("MOBILITY FEATURE: LMC (fid=1)", content)
        self.assertIn("PATTERN FEATURE: DIAG3 (fid=2)", content)
        self.assertIn("PATTERN FEATURE: CORE (fid=3)", content)
        self.assertEqual(content.count("(Table rows omitted"), 1)
        # rlm_01 has no su_analysis section (the default FALSE): the
        # report is unchanged — no SU columns, no consistency line.
        self.assertNotIn("PROBABILITY", content)
        self.assertNotIn("SU Sample Consistency", content)
        self.assertEqual(_masked_report_hash(content),
                         "176a80b5d3d70549c62c12be127982ac7baaed60281ebc542bd457c1d3670162")

        logs = self.mock_stdout.getvalue()
        self.assertIn("Optimization Status         : CONVERGED_MIN_GRAD (16 iters)", logs)
        self.assertIn("Generalization Gap (RMSE)   : 23.87", logs)
        self.assertIn("Substitution Delta (RMSE)   : 3.36", logs)


class _MockCtx:
    """The NO-DB mock context for the SU sample columns: the real
    rlm_00 cfg + feature_set (the facade run to FEATURES) + the
    SYNTHETIC wmap / indexes / game values / corpus marginal."""

    def __init__(self, cfg, feature_set, indexes, game_values, tables,
                 n_features, n_dense, iwmap_feature_offset):
        self.cfg = cfg
        self.feature_set = feature_set
        self.hlp_indexes = type('I', (), {'indexes': indexes})()
        self.game_values = game_values
        self.su_analysis_tables = tables
        self.wmap = np.zeros((n_dense, 3), dtype=np.int64)
        name_to_fid = {f.name: i
                       for i, f in enumerate(feature_set.features)}
        self.wmap[0, :] = (0, 0, 1)  # the intercept slot
        for (name, _c0, _c1, nc, _ni) in feature_set.feature_blocks:
            fid = name_to_fid[name]
            for c in range(nc):
                self.wmap[iwmap_feature_offset[fid] + c, :] = (
                    fid, c, 1)
        self.wmap_fallback = None
        self.iwmap = np.arange(n_dense, dtype=np.int64)
        self.w = 0.001 * (np.arange(n_dense, dtype=np.float64) + 1.0)
        self.w_dense = self.w.copy()
        self.iwmap_feature_offset = iwmap_feature_offset
        self.feature_w_ranges = np.full((n_features, 2), -1,
                                        dtype=np.int64)
        self.config_checksum = "ab" * 32
        self.train_metrics = {}
        self.train_dense_metrics = {}
        self.vld_metrics = {}
        self.opt_info = {}


def _make_su_ctx(tmp, total_positions, corpus_kind='match'):
    """The mock ctx over the real rlm_00 campaign (the facade runs
    CREATED -> CONFIG -> FEATURES, the D-287 idiom): 100 synthetic
    training positions (the 2-code concentrated codes — code 0 for
    the first 50 positions, code 1 for the rest — the same rule for
    every sub-variable), the complete synthetic wmap (one row per
    configuration, freq 1 — every table row is STATUS C), and the
    synthetic corpus marginal (one entry per sub-variable, the
    observed support, summing to total_positions): 'match' = 3x the
    training counts (the TV 0.0 match); 'marginal' = the 9-count
    0 -> 1 LMC shift (the hand-computed TV 0.03, the chi2 0.3613);
    'deviating' = the one-point LMC mass (the chi-square inf, the
    hand-computed TV 0.5)."""
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
    indexes = np.zeros((n_positions, max_col), dtype=np.uint32)
    sub_counts = {}
    for (name, c0, c1, n_conf, n_inst) in blocks:
        for i in range(n_inst):
            # The 2-code concentration: 50 positions per code.
            indexes[:, c0 + i] = (
                np.arange(n_positions) >= 50).astype(np.uint32)
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
            codes = np.array(sorted(base), dtype=np.uint32)
            counts = np.array([base[c] for c in sorted(base)],
                              dtype=np.int64)
            marginal.append((name, i, n_conf, codes, counts))
    game_values = (np.arange(n_positions) % 7) / 7.0 - 0.5
    # The dense layout: the intercept slot + the non-intercept
    # configurations (the real iwmap_feature_offset construction).
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
    """The independent oracle: the pooled adherence of one feature
    (the synthetic indexes vs the synthetic corpus marginal)."""
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
    return adherence(db, pool)


def _expected_su_line(ctx, name, blocks):
    """The independent oracle of the 'SU Sample Consistency' line:
    re-derives the pooled adherence from the ctx and renders the
    contract string."""
    a = _pooled_adherence(ctx, name, blocks)
    tv = a['tv']
    chi2 = "inf" if math.isinf(a['chi2']) else f"{a['chi2']:.1f}"
    p = "nan" if math.isnan(a['p']) else f"{a['p']:.2e}"
    verdict = ('CONSISTENT' if tv <= 0.01
               else 'MARGINAL' if tv <= 0.05 else 'DEVIATING')
    return (f"  SU Sample Consistency       : TV {tv:.4f}  chi2 {chi2} "
            f"(p {p}, merged {a['merged']})  ->  {verdict}")


class TestSuSampleColumns(unittest.TestCase):
    """The SU sample columns (the PROBABILITY / SU_PROBABILITY) + the
    'SU Sample Consistency' header line: the NO-DB suite over the mock
    ctx (the real rlm_00 campaign to FEATURES, the synthetic wmap /
    indexes / corpus marginal). Four modes: the SU off (the unchanged
    table), the ok consistent / marginal / deviating (the columns +
    the verdict line), the too small (the N/A note, no columns)."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_su_off_unchanged(self):
        # The SU_ANALYSIS level disabled (the tables None): the report
        # is unchanged — no columns, no header line.
        ctx, _ = _make_su_ctx(self.tmp, 300)
        ctx.su_analysis_tables = None
        rep = format_file_report(ctx)
        self.assertNotIn("PROBABILITY", rep)
        self.assertNotIn("SU Sample Consistency", rep)

    def test_ok_consistent(self):
        # The corpus = 3x the training counts (the TV 0.0 match, the
        # hand-computed chi2 0.0 / p 1.0): the columns + the 5
        # CONSISTENT lines (the 2-code mock makes all 5 identical).
        ctx, blocks = _make_su_ctx(self.tmp, 300, 'match')
        rep = format_file_report(ctx)
        self.assertIn("| PROBABILITY | SU_PROBABILITY |", rep)
        self.assertIn(_expected_su_line(ctx, 'LMC', blocks), rep)
        self.assertEqual(
            rep.count("TV 0.0000  chi2 0.0 (p 1.00e+00, merged 0)"), 5)
        self.assertEqual(rep.count("->  CONSISTENT"), 5)

    def test_ok_marginal(self):
        # The 9-count 0 -> 1 LMC shift (the hand-computed TV 0.03,
        # the chi2 9/47 + 9/53 = 0.3613): the LMC line is MARGINAL,
        # the other 4 features stay CONSISTENT.
        ctx, blocks = _make_su_ctx(self.tmp, 300, 'marginal')
        rep = format_file_report(ctx)
        self.assertIn(_expected_su_line(ctx, 'LMC', blocks), rep)
        self.assertIn(
            "TV 0.0300  chi2 0.4 (p 5.48e-01, merged 0)  ->  MARGINAL",
            rep)
        self.assertEqual(rep.count("->  MARGINAL"), 1)
        self.assertEqual(rep.count("->  CONSISTENT"), 4)

    def test_ok_deviating_inf_chi2(self):
        # The one-point LMC corpus mass: the DB observes codes the
        # corpus never shows (the chi-square inf, the p 0) + the
        # hand-computed TV 0.5 -> DEVIATING.
        ctx, blocks = _make_su_ctx(self.tmp, 300, 'deviating')
        rep = format_file_report(ctx)
        self.assertIn(_expected_su_line(ctx, 'LMC', blocks), rep)
        self.assertIn(
            "TV 0.5000  chi2 inf (p 0.00e+00, merged 1)  ->  DEVIATING",
            rep)
        self.assertEqual(rep.count("->  DEVIATING"), 1)
        self.assertEqual(rep.count("->  CONSISTENT"), 4)

    def test_too_small(self):
        # The corpus under 2x the training size (3 < 200): the N/A
        # header note, no columns, the 135 separator.
        ctx, _ = _make_su_ctx(self.tmp, 3, 'match')
        rep = format_file_report(ctx)
        self.assertIn(
            "  SU Sample Consistency       : N/A (SU corpus too small: "
            "3 < 2x training 100)", rep)
        self.assertNotIn("PROBABILITY", rep)
        self.assertNotIn("->  ", rep)

    def test_probability_values(self):
        # The column values, re-derived from the synthetic data: the
        # PROBABILITY column sums to 100% (the total_freq invariant)
        # and the SU_PROBABILITY is the pooled corpus share (the 3x
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
        # The synthetic wmap freq is 1 per configuration (every row
        # is STATUS C): the row PROBABILITY is 100/n_conf, the
        # SU_PROBABILITY 300/n_conf (the 3x corpus).
        prob = 100.0 * 1 / n_conf
        su_p = 100.0 * pool[0] / corpus_total
        rep = format_file_report(ctx)
        # The LMC table's column-header line (the mobility layout).
        self.assertIn("| PROBABILITY | SU_PROBABILITY |", rep)
        # The exact probability cells (49 rows share them).
        self.assertIn(f"{prob:.3f}%", rep)
        self.assertIn(f"{su_p:.3f}%", rep)
        # The PROBABILITY column sums to 100% over the LMC rows
        # (the 3-decimal rounding leaves the n_conf x 0.0005 band:
        # 0.0325 at 65 rows).
        lmc0 = rep.index("MOBILITY FEATURE: LMC")
        lmc1 = rep.index("\n\n", lmc0)
        rows = [l for l in rep[lmc0:lmc1].splitlines()
                if re.match(r"\s+\d+\s+\| [CIC]", l)]
        self.assertEqual(len(rows), n_conf)
        probs = [float(re.search(r"\|\s+([\d.]+)% \|", r).group(1))
                 for r in rows]
        self.assertAlmostEqual(sum(probs), 100.0, delta=0.05)

    def test_intercept_section_present(self):
        # The rlm_00 feature set has an intercept: the report carries
        # the INTERCEPT section (before the MOBILITY details) with the
        # single Weight line (4 decimals, re-derived from the ctx).
        ctx, _ = _make_su_ctx(self.tmp, 300, 'match')
        self.assertIsNotNone(ctx.feature_set.intercept)
        fid = ctx.feature_set.features.index(ctx.feature_set.intercept)
        w_idx = int(ctx.iwmap[int(ctx.iwmap_feature_offset[fid])])
        expected = f"  {'Weight (w)':<28}: {float(ctx.w[w_idx]):+.4f}"
        rep = format_file_report(ctx)
        self.assertIn("INTERCEPT:", rep)
        self.assertIn(expected, rep)
        # The section precedes the MOBILITY details.
        self.assertLess(rep.index("INTERCEPT:"),
                        rep.index("MOBILITY FEATURES DETAILS:"))

    def test_intercept_section_absent(self):
        # The no-intercept branch (fset.intercept None — the rlm_02
        # shape, exercised NO-DB): no INTERCEPT section.
        ctx, _ = _make_su_ctx(self.tmp, 300, 'match')
        ctx.feature_set.intercept = None
        rep = format_file_report(ctx)
        self.assertNotIn("INTERCEPT:", rep)


class TestSuSampleEndToEnd(unittest.TestCase):
    """The SU sample columns end-to-end on the REAL rlm_00 pipeline
    (the 10,000-position corpus, the 200 training positions): the
    structure + the independently re-derived 'SU Sample Consistency'
    lines. DB-gated (the rlm_00 DB extraction)."""

    def setUp(self):
        db_long_gate(self)
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
        """The 10,000-position corpus vs the 200 training positions:
        the corpus is NOT under 2x the training size, so the two
        columns + the 5 consistency lines (one per feature) are in
        the file report — each line re-derived from the ctx (the
        real corpus marginal vs the real indexes)."""
        self.rlm.move_to_step('ANALYTICS')
        self.assertEqual(self.rlm.current_step, 15)
        content = (self.tmp_dir / "model_analytics_report.txt").read_text(
            encoding="utf-8")
        self.assertIn("PROBABILITY", content)
        self.assertIn("SU_PROBABILITY", content)
        self.assertEqual(content.count("SU Sample Consistency"), 5)
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
            a = adherence(db, pool)
            tv = a['tv']
            chi2 = "inf" if math.isinf(a['chi2']) else f"{a['chi2']:.1f}"
            p = "nan" if math.isnan(a['p']) else f"{a['p']:.2e}"
            verdict = ('CONSISTENT' if tv <= 0.01
                       else 'MARGINAL' if tv <= 0.05 else 'DEVIATING')
            expected = (f"  SU Sample Consistency       : TV {tv:.4f}  "
                         f"chi2 {chi2} (p {p}, merged {a['merged']})  ->  "
                         f"{verdict}")
            self.assertIn(expected, content, name)
        # The rlm_00 feature set has an intercept: the INTERCEPT
        # section (before the MOBILITY details) with the single Weight
        # line (4 decimals), re-derived from the ctx.
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
    """The D-311 cross-level invariant, end-to-end on the REAL rlm_00
    pipeline (the 200 training positions): for the single-instance
    features (n_inst == 1 — ALMC, LMC, DLMC) the ANALYTICS pooled
    grouping (ALL the instances of the feature) coincides with the
    ANOVA level's per-sub-variable grouping — the same computation —
    so the 'Eta-Squared (Discrimination)' line and the 'ANOVA <name>
    inst 0: eta2 ...' line must agree. DB-gated (the rlm_00 DB
    extraction)."""

    def setUp(self):
        db_long_gate(self)
        self.patcher_stdout = patch('sys.stdout', new=StringIO())
        self.mock_stdout = self.patcher_stdout.start()
        self._tmp = tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE))
        self.tmp_dir = Path(self._tmp.name)
        self.json_config = str(WORKSPACE_ROOT / "test" / "reversi" /
                               "data" / "rlm_00.json")
        self.rlm = LogisticModel(self.json_config,
                                 verbosity=Verbosity.HIGH,
                                 base_dir_override=self.tmp_dir)
        # Force-enable the ANOVA level after CONFIG (the rlm_00
        # fixture keeps it opt-in FALSE) so the chain to ANALYTICS
        # produces BOTH reports.
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
        """The two reports, both re-parsed line by line: the 3
        single-instance features carry the same eta² in the ANALYTICS
        details table and in the ANOVA report (the printed 4
        decimals)."""
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


if __name__ == '__main__':
    unittest.main()
