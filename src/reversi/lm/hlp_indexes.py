#
# hlp_indexes.py
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

from __future__ import annotations

import hashlib

from typing import TYPE_CHECKING
from pydantic import validate_call, ConfigDict
from pathlib import Path
from reversi.tools import binio

from reversi.index import IndexArray

if TYPE_CHECKING:
    from reversi.lm.logistic_model import LMContext



__all__ = ['LMIndexes',
           'hlp_indexes_store_to_file',
           'hlp_indexes_load_from_file',
           'hlp_indexes_compute',
           'hlp_indexes_is_cache_consistent']



class LMIndexes:
    """
    Holds the 2D index matrix together with the hash signature of the feature set used to compute it.
    """
    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def __init__(self,
                 rds_checksum: str,
                 feature_set_hash: str,
                 indexes: IndexArray):
        """
        Initialize the LMIndexes instance.

        Args:
            rds_checksum: the hash taken from the rds data set.
            feature_set_hash: the hash code of the feature set used to compute the indexes.
            indexes: the 2D (M, P) uint32 design-matrix index array (each cell is a weight index).
        """
        self.rds_checksum = rds_checksum
        self.feature_set_hash = feature_set_hash
        self.indexes = indexes

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def compute_sha3_256_hash(self) -> str:
        """
        Compute the SHA3-256 hash of the raw bytes of the indexes matrix.

        Returns:
            str: the 64-char hex digest.
        """
        hasher = hashlib.sha3_256()
        hasher.update(self.indexes.tobytes())
        sha3_256_hash = hasher.hexdigest()
        return sha3_256_hash

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def __repr__(self) -> str:
        """
        Summarize the instance in a concise one-line repr (the two hashes + the indexes shape).
        """
        return (f"LMIndexes(rds_checksum={self.rds_checksum!r}, "
                f"feature_set_hash={self.feature_set_hash!r}, "
                f"indexes={self.indexes.shape})")


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def hlp_indexes_store_to_file(
        hlp_indexes: LMIndexes,
        filename: str | Path,
        compressed: bool = True
) -> None:
    """
    Save the LMIndexes instance to a binary file.

    LZ4 whole-file compression by default. Note: the SHA3-256 sidecar is written by the binio writer
    (the checksum service is on by default); in the pipeline flow cache_manager re-writes the same
    sidecar (idempotent).

    Args:
        hlp_indexes: the instance to persist.
        filename: the destination path.
        compressed: True (the default) — the LZ4 whole-file compression.
    """
    filename = Path(filename)

    description = "LMIndexes binary data file"
    version = 1

    with binio.BinaryWriter(filename, compressed=compressed) as w:

        #: Write header
        w.write_header(description, version)

        #: Write the rds_checksum
        w.write_string(hlp_indexes.rds_checksum)

        #: Write the feature_set_hash
        w.write_string(hlp_indexes.feature_set_hash)

        # Write the data of the 2D indexes matrix
        w.write_array(hlp_indexes.indexes)

    return


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def hlp_indexes_load_from_file(
        filename: str | Path,
        checksum: bool = True,
        compressed: bool = True
) -> LMIndexes:
    """
    Load the LMIndexes instance from a binary file.

    LZ4 whole-file compression by default.

    Args:
        filename: the source path.
        checksum: True (the default) — verify the SHA3-256 sidecar before reading the file.
        compressed: True (the default) — the file is LZ4-compressed.

    Returns:
        LMIndexes: the loaded instance.
    """

    if checksum:
        is_consistent = binio.verify_sha3_256_sidecar(filename)
        if not is_consistent:
            raise RuntimeError("The checksum file signature doesn't match with current file.")

    expected_description = "LMIndexes binary data file"
    expected_version = 1

    with binio.BinaryReader(filename, compressed=compressed) as r:

        # Read the file header info
        description, version = r.read_header()
        if description != expected_description:
            raise RuntimeError(f"The file is not a proper {expected_description}.")
        if version != expected_version:
            raise RuntimeError(f"The file version is not consistent, found {version}, expected {expected_version}")

        #: Read the rds_checksum
        rds_checksum = r.read_string()

        #: Read the feature_set_hash
        feature_set_hash = r.read_string()

        # Read the data of the 2D indexes matrix
        indexes = r.read_array()

    hlp_indexes = LMIndexes(rds_checksum, feature_set_hash, indexes)

    return hlp_indexes

#: Here validation is not possible, it brings in a convoluted issue with circular imports.
def hlp_indexes_compute(
        ctx: LMContext
) -> LMIndexes:
    """
    Compute the model indexes from the live context.

    Args:
        ctx: the live context: the rds_checksum + the feature set (its hash, its indexes).

    Returns:
        LMIndexes: the freshly computed instance (the cache layer stores it).
    """
    rds_checksum = ctx.rds_checksum
    feature_set_hash = ctx.feature_set.hash
    indexes = ctx.feature_set.compute_indexes(ctx.positions)
    hlp_indexes = LMIndexes(rds_checksum, feature_set_hash, indexes)
    return hlp_indexes


def hlp_indexes_is_cache_consistent(
        ctx: LMContext,
        hlp_indexes: LMIndexes
) -> bool:
    """
    Compare the live configuration with the cached dataset metadata.

    Args:
        ctx: the live context (the rds_checksum + the feature-set hash).
        hlp_indexes: the cached instance.

    Returns:
        bool: True when both the rds checksum and the feature-set hash match.
    """

    cached_rds_checksum = hlp_indexes.rds_checksum
    cached_feature_set_hash = hlp_indexes.feature_set_hash
    expected_rds_checksum = ctx.rds_checksum
    expected_feature_set_hash = ctx.feature_set.hash
    is_cache_consistent = (cached_feature_set_hash == expected_feature_set_hash and
                           cached_rds_checksum == expected_rds_checksum)

    return is_cache_consistent
