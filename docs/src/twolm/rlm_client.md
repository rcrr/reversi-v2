# twolm/rlm_client.py
The INFERENCE API of the twolm package — the first module that is a
pure CONSUMER of the pipeline output: given a `ModelWeights` (loaded
from the saved file), `make_evaluation_function` closes over it and
returns a scalar Evaluation Function `ef: Position -> float` in Y
space (the game-value space the engine uses). No database, no cache,
no pipeline: a saved model file is all the client needs — this is the
shape Roberto's endgame-solver production models (the `A2xxx` family)
plug into.
> State: D-104 · 7fb070b · 2026-09-03 · suite 5/0/0 (via
  test_lm_worker_full_chain — the EF is pinned bit-exact in the
  A2030 + A2050 tests, A2050 LONG-gated)

## API

| name | contract |
|---|---|
| `make_evaluation_function(mw: ModelWeights) -> Callable[[Position], float]` | The only export (`__all__`, L40 — M1, the bring-in had none). Closes over `mw`; the closure setup (L47-53) runs ONCE per factory call: `offsets = mw.iwmap_feature_offset`, `_, z2y = zed_fun_factory(mw.logit_clipping)` (only the z→y half — the client never transforms observations), `expanded_offsets = np.repeat(offsets[:-1], n_instances_per_feature)` (the per-INSTANCE w_dense start offsets) |

## Architecture

72 lines (post D-104).

- Imports (L28-37): numpy, `typing.Callable`, `ModelWeights` from
  model_weights (the T2 dead import of `model_weights_read_file` is
  gone — the client does not read files, it only consumes an
  already-loaded `ModelWeights`), `zed_fun_factory` from hlp_zed,
  `sigmoid` from rlm_gradient, `Position` from board (annotation
  only).
- `make_evaluation_function` (L43-72): the closure setup (L47-53),
  then `ef(p)` (L55-70), four steps per call: 1.
  `indexes = mw.feature_set.compute_indexes(np.array([p]))[0]` — the
  principal indexes, one per feature INSTANCE (length
  `feature_set.n_instances`), the same columns the training design
  matrix has (feature.py L265); 2. `w_indices =
  expanded_offsets + indexes; weights = mw.w_dense[w_indices]`; 3.
  `linear_predictor = np.sum(weights); z_pred =
  sigmoid(linear_predictor)` — the Z-space prediction; 4.
  `y_pred = z2y(np.array([z_pred], dtype=np.float32))[0]` — back to
  Y space, returned as a Python `float`.

The dense path and the substitution rule (verified):
`iwmap_feature_offset` is a BOUNDARY array of shape (F+1,) —
hlp_wmaps L212-213 builds it as `np.zeros(len(features) + 1,
dtype=np.uint32)` with `[1:] = np.cumsum(f_num_configurations)`;
`offsets[fid]` is the first w_dense slot of feature `fid`
(`offsets[F]` = K). So `offsets[:-1]` is the per-feature start and
repeating each start `n_instances_fid` times gives, for every design-
matrix column (feature instance), the w_dense slot of that instance's
configuration — which is why `expanded_offsets + indexes` indexes
`w_dense` correctly (a probe using `offsets` without `[:-1]` would
misalign every feature after the first). The gathered values are the
TRAINED weights for confirmed configurations (frequency ≥
`stat_model.frequency_cut_off`) and the SUBSTITUTION values (orbit
mean for patterns, `np.interp` for mobility — rlm_generate L167-196)
for every configuration without a dedicated weight (unseen + below-
cutoff "IC"). Consequence (D-104, verified measured): the dense path
and the literal compressed model (`ctx.w` over `ctx.design_matrix`)
agree on a training position iff every configuration it touches is
confirmed — rlm_04 (cut 10): 1923/199932 positions differ (373 EDGE
configs in `wmap_fallback`, freq < 10; max |Δy| 31.56, mean 4.98);
rlm_01 (cut 2): 5/10. The ef pins are therefore pinned against the
DENSE values (what the shipped model actually computes); the A2050/
rlm_03 pins (cut 1) equal the compressed values as well.

## Verified invariants

Pinned by the statics of `probes/verify_save.py` (A7 no dead import,
A8 the `__all__`, A9 no ws lines; the full 17-check census is in
lm_worker_save.md) + the full-chain suite — the D-104 probe's EF
tier (C10/C11/D10) moved to the suite at D-106 step 3 (frozen in the
archive).

- rlm_04 EF bit-exact on 6 pinned training positions: pos 0 →
  −37.12018585205078, pos 1 → −28.228458404541016, pos 7 →
  45.391082763671875, pos 123 → 40.502410888671875, pos 999 →
  16.26209259033203, pos 199931 → 23.326324462890625 — the exact
  float64 views of the f32 z2y outputs; `assertEqual` bit-exact
  (suite A2030).
- rlm_04 EF on `vld_positions[42]` → 11.932792663574219 (O4,
  accepted by Roberto): rlm_04 validation (bid [5]) contains EDGE
  configurations unseen in training, so this pin covers the
  substitution path end-to-end.
- rlm_03 EF bit-exact on 6 pinned training positions (suite A2050,
  LONG): pos 0 → 7.2613525390625, pos 5 → −32.98143768310547,
  pos 123 → 40.5123291015625, pos 555 → 24.14972686767578,
  pos 9999 → −19.389434814453125, pos 1999178 → 57.8465576171875.
- The ef equals the hand-computed internal dense formula
  (`z2y(sigmoid(sum(w_dense[offsets + idxs])))`) bit-for-bit on all 12
  positions (the suite asserts ef-vs-ef equality through the
  round-tripped file — the same values).

## Open issues

None.

## Conventions

- No `@validate_call` on `make_evaluation_function` (O5, accepted):
  it is a data-side factory like the rlm_analytics functions, not a
  worker factory.
- `compute_indexes(np.array([p]))` wraps the single Position in a
  length-1 array (the batched API); the `[0]` unwraps it.
- `np.repeat(offsets[:-1], ...)` is u32 arithmetic:
  `expanded_offsets` u32 + `indexes` int32 promotes to int64 — a
  safe fancy-index dtype.
- The sigmoid/z2y calls reuse the pipeline's own functions
  (hlp_zed / rlm_gradient) — the client cannot drift from the
  model's own transforms.

## Integration

- `ModelWeights` is the only input; `model_weights_read_file`
  (model_weights.md) is the producer — the test module composes the
  two.
- Y-space output: the EF returns game values directly (the z2y
  inverse), usable by the engine as a plain evaluation function.
- Per-position cost: one `compute_indexes` call (the Numba kernels) +
  one f32 gather of `n_instances` values + one sum + sigmoid + z2y.
