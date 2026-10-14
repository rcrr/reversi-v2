#
# test_wrk_plot.py
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
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; or the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA
# or visit the site <http://www.gnu.org/licenses/>.
#

#
# How to run the wrk_plot unit tests. Run from the workspace root (the directory containing .venv
# and src).
#
# -0- Activate the environment.
#
# $ source .venv/bin/activate
#
# -1- Run the tests (no DB needed — the worker is exercised directly on a synthetic rlm_04-mirror
# context, the same layout as test_wrk_client_check.py).
#
# time python3 -m unittest test.reversi.lm.test_wrk_plot
#

import unittest
import hashlib
import tempfile
from pathlib import Path
from types import SimpleNamespace

import numpy as np

from reversi.board import Bitboard, make_position
from reversi.feature import Feature, FeatureSet
from reversi.mobility import Mobility, MobilitySet
from reversi.pattern import Pattern, PatternSet
from reversi.lm.hlp_zed import hlp_zed_fun_factory
from reversi.lm.hlp_plot import HLP_PLOT_NAMES
from reversi.lm.logistic_model import LMContext
from reversi.lm.wrk_plot import wrk_plot
from reversi.lm.hlp_validate import hlp_validate_model
from reversi.lm.hlp_analytics import hlp_analytics_compute_training_dense_metrics
from test.reversi.paths import CUSTOM_TMP_BASE
from reversi.index import Index
from test.reversi.tags import tier_long

SEED = 42
N_TRN = 1200
N_VLD = 1000
ALPHA = 0.01

PNG_MAGIC = b"\x89PNG"
PDF_MAGIC = b"%PDF"


