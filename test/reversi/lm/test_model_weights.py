#
# test_model_weights.py
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

# How to run the model weights unit tests.
#
# Run from the workspace root (the directory containing .venv and src).
#
# -0- Activate the environment.
#
# $ source .venv/bin/activate
#
# -1- Run the tests.
#
# time PERF=0 python3 -m unittest test.reversi.lm.test_model_weights
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
from reversi.tools.binio import BinaryWriter
from reversi.lm.model_weights import (
    MODEL_WEIGHTS_FILE_HEADER_STR,
    model_weights_read_file,
    model_weights_write_file,
)
from test.reversi.paths import CUSTOM_TMP_BASE


def _mock_ctx():
    """The minimal mock ctx the writer reads (the NO-DB idiom: a tiny 2-feature set, 3 weights)."""
    dump = '{"name": "test_model", "empty_count": 20}'
    checksum = hashlib.sha3_256(dump.encode()).hexdigest()
    return SimpleNamespace(
        cfg=SimpleNamespace(
            name="test_model",
            empty_count=20,
            stat_model=SimpleNamespace(logit_clipping=6.0),
            model_dump_json=lambda indent=None: dump,
        ),
        config_checksum=checksum,
        training_pop_stats={'count': 100, 'mean': 0.5, 'std_dev': 0.1, 'variance': 0.01},
        opt_info={'reason': 'CONVERGED', 'iters': 10, 'f': 0.25, 'g_norm': 0.01},
        vld_metrics={'vld_samples': 50, 'vld_rmse_y': 1.5, 'vld_mae_y': 1.2, 'vld_loss': 0.3},
        feature_set=FeatureSet(
            "fs_test", Feature.new_intercept(),
            MobilitySet("mset", [Mobility("LMC", np.uint64(0xff), "mover")]),
            PatternSet("pset", [Pattern("EDGE", np.uint64(0x00ff))])),
        iwmap_feature_offset=np.array([0, 2, 3], dtype=np.uint32),
        w_dense=np.array([1.0, 2.0, 3.0], dtype=np.float32),
    )


def _write(path, compressed):
    model_weights_write_file(_mock_ctx(), path, compressed=compressed)


class TestRoundTrip(unittest.TestCase):
    """The v2 file: write then read, every section back (compressed and uncompressed)."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE))
        self.path = Path(self._tmp.name) / "model.bin"

    def tearDown(self):
        self._tmp.cleanup()

    def _assert_round_trip(self, compressed):
        _write(self.path, compressed)
        mw = model_weights_read_file(self.path, compressed=compressed)
        self.assertEqual(mw.version, 2)
        self.assertEqual(mw.name, "test_model")
        self.assertEqual(mw.ec, 20)
        self.assertAlmostEqual(mw.logit_clipping, 6.0)
        self.assertEqual(mw.training_pop_stats['count'], 100)
        self.assertAlmostEqual(mw.training_pop_stats['mean'], 0.5, places=6)
        self.assertEqual(mw.opt_info['reason'], 'CONVERGED')
        self.assertEqual(mw.opt_info['iters'], 10)
        self.assertAlmostEqual(mw.vld_metrics['vld_rmse_y'], 1.5, places=6)
        fs = mw.feature_set
        self.assertEqual(fs.name, "fs_test")
        self.assertIsNotNone(fs.intercept)
        self.assertEqual(fs.mset.mobilities[0].name, "LMC")
        self.assertEqual(fs.mset.mobilities[0].side, "mover")
        self.assertEqual(fs.pset.patterns[0].name, "EDGE")
        self.assertTrue(np.array_equal(mw.iwmap_feature_offset, np.array([0, 2, 3], dtype=np.uint32)))
        self.assertTrue(np.allclose(mw.w_dense, [1.0, 2.0, 3.0]))
        self.assertEqual(mw.config_dump, '{"name": "test_model", "empty_count": 20}')
        self.assertEqual(mw.config_checksum,
                         hashlib.sha3_256('{"name": "test_model", "empty_count": 20}'.encode()).hexdigest())

    def test_round_trip_compressed(self):
        self._assert_round_trip(True)

    def test_round_trip_uncompressed(self):
        self._assert_round_trip(False)


class TestReadRejections(unittest.TestCase):
    """The reader's three guards: the description, the version, the configuration checksum."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE))
        self.path = Path(self._tmp.name) / "model.bin"

    def tearDown(self):
        self._tmp.cleanup()

    def test_rejects_wrong_description(self):
        with BinaryWriter(self.path, compressed=False) as w:
            w.write_header("WRONG", version=2)
        with self.assertRaises(ValueError) as cm:
            model_weights_read_file(self.path, compressed=False)
        self.assertIn("File header mismatch", str(cm.exception))

    def test_rejects_bad_version(self):
        with BinaryWriter(self.path, compressed=False) as w:
            w.write_header(MODEL_WEIGHTS_FILE_HEADER_STR, version=3)
        with self.assertRaises(ValueError) as cm:
            model_weights_read_file(self.path, compressed=False)
        self.assertIn("version", str(cm.exception))

    def test_rejects_config_checksum_mismatch(self):
        ctx = _mock_ctx()
        ctx.config_checksum = "0" * 64  # the sentinel for a v1 file: never matches the v2 dump
        model_weights_write_file(ctx, self.path, compressed=False)
        with self.assertRaises(ValueError) as cm:
            model_weights_read_file(self.path, compressed=False)
        self.assertIn("checksum", str(cm.exception).lower())


if __name__ == "__main__":
    unittest.main()
