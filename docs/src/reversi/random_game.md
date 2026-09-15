# reversi/random_game.py
The random game of Reversi, one building block at a time: the
standard start (`initial_game_position`, the CANONICAL source of
the standard start — the D-192 initial-position fix re-lands
hlp_wave.INITIAL_MOVER / INITIAL_OPP and hlp_random_play.
initial_position on it) and the random move pick
(`choose_random_move`, the D-193).
> State: D-193 (the choose_random_move pick) + D-192 ·
2026-09-15 · suite 2/0/0

## API
- `initial_game_position() -> PositionField` — the standard
  start: the mover (black, the starting player) holds E4+D5
  (0x0000000810000000), the opponent (white) holds D4+E5
  (0x0000001008000000) — the 2x2 center, both sides with
  exactly 4 legal moves, ec = 60.
- `choose_random_move(p, prng) -> Bitboard` — a random legal
  move (the D-193): the position's legal moves (board.
  position_legal_moves) + the uniform PRNG pick (prng.
  choose_one_from_set64). @validate_call
  (arbitrary_types_allowed). The PRNG is INJECTED — the caller
  owns the stream (the "one seed for all" discipline). No legal
  move: returns the empty bitboard 0 (the pick's (0, 64)
  sentinel — 64 = PA in the Move domain — is the caller's
  pass signal).

## Architecture
- Pure functions over board.py: no state of their own, no PRNG
  of their own — the MT19937 stream is the caller's (the pick
  consumes exactly one draw per non-empty pick). The docstring
  of initial_game_position carries the board diagram (the
  canonical orientation: row 1 on top, column a on the left).
- The module grows with the random-game machinery (the name is
  the game, not just the start) — the mirror follows.

## Verified invariants
- The mover / opponent square sets: the mover {E4, D5}, the
  opponent {D4, E5}; the Position dtype + the Bitboard field
  types — pinned by test_random_game::TestInitialGame::
  test_initial_game_position (the squares via
  bitboard_to_square_list + square_to_str).
- The random pick (the D-193): every draw is a member of the
  legal set, and the EXACT 1000-draw frequencies
  [258, 229, 249, 264] over the initial-position legal set
  {D3, C4, F5, E6} at seed 93 — pinned by
  test_random_game::TestChooseRandomMove::test_choose_random_
  move (the golden-pinned MT19937 stream makes it bit-stable;
  it also pins the one-draw-per-pick consumption).

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
- board.py (make_position, Bitboard, PositionField,
  position_legal_moves).
- tools/prng.py (the MT19937 — the injected stream; the
  choose_one_from_set64 pick, D-193).
- Consumers (the D-192 re-landing): hlp_wave.INITIAL_MOVER /
  INITIAL_OPP (the G0 corpus engine) + hlp_random_play.
  initial_position (the FEATURE_ANALYSIS data plane).
