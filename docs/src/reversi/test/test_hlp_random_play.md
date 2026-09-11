# reversi/test/test_hlp_random_play.py
The NO-DB micro-suite of the single-game random play generator
(the I-017 T4, D-162): the ODP-9 table properties, the pick
kernel, the initial position, the HAND-COUNTED games (the
identity-table trace, the pass branch, the full game) and the
seeded games (the pinned trajectories + the independent
replay). 4 classes / 12 tests / no DB.
> State: D-162 · pending · 2026-09-11 · suite 12/0/0

## Coverage

| class | tests | what it pins |
|---|---|---|
| `TestPickTable` | 2 | `test_valid_permutations` (all 64 rows are permutations of 0..n-1, the shape (65, 64), the read-only flag); `test_reproducible` (same seed equal, different seed differs) |
| `TestPickMove` | 2 | `test_kth_set_bit_walk` (the 0b101 legal: counter 0, 1, 2 -> [0, 2, 0] — the 2 % 2 wrap); `test_pass_no_consume` (the PA + the untouched counter) |
| `TestInitialPosition` | 1 | `test_the_start` (the D4+E5 / D5+E4 hex pins, the {E3, F4, C5, D6} legal set — the hand-derived one, the opponent's 4 as well, the ec = 60) |
| `TestHandCountedGames` | 3 | `test_identity_short_game` (the 3-ply E3/F3/C5 trace — the first move E3 hand-derived: rank 0 = the lowest legal — the final position hex, the ec trace [59, 58, 57], the replay); `test_pass_from_wall_position` (the synthetic corner wall: the A1+C3 mover walled in by the 17-stone wall — ZERO legal moves verified, the PA then D3, the ec kept by the pass [45, 44]); `test_full_game` (seed 3 to ec = 0: 60 plies, the board fills 35/29, the game-over fires, the replay) |
| `TestSeededGames` | 4 | `test_seed7_pinned` (40 plies, ec 20, the first 10 moves F4/D3/C2/F5/D6/C5/G6/G5/G4/H7, the final position hex, the 40-stone count, the replay); `test_seed8_differs` (the moves + the final position differ, the seed-8 pinned tail); `test_counter0_phase_shifts` (the same seed, counter0 0 vs 7: the same 1-ply length, a different first move — rank 0 vs 7 % 4 = 3); `test_ec_target_domain` (the ValueError outside [0, 60], the >= 60 zero-ply arrest) |

## Goldens pinned

- The identity-table regime: the `_identity_table()` fixture
  (table[n] = (0, ..., n-1)) makes the pick the (counter %
  k)-th set bit — the fully hand-computable regime (the E3 and
  the D3 first moves are hand-derived).
- The seeded trajectories: the seed-7 and the seed-8 literals
  (the plies, the ec, the first 10 moves, the final position
  hex) — the determinism proof (the same seed, the same
  trajectory, forever).
- The independent replay (`_replay`, the house double-check):
  every ply recomputed from the rules (board.py) + the table
  walk WITHOUT the module's loop logic — the pass only when
  legal == 0, the pick only the table value, the ec only the
  formula.

## Conventions

- The house test header (the "How to run" block).
- The synthetic positions by their hex literals + the square
  names in the comments (the naming convention: uppercase,
  A1 = top-left = bit 0).
- The module-internal seam (`_play_from`) used directly for
  the pass branch (a random_play from the initial position
  cannot reach a wall in a few plies).

## Integration

- Consumed by `run_utests.sh` (section 4 — the pipeline, at the
  head: the T12-level data module, the worker pending).
- The T5 wave engine reuses these pins (the single-game trace
  is the cross-validation reference).
