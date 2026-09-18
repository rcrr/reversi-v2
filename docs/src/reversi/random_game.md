# reversi/random_game.py
The random game of Reversi, one building block at a time: the
random move pick (`random_game_choose_move`), the random move
execution (`random_game_make_move` — pick a move, apply it, return
the resulting position + the move), and the random path
(`random_game_play_path` — play random moves until the empty count
reaches the target, or a game-over position).

## API
- `random_game_choose_move(p, prng) -> Bitboard` — a random legal
  move: the position's legal moves (board.
  position_legal_moves) + the uniform PRNG pick (prng.
  choose_one_from_set64). @validate_call
  (arbitrary_types_allowed). The PRNG is INJECTED — the caller
  owns the stream (the "one seed for all" discipline). No legal
  move: returns the empty bitboard 0 (the pick's (0, 64)
  sentinel — 64 = PA in the Move domain — is the caller's
  pass signal).
- `random_game_make_move(p, prng) -> (PositionField,
  Move)` — executes a random legal move: asks
  random_game_choose_move for the move, applies it on p via board.
  position_flips, and returns the resulting position together
  with the move that was played (a Move: the square position, or
  64 = PA). The returned position is the position_flips output
  (the next player's view: the mover / opponent fields are
  swapped with respect to the input). No legal move: the move is
  PA and the returned position is the swapped position (the
  players inverted) — never None. @validate_call
  (arbitrary_types_allowed).
- `random_game_play_path(p, target_ec, prng) -> (PositionField,
  int)` — plays a sequence of random legal moves (via
  random_game_make_move) until the empty count reaches
  target_ec (or a game-over position is hit: the two consecutive
  passes break the loop). Returns the final position + its empty
  count. If the starting position is already at or below
  target_ec, it is returned as-is. @validate_call
  (arbitrary_types_allowed).

## Architecture
- Pure functions over board.py: no state of their own, no PRNG
  of their own — the MT19937 stream is the caller's (the pick
  consumes exactly one draw per non-empty pick; the pass is the
  (0, 64) sentinel — 64 = PA in the Move domain).
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
- The random move execution: from a 20-empty-square position
  with two legal moves (G1, G2), N = 12 draws (seed 93) yield
  ONLY the two resulting boards (both appear), each returned
  position is exactly the position_flips output for the drawn
  move, and each is one stone ahead of the fixture; a position
  with no legal move returns (the swapped position, PA) — pinned
  by test_random_game::TestRandomGameMakeMove.
- The random path: plays random moves until the empty count
  reaches the target (or a game-over position) — the final empty
  count is <= the start and >= the target, the double-pass
  game-over break stops the loop with the input view returned (the
  pass is PA = 64), and a moveless mover continues via the pass
  swap — pinned by test_random_game::TestRandomGamePlayPath.

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
- board.py (Bitboard, Move, PositionField, bitboard_bsr,
  position_flips, position_legal_moves, position_empty_count).
- tools/prng.py (the MT19937 — the injected stream; the
  choose_one_from_set64 pick).
