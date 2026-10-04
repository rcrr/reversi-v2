# test/reversi/test_board.py
The board unit suite — 50 classes / 274 tests (+ the 32 inherited from the 8 D8 blueprint subclasses = 308), 8
PERF-gated (`@skipUnless(PERF == '1')`). Companion of docs/src/reversi/board.md.

## Coverage

| area (classes) | tests | what it pins |
|---|---|---|
| A — Square/Move/bitboard primitives (TestSquare 10, TestMove 11, TestBitboardFromSignedInt 9, TestBitboardToSignedInt 10, TestBitboardFromHexStr 10, TestBitboardBsr 2, TestBitboardPrint 1, TestBitboardCount 3, TestBitboardTransformationFa1h8Comp 1) | 57 | construction + the named move codes (`MOVE_PA` / `MOVE_NA` / `MOVE_UN` pinned to 64/65/66 and to the `move_from_str` names), the `uint64(1) << 64 → 0` wrap of the non-square codes in `move_as_bitboard` (pinned as-is), from/to signed-int (the zero-copy view + the bare-int ValidationError + the pydantic v2 major pin), hex (16-char, case-insensitive, error paths), bsr (Python int), the 9-line print golden, count (empty/full/ar), the fa1h8 composition pinned to the golden constant |
| B — D8 transformations (the BaseBitboardTransformationTest blueprint 4×8; the 8 concrete classes: 32 inherited + 29 own (the 2-D / 3-D / non-contiguous / empty shape tests: all 8 classes, ro090 2-D only); TestBitboardTransformations 10, TestBitboardAntiTransformations 7, TestD8FunctionTables 3, TestNumbaReflectionOverloads 2, TestBitboardD8GroupLaw 6, TestBitboardToSquareList 3, TestBitboardToSquareArray 3, TestBitboardToStringList 3) | 98 | the 14 structural (input, expected) pairs per primitive (112 values, hand re-derived), scalar + vector + wrong-type + PERF 1M per primitive, the orbit slots (the 1↔3 anti swap), the anti-path error branches, the D8 GROUP LAW (identity as property, ro090∘ro090 == ro180, anti∘transform == identity), the numba overload reflection, to_string_list, full-board inputs |
| C — position creation/eq/print/empties/legal moves (TestPositionCreation 8, TestInitialGame 1, TestPositionEq 11, TestPositionFieldValidation 2, TestPositionPrint 6, TestPositionEmpties 5, TestPositionEmptyCount 5, TestPositionLegalMoves 16) | 54 | the `ar`/`opponent` shared fixture (0x40001ccaeb400024 / 0x92fc6234143c7848), the `make_position` inputs-never-aliased pin (arrays + lists), the official Othello start (initial_game_position), the 9-line position print golden, per-field position_eq + the PositionField SkipValidation hole pinned, the 123-row legal-moves bulk (external reference, 3 construction paths incl. zero-copy) + the 4 error branches (the same-shape ValueError verbatim, the dtype rejection, the mixed-kind TypeError), the empty count (scalar + array + the cross-check), the N-D legal-moves shape tests |
| D — game ops/endgame/D8 (TestPositionCollisions 2, TestPositionCheckCollisions 5, TestPositionLegalMovesCount 1, TestPositionFlips 19, TestPositionMakeMove 20, TestPositionCountDifference 1, TestPositionFinalValue 7, TestPositionHasToPass 2, TestPositionIsGameOver 3, TestPositionIsMoveLegal 4, TestPositionTrFunctions 9, TestPositionTransformations 2, TestPositionAntiTransformations 2) | 77 | the collision message substrings, the flips early-return branches (all three: PASS swap, non-single-bit, illegal-no-flip), the None-on-illegal pin, the PA-swap branches (`move == MOVE_PA` in both `position_make_move` and the flips kernel), the PASS-on-a-zero-bitboard convention of `position_flips` (scalar + the bulk + the array batch + the fuzz parity), the 3 WOFC branches, the NOT-FULL is_game_over true case via the PA-swap path, the updated-position asserts in the flips bulk, the `position_ro000` identity-copy pin, lowercase rejections |
| E — hash, njit primitives, meta (TestPositionHash 17, TestPositionHashLegacyParity 2, TestNumbaPrimitives 2, TestPydanticVersion 1) | 22 | the Zobrist hash (the view dependence, the pinned values) + the legacy C parity on the FFO-12 sample, the two per-lane njit primitives (`legal_moves_of` / `flips_of_move`) against the batch and scalar paths, the pydantic v2 major version (the non-coercion validation pins depend on it) |

## Goldens pinned

- The two 9-line print goldens: the bitboard (the 19 squares of the `ar` fixture) and the position (mover 17 /
  opponent 27 / empties 20).
- The 112 D8 primitive pairs + the orbit slot order + the 123-row legal-moves bulk (all independently re-derived —
  zero mismatches; the value base of the suite).
- The `ar_reflection_a1h8` / `ar_reflection_h1a8` header constants.
- The move-code literals: `MOVE_PA == 64`, `MOVE_NA == 65`, `MOVE_UN == 66` (the anchor of the named constants) and
  their identity with `move_from_str('PA' / 'NA' / 'UN')`.
- The pydantic v2 major.

## Conventions

- The header constants keep their transposed-looking names (`row_1` is the first ROW, `column_a` the first column, ...)
  — NOT a defect: this is Reversi, not chess; the canonical row/column vocabulary is notes/naming.md.
- PERF gates measure (b/s print), never fail on slowness; the 1M populations are uniform (`np.tile` / `np.full`).
- The shared fixture pair is disjoint (`mover & opponent == 0`), so the Area-C collision checks pass trivially there;
  the raise path is exercised only in TestPositionCheckCollisions.
- The move codes are used by NAME (`MOVE_PA`, not `64`); the literal values are pinned once, in `TestMove`.

## Integration

- Module under test: `board.md` (the engine core: Square/Move, bitboards, D8, positions, legal moves, WOFC).
- The same position fixture is shared with the pattern / mobility suites; the naming rulings (notes/naming.md) are the
  canonical reference for every name in this file.
