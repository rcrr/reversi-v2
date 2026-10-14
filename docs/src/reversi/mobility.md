# reversi/mobility.py
The mobility feature of the Reversi engine: a scalar table-lookup feature counting the moves available for a player
over a square set (`mask`), selected by a side flag (`side`). The game rules define the available moves only for the
player to move: 'mover' counts the mover's legal moves (the mobility — the standard LMC, Legal Move Count, uses the
full-board mask); the anti-mobility is a feature-level definition: 'opponent' counts the moves the opponent would have
if it were the opponent's turn to move (the would-be moves — the standard ALMC, Anti Legal Move Count).
Numba kernel, `Index` (uint32) indexes.

## API

| name | contract |
|---|---|
| `Mobility(name: str, mask: Bitboard, side: Literal['mover', 'opponent'])` | Strict `@validate_call` (any other type → `ValidationError`); sets `n_configurations = k + 1` and `n_instances = 1`; `__repr__`; `print()` the `[Mobility: name = {name:8s}, mask = 0x…, side = …]` line |
| `MobilitySet(name: str, mobilities: List[Mobility])` | Strict `@validate_call`; duplicate names or duplicate (mask, side) pairs → `ValueError` (the SAME mask with the two sides is a valid pair — the standard LMC + ALMC); sorted storage; `sha3_256` hash over the 8 LE mask bytes + 1 side byte per element in sorted order; `__repr__`; `names` / `masks` are `@property` |
| `MobilitySet.compute_indexes(positions: PositionArray) -> IndexArray` | The uint32 index matrix of shape positions.shape + (L,) via the Numba kernel (a 1-D batch gives (N, L); any-shape batches supported, the 1-D path with no flatten copy); the column contract (docstring): column j is the j-th mobility in the set's SORTED (mask, side) order, NOT the caller's insertion order — label columns with `ms.names` (a `@property`, not a method) |
| `popcount64(b)` | Scalar/vectorized SWAR popcount (a test/inspection helper), `@nb.vectorize(uint32(uint64), cache=True)`; OUT of `__all__` (the test file imports it by name) |

## Architecture

- Imports: `reversi.board` (Bitboard, BitboardArray, PositionArray, legal_moves, bitboard_count), `reversi.index`
  (the `Index` / `IndexArray` type aliases), numpy, numba; `__all__` = [Mobility, MobilitySet].
- `Mobility`: the class docstring carries the LMC/ALMC glossary + the index formula + the n_configurations semantics;
  `__init__`; `print`.
- `MobilitySet`: the docstring states the sorted-order contract; `__init__` (dup checks, sorted storage, hash); `names`,
  `masks` ((N, 2) uint64: column 0 the mask, column 1 the side code 0 = mover / 1 = opponent), `print_summary`,
  `compute_indexes`.
- Kernels: `popcount64` over `_numba_popcount64_kernel` (the SWAR UFunc); `_numba_compute_indexes_kernel` (`@nb.njit`,
  (N, L) output, scalar ops — only the output matrix is allocated).

The index formula (verified): `index = popcount(lms & mask)` for `side = 'mover'`, `index = popcount(alms & mask)` for
`side = 'opponent'`. Range `[0, k]` with every integer reachable, so **`n_configurations = k + 1` is the count of
DISTINCT index values** (the feature-table size), not the number of (lms, alms) pairs.

The set hash = `sha3_256` over `mask.to_bytes(8, 'little') + <1 side byte: 0 mover / 1 opponent>` per element in sorted
order — the `PatternSet.hash` construction style; order-insensitive; empty set → `sha3_256(b'')` (ACCEPTED — the
deliberate divergence from PatternSet fail-fast).

## Verified invariants

Pinned by `probes/verify_mobility.py` (the 5 active sections: 1, 2, 3, 4, 6) and the suite.

- popcount64 (section 1): scalar + vectorized vs `int.bit_count()` on 200,010 values (edge constants + 200,000 random
  64-bit) — zero mismatches; vectorized shape/dtype (uint32) exact.
- n_configurations (section 2): == the number of DISTINCT index values, brute force over all mask subsets for 6
  (mask, side) cases incl. the same mask on both sides.
- compute_indexes (section 3): vs pure-Python ground truth on 200 random positions × 6 mobilities (the full-board
  LMC/ALMC pair + 2 partial masks on both sides, columns in sorted order) — all match; dtype/shape (N, L) uint32 exact.
- The golden (section 4): the suite's `[13, 11]` re-derived independently — golden position (mover
  `0x40001ccaeb400024`, 17 stones; opponent `0x92fc6234143c7848`, 27 stones) has lms = `0x2c03810000820690` (13), alms =
  `0x2002810100838012` (11); sorted columns LMC = 13, ALMC = 11.
- The N-D shape edges (suite): the (1,2) → (1,2,L), (2,1,2) → (2,1,2,L), F-order (1,2) parity and the empty
  (0,2) → (0,2,L) batches, element-wise as the 1-D call; the strict argument typing (None / list / str / plain
  ndarray → ValidationError, the subTest loop).
- The opponent-side boundary (section 6): mask = 0xF, side = opponent, the crafted position (mover E1, opponent
  F1/G1/H1 → alms = D1) → index 1, kernel == ground truth.
- The standard-set hash (suite pin): `d857e3c3e1d2fcadcea4d0125c69e518c74a34dc694598ac9ad57dda1e3037b8` for the
  LMC/ALMC pair — literal-pinned in test_hash_calculation_verification + test_print_summary.

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
- The `IndexArray` import from index.py is load-bearing (pydantic validates the return array on every call — the
  BeforeValidator rides on the Annotated alias).
- Board layout (bit = 8×(row−1)+(col−1)); the caller-checks-collisions contract does not apply (no principal / collision
  concept here).

## Integration

- The FEATURES pipeline level: wrk_features builds the level's `Mobility` objects from the config
  (`cfg_mset.mobility_features`); the feature order there is [INTERCEPT, LMC, ALMC, EDGE, ELLE].
- `test_mobility.md` mirrors the suite; `index.md` is the type-alias home reference; `pattern.md` the sibling-module
  reference (hash construction).
