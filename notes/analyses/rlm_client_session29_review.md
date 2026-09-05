<!-- ARCHIVED — D-106 step 25 (the docs/ rewrite, 2026-09-04): the MODEL_WEIGHTS + RLM_CLIENT pair (model_weights.md + this doc) moved out of docs/src/twolm/ into the snapshot schema per docs_rules.md §1/§4. This is a frozen historical record: it is never updated. Stale-in-current-context notes: (1) this doc was written AT the D-104 campaign (session 29, post-campaign state) — its line appendix is still the current one (no source change since 7fb070b). (2) the "30-check probe" figure: post D-106 step 3 the EF goldens (C10/C11/D10) were moved to the test_lm_worker_full_chain pins — the probe keeps the 17 statics + C5 + D0. -->

# twolm/rlm_client.py

Analysis date: 2026-09-02 — analysis session 29 (D-104, the SAVE
bring-in, Roberto's commit fe506c6); fix campaign D-104 (T2 dead import
+ T4 ws + M1 `__all__`) approved by Roberto and applied in the same
session. Brought in by Roberto as the third SAVE-family module: the
INFERENCE API that consumes the model file written by
`lm_worker_save` / `model_weights`.

The first module of the twolm package that is a pure CONSUMER of the
pipeline output: given a `ModelWeights` (loaded from the saved file),
`make_evaluation_function` closes over it and returns a scalar
Evaluation Function `ef: Position -> float` in Y space (the game-value
space the engine uses). No database, no cache, no pipeline: a saved
model file is all the client needs — this is the shape Roberto's
endgame-solver production models (the `A2xxx` family) plug into.

## Suite status (session 29, post D-104)

