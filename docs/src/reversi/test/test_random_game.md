# reversi/test/test_random_game.py
The NO-DB micro-suite of the random_game module: the initial
game position (the official Othello setup — the mover /
opponent square sets + the types) and the random move pick
(the D-193 golden frequencies).
> State: D-193 (the choose_random_move golden) + D-192 ·
2026-09-15 · suite 2/0/0

## Coverage

| class | tests | what it pins |
|---|---|---|
| `TestInitialGame` | 1 | `test_initial_game_position` (the Position dtype, the Bitboard field types, the mover {E4, D5} + the opponent {D4, E5} square sets — the official Othello setup, the D-192 canonical source) |
| `TestChooseRandomMove` | 1 | `test_choose_random_move` (the D-193: seed 93, 1000 draws from the initial position — every draw a member of the legal set {D3, C4, F5, E6} + the EXACT frequencies [258, 229, 249, 264]) |

## Goldens pinned

- The initial-position square sets: the mover {E4, D5}
  (0x0000000810000000), the opponent {D4, E5}
  (0x0000001008000000) — the official Othello International
  setup (Roberto's check; the D-192 fix re-lands the G0
  corpus generators on it).
- The pick golden (the D-193): the exact 1000-draw
  frequencies [258, 229, 249, 264] over the legal squares
  {D3, C4, F5, E6} at seed 93 — the golden-pinned MT19937
  stream makes it bit-stable; it protects the pick's
  distribution AND the one-draw-per-pick stream consumption
  (the get_double_in_c0_o1 draw per non-empty pick).

## Conventions

- The house test header (the "How to run" block).
- The expected square names in the canonical lists (the
  naming convention: uppercase, A1 = top-left = bit 0); the
  bitboard → squares via bitboard_to_square_list +
  square_to_str, reversed to the A1 → H8 order.
- The golden frequencies as literal arrays (the nptest.
  assert_array_equal pin) — no tolerance, the stream is
  deterministic.

## Integration

- Consumed by `run_utests.sh` (section 1 — the board &
  pattern concepts, after test_board).
