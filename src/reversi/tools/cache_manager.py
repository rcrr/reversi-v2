#
# cache_manager.py
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

"""
Utility module to handle computation caching with a 4-step validation pipeline. It abstracts file
I/O, checksum validation, and cache invalidation. Checksum sidecar I/O is delegated to the
reversi.tools.binio sidecar API.
"""

from pathlib import Path
from typing import Callable, TypeVar

from pydantic import ConfigDict, validate_call

from reversi.tools.binio import (
    BinaryFormatError,
    verify_sha3_256_sidecar,
    write_sha3_256_sidecar,
)
from reversi.tools.state_machine import Relevance


__all__ = ['cache_manager_load_or_compute']


#: Generic type for the cached data structure
T = TypeVar('T')

#: Type aliases for injected business logic callbacks
ComputeFunc = Callable[[], T]
LoadFunc = Callable[[Path], T]
StoreFunc = Callable[[T, Path], None]
ValidateFunc = Callable[[T], bool]
LoggerFunc = Callable[[Relevance, str], None]


SHA3_256_CHECKSUM_SUFFIX = ".SHA3-256"


def _verify_checksum(file_path: Path) -> bool:
    """Verifies that the checksum sidecar of the data file exists and matches it (the pipeline step 2).

    Delegates to the binio sidecar API: a missing sidecar (FileNotFoundError), a malformed sidecar
    (BinaryFormatError) and an undecodable sidecar (UnicodeDecodeError) all mean "no valid sidecar"
    for the pipeline, so they are mapped to False instead of raising.

    Args:
        file_path (Path): The data file (the sidecar path is derived from it).
    """
    try:
        return verify_sha3_256_sidecar(file_path, suffix=SHA3_256_CHECKSUM_SUFFIX)
    except (FileNotFoundError, BinaryFormatError, UnicodeDecodeError):
        return False


def _delete_cache_files(cache_path: Path) -> None:
    """Safely deletes both the data file and its checksum sidecar.

    Args:
        cache_path (Path): The data file (the sidecar path is derived from it).
    """
    checksum_path = cache_path.with_suffix(cache_path.suffix + SHA3_256_CHECKSUM_SUFFIX)
    cache_path.unlink(missing_ok=True)
    checksum_path.unlink(missing_ok=True)


def _compute_sha3_256_hash(data: T) -> str | None:
    """Computes the data checksum of the cached object via duck typing.

    Looks for a callable compute_sha3_256_hash attribute on the data object; the data checksum is a
    different value and a different concept from the cache file checksum (the sidecar).

    Args:
        data (T): The cached data object.

    Returns:
        str: The object's content hash, or None when the attribute is missing or not callable.
    """
    callable_method = getattr(data, "compute_sha3_256_hash", None)

    if callable(callable_method):
        data_checksum = callable_method()  # Returns the sha3_256_checksum
    else:
        data_checksum = None
    return data_checksum


