# reversi/test/test_random_game.py
The NO-DB micro-suite of the random_game module: the initial
game position (the official Othello setup — the mover /
opponent square sets + the types).
> State: D-192 · 2026-09-15 · suite 1/0/0

## Coverage

| class | tests | what it pins |
|---|---|---|
| `TestInitialGame` | 1 | `test_initial_game_position` (the Position dtype, the Bitboard field types, the mover {E4, D5} + the opponent {D4, E5} square sets — the official Othello setup, the D-192 canonical source) |

## Goldens pinned

- The initial-position square sets: the mover {E4, D5}
  (0x0000000810000000), the opponent {D4, E5}
  (0x0000001008000000) — the official Othello International
  setup (Roberto's check; the D-192 fix re-lands the G0
  corpus generators on it).

## Conventions

- The house test header (the "How to run" block).
- The expected square names in the canonical lists (the
  naming convention: uppercase, A1 = top-left = bit 0); the
  bitboard → squares via bitboard_to_square_list +
  square_to_str, reversed to the A1 → H8 order.

## Integration

- Consumed by `run_utests.sh` (section 1 — the board &
  pattern concepts, after test_board).
