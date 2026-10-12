#
# test_hlp_indexes.py
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
# How to run the hlp_indexes unit tests.
#
# Run from the workspace root (the directory containing .venv and src).
#
# -0- Activate the environment.
#
# $ source .venv/bin/activate
#
# -1- Run the tests.
#
# time python3 -m unittest test.reversi.lm.test_hlp_indexes
#

"""Unit tests for the reversi.lm.hlp_indexes module."""

import unittest
from unittest.mock import patch, call, MagicMock
from pathlib import Path

from pydantic import ValidationError

from reversi.lm import hlp_indexes

import numpy as np
from reversi.index import Index

# A dummy 2D array of uint32 to be used across tests
DUMMY_INDEXES = np.zeros((2, 2), dtype=Index)


class TestLMIndexes(unittest.TestCase):
    """Tests for the LMIndexes class."""

    def test_init_success(self):
        """Test successful initialization with valid parameters."""
        hash_val = "abc123"

        obj = hlp_indexes.LMIndexes(
            rds_checksum=hash_val,
            feature_set_hash=hash_val,
            indexes=DUMMY_INDEXES
        )

        self.assertEqual(obj.feature_set_hash, hash_val)
        self.assertEqual(obj.rds_checksum, hash_val)
        self.assertIsInstance(obj.indexes, np.ndarray)
        self.assertEqual(obj.indexes.dtype, Index)
        self.assertIs(obj.indexes, DUMMY_INDEXES)

    def test_init_fails_with_invalid_hash_type(self):
        """Test that Pydantic validation fails if feature_set_hash is not a string."""
        indexes = DUMMY_INDEXES

        with self.assertRaises(ValidationError):
            hlp_indexes.LMIndexes(
                rds_checksum='abc',
                feature_set_hash=12345,
                indexes=indexes
            )

    def test_init_fails_with_invalid_indexes_type(self):
        """Test that Pydantic validation fails if indexes is not an IndexArray."""
        with self.assertRaises(ValidationError):
            hlp_indexes.LMIndexes(
                rds_checksum="valid_hash",
                feature_set_hash="valid_hash",
                indexes=[[1, 2], [3, 4]]
            )


    def test_repr_one_line_summary(self):
        """The one-line repr: the two hashes + the indexes shape."""
        obj = hlp_indexes.LMIndexes("abc", "def", DUMMY_INDEXES)
        self.assertEqual(
            repr(obj),
            "LMIndexes(rds_checksum='abc', feature_set_hash='def', indexes=(2, 2))")


class TestHlpIndexesStoreToFile(unittest.TestCase):
    """Tests for the hlp_indexes_store_to_file function."""

    @patch('reversi.lm.hlp_indexes.binio')
    def test_store_to_file_success(self, mock_binio):
        """Test that data is written to the binary file in the correct order and format."""
        mock_writer = MagicMock()
        mock_binio.BinaryWriter.return_value.__enter__.return_value = mock_writer

        hash_val_a = "hash_xyz"
        hash_val_b = "hash_abc"
        indexes = DUMMY_INDEXES
        rlm_idx = hlp_indexes.LMIndexes(hash_val_a, hash_val_b, indexes)
        filename = "test_output.bin"

        hlp_indexes.hlp_indexes_store_to_file(rlm_idx, filename)

        # 1. Verify the writer was instantiated correctly (the compressed default is passed through)
        mock_binio.BinaryWriter.assert_called_once_with(Path(filename), compressed=True)

        # 2. Define the exact expected sequence of calls
        expected_desc = "LMIndexes binary data file"
        expected_version = 1

        expected_calls = [
            call.write_header(expected_desc, expected_version),
            call.write_string(hash_val_a),
            call.write_string(hash_val_b),
            call.write_array(indexes)
        ]

        # 3. Assert the writer received these calls in this exact order
        mock_writer.assert_has_calls(expected_calls, any_order=False)

        self.assertEqual(mock_writer.method_calls, expected_calls)

    @patch('reversi.lm.hlp_indexes.binio')
    def test_store_to_file_accepts_path_object(self, mock_binio):
        """Test that the function handles pathlib.Path objects correctly."""
        mock_writer = MagicMock()
        mock_binio.BinaryWriter.return_value.__enter__.return_value = mock_writer

        indexes = DUMMY_INDEXES
        rlm_idx = hlp_indexes.LMIndexes("h", "h", indexes)
        filename_path = Path("dir/test_output.bin")

        hlp_indexes.hlp_indexes_store_to_file(rlm_idx, filename_path)

        mock_binio.BinaryWriter.assert_called_once_with(filename_path, compressed=True)


