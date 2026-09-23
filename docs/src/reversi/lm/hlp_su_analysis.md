# reversi/lm/hlp_su_analysis.py
The SU analysis LOGIC (the hlp of the SU_ANALYSIS worker, D-289): the streaming frequency
accumulators (the marginal + the joint, the phase-1 data plane — the D-295 hlp_random_play
migration, the position language D-296), the corpus generator (phase 1, the expensive part —
the random_game play-path engine), the binio cache I/O (the D-288 layout), the
consistency signature, and the statistics (phase 2: the dispersion + the never-observed audit + the SU
pairs, the TXT report + the optional CSV). NO DB (the design section 3.3): the corpus is the level's own.
The worker (wrk_su_analysis.py) is the orchestration skeleton (the wrk_design_matrix minimalism).

## API
- `hlp_su_analysis_compute(ctx) -> dict` — phase 1: the corpus generator (the random_game play-path
  batches from the canonical start, the MT19937 seed, the ec arrest; the batch size min(_WAVE_SIZE,
  total - harvested)) + the streaming accumulation (the marginal + the joint for the configured pairs —
  the corpus never materializes in RAM). Returns the tables dict: the signature + the marginal + the
  joint (None when no pairs).
- `hlp_su_analysis_store_to_file(data, filename)` — the binio store (D-288): the header (the "SU_ANALYSIS
  corpus cache" description + the format version 1) + the signature block + the marginal + the joint (the
  per-instance in the sorted (ii, jj) order). The LZ4 compression (D-139), the sidecar owned by the
  cache_manager (D-072).
- `hlp_su_analysis_load_from_file(filename, checksum=True) -> dict` — the binio load: the sidecar check
  (when checksum — the worker passes False, the manager verifies at its step 2), the header
  description/version guard (the hlp_generate idiom), the ordered block reads. A foreign or truncated
  file raises RuntimeError (the manager's R2 then deletes + recomputes, D-071).
- `hlp_su_analysis_is_cache_consistent(ctx, cached) -> bool` — the cached signature vs the live one (the
  FeatureSet domain hash + the spec + the pairs), the DEBUG log.
- `hlp_su_analysis_statistics(ctx, tables) -> Path` — phase 2 (cheap, recomputed on EVERY run): the
  per-sub-variable dispersion + the never-observed audit (over the THEORETICAL configuration space,
  D-278/279), the SU pairs (2·I / (H_u + H_v), the same-feature diagonal omitted), the TXT report (the
  Section A + the optional Section B rarity — the config's rarity_thresholds, the half-open bins
  [0, t1), ..., [tk, inf), D-292 — + the Section C (the preambles after its title: the
  _SU_DESCRIPTION + the _SU_LEGEND, the D-293 follow-up), dir_name under base_dir) — the data
   rows are COLUMN-ALIGNED (D-293: the name / the inst
  LEFT-justified to the max width, the numeric values RIGHT-justified to the computed max width —
  the K_obs / never-obs / per-bin fields carry the +1 margin; the Section B preamble runs at
  column 0, no parentheses) — + the optional CSV (the export_csv flag).
- The consistency signature (the FeatureSet DOMAIN hash — the set's unique identifier over its semantic
  content, D-291 — + the spec + the pairs) is INTERNAL: the `_signature` private feeds the compute + the
  is_cache_consistent — it is NOT part of the module API (the `__all__` policy, D-290: only the
  cross-module functions are exposed; the test / the probe reach the name directly).
- The frequency accumulators are PRIVATE as well (the D-295 hlp_random_play migration, the
  D-290 policy): `_MarginalAccumulator(fset)` (the streaming marginal: per sub-variable
  the code -> count; the DENSE bincount when n_conf <= _DENSE_THRESHOLD (1e6), else the
  UNIQUE-MERGE dict; `.add(pos)` feeds a PositionArray corpus chunk, the position language
  D-296, `.result()` the observed (name, instance, n_conf, codes, counts)),
  `_JointAccumulator(fset, su_pairs)` (the per-feature blocks come from the fset's own
  feature_blocks property, D-297; per requested pair and per (instance_i,
  instance_j) the (code_i, code_j) -> count, the SPARSE packed-u64 key code_i * n_conf_j +
  code_j; the same-feature diagonal is built and OMITTED downstream — the SU = 1 lock). The
  module speaks the position language end-to-end (D-296): the corpus batch is the np.full of
  the initial_game_position scalar, the accumulators are fed the final[keep] slices, and the
  parallel (mover, opponent) arrays never cross a module boundary. The test / the probe reach
  the names directly.

## Architecture
- The corpus engine: the random_game play-path batches (the fresh lanes from the canonical start, the
  uniform pick on the injected MT19937), the harvested lanes at EXACTLY the target ec (the double-pass
  game-over lanes dropped), the accumulators fed per batch.
- The binio layout (D-288): the 4 blocks — the signature (the hash + the 5 spec fields + the pairs), the
  marginal (the (name, instance, n_conf) + the codes u32 / counts i64 arrays), the joint (the presence
  flag + the pairs, the per-instance sorted).
- The ctx idiom: the compute / statistics / consistency take the ctx (the house idiom,
  hlp_design_matrix_compute(ctx)).
- The private kernels: the signature (_signature), the 4 binio block readers/writers, the
  frequency accumulators (_MarginalAccumulator, _JointAccumulator, _DENSE_THRESHOLD), the SU
  kernels (_su_values, _su_groups, _su_canon, _theoretical_configs, _feature_instances,
  _marginal_lookup, _rarity_bins, _export_csv).

## Verified invariants
- The signature is a pure function of (feature_set, spec, pairs): pinned by test_hlp_su_analysis (the
  independent sha3_256) + the verify_su_analysis B8-B11 (the seed / pair change).
- The binio round-trip: pinned by test_hlp_su_analysis (with / without the joint) + the verify_su_analysis
  C5-C7 (the probe's OWN re-derivation, the a/b/c line).
- The SU dedup + the canonical sort + the diagonal omission: pinned by test_hlp_su_analysis + the
  verify_su_analysis B13.
- The corpus determinism (the seed pin): pinned by test_hlp_su_analysis + the worker suite (the 1e7 VLONG).
- The position-language discipline (D-296): pinned by the verify_su_analysis A10 (the no
  parallel-arrays / no rebuild structural fact) + the test / the probe PositionArray feeding.
- The accumulators: pinned by test_hlp_su_analysis (the migrated TestMarginalAccumulator /
  TestJointAccumulator / TestPrngIntegration — the LMC vs the INDEPENDENT position_legal_moves
  oracle, the R2 / the joints vs the per-position dict, the chunk-merge invariance, the
  reproducibility) + the verify_su_analysis B3-B7.

## Open issues

None.

## Conventions
- A FORMAT change bumps `_CACHE_VERSION` (the header rejects the old file) — orthogonal to the DATA
  signature (a generator change bumps `_GENERATOR_VERSION` instead, the corpus lineage).
- The per-instance joint entries are written in the SORTED (ii, jj) order (the deterministic layout).

## Integration
- Consumed by wrk_su_analysis (the 5 flow functions: compute / store / load / consistency / statistics —
  the cache_manager_load_or_compute wiring).
- Reuses: hlp_feature_analysis (the dispersion / entropy / MI / SU kernels), random_game (the
  play-path engine), binio (the cache I/O), the board (initial_game_position),
  prng (MT19937). The accumulators are LOCAL (the D-295 migration).
- The EFFECT_SIZE level consumes the published tables (the ctx.su_analysis_tables — the worker's job).
