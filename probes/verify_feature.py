#!/usr/bin/env python
#
# verify_feature.py — independent verification of the feature module goldens.
#
# Independence rules (same discipline as the mobility/pattern campaigns):
#  - NO import of twolm.feature (the module under test).
#  - reversi.board (proven kernel, 193/0/12 GREEN) is used ONLY for:
#      * the 8 D8 transformations / anti-transformations of masks/positions
#        (slot order canonized in notes/naming.md, D-014),
#      * legal_moves (proven game kernel).
#  - Everything else (orbits, base-3 indexes, principal min-reduction,
#    hashes, legal-move re-derivation cross-check) is pure Python arithmetic.
#
# Checks:
#   A. FeatureSet hash re-implemented from scratch (full 17-feature set).
#   B. Per-pattern n_instances (orbit sizes) in mask-sorted order.
#   C. compute_indexes golden: 3 positions x 10 columns, pure Python.
#   D. LMC cross-check: pure Python legal moves vs board.legal_moves.
#   E. Live structural check (imports twolm.feature only here):
#      factories, features order, n_instances, edge shapes, raises.
#
# Run: .venv/bin/python scratch/verify_feature.py
#

import hashlib
import sys

import numpy as np

from reversi.board import (Bitboard, make_position, legal_moves,
                         bitboard_transformations, bitboard_anti_transformations)

FULL = 0xFFFFFFFFFFFFFFFF

# ---------------------------------------------------------------------------
# Pure Python helpers (independent of twolm.feature)
# ---------------------------------------------------------------------------

def squares_of(mask):
    """Bit positions of a mask, ascending board order (A1 first)."""
    return [b for b in range(64) if (mask >> b) & 1]


def legal_moves_pure(mover, opponent):
    """Pure Python legal moves: 8-direction rays, standard Reversi rules."""
    empty = ~(mover | opponent) & FULL
    lm = 0
    for r in range(8):
        for c in range(8):
            b = 8 * r + c
            if not (empty >> b) & 1:
                continue
            for dr, dc in ((1, 0), (1, 1), (0, 1), (-1, 1),
                           (-1, 0), (-1, -1), (0, -1), (1, -1)):
                rr, cc = r + dr, c + dc
                seen_own = False
                while 0 <= rr < 8 and 0 <= cc < 8:
                    rb = 8 * rr + cc
                    if (opponent >> rb) & 1:
                        seen_own = True
                    elif (mover >> rb) & 1:
                        if seen_own:
                            lm |= 1 << b
                        break
                    else:
                        break
                    rr += dr
                    cc += dc
    return lm


def sym_index(mover, opponent, squares):
    """2*idx_o + idx_m with base-3 digits in ascending square order."""
    idx_m = idx_o = 0
    for k, s in enumerate(squares):
        p3 = 3 ** k
        if (mover >> s) & 1:
            idx_m += p3
        if (opponent >> s) & 1:
            idx_o += p3
    return 2 * idx_o + idx_m


def principal_columns(mover, opponent, mask):
    """
    Pure Python replica of PatternSet.compute_principal_indexes for ONE
    pattern. For each unique orbit mask of the 8 regular transforms
    (first-seen slot order), the column value is the minimum over the
    slot group of 2*idx_o + idx_m evaluated on the ANTI-transformed
    position (slot pairing s <-> s, per the D8 convention).
    """
    tmasks = [int(t) for t in bitboard_transformations(np.uint64(mask))]
    m_atr = [int(t) for t in bitboard_anti_transformations(np.uint64(mover))]
    o_atr = [int(t) for t in bitboard_anti_transformations(np.uint64(opponent))]
    sq = squares_of(mask)
    syms = [sym_index(m_atr[s], o_atr[s], sq) for s in range(8)]
    seen = []
    for t in tmasks:
        if t not in seen:
            seen.append(t)
    return [min(syms[s] for s in range(8) if tmasks[s] == g) for g in seen]


def orbit_size(mask):
    tmasks = [int(t) for t in bitboard_transformations(np.uint64(mask))]
    seen = []
    for t in tmasks:
        if t not in seen:
            seen.append(t)
    return len(seen), seen


def sha3_le(*values):
    return hashlib.sha3_256(b''.join(v.to_bytes(8, 'little') for v in values)).hexdigest()


# ---------------------------------------------------------------------------
# Test data (copied verbatim from test_feature.py)
# ---------------------------------------------------------------------------