class TestHlpIndexesLoadFromFile(unittest.TestCase):
    """Tests for the hlp_indexes_load_from_file function."""

    @patch('reversi.lm.hlp_indexes.binio')
    def test_load_from_file_success_with_checksum(self, mock_binio):
        """Test successful loading when checksum verification is enabled (default)."""
        mock_binio.verify_sha3_256_sidecar.return_value = True

        mock_reader = MagicMock()
        mock_reader.read_header.return_value = ("LMIndexes binary data file", 1)
        mock_reader.read_string.return_value = "stored_hash"
        mock_reader.read_array.return_value = DUMMY_INDEXES

        mock_binio.BinaryReader.return_value.__enter__.return_value = mock_reader

        result = hlp_indexes.hlp_indexes_load_from_file("test.bin", checksum=True)

        mock_binio.verify_sha3_256_sidecar.assert_called_once_with("test.bin")
        # The reader is opened with the compressed default
        mock_binio.BinaryReader.assert_called_once_with("test.bin", compressed=True)

        self.assertIsInstance(result, hlp_indexes.LMIndexes)
        self.assertEqual(result.feature_set_hash, "stored_hash")
        self.assertIsInstance(result.indexes, np.ndarray)
        self.assertEqual(result.indexes.dtype, Index)
        self.assertIs(result.indexes, DUMMY_INDEXES)

    @patch('reversi.lm.hlp_indexes.binio')
    def test_load_from_file_success_without_checksum(self, mock_binio):
        """Test that checksum verification is skipped when checksum=False."""
        mock_reader = MagicMock()
        mock_reader.read_header.return_value = ("LMIndexes binary data file", 1)
        mock_reader.read_string.return_value = "stored_hash"
        mock_reader.read_array.return_value = DUMMY_INDEXES

        mock_binio.BinaryReader.return_value.__enter__.return_value = mock_reader

        hlp_indexes.hlp_indexes_load_from_file("test.bin", checksum=False)

        mock_binio.verify_sha3_256_sidecar.assert_not_called()

    @patch('reversi.lm.hlp_indexes.binio')
    def test_load_from_file_checksum_mismatch(self, mock_binio):
        """Test that RuntimeError is raised if the sidecar checksum fails."""
        mock_binio.verify_sha3_256_sidecar.return_value = False

        with self.assertRaises(RuntimeError) as context:
            hlp_indexes.hlp_indexes_load_from_file("test.bin", checksum=True)

        self.assertIn("checksum file signature doesn't match", str(context.exception))

    @patch('reversi.lm.hlp_indexes.binio')
    def test_load_from_file_invalid_description(self, mock_binio):
        """Test behavior when the file header description is incorrect."""
        mock_binio.verify_sha3_256_sidecar.return_value = True

        mock_reader = MagicMock()
        mock_reader.read_header.return_value = ("Wrong Description", 1)
        mock_binio.BinaryReader.return_value.__enter__.return_value = mock_reader

        with self.assertRaises(RuntimeError) as context:
            hlp_indexes.hlp_indexes_load_from_file("test.bin")

        self.assertIn("not a proper", str(context.exception))

    @patch('reversi.lm.hlp_indexes.binio')
    def test_load_from_file_invalid_version(self, mock_binio):
        """Test behavior when the file header version is incorrect."""
        mock_binio.verify_sha3_256_sidecar.return_value = True

        mock_reader = MagicMock()
        mock_reader.read_header.return_value = ("LMIndexes binary data file", 99)
        mock_binio.BinaryReader.return_value.__enter__.return_value = mock_reader

        with self.assertRaises(RuntimeError) as context:
            hlp_indexes.hlp_indexes_load_from_file("test.bin")

        self.assertIn("version is not consistent", str(context.exception))


class TestHlpIndexesCompute(unittest.TestCase):
    """Tests for the hlp_indexes_compute function."""

    def test_compute_success(self):
        """Test that indexes are computed correctly from the model."""
        # 2. The module is not mocked; only a fake "model" object is created
        mock_model = MagicMock()
        expected_hash = "model_hash_999"
        expected_indexes = DUMMY_INDEXES

        mock_model.rds_checksum = expected_hash
        mock_model.feature_set.hash = expected_hash
        mock_model.feature_set.compute_indexes.return_value = expected_indexes
        mock_model.positions = "dummy_positions"

        result = hlp_indexes.hlp_indexes_compute(mock_model)

        mock_model.feature_set.compute_indexes.assert_called_once_with("dummy_positions")

        self.assertIsInstance(result, hlp_indexes.LMIndexes)
        self.assertEqual(result.feature_set_hash, expected_hash)
        self.assertIs(result.indexes, expected_indexes)


class TestHlpIndexesIsCacheConsistent(unittest.TestCase):
    """Tests for the hlp_indexes_is_cache_consistent function."""

    def test_is_cache_consistent_returns_true(self):
        """Test that the function returns True when hashes match."""
        mock_model = MagicMock()
        mock_model.rds_checksum = "identical_hash"
        mock_model.feature_set.hash = "identical_hash"

        rlm_idx = hlp_indexes.LMIndexes(
            rds_checksum="identical_hash",
            feature_set_hash="identical_hash",
            indexes=DUMMY_INDEXES
        )

        result = hlp_indexes.hlp_indexes_is_cache_consistent(mock_model, rlm_idx)
        self.assertTrue(result)

    def test_is_cache_consistent_returns_false(self):
        """Test that the function returns False when hashes differ."""
        mock_model = MagicMock()
        mock_model.rds_checksum = "identical_hash"
        mock_model.feature_set.hash = "live_hash"

        rlm_idx = hlp_indexes.LMIndexes(
            rds_checksum="identical_hash",
            feature_set_hash="outdated_cached_hash",
            indexes=DUMMY_INDEXES
        )

        result = hlp_indexes.hlp_indexes_is_cache_consistent(mock_model, rlm_idx)
        self.assertFalse(result)

    def test_is_cache_consistent_returns_false_rds_differs(self):
        """Test that the function returns False when only the rds_checksum differs."""
        mock_model = MagicMock()
        mock_model.rds_checksum = "live_hash"
        mock_model.feature_set.hash = "identical_hash"

        rlm_idx = hlp_indexes.LMIndexes(
            rds_checksum="outdated_cached_hash",
            feature_set_hash="identical_hash",
            indexes=DUMMY_INDEXES
        )

        result = hlp_indexes.hlp_indexes_is_cache_consistent(mock_model, rlm_idx)
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
