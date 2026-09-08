#
# test_hlp_design_matrix.py
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
# How to run the hlp_design_matrix unit tests.
#
# Run from the workspace root (the directory containing .venv and src).
#
# -0- Activate the environment.
#
# $ source .venv/bin/activate
#
# -1- Run the tests.
#
# time python3 -m unittest reversi.test.test_hlp_design_matrix
#

import unittest
import tempfile

import numpy as np
import numpy.testing as nptest

from pathlib import Path
from types import SimpleNamespace

from pydantic import ValidationError

from reversi.tools import binio
from reversi.lm.hlp_design_matrix import (LMDesignMatrix,
                                     hlp_design_matrix_compute,
                                     hlp_design_matrix_store_to_file,
                                     hlp_design_matrix_load_from_file,
                                     hlp_design_matrix_is_cache_consistent)
from reversi.test.paths import CUSTOM_TMP_BASE


class TestRLMDesignMatrixCompute(unittest.TestCase):
    """Tests the mathematical logic of hlp_design_matrix_compute in isolation."""

    def setUp(self):
        # Create a dummy context to feed into hlp_design_matrix_compute
        self.ctx = SimpleNamespace(
            wmaps_obj_checksum="abc123"
        )

        # 1. Define a mock feature set with 2 features
        # Feature 0: 1 instance, 3 possible configurations (0, 1, 2)
        # Feature 1: 2 instances, 2 possible configurations (0, 1)
        self.ctx.feature_set = SimpleNamespace(
            features=[
                SimpleNamespace(name="F0", n_instances=1, n_configurations=3),
                SimpleNamespace(name="F1", n_instances=2, n_configurations=2)
            ]
        )

        # 2. Define the accumulated iwmap feature offsets [0, 3, 5]
        self.ctx.iwmap_feature_offset = np.array([0, 3, 5], dtype=np.uint32)

        # 3. Define the iwmap (length 5): F0 configs (0,1,2) -> w (1,0,0),
        #    F1 configs (0,1) -> w (2,3)
        self.ctx.iwmap = np.array([1, 0, 0, 2, 3], dtype=np.int64)

        # 4. Define a mock indexes matrix (Shape: N=4, I=3)
        self.ctx.hlp_indexes = SimpleNamespace(
            indexes=np.array([
                [0, 0, 0],  # F0=0, F1=0,0
                [0, 1, 1],  # F0=0, F1=1,1
                [2, 0, 1],  # F0=2, F1=0,1
                [1, 1, 0],  # F0=1, F1=1,0
            ], dtype=np.uint32)
        )

    def test_compute(self):
        """Test the Design Matrix computation: X[i,j] = iwmap[pindexes + col_offsets]."""
        dm = hlp_design_matrix_compute(self.ctx)

        # The wmaps checksum is carried over for the cache consistency check
        self.assertEqual(dm.wmaps_obj_checksum, "abc123")

        # Check X (4, 3) uint32:
        # col_offsets = [0, 3, 3] (repeat the feature start offsets per instance)
        # row 0: pindexes [0,0,0] + [0,3,3] = [0,3,3] -> iwmap -> (1, 2, 2)
        # row 1: pindexes [0,1,1] + [0,3,3] = [0,4,4] -> iwmap -> (1, 3, 3)
        # row 2: pindexes [2,0,1] + [0,3,3] = [2,3,4] -> iwmap -> (0, 2, 3)
        # row 3: pindexes [1,1,0] + [0,3,3] = [1,4,3] -> iwmap -> (0, 3, 2)
        self.assertEqual(dm.X.shape, (4, 3))
        self.assertEqual(dm.X.dtype, np.uint32)
        nptest.assert_array_equal(dm.X, np.array([
            [1, 2, 2],
            [1, 3, 3],
            [0, 2, 3],
            [0, 3, 2]
        ], dtype=np.uint32))

    def test_compute_rejects_invalid_pindex(self):
        """A pindex pointing at an iwmap slot without a weight (-1) raises."""
        # Feature 0 config 2 maps to no weight (the -1 sentinel)
        self.ctx.iwmap = np.array([1, 0, -1, 2, 3], dtype=np.int64)
        with self.assertRaises(ValueError) as context:
            hlp_design_matrix_compute(self.ctx)
        self.assertIn("pindexes is referring an invalid value", str(context.exception))


class TestRLMDesignMatrixCacheConsistency(unittest.TestCase):
    """Tests the cache validation logic."""

    def setUp(self):
        self.ctx = SimpleNamespace(
            wmaps_obj_checksum="abc123"
        )

        self.dm_valid = LMDesignMatrix(
            wmaps_obj_checksum="abc123",
            X=np.array([[0, 1], [2, 3]], dtype=np.uint32)
        )

        self.dm_wrong_checksum = LMDesignMatrix(
            wmaps_obj_checksum="wrong",
            X=np.array([[0, 1], [2, 3]], dtype=np.uint32)
        )

    def test_consistent_cache(self):
        self.assertTrue(hlp_design_matrix_is_cache_consistent(self.ctx, self.dm_valid))

    def test_inconsistent_checksum(self):
        self.assertFalse(hlp_design_matrix_is_cache_consistent(self.ctx, self.dm_wrong_checksum))


