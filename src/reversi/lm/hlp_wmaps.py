#
# hlp_wmaps.py
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

from __future__ import annotations

import hashlib
import numpy as np

from typing import TYPE_CHECKING
from pathlib import Path
from pydantic import validate_call, ConfigDict

from reversi.tools import binio

if TYPE_CHECKING:
    from reversi.lm.logistic_model import LMContext

__all__ = ['LMWMaps', 'hlp_wmaps_store_to_file', 'hlp_wmaps_load_from_file',
           'hlp_wmaps_compute', 'hlp_wmaps_is_cache_consistent']


class LMWMaps:
    """
    The computed Weight Maps (WMaps) of the model: the arrays mapping feature configurations to the
    weight vector W.

    The fields:
      hlp_indexes_checksum (str) — the hash of the Reversi Logistic Model indexes.
      cut_off (int) — the frequency cut-off threshold used to filter rare configurations.
      feature_w_ranges (np.ndarray, shape(F, 3)) — per feature, ordered by fid (feature index):
        [0] fallback: the w index used for the fallback (cut-off) configurations;
        [1] w_min: the first w index assigned to the feature (== fallback when fallback is not -1);
        [2] w_max: the last w index assigned to the feature.
      iwmap_feature_offset (np.ndarray, shape(F + 1,)) — the position of a feature in the iwmap
        array: iwmap_feature_offset[fid] is the position of configuration zero of the feature fid.
      iwmap (np.ndarray, shape(K,)) — for each possible configuration, the w index; -1 when the
        configuration is not found in the dataset. Given fid and feature_conf_id:
        iwmap[iwmap_feature_offset[fid] + feature_conf_id] returns the w index of (fid, feature_conf_id).
      wmap (np.ndarray, shape(W, 3)) — for each w index: the feature index, the configuration index,
        the configuration frequency (fid, feature_conf_id, feature_conf_frequency = wmap[w_index]).
        The -1 configuration identifies the weight assigned to the fallback configurations (one per
        feature, when required).
      wmap_fallback (np.ndarray, shape(F_cut, 3)) — the wmap entries excluded by the cut-off:
        [fid, feature_conf_id, feature_conf_frequency] (the configuration frequency within the dataset).
      w (np.ndarray, shape(W,)) — the model weights vector, initialized to zeros.

    Where: F = the count of features defined by the model (Intercept, Mobilities, Patterns);
    K = the count of all feature configurations (K = sum(f.n_configurations for f in features));
    W = the count of all model weights; F_cut = the count of all cut-off configurations.
    """

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def __init__(self,
                 hlp_indexes_checksum: str, cut_off: int, feature_w_ranges: np.ndarray,
                 iwmap_feature_offset: np.ndarray, iwmap: np.ndarray, wmap: np.ndarray,
                 wmap_fallback: np.ndarray, w: np.ndarray):
        """
        Initialize the WMaps data object from the computed arrays (all stored by reference).

        Args:
            hlp_indexes_checksum (str): the hash of the Reversi Logistic Model indexes.
            cut_off (int): the frequency cut-off threshold used to filter rare configurations.
            feature_w_ranges (np.ndarray): the (F, 3) per-feature [fallback, w_min, w_max] indices.
            iwmap_feature_offset (np.ndarray): the (F + 1,) per-feature position in the iwmap array.
            iwmap (np.ndarray): the (K,) configuration -> w-index map (-1 when the configuration is
                unseen).
            wmap (np.ndarray): the (W, 3) [fid, config_id_or_-1, frequency] rows.
            wmap_fallback (np.ndarray): the (F_cut, 3) cut-off-excluded [fid, config_id, frequency]
                rows.
            w (np.ndarray): the (W,) model weights vector.
        """
        self.hlp_indexes_checksum = hlp_indexes_checksum
        self.cut_off = cut_off
        self.feature_w_ranges = feature_w_ranges
        self.iwmap_feature_offset = iwmap_feature_offset
        self.iwmap = iwmap
        self.wmap = wmap
        self.wmap_fallback = wmap_fallback
        self.w = w

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def compute_sha3_256_hash(self) -> str:
        """
        Compute the sha3_256 hash of the 6 WMaps ARRAYS in declaration order.

        The two metadata scalars (hlp_indexes_checksum, cut_off) are NOT hashed. This is the
        duck-typed data-checksum hook the cache_manager invokes (its 3rd return element).

        Returns:
            str: the sha3_256 hex digest of the 6 array tobytes.
        """
        hasher = hashlib.sha3_256()
        hasher.update(self.feature_w_ranges.tobytes())
        hasher.update(self.iwmap_feature_offset.tobytes())
        hasher.update(self.iwmap.tobytes())
        hasher.update(self.wmap.tobytes())
        hasher.update(self.wmap_fallback.tobytes())
        hasher.update(self.w.tobytes())
        sha3_256_hash = hasher.hexdigest()
        return sha3_256_hash


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def hlp_wmaps_store_to_file(wmaps: LMWMaps, filename: str | Path, compressed: bool = True) -> None:
    """
    Save the WMaps instance to a binary file: the header (the "LMWMaps binary data file" description
    + the format version 1) + the checksum string + the i32 cut_off + the 6 arrays in declaration
    order.

    LZ4 whole-file compression by default.

    Args:
        wmaps (LMWMaps): the WMaps instance to store.
        filename (str | Path): the target file.
        compressed (bool): the LZ4 whole-file compression (default True).
    """
    filename = Path(filename)
    description = "LMWMaps binary data file"
    version = 1

    with binio.BinaryWriter(filename, compressed=compressed) as w:
        w.write_header(description, version)
        w.write_string(wmaps.hlp_indexes_checksum)
        w.write_i32(wmaps.cut_off)
        w.write_array(wmaps.feature_w_ranges)
        w.write_array(wmaps.iwmap_feature_offset)
        w.write_array(wmaps.iwmap)
        w.write_array(wmaps.wmap)
        w.write_array(wmaps.wmap_fallback)
        w.write_array(wmaps.w)


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def hlp_wmaps_load_from_file(filename: str | Path, checksum: bool = True,
                             compressed: bool = True) -> LMWMaps:
    """
    Load a WMaps instance from a binary file: the sidecar check (when checksum) + the header
    description / version guard + the ordered block reads, returning a fresh object.

    LZ4 whole-file compression by default.

    Args:
        filename (str | Path): the cache file.
        checksum (bool): verify the .SHA3-256 sidecar first (default True).
        compressed (bool): the LZ4 whole-file compression (default True).

    Returns:
        LMWMaps: the reconstructed WMaps instance.

    Raises:
        RuntimeError: the checksum mismatch, the foreign header description, the foreign format
            version, or a truncated file.
    """
    if checksum:
        if not binio.verify_sha3_256_sidecar(filename):
            raise RuntimeError("The checksum file signature doesn't match with current file.")

    expected_description = "LMWMaps binary data file"
    expected_version = 1

    with binio.BinaryReader(filename, compressed=compressed) as r:
        description, version = r.read_header()
        if description != expected_description:
            raise RuntimeError(f"The file is not a proper {expected_description}.")
        if version != expected_version:
            raise RuntimeError(f"File version mismatch: found {version}, expected {expected_version}")

        hlp_indexes_checksum = r.read_string()
        cut_off = r.read_i32()

        feature_w_ranges = r.read_array()
        iwmap_feature_offset = r.read_array()
        iwmap = r.read_array()
        wmap = r.read_array()
        wmap_fallback = r.read_array()
        w = r.read_array()

    return LMWMaps(
        hlp_indexes_checksum=hlp_indexes_checksum, cut_off=cut_off,
        feature_w_ranges=feature_w_ranges, iwmap_feature_offset=iwmap_feature_offset,
        iwmap=iwmap, wmap=wmap, wmap_fallback=wmap_fallback, w=w)


