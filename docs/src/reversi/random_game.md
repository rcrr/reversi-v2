# reversi/random_game.py
The initial game position of Reversi: the single function
`initial_game_position`, the standard start as a Position. It
is the CANONICAL source of the standard start (the D-192
initial-position fix re-lands hlp_wave.INITIAL_MOVER /
INITIAL_OPP and hlp_random_play.initial_position on it).
> State: D-192 · 2026-09-15 · suite 1/0/0

## API
- `initial_game_position() -> PositionField` — the standard
  start: the mover (black, the starting player) holds E4+D5
  (0x0000000810000000), the opponent (white) holds D4+E5
  (0x0000001008000000) — the 2x2 center, both sides with
  exactly 4 legal moves, ec = 60.

## Architecture
- A pure function over board.make_position (two Bitboard
  literals): no state, no PRNG, no I/O. The docstring carries
  the board diagram (the canonical orientation: row 1 on top,
  column a on the left).
- The canonical source of the standard start (D-192): the G0
  corpus generators carry the matching literals (hlp_wave's
  INITIAL_MOVER / INITIAL_OPP, hlp_random_play.initial_
  position) — the official Othello International setup
  (Roberto's check), not an arbitrary convention.

## Verified invariants
- The mover / opponent square sets: the mover {E4, D5}, the
  opponent {D4, E5}; the Position dtype + the Bitboard field
  types — pinned by test_random_game::TestInitialGame::
  test_initial_game_position (the squares via
  bitboard_to_square_list + square_to_str).

## Open issues
None.

## Conventions
- The GNU header (the house template).
- The naming convention (notes/naming.md): the square names
  uppercase, A1 = top-left = bit 0 (bit = 8*(row-1) +
  (col-1)).
- The module grows with the random-game machinery (the name
  is the game, not just the start) — the mirror follows.

## Integration
- board.py (make_position, Bitboard, PositionField).
- Consumers (the D-192 re-landing): hlp_wave.INITIAL_MOVER /
  INITIAL_OPP (the G0 corpus engine) + hlp_random_play.
  initial_position (the FEATURE_ANALYSIS data plane).
