#
# hlp_gate.py
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See
# the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA
# or visit the site <http://www.gnu.org/licenses/>.
#

"""
The T6 DESIGN GATE (the I-017, the v4 doc section 7 —
notes/random_permutation_table.md, FROZEN): the pre-registered
empirical certification that the G1 (ODP-9 table pick) corpus
is statistically indistinguishable from the G0 (the uniform
per-move PRNG draw) reference at the 1e6 scale, with the
table-aware dual criterion (the absolute delta* = 2e-3 + the
parametric q95 of the MEASURED D0 noise) and the family-wise
control. The corpus is the I-017 FEATURES step: the campaign
config (the rlm JSON) supplies the sub-variables (the
FeatureSet, 12 features) and the model's ec (the arrest rule,
IDENTICAL for G0 and G1 — the doc Amendment 1a).

ENGINES (both LOCKSTEP waves, the T5 hlp_wave semantics —
step = one real move per live lane, the pass folded into the
step, the double pass kills the lane):
  G1: the ODP-9 table pick (hlp_wave's pick, the same table
      build, the slot phase pin counter0 = slot).
  G0: the uniform reference — a single GLOBAL MT19937 (the
      project's golden-pinned PRNG, the "one seed for all"
      pin), one draw per (lane, step) in lane order: the
      real-move lanes pick the (draw % k)-th set bit (the
      modulo bias < k/2^64, 12 orders below the noise
      floor); the pass/dead lanes' draws are consumed
      (unused). No PRNG in the G1 loop (the ODP-9 design).

TESTS (v4 section 7):
  1. the table A1 re-check (the per-width rank histogram) +
     the per-width PHASE-OCCUPANCY SCAN (the cross-slot
     histogram of (slot + counter) mod k vs uniform, the
     chi-square k-1 df, Bonferroni over the 64 widths).
  2. the ARREST-STRATIFIED marginals (PRIMARY): per
     sub-variable, per ec level (60 down to the arrest ec),
     the TV of the G1-vs-G0 position codes; the pass
     frequencies (the per-game ply-count distribution); the
     pooled full-trajectory marginal (SECONDARY).
  3. the FOCUSED joints (PRIMARY): per sampled SU pair
     (the feature pairs with the per-instance cell product
     n_conf_A x n_conf_B <= 1e6), the joint codes at the
     SAME position (the SU unit), stratified by the arrest
     ply width k (strata 1..8, 9+): the per-stratum TV + KL.
  4. the small-k dedicated pass (the k <= 4 strata of test 3).
  5. the pooled joint chi-square (DEMOTED: a coarse sanity
     check, reported only).
  6. the phase-continuity scan (the slot-base offsets
     0 / 7 / 4000001: the frequency tables within the G0
     noise of each other).

D0 BOOTSTRAP (v4): 20 G0-vs-G0 replicate pairs at the pair
scale (1e5), the parametric q95 = mean + 1.645*sd per
comparison unit (the TV's empirical CV ~ 2%), rescaled to
the gate scale by the 1/sqrt(N) law (the single factor
sqrt(pair_scale / gate_scale) — the pooled and the per-ec
units share it: the pooled population scales with games*40,
the per-ec strata with games, same ratio).

PASS (v4 — the 1e6 design gate: ALL of (i)-(iii) must hold;
(iv) is the 1e7 BUILD gate, at corpus build time):
  (i)  ABSOLUTE (TABLE-AWARE): every D < delta*_unit =
       max(2e-3, q95(D0_unit));
  (ii) RELATIVE (PRIMARY): every D < the parametric q95 of
       the measured D0 at the unit's scale;
  (iii) the focused tests (3-4) under the family control
       (Bonferroni over the pair x stratum family for the
       chi-square p-values, BH-FDR as the secondary
       diagnostic) + the test 1 phase-occupancy scan.

USAGE (from the workspace root, the venv activated):
  python3 -m reversi.lm.hlp_gate \
      --config src/reversi/test/data/rlm_03.json \
      --n-games 1000000 --pairs 20 --pair-scale 100000 \
      --seed 42 --outdir scratch/gate_1e6
"""

from __future__ import annotations

import argparse
import json
import math
import os
import time

import numpy as np
import numba as nb

from reversi.board import (legal_moves, make_position,
                           position_make_move)
from reversi.lm.hlp_wave import (INITIAL_MOVER, INITIAL_OPP, PA,
                                 MAX_EC)

__all__ = ['load_campaign', 'run_gate']

#: The MT19937-64 constants (tools/prng.py, the C verbatim).
_NN = 312
_MM = 156
_UM = np.uint64(0xFFFFFFFF80000000)
_LM = np.uint64(0x000000007FFFFFFF)
_MAG = np.uint64(0xB5026F5AA96619E9)


# ---------------------------------------------------------------------
# The MT19937-64 batch-draw kernels (the numba port of the
# golden-pinned PRNG — the gate's G0 stream).
# ---------------------------------------------------------------------

@nb.njit(cache=True)
def _mt19937_init(mt, seed):
    """C prng_mt19937_init_by_seed, line by line (the verbatim
    quirk: the loop leaves mti == NN — the first draw twists
    the just-initialized array). Returns mti."""
    mt[0] = np.uint64(seed)
    for i in range(1, _NN):
        prev = mt[i - 1]
        mt[i] = np.uint64(6364136223846793005) * (prev ^ (prev >> 62)) \
            + np.uint64(i)
    return _NN


