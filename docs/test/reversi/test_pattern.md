# test/reversi/test_pattern.py
The pattern unit suite — 13 classes / 65 tests, 3 PERF-gated (1M-size pack, `compute_indexes_on_position`, set
`compute_principal_indexes`), ~1.1 s, no DB.

## Coverage

| class | tests | what it pins |
|---|---|---|
| `TestPattern` | 9 | constructor strictness (the strict `__init__`: 2 `ValidationError`, >18 squares `ValueError`), the ELLE attribute golden (tmasks, squares/snames, the counts, trans_fs/anti_trans_fs, snames_t), non-principal `ValueError` (BAD_ELLE), the R1 regression (FOURC 4-corners, the lowest-orbit-mask principal `0x8100000000000081`, + b1/a2/h2 edges), the `__repr__` golden |
| `TestPatternType` | 3 | the `PatternType` classification (strict init) |
| `TestPatternPack` | 7 | the 18-bitboard setUp (empty, full, rows 1-8, columns 1-8); pack-plan + scalar + vectorized goldens for ELLE, EDGE, R2, CORNER, DIAG8, FOURC (the `run_test_vectorized` helper: pack vs golden + unpack round-trip); PERF 1M over 5 patterns × tiled 18-board array (mixed-row kernels) |
| `TestPatternSymmetries` | 3 | the 29-row `symmetry_fs` table (the named patterns from ELLE to TWOND — per-row `subTest`) + the Burnside `n_invariant_configs`/`n_unique_configs` pins |
| `TestPatternMdpRecord` | 5 | the full 24-column `mdp_record()` strings (ELLE 4 squares, EDGE 8 squares) + the breadth additions |
| `TestTransformationsCayleyTable` | 4 | the 8 D8 functions in paper order (e, r, r2, r3, sv, sh, d1, d2) + the `trm = [0,1,2,3,4,6,7,5]` relabel to canonical D8 slot order (notes/naming.md); the 8×8 Cayley table checked as `cayley[i,j](data) == trs[j](trs[i](data))` on `ar`, 14 structural bitboards, and all 29 `sample_pattern_data` masks |
| `TestPatternPrint` | 1 | the EDGE `print()` full 13-line string golden |
| `TestPatternMdpCsvFile` | 5 | the `mdp_csv_file` classmethod via `mock_open` + `MagicMock(spec=Pattern)`; the 3 `TypeError` messages asserted with EXACT `assertEqual` |
| `TestPatternComputeIndexes` | 4 | scalar + 1-D array + multi-position row independence + PERF 1M |
| `TestPatternSet` | 12 | construction (duplicate names/masks `ValueError`s + the empty pattern list), the `names`/`masks` properties, the `hash` formula with the golden pinned, the `__repr__` / `print_summary` / `print` goldens |
| `TestPatternPrincipalIndex` | 1 | the single-pattern principal-index dict |
| `TestPatternComputePrincipalIndexDict` | 7 | the full principal-index dicts (9, 27, 81 entries) as `np.array` goldens |
| `TestPatternSetComputePrincipalIndexes` | 4 | scalar + 1-D + multi-position + PERF 1M |

## Goldens pinned

- Full-string goldens: the EDGE `print()` 13-line string, the `mdp_record` 24-column strings (ELLE/EDGE).
- `np.array` goldens: the pack-plan triples, the index vectors, the 49 first-row pipeline values, the principal-index
  dicts (9/27/81).
- The 29-row `symmetry_fs` table + the Burnside attributes, the `PatternSet.hash` golden literal, the `__repr__` golden.
- The shared position fixture (the board suite's pair, see test_board.md) is used by the 2 compute-indexes classes.

## Conventions

- Dual scalar/array API everywhere; the 1M size is behind `PERF=1`.
- Error paths: `assertRaises` + message substring (`"not principal"`, `"duplicate names"`, `"duplicate masks"`), EXCEPT
  `mdp_csv_file` where all three `TypeError` messages are exact `assertEqual`.
- Star import `from reversi.pattern import *` (the 6 `__all__` names) + explicit board-function imports; the Cayley test
  builds its OWN local 29-row pattern table (it does not use the star-imported `sample_pattern_data`).
- The module-level D8 fixture `ar` is the single Cayley exercise board (no pre-transformed copies).

## Integration

- Module under test: `pattern.md` (the pattern bitboard/packing layer — D8 transforms, pack plans, symmetry functions,
  base-3 configuration indexes, principal indexes, MDP record/CSV output).
- The mobility.md sibling shares the fixture position and the hash-construction idiom; the D8 naming rulings
  (notes/naming.md) apply to every D8 name here.
