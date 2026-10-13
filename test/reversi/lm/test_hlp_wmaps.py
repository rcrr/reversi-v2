#
# test_hlp_wmaps.py
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
#
# How to run the hlp_wmaps unit tests.
#
# Run from the workspace root (the directory containing .venv and src).
#
# -0- Activate the environment.
#
# $ source .venv/bin/activate
#
# -1- Run the tests.
#
# time python3 -m unittest test.reversi.lm.test_hlp_wmaps
#

import unittest
import tempfile

import numpy as np
import numpy.testing as nptest

from pathlib import Path
from types import SimpleNamespace

from pydantic import ValidationError

from reversi.tools import binio
from reversi.lm.hlp_wmaps import (LMWMaps,
                                 hlp_wmaps_compute,
                                 hlp_wmaps_store_to_file,
                                 hlp_wmaps_load_from_file,
                                 hlp_wmaps_is_cache_consistent)
from test.reversi.paths import CUSTOM_TMP_BASE
from reversi.index import Index
from reversi.index import ExtendedIndex, Index


class TestHlpWmapsCompute(unittest.TestCase):
    """Tests the mathematical logic of hlp_wmaps_compute in isolation."""

    def setUp(self):
        # Create a dummy context to feed into hlp_wmaps_compute
        self.ctx = SimpleNamespace(
            hlp_indexes_checksum="abc123"
        )

        # 1. Define a mock feature set with 2 features Feature 0: 1 instance, 3 possible
        # configurations (0, 1, 2) Feature 1: 2 instances, 2 possible configurations (0, 1)
        self.ctx.feature_set = SimpleNamespace(
            hash="zyz789",
            features=[
                SimpleNamespace(name="F0", n_instances=1, n_configurations=3),
                SimpleNamespace(name="F1", n_instances=2, n_configurations=2)
            ]
        )

        # 2. Define a mock configuration with a cut-off of 2
        self.ctx.cfg = SimpleNamespace(
            stat_model=SimpleNamespace(frequency_cut_off=2)
        )

        # 3. Define a mock indexes matrix (Shape: N=4, I=3) F0 (col 0): 0 appears 2x, 1 appears 1x,
        # 2 appears 1x F1 (col 1,2): raveled 0 appears 4x, 1 appears 4x
        self.ctx.hlp_indexes = SimpleNamespace(
            indexes=np.array([
                [0, 0, 0],  # F0=0, F1=0,0
                [0, 0, 0],  # F0=0, F1=0,0
                [1, 1, 1],  # F0=1, F1=1,1
                [2, 1, 1],  # F0=2, F1=1,1
            ], dtype=Index)
        )

    def test_compute_with_fallback(self):
        """Test WMAPS computation with frequency cut-off active."""
        wmaps = hlp_wmaps_compute(self.ctx)

        # Check basic attributes
        self.assertEqual(wmaps.hlp_indexes_checksum, "abc123")
        self.assertEqual(wmaps.cut_off, 2)
        self.assertEqual(len(wmaps.w), 4)  # Expected weights: 1 fallback + 1 above for F0, 2 above for F1

        # Check iwmap_feature_offset (accumulated n_configurations: [0, 3, 5])
        nptest.assert_array_equal(wmaps.iwmap_feature_offset, np.array([0, 3, 5], dtype=Index))

        # Check feature_w_ranges [fallback, w_min, w_max] F0: fallback=0, w_min=0, w_max=1 F1:
        # fallback=-1, w_min=2, w_max=3
        nptest.assert_array_equal(wmaps.feature_w_ranges, np.array([
            [0, 0, 1],
            [-1, 2, 3]
        ], dtype=ExtendedIndex))

        # Check iwmap (length 5) F0 configs (0, 1, 2) -> 0 gets w=1, 1 gets w=0 (fallback), 2 gets
        # w=0 (fallback) F1 configs (0, 1)    -> 0 gets w=2, 1 gets w=3
        nptest.assert_array_equal(wmaps.iwmap, np.array([1, 0, 0, 2, 3], dtype=ExtendedIndex))

        # Check wmap [fid, config_id, freq] w=0 (F0 fallback): config_id=-1, freq=2 (from configs 1
        # and 2) w=1 (F0 config 0): config_id=0, freq=2 w=2 (F1 config 0): config_id=0, freq=4 w=3
        # (F1 config 1): config_id=1, freq=4
        nptest.assert_array_equal(wmaps.wmap, np.array([
            [0, -1, 2],
            [0,  0, 2],
            [1,  0, 4],
            [1,  1, 4]
        ], dtype=ExtendedIndex))

        # Check wmap_fallback [fid, config_id, freq] F0 config 1 (freq 1) and F0 config 2 (freq 1)
        nptest.assert_array_equal(wmaps.wmap_fallback, np.array([
            [0, 1, 1],
            [0, 2, 1]
        ], dtype=ExtendedIndex))

    def test_compute_nd_indexes_matches_1d(self):
        """
        N-D sanity: a (2, 2, I) pindexes matrix (an any-shape position batch) gives the same wmaps
        as its C-order (N, I) ravel — the feature columns are the last axis.
        """
        nd_ctx = SimpleNamespace(
            hlp_indexes_checksum="abc123",
            feature_set=self.ctx.feature_set,
            cfg=self.ctx.cfg,
            hlp_indexes=SimpleNamespace(
                indexes=self.ctx.hlp_indexes.indexes.reshape(2, 2, 3))
        )

        wmaps_nd = hlp_wmaps_compute(nd_ctx)
        wmaps_1d = hlp_wmaps_compute(self.ctx)

        self.assertEqual(len(wmaps_nd.w), len(wmaps_1d.w))
        nptest.assert_array_equal(wmaps_nd.iwmap, wmaps_1d.iwmap)
        nptest.assert_array_equal(wmaps_nd.wmap, wmaps_1d.wmap)
        nptest.assert_array_equal(wmaps_nd.wmap_fallback, wmaps_1d.wmap_fallback)
        nptest.assert_array_equal(wmaps_nd.feature_w_ranges, wmaps_1d.feature_w_ranges)
        nptest.assert_array_equal(wmaps_nd.iwmap_feature_offset, wmaps_1d.iwmap_feature_offset)

    def test_compute_without_fallback(self):
        """Test WMAPS computation when cut-off is 0 (no fallbacks)."""
        # Modify cut-off to 0
        self.ctx.cfg.stat_model.frequency_cut_off = 0

        wmaps = hlp_wmaps_compute(self.ctx)

        # With no fallback, every unique config gets its own weight F0 has 3 configs (w=0, 1, 2), F1
        # has 2 configs (w=3, 4)
        self.assertEqual(len(wmaps.w), 5)

        # wmap_fallback should be empty but maintain shape (0, 3)
        self.assertEqual(wmaps.wmap_fallback.shape, (0, 3))

        # F0 should have fallback -1
        self.assertEqual(wmaps.feature_w_ranges[0, 0], -1)


