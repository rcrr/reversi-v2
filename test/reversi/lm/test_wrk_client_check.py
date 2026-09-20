#
# test_wrk_client_check.py
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
# How to run the CLIENT_CHECK worker unit tests.
#
# Run from the workspace root (the directory containing .venv and src).
#
# -0- Activate the environment.
#
# $ source .venv/bin/activate
#
# -1- Run the tests (no DB needed — the worker is exercised directly
#     on a synthetic rlm_04-mirror context, the same layout as
#     test_client.py).
#
# time python3 -m unittest test.reversi.lm.test_wrk_client_check
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
from reversi.lm.model_weights import model_weights_write_file
from reversi.lm.logistic_model import LMContext
from reversi.lm.wrk_client_check import wrk_client_check
from reversi.lm.hlp_validate import validate_model
from test.reversi.paths import CUSTOM_TMP_BASE

SEED = 42
N_VLD = 2000
ALPHA = 0.01


class TestWrkClientCheck(unittest.TestCase):
    """The CLIENT_CHECK worker on a synthetic
    rlm_04-mirror context: the model file round-trip + the client's
    array EF vs the in-memory VALIDATE forward pass. No DB, no
    pipeline: the worker is exercised directly. The Worker.up
    @validate_call gate (context: Context) requires a REAL LMContext;
    the cfg attribute is the SimpleNamespace stand-in (the v2
    micro-test idiom), the log_event a capturing lambda."""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(dir=str(CUSTOM_TMP_BASE))
        self._events = []
        self._ctx = self._build_ctx()

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)

    def _build_ctx(self):
        rng = np.random.default_rng(SEED)

        # The rlm_04 feature layout (the fixture rlm_04.json, as in
        # test_client.py): intercept + LMC (the full board, amask 0)
        # + EDGE (row 1) — the production iwmap pin [0, 1, 66, 6627].
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

        # Seeded collision-free validation positions (the EF caller
        # contract: mover & opponent == 0) + int8 game values (the
        # regab contract: [-64, 64] in steps of 2).
        m = rng.integers(0, 2**64, size=N_VLD, dtype=np.uint64)
        o = rng.integers(0, 2**64, size=N_VLD, dtype=np.uint64)
        o &= ~m
        positions = make_position(m, o)
        game_values = (rng.integers(-32, 33, size=N_VLD) * 2
                       ).astype(np.int8)

        # The real ZED transforms (the f32 affine pair of logit
        # clipping 0.01, the rlm_03/rlm_04 fixture value).
        y2z, z2y = zed_fun_factory(ALPHA)

        ctx = LMContext(
            config_file_path=Path(self.tmp_dir) / "config.json")
        dump = '{"name": "SYNTH_CC", "marker": "SYNTH"}'
        ctx.cfg = SimpleNamespace(
            name="SYNTH_CC",
            base_dir=Path(self.tmp_dir),
            output=Path("synth_client_check.dat"),
            client_check_tol=1e-8,
            regab_data_set=SimpleNamespace(ec=20),
            stat_model=SimpleNamespace(logit_clipping=ALPHA),
            model_dump_json=lambda indent=4: dump,
        )
        ctx.config_checksum = hashlib.sha3_256(dump.encode()).hexdigest()
        ctx.feature_set = fs
        ctx.iwmap_feature_offset = offsets
        ctx.w_dense = w_dense
        ctx.y2z, ctx.z2y = y2z, z2y
        ctx.vld_positions = positions
        ctx.vld_game_values = game_values
        ctx.training_pop_stats = {"count": 100, "mean": 0.5,
                                  "std_dev": 1.5, "variance": 2.25}
        ctx.opt_info = {"reason": "CONVERGED_MIN_GRAD", "iters": 7,
                        "f": 0.01, "g_norm": 1e-6}
        ctx.vld_metrics = {"vld_samples": N_VLD, "vld_rmse_y": 1.0,
                           "vld_mae_y": 0.5, "vld_loss": 0.0025}
        # The validation series the check consumes — published
        # by VALIDATE, here derived with the SAME hlp_validate pass
        # (the level that owns it) on the synthetic state.
        ctx.vld_rn = validate_model(ctx).rn_y
        # The log capture (the LMContext default is the no-op lambda).
        ctx.log_event = lambda relevance, message: \
            self._events.append((relevance, message))
        return ctx

    def _write_model_file(self):
        # The real SAVE write (the v2 model file, LZ4, the binio
        # sidecar included).
        ctx = self._ctx
        model_weights_write_file(ctx, ctx.cfg.base_dir / ctx.cfg.output,
                                 compressed=True)

    # -- the factory + the happy path ------------------------------------

    def test_factory_returns_named_worker(self):
        """The factory (the uniform @validate_call idiom) returns the
        CLIENT_CHECK worker."""
        self.assertEqual(wrk_client_check().name, "CLIENT_CHECK")

    def test_up_passes_on_unmodified_file(self):
        """The file round-trip + the client's array EF reproduce the
        validation residuals BIT-EXACTLY (max difference 0.0 < the
        1e-8 tolerance — the same f32 pipeline over the bit-exact
        round-trip): the check passes and logs the completion line
        (the bit-identity golden)."""
        self._write_model_file()
        wrk_client_check().up(self._ctx)
        messages = [m for _, m in self._events]
        self.assertIn("Starting client check...", messages)
        self.assertIn(
            "Client check passed: 2000 validation residuals, "
            "max difference 0.000e+00 (tolerance 1.0e-08).",
            messages)

    def test_up_missing_file_raises(self):
        """No SAVE artifact (the file was never written): the read
        raises, the exception propagates (the failure
        semantics: the machine logs and re-raises, the step stays at
        CLIENT_CHECK)."""
        with self.assertRaises(FileNotFoundError):
            wrk_client_check().up(self._ctx)

    # -- the failure path ---------------------------------------------------

    def test_up_diverged_weights_raise(self):
        """The FILE diverges from the validation series (the drift
        case): the file is written from a
        DIVERGED in-memory state, so its residuals differ from the
        series VALIDATE published — the max difference is far above
        the 1e-8 tolerance, the worker logs the ERROR line and raises
        RuntimeError."""
        self._ctx.w_dense = self._ctx.w_dense + np.float32(1e-3)
        self._write_model_file()
        with self.assertRaisesRegex(
                RuntimeError,
                r"CLIENT_CHECK failed: the validation residuals "
                r"recomputed from the saved model file differ from "
                r"the in-memory validation residuals by [\d.]+e-\d+ "
                r"\(first at position \d+\), above the tolerance "
                r"1\.0e-08\."):
            wrk_client_check().up(self._ctx)
        failed = [m for _, m in self._events if "FAILED" in m]
        self.assertEqual(len(failed), 1)

    def test_tolerance_is_read_from_config(self):
        """The tolerance is the cfg field (the JSON config value, not
        a module constant): the same diverged FILE (max difference
        ~0.2, written from a diverged state) is ADMITTED by a wide
        tolerance (1.0) and REJECTED by a tight one (1e-4)."""
        self._ctx.w_dense = self._ctx.w_dense + np.float32(1e-3)
        self._write_model_file()
        self._ctx.cfg.client_check_tol = 1.0
        wrk_client_check().up(self._ctx)  # passes: ~0.2 < 1.0
        self._ctx.cfg.client_check_tol = 1e-4
        with self.assertRaises(RuntimeError):
            wrk_client_check().up(self._ctx)

    # -- the down step ----------------------------------------------------

    def test_down_is_a_noop_log(self):
        """The stateless _down (as SAVE): log only, nothing is
        cleared (the worker re-reads the file on every up-move)."""
        wrk_client_check().down(self._ctx)
        messages = [m for _, m in self._events]
        self.assertIn("Clearing client check attributes...", messages)


if __name__ == '__main__':
    unittest.main()
