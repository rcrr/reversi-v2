#
# hlp_design_matrix.py
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

# reversi/lm/hlp_design_matrix.py
from __future__ import annotations

import hashlib
import numpy as np

from typing import TYPE_CHECKING
from pathlib import Path
from pydantic import validate_call, ConfigDict

from reversi.tools import binio

if TYPE_CHECKING:
    from reversi.lm.logistic_model import LMContext



__all__ = ['ReversiLogisticModelDesignMatrix',
           'hlp_design_matrix_store_to_file',
           'hlp_design_matrix_load_from_file',
           'hlp_design_matrix_compute',
           'hlp_design_matrix_is_cache_consistent']



class ReversiLogisticModelDesignMatrix:
    """Represents the computed Design Matrix (X)."""
    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def __init__(self, wmaps_obj_checksum: str, X: np.ndarray):
        self.wmaps_obj_checksum = wmaps_obj_checksum
        self.X = X

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def compute_sha3_256_hash(self) -> str:
        hasher = hashlib.sha3_256()
        hasher.update(self.X.tobytes())
        sha3_256_hash = hasher.hexdigest()
        return sha3_256_hash


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def hlp_design_matrix_store_to_file(dm: ReversiLogisticModelDesignMatrix, filename: str | Path) -> None:
    """Saves the Design Matrix instance to a binary file."""
    filename = Path(filename)
    description = "ReversiLogisticModelDesignMatrix binary data file"
    version = 1

    with binio.BinaryWriter(filename) as w:
        w.write_header(description, version)
        w.write_string(dm.wmaps_obj_checksum)
        w.write_array(dm.X)


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def hlp_design_matrix_load_from_file(filename: str | Path, checksum: bool = True) -> ReversiLogisticModelDesignMatrix:
    """Loads a Design Matrix instance from a binary file."""
    if checksum:
        if not binio.verify_sha3_256_sidecar(filename):
            raise RuntimeError("The checksum file signature doesn't match with current file.")

    expected_description = "ReversiLogisticModelDesignMatrix binary data file"
    expected_version = 1

    with binio.BinaryReader(filename) as r:
        description, version = r.read_header()
        if description != expected_description:
            raise RuntimeError(f"The file is not a proper {expected_description}.")
        if version != expected_version:
            raise RuntimeError(f"File version mismatch: found {version}, expected {expected_version}")

        wmaps_obj_checksum = r.read_string()
        X = r.read_array()

    return ReversiLogisticModelDesignMatrix(
        wmaps_obj_checksum=wmaps_obj_checksum,
        X=X
    )


#: Here validation is not possible, it brings in a convoluted issue with circular imports.
def hlp_design_matrix_compute(ctx: "LMContext") -> ReversiLogisticModelDesignMatrix:
    """Computes the Design Matrix X from principal indexes and iwmap."""
    pindexes = ctx.hlp_indexes.indexes

    n_instances_per_feature = [f.n_instances for f in ctx.feature_set.features]
    col_offsets = np.repeat(ctx.iwmap_feature_offset[:-1], n_instances_per_feature)
    pindexes_with_offsets = pindexes + col_offsets

    if np.any(ctx.iwmap[pindexes_with_offsets] == -1):
        raise ValueError("It should never happen, pindexes is referring an invalid value.")

    X = np.empty(pindexes.shape, dtype=np.uint32)
    #: Explicit cast: ctx.iwmap is int64 (the -1 unseen-config sentinel),
    #: X is uint32 — the implicit output cast is deprecated (NumPy 2.5).
    np.take(ctx.iwmap.astype(np.uint32), pindexes_with_offsets, out=X)

    return ReversiLogisticModelDesignMatrix(
        wmaps_obj_checksum=ctx.wmaps_obj_checksum,
        X=X
    )


def hlp_design_matrix_is_cache_consistent(ctx: "LMContext", dm: ReversiLogisticModelDesignMatrix) -> bool:
    """Validates the cache by checking wmaps_obj_checksum."""
    is_hash_consistent = dm.wmaps_obj_checksum == ctx.wmaps_obj_checksum
    return is_hash_consistent
