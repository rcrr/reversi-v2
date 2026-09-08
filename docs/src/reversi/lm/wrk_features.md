# reversi/lm/wrk_features.py
The FEATURES worker of the RLM pipeline — the 4th active level
(CREATED → CONFIG → POSITIONS → FEATURES), enabled line-by-line
by Roberto in f051dd3. Unlike POSITIONS this is a PURE-COMPUTE
level: it builds a FeatureSet from the CONFIG-loaded cfg (no DB,
no cache_manager, no cache file — the flat rlmwf_03_FEATURES*
files never materialize) and exposes it as `ctx.feature_set`.
> State: D-082 · 1a9f045 · 2026-08-31 · suite 3/0/0 (2 DB-gated)

## API

| name | contract |
|---|---|
| `wrk_features()` | the factory — `@validate_call(config=ConfigDict(arbitrary_types_allowed=True))` returning `Worker("FEATURES", _up, _down)` |

(The loaders `_load_features` / `_load_intercept` /
`_load_patterns` / `_load_mobility` are private helpers; the
zero-feature guard test drives `_load_features` directly.)

## Architecture

- `_up`: INFO "Loading board features as defined by the model..."
  → `ctx.feature_set = _load_features(ctx)`.
- `_down`: INFO "Clearing features..." → `ctx.feature_set = None`.
- `_load_features`: (1) the three loaders; (2)
  `FeatureSet(ctx.cfg.feature_set.name, intercept, mset, pset)` —
  the name from the schema's `FeatureSetConfig.name` (default
  `'NoNameFeatureSet'` — the fixture has no name key); (3) the
  zero-feature guard: `len(feature_set.features) == 0` → ERROR log
  + ValueError ("The feature count is zero. It is not possible to
  generate a model without features."); (4) the INFO summary
  (name, hash, has Intercept / has MobilitySet / has PatternSet +
  the children's name/hash) and the DEBUG per-feature table
  (`{i:03d} [category] name n_instances n_configurations`).
- `_load_intercept`: truthy `cfg.feature_set.intercept` (a plain
  bool, `Optional[bool] = False`) → `Feature.new_intercept()`
  (INTERCEPT, 1/1), else None.
- `_load_patterns`: truthy `cfg.feature_set.pattern_set` →
  `Pattern(elt.name, elt.mask)` per element (the schema's
  field_validator already converted the 16-hex no-0x strings to
  Bitboard) → `PatternSet(name, patterns)`; DEBUG lines per
  pattern (name, 16-hex mask); else None.
- `_load_mobility`: truthy `cfg.feature_set.mobility_set` →
  `Mobility(elt.name, elt.mask, elt.amask)` per element →
  `MobilitySet(name, mobilities)`; DEBUG lines per mobility (name,
  mask, amask — D-082 R1: the amask is now printed correctly);
  else None. The `if cfg_x:` truthiness gates: the intercept is a
  genuine truthiness check, the two sets are pydantic models —
  present or None.

## Verified invariants

Pinned by the 40-check `probes/verify_wrk_features.py` +
the 3-test `test_wrk_features.py`.

- Source shape: the 125-line file, `__all__ =
  ['wrk_features']`, the factory name "FEATURES", the
  RLMContext import under TYPE_CHECKING (circular guard), the
  worker does NOT import cache_manager, the `@validate_call`
  factory (D-082 M1), the amask log (D-082 R1), the orphan
  comment gone (D-082 M3), no non-comment trailing whitespace —
  probe A1-A9.
- The loaded state: step 3 / "FEATURES" after the move; the
  feature_set populated; the 'NoNameFeatureSet' default name; the
  intercept; the MobilitySet 'BasicMobilitySet' with the 3 fixture
  members in sorted (mask, amask) order; the PatternSet
  'BasicPatternSet' with the 2 fixture members in sorted mask
  order; the feature order (intercept, mobilities, patterns);
  n_features 6 / n_instances 16; the per-feature counts (LMC
  65/1, ALMC 65/1, DLMC 129/1, ELLE 81/8, EDGE 6561/4); the 3
  mobility DEBUG lines with the TRUE amasks — probe B2-B8c.
- The independent re-derivation: the mset/pset hashes match a
  public-API build from the fixture values; the fs hash =
  sha3_256(b'INTERCEPT' + mset.hash + pset.hash); the independent
  FeatureSet is identical (feature list + hash) — probe B9a-d.
- The level boundary: only the CONFIG + POSITIONS flat cache
  files exist (no rlmwf_03_FEATURES* — the pure-compute level
  writes nothing) — probe B10; down to CONFIG clears
  feature_set — probe B12; a second run on the same base dir:
  the POSITIONS cache hit, no DB extraction, the identical
  feature set — probe B13a-c.
- The test-file pins: the 206-line file, 2 classes / 3 tests,
  the D-065 idiom (shared CUSTOM_TMP_BASE), the SKIP_REGAB_DB
  gate, the load-bearing Path import, the header grammar, the
  as-is M1 comment, the whitespace, the golden test's 3 hash
  literals + the feature-order/counts pin — probe C1-C10.
- The suite: `TestLMWorkerFeatures` (2, DB-gated — setUp moves
  through POSITIONS, which hits the DB on a fresh base dir):
  `test_build_feature_set` (None before, move to 'FEATURES' =
  step 3, populated after) and `test_feature_set_content_golden`
  (the full content pin); `TestLMWorkerFeaturesGuards` (1, DB-free
  — the D-106 step-3 conversion of probe B11): the zero-feature
  payload (intercept off, no sets) driven through
  `_load_features` with a SimpleNamespace ctx → ValueError
  "The feature count is zero" + a Relevance.ERROR event.

## Open issues

None.

## Conventions

- The pure-compute level: no cache file, no cache_manager, no DB
  of its own — the flat rlmwf_03_FEATURES* naming never
  materializes; the D-082 R1 fix: the mobility DEBUG log prints
  the true amask (probe B8a-c).
- Test artifacts: the D-065 idiom + the D-085 WORKSPACE_ROOT /
  CUSTOM_TMP_BASE anchoring; the DB tests sit behind the
  `SKIP_REGAB_DB` gate.

## Integration

- The 4th RLM level; the facade (`logistic_model.py`) instantiates
  the machine + `Worker` (the line-by-line enablement f051dd3).
- Consumes the `feature` module (Feature/FeatureSet) and the
  CONFIG-loaded `ctx.cfg.feature_set`; publishes
  `ctx.feature_set` for the INDEXES level onward.
