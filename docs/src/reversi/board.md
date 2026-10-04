# reversi/board.py
The board domain model of the Reversi engine: squares, moves, bitboards, positions, and everything that operates on them
— the D8 symmetry group, legal-move and flip-set computation, move execution, end-of-game scoring. No game loop, no
search, no clock, no UI.

## API

The 74 `__all__` names. Dual contract throughout: scalar in → scalar out, any-shape array in → same-shape array out,
unless stated.

| family | name | contract |
|---|---|---|
| Square | `Square` | type alias `np.uint8` — one square, 0 = A1 … 63 = H8 |
| Square | `SquareArray` | annotated `NDArray[np.uint8]`; BeforeValidator rejects any other dtype |
| Square | `square_from_str(name: str) -> Square` | "A1".."H8", uppercase only; ValueError on invalid or lowercase |
| Square | `square_to_str(sq) -> str` | the inverse mapping |
| Square | `square_as_bitboard(sq) -> Bitboard` | the single-bit mask `1 << sq`; a value at or above 64 wraps to the empty bitboard (the same NumPy shift wrap as `move_as_bitboard`) |
| Square | `square_validate_range(sq) -> None` | ValueError if any value outside [0..63] (scalar or array) |
| Move | `Move` | type alias `np.uint8`; 0..63 squares, then the non-square codes PA / NA / UN |
| Move | `MoveArray` | annotated uint8 array (reuses the square validator) |
| Move | `MOVE_PA` / `MOVE_NA` / `MOVE_UN` | the named non-square move codes (64 / 65 / 66): the single source of the PA / NA / UN values |
| Move | `move_from_str(name: str) -> Move` | the 67 names; ValueError on invalid or lowercase |
| Move | `move_to_str(mo) -> str` | the inverse mapping |
| Move | `move_as_bitboard(mo) -> Bitboard` | `1 << mo`; the non-square codes (`MOVE_PA` / `MOVE_NA` / `MOVE_UN`) wrap to the empty bitboard (the documented NumPy shift semantics) |
| Move | `move_validate_range(mo) -> None` | ValueError if any value outside [0..66] (via `__move_max_value__`) |
| Bitboard | `Bitboard` | type alias `np.uint64` — a set of squares, bit i = square i |
| Bitboard | `BitboardArray` | annotated uint64 array, strict dtype |
| Bitboard | `bitboard_from_signed_int(i) -> Bitboard \| BitboardArray` | int64 → uint64 bit reinterpretation; the array result is a zero-copy view (shared buffer); bare Python int → ValidationError; arrays of any shape |
| Bitboard | `bitboard_to_signed_int(bb) -> np.int64 \| NDArray` | the inverse (PostgreSQL storage path); the array result is a zero-copy view (shared buffer); arrays of any shape |
| Bitboard | `bitboard_from_hex_str(h) -> Bitboard \| BitboardArray` | 16-char hex, no `0x` prefix, case-insensitive; the array path is `np.frompyfunc` (element-wise Python loop); arrays of any shape |
| Bitboard | `bitboard_bsr(bb) -> int` | index of the most significant set bit (63..0); 0 → -1; scalar only |
| Bitboard | `bitboard_count(bb) -> np.uint8 \| npt.NDArray[np.uint8]` | popcount via `np.bitwise_count`; dual scalar/array |
| Bitboard | `legal_moves_of(mover, opponent) -> Bitboard` | the per-lane legal-move set — the njit domain wrapper over the private core `_kogge_stone_lms` (the same encapsulation pattern as `flips_of_move` / `_kogge_stone_mm`): the single source of the geometry, called per lane by the vectorized kernel and by the numba compositions (random_game's fused engine) |
| Bitboard | `flips_of_move(mover, opponent, move) -> Bitboard` | the flip set of the single-bit move — the njit flip primitive (the Kogge-Stone core) for the numba compositions |
| Bitboard | `bitboard_print(bb, output)` | 2-D text; row 1 on top, column a on the left |
| Bitboard | `bitboard_to_square_list(bb) -> List[Square]` | the squares, descending (H8 → A1) |
| Bitboard | `bitboard_to_square_array(bb) -> SquareArray` | as a uint8 array |
| Bitboard | `bitboard_to_string_list(bb) -> List[str]` | as "A1"-style names |
| D8 | `bitboard_transformations(bb) -> BitboardArray` | all 8: scalar → (8,), any-shape array (S,) → S + (8,); the fixed slot order ro000/ro090/ro180/ro270/fvert/fh1a8/fhori/fa1h8 |
| D8 | `bitboard_anti_transformations(bb) -> BitboardArray` | the 8 inverses; same order, slots 1/3 swapped (ro270, ro090); scalar → (8,), any-shape array (S,) → S + (8,) |
| D8 | `bitboard_fa1h8(bb) -> Bitboard \| BitboardArray` | reflection on the a1-h8 diagonal (h1 ↔ a8); dual scalar/array; arrays of any shape; numba `@overload` for JIT contexts |
| D8 | `bitboard_fh1a8(bb) -> Bitboard \| BitboardArray` | reflection on the h1-a8 diagonal (a1 ↔ h8); dual scalar/array; arrays of any shape; numba `@overload` for JIT contexts |
| D8 | `bitboard_fhori(bb) -> Bitboard \| BitboardArray` | reflection on the horizontal axis (row 1 ↔ row 8); dual scalar/array; arrays of any shape; numba `@overload` for JIT contexts |
| D8 | `bitboard_fvert(bb) -> Bitboard \| BitboardArray` | reflection on the vertical axis (column a ↔ column h); dual scalar/array; arrays of any shape; numba `@overload` for JIT contexts |
| D8 | `bitboard_ro000(bb)` | the identity — a fresh copy of the input (no aliasing, the same contract as the other 7 D8 functions and `position_ro000`) |
| D8 | `bitboard_ro090` / `bitboard_ro180` / `bitboard_ro270` | the rotations (clockwise), composed from the reflections; arrays of any shape (inherited) |
| D8 | `bitboard_trans_fs` | the 8 transform functions, as a plain list |
| D8 | `bitboard_anti_trans_fs` | the 8 inverse functions, same form |
| D8 | `bitboard_transformation_labels` | the 8 slot labels, a plain Python list of str |
| D8 | `bitboard_anti_transformation_labels` | the 8 anti slot labels, a plain Python list |
| Position | `Position` | the numpy structured dtype `[('mover', u64), ('opponent', u64)]` |
| Position | `PositionField` | `Annotated[np.void, SkipValidation]` — the scalar, validation skipped |
| Position | `PositionArray` | annotated array; a 2-D uint64 (N,2) is coerced to a Position view by the BeforeValidator |
| Position | `make_position(mover, opponent) -> np.void \| ndarray` | scalar / 1-D / 2-D; fresh interleaved (shape,2) buffer, inputs copied, output a zero-copy view; shape mismatch → ValueError |
| Position | `initial_game_position() -> PositionField` | the standard start: mover (black) E4+D5 (0x0000000810000000), opponent (white) D4+E5 (0x0000001008000000) — the 2x2 center, both sides 4 legal moves, ec = 60; scalar only |
| Position | `position_eq(a, b) -> bool` | `np.array_equal` |
| Position | `position_print(p, output)` | 2-D text: '@' mover, 'O' opponent, '.' empty |
| Position | `position_empties(p) -> Bitboard \| BitboardArray` | `~(mover \| opponent)` |
| Position | `position_collisions(p) -> Bitboard \| BitboardArray` | `mover & opponent` — must always be 0 |
| Position | `position_check_collisions(p) -> None` | ValueError with count + first index when non-zero |
| Position | `position_legal_moves(p) -> Bitboard \| BitboardArray` | the legal-move set (delegates to `legal_moves`) |
| Position | `legal_moves(mover, opponent) -> Bitboard \| BitboardArray` | dual; both args the same kind (mixed → TypeError); strict uint64 in, same-shape check (mismatch → ValueError), arrays of any shape |
| Position | `position_legal_moves_count(p) -> int` | popcount of the legal set; scalar |
| Position | `position_flips(p: PositionField \| PositionArray, move: Bitboard \| BitboardArray) -> (Bitboard \| BitboardArray, PositionField \| PositionArray \| None)` | dual: scalar — Kogge-Stone flip set + updated position; a zero (PASS) move swaps the players, an illegal or non-single-bit move → `(0, None)`; array — per-element: a zero (PASS) move swaps the players, an illegal move gets flips[i] = 0 and the input position unchanged (no None in the array); both args the same kind (mixed → TypeError), same-shape check (mismatch → ValueError), arrays of any shape |
| Position | `position_make_move(p: PositionField \| PositionArray, move: Move \| MoveArray) -> PositionField \| PositionArray \| None` | dual: scalar — execute, 64 (PA) swaps the players without verification, > 64 → ValueError, illegal EMPTY square (no flipping ray) → None; array — per-element PA swap + illegal keeps the input position, any array value > 64 → ValueError before the kernel; both args the same kind (mixed → TypeError), same-shape check (mismatch → ValueError), arrays of any shape. A move on an OCCUPIED square is unexpected behavior (the caller's responsibility): the flip ray is computed and, when non-zero, APPLIED — own-stone square → well-formed but unreachable position (count short by one); opponent-stone square → corrupt position (the square in BOTH bitboards) |
| Position | `position_count_difference(p) -> int` | `count(mover) - count(opponent)` |
| Position | `position_final_value(p) -> int` | WOFC end score: the difference, empty squares assigned to the leader |
| Position | `position_empty_count(p) -> np.uint8 \| npt.NDArray[np.uint8]` | popcount of `position_empties`; dual |
| Position | `position_has_to_pass(p) -> bool` | the mover has no legal move |
| Position | `position_is_game_over(p) -> bool` | no legal move for the mover and, after the pass, none for the opponent either |
| Position | `position_is_move_legal(p, move: Move) -> bool` | a legal square, or the pass only when the legal set is empty; > 64 → False |
| Position | `position_hash(p) -> Bitboard \| BitboardArray` | the 64-bit Zobrist hash: mover discs → the first 64 legacy blacks slots, opponent → the legacy whites slots, no complement — exactly the legacy `game_position_x_hash` of (blacks = mover, whites = opponent, player = BLACK); a legacy WHITE position = the one's complement (the C `if (p) hash = ~hash`); pure function of the pair (no legality validation); scalar + any-shape array (+ the (N,2) coercion), empty array OK |
| Position | `position_ro000` / `position_ro090` / `position_ro180` / `position_ro270` / `position_fvert` / `position_fh1a8` / `position_fhori` / `position_fa1h8` | the 8 per-field D8 transforms; `position_ro000` returns a copy |
| Position | `position_transformations(p) -> PositionArray` | all 8, same slot order as the bitboards |
| Position | `position_anti_transformations(p) -> PositionArray` | all 8 inverses (slots 1/3 swapped) |

## Architecture

Layered, low → high:

```
Square (uint8)          Move (uint8, + 64=PA, 65=NA, 66=UN)
        \        /                    \
 Bitboard (uint64, bit i = square i)  Move utils
        \
 Position (structured dtype: mover + opponent, u64 each)
        \
 game ops: legal moves, flips, make_move, WOFC scoring, D8
```

- **Dual scalar/array API** — every public function: an `isinstance` scalar check, the array path, the numba kernel, the
  output adapted back to the input kind; arrays of any shape (1-D straight to the kernel, no flatten copy; N-D flattens
  C-order and reshapes back). `legal_moves`, `position_flips`, `position_make_move` are the strict dual: scalar or
  ndarray only (mixed → TypeError), the same-shape check.
- **Numba** — `njit(parallel=True, cache=True)` on the hot kernels (the 2 D8 batch transform kernels + the 4 reflection
  array impls + the 4 scalar impls with `inline='always'` + `_vectorized_legal_moves` + `_vectorized_flips` +
  `_vectorized_make_move` + `_vectorized_position_hash`), `prange` on the batch loops; the PUBLIC per-lane njit
  primitives (`legal_moves_of`, `flips_of_move`, both `inline='always'`) are the single sources of the two geometries:
  the vectorized kernels call them per lane and the numba compositions of the other modules (random_game's fused
  engine) call the same functions — the source is written once, the compiler inlines the machine code at the call
  sites; `_kogge_stone_mm` is `@njit(inline='always')` (the shared per-element flip primitive — the scalar path
  calls it); `_zobrist_position_fold` is `@njit(cache=True)` (the shared per-element hash primitive — the scalar
  path calls it); `@overload` on the 4 reflection primitives so JIT code can call them (registered on the
  pydantic-wrapped names — verified resolvable in a JIT context).
- **Pydantic** — `@validate_call` + `arbitrary_types_allowed` on the public functions (the njit primitives and
  `initial_game_position` excepted); `Annotated` + `BeforeValidator` enforce the dtypes; `SkipValidation` on
  `PositionField` (the np.void scalar).
- **Zero-copy discipline** — `make_position` allocates a fresh interleaved (…,2) block, copies the inputs in (never
  aliased), returns a `.view(Position)` of that block; the signed-int converters return views (documented aliasing).
- **Kogge-Stone legal moves** — 4 directions × 2 senses with precomputed boundary masks (`_mask_l`/`_mask_r`: +1→column
  a, +7→column h, +8→none, +9→column a, and the mirrors) and 1/2/4 slide tables; generator/propagator: `p &= (p << k)`
  kills propagation at the first non-opponent cell (a run broken by an empty square yields no false move); the final
  `g & ~mover` and the empties mask exclude occupied squares and the generator itself.
- **Flip set** (`_kogge_stone_mm`) — the same 1/2/4 slides over 8 directions; the blocker `gt` requires a mover disc
  immediately past the run end; the result is `& ~generator` (move square excluded). The primitive is
  `@njit(inline='always')` and runs per element inside the `_vectorized_flips` / `_vectorized_make_move` `prange`
  kernels (3-array return, re-assembled with `make_position`); the flip kernel does NOT check the move square emptiness
  (the caller's responsibility).
- **Zobrist position hash** (`position_hash`) — the 128 legacy URANDOM bitstrings (`_zobrist_bitstrings`: the canon,
  SHA-3-pinned) + the SWAR byte-fold tables `_zobrist_byte_fold` (2×8×256, generated at import, deterministic, 32 KB
  L1-resident): 16 lookups per position, no per-bit loop. XOR-incremental by construction (a disc flip at square i
  contributes `zobrist[i] ^ zobrist[i+64]` — the legacy `zobrist_flip_bitstrings` entry); legacy-comparable under the
  fixed bridge (blacks = mover, whites = opponent, player = BLACK; a legacy WHITE position = the one's complement).
- **Platform: little-endian only** — no portability work planned.

## Verified invariants

- D8 group law: ro000 identity, ro090² = ro180, ro090∘ro270 = id, the 4 reflections involutive, anti-transform inverts
  transform — `test_board::TestBitboardD8GroupLaw` (+ the two identity-copy pins, the bitboard and the position layers).
- All 8 bitboard transforms vs hand-computed scalar goldens and (N,8) outputs —
  `test_board::TestBitboardTransformation{Ro000…Fa1h8}`.
- The function/label tables produce the correct slot order — `test_board::TestD8FunctionTables`.
- Legal-move correctness at all 4 boundaries × both senses, incl. runs broken by empty squares —
  `test_board::TestPositionLegalMoves` (corner c1/h8 + the hand-computed bulk table + the same-shape ValueError pin),
  `TestPositionLegalMovesCount`.
- The flip set (runs up to 7, blocker past the run end, move square excluded) — `test_board::TestPositionFlips` (base +
  the PASS swap + bulk + the array bulk/fuzz parity + the array pass batch + guards), `TestPositionMakeMove` (incl. the
  PA swap, None on illegal, the array batch + fuzz parity + guards).
- The empty-square equivalence: an empty square is legal exactly when it flips something (the flip kernel and the
  legal-moves kernel share the geometry); an occupied square is never legal —
  `test_board::TestPositionFlips::test_position_flips_array_matches_scalar` (the fixed-seed fuzz).
- The collision invariant (mover & opponent = 0) and `make_position` copy-then-view (inputs never aliased) —
  `test_board::TestPositionCollisions` / `TestPositionCheckCollisions` / `TestPositionCreation`.
- The standard start (mover {E4, D5}, opponent {D4, E5}; the Position dtype + the Bitboard field types) —
  `test_board::TestInitialGame::test_initial_game_position` (the squares via bitboard_to_square_list + square_to_str).
- The signed-int round-trip (PostgreSQL path, incl. the shared-buffer view; bare-int rejection) —
  `test_board::TestBitboardFromSignedInt` / `TestBitboardToSignedInt` (+ `TestPydanticVersion`).
- WOFC end scoring (empty squares to the leader; draw / full-board / all-squares branches) —
  `test_board::TestPositionFinalValue`.
- Game-over semantics (no move for the mover and none for the opponent after the pass, incl. the not-full case) —
  `test_board::TestPositionIsGameOver` / `TestPositionHasToPass` / `TestPositionIsMoveLegal`.
- Move-code discipline (64/65/66 → the empty bitboard; the pass legal iff no legal move) — `test_board::TestMove` /
  `TestPositionIsMoveLegal`.
- Position-level D8 transforms (scalar + array) — `test_board::TestPositionTrFunctions` / `TestPositionTransformations`
  / `TestPositionAntiTransformations`.
- The `@overload` of the 4 reflection primitives in a numba JIT context — `test_board::TestNumbaReflectionOverloads`
  (scalar + array JIT outputs vs the direct-call goldens).
- position_hash: the goldens (the initial position 0xC4292FC2B2633A16 + 5 fixed pairs, derived from the legacy C
  `game_position_x_hash_plain`) and the SHA-3-256 pin of the packed table — `test_board::TestPositionHash`.
- The legacy WHITE complement bridge (legacy(blacks, whites, WHITE) = ~position_hash(blacks, whites)) —
  `test_board::TestPositionHash::test_legacy_white_complement_bridge`.
- position_hash parity / (N,2) coercion / empty array / the rejections / determinism — `test_board::TestPositionHash`.
- The hash quality: the avalanche band (128 single-bit flips of the start, every output bit flips 40..88 of 128) and
  zero collisions on random pairs (10k; 1e6 under LONG, the birthday bound) —
  `test_board::TestPositionHash::test_avalanche_bit_flips` / `test_no_collisions`.
- The legacy-C parity: the `position_hash` values match the legacy engine row by row over the FFO-12 solve-log sample
  (the committed 1002-row stride) — `test_board::TestPositionHashLegacyParity`.
- The per-lane primitives (`legal_moves_of` / `flips_of_move`) and the counts
  (`bitboard_count` / `position_empty_count`) — `test_board::TestNumbaPrimitives` / `TestBitboardCount` /
  `TestPositionEmptyCount`.


## Open issues

None.

## Conventions

- Reversi vocabulary: column (a–h, left→right), row (1–8, top→ bottom); A1 = top-left = bit 0, H8 = bit 63; diagrams
  read row 1 on top.
- The D8 slot order is fixed (notes/naming.md): never reorder or rename; the anti tables differ only in slots 1/3. New
  public functions: `@validate_call` with `arbitrary_types_allowed`, the dual scalar/array signature with the standard
  `atleast_1d`/ndim pattern, a docstring stating the shape contract.
- The move codes are the NAMED constants `MOVE_PA` / `MOVE_NA` / `MOVE_UN` (the single source): the bare 64/65/66
  never appears in the code. The flips domain is separate: `position_flips` takes a BITBOARD and its pass is the zero
  bitboard, not `MOVE_PA`.
- The Zobrist table `_zobrist_bitstrings` is canon (the legacy C constants): never regenerate, reorder or edit; a change
  breaks the legacy comparability and every pinned golden. The hash is view-dependent by design (the two views of a
  board are different positions).
- The type aliases are SEMANTIC domain types, not dtype shortcuts (D-217): `Square` is an index into the 64-square
  space, `Bitboard` a set of squares, `Position` a game position. The raw numpy forms are deliberate wherever the value
  is not a domain concept — the ordinal counts (`bitboard_count`, `position_empty_count` →
  `np.uint8 | npt.NDArray[np.uint8]`, NOT `SquareArray`), the int64 storage forms (`bitboard_from/to_signed_int`), the
  generic `make_position` return (scalar, 1-D or 2-D). Do not "uniform" them toward the aliases.

## Integration

- Consumed by: `pattern.py` (the D8 orbits, the principal masks), `mobility.py`, `feature.py`, `regab.py` (DB row ↔
  position), `client.py`, `hlp_config_schemas.py`, `random_game.py`.
- A pure domain module: not a pipeline level, no ctx fields, no cache.
