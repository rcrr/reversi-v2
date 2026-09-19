# reversi/test/test_client.py
Unit tests for the client Evaluation Functions: 1 class / 7 tests, no DB, no gate, no artifacts — a synthetic
rlm_04-mirror `ModelWeights` built in setUp (the client never touches the pipeline state).

## Coverage

| class (line) | tests | what it pins |
|---|---|---|
| `TestClientEvaluationFunction` (plain `unittest.TestCase`; setUp builds the rlm_04-mirror weights: intercept + LMC (full board, amask 0) + EDGE (row 1), `w_dense` seeded (SEED=42) f32; `_positions` generates seeded collision-free boards) | 7 | `test_parity_bit_exact`: the array EF equals the scalar EF element-by-element (`assert_array_equal`) over 1000 seeded collision-free positions — the vectorization must not move a single f32 bit, and the output dtype/shape is (1000,) float32; `test_u64_coercion`: the raw (N, 2) uint64 form coerces to the same result as the structured form (the PositionArray BeforeValidator); `test_2d_structured_raises_value_error`: a 2-D structured PositionArray is admitted by the validator (no ndim check there) and hits the standard 1-D guard with a `ValueError` naming "1-D PositionArray"; `test_scalar_position_rejected`: a scalar `np.void` raises the Pydantic `ValidationError` (strict array — the scalar contract is `make_evaluation_function`); `test_list_rejected`: bare Python lists (int list + tuple list) raise `ValidationError`, as for the rest of the dual API; `test_empty_batch`: the N=0 edge returns an empty (0,) float32 array; `test_performance_1m` (PERF=1 gate): the house print pattern over a dense 1,000,000-board batch — warmup 10, `perf_counter`, the `[PERF make_evaluation_function_array]` print, the sanity check (the first 100 outputs bit-exact vs the scalar EF + a deterministic re-run) |

## Goldens pinned

- The rlm_04 iwmap layout `[0, 1, 66, 6627]` (intercept 1 + LMC 65 + EDGE 3^8 = 6627): the synthetic weights replicate
  the PRODUCTION rlm_04 boundary array (asserted in setUp) — the synthetic EF is therefore the same inference shape as
  the A2xxx test models.
- The bit-exact parity itself: no float literals (the scalar EF is the reference) — the pin protects the vectorization
  from any numeric drift (a changed sum order, a dtype promotion, a different gather would break it).
- No float goldens in the PERF test: it is print-only, with the bit-exact sanity check, not a performance gate.

## Conventions

- No DB / no artifacts: the `ModelWeights` is constructed directly (no `model_weights_read_file`, no chain, no cache
  file) — the module runs in the default tier from any CWD.
- The PERF test follows the house print pattern: `PERF=1` gate, 1M boards, the `[PERF ...]` print, the determinism +
  head-parity sanity checks.
- The seeded collision-free generation (the EF caller contract: mover & opponent == 0) mirrors the fuzz idiom (fixed
  seeds, the invariant pinned, no garbage left).

## Integration

- Modules under test: client.md (both factories; the guards are the array closure's own). The end-to-end TRAINED-model
  pin (the A2030 batch parity over the full 199932-position set + vld[42]) lives in test_lm_worker_full_chain.md — this
  module keeps the client covered without a live DB.