@nb.njit(cache=True)
def _mt19937_batch(mt, mti, n):
    """The n successive u64 draws (the twist + the 4-op temper,
    prng.c L380-414 line by line). Returns (draws, mti)."""
    out = np.empty(n, dtype=np.uint64)
    for j in range(n):
        if mti >= _NN:
            i = 0
            while i < _NN - _MM:
                x = (mt[i] & _UM) | (mt[i + 1] & _LM)
                mt[i] = mt[i + _MM] ^ (x >> 1) ^ \
                    (np.uint64(0) if (x & np.uint64(1)) == 0 else _MAG)
                i += 1
            while i < _NN - 1:
                x = (mt[i] & _UM) | (mt[i + 1] & _LM)
                mt[i] = mt[i + (_MM - _NN)] ^ (x >> 1) ^ \
                    (np.uint64(0) if (x & np.uint64(1)) == 0 else _MAG)
                i += 1
            x = (mt[_NN - 1] & _UM) | (mt[0] & _LM)
            mt[_NN - 1] = mt[_MM - 1] ^ (x >> 1) ^ \
                (np.uint64(0) if (x & np.uint64(1)) == 0 else _MAG)
            mti = 0
        x = mt[mti]
        mti += 1
        x = x ^ ((x >> 29) & np.uint64(0x5555555555555555))
        x = x ^ ((x << 17) & np.uint64(0x71D67FFFEDA60000))
        x = x ^ ((x << 37) & np.uint64(0xFFF7EEE000000000))
        x = x ^ (x >> 43)
        out[j] = x
    return out, mti


# ---------------------------------------------------------------------
# The pick kernels (G1: the ODP-9 table; G0: the uniform draw).
# The HW popcount (numba has no .bit_count on uint64).
# ---------------------------------------------------------------------

@nb.njit(parallel=True, cache=True)
def _popcount_u64(src):
    """The per-element popcount (the classic 5-op reduce)."""
    n = src.shape[0]
    out = np.empty(n, dtype=np.int64)
    for i in nb.prange(n):
        x = src[i]
        c = x - ((x >> 1) & np.uint64(0x5555555555555555))
        c = (c & np.uint64(0x3333333333333333)) + \
            ((c >> 2) & np.uint64(0x3333333333333333))
        c = (c + (c >> 4)) & np.uint64(0x0F0F0F0F0F0F0F0F)
        out[i] = int((c * np.uint64(0x0101010101010101)) >> 56)
    return out


def _kth_set_bit_kernel(src, rank):
    """The rank-th set bit (the canonical ascending order) —
    the shared tail of the two pick kernels (numba-compiled
    through the callers)."""
    y = src
    for _ in range(rank):
        y &= y - np.uint64(1)
    lb = y & -y
    square = 0
    while lb > np.uint64(1):
        lb >>= 1
        square += 1
    return np.uint8(square)


@nb.njit(parallel=True, cache=True)
def _pick_g1(src, counter, table):
    """The G1 ODP-9 pick (hlp_wave._pick_wave, the same
    semantics): rank = table[k][counter % k]; k == 0 ->
    (PA, no step)."""
    n = src.shape[0]
    move = np.empty(n, dtype=np.uint8)
    step = np.empty(n, dtype=np.bool_)
    for i in nb.prange(n):
        x = src[i]
        c = x - ((x >> 1) & np.uint64(0x5555555555555555))
        c = (c & np.uint64(0x3333333333333333)) + \
            ((c >> 2) & np.uint64(0x3333333333333333))
        c = (c + (c >> 4)) & np.uint64(0x0F0F0F0F0F0F0F0F)
        k = int((c * np.uint64(0x0101010101010101)) >> 56)
        if k == 0:
            move[i] = np.uint8(PA)
            step[i] = False
            continue
        rank = int(table[k, counter[i] % k])
        y = x
        for _ in range(rank):
            y &= y - np.uint64(1)
        lb = y & -y
        square = 0
        while lb > np.uint64(1):
            lb >>= 1
            square += 1
        move[i] = np.uint8(square)
        step[i] = True
    return move, step


@nb.njit(parallel=True, cache=True)
def _pick_g0(draws, src):
    """The G0 uniform pick: rank = draw % k (the modulo bias
    < k/2^64, 12 orders below the noise floor); k == 0 ->
    (PA, no step)."""
    n = src.shape[0]
    move = np.empty(n, dtype=np.uint8)
    step = np.empty(n, dtype=np.bool_)
    for i in nb.prange(n):
        x = src[i]
        c = x - ((x >> 1) & np.uint64(0x5555555555555555))
        c = (c & np.uint64(0x3333333333333333)) + \
            ((c >> 2) & np.uint64(0x3333333333333333))
        c = (c + (c >> 4)) & np.uint64(0x0F0F0F0F0F0F0F0F)
        k = int((c * np.uint64(0x0101010101010101)) >> 56)
        if k == 0:
            move[i] = np.uint8(PA)
            step[i] = False
            continue
        rank = int(draws[i] % np.uint64(k))
        y = x
        for _ in range(rank):
            y &= y - np.uint64(1)
        lb = y & -y
        square = 0
        while lb > np.uint64(1):
            lb >>= 1
            square += 1
        move[i] = np.uint8(square)
        step[i] = True
    return move, step


# ---------------------------------------------------------------------
# The config / feature-set loading (the pipeline's own path:
# json5 + LMConfig; the FeatureSet built as wrk_features does).
# ---------------------------------------------------------------------

