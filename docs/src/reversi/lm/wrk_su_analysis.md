# reversi/lm/wrk_su_analysis.py
The SU_ANALYSIS worker (the SU level, step 3): the SU-analysis corpus generator (the PRNG seed + the ec arrest + the
wave tier) + the statistics. Phase 1 (the corpus) is CACHED — the FIRST cache level whose consistency signature carries
the feature_set hash INSTEAD of the rds_checksum (the corpus is INDEPENDENT of the DB). Phase 2 (the statistics) is
cheap and recomputed on EVERY run, including the cache hit. The level publishes the corpus frequency tables on the ctx
(the cross-level blackboard) for the EFFECT_SIZE level (the adherence, step 6). The worker semantics: the generation
error fails the level, the machine re-raises, the _down clears the ctx artifacts.

## API
- `wrk_su_analysis() -> Worker` — the factory: the `Worker("SU_ANALYSIS", _up, _down)` (the house worker pattern).
- `_up(ctx)`: (1) the enable check — `su_analysis.enable` false makes the level a no-op (opt-in), the tables stay None;
  (2) phase 1 — the cache flow (the `cache_manager_load_or_compute`, the rlmwf_03 slot, the feature_set hash + spec +
  pairs signature, NO rds_checksum); (3) phase 2 — the statistics (the per-sub-variable dispersion + the never-observed
  audit + the requested SU pairs); (4) the outputs — the console (INFO per sub-variable + the top SU pairs) + the TXT
  report (dir_name under base_dir, the PlotConfig pattern) + the optional CSV (the export_csv flag); (5) the ctx
  publication — the `ctx.su_analysis_tables` (the marginal + the joint, for the EFFECT_SIZE level).
- `_down(ctx)`: clears the `ctx.su_analysis_tables` (recovery).

## Architecture
- **The cache flow** — the `rlmwf_03_SU_ANALYSIS.dat` file (the pickle of the tables dict) + the .SHA3-256 sidecar (the
  8192-chunk verify). The consistency signature (`_signature`): the feature_set hash (the sha3_256 of the feature_set
  config's normalized dump, the first 16 hex) + the generation spec (the seed, the total_positions, the ec, the
  generator version `su-corpus-2` — an older version string marks a corpus built on the swapped start, never reusable —,
  the PRNG version `mt19937-64`) + the su_pairs list (the canonical sorted form). A pair-list change invalidates the
  corpus cache → a full regeneration; the two-tier cache (the marginals keyed on (features, spec) + the joints keyed on
  (+ pairs)) is the parked v2 refinement.
- **The compute path (phase 1)** — the SU-analysis corpus generator (the `run_wave`, the wave size
  `min(1e6, total_positions)`: the wave is the PARALLELISM, and the lanes beyond the corpus are pure overhead — the
  1e6-lane arrays (~48 MB) and the per-step glue cost ~3.4 s for a 10k-position harvest that a 10k-lane wave does in
  ~0.04 s; the production corpora (1e7) keep 1e6 lanes, bit-identical) + the streaming accumulation (the
  `MarginalAccumulator` + the `JointAccumulator` for the requested pairs). The blocks come from `_feature_blocks(fset)`
  (the fset.features order, the documented column layout: the intercept, then the mobilities, then the patterns).
- **The statistics (phase 2)** — the per-sub-variable `dispersion` (the K_obs / H / H_norm / coverage) + the
  `never_observed_audit` (the n_conf - K_obs + the rarity profile); the requested SU pairs: for each (name_i, name_j)
  pair and each (inst_i, inst_j), the `symmetric_uncertainty(2·I / (H_i + H_j))` from the joint + the two marginals. The
  same-feature DIAGONAL (inst_i == inst_j) is OMITTED (the SU = 1 lock — not a measurement; the off-diagonal is the
  anisotropy measure).
- **The ctx field** — the `LMContext.su_analysis_tables` (the cross-level blackboard, the pre-declared field) carries
  the tables dict (the marginal + the joint) for the EFFECT_SIZE level (the adherence, step 6).

## Verified invariants
- Pinned by `test_wrk_su_analysis.py` (8 tests, the NO-DB mock-ctx suite, the rlm_00 fixture's feature set, the tiny
  SU-analysis corpus): the factory (the SU_ANALYSIS name); the enable no-op (opt-in — the tables stay None, the
  "disabled" log); the compute + the publish (the 2000-position corpus -> the tables + the TXT report + the ctx
  publication, the no-su_pairs -> the joint None); the cache hit (the second run, the "loaded from cache" log); the
  signature invalidation (the corpus change -> the recompute); the su_pairs joint (the (EDGE, LMC) pair, the canonical
  order); the optional CSV (the export_csv flag -> the CSV file); the down (recovery — the tables cleared).
- Pinned by the 43-check `probes/verify_su_analysis.py` (the campaign level): the module structure + the no-DB
  discipline; the independent re-derivations (the marginal vs the FeatureSet's own batch bincount, the joint vs a
  pure-python Counter, the SU values vs the RATIO-FORM mutual information, the signature vs an independently recomputed
  feature_set hash); the live rlm_00 run (the step-3 stop, the cache + its sidecar, the report lines vs pure-python
  math, the phase-2 recompute on the cache hit, the down, the opt-in absence of both artifacts); the rename
  completeness over src/docs/probes/tools.

## Open issues
- The SU / the entropy / the MI math: `hlp_feature_analysis` is a shared-kernels module (also the ANOVA + the adherence
  of the EFFECT_SIZE level), so the two levels' math evolves together.
- The two-tier cache (the v2 refinement, parked): the marginals keyed on (features, spec) + the joints keyed on (+
  pairs) so a pair experiment reuses the marginal corpus.

## Conventions
- The house worker pattern: the `wrk_X() -> Worker` factory + the `_up`/`_down`.
- The SU-analysis corpus is IN-MEMORY only (never a file) — the BufferSink holds it in RAM, the accumulator processes
  the flattened (mover, opp) arrays.
- The SU / the entropy / the MI / the dispersion / the audit are the hlp_feature_analysis kernels — the
  from-frequency-tables math.

## Integration
- Consumes the `ctx.cfg` (the su_analysis config) + the `ctx.feature_set` (the FEATURES level, step 2) ONLY (no DB, no
  positions — the design section 3.3).
- The consumer: the EFFECT_SIZE worker reads the `ctx.su_analysis_tables` for the adherence (the c metric of the
  design section 3.5), with the graceful degradation when the level is disabled (the tables None).
- The wiring registers the worker at step 3 (the rlmwf_03 slot) + the EFFECT_SIZE at step 6; the VLONG scale test
  (`test_wrk_su_analysis::TestSuCorpusAtScale`, D-256) runs the corpus at the ODP-1 size.
