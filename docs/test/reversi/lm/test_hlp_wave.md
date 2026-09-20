# test/reversi/lm/test_hlp_wave.py
The NO-DB micro-suite of the concurrent WAVE generator (the corpus engine): the batch draw vs the golden-pinned
reference PRNG, the W=1 trajectory vs the scalar reference loop, the run integrity + the determinism, and the VVLONG 1e6
benchmark. 2 classes / 4 tests (3 + the VVLONG-gated benchmark) / no DB.

## Coverage

| class | tests | what it pins |
|---|---|---|
| `TestWaveEngine` | 3 | `test_batch_matches_reference` (the class `get_uint64_batch` vs a scalar `get_uint64` walk on the same seed — bit-exact over 2000 draws, the 312-word twist boundary crossed, plus the 100-draw continuation); `test_w1_trajectory_vs_scalar` (the W=1 wave vs the in-test scalar wave loop: the same stream discipline — one draw per step, the pass folded into the step, the dead lane's draw consumed — the move sequence and the final mover/opponent bit-exact, seed 23 / ec 50); `test_run_integrity_and_determinism` (1000 games, W=250, ec=20: the quota, the 1000 unique slots, every harvested position at EXACTLY ec 20, the same seed + slot_base replaying bit-exactly, and seed 43 differing from seed 42 — the stream-is-consumed guard) |
| `TestBenchmark` | 1 (VVLONG) | `test_1e6_wave_wall_clock` (the gate scale: 1e6 games, W=1e6, ec=20, seed 42 — the printed wall time is the deliverable, the assertion is the generous 600 s order-of-magnitude guard) |

## Goldens pinned

- The reference PRNG: a SECOND `MT19937(7)` instance walked with the scalar `get_uint64` — the batch kernel is pinned
  against the same class, not against a literal (the literals belong to the prng golden suite).
- The W=1 scalar reference loop: an in-test re-implementation of the wave stream discipline (`_kth_bit` = the rank-th
  set bit, one draw per step, the pass swapped, the double pass breaking the loop) — the independent derivation of the
  engine's trajectory (seed 23, ec 50).
- The run-integrity literals: 1000 harvested, 1000 unique slots, ec 20 on every position (64 - popcount(mover|opp)),
  seeds 42 / 43.

## Conventions

- The house test header (the "How to run" block).
- The VVLONG gate: `@unittest.skipUnless(tier_vvlong())` on the benchmark class; the default tier runs the 3 engine
  tests.
- The benchmark asserts a wall-clock GUARD only (600 s): the deliverable is the printed games/s line (no performance
  gates).

## Integration

- Consumed by `run_utests.sh` (section 4 — the pipeline, next to `test_hlp_random_play`).
- It pins `reversi/lm/hlp_wave.py` (the wave engine) and, in passing, the `tools/prng.py` batch draw the engine drives.
