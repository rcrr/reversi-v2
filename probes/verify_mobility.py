#
# verify_mobility.py
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

#
# verify_mobility.py — independent verification of reversi/mobility.py
#
# Ground truth: pure-Python popcount (int.bit_count) + board.legal_moves
# (independently verified by the board suite).
#
import random

import numpy as np

from reversi.board import (Bitboard, bitboard_from_signed_int,
                         legal_moves, make_position)
from reversi.mobility import Mobility, MobilitySet, popcount64


def main():
    rng = random.Random(20260828)
    failures = []

    # ------------------------------------------------------------------
    # 1. popcount64 (scalar + vectorized) vs int.bit_count
    # ------------------------------------------------------------------
    specials = [0, 1, 2, 0x5555555555555555, 0xAAAAAAAAAAAAAAAA,
                0x1, 0x8000000000000000, 0xFFFFFFFFFFFFFFFF,
                0x0F0F0F0F0F0F0F0F, 0x3333333333333333]
    values = specials + [rng.getrandbits(64) for _ in range(200_000)]
    bad = 0
    for v in values:
        b = Bitboard(v)
        if int(popcount64(b)) != v.bit_count():
            bad += 1
    if bad:
        failures.append(f'popcount64 scalar: {bad}/{len(values)} mismatches')
    arr = np.array(values, dtype=Bitboard)
    ref = np.array([v.bit_count() for v in values], dtype=np.uint32)
    got = popcount64(arr)
    if not (got.shape == ref.shape and got.dtype == np.uint32 and
            (got == ref).all()):
        failures.append('popcount64 vectorized mismatch')

    # ------------------------------------------------------------------
    # 2. n_configurations == number of DISTINCT index values
    #    brute force over all subsets of the mask, both sides
    # ------------------------------------------------------------------
    def distinct_index_values(mask, side):
        seen = set()
        # enumerate all subsets of mask for the side's legal moves
        # index = popcount(lms & mask)  (mover) / popcount(alms & mask) (opponent)
        subs = [0]
        for bit in [i for i in range(64) if (mask >> i) & 1]:
            subs = subs + [s | (1 << bit) for s in subs]
        for u in subs:
            seen.add((u & mask).bit_count())
        return len(seen)

    cases = [
        (0x3, 'mover'),      # k=2 -> 3
        (0x7, 'opponent'),   # k=3 -> 4
        (0xF, 'mover'),      # k=4 -> 5
        (0xF, 'opponent'),   # k=4, same mask other side -> 5
        (0x5, 'mover'),      # k=2 -> 3
        (0x0, 'mover'),      # k=0 -> 1
    ]
    for mask, side in cases:
        m = Mobility('CFG', Bitboard(mask), side)
        brute = distinct_index_values(mask, side)
        if m.n_configurations != brute:
            failures.append(f'n_configurations mask=0x{mask:x} side={side}: '
                            f'class={m.n_configurations} brute={brute}')

    # ------------------------------------------------------------------
    # 3. compute_indexes vs pure-Python ground truth, random positions
    # ------------------------------------------------------------------
    mob_masks = [
        ('LMC', 0xFFFFFFFFFFFFFFFF, 'mover'),
        ('ALMC', 0xFFFFFFFFFFFFFFFF, 'opponent'),
        ('CORNERS', 0x8989898989898980, 'mover'),
        ('CORNERS_O', 0x8989898989898980, 'opponent'),
        ('MID', 0x3333CC3333CC3333, 'mover'),
        ('MID_O', 0x3333CC3333CC3333, 'opponent'),
    ]
    ms = MobilitySet('V', [Mobility(n, Bitboard(m), s)
                           for n, m, s in mob_masks])
    L = len(mob_masks)
    N = 200
    for trial in range(N):
        mover = rng.getrandbits(64)
        opp = rng.getrandbits(64) & ~mover
        m_bb, o_bb = Bitboard(mover), Bitboard(opp)
        lms = int(legal_moves(m_bb, o_bb))
        alms = int(legal_moves(o_bb, m_bb))
        positions = np.full(1, make_position(m_bb, o_bb))
        idx = ms.compute_indexes(positions)
        # columns follow the SET'S SORTED order, not the input list order
        ordered = sorted(mob_masks, key=lambda t: (t[1], t[2]))
        for j, (n, mk, sd) in enumerate(ordered):
            exp = (lms if sd == 'mover' else alms) & mk
            exp = exp.bit_count()
            if int(idx[0, j]) != exp:
                failures.append(f'compute_indexes pos {trial} {n}: '
                                f'kernel={int(idx[0, j])} expected={exp}')
                break
    # dtype / shape
    if idx.dtype != np.uint32 or idx.shape != (1, L):
        failures.append(f'compute_indexes dtype/shape: {idx.dtype} {idx.shape}')

    # ------------------------------------------------------------------
    # 4. the existing test golden [13, 11] re-derived independently
    # ------------------------------------------------------------------
    mover = bitboard_from_signed_int(np.int64(4611717676283199524))
    opponent = bitboard_from_signed_int(np.int64(-7855295674223658936))
    lms = int(legal_moves(mover, opponent))
    alms = int(legal_moves(opponent, mover))
    std = [('LMC', 0xFFFFFFFFFFFFFFFF, 'mover'),
           ('ALMC', 0xFFFFFFFFFFFFFFFF, 'opponent')]
    # columns in the set's sorted (mask, side) order: LMC, ALMC
    derived = [ ((lms if sd == 'mover' else alms) & mk).bit_count()
                for _, mk, sd in sorted(std, key=lambda t: (t[1], t[2])) ]
    print('golden re-derivation:', derived, '  test expects [13, 11]')
    if derived != [13, 11]:
        failures.append(f'golden mismatch: {derived}')

    # ------------------------------------------------------------------
    # 5. (deleted at D-106 step 3, class c): hash formula,
    #    order-insensitivity and empty-set hash are pinned by
    #    test_mobility.py::TestMobilitySet::test_hash_calculation_
    #    verification / test_hash_equivalence_same_keys /
    #    test_init_empty_list (the latter also pins e.masks' (0, 2)
    #    shape — the group 5 b1-mod re-pin of step 2 collapses there)
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # 6. opponent-side boundary: the raw opponent count over the mask
    # ------------------------------------------------------------------
    # mask=0xF, side=opponent; the position has the mover on E1 (no legal
    # moves) and the opponent on F1, G1, H1 (one legal move, D1) -> index 1
    ml2 = [Mobility('U', Bitboard(0xF), 'opponent')]
    ms2 = MobilitySet('U', ml2)
    mover = Bitboard(0x0000000000000010)
    opponent = Bitboard(0x00000000000000E0)
    idx2 = ms2.compute_indexes(np.full(1, make_position(mover, opponent)))
    alms2 = int(legal_moves(opponent, mover))
    exp2 = (alms2 & 0xF).bit_count()
    print('opponent-side pos: alms=0x%x kernel=%d expected=%d'
          % (alms2, int(idx2[0, 0]), exp2))
    if int(idx2[0, 0]) != exp2:
        failures.append('opponent-side position mismatch')

    # ------------------------------------------------------------------
    print()
    if failures:
        print('FAILURES:')
        for f in failures:
            print(' -', f)
    else:
        print('ALL CHECKS PASSED')


if __name__ == '__main__':
    main()