class TestHlpWmapsCacheConsistency(unittest.TestCase):
    """Tests the cache validation logic."""

    def setUp(self):
        self.ctx = SimpleNamespace(
            hlp_indexes_checksum="abc123"
        )
        self.ctx.feature_set = SimpleNamespace(hash="zyz789")
        self.ctx.cfg = SimpleNamespace(stat_model=SimpleNamespace(frequency_cut_off=5))

        # Use empty arrays instead of None to satisfy Pydantic validation
        empty_arr = np.array([])

        self.wmaps_valid = LMWMaps(
            hlp_indexes_checksum="abc123", cut_off=5,
            feature_w_ranges=empty_arr, iwmap_feature_offset=empty_arr, iwmap=empty_arr,
            wmap=empty_arr, wmap_fallback=empty_arr, w=np.zeros(1)
        )

        self.wmaps_wrong_hash = LMWMaps(
            hlp_indexes_checksum="wrong", cut_off=5,
            feature_w_ranges=empty_arr, iwmap_feature_offset=empty_arr, iwmap=empty_arr,
            wmap=empty_arr, wmap_fallback=empty_arr, w=np.zeros(1)
        )

        self.wmaps_wrong_cutoff = LMWMaps(
            hlp_indexes_checksum="abc123", cut_off=99,
            feature_w_ranges=empty_arr, iwmap_feature_offset=empty_arr, iwmap=empty_arr,
            wmap=empty_arr, wmap_fallback=empty_arr, w=np.zeros(1)
        )

    def test_consistent_cache(self):
        self.assertTrue(hlp_wmaps_is_cache_consistent(self.ctx, self.wmaps_valid))

    def test_inconsistent_hash(self):
        self.assertFalse(hlp_wmaps_is_cache_consistent(self.ctx, self.wmaps_wrong_hash))

    def test_inconsistent_cutoff(self):
        self.assertFalse(hlp_wmaps_is_cache_consistent(self.ctx, self.wmaps_wrong_cutoff))


