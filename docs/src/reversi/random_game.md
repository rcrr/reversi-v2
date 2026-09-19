# reversi/random_game.py
The random game of Reversi, one building block at a time: the
random move pick (`random_game_choose_move`), the random move
execution (`random_game_make_move` — pick a move, apply it, return
the resulting position + the move), and the random path
(`random_game_play_path` — play random moves until the empty count
reaches the target, or a game-over position). Dual scalar/array
(the D-219 campaign): a 1-D PositionArray in gives the per-element
results computed on the ONE injected prng stream.

## API
- `random_game_choose_move(p, prng) -> Bitboard | BitboardArray` —
  a random legal move: the position's legal moves (board.
  position_legal_moves) + the uniform PRNG pick (the scalar path
  via prng.choose_one_from_set64). Dual scalar/array (D-219, the
  D-140 pattern; the 2-D (N,2) uint64 input coerced).
  @validate_call (arbitrary_types_allowed). The PRNG is INJECTED —
  the caller owns the stream (the "one seed for all" discipline).
  The stream contract: the array call is BIT-IDENTICAL to the
  sequential scalar processing of the same positions with the same
  stream — one draw per non-empty legal set, no draw for a pass. No
  legal move: the empty bitboard 0 (the
  pick's (0, 64) sentinel — 64 = PA in the Move domain — is the
  caller's pass signal).
- `random_game_make_move(p, prng) -> (PositionField | PositionArray,
  Move | MoveArray)` — executes a random legal move: asks
  random_game_choose_move for the move, applies it on p via board.
  position_flips, and returns the resulting position together
  with the move that was played (a Move: the square position, or
  64 = PA). The returned position is the position_flips output
  (the next player's view: the mover / opponent fields are
  swapped with respect to the input). No legal move: the move is
  PA and the returned position is the swapped position (the
  players inverted). Dual scalar/array (D-220): the
  per-element semantics is the scalar one (a zero move swaps the
  players, a legal move flips); the choose_move stream contract is
  inherited. @validate_call (arbitrary_types_allowed).
- `random_game_play_path(p, target_ec, prng) -> (PositionField |
  PositionArray, np.uint8 | uint8 array)` — plays a sequence of
  random legal moves (via random_game_make_move) until the empty
  count reaches target_ec (or a game-over position is hit: the two
  consecutive passes break the loop). Returns the final position +
  its empty count (an ordinal np.uint8 — D-217). If the starting
  position is already at or below target_ec, it is returned as-is.
  Dual scalar/array (D-222): the array stream contract — the
  lanes advance in lockstep, one draw per active lane per step, in
  element order (the mover plays, or the mover passes and the
  opponent plays); the game-over lanes consume no draw. The N == 1 array call is BIT-IDENTICAL to the scalar call.
  The target is ONE shared value for the batch. @validate_call
  (arbitrary_types_allowed).

## Architecture
- Pure functions over board.py: no state of their own, no PRNG
  of their own — the MT19937 stream is the caller's (the pick
  consumes exactly one draw per non-empty pick; the pass is the
  (0, 64) sentinel — 64 = PA in the Move domain).
- The dual array path (D-219): the legal sets are computed before
  any draw (they are draw-independent), one get_uint64_batch call
  pre-draws for the non-empty elements, and the prng batch kernel
  (pick_one_from_set64_batch — the single source of the pick
  technique, D-221) folds each draw into its element.
- The empty move set: the module constant `_EMPTY_MOVE_SET`
  (`Bitboard(0)`) — the pass signal of the pick domain, the batch
  kernel's no-pick value.
- The dual array make_move (D-220): a pure COMPOSITION of the
  verified dual functions — the D-219 batch pick (the stream
  contract inherited) + the D-140 position_flips — plus one numpy
  line for the codes (np.bitwise_count(move - 1): the bit index of
  a single-bit move, and the wrap-around of an empty move gives
  64 = PA — no kernel of its own).