class TestWrkPlot(unittest.TestCase):
    """
    The PLOT worker on a synthetic rlm_04-mirror context (no DB, no pipeline): the whitelist pilot,
    the directory resolution, the seven figures, the formats, the determinism. The Worker.up
    @validate_call gate requires a REAL LMContext (the cfg attribute is the stand-in).
    """

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE))
        self.tmp_dir = self._tmp.name
        self._events = []
        self._ctx = self._build_ctx()

    def tearDown(self):
        if getattr(self, '_tmp', None) is not None:
            self._tmp.cleanup()

    def _plot_cfg(self, **kw):
        base = dict(enable=True, format="png", dpi=150,
                    dir_name="plots", plots=list(HLP_PLOT_NAMES),
                    binned_note=r" $(binned\ every\ 2)$",
                    jitter_seed=42, kde_seed=43, kde_max_points=100_000,
                    jitter_fitted_x=0.005, jitter_y=0.005,
                    jitter_gv_x=0.7, kde_grid=512, axis_gv=64.0,
                    axis_density=72.0, tick_step=8.0,
                    series_label_x={"Validation": 0.04, "Training": 0.674,
                                    "Reference": 0.75},
                    series_label_y={"Validation": 0.80, "Training": 0.96,
                                    "Reference": 0.98})
        base.update(kw)
        return SimpleNamespace(**base)

    def _build_ctx(self):
        rng = np.random.default_rng(SEED)

        # The rlm_04 feature layout (the fixture rlm_04.json, as in test_wrk_client_check.py):
        # intercept + LMC + EDGE — the production iwmap pin [0, 1, 66, 6627].
        intercept = Feature.new_intercept()
        mset = MobilitySet("MOBILITY",
                           [Mobility("LMC", Bitboard(0xFFFFFFFFFFFFFFFF),
                                     'mover')])
        pset = PatternSet("EDGE", [Pattern("EDGE", Bitboard(0xFF))])
        fs = FeatureSet("SYNTH_RLM04", intercept, mset, pset)
        offsets = np.concatenate(
            ([0], np.cumsum([f.n_configurations for f in fs.features]))
        ).astype(Index)
        self.assertEqual(offsets.tolist(), [0, 1, 66, 6627])
        w_dense = rng.standard_normal(int(offsets[-1]), dtype=np.float32)

        # The training design indexes: ONE COLUMN PER FEATURE INSTANCE (the compute_indexes layout),
        # each column holding the configuration index within its feature (the hlp_indexes.indexes
        # contract, as in the real INDEXES level).
        indexes = np.concatenate([
            rng.integers(0, f.n_configurations,
                         size=(N_TRN, f.n_instances), dtype=Index)
            for f in fs.features], axis=1)

        # Training game values + seeded collision-free validation positions (the EF caller contract)
        # + int8 game values.
        game_values = (rng.integers(-32, 33, size=N_TRN) * 2
                       ).astype(np.int8)
        m = rng.integers(0, 2**64, size=N_VLD, dtype=np.uint64)
        o = rng.integers(0, 2**64, size=N_VLD, dtype=np.uint64)
        o &= ~m
        positions = make_position(m, o)
        vld_game_values = (rng.integers(-32, 33, size=N_VLD) * 2
                           ).astype(np.int8)

        # The real ZED transforms (the f32 affine pair of logit clipping 0.01, the rlm_03/rlm_04
        # fixture value).
        y2z, z2y = hlp_zed_fun_factory(ALPHA)

        ctx = LMContext(
            config_file_path=Path(self.tmp_dir) / "config.json")
        ctx.cfg = SimpleNamespace(
            name="SYNTH_PLOT",
            base_dir=Path(self.tmp_dir),
            plot=self._plot_cfg(),
        )
        ctx.feature_set = fs
        ctx.iwmap_feature_offset = offsets
        ctx.w_dense = w_dense
        ctx.hlp_indexes = SimpleNamespace(indexes=indexes)
        ctx.game_values = game_values
        ctx.y2z, ctx.z2y = y2z, z2y
        ctx.vld_positions = positions
        ctx.vld_game_values = vld_game_values
        # The series the pipeline publishes (ANALYTICS + VALIDATE) and PLOT only assembles, never
        # re-derives — here computed with the same functions, on the synthetic state.
        ctx.train_dense_rn = hlp_analytics_compute_training_dense_metrics(ctx).rn_y
        _vr = hlp_validate_model(ctx)
        ctx.vld_y_pred, ctx.vld_rn = _vr.y_pred, _vr.rn_y
        ctx.log_event = lambda relevance, message: \
            self._events.append((relevance, message))
        return ctx

    # -- the factory + the no-op pilots ----------------------------------

    def test_factory_returns_named_worker(self):
        """The factory (the uniform @validate_call idiom) returns the PLOT worker."""
        self.assertEqual(wrk_plot().name, "PLOT")

    def test_up_disabled_is_a_noop(self):
        """
        The master switch: enable=false does NOTHING, even with the full whitelist — log only, no
        directory, no files.
        """
        self._ctx.cfg.plot = self._plot_cfg(enable=False)
        wrk_plot().up(self._ctx)
        self.assertFalse((self._ctx.cfg.base_dir / "plots").exists())
        messages = [m for _, m in self._events]
        self.assertEqual(messages, ["PLOT skipped: plot.enable is false."])

    def test_up_empty_whitelist_is_a_noop(self):
        """An empty whitelist (names are OPTIONAL): the level does nothing — log only."""
        self._ctx.cfg.plot = self._plot_cfg(plots=[])
        wrk_plot().up(self._ctx)
        self.assertFalse((self._ctx.cfg.base_dir / "plots").exists())
        messages = [m for _, m in self._events]
        self.assertEqual(
            messages, ["PLOT skipped: no plot names requested."])

    # -- the happy path ----------------------------------------------------

    @unittest.skipUnless(tier_long(), "Skipping the LONG-tier test (set LONG=1 to run)")
    def test_up_all_seven_png(self):
        """
        The full whitelist in png: the seven figures in base_dir/plots, the PNG magic + a
        non-trivial size, the per-plot save lines and the completion line; the second up-move
        REGENERATES byte-identical files (seeded jitter + deterministic Agg rendering).
        """
        ctx = self._ctx
        wrk_plot().up(ctx)
        plot_dir = ctx.cfg.base_dir / "plots"
        for name in HLP_PLOT_NAMES:
            p = plot_dir / f"{name}.png"
            self.assertTrue(p.exists(), f"missing {p}")
            self.assertEqual(p.read_bytes()[:4], PNG_MAGIC)
            self.assertGreater(p.stat().st_size, 5000)
        first = {n: hashlib.sha3_256((plot_dir / f"{n}.png")
                                     .read_bytes()).hexdigest()
                 for n in HLP_PLOT_NAMES}
        wrk_plot().up(ctx)
        for n, h in first.items():
            self.assertEqual(hashlib.sha3_256(
                (plot_dir / f"{n}.png").read_bytes()).hexdigest(), h,
                f"plot {n} not deterministic across up-moves")
        messages = [m for _, m in self._events]
        for name in HLP_PLOT_NAMES:
            self.assertIn(f"Plot '{name}' saved: "
                          f"{plot_dir / (name + '.png')}", messages)
        self.assertIn(f"PLOT done: 7 plot(s) written to {plot_dir}.",
                      messages)

    @unittest.skipUnless(tier_long(), "Skipping the LONG-tier test (set LONG=1 to run)")
    def test_up_format_pair_writes_both(self):
        """
        The 'pdf,png' pair: each whitelisted name is written in BOTH formats (the pdf is the vector
        one, no dpi).
        """
        ctx = self._ctx
        ctx.cfg.plot = self._plot_cfg(format="pdf,png",
                                      plots=["parity", "resid_qq"])
        wrk_plot().up(ctx)
        plot_dir = ctx.cfg.base_dir / "plots"
        for name in ("parity", "resid_qq"):
            self.assertEqual((plot_dir / f"{name}.pdf").read_bytes()[:4],
                             PDF_MAGIC)
            self.assertEqual((plot_dir / f"{name}.png").read_bytes()[:4],
                             PNG_MAGIC)
        # Exactly 4 files: two names x two formats, nothing else.
        self.assertEqual(len(list(plot_dir.iterdir())), 4)

    def test_up_absolute_dir_name(self):
        """
        An ABSOLUTE dir_name is used as-is — the plots may live outside base_dir; the relative
        default does not leak there.
        """
        ctx = self._ctx
        abs_dir = Path(self.tmp_dir) / "elsewhere" / "figures"
        ctx.cfg.plot = self._plot_cfg(dir_name=str(abs_dir),
                                      plots=["resid_vs_gv"])
        wrk_plot().up(ctx)
        p = abs_dir / "resid_vs_gv.png"
        self.assertTrue(p.exists())
        self.assertEqual(p.read_bytes()[:4], PNG_MAGIC)
        self.assertFalse((ctx.cfg.base_dir / "plots").exists())

    def test_up_partial_whitelist(self):
        """
        Only the LISTED names are generated: a listed name is written, an unlisted one is skipped).
        """
        ctx = self._ctx
        ctx.cfg.plot = self._plot_cfg(plots=["resid_vs_fitted"])
        wrk_plot().up(ctx)
        plot_dir = ctx.cfg.base_dir / "plots"
        self.assertEqual(sorted(p.name for p in plot_dir.iterdir()),
                         ["resid_vs_fitted.png"])
        messages = [m for _, m in self._events]
        self.assertIn("PLOT done: 1 plot(s) written to "
                      f"{plot_dir}.", messages)

    # -- the golden --------------------------------------------------------

    def test_parity_png_golden(self):
        """
        The rendering golden: the parity figure of the synthetic context (SEED 42, N_TRN 1200 /
        N_VLD 1000, the rlm_04 mirror, 150 dpi) hashes to the pinned value; version-sensitive like
        the f32 goldens — it moves when matplotlib, numpy or the environment fonts change.
        """
        ctx = self._ctx
        ctx.cfg.plot = self._plot_cfg(plots=["parity"])
        wrk_plot().up(ctx)
        p = ctx.cfg.base_dir / "plots" / "parity.png"
        self.assertEqual(
            hashlib.sha3_256(p.read_bytes()).hexdigest(),
            '7939f3b3dceaa959a5683baf3dc4303e6e4df4ba252d19008e1033ba730b03c0')

    # -- the down step ----------------------------------------------------

    def test_down_is_a_noop_log(self):
        """The stateless _down (as SAVE / CLIENT_CHECK): log only."""
        wrk_plot().down(self._ctx)
        messages = [m for _, m in self._events]
        self.assertIn("Clearing plot attributes...", messages)

    # -- the small (NORMAL-tier) up tests ----------------------------------

    def _build_small_ctx(self):
        """
        A SMALLER variant of the class's synthetic ctx (N_TRN 100 / N_VLD 75, dpi 50): the same
        layout as _build_ctx with the reduced row counts — the fast NORMAL-tier up tests.
        """
        n_trn, n_vld = 100, 75
        rng = np.random.default_rng(SEED)

        # The rlm_04 feature layout (the same fixture layout as _build_ctx).
        intercept = Feature.new_intercept()
        mset = MobilitySet("MOBILITY",
                           [Mobility("LMC", Bitboard(0xFFFFFFFFFFFFFFFF),
                                     'mover')])
        pset = PatternSet("EDGE", [Pattern("EDGE", Bitboard(0xFF))])
        fs = FeatureSet("SYNTH_RLM04", intercept, mset, pset)
        offsets = np.concatenate(
            ([0], np.cumsum([f.n_configurations for f in fs.features]))
        ).astype(Index)
        self.assertEqual(offsets.tolist(), [0, 1, 66, 6627])
        w_dense = rng.standard_normal(int(offsets[-1]), dtype=np.float32)

        indexes = np.concatenate([
            rng.integers(0, f.n_configurations,
                         size=(n_trn, f.n_instances), dtype=Index)
            for f in fs.features], axis=1)

        game_values = (rng.integers(-32, 33, size=n_trn) * 2
                       ).astype(np.int8)
        m = rng.integers(0, 2**64, size=n_vld, dtype=np.uint64)
        o = rng.integers(0, 2**64, size=n_vld, dtype=np.uint64)
        o &= ~m
        positions = make_position(m, o)
        vld_game_values = (rng.integers(-32, 33, size=n_vld) * 2
                           ).astype(np.int8)

        y2z, z2y = hlp_zed_fun_factory(ALPHA)

        ctx = LMContext(
            config_file_path=Path(self.tmp_dir) / "config.json")
        ctx.cfg = SimpleNamespace(
            name="SYNTH_PLOT_SMALL",
            base_dir=Path(self.tmp_dir),
            plot=self._plot_cfg(dpi=50))
        ctx.feature_set = fs
        ctx.iwmap_feature_offset = offsets
        ctx.w_dense = w_dense
        ctx.hlp_indexes = SimpleNamespace(indexes=indexes)
        ctx.game_values = game_values
        ctx.y2z, ctx.z2y = y2z, z2y
        ctx.vld_positions = positions
        ctx.vld_game_values = vld_game_values
        ctx.train_dense_rn = hlp_analytics_compute_training_dense_metrics(ctx).rn_y
        _vr = hlp_validate_model(ctx)
        ctx.vld_y_pred, ctx.vld_rn = _vr.y_pred, _vr.rn_y
        ctx.log_event = lambda relevance, message: \
            self._events.append((relevance, message))
        return ctx

    def test_up_format_pair_writes_both_small(self):
        """
        The 'pdf,png' pair at SMALL scale: the single whitelisted name is written in BOTH formats,
        exactly two files, the single saved line lists both paths.
        """
        ctx = self._build_small_ctx()
        ctx.cfg.plot = self._plot_cfg(dpi=50, format="pdf,png",
                                      plots=["parity"])
        wrk_plot().up(ctx)
        plot_dir = ctx.cfg.base_dir / "plots"
        self.assertEqual((plot_dir / "parity.pdf").read_bytes()[:4], PDF_MAGIC)
        self.assertEqual((plot_dir / "parity.png").read_bytes()[:4], PNG_MAGIC)
        # Exactly 2 files: one name x two formats, nothing else.
        self.assertEqual(len(list(plot_dir.iterdir())), 2)
        messages = [m for _, m in self._events]
        self.assertIn("Plot 'parity' saved: "
                      f"{plot_dir / 'parity.pdf'}, {plot_dir / 'parity.png'}",
                      messages)


if __name__ == '__main__':
    unittest.main()
