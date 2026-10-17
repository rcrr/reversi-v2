#
# test_wrk_anova.py
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
# How to run the wrk_anova module unit tests.
#
# Run from the workspace root (the directory containing .venv and src).
#
# -0- Activate the environment.
#
# $ source .venv/bin/activate
#
# -1- Run the tests (no database — the mock ctx, the synthetic indexes + the game values).
#
# time PERF=0 python3 -m unittest test.reversi.lm.test_wrk_anova
#

import tempfile
import unittest
from pathlib import Path

import numpy as np

from reversi.lm.logistic_model import LogisticModel
from reversi.lm.wrk_anova import _down, _up, wrk_anova
from reversi.tools.state_machine import Verbosity
from test.reversi.paths import WORKSPACE_ROOT
from reversi.index import Index


class _MockIndexes:
    def __init__(self, indexes):
        self.indexes = indexes


class _MockCtx:
    """
    The no-DB mock context (the worker's blackboard): the cfg, the feature_set, the hlp_indexes (the
    synthetic raw codes), the game_values, the su_analysis_tables, the log buffer.
    """

    def __init__(self, cfg, feature_set, indexes, game_values, tables):
        self.cfg = cfg
        self.feature_set = feature_set
        self.hlp_indexes = _MockIndexes(indexes)
        self.game_values = game_values
        self.su_analysis_tables = tables
        self.events = []

    def log_event(self, relevance, msg):
        self.events.append((relevance, msg))


def _make_ctx(tmp, enable=True, tables=None, n_positions=100, seed=7):
    """
    A mock ctx over the REAL pipeline's campaign: the facade runs CREATED -> CONFIG -> FEATURES on
    the rlm_00 fixture (the target_level stop + the base_dir override) and the cfg + the feature_set
    come from the real context — no parallel loader. The raw codes + the game values stay SYNTHETIC
    (the DB data, not generatable no-DB).
    """
    rlm = LogisticModel(str(WORKSPACE_ROOT / "test" / "reversi" /
                            "data" / "rlm_00.json"),
                        verbosity=Verbosity.NONE,
                        base_dir_override=tmp)
    rlm.run("FEATURES")
    cfg = rlm.context.cfg
    fset = rlm.context.feature_set
    blocks = fset.feature_blocks
    cfg.anova.enable = enable
    max_col = max(c1 for (_n, c0, c1, _nc, _ni) in blocks)
    rng = np.random.default_rng(seed)
    indexes = np.zeros((n_positions, max_col), dtype=Index)
    for (name, c0, c1, n_conf, n_inst) in blocks:
        for i in range(n_inst):
            indexes[:, c0 + i] = rng.integers(
                0, n_conf, size=n_positions)
    game_values = rng.standard_normal(n_positions)
    return _MockCtx(cfg, fset, indexes, game_values, tables), blocks


class TestWrkAnova(unittest.TestCase):
    """
    The ANOVA worker NO-DB suite: the factory, the enable no-op, the ANOVA, the graceful
    degradation, the adherence, the report, the down (the no-op).
    """

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_factory(self):
        w = wrk_anova()
        self.assertEqual(w.name, "ANOVA")

    def test_enable_no_op(self):
        # The opt-in: the enable false makes the level a no-op (the "disabled" log).
        ctx, _ = _make_ctx(self.tmp, enable=False)
        _up(ctx)
        self.assertTrue(any("disabled" in m for (_r, m) in ctx.events))
        # The no-op consequence: no report dir is created.
        self.assertFalse((self.tmp / "anova").exists())

    def test_anova(self):
        # The eta²/omega² per sub-variable: the REPORT has one ANOVA line per sub-variable (the
        # instance count — the log carries only the "report written" artifact line). Counted by
        # the "eta2" marker in the report content.
        ctx, blocks = _make_ctx(self.tmp, enable=True, tables=None)
        _up(ctx)
        n_sub = sum(ni for (_n, c0, c1, _nc, ni) in blocks)
        report = (self.tmp / "anova" / "anova_report.txt").read_text(encoding="utf-8")
        self.assertEqual(report.count("eta2"), n_sub)

    def test_adherence_graceful_degradation(self):
        # The tables None (the SU_ANALYSIS disabled): the adherence is SKIPPED (the log note), the
        # ANOVA runs.
        ctx, _ = _make_ctx(self.tmp, enable=True, tables=None)
        _up(ctx)
        self.assertTrue(any("SKIPPED" in m for (_r, m) in ctx.events))
        self.assertTrue(any("ANOVA" in m for (_r, m) in ctx.events))

    def test_adherence_computed(self):
        # The tables set (the ideal = the synthetic distribution): the adherence is computed (the
        # log has the Adherence lines, the top-N).
        ctx, blocks = _make_ctx(self.tmp, enable=True, tables=None)
        marginal = []
        for (name, c0, c1, n_conf, n_inst) in blocks:
            for i in range(n_inst):
                codes = ctx.hlp_indexes.indexes[:, c0 + i]
                uniq, cnt = np.unique(codes, return_counts=True)
                marginal.append((name, i, n_conf, uniq, cnt))
        ctx.su_analysis_tables = {'marginal': marginal,
                                       'joint': None}
        _up(ctx)
        report = (self.tmp / "anova" / "anova_report.txt").read_text(encoding="utf-8")
        self.assertTrue("Adherence" in report)

    def test_report_written(self):
        # The TXT report (the dir_name under base_dir).
        ctx, _ = _make_ctx(self.tmp, enable=True, tables=None)
        _up(ctx)
        report = self.tmp / "anova" / "anova_report.txt"
        self.assertTrue(report.exists())

    def test_down_no_op(self):
        # The down is a no-op (the log note).
        ctx, _ = _make_ctx(self.tmp, enable=True, tables=None)
        _up(ctx)
        _down(ctx)
        self.assertTrue(any("down" in m for (_r, m) in ctx.events))


if __name__ == '__main__':
    unittest.main()
