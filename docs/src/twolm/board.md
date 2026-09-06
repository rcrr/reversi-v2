# twolm/board.py
The board domain model of the Reversi engine: squares, moves,
bitboards, positions, and everything that operates on them — the
D8 symmetry group, legal-move and flip-set computation, move
execution, end-of-game scoring. No game loop, no search, no clock,
no UI.
> State: D-018 · b070918 · 2026-08-27 · suite 193/0/12

## API

The 68 `__all__` names. Dual contract throughout: scalar in →
scalar out, 1-D array in → array out (same shape), unless stated.

| family | name | contract |
|---|---|---|
| Square | `Square` | type alias `np.uint8` — one square, 0 = A1 … 63 = H8 |
| Square | `SquareArray` | annotated `NDArray[np.uint8]`; BeforeValidator rejects any other dtype |
| Square | `square_from_str(name: str) -> Square` | "A1".."H8", uppercase only; ValueError on invalid or lowercase |
| Square | `square_to_str(sq) -> str` | the inverse mapping |
| Square | `square_as_bitboard(sq) -> Bitboard` | the single-bit mask `1 << sq` |
| Square | `square_validate_range(sq) -> None` | ValueError if any value outside [0..63] (scalar or array) |
| Move | `Move` | type alias `np.uint8`; 0..63 squares + 64 = PA, 65 = NA, 66 = UN |
| Move | `MoveArray` | annotated uint8 array (reuses the square validator) |
| Move | `move_from_str(name: str) -> Move` | the 67 names; ValueError on invalid or lowercase |
| Move | `move_to_str(mo) -> str` | the inverse mapping |
| Move | `move_as_bitboard(mo) -> Bitboard` | `1 << mo`; codes 64-66 wrap to the empty bitboard (documented NumPy shift semantics) |
| Move | `move_validate_range(mo) -> None` | ValueError if any value outside [0..66] (via `__move_max_value__`) |
| Bitboard | `Bitboard` | type alias `np.uint64` — a set of squares, bit i = square i |
| Bitboard | `BitboardArray` | annotated uint64 array, strict dtype |
| Bitboard | `bitboard_from_signed_int(i) -> Bitboard \| BitboardArray` | int64 → uint64 bit reinterpretation; the array result is a zero-copy view (shared buffer); bare Python int → ValidationError; 1-D only |
| Bitboard | `bitboard_to_signed_int(bb) -> np.int64 \| NDArray` | the inverse (PostgreSQL storage path); 1-D only |
| Bitboard | `bitboard_from_hex_str(h) -> Bitboard \| BitboardArray` | 16-char hex, no `0x` prefix, case-insensitive; the array path is `np.frompyfunc` (element-wise Python loop) |
| Bitboard | `bitboard_bsr(bb) -> int` | index of the most significant set bit (63..0); 0 → -1; scalar only |
| Bitboard | `bitboard_count(bb) -> np.uint8` | popcount via `np.bitwise_count`; scalar only |
| Bitboard | `bitboard_print(bb, output)` | 2-D text; row 1 on top, column a on the left |
| Bitboard | `bitboard_to_square_list(bb) -> List[Square]` | the squares, descending (H8 → A1) |
| Bitboard | `bitboard_to_square_array(bb) -> SquareArray` | as a uint8 array |
| Bitboard | `bitboard_to_string_list(bb) -> List[str]` | as "A1"-style names |
| D8 | `bitboard_transformations(bb) -> BitboardArray` | all 8: scalar → (8,), (N,) → (N,8); fixed slot order (D-014): ro000, ro090, ro180, ro270, fvert, fh1a8, fhori, fa1h8 |
| D8 | `bitboard_anti_transformations(bb) -> BitboardArray` | the 8 inverses; same order, slots 1/3 swapped (ro270, ro090) |
| D8 | `bitboard_fa1h8` / `fh1a8` / `fhori` / `fvert` | the 4 reflections; dual scalar/array; each has a numba `@overload` for JIT contexts |
| D8 | `bitboard_ro000(bb)` | the identity — a fresh copy of the input (D-111 M1: no aliasing, the same contract as the other 7 D8 functions and `position_ro000`) |
| D8 | `bitboard_ro090` / `ro180` / `ro270 (bb)` | the rotations (clockwise), composed from the reflections |
| D8 | `bitboard_trans_fs` | the 8 transform functions, as a plain list (D-111 M3) |
| D8 | `bitboard_anti_trans_fs` | the 8 inverse functions, same form |
| D8 | `bitboard_transformation_labels` | the 8 slot labels, `np.array` of str |
| D8 | `bitboard_anti_transformation_labels` | the 8 anti slot labels |
| Position | `Position` | the numpy structured dtype `[('mover', u64), ('opponent', u64)]` |
| Position | `PositionField` | `Annotated[np.void, SkipValidation]` — the scalar, validation skipped |
| Position | `PositionArray` | annotated array; a 2-D uint64 (N,2) is coerced to a Position view by the BeforeValidator |
| Position | `make_position(mover, opponent) -> np.void \| ndarray` | scalar / 1-D / 2-D; fresh interleaved (shape,2) buffer, inputs copied, output a zero-copy view; shape mismatch → ValueError |
| Position | `position_eq(a, b) -> bool` | `np.array_equal` |
| Position | `position_print(p, output)` | 2-D text: '@' mover, 'O' opponent, '.' empty |
| Position | `position_empties(p) -> Bitboard \| BitboardArray` | `~(mover \| opponent)` |
| Position | `position_collisions(p) -> Bitboard \| BitboardArray` | `mover & opponent` — must always be 0 |
| Position | `position_check_collisions(p) -> None` | ValueError with count + first index when non-zero |
| Position | `position_legal_moves(p) -> Bitboard \| BitboardArray` | the legal-move set (delegates to `legal_moves`) |
| Position | `legal_moves(mover, opponent) -> Bitboard \| BitboardArray` | dual; both args the same kind (mixed → TypeError); strict uint64 in (Open M5) |
| Position | `position_legal_moves_count(p) -> int` | popcount of the legal set; scalar |
| Position | `position_flips(p, move: Bitboard) -> Tuple[Bitboard, PositionField \| None]` | Kogge-Stone flip set + updated position; illegal or non-single-bit move → `(0, None)` |
| Position | `position_make_move(p, move: Move) -> PositionField \| None` | execute; 64 (PA) swaps the players without verification; > 64 → ValueError; illegal square → None |
| Position | `position_count_difference(p) -> int` | `count(mover) - count(opponent)` |
| Position | `position_final_value(p) -> int` | WOFC end score: the difference, empty squares assigned to the leader |
| Position | `position_has_to_pass(p) -> bool` | the mover has no legal move |
| Position | `position_is_game_over(p) -> bool` | no legal move for the mover and, after the pass, none for the opponent either |
| Position | `position_is_move_legal(p, move: Move) -> bool` | a legal square, or the pass only when the legal set is empty; > 64 → False |
| Position | `position_fa1h8` / `…ro270 (p) -> PositionField` | the 8 per-field D8 transforms; `position_ro000` returns a copy |
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