The EF is pinned bit-exact in `test_lm_worker_full_chain`: 6 training
positions on rlm_04 (A2030) and 6 on rlm_03 (A2050, LONG), plus one
rlm_04 VALIDATION position (`vld_positions[42]`) that exercises the
w_dense substitution path (see "The dense path and the substitution
rule" below).

## Architecture (72 lines, post D-104)

- L28-37 imports: numpy, `typing.Callable`, `ModelWeights` from
  model_weights (the T2 dead import of
  `model_weights_read_file` is removed — the client does not read
  files, it only consumes an already-loaded `ModelWeights`),
  `zed_fun_factory` from rlm_zed, `sigmoid` from rlm_gradient,
  `Position` from board (annotation only).
- L40 `__all__ = ['make_evaluation_function']` (M1 — the bring-in had
  no `__all__`; the other three new modules all have one).
- L43-72 `make_evaluation_function(mw)`:
  - L47-53 the closure setup, computed ONCE per factory call:
    `offsets = mw.iwmap_feature_offset`; `_, z2y =
    zed_fun_factory(mw.logit_clipping)` (only the z→y half is needed —
    the client never transforms observations); `expanded_offsets =
    np.repeat(offsets[:-1], n_instances_per_feature)` — the per-INSTANCE
    w_dense start offsets (below).
  - L55-70 `ef(p)`, four steps per call:
    1. `indexes = mw.feature_set.compute_indexes(np.array([p]))[0]` —
       the principal indexes for the position, one per feature
       INSTANCE (length `feature_set.n_instances`), the same columns the
       training design matrix has (feature.py L265);
    2. `w_indices = expanded_offsets + indexes`; `weights =
       mw.w_dense[w_indices]` — the per-instance dense weights;
    3. `linear_predictor = np.sum(weights)`; `z_pred =
       sigmoid(linear_predictor)` — the Z-space prediction;
    4. `y_pred = z2y(np.array([z_pred], dtype=np.float32))[0]` — back
       to Y space, returned as a Python `float`.

## The dense path and the substitution rule (verified)

`iwmap_feature_offset` is a BOUNDARY array of shape (F+1,) —
rlm_wmaps L212-213 builds it as `np.zeros(len(features) + 1,
dtype=np.uint32)` with `[1:] = np.cumsum(f_num_configurations)`.
`offsets[fid]` is the first w_dense slot of feature `fid`
(`offsets[F]` is K, the total). Therefore `offsets[:-1]` is exactly the
per-feature start, and repeating each start `n_instances_fid` times
gives, for every design-matrix column (feature instance), the w_dense
slot of that instance's configuration — which is why
`expanded_offsets + indexes` indexes `w_dense` correctly (verified
against the construction code; a probe using `offsets` without `[:-1]`
would misalign every feature after the first).

The values gathered are the TRAINED weights for confirmed
configurations (frequency ≥ `stat_model.frequency_cut_off`) and the
SUBSTITUTION values (frequency-weighted orbit mean for patterns,
`np.interp` for mobility — rlm_generate L167-196) for every
configuration without a dedicated weight: unseen ones AND the
below-cutoff ("IC") ones. Consequence (Roberto's D-104 point, verified
measured): the client's dense path and the literal compressed model
(`ctx.w` over `ctx.design_matrix`) agree on a training position iff
every configuration that position touches is confirmed. With
`frequency_cut_off = 1` (rlm_02, rlm_03) that is always true on
training data; with a higher cut it is not:

- rlm_04 (cut 10): 1923 of 199932 training positions (0.96%) differ
  between the two passes (373 EDGE configurations sit in
  `wmap_fallback` with freq < 10); max |Δy| 31.56, mean 4.98 over the
  differing ones.
- rlm_01 (cut 2): 5 of 10 training positions differ.

The ef pins in the test module are therefore pinned against the DENSE
values (what the shipped model actually computes); the A2050/rlm_03
pins happen to equal the compressed values as well (cut 1).

## Verified facts (D-104 probe — 30 checks, 0 mismatches)

- rlm_04 EF bit-exact on 6 pinned training positions: pos 0 →
  −37.12018585205078, pos 1 → −28.228458404541016, pos 7 →
  45.391082763671875, pos 123 → 40.502410888671875, pos 999 →
  16.26209259033203, pos 199931 → 23.326324462890625 (C10) — the
  exact float64 views of the f32 z2y outputs; `assertEqual` in the test
  module is bit-exact.
- rlm_04 EF on `vld_positions[42]` → 11.932792663574219 (C11, O4
  accepted by Roberto): rlm_04 validation (bid [5]) contains EDGE
  configurations unseen in training, so this pin covers the
  substitution path end-to-end.
- rlm_03 EF bit-exact on 6 pinned training positions: pos 0 →
  7.2613525390625, pos 5 → −32.98143768310547, pos 123 →
  40.5123291015625, pos 555 → 24.14972686767578, pos 9999 →
  −19.389434814453125, pos 1999178 → 57.8465576171875 (D10).
- The ef equals the hand-computed internal dense formula
  (`z2y(sigmoid(sum(w_dense[offsets + idxs])))`) bit-for-bit on all 12
  positions (probe cross-check; the test module asserts ef-vs-ef
  equality through the round-tripped file, which is the same values).

## Minor notes (D-104 observations, report-only)

- O5 (accepted): no `@validate_call` on `make_evaluation_function` —
  it is a data-side factory like the rlm_analytics functions, not a
  worker factory.
- `compute_indexes(np.array([p]))` wraps the single Position in a
  length-1 array (the batched API); the `[0]` unwraps it.
- `np.repeat(offsets[:-1], ...)` is u32 arithmetic: `expanded_offsets`
  is u32, `indexes` is int32, the sum promotes to int64 — a safe
  fancy-index dtype.
- The sigmoid/z2y calls reuse the pipeline's own functions (rlm_zed /
  rlm_gradient) — the client cannot drift from the model's own
  transforms.

## Integration notes

- `ModelWeights` is the only input; `model_weights_read_file` (in
  model_weights) is the producer. The test module composes the two.
- Y-space output: the EF returns game values directly (the z2y
  inverse), so the engine can use it as a plain evaluation function.
- Per-position cost: one `compute_indexes` call (the numba kernels) +
  one f32 gather of `n_instances` values + one sum + sigmoid + z2y.

## Appendix — line reference (post D-104, 72 lines)

- L1-26 license header (canonical, untouched)
- L28-37 imports
- L40 `__all__` (M1)
- L43-46 factory signature + docstring
- L47-53 closure setup (offsets, z2y, expanded_offsets)
- L55-70 `ef` (the 4 numbered steps)
- L72 `return ef`
