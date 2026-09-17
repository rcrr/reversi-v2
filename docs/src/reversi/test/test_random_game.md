# reversi/test/test_random_game.py
The NO-DB micro-suite of the random_game module: the initial
game position (the official Othello setup — the mover /
opponent square sets + the types), the random move pick (the
golden frequencies), the EC20 multi-position check
(choose_random_move over six 20-empty-square positions — the
per-position validity + the equidistribution over the available
options), and the random move execution (game_position_make_
random_move — the returned position + the move).

## Coverage

| class | tests | what it pins |
|---|---|---|
| `TestInitialGame` | 1 | `test_initial_game_position` (the Position dtype, the Bitboard field types, the mover {E4, D5} + the opponent {D4, E5} square sets — the official Othello setup, the canonical source) |
| `TestChooseRandomMove` | 1 | `test_choose_random_move` (seed 93, 1000 draws from the initial position — every draw a member of the legal set {D3, C4, F5, E6} + the EXACT frequencies [258, 229, 249, 264]) |
| `TestChooseRandomMoveEC20` | 2 | the six 20-empty-square positions (fixtures inline in the test; 13/0/0/9/0/13 legal options per position): `test_choose_random_move_ec20` (for each position, choose_random_move returns a single legal move when the position has options, or the pass — an empty move — when it has none); `test_choose_random_move_ec20_equidistributed` (N = 1000 draws per position: every draw is validated, and the frequencies accumulated over the AVAILABLE options are reasonably flat — a chi-square over the k options, df = k - 1, kept below the 4-sigma threshold) |
| `TestGamePositionMakeRandomMove` | 3 | `game_position_make_random_move` (pick a random move, apply it on the position via position_flips, return the resulting position + the move): a 20-empty-square fixture with exactly two legal moves (G1, G2, the legal-move set 16448): `test_n_simulations_give_only_the_two_boards` (N = 12 draws, seed 93 — both legal moves appear and ONLY the two resulting boards come out); `test_the_returned_position_is_consistent_with_the_move` (every returned position is exactly the position_flips output for the drawn move); `test_the_returned_position_is_one_move_ahead` (each returned position is one stone ahead of the fixture: 44→45 stones, 20→19 empty) |

## Goldens pinned

- The initial-position square sets: the mover {E4, D5}
  (0x0000000810000000), the opponent {D4, E5}
  (0x0000001008000000) — the official Othello International
  setup.
- The pick golden: the exact 1000-draw
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