def load_campaign(config_path: str):
    """
    Loads the campaign config (json5, the pipeline's own
    loader) + the FeatureSet (the wrk_features pure mapping)
    + the per-feature column blocks (the documented column
    layout: the intercept, then the mobilities in the (mask,
    amask) sorted order, then the patterns in the mask sorted
    order — the fset.features order).

    Returns:
      (cfg, fset, blocks) — blocks: the list of
      (name, col_start, col_end, n_conf, n_inst) over the
      non-intercept features (the gate's sub-variables).
    """
    import json5
    from reversi.feature import Feature, FeatureSet
    from reversi.lm.hlp_config_schemas import LMConfig
    from reversi.mobility import Mobility, MobilitySet
    from reversi.pattern import Pattern, PatternSet

    with open(config_path, 'r', encoding='utf-8') as f:
        raw = json5.load(f)
    cfg = LMConfig(**raw)
    fsc = cfg.feature_set
    fset = FeatureSet(
        fsc.name,
        Feature.new_intercept() if fsc.intercept else None,
        (MobilitySet(fsc.mobility_set.name,
                     [Mobility(e.name, e.mask, e.amask)
                      for e in fsc.mobility_set.mobility_features])
         if fsc.mobility_set else None),
        (PatternSet(fsc.pattern_set.name,
                    [Pattern(e.name, e.mask)
                     for e in fsc.pattern_set.patterns])
         if fsc.pattern_set else None))
    blocks = []
    col = 1 if (fset.intercept is not None) else 0
    for f in fset.features:
        if f.category in (0, 'intercept') or f.name == 'INTERCEPT':
            continue
        blocks.append((f.name, col, col + int(f.n_instances),
                       int(f.n_configurations), int(f.n_instances)))
        col += int(f.n_instances)
    return cfg, fset, blocks


def _to_positions(mover, opp) -> np.ndarray:
    """The direct PositionArray build (the interleaved
    structured array — the make_position layout, no pydantic
    in the gate hot path)."""
    n = mover.shape[0]
    pa = np.empty(n, dtype=np.dtype([('mover', np.uint64),
                                     ('opponent', np.uint64)]))
    pa['mover'] = mover
    pa['opponent'] = opp
    return pa


def _pooled_counts(acc, blocks, bidx, n_ec):
    """The pooled per-feature counts (the sum over the ec
    levels, the sparse (codes, counts) form, the structured
    keys)."""
    agg = {}
    for e in range(n_ec):
        cset = acc.ec_counts[e][bidx]
        if cset is None:
            continue
        u, cnt = cset
        keys = [tuple(v) for v in u.tolist()]
        for key, n in zip(keys, cnt):
            agg[key] = agg.get(key, 0) + int(n)
    dt = np.dtype([(f'c{i}', np.uint32)
                   for i in range(blocks[bidx][4])])
    if not agg:
        return np.empty(0, dtype=dt), np.empty(0, dtype=np.int64)
    items = sorted(agg.items())
    u = np.array([k for k, _ in items], dtype=dt)
    c = np.array([v for _, v in items], dtype=np.int64)
    return u, c


def _feature_codes(idx: np.ndarray, block: tuple) -> np.ndarray:
    """The feature code per position: a STRUCTURED array of
    the n_inst instance columns (the exact key — no packed-
    int overflow: the 2X5COR code space is 59049^8 >> 2^64).
    np.unique / np.searchsorted are lexicographic on the
    fields (exact)."""
    name, c0, c1, n_conf, n_inst = block
    dt = np.dtype([(f'c{i}', np.uint32) for i in range(n_inst)])
    out = np.empty(idx.shape[0], dtype=dt)
    for i in range(n_inst):
        out[f'c{i}'] = idx[:, c0 + i]
    return out


def _joint_key(ca: np.ndarray, cb: np.ndarray) -> np.ndarray:
    """The joint (c_A, c_B) code: the combined structured
    array (the a-fields, then the renamed b-fields)."""
    da = ca.dtype
    db = np.dtype([(n.replace('c', 'b'), t)
                   for (n, t) in cb.dtype.descr])
    dt = np.dtype(da.descr + db.descr)
    out = np.empty(ca.shape[0], dtype=dt)
    for (n, _) in da.fields.items():
        out[n] = ca[n]
    for (n, _) in cb.dtype.descr:
        out[n.replace('c', 'b')] = cb[n]
    return out


# ---------------------------------------------------------------------
# The wave generators (G1 / G0), with the gate observers.
# ---------------------------------------------------------------------

class _Accumulators:
    """The per-run observations (the gate's data plane)."""

    def __init__(self, n_ec_levels: int, blocks):
        self.n_blocks = len(blocks)
        # per-ec position codes: list[ec] -> list[block] ->
        # (code_array, count_array) sparse counts (the union-
        # support compact form).
        self.ec_counts = [None] * n_ec_levels
        # the pass counts per harvested game (the per-game
        # ply-count distribution).
        self.pass_hist = {}
        # the per-width visit + phase + rank histograms
        # (G1 only): width -> [visits, phase_hist(k,),
        #                       rank_hist(k,)]
        self.widths = {}
        # the arrested (mover, opp, slot) — the corpus.
        self.arrested = []

    def add_ec(self, ec, idx, blocks):
        slot = self.ec_counts
        p = MAX_EC - ec  # the level position (0..n_ec-1)
        row = slot[p] if slot[p] is not None else [None] * len(blocks)
        slot[p] = row
        for b, blk in enumerate(blocks):
            if row[b] is None:
                codes = _feature_codes(idx, blk)
                u, inv = np.unique(codes, return_inverse=True)
                cnt = np.bincount(inv)
                row[b] = (u, cnt)


