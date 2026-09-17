# reversi/lm/client.py
The INFERENCE API of the reversi package — a pure CONSUMER of the
pipeline output: given a `ModelWeights` (loaded from the saved
file), the two factories close over it and return Evaluation
Functions in Y space (the game-value space the engine uses) — a
scalar `ef: Position -> float` and a vectorized
`ef: PositionArray -> (N,) float32` (bit-exact per position). No
database, no cache, no pipeline: a saved model file is all the
client needs — the shape the endgame-solver production models
(the `A2xxx` family) plug into.

## API

| name | contract |
|---|---|
| `make_evaluation_function(mw: ModelWeights) -> Callable[[Position], float]` | The scalar EF factory (`@validate_call`, arbitrary_types_allowed). Closes over `mw` via `_prepare_weights`; the returned `ef` takes a scalar Position and returns a Python float (the f32 z2y output as a float64 view). |
| `make_evaluation_function_array(mw: ModelWeights) -> Callable[[PositionArray], npt.NDArray[np.float32]]` | The vectorized EF factory (`@validate_call`). The returned `ef` is STRICT ARRAY: it accepts a 1-D PositionArray (a (N, 2) uint64 array is coerced by the PositionArray validator) and returns a (N,) float32 array, bit-exact vs the scalar EF per position. A 2-D structured array raises `ValueError` (the standard 1-D guard); a scalar Position or bare lists raise the Pydantic `ValidationError`. |

## Architecture

136 lines.

- Imports (L28-40): numpy + numpy.typing, `typing.Callable`,
  `pydantic.validate_call/ConfigDict`, `ModelWeights`,
  `zed_fun_factory`, `sigmoid`, `Position`/`PositionArray`
  (annotation-only use).
- `_prepare_weights` (L47-66): the closure setup shared by BOTH
  factories: `offsets = mw.iwmap_feature_offset`, `z2y =
  zed_fun_factory(mw.logit_clipping)` (only the z→y half — the
  client never transforms observations), `expanded_offsets =
  np.repeat(offsets[:-1], n_instances_per_feature)` (the
  per-INSTANCE w_dense start offsets: each feature's start repeated
  n_instances times — e.g. EDGE's start, 4 times for its 4
  instances).
- `make_evaluation_function` (L69-93): `ef(p)` — 1. `indexes =
  mw.feature_set.compute_indexes(np.array([p]))[0]` (the length-1
  batch wrap, one index per feature INSTANCE); 2. `weights =
  mw.w_dense[expanded_offsets + indexes]`; 3. `z_pred =
  sigmoid(np.sum(weights))`; 4. `y_pred =
  z2y(np.array([z_pred], dtype=np.float32))[0]`, returned as a
  Python float.
- `make_evaluation_function_array` (L96-136): `ef(p)` — 1. the 1-D
  guard (the PositionArray validator admits 2-D structured arrays,
  no ndim check there); 2. `indexes =
  mw.feature_set.compute_indexes(p)` — the SAME batch API the scalar
  path wraps (the numba prange kernel over N; no new kernel);
  3. `weights = mw.w_dense[expanded_offsets + indexes]` (the (I,) u32
  broadcast over the (N, I) u32 batch) and `linear_predictor =
  weights.sum(axis=1)` (the per-row f32 sum — the same 1-D reduction
  as the scalar `np.sum`, hence bit-exact per row); 4. `return
  z2y(sigmoid(linear_predictor))` (element-wise f32 expit + affine).
  No numba in the client: the cost is dominated by
  `compute_indexes`, exactly as in the DESIGN_MTR level.

The dense path and the substitution rule (verified):
`iwmap_feature_offset` is a BOUNDARY array of shape (F+1,) —
`offsets[fid]` is the first w_dense slot of feature `fid`
(`offsets[F]` = K), so `expanded_offsets + indexes` indexes
`w_dense` correctly per design-matrix column (a probe using
`offsets` without `[:-1]` would misalign every feature after the
first). The gathered values are the TRAINED weights for confirmed
configurations (frequency ≥ `stat_model.frequency_cut_off`) and the
SUBSTITUTION values (orbit mean for patterns, `np.interp` for
mobility — hlp_generate L167-196) for every configuration without a
dedicated weight (unseen + below-cutoff "IC"). Consequence (verified
measured): the dense path and the literal compressed model
(`ctx.w` over `ctx.design_matrix`) agree on a training position iff
every configuration it touches is confirmed — rlm_04 (cut 10):
1923/199932 positions differ (373 EDGE configs in `wmap_fallback`,
freq < 10; max |Δy| 31.56, mean 4.98); rlm_01 (cut 2): 5/10. The ef
pins are therefore pinned against the DENSE values (what the shipped
model actually computes); the rlm_03 pins (cut 1) equal the
compressed values as well.