- **Dual scalar/array API** — every public function: an
  `isinstance` scalar check, `np.atleast_1d`, a 1-D ndim guard, the
  numba kernel, the output adapted back to the input kind.
  `legal_moves` is the exception: strict uint64 scalar or ndarray
  only (Open M5).
- **Numba** — `njit(parallel=True, cache=True)` on the hot kernels
  (the two D8 batch transform fns, the 8 scalar transform impls,
  `_vectorized_legal_moves`), `prange` on the batch loops;
  `@overload` on the 4 reflection primitives so JIT code can call
  them (registered on the pydantic-wrapped names — Open M7).
- **Pydantic** — `@validate_call` with `arbitrary_types_allowed` on
  every public function; `Annotated` + `BeforeValidator` enforce the
  dtypes; `SkipValidation` on `PositionField` (the np.void scalar).
- **Zero-copy discipline** — `make_position` allocates a fresh
  interleaved (…,2) block, copies the inputs in (never aliased),
  returns a `.view(Position)` of that block; the signed-int
  converters return views (documented aliasing).
- **Kogge-Stone legal moves** — 4 directions × 2 senses with
  precomputed boundary masks (`_mask_l`/`_mask_r`: +1→column a,
  +7→column h, +8→none, +9→column a, and the mirrors) and 1/2/4
  slide tables; generator/propagator: `p &= (p << k)` kills
  propagation at the first non-opponent cell (a run broken by an
  empty square yields no false move); the final `g & ~mover` and the
  empties mask exclude occupied squares and the generator itself.
