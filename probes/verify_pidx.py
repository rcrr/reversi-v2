"""Re-derive principal-index dicts from first principles (board.py only)."""
import sys
import numpy as np
sys.path.insert(0, 'src')
from reversi.board import (Bitboard, bitboard_ro000, bitboard_ro090, bitboard_ro180,
                         bitboard_ro270, bitboard_fvert, bitboard_fh1a8,
                         bitboard_fhori, bitboard_fa1h8, bitboard_to_square_list,
                         square_as_bitboard)
SLOTS = [bitboard_ro000, bitboard_ro090, bitboard_ro180, bitboard_ro270,
         bitboard_fvert, bitboard_fh1a8, bitboard_fhori, bitboard_fa1h8]
SLOTN = ['ro000','ro090','ro180','ro270','fvert','fh1a8','fhori','fa1h8']


def val(x): return int.from_bytes(x.data, 'little')


def perm_of(mask, g):
    """Induced permutation on the pattern's squares (ascending bit order).
    perm[k] = j  such that  g(bits[k]) == bits[j]."""
    bits = sorted(i for i in range(64) if (mask >> i) & 1)
    pos = {b: k for k, b in enumerate(bits)}
    perm = []
    for b in bits:
        img = val(g(Bitboard(np.uint64(1 << b))))
        perm.append(pos[img.bit_length() - 1])
    return perm


def principal_dict(mask, sf_slots):
    """Recompute principal_index_dict. Applied = [ro000] + symmetry_fs."""
    bits = sorted(i for i in range(64) if (mask >> i) & 1)
    n = len(bits)
    total = 3 ** n
    perms = [perm_of(mask, SLOTS[s]) for s in [0] + sf_slots]
    pdict = []
    for idx in range(total):
        digs = [(idx // (3 ** k)) % 3 for k in range(n)]  # digit k at square bits[k]
        best = idx
        for perm in perms:
            # new digit at position j = old digit at position k where perm[k]==j
            inv = [0] * n
            for k, j in enumerate(perm):
                inv[j] = k
            newdig = [digs[inv[j]] for j in range(n)]
            v = 0
            for j, d in enumerate(newdig):
                v += d * (3 ** j)
            best = min(best, v)
        pdict.append(best)
    return np.array(pdict, dtype=np.uint32)

fails = []
def check(label, ok, detail=''):
    print(('PASS ' if ok else 'FAIL ') + label + (f'  {detail}' if detail and not ok else ''))
    if not ok: fails.append(label)

# ---- CORE (symmetry_fs = all 7 non-identity) ----
core_mask = 0x0000001818000000
core_golden = [
  0,  1,  2,  1,  4,  5,  2,  5,  8,  1,
  4,  5, 12, 13, 14, 15, 16, 17,  2,  5,
  8, 15, 16, 17, 24, 25, 26,  1, 12, 15,
  4, 13, 16,  5, 14, 17,  4, 13, 16, 13,
 40, 41, 16, 41, 44,  5, 14, 17, 16, 41,
 44, 25, 52, 53,  2, 15, 24,  5, 16, 25,
  8, 17, 26,  5, 16, 25, 14, 41, 52, 17,
 44, 53,  8, 17, 26, 17, 44, 53, 26, 53,
 80,
]
core = principal_dict(core_mask, [1,2,3,4,5,6,7])
check('CORE 81-entry principal dict', list(core) == core_golden)
cu = sorted(set(core_golden))
check('CORE unique principals (21)', cu == [0,1,2,4,5,8,12,13,14,15,16,17,24,25,26,40,41,44,52,53,80] and len(cu) == 21)

# ---- DIAG3 (symmetry_fs = [fa1h8] only) ----
diag3_mask = 0x0000000000010204
diag3_golden = [0,1,2,3,4,5,6,7,8,1,10,11,4,13,14,7,16,17,2,11,20,5,14,23,8,17,26]
diag3 = principal_dict(diag3_mask, [7])
check('DIAG3 27-entry principal dict', list(diag3) == diag3_golden)
d3u = sorted(set(diag3_golden))
check('DIAG3 unique principals (18)', d3u == [0,1,2,3,4,5,6,7,8,10,11,13,14,16,17,20,23,26] and len(d3u) == 18)

# ---- ELLE (symmetry_fs = [] -> identity) ----
elle_mask = 0x0000000000000107
elle = principal_dict(elle_mask, [])
check('ELLE identity principal dict (81 = range)', list(elle) == list(range(81)))

print()
if fails:
    print(f'{len(fails)} FAILURES: {fails}'); sys.exit(1)
print('ALL PRINCIPAL-DICT CHECKS PASSED')
