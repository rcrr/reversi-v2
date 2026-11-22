# test/reversi/lm/test_multi_ply_ef.py
Unit tests for the multi-ply evaluation function (D-674: the compiled EF leaf; D-675: the
float32 alpha-beta + the public factory): 3 classes / 18 tests, no DB — the rebuildable LM
fixtures (D-671/672: `require_lm_fixture` + `model_weights_read_file`) + seeded (SEED=42)
collision-free playout positions (the fast-tier scale: 10-20 positions per test — the
playout generation + the pure-Python oracle are the cost drivers, the compiled search is
milliseconds; the full 100-position scale sits in the LONG tier).

## Coverage

| class | tests | what it pins |
|---|---|---|
| `TestMultiPlyEfLeaf` (plain `unittest.TestCase`; setUpClass loads the fixture ec16 model, prepares the plan, playout-generates the 10 positions) | 5 | `test_index_parity_bit_exact`: every compiled index row is bit-exact vs the client's `feature_set.compute_indexes` row (`assert_array_equal`); `test_index_parity_bit_exact_full_scale` (LONG): the 100-position parity scale; `test_leaf_value_within_measured_bound`: the leaf value is within 0.05 in Y of the client EF (a drift detector, 6000× the D-674 measured margin — max 8e-6, 85/100 bit-equal); `test_leaf_value_deterministic`: two leaf calls return the same f32 bits; `test_plan_dtypes`: the plan carries the house dtypes (u32 indexes, u64 bitboards, u8 sides, f32 affine) |
| `TestMultiPlyEfSearch` (setUpClass: 20 playout positions at ec20 + the fixture models ec20/19/18) | 11 | `test_depth0_anchor_bit_exact`: the A == B batch equals the client EF bit-exactly (the delegation anchor, 20 positions); `test_depth1_vs_minimax_oracle`: 20 positions vs the INDEPENDENT full-width minimax oracle (pure Python, no pruning, its own move enumeration, the compiled leaf at the horizon) — `assert_allclose` 1e-3; `test_depth2_vs_minimax_oracle`: 5 positions at two plies; `test_depth12_full_scale_oracle` (LONG): the 100-position oracle scale at depths 1 and 2; `test_depth34_structural`: 10 positions each at depths 3-4 — float32, the batch shape, the D-670 range |v| ≤ R, determinism; `test_depth34_full_scale_structural` (LONG): the 100-position structural scale; `test_output_range_and_determinism`: the structural contract at depths 1-2; `test_below_horizon_raises`: A < B → `ValueError`; `test_scalar_position_rejected` / `test_bare_list_rejected`: the strict array contract → Pydantic `ValidationError`; `test_empty_batch`: the empty float32 array |
| `TestMultiPlyEfDiscipline` (a trivial INTERCEPT-ONLY synthetic ModelWeights, B = 27; the scanned playout pass constant at ec28) | 2 | `test_normal_root_is_minus_y0`: a normal depth-1 root is −y0 (all children the constant leaf); `test_pass_root_is_plus_y0`: a pass root is +y0 (the negamax sign flip through the pass) — both pinned against the scipy-expit reference y0 (delta 1e-4) |