- **Flip set** (`_kogge_stone_mm`) — the same 1/2/4 slides over 8
  directions; the blocker `gt` requires a mover disc immediately
  past the run end; the result is `& ~generator` (move square
  excluded).
- **D8 slot order** is fixed (D-014, notes/naming.md) — the anti
  tables swap only slots 1/3.
- **Platform: little-endian only** (D-022) — no portability work
  planned.

## Verified invariants

- D8 group law: ro000 identity, ro090² = ro180, ro090∘ro270 = id,
  the 4 reflections involutive, anti-transform inverts transform —
  `test_board::TestBitboardD8GroupLaw` (+ `TestBitboardTransformationFa1h8Comp`);
  the identity copy (no aliasing) at
  `TestBitboardD8GroupLaw::test_ro000_array_is_a_fresh_copy`.
- All 8 bitboard transforms vs hand-computed scalar goldens and
  (N,8) vectorized outputs — per-transform
  `test_board::TestBitboardTransformation{Ro000…Fa1h8}`.
- The function/label tables produce the correct slot order —
  `test_board::TestBitboardTransformations` /
  `TestBitboardAntiTransformations`.
- Legal-move correctness at all 4 boundaries × both senses, incl.
  runs broken by empty squares — `test_board::TestPositionLegalMoves`
  (corner c1/h8 + bulk hand-computed table),
  `TestPositionLegalMovesCount`; the 1-D guard (D-111 M5: 2-D →
  ValueError) at `TestPositionLegalMoves::test_legal_moves_2d_{
  mover,opponent}_raises_value_error`.
- The flip set (runs up to 7, blocker past the run end, move square
  excluded) — `test_board::TestPositionFlips` (base + bulk),
  `TestPositionMakeMove` (incl. the PA swap and None on illegal).
- The collision invariant (mover & opponent = 0) —
  `test_board::TestPositionCollisions` / `TestPositionCheckCollisions`.
- `make_position` copy-then-view (inputs never aliased) —
  `test_board::TestPositionCreation`.
- The signed-int round-trip (PostgreSQL path, incl. the
  shared-buffer view; bare-int rejection) —
  `test_board::TestBitboardFromSignedInt` / `TestBitboardToSignedInt`
  (+ `TestPydanticVersion`).
- WOFC end scoring (empty squares to the leader; draw / full-board /
  all-squares branches) — `test_board::TestPositionFinalValue`.
- Game-over semantics (no move for the mover and none for the
  opponent after the pass, incl. the not-full case) —
  `test_board::TestPositionIsGameOver` / `TestPositionHasToPass` /
  `TestPositionIsMoveLegal`.
- Move-code discipline (64/65/66 → the empty bitboard; the pass
  legal iff no legal move) — `test_board::TestMove` /
  `TestPositionIsMoveLegal`.
- Position-level D8 transforms (scalar + array) —
  `test_board::TestPositionTrFunctions` /
  `TestPositionTransformations` / `TestPositionAntiTransformations`.

## Open issues

- M7 — the `@overload` of the 4 reflection primitives is registered
  on the `@validate_call` wrappers; no test exercises the overloads
  in a numba (JIT) context.

## Conventions

- Reversi vocabulary: column (a–h, left→right), row (1–8, top→
  bottom); A1 = top-left = bit 0, H8 = bit 63; diagrams read row 1
  on top (D-013).
- The D8 slot order is fixed (D-014, notes/naming.md): never reorder
  or rename; the anti tables differ only in slots 1/3.
- New public functions: `@validate_call` with
  `arbitrary_types_allowed`, the dual scalar/array signature with the
  standard `atleast_1d`/ndim pattern, a docstring stating the shape
  contract.
- The move codes 64/65/66 are magic numbers by design (PA/NA/UN);
  constants parked (I-003).
- Little-endian only (D-022): no endianness portability work.

## Integration

- Consumed by: `pattern.py` (the D8 orbits, the principal masks),
  `mobility.py`, `feature.py`, `regab.py` (DB row ↔ position),
  `rlm_client.py`, `rlm_config_schemas.py`.
- A pure domain module: not a pipeline level, no ctx fields, no
  cache.
