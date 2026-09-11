#
# test_wrk_plot.py
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
#
# How to run the PLOT worker unit tests.
#
# Run from the workspace root (the directory containing .venv and src).
#
# -0- Activate the environment.
#
# $ source .venv/bin/activate
#
# -1- Run the tests (no DB needed — the worker is exercised directly
#     on a synthetic rlm_04-mirror context, the same layout as
#     test_wrk_client_check.py).
#
# time python3 -m unittest reversi.test.test_wrk_plot
#

import unittest
import shutil
import hashlib
import tempfile
from pathlib import Path
from types import SimpleNamespace

import numpy as np

from reversi.board import Bitboard, make_position
from reversi.feature import Feature, FeatureSet
from reversi.mobility import Mobility, MobilitySet
from reversi.pattern import Pattern, PatternSet
from reversi.lm.hlp_zed import zed_fun_factory
from reversi.lm.hlp_plot import PLOT_NAMES
from reversi.lm.logistic_model import LMContext
from reversi.lm.wrk_plot import wrk_plot
from reversi.test.paths import CUSTOM_TMP_BASE

SEED = 42
N_TRN = 1200
N_VLD = 1000
ALPHA = 0.01

PNG_MAGIC = b"\x89PNG"
PDF_MAGIC = b"%PDF"