class TestHlpWmapsIO(unittest.TestCase):
    """Tests the binary serialization and deserialization."""

    @classmethod
    def setUpClass(cls):
        CUSTOM_TMP_BASE.mkdir(parents=True, exist_ok=True)

    def setUp(self):
        # TemporaryDirectory created FIRST so a mid-setup failure still leaves a cleanable temp dir.
        self._tmp = tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE))
        self.tmp_dir = Path(self._tmp.name)
        self.filepath = self.tmp_dir / "wmaps_test.dat"

        # Create a fully populated WMaps object to serialize
        self.wmaps_original = LMWMaps(
            hlp_indexes_checksum="io_test_hash",
            cut_off=42,
            feature_w_ranges=np.array([[0, 1, 2]], dtype=ExtendedIndex),
            iwmap_feature_offset=np.array([0, 3], dtype=Index),
            iwmap=np.array([1, 0, 2], dtype=ExtendedIndex),
            wmap=np.array([[0, 0, 10], [0, 1, 20]], dtype=ExtendedIndex),
            wmap_fallback=np.array([[0, 2, 5]], dtype=ExtendedIndex),
            w=np.array([0.1, 0.2, 0.3], dtype=np.float32)
        )

    def tearDown(self):
        if getattr(self, '_tmp', None) is not None:
            self._tmp.cleanup()

    def test_store_and_load_cycle(self):
        """Test that storing and loading returns an identical object."""
        # Write to disk
        hlp_wmaps_store_to_file(self.wmaps_original, self.filepath)
        self.assertTrue(self.filepath.exists())

        # Read from disk
        wmaps_loaded = hlp_wmaps_load_from_file(self.filepath, checksum=False)

        # Validate scalar attributes
        self.assertEqual(wmaps_loaded.hlp_indexes_checksum, "io_test_hash")
        self.assertEqual(wmaps_loaded.cut_off, 42)

        # Validate numpy arrays
        nptest.assert_array_equal(wmaps_loaded.feature_w_ranges, self.wmaps_original.feature_w_ranges)
        nptest.assert_array_equal(wmaps_loaded.iwmap_feature_offset, self.wmaps_original.iwmap_feature_offset)
        nptest.assert_array_equal(wmaps_loaded.iwmap, self.wmaps_original.iwmap)
        nptest.assert_array_equal(wmaps_loaded.wmap, self.wmaps_original.wmap)
        nptest.assert_array_equal(wmaps_loaded.wmap_fallback, self.wmaps_original.wmap_fallback)
        nptest.assert_array_equal(wmaps_loaded.w, self.wmaps_original.w)
        nptest.assert_array_almost_equal(wmaps_loaded.w, self.wmaps_original.w)

    def test_compute_sha3_256_hash_golden(self):
        """The duck-typed hash is stable for the known object (golden content)."""
        self.assertEqual(
            self.wmaps_original.compute_sha3_256_hash(),
            "12c3344ec23c798d7b35eb6eae01034b29ee5c539bfb2018ca2eabc73c861dfa")

    def test_load_with_valid_sidecar(self):
        """The checksum=True path accepts a matching sidecar (the binio sidecar format)."""
        hlp_wmaps_store_to_file(self.wmaps_original, self.filepath)
        binio.write_sha3_256_sidecar(self.filepath)
        wmaps_loaded = hlp_wmaps_load_from_file(self.filepath, checksum=True)
        self.assertEqual(wmaps_loaded.hlp_indexes_checksum, "io_test_hash")
        self.assertEqual(wmaps_loaded.cut_off, 42)

    def test_load_with_mismatched_sidecar(self):
        """A corrupted .dat against its sidecar raises the precise RuntimeError."""
        hlp_wmaps_store_to_file(self.wmaps_original, self.filepath)
        binio.write_sha3_256_sidecar(self.filepath)
        with open(self.filepath, "r+b") as f:
            f.seek(100)
            original = f.read(1)
            f.seek(100)
            f.write(bytes([original[0] ^ 0xFF]))
        with self.assertRaises(RuntimeError) as context:
            hlp_wmaps_load_from_file(self.filepath, checksum=True)
        self.assertIn("checksum file signature doesn't match", str(context.exception))

    def test_load_rejects_wrong_description(self):
        """A file whose header description is not the WMaps one is rejected."""
        with binio.BinaryWriter(str(self.filepath), checksum=False,
                                compressed=True) as w:
            w.write_header("A description that is not the WMaps one", 1)
        with self.assertRaises(RuntimeError) as context:
            hlp_wmaps_load_from_file(self.filepath, checksum=False)
        self.assertIn("not a proper", str(context.exception))

    def test_load_rejects_version_mismatch(self):
        """A file whose header version is not 1 is rejected."""
        with binio.BinaryWriter(str(self.filepath), checksum=False,
                                compressed=True) as w:
            w.write_header("LMWMaps binary data file", 2)
        with self.assertRaises(RuntimeError) as context:
            hlp_wmaps_load_from_file(self.filepath, checksum=False)
        self.assertIn("version mismatch", str(context.exception))

    def test_store_compressed_by_default(self):
        """Store writes an LZ4 frame by default and load (the compressed default) round-trips it."""
        hlp_wmaps_store_to_file(self.wmaps_original, self.filepath)
        with open(self.filepath, "rb") as f:
            self.assertEqual(f.read(4), b"\x04\x22\x4d\x18")  # LZ4 frame magic
        wmaps_loaded = hlp_wmaps_load_from_file(self.filepath, checksum=False)
        self.assertEqual(wmaps_loaded.hlp_indexes_checksum, "io_test_hash")
        self.assertEqual(wmaps_loaded.cut_off, 42)

    def test_load_defaults_reject_uncompressed_file(self):
        """
        The compressed default fails loud on a legacy uncompressed file (cache invalidation, not a
        silent misread).
        """
        with binio.BinaryWriter(str(self.filepath), checksum=False,
                                compressed=False) as w:
            w.write_header("LMWMaps binary data file", 1)
        with self.assertRaises(binio.BinaryFormatError):
            hlp_wmaps_load_from_file(self.filepath, checksum=False)


class TestHlpWmapsInit(unittest.TestCase):
    """Tests the __init__ validation of LMWMaps."""

    def _make_valid(self, **overrides):
        kwargs = dict(
            hlp_indexes_checksum="abc123",
            cut_off=5,
            feature_w_ranges=np.array([[0, 0, 1]], dtype=ExtendedIndex),
            iwmap_feature_offset=np.array([0, 2], dtype=Index),
            iwmap=np.array([0, 1], dtype=ExtendedIndex),
            wmap=np.array([[0, 0, 3]], dtype=ExtendedIndex),
            wmap_fallback=np.array([]),
            w=np.zeros(2, dtype=np.float32),
        )
        kwargs.update(overrides)
        return LMWMaps(**kwargs)

    def test_init_accepts_valid_arrays(self):
        self._make_valid()

    def test_init_fails_with_invalid_cut_off_type(self):
        with self.assertRaises(ValidationError):
            self._make_valid(cut_off="not_an_int")


if __name__ == '__main__':
    unittest.main()
