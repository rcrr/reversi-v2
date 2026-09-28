# Performance Baseline — the wave tier (the OPTIMIZATION
# phase reference)

> State: the D-175/D-176 baseline (2026-09-13). Hardware:
> 8 cores, 188 GB RAM. Purpose: the reference numbers for
> the profiling session (the OPTIMIZE pattern, scheduled
> AFTER the SU level is complete — Roberto has ideas; the
> commitment: a step-by-step algorithm walkthrough + the
> code reviewed together). The goal: beat these.

## The wave corpus engine (run_wave, W=1e6, seed 42 — the
harvest throughput, the dead-lane overhead INCLUDED)

| config | N | wall | rate | note |
|---|---|---|---|---|
| wave ec=0 (the full game) | 1e7 | 52.8 s | 189,571 games/s = ~11.4M moves/s (60 moves) | steady state (11 waves) |
| wave ec=20 | 1e7 | 36.0 s | 277,470 games/s = ~11.1M moves/s (40 moves) | steady state (11 waves) |
| wave ec=20 | 1e6 | 6.9 s | 144,188 games/s | single wave, warmup-tainted |
| wave ec=0 | 1e6 | 11.6 s | 86,480 games/s | single wave, warmup-tainted |
| G1 ec=20 (the reference) | 1e6 | 5.3 s | 188,491 games/s | single wave, warmup-tainted (the clean steady-state G1: 5.4 s = 185,415 games/s, the LONG tier — the DUE resolved) |

KEY INVARIANT: the moves/s is ~11M constant (the per-move
cost dominates; the games/s scales 60/moves-per-game).
The gated 1e6 runs (gate observation included): G1 20.5
min, the wave 19.6 min. The T4 scalar reference: 4.55 ms/game
(the GLM audit) — the wave tier is ~150× T4 at ec=20.
Feature encoding: fset.compute_indexes = 1.7M positions/s.

## The T10 accumulation throughput (the 1e7 SU-analysis corpus on the
real A2050 feature set, 47 sub-variables — D-180)

| stage | wall | rate | note |
|---|---|---|---|
| generation (11 waves) | 33.9 s | 294,564 games/s | the baseline match |
| marginal (47 sub-variables) | 9.2 s | 1.08M pos/s | ~100x BELOW the section 7 model (11-33 min) — NO numba needed |
| joint light (LMC x R2, 4 inst-pairs) | 6.7 s | 1.49M pos/s | fine for the typical request |
| joint heavy (2X5COR x 2X5COR, 64 inst-pairs) | 274 s | 36,470 pos/s | the Python dict merge bottleneck — the numba dict-pass lever if the heavy pairs must fly (deferred to T16) |

The default pipeline (the marginal, su_pairs = []) is 43 s
total at 1e7 (gen + marginal) — the numba optimization is NOT
needed for the default; the heavy-pair joint is the only slow
path (a known cost for the heavy pair requests).

## The suite

843/0/97 default (2026-09-13, after T7-T9; +10 the I-017
micro-suite).

## Why it matters

Beyond the pleasure of well-made code that flies: large
population generation will be needed AGAIN for future
projects (not yet disclosed) — the wave tier must stay
fast. The baseline above is the starting point of the
profiling session.
