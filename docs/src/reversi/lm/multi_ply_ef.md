# reversi/lm/multi_ply_ef.py
The multi-ply evaluation function (D-674: the compiled EF leaf kernel + the per-model index
plan; D-675: the float32 alpha-beta search + the public `make_evaluation_function` factory).
The search-based evaluation over a `ModelWeights`: the search descends from the position's
empty count A to the model's horizon B = `mw.ec` (A < B is a contract `ValueError`; A == B
is the pure EF — the factory delegates the horizon lanes to the client EF in a SINGLE
batched call, so the depth-0 anchor is bit-exact by construction); a horizon leaf value is
the EF of that position computed by the COMPILED leaf.

## API

| name | contract |
|---|---|
| `make_evaluation_function(mw: ModelWeights) -> Callable[[PositionArray], NDArray[f32]]` | the public factory — the returned `ef` is STRICT ARRAY (the client array-EF contract: a structured PositionArray of any shape in, same-shape float32 out; a (N, 2) uint64 batch is coerced to 1-D by the PositionArray validator; a scalar Position or bare lists raise the Pydantic `ValidationError`). Every position's empty count A must be >= the model horizon B = `mw.ec` (a `ValueError` naming the offending count); the batch is split first: the A == B lanes go to the CLIENT EF itself in a SINGLE batched call (the bit-exact depth-0 anchor — the EF is per-position, so the batched values are the individual ones), only the A > B lanes run on the worker pool in the alpha-beta search to the horizon (the D-669 idiom: the compiled search releases the GIL) |
| `prepare_multi_ply_plan(mw: ModelWeights) -> tuple` | `@validate_call` — the per-model prepared data of the compiled EF leaf (computed ONCE, closed over by the factory): the 17-tuple (the client's `expanded_offsets` + the z2y affine `a1`/`b1` (the EXACT hlp_zed formula) + the intercept flag + the mobility masks/sides + the pattern-block arrays the leaf needs) |
| `_ef_leaf_indexes(mover, opponent, <plan[3:]>)` | private njit — the compiled index pipeline of a single position: the SERIAL transcription of the client's njit kernels (the anti-transformation scalar impls of board.py, the mobility loop of mobility.py, the pack/base-3/coset-min pipeline of pattern.py) — bit-exact with `FeatureSet.compute_indexes` |
| `_ef_leaf_value(mover, opponent, w_dense, <plan>)` | private njit — the full compiled EF leaf: the index row + the f32 gather + the SEQUENTIAL f32 sum + the piecewise f32 expit (the scipy form) + the z2y affine; deterministic, within the measured bound of the client EF |
| `_ab_eval(mover, opponent, state, w_dense, <plan>, horizon_stones)` | private njit — the float32 alpha-beta (the endgame-solver discipline, value-only): the horizon node is the EF leaf, the terminal the exact WOF as f32, the no-move node passes (sides swap, value negated); the static bsf move order, the zero-window propagation (the child window is the negated parent window), the cutoff at value >= beta, the strict > alpha rise; `state` is the 2-element F64 (alpha, beta) array (the f32 windows are exact in f64 — the int64 state of the endgame solver fits there only because the game values are integers) |

## Architecture

- No-drift principle (client.md): the leaf inlines the BODIES of the pipeline's own njit
  kernels in their single-position form, and uses the client's own `_prepare_weights` for
  the dense offsets. The batch `parallel=True` kernels are NOT called: they cannot run from
  the worker-pool threads (the LLVM `allocate_sched` crash) — and the serial transcription
  is 170-190x FASTER at N=1 (the batch forms pay a large fixed prange/scheduler overhead per
  call). The index-parity test pins the bit-exact agreement with the client's
  `compute_indexes`, so a drift in one of the two transcriptions turns the suite red.
- The z2y affine constants are the EXACT `hlp_zed_fun_factory` formula (the f64 division
  then the f32 cast) — bit-identical to the client's z2y closure.
- The pattern block of the plan MIRRORS the Python preparation of
  `PatternSet.compute_principal_indexes` (pattern.py).
- The expit is the scipy piecewise form in f32 (x ≥ 0: 1/(1+exp(−x)); x < 0:
  e = exp(x), e/(1+e)) — the same shape as the client's `sigmoid` (scipy expit).
- The search values are seen from the point of view of the mover at each node (the child
  values are negated at each ply — the negamax convention of the endgame solver, whose
  `final_value_of` leaf is already mover-point-of-view).

## Verified invariants

Pinned by `test_multi_ply_ef` (18 tests, no DB — the rebuildable LM fixtures D-671/672 +
seeded playout positions; the full 100-position scale in the LONG tier):

- Index parity BIT-EXACT: every compiled index row equals the client's
  `feature_set.compute_indexes` row (`assert_array_equal`).
- Leaf value within the measured bound: |leaf − client EF| ≤ 0.05 in Y (a drift detector,
  6000× the D-674 measurement: max 8e-6, 85/100 positions bit-equal); deterministic (two
  calls, the same f32 bits); plan dtypes the house contracts.
- Depth-0 anchor BIT-EXACT: the A == B batch equals the client EF bit-exactly (the single
  batched delegation call).
- Depth 1-2 vs the INDEPENDENT full-width minimax oracle (pure Python, no pruning, its own
  move enumeration — the oracle's independence is in the search logic; the horizon leaves
  use the compiled leaf, a separately pinned concern): `assert_allclose` rtol/atol 1e-3.
- Depth 3-4 structural: float32, the batch shape, |v| within the D-670 range
  (R = 64/(1−2c)), determinism.
- The search contract: A < B → `ValueError`; scalar Position / bare lists → `ValidationError`;
  the empty batch → the empty float32 array.
- The search discipline on a trivial INTERCEPT-ONLY model (the hand-computable values): a
  normal depth-1 root is −y0, a PASS root is +y0 (the negamax sign convention + the pass
  handling, pinned exactly against the scipy-expit reference y0).

## Conventions

- The Y output range contract (D-670) applies unchanged: NO clip anywhere; the root window
  is derived from the clipping: R = ceil(64/(1−2c)) + 1 (67 for c = 0.01 — it strictly
  contains the EF range ±64/(1−2c) = ±65.31, as the C ground window ±66 contains the
  game-value range).
- v1 is VALUE-ONLY (no root best move) — the move-ordering / best-move stage is deferred
  (the user: "per ora NON facciamo un dynamic ordering").
- The compiled search releases the GIL: the A > B lanes run on the worker pool (one thread
  per CPU, capped at the lane count, a queue of lane indices, the lane errors surfaced at
  the boundary — the D-669 `_solve_pool` idiom); the A == B lanes never enter the pool (one
  batched client-EF call — the per-lane pool delegation was the batch-overhead bottleneck at
  scale: 189,721 one-position calls took ~6.5 min, the single batched call ~1 s).