class TestRLMDesignMatrixIO(unittest.TestCase):
    """Tests the binary serialization and deserialization."""

    @classmethod
    def setUpClass(cls):
        CUSTOM_TMP_BASE.mkdir(parents=True, exist_ok=True)

    def setUp(self):
        # TemporaryDirectory created FIRST so a mid-setup failure
        # still leaves a cleanable temp dir.
        self._tmp = tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE))
        self.tmp_dir = Path(self._tmp.name)
        self.filepath = self.tmp_dir / "design_matrix_test.dat"

        # Create a fully populated Design Matrix object to serialize
        self.dm_original = LMDesignMatrix(
            wmaps_obj_checksum="io_test_hash",
            X=np.array([[1, 2, 2], [1, 3, 3]], dtype=np.uint32)
        )

    def tearDown(self):
        if getattr(self, '_tmp', None) is not None:
            self._tmp.cleanup()

    def test_store_and_load_cycle(self):
        """Test that storing and loading returns an identical object."""
        # Write to disk
        hlp_design_matrix_store_to_file(self.dm_original, self.filepath)
        self.assertTrue(self.filepath.exists())

        # Read from disk
        dm_loaded = hlp_design_matrix_load_from_file(self.filepath, checksum=False)

        # Validate scalar attributes
        self.assertEqual(dm_loaded.wmaps_obj_checksum, "io_test_hash")

        # Validate the numpy array (the dtype contract must survive the round-trip)
        self.assertEqual(dm_loaded.X.dtype, np.uint32)
        nptest.assert_array_equal(dm_loaded.X, self.dm_original.X)

    def test_compute_sha3_256_hash_golden(self):
        """The duck-typed hash is stable for the known object (golden content)."""
        self.assertEqual(
            self.dm_original.compute_sha3_256_hash(),
            "da86a916e03c76befa6f5df70e6221b0f9a355173e356ea63fef89ea9719757b")

    def test_load_with_valid_sidecar(self):
        """The checksum=True path accepts a matching sidecar (the D-072 machine)."""
        hlp_design_matrix_store_to_file(self.dm_original, self.filepath)
        binio.write_sha3_256_sidecar(self.filepath)
        dm_loaded = hlp_design_matrix_load_from_file(self.filepath, checksum=True)
        self.assertEqual(dm_loaded.wmaps_obj_checksum, "io_test_hash")

    def test_load_with_mismatched_sidecar(self):
        """A corrupted .dat against its sidecar raises the precise RuntimeError."""
        hlp_design_matrix_store_to_file(self.dm_original, self.filepath)
        binio.write_sha3_256_sidecar(self.filepath)
        with open(self.filepath, "r+b") as f:
            f.seek(-1, 2)
            original = f.read(1)
            f.seek(-1, 2)
            f.write(bytes([original[0] ^ 0xFF]))
        with self.assertRaises(RuntimeError) as context:
            hlp_design_matrix_load_from_file(self.filepath, checksum=True)
        self.assertIn("checksum file signature doesn't match", str(context.exception))

    def test_load_rejects_wrong_description(self):
        """A file whose header description is not the Design Matrix one is rejected."""
        with binio.BinaryWriter(str(self.filepath), checksum=False) as w:
            w.write_header("A description that is not the Design Matrix one", 1)
        with self.assertRaises(RuntimeError) as context:
            hlp_design_matrix_load_from_file(self.filepath, checksum=False)
        self.assertIn("not a proper", str(context.exception))

    def test_load_rejects_version_mismatch(self):
        """A file whose header version is not 1 is rejected."""
        with binio.BinaryWriter(str(self.filepath), checksum=False) as w:
            w.write_header("LMDesignMatrix binary data file", 2)
        with self.assertRaises(RuntimeError) as context:
            hlp_design_matrix_load_from_file(self.filepath, checksum=False)
        self.assertIn("version mismatch", str(context.exception))


class TestRLMDesignMatrixInit(unittest.TestCase):
    """Tests the __init__ validation of LMDesignMatrix."""

    def _make_valid(self, **overrides):
        kwargs = dict(
            wmaps_obj_checksum="abc123",
            X=np.array([[0, 0, 1], [0, 1, 2]], dtype=np.uint32),
        )
        kwargs.update(overrides)
        return LMDesignMatrix(**kwargs)

    def test_init_accepts_valid_arrays(self):
        self._make_valid()

    def test_init_fails_with_invalid_X_type(self):
        with self.assertRaises(ValidationError):
            self._make_valid(X="not_an_array")


if __name__ == '__main__':
    unittest.main()
