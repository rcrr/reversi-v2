# reversi/lm/model_weights.py
The persistence layer of the saved LM model: the third data module in the pipeline family (after hlp_indexes/hlp_wmaps
and the hlp_generate store/load pair) and the first with a plain `@dataclass` (no pydantic BaseModel, no
`@validate_call` on the data functions — consistent with hlp_validate/hlp_analytics). It serializes the INFERENCE SUBSET
of `LMContext` into one lz4-compressed binary file (binio) so that `client.make_evaluation_function` can evaluate board
positions without the database, the cache, or most of the pipeline state.

## API

| name | contract |
|---|---|
| `ModelWeights` | Plain mutable `@dataclass` (L53-72), 12 fields: the 10 in file order (`version` — the FILE header version, not a schema version —, `name`, `ec`, `logit_clipping`, `opt_info` (Dict), `training_pop_stats` (Dict), `vld_metrics` (Dict), `feature_set: FeatureSet`, `iwmap_feature_offset` (np.ndarray), `w_dense` (np.ndarray)) + the `config_dump: str \| None = None` / `config_checksum: str \| None = None` pair (defaulted, trailing — the dataclass requires defaulted fields last — although the FILE section LEADS the body); both are None for v1 files; the instance is only ever produced by `model_weights_read_file` |
| `model_weights_write_file(ctx, path, compressed=True)` | Serialize the inference subset, section order 0-9 (below); the file header constants (L77-78): `"RGLM_BINARY_WEIGHTS"` / version 2 |
| `model_weights_read_file(path, compressed=True) -> ModelWeights` | Mirror of the write order; the two GUARDS first (L169-172) — `ValueError` with the exact messages pinned by the test module: `File header mismatch, expected 'RGLM_BINARY_WEIGHTS', found '<desc>'.` and `File header version, expected '1' or '2', found '<v>'.` — then, v2 only (L175-189): the config provenance read + the corruption sentinel `Config section checksum mismatch, expected '<stored>', recomputed '<sha3_256 of the dump>'.` (the stored checksum must cover the embedded dump) |

## Architecture

276 lines.

- Imports (L28-41): `hashlib` (the sentinel recompute), dataclass, typing (TYPE_CHECKING, Any, Dict), pathlib.Path,
  numpy, binio `BinaryWriter`/`BinaryReader`, `Feature`/`FeatureSet`, `Mobility`/`MobilitySet`, `Pattern`/ `PatternSet`;
  `LMContext` under TYPE_CHECKING. `__all__` (L46-48) = [ModelWeights, model_weights_read_file,
  model_weights_write_file].
- `model_weights_write_file` (L81-157) — section order (the numbered comments are the spec): 0. header
  (`"RGLM_BINARY_WEIGHTS"`, version 2); 1. **configuration provenance (LEADS the body)**: `ctx.config_checksum` (the
  CONFIG-level fingerprint, the sentinel first) + `ctx.cfg.model_dump_json(indent=4)` (the normalized dump — the
  effective config, the base_dir override included; the model file is the single source); 2. metadata — `name` + `ec` +
  `logit_clipping` (f32); 3. training population stats — `count` (u64) + `mean`/`std_dev`/`variance` (f32 each — the
  float64 stats are TRUNCATED by the format); 4. optimization info — 4 of the 5 context keys: `reason` (string), `iters`
  (u32), `f` (f32), `g_norm` (f32); `converged` is NOT persisted (derivable from `reason == 'CONVERGED_*'`); 5.
  validation metrics — 4 of the 7: `vld_samples` (u32), `vld_rmse_y`/`vld_mae_y`/`vld_loss` (f32);
  `vld_mse_z`/`vld_mae_z`/`vld_mse_y` are NOT persisted; 6. FeatureSet — `name` + `intercept` flag (u8); 7. MobilitySet
  — presence flag (u8) + `name` + count (u32) + per mobility `name`/`mask` (u64)/`amask` (u64); 8. PatternSet — presence
  flag (u8) + `name` + count (u32) + per pattern `name`/`mask` (u64); 9. `iwmap_feature_offset` (write_array u32) +
  `w_dense` (write_array f32).