def _compute_and_store(cache_path: Path, compute_fn: ComputeFunc[T],
                       store_fn: StoreFunc[T], logger_fn: LoggerFunc) -> tuple[bool, T, str | None]:
    """Executes the shared compute tail: compute, store, and write the sidecar.

    Args:
        cache_path (Path): The cache data file (the sidecar path is derived from it).
        compute_fn (ComputeFunc[T]): The business-logic computation (no arguments, returns the data).
        store_fn (StoreFunc[T]): The business-logic store (data, cache_path).
        logger_fn (LoggerFunc): The log sink (a Relevance, message pair).

    Returns:
        tuple: The (False, data, data_checksum) triple — always a fresh computation (cache_hit
            False), the computed data, and its duck-typed data checksum (None when absent).
    """
    logger_fn(Relevance.INFO, "Executing heavy computation...")
    data = compute_fn()

    data_checksum = _compute_sha3_256_hash(data)

    logger_fn(Relevance.INFO, f"Computation finished. Storing to cache '{cache_path}'...")
    store_fn(data, cache_path)

    write_sha3_256_sidecar(cache_path, suffix=SHA3_256_CHECKSUM_SUFFIX)
    logger_fn(Relevance.INFO, "Cache file and checksum successfully written.")

    return False, data, data_checksum


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def cache_manager_load_or_compute(cache_path: Path,
                                  is_allowed: bool,
                                  load_fn: LoadFunc[T],
                                  store_fn: StoreFunc[T],
                                  validate_fn: ValidateFunc[T],
                                  compute_fn: ComputeFunc[T],
                                  logger_fn: LoggerFunc
                                  ) -> tuple[bool, T, str | None]:
    """Orchestrates the 4-step cache validation pipeline (load cached data or recompute).

    Every failure path deletes the cache files and converges on the compute tail, so the caller
    always gets fresh, stored, checksummed data. When the data object has a callable
    compute_sha3_256_hash method it is used to compute the data checksum — a different value and a
    different concept from the cache file checksum — returned as the third element of the result tuple.

    Args:
        cache_path (Path): The cache data file (coerced from str by the validate_call gate).
        is_allowed (bool): Step 0 — is caching allowed for this step? When False, computation is
            forced; the result is STILL stored to the cache file (intentional: a cache-disabled run
            always warms the cache).
        load_fn (LoadFunc[T]): The business-logic loader (cache_path) -> data.
        store_fn (StoreFunc[T]): The business-logic store (data, cache_path).
        validate_fn (ValidateFunc[T]): Step 3 — the business-logic data validation (data) -> bool.
        compute_fn (ComputeFunc[T]): The business-logic computation (no arguments) -> data.
        logger_fn (LoggerFunc): The log sink (a Relevance, message pair).

    Returns:
        tuple: The (cache_hit, data, data_checksum) triple — True when the data was loaded from the
            verified cache, False when it was computed; the computed or loaded data; the duck-typed
            data object checksum, or None when absent.
    """

    #: Step 0: Is cache allowed?
    if not is_allowed:
        logger_fn(Relevance.INFO, "Cache not allowed by configuration. Forcing computation.")
        return _compute_and_store(cache_path, compute_fn, store_fn, logger_fn)

    #: Step 1: Is cache present?
    if not cache_path.exists():
        logger_fn(Relevance.INFO, f"Cache file not found at '{cache_path}'. Forcing computation.")
        return _compute_and_store(cache_path, compute_fn, store_fn, logger_fn)

    #: Step 2: Is checksum consistent?
    if not _verify_checksum(cache_path):
        logger_fn(Relevance.WARN, f"Checksum validation failed for '{cache_path}' "
                                  "(sidecar missing or mismatched). Deleting cache and recomputing.")
        _delete_cache_files(cache_path)
        return _compute_and_store(cache_path, compute_fn, store_fn, logger_fn)

    # : Step 3: Is application data valid? (Business Logic) load + data checksum + validation are
    # all in the try: a raising load_fn, a raising data checksum, or a raising validate_fn all
    # invalidate the cache and force recomputation.
    try:
        cached_data = load_fn(cache_path)
        cached_checksum = _compute_sha3_256_hash(cached_data)
        is_valid = validate_fn(cached_data)
    except Exception as e:
        logger_fn(Relevance.ERROR, f"Failed to load or validate cache file '{cache_path}': {e}. Recomputing.")
        _delete_cache_files(cache_path)
        return _compute_and_store(cache_path, compute_fn, store_fn, logger_fn)

    if not is_valid:
        logger_fn(Relevance.WARN, f"Application data validation failed for '{cache_path}'. "
                                  "Deleting cache and recomputing.")
        _delete_cache_files(cache_path)
        return _compute_and_store(cache_path, compute_fn, store_fn, logger_fn)

    #: All steps passed: return cached data
    logger_fn(Relevance.INFO, f"Cache successfully loaded and validated from '{cache_path}'.")
    return True, cached_data, cached_checksum
