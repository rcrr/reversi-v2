#
# test_wrk_su_analysis.py
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

# How to run the wrk_su_analysis unit tests.
#
# Run from the workspace root (the directory containing .venv and src).
#
# -0- Activate the environment.
#
# $ source .venv/bin/activate
#
# -1- Run the tests (no database — the mock ctx, the tiny corpus).
#
# time PERF=0 python3 -m unittest test.reversi.lm.test_wrk_su_analysis
#

import tempfile
import time
import unittest
from pathlib import Path

from unittest import skipUnless

import numpy as np

from reversi.lm.logistic_model import LogisticModel
from reversi.lm.wrk_su_analysis import (
    _down, _up, wrk_su_analysis)
from reversi.tools.state_machine import Verbosity
from test.reversi.paths import CUSTOM_TMP_BASE, WORKSPACE_ROOT
from test.reversi.tags import tier_vlong


class _MockCtx:
    """
    The no-DB mock context (the worker's blackboard): the cfg, the feature_set, the cache path, the
    use_cache flag, the log buffer, and the su_analysis_tables artifact.
    """

    def __init__(self, cfg, feature_set, cache_path, use_cache=True):
        self.cfg = cfg
        self.feature_set = feature_set
        self._cache_path = cache_path
        self.use_cache = use_cache
        self.su_analysis_tables = None
        self.events = []

    def log_event(self, relevance, msg):
        self.events.append((relevance, msg))

    def get_cache_file_full_path_for_current_level(self):
        return self._cache_path


def _make_ctx(tmp, n_positions, enable=True, su_pairs=None,
              use_cache=True):
    """
    A mock ctx over the REAL pipeline's campaign: the facade runs CREATED -> CONFIG -> FEATURES on
    the rlm_00 fixture (the cfg + feature_set come from the real context — no parallel loader), the
    su_analysis knobs are mutated on the loaded cfg.
    """
    rlm = LogisticModel(str(WORKSPACE_ROOT / "test" / "reversi" /
                            "data" / "rlm_00.json"),
                        verbosity=Verbosity.NONE,
                        base_dir_override=tmp)
    rlm.run("FEATURES")
    cfg = rlm.context.cfg
    fset = rlm.context.feature_set
    cfg.su_analysis.enable = enable
    cfg.su_analysis.corpus.total_positions = n_positions
    cfg.empty_count = 20
    cfg.su_analysis.corpus.seed = 42
    # The explicit no-pairs (the default) — independent of the fixture's su_pairs.
    cfg.su_analysis.su_pairs = \
        [tuple(p) for p in su_pairs] if su_pairs is not None else []
    cache_path = tmp / "rlmwf_03_SU_ANALYSIS.dat"
    return _MockCtx(cfg, fset, cache_path, use_cache=use_cache)


