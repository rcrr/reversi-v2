# reversi/test/test_hlp_random_play.py
The NO-DB micro-suite of the single-game random play generator
(the I-017 T4, D-162) + the marginal / joint frequency
accumulators (the I-017 T7, D-177 + T8, D-178) + the PRNG
integration (T9): the ODP-9 table properties, the pick kernel,
the initial position, the HAND-COUNTED games (the identity-table
trace, the pass branch, the full game, the non-full double pass
— the D-169 fix), the seeded games (the pinned trajectories +
the independent replay), the ec pin (the hand-counted stone
counts), the marginal accumulator (the LMC vs the independent
oracle, the R2 cross-check, the chunk-merge), the joint
accumulator (the cross-feature + the same-feature, the diagonal
the SU = 1 lock), and the PRNG integration (the corpus
reproducibility + the end-to-end marginals). 9 classes / 23
tests / no DB.
> State: D-162 (T4) + D-177 (T7) + D-178 (T8) + D-179 (T9) ·
2026-09-13 · suite 23/0/0

## Coverage

| class | tests | what it pins |
|---|---|---|
| `TestPickTable` | 2 | `test_valid_permutations` (all 64 rows are permutations of 0..n-1, the shape (65, 64), the read-only flag); `test_reproducible` (same seed equal, different seed differs) |
| `TestPickMove` | 2 | `test_kth_set_bit_walk` (the 0b101 legal: counter 0, 1, 2 -> [0, 2, 0] — the 2 % 2 wrap); `test_pass_no_consume` (the PA + the untouched counter) |
| `TestInitialPosition` | 1 | `test_the_start` (the D4+E5 / D5+E4 hex pins, the {E3, F4, C5, D6} legal set — the hand-derived one, the opponent's 4 as well, the ec = 60) |
| `TestHandCountedGames` | 4 | `test_identity_short_game` (the 3-ply E3/F3/C5 trace — the first move E3 hand-derived: rank 0 = the lowest legal — the final position hex, the ec trace [59, 58, 57], the replay); `test_pass_from_wall_position` (the synthetic corner wall: the A1+C3 mover walled in by the 17-stone wall — ZERO legal moves verified, the PA then D3, the ec kept by the pass [45, 44]); `test_non_full_double_pass_is_game_over` (the constructed 61-stone deadlock — E4, F4, G4 empty, the 57-stone field walled around the empty run + the 4-stone A2..B3 block, ONE pass then the game-over, the ec = 3 kept — the D-169 fix's regression guard); `test_full_game` (seed 3 to ec = 0: 60 plies, the board fills 35/29, the game-over fires, the replay) |
| `TestSeededGames` | 4 | `test_seed7_pinned` (40 plies, ec 20, the first 10 moves F4/D3/C2/F5/D6/C5/G6/G5/G4/H7, the final position hex, the 40-stone count, the replay); `test_seed8_differs` (the moves + the final position differ, the seed-8 pinned tail); `test_counter0_phase_shifts` (the same seed, counter0 0 vs 7: the same 1-ply length, a different first move — rank 0 vs 7 % 4 = 3); `test_ec_target_domain` (the ValueError outside [0, 60], the >= 60 zero-ply arrest) |
| `TestEcPin` | 2 | `test_hand_counted_stone_counts` (D-177: the identity 3-ply, each real move adds one stone — the hand-counted 4, 5, 6, 7 stones -> ec 60, 59, 58, 57, ec_of = 64 - popcount(mover\|opponent) at each step, the re-derivation matches the game); `test_empty_count_identity` (the ec at the arrest = 64 - occupied, <= ec_target) |
| `TestMarginalAccumulator` | 3 | (D-177; the toy corpus, a 300-game G0 wave at ec 20, the toy FeatureSet = the intercept + the LMC + the R2) `test_lmc_hand_counted` (the single-instance dense bincount vs the INDEPENDENT oracle position_legal_moves — NOT compute_indexes); `test_pattern_cross_check` (the R2 inst0 vs an independent per-position dict via compute_indexes); `test_chunk_merge` (one chunk == two half-chunks) |
| `TestJointAccumulator` | 3 | (D-178; the same toy corpus, a 200-game G0 wave) `test_cross_feature_joint` (the (LMC, R2) 4 instance-pairs, each joint vs the independent per-position oracle); `test_same_feature_diagonal` (the (R2, R2) 16 instance-pairs, the diagonal ZERO off-diagonal — the SU = 1 lock); `test_chunk_merge` (one chunk == two half-chunks) |
| `TestPrngIntegration` | 2 | (T9; the G0 wave -> the accumulator, the 2-feature toy set) `test_corpus_reproducibility` (same seed -> the SAME frequency tables bit-exact, the different seed -> different); `test_small_end_to_end_marginals` (every sub-variable sum == N, K_obs <= n_conf, the LMC marginal vs the INDEPENDENT oracle position_legal_moves) |

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
- The toy FeatureSet (the T7-T9 accumulator infrastructure):
  the `_toy_fset()` = the intercept + the LMC (mask all, amask
  0 — the code the legal-move count) + the R2 (the 8-square
  mask, the 4 D8 instances, n_conf 6561); the `_toy_blocks()`
  mirrors load_campaign's column layout; the `_toy_corpus()`
  the small G0 wave (the seed, the ec, the N).
- The INDEPENDENT oracles (the house double-check, T7-T9): the
  LMC marginal via position_legal_moves (NOT compute_indexes);
  the R2 / the joints via the manual per-position dict over
  compute_indexes.

## Conventions

- The house test header (the "How to run" block).
- The synthetic positions by their hex literals + the square
  names in the comments (the naming convention: uppercase,
  A1 = top-left = bit 0).
- The module-internal seam (`_play_from`) used directly for
  the pass branch (a random_play from the initial position
  cannot reach a wall in a few plies).
- The accumulators' micro-suites reuse the toy FeatureSet / the
  toy blocks / the toy corpus helpers (the TestMarginalAccumulator
  static methods, shared by the joint + the integration
  classes) — the small, no-DB, hand-checkable infrastructure.

## Integration

- Consumed by `run_utests.sh` (section 4 — the pipeline, at the
  head: the T16-level data module, the worker pending).
- The T5 wave engine reuses these pins (the single-game trace
  is the cross-validation reference).
- The T7-T9 accumulators are the FEATURE_ANALYSIS phase-1 data
  plane (the marginals + the joints); the T16 worker wires
  them into the pipeline (the cache flow + the reports).