def _wave_generate(engine, total, ec_target, table, W, slot_base,
                   mt, mti, blocks, fset, acc):
    """
    The lockstep wave driver with the gate observers (both
    engines share the structure; engine = 'g1' | 'g0').
    Observers: the per-ec feature codes (the pre-step ec
    level + the arrested positions), the per-game pass
    counts, the per-width rank/phase histograms (G1).
    """
    S = MAX_EC - int(ec_target)
    n_ec = MAX_EC - int(ec_target) + 1
    M = np.full(W, INITIAL_MOVER, dtype=np.uint64)
    O = np.full(W, INITIAL_OPP, dtype=np.uint64)
    slot = np.arange(slot_base, slot_base + W, dtype=np.int64)
    counter = slot.copy()
    alive = np.ones(W, dtype=np.bool_)
    pass_count = np.zeros(W, dtype=np.int64)
    next_slot = slot_base + W
    harvested = 0
    while harvested < total:
        for s in range(S):
            lm = legal_moves(M, O)
            lo = legal_moves(O, M)
            pass_mask = lm == 0
            dead = pass_mask & (lo == 0)
            src = np.where(pass_mask, lo, lm)
            # OBSERVE (before the step): the start ec level
            # 60 (before the first step) + the width +
            # rank/phase of the real picks.
            if s == 0:
                ai = np.nonzero(alive)[0]
                if ai.size:
                    idx = fset.compute_indexes(
                        _to_positions(M[ai], O[ai]))
                    acc.add_ec(MAX_EC, idx, blocks)
            if engine == 'g1':
                k_arr = _popcount_u64(lm)
                for k in range(1, 65):
                    m = k_arr == k
                    if not m.any():
                        continue
                    # the v4 phase: (g + m_g) mod k, m_g = the
                    # moves made (counter - slot) -> counter
                    # mod k (the rank argument, v4 L545).
                    ph = counter[m] % k
                    rk = table[k, counter[m] % k]
                    w = acc.widths.setdefault(
                        k, [0, np.zeros(k, np.int64),
                            np.zeros(k, np.int64)])
                    w[0] += int(m.sum())
                    w[1] += np.bincount(ph, minlength=k)
                    w[2] += np.bincount(rk, minlength=k)
            # THE PICK (the engine difference).
            if engine == 'g1':
                move, _ = _pick_g1(src, counter, table)
            else:
                draws, mti = _mt19937_batch(mt, mti, W)
                move, _ = _pick_g0(draws, src)
            move = np.where(dead, np.uint8(PA), move)
            swapped = pass_mask & ~dead
            out = position_make_move(
                _to_positions(np.where(swapped, O, M),
                              np.where(swapped, M, O)), move)
            M, O = out['mover'], out['opponent']
            counter += (~dead).astype(np.int64)
            if pass_mask.any():
                pass_count[pass_mask] += 1
            if dead.any():
                alive &= ~dead
            # OBSERVE (per-ec feature codes): AFTER the step
            # the live lanes are at ec = 60 - s - 1 (59..21);
            # the arrest ec (20) is observed ONLY from the
            # boundary harvest (no double count), the start
            # ec (60) before the first step.
            if s < S - 1:
                ai = np.nonzero(alive)[0]
                if ai.size:
                    idx = fset.compute_indexes(
                        _to_positions(M[ai], O[ai]))
                    acc.add_ec(MAX_EC - s - 1, idx, blocks)
        # THE BOUNDARY: the harvest (the arrest ec level) +
        # the respawn.
        ai = np.nonzero(alive)[0]
        n = min(int(ai.size), total - harvested)
        if n:
            hidx = ai[:n]
            idx = fset.compute_indexes(
                _to_positions(M[hidx], O[hidx]))
            acc.add_ec(int(ec_target), idx, blocks)
            for g in range(n):
                pc = int(pass_count[hidx[g]])
                acc.pass_hist[pc] = acc.pass_hist.get(pc, 0) + 1
            acc.arrested.append((M[hidx].copy(), O[hidx].copy(),
                                 slot[hidx].copy()))
        M[:] = INITIAL_MOVER
        O[:] = INITIAL_OPP
        slot[:] = next_slot + np.arange(W, dtype=np.int64)
        counter = slot.copy()
        next_slot += W
        alive[:] = True
        pass_count[:] = 0
        harvested += n
    return mti


# ---------------------------------------------------------------------
# The statistics (the TV / KL / chi-square + the thresholds).
# ---------------------------------------------------------------------

def _tv(c1, c2) -> float:
    """The total variation of two count vectors (the sparse
    (code, count) compact form, the union support):
    TV = 0.5 * sum_c |c1(c)/N1 - c2(c)/N2|."""
    a1, n1 = c1
    a2, n2 = c2
    if a1.size == 0 and a2.size == 0:
        return 0.0
    N1 = int(n1.sum())
    N2 = int(n2.sum())
    codes = np.concatenate([a1, a2])
    u, inv = np.unique(codes, return_inverse=True)
    h1 = np.bincount(inv[:a1.size], weights=n1, minlength=u.size)
    h2 = np.bincount(inv[a1.size:], weights=n2, minlength=u.size)
    return 0.5 * float(np.sum(np.abs(h1 / N1 - h2 / N2)))


def _kl(c1, c2) -> float:
    """The KL divergence D(p1 || p2) (the sparse form, the
    p1-support terms; a p1-supported code absent from p2
    -> the large cap of 50 nats, the sparse-table
    convention)."""
    a1, n1 = c1
    a2, n2 = c2
    N1 = int(n1.sum())
    N2 = int(n2.sum())
    if N1 == 0 or N2 == 0:
        return 0.0
    m = np.searchsorted(a2, a1)
    m = np.clip(m, 0, a2.size)
    match = (m < a2.size) & (a2[np.clip(m, 0, a2.size - 1)] == a1)
    p1 = n1 / N1
    p2 = np.zeros(a1.size)
    p2[match] = n2[np.clip(m, 0, a2.size - 1)][match] / N2
    terms = np.zeros(a1.size)
    ok = (p1 > 0) & match
    terms[ok] = p1[ok] * np.log(p1[ok] / p2[ok])
    inf = (p1 > 0) & ~match
    terms[inf] = p1[inf] * 50.0  # the large cap
    return float(terms.sum())


