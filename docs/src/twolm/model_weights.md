# twolm/model_weights.py
The persistence layer of the saved RLM model: the third data module in
the pipeline family (after hlp_indexes/rlm_wmaps and the rlm_generate
store/load pair) and the first with a plain `@dataclass` (no pydantic
BaseModel, no `@validate_call` on the data functions — consistent with
rlm_validate/rlm_analytics). It serializes the INFERENCE SUBSET of
`RLMContext` into one lz4-compressed binary file (binio) so that
`rlm_client.make_evaluation_function` can evaluate board positions
without the database, the cache, or most of the pipeline state.
> State: D-104 · 7fb070b · 2026-09-03 · suite 5/0/0 (via
  test_lm_worker_full_chain — 2 ungated read guards; the rest DB-
  gated, A2050 additionally LONG-gated)

## API

| name | contract |
|---|---|
| `ModelWeights` | Plain mutable `@dataclass` (L51-63), 10 fields in file order: `version` (the FILE header version, not a schema version), `name`, `ec`, `logit_clipping`, `opt_info` (Dict), `training_pop_stats` (Dict), `vld_metrics` (Dict), `feature_set: FeatureSet`, `iwmap_feature_offset` (np.ndarray), `w_dense` (np.ndarray); the instance is only ever produced by `model_weights_read_file` |
| `model_weights_write_file(ctx, path, compressed=True)` | Serialize the inference subset, section order 1-8 (below); the file header constants (L68-69): `"RGLM_BINARY_WEIGHTS"` / version 1 |
| `model_weights_read_file(path, compressed=True) -> ModelWeights` | Mirror of the write order; the two GUARDS first (L144-151) — `ValueError` with the exact messages pinned by the test module: `File header mismatch, expected 'RGLM_BINARY_WEIGHTS', found '<desc>'.` and `File header version, expected '1', found '<v>'.` |

## Architecture

237 lines (post D-104).

- Imports (L28-41): dataclass, typing (TYPE_CHECKING, Any, Dict),
  pathlib.Path, numpy, binio `BinaryWriter`/`BinaryReader`,
  `Feature`/`FeatureSet`, `Mobility`/`MobilitySet`, `Pattern`/
  `PatternSet`; `RLMContext` under TYPE_CHECKING. `__all__` (L45-47) =
  [ModelWeights, model_weights_read_file, model_weights_write_file].
- `model_weights_write_file` (L72-136) — section order (the numbered
  comments are the spec): 1. header + `name` + `ec` +
  `logit_clipping` (f32); 2. training population stats — `count`
  (u64) + `mean`/`std_dev`/`variance` (f32 each — the float64 stats
  are TRUNCATED by the format); 3. optimization info — 4 of the 5
  context keys: `reason` (string), `iters` (u32), `f` (f32),
  `g_norm` (f32); `converged` is NOT persisted (derivable from
  `reason == 'CONVERGED_*'`); 4. validation metrics — 4 of the 7:
  `vld_samples` (u32), `vld_rmse_y`/`vld_mae_y`/`vld_loss` (f32);
  `vld_mse_z`/`vld_mae_z`/`vld_mse_y` are NOT persisted; 5.
  FeatureSet — `name` + `intercept` flag (u8); 6. MobilitySet —
  presence flag (u8) + `name` + count (u32) + per mobility
  `name`/`mask` (u64)/`amask` (u64); 7. PatternSet — presence flag
  (u8) + `name` + count (u32) + per pattern `name`/`mask` (u64); 8.
  `iwmap_feature_offset` (write_array u32) + `w_dense` (write_array
  f32).
- `model_weights_read_file` (L139-237): the guards (L144-151), then
  the mirror read — reconstructing `Mobility`/`Pattern` objects
  (the `int(m.mask)` / `int(m.amask)` conversions normalize numpy
  uint64 scalars to Python ints), `MobilitySet`/`PatternSet`, the
  intercept via `Feature.new_intercept()`, the two arrays via
  `read_array` (dtype preserved: u32 / f32 — the round-trip is
  bit-exact, verified by tobytes sha3).

## Verified invariants

Pinned by the statics of `probes/verify_save.py` (A4 no-ws, A5 the
header str/ver + the 3-`__all__`, A6 the 10 fields; the full 17-
check census is in lm_worker_save.md) + the full-chain suite. The
D-104 probe's live tier (the C/D round-trip goldens, deleted at
D-106 step 3 → the test pins) froze in the archive.

- rlm_04 (K=6627) round-trip bit-exact: `feature_set.hash`
  `ec4f15374a00b729629d62ee0eb4354cbf163950672b7a9db9f81375e40559ef`
  (== the live context hash), `iwmap_feature_offset`
  `[0, 1, 66, 6627]` u32, `w_dense` (6627,) f32 sha3
  `7ecdeba66d9f34b9396e199dd4a5933196131db497ff88fce726bcd75f1f4f37`
  (== the live `ctx.w_dense` tobytes hash) — suite A2030.
- rlm_03 (13 features, K=167331): `feature_set.hash`
  `2c8bb32b40eff2c1e22b992e56b8d60fb51c17afb81d48f9414aef46c349e43d`,
  the 14-entry boundary
  `[0, 1, 66, 59115, 118164, 124725, 144408, 150969, 151050, 157611,
  157854, 158583, 160770, 167331]`, `w_dense` (167331,) f32 sha3
  `a012689f70ef8a492ce0fbf374a49e79e62f758a83fce94540a459bd28b527fc`
  — suite A2050 (LONG).
- The f32-truncated vld metrics round-trip to values whose float64
  views EQUAL the original context values (they are f32-
  representable); the tps stats are NOT (true float64 truncations —
  rlm_04 mean −1.3912930396334753 → f32 −1.3912930488586426, pinned
  as DISTINCT values).
- The write is byte-deterministic: the 2nd-instance file hash equals
  the first (suite test_second_instance_deterministic — 6 'Cache
  successfully loaded' hits, 7 cache files).
- The 2 read guards (suite TestModelWeightsReadGuards, ungated): the
  exact `ValueError` strings, raised before any other read.

## Open issues

None.

## Conventions

- The persisted subsets are by design (inference needs): 4/5
  opt_info, 4/7 vld metrics, tps 4/4 — nothing in the client or the
  tests requires the dropped keys (O2, report-only).
- No `@validate_call` on the two data functions (consistent with
  rlm_validate / rlm_analytics — O5, accepted by Roberto).
- The f32 truncation of the float64 tps stats is a FORMAT property,
  not a bug: the file is the inference artifact, f32 throughout the
  weight-bearing parts.

## Integration

- Consumed only by `lm_worker_save` (write) and `rlm_client` + the
  test module (read).
- The `ModelWeights` instance is the ONLY argument of
  `make_evaluation_function` — the client API's contract type.
- File naming: `<cfg.output>` + binio's automatic
  `<name>.SHA3-256` sidecar (verified by
  `verify_sha3_256_sidecar` in the test module).
