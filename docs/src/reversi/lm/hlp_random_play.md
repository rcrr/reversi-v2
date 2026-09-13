# reversi/lm/hlp_random_play.py
The single-game random play generator (the I-017 T4, D-162) +
the marginal frequency accumulator (the I-017 T7, D-177): from
the initial position, a seeded loop over plies — the legal
moves (board.py), the move pick via the ODP-9 permutation
lookup table, position_make_move (D-140), the pass, the game
over, and the ec ARREST (the corpus keeps every ply of the
arrested game); the streaming per-sub-variable (code -> count)
marginal over the corpus (the FEATURE_ANALYSIS phase-1 data
plane). The data module of the FEATURE_ANALYSIS level (the
worker lands in T16).
> State: D-162 (T4) + D-177 (T7: the ec pin + the marginal
accumulator) + D-178 (T8: the joint accumulator) + D-179 (T9:
the PRNG integration) · 2026-09-13 · suite 23/0/0

## API
- `RandomGame` — the dataclass outcome: the arrested position,
  the full move list (squares + PA), the ec trace, the ec at
  arrest, `stopped_by` ('ec' | 'game_over'), the table seed,
  the counter0 phase, the `plies` property.
- `ec_of(p)` — the ec formula: 64 - the occupied squares (the
  moves remaining; the same expression
  board.position_final_value uses inline). PINNED (T7, D-177):
  EXACTLY the DB's `empty_count` — the regab extraction
  filters `empty_count = ec` (regab.py, the "mele con mele"
  window constraint); `empty_count` = the empty squares =
  64 - popcount(mover | opponent). The corpus is arrested in
  the SAME window as the DB extraction.
- `initial_position()` — the standard start (the D4+E5 / D5+E4
  2x2 center, both sides 4 legal moves, ec = 60).
- `build_pick_table(seed)` — the ODP-9 table (lru_cached,
  read-only): the seeded {n -> permutation of 0..n-1} over
  n = 1..64, Fisher-Yates over the seeded MT19937, the 2016
  total draws.
- `pick_move(legal, table, counter)` — the steady-state pick
  (NO PRNG): rank = table[k][counter % k], the move = the rank-
  th set bit; k == 0 -> (PA, counter) — the pass consumes NO
  counter step.
- `random_play(seed, ec_target, counter0=0, table=None)` — the
  public game (from the initial position; the ec arrest is
  checked before every ply; the MAX_PLIES=300 defensive guard).