PAT13 = [
    ('R2',     0x000000000000FF00),
    ('R3',     0x0000000000FF0000),
    ('R4',     0x00000000FF000000),
    ('XEDGE',  0x00000000000042FF),
    ('DIAG4',  0x0000000001020408),
    ('DIAG5',  0x0000000102040810),
    ('DIAG6',  0x0000010204081020),
    ('DIAG7',  0x0001020408102040),
    ('DIAG8',  0x0102040810204080),
    ('CORNER', 0x0000000000070707),
    ('2X5COR', 0x0000000000001F1F),
    ('RCT2X4', 0x0000003C3C000000),
    ('CORE',   0x0000001818000000),
]
MOB3 = [
    ('LMC',  0xFFFFFFFFFFFFFFFF, 0x0000000000000000),
    ('ALMC', 0x0000000000000000, 0xFFFFFFFFFFFFFFFF),
    ('DLMC', 0xFFFFFFFFFFFFFFFF, 0xFFFFFFFFFFFFFFFF),
]

POSITIONS = [
    (0x01054FD4327E1C10, 0xE8D03028C880C084),
    (0x40785CEAFB400004, 0x92042214043C7878),
    (0x01010389C34F5100, 0x607CBC743CB02400),
]

# Golden from test_feature.py TestFeatureSetComputeIndexes
GOLDEN = [
    [ 0,  4, 515, 5993, 2375,   13, 12, 32,  4, 14 ],
    [ 0,  8, 483,  110, 1517,   27, 29, 44, 41, 24 ],
    [ 0, 15,   0,  612, 1945, 1093, 22, 22, 19, 22 ],
]

# Golden from test_feature.py TestFeatureSet.test_init
GOLDEN_N_INSTANCES = [1, 1, 1, 1, 8, 4, 4, 4, 4, 4, 4, 4, 1, 2, 4, 4, 2]
GOLDEN_FEATURE_HASH = 'f5663932421232ba007622198625344deb9eb9aed58f8ad5c71eabc016b74167'
GOLDEN_MSET_HASH = '2e5535935d46d82a941ef87d43d22562735db9b6bf41db51d6eb6a8f21208a94'
GOLDEN_PSET_HASH = 'ff97ce55dcb0ebc5f4b62272dde7c3ead438b0feec2411fd258f68a7210040ea'

failures = 0

def check(label, got, want):
    global failures
    ok = got == want
    if not ok:
        failures += 1
    print(f"[{'OK' if ok else 'MISMATCH'}] {label}")
    if not ok:
        print(f"    got : {got}")
        print(f"    want: {want}")


# ---------------------------------------------------------------------------
# A. Hashes, re-implemented from scratch
# ---------------------------------------------------------------------------
print("=" * 72)
print("A. Hashes (re-implemented, no twolm.feature / no .hash attribute)")
print("=" * 72)

mob_sorted = sorted(MOB3, key=lambda t: (t[1], t[2]))
mset_hash = sha3_le(*[v for _, m, a in mob_sorted for v in (m, a)])
check("MobilitySet hash (3, sorted (mask,amask))", mset_hash, GOLDEN_MSET_HASH)
print(f"    mobilities sorted order: {[n for n, _, _ in mob_sorted]}")

pat_sorted = sorted(PAT13, key=lambda t: t[1])
pset_hash = sha3_le(*[m for _, m in pat_sorted])
check("PatternSet hash (13, sorted mask)", pset_hash, GOLDEN_PSET_HASH)
print(f"    patterns sorted order: {[n for n, _ in pat_sorted]}")

feat_hash = hashlib.sha3_256(
    b'INTERCEPT' + mset_hash.encode('utf-8') + pset_hash.encode('utf-8')
).hexdigest()
check("FeatureSet hash (INTERCEPT + mset + pset hex strings)",
      feat_hash, GOLDEN_FEATURE_HASH)

# ---------------------------------------------------------------------------
# B. Orbit sizes (n_instances) per pattern, mask-sorted order
# ---------------------------------------------------------------------------
print()
print("=" * 72)
print("B. Pattern orbit sizes (n_instances), mask-sorted order")
print("=" * 72)

ninst_pat = []
for name, m in pat_sorted:
    n, _ = orbit_size(m)
    ninst_pat.append(n)
    print(f"    {name:8s} mask=0x{m:016X}  n_instances={n}")
expected = [1, 1, 1, 1] + ninst_pat  # intercept + 3 mobilities + 13 patterns
check("full per-feature n_instances list (1+3+13)",
      expected, GOLDEN_N_INSTANCES)
check("sum (FeatureSet.n_instances)", sum(expected), 53)