def _chi2_p(c1, c2) -> tuple[float, float]:
    """The 2-sample chi-square over the union support
    (the sparse table) — the (statistic, p-value) pair; the
    p by the normal tail of the chi-square (df large enough
    for the gate tables; the coarse instruments anyway)."""
    a1, n1 = c1
    a2, n2 = c2
    if a1.size == 0 and a2.size == 0:
        return 0.0, 1.0
    codes = np.concatenate([a1, a2])
    u, inv = np.unique(codes, return_inverse=True)
    df = u.size - 1
    if df <= 0:
        return 0.0, 1.0
    tot = int(n1.sum()) + int(n2.sum())
    h1 = np.bincount(inv[:a1.size], weights=n1, minlength=u.size)
    h2 = np.bincount(inv[a1.size:], weights=n2, minlength=u.size)
    if tot == 0:
        return 0.0, 1.0
    if float(np.sum(h1 + h2)) > 0 and \
            np.array_equal(h1, h2):
        return 0.0, 1.0
    exp = tot * (h1 + h2) / (2 * tot)
    with np.errstate(divide='ignore', invalid='ignore'):
        term = np.where(exp > 0, (h1 - exp) ** 2 / exp +
                        (h2 - exp) ** 2 / exp, 0.0)
    stat = float(term.sum())
    # the chi-square tail by the Wilson-Hilferty normal approx
    z = ((stat / df) ** (1 / 3) - (1 - 2 / (9 * df))) * \
        math.sqrt(2 * df - 1 / 3) if df > 0 else 0.0
    p = 0.5 * math.erfc(z / math.sqrt(2))
    return stat, float(p)


def _bh_fdr(pvals, alpha=0.05):
    """The Benjamini-Hochberg FDR rejection mask (the
    secondary diagnostic)."""
    p = np.asarray(pvals, dtype=float)
    order = np.argsort(p)
    n = p.size
    rank = np.empty(n, dtype=float)
    rank[order] = np.arange(1, n + 1)
    thresh = alpha * rank / max(n, 1)
    # the largest r with p(r) <= alpha*r/n, then reject all
    # up to it.
    ok = p <= thresh
    r_max = 0
    for i in range(n - 1, -1, -1):
        if ok[i]:
            r_max = i + 1
            break
    reject = np.zeros(n, dtype=bool)
    if r_max:
        idx = order[:r_max]
        reject[idx] = True
    return reject


# ---------------------------------------------------------------------
# The gate proper.
# ---------------------------------------------------------------------

