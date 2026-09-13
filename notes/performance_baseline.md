# Performance Baseline — the wave tier (the OPTIMIZATION
# phase reference)

> State: the D-175/D-176 baseline (2026-09-13). Hardware:
> 8 cores, 188 GB RAM. Purpose: the reference numbers for
> the profiling session (the OPTIMIZE pattern, scheduled
> AFTER the SU level is complete — Roberto has ideas; the
> commitment: a step-by-step algorithm walkthrough + the
> code reviewed together). The goal: beat these.

## The G0 corpus engine (run_wave_g0, W=1e6, seed 42 — the
harvest throughput, the dead-lane overhead INCLUDED)

| config | N | wall | rate | note |
|---|---|---|---|---|
| G0 ec=0 (the full game) | 1e7 | 52.8 s | 189,571 games/s = ~11.4M moves/s (60 moves) | steady state (11 waves) |
| G0 ec=20 | 1e7 | 36.0 s | 277,470 games/s = ~11.1M moves/s (40 moves) | steady state (11 waves) |
| G0 ec=20 | 1e6 | 6.9 s | 144,188 games/s | single wave, warmup-tainted |
| G0 ec=0 | 1e6 | 11.6 s | 86,480 games/s | single wave, warmup-tainted |
| G1 ec=20 (the reference) | 1e6 | 5.3 s | 188,491 games/s | single wave, warmup-tainted — the clean steady-state G1 benchmark is DUE |

KEY INVARIANT: the moves/s is ~11M constant (the per-move
cost dominates; the games/s scales 60/moves-per-game).
The gated 1e6 runs (gate observation included): G1 20.5
min, G0 19.6 min. The T4 scalar reference: 4.55 ms/game
(the GLM audit) — the wave tier is ~150× T4 at ec=20.
Feature encoding: fset.compute_indexes = 1.7M positions/s.

## The suite

833/0/97 default (2026-09-13).

## Why it matters

Beyond the pleasure of well-made code that flies: large
population generation will be needed AGAIN for future
projects (not yet disclosed) — the wave tier must stay
fast. The baseline above is the starting point of the
profiling session.
