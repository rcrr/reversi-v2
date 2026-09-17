# reversi/lm/hlp_gate.py
The campaign config loader (the pipeline's own loader):
loads the campaign JSON5 + the FeatureSet (the wrk_features
pure mapping) + the per-feature column blocks (the
documented column layout). The worker tests
(test_wrk_feature_analysis, test_wrk_effect_size) use it to
build the campaign (the feature set + the column blocks) for
the accumulator / the effect-size tests.

## API
- `load_campaign(config_path) -> (cfg, fset, blocks)` —
  loads the campaign config (json5, the pipeline's own
  loader) + the FeatureSet (the wrk_features pure mapping)
  + the per-feature column blocks (the documented column
  layout: the intercept, then the mobilities in the (mask,
  amask) sorted order, then the patterns in the mask sorted
  order — the fset.features order). Returns (cfg, fset,
  blocks) — blocks: the list of (name, col_start, col_end,
  n_conf, n_inst) over the non-intercept features (the
  sub-variables).

## Integration
- `load_campaign` reuses the pipeline's own loader path
  (json5 + `LMConfig(**raw)`, the `wrk_features` pure
  mapping) — no DB.
- Consumer: the worker tests (test_wrk_feature_analysis,
  test_wrk_effect_size) — they build the campaign (the
  feature set + the column blocks) for the accumulator /
  the effect-size tests.
