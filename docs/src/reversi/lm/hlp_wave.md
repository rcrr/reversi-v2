# reversi/lm/hlp_wave.py
The concurrent WAVE generator (the I-017 T5, D-170): the G₁
(ODP-9) corpus engine — W lanes of games in LOCKSTEP (step
= one real move, the pass folds into the step, the double
pass discards the lane), the boundary harvest + respawn,
the bit-exact cross-validation against the T4 reference.
> State: D-170 · pending · 2026-09-12 · suite 11/0/1 (LONG: the 1e6 benchmark)

## API
- `WaveState` / `make_wave(W, slot_base)` — the wave arrays
  (mover/opp u64, counter i64 = the slot, slot i64, alive
  bool) + the run bookkeeping (next_slot, steps,
  harvested, dead_total).
- `step_wave(state, table) -> (move, pass_mask, dead)` — one
  lockstep step (five full-wave vectorized calls, zero
  per-lane branching): the two Kogge-Stone legal passes
  (the pass lanes' source is the swapped side's legal set),
  `_pick_wave`, the make_move (the swapped source for the
  pass lanes), the counter walk (`~dead`).
- `run_wave(total, ec_target, table, wave_size, sink,
  slot_base)` — the S = 60 - ec_target lockstep steps, the
  boundary harvest + respawn, until the quota is met.
- `BufferSink` — the v1 in-memory sink (the boundary chunks
  (mover, opp, slot); `flatten()`).
- `_pick_wave(src, counter, table) -> (move, step)` — the
  numba-parallel ODP-9 pick (the HW popcount, the rank
  lookup table[k][counter % k], the rank-th set bit).

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
- Cross-validation: lane g ≡
  `random_play(seed, ec_target, counter0=g)` (T4, D-162):
  the semantics is a function of (table, slot) only —
  lanes/threads never enter the semantics (reproducible by
  construction; LAW-2 pins it).
- Parallelism: lanes in parallel (prange) — the house
  pattern: the shared Kogge-Stone kernels are already
  @nb.njit(parallel=True, cache=True); the per-lane per-ply
  work (a u64) is below the thread-split threshold.
- Sink v1: the arrested POSITIONS only (mover, opp, slot) —
  "di quello si prendono le statistiche" (Roberto); the file
  writer / corpus format (the POSITIONS step D-157
  alignment) is the T6 concern.

## Verified invariants
- K1: `_pick_wave` vs `pick_move` — 2000 random triples +
  the zero-src pass (PA, no step) + the hand-computed
  identity row.
- LAW-1: 63 games (W=7, 9 waves) at ec ∈ {55, 40, 20}:
  every harvested (mover, opp) bit-identical to the T4
  random_play at the same slot, the slots unique.
- LAW-2: the phase invariance — slot 1234 harvested from a
  W=1 wave and from a W=100 wave (lane 34) is the same
  position.
- The W=1 trajectory: slot 712 (the first pass carrier of
  the seed-42 scan — passes are ~0.05% of the games: 42
  plies, the PAs at plies 31/33, the pinned literals): the
  wave trajectory (the recorded PA + the folded real move)
  ≡ the T4 move list, the final position bit-identical.
- LAW-3: the synthetic corner wall (the T4 A1+C3 mover
  corner walled by the 17-stone block): ONE step = [PA,
  D3] (the rank-0 fold), the counter walks exactly ONCE,
  the applied position ≡ the T4 [PA, D3] outcome.
- LAW-4: the constructed non-full deadlock (61 stones, 3
  empty — E4, F4, G4; the 57-stone field + the 4-stone
  A2..B3 block, the pinned literal): the lane DIES on the
  first step (the PA-swap coast — the occupied set is
  invariant, the fields are swapped — the frozen counter),
  it is not harvested, the wave respawns it with slot 1 at
  the initial position.
- The run integrity: the quota exactly 1000, the slots
  unique, every harvested position at EXACTLY ec 20 (the
  boundary invariant); the ec domain [0, 60]; the ec=60
  arrest is the initial position (0 steps per wave).
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
  D-157 alignment): T6.
- The G₀ reference generator (the per-move PRNG draw, the
  doc §2): the T6 gate tool.

## Conventions
- The numba house pattern: @nb.njit(parallel=True,
  cache=True), prange over lanes; the HW popcount (numba
  has no .bit_count on uint64); the u64 arithmetic wants
  explicit np.uint64 constants (u64 - int promotes to
  float64 in numba).
- The slots run ONWARD across waves (a dead lane consumes
  its slot — the harvested slots are unique but NOT
  contiguous); counter = slot (the phase pin).
- The test seam: the tests mutate the wave arrays directly
  (the lane injection) — no injection API in the engine.

## Integration
- run_utests.sh section 4 (next to test_hlp_random_play).
- The T6 design gate (the v4 doc §7) runs on top: the G₁
  1e6 ≈ 5 s (the wave) + the G₀ pairs (the T4 Python).
- The I-017 pipeline: the wave is the POSITIONS-level
  generator (the step 3, D-157) at the numba tier.
