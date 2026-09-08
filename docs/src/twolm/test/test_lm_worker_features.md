# twolm/test/test_lm_worker_features.py
The suite of the FEATURES worker (Roberto's file, copied from the
original repo with the f051dd3 line-by-line enablement; the
D-082 T1-T4 + M2 campaign re-anchored it, and D-106 step 3 moved
the B11 probe guard into it). 2 classes / 3 tests (2 DB-gated +
1 DB-free guard) / no PERF.
> State: D-106 · b05adfd · 2026-09-04 · suite 3/0/0 (2 DB-gated)

## Coverage

| class | what it pins |
|---|---|
| `TestLMWorkerFeatures` (2, `SKIP_REGAB_DB` gated) | `test_build_feature_set` (feature_set None before, move to 'FEATURES' = step 3 / worker "FEATURES" pinned, populated after) and `test_feature_set_content_golden` (the rlm_00.json fixture must build the EXACT expected FeatureSet — see the goldens below) |
| `TestLMWorkerFeaturesGuards` (1, DB-free — no regab DB, no model, no cache) | `test_zero_features_raises_value_error` — the fail-fast guard: the payload with `feature_set.intercept: False` (no sets) drives `_load_features` directly with a minimal SimpleNamespace context (log_event captured) → ValueError "The feature count is zero" + a Relevance.ERROR event. D-106 step 3: converted from the verify_lm_worker_features.py B11 probe |

The shared setUp of the DB-gated class: the db_long_gate FIRST
(the SKIP_REGAB_DB + LONG tier gates, D-130; the setUp moves
through POSITIONS, which hits the DB on a
fresh base dir) + stdout patched to a StringIO + the D-065
`TemporaryDirectory` idiom (the shared `CUSTOM_TMP_BASE` from
`reversi.test.paths`, `setUpClass` mkdir, the temp dir created FIRST
so a mid-setup failure still leaves a cleanable dir) + a
`LogisticModel` on the `rlm_00.json` fixture (anchored to
`WORKSPACE_ROOT`, `base_dir_override` = the tmp dir,
`Verbosity.LOW`) + the pipeline preconditions pinned (step 0
`CREATED`, the move to POSITIONS = step 2 / `POSITIONS`) + a
defensive tearDown. The setUp keeps the "as FEATURES depends on
the configuration loaded there" comment as-is per Roberto's call
(M1 / I-012: evaluating moving the FEATURES level before
POSITIONS — it also pins the step numbering).

## Goldens pinned

- The 3 hash literals: the FeatureSet `453e918a…5a159` (=
  sha3_256 over b'INTERCEPT' + the mset hash hex + the pset hash
  hex), the mset `2e553593…08a94` (the same literal test_mobility
  pins), the pset `04d52f12…c18` — independently re-derived from
  the public API (session 22, D-082).
- The name `'NoNameFeatureSet'` (the schema default — the fixture
  has no name key).
- The members: the MobilitySet 'BasicMobilitySet' with the 3
  fixture entries in the sorted (mask, amask) order (ALMC
  0/FFFF…, LMC FFFF…/0, DLMC FFFF…/FFFF…); the PatternSet
  'BasicPatternSet' with the 2 fixture entries in the sorted mask
  order (EDGE 0x00000000000000FF, ELLE 0x0000000000000107).
- The feature list order + per-feature counts: [INTERCEPT 1/1,
  ALMC 65/1, LMC 65/1, DLMC 129/1, EDGE 6561/4, ELLE 81/8] and
  `n_instances` 16.

## Conventions

- The D-065 idiom + the D-085 `WORKSPACE_ROOT`/`CUSTOM_TMP_BASE`
  anchoring (shared `reversi.test.paths`).
- The `SKIP_REGAB_DB` gate at the top of setUp (the test_regab
  pattern) — the setUp moves to POSITIONS, which needs the live
  regab DB.
- The guard class stays DB-free: the guard fires before any data
  access, so it drives `_load_features` with a minimal context.

## Integration

- The DB-gated class exercises the real pipeline (CONFIG →
  POSITIONS → FEATURES) through `LogisticModel`; the guard class
  pins the fail-fast path in isolation.
- The 40-check probe re-derives the same FeatureSet independently
  (public API) and pins the level boundary (no rlmwf_03_FEATURES*
  file ever materializes).
