#
# pattern.py
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
pattern - pattern recognition for the Reversi pattern pipeline.

A pattern is a set of board squares given by its principal mask. The module computes the D8 orbit
(instances, stabilizer, the permutations the stabilizer induces on the squares), packs the 64-bit
board into S contiguous bits (the PEXT-style plan), encodes every configuration in base 3 (3^S
states, uint32), and reduces each configuration to its principal index under the induced symmetries
(Burnside). PatternSet runs the whole pipeline for N positions through one fused Numba kernel;
PatternType is the closed table of the 12 supported shapes.

Design choices --------------

* **Principal mask rule**: a mask is principal iff it is the numerically lowest of its 8 D8
  transforms; the constructor rejects the rest and names the offending slot.
* **PEXT-style packing**: the S squares compress to S contiguous bits; the plan's "planes" are runs
  of consecutive set bits (single-run patterns take a fast path).
* **Base-3 indexing**: digit k is 0 empty / 1 mover / 2 opponent; the principal index is the min
  over the configuration's orbit under the stabilizer's induced permutations.
* **Pydantic + Numba layering**: the constructor is a strict @validate_call; the hot paths are
  njit(parallel=True, cache=True); the construction-time path calls the pydantic-wrapped scalar
  functions directly.
* **Closed type table**: a fingerprint not in PatternType (the 12 members) raises at construction. *
**Platform: little-endian only**.
"""

from __future__ import annotations

from typing import TypeAlias, List, Tuple, Union, IO, Annotated
from enum import Enum
from pydantic import validate_call, ConfigDict, BeforeValidator

import sys
import io
import hashlib

import numpy as np
import numpy.typing as npt

import numba as nb

from reversi.board import (
    Square,
    square_as_bitboard, square_from_str, square_to_str,
    Bitboard, BitboardArray,
    bitboard_ro000,
    bitboard_count, bitboard_transformations,
    bitboard_to_square_list, bitboard_to_string_list,
    bitboard_trans_fs, bitboard_anti_trans_fs, bitboard_bsr,
    bitboard_anti_transformations,
    bitboard_transformation_labels, bitboard_anti_transformation_labels,
    PositionField, PositionArray
)

__all__ = ['Index', 'IndexArray',
           'Pattern', 'PatternType', 'sample_pattern_data',
           'PatternSet']

#: Represents a reversi pattern index.
Index: TypeAlias = np.uint32

def validate_index_array(v: any) -> any:
    """Ensure a numpy array strictly uses the uint32 dtype (scalars pass through)."""
    if isinstance(v, np.ndarray) and v.dtype != np.uint32:
        raise ValueError(f"Array dtype must be uint32, got {v.dtype}")
    return v

#: A Pydantic-compatible type hint for Index (np.uint32) arrays.
IndexArray = Annotated[npt.NDArray[np.uint32], BeforeValidator(validate_index_array)]

#: Conservative engine limit on the number of pattern squares. 18 is well inside the uint32 index
#: space (3^20 < 2^32), so 18 is a project choice, not a uint32 constraint.
MAX_NUMBER_OF_SQUARES_FOR_PATTERN = 18


class PatternType(Enum):
    TYPE_0 = (
        ("I0", "T1", "T2", "T3", "T4", "T5", "T6", "T7"),
        {"type": "0", "sample_mask": 0x0000000000000107, "sample_name": "ELLE", "level": 1, "n_instances": 8, "n_stabilizers": 1}
    )
    TYPE_1 = (
        ("I0", "T1", "S0", "S1", "T4", "T5", "S4", "S5"),
        {"type": "1", "sample_mask": 0x0000000c30000000, "sample_name": "SNAKE", "level": 2, "n_instances": 4, "n_stabilizers": 2}
    )
    TYPE_2 = (
        ("I0", "T1", "T2", "T3", "S0", "S1", "S2", "S3"),
        {"type": "2", "sample_mask": 0x00000000000000ff, "sample_name": "EDGE", "level": 2, "n_instances": 4, "n_stabilizers": 2}
    )
    TYPE_3 = (
        ("I0", "T1", "T2", "T3", "S1", "S2", "S3", "S0"),
        {"type": "3", "sample_mask": 0x0000000000010204, "sample_name": "DIAG3", "level": 2, "n_instances": 4, "n_stabilizers": 2}
    )
    TYPE_3D = (
        ("I0", "T1", "T2", "T3", "I1", "I2", "I3", "I0"),
        {"type": "3D", "sample_mask": 0x0000000000000001, "sample_name": "DOTA1", "level": 2, "n_instances": 4, "n_stabilizers": 2}
    )
    TYPE_4 = (
        ("I0", "T1", "T2", "T3", "S2", "S3", "S0", "S1"),
        {"type": "4", "sample_mask": 0x010100c1c1000101, "sample_name": "TAU", "level": 2, "n_instances": 4, "n_stabilizers": 2}
    )
    TYPE_5 = (
        ("I0", "T1", "T2", "T3", "S3", "S0", "S1", "S2"),
        {"type": "5", "sample_mask": 0x010204081020c0c0, "sample_name": "MACE", "level": 2, "n_instances": 4, "n_stabilizers": 2}
    )
    TYPE_6 = (
        ("I0", "S0", "S0", "S0", "T4", "S4", "S4", "S4"),
        {"type": "6", "sample_mask": 0x000008381c100000, "sample_name": "COREA", "level": 4, "n_instances": 2, "n_stabilizers": 4}
    )
    TYPE_7 = (
        ("I0", "T1", "S0", "S1", "S1", "S0", "S1", "S0"),
        {"type": "7", "sample_mask": 0x030304081020c0c0, "sample_name": "BARBEL", "level": 4, "n_instances": 2, "n_stabilizers": 4}
    )
    TYPE_7D = (
        ("I0", "T1", "S0", "S1", "I3", "I0", "I1", "I2"),
        {"type": "7D", "sample_mask": 0x0102040810204080, "sample_name": "DIAG8", "level": 4, "n_instances": 2, "n_stabilizers": 4}
    )
    TYPE_8 = (
        ("I0", "T1", "S0", "S1", "S0", "S1", "S0", "S1"),
        {"type": "8", "sample_mask": 0x0000003c3c000000, "sample_name": "RCT2X4", "level": 4, "n_instances": 2, "n_stabilizers": 4}
    )
    TYPE_9 = (
        ("I0", "S0", "S0", "S0", "S0", "S0", "S0", "S0"),
        {"type": "9", "sample_mask": 0x0000001818000000, "sample_name": "CORE", "level": 8, "n_instances": 1, "n_stabilizers": 8}
    )

    def __init__(self, fingerprint, data):
        self.fingerprint = tuple(fingerprint)
        self.data = data

    @classmethod
    def from_fingerprint(cls, fingerprint):
        """Look up the table entry for a fingerprint (a tuple or list of 8 markers); return None if unknown."""
        if not hasattr(cls, "_lookup"):
            cls._lookup = {item.fingerprint: item for item in cls}
        return cls._lookup.get(tuple(fingerprint))


class Pattern:
    """A Reversi pattern: a set of board squares given by its principal mask.

