#
# test_cache_manager.py
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
# How to use the unit tests cache_manager module.
#
# Run from the workspace root (the directory containing .venv and src).
#
# -0- Activate the environment.
#
# $ source .venv/bin/activate
#
# -1- Run the tests.
#
# time python3 -m unittest test.reversi.tools.test_cache_manager
#

"""
Unit tests for the reversi.tools.cache_manager module.

This suite verifies the 4-step validation pipeline, ensuring that caching, checksum validation,
fallback computation logic, and the cache_hit flag behave predictably under various scenarios.
"""

import unittest
import tempfile

from pathlib import Path
from unittest.mock import MagicMock

from reversi.tools.binio import compute_sha3_256, write_sha3_256_sidecar
from reversi.tools.cache_manager import (
    cache_manager_load_or_compute,
    _verify_checksum,
    _delete_cache_files,
    SHA3_256_CHECKSUM_SUFFIX,
)
from reversi.tools.state_machine import Relevance
from test.reversi.paths import CUSTOM_TMP_BASE


#: A constant dummy payload to simulate computed/cached data
DUMMY_DATA = {"result": "success", "value": 42}


class DataWithChecksum:
    """Data object WITH the duck-typed compute_sha3_256_hash method."""

    def __init__(self, payload, digest):
        self.payload = payload
        self.digest = digest

    def compute_sha3_256_hash(self):
        return self.digest


class DataWithBrokenChecksum(DataWithChecksum):
    """Data object whose compute_sha3_256_hash raises."""

    def compute_sha3_256_hash(self):
        raise RuntimeError("hash boom")


def checksum_path_for(data_path: Path) -> Path:
    """The module's sidecar path for a data file."""
    return data_path.with_suffix(data_path.suffix + SHA3_256_CHECKSUM_SUFFIX)


class BaseCacheTestCase(unittest.TestCase):
    """Base test case to handle custom temporary directory setup and teardown."""

    @classmethod
    def setUpClass(cls):
        """Ensure the custom temporary base directory exists."""
        CUSTOM_TMP_BASE.mkdir(parents=True, exist_ok=True)

    def setUp(self):
        """Create a temporary directory inside <workspace-root>/build/tmp/."""
        self.temp_dir = tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE))

    def tearDown(self):
        """Clean up the temporary directory."""
        self.temp_dir.cleanup()


class TestChecksumHelpers(BaseCacheTestCase):
    """Tests for the low-level checksum utility functions."""

    def setUp(self):
        super().setUp()
        self.temp_path = Path(self.temp_dir.name) / "test_data.dat"
        self.temp_path.write_text("Hello, Cache World!")

    def test_binio_sidecar_verifies(self):
        """
        A sidecar written by binio's own API verifies through the _verify_checksum wrapper — both
        modules share one sidecar format and one verifier.
        """
        write_sha3_256_sidecar(self.temp_path)
        self.assertTrue(_verify_checksum(self.temp_path))

    def test_legacy_bare_hex_sidecar_still_verifies(self):
        """
        A legacy bare-hexdigest sidecar (the old format: no filename, no newline) still verifies,
        because binio's parser takes the first whitespace-separated token — no cache invalidation
        for existing on-disk caches.
        """
        checksum_path_for(self.temp_path).write_text(
            compute_sha3_256(self.temp_path)
        )
        self.assertTrue(_verify_checksum(self.temp_path))

    def test_verify_checksum_fails_if_sidecar_missing(self):
        """Verify that verification returns False if the .SHA3-256 file does not exist."""
        self.assertFalse(_verify_checksum(self.temp_path))

    def test_verify_checksum_fails_if_sidecar_mismatched(self):
        """
        Verify that a well-formed sidecar holding the WRONG digest fails the verification step
        (binio compares it against the recomputed hash).
        """
        checksum_path_for(self.temp_path).write_text("0" * 64)
        self.assertFalse(_verify_checksum(self.temp_path))

    def test_verify_checksum_fails_if_sidecar_malformed(self):
        """
        Verify that a malformed sidecar (binio's BinaryFormatError) or an undecodable one
        (UnicodeDecodeError) maps to False via the wrapper, never to a raised exception.
        """
        checksum_path = checksum_path_for(self.temp_path)
        checksum_path.write_text("not a hex digest at all")
        self.assertFalse(_verify_checksum(self.temp_path))
        checksum_path.write_bytes(b"\xff\xfe\x00garbage")
        self.assertFalse(_verify_checksum(self.temp_path))

    def test_delete_cache_files_removes_both(self):
        """Verify that _delete_cache_files removes both data and checksum files."""
        write_sha3_256_sidecar(self.temp_path)

        self.assertTrue(self.temp_path.exists())
        self.assertTrue(self.temp_path.with_suffix(
            self.temp_path.suffix + SHA3_256_CHECKSUM_SUFFIX
        ).exists())

        _delete_cache_files(self.temp_path)

        self.assertFalse(self.temp_path.exists())
        self.assertFalse(self.temp_path.with_suffix(
            self.temp_path.suffix + SHA3_256_CHECKSUM_SUFFIX
        ).exists())

    def test_delete_cache_files_does_not_raise_if_missing(self):
        """Verify that deletion is idempotent and does not raise FileNotFoundError."""
        _delete_cache_files(self.temp_path)
        _delete_cache_files(self.temp_path)

    def test_sidecar_content_is_binio_format(self):
        """
        The sidecar holds binio's sha3_256sum-style line
        "<hexdigest>  <basename>\n" — cache_manager no longer keeps
        its own bare-hexdigest format (see the module doc).
        """
        write_sha3_256_sidecar(self.temp_path)
        digest = compute_sha3_256(self.temp_path)
        content = checksum_path_for(self.temp_path).read_text()
        self.assertEqual(content, f"{digest}  {self.temp_path.name}\n")


