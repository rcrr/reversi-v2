# test/reversi/lm/test_hlp_su_analysis.py
The SU analysis LOGIC NO-DB suite (D-289): the consistency signature (the feature_set hash vs the independently
recomposed FeatureSet DOMAIN hash, D-291, the spec + the canonical pairs), the binio round-trip (with / without the
joint), the load guards (the
sidecar / the description / the version), the compute determinism (the seed pin), the theoretical configuration
space (D-278/279), the SU groups (the dedup + the canonical sort), the diagonal omission, the report + the
optional CSV, the rarity bins (the config-driven Section B, D-292), and the cache consistency. D-295: the
streaming frequency accumulators (the marginal / the joint micro-suite + the PRNG integration) moved here
from the retired test_hlp_random_play; D-296: the corpus helper + the accumulators speak the position
language (the PositionArray feeding). 4 classes / 21 tests / no database.

## Coverage

| class | tests | what it pins |
|---|---|---|
| `TestHlpSuAnalysis` | 13 | `test_signature` (the feature_set hash == the FeatureSet domain hash, independently recomposed from the child-set hashes (the INTERCEPT marker + the mset / pset hashes, D-291) + the spec fields + the pairs in the config's canonical sorted order); `test_binio_round_trip_joint` (the store -> load identity: the signature, the marginal arrays, the joint per-instance dict); `test_binio_round_trip_no_joint` (the joint None -> the presence flag -> None); `test_load_guards` (the corrupted sidecar / the wrong description / the wrong version -> RuntimeError, the manager's R2 path); `test_compute_determinism` (the same seed -> the identical marginal; a different seed -> a different one); `test_theoretical_configs` (the independent re-derivation over the fset's own attributes + the PATTERN -> n_unique_configs / the MOBILITY -> n_configurations + the INTERCEPT excluded); `test_su_groups_dedup_sort` (the (i, j) / (j, i) dedup, the canonical endpoint order, the groups in the configured order); `test_su_values_diagonal_omitted` (the same-feature diagonal (ii == jj) is omitted, the SU = 1 lock); `test_statistics_report` (the Section A + the Section B rarity (the fixture carries the thresholds) + the Section C, the header lines, the CSV OFF by default); `test_rarity_bins` (the half-open bins [0, t1), ..., [tk, inf) — the first bin the zero-frequency codes — independently recomputed, the report lines asserted verbatim, the D-293 alignment included); `test_rarity_empty_off` (the empty list -> no Section B, the SU pairs always Section C); `test_export_csv` (the export_csv flag -> the marginal + the su rows); `test_is_cache_consistent` (the same spec -> True; the seed change -> False) |
| `TestMarginalAccumulator` | 3 | (the D-295 migration; the toy corpus, a 300-game play-path corpus at ec 20, the toy FeatureSet = the intercept + the LMC + the R2) `test_lmc_hand_counted` (the single-instance dense bincount vs the INDEPENDENT oracle position_legal_moves — NOT compute_indexes); `test_pattern_cross_check` (the R2 inst0 vs an independent per-position dict via compute_indexes); `test_chunk_merge` (one chunk == two half-chunks) |
| `TestJointAccumulator` | 3 | (the D-295 migration; the same toy corpus, a 200-game play-path corpus) `test_cross_feature_joint` (the (LMC, R2) 4 instance-pairs, each joint vs the independent per-position oracle); `test_same_feature_diagonal` (the (R2, R2) 16 instance-pairs, the diagonal ZERO off-diagonal — the SU = 1 lock); `test_chunk_merge` (one chunk == two half-chunks) |
| `TestPrngIntegration` | 2 | (the D-295 migration; the play-path corpus -> the accumulator, the 2-feature toy set) `test_corpus_reproducibility` (same seed -> the SAME frequency tables bit-exact, the different seed -> different); `test_small_end_to_end_marginals` (every sub-variable sum == N, K_obs <= n_conf, the LMC marginal vs the INDEPENDENT oracle position_legal_moves) |

## Goldens pinned

- The signature: the feature_set hash (the FeatureSet DOMAIN hash — the set's unique identifier, recomposed from
  the INTERCEPT marker + the mset / pset hash hex strings, D-291) + the seed 42 / the total_positions / the
  ec 20 / the generator version "su-corpus-3" / the PRNG version "mt19937-64" + the su_pairs (the config's
  canonical sorted order).
- The rarity bins (D-292): the half-open [0, t1), [t1, t2), ..., [tk, inf) — the first bin the zero-frequency
  codes (the theoretical space minus the observed support); the fixture's thresholds [1, 2, 5, 10, 100].
- The binio layout (D-288): the header (the "SU_ANALYSIS corpus cache" description + the format version 1) + the
  signature block + the marginal + the joint (the per-instance in the sorted (ii, jj) order), the LZ4 compressed.
- The deterministic corpus: the MT19937 seed 42 stream (the two fresh same-spec computes are the identical
  marginal tables).
- The theoretical space (D-278/279): the PATTERN's n_unique_configs (the orbit representatives), the MOBILITY's
  n_configurations.
- The SU semantics: the symmetric dedup, the canonical endpoint order, the diagonal omission.
- The accumulators (the D-295 migration): the toy FeatureSet (the `_toy_fset()` = the intercept + the LMC (the
  legal-move count as the code) + the R2 (the 8-square mask, the 4 D8 instances, n_conf 6561)); the
  `_toy_blocks()` mirrors the pipeline's column layout; the `_corpus()` the small play-path corpus (the
  random_game engine, D-285 — a PositionArray, the D-296 position language); the INDEPENDENT oracles (the LMC
  via position_legal_moves, NOT compute_indexes; the R2 / the joints via the manual per-position dict over
  compute_indexes).

## Conventions

- The house test header (the "How to run" block).
- The NO-DB suite: the ctx is the REAL pipeline stopped at the FEATURES level (the D-287 idiom: the silent
  Verbosity.NONE, the base_dir override to the tmp dir, the knobs mutated on the loaded cfg) — the same pattern
  the worker-suite _make_ctx uses, minus the mock. The tiny corpus (2000 positions) keeps the suite fast (no
  LONG tier).
- The `tempfile.TemporaryDirectory` per test (the cache files + the report + the CSV land in a tmp dir, the
  tearDown cleans up).
- The migrated micro-suites reuse the toy FeatureSet / the toy blocks / the toy corpus helpers (the
  TestMarginalAccumulator static methods, shared by the joint + the integration classes) — the small, no-DB,
  hand-checkable infrastructure (the D-295 migration).

## Integration

- Consumed by `run_utests.sh` (section 4 — the pipeline, at the step 3 hlp position: right before the
  test_wrk_su_analysis worker suite).
- The hlp under test: reversi.lm.hlp_su_analysis (the 5 flow functions + the private kernels — the signature,
  the binio readers/writers, the D-295 accumulators, the SU kernels); the companion is test_wrk_su_analysis
  (the worker orchestration, the 1e7 VLONG).
