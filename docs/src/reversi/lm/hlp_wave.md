# reversi/lm/hlp_wave.py
The concurrent WAVE generator (the I-017 T5, D-170 + D-174):
the G0 corpus engine — W lanes of games in LOCKSTEP (step =
one real move, the pass folds into the step, the double pass
discards the lane), the boundary harvest + respawn, the G0
uniform pick from the single global golden-pinned MT19937
(the I-017 CORPUS GENERATOR, the D-174 design call).
> State: D-170 + D-174 + D-192 (the initial-position fix —
the official Othello setup) + D-194 (the PRNG kernels moved
out to tools/prng.py — the single source) + D-195 (the wave
drives the stream through the class get_uint64_batch) ·
2026-09-15 · the G0 engine tests + the LONG 1e6 G0 benchmark ·
the G0 engine is the I-017 CORPUS GENERATOR (Roberto's design
call)

## API
- `INITIAL_MOVER` / `INITIAL_OPP` — the standard start (the
  official Othello setup, D-192: the mover (black, the
  starting player) E4+D5, the opponent (white) D4+E5;
  random_game.initial_game_position is the canonical source).
- `WaveState` / `make_wave(W, slot_base)` — the wave arrays
  (mover/opp u64, counter i64 = the step counter, slot i64,
  alive bool) + the run bookkeeping (next_slot, steps,
  harvested, dead_total).
- `step_wave_g0(state, prng) -> (move, pass_mask, dead)` — the
  G0 lockstep step (five full-wave vectorized calls, zero
  per-lane branching): the two Kogge-Stone legal passes (the
  pass lanes' source is the swapped side's legal set),
  `_pick_g0` (the uniform pick from the GLOBAL MT19937 stream
  — W draws per step via prng.get_uint64_batch, lane order),
  the make_move (the swapped source for the pass lanes), the
  counter walk (`~dead`). The stream state lives in the prng
  object (the class is the single public interface, the D-195).
- `run_wave_g0(total, ec_target, seed, wave_size, sink,
  slot_base)` — the G0 corpus run (the I-017 CORPUS
  GENERATOR, D-174): the S = 60 - ec_target lockstep steps,
  the boundary harvest + respawn, until the quota is met;
  the stream is GLOBAL across waves (the (wave, step, lane)
  draw order); deterministic in (seed, slot_base).
- `BufferSink` — the v1 in-memory sink (the boundary chunks
  (mover, opp, slot); `flatten()`).
- The G0 stream (the MT19937) is tools/prng.py — the single
  source (the D-194 move): this module imports the MT19937
  class and drives the wave through `get_uint64_batch(W)` (the
  D-195; it carries no PRNG code).
- `_pick_g0(draws, src) -> (move, step)` — the numba-
  parallel uniform pick (the HW popcount, the rank = draw
  % k, the rank-th set bit; the modulo bias < k/2^64, 12
  orders below the noise floor).

## Architecture
- The lockstep invariant (Roberto's option A, refined): one
  step = one REAL MOVE per live lane; the pass FOLDS into
  the step (the pass lane's move is picked from the swapped
  side's legal set — the second Kogge-Stone pass of the
  step, uniform, no partial recompute). A real move places
  exactly one stone (the flips recolor, they do not add),
  so ec = 60 - steps and every live lane is at EXACTLY
  ec_target at the boundary: the harvest is the WHOLE wave
  (no ragged exits, no per-step harvest mask, no inline
  respawn — the "brutish" logic lives in the rare per-wave
  boundary code).
- The double pass (the game over): at a step lm == 0 AND
  lo == 0 (the board is unchanged, so the state is
  terminal, full or not) kills the lane: it COASTS on the
  PA swap (the documented kernel behaviour — the only input
  that cannot corrupt the stale state; see Open issues),
  its counter freezes, it is not harvested, and it respawns
  at the boundary with the next slot.
- Parallelism: lanes in parallel (prange) — the house
  pattern: the shared Kogge-Stone kernels are already
  @nb.njit(parallel=True, cache=True); the per-lane per-ply
  work (a u64) is below the thread-split threshold.
- Sink v1: the arrested POSITIONS only (mover, opp, slot) —
  "di quello si prendono le statistiche" (Roberto); the file
  writer / corpus format (the POSITIONS step D-157
  alignment) is the 1e7 build concern.
- The G0 stream (D-174): a SINGLE GLOBAL MT19937 (the
  project's golden-pinned PRNG, the "one seed for all" pin;
  the class + the kernels are tools/prng.py — the D-194
  single source, driven through get_uint64_batch, the
  D-195) — one draw per (lane, step) in lane order, W draws
  per step; the pass/dead lanes' draws are CONSUMED
  (unused); the stream is global across waves (the run is
  one stream). The G0 trajectory of lane g depends on the
  (lane, step) draw ORDER (the W=1 trajectory is the scalar
  reference; the cross-W invariance does NOT apply to G0 by
  design — the trajectory is a function of the draw order,
  not just the slot).

## Verified invariants
- G0 (D-174/D-195): the batch draw (the class
  get_uint64_batch) vs the golden-pinned reference PRNG —
  bit-exact (2000 draws + the twist across the 312-word
  boundary + the continuation).
- G0 (D-174): the W=1 trajectory vs the scalar G0
  reference loop (the same stream discipline — one draw
  per step, the pass folded into the step, the dead
  lane's draw consumed): the moves + the final position
  bit-exact (seed 23, ec 50, the pinned literals).
- G0 (D-174): the run integrity + the determinism — 1000
  games (W=250, ec=20): the quota, the unique slots, every
  harvested position at EXACTLY ec 20; the same seed +
  slot_base replays bit-exactly (the second run identical
  mover/opp/slot); a different seed changes the harvest
  (the stream is consumed).
- The LONG benchmark (2026-09-12): 1e6 games (W=1e6,
  ec=20) in 5.3 s (188k games/s; the target was ≤ 120 s):
  2 waves, 36195 dead lanes absorbed by the respawn path,
  exactly 1e6 harvested. The 1e7 extrapolation ≈ 50 s
  (the target was ≤ 15 min).

## Open issues
- The board.py make_move legality test (scalar AND array):
  "the flips are non-zero" instead of "the square is EMPTY
  and the flips are non-zero" — an occupied square with a
  flipping ray is APPLIED (the docstrings promise None /
  unchanged). It never fires in the pipeline (only legal
  moves + PA are ever passed); the wave routes around it
  (the dead lanes ride the PA swap). The fix is 2 lines
  (the occupancy check) — Roberto's call (flagged in the
  D-170 report).
- The sink file writer + the corpus format (the POSITIONS
  D-157 alignment).

## Conventions
- The numba house pattern: @nb.njit(parallel=True,
  cache=True), prange over lanes; the HW popcount (numba
  has no .bit_count on uint64); the u64 arithmetic wants
  explicit np.uint64 constants (u64 - int promotes to
  float64 in numba).
- The slots run ONWARD across waves (a dead lane consumes
  its slot — the harvested slots are unique but NOT
  contiguous); counter = slot (the step counter).
- The test seam: the tests mutate the wave arrays directly
  (the lane injection) — no injection API in the engine.

## Integration
- run_utests.sh section 4 (next to test_hlp_random_play).
- The I-017 pipeline: the wave is the POSITIONS-level
  generator (the step 3, D-157) at the numba tier; the
  worker wrk_feature_analysis.py feeds the harvest to the
  accumulators (hlp_random_play).