class TestWrkPlot(unittest.TestCase):
    """The PLOT worker (the 17th level, D-149) on a synthetic
    rlm_04-mirror context: the whitelist pilot, the directory
    resolution, the seven figures, the formats, the determinism.
    No DB, no pipeline: the worker is exercised directly. The
    Worker.up @validate_call gate (context: Context) requires a REAL
    LMContext; the cfg attribute is the SimpleNamespace stand-in
    (the D-144 v2 micro-test idiom), the log_event a capturing
    lambda."""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(dir=str(CUSTOM_TMP_BASE))
        self._events = []
        self._ctx = self._build_ctx()

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)

    def _plot_cfg(self, **kw):
        base = dict(enable=True, format="png", dpi=150,
                    dir_name="plots", plots=list(PLOT_NAMES))
        base.update(kw)
        return SimpleNamespace(**base)

    def _build_ctx(self):
        rng = np.random.default_rng(SEED)

        # The rlm_04 feature layout (the fixture rlm_04.json, as in
        # test_wrk_client_check.py): intercept + LMC + EDGE — the
        # production iwmap pin [0, 1, 66, 6627].
        intercept = Feature.new_intercept()
        mset = MobilitySet("MOBILITY",
                           [Mobility("LMC", Bitboard(0xFFFFFFFFFFFFFFFF),
                                     Bitboard(0))])
        pset = PatternSet("EDGE", [Pattern("EDGE", Bitboard(0xFF))])
        fs = FeatureSet("SYNTH_RLM04", intercept, mset, pset)
        offsets = np.concatenate(
            ([0], np.cumsum([f.n_configurations for f in fs.features]))
        ).astype(np.uint32)
        self.assertEqual(offsets.tolist(), [0, 1, 66, 6627])
        w_dense = rng.standard_normal(int(offsets[-1]), dtype=np.float32)

        # The training design indexes: ONE COLUMN PER FEATURE
        # INSTANCE (the compute_indexes layout), each column holding
        # the configuration index within its feature (the
        # hlp_indexes.indexes contract, as in the real INDEXES level).
        indexes = np.concatenate([
            rng.integers(0, f.n_configurations,
                         size=(N_TRN, f.n_instances), dtype=np.uint32)
            for f in fs.features], axis=1)

        # Training game values + seeded collision-free validation
        # positions (the EF caller contract) + int8 game values.
        game_values = (rng.integers(-32, 33, size=N_TRN) * 2
                       ).astype(np.int8)
        m = rng.integers(0, 2**64, size=N_VLD, dtype=np.uint64)
        o = rng.integers(0, 2**64, size=N_VLD, dtype=np.uint64)
        o &= ~m
        positions = make_position(m, o)
        vld_game_values = (rng.integers(-32, 33, size=N_VLD) * 2
                           ).astype(np.int8)

        # The real ZED transforms (the f32 affine pair of logit
        # clipping 0.01, the rlm_03/rlm_04 fixture value).
        y2z, z2y = zed_fun_factory(ALPHA)

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
        ctx.log_event = lambda relevance, message: \
            self._events.append((relevance, message))
        return ctx

    # -- the factory + the no-op pilots ----------------------------------

    def test_factory_returns_named_worker(self):
        """The factory (the uniform @validate_call idiom) returns the
        PLOT worker."""
        self.assertEqual(wrk_plot().name, "PLOT")

    def test_up_disabled_is_a_noop(self):
        """The master switch (the D-149 ruling): enable=false does
        NOTHING, even with the full whitelist — log only, no
        directory, no files."""
        self._ctx.cfg.plot = self._plot_cfg(enable=False)
        wrk_plot().up(self._ctx)
        self.assertFalse((self._ctx.cfg.base_dir / "plots").exists())
        messages = [m for _, m in self._events]
        self.assertEqual(messages, ["PLOT skipped: plot.enable is false."])

    def test_up_empty_whitelist_is_a_noop(self):
        """An empty whitelist (names are OPTIONAL, D-149): the level
        does nothing — log only."""
        self._ctx.cfg.plot = self._plot_cfg(plots=[])
        wrk_plot().up(self._ctx)
        self.assertFalse((self._ctx.cfg.base_dir / "plots").exists())
        messages = [m for _, m in self._events]
        self.assertEqual(
            messages, ["PLOT skipped: no plot names requested."])

    # -- the happy path ----------------------------------------------------

    def test_up_all_seven_png(self):
        """The full whitelist in png: the seven figures in
        base_dir/plots (the relative dir_name default), the PNG
        magic + a non-trivial size, the per-plot save lines and the
        completion line. The second up-move REGENERATES byte-
        identical files (the seeded jitter + the deterministic Agg
        rendering)."""
        ctx = self._ctx
        wrk_plot().up(ctx)
        plot_dir = ctx.cfg.base_dir / "plots"
        for name in PLOT_NAMES:
            p = plot_dir / f"{name}.png"
            self.assertTrue(p.exists(), f"missing {p}")
            self.assertEqual(p.read_bytes()[:4], PNG_MAGIC)
            self.assertGreater(p.stat().st_size, 5000)
        first = {n: hashlib.sha3_256((plot_dir / f"{n}.png")
                                     .read_bytes()).hexdigest()
                 for n in PLOT_NAMES}
        wrk_plot().up(ctx)
        for n, h in first.items():
            self.assertEqual(hashlib.sha3_256(
                (plot_dir / f"{n}.png").read_bytes()).hexdigest(), h,
                f"plot {n} not deterministic across up-moves")
        messages = [m for _, m in self._events]
        for name in PLOT_NAMES:
            self.assertIn(f"Plot '{name}' saved: "
                          f"{plot_dir / (name + '.png')}", messages)
        self.assertIn(f"PLOT done: 7 plot(s) written to {plot_dir}.",
                      messages)

    def test_up_format_pair_writes_both(self):
        """The 'pdf,png' pair (D-149): each whitelisted name is
        written in BOTH formats (the pdf is the vector one, no
        dpi)."""
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
        """An ABSOLUTE dir_name (the D-149 ruling) is used as-is —
        the plots may live outside base_dir; the relative default
        does not leak there."""
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
        """Only the LISTED names are generated (the D-149 ruling: a
        listed name is written, an unlisted one is skipped)."""
        ctx = self._ctx
        ctx.cfg.plot = self._plot_cfg(plots=["resid_vs_fitted"])
        wrk_plot().up(ctx)
        plot_dir = ctx.cfg.base_dir / "plots"
        self.assertEqual(sorted(p.name for p in plot_dir.iterdir()),
                         ["resid_vs_fitted.png"])
        messages = [m for _, m in self._events]
        self.assertIn("PLOT done: 1 plot(s) written to "
                      f"{plot_dir}.", messages)

    # -- the outlier report --------------------------------------------------

    def test_up_outlier_report(self):
        """The D-150 top-20 extreme-outlier report (Roberto's
        "uno spunto capire come mai il modello sbarella cosi"):
        the header line + exactly 20 "vld position" lines (the
        position's bitboards, the game value, the fitted, the
        residual), in descending |residual| order (the stable
        argsort: the report is deterministic)."""
        ctx = self._ctx
        ctx.cfg.plot = self._plot_cfg(plots=["parity"])
        wrk_plot().up(ctx)
        messages = [m for _, m in self._events]
        self.assertIn(
            "Top 20 extreme validation residuals (outlier report):",
            messages)
        outlier_lines = [m for m in messages
                         if "vld position" in m and "residual" in m]
        self.assertEqual(len(outlier_lines), 20)
        self.assertIn("  1.", outlier_lines[0])
        self.assertIn("  20.", outlier_lines[-1])
        # The order: the |residual| is non-increasing down the
        # list (the last reported value, parsed from the line).
        import re
        values = [float(re.search(r"residual ([+\-][\d.]+)$", m)
                        .group(1)) for m in outlier_lines]
        self.assertTrue(all(abs(a) >= abs(b)
                            for a, b in zip(values, values[1:])))

    # -- the golden --------------------------------------------------------

    def test_parity_png_golden(self):
        """The D-149 rendering golden (re-pinned at D-150 for the
        fixed axes + the two-line title; re-pinned at D-158 for the
        env drift — the rendering is visually identical, only the
        font rasterization bytes moved): the parity figure of the
        synthetic context (SEED 42, N_TRN 1200 / N_VLD 1000, the
        rlm_04 mirror, png at 150 dpi) hashes to the pinned value.
        Version-sensitive like the other f32 goldens (D-127): it
        moves when matplotlib or numpy changes."""
        ctx = self._ctx
        ctx.cfg.plot = self._plot_cfg(plots=["parity"])
        wrk_plot().up(ctx)
        p = ctx.cfg.base_dir / "plots" / "parity.png"
        self.assertEqual(
            hashlib.sha3_256(p.read_bytes()).hexdigest(),
            'fdb8162d8f1696ee86c3fa86157720f53aaf6d05abfffd70ecc5a58e41e22ab5')

    # -- the down step ----------------------------------------------------

    def test_down_is_a_noop_log(self):
        """The stateless _down (as SAVE / CLIENT_CHECK): log only."""
        wrk_plot().down(self._ctx)
        messages = [m for _, m in self._events]
        self.assertIn("Clearing plot attributes...", messages)


if __name__ == '__main__':
    unittest.main()
