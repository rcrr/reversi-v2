#
# test_hlp_su_analysis.py
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
# How to run the hlp_su_analysis module unit tests.
#
# Run from the workspace root (the directory containing .venv and src).
#
# -0- Activate the environment.
#
# $ source .venv/bin/activate
#
# -1- Run the tests (no database — the real-pipeline ctx stopped at
#     the FEATURES level, the D-287 idiom).
#
# time PERF=0 python3 -m unittest test.reversi.lm.test_hlp_su_analysis
#

"""
The SU analysis LOGIC NO-DB suite (D-289): the consistency
signature (the feature_set hash, the independent sha3_256), the
binio round-trip (with / without the joint), the load guards (the
description / the version / the sidecar), the compute determinism,
the theoretical configuration space (D-278/D-279), the SU groups
(dedup + the canonical sort), the diagonal omission, the report +
the optional CSV, and the cache consistency.
"""

import hashlib
import tempfile
import unittest
from pathlib import Path

import numpy as np

from reversi.tools import binio
from reversi.tools.state_machine import Verbosity
from reversi.lm import hlp_su_analysis as hlp
from reversi.lm.hlp_su_analysis import (
    hlp_su_analysis_compute,
    hlp_su_analysis_load_from_file,
    hlp_su_analysis_statistics,
    hlp_su_analysis_store_to_file,
    hlp_su_analysis_is_cache_consistent)
from reversi.lm.logistic_model import LogisticModel
from test.reversi.paths import WORKSPACE_ROOT

FIXTURE = (WORKSPACE_ROOT / "test" / "reversi" / "data" / "rlm_00.json")


