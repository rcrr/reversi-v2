# reversi/test/test_board.py
The board unit suite — 43 classes / 193 tests (161 defined + 32
inherited through the 8 D8 blueprint subclasses), 12 PERF-gated
(`@skipUnless(PERF == '1')`), ~1.3 s. Companion of
docs/src/reversi/board.md. The file is 2377 lines.

## Coverage

| area (classes) | tests | what it pins |
|---|---|---|
| A — Square/Move/bitboard primitives (TestSquare L89: 10, TestMove L168: 10, TestBitboardFromSignedInt L265: 5, TestBitboardToSignedInt L314: 6, TestBitboardFromHexStr L374: 7, TestBitboardBsr L441: 2, TestBitboardPrint L476: 1, TestBitboardCount L501: 2, TestBitboardTransformationFa1h8Comp L512: 1) | 44 | construction + the special codes (PA/NA/UN → 64/65/66), the R3 `uint64(1)<<64 → 0` wrap documented in the as_bitboard tests, from/to signed-int (the zero-copy view + the bare-int ValidationError + the pydantic v2 major pin), hex (16-char, case-insensitive, error paths), bsr (Python int), the 9-line print golden, count (empty/full/ar), the fa1h8 composition pinned to the golden constant |
| B — D8 transformations (BaseBitboardTransformationTest L544 blueprint 4×8; 8 concrete L642-719: 32 inherited; TestBitboardTransformations L730: 7, TestBitboardAntiTransformations L819: 4, TestBitboardD8GroupLaw L878: 5, TestBitboardToSquareList L920: 3, TestBitboardToSquareArray L945: 3, TestBitboardToStringList L988: 3) | 57 | the 14 structural (input, expected) pairs per primitive (112 values, hand re-derived), scalar + vector + wrong-type + PERF 1M per primitive, the orbit slots (the 1↔3 anti swap), the anti-path error branches, the D8 GROUP LAW (identity as property, ro090∘ro090 == ro180, anti∘transform == identity), to_string_list, full-board inputs |
| C — position creation/eq/print/empties/legal moves (TestPositionCreation L1015: 7, TestPositionEq L1147: 11, TestPositionFieldValidation L1273: 2, TestPositionPrint L1293: 6, TestPositionEmpties L1390: 5, TestPositionLegalMoves L1471: 11) | 42 | the `ar`/`opponent` shared fixture (0x40001ccaeb400024 / 0x92fc6234143c7848), the 9-line position print golden, per-field position_eq + the PositionField SkipValidation hole pinned, the 120-row legal-moves bulk (external reference, 3 construction paths incl. zero-copy) + the 4 error branches, the 2-D "must be 1D" message verbatim |
| D — game ops/endgame/D8 (TestPositionCollisions L1742: 2, TestPositionCheckCollisions L1773: 5, TestPositionLegalMovesCount L1851: 1, TestPositionFlips L1864: 6, TestPositionMakeMove L2014: 6, TestPositionCountDifference L2073: 1, TestPositionFinalValue L2083: 7, TestPositionHasToPass L2141: 2, TestPositionIsGameOver L2157: 3, TestPositionIsMoveLegal L2184: 4, TestPositionTrFunctions L2235: 8, TestPositionTransformations L2282: 2, TestPositionAntiTransformations L2326: 2) | 49 | the collision message substrings, the R2 early-return triggers (all three), the R1 None-on-illegal pin, the PA-swap branches (the explicit `move == 64`), the 3 WOFC branches, the NOT-FULL is_game_over true case via the PA-swap path, the updated-position asserts in the flips bulk, lowercase rejections |
| E — meta (TestPydanticVersion L2370: 1) | 1 | the pydantic v2 major version (the R4 pin depends on pydantic v2 non-coercion) |

## Goldens pinned

- The `ar` board print 9-line string (mover 17 / opponent 27 /
  empties 13) + the position print 9-line string.
- The 112 D8 primitive pairs + the orbit slot order + the 120-row
  legal-moves bulk (all independently re-derived at analysis time —
  zero mismatches; the value base of the suite).
- The `ar_reflection_a1h8`/`ar_reflection_h1a8` header constants.
- The pydantic v2 major.

## Conventions

- The header constants (L78-86 area) keep their transposed-looking
  names (row_1 = file a, ...) — REJECTED as a defect: this
  is Reversi, not chess; the canonical row/column vocabulary is
  notes/naming.md. No rename done (or to do).
- The D8 diagram docstrings were refuted cell-by-cell:
  all match the code under the canonical convention; only the
  "rotaded" typo stood (fixed in board.py).
- PERF gates measure (b/s print), never fail on slowness; the 1M
  populations are uniform (`np.tile`/`np.full`).
- The shared fixture pair is disjoint (`mover & opponent == 0`), so
  the Area-C collision checks pass trivially there; the raise path is
  exercised only in TestPositionCheckCollisions.

## Integration

- Module under test: `board.md` (the engine core: Square/Move,
  bitboards, D8, positions, legal moves, WOFC).
- The same position fixture is shared with the pattern / mobility
  suites; the naming rulings (notes/naming.md) are the
  canonical reference for every name in this file.