- `_play_from(p, table, counter0, ec_target, seed)` — the loop
  seam from an arbitrary start (the tests' pass-branch entry).
- `MarginalAccumulator(fset, blocks)` — the streaming
  marginal frequency accumulator (T7, D-177): per sub-variable
  (the (feature, instance) column) the code -> count. The
  analysis unit is ONE design-index column (the design-matrix
  unit the weights live on) — each pattern instance is its own
  categorical variable (the code a single uint32 in [0,
  n_conf), no packing / no overflow: the 2X5COR^8
  structured-key concern is the feature-level / the joint
  statistics, not the per-column marginal). `.add(mover, opp)`
  feeds a corpus chunk (the wave boundary harvest); `.result()`
  returns per sub-variable (name, instance, n_conf, codes,
  counts) — the observed (non-zero support), len(codes) =
  K_obs, never-observed = n_conf - K_obs. The split:
  n_conf <= _DENSE_THRESHOLD (1e6; the A2050 max is 59049) ->
  the DENSE bincount, else the UNIQUE-MERGE dict. POOLED over
  all fed positions (the single-ec corpus — no per-ec split).
 - `JointAccumulator(fset, blocks, su_pairs)` — the streaming
   joint frequency accumulator (T8, D-178): per REQUESTED su
   pair (F_i, F_j) and per (instance_i, instance_j) in the pair,
   the (code_i, code_j) -> count — the instance×instance level
   (P6's matrix). The joint is SPARSE (the code_i x code_j space
   is too large for the dense — the unique-merge split). The key
   is the packed u64 (code_i * n_conf_j + code_j) — safe for the
   A2050 scale (the max is 59049^2 << 2^64). The same-feature
   pair (F, F) is allowed: the diagonal (the variable with itself)
   is the SU = 1 lock (OMITTED per the ODP-4 close); the off-
   diagonal (the D8 orientations of the same mask) is the
   anisotropy measure. `.result()` returns per pair (name_i,
   name_j, { (inst_i, inst_j): (codes_i, codes_j, counts) }).

## Architecture
- The ODP-9 pick (the doc design, D-162 landing): the random
  move is NOT picked by a PRNG draw per move — the seeded
  table (2016 draws at setup) + the per-game counter walk.
  NO PRNG in the loop (the doc: "the PRNG becomes the
  bottleneck" is the rejected alternative). T4 is the
  single-game path (no performance pressure); T5 is the numba
  wave engine that replays the SAME per-slot logic.
- The per-game phase (the D-162 pin): counter0 = the T5 slot
  id (slot i passes counter0 = i) — without a per-game phase
  every game would share the same rank walk (all 1e6 games
  make the same first move — the corpus would degenerate).
- The ec arrest (the "mele con mele" window constraint): the
  game stops when ec <= ec_target, checked before every ply;
  the corpus keeps every ply (the full trajectory).
- The game over: two consecutive passes (the
  position_is_game_over double-check) or the full board —
  the full board fires in the real-move branch; the
  non-full double pass in the pass branch (the D-169 fix:
  the pre-fix loop checked only the real-move branch and
  would spin passes to the MAX_PLIES guard on the rare
  non-full deadlock).
- The pass: the position_make_move PA (the player swap; board.py
  does not verify the pass-only-legal invariant — the loop
  guarantees it: the pass is played iff legal == 0).

## Verified invariants
- The initial position: the mover 0x0000001008000000 (D4+E5),
  the opponent 0x0000000810000000 (D5+E4), the legal set
  {E3, F4, C5, D6} (hand-derived), ec = 60.
- The table: every row n a valid permutation of 0..n-1 (all
  64 rows); same seed -> same table, different seed differs;
  the read-only flag (the lru_cache sharing).
- The pick kernel: the identity-table literals (the (counter %
  k)-th set bit, the 2 % 2 wrap), the no-consume pass.
- The hand-counted games (test_hlp_random_play): the identity-
  table 3-ply trace (the first move E3 hand-derived — rank 0 =
  the lowest legal square), the pass branch from the synthetic
  corner wall (the mover A1+C3 walled in by the 17-stone wall
  — ZERO legal moves verified; after the pass {D3, C4, D4};
  the PA then D3, the ec kept by the pass), the full 60-ply
  game (seed 3 to ec = 0: the board fills 35/29, the game-over
  fires), the NON-FULL double pass (the constructed 61-stone
  deadlock — E4, F4, G4 empty, the 57-stone field walled
  around the empty run + the 4-stone A2..B3 block, the
  pinned literal: ONE pass then the game-over, ec = 3 kept —
  the D-169 fix's regression guard).
- The seeded games: the seed-7 trajectory pinned (40 plies, ec
  20, the first 10 moves, the final position) + the
  INDEPENDENT REPLAY (every ply recomputed from the rules +
  the table walk, without the loop logic); the seed-8 differs;
  the counter0 phase shifts the first move (rank 0 vs
  7 % 4 = 3).
- The ec domain: ec_target out of [0, 60] raises; ec_target
  >= 60 arrests before the first ply (0 plies, ec = 60).
- The ec pin (T7, D-177): ec_of = 64 - the occupied squares,
  hand-counted over the identity 3-ply (no pass) game — the
  stone count 4, 5, 6, 7 -> ec 60, 59, 58, 57 (each real move
  adds one stone; the flips recolor, they do not add) + the
  empty-square identity on a longer game (ec at the arrest
  <= ec_target). This IS the DB's `empty_count` (the regab
  `empty_count = ec` filter) — the "mele con mele" window.
- The marginal accumulator (T7, D-177; the toy corpus, a
  300-game G0 wave at ec 20, the toy FeatureSet = the intercept
  + the LMC + the R2): the LMC (single-instance, the dense
  bincount) hand-counted against the INDEPENDENT oracle
  position_legal_moves (the legal-move count per position —
  NOT compute_indexes); the R2 inst0 (multi-instance feature,
  one column) cross-checked against an independent per-position
  dict count via compute_indexes; the CHUNK-MERGE invariance
  (one chunk == two half-chunks, the dense + the merge are
  chunk-invariant). Every sub-variable's count sum == N, every
  K_obs <= n_conf.
 - The joint accumulator (T8, D-178; the same toy corpus, a
   200-game G0 wave at ec 20): the (LMC, R2) cross-feature pair
   (the 4 instance-pairs (0, j)) + the (R2, R2) same-feature pair
   (the 16 instance-pairs (4 x 4)), each joint (code_i, code_j)
   -> count cross-checked against the INDEPENDENT per-position
   oracle (the manual dict via compute_indexes); the SAME-
   FEATURE DIAGONAL (ii, ii) has ZERO off-diagonal entries (the
   variable with itself, code_i == code_j always — the SU = 1
   lock); the CHUNK-MERGE invariance (one chunk == two half-
   chunks, the marginals and the joints alike). Every joint's
   count sum == N.

## Open issues
- (RESOLVED, D-177) The EXACT ec formula: PINNED — ec_of = 64 -
  popcount(mover | opponent) = the DB's `empty_count` (the
  regab `empty_count = ec` filter, the "mele con mele" window).
- The T5 wave engine (the numba tier) — LANDED (D-170,
  hlp_wave.py): the lockstep advance step, the boundary
  harvest + respawn, the streaming to the sink — the same
  pick semantics (this module's trace is the T5
  cross-validation reference; LAW-1/2 pin the bit-exact
  equivalence).
- The T6 vectorized pick kernel + the distribution test (the
  seeded rows' uniformity on a tiny corpus — the ODP-9
  closing).
- The mover-convention alignment with the DB extraction (the
  T16 detail — the symmetric start makes it a pure label).

## Conventions
- The house GNU header + the provenance docstring (the doc
  sections, the D-number).
- The @validate_call on the public game entry (the pydantic
  domain pins: the ec_target [0, 60]).
- The naming convention: the square names uppercase (D4, E5 —
  board.py move_from_str), A1 = top-left = bit 0.
- The module docstring carries the design rationale (the
  ODP-9 rejection of the PRNG-in-loop, the counter0 pin, the
  ec pin — D-177).

## Integration
- Consumes `board.py` (the Position, the legal moves, the
  D-140 make_move, the game over) + `tools/prng.py` (the MT19937
  table build, the D-159 port).
- Future consumer: the FEATURE_ANALYSIS level (T16, the worker
  wrk_feature_analysis.py) — the accumulator is the phase-1
  (corpus -> frequency tables) data plane; the corpus is the
  G0 wave (hlp_wave.run_wave_g0, D-174) fed chunk-by-chunk.
- Not a pipeline level itself: the lm data module of the
  future level (like hlp_validate / hlp_plot).