#: Here validation is not possible, it brings in a convoluted issue with circular imports.
def hlp_wmaps_compute(ctx: "LMContext") -> LMWMaps:
    """
    Compute the WMaps from the feature frequencies and the cut-off threshold.

    The input pindexes matrix is dense by contract: every cell holds a valid configuration index in
    0..n_configurations - 1 (the indexes are unsigned and never -1), so the -1 'unseen
    configuration' sentinel can only appear in the OUTPUT iwmap. Per feature: the configurations
    below the cut-off frequency share the feature's single fallback weight (the -1 config_id row,
    first, with the summed frequency), the above-cutoff configurations get contiguous weight
    indices, and the weights vector starts at zero (length = the total count of assigned weights).

    Args:
        ctx (LMContext): the LMContext (the pindexes from the INDEXES level, the feature_set, the
            frequency_cut_off config).

    Returns:
        LMWMaps: the fresh object (the 6 arrays + the 2 metadata scalars).
    """
    cut_off = ctx.cfg.stat_model.frequency_cut_off
    features = ctx.feature_set.features

    f_num_configurations = np.array([f.n_configurations for f in features], dtype=np.uint32)
    iwmap_feature_offset = np.zeros(len(features) + 1, dtype=np.uint32)
    iwmap_feature_offset[1:] = np.cumsum(f_num_configurations)

    K = iwmap_feature_offset[-1]

    iwmap = np.full(K, -1, dtype=np.int64)
    pindexes = ctx.hlp_indexes.indexes
    next_w = 0
    f_w_ranges = []
    wmap_blocks = []
    fallback_data = []

    col_offset = 0
    for fid, f in enumerate(features):
        cols = list(range(col_offset, col_offset + f.n_instances))
        # Ellipsis: the feature columns are the LAST axis of the pindexes
        # matrix (a 1-D position batch gives the classic (N, I) layout;
        # an N-D batch keeps the same last-axis column layout).
        f_pindexes = pindexes[..., cols]
        flat_f_pindexes = f_pindexes.ravel()

        unique_values, counts = np.unique(flat_f_pindexes, return_counts=True)
        stats = np.column_stack((unique_values, counts))

        mask = stats[:, 1] < cut_off
        stats_filtered_below = stats[mask]

        w_indices = np.empty(len(stats), dtype=np.int64)
        if len(stats_filtered_below) > 0:
            fallback = next_w
            w_indices[mask] = fallback
            next_w += 1
            fallback_feature_configuration_is_present = True
        else:
            fallback = -1
            fallback_feature_configuration_is_present = False

        n_above = (~mask).sum()
        if n_above > 0:
            w_indices[~mask] = np.arange(next_w, next_w + n_above)
            next_w += n_above

        stats = np.column_stack((stats, w_indices))

        f_iwmap = iwmap[iwmap_feature_offset[fid]:iwmap_feature_offset[fid + 1]]
        f_iwmap[stats[:, 0].astype(np.int64)] = stats[:, 2]

        w_min = w_indices.min() if len(w_indices) > 0 else -1
        w_max = w_indices.max() if len(w_indices) > 0 else -1
        f_w_ranges.append({
            'fallback': fallback,
            'w_min': w_min,
            'w_max': w_max
        })

        num_w_feature = w_max - w_min + 1
        feature_w_mapping = np.empty((num_w_feature, 3), dtype=np.int64)
        feature_w_mapping[:, 0] = fid
        feature_w_mapping[:, 1] = -1

        if fallback_feature_configuration_is_present:
            fallback_freq = stats_filtered_below[:, 1].sum()
            fallback_rel_idx = fallback - w_min
            feature_w_mapping[fallback_rel_idx, 2] = fallback_freq

            for row in stats_filtered_below:
                fallback_data.append([fid, row[0], row[1]])

        above_mask = ~mask
        if above_mask.any():
            w_above = stats[above_mask, 2]
            config_above = stats[above_mask, 0]
            freq_above = stats[above_mask, 1]
            relative_indices = (w_above - w_min).astype(np.int64)
            feature_w_mapping[relative_indices, 1] = config_above
            feature_w_mapping[relative_indices, 2] = freq_above
        wmap_blocks.append(feature_w_mapping)

        col_offset += f.n_instances

    wmap = np.vstack(wmap_blocks)
    fallback_details_table = np.array(fallback_data, dtype=np.int64)
    if fallback_details_table.size == 0:
        fallback_details_table = fallback_details_table.reshape(0, 3)

    feature_w_ranges_arr = np.array([[m['fallback'], m['w_min'], m['w_max']] for m in f_w_ranges],
                                    dtype=np.int64)
    w = np.zeros(next_w, dtype=np.float32)

    return LMWMaps(
        hlp_indexes_checksum=ctx.hlp_indexes_checksum, cut_off=cut_off,
        feature_w_ranges=feature_w_ranges_arr, iwmap_feature_offset=iwmap_feature_offset,
        iwmap=iwmap, wmap=wmap, wmap_fallback=fallback_details_table, w=w)


def hlp_wmaps_is_cache_consistent(ctx: "LMContext", wmaps: LMWMaps) -> bool:
    """
    Check the WMaps cache consistency: the cached metadata vs the live one.

    The PURE 2-field compare (no DB, no recompute) — the cache_manager validate_fn.

    Args:
        ctx (LMContext): the LMContext (the live hlp_indexes_checksum + the frequency_cut_off).
        wmaps (LMWMaps): the cached WMaps instance.

    Returns:
        bool: True when both the hlp_indexes_checksum and the cut_off match.
    """
    is_hash_consistent = wmaps.hlp_indexes_checksum == ctx.hlp_indexes_checksum
    is_cut_off_consistent = wmaps.cut_off == ctx.cfg.stat_model.frequency_cut_off
    return is_hash_consistent and is_cut_off_consistent
