# reversi/lm/wrk_su_analysis.py
The SU_ANALYSIS worker (the SU level, step 3) — the level ORCHESTRATION SKELETON (D-289, the wrk_design_matrix
minimalism): the enable guard (the disabled path logs and publishes None on the ctx — the ANOVA level's graceful
degradation input), the CACHED corpus (phase 1, the expensive part — the cache_manager load-or-compute flow
over the hlp callbacks, the ctx.use_cache gate; the hlp owns the binio I/O (D-288) + the consistency signature
over the FeatureSet domain hash (D-291)), the statistics (phase 2 — the hlp, cheap, recomputed on EVERY run
including the cache hit), and the ctx publication (the corpus frequency tables for the ANOVA level, the
adherence, step 6). ALL the analysis logic lives in hlp_su_analysis.py (its mirror: the corpus engine, the
binio layout, the signature, the statistics kernels).

## API

- `wrk_su_analysis() -> Worker` — the factory (@validate_call).
- `_up(ctx)`: the enable no-op (the "disabled" log, the tables cleared) → the cache_manager_load_or_compute over
  the hlp (the load with checksum=False — the manager verifies the sidecar at its step 2, no double hash) → the
  "loaded from cache / computed" log → the hlp statistics (phase 2) → the ctx.su_analysis_tables publication.
- `_down(ctx)`: clears the ctx.su_analysis_tables (the failure recovery).

## Architecture

- The skeleton (D-289): the wrk owns the LEVEL (the enable, the cache flow, the publication, the failure recovery); the hlp
  owns the LOGIC (the corpus, the binio I/O, the signature, the statistics) — the wrk_design_matrix split. The
  worker is ~100 lines: no csv, no hashlib, no numpy, no analysis kernel.
- The two-tier flow: phase 1 (the corpus) is CACHED (the expensive part — the 1e7 corpus is ~18 s cold); phase 2
  (the statistics) is RECOMPUTED on every run (the cheap part — the cache hit runs the full statistics over the
  loaded tables), so the report always reflects the current spec.
- The cache file: the rlmwf_03_SU_ANALYSIS.dat (the hlp binio, D-288: the header + the signature block + the
  marginal + the joint, the LZ4) + the .SHA3-256 sidecar (the cache_manager, the 1 MiB-chunk verify).
- The consistency signature (the hlp): the FeatureSet domain hash (the set's unique identifier, D-291) +
  the generation spec (the seed, the total_positions,
  the ec, the generator version su-corpus-5, the PRNG version mt19937-64) + the su_pairs. A pair-list change
  invalidates the corpus cache → a full regeneration. The old pickle caches self-invalidate (the D-288 R2 path).

## Verified invariants

- The level contract: the enable no-op (the tables stay None), the compute + the publish, the cache hit (the
  "loaded from cache" log), the signature invalidation (the recompute), the corpus determinism (the seed pin), the
  su_pairs joint, the optional CSV, the down (the tables cleared) — pinned by test_wrk_su_analysis (10 tests; the
  1e7 corpus scale test is VLONG, 10/0/0).
- The logic invariants (the signature, the binio I/O, the SU kernels, the report / the CSV): pinned by
  test_hlp_su_analysis (11 tests) + the verify_su_analysis probe (44 checks — the A-tier text pins cover the
  worker + the hlp, the C-tier live run).
- The failure semantics: the generation error fails the level, the machine re-raises, the _down clears the ctx
  artifacts.

## Open issues

None.

## Conventions

- The hlp functions take the ctx (the house idiom, hlp_design_matrix_compute(ctx)).
- The skeleton keeps NO analysis import (no csv / hashlib / numpy): a new analysis kernel goes to the hlp,
  never to the worker.
- The cache slot: the rlmwf_03 prefix (the level number 3) + the level name; the report / the CSV live under
  the su_analysis directory (the dir_name under base_dir).

## Integration

- The cache flow: cache_manager_load_or_compute (the hlp load / store / consistency / compute).
- The publication consumer: the ANOVA level (step 6, the adherence over ctx.su_analysis_tables).
- The report: the su_analysis directory under base_dir (the report_file_name + the optional su_analysis.csv).
