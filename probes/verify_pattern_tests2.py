"""Independent re-derivation of test_pattern.py golden values.

Uses ONLY reversi.board (verified in the board campaign) + pure-Python math.
Does NOT import reversi.pattern, so the checks are non-circular.
"""
import sys
import numpy as np
sys.path.insert(0, 'src')
from reversi.board import (Bitboard, Square, square_as_bitboard,
                         bitboard_ro000, bitboard_ro090, bitboard_ro180,
                         bitboard_ro270, bitboard_fvert, bitboard_fh1a8,
                         bitboard_fhori, bitboard_fa1h8)

TRS = [bitboard_ro000, bitboard_ro090, bitboard_ro180, bitboard_ro270,
       bitboard_fvert, bitboard_fh1a8, bitboard_fhori, bitboard_fa1h8]

def B(v):
    return Bitboard(np.uint64(int(v)))

def val(x):
    return int.from_bytes(x.data, 'little')

failures = []
def check(label, ok, detail=''):
    print(('PASS ' if ok else 'FAIL ') + label + (f'  {detail}' if detail and not ok else ''))
    if not ok:
        failures.append(label)

# ---- A. Orbit / stabilizer / principal for all 29 sample masks (pure board math)
masks = [
    (0x0000000000000107, 'ELLE'),   (0x0000000C30000000, 'SNAKE'),
    (0x00000000000000FF, 'EDGE'),   (0x000000000000FF00, 'R2'),
    (0x0000000000FF0000, 'R3'),     (0x00000000FF000000, 'R4'),
    (0x00000000000042FF, 'XEDGE'),  (0x0000000000010204, 'DIAG3'),
    (0x0000000001020408, 'DIAG4'),  (0x0000000102040810, 'DIAG5'),
    (0x0000010204081020, 'DIAG6'),  (0x0001020408102040, 'DIAG7'),
    (0x0102040810204080, 'DIAG8'),  (0x0000000000070707, 'CORNER'),
    (0x0000000000001F1F, '2X5COR'), (0x0000000000003F3F, '2X6COR'),
    (0x0000003C3C000000, 'RCT2X4'), (0x000000000000C3FF, 'CASTLE'),
    (0x030304081020C0C0, 'BARBEL'), (0x010204081020C0C0, 'MACE'),
    (0x8100000000000081, 'FOURC'),  (0x0000001818000000, 'CORE'),
    (0x0000241818240000, 'CORED'),  (0x000008381C100000, 'COREA'),
    (0x83800000000001C1, 'WHIRL'),  (0x010100C1C1000101, 'TAU'),
    (0x0000000000000001, 'DOTA1'),  (0x0000000000000002, 'DOTB1'),
    (0x0000000000000201, 'TWOND'),
]
ok_os = ok_min = True
for mask, name in masks:
    orbit = sorted({val(TRS[i](B(mask))) for i in range(8)})
    n_orbit = len(orbit)
    if 8 % n_orbit != 0:
        ok_os = False
        print(f'   {name}: orbit {n_orbit} does not divide 8')
    if orbit[0] != mask:
        ok_min = False
        print(f'   {name}: mask is NOT the numeric orbit minimum (min=0x{orbit[0]:x})')
check('29 masks: orbit size divides 8 (|Orb|*|Stab|=8)', ok_os)
check('29 masks: each is the numeric minimum of its orbit (principal rule)', ok_min)

# ---- B. ELLE tmasks golden (8 orbit masks, D8 slot order)
m = B(0x107)
expected_tmasks = [0x107, 0x8080C0, 0xE080000000000000, 0x301010000000000,
                   0x80E0, 0xC080800000000000, 0x701000000000000, 0x10103]
computed = [val(TRS[i](m)) for i in range(8)]
check('ELLE tmasks golden (8 orbit masks, D8 slot order)', computed == expected_tmasks)

# ---- C. SMALL (0x18 = {D1,E1}) principal dict, pure base-3 (no pattern.py)
d = []
for i in range(9):
    d0, d1 = i % 3, (i // 3) % 3
    d.append(min(i, d1 + 3 * d0))
unique = sorted(set(d))
check('SMALL principal dict', d == [0, 1, 2, 1, 4, 5, 2, 5, 8], f'got {d}')
check('SMALL unique principals', unique == [0, 1, 2, 4, 5, 8] and len(unique) == 6, f'got {unique}')

# ---- D. D8 closure on ar + trm is a permutation
ar = 0x22120a0e1222221e
images = {val(TRS[h](B(ar))) for h in range(8)}
closure = all(val(TRS[k](B(val(TRS[j](B(ar)))))) in images
              for i in range(8) for j in range(8) for k in range(8))
check('D8 closure on ar', closure)
trm = [0, 1, 2, 3, 4, 6, 7, 5]
check('trm is a permutation of 0..7', sorted(trm) == list(range(8)))

# ---- E. Large-set arithmetic (13 patterns, sorted by mask value as PatternSet does)
large = [
    ('R2',     0x000000000000FF00), ('R3',     0x0000000000FF0000),
    ('R4',     0x00000000FF000000), ('XEDGE',  0x00000000000042FF),
    ('DIAG4',  0x0000000001020408), ('DIAG5',  0x0000000102040810),
    ('DIAG6',  0x0000010204081020), ('DIAG7',  0x0001020408102040),
    ('DIAG8',  0x0102040810204080), ('CORNER', 0x0000000000070707),
    ('2X5COR', 0x0000000000001F1F), ('RCT2X4', 0x0000003C3C000000),
    ('CORE',   0x0000001818000000),
]
large_sorted = sorted(large, key=lambda t: t[1])
expected_order = ['2X5COR', 'XEDGE', 'R2', 'CORNER', 'R3', 'DIAG4', 'R4',
                  'DIAG5', 'CORE', 'RCT2X4', 'DIAG6', 'DIAG7', 'DIAG8']
check('large-set pattern order (sorted by mask value)',
      [n for n, _ in large_sorted] == expected_order)
attribution = {  # from the test file (index, I, r0, r1)
    '2X5COR': (0, 8, 0, 7), 'XEDGE': (1, 4, 8, 11), 'R2': (2, 4, 12, 15),
    'CORNER': (3, 4, 16, 19), 'R3': (4, 4, 20, 23), 'DIAG4': (5, 4, 24, 27),
    'R4': (6, 4, 28, 31), 'DIAG5': (7, 4, 32, 35), 'CORE': (8, 1, 36, 36),
    'RCT2X4': (9, 2, 37, 38), 'DIAG6': (10, 4, 39, 42), 'DIAG7': (11, 4, 43, 46),
    'DIAG8': (12, 2, 47, 48),
}
J, ok_attr, ok_orbit_sizes = 0, True, True
for i, (name, mask) in enumerate(large_sorted):
    I = len({val(TRS[k](B(mask))) for k in range(8)})  # n_instances from first principles
    ei, eI, er0, er1 = attribution[name]
    if (ei, eI, er0, er1) != (i, I, J, J + I - 1):
        ok_attr = False
        print(f'   {name}: computed (i={i}, I={I}, r0={J}, r1={J+I-1}) != test ({ei}, {eI}, {er0}, {er1})')
    if I != len({val(TRS[k](B(mask))) for k in range(8)}):
        ok_orbit_sizes = False
    J += I
check(f'large-set J = {J}', J == 49)
check('large-set attribution (index, I, r0, r1) matches test goldens', ok_attr)

print()
if failures:
    print(f'{len(failures)} FAILURES: {failures}')
    sys.exit(1)
print('ALL CHECKS PASSED')