# ---------------------------------------------------------------------------
# C. compute_indexes golden, pure Python (intercept + LMC + EDGE + DIAG4)
# ---------------------------------------------------------------------------
print()
print("=" * 72)
print("C. compute_indexes golden (pure Python)")
print("=" * 72)

EDGE = 0x00000000000000FF
DIAG4 = 0x0000000001020408

rows = []
for i, (m, o) in enumerate(POSITIONS):
    lmc_pure = legal_moves_pure(m, o).bit_count()
    lmc_kernel = int(legal_moves(np.uint64(m), np.uint64(o))).bit_count()
    check(f"pos {i}: LMC pure vs board.legal_moves", lmc_pure, lmc_kernel)
    cols = [0, lmc_pure]
    cols += principal_columns(m, o, EDGE)
    cols += principal_columns(m, o, DIAG4)
    check(f"pos {i}: 10-column row", cols, GOLDEN[i])
    rows.append(cols)

# ---------------------------------------------------------------------------
# D. Live structural check (only here we import twolm.feature)
# ---------------------------------------------------------------------------
print()
print("=" * 72)
print("D. Live structural check (twolm.feature)")
print("=" * 72)

import twolm.feature as F
from twolm.mobility import Mobility, MobilitySet
from twolm.pattern import Pattern, PatternSet

# D1. Factories
f_int = F.Feature.new_intercept()
# (D1 field pins — new_intercept / new_from_mobility / new_from_
#  pattern — deleted at D-106 step 3, class c: pinned by
#  test_feature.py::TestFeature::test_new_intercept /
#  test_new_from_mobility / test_new_from_pattern, all 5 fields
#  each. The f_int binding stays: D5 uses it; the m/f_mob and
#  p/f_pat bindings were used only by the deleted checks.)
# (D2 Feature() direct-construction RuntimeError deleted at D-106
#  step 3, class c: pinned by test_feature.py::TestFeature::
#  test_init_raises_runtime_error)
# (D3 FeatureSet structural — hash golden, n_instances 53,
#  len(features) 17, feature order, categories — deleted at D-106
#  step 3, class c: pinned by test_feature.py::TestFeatureSet::
#  test_init (the exact hash, the per-feature n_instances list, the
#  17-name order). The mset/pset bindings it defined were used only
#  by the deleted D4.)
# (D4 wrong-intercept ValueError deleted at D-106 step 3, class c:
#  pinned by test_feature.py::TestFeatureSet::
#  test_init_invalid_intercept_category_raises_value_error)

# D5. compute_indexes live vs pure Python matrix
ml = [x[0] for x in POSITIONS]
ol = [x[1] for x in POSITIONS]
positions = make_position(ml, ol)
small_mset = MobilitySet('S', [Mobility('LMC', Bitboard(FULL), Bitboard(0))])
small_pset = PatternSet('S', [Pattern('EDGE', Bitboard(EDGE)),
                              Pattern('DIAG4', Bitboard(DIAG4))])
small_fset = F.FeatureSet('S', f_int, small_mset, small_pset)
live = small_fset.compute_indexes(positions)
check("live compute_indexes matrix (3x10)",
      live.tolist(), rows)
check("live compute_indexes dtype", str(live.dtype), "uint32")

# D6. Edge shapes
empty_pos = make_position([], [])
check("N=0 shape", small_fset.compute_indexes(empty_pos).shape, (0, 10))
empty_fset = F.FeatureSet('E', None, None, None)
check("I=0 shape", empty_fset.compute_indexes(positions).shape, (3, 0))
check("N=0 & I=0 shape", empty_fset.compute_indexes(empty_pos).shape, (0, 0))
check("I=0 dtype", str(empty_fset.compute_indexes(positions).dtype), "uint32")

# D7. Wrong argument types for compute_indexes
import pydantic
for bad in [None, [1, 2], "invalid_string", np.array([1, 2])]:
    try:
        small_fset.compute_indexes(bad)
        check(f"compute_indexes({type(bad).__name__}) raises ValidationError",
              "no exception", "ValidationError")
    except pydantic.ValidationError:
        check(f"compute_indexes({type(bad).__name__}) raises ValidationError",
              "ValidationError", "ValidationError")
    except Exception as e:
        check(f"compute_indexes({type(bad).__name__}) raises ValidationError",
              f"{type(e).__name__}: {e}", "ValidationError")

# ---------------------------------------------------------------------------
print()
if failures:
    print(f"RESULT: {failures} MISMATCH(ES)")
    sys.exit(1)
print("RESULT: ALL CHECKS PASSED")
