# reversi/lm/hlp_gate.py
The campaign config loader (the pipeline's own loader): loads the campaign JSON5 + the FeatureSet (the wrk_features pure
mapping) + the per-feature column blocks (the documented column layout). The worker tests (test_wrk_feature_analysis,
test_wrk_effect_size) use it to build the campaign (the feature set + the column blocks) for the accumulator / the
effect-size tests.

## API
- `load_campaign(config_path) -> (cfg, fset, blocks)` — loads the campaign config (json5, the pipeline's own loader) +
  the FeatureSet (the wrk_features pure mapping) + the per-feature column blocks (the documented column layout: the
  intercept, then the mobilities in the (mask, amask) sorted order, then the patterns in the mask sorted order — the
  fset.features order). Returns (cfg, fset, blocks) — blocks: the list of (name, col_start, col_end, n_conf, n_inst)
  over the non-intercept features (the sub-variables).

## Architecture

- A single pure function: `load_campaign` reads the JSON5 file, validates it through the pydantic `LMConfig`, and
  rebuilds the `FeatureSet` with the same factories the pipeline uses (`Feature.new_intercept()`, `Mobility` /
  `MobilitySet`, `Pattern` / `PatternSet`) — the loader is the pipeline's own path, never a parallel re-implementation.
- The column walk: `col` starts at 1 when the intercept is present (it owns column 0) and every non-intercept feature
  takes `n_instances` consecutive columns, in `fset.features` order — the FeatureSet's SORTED storage order (the
  mobilities in the (mask, amask) order, then the patterns in the mask order), not the config file's order.
- The block tuple `(name, col_start, col_end, n_conf, n_inst)` is the whole contract: the consumer builds its synthetic
  tables from it.
- No DB, no cache, no state; the heavy imports are function-local (the worker tests import this module and must stay
  DB-free and fast).

## Verified invariants

- The blocks tile the non-intercept columns with no gap and no overlap, and `col_end - col_start == n_inst` for every
  feature: pinned by the worker tests that build their synthetic index matrix from the blocks
  (`test_wrk_effect_size::_make_ctx` fills `indexes[:, c0 + i]` for every instance) — a wrong layout misaligns the
  tables and the effect-size goldens fail.
- The intercept is EXCLUDED from the blocks (one column, no configuration space) while `col` still counts it: pinned by
  the same construction over the `rlm_00` fixture, where the intercept is present (the first block starts at column 1).

## Open issues

None.

## Conventions

- The loader mirrors the pipeline's construction path (`json5` + `LMConfig(**raw)` + the FeatureSet factories): a change
  in the config schema or in the feature construction lands here in the same commit.
- The function-local imports are deliberate: the test modules import this file and must not pull the pipeline in.

## Integration
- `load_campaign` reuses the pipeline's own loader path (json5 + `LMConfig(**raw)`, the `wrk_features` pure mapping) —
  no DB.
- Consumer: the worker tests (test_wrk_feature_analysis, test_wrk_effect_size) — they build the campaign (the feature
  set + the column blocks) for the accumulator / the effect-size tests.
