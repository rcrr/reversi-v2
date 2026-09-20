# test/reversi/lm/test_wrk_features.py
The suite of the FEATURES worker. 2 classes / 3 tests (all DB-free) / no PERF.

## Coverage

| class | what it pins |
|---|---|
| `TestLMWorkerFeatures` (2, DB-free) | `test_build_feature_set` (feature_set None before, move to 'FEATURES' = step 2 / worker "FEATURES" pinned, populated after) and `test_feature_set_content_golden` (the rlm_00.json fixture must build the EXACT expected FeatureSet — see the goldens below) |
| `TestLMWorkerFeaturesGuards` (1, DB-free — no regab DB, no model, no cache) | `test_zero_features_raises_value_error` — the fail-fast guard: the payload with `feature_set.intercept: False` (no sets) drives `_load_features` directly with a minimal SimpleNamespace context (log_event captured) → ValueError "The feature count is zero" + a Relevance.ERROR event — the zero-feature guard |

The shared setUp of the class (DB-free — the setUp moves directly to FEATURES: no gate, no POSITIONS move): stdout
patched to a StringIO + the
`TemporaryDirectory` idiom (the shared `CUSTOM_TMP_BASE` from `test.reversi.paths`, `setUpClass` mkdir, the temp dir
created FIRST so a mid-setup failure still leaves a cleanable dir) + a `LogisticModel` on the `rlm_00.json` fixture
(anchored to `WORKSPACE_ROOT`, `base_dir_override` = the tmp dir, `Verbosity.LOW`) + the pipeline preconditions pinned
(step 0 `CREATED`) + a defensive tearDown. The tests move to FEATURES (step 2) and pin the feature-set content.

## Goldens pinned

- The 3 hash literals: the FeatureSet `453e918a…5a159` (= sha3_256 over b'INTERCEPT' + the mset hash hex + the pset hash
  hex), the mset `2e553593…08a94` (the same literal test_mobility pins), the pset `04d52f12…c18` — independently
  re-derived from the public API.
- The name `'NoNameFeatureSet'` (the schema default — the fixture has no name key).
- The members: the MobilitySet 'BasicMobilitySet' with the 3 fixture entries in the sorted (mask, amask) order (ALMC
  0/FFFF…, LMC FFFF…/0, DLMC FFFF…/FFFF…); the PatternSet 'BasicPatternSet' with the 2 fixture entries in the sorted
  mask order (EDGE 0x00000000000000FF, ELLE 0x0000000000000107).
- The feature list order + per-feature counts: [INTERCEPT 1/1, ALMC 65/1, LMC 65/1, DLMC 129/1, EDGE 6561/4, ELLE 81/8]
  and `n_instances` 16.

## Conventions

- The `TemporaryDirectory` idiom + the `WORKSPACE_ROOT`/`CUSTOM_TMP_BASE` anchoring (shared `test.reversi.paths`).
- DB-free: no gate — the setUp moves to FEATURES directly (CONFIG + FEATURES only; no POSITIONS, no DB).
- The guard class stays DB-free: the guard fires before any data access, so it drives `_load_features` with a minimal
  context.

## Integration

- The class exercises the real pipeline (CONFIG → FEATURES) through `LogisticModel`; the guard class pins the fail-fast
  path in isolation.
- The 41-check probe re-derives the same FeatureSet independently (public API) and pins the level boundary (no cache
  files at all at the FEATURES stop — no rlmwf_02_FEATURES* ever materializes).
