# reversi/mobility.py
The mobility feature of the Reversi engine: a scalar table-lookup feature counting the mover's legal moves masked by a
square set (`mask`), optionally combined with the opponent's pseudo-legal moves masked by a second set (`amask`).
Standard instances (the glossary in the class docstring): LMC = Legal Move Count (`popcount(lms)`), ALMC = Anti Legal
Move Count (`64 − popcount(alms)`), DLMC = Difference Legal Move Count (both all-64). Numba kernel, `Index` (uint32)
indexes.

## API

| name | contract |
|---|---|
| `Mobility(name: str, mask: Bitboard, amask: Bitboard)` | Strict `@validate_call` (any other type → `ValidationError`); sets `n_configurations = k + a + 1` and `n_instances = 1`; `__repr__`; `print()` the `[Mobility: name = {name:8s}, mask = 0x…, amask = 0x…]` line |
| `MobilitySet(name: str, mobilities: List[Mobility])` | Strict `@validate_call`; duplicate names or duplicate (mask, amask) pairs → `ValueError`; sorted storage; `sha3_256` hash over the 16 LE bytes per element in sorted order; `__repr__`; `names` / `masks` are `@property` |
| `MobilitySet.compute_indexes(positions: PositionArray) -> IndexArray` | The (N, L) uint32 index matrix via the Numba kernel; the column contract (docstring): column j is the j-th mobility in the set's SORTED (mask, amask) order, NOT the caller's insertion order — label columns with `ms.names` (a `@property`, not a method) |
| `popcount64(b)` | Public scalar/vectorized SWAR popcount, `@nb.vectorize(uint32(uint64), cache=True)`; OUT of `__all__` (test/inspection helper; the test file imports it by name) |

## Architecture

306 lines.

- Imports: `reversi.board` (Bitboard, BitboardArray, PositionArray, legal_moves, bitboard_count), `reversi.pattern`
  (only the `Index` / `IndexArray` type aliases, deliberate reuse), numpy, numba; `__all__` = [Mobility, MobilitySet].
- `Mobility`: the class docstring carries the LMC/ALMC/DLMC glossary + the index formula + the n_configurations
  semantics; `__init__`; `print`.
- `MobilitySet`: the docstring states the sorted-order contract; `__init__` (dup checks, sorted storage, hash); `names`,
  `masks` ((N, 2) uint64), `print_summary`, `compute_indexes`.
- Kernels: `popcount64` over `_numba_popcount64_kernel` (the SWAR UFunc); `_numba_compute_indexes_kernel` (`@nb.njit`,
  (N, L) output, scalar ops — only the output matrix is allocated).

The index formula (verified): `index = popcount(lms & mask) + (popcount(amask) − popcount(alms & amask))`. Range
`[0, k + a]` with every integer reachable, so **`n_configurations = k + a + 1` is the count of DISTINCT index values**
(the feature-table size), not `(k + 1)(a + 1)`. Underflow-safe: `popcount(alms & amask) ≤ a` always, so the kernel's
`shifts[j] − alms_count` never wraps. Overlapping mask/amask are legal (DLMC has both all-64 — a square in both
contributes +1 and −1); `lms ∩ alms` is not guaranteed empty, no special case.

The set hash = `sha3_256` over `mask.to_bytes(8, 'little') + amask.to_bytes(8, 'little')` per element in sorted order —
the `PatternSet.hash` construction style; order-insensitive; empty set → `sha3_256(b'')` (ACCEPTED — the deliberate
divergence from PatternSet fail-fast).

## Verified invariants

Pinned by the 5-section `probes/verify_mobility.py` + the 26-test suite (25 run + the PERF skip).

- popcount64 (section 1): scalar + vectorized vs `int.bit_count()` on 200,010 values (edge constants + 200,000 random
  64-bit) — zero mismatches; vectorized shape/dtype (uint32) exact.
- n_configurations (section 2): == the number of DISTINCT index values, brute force over all (lms, alms) subsets for 6
  (k, a) cases incl. the overlapping (4,4).
- compute_indexes (section 3): vs pure-Python ground truth on 200 random positions × 5 mobilities (LMC/ALMC/DLMC + 2
  partial masks, columns in sorted order) — all match; dtype/shape (N, L) uint32 exact.
- The golden (section 4): the suite's `[53, 13, 66]` re-derived independently — golden position (mover
  `0x40001ccaeb400024`, 17 stones; opponent `0x92fc6234143c7848`, 27 stones) has lms = `0x2c03810000820690` (13), alms =
  `0x2002810100838012` (11); sorted columns ALMC = 64−11 = 53, LMC = 13, DLMC = 13+53 = 66.
- The underflow boundary (section 6): mask = amask = 0xF, lms = 0, alms = 0x8 → index 3, kernel == ground truth.
- The standard-set hash (suite pin): `2e5535935d46d82a941ef87d43d22562735db9b6bf41db51d6eb6a8f21208a94` for the
  LMC/ALMC/DLMC triple — literal-pinned in test_hash_calculation_verification + test_print_summary.

## Open issues

None.

## Conventions

- `print` uses `{name:8s}` — names longer than 8 chars widen the column (cosmetic, deliberate).
- The empty list is accepted (harmless no-op) — the deliberate divergence from the PatternSet fail-fast.
- No PERF GATES anywhere — the 1M-position PERF test is print-only like every PERF test in the repo; the ±30% figure is
  a comparison discipline, not a gate.
- The kernel calls the vectorized popcount scalarly per (i, j) — a pure-njit scalar popcount would drop the UFunc
  dispatch; deliberate.
- `n_instances = 1` is CORRECT for a scalar feature (no symmetry-orbit family as in Pattern) — documented in the class
  docstring.
- The `IndexArray` import from pattern.py is deliberate (type-alias reuse: pydantic validates the return array on every
  call, the pattern.py `compute_principal_indexes` convention) — do not "simplify" it away without a decision.
- Board layout (bit = 8×(row−1)+(col−1)); the caller-checks-collisions contract does not apply (no principal / collision
  concept here).

## Integration

- The FEATURES pipeline level: wrk_features builds the level's `Mobility` objects from the config
  (`cfg_mset.mobility_features`); the feature order there is [INTERCEPT, ALMC, LMC, DLMC, EDGE, ELLE].
- `test_mobility.md` mirrors the suite; `pattern.md` is the sibling-module reference (hash construction, type-alias
  reuse).
