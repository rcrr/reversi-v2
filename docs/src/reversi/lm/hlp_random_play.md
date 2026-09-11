# reversi/lm/hlp_random_play.py
The single-game random play generator (the I-017 T4, D-162):
from the initial position, a seeded loop over plies — the legal
moves (board.py), the move pick via the ODP-9 permutation
lookup table, position_make_move (D-140), the pass, the game
over, and the ec ARREST (the corpus keeps every ply of the
arrested game). The data module of the future FEATURE_ANALYSIS
level (the worker lands in T12).
> State: D-162 · pending · 2026-09-11 · suite 12/0/0

## API
- `RandomGame` — the dataclass outcome: the arrested position,
  the full move list (squares + PA), the ec trace, the ec at
  arrest, `stopped_by` ('ec' | 'game_over'), the table seed,
  the counter0 phase, the `plies` property.
- `ec_of(p)` — the PROVISIONAL ec formula: 64 - occupied (the
  moves remaining; the same expression
  board.position_final_value uses inline). T7 pins the EXACT
  formula against Roberto's DB code — if it differs, only this
  function changes (the loop is formula-agnostic).
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
  checked at the end of every ply (the full board fires the
  game-over before the next ec check).
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
  fires).
- The seeded games: the seed-7 trajectory pinned (40 plies, ec
  20, the first 10 moves, the final position) + the
  INDEPENDENT REPLAY (every ply recomputed from the rules +
  the table walk, without the loop logic); the seed-8 differs;
  the counter0 phase shifts the first move (rank 0 vs
  7 % 4 = 3).
- The ec domain: ec_target out of [0, 60] raises; ec_target
  >= 60 arrests before the first ply (0 plies, ec = 60).

## Open issues
- The EXACT ec formula: T7 pins it against Roberto's DB code
  (the "mele con mele" constraint) — ec_of is the provisional
  64 - occupied.
- The T5 wave engine (the numba tier): the vectorized advance
  step, the respawn of the finished slots, the streaming to
  the accumulators — the same pick semantics (this module's
  trace is the T5 cross-validation reference).
- The T6 vectorized pick kernel + the distribution test (the
  seeded rows' uniformity on a tiny corpus — the ODP-9
  closing).
- The mover-convention alignment with the DB extraction (the
  T12 detail — the symmetric start makes it a pure label).

## Conventions
- The house GNU header + the provenance docstring (the doc
  sections, the D-number).
- The @validate_call on the public game entry (the pydantic
  domain pins: the ec_target [0, 60]).
- The naming convention: the square names uppercase (D4, E5 —
  board.py move_from_str), A1 = top-left = bit 0.
- The module docstring carries the design rationale (the
  ODP-9 rejection of the PRNG-in-loop, the counter0 pin, the
  ec provisional status).

## Integration
- Consumes `board.py` (the Position, the legal moves, the
  D-140 make_move, the game over) + `tools/prng.py` (the MT19937
  table build, the D-159 port).
- Future consumer: the FEATURE_ANALYSIS level (T12, the worker
  wrk_feature_analysis.py) — the seeded corpus generator of
  the plan §3.2/§3.3 (the wave engine is the T5 extension of
  this module).
- Not a pipeline level itself: the lm data module of the
  future level (like hlp_validate / hlp_plot).