- `model_weights_read_file` (L160-276): the guards (L169-172 — version `not in (1, 2)` raises, the v1 files stay
  readable, the backward-compat the v2 spec required), then the v2-only config provenance read + sentinel (L175-189),
  then the mirror read — reconstructing `Mobility`/`Pattern` objects (the `int(m.mask)` / `int(m.amask)` conversions
  normalize numpy uint64 scalars to Python ints), `MobilitySet`/`PatternSet`, the intercept via
  `Feature.new_intercept()`, the two arrays via `read_array` (dtype preserved: u32 / f32 — the round-trip is bit-exact,
  verified by tobytes sha3), and the dataclass with `config_dump`/`config_checksum` (None on v1).

## Verified invariants

Pinned by the statics of `probes/verify_save.py` (A4 no-ws, A5 the header str/ver 2 + the 3-`__all__`, A6 the 12 fields,
A6b the config section LEADS the body + the `version not in (1, 2)` guard + the corruption sentinel; the full 18-check
census is in wrk_save.md) + the full-chain suite.

- rlm_04 (K=6627) round-trip bit-exact: `feature_set.hash`
  `ec4f15374a00b729629d62ee0eb4354cbf163950672b7a9db9f81375e40559ef` (== the live context hash), `iwmap_feature_offset`
  `[0, 1, 66, 6627]` u32, `w_dense` (6627,) f32 sha3 `7ecdeba66d9f34b9396e199dd4a5933196131db497ff88fce726bcd75f1f4f37`
  (== the live `ctx.w_dense` tobytes hash) — suite A2030.
- rlm_03 (13 features, K=167331): `feature_set.hash` `2c8bb32b40eff2c1e22b992e56b8d60fb51c17afb81d48f9414aef46c349e43d`,
  the 14-entry boundary
  `[0, 1, 66, 59115, 118164, 124725, 144408, 150969, 151050, 157611, 157854, 158583, 160770, 167331]`, `w_dense`
  (167331,) f32 sha3 `a012689f70ef8a492ce0fbf374a49e79e62f758a83fce94540a459bd28b527fc` — suite A2050 (VLONG).
- The f32-truncated vld metrics round-trip to values whose float64 views EQUAL the original context values (they are
  f32-representable); the tps stats are NOT (true float64 truncations — rlm_04 mean −1.3912930396334753 → f32
  −1.3912930488586426, pinned as DISTINCT values).
- The write is byte-deterministic WITHIN a base dir: the 2nd-instance file hash equals the first (suite
  test_second_instance_deterministic — 6 'Cache successfully loaded' hits, 7 cache files). The file-level sha3 LITERAL
  goldens (v1: 21603 B / bcf8d918… A2030, 515042 B / 3ad18058… A2050) are RETIRED — the embedded dump carries the run's
  base_dir, so the bytes are legitimately run-specific across base dirs (v1 was byte-stable across runs precisely
  BECAUSE it carried no run data). The size literal becomes a BAND (22700-22800 B A2030, 516400-516500 B A2050): the raw
  v2 content is 100% deterministic apart from the 8 random base_dir chars, and those shift LZ4's match structure by a
  few bytes (measured: the same raw A2050 content compresses to 516459 or 516455 depending on the name); the
  same-base-dir byte identity + the read-back provenance pins carry the determinism guarantee.
- The v2 micro tier (suite TestModelWeightsV2, ungated, no DB): the hand-crafted v1 file loads with `config_dump` /
  `config_checksum` None (backward compat); the synthetic-ctx v2 round-trip (every field + the embedded dump + the
  fingerprint); the v2 corruption sentinel (stored checksum ≠ sha3_256(dump) → `ValueError`).
- The 2 read guards (suite TestModelWeightsReadGuards, ungated): the exact `ValueError` strings, raised before any other
  read — the version guard now reads `expected '1' or '2'`.

## Open issues

None.

## Conventions

- The persisted subsets are by design (inference needs): 4/5 opt_info, 4/7 vld metrics, tps 4/4 — nothing in the client
  or the tests requires the dropped keys (O2, report-only).
- No `@validate_call` on the two data functions (consistent with hlp_validate / hlp_analytics — O5).
- The f32 truncation of the float64 tps stats is a FORMAT property, not a bug: the file is the inference artifact, f32
  throughout the weight-bearing parts.

## Integration

- Consumed only by `wrk_save` (write) and `client` + the test module (read).
- The `ModelWeights` instance is the ONLY argument of `make_evaluation_function` — the client API's contract type.
- File naming: `<cfg.output>` + binio's automatic `<name>.SHA3-256` sidecar (verified by `verify_sha3_256_sidecar` in
  the test module).
