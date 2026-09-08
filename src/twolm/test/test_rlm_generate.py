#
# test_rlm_generate.py
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
# How to run the rlm_generate unit tests.
#
# Run from the workspace root (the directory containing .venv and src).
#
# -0- Activate the environment.
#
# $ source .venv/bin/activate
#
# -1- Run the tests.
#
# time python3 -m unittest twolm.test.test_rlm_generate
#

import unittest
import tempfile

import numpy as np
import numpy.testing as nptest

from pathlib import Path
from types import SimpleNamespace

from pydantic import ValidationError

from reversi.tools import binio
from twolm.state_machine import Relevance
from twolm.rlm_generate import (ReversiLogisticModelDenseWeights,
                                rlm_generate_store_to_file,
                                rlm_generate_load_from_file,
                                rlm_generate_is_cache_consistent,
                                compute_w_dense)
from twolm.test.paths import CUSTOM_TMP_BASE


class TestRLMGenerateCompute(unittest.TestCase):
    """Tests the dense weight generation logic."""

    def setUp(self):
        # Mock context with 3 features: Intercept, Pattern, Mobility
        self.ctx = SimpleNamespace()

        # Feature 0: Intercept (cat 0, 1 config)
        # Feature 1: Pattern (cat 2, 3 configs) -> ref mock (identity principal map)
        # Feature 2: Mobility (cat 1, 5 configs)
        self.ctx.feature_set = SimpleNamespace(
            hash="abc",
            features=[
                SimpleNamespace(name="INT", category=0, n_instances=1, n_configurations=1),
                SimpleNamespace(name="PAT", category=2, n_instances=1, n_configurations=3,
                                ref=SimpleNamespace(convert_to_principal_index=lambda x: x)), # Mock identity
                SimpleNamespace(name="MOB", category=1, n_instances=1, n_configurations=5)
            ]
        )

        # iwmap_feature_offset: [0, 1, 4, 9]
        self.ctx.iwmap_feature_offset = np.array([0, 1, 4, 9], dtype=np.uint32)

        # iwmap
        # INT (idx 0): [0]
        # PAT (idx 1,2,3): [-1, 1, 0]  (config 0 fallback->0, config 1->1, config 2 fallback->0)
        # MOB (idx 4,5,6,7,8): [-1, 2, -1, 3, -1] (config 1->2, config 3->3)
        self.ctx.iwmap = np.array(
            [0,  -1, 1, 0,  -1, 2, -1, 3, -1],
            dtype=np.int64
        )

        # w_ranges [fallback, w_min, w_max]
        # INT: [ -1, 0, 0 ]
        # PAT: [ 0, 0, 1 ]  (fallback is weight 0, w_min=0, w_max=1)
        # MOB: [ -1, 2, 3 ] (no fallback, w_min=2, w_max=3)
        self.ctx.feature_w_ranges = np.array([
            [-1, 0, 0],
            [ 0, 0, 1],
            [-1, 2, 3]
        ], dtype=np.int64)

        # wmap [fid, config_id, freq]
        # PAT config 1 has freq 10. PAT fallback (-1) has freq 3.
        # MOB config 1 has freq 5, config 3 has freq 5. No fallback.
        self.ctx.wmap = np.array([
            [1, -1, 3],
            [1, 1, 10],
            [2, 1, 5],
            [2, 3, 5]
        ], dtype=np.int64)

        # Compressed weights vector w
        # w[0] = 0.5 (Intercept, also Pattern fallback)
        # w[1] = -0.2 (Pattern config 1)
        # w[2] = 1.0 (Mobility config 1)
        # w[3] = 3.0 (Mobility config 3)
        self.ctx.w = np.array([0.5, -0.2, 1.0, 3.0], dtype=np.float32)
        self.ctx.w_checksum = "abc654"

        # Mock logger
        self.ctx.log_event = lambda rel, msg: None

    def test_compute_w_dense(self):
        dense_obj = compute_w_dense(self.ctx)
        w_dense = dense_obj.w_dense

        self.assertEqual(w_dense.dtype, np.float32)
        self.assertEqual(len(w_dense), 9) # 1 + 3 + 5

        # Intercept (index 0)
        nptest.assert_allclose(w_dense[0], 0.5)

        # Pattern (indices 1, 2, 3)
        # Config 0 is fallback -> weighted_mean = (-0.2 * 10) / 10 = -0.2
        # Config 1 is seen -> -0.2
        # Config 2 is fallback -> -0.2
        nptest.assert_allclose(w_dense[1:4], np.array([-0.2, -0.2, -0.2], dtype=np.float32))

        # Mobility (indices 4, 5, 6, 7, 8)
        # Config 0 (idx 4) unseen -> clamp to config 1 (1.0)
        # Config 1 (idx 5) seen -> 1.0
        # Config 2 (idx 6) unseen -> interpolate between 1.0 and 3.0 -> 2.0
        # Config 3 (idx 7) seen -> 3.0
        # Config 4 (idx 8) unseen -> clamp to config 3 (3.0)
        expected_mob = np.array([1.0, 1.0, 2.0, 3.0, 3.0], dtype=np.float32)
        nptest.assert_allclose(w_dense[4:9], expected_mob)

    def test_unknown_category_raises(self):
        # A feature category outside 0/1/2 is a hard error with a precise message.
        ctx = SimpleNamespace()
        ctx.feature_set = SimpleNamespace(
            hash="x",
            features=[SimpleNamespace(name="X", category=9, n_instances=1, n_configurations=1)]
        )
        ctx.iwmap_feature_offset = np.array([0, 1], dtype=np.uint32)
        ctx.iwmap = np.array([0], dtype=np.int64)
        ctx.feature_w_ranges = np.array([[-1, 0, 0]], dtype=np.int64)
        ctx.wmap = np.zeros((0, 3), dtype=np.int64)
        ctx.w = np.array([0.1], dtype=np.float32)
        ctx.w_checksum = "z"
        ctx.log_event = lambda rel, msg: None

        with self.assertRaises(RuntimeError) as context:
            compute_w_dense(ctx)
        self.assertEqual(str(context.exception), "The feature category is unknown: 9")

    def test_mobility_without_seen_configs_warns_and_zeroes(self):
        # A mobility feature with no seen configurations keeps the zero
        # weights and logs exactly one WARN event.
        events = []
        ctx = SimpleNamespace()
        ctx.feature_set = SimpleNamespace(
            hash="x",
            features=[SimpleNamespace(name="MOB", category=1, n_instances=1, n_configurations=4)]
        )
        ctx.iwmap_feature_offset = np.array([0, 4], dtype=np.uint32)
        ctx.iwmap = np.array([-1, -1, -1, -1], dtype=np.int64)
        ctx.feature_w_ranges = np.array([[-1, 0, 0]], dtype=np.int64)
        ctx.wmap = np.zeros((0, 3), dtype=np.int64)
        ctx.w = np.array([0.0], dtype=np.float32)
        ctx.w_checksum = "z"
        ctx.log_event = lambda rel, msg: events.append((rel, msg))

        w_dense = compute_w_dense(ctx).w_dense

        nptest.assert_array_equal(w_dense, np.zeros(4, dtype=np.float32))
        self.assertEqual(len(events), 1)
        self.assertIs(events[0][0], Relevance.WARN)
        self.assertIn("no seen configurations", events[0][1])


