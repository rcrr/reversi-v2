#
# test_wrk_save.py
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

# How to run the wrk_save unit tests.
#
# Run from the workspace root (the directory containing .venv and src).
#
# -0- Activate the environment.
#
# $ source .venv/bin/activate
#
# -1- Run the tests.
#
# time PERF=0 python3 -m unittest test.reversi.lm.test_wrk_save
#

import hashlib
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import numpy as np

from reversi.feature import Feature, FeatureSet
from reversi.mobility import Mobility, MobilitySet
from reversi.pattern import Pattern, PatternSet
from reversi.tools.state_machine import Worker
from reversi.lm.model_weights import model_weights_read_file
from reversi.lm.wrk_save import _down, _up, wrk_save
from test.reversi.paths import CUSTOM_TMP_BASE


def _mock_ctx(base_dir):
    """The minimal mock ctx the SAVE level reads (the NO-DB idiom: a tiny 2-feature set)."""
    dump = '{"name": "test_model", "empty_count": 20}'
    return SimpleNamespace(
        cfg=SimpleNamespace(
            base_dir=Path(base_dir),
            output="model.bin",
            name="test_model",
            empty_count=20,
            stat_model=SimpleNamespace(logit_clipping=6.0),
            model_dump_json=lambda indent=None: dump,
        ),
        config_checksum=hashlib.sha3_256(dump.encode()).hexdigest(),
        training_pop_stats={'count': 100, 'mean': 0.5, 'std_dev': 0.1, 'variance': 0.01},
        opt_info={'reason': 'CONVERGED', 'iters': 10, 'f': 0.25, 'g_norm': 0.01},
        vld_metrics={'vld_samples': 50, 'vld_rmse_y': 1.5, 'vld_mae_y': 1.2, 'vld_loss': 0.3},
        feature_set=FeatureSet(
            "fs_test", Feature.new_intercept(),
            MobilitySet("mset", [Mobility("LMC", np.uint64(0xff), "mover")]),
            PatternSet("pset", [Pattern("EDGE", np.uint64(0x00ff))])),
        iwmap_feature_offset=np.array([0, 2, 3], dtype=np.uint32),
        w_dense=np.array([1.0, 2.0, 3.0], dtype=np.float32),
        log_event=lambda rel, msg: None,
    )


class TestFactory(unittest.TestCase):
    """The wrk_save factory: the SAVE worker instance."""

    def test_returns_the_save_worker(self):
        w = wrk_save()
        self.assertIsInstance(w, Worker)
        self.assertEqual(w.name, "SAVE")


class TestSaveUp(unittest.TestCase):
    """The SAVE level on a mock ctx (the NO-DB idiom): the artifact lands, the echo is bounded."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE))
        self.events = []
        self.ctx = _mock_ctx(self._tmp.name)
        self.ctx.log_event = lambda rel, msg: self.events.append((rel, msg))

    def tearDown(self):
        self._tmp.cleanup()

    def test_up_writes_the_readable_artifact(self):
        _up(self.ctx)
        out = self.ctx.cfg.base_dir / self.ctx.cfg.output
        self.assertTrue(out.exists())
        mw = model_weights_read_file(out)
        self.assertEqual(mw.name, "test_model")
        self.assertEqual(mw.version, 2)

    def test_up_logs_the_bounded_detail(self):
        _up(self.ctx)
        msgs = [m for _, m in self.events]
        self.assertEqual(msgs[0], "Saving model weights to disk...")
        self.assertTrue(any("Model weights saved to" in m for m in msgs))
        self.assertTrue(any("checksum" in m for m in msgs))
        self.assertEqual(len(msgs), 3)


class TestSaveDown(unittest.TestCase):
    """The clearing no-op: it only logs."""

    def test_down_logs_only(self):
        events = []
        ctx = SimpleNamespace(log_event=lambda rel, msg: events.append(msg))
        _down(ctx)
        self.assertEqual(events, ["Clearing save attributes..."])


if __name__ == "__main__":
    unittest.main()
