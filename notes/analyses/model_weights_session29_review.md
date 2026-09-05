<!-- ARCHIVED — D-106 step 25 (the docs/ rewrite, 2026-09-04): the MODEL_WEIGHTS + RLM_CLIENT pair (this doc + rlm_client.md) moved out of docs/src/twolm/ into the snapshot schema per docs_rules.md §1/§4. This is a frozen historical record: it is never updated. Stale-in-current-context notes: (1) this doc was written AT the D-104 campaign (session 29, post-campaign state) — its line appendix is still the current one (no source change since 7fb070b). (2) the "30-check probe" figure: post D-106 step 3 the surviving verify_save.py checks are the 17 in the SAVE worker doc — the C/D-tier live goldens (the rlm_04/rlm_03 round-trip hashes, the EF values) were moved to the test_lm_worker_full_chain pins, and only the statics (A4-A6 model_weights, A7-A9 rlm_client) + C5 + D0 remain in the probe. -->

# twolm/model_weights.py

Analysis date: 2026-09-02 — analysis session 29 (D-104, the SAVE
bring-in, Roberto's commit fe506c6); fix campaign D-104 (T2/T4 items)
approved by Roberto and applied in the same session. Brought in by
Roberto together with `lm_worker_save.py` and `rlm_client.py`.

The persistence layer of the saved RLM model: the THIRD data module in
the pipeline family (after `rlm_indexes`/`rlm_wmaps` and the
`rlm_generate` store/load pair) and the FIRST one with a plain
`@dataclass` (no pydantic BaseModel, no `@validate_call` on the data
functions — the rlm_indexes-L166 class, consistent with
`rlm_validate`/`rlm_analytics`). It serializes the INFERENCE SUBSET of
`RLMContext` into one lz4-compressed binary file (binio) so that
`rlm_client.make_evaluation_function` can evaluate board positions
without the database, the cache, or most of the pipeline state.

## Suite status (session 29, post D-104)

Covered by `test_lm_worker_full_chain`: the round-trip is pinned on
both rlm_04 (A2030) and rlm_03 (A2050, LONG), and the two read guards
are pinned by the ungated `TestModelWeightsReadGuards` class.

## Architecture (237 lines, post D-104)

- L28-41 imports: dataclass, typing (TYPE_CHECKING, Any, Dict),
  pathlib.Path, numpy, binio `BinaryWriter`/`BinaryReader`, `Feature`/
  `FeatureSet`, `Mobility`/`MobilitySet`, `Pattern`/`PatternSet`;
  `RLMContext` under TYPE_CHECKING.
- L45-47 `__all__ = ['ModelWeights', 'model_weights_read_file',
  'model_weights_write_file']`.
- L51-63 `@dataclass ModelWeights` — 10 fields in file order:
  `version: int` (the FILE header version, not a schema version),
  `name: str`, `ec: int`, `logit_clipping: float`,
  `opt_info: Dict[str, Any]`, `training_pop_stats: Dict[str, Any]`,
  `vld_metrics: Dict[str, Any]`, `feature_set: FeatureSet`,
  `iwmap_feature_offset: np.ndarray`, `w_dense: np.ndarray`.
  A plain mutable dataclass (not frozen); the instance is only ever
  produced by `model_weights_read_file`.
- L68-69 the file header constants:
  `MODEL_WEIGHTS_FILE_HEADER_STR = "RGLM_BINARY_WEIGHTS"`,
  `MODEL_WEIGHTS_FILE_HEADER_VER = 1`.
- L72-136 `model_weights_write_file(ctx, path, compressed=True)` —
  section order in the file (the numbered comments are the spec):
  1. header + `name`, `ec`, `logit_clipping` (f32);
  2. training population stats: `count` (u64) + `mean`/`std_dev`/
     `variance` (f32 each — the float64 stats are TRUNCATED by the
     format: e.g. rlm_04 mean −1.3912930396334753 → f32
     −1.3912930488586426);
  3. optimization info: 4 of the 5 context keys — `reason` (string),
     `iters` (u32), `f` (f32), `g_norm` (f32); `converged` is NOT
     persisted (derivable from `reason == 'CONVERGED_*'`);
  4. validation metrics: 4 of the 7 — `vld_samples` (u32),
     `vld_rmse_y`/`vld_mae_y`/`vld_loss` (f32 each); `vld_mse_z`,
     `vld_mae_z`, `vld_mse_y` are NOT persisted;
  5. FeatureSet: `name` (string) + `intercept` flag (u8, 1/0);
  6. MobilitySet: presence flag (u8) + `name` + `len(mobilities)` (u32)
     + per mobility `name` (string), `mask` (u64), `amask` (u64);
  7. PatternSet: presence flag (u8) + `name` + `len(patterns)` (u32) +
     per pattern `name` (string), `mask` (u64);
  8. `iwmap_feature_offset` (write_array, u32) and `w_dense`
     (write_array, f32).
- L139-237 `model_weights_read_file(path, compressed=True)`:
  - L144-151 the two GUARDS, both `ValueError` with exact messages
    (pinned by the test module):
    `File header mismatch, expected 'RGLM_BINARY_WEIGHTS', found
    '<desc>'.` and `File header version, expected '1', found '<v>'.`
  - the mirror of the write order, reconstructing `Mobility`/`Pattern`
    objects, `MobilitySet`/`PatternSet`, the intercept via
    `Feature.new_intercept()`, and the two arrays via `read_array`
    (dtype preserved: u32 / f32 — the round-trip is bit-exact, verified
    by tobytes sha3).

## Verified facts (D-104 probe — 30 checks, 0 mismatches)

- rlm_04 (K=6627): round-trip bit-exact — `feature_set.hash`
  `ec4f15374a00b729629d62ee0eb4354cbf163950672b7a9db9f81375e40559ef`
  (equal to the live context hash), `iwmap_feature_offset`
  `[0, 1, 66, 6627]` u32, `w_dense` (6627,) f32 sha3
  `7ecdeba66d9f34b9396e199dd4a5933196131db497ff88fce726bcd75f1f4f37`
  (equal to the live `ctx.w_dense` tobytes hash) — probe C7-C9.
- rlm_03 (13 features, K=167331): `feature_set.hash`
  `2c8bb32b40eff2c1e22b992e56b8d60fb51c17afb81d48f9414aef46c349e43d`,
  14 boundary entries
  `[0, 1, 66, 59115, 118164, 124725, 144408, 150969, 151050, 157611,
  157854, 158583, 160770, 167331]`, `w_dense` (167331,) f32 sha3
  `a012689f70ef8a492ce0fbf374a49e79e62f758a83fce94540a459bd28b527fc`
  (D7).
- The f32-truncated vld metrics round-trip to values whose float64
  views EQUAL the original float64 context values (the vld metrics are
  f32-representable: e.g. rlm_04 `vld_loss` 0.00575742032378912 both
  sides) — the tps stats are NOT (they are true float64 truncations,
  pinned as distinct values).
- The write is byte-deterministic: second-instance file hash equals the
  first (C14/D tier).
- Read guards B1/B2 (exact ValueError strings above).

## Minor notes (D-104 observations, report-only)

- O2: the persisted subsets are by design (inference needs): 4/5
  opt_info (`converged` dropped — derivable), 4/7 vld metrics (the z/mse
  family dropped), tps 4/4. Nothing in the client or the tests
  requires the dropped keys.
- The `int(m.mask)` / `int(m.amask)` conversions on the read side
  normalize numpy uint64 scalars to Python ints for the Mobility/
  Pattern constructors.
- No `@validate_call` on the two data functions (consistent with
  rlm_validate / rlm_analytics — O5, accepted by Roberto).
- T4 removed the 2 ws-only lines (L152/L156 of the bring-in, in the
  read function); no dead imports (all 9 module imports are used,
  `Feature` on the read side only).

## Integration notes

- Consumed only by `lm_worker_save` (write) and `rlm_client` + the
  test module (read).
- The `ModelWeights` instance is the ONLY argument of
  `make_evaluation_function` — the client API's contract type.
- File naming: `<cfg.output>` + binio's automatic
  `<name>.SHA3-256` sidecar (verified by
  `verify_sha3_256_sidecar` in the test module).

## Appendix — line reference (post D-104, 237 lines)

- L1-26 license header (canonical, untouched)
- L28-41 imports
- L45-47 `__all__`
- L51-63 `@dataclass ModelWeights` (10 fields)
- L68-69 header constants
- L72-136 `model_weights_write_file` (sections 1-8)
- L139-237 `model_weights_read_file` (guards L148-151, mirror read)
