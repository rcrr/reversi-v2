#
# hlp_su_analysis.py
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
The SU analysis LOGIC (the hlp of the SU_ANALYSIS worker): the
streaming frequency accumulators (the marginal + the joint, the
phase-1 data plane), the corpus generator (the random_game
play-path engine, phase 1 — the expensive part), the binio cache
I/O (the header + the signature block + the marginal + the joint)
+ the consistency signature (the feature_set hash + the spec + the
pairs) + the SU statistics kernels (the entropy / the MI / the SU /
the dispersion / the never-observed audit) + the statistics
(phase 2: the SU pairs, the TXT report + the optional CSV). NO DB:
the corpus is the level's own, the random_game play-path engine.
The worker (wrk_su_analysis.py) is the orchestration skeleton: the
enable no-op, the cache_manager flow, the ctx publication.
"""

from __future__ import annotations

import csv
import hashlib
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from typing import TYPE_CHECKING, TypedDict

import numpy as np
import numpy.typing as npt

from pydantic import ConfigDict, validate_call

from reversi.board import initial_game_position
from reversi.feature import FeatureSet
from reversi.pattern import IndexArray
from reversi.random_game import random_game_play_path
from reversi.tools import binio
from reversi.tools.binio import BinaryReader, BinaryWriter
from reversi.tools.prng import MT19937
from reversi.tools.state_machine import Relevance
if TYPE_CHECKING:
    from reversi.lm.logistic_model import LMContext


# The 5 FLOW functions (the wrk/hlp boundary) + the SuTables
# tables type. The consistency signature is INTERNAL (the
# _signature private): it feeds the compute + the is_cache_consistent,
# it is not part of the module API (only the cross-module names are
# exposed — the test / the probe reach the private names directly).
__all__ = ['SuTables',
           'hlp_su_analysis_compute',
           'hlp_su_analysis_store_to_file',
           'hlp_su_analysis_load_from_file',
           'hlp_su_analysis_is_cache_consistent',
           'hlp_su_analysis_statistics']

# The batch size CEILING (the cache signature carries the generator
# version, not this value). The actual size is min(this, the corpus
# size), because the lanes beyond the corpus are pure overhead; the
# value is the measured sweet spot. NOTE: the wave size is part of
# the generator BEHAVIOUR (the per-step draw batch size shifts the
# MT19937 stream — the corpora are NOT identical across wave
# sizes), so a wave-size bump always comes with the
# _GENERATOR_VERSION bump.
_WAVE_SIZE = 3_000_000
# The corpus-generator version, part of the cache signature (the
# random_game play-path corpus, the 3e6-lane waves). A version
# bump invalidates every cached corpus, which is exactly the
# point: the signature exists so that a change of the generator's
# behaviour can never be reused silently.
_GENERATOR_VERSION = "su-corpus-5"
_PRNG_VERSION = "mt19937-64"
# The cache file format: the file description + the format VERSION.
# A format change bumps the version (the header rejects the old
# file) — orthogonal to the DATA signature (the feature_set hash +
# the spec + the pairs), which governs consistency, not format.
_CACHE_DESCRIPTION = "SU_ANALYSIS corpus cache"
_CACHE_VERSION = 1
# The SU description (the report's Section C preamble): the
# normalized shared information — the bias-compensated correlation.
_SU_DESCRIPTION = (
    "It evaluates the normalized relationship, dependency, "
    "or shared variance between variables,",
    "compensating for the inherent mathematical bias found "
    "in raw information gain.",
)
# The SU range legend (the report's interpretation key, the Section C
# preamble after the description): the SU value bands + their
# meaning. The SU = 2·I / (H_u + H_v) in [0, 1] is the normalized
# shared information — the bias-compensated correlation.
_SU_LEGEND = (
    "SU        : Meaning",
    "0.0       : Perfect orthogonality",
    "0.0 - 0.1 : Excellent independence",
    "0.1 - 0.3 : Moderate correlation",
    "0.3 - 0.5 : Strong correlation",
    "over 0.5  : Very strong correlation",
)
# The Section A KPI legend (the per-sub-variable statistics key; the
# theoretical configuration space = n_unique_configs for a pattern /
# the value range for a mobility — the denominator of the coverage /
# the never-observed audit).
_KPI_LEGEND = (
    "K_obs    : distinct configurations observed (of the theoretical "
    "space)",
    "H        : Shannon entropy of the observed distribution (bits)",
    "H_norm   : H / log2(K_obs) in [0,1] — 1.0 = uniform over the observed",
    "coverage : observed / theoretical — the ratio of observed to "
    "total theoretical configurations (some are unreachable by the "
    "game's rules)",
    "never-obs: theoretical − observed (theoretical configurations "
    "never seen)",
)


# ---------------------------------------------------------------------
# The frequency accumulators (the phase-1 data plane): the
# streaming per-sub-variable (code -> count) marginal + the joint
# accumulation over the corpus. The analysis unit is the
# (feature, instance) sub-variable = ONE design-index column (the
# design-matrix unit, the unit the weights live on): each pattern
# instance is its own categorical variable (the code a single
# uint32 in [0, n_conf) — no packing, no overflow), the mobility a
# single column.
# ---------------------------------------------------------------------

#: The dense-bincount threshold: a sub-variable with
#: n_conf <= this uses the DENSE histogram (all the current
#: sub-variables, the max is 59049); above it, the UNIQUE-MERGE
#: dict (the wider code spaces).
_DENSE_THRESHOLD = 1_000_000


#: The marginal table shape (the _MarginalAccumulator.result()
#: output, the binio marginal block, the statistics input): the
#: per-sub-variable list (the expanded block order) of
#: (name, instance_idx, n_conf, codes, counts) — the observed
#: support, the codes uint32, the counts int64.
_MarginalTable = list[tuple[str, int, int,
                            npt.NDArray[np.uint32],
                            npt.NDArray[np.int64]]]


#: The joint table shape (the _JointAccumulator.result() output,
#: the binio joint block, the _su_values input): the per-pair list
#: of (name_i, name_j, per_instance) — per_instance the
#: { (inst_i, inst_j): (codes_i, codes_j, counts) } observed joint,
#: the codes uint32, the counts int64. (None at the tables level
#: when no pairs are configured — the _JointAccumulator is not
#: built; the binio joint block carries the presence flag.)
_JointTable = list[tuple[str, str,
                         dict[tuple[int, int],
                              tuple[npt.NDArray[np.uint32],
                                    npt.NDArray[np.uint32],
                                    npt.NDArray[np.int64]]]]]


class SuTables(TypedDict):
    """
    The tables dict (the PUBLIC type): the output of
    hlp_su_analysis_compute, the input of hlp_su_analysis_store_to_file
    (the @validate_call deep-validates it: the structure + the array
    dtypes), the output of hlp_su_analysis_load_from_file.
    'signature': the consistency signature block (the plain dict),
    'marginal':  the _MarginalTable,
    'joint':     the _JointTable, or None (no pairs configured).
    """
    signature: dict
    marginal: _MarginalTable
    joint: _JointTable | None


class _MarginalAccumulator:
    """
    The streaming marginal frequency accumulator: per
    sub-variable (the (feature, instance) column), the
    code -> count over the fed positions. Feed it the corpus in
    chunks via add (the index-matrix slices from
    fset.compute_indexes); read the result with result.

    Each sub-variable is ONE design-index column: the code is a
    single uint32 in [0, n_conf) (no packing, no overflow).

    The accumulator is POOLED over all fed positions (the corpus
    is a single-ec population — arrested at the model's ec — so
    there is no per-ec split here).
    """

    def __init__(self, fset: FeatureSet) -> None:
        """
        Args:
          fset: the FeatureSet (the feature_blocks provider — the
                per-feature blocks come from its feature_blocks
                property, the (name, col_start, col_end, n_conf,
                n_inst) over the non-intercept features, each
                expanding to n_inst sub-variables, one per
                instance column).

        State: the per-sub-variable storage (the dense histogram
        or the unique-merge dict, per _DENSE_THRESHOLD) + the
        n_positions counter (0).
        """
        self.fset = fset
        # Expand the feature blocks into the per-instance sub-
        # variables: (name, instance_idx, col, n_conf).
        self.subvars: list = []
        for (name, c0, c1, n_conf, n_inst) in fset.feature_blocks:
            for i in range(n_inst):
                self.subvars.append((name, i, c0 + i, n_conf))
        self._dense: list = []
        self._sparse: list = []
        for (name, i, col, n_conf) in self.subvars:
            if n_conf <= _DENSE_THRESHOLD:
                self._dense.append(np.zeros(n_conf, dtype=np.int64))
                self._sparse.append(None)
            else:
                self._dense.append(None)
                self._sparse.append({})
        self.n_positions: int = 0

    def add(self, idx: IndexArray) -> None:
        """
        Accumulate one chunk of corpus INDEXES (the uint32
        (N, I) index matrix from fset.compute_indexes — the same
        matrix the joint accumulator is fed, the compute loop
        computes it once per wave). An empty chunk is a no-op.

        State: the per-sub-variable counts + n_positions.
        """
        n = int(idx.shape[0])
        if n == 0:
            return
        for sidx, (name, i, col, n_conf) in enumerate(self.subvars):
            codes = idx[:, col]
            if self._dense[sidx] is not None:
                self._dense[sidx] += np.bincount(
                    codes.astype(np.intp), minlength=n_conf)
            else:
                u, cnt = np.unique(codes, return_counts=True)
                d = self._sparse[sidx]
                for k, c in zip(u.tolist(), cnt):
                    d[k] = d.get(k, 0) + int(c)
        self.n_positions += n

    def result(self) -> _MarginalTable:
        """
        The per-sub-variable marginal: a list (over sub-
        variables, in the expanded block order) of
        (name, instance_idx, n_conf, codes, counts) — the
        OBSERVED codes (the non-zero support) as uint32, the
        counts as int64. len(codes) is the K_obs of the sub-
        variable; the never-observed count is n_conf - K_obs.
        """
        out = []
        for sidx, (name, i, col, n_conf) in enumerate(self.subvars):
            if self._dense[sidx] is not None:
                cnt = self._dense[sidx]
                nz = cnt > 0
                codes = np.nonzero(nz)[0].astype(np.uint32)
                out.append((name, i, n_conf, codes,
                            cnt[nz].astype(np.int64)))
            else:
                items = sorted(self._sparse[sidx].items())
                codes = np.array([k for k, _ in items],
                                 dtype=np.uint32)
                c = np.array([v for _, v in items], dtype=np.int64)
                out.append((name, i, n_conf, codes, c))
        return out


def _joint_cell_merge(joints, pi, ii, jj, bi, bj, idx) -> None:
    """
    Fold one chunk of corpus INDEXES into ONE joint cell's
    (K, C) storage: the chunk's unique output is merged into the
    already-observed keys (the matched counts accumulate, the new
    keys are appended and the (K, C) re-sorted — the sorted-K
    invariant keeps the next chunk's searchsorted valid). ONE
    cell per call: the cells are independent (their registry
    entries never cross), which is what makes the add's thread
    pool safe.

    Args:
      joints: the per-pair cell registries (the
        _JointAccumulator.joints list).
      pi:     the pair index into joints.
      ii/jj:  the instance pair = the cell key (ii, jj).
      bi/bj:  the two feature blocks, the (name, col_start,
        col_end, n_conf, n_inst) tuples.
      idx:    the chunk's index matrix (read-only).

    State: joints[pi][(ii, jj)] is replaced by the merged
    (K, C); nothing else is touched.
    """
    ncj = np.uint64(bj[3])
    ci = idx[:, bi[1] + ii].astype(np.uint64)
    cj = idx[:, bj[1] + jj].astype(np.uint64)
    key = ci * ncj + cj
    u, cnt = np.unique(key, return_counts=True)
    K, C = joints[pi][(ii, jj)]
    if K.size == 0:
        # The first wave: the unique output IS the (sorted)
        # support.
        K = u
        C = cnt.astype(np.int64)
    else:
        i = np.searchsorted(K, u)
        # The clip makes the compare safe for the insert-
        # past-the-end tail (those keys can only be NEW: a key
        # larger than K[-1] never matches).
        i = np.clip(i, 0, K.size - 1)
        m = K[i] == u
        if m.any():
            np.add.at(C, i[m], cnt[m])
        nu = u[~m]
        if nu.size:
            K = np.concatenate([K, nu])
            C = np.concatenate([C, cnt[~m]])
            o = np.argsort(K, kind='stable')
            K, C = K[o], C[o]
    joints[pi][(ii, jj)] = (K, C)


class _JointAccumulator:
    """
    The streaming joint frequency accumulator:
    per REQUESTED su pair (F_i, F_j) and per (instance_i,
    instance_j) in the pair, the (code_i, code_j) -> count over
    the fed positions — the instance×instance level (the joint
    matrix). The joint is SPARSE (the code_i x code_j space is
    too large for the dense). The key is the packed u64
    (code_i * n_conf_j + code_j); result unpacks the
    (code_i, code_j).

    The same-feature pair (F, F) is allowed: the diagonal cell
    (the variable with itself) is NOT BUILT — it is the marginal
    itself (the redundant (u, u) joint); the registry holds the
    off-diagonal only (the D8 orientations of the same mask, the
    anisotropy measure).

    The per-cell merges are independent (each touches only its
    own registry entry) and the add runs them on a thread pool;
    a cell's result is a pure function of its own (K, C) history
    + the chunk's column pair (deterministic).
    """

    def __init__(self, fset: FeatureSet,
                 su_pairs: list[tuple[str, str]]) -> None:
        """
        Args:
          fset:     the FeatureSet (the feature_blocks provider).
          su_pairs: the REQUESTED pairs, a list of
                    (feature_i, feature_j) name tuples (the
                    canonical form; the same-feature (F, F) is
                    allowed).

        State: the per-pair cell registry (the (K, C) per
        off-diagonal cell — the same-feature diagonal cells are
        absent) + the per-pair meta + n_positions (0).
        """
        self.fset = fset
        self._block = {b[0]: b for b in fset.feature_blocks}
        self.pairs = list(su_pairs)
        # Per pair: the { (inst_i, inst_j): (K, C) } cell registry
        # + the per-pair meta (ni, nj, block_i, block_j). The
        # same-feature DIAGONAL cell (ii == jj) is NOT BUILT — it
        # is the marginal itself (the (u, u) joint IS the
        # marginal of u), the _su_values omits it (the SU = 1
        # lock) and nothing downstream consumes it. The registry
        # is the single source of truth: the add iterates its
        # keys.
        self.joints: list = []
        self._meta: list = []
        for (ni, nj) in self.pairs:
            bi = self._block[ni]
            bj = self._block[nj]
            d = {}
            for ii in range(bi[4]):
                for jj in range(bj[4]):
                    if ni == nj and ii == jj:
                        continue  # The diagonal cell: not built.
                    # The per-cell storage: the OBSERVED keys
                    # (u64, sorted) + the counts (int64) — empty
                    # until the first chunk.
                    d[(ii, jj)] = (np.zeros(0, dtype=np.uint64),
                                   np.zeros(0, dtype=np.int64))
            self.joints.append(d)
            self._meta.append((ni, nj, bi, bj))
        self.n_positions: int = 0

    def add(self, idx: IndexArray) -> None:
        """
        Accumulate one chunk of corpus INDEXES (the uint32
        (N, I) index matrix from fset.compute_indexes — the same
        matrix the marginal accumulator is fed, the compute loop
        computes it once per wave). The per-cell merges run on a
        thread pool (the single-cell case stays inline); the idx
        is read-only during the call. An empty chunk is a no-op.

        State: the cell registry (per cell, the merged (K, C)) +
        n_positions.
        """
        n = int(idx.shape[0])
        if n == 0:
            return
        # The cell work list, from the registry (the diagonal
        # cells are absent).
        cells = [(pi, ii, jj, bi, bj)
                 for pi, (_ni, _nj, bi, bj) in enumerate(self._meta)
                 for (ii, jj) in self.joints[pi]]
        if len(cells) > 1:
            with ThreadPoolExecutor(
                max_workers=min(len(cells), os.cpu_count() or 4)
            ) as pool:
                list(pool.map(
                    lambda t: _joint_cell_merge(self.joints, t[0], t[1],
                                                t[2], t[3], t[4], idx),
                    cells))
        else:
            for (pi, ii, jj, bi, bj) in cells:
                _joint_cell_merge(self.joints, pi, ii, jj, bi, bj, idx)
        self.n_positions += n

    def result(self) -> _JointTable:
        """
        The per-pair joint: a list (over pairs, in pair order)
        of (name_i, name_j, per_instance) — per_instance a dict
        { (inst_i, inst_j): (codes_i, codes_j, counts) } the
        OBSERVED joint (the non-zero support), the codes
        unpacked as uint32, the counts as int64. The same-feature
        DIAGONAL cells are ABSENT (not built — they are the
        marginal itself).
        """
        out = []
        for pi, (ni, nj, bi, bj) in enumerate(self._meta):
            ncj = np.uint64(bj[3])
            pd = {}
            for (ii, jj) in self.joints[pi]:
                # The (K, C) ARE the observed joint (the sorted
                # keys + the counts) — no sort, no dict.
                K, C = self.joints[pi][(ii, jj)]
                codes_i = (K // ncj).astype(np.uint32)
                codes_j = (K % ncj).astype(np.uint32)
                cnt = C
                pd[(ii, jj)] = (codes_i, codes_j, cnt)
            out.append((ni, nj, pd))
        return out


def _signature(ctx: "LMContext") -> dict:
    """The cache consistency signature (INTERNAL — it feeds the
    compute + the is_cache_consistent): the feature_set hash (the
    FeatureSet DOMAIN hash — the set's unique identifier over its
    semantic content) + the generation spec (the seed, the
    total_positions, the ec, the generator version, the PRNG
    version) + the su_pairs list (the configured order)."""
    corpus = ctx.cfg.su_analysis.corpus
    return {
        'feature_set_hash': ctx.feature_set.hash,
        'seed': corpus.seed,
        'total_positions': corpus.total_positions,
        'ec': ctx.cfg.empty_count,
        'generator_version': _GENERATOR_VERSION,
        'prng_version': _PRNG_VERSION,
        'su_pairs': [list(p) for p in ctx.cfg.su_analysis.su_pairs],
    }


#: Here validation is not possible: it would bring in a circular
#: import (the LMContext facade, the hlp_design_matrix idiom).
def hlp_su_analysis_compute(ctx: "LMContext") -> dict:
    """Phase 1 — the corpus (the expensive part): generates the
    SU-analysis corpus with the random_game play-path engine (the
    batches of fresh lanes from the canonical start, the PRNG
    seed, the ec arrest) and streams it to the accumulators (the
    marginal + the joint for the requested pairs, fed per batch —
    the corpus never materializes in RAM). The harvested lanes
    are the batch lanes at EXACTLY the target ec (the double-pass
    game-over lanes are dropped, the quota filled by the next
    batch); the slots provenance is not carried. Each wave's
    index matrix (fset.compute_indexes over the harvested lanes)
    is computed once in the loop and fed to BOTH accumulators.

    Args:
      ctx: the LMContext (the cfg.su_analysis corpus spec + the
        feature_set — the FEATURES phase done).

    Returns:
      the tables dict: the signature + the marginal + the joint
      (None when no pairs are configured).

    State: none persistent (the accumulators are local); the PRNG
    is fresh (the corpus seed).
    """
    cfg_fa = ctx.cfg.su_analysis
    fset = ctx.feature_set
    corpus = cfg_fa.corpus
    ctx.log_event(Relevance.INFO,
                  f"Generating the SU_ANALYSIS corpus: "
                  f"[TOTAL: {corpus.total_positions:,}], [EC: {ctx.cfg.empty_count}], "
                  f"[SEED: {corpus.seed}], the batch tier.")
    total = corpus.total_positions
    ec = ctx.cfg.empty_count
    prng = MT19937(corpus.seed)
    igp = initial_game_position()
    marg = _MarginalAccumulator(fset)
    joint = _JointAccumulator(fset, cfg_fa.su_pairs) \
        if cfg_fa.su_pairs else None
    harvested = waves = dead = 0
    while harvested < total:
        # The batch size is capped by the remaining quota: a
        # smaller corpus needs fewer lanes, and the lanes beyond
        # it only pay allocation + glue. The batch is the n
        # copies of the canonical start (the np.full of the
        # structured scalar, the position language, D-296).
        n = min(_WAVE_SIZE, total - harvested)
        batch = np.full(n, igp)
        final, ec_arr = random_game_play_path(batch, ec, prng)
        keep = ec_arr == ec
        dead += int((~keep).sum())
        # The wave's index matrix is computed ONCE here and fed to
        # BOTH accumulators.
        idx = fset.compute_indexes(final[keep])
        marg.add(idx)
        if joint is not None:
            joint.add(idx)
        harvested += int(keep.sum())
        waves += 1
    ctx.log_event(Relevance.INFO,
                  f"Corpus generated: [HARVESTED: {harvested:,}], "
                  f"[WAVES: {waves}], [DEAD: {dead:,}].")
    return {'signature': _signature(ctx),
            'marginal': marg.result(),
            'joint': joint.result() if joint is not None else None}


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def hlp_su_analysis_store_to_file(data: SuTables,
                                  filename: str | Path) -> None:
    """Write the tables dict to the binio cache file (the header +
    the signature block + the marginal + the joint, LZ4-
    compressed; the .SHA3-256 sidecar is owned by the
    cache_manager, not written here).

    Args:
      data:     the SuTables (the @validate_call deep-validates it
                before the body runs: the structure + the array
                dtypes).
      filename: the target file (str or Path; created /
                overwritten).

    State: writes the file.
    """
    with binio.BinaryWriter(filename, compressed=True,
                            checksum=False) as w:
        w.write_header(_CACHE_DESCRIPTION, _CACHE_VERSION)
        _write_signature(w, data['signature'])
        _write_marginal(w, data['marginal'])
        _write_joint(w, data['joint'])


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def hlp_su_analysis_load_from_file(filename: str | Path,
                                   checksum: bool = True) -> dict:
    """Read the tables dict from the binio cache file: the sidecar
    check (when checksum) + the header description / version guard
    + the ordered block reads. The cache_manager ALREADY verifies
    the sidecar (its step 2), so the worker passes checksum=False
    (no double hash).

    Args:
      filename: the cache file (str or Path).
      checksum: verify the .SHA3-256 sidecar first (default True;
                the worker passes False).

    Returns:
      the tables dict {'signature', 'marginal', 'joint'}.

    Raises:
      RuntimeError: the checksum mismatch, the foreign header
      description, the foreign format version, or a truncated
      file (the manager's R2 path then deletes the cache and
      recomputes).
    """
    if checksum and not binio.verify_sha3_256_sidecar(filename):
        raise RuntimeError("Checksum mismatch.")
    with binio.BinaryReader(filename, compressed=True) as r:
        description, version = r.read_header()
        if description != _CACHE_DESCRIPTION:
            raise RuntimeError(f"Wrong file format: {description}")
        if version != _CACHE_VERSION:
            raise RuntimeError(f"Wrong file version: {version}")
        signature = _read_signature(r)
        marginal = _read_marginal(r)
        joint = _read_joint(r)
    return {'signature': signature, 'marginal': marginal, 'joint': joint}


def _write_signature(w: BinaryWriter, sig: dict) -> None:
    """The signature block: the feature_set hash + the 5 spec fields +
    the su_pairs (the configured order, the 2-tuples)."""
    w.write_string(sig['feature_set_hash'])
    w.write_u64(sig['seed'])
    w.write_u64(sig['total_positions'])
    w.write_u64(sig['ec'])
    w.write_string(sig['generator_version'])
    w.write_string(sig['prng_version'])
    w.write_u32(len(sig['su_pairs']))
    for pair in sig['su_pairs']:
        w.write_string(pair[0])
        w.write_string(pair[1])


def _read_signature(r: BinaryReader) -> dict:
    """The signature block read-back (the plain ints, the [str, str]
    pairs — the live signature shape)."""
    signature = {
        'feature_set_hash': r.read_string(),
        'seed': int(r.read_u64()),
        'total_positions': int(r.read_u64()),
        'ec': int(r.read_u64()),
        'generator_version': r.read_string(),
        'prng_version': r.read_string(),
    }
    n_pairs = int(r.read_u32())
    signature['su_pairs'] = [[r.read_string(), r.read_string()]
                             for _ in range(n_pairs)]
    return signature


def _write_marginal(w: BinaryWriter, marginal: _MarginalTable) -> None:
    """The marginal block: the (name, instance, n_conf) + the codes +
    the counts arrays (the observed support)."""
    w.write_u32(len(marginal))
    for (name, i, n_conf, codes, counts) in marginal:
        w.write_string(name)
        w.write_u32(i)
        w.write_u64(n_conf)
        w.write_array(codes)
        w.write_array(counts)


def _read_marginal(r: BinaryReader) -> _MarginalTable:
    n = int(r.read_u32())
    marginal = []
    for _ in range(n):
        marginal.append((r.read_string(), int(r.read_u32()),
                         int(r.read_u64()), r.read_array(), r.read_array()))
    return marginal


def _write_joint(w: BinaryWriter, joint: _JointTable | None) -> None:
    """The joint block: the presence flag + the pairs; the
    per-instance entries in the SORTED (ii, jj) order (the
    deterministic layout)."""
    if joint is None:
        w.write_u8(0)
        return
    w.write_u8(1)
    w.write_u32(len(joint))
    for (name_i, name_j, per_instance) in joint:
        w.write_string(name_i)
        w.write_string(name_j)
        w.write_u32(len(per_instance))
        for (ii, jj) in sorted(per_instance):
            codes_i, codes_j, counts = per_instance[(ii, jj)]
            w.write_u32(ii)
            w.write_u32(jj)
            w.write_array(codes_i)
            w.write_array(codes_j)
            w.write_array(counts)


def _read_joint(r: BinaryReader) -> _JointTable | None:
    """The joint block read-back (None when the flag is 0)."""
    if int(r.read_u8()) == 0:
        return None
    n = int(r.read_u32())
    out = []
    for _ in range(n):
        name_i = r.read_string()
        name_j = r.read_string()
        k = int(r.read_u32())
        per_instance = {}
        for _ in range(k):
            ii = int(r.read_u32())
            jj = int(r.read_u32())
            per_instance[(ii, jj)] = (r.read_array(), r.read_array(),
                                      r.read_array())
        out.append((name_i, name_j, per_instance))
    return out


#: Here validation is not possible: it would bring in a circular
#: import (the LMContext facade, the hlp_design_matrix idiom).
def hlp_su_analysis_is_cache_consistent(ctx: "LMContext",
                                        cached: dict) -> bool:
    """The cache consistency: the cached signature vs the live
    signature (the feature_set hash + the spec + the pairs)."""
    live = _signature(ctx)
    consistent = cached.get('signature', {}) == live
    ctx.log_event(Relevance.DEBUG,
                  f"SU_ANALYSIS cache consistent: {consistent}.")
    if not consistent:
        ctx.log_event(Relevance.DEBUG,
                      f"  cached: {cached.get('signature')}\n"
                      f"  live:   {live}")
    return consistent


# ---------------------------------------------------------------------
# The SU statistics kernels (the phase-2 pure math over the
# frequency tables): the entropy / the mutual information / the
# SU / the dispersion / the never-observed audit.
# ---------------------------------------------------------------------

def _entropy(counts: np.ndarray) -> float:
    """
    The Shannon entropy H in bits, from the count array (the
    marginal or the joint). The 0-log-0 convention: the zero
    counts contribute 0. The empty / the all-zero counts -> 0.

    Args:
      counts: the count array (any shape; the non-zero entries
        are the observed support).
    """
    c = np.asarray(counts, dtype=np.float64).ravel()
    c = c[c > 0]
    n = c.sum()
    if n == 0:
        return 0.0
    p = c / n
    return float(-(p * np.log2(p)).sum())


def _mutual_information(joint_counts: np.ndarray, H_u: float,
                        H_v: float) -> float:
    """
    The mutual information I(u; v) in bits, from the joint
    counts + the PRE-COMPUTED marginal entropies (the caller
    computes each sub-variable's entropy once and passes it).
    The identity I = H(u) + H(v) - H(u, v) (the joint entropy
    is the entropy of the joint counts); clamped to >= 0 (the
    floating-point rounding of the identity can give a tiny
    negative).

    Args:
      joint_counts: the (u, v) joint counts (the observed
        cells).
      H_u:          the entropy of u (bits, pre-computed).
      H_v:          the entropy of v (bits, pre-computed).
    """
    I = H_u + H_v - _entropy(joint_counts)
    return float(max(0.0, I))


def _symmetric_uncertainty(I: float, H_u: float,
                          H_v: float) -> float:
    """
    The symmetrical uncertainty SU(u, v) = 2·I / (H(u) +
    H(v)), in [0, 1]. The 0-denominator guard: SU = 0 if
    H(u) + H(v) == 0 (the degenerate variables — the code-0
    "no match" single-category).

    Args:
      I:    the mutual information I(u; v) (bits).
      H_u:  the entropy of u (bits).
      H_v:  the entropy of v (bits).
    """
    denom = H_u + H_v
    if denom == 0:
        return 0.0
    return float(2.0 * I / denom)


def _dispersion(counts: np.ndarray, n_configurations: int) -> dict:
    """
    The per-sub-variable dispersion: K_obs (the distinct
    observed codes), H (the entropy in bits), H_norm = H /
    log2(K_obs) (else 0 — the K_obs <= 1 guard), the coverage =
    K_obs / n_configurations (the theoretical range).

    Args:
      counts: the sub-variable's count array (the observed
        support; the dense form with the zero entries is
        accepted — the zeros are filtered).
      n_configurations: the theoretical code range of the sub-
        variable (the full range, incl. the never-observed).

    Returns:
      {'k_obs', 'h', 'h_norm', 'coverage'}.
    """
    observed = np.asarray(counts, dtype=np.float64).ravel()
    observed = observed[observed > 0]
    k_obs = int(observed.shape[0])
    H = _entropy(observed)
    h_norm = (H / float(np.log2(k_obs))) if k_obs > 1 else 0.0
    n_conf = int(n_configurations)
    coverage = (k_obs / n_conf) if n_conf > 0 else 0.0
    return {'k_obs': k_obs, 'h': H, 'h_norm': h_norm,
            'coverage': coverage}


def _never_observed_audit(counts: np.ndarray,
                          n_configurations: int) -> dict:
    """
    The never-observed audit: the number of theoretical codes
    never seen in the corpus (n_configurations - K_obs).

    Args:
      counts: the sub-variable's count array (the observed
        support; the dense form with the zero entries is
        accepted — the zeros are filtered).
      n_configurations: the theoretical code range of the sub-
        variable (the full range, incl. the never-observed).

    Returns:
      {'k_obs', 'never_observed'}.
    """
    observed = np.asarray(counts, dtype=np.float64).ravel()
    observed = observed[observed > 0]
    k_obs = int(observed.shape[0])
    never = int(n_configurations) - k_obs
    return {'k_obs': k_obs, 'never_observed': never}


def _marginal_lookup(marginal: _MarginalTable) -> dict:
    """The (name, instance_idx) -> counts lookup (the sub-
    variables' marginal counts, for the SU marginals)."""
    return {(name, i): counts
            for (name, i, _nc, _codes, counts) in marginal}


#: The SU summary shape (the _su_values output, the _su_groups
#: input): the list of (name_i, inst_i, name_j, inst_j, su) — one
#: per computed off-diagonal cell.
_SuSummary = list[tuple[str, int, str, int, float]]


#: The SU groups shape (the _su_groups output, the _export_csv
#: input): the list of ((feature_i, feature_j), the group's
#: _SuSummary entries).
_SuGroups = list[tuple[tuple[str, str], _SuSummary]]


def _su_values(joint: _JointTable, lookup: dict) -> _SuSummary:
    """The requested SU values: for each configured
    (name_i, name_j) pair and each (inst_i, inst_j) cell, the SU
    = 2*I / (H_i + H_j) from the joint + the two marginals. The
    same-feature DIAGONAL (inst_i == inst_j) is OMITTED (the SU
    = 1 lock — not a measurement); a diagonal entry present in an
    older joint table is skipped the same way.

    Args:
      joint:  the _JointTable (the per-pair observed joints).
      lookup: the (name, instance) -> counts marginal lookup
              (the _marginal_lookup output).

    Returns:
      the list of (name_i, inst_i, name_j, inst_j, su) entries
      (the _SuSummary).
    """
    su = []
    h_cache: dict = {}
    for (name_i, name_j, per_instance) in joint:
        same_feature = (name_i == name_j)
        for (ii, jj) in per_instance:
            if same_feature and ii == jj:
                continue  # The diagonal: the SU = 1 lock, omitted.
            codes_i, codes_j, counts = per_instance[(ii, jj)]
            mi = lookup.get((name_i, ii))
            mj = lookup.get((name_j, jj))
            if mi is None or mj is None:
                continue
            ki = (name_i, ii)
            h_i = h_cache.get(ki)
            if h_i is None:
                h_i = h_cache[ki] = _entropy(mi)
            kj = (name_j, jj)
            h_j = h_cache.get(kj)
            if h_j is None:
                h_j = h_cache[kj] = _entropy(mj)
            I = _mutual_information(counts, h_i, h_j)
            su.append((name_i, ii, name_j, jj,
                       _symmetric_uncertainty(I, h_i, h_j)))
    return su


def _feature_instances(marginal: _MarginalTable) -> list:
    """The distinct feature names, first-seen order (the model's
    features — the sub-variable names: LMC, EDGE, ...)."""
    seen = []
    for (name, _i, _nc, _codes, _counts) in marginal:
        if name not in seen:
            seen.append(name)
    return seen


def _theoretical_configs(fset: FeatureSet) -> dict:
    """The (name, instance) -> THEORETICAL configuration count
    (the denominator of the coverage + the never-observed audit).
    A PATTERN's observed codes are the PRINCIPAL indices (the
    orbit representatives), so its theoretical space is
    n_unique_configs (the number of equivalence classes under the
    pattern's symmetry — the distinct principal indices), NOT
    n_configurations (the raw 3^n); some of those are unreachable
    by the game's rules (the never-observed audit does not try to
    count them). A MOBILITY's codes are the raw values (no
    symmetry reduction), so its theoretical space is
    n_configurations."""
    space = {}
    for f in fset.features:
        if f.name == 'INTERCEPT':
            continue
        n_unique = getattr(f.ref, 'n_unique_configs', None)
        eff = n_unique if n_unique is not None else f.n_configurations
        for i in range(f.n_instances):
            space[(f.name, i)] = eff
    return space


def _su_canon(name_i: str, inst_i: int,
              name_j: str, inst_j: int) -> tuple:
    """The canonical endpoint order of a SU pair: the two
    (name, inst) tuples sorted. The (i, j) and the (j, i) directions
    of the SAME measurement map to the same canonical form."""
    a = (name_i, inst_i)
    b = (name_j, inst_j)
    return (a, b) if a <= b else (b, a)


def _su_groups(su_summary: _SuSummary,
               su_pairs: list[tuple[str, str]]) -> _SuGroups:
    """The deduplicated + sorted SU groups (the report's Section C).
    The SU is SYMMETRIC (2·I / (H_u + H_v)), so the (i, j) and the
    (j, i) directions of a pair are the SAME measurement — each is
    shown ONCE, in the canonical endpoint order. The groups are the
    feature-pairs (the header), in the configured order; within a
    group the entries are sorted by the CANONICAL ENDPOINT ORDER (the
    lexicographic (feature, instance) order: EDGE[0]-EDGE[1],
    EDGE[0]-EDGE[2], EDGE[1]-EDGE[2], ...)."""
    # 1. The dedup: the (i, j) and the (j, i) of a pair are one
    #    measurement — keep the first, in the canonical endpoint order.
    seen = set()
    deduped = []
    for (ni, ii, nj, jj, s) in su_summary:
        (an, ai), (bn, bi) = _su_canon(ni, ii, nj, jj)
        key = (an, ai, bn, bi)
        if key in seen:
            continue
        seen.add(key)
        deduped.append((an, ai, bn, bi, s))
    # 2. The group order: the configured feature-pairs (the canonical
    #    name order) first, then any not in the config (defensive).
    order = []
    for pair in su_pairs:
        gk = tuple(sorted(pair))
        if gk not in order:
            order.append(gk)
    for (an, _ai, bn, _bi, _s) in deduped:
        gk = tuple(sorted((an, bn)))
        if gk not in order:
            order.append(gk)
    # 3. The group + the sort (the canonical endpoint order).
    groups = {gk: [] for gk in order}
    for (an, ai, bn, bi, s) in deduped:
        groups[tuple(sorted((an, bn)))].append((an, ai, bn, bi, s))
    return [(gk, sorted(groups[gk],
                        key=lambda t: ((t[0], t[1]), (t[2], t[3]))))
            for gk in order]


def _rarity_bins(counts: np.ndarray, n_configurations: int,
                 thresholds: list[int]) -> list:
    """The per-bin frequency histogram (the report's optional
    'Section B: Rarity report'): the half-open bins
    [0, t1), [t1, t2), ..., [tk, inf) — the FIRST bin the
    zero-frequency codes (the never-observed ones) — over the
    sub-variable's count array.

    Args:
      counts:           the sub-variable's count array (the
                        observed support; the dense form with the
                        zero entries is accepted — the zeros are
                        filtered).
      n_configurations: the theoretical code range of the sub-
                        variable (the full range, incl. the never-
                        observed).
      thresholds:       the bin edges (the config's
                        rarity_thresholds).

    Returns:
      the list of k+1 bin counts (int).
    """
    observed = np.asarray(counts, dtype=np.int64).ravel()
    observed = observed[observed > 0]
    t = np.asarray(thresholds, dtype=np.int64)
    idx = np.searchsorted(t, observed, side='right')
    bins = np.bincount(idx, minlength=len(t) + 1)
    bins[0] += int(n_configurations) - int(observed.shape[0])
    return [int(b) for b in bins]


def _export_csv(ctx: "LMContext", tables: dict,
                su_groups: _SuGroups) -> Path:
    """The optional CSV: the per-sub-variable marginal tables +
    the per-pair SU instance entries (the deduplicated + sorted
    groups). Written to base_dir / dir_name / 'su_analysis.csv'
    (the parent dirs are created).

    Args:
      ctx:       the LMContext (the base_dir + the dir_name + the
                 feature_set for the theoretical spaces).
      tables:    the tables dict (the marginal).
      su_groups: the _SuGroups (the deduplicated + sorted groups).

    Returns:
      the CSV path.
    """
    cfg_fa = ctx.cfg.su_analysis
    csv_path = Path(ctx.cfg.base_dir) / cfg_fa.dir_name / \
        "su_analysis.csv"
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    theoretical = _theoretical_configs(ctx.feature_set)
    with open(csv_path, 'w', newline='', encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(['type', 'feature', 'inst', 'n_conf', 'k_obs',
                    'h', 'h_norm', 'coverage', 'never_observed', 'su'])
        for (name, i, nc, _codes, counts) in tables['marginal']:
            eff = theoretical.get((name, i), nc)
            d = _dispersion(counts, eff)
            a = _never_observed_audit(counts, eff)
            w.writerow(['marginal', name, i, eff, d['k_obs'],
                        f"{d['h']:.6f}", f"{d['h_norm']:.6f}",
                        f"{d['coverage']:.6f}", a['never_observed'], ''])
        for gk, grp in su_groups:
            for (an, ai, bn, bi, s) in grp:
                w.writerow(['su', f"{an} - {bn}", f"{ai}x{bi}", '', '',
                            '', '', '', '', f"{s:.6f}"])
    return csv_path


#: Here validation is not possible: it would bring in a circular
#: import (the LMContext facade, the hlp_design_matrix idiom).
def hlp_su_analysis_statistics(ctx: "LMContext", tables: dict) -> Path:
    """Phase 2 — the statistics (cheap, recomputed on EVERY run,
    including the cache hit): the per-sub-variable dispersion +
    the never-observed audit + the requested SU pairs. The
    console (INFO) + the TXT report (dir_name under base_dir) +
    the optional CSV (the export_csv flag).

    Args:
      ctx:    the LMContext (the cfg.su_analysis report options +
              the base_dir + the feature_set).
      tables: the tables dict (the marginal + the joint).

    Returns:
      the TXT report path.

    State: writes the TXT report (always) + the CSV (when the
    export_csv flag); the report rows are logged at INFO.
    """
    cfg_fa = ctx.cfg.su_analysis
    marginal = tables['marginal']
    joint = tables['joint']
    lookup = _marginal_lookup(marginal)
    su_summary = _su_values(joint, lookup) if joint is not None else []
    su_groups = _su_groups(su_summary, cfg_fa.su_pairs)
    pairs_str = ", ".join(" - ".join(tuple(sorted(pair)))
                          for pair in cfg_fa.su_pairs) \
        if cfg_fa.su_pairs else "(none)"
    lines = ["Symmetrical Uncertainity Analysis Report", "=" * 40]
    lines.append("")
    lines.append(f"Corpus: {cfg_fa.corpus.total_positions:,} positions")
    lines.append(f"Features: {', '.join(_feature_instances(marginal))}")
    lines.append(f"SU pairs: {pairs_str}")
    lines.append("")
    theoretical = _theoretical_configs(ctx.feature_set)
    lines.append("Section A: Properties of features selected by "
                 "the logistic model")
    lines.extend(_KPI_LEGEND)
    a_rows = []
    for (name, i, nc, _codes, counts) in marginal:
        eff = theoretical.get((name, i), nc)
        d = _dispersion(counts, eff)
        a = _never_observed_audit(counts, eff)
        a_rows.append((name, i, f"{d['k_obs']}/{eff}",
                       f"{d['h']:.3f}", f"{d['h_norm']:.3f}",
                       f"{d['coverage']:.3f}", str(a['never_observed'])))
    # The column alignment (D-293): the name / the inst LEFT-justified
    # to the max width; the numeric values RIGHT-justified to the
    # computed max width (the K_obs / the never-obs fields carry the
    # +1 separator margin — the shortest value keeps a 1-space gap).
    name_w = max(len(r[0]) for r in a_rows)
    inst_w = max(len(str(r[1])) for r in a_rows)
    kw = max(len(r[2]) for r in a_rows) + 1
    hw = max(len(r[3]) for r in a_rows)
    hnw = max(len(r[4]) for r in a_rows)
    covw = max(len(r[5]) for r in a_rows)
    nw = max(len(r[6]) for r in a_rows) + 1
    for (name, i, kobs, h, hn, cov, never) in a_rows:
        line = (f"  {name:<{name_w}} inst {i:>{inst_w}}: "
                f"K_obs{kobs:>{kw}}, H {h:>{hw}}, "
                f"H_norm {hn:>{hnw}}, coverage {cov:>{covw}}, "
                f"never-obs{never:>{nw}}")
        lines.append(line)
        ctx.log_event(Relevance.INFO, line)
    lines.append("")
    thresholds = cfg_fa.rarity_thresholds or []
    if thresholds:
        lines.append("Section B: Rarity report")
        lines.append("The per-bin frequencies of the codes: the "
                     "half-open bins [0, t1), [t1, t2), ..., [tk, inf)")
        lines.append("The first bin the zero-frequency codes, the "
                     "configurations random play almost never reaches: "
                     "the weights that can never be learned.")
        b_rows = []
        for (name, i, nc, _codes, counts) in marginal:
            eff = theoretical.get((name, i), nc)
            b_rows.append((name, i,
                           _rarity_bins(counts, eff, thresholds)))
        labels, lo = [], 0
        for t in thresholds:
            labels.append(f"[{lo},{t})")
            lo = t
        labels.append(f"[{lo},inf)")
        # The per-bin column alignment (D-293): each bin value
        # RIGHT-justified to its own max width (+1 margin), the
        # labels at natural width, the same name / inst prefix as
        # the Section A.
        bwidths = [max(len(str(r[2][j])) for r in b_rows) + 1
                   for j in range(len(labels))]
        for (name, i, bins) in b_rows:
            parts = [f"{labels[j]}{bins[j]:>{bwidths[j]}}"
                     for j in range(len(labels))]
            line = f"  {name:<{name_w}} inst {i:>{inst_w}}: " \
                + " | ".join(parts)
            lines.append(line)
            ctx.log_event(Relevance.INFO, line)
        lines.append("")
    lines.append("Section C: Symmetrical uncertainity")
    lines.extend(_SU_DESCRIPTION)
    lines += list(_SU_LEGEND)
    if not su_groups:
        lines.append("  (no SU pairs configured)")
    for gk, grp in su_groups:
        header = " - ".join(gk)
        lines.append(header)
        ctx.log_event(Relevance.INFO, header)
        for (an, ai, bn, bi, s) in grp[:20]:
            line = f"  SU {an}[{ai}] - {bn}[{bi}] = {s:.4f}"
            lines.append(line)
            ctx.log_event(Relevance.INFO, line)
        if not grp:
            lines.append("  (none)")
    report_path = Path(ctx.cfg.base_dir) / cfg_fa.dir_name / \
        cfg_fa.report_file_name
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    ctx.log_event(Relevance.INFO,
                  f"SU_ANALYSIS report written: {report_path}.")
    if cfg_fa.export_csv:
        csv_path = _export_csv(ctx, tables, su_groups)
        ctx.log_event(Relevance.INFO,
                      f"SU_ANALYSIS CSV written: {csv_path}.")
    return report_path