class TestHlpSuAnalysis(unittest.TestCase):
    """The SU analysis logic suite: the signature, the binio I/O,
    the compute determinism, the statistics kernels, the report +
    the CSV, the cache consistency. The ctx is the REAL pipeline
    stopped at the FEATURES level (the D-287 idiom), silent."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def _ctx(self, total=2000, seed=42, su_pairs=None):
        """The real pipeline stopped at the FEATURES level, with the
        su_analysis knobs mutated on the loaded cfg (the D-287
        idiom, the worker-suite _make_ctx pattern minus the mock)."""
        rlm = LogisticModel(str(FIXTURE), verbosity=Verbosity.NONE,
                            base_dir_override=self.tmp)
        rlm.run("FEATURES")
        ctx = rlm.context
        ctx.cfg.su_analysis.corpus.total_positions = total
        ctx.cfg.su_analysis.corpus.seed = seed
        if su_pairs is not None:
            ctx.cfg.su_analysis.su_pairs = [tuple(p) for p in su_pairs]
        return ctx

    def _same_marginal(self, a, b):
        self.assertEqual(len(a), len(b))
        for (n1, i1, nc1, c1, t1), (n2, i2, nc2, c2, t2) in zip(a, b):
            self.assertEqual((n1, i1, nc1), (n2, i2, nc2))
            self.assertTrue(np.array_equal(c1, c2))
            self.assertTrue(np.array_equal(t1, t2))

    def test_signature(self):
        # The signature: the feature_set hash = the FeatureSet DOMAIN
        # hash (D-291) — recomposed INDEPENDENTLY from the child sets
        # (the INTERCEPT marker + the mset / pset hash hex strings) +
        # the spec + the fixture's pairs.
        ctx = self._ctx()
        # The signature is INTERNAL (the D-290 policy): the test
        # reaches the name directly, as the probe does.
        sig = hlp._signature(ctx)
        fs = ctx.feature_set
        chunks = []
        if fs.intercept:
            chunks.append(b"INTERCEPT")
        if fs.mset:
            chunks.append(fs.mset.hash.encode())
        if fs.pset:
            chunks.append(fs.pset.hash.encode())
        ref = hashlib.sha3_256(b"".join(chunks)).hexdigest()
        self.assertEqual(sig["feature_set_hash"], ref)
        self.assertEqual(sig["feature_set_hash"], fs.hash)
        self.assertEqual(sig["seed"], 42)
        self.assertEqual(sig["total_positions"], 2000)
        self.assertEqual(sig["ec"], 20)
        self.assertEqual(sig["generator_version"], "su-corpus-3")
        self.assertEqual(sig["prng_version"], "mt19937-64")
        # The fixture's pair, in the config's canonical (sorted) order.
        self.assertEqual(sig["su_pairs"], [["EDGE", "LMC"]])

    def test_binio_round_trip_joint(self):
        # The store -> load round-trip with the joint: the signature,
        # the marginal (the arrays) + the joint (the per-instance
        # dict) come back identical.
        ctx = self._ctx()
        tables = hlp_su_analysis_compute(ctx)
        path = self.tmp / "rt_joint.dat"
        hlp_su_analysis_store_to_file(tables, path)
        back = hlp_su_analysis_load_from_file(path, checksum=False)
        self.assertEqual(back["signature"], tables["signature"])
        self._same_marginal(back["marginal"], tables["marginal"])
        self.assertEqual(len(back["joint"]), len(tables["joint"]))
        for (n1, nj1, pd1), (n2, nj2, pd2) in zip(back["joint"],
                                                  tables["joint"]):
            self.assertEqual((n1, nj1), (n2, nj2))
            self.assertEqual(set(pd1), set(pd2))
            for key in pd2:
                for a, b in zip(pd1[key], pd2[key]):
                    self.assertTrue(np.array_equal(a, b))

    def test_binio_round_trip_no_joint(self):
        # The no-pairs case: the joint is None and comes back None
        # (the presence flag).
        ctx = self._ctx(su_pairs=[])
        tables = hlp_su_analysis_compute(ctx)
        self.assertIsNone(tables["joint"])
        path = self.tmp / "rt_nojoint.dat"
        hlp_su_analysis_store_to_file(tables, path)
        back = hlp_su_analysis_load_from_file(path, checksum=False)
        self.assertIsNone(back["joint"])
        self._same_marginal(back["marginal"], tables["marginal"])

    def test_load_guards(self):
        # The load guards: the sidecar mismatch (the corrupted
        # content), the wrong description, the wrong version — all
        # fail loudly (the manager's R2 then deletes + recomputes).
        ctx = self._ctx()
        tables = hlp_su_analysis_compute(ctx)
        path = self.tmp / "g.dat"
        hlp_su_analysis_store_to_file(tables, path)
        binio.write_sha3_256_sidecar(path)
        with open(path, "ab") as f:
            f.write(b"X")  # Corrupt the content (the sidecar now mismatches).
        with self.assertRaises(RuntimeError):
            hlp_su_analysis_load_from_file(path)
        with binio.BinaryWriter(self.tmp / "b.dat", compressed=True,
                                checksum=False) as w:
            w.write_header("WRONG description", 1)
        with self.assertRaises(RuntimeError):
            hlp_su_analysis_load_from_file(self.tmp / "b.dat",
                                           checksum=False)
        with binio.BinaryWriter(self.tmp / "c.dat", compressed=True,
                                checksum=False) as w:
            w.write_header("SU_ANALYSIS corpus cache", 99)
        with self.assertRaises(RuntimeError):
            hlp_su_analysis_load_from_file(self.tmp / "c.dat",
                                           checksum=False)

    def test_compute_determinism(self):
        # The compute: the same seed -> the identical marginal; a
        # different seed -> a different one (the PRNG stream is
        # pinned).
        a = hlp_su_analysis_compute(self._ctx())
        b = hlp_su_analysis_compute(self._ctx())
        self._same_marginal(a["marginal"], b["marginal"])
        c = hlp_su_analysis_compute(self._ctx(seed=43))
        self.assertFalse(all(np.array_equal(t1, t2)
                             for (_n, _i, _nc, _c, t1),
                             (_n2, _i2, _nc2, _c2, t2)
                             in zip(a["marginal"], c["marginal"])))

    def test_theoretical_configs(self):
        # The theoretical configuration space (D-278/D-279): the
        # independent re-derivation over the fset's own attributes +
        # the PATTERN -> n_unique_configs / the MOBILITY ->
        # n_configurations semantics + the INTERCEPT excluded.
        ctx = self._ctx()
        space = hlp._theoretical_configs(ctx.feature_set)
        exp = {}
        for f in ctx.feature_set.features:
            if f.name == 'INTERCEPT':
                continue
            nu = getattr(f.ref, 'n_unique_configs', None)
            eff = nu if nu is not None else f.n_configurations
            for i in range(f.n_instances):
                exp[(f.name, i)] = eff
        self.assertEqual(space, exp)
        for f in ctx.feature_set.features:
            if f.name == 'INTERCEPT':
                continue
            if getattr(f.ref, 'n_unique_configs', None) is not None:
                self.assertEqual(space[(f.name, 0)], f.ref.n_unique_configs)
            else:
                self.assertEqual(space[(f.name, 0)], f.n_configurations)
        for i in range(ctx.feature_set.features[0].n_instances):
            self.assertNotIn(("INTERCEPT", i), space)

    def test_su_groups_dedup_sort(self):
        # The SU groups: the (i, j) / the (j, i) are ONE measurement
        # (deduped, the canonical endpoint order), the groups in the
        # configured order, the entries canonically sorted.
        su = [("LMC", 0, "EDGE", 1, 0.3),
              ("EDGE", 1, "LMC", 0, 0.3),  # The reverse direction.
              ("EDGE", 0, "LMC", 0, 0.7),
              ("EDGE", 2, "LMC", 0, 0.5)]
        groups = hlp._su_groups(su, [("LMC", "EDGE")])
        self.assertEqual(len(groups), 1)
        gk, grp = groups[0]
        self.assertEqual(gk, ("EDGE", "LMC"))
        self.assertEqual(len(grp), 3)
        self.assertEqual((grp[0][0], grp[0][1], grp[0][2], grp[0][3]),
                         ("EDGE", 0, "LMC", 0))
        self.assertEqual((grp[1][0], grp[1][1], grp[1][2], grp[1][3]),
                         ("EDGE", 1, "LMC", 0))
        self.assertEqual((grp[2][0], grp[2][1], grp[2][2], grp[2][3]),
                         ("EDGE", 2, "LMC", 0))

    def test_su_values_diagonal_omitted(self):
        # The SU values: the same-feature DIAGONAL (ii == jj) is
        # omitted (the SU = 1 lock), the off-diagonal is kept.
        joint = [("EDGE", "EDGE",
                  {(0, 0): (np.array([0, 1]), np.array([0, 1]),
                             np.array([2, 2])),
                   (0, 1): (np.array([0]), np.array([1]),
                             np.array([2]))})]
        lookup = {("EDGE", 0): np.array([1, 1]),
                  ("EDGE", 1): np.array([1, 1])}
        su = hlp._su_values(joint, lookup)
        self.assertEqual(len(su), 1)
        self.assertEqual((su[0][0], su[0][1], su[0][2], su[0][3]),
                         ("EDGE", 0, "EDGE", 1))

    def test_statistics_report(self):
        # The statistics (phase 2): the report file under base_dir
        # (the Section A + the optional Section B rarity — the
        # fixture carries the thresholds — + the Section C, the
        # header lines) + the CSV OFF (the fixture default).
        ctx = self._ctx()
        tables = hlp_su_analysis_compute(ctx)
        report = hlp_su_analysis_statistics(ctx, tables)
        self.assertTrue(report.exists())
        txt = report.read_text()
        self.assertIn("Symmetrical Uncertainity Analysis Report", txt)
        self.assertIn("Section A: Properties of features selected by",
                      txt)
        self.assertIn("Section B: Rarity report", txt)
        self.assertIn("Section C: Symmetrical uncertainity", txt)
        self.assertIn("SU pairs: EDGE - LMC", txt)
        self.assertFalse((self.tmp / "su_analysis" /
                          "su_analysis.csv").exists())

    def test_rarity_bins(self):
        # The Section B bins (D-292): the half-open [0, t1),
        # ..., [tk, inf) — the first bin the zero-frequency
        # codes. The bins are recomputed INDEPENDENTLY (the pure
        # python count) and the report lines asserted verbatim.
        ctx = self._ctx()
        tables = hlp_su_analysis_compute(ctx)
        report = hlp_su_analysis_statistics(ctx, tables)
        txt = report.read_text()
        self.assertIn("Section B: Rarity report", txt)
        thr = ctx.cfg.su_analysis.rarity_thresholds
        self.assertEqual(thr, [1, 2, 5, 10, 100])
        theoretical = hlp._theoretical_configs(ctx.feature_set)
        b_rows = []
        for (name, i, nc, _codes, counts) in tables["marginal"]:
            eff = theoretical.get((name, i), nc)
            obs = [c for c in np.asarray(counts).tolist() if c > 0]
            bins = [0] * (len(thr) + 1)
            for c in obs:
                bins[sum(1 for t in thr if c >= t)] += 1
            bins[0] += eff - len(obs)
            b_rows.append((name, i, bins))
        labels, lo = [], 0
        for t in thr:
            labels.append(f"[{lo},{t})")
            lo = t
        labels.append(f"[{lo},inf)")
        # The D-293 alignment: the name LEFT-justified to the max,
        # each bin value RIGHT-justified to its own max width + 1.
        name_w = max(len(r[0]) for r in b_rows)
        inst_w = max(len(str(r[1])) for r in b_rows)
        bwidths = [max(len(str(r[2][j])) for r in b_rows) + 1
                   for j in range(len(labels))]
        for (name, i, bins) in b_rows:
            parts = [f"{labels[j]}{bins[j]:>{bwidths[j]}}"
                     for j in range(len(labels))]
            self.assertIn(
                f"  {name:<{name_w}} inst {i:>{inst_w}}: "
                + " | ".join(parts), txt)

    def test_rarity_empty_off(self):
        # The empty list = the section off (the D-292 rule): no
        # Section B, and the SU pairs are ALWAYS Section C.
        ctx = self._ctx()
        ctx.cfg.su_analysis.rarity_thresholds = []
        tables = hlp_su_analysis_compute(ctx)
        report = hlp_su_analysis_statistics(ctx, tables)
        txt = report.read_text()
        self.assertNotIn("Section B: Rarity report", txt)
        self.assertIn("Section C: Symmetrical uncertainity", txt)

    def test_export_csv(self):
        # The optional CSV: the marginal rows + the su rows (the
        # export_csv flag).
        ctx = self._ctx()
        ctx.cfg.su_analysis.export_csv = True
        tables = hlp_su_analysis_compute(ctx)
        hlp_su_analysis_statistics(ctx, tables)
        csv_path = self.tmp / "su_analysis" / "su_analysis.csv"
        self.assertTrue(csv_path.exists())
        lines = csv_path.read_text().splitlines()
        self.assertEqual(lines[0].split(",")[0], "type")
        self.assertTrue(any(l.startswith("marginal,") for l in lines[1:]))
        self.assertTrue(any(l.startswith("su,") for l in lines[1:]))

    def test_is_cache_consistent(self):
        # The cache consistency: the same spec -> True; the seed
        # change -> False.
        ctx = self._ctx()
        live = hlp._signature(ctx)
        cached = {'signature': dict(live)}
        self.assertTrue(hlp_su_analysis_is_cache_consistent(ctx, cached))
        ctx.cfg.su_analysis.corpus.seed = 43
        self.assertFalse(hlp_su_analysis_is_cache_consistent(ctx, cached))