def run_gate(config_path: str, n_games: int, ec: int, seed: int,
             pairs: int, pair_scale: int, wave_size: int,
             outdir: str) -> dict:
    """
    Runs the full T6 design gate (the v4 section 7) and
    writes the report. Returns the verdict dict.
    """
    t_start = time.time()
    os.makedirs(outdir, exist_ok=True)
    cfg, fset, blocks = load_campaign(config_path)
    ec = int(ec) if ec is not None else int(cfg.regab_data_set.ec)
    n_blocks = len(blocks)
    S = MAX_EC - ec
    n_ec = MAX_EC - ec + 1
    report = {'config': config_path, 'ec': ec, 'n_games': n_games,
              'seed': seed, 'pairs': pairs, 'pair_scale': pair_scale,
              'features': [b[0] for b in blocks]}

    # The table (G1) + the MT19937 state (G0): one seed for
    # all (the "one for the JSON" pin — the provenance).
    from reversi.lm.hlp_random_play import build_pick_table
    table = build_pick_table(seed)

    print(f"[gate] G1 corpus: {n_games} games, W={wave_size}, "
          f"ec={ec}, seed={seed}")
    acc_g1 = _Accumulators(n_ec, blocks)
    _wave_generate('g1', n_games, ec, table, wave_size, 0,
                   None, 0, blocks, fset, acc_g1)
    t_g1 = time.time() - t_start
    print(f"[gate] G1 done in {t_g1:.1f}s")

    print(f"[gate] G0 corpus: {n_games} games (the global "
          f"MT19937 stream)")
    acc_g0 = _Accumulators(n_ec, blocks)
    mt0 = np.zeros(_NN, dtype=np.uint64)
    _mt19937_init(mt0, seed)
    mti0 = _NN
    t0 = time.time()
    _wave_generate('g0', n_games, ec, table, wave_size, 0,
                   mt0, mti0, blocks, fset, acc_g0)
    t_g0 = time.time() - t0
    print(f"[gate] G0 done in {t_g0:.1f}s")

    # TEST 2 (the PRIMARY stratified marginals) — the per-ec
    # TV per feature + the pooled + the pass frequencies.
    units = {}  # name -> {'D':, 'kappa':, 'd0': [..]}
    for b, blk in enumerate(blocks):
        name = blk[0]
        d_ec, p_ec = [], []
        for e in range(n_ec):
            i_ec = e
            c1 = acc_g1.ec_counts[i_ec][b]
            c0 = acc_g0.ec_counts[i_ec][b]
            if c1 is None or c0 is None:
                continue
            d_ec.append(_tv(c1, c0))
            p_ec.append(_chi2_p(c1, c0)[1])
        # the pooled = the sum over ec (the code union).
        u1, n1 = _pooled_counts(acc_g1, blocks, b, n_ec)
        u0, n0 = _pooled_counts(acc_g0, blocks, b, n_ec)
        units[f'{name}:pooled'] = {'D': _tv((u1, n1), (u0, n0)),
                                   'p': _chi2_p((u1, n1), (u0, n0))[1]}
        units[f'{name}:per-ec:max'] = {
            'D': max(d_ec) if d_ec else 0.0,
            'p': min(p_ec) if p_ec else 1.0}
    # the pass frequencies (the per-game ply-count
    # distribution).
    pk = sorted(set(acc_g1.pass_hist) | set(acc_g0.pass_hist))
    v1 = np.array([acc_g1.pass_hist.get(k, 0) for k in pk],
                  dtype=np.int64)
    v0 = np.array([acc_g0.pass_hist.get(k, 0) for k in pk],
                  dtype=np.int64)
    ku = np.arange(len(pk), dtype=np.uint64)
    units['passes:per-game'] = {'D': _tv((ku, v1), (ku, v0)),
                                'p': _chi2_p((ku, v1), (ku, v0))[1]}

    # TEST 3/4 (the focused joints) — the sampled SU pairs
    # (the per-instance cell product <= 1e6), the arrest
    # stratification by the ply width.
    conf = {b[0]: b[3] for b in blocks}
    names = [b[0] for b in blocks]
    su_pairs = []
    for i in range(n_blocks):
        for j in range(i + 1, n_blocks):
            if conf[names[i]] * conf[names[j]] <= 1_000_000:
                su_pairs.append((names[i], names[j]))
    report['su_pairs'] = su_pairs
    # the arrest codes + widths (from the G1/G0 corpora).
    def arrest_data(acc):
        M = np.concatenate([c[0] for c in acc.arrested])
        O = np.concatenate([c[1] for c in acc.arrested])
        idx = fset.compute_indexes(_to_positions(M, O))
        w = _popcount_u64(legal_moves(M, O))
        return idx, w
    idx1, w1 = arrest_data(acc_g1)
    idx0, w0 = arrest_data(acc_g0)
    strata = [(k, k) for k in range(1, 9)] + [(9, 64)]
    joint_units = []
    for (fa, fb) in su_pairs:
        ba = next(b for b in blocks if b[0] == fa)
        bb = next(b for b in blocks if b[0] == fb)
        ca1 = _feature_codes(idx1, ba)
        cb1 = _feature_codes(idx1, bb)
        ca0 = _feature_codes(idx0, ba)
        cb0 = _feature_codes(idx0, bb)
        for (klo, khi) in strata:
            ma = (w1 >= klo) & (w1 <= khi)
            mb = (w0 >= klo) & (w0 <= khi)
            if not ma.any() or not mb.any():
                continue
            key1 = _joint_key(ca1[ma], cb1[ma])
            key0 = _joint_key(ca0[mb], cb0[mb])
            u1k, inv1 = np.unique(key1, return_inverse=True)
            n1k = np.bincount(inv1)
            u0k, inv0 = np.unique(key0, return_inverse=True)
            n0k = np.bincount(inv0)
            d = _tv((u1k, n1k), (u0k, n0k))
            p = _chi2_p((u1k, n1k), (u0k, n0k))[1]
            kl = _kl((u1k, n1k), (u0k, n0k))
            joint_units.append(
                {'pair': f'{fa}x{fb}', 'k': f'{klo}-{khi}',
                 'D': d, 'KL': kl, 'p': p,
                 'small_k': klo <= 4})
    # the family control (test 3-4): the Bonferroni + the
    # BH-FDR over the joint family.
    if joint_units:
        jp = np.array([u['p'] for u in joint_units])
        n_j = jp.size
        bonf_significant = int((jp < 0.05 / n_j).sum())
        fdr_reject = int(_bh_fdr(jp).sum())
        joint_units_bonf = {'n': n_j,
                            'bonferroni_significant': bonf_significant,
                            'bh_fdr_rejected': fdr_reject}
    else:
        joint_units_bonf = {'n': 0}

    # TEST 1 (the table A1 + the phase-occupancy scan, G1).
    test1 = {}
    bonf_alpha = 0.05 / 64
    worst_phase_p = 1.0
    for k in sorted(acc_g1.widths):
        visits, ph, rk = acc_g1.widths[k]
        if visits < k:
            continue
        p_ph = _chi2_p((np.arange(k, dtype=np.uint64), ph),
                       (np.arange(k, dtype=np.uint64),
                        np.full(k, visits // k, np.int64)))[1]
        p_rk = _chi2_p((np.arange(k, dtype=np.uint64), rk),
                       (np.arange(k, dtype=np.uint64),
                        np.full(k, visits // k, np.int64)))[1]
        worst_phase_p = min(worst_phase_p, p_ph)
        test1[k] = {'visits': int(visits),
                    'phase_p': float(p_ph),
                    'rank_p': float(p_rk)}
    test1_summary = {'widths_tested': len(test1),
                     'bonferroni_alpha': bonf_alpha,
                     'worst_phase_p': float(worst_phase_p),
                     'phase_scan_pass': worst_phase_p >= bonf_alpha}

    # TEST 6 (the phase continuity — the slot-base offsets):
    # the base run IS the main G1 run (slot_base 0); the
    # offset runs use the SAME table seed (the slot base
    # shifts the phase — a phase-locked artifact would move
    # the tables beyond the G0 noise).
    offsets = [7, 4000001]
    base_counts = acc_g1  # the base run IS the main G1
    test6 = {0: {'note': 'the base run (the main G1)'}}
    for off in offsets:
        acc6 = _Accumulators(n_ec, blocks)
        _wave_generate('g1', n_games, ec, table,
                       min(wave_size, n_games), off,
                       None, 0, blocks, fset, acc6)
        # the pooled per-feature TV vs the base (the offset
        # run uses the same table seed — the slot base shifts
        # the phase; a phase-locked artifact would move the
        # tables beyond the G0 noise).
        dmax = 0.0
        for b, blk in enumerate(blocks):
            u1, n1 = _pooled_counts(acc6, blocks, b, n_ec)
            u2, n2 = _pooled_counts(base_counts, blocks, b, n_ec)
            dmax = max(dmax, _tv((u1, n1), (u2, n2)))
        test6[off] = {'max_pooled_TV_vs_base': float(dmax)}

    # TEST 5 (the demoted pooled joint chi-square — reported).
    test5 = []
    for (fa, fb) in su_pairs[:6]:  # a sample (the demoted
        # instrument — the report only)
        ba = next(b for b in blocks if b[0] == fa)
        bb = next(b for b in blocks if b[0] == fb)
        key1 = _joint_key(_feature_codes(idx1, ba),
                          _feature_codes(idx1, bb))
        key0 = _joint_key(_feature_codes(idx0, ba),
                          _feature_codes(idx0, bb))
        u1, inv1 = np.unique(key1, return_inverse=True)
        u0, inv0 = np.unique(key0, return_inverse=True)
        stat, p = _chi2_p((u1, np.bincount(inv1)),
                          (u0, np.bincount(inv0)))
        test5.append({'pair': f'{fa}x{fb}', 'stat': stat, 'p': p})

    # THE D0 BOOTSTRAP (the 20 G0-vs-G0 pairs at the pair
    # scale — the parametric q95 per unit).
    print(f"[gate] D0 bootstrap: {pairs} G0-vs-G0 pairs at "
          f"{pair_scale}")
    d0 = {}  # unit name -> list of D
    d0_units = [u for u in units] + [f"{u['pair']}:{u['k']}"
                                     for u in joint_units]
    for i in range(pairs):
        mtA = np.zeros(_NN, dtype=np.uint64)
        _mt19937_init(mtA, seed + 1000 + 2 * i)
        mtB = np.zeros(_NN, dtype=np.uint64)
        _mt19937_init(mtB, seed + 1000 + 2 * i + 1)
        w_pair = min(wave_size, pair_scale)
        accA = _Accumulators(n_ec, blocks)
        _wave_generate('g0', pair_scale, ec, table, w_pair, 0,
                       mtA, _NN, blocks, fset, accA)
        accB = _Accumulators(n_ec, blocks)
        _wave_generate('g0', pair_scale, ec, table, w_pair, 0,
                       mtB, _NN, blocks, fset, accB)
        for name in units:
            if name.endswith(':pooled'):
                feat = name[:-7]  # drop ':pooled'
                bidx = blocks.index(
                    next(b for b in blocks if b[0] == feat))
                u1, n1 = _pooled_counts(accA, blocks, bidx, n_ec)
                u2, n2 = _pooled_counts(accB, blocks, bidx, n_ec)
                d0.setdefault(name, []).append(
                    _tv((u1, n1), (u2, n2)))
            elif name.endswith(':per-ec:max'):
                feat = name[:-11]  # drop ':per-ec:max'
                blk = next(b for b in blocks if b[0] == feat)
                bidx = blocks.index(blk)
                dmax = 0.0
                for e in range(n_ec):
                    i_ec = e
                    cA = accA.ec_counts[i_ec][bidx]
                    cB = accB.ec_counts[i_ec][bidx]
                    if cA is None or cB is None:
                        continue
                    dmax = max(dmax, _tv(cA, cB))
                d0.setdefault(name, []).append(dmax)
            elif name == 'passes:per-game':
                pkA = sorted(set(accA.pass_hist) | set(accB.pass_hist))
                kA = np.arange(len(pkA), dtype=np.uint64)
                nA = np.array([accA.pass_hist.get(k, 0)
                               for k in pkA], dtype=np.int64)
                nB = np.array([accB.pass_hist.get(k, 0)
                               for k in pkA], dtype=np.int64)
                d0.setdefault(name, []).append(_tv((kA, nA),
                                                   (kA, nB)))
        # the joint units (the arrest data at the pair scale).
        iA, wA = arrest_data(accA)
        iB, wB = arrest_data(accB)
        for (fa, fb) in su_pairs:
            ba = next(b for b in blocks if b[0] == fa)
            bb = next(b for b in blocks if b[0] == fb)
            for (klo, khi) in strata:
                ma = (wA >= klo) & (wA <= khi)
                mb = (wB >= klo) & (wB <= khi)
                if not ma.any() or not mb.any():
                    d0.setdefault(
                        f'{fa}x{fb}:{klo}-{khi}', []).append(0.0)
                    continue
                k1 = _joint_key(_feature_codes(iA, ba)[ma],
                                _feature_codes(iA, bb)[ma])
                k2 = _joint_key(_feature_codes(iB, ba)[mb],
                                _feature_codes(iB, bb)[mb])
                u1k, inv1 = np.unique(k1, return_inverse=True)
                u2k, inv2 = np.unique(k2, return_inverse=True)
                d0.setdefault(
                    f'{fa}x{fb}:{klo}-{khi}', []).append(
                    _tv((u1k, np.bincount(inv1)),
                        (u2k, np.bincount(inv2))))

    # THE CRITERION (v4 — the 1e6 design gate: (i)-(iii)).
    rescale = math.sqrt(pair_scale / n_games)  # the 1/sqrt(N)
    crit = {}
    for name in d0_units:
        vals = np.array(d0.get(name, [0.0]), dtype=float)
        q95 = float(vals.mean() + 1.645 * vals.std()) * rescale
        unit = units.get(name)
        d = unit['D'] if unit else next(
            (u['D'] for u in joint_units
             if f"{u['pair']}:{u['k']}" == name), 0.0)
        crit[name] = {'D': float(d), 'd0_q95_1e6': q95,
                      'delta_star': max(2e-3, q95),
                      'i_pass': d < max(2e-3, q95),
                      'ii_pass': d < q95 if q95 > 0 else True}
    n_units = len(crit)
    i_all = all(c['i_pass'] for c in crit.values())
    ii_all = all(c['ii_pass'] for c in crit.values())
    iii_ok = test1_summary['phase_scan_pass'] and \
        (joint_units_bonf['n'] == 0 or
         joint_units_bonf['bonferroni_significant'] == 0)
    verdict = 'PASS' if (i_all and ii_all and iii_ok) else 'FAIL'

    result = {
        'verdict': verdict,
        'n_units': n_units,
        'criterion': {'i_all': bool(i_all), 'ii_all': bool(ii_all),
                      'iii': {'phase_scan': test1_summary,
                              'joint_family': joint_units_bonf},
                      'iv_build_gate_1e7': 'PENDING (the corpus build)'},
        'd0_rescale_factor': rescale,
        'test2_units': {k: {'D': v['D'], 'p': v['p']}
                        for k, v in units.items()},
        'test3_joint_units': joint_units,
        'test1': test1_summary,
        'test5_demoted': test5,
        'test6_phase_continuity': test6,
        'd0_q95_per_unit': {k: v['d0_q95_1e6'] for k, v in crit.items()},
        'timing_s': {'total': time.time() - t_start,
                     'g1': t_g1, 'g0': t_g0},
        **{k: v for k, v in report.items()},
    }
    with open(os.path.join(outdir, 'gate_results.json'), 'w') as f:
        json.dump(result, f, indent=2, default=float)
    _write_report(os.path.join(outdir, 'gate_report.txt'), result)
    print(f"[gate] VERDICT: {verdict} "
          f"({result['n_units']} units; (i)={i_all} (ii)={ii_all} "
          f"(iii)={iii_ok}; (iv) pending the 1e7 build gate)")
    print(f"[gate] report: {outdir}/gate_report.txt")
    return result


def _write_report(path: str, r: dict) -> None:
    """The human-readable report (the gate's deliverable)."""
    lines = []
    a = lines.append
    a('THE T6 DESIGN GATE REPORT (the v4 doc section 7)')
    a('=' * 64)
    a(f"config: {r['config']}   ec: {r['ec']}   n_games: {r['n_games']}")
    a(f"seed: {r['seed']}   pairs: {r['pairs']} "
      f"@ {r['pair_scale']}   features: {len(r['features'])}")
    a(f"VERDICT: {r['verdict']}   "
      f"((i)={r['criterion']['i_all']} "
      f"(ii)={r['criterion']['ii_all']} "
      f"(iii)={r['criterion']['iii']} "
      f"(iv)={r['criterion']['iv_build_gate_1e7']})")
    a(f"D0 rescale factor (1/sqrt(N)): {r['d0_rescale_factor']:.4f}")
    a('')
    a('TEST 1 (the table A1 + the phase-occupancy scan):')
    t1 = r['test1']
    a(f"  widths tested: {t1['widths_tested']}  "
      f"Bonferroni alpha: {t1['bonferroni_alpha']:.2e}  "
      f"worst phase p: {t1['worst_phase_p']:.3e}  "
      f"pass: {t1['phase_scan_pass']}")
    a('')
    a('TEST 2 (the stratified marginals — PRIMARY):')
    for k, v in sorted(r['test2_units'].items()):
        a(f"  {k:22s} D = {v['D']:.3e}   chi2 p = {v['p']:.2e}")
    a('')
    a('TEST 3 (the focused joints — PRIMARY):')
    for u in r['test3_joint_units']:
        tag = ' [small-k]' if u['small_k'] else ''
        a(f"  {u['pair']:18s} k={u['k']:4s} D = {u['D']:.3e}  "
          f"KL = {u['KL']:.3e}  p = {u['p']:.2e}{tag}")
    a(f"  family control: {r['criterion']['iii']['joint_family']}")
    a('')
    a('TEST 5 (the demoted pooled joint chi-square — reported):')
    for u in r['test5_demoted']:
        a(f"  {u['pair']:18s} stat = {u['stat']:.1f}  p = {u['p']:.2e}")
    a('')
    a('TEST 6 (the phase continuity):')
    for off, v in r['test6_phase_continuity'].items():
        a(f"  slot_base {off:8d}: {v}")
    a('')
    a('THE D0 NOISE (the q95 at the 1e6 scale, the top 10):')
    d0s = sorted(r['d0_q95_per_unit'].items(),
                 key=lambda kv: -kv[1])[:10]
    for k, v in d0s:
        a(f"  {k:28s} q95 = {v:.3e}")
    a('')
    a(f"timing: {r['timing_s']}")
    with open(path, 'w') as f:
        f.write('\n'.join(lines) + '\n')


def main() -> None:
    ap = argparse.ArgumentParser(description='the T6 design gate')
    ap.add_argument('--config',
                    default='src/reversi/test/data/rlm_03.json')
    ap.add_argument('--n-games', type=int, default=1_000_000)
    ap.add_argument('--ec', type=int, default=None)
    ap.add_argument('--seed', type=int, default=42)
    ap.add_argument('--pairs', type=int, default=20)
    ap.add_argument('--pair-scale', type=int, default=100_000)
    ap.add_argument('--wave-size', type=int, default=1_000_000)
    ap.add_argument('--outdir', default='scratch/gate_1e6')
    args = ap.parse_args()
    run_gate(args.config, args.n_games, args.ec, args.seed,
             args.pairs, args.pair_scale, args.wave_size, args.outdir)


if __name__ == '__main__':
    main()