class TestRLMGenerateCacheConsistency(unittest.TestCase):
    """Tests the cache consistency logic (the w_checksum metadata compare)."""

    def setUp(self):
        self.ctx = SimpleNamespace(w_checksum="abc654")
        arr = np.array([0.5, -0.2], dtype=np.float32)
        self.dw_matching = ReversiLogisticModelDenseWeights("abc654", arr)
        self.dw_stale = ReversiLogisticModelDenseWeights("stale", arr)

    def test_consistent_checksum(self):
        self.assertTrue(rlm_generate_is_cache_consistent(self.ctx, self.dw_matching))

    def test_inconsistent_checksum(self):
        self.assertFalse(rlm_generate_is_cache_consistent(self.ctx, self.dw_stale))


class TestRLMGenerateIO(unittest.TestCase):
    """Tests the binary serialization and deserialization."""

    @classmethod
    def setUpClass(cls):
        CUSTOM_TMP_BASE.mkdir(parents=True, exist_ok=True)

    def setUp(self):
        # TemporaryDirectory created FIRST so a mid-setup failure
        # still leaves a cleanable temp dir.
        self._tmp = tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE))
        self.tmp_dir = Path(self._tmp.name)
        self.filepath = self.tmp_dir / "dense.dat"

        # A fully populated dense-weights object to serialize
        self.dw_original = ReversiLogisticModelDenseWeights(
            "io_test_checksum",
            np.array([0.5, -0.2, 1.0, 3.0], dtype=np.float32)
        )

    def tearDown(self):
        if getattr(self, '_tmp', None) is not None:
            self._tmp.cleanup()

    def test_store_and_load_cycle(self):
        """Test that storing and loading returns an identical object."""
        rlm_generate_store_to_file(self.dw_original, self.filepath)
        self.assertTrue(self.filepath.exists())

        dw_loaded = rlm_generate_load_from_file(self.filepath, checksum=False)

        self.assertEqual(dw_loaded.w_checksum, "io_test_checksum")
        self.assertEqual(dw_loaded.w_dense.dtype, np.float32)
        nptest.assert_array_equal(dw_loaded.w_dense, self.dw_original.w_dense)

    def test_compute_sha3_256_hash_golden(self):
        """The duck-typed hash is stable for the known object (golden content)."""
        self.assertEqual(
            self.dw_original.compute_sha3_256_hash(),
            "460c993da80d5ff6fd5581660d71be905c482eadc5520718b56051f6545cd07a")

    def test_load_with_valid_sidecar(self):
        """The checksum=True path accepts a matching sidecar (the D-072 machine)."""
        rlm_generate_store_to_file(self.dw_original, self.filepath)
        binio.write_sha3_256_sidecar(self.filepath)
        dw_loaded = rlm_generate_load_from_file(self.filepath, checksum=True)
        self.assertEqual(dw_loaded.w_checksum, "io_test_checksum")
        nptest.assert_array_equal(dw_loaded.w_dense, self.dw_original.w_dense)

    def test_load_with_mismatched_sidecar(self):
        """A corrupted .dat against its sidecar raises the precise RuntimeError."""
        rlm_generate_store_to_file(self.dw_original, self.filepath)
        binio.write_sha3_256_sidecar(self.filepath)
        size = self.filepath.stat().st_size
        with open(self.filepath, "r+b") as f:
            f.seek(size // 2)
            original = f.read(1)
            f.seek(size // 2)
            f.write(bytes([original[0] ^ 0xFF]))
        with self.assertRaises(RuntimeError) as context:
            rlm_generate_load_from_file(self.filepath, checksum=True)
        self.assertEqual(str(context.exception), "Checksum mismatch.")

    def test_load_rejects_wrong_description(self):
        """A file whose header description is not the dense-weights one is rejected."""
        with binio.BinaryWriter(str(self.filepath), checksum=False) as w:
            w.write_header("A description that is not the dense-weights one", 1)
        with self.assertRaises(RuntimeError) as context:
            rlm_generate_load_from_file(self.filepath, checksum=False)
        self.assertEqual(
            str(context.exception),
            "Wrong file format: A description that is not the dense-weights one")

    def test_load_rejects_version_mismatch(self):
        """A file whose header version is not 1 is rejected (the T1 gate)."""
        with binio.BinaryWriter(str(self.filepath), checksum=False) as w:
            w.write_header("RGLM Dense Weights binary data file", 2)
        with self.assertRaises(RuntimeError) as context:
            rlm_generate_load_from_file(self.filepath, checksum=False)
        self.assertEqual(
            str(context.exception),
            "File version mismatch: found 2, expected 1")


class TestRLMGenerateInit(unittest.TestCase):
    """Tests the __init__ validation of ReversiLogisticModelDenseWeights."""

    def test_init_accepts_valid_arrays(self):
        ReversiLogisticModelDenseWeights("abc", np.array([0.5], dtype=np.float32))

    def test_init_fails_with_list_w_dense(self):
        with self.assertRaises(ValidationError):
            ReversiLogisticModelDenseWeights("abc", [1.0, 2.0])

    def test_init_fails_with_non_str_w_checksum(self):
        with self.assertRaises(ValidationError):
            ReversiLogisticModelDenseWeights(123, np.zeros(2, dtype=np.float32))


if __name__ == '__main__':
    unittest.main()
