# ARCHIVED — read-only Burnside study for twolm.pattern (the
# formula↔enumeration ground-truth cross-check over 26 sample
# patterns), 2026-09-04. Purpose served: the D-032 Burnside
# attributes are in and pinned by test_pattern.py; the production
# formula lives in pattern.py and is documented in the mirror doc.
# Classification b2 (D-106 step 1, scratch/classification.md) — with
# the open option noted there: the formula↔enumeration sub-check
# could be revived as a standalone category-a probe if the pattern
# doc's "Verified invariants" section wants it. Results quoted in
# notes/decisions.md (D-032) and docs/src/twolm/pattern.md (the
# Burnside counts section; the principal-dict cross-check).
#!/usr/bin/env python
"""Read-only Burnside study for twolm.pattern (NO source modification).

Candidate formulas (G' = image of the mask-stabilizer on the S pattern
squares, i.e. the deduplicated induced permutations including identity):

  n_invariant = 3^B                  B = # orits of G' on the S squares
  n_unique    = (1/|G'|) * sum_{g} 3^{c(g)}    (Burnside on the 3^S configs)

Ground truth, computed independently:
  n_unique    <- p.principal_index_count  (production principal dict)
  n_invariant <- direct enumeration of all 3^S configurations, checking
                 digit invariance under every induced permutation
                 (vectorized numpy; does NOT use Burnside's theorem).
"""
import sys
sys.path.insert(0, "/home/rcrr/base/prj/dsh/src")

import numpy as np
from twolm.board import Bitboard, Square, bitboard_bsr, square_as_bitboard
from twolm.pattern import Pattern

SAMPLES = [
    ("ELLE", 0x107),
    ("SNAKE", 0xC30000000),
    ("EDGE", 0xFF),
    ("R2", 0xFF00),
    ("R3", 0xFF0000),
    ("R4", 0xFF000000),
    ("XEDGE", 0x42FF),
    ("DIAG3", 0x10204),
    ("DIAG4", 0x1020408),
    ("DIAG5", 0x102040810),
    ("DIAG6", 0x10204081020),
    ("DIAG7", 0x1020408102040),
    ("DIAG8", 0x102040810204080),
    ("CORNER", 0x70707),
    ("2X5COR", 0x1F1F),
    ("2X6COR", 0x3F3F),
    ("RCT2X4", 0x3C3C000000),
    ("CASTLE", 0xC3FF),
    ("BARBEL", 0x030304081020C0C0),
    ("MACE", 0x010204081020C0C0),
    ("FOURC", 0x8100000000000081),
    ("CORE", 0x1818000000),
    ("CORED", 0x241818240000),
    ("COREA", 0x8381C100000),
    ("WHIRL", 0x83800000000001C1),
    ("TAU", 0x010100C1C1000101),
    ("DOTA1", 0x1),
    ("DOTB1", 0x2),
    ("TWOND", 0x201),
]


def induced_perm(f, squares_int):
    """Permutation of f on the pattern squares: perm[i] = j with f(sq_i) = sq_j."""
    idx = {s: i for i, s in enumerate(squares_int)}
    perm = []
    for s in squares_int:
        img = f(square_as_bitboard(Square(s)))
        assert int(img) != 0, "transformation killed a square?"
        ipos = int(bitboard_bsr(img))
        assert ipos in idx, f"image square {ipos} not in pattern"
        perm.append(idx[ipos])
    return tuple(perm)


def cycle_lengths(perm):
    seen = [False] * len(perm)
    lens = []
    for i in range(len(perm)):
        if seen[i]:
            continue
        x, n = i, 0
        while not seen[x]:
            seen[x] = True
            n += 1
            x = perm[x]
        lens.append(n)
    return sorted(lens, reverse=True)


def cycle_type_str(perm):
    from collections import Counter
    cnt = Counter(cycle_lengths(perm))
    return " ".join(f"{k}^{v}" if v > 1 else f"{k}" for k, v in sorted(cnt.items()))


def group_orbits(perms, n):
    seen = [False] * n
    n_orb = 0
    for i in range(n):
        if seen[i]:
            continue
        n_orb += 1
        stack, seen[i] = [i], True
        while stack:
            x = stack.pop()
            for p in perms:
                y = p[x]
                if not seen[y]:
                    seen[y] = True
                    stack.append(y)
    return n_orb


def n_invariant_enumerated(S, perms):
    """Count configs fixed by every g in perms by full enumeration (no Burnside)."""
    N = 3 ** S
    pow3 = 3 ** np.arange(S, dtype=np.uint64)
    digits = ((np.arange(N, dtype=np.uint64)[:, None] // pow3[None, :]) % 3).astype(np.uint8)
    ok = np.ones(N, dtype=bool)
    for p in perms:
        pa = np.asarray(p, dtype=np.int64)
        ok &= np.all(digits == digits[:, pa], axis=1)
        if not ok.any():
            break
    return int(ok.sum())


def main():
    rows, all_ok, details = [], True, []
    for name, mask in SAMPLES:
        p = Pattern(name, Bitboard(np.uint64(mask)))
        squares_int = [int(s) for s in p.squares]
        S = len(squares_int)
        for f in p.symmetry_fs:  # sanity: symmetry_fs are mask stabilizers
            assert int(f(p.mask)) == int(p.mask), f"{name}: non-stabilizer in symmetry_fs"
        idp = tuple(range(S))
        G = [idp]
        for f in p.symmetry_fs:
            t = induced_perm(f, squares_int)
            if t not in G:
                G.append(t)
        burnsum = sum(3 ** len(cycle_lengths(g)) for g in G)
        assert burnsum % len(G) == 0, (name, burnsum, len(G))
        n_unique_formula = burnsum // len(G)
        B = group_orbits(G, S)
        n_inv_formula = 3 ** B
        n_inv_gt = n_invariant_enumerated(S, G)
        p.compute_principal_index_dict()
        n_unique_gt = int(p.principal_index_count)
        ok = n_inv_formula == n_inv_gt and n_unique_formula == n_unique_gt
        all_ok &= ok
        rows.append((name, S, int(p.n_stabilizers), len(p.symmetry_fs), len(G), B,
                     n_inv_formula, n_inv_gt, n_unique_formula, n_unique_gt,
                     "OK" if ok else "MISMATCH"))
        details.append((name, [cycle_type_str(g) for g in G]))

    print(f"{'pattern':<8} {'S':>2} {'nStab':>5} {'|sym|':>4} {'|G|':>3} "
          f"{'B':>2} {'3^B inv':>7} {'inv_enum':>8} {'n_unique':>7} {'uniq_gt':>7}  {'res':>8}")
    for r in rows:
        print(f"{r[0]:<8} {r[1]:>2} {r[2]:>5} {r[3]:>4} {r[4]:>3} {r[5]:>2} "
              f"{r[6]:>7} {r[7]:>8} {r[8]:>7} {r[9]:>7}  {r[10]:>8}")
    print()
    print("cycle types of each distinct induced permutation (id first):")
    for name, cts in details:
        print(f"  {name:<8}: " + "  ".join(cts))
    print()
    print("ALL MATCH" if all_ok else "MISMATCH FOUND")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
