# test/reversi/lm/test_wrk_su_analysis.py
The NO-DB suite of the SU_ANALYSIS worker: the factory (the worker name), the enable no-op (the opt-in), the compute +
the publish (the tiny SU-analysis corpus, the phase-2 statistics, the TXT report), the cache hit (the second run), the
signature invalidation (the corpus change), the corpus determinism (the random_game generator's stream on the seed), the
su_pairs joint, the optional CSV, and the down (the recovery). 2 classes / 10 tests (the 9-test mock-ctx suite + the
VLONG 1e7 scale test) / no database.

## Coverage

| class | tests | what it pins |
|---|---|---|
| `TestWrkSuAnalysis` | 9 | `test_factory` (the worker factory: the SU_ANALYSIS name); `test_enable_no_op` (the opt-in: the enable false -> the no-op, the tables stay None, the "disabled" log); `test_compute_and_publish` (the 2000-position SU-analysis corpus -> the phase-1 tables + the phase-2 statistics + the TXT report + the ctx publication, the no-su_pairs -> the joint None); `test_cache_hit` (the second run, the same signature -> the "loaded from cache" log); `test_signature_invalidation` (the corpus change (the total_positions) -> the recompute); `test_corpus_determinism` (the random_game play-path generator: the two fresh same-spec computes are the IDENTICAL marginal tables, a different seed changes them); `test_su_pairs_joint` (the requested su_pairs: the joint is computed, the (EDGE, LMC) pair, the canonical order); `test_export_csv` (the export_csv flag -> the CSV file is written); `test_down_clears` (the recovery: the down clears the tables) |
| `TestSuCorpusAtScale` | 1 (VLONG) | the 1e7-position corpus: the harvested count, the marginal totals (one count per position per sub-variable), the cache write + the HIT on a second run with the same signature |

## Goldens pinned

- The tiny corpus: the rlm_00 fixture's feature set (the LMC / the ALMC / the DLMC + the ELLE / the EDGE), the 2000-4000
  positions at ec 20, seed 42 (the "uno per tutti").
- The cache consistency: the feature_set hash + the generation spec (the seed, the total_positions, the ec, the
  generator version "su-corpus-5", the PRNG version "mt19937-64") + the su_pairs (the canonical sorted form) — the NO
  rds_checksum (the new cache lineage).
- The phase-2 recompute: the statistics run on EVERY run (the cache hit included) — the "loaded from cache" + the report
  both on the hit run.
- The opt-in: the enable false -> the no-op (the tables None, the "disabled" log).
- The recovery: the down clears the su_analysis_tables.

## Conventions

- The house test header (the "How to run" block).
- The NO-DB mock-ctx suite: the `_MockCtx` (the cfg, the feature_set, the cache path, the use_cache, the log buffer, the
  tables artifact) over the REAL pipeline's campaign: the facade runs CREATED -> CONFIG -> FEATURES on the rlm_00
  fixture (the target_level stop + the base_dir override — no parallel loader). The tiny corpus (the 2000-4000
  positions) keeps the suite fast (no LONG tier); the 1e7 scale test is VLONG.
- The `tempfile.TemporaryDirectory` per test (the cache + the report + the CSV land in a tmp dir, the tearDown cleans
  up).

## Integration

- Consumed by `run_utests.sh` (section 4 — the pipeline, at the step 3 worker position: between the
  hlp\_su\_analysis logic suite and the POSITIONS worker test).
- The worker (wrk_su_analysis) is registered at step 3 by the 19-level wiring (the 19 levels, the rlmwf_03 slot).
