# test/reversi/lm/test_multi_ply_ef.py
Unit tests for the multi-ply EF compiled leaf (D-674): 1 class / 4 tests, no DB — the
fixture model ec16 (the rebuildable LM fixture, D-671/672: `require_lm_fixture` +
`model_weights_read_file`) + 100 seeded (SEED=42) collision-free positions playout-generated
to ec16 (a random playout from the initial position to the target empty count).

## Coverage

| class | tests | what it pins |
|---|---|---|
| `TestMultiPlyEfLeaf` (plain `unittest.TestCase`; setUpClass loads the fixture ec16 model, prepares the plan, playout-generates the 100 positions) | 4 | `test_index_parity_bit_exact`: every compiled index row is bit-exact vs the client's `feature_set.compute_indexes` row (`assert_array_equal`, 100 positions) — the same njit kernels, the same prepared data; `test_leaf_value_within_measured_bound`: the leaf value is within 0.05 in Y of the client EF on all 100 positions (a drift detector, 6000× the D-674 measured margin — max 8e-6, 85/100 bit-equal); `test_leaf_value_deterministic`: two leaf calls return the same f32 bits; `test_plan_dtypes`: the plan carries the house dtypes (u32 indexes, u64 bitboards, u8 sides, f32 affine) |