class TestCacheManagerPipeline(BaseCacheTestCase):
    """
    Tests for the main cache_manager_load_or_compute orchestration function. Verifies both the
    returned data and the cache_hit boolean flag.
    """

    def setUp(self):
        super().setUp()
        self.cache_path = Path(self.temp_dir.name) / "cache.dat"

        self.mock_compute = MagicMock(return_value=DUMMY_DATA)
        self.mock_store = MagicMock(side_effect=self._fake_store)
        self.mock_load = MagicMock(return_value=DUMMY_DATA)
        self.mock_validate = MagicMock(return_value=True)
        self.mock_logger = MagicMock()

    @staticmethod
    def _fake_store(data: object, path: Path) -> None:
        """Simulates a real store function by physically writing data to disk."""
        path.write_text(str(data))

    def test_step0_not_allowed_forces_computation(self):
        """Step 0: If caching is not allowed, it must compute, store, and return cache_hit=False."""
        self.cache_path.write_text("old data")

        cache_hit, result, checksum = cache_manager_load_or_compute(
            cache_path=self.cache_path,
            is_allowed=False,
            load_fn=self.mock_load,
            store_fn=self.mock_store,
            validate_fn=self.mock_validate,
            compute_fn=self.mock_compute,
            logger_fn=self.mock_logger
        )

        self.assertFalse(cache_hit, "cache_hit must be False when cache is not allowed.")
        self.assertEqual(result, DUMMY_DATA)
        self.assertIsNone(checksum, "plain dict data has no compute_sha3_256_hash method.")
        self.mock_compute.assert_called_once()
        self.mock_store.assert_called_once_with(DUMMY_DATA, self.cache_path)
        self.mock_load.assert_not_called()

        self.mock_logger.assert_any_call(
            Relevance.INFO, "Cache not allowed by configuration. Forcing computation."
        )

        # Even when caching is not allowed the result is transcribed to the cache file — warm the cache.
        self.assertTrue(self.cache_path.exists())
        self.assertTrue(checksum_path_for(self.cache_path).exists())
        self.assertTrue(_verify_checksum(self.cache_path))
        self.assertEqual(self.cache_path.read_text(), str(DUMMY_DATA))

    def test_step1_missing_file_forces_computation(self):
        """
        Step 1: If cache is allowed but file is missing, it must compute, store, and return cache_hit=False.
        """
        cache_hit, result, checksum = cache_manager_load_or_compute(
            cache_path=self.cache_path,
            is_allowed=True,
            load_fn=self.mock_load,
            store_fn=self.mock_store,
            validate_fn=self.mock_validate,
            compute_fn=self.mock_compute,
            logger_fn=self.mock_logger
        )

        self.assertFalse(cache_hit, "cache_hit must be False when file is missing.")
        self.assertEqual(result, DUMMY_DATA)
        self.assertIsNone(checksum, "plain dict data has no compute_sha3_256_hash method.")
        self.mock_compute.assert_called_once()
        self.mock_store.assert_called_once()
        self.mock_load.assert_not_called()

    def test_step2_checksum_mismatch_forces_recomputation(self):
        """
        Step 2: If file exists but checksum fails, it must delete files, compute, store, and return cache_hit=False.
        """
        self.cache_path.write_text("corrupted data")
        checksum_path = self.cache_path.with_suffix(
            self.cache_path.suffix + SHA3_256_CHECKSUM_SUFFIX
        )
        checksum_path.write_text("0" * 64)

        cache_hit, result, checksum = cache_manager_load_or_compute(
            cache_path=self.cache_path,
            is_allowed=True,
            load_fn=self.mock_load,
            store_fn=self.mock_store,
            validate_fn=self.mock_validate,
            compute_fn=self.mock_compute,
            logger_fn=self.mock_logger
        )

        self.assertFalse(cache_hit, "cache_hit must be False on checksum mismatch.")
        self.assertEqual(result, DUMMY_DATA)
        self.assertIsNone(checksum, "plain dict data has no compute_sha3_256_hash method.")
        self.mock_compute.assert_called_once()
        self.mock_store.assert_called_once()
        self.mock_load.assert_not_called()

        self.mock_logger.assert_any_call(
            Relevance.WARN,
            f"Checksum validation failed for '{self.cache_path}' "
            f"(sidecar missing or mismatched). Deleting cache and recomputing.",
        )

        # The recompute actually replaced the stale bytes and left a valid sidecar behind.
        self.assertEqual(self.cache_path.read_text(), str(DUMMY_DATA))
        self.assertTrue(_verify_checksum(self.cache_path))

    def test_step3a_load_exception_forces_recomputation(self):
        """
        Step 3a: If checksum is ok, but load_fn raises an exception, it must delete files, compute,
        store, and return cache_hit=False.
        """
        self.cache_path.write_text("valid data")
        write_sha3_256_sidecar(self.cache_path)

        self.mock_load.side_effect = IOError("Disk read error")

        cache_hit, result, checksum = cache_manager_load_or_compute(
            cache_path=self.cache_path,
            is_allowed=True,
            load_fn=self.mock_load,
            store_fn=self.mock_store,
            validate_fn=self.mock_validate,
            compute_fn=self.mock_compute,
            logger_fn=self.mock_logger
        )

        self.assertFalse(cache_hit, "cache_hit must be False when load_fn raises an exception.")
        self.assertEqual(result, DUMMY_DATA)
        self.assertIsNone(checksum, "plain dict data has no compute_sha3_256_hash method.")
        self.mock_compute.assert_called_once()
        self.mock_store.assert_called_once()

        self.mock_logger.assert_any_call(
            Relevance.ERROR,
            f"Failed to load or validate cache file '{self.cache_path}': Disk read error. Recomputing."
        )

        # The recompute actually replaced the stale bytes and left a valid sidecar behind.
        self.assertEqual(self.cache_path.read_text(), str(DUMMY_DATA))
        self.assertTrue(_verify_checksum(self.cache_path))

    def test_step3b_validation_fails_forces_recomputation(self):
        """
        Step 3b: If checksum is ok, load succeeds, but validate_fn returns False, it must delete
        files, compute, store, and return cache_hit=False.
        """
        self.cache_path.write_text("valid data")
        write_sha3_256_sidecar(self.cache_path)

        self.mock_validate.return_value = False

        cache_hit, result, checksum = cache_manager_load_or_compute(
            cache_path=self.cache_path,
            is_allowed=True,
            load_fn=self.mock_load,
            store_fn=self.mock_store,
            validate_fn=self.mock_validate,
            compute_fn=self.mock_compute,
            logger_fn=self.mock_logger
        )

        self.assertFalse(cache_hit, "cache_hit must be False when validation fails.")
        self.assertEqual(result, DUMMY_DATA)
        self.assertIsNone(checksum, "plain dict data has no compute_sha3_256_hash method.")
        self.mock_compute.assert_called_once()
        self.mock_store.assert_called_once()
        self.mock_validate.assert_called_once_with(DUMMY_DATA)

        # The recompute actually replaced the stale bytes and left a valid sidecar behind.
        self.assertEqual(self.cache_path.read_text(), str(DUMMY_DATA))
        self.assertTrue(_verify_checksum(self.cache_path))

    def test_success_path_returns_cached_data(self):
        """
        Success Path: If all 4 steps pass, it must return the loaded data WITHOUT calling compute or
        store, and return cache_hit=True.
        """
        self.cache_path.write_text("valid data")
        write_sha3_256_sidecar(self.cache_path)

        cached_payload = {"result": "from_cache"}
        self.mock_load.return_value = cached_payload

        cache_hit, result, checksum = cache_manager_load_or_compute(
            cache_path=self.cache_path,
            is_allowed=True,
            load_fn=self.mock_load,
            store_fn=self.mock_store,
            validate_fn=self.mock_validate,
            compute_fn=self.mock_compute,
            logger_fn=self.mock_logger
        )

        self.assertTrue(cache_hit, "cache_hit must be True on successful cache load.")
        self.assertEqual(result, cached_payload)
        self.assertIsNone(checksum, "plain dict data has no compute_sha3_256_hash method.")
        self.mock_load.assert_called_once_with(self.cache_path)
        self.mock_validate.assert_called_once_with(cached_payload)

        self.mock_compute.assert_not_called()
        self.mock_store.assert_not_called()

        self.mock_logger.assert_any_call(
            Relevance.INFO, f"Cache successfully loaded and validated from '{self.cache_path}'."
        )

    # ------------------------------------------------------------------
    # The duck-typed compute_sha3_256_hash data-checksum path.
    # ------------------------------------------------------------------

    def test_compute_path_returns_data_checksum(self):
        """
        Data WITH a compute_sha3_256_hash method -> the method's value is the 3rd return element on
        the compute path.
        """
        digest = "ab" * 32
        data = DataWithChecksum(payload="computed", digest=digest)
        self.mock_compute.return_value = data

        cache_hit, result, checksum = cache_manager_load_or_compute(
            cache_path=self.cache_path,
            is_allowed=False,
            load_fn=self.mock_load,
            store_fn=self.mock_store,
            validate_fn=self.mock_validate,
            compute_fn=self.mock_compute,
            logger_fn=self.mock_logger
        )

        self.assertFalse(cache_hit)
        self.assertIs(result, data)
        self.assertEqual(checksum, digest)

    def test_load_path_returns_data_checksum(self):
        """
        Valid cache, loaded data WITH the method -> its value is the 3rd return element on the load path.
        """
        self.cache_path.write_text("valid data")
        write_sha3_256_sidecar(self.cache_path)
        digest = "cd" * 32
        cached = DataWithChecksum(payload="cached", digest=digest)
        self.mock_load.return_value = cached

        cache_hit, result, checksum = cache_manager_load_or_compute(
            cache_path=self.cache_path,
            is_allowed=True,
            load_fn=self.mock_load,
            store_fn=self.mock_store,
            validate_fn=self.mock_validate,
            compute_fn=self.mock_compute,
            logger_fn=self.mock_logger
        )

        self.assertTrue(cache_hit)
        self.assertIs(result, cached)
        self.assertEqual(checksum, digest)

    def test_checksum_method_missing_returns_none(self):
        """
        Data WITHOUT the method (plain dict) -> the 3rd return element is None on the compute path.
        """
        self.cache_path.write_text("old data")

        cache_hit, result, checksum = cache_manager_load_or_compute(
            cache_path=self.cache_path,
            is_allowed=False,
            load_fn=self.mock_load,
            store_fn=self.mock_store,
            validate_fn=self.mock_validate,
            compute_fn=self.mock_compute,
            logger_fn=self.mock_logger
        )

        self.assertFalse(cache_hit)
        self.assertEqual(result, DUMMY_DATA)
        self.assertIsNone(checksum)

    def test_checksum_attribute_not_callable_returns_none(self):
        """
        A compute_sha3_256_hash attribute that is NOT callable -> None, no exception, success path intact.
        """
        self.cache_path.write_text("valid data")
        write_sha3_256_sidecar(self.cache_path)
        cached = DataWithChecksum(payload="cached", digest="ef" * 32)
        cached.compute_sha3_256_hash = 5  # non-callable attribute
        self.mock_load.return_value = cached

        cache_hit, result, checksum = cache_manager_load_or_compute(
            cache_path=self.cache_path,
            is_allowed=True,
            load_fn=self.mock_load,
            store_fn=self.mock_store,
            validate_fn=self.mock_validate,
            compute_fn=self.mock_compute,
            logger_fn=self.mock_logger
        )

        self.assertTrue(cache_hit)
        self.assertIs(result, cached)
        self.assertIsNone(checksum)

    def test_load_path_checksum_method_raises_recomputes(self):
        """
        The data checksum method RAISING on the load path is caught by the step-3 try/except ->
        delete + recompute; the ERROR log carries the exception text.
        """
        self.cache_path.write_text("valid data")
        write_sha3_256_sidecar(self.cache_path)
        self.mock_load.return_value = DataWithBrokenChecksum(payload="cached", digest="00" * 32)

        cache_hit, result, checksum = cache_manager_load_or_compute(
            cache_path=self.cache_path,
            is_allowed=True,
            load_fn=self.mock_load,
            store_fn=self.mock_store,
            validate_fn=self.mock_validate,
            compute_fn=self.mock_compute,
            logger_fn=self.mock_logger
        )

        self.assertFalse(cache_hit)
        self.assertEqual(result, DUMMY_DATA, "the broken load is discarded, the data is recomputed")
        self.assertIsNone(checksum, "the recomputed plain dict has no checksum method")
        self.mock_logger.assert_any_call(
            Relevance.ERROR,
            f"Failed to load or validate cache file '{self.cache_path}': hash boom. Recomputing.",
        )
        self.assertEqual(self.cache_path.read_text(), str(DUMMY_DATA))

    def test_validate_exception_forces_recomputation(self):
        """
        A validate_fn that RAISES is caught by the step-3 try/except (same treatment as a load
        failure) -> delete + recompute; the ERROR log carries the exception text.
        """
        self.cache_path.write_text("valid data")
        write_sha3_256_sidecar(self.cache_path)

        def bad_validate(data):
            raise ValueError("validator bug")

        cache_hit, result, checksum = cache_manager_load_or_compute(
            cache_path=self.cache_path,
            is_allowed=True,
            load_fn=self.mock_load,
            store_fn=self.mock_store,
            validate_fn=bad_validate,
            compute_fn=self.mock_compute,
            logger_fn=self.mock_logger
        )

        self.assertFalse(cache_hit)
        self.assertEqual(result, DUMMY_DATA)
        self.assertIsNone(checksum)
        self.mock_logger.assert_any_call(
            Relevance.ERROR,
            f"Failed to load or validate cache file '{self.cache_path}': validator bug. Recomputing.",
        )
        self.assertEqual(self.cache_path.read_text(), str(DUMMY_DATA))

    def test_step2_missing_sidecar_forces_recomputation(self):
        """
        The step-2 branch also fires when the sidecar is merely MISSING (not only on mismatch):
        WARN, delete, recompute.
        """
        self.cache_path.write_text("valid data")  # data exists, no sidecar

        cache_hit, result, checksum = cache_manager_load_or_compute(
            cache_path=self.cache_path,
            is_allowed=True,
            load_fn=self.mock_load,
            store_fn=self.mock_store,
            validate_fn=self.mock_validate,
            compute_fn=self.mock_compute,
            logger_fn=self.mock_logger
        )

        self.assertFalse(cache_hit)
        self.assertEqual(result, DUMMY_DATA)
        self.assertIsNone(checksum)
        self.mock_compute.assert_called_once()
        self.mock_store.assert_called_once()
        self.mock_load.assert_not_called()
        self.mock_logger.assert_any_call(
            Relevance.WARN,
            f"Checksum validation failed for '{self.cache_path}' "
            f"(sidecar missing or mismatched). Deleting cache and recomputing.",
        )


class TestValidateCallCoercion(unittest.TestCase):
    """
    The @validate_call on cache_manager_load_or_compute type-coerces the arguments in pydantic lax mode.
    """

    def test_str_cache_path_is_coerced_to_path(self):
        """
        A str cache_path is coerced to a Path: the inner store_fn callback observes a pathlib Path,
        and the flow then dies in the framework's sidecar write (FileNotFoundError — the no-op
        store_fn never created the file).
        """
        seen = []
        with self.assertRaises(FileNotFoundError):
            cache_manager_load_or_compute(
                cache_path="not-a-path", is_allowed=False,
                load_fn=lambda p: None,
                store_fn=lambda d, p: seen.append(p),
                validate_fn=lambda d: True, compute_fn=lambda: None,
                logger_fn=lambda r, m: None)
        self.assertTrue(seen, "store_fn was not called")
        self.assertIsInstance(seen[0], Path)


if __name__ == '__main__':
    unittest.main()
