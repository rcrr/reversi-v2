# reversi/lm/multi_ply_ef.py
The multi-ply evaluation function (D-674: the compiled EF leaf kernel + the per-model index
plan; D-675 adds the alpha-beta search + the public factory). The search-based evaluation
over a `ModelWeights`: the search descends from the position's empty count A to the model's
horizon B = `mw.ec` (A < B is a contract `ValueError`; A == B is the pure EF — the factory
delegates to the client EF, so the depth-0 anchor is bit-exact by construction); a horizon
leaf value is the EF of that position computed by the COMPILED leaf.

## API

| name | contract |
|---|---|
| `prepare_multi_ply_plan(mw: ModelWeights) -> tuple` | `@validate_call` — the per-model prepared data of the compiled EF leaf (computed ONCE, closed over by the factory): the 17-tuple (the client's `expanded_offsets` + the z2y affine `a1`/`b1` + the intercept flag + the mobility masks/sides + the 11 pattern-block arrays the principal-indexes kernel needs) |
| `_ef_leaf_indexes(mover, opponent, <plan[3:]>)` | private njit — the compiled index pipeline of a single position: the SAME njit kernels the client EF uses (the `FeatureSet.compute_indexes` pydantic wrapper inlined) — bit-exact with it; returns the (I,) uint32 index row |
| `_ef_leaf_value(mover, opponent, w_dense, <plan>)` | private njit — the full compiled EF leaf: the index row + the f32 gather + the SEQUENTIAL f32 sum + the piecewise f32 expit (the scipy form) + the z2y affine; deterministic, within the measured bound of the client EF |

## Architecture

- No-drift principle (client.md): the leaf reuses the pipeline's own njit kernels — the
  anti-transformations + the principal-indexes kernel of pattern.py, the indexes kernel of
  mobility.py, the legal-moves vector kernel of board.py — and the client's own
  `_prepare_weights` for the dense offsets.
- The z2y affine constants are the EXACT `hlp_zed_fun_factory` formula (the f64 division
  then the f32 cast) — bit-identical to the client's z2y closure.
- The pattern block of the plan MIRRORS the Python preparation of
  `PatternSet.compute_principal_indexes` (pattern.py) — the index-parity test pins the
  agreement, so a drift in one of the two preparations turns the suite red.
- The expit is the scipy piecewise form in f32 (x ≥ 0: 1/(1+exp(−x)); x < 0:
  e = exp(x), e/(1+e)) — the same shape as the client's `sigmoid` (scipy expit).

## Verified invariants

Pinned by `test_multi_ply_ef` (4 tests, no DB — the fixture model ec16, the rebuildable LM
fixture D-671/672, + 100 seeded playout positions at ec16):

- Index parity BIT-EXACT: every compiled index row equals the client's
  `feature_set.compute_indexes` row (`assert_array_equal`, 100 positions).
- Leaf value within the measured bound: |leaf − client EF| ≤ 0.05 in Y on all 100 positions
  (a drift detector, 6000× the measured margin — the D-674 measurement: max 8e-6, mean
  6.5e-7, 85/100 positions bit-equal; the 409-ulp linear-predictor gap of the numpy pairwise
  sum vs the sequential sum is compressed to ~1e-6 in Y by the expit).
- Determinism: two leaf calls return the same f32 bits.
- Plan dtypes: u32 indexes / u64 bitboards / u8 sides / f32 affine (the house contracts).

## Conventions

- The Y output range contract (D-670) applies unchanged: NO clip anywhere; the search window
  is derived from `logit_clipping` (R = 64/(1−2c) + margin — ±66 for c = 0.01, the same
  ground window the endgame solver's alpha-beta uses).
- The leaf is value-only in v1 (no best move) — the search-based evaluation returns the
  value of the position; the root best move is a D-675+ concern.