- The dual array play_path (D-222): the STEP ENGINE, in three named
  units — `_play_path_engine` (the step loop + the termination
  bound), `_play_path_step` (the lane classification and the
  advance), `_apply_picked_moves` (the masked position_flips on the
  lane subset). Per step the mover's legal set is computed on the
  batch and the opponent's ONLY on the pass-lane subset (rare
  mid-game — the D-228 profiling fix); both draw-independent; they
  classify the active lanes:
  mover_plays (the disc placed by the mover),
  mover_passes_opponent_plays (the pass costs no draw, the opponent
  plays from the swapped view), double_pass_game_over (harvested,
  no draw, the input view returned); one get_uint64_batch
  pre-draws for the needing lanes (the prefix slot map) and
  pick_one_from_set64_batch + position_flips advance them. The
  termination is mathematical (every non-terminal step decreases a
  lane's ec by one); the step bound is derived from the input (the
  ec surplus over the target, plus one).
- The module grows with the random-game machinery (the name is
  the game, not just the start) — the mirror follows.

## Verified invariants
- The random pick: every draw is a member of the
  legal set, and the EXACT 1000-draw frequencies
  [258, 229, 249, 264] over the initial-position legal set
  {D3, C4, F5, E6} at seed 93 — pinned by
  test_random_game::TestRandomGameChooseMove::
  test_random_game_choose_move (the golden-pinned MT19937 stream
  makes it bit-stable; it also pins the one-draw-per-pick
  consumption). The EC20 fixtures (six 20-empty-square
  positions) pin the pick at the low-empty-count end —
  test_random_game::TestRandomGameChooseMoveEC20.
- The array pick (D-219): the batch over the six EC20 positions +
  the initial position (13/0/0/9/0/13/4 legal options) is
  bit-identical to the sequential scalar processing with the same
  seed, and the two streams stay aligned afterwards (the passes
  consume no draw) — pinned by test_random_game::
  TestRandomGameChooseMoveArray::test_array_matches_sequential_scalar.
- The random move execution: from a 20-empty-square position
  with two legal moves (G1, G2), N = 12 draws (seed 93) yield
  ONLY the two resulting boards (both appear), each returned
  position is exactly the position_flips output for the drawn
  move, and each is one stone ahead of the fixture; a position
  with no legal move returns (the swapped position, PA) — pinned
  by test_random_game::TestRandomGameMakeMove.
- The array move execution (D-220): the batch (positions + codes)
  over the mixed EC20 fixtures + the initial position is
  bit-identical to the sequential scalar processing with the same
  seed (the streams stay aligned), and every returned position is
  the scalar position_flips output for its drawn code — pinned by
  test_random_game::TestRandomGameMakeMoveArray::
  test_array_matches_sequential_scalar /
  test_returned_positions_consistent_with_the_codes.
- The random path: plays random moves until the empty count
  reaches the target (or a game-over position) — the final empty
  count is <= the start and >= the target, the double-pass
  game-over break stops the loop with the input view returned (the
  pass is PA = 64), and a moveless mover continues via the pass
  swap — pinned by test_random_game::TestRandomGamePlayPath.
- The array play path (D-222): the N == 1 array call is
  bit-identical to the scalar call (the scalar bridge: the
  position, the ec, and the stream alignment — over the standard,
  the single-pass, the game-over, and the deep 46-move initial
  paths) — pinned by test_random_game::
  TestRandomGamePlayPathArray::test_single_lane_array_matches_scalar;
  the whole-batch determinism, the game-over lane (the input view
  + its own ec), the target landing, and the ec bounds —
  test_random_game::TestRandomGamePlayPathArray::test_determinism /
  test_ec_contract.

## Open issues
None.

## Conventions
- The GNU header (the house template).
- The naming convention (notes/naming.md): the square names
  uppercase, A1 = top-left = bit 0 (bit = 8*(row-1) +
  (col-1)).
- @validate_call (pydantic, arbitrary_types_allowed) on the
  public functions (the house dual-API contract).

## Integration
- board.py (Bitboard, BitboardArray, Move, PositionField,
  PositionArray, bitboard_bsr, position_flips, position_legal_moves,
  position_empty_count).
- tools/prng.py (the MT19937 — the injected stream; the
  choose_one_from_set64 pick; the get_uint64_batch pre-draw).