class TestWrkSuAnalysis(unittest.TestCase):
    """
    The SU_ANALYSIS worker NO-DB suite: the factory, the enable no-op, the compute + the publish,
    the cache hit, the signature invalidation, the su_pairs joint, the down (the recovery).
    """

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_factory(self):
        # The worker factory: the SU_ANALYSIS name.
        w = wrk_su_analysis()
        self.assertEqual(w.name, "SU_ANALYSIS")

    def test_enable_no_op(self):
        # The opt-in: the enable false makes the level a no-op (the tables stay None, the "disabled" log).
        ctx = _make_ctx(self.tmp, 1000, enable=False)
        _up(ctx)
        self.assertIsNone(ctx.su_analysis_tables)
        self.assertTrue(any("disabled" in m for (_r, m) in ctx.events))

    def test_compute_and_publish(self):
        # The tiny SU-analysis corpus (2000, ec 20, seed 42) -> the phase- 1 tables + the phase-2
        # statistics + the TXT report + the ctx publication.
        ctx = _make_ctx(self.tmp, 2000, enable=True)
        _up(ctx)
        t = ctx.su_analysis_tables
        self.assertIsNotNone(t)
        self.assertIn('marginal', t)
        self.assertIn('joint', t)
        self.assertIn('signature', t)
        self.assertGreater(len(t['marginal']), 0)
        self.assertIsNone(t['joint'])  # No su_pairs -> no joint.
        report = self.tmp / "su_analysis" / \
            "su_analysis_report.txt"
        self.assertTrue(report.exists())

    def test_cache_hit(self):
        # The second run (the same signature): the cache hit (the "loaded from cache" log).
        _up(_make_ctx(self.tmp, 2000, enable=True))
        ctx2 = _make_ctx(self.tmp, 2000, enable=True)
        _up(ctx2)
        self.assertTrue(any("loaded from cache" in m
                            for (_r, m) in ctx2.events))

    def test_signature_invalidation(self):
        # The corpus change (the total_positions): the signature invalidates the cache (the recompute).
        _up(_make_ctx(self.tmp, 2000, enable=True))
        ctx2 = _make_ctx(self.tmp, 3000, enable=True)
        _up(ctx2)
        self.assertTrue(any("corpus: computed" in m
                            for (_r, m) in ctx2.events))

    def test_corpus_determinism(self):
        # The random_game play-path generator (su-corpus-5): two fresh computes with the same spec
        # are the IDENTICAL marginal tables (the stream is deterministic on the seed), a different
        # seed changes them (the stream is consumed). use_cache False still WARMS the cache — the
        # per-run dirs must exist.
        for sub in ("a", "b", "c"):
            (self.tmp / sub).mkdir(parents=True)
        ctx_a = _make_ctx(self.tmp / "a", 2000, use_cache=False)
        ctx_b = _make_ctx(self.tmp / "b", 2000, use_cache=False)
        _up(ctx_a)
        _up(ctx_b)
        ta = ctx_a.su_analysis_tables['marginal']
        tb = ctx_b.su_analysis_tables['marginal']
        self.assertEqual(len(ta), len(tb))
        for (na, ia, nca, ca, ka), (nb, ib, ncb, cb, kb) in zip(ta, tb):
            self.assertEqual((na, ia, nca), (nb, ib, ncb))
            self.assertTrue(np.array_equal(ca, cb))
            self.assertTrue(np.array_equal(ka, kb))
        ctx_c = _make_ctx(self.tmp / "c", 2000, use_cache=False)
        ctx_c.cfg.su_analysis.corpus.seed = 43
        _up(ctx_c)
        tc = ctx_c.su_analysis_tables['marginal']
        self.assertTrue(any(not np.array_equal(ka, kc)
                            for (_na, _ia, _nca, _ca, ka),
                            (_nb, _ib, _ncb, _cb, kc) in zip(ta, tc)))

    def test_su_pairs_joint(self):
        # The requested su_pairs: the joint is computed (the (EDGE, LMC) pair, the canonical order).
        ctx = _make_ctx(self.tmp, 4000, enable=True,
                        su_pairs=[("EDGE", "LMC")])
        _up(ctx)
        t = ctx.su_analysis_tables
        self.assertIsNotNone(t['joint'])
        names = [(ni, nj) for (ni, nj, _pi) in t['joint']]
        self.assertIn(("EDGE", "LMC"), names)

    def test_export_csv(self):
        # The optional CSV (the export_csv flag): the CSV file is written.
        ctx = _make_ctx(self.tmp, 2000, enable=True)
        ctx.cfg.su_analysis.export_csv = True
        _up(ctx)
        csv_path = self.tmp / "su_analysis" / \
            "su_analysis.csv"
        self.assertTrue(csv_path.exists())

    def test_down_clears(self):
        # The recovery: the down clears the tables.
        ctx = _make_ctx(self.tmp, 2000, enable=True)
        _up(ctx)
        self.assertIsNotNone(ctx.su_analysis_tables)
        _down(ctx)
        self.assertIsNone(ctx.su_analysis_tables)



@skipUnless(tier_vlong(),
            "Skipping the 1e7 corpus test (set VLONG=1 or VVLONG=1 "
            "to run)")
class TestSuCorpusAtScale(unittest.TestCase):
    """
    The SU-analysis corpus at the 1e7 scale (ec 20, seed 42, the rlm_00 feature set; the VLONG cold
    run is ~50 s): the harvested count, the marginal totals, the cache write + hit, and the
    signature identity between the two runs.
    """

    N = 10_000_000

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE))
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_the_corpus_at_the_odp1_scale(self):
        ctx = _make_ctx(self.tmp, self.N, enable=True)
        t0 = time.perf_counter()
        _up(ctx)
        cold = time.perf_counter() - t0

        # 1. The corpus: exactly N harvested positions (the wave engine at scale, the ec 20 arrest).
        self.assertTrue(
            any(f"[HARVESTED: {self.N:,}]" in m for (_r, m) in ctx.events),
            f"the harvest line is missing: {[m for (_r, m) in ctx.events if 'HARVESTED' in m]}")

        # 2. The tables: every sub-variable's counts sum to N (one count per position) and the
        # signature is published.
        tables = ctx.su_analysis_tables
        self.assertIsNotNone(tables)
        self.assertIn('signature', tables)
        marginal = tables['marginal']
        self.assertGreater(len(marginal), 0)
        for (name, i, nc, _codes, counts) in marginal:
            self.assertEqual(int(counts.sum()), self.N,
                             f"the marginal totals of {name} inst {i} "
                             f"are {int(counts.sum())}, not {self.N}")

        # 3. The cache: written, then HIT by a second run with the same signature (the 1e7 spec is
        # part of it).
        self.assertTrue(ctx._cache_path.exists(),
                        "the corpus cache was not written")
        ctx2 = _make_ctx(self.tmp, self.N, enable=True)
        _up(ctx2)
        self.assertTrue(
            any("Cache successfully loaded and validated" in m
                for (_r, m) in ctx2.events),
            "the second run did not hit the cache")
        self.assertEqual(ctx2.su_analysis_tables['signature'],
                         tables['signature'])
        print(f"\n[VLONG] the 1e7 corpus: {cold:.1f} s cold")


if __name__ == '__main__':
    unittest.main()
