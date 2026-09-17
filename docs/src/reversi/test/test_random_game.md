# reversi/test/test_random_game.py
The NO-DB micro-suite of the random_game module: the initial
game position (the official Othello setup — the mover /
opponent square sets + the types), the random move pick (the
D-193 golden frequencies), and the EC20 multi-position check
(choose_random_move over six 20-empty-square positions — the
per-position validity + the equidistribution over the available
options).
> State: D-204 (the EC20 equidistribution test) + D-193 + D-192 ·
2026-09-15 · suite 4/0/0

## Coverage

| class | tests | what it pins |
|---|---|---|
| `TestInitialGame` | 1 | `test_initial_game_position` (the Position dtype, the Bitboard field types, the mover {E4, D5} + the opponent {D4, E5} square sets — the official Othello setup, the D-192 canonical source) |
| `TestChooseRandomMove` | 1 | `test_choose_random_move` (the D-193: seed 93, 1000 draws from the initial position — every draw a member of the legal set {D3, C4, F5, E6} + the EXACT frequencies [258, 229, 249, 264]) |
| `TestChooseRandomMoveEC20` | 2 | the six 20-empty-square positions (fixtures inline in the test; 13/0/0/9/0/13 legal options per position): `test_choose_random_move_ec20` (for each position, choose_random_move returns a single legal move when the position has options, or the pass — an empty move — when it has none); `test_choose_random_move_ec20_equidistributed` (N = 1000 draws per position: every draw is validated, and the frequencies accumulated over the AVAILABLE options are reasonably flat — a chi-square over the k options, df = k - 1, kept below the 4-sigma threshold) |

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