The construction computes the D8 orbit structure (instances, stabilizer, the induced permutations on
the pattern squares), the PEXT-style pack plan, and the base-3 configuration bookkeeping; the
principal-index structures are computed lazily by compute_principal_index_dict().

Attributes:
    name (str): the human-readable pattern label.
    mask (Bitboard): the principal mask (the numerically lowest of the 8 D8 transforms).
    n_squares (np.uint8): the number of set bits in the mask.
    n_configurations (int): 3 ** n_squares. tmasks (np.ndarray(8, Bitboard)): the 8 D8 transforms in
        canonical slot order.
    squares (List[Square]): the pattern square indices in ascending board order (A1 first).
    snames (List[str]): the pattern square names.
    unique_masks (List[Bitboard]): the distinct tmasks in first-seen order.
    mask_to_index (Dict[Bitboard, int]): the first-seen slot of each transformed mask. mask_indexes
        (np.ndarray(8, uint8)): for each slot, the first-seen slot of its mask. unique_mask_indexes
        (np.ndarray(n_instances, uint8)): the first-seen slots of the unique masks.
    n_instances (int): the orbit size |Orb(P)|.
    n_stabilizers (int): 8 // n_instances.
    trans_fs (List[Callable]): the transform functions of the unique instances (first-seen slots).
    anti_trans_fs (List[Callable]): the inverse transform functions of the unique instances.
    pack_plan (Tuple[BitboardArray, BitboardArray, NDArray[uint8]]): (p_masks, u_masks, p_shifts),
        the run-based pack/unpack plan.
    unique_symmetric_instance_indexes (List[int]): the stabilizer slots whose induced permutation on
        the pattern squares is distinct and non-identity (the automorphism group).
    symmetry_fs (List[Callable]): the transform functions of those stabilizer slots.
    anti_symmetry_fs (List[Callable]): the inverse transform functions of those slots.
    n_invariant_configs (int): 3^B, B = the number of G'-orbits on the pattern squares (G' = the
        group of the permutations the stabilizer induces on the squares).
    n_unique_configs (int): the Burnside average (1/|G'|) * sum_g 3^cycles(g); equals
        principal_index_count after compute_principal_index_dict().
    squares_t (List[List[int]]): per slot, the transformed pattern square indices.
    snames_t (List[List[str]]): per slot, the transformed pattern square names.
    squares_ts (List[List[int]]): squares_t, each row sorted.
    fingerprint (List[str]): the 8-slot I/S/T fingerprint (e.g. "I0", "T1", "S3").
    type_info (PatternType): the table entry matching the fingerprint. powers_3
        (np.ndarray(n_squares, Index)): 3**k for k in 0..n_squares-1. bit_shifts
        (np.ndarray(n_squares, Index)): 0..n_squares-1. trans_fs_labels (np.ndarray(n_instances,
        str)): the D8 labels of the instance transform functions. anti_trans_fs_labels
        (np.ndarray(n_instances, str)): the D8 labels of the instance inverse transform functions.
        symmetry_fs_labels (np.ndarray(len(symmetry_fs), str)): the D8 labels of the symmetry functions.
    principal_index_dict (NDArray[Index] | None): configuration index -> principal index (lazy).
    principal_indexes (NDArray[Index] | None): the unique principal indexes (lazy).
    principal_index_count (int | None): len(principal_indexes) (lazy)."""

    @classmethod
    def mdp_csv_file(cls, patterns: list[Pattern], filename: str) -> None:
        """Write the MDP CSV file for the provided patterns (the header line + one record per pattern).

Args:
    patterns (list[Pattern]): the patterns to write.
    filename (str): the output CSV path.

Raises:
    TypeError: patterns is not a list, any element is not a Pattern, or filename is not a str."""
        if not isinstance(patterns, list):
            raise TypeError("Argument patterns must be a list.")
        if not isinstance(filename, str):
            raise TypeError("Argument filename must be a string.")
        if not all(isinstance(p, Pattern) for p in patterns):
            raise TypeError("All elements in patterns must be Pattern instances.")

        with open(filename, 'w') as f:
            header = (
                "name,mask,"
                "n_squares,n_configurations,n_instances,n_stabilizers,"
                "cells,tmasks,mask_indexes,unique_masks,unique_mask_indexes,tr,at,sf,"
                "cells_t0,cells_t1,cells_t2,cells_t3,cells_t4,cells_t5,cells_t6,cells_t7,"
                "fingerprint,type"
            )
            f.write(header + "\n")
            for pattern in patterns:
                f.write(pattern.mdp_record() + '\n')

    @validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
    def __init__(self, name: str, mask: Bitboard):
        """Build the pattern from its principal mask.

Args:
    name (str): the human-readable pattern label.
    mask (Bitboard): the principal mask (strict np.uint64 scalar, no coercion).

Raises:
    ValidationError: the name is not a str, or the mask is not an np.uint64 scalar.
    ValueError: the mask is empty, it selects more than 18 squares, it is not the principal mask of
        its orbit (the error lists all 8 transforms and names the offending slot), or the
        fingerprint is not in the PatternType table."""
        self.name = name
        self.mask = mask
        self.n_squares = bitboard_count(mask)
        if self.n_squares == 0:
            raise ValueError(f"Pattern {self.name} has an empty mask: a pattern must select at least one square.")
        if self.n_squares > MAX_NUMBER_OF_SQUARES_FOR_PATTERN:
            raise ValueError(f"More than 18 squares is not supported! n_squares = {self.n_squares}. Aborting!")
        self.n_configurations = 3 ** int(self.n_squares)
        self.tmasks = bitboard_transformations(mask)
        self.squares = bitboard_to_square_list(mask)[::-1]
        self.snames = bitboard_to_string_list(mask)[::-1]
        self.unique_masks = list(dict.fromkeys(self.tmasks))
        # Reverse iteration: for duplicate mask values the LAST-written entry wins, i.e. the FIRST
        # (lowest) slot index — consistent with the first-seen order of unique_masks (dict.fromkeys) above.
        self.mask_to_index = {m: i for i, m in reversed(list(enumerate(self.tmasks)))}
        self.mask_indexes = np.zeros(8, dtype=np.uint8)
        for i, tmask in enumerate(self.tmasks):
            self.mask_indexes[i] = self.mask_to_index[tmask]
        self.unique_mask_indexes = np.array(list(dict.fromkeys(self.mask_indexes)))
        # n_instances corresponds to the cardinality of the orbit |Orb(P)|
        self.n_instances = len(self.unique_masks)
        # n_stabilizers corresponds to the order of the stabilizer |Stab(P)|
        self.n_stabilizers = 8 // self.n_instances
        self.trans_fs = [bitboard_trans_fs[i] for i in self.unique_mask_indexes]
        self.anti_trans_fs = [bitboard_anti_trans_fs[i] for i in self.unique_mask_indexes]

        def _check_mask_is_principal() -> int:
            """Check that the mask is the principal mask of its orbit.

The principal mask is the numerically lowest of the 8 transforms: a mask is a 64-bit integer, so the
orbit minimum is a unique representative.

Returns:
    The index of the offending transformation if the mask is not principal, else 0."""
            instance: int = 0
            principal = Bitboard(self.tmasks[0])
            for i in range(1, 8):
                if self.tmasks[i] < principal:
                    instance = i
                    break
            return instance

        principal_instance = _check_mask_is_principal()
        if principal_instance != 0:
            mesg = (
                "Argument mask is not principal, check transformations.\n"
                f"  Transformed masks: [{', '.join(f'0x{x:016X}' for x in self.tmasks)}]\n"
                f"  Principal instance is: #{principal_instance}, value: {self.tmasks[principal_instance]:016x}"
            )
            raise ValueError(mesg)

        def _precompute_pack_unpack_plans() -> Tuple[BitboardArray,
                                                     BitboardArray,
                                                     npt.NDArray[np.uint8]]:
            """Precompute the run-based pack/unpack plan (the p_masks, u_masks, p_shifts arrays)."""
            mask = self.mask
            one = Bitboard(1)
            all_ones = Bitboard(0xFFFFFFFFFFFFFFFF)
            dest_pos = 0
            source_pos = 0

            p_masks, u_masks, p_shifts = [], [], []

            while source_pos < 64:
                while source_pos < 64 and not (mask & (one << source_pos)):
                    source_pos += 1
                if source_pos >= 64: break

                start_source = source_pos
                while source_pos < 64 and (mask & (np.uint64(1) << source_pos)):
                    source_pos += 1
                block_len = source_pos - start_source

                pack_mask = (all_ones >> (64 - block_len)) << start_source
                shift_amount = start_source - dest_pos
                p_masks.append(pack_mask)
                p_shifts.append(shift_amount)

                unpack_mask = (all_ones >> (64 - block_len)) << dest_pos
                u_masks.append(unpack_mask)

                dest_pos += block_len

            return (np.array(p_masks, dtype=Bitboard),
                    np.array(u_masks, dtype=Bitboard),
                    np.array(p_shifts, dtype=np.uint8))


        self.pack_plan = _precompute_pack_unpack_plans()

        @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
        def _get_position_mapping(symms: List[List[int]]) -> List[int]:
            """Map each symmetry permutation to the index of its first occurrence.

Args:
    symms (List[List[int]]): the per-stabilizer-slot square permutations.

Returns:
    The first-occurrence index of each distinct permutation."""
            seen = {}
            res = []
            for i, arr in enumerate(symms):
                content = tuple(arr)
                if content not in seen:
                    seen[content] = i
                res.append(seen[content])
            return res

        symmetric_instance_indexes = np.where(self.mask_indexes == 0)[0]

        symms = []
        for i, instance_idx in enumerate(symmetric_instance_indexes):
            tfn = bitboard_trans_fs[instance_idx]
            atfn = bitboard_anti_trans_fs[instance_idx]
            exchanges = np.zeros(self.n_squares, dtype=np.uint8)
            for j in range(self.n_squares):
                sq = Square(j)
                sqm = square_as_bitboard(sq)
                sqm_up = self._unpack_bb(sqm)
                m = tfn(sqm_up)
                e = self._pack_bb(m)
                idx = bitboard_bsr(e)
                exchanges[j] = idx
            symms.append(exchanges)
        pos_map = _get_position_mapping(symms)
        unique_pos_map = set(pos_map)
        unique_pos_map.discard(0)
        self.unique_symmetric_instance_indexes = [int(x) for i, x in enumerate(symmetric_instance_indexes) if i in unique_pos_map]
        self.symmetry_fs = [bitboard_trans_fs[idx] for idx in self.unique_symmetric_instance_indexes]
        self.anti_symmetry_fs = [bitboard_anti_trans_fs[idx] for idx in self.unique_symmetric_instance_indexes]
        self._compute_symmetry_burnside_counts()

        self._compute_transformed_cells()
        self.squares_ts = [sorted(l) for l in self.squares_t]

        self.fingerprint: list[str | None] = [None] * 8
        self.fingerprint[0] = "I0"
        for i in range(1, 8):
            transformed_squares = self.squares_t[i]
            sorted_transformed_squares = self.squares_ts[i]
            found_i = False
            found_s = False
            pos_i = -1
            pos_s = -1
            for j in range(0, i):
                if not found_i and transformed_squares == self.squares_t[j]:
                    found_i = True
                    pos_i = j
                if not found_s and sorted_transformed_squares == self.squares_ts[j]:
                    found_s = True
                    pos_s = j
            if found_i:
                marker = f"I{pos_i}"
            elif found_s:
                marker = f"S{pos_s}"
            else:
                marker = f"T{i}"
            self.fingerprint[i] = marker

        self.type_info = PatternType.from_fingerprint(self.fingerprint)

        if self.type_info is None:
            message = (
                f"\n"
                f"  Name = {self.name}, mask = 0x{self.mask:016x}\n"
                f"  Fingerprint: [{', '.join(f'{fp}' for fp in self.fingerprint)}]\n"
            )
            raise ValueError(f"The pattern fingerprint has not been found: {message}")

        # The static type-table fields must agree with the values computed for the pattern (the 11
        # entries are consistent — spot-verified; raise if a future table edit breaks this).
        table_ni, table_ns = self.type_info.data["n_instances"], self.type_info.data["n_stabilizers"]
        if (self.n_instances, self.n_stabilizers) != (table_ni, table_ns):
            raise AssertionError(
                f"Type table inconsistency for {self.name}: computed "
                f"n_instances={self.n_instances}, n_stabilizers={self.n_stabilizers} "
                f"vs table n_instances={table_ni}, n_stabilizers={table_ns}."
            )

        # Used by compute_indexes_on_position and the PatternSet pipeline.
        self.powers_3 = 3 ** np.arange(self.n_squares, dtype=Index)
        self.bit_shifts = np.arange(self.n_squares, dtype=Index)

        # Used for printing information on the pattern
        self.trans_fs_labels = [bitboard_transformation_labels[i] for i in self.unique_mask_indexes]
        self.anti_trans_fs_labels = [bitboard_anti_transformation_labels[i] for i in self.unique_mask_indexes]
        self.symmetry_fs_labels = [bitboard_transformation_labels[i] for i in self.unique_symmetric_instance_indexes]

        # Get computed only if used.
        self.principal_index_dict: Union[npt.NDArray[Index], None] = None
        self.principal_indexes: Union[npt.NDArray[Index], None] = None
        self.principal_index_count: Union[int, None] = None

        # Invariance check
        self._check_invariances()


    def _compute_transformed_cells(self) -> None:
        """Compute the per-slot transformed square indices (squares_t) and names (snames_t).
        """
        self.squares_t = [[] for _ in range(8)]
        self.snames_t = [[] for _ in range(8)]
        for i, cell_name in enumerate(self.snames):
            sq = square_from_str(cell_name)
            sq_set = square_as_bitboard(sq)
            for j in range(8):
                transformed_sq = bitboard_trans_fs[j](sq_set)
                if transformed_sq != 0:
                    pos = bitboard_bsr(transformed_sq)
                    transformed_cell = Square(pos)
                    transformed_cell_name = square_to_str(Square(pos))
                else:
                    transformed_cell = None
                    transformed_cell_name = ""
                if transformed_cell is not None:
                    self.squares_t[j].append(int(transformed_cell))
                self.snames_t[j].append(transformed_cell_name)

    def _compute_symmetry_burnside_counts(self) -> None:
        """Compute the Burnside counts of the pattern configurations.

n_invariant_configs = 3^B (B = the number of G'-orbits on the pattern squares, where G' is the group
of the permutations the mask stabilizer induces on the squares). n_unique_configs = the Burnside
average (1/|G'|) * sum_g 3^cycles(g) over the distinct induced permutations; it equals
principal_index_count once compute_principal_index_dict() has run."""
        S = int(self.n_squares)
        square_index = {sq: i for i, sq in enumerate(self.squares)}
        perms = [tuple(range(S))]
        for f in self.symmetry_fs:
            perm = tuple(square_index[int(bitboard_bsr(f(square_as_bitboard(sq))))]
                         for sq in self.squares)
            if perm not in perms:
                perms.append(perm)
        # B = number of orbits of G' on the S squares
        seen = [False] * S
        n_orbits = 0
        for i in range(S):
            if seen[i]:
                continue
            n_orbits += 1
            stack = [i]
            seen[i] = True
            while stack:
                x = stack.pop()
                for p in perms:
                    y = p[x]
                    if not seen[y]:
                        seen[y] = True
                        stack.append(y)
        self.n_invariant_configs = 3 ** n_orbits

        def _cycles(perm: tuple) -> int:
            visited = [False] * S
            c = 0
            for i in range(S):
                if visited[i]:
                    continue
                c += 1
                x = i
                while not visited[x]:
                    visited[x] = True
                    x = perm[x]
            return c

        self.n_unique_configs = sum(3 ** _cycles(p) for p in perms) // len(perms)

    def _check_invariances(self) -> None:
        """Run the internal consistency checks on the symmetry mapping (mask_indexes, unique_mask_indexes,
symmetry functions); raise AssertionError on a violation."""
        # 1. Check consistency between mask_indexes and unique_masks The number of unique values in
        # mask_indexes must match len(unique_masks)
        if len(set(self.mask_indexes)) != self.n_instances:
            raise AssertionError("Inconsistency between mask_indexes and n_instances.")

        # 2. Check that unique_mask_indexes points to the correct unique masks
        for i, m_idx in enumerate(self.unique_mask_indexes):
            if self.tmasks[m_idx] != self.unique_masks[i]:
                raise AssertionError(f"Unique mask mismatch at index {m_idx}.")

        # 3. Check Symmetry Functions (Automorphisms) For each symmetry_f, transforming the
        # principal mask must yield the same mask
        for i, f_idx in enumerate(self.unique_symmetric_instance_indexes):
            f = self.symmetry_fs[i]
            transformed_mask = f(self.mask)
            if transformed_mask != self.mask:
                raise AssertionError(f"Symmetry function at index {f_idx} does not preserve the mask.")

        # 4. Check Mapping logic: symmetry_fs must be a subset of the first 8 transformations
        if not set(self.symmetry_fs).issubset(set(bitboard_trans_fs)):
            raise AssertionError("symmetry_fs contains unknown transformation functions.")

    def mdp_record(self) -> str:
        """Return the pattern's MDP CSV record line (the 24 comma-separated fields)."""
        ptype = self.type_info.data["type"]
        return (
            f"{self.name},{self.mask:016X},{self.n_squares},{self.n_configurations}"
            f",{self.n_instances},{self.n_stabilizers},{':'.join(self.snames)}"
            f",{':'.join(f'{m:016X}' for m in self.tmasks)}"
            f",{':'.join(str(i) for i in self.mask_indexes)}"
            f",{':'.join(f'{m:016X}' for m in self.unique_masks)}"
            f",{':'.join(str(i) for i in self.unique_mask_indexes)}"
            f",{':'.join(f'{fn}' for fn in self.trans_fs_labels)}"
            f",{':'.join(f'{fn}' for fn in self.anti_trans_fs_labels)}"
            f",{':'.join(f'{fn}' for fn in self.symmetry_fs_labels)}"
            f",{','.join(':'.join(self.snames_t[i]) for i in range(8))}"
            f",{':'.join(f'{fp}' for fp in self.fingerprint)}"
            f",{ptype}"
        )

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def __repr__(self) -> str:
        """Return the one-line summary (same info as the first line of print())."""
        return f"Pattern(name={self.name!r}, mask=0x{self.mask:016x})"

    def print(self, output: Union[IO, io.StringIO] = sys.stdout) -> None:
        """Print the detailed pattern report to the output stream (stdout by default)."""
        prt = lambda msg: print(msg, file=output)
        ptype = self.type_info.data["type"]
        prt(f"[Pattern: name = {self.name}, mask = 0x{self.mask:016x}]")
        prt(
            f"  [n_squares = {self.n_squares}, n_configurations = {self.n_configurations}, "
            f"n_instances = {self.n_instances}, n_stabilizers = {self.n_stabilizers}, type = {ptype}]"
        )
        prt(f"  Cells:                [{', '.join(f'{cn}' for cn in self.snames)}]")
        prt(f"  Transformed masks:    [{', '.join(f'0x{x:016X}' for x in self.tmasks)}]")
        prt(f"  Mask indexes:         [{', '.join(f'{x}' for x in self.mask_indexes)}]")
        prt(f"  Unique masks:         [{', '.join(f'0x{x:016X}' for x in self.unique_masks)}]")
        prt(f"  Unique mask indexes:  [{', '.join(f'{x}' for x in self.unique_mask_indexes)}]")
        prt(f"  Transf. functions:    [{', '.join(f'{fn}' for fn in self.trans_fs_labels)}]")
        prt(f"  Anti-transf. f.:      [{', '.join(f'{fn}' for fn in self.anti_trans_fs_labels)}]")
        prt(f"  Symmetry functions:   [{', '.join(f'{fn}' for fn in self.symmetry_fs_labels)}]")
        prt(f"  Transformed cells:    [{', '.join(f'{l}' for l in self.squares_t)}]")
        prt(f"  Transf. sorted cells: [{', '.join(f'{l}' for l in self.squares_ts)}]")
        prt(f"  Fingerprint:          [{', '.join(f'{fp}' for fp in self.fingerprint)}]")

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def _pack_bb(self, bb: Bitboard | BitboardArray) -> Bitboard | BitboardArray:
        """Pack a bitboard (or an array of bitboards) into the pattern's contiguous square bits.

Args:
    bb (Bitboard | BitboardArray): the input bitboard or array.

Returns:
    The packed value (a Bitboard scalar for a scalar input, an array otherwise)."""
        pack_masks, _, pack_shifts = self.pack_plan

        # Ensure data is passed as a NumPy array for Numba compatibility
        bb_arr = np.asarray(bb, dtype=np.uint64)

        result = _numba_pack_bb_kernel(bb_arr, pack_masks, pack_shifts)

        # If input was a scalar/object, match your original type expectations if needed
        return result if isinstance(bb, np.ndarray) else Bitboard(result.item())

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def _unpack_bb(self, packed_bb: Bitboard | BitboardArray) -> Bitboard | BitboardArray:
        """Unpack a packed square set back to the pattern square positions (the inverse of _pack_bb).

Args:
    packed_bb (Bitboard | BitboardArray): the packed bitboard or array.

Returns:
    The restored bitboard (scalar or array, matching the input)."""
        _, unpack_masks, pack_shifts = self.pack_plan

        # Ensure correct NumPy type formatting before calling Numba
        packed_arr = np.asarray(packed_bb, dtype=np.uint64)

        # Call the parallelized Numba unpacking kernel
        result = _numba_unpack_bb_kernel(packed_arr, unpack_masks, pack_shifts)

        # Match the scalar or array output format of the input
        return result if isinstance(packed_bb, np.ndarray) else Bitboard(result.item())

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def compute_indexes_on_position(self, pos: PositionField | PositionArray) -> npt.NDArray[Index]:
        """Compute the pattern indexes on the given position (or an array of positions).

The anti-transform -> pack -> base-3 pipeline over the unique instance masks.

Args:
    pos (PositionField | PositionArray): a single position or an array of any shape.

Precondition:
    The positions are collision-free (mover & opponent == 0); the caller validates (e.g.
    board.position_check_collisions).

Returns:
    A 1-D array of uint32 indexes for a scalar input; pos.shape + (n_instances,) for an array
    input (a 1-D (N,) batch gives (N, n_instances); the N-D path flattens the (..., 8)
    transformation matrices to (-1, 8) before the column selection)."""
        is_scalar = not isinstance(pos, np.ndarray)

        m = np.atleast_1d(pos['mover'])
        o = np.atleast_1d(pos['opponent'])

        # 1. High-speed C-layout anti-transformations
        atrs_m = bitboard_anti_transformations(m)
        atrs_o = bitboard_anti_transformations(o)

        is_nd = atrs_m.ndim > 2
        if is_nd:
            # The N-D contract: flatten the transformation matrices to (-1, 8) so the column
            # selection below picks the instance axis (an N-D [:, indexes] would index the middle
            # axis instead).
            atrs_m = atrs_m.reshape(-1, 8)
            atrs_o = atrs_o.reshape(-1, 8)

        # 2. Extract unique symmetries along the column axis safely
        sym_m = atrs_m[:, self.unique_mask_indexes]
        sym_o = atrs_o[:, self.unique_mask_indexes]

        # 3. Pack the instance bitboards with the pattern pack plan.
        packed_m = self._pack_bb(sym_m)
        packed_o = self._pack_bb(sym_o)

        # 4. Compute the base-3 indexes on the packed tensors.
        ret = _numba_computes_indexes_kernel(
            packed_m,
            packed_o,
            self.bit_shifts,
            self.powers_3
        )

        if is_scalar:
            return ret[0] # Return as scalar view if input was a single field
        if is_nd:
            # Reshape the flat (N, M_unique) result back to the positions shape + (M_unique,).
            return ret.reshape(pos.shape + (ret.shape[1],))
        return ret

    def compute_principal_index_dict(self) -> None:
        """Compute the principal-index structures (populates the lazy attributes).

principal_index_dict maps each configuration index to its principal index (the minimum over its
stabilizer orbit); principal_indexes and principal_index_count are derived from it."""
        def _symmetry_transformations(ss_array: npt.NDArray[Bitboard],
                                     symmetry_functions: List[Callable[[npt.NDArray[np.uint64]], npt.NDArray[np.uint64]]]) -> npt.NDArray[np.uint64]:
            # Apply each function to the entire array and collect the results in a list
            symmetries = [f(ss_array) for f in symmetry_functions]
            # Stack the columns into a single matrix N x X
            return np.column_stack(symmetries)

        def _compute_mover_opponent_by_index_value(n_squares: int) -> Tuple[BitboardArray, BitboardArray]:
            N = 3 ** n_squares
            indices = np.arange(N, dtype=Index)
            powers = 3 ** np.arange(n_squares, dtype=Index)
            digits = (indices[:, None] // powers) % 3
            bit_powers = Bitboard(1) << np.arange(n_squares, dtype=Bitboard)
            m = np.sum((digits == 1) * bit_powers, axis=1, dtype=Bitboard)
            o = np.sum((digits == 2) * bit_powers, axis=1, dtype=Bitboard)
            return m, o

        def _compute_indexes_on_ss_packed_tensor(p: Pattern,
                                                 m: npt.NDArray[np.uint64],
                                                 o: npt.NDArray[np.uint64]
                                                 ) -> npt.NDArray[np.uint32]:
            """Compute the base-3 configuration indexes on the packed mover/opponent tensors.

Args:
    m (npt.NDArray[np.uint64]): the packed mover square sets.
    o (npt.NDArray[np.uint64]): the packed opponent square sets (same shape as m).

Returns:
    The configuration indexes (same shape as m)."""
            combined = np.stack([m, o])
            bits = (combined[..., np.newaxis] >> p.bit_shifts) & 1
            idxs = bits @ p.powers_3
            indexes = (idxs[0] + 2 * idxs[1]).astype(np.uint32)
            return indexes

        # -1- Compute the packed configurations of mover and opponent. This code is executed the
        # same for each pattern, so it could be factored and memoized, doing it for the largest one.
        # It is not done because this computation is not part of the data pipeline.
        m, o = _compute_mover_opponent_by_index_value(int(self.n_squares))

        # -2- Unpack the two square sets to get the instance 0 of the pattern with the given index.
        m_unpacked, o_unpacked = self._unpack_bb(m), self._unpack_bb(o)

        # -3- Apply the symmetry operations
        symm_tr_fs = [bitboard_ro000] + self.symmetry_fs
        m_syms = _symmetry_transformations(m_unpacked, symm_tr_fs)
        o_syms = _symmetry_transformations(o_unpacked, symm_tr_fs)

        # -4- Pack the results
        m_syms_packed = self._pack_bb(m_syms)
        o_syms_packed = self._pack_bb(o_syms)

        # -5- Calculate the indexes of the symmetric instances
        sym_indexes = _compute_indexes_on_ss_packed_tensor(self, m_syms_packed, o_syms_packed)

        # -6- Take the lowest available value and insert it into principal_index_dict[index]
        self.principal_index_dict = sym_indexes.min(axis=1)
        self.principal_indexes = np.unique(self.principal_index_dict)
        self.principal_index_count = len(self.principal_indexes)

        return

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def convert_to_principal_index(self, index: IndexArray) -> IndexArray:
        """Convert configuration indexes to their principal indexes (computes the dictionary on first use).

Args:
    index (IndexArray): an array of uint32 configuration indexes (the ndarray dtype is enforced; a
        scalar is rejected by the NDArray check).

Returns:
    The principal indexes (an IndexArray, the same shape as the input)."""
        if self.principal_index_dict is None:
            self.compute_principal_index_dict()
        principal_index = self.principal_index_dict[index]
        return principal_index


@nb.njit(parallel=True, cache=True)
def _numba_pack_bb_kernel(bb_array, pack_masks, pack_shifts):
    """Numba PEXT-simulation kernel: pack a flat bitboard array with the plan's (masks, shifts);
single-plane and multi-plane cases."""
    # Flattens the input view to easily iterate over any multidimensional shape
    flat_bb = bb_array.ravel()
    num_elements = flat_bb.size
    num_planes = pack_masks.shape[0]

    # Pre-allocate output array using np.empty (no initialization overhead)
    out = np.empty(num_elements, dtype=Bitboard)

    # CASE 1: Single-plane optimization (e.g., EDGE pattern)
    if num_planes == 1:
        mask = pack_masks[0]
        shift = pack_shifts[0]
        # nb.prange automatically distributes iterations across threads
        for i in nb.prange(num_elements):
            out[i] = (flat_bb[i] & mask) >> shift

    # CASE 2: Multi-plane optimization (e.g., CORNER, DIAG8)
    else:
        for i in nb.prange(num_elements):
            val = flat_bb[i]
            acc = np.uint64(0)
            for p in range(num_planes):
                acc |= (val & pack_masks[p]) >> pack_shifts[p]
            out[i] = acc

    return out.reshape(bb_array.shape)

@nb.njit(parallel=True, cache=True)
def _numba_unpack_bb_kernel(packed_array, unpack_masks, pack_shifts):
    """Numba PDEP-simulation kernel: unpack a flat packed array with the plan's (masks, shifts);
single-plane and multi-plane cases."""
    flat_packed = packed_array.ravel()
    num_elements = flat_packed.size
    num_planes = unpack_masks.size  # Total number of bits/planes in the plan

    # Pre-allocate output array instantly using np.empty
    out = np.empty(num_elements, dtype=np.uint64)

    # CASE 1: Single-plane optimization (e.g., EDGE pattern)
    if num_planes == 1:
        mask = unpack_masks[0]
        shift = pack_shifts[0]
        for i in nb.prange(num_elements):
            out[i] = (flat_packed[i] & mask) << shift

    # CASE 2: Multi-plane optimization (e.g., CORNER, DIAG8)
    else:
        for i in nb.prange(num_elements):
            val = flat_packed[i]
            acc = np.uint64(0)
            for p in range(num_planes):
                acc |= (val & unpack_masks[p]) << pack_shifts[p]
            out[i] = acc

    return out.reshape(packed_array.shape)

@nb.njit(parallel=True, cache=True)
def _numba_computes_indexes_kernel(packed_m, packed_o, bit_shifts, powers_3):
    """Numba base-3 kernel: compute the configuration indexes on packed mover/opponent arrays (the 1-D
single-position and the 2-D (N, M) batch cases)."""
    B = len(bit_shifts)

    if packed_m.ndim == 1:
        # 1D Array Input Case (Scalar Position Field)
        M = packed_m.shape[0]
        out = np.zeros(M, dtype=Index)
        for j in range(M):
            val_m = packed_m[j]
            val_o = packed_o[j]
            idx_sum = Index(0)
            for b in range(B):
                shift = bit_shifts[b]
                bit_m = (val_m >> shift) & Bitboard(1)
                bit_o = (val_o >> shift) & Bitboard(1)
                idx_sum += (bit_m * powers_3[b]) + (bit_o * (Index(2) * powers_3[b]))
            out[j] = idx_sum
        return out
    else:
        # 2D Array Input Case (N positions, M_unique symmetries)
        N, M = packed_m.shape
        # Flatten output array for continuous L1/L2 cache efficiency
        total_elements = N * M
        out_flat = np.zeros(total_elements, dtype=Index)

        # Flatten input views completely to eliminate non-contiguous stride overheads
        flat_m = packed_m.ravel()
        flat_o = packed_o.ravel()

        for i in nb.prange(total_elements):
            val_m = flat_m[i]
            val_o = flat_o[i]
            idx_sum = Index(0)
            for b in range(B):
                shift = bit_shifts[b]
                bit_m = (val_m >> shift) & Bitboard(1)
                bit_o = (val_o >> shift) & Bitboard(1)
                idx_sum += (bit_m * powers_3[b]) + (bit_o * (Index(2) * powers_3[b]))
            out_flat[i] = idx_sum

        # Reshape back to (N, M) instantaneously at the C-level with zero data copying
        return out_flat.reshape((N, M))

#: ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###

#:
#: A list of Patterns.
#:
#: Use it to generate the mdp.csv file used by the LaTeX document:
#:
#: $ cd <workspace root>
#:
#: $ source .venv/bin/activate
#:
#: $ python
#:
#: >>> from reversi.board import *
#:
#: >>> from reversi.pattern import *
#:
#: >>> sample_patterns = [Pattern(name, Bitboard(mask)) for name, mask in sample_pattern_data]
#:
#: >>> Pattern.mdp_csv_file(sample_patterns, 'build/tmp/mdp_test.csv')
#:
sample_pattern_data = [
    ('ELLE',   0x0000000000000107),
    ('SNAKE',  0x0000000C30000000),
    ('EDGE',   0x00000000000000FF),
    ('R2',     0x000000000000FF00),
    ('R3',     0x0000000000FF0000),
    ('R4',     0x00000000FF000000),
    ('XEDGE',  0x00000000000042FF),
    ('DIAG3',  0x0000000000010204),
    ('DIAG4',  0x0000000001020408),
    ('DIAG5',  0x0000000102040810),
    ('DIAG6',  0x0000010204081020),
    ('DIAG7',  0x0001020408102040),
    ('DIAG8',  0x0102040810204080),
    ('CORNER', 0x0000000000070707),
    ('2X5COR', 0x0000000000001F1F),
    ('2X6COR', 0x0000000000003F3F),
    ('RCT2X4', 0x0000003C3C000000),
    ('CASTLE', 0x000000000000C3FF),
    ('BARBEL', 0x030304081020C0C0),
    ('MACE',   0x010204081020C0C0),
    ('FOURC',  0x8100000000000081),
    ('CORE',   0x0000001818000000),
    ('CORED',  0x0000241818240000),
    ('COREA',  0x000008381C100000),
    ('WHIRL',  0x83800000000001C1),
    ('TAU',    0x010100C1C1000101),
    ('DOTA1',  0x0000000000000001),
    ('DOTB1',  0x0000000000000002),
    ('TWOND',  0x0000000000000201),
]

#: ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###

class PatternSet:
    """A named, mask-sorted collection of patterns.

Attributes:
    name (str): the human-readable set label.
    patterns (List[Pattern]): the patterns sorted by mask value.
    hash (str): the sha3_256 hex digest of the concatenated little-endian mask bytes."""

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def __init__(self, name: str, patterns: List[Pattern]):
        """Build the set from a name and a non-empty list of patterns.

Args:
    name (str): the human-readable set label.
    patterns (List[Pattern]): the patterns to include.

Raises:
    ValidationError: the name is not a str, or a list element is not a Pattern.
    ValueError: the list is empty, or the pattern names or masks are not unique."""
        # Reject an empty pattern set: it is meaningless for the indexing pipeline (no patterns ->
        # no indexes) and would crash deeper in compute_principal_indexes with an unhelpful max() error.
        if not patterns:
            raise ValueError('Patterns list cannot be empty')

        # Extract and check for duplicate names
        names = [p.name for p in patterns]
        if len(names) != len(set(names)):
            raise ValueError('Patterns list contains duplicate names')

        # Extract masks and check for duplicates
        masks = [pattern.mask for pattern in patterns]
        if len(masks) != len(set(masks)):
            raise ValueError('Patterns list contains duplicate masks')

        # Sort patterns by mask value
        self.patterns = sorted(patterns, key=lambda p: p.mask)

        # Create hash of sorted masks
        hash_input = b''.join(pattern.mask.tobytes() for pattern in self.patterns)
        self.hash = hashlib.sha3_256(hash_input).hexdigest()

        self.name = name

    def __repr__(self) -> str:
        """Return the one-line summary (name, set hash, the patterns via their own __repr__)."""
        return f"PatternSet(name={self.name!r}, hash={self.hash}, patterns={self.patterns})"

    @property
    def names(self) -> List[str]:
        """Return the list of the pattern names (the set's sorted order)."""
        return [pattern.name for pattern in self.patterns]

    @property
    def masks(self) -> np.ndarray:
        """Return the pattern masks as a uint64 array (the set's sorted order)."""
        return np.array([pattern.mask for pattern in self.patterns], dtype=np.uint64)

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def print_summary(self, output: Union[IO, io.StringIO] = sys.stdout) -> None:
        """Print the set summary (name, length, hash, one line per pattern) to the output stream (stdout by default)."""
        prt = lambda msg: print(msg, file=output)
        prt(f"PatternSet: name = {self.name}, length = {len(self.patterns)}, hash = {self.hash}")
        for p in self.patterns:
            prt(f"  Pattern: name = {p.name}, mask = 0x{p.mask:016x}")

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def print(self, output: Union[IO, io.StringIO] = sys.stdout) -> None:
        """Print the set summary followed by every pattern's detailed report, to the output stream
        (stdout by default)."""
        print(f"PatternSet: name = {self.name}, length = {len(self.patterns)}, hash = {self.hash}", file=output)
        for pattern in self.patterns:
            pattern.print(output=output)

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def compute_principal_indexes(self, positions: PositionArray) -> IndexArray:
        """Compute the principal indexes of every pattern in the set, on the given positions.

The fused Numba pipeline (anti-transform, inlined pack, base-3, per-pattern coset minimum).

Precondition:
    The positions are collision-free (mover & opponent == 0); the caller validates (e.g.
    board.position_check_collisions).

Returns:
    A positions.shape + (total_cols,) uint32 array, total_cols = the sum of the distinct-mask
    groups (n_instances) over the set's patterns, concatenated in mask-sorted order (a 1-D (N,)
    batch gives (N, total_cols); the 1-D path passes the (N, 8) arrays straight to the kernel)."""
        L = len(self.patterns)

        m = positions['mover']
        o = positions['opponent']

        # 1. High-speed C-layout anti-transformations
        m_atrxs = bitboard_anti_transformations(m)
        o_atrxs = bitboard_anti_transformations(o)

        # 2. Extract layout dimensions and structural invariants
        S_max = max(p.n_squares for p in self.patterns)
        P_max = max(p.pack_plan[0].shape[0] for p in self.patterns) # Max configuration planes

        powers_3 = np.array([3**j for j in range(S_max)], dtype=Index)

        # Pre-allocate structures for unified vectorized stack execution
        n_squares_arr = np.array([p.n_squares for p in self.patterns], dtype=Index)
        num_planes_arr = np.empty(L, dtype=Index)

        bit_shifts_matrix = np.zeros((L, S_max), dtype=Index)
        idx_sort_matrix = np.zeros((L, 8), dtype=Index)

        n_groups_arr = np.empty(L, dtype=Index)
        group_size_arr = np.empty(L, dtype=Index)
        col_offsets = np.empty(L, dtype=Index)

        pack_masks_3d = np.zeros((L, P_max), dtype=Bitboard)
        pack_shifts_3d = np.zeros((L, P_max), dtype=Bitboard)

        current_col = 0
        for i, p in enumerate(self.patterns):
            S = p.n_squares
            bit_shifts_matrix[i, :S] = p.bit_shifts

            # Extract grouping properties for the reduction step
            mi = p.mask_indexes
            unique_vals = np.unique(mi)
            n_groups = len(unique_vals)

            n_groups_arr[i] = n_groups
            group_size_arr[i] = 8 // n_groups
            idx_sort_matrix[i, :] = np.argsort(mi)
            col_offsets[i] = current_col

            # Unpack PEXT simulation attributes from each pattern's pack_plan
            p_masks, _, p_shifts = p.pack_plan
            num_planes = p_masks.shape[0]
            num_planes_arr[i] = num_planes

            pack_masks_3d[i, :num_planes] = p_masks
            pack_shifts_3d[i, :num_planes] = p_shifts

            current_col += n_groups

        # 3. Stream data straight into the optimized Numba kernel
        if m_atrxs.ndim == 2:
            # The 1-D fast path: the (N, 8) transformation arrays go straight to the kernel.
            return _numba_compute_principal_indexes_kernel(
                m_atrxs,
                o_atrxs,
                n_squares_arr,
                bit_shifts_matrix,
                powers_3,
                n_groups_arr,
                group_size_arr,
                idx_sort_matrix,
                current_col,
                col_offsets,
                num_planes_arr,
                pack_masks_3d,
                pack_shifts_3d
            )
        # The N-D contract: the kernel over the (-1, 8) flattened C-order views, the output reshaped
        # to the positions shape + (total_cols,).
        return _numba_compute_principal_indexes_kernel(
            m_atrxs.reshape(-1, 8),
            o_atrxs.reshape(-1, 8),
            n_squares_arr,
            bit_shifts_matrix,
            powers_3,
            n_groups_arr,
            group_size_arr,
            idx_sort_matrix,
            current_col,
            col_offsets,
            num_planes_arr,
            pack_masks_3d,
            pack_shifts_3d
        ).reshape(positions.shape + (current_col,))



@nb.njit(parallel=True, cache=True)
def _numba_compute_principal_indexes_kernel(
    m_atrxs: np.ndarray,          # Shape: (N, 8), dtype: Bitboard
    o_atrxs: np.ndarray,          # Shape: (N, 8), dtype: Bitboard
    n_squares_arr: np.ndarray,    # Shape: (L,), dtype: Index
    bit_shifts_matrix: np.ndarray,# Shape: (L, S_max), dtype: Index
    powers_3: np.ndarray,         # Shape: (S_max,), dtype: Index
    n_groups_arr: np.ndarray,     # Shape: (L,), dtype: Index
    group_size_arr: np.ndarray,   # Shape: (L,), dtype: Index
    idx_sort_matrix: np.ndarray,  # Shape: (L, 8), dtype: Index
    total_cols: int,
    col_offsets: np.ndarray,      # Shape: (L,), dtype: Index
    num_planes_arr: np.ndarray,   # Shape: (L,), dtype: Index
    pack_masks_3d: np.ndarray,    # Shape: (L, P_max), dtype: Bitboard
    pack_shifts_3d: np.ndarray    # Shape: (L, P_max), dtype: Bitboard
) -> np.ndarray:
    """The fused Numba pipeline kernel: for every position (row) and pattern (L), the inlined PEXT pack,
the base-3 index, and the per-pattern coset minimum, streamed into the (N, total_cols) output grid."""
    BITBOARD_ZERO = Bitboard(0)
    BITBOARD_ONE = Bitboard(1)
    INDEX_TWO = Index(2)
    INDEX_ZERO = Index(0)

    N = m_atrxs.shape[0]
    L = n_squares_arr.shape[0]

    # Pre-allocate the massive contiguous block to avoid memory fragmentation
    out = np.empty((N, total_cols), dtype=Index)

    # Parallelize at the position level to ensure maximum CPU core saturation
    for n in nb.prange(N):
        # Local thread-safe array for the 8 calculated symmetry indices
        local_symmetry_indexes = np.empty(8, dtype=Index)

        for i in range(L):
            S = n_squares_arr[i]
            n_groups = n_groups_arr[i]
            group_size = group_size_arr[i]
            col_offset = col_offsets[i]
            num_planes = num_planes_arr[i]

            # --- LOOP FUSION 1: Integrated PEXT Simulation Layer ---
            for s in range(8):
                val_m = m_atrxs[n, s]
                val_o = o_atrxs[n, s]

                packed_m = BITBOARD_ZERO
                packed_o = BITBOARD_ZERO

                # Inline simulation of the _numba_pack_bb_kernel multi-plane logic
                for p in range(num_planes):
                    mask = pack_masks_3d[i, p]
                    shift = pack_shifts_3d[i, p]
                    packed_m |= (val_m & mask) >> shift
                    packed_o |= (val_o & mask) >> shift

                # --- LOOP FUSION 2: Ternary Base-3 Indexing Layer ---
                idx_m = INDEX_ZERO
                idx_o = INDEX_ZERO

                for b in range(S):
                    shift_val = bit_shifts_matrix[i, b]
                    p3 = powers_3[b]

                    bit_m = (packed_m >> shift_val) & BITBOARD_ONE
                    bit_o = (packed_o >> shift_val) & BITBOARD_ONE

                    idx_m += np.uint32(bit_m) * p3
                    idx_o += np.uint32(bit_o) * p3

                local_symmetry_indexes[s] = (INDEX_TWO * idx_o) + idx_m

            # --- LOOP FUSION 3: Structural Group Minimum Reduction Layer ---
            for g in range(n_groups):
                min_val = np.uint32(4294967295) # Initialize with UINT32_MAX
                start_idx = g * group_size

                for k in range(group_size):
                    sorted_s = idx_sort_matrix[i, start_idx + k]
                    val = local_symmetry_indexes[sorted_s]
                    if val < min_val:
                        min_val = val

                # Direct streaming write into the contiguous final output grid
                out[n, col_offset + g] = min_val

    return out
