# mobility.py analysis

_Analyzed 2026-08-28 (session 10). Source: 248 lines, added 2026-08-28
(commit 62748ca). Suite baseline: `twolm.test.test_mobility` 23/0/1
GREEN (1 skip = PERF gate). Environment: numpy 2.5.2, numba 0.67.0,
Python 3.12.3._

## What it is

`mobility.py` implements the **mobility feature** of the Reversi
engine: a scalar table-lookup feature that counts the mover's legal
moves, masked by a square set (`mask`), optionally combined with the
opponent's pseudo-legal moves masked by a second set (`amask`). The
three standard instances (per the test fixtures) are:

| name   | mask        | amask | meaning |
|--------|-------------|-------|---------|
| LMC    | all 64      | 0x0   | Legal-Moves Count: `popcount(lms)` |
| ALMC   | 0x0         | all 64 | Anti-LMC: `64 − popcount(alms)` (opponent's pseudo-moves, "as if the opponent had to move") |
| DLMC   | all 64      | all 64 | LMC − ALMC centered on 64: `popcount(lms) + 64 − popcount(alms)` — the classical mobility-difference feature |

The module exports `Mobility`, `MobilitySet`, `popcount64`
(`__all__`, L52-54).

## The feature index formula (verified)

For a `Mobility(name, mask, amask)` with `k = popcount(mask)`,
`a = popcount(amask)`, on a position with mover's legal moves `lms`
and opponent's legal moves `alms`:

```
index = popcount(lms & mask) + ( a − popcount(alms & amask) )
```

- **Range**: `index ∈ [0, k + a]`, every integer in the range is
  reachable by some (lms, alms) pair → **`n_configurations = k + a + 1`
  is the count of DISTINCT index values** (i.e. the feature-table
  size). It is *not* `(k+1)(a+1)` (the pair count). Brute-force
  verified for (k, a) ∈ {(2,0), (0,3), (2,3), (2,2), (4,4 overlapping),
  (0,0)} — all match the class value (this session,
  `scratch/verify_mobility.py`).
- **Underflow safety**: `popcount(alms & amask) ≤ popcount(amask) = a`
  always (intersection ⊆ amask), so the uint32 subtraction
  `shifts[j] − alms_count` in the kernel can never wrap; the kernel
  comment "Order matters, we must avoid incurring in an underflow"
  (L245) is correct. Boundary position verified live (mask = amask =
  0xF, lms = 0x0, alms = 0x8 → index 3, kernel == ground truth).
- **Overlapping mask/amask** are legal (DLMC has both = all 64): a
  square in both contributes +1 (as mover's move) and −1 (as
  opponent's move) where both masks cover it — the formula stays a
  well-defined count; the distinct-value range is still `[0, k+a]`.
- **lms ∩ alms is not guaranteed empty** (a square can sandwich
  opponent pieces in one direction and mover pieces in another):
  handled by the same formula, no special case needed.

## Architecture

```
mobility.py
├── Mobility                      (L58)  one feature: name, mask, amask
│   ├── __init__  @validate_call (L66)   strict types; n_configurations; n_instances = 1
│   └── print     @validate_call (L86)   "[Mobility: name = .., mask = 0x.., amask = 0x..]"
├── MobilitySet                   (L96)  ordered collection
│   ├── __init__  @validate_call (L104)  dup-name / dup-key checks; sorted storage; sha3_256 hash
│   ├── names()               (L141)     [str] in sorted order
│   ├── masks()               (L150)     (N, 2) uint64 array [[mask, amask], ...] sorted
│   ├── print_summary         (L163)     header (name, length, hash) + one line per mobility
│   └── compute_indexes       (L174)     (N, L) uint32 via Numba kernel
├── popcount64          @validate_call (L201)  public scalar/vectorized popcount
├── _numba_popcount64_kernel   (L208)  @nb.vectorize uint64 -> uint32 (SWAR)
└── _numba_compute_indexes_kernel (L223)  @nb.njit, (N, L) output, no temp allocations
```

Dependencies: `twolm.board` (Bitboard, BitboardArray, PositionArray,
legal_moves, bitboard_count) and `twolm.pattern` (**only** for the
`Index`/`IndexArray` type aliases, L39) — consistent with pattern.py's
own use of the same aliases.

### Construction — `Mobility.__init__` (L66-83)

Strict `@validate_call` (same D-023 style as Pattern): `name: str`,
`mask: Bitboard`, `amask: Bitboard`; any other type →
`pydantic.ValidationError`. No emptiness checks: `mask = amask = 0x0`
is accepted (a constant-zero feature, n_configurations = 1) — unlike
Pattern, which rejects the empty mask. `n_instances` is hardcoded 1:
mobility is a single scalar feature with no symmetry-orbit instances
(contrast: Pattern computes n_instances from its orbit, D-014
semantics). The class docstring (L60-62) is terse and grammatically
off ("Otherwise is the measure..."); see R1.

### Construction — `MobilitySet.__init__` (L104-139)

1. duplicate **names** → `ValueError('Mobilities list contains
   duplicate names')`;
2. duplicate **(mask, amask)** pairs → `ValueError('Mobilities list
   contains duplicate (mask, amask) pairs')` (checked as Python
   tuples, L123-125);
3. storage is **sorted by (mask, amask)** lexicographically (L129);
4. `hash = sha3_256` over the concatenation of `mask.tobytes() +
   amask.tobytes()` (8 LE bytes each) per element **in sorted order**
   (L133-137) — same construction style as `PatternSet.hash`
   (D-007 mirror). Verified independently: for the LMC/ALMC/DLMC
   triple the class hash is
   `2e5535935d46d82a941ef87d43d22562735db9b6bf41db51d6eb6a8f21208a94`,
   equal to a from-scratch reimplementation (this session);
   order-insensitive (reversed input → same hash); empty set →
   `sha3_256(b'')` (tested in `test_init_empty_list`).

**An empty list is accepted** (no fail-fast, unlike PatternSet which
rejects empty with a clear ValueError — minor-sweep #17). The suite
pins this behaviour deliberately (`test_init_empty_list`: name,
length 0, `names() == []`, `masks().shape == (0, 2)`, empty hash), so
it is intended; an empty mobility set is a harmless no-op. Noted as a
deliberate cross-module divergence (M4).

### Output column layout (implicit) — **verified trap**

`compute_indexes` builds its `masks`/`amasks` arrays from
`self.mobilities` — the **sorted** storage — so **column j of the
returned (N, L) array is the j-th mobility in sorted (mask, amask)
order, not in the caller's insertion order** (L189-190). The
docstring does not say this (R2). Live proof (this session): a set
inserted as [LMC, ALMC, DLMC, CORNERS, MID] returns columns in order
[ALMC, MID, CORNERS, LMC, DLMC]. The suite's golden
`[53, 13, 66]` is in sorted order: ALMC = 64 − 11 = 53, LMC = 13,
DLMC = 13 + 53 = 66 for the golden position (13 mover moves, 11
opponent pseudo-moves — see "Verified"). Callers labelling columns
must use `ms.names()` / `ms.masks()`, which return the same sorted
order — consistent, but easy to miss.

### compute_indexes (L174-194)

`@validate_call` with `positions: PositionArray → IndexArray`.
Pipeline: `lms = legal_moves(mover, opponent)`,
`alms = legal_moves(opponent, mover)` (board.py Numba kernel, scalar
and array paths verified identical this session), then per-element
precomputation `shifts = np.bitwise_count(amasks)` (NumPy 2.0+ API;
numpy 2.5.2 here) and the JIT kernel:

```
indexes[i, j] = popcount(lms[i] & masks[j])
              + (uint32(shifts[j]) − popcount(alms[i] & amasks[j]))
```

Only the output matrix is allocated (L231); scalar ops, no temporaries
inside the loops. The `IndexArray` return annotation (with its
`BeforeValidator` dtype check, pattern.py L74) means pydantic also
validates the return array on every call — identical convention to
pattern.py `compute_principal_indexes` (L1149), so consistent, not a
defect.

### popcount64 (L201-220)

Public scalar/vectorized 64-bit popcount: a classic SWAR (Hacker's
Delight-style) implementation wrapped in `@nb.vectorize(
nb.uint32(nb.uint64), cache=True)` — expands to NumPy UFunc arrays.
Docstring: "Used to test the numba kernel." — ambiguous status: it is
in `__all__` and used by the kernel, but the docstring reads like a
test helper (R3). Verified against `int.bit_count()` on 200,010
values (edge constants + 200,000 random 64-bit), both scalar and
vectorized calls — zero mismatches; vectorized output shape/dtype
(uint32) exact.

## Verified (this session, 2026-08-28)

Independent ground truth = pure-Python `int.bit_count()` +
board.py `legal_moves` (itself suite-verified). Script:
`scratch/verify_mobility.py` (untracked, per convention).

| # | fact | result |
|---|------|--------|
| V1 | popcount64 scalar, 200,010 values (incl. 0x5555…, 0x8000…, 0xFF… masks) | == `int.bit_count()` |
| V2 | popcount64 vectorized, same array | shape/dtype/elements exact |
| V3 | n_configurations == distinct index values, brute force, 6 (k, a) cases incl. overlapping masks | all match |
| V4 | compute_indexes vs pure Python, 200 random positions × 5 mobilities (LMC/ALMC/DLMC + 2 partial masks) | all match (columns in sorted order) |
| V5 | suite golden [53, 13, 66] re-derived: golden position (mover `0x40001ccaeb400024`, 17 stones; opponent `0x92fc6234143c7848`, 27 stones) has lms = `0x2c03810000820690` (13), alms = `0x2002810100838012` (11) → ALMC 53, LMC 13, DLMC 66 | match |
| V6 | hash formula re-implemented from scratch (sorted pairs, 16 LE bytes each, sha3_256); order-insensitivity; empty-set hash | all match |
| V7 | underflow boundary: mask = amask = 0xF, lms = 0, alms = 0x8 → 3 | kernel == ground truth |
| V8 | legal_moves scalar vs array path on the same position | identical |
| V9 | full suite baseline | 23/0/1 GREEN |

## Real issues (candidates for fix, priority order)

_Roberto's standing rule: per-item proposal, apply only on explicit
approval. **R1-R6 all approved and applied 2026-08-28 (D-035, batch
commit); suite 23/0/1 GREEN throughout (no behavior change).**_

- **R1 — Mobility/MobilitySet docstrings (doc-only). DONE (D-035).** The
  class docstring L59-63 was grammatically broken ("Otherwise is the
  measure of...") and did not state the index formula or what
  `n_configurations` counts. Rewritten with the verified formula,
  the n_configurations semantics, and the n_instances note; the set
  docstring's "mast" typo and "a ascending" fixed, sorted-order
  clause added.
- **R2 — compute_indexes docstring (doc-only). DONE (D-035).** Now
  states the full contract: formula, args/returns, and the column
  order rule (sorted (mask, amask) order, same as names/masks, NOT
  insertion order).
- **R3 — popcount64 status (design call). DONE (D-035, option b).**
  Roberto: removed from `__all__` (test/inspection helper, not
  public API); the upcoming engine "may not be Python — we'll see".
  Direct import in the test file unaffected.
- **R4 — dead imports (hygiene, code). DONE (D-035).**
  `bitboard_transformations` (L34) and `square_from_str` (L36)
  removed.
- **R5 — API-shape consistency with PatternSet (consistency, code).
  DONE (D-035).** `names`/`masks` now `@property` (D-024 alignment);
  `__repr__` added to both classes (pattern-style one-liner); 4 test
  call-sites updated; docstring references updated.
- **R6 — n_instances = 1 (left as-is, decision). DONE (D-035).**
  Correct for a scalar feature: the index is a single uint32 computed
  directly from the (mask, amask) pair — no family of symmetric
  instances with separate tables as in Pattern. Doc note shipped
  with R1.

## Minor issues / inconsistencies

_All five noted items disposed 2026-08-28 (D-036), per Roberto:
M1 applied (glossary), M2/M3/M5 left as-is, M4 corrected (it was
mis-stated — see below)._

- **M1 — abbreviation glossary. DONE (D-036).** LMC / ALMC / DLMC
  were never expanded in the module. Canonical expansions confirmed
  by Roberto (from the 2008 program) and shipped in the Mobility
  class docstring: LMC = Legal Move Count, ALMC = Anti Legal Move
  Count, DLMC = Difference Legal Move Count.
- **M2 — Mobility name padding.** `print` uses `{self.name:8s}` —
  names longer than 8 chars widen the column (no truncation, no
  error). Cosmetic; **left as-is** per Roberto.
- **M3 — empty-set acceptance.** Deliberate (tested) and diverges
  from PatternSet fail-fast; **left as-is** per Roberto
  ("lasciamo così").
- **M4 — no PERF gate (corrected).** The suite's PERF test (1M
  positions) prints throughput and asserts no threshold — and
  neither do the board or pattern PERF tests: all PERF tests in
  this repo are print-only (they assert output correctness, not a
  performance target). The ±30% figure in NOTES.md is the
  campaign comparison discipline (within-campaign deltas are noise;
  never compare across sessions/machines), not a test gate. The
  original analysis text claimed the board suite "carries ±30%
  gates" — that was wrong; corrected here.
- **M5 — kernel per-element UFunc call.** The inner loop calls the
  `@nb.vectorize`d popcount scalarly per (i, j); a pure `@nb.njit`
  scalar popcount (or per-row vectorization) could remove the UFunc
  dispatch overhead. Observation only — **left as-is** per Roberto
  ("E' un TEST"); any change would be PERF-gated engine work.

## Conventions to respect in any new work on this file

- Board bit layout (D-013 naming, verified): bit = 8×(row−1)+(col−1);
  A1 = bit 0 … H8 = bit 63. Masks in fixtures use this layout.
- The D-025 contract (caller checks collisions) does not apply here:
  `compute_indexes` has no principal/collision concept — it is a
  pure (N) → (N, L) map; no precondition on the positions array.
- Index dtype is `Index` (np.uint32); `n_configurations ≤ 129` for
  any 64-square mask pair, far inside uint32.
- `IndexArray` import from pattern.py is deliberate (type-alias
  reuse, return-value validation) — do not "simplify" it away without
  a decision.
- Doc mirror (D-007): this file documents src/twolm/mobility.py.

## Verdict

A small, **correct** module: the Numba kernel, the popcount SWAR, the
hash construction, and the n_configurations semantics all check out
against independent ground truth (V1–V8, zero mismatches; 200-position
random differential testing). The suite (23/0/1) covers construction,
both collision checks, sorting, hash equivalence, print goldens,
underflow boundary, empty set, empty positions, and 32-line popcount
goldens. The module-side gaps (R1–R6: documentary, consistency,
dead imports, n_instances) were all approved and applied the same
day (D-035 batch). What remains is the test file itself (to be
analyzed next as `docs/src/twolm/test/test_mobility.md` —
preliminary observations: a dead `if False:` block in
`TestMobilitySet.test_init` with no live assertion, three
"raises_assertion" names, hash self-comparisons in
`test_hash_calculation_verification`/`test_print_summary`, and no
multi-position row-independence test for `compute_indexes` — the
known T-patterns from test_pattern.py). No real logic defect found
in this session.
