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
    #    brute force over all (lms, alms) subsets for small k, a
    #    (includes overlapping mask/amask cases)
    # ------------------------------------------------------------------
    def distinct_index_values(mask, amask):
        k = mask.bit_count()
        a = amask.bit_count()
        seen = set()
        # enumerate all subsets of mask (lms side) and of amask (alms side)
        # index = popcount(lms & mask) + (popcount(amask) - popcount(alms & amask))
        ms = [mask]
        bits = [i for i in range(64) if (mask >> i) & 1]
        subs = [0]
        for bit in bits:
            subs = subs + [s | (1 << bit) for s in subs]
        asubs = [0]
        for bit in [i for i in range(64) if (amask >> i) & 1]:
            asubs = asubs + [s | (1 << bit) for s in asubs]
        for u in subs:
            for v in asubs:
                seen.add((u & mask).bit_count() + a - (v & amask).bit_count())
        return len(seen)

    cases = [
        (0x3, 0x0),          # k=2 a=0  -> 3
        (0x0, 0x7),          # k=0 a=3  -> 4
        (0x3, 0x7),          # k=2 a=3  -> 6
        (0x5, 0xA),          # k=2 a=2  -> 5
        (0xF, 0xF),          # k=4 a=4, full overlap -> 9
        (0x0, 0x0),          # k=0 a=0  -> 1
    ]
    for mask, amask in cases:
        m = Mobility('CFG', Bitboard(mask), Bitboard(amask))
        brute = distinct_index_values(mask, amask)
        if m.n_configurations != brute:
            failures.append(f'n_configurations mask=0x{mask:x} amask=0x{amask:x}: '
                            f'class={m.n_configurations} brute={brute}')

    # ------------------------------------------------------------------
    # 3. compute_indexes vs pure-Python ground truth, random positions
    # ------------------------------------------------------------------
    mob_masks = [
        ('LMC', 0xFFFFFFFFFFFFFFFF, 0x0),
        ('ALMC', 0x0, 0xFFFFFFFFFFFFFFFF),
        ('DLMC', 0xFFFFFFFFFFFFFFFF, 0xFFFFFFFFFFFFFFFF),
        ('CORNERS', 0x8989898989898980, 0x0),
        ('MID', 0x3333CC3333CC3333, 0x0FF000FF000FF00),
    ]
    ms = MobilitySet('V', [Mobility(n, Bitboard(m), Bitboard(a))
                           for n, m, a in mob_masks])
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
        for j, (n, mk, amk) in enumerate(ordered):
            exp = (lms & mk).bit_count() + amk.bit_count() - (alms & amk).bit_count()
            if int(idx[0, j]) != exp:
                failures.append(f'compute_indexes pos {trial} {n}: '
                                f'kernel={int(idx[0, j])} expected={exp}')
                break
    # dtype / shape
    if idx.dtype != np.uint32 or idx.shape != (1, L):
        failures.append(f'compute_indexes dtype/shape: {idx.dtype} {idx.shape}')

    # ------------------------------------------------------------------
    # 4. the existing test golden [53, 13, 66] re-derived independently
    # ------------------------------------------------------------------
    mover = bitboard_from_signed_int(np.int64(4611717676283199524))
    opponent = bitboard_from_signed_int(np.int64(-7855295674223658936))
    lms = int(legal_moves(mover, opponent))
    alms = int(legal_moves(opponent, mover))
    std = [('LMC', 0xFFFFFFFFFFFFFFFF, 0x0),
           ('ALMC', 0x0, 0xFFFFFFFFFFFFFFFF),
           ('DLMC', 0xFFFFFFFFFFFFFFFF, 0xFFFFFFFFFFFFFFFF)]
    # columns in the set's sorted (mask, amask) order: ALMC, LMC, DLMC
    derived = [ (lms & mk).bit_count() + amk.bit_count() - (alms & amk).bit_count()
                for _, mk, amk in sorted(std, key=lambda t: (t[1], t[2])) ]
    print('golden re-derivation:', derived, '  test expects [53, 13, 66]')
    if derived != [53, 13, 66]:
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
    # 6. underflow boundary: alms_count can equal shift (max)
    # ------------------------------------------------------------------
    # mask=amask=0xF; craft lms=0, alms=0xF (all 4 in mask) -> index 0
    ml2 = [Mobility('U', Bitboard(0xF), Bitboard(0xF))]
    ms2 = MobilitySet('U', ml2)
    # find a real position: use the underflow test position from the suite
    mover = Bitboard(0x0000000000000010)
    opponent = Bitboard(0x00000000000000E0)
    idx2 = ms2.compute_indexes(np.full(1, make_position(mover, opponent)))
    lms2 = int(legal_moves(mover, opponent))
    alms2 = int(legal_moves(opponent, mover))
    exp2 = (lms2 & 0xF).bit_count() + 4 - (alms2 & 0xF).bit_count()
    print('underflow pos: lms=0x%x alms=0x%x kernel=%d expected=%d'
          % (lms2, alms2, int(idx2[0, 0]), exp2))
    if int(idx2[0, 0]) != exp2:
        failures.append('underflow position mismatch')

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