## Verified invariants

Pinned by the statics of `probes/verify_save.py` (A7 no dead import,
A8 the 2-entry `__all__`, A9 no ws lines) + the full-chain suite +
`test_client`.

- rlm_04 EF bit-exact on 6 pinned training positions: pos 0 →
  −37.12018585205078, pos 1 → −28.228458404541016, pos 7 →
  45.391082763671875, pos 123 → 40.502410888671875, pos 999 →
  16.26209259033203, pos 199931 → 23.326324462890625 (suite A2030).
- rlm_04 EF on `vld_positions[42]` → 11.932792663574219: rlm_04
  validation (bid [5]) contains EDGE configurations unseen in
  training — the substitution path (orbit weighted mean) pinned
  end-to-end (suite A2030).
- rlm_03 EF bit-exact on 6 pinned training positions (suite A2050,
  VLONG): pos 0 → 7.2613525390625, pos 5 → −32.98143768310547, pos
  123 → 40.5123291015625, pos 555 → 24.14972686767578, pos 9999 →
  −19.389434814453125, pos 1999178 → 57.8465576171875.
- VECTORIZED parity: the array EF equals the scalar EF
  bit-exactly per position — (a) on the synthetic rlm_04-mirror
  weights over 1000 seeded collision-free positions
  (test_client::test_parity_bit_exact, no DB); (b) on the TRAINED
  rlm_04 model: one batch call over the full 199932-position
  training set, the same 6 pins + the vld[42] pin (suite A2030).
  The vectorization removes the length-1 wrap and nothing else —
  the same math, the same bits.
- (N, 2) uint64 coercion: the array EF on the raw (N, 2) form
  equals the structured-form result (test_client::
  test_u64_coercion); the N=0 edge returns an empty (0,) f32
  (test_client::test_empty_batch).

## Open issues

None.

## Conventions

- BOTH factories are `@validate_call` (arbitrary_types_allowed);
  the array ef closure is validated too (the PositionArray
  annotation does the (N, 2) u64 coercion).
- Strict array: the array ef takes a
  1-D PositionArray only (the scalar contract is the other
  factory); the 1-D guard in the closure is the house pattern (the
  PositionArray validator does NOT check ndim for the
  structured dtype).
- Precondition (the compute_principal_indexes caller contract):
  the positions are collision-free (mover & opponent == 0); the
  client does not re-check.
- The sigmoid/z2y calls reuse the pipeline's own functions
  (hlp_gradient / hlp_zed) — the client cannot drift from the
  model's own transforms.
- The u32 arithmetic: expanded_offsets u32 + indexes u32 → u32 (the
  measured runtime promotion; the gather is a plain fancy index
  into the f32 w_dense).

## Integration

- `ModelWeights` is the only input; `model_weights_read_file`
  (model_weights.md) is the producer — the test modules compose the
  two.
- In-pipeline consumer: the CLIENT_CHECK level (the 16th
  level, after SAVE) re-reads the saved model file and builds the
  ARRAY EF on it — it recomputes the validation residuals in Y
  space and compares them to the in-memory VALIDATE forward pass
  within `client_check_tol` (the C1 ruling: the array form, the
  1100× speed ratio; the scalar EF stays pinned by test_client +
  the full-chain EF pins).
- Y-space output: both EFs return game values directly (the z2y
  inverse), usable by the engine as evaluation functions; the
  vectorized form is the batch workhorse (analytics over large
  position sets, the performance-study territory).
- Per-position cost: one `compute_indexes` call (the Numba kernels)
  + one f32 gather of `n_instances` values + one sum + sigmoid +
  z2y. Measured (this machine): 5,117 b/s scalar vs
  5,640,701 b/s array (the 1M-board PERF print test).
