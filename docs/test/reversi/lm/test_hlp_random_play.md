# test/reversi/lm/test_hlp_random_play.py
The NO-DB micro-suite of the SU_ANALYSIS frequency data plane: the marginal / joint frequency accumulators + the
PRNG integration. The initial position, the ec pin (the hand-counted stone counts), the marginal accumulator (the LMC vs
the independent oracle, the R2 cross-check, the chunk-merge), the joint accumulator (the cross-feature + the
same-feature, the diagonal the SU = 1 lock), and the PRNG integration (the corpus reproducibility + the end-to-end
marginals). 5 classes / 10 tests / no DB.

## Coverage

| class | tests | what it pins |
|---|---|---|
| `TestInitialPosition` | 1 | `test_the_start` (the E4+D5 / D4+E5 hex pins — the official Othello setup, the mover {D3, C4, F5, E6} legal set — the hand-derived one, the opponent's 4 as well, the ec = 60) |
| `TestEcPin` | 1 | `test_ec_formula_hand_crafted` (the initial position ec 60, the hand-crafted 24-stone position ec 40, the full board ec 0 — ec_of = 64 - popcount(mover\|opponent)) |
| `TestMarginalAccumulator` | 3 | (the toy corpus, a 300-game play-path corpus at ec 20, the toy FeatureSet = the intercept + the LMC + the R2) `test_lmc_hand_counted` (the single-instance dense bincount vs the INDEPENDENT oracle position_legal_moves — NOT compute_indexes); `test_pattern_cross_check` (the R2 inst0 vs an independent per-position dict via compute_indexes); `test_chunk_merge` (one chunk == two half-chunks) |
| `TestJointAccumulator` | 3 | (the same toy corpus, a 200-game play-path corpus) `test_cross_feature_joint` (the (LMC, R2) 4 instance-pairs, each joint vs the independent per-position oracle); `test_same_feature_diagonal` (the (R2, R2) 16 instance-pairs, the diagonal ZERO off-diagonal — the SU = 1 lock); `test_chunk_merge` (one chunk == two half-chunks) |
| `TestPrngIntegration` | 2 | (the play-path corpus -> the accumulator, the 2-feature toy set) `test_corpus_reproducibility` (same seed -> the SAME frequency tables bit-exact, the different seed -> different); `test_small_end_to_end_marginals` (every sub-variable sum == N, K_obs <= n_conf, the LMC marginal vs the INDEPENDENT oracle position_legal_moves) |

## Goldens pinned

- The ec pin: ec_of = 64 - the occupied squares, hand-counted over the initial position (4 stones, ec 60) + a
  hand-crafted 24-stone position (ec 40) + the full board (ec 0).
- The toy FeatureSet (the accumulator infrastructure): the `_toy_fset()` = the intercept + the LMC (mask all, amask 0 —
  the code the legal-move count) + the R2 (the 8-square mask, the 4 D8 instances, n_conf 6561); the `_toy_blocks()`
  mirrors the pipeline's column layout (the `feature_blocks` property, D-266); the `_toy_corpus()` the small
  play-path corpus (the seed, the ec, the N; the random_game generator, D-285).
- The INDEPENDENT oracles (the house double-check): the LMC marginal via position_legal_moves (NOT compute_indexes); the
  R2 / the joints via the manual per-position dict over compute_indexes.

## Conventions

- The house test header (the "How to run" block).
- The synthetic positions by their hex literals + the square names in the comments (the naming convention: uppercase, A1
  = top-left = bit 0).
- The accumulators' micro-suites reuse the toy FeatureSet / the toy blocks / the toy corpus helpers (the
  TestMarginalAccumulator static methods, shared by the joint + the integration classes) — the small, no-DB,
  hand-checkable infrastructure.

## Integration

- Consumed by `run_utests.sh` (section 4 — the pipeline).
- The accumulators are the SU_ANALYSIS phase-1 data plane (the marginals + the joints); the worker wires them into
  the pipeline (the cache flow + the reports).
