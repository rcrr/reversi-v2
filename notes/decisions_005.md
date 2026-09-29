# Decisions log — volume 005 (closed)

Format: D-NNN | date | decision | rationale

Volume 005: D-301…D-332 (2026-09-23 → 2026-09-29); closed at the D-333 rotation (the open log had 4460 lines > the
amended 1000 cap); the open log continues in notes/decisions.md.

D-301 | 2026-09-23 | the never-observed audit's RARITY profile is REMOVED (Roberto, the deep cleanup — option (ii) over
         the make-it-required (i)): the audit
         `_never_observed_audit(counts, n_configurations, rarity_thresholds=(1, 2, 5, 10, 100))` carried a HARDCODED
         default that was a phantom second source of truth — the config's rarity_thresholds defaults to None (the rarity
         section OFF), yet the function's default was (1, 2, 5, 10, 100), and the two were unconnected. ANALYSIS: the
         rarity sub-dict was DEAD in production — the report's config-driven 'Section B: Rarity report' (D-292) is built
         by the SEPARATE _rarity_bins kernel fed with cfg_fa.rarity_thresholds or []; the 2 src audit call sites
         (_export_csv + the statistics) consume ONLY never_observed (n_configurations - K_obs, threshold-independent);
         the rarity dict was consumed only by the test micro-suite. (1) The kernel is now _never_observed_audit(counts,
         n_configurations) -> {'k_obs', 'never_observed'} — the rarity_thresholds argument and the rarity sub-dict are
         GONE (the default is removed at the root, not made required). (2) The 2 src call sites are UNCHANGED (they
         never passed thresholds, they read only never_observed). (3) The 3 test rows drop the rarity goldens (the class
         docstring + the hand-computed / empty rows keep the k_obs / never_observed checks). The config-driven Section B
         rarity is UNTOUCHED (still _rarity_bins + the config thresholds, D-292). EQUIVALENCE: never_observed is
         threshold-independent and the tables (compute phase) are untouched, so the 1e7 tables stay bit-identical + the
         statistics report + CSV byte-identical (the rlmwf_03 caches stay valid). VERIFICATION: the full suite (fast
         tier) 947/0/97 GREEN, test_hlp_su_analysis 37/0/0, the worker suite VLONG 10/0/0 (the 1e7 corpus), the
         verify_su_analysis probe 45 / 0, the verify_effect_size probe 29 / 0, the docs audit 92 mirrors with the 6
         pre-existing findings only.

D-302 | 2026-09-23 | the INCOMPLETE signatures are COMPLETED (Roberto: many methods of hlp_su_analysis were missing the
         argument types — the (b) option over the minimal (a): concrete types + the private TypeAliases, over the (c)
         TypedDict, skipped): the module had 31 def, 29 incomplete — 46 missing parameter annotations + 4 missing return
         annotations (the accumulators' 2 result(), _read_joint, _su_values). (1) IMPORTS: FeatureSet (reversi.feature —
         no cycle, wrk_features / model_weights already import it), IndexArray (reversi.pattern), BinaryReader /
         BinaryWriter (reversi.tools.binio), numpy.typing (the client.py idiom). (2) THE 4 PRIVATE ALIASES for the
         recurring structured shapes: _MarginalTable (the result() / binio / statistics marginal — the per-sub-variable
         (name, inst, n_conf, codes u32, counts i64)), _JointTable (the per-pair (ni, nj, {(ii, jj): (codes_i, codes_j,
         counts)})), _SuSummary (the (ni, ii, nj, jj, su) list), _SuGroups (the (gk, entries) list) —
         underscore-private, the __all__ policy (D-290) intact. (3) THE 46 + 4 ANNOTATED: fset the FeatureSet, idx the
         IndexArray (the EXACT fset.compute_indexes return — the D-300 index matrix becomes readable in the signature),
         w / r the binio classes, filename str | Path (the hlp_generate idiom), ctx the "LMContext", data / tables /
         cached / sig / lookup dict, counts / joint_counts np.ndarray, n_configurations int, thresholds list[int], H_u /
         H_v / I float, su_pairs list[tuple[str, str]] (the schema's List[Tuple[str, str]]), the _su_canon str / int
         pairs, the _write_joint / _read_joint _JointTable | None (the binio presence flag). (4) INERT AT RUNTIME: the
         from __future__ import annotations is already in head — every annotation is a lazy string; NO @validate_call on
         the 31 functions (only the worker factory, untouched) — zero behaviour change: the tables / report / CSV
         untouched, the rlmwf_03 caches stay valid. VERIFICATION: the full suite (fast tier) 947/0/97 GREEN, the
         verify_su_analysis probe 45 / 0, the verify_effect_size probe 29 / 0, the docs audit 92 mirrors with the 6
         pre-existing findings only (the mirror net-zero at the 120 ceiling: the 2 line-merges + the 2-line Conventions
         bullet, the .add(idx: IndexArray) weave).

D-303 | 2026-09-23 | the Pydantic boundary: the store / the load are @validate_call-ed (the SuTables DEEP validation)
         (Roberto: the 5 __all__ flow functions are called ONCE by the pipeline — can they carry the Pydantic
         signatures? 'un approccio rigoroso' — the (B) option, the full rigor, with SuTables PUBLIC in __all__): the
         house precedent already decided this exact question for the package (hlp_design_matrix / hlp_generate /
         hlp_indexes / hlp_wmaps / hlp_zed: the store / load ARE decorated, the ctx functions are NOT — the documented
         comment 'Here validation is not possible, it brings in a convoluted issue with circular imports'). ANALYSIS:
         (1) the circular chain is REAL — the logistic_model facade imports wrk_su_analysis (line 45) BEFORE the
         LMContext class is defined, so a runtime import of LMContext in hlp_su_analysis would fail at import time;
         EXPERIMENT: a @validate_call signature with a TYPE_CHECKING-only forward reference FAILS at decoration time
         (NameError, pydantic 2.13.4). (2) The 2 I/O functions ARE decorated: hlp_su_analysis_store_to_file(data:
         SuTables, filename: str | Path) + hlp_su_analysis_load_from_file (filename: str | Path, checksum: bool = True),
         the house ConfigDict(arbitrary_types_allowed=True). (3) The 3 ctx functions (compute / is_cache_consistent /
         statistics) stay UNDECORATED with the house precedent comment (the hlp_design_matrix idiom, the D-303 pointer).
         (4) THE SuTables PUBLIC TypedDict (the D-302 option (c), resurrected — the deferred precision now has a
         purpose): signature dict + marginal _MarginalTable + joint _JointTable | None. The store DEEP-validates it: the
         structure + the array dtypes (uint32 / int64) — MEASURED on the 1e7-shaped tables (28 cells, ~465k keys/cell):
         ~19 us (the shallow dict would be 2 us) — invisible against the binio write / read (seconds); the array leaves
         are passed through (no copy, verified), the containers are rebuilt (the store is read-only, no behaviour
         change). Lax-mode caveat: a wrong array DTYPE is converted (int64 -> uint32), a structurally malformed table
         (the 4-tuple marginal entry, a missing key) is REJECTED with a ValidationError — pinned by the new test. (5)
         The cache_manager synergy: a raising load_fn / validate_fn falls into the R2 path (the delete +
         recompute, D-071) — the validation joins the recovery flow for free. VERIFICATION: the full suite (fast tier)
         948/0/97 GREEN (+1: test_store_deep_validation — the real compute output passes, the 4-tuple marginal + the
         missing key are rejected), the worker suite VLONG 10/0/0 (the 1e7 corpus 18.5 s cold, the baseline 18.7 s — the
         decorator costs zero on the real path), the verify_su_analysis probe 45 / 0, the verify_effect_size probe 29 /
         0, the docs audit 92 mirrors with the 6 pre-existing findings only (the mirror net-zero at the 120 ceiling: the
         2 line-merges + the 3-line Conventions bullet + the 3 inline weaves).

D-304 | 2026-09-23 | SU_ANALYSIS throughput: the 2e6-lane wave + the threaded joint merge + the diagonal skip The COLD
         profiling campaign (the scratch/bench_su instrumented replica + the public wall runs, the rlm_test_su_00 1e7 /
         28-cell fixture) measured the SU_ANALYSIS level: gen ~56% (the 8-thread numba prange, the serial MT19937 batch
         inside), the joint ~37% (the single-thread np.unique fold), the idx ~7%, the marg ~1%. THE WAVE SIZE: 36.3 s at
         1e6, 32.7 s at 2e6 (-10%), 31.2 s at 4e6 (-14%, the diminishing returns + the ~280 MB extra peak RAM) - 2e6 is
         the sweet spot. THREE changes: (1) THE 2e6-LANE WAVE, with the _GENERATOR_VERSION bump "su-corpus-3" ->
         "su-corpus-4": the measured finding that drove it - the wave size is a generator BEHAVIOUR. The per-step draw
         batch size depends on the wave's lane count, so a different wave size shifts the whole MT19937 stream: the
         corpora are NOT identical across wave sizes (100% of the positions differ, lane 0 included - verified on a 5k
         toy corpus), and the cache signature does NOT carry the wave size, so without the bump the old lineage would
         have been silently reused; the bump fires the designed D-071 R2 delete + recompute on the next 1e7 run. (2) THE
         THREAD-JOINT: the per-cell merges (the D-299 vectorized fold, the _joint_cell_merge) are INDEPENDENT (each
         touches only its own registry entry) - the add feeds them to a ThreadPoolExecutor (min(cells, cpu_count)
         workers, the numpy sort releases the GIL); the single-cell case stays inline. Deterministic: a cell's result is
         a pure function of its own (K, C) history + the wave's column pair (the scratch smoke test: the 2-wave threaded
         accumulation == the independent per-position oracle, bit-identical across runs). (3) THE DIAGONAL SKIP: the
         same-feature (ii, ii) cells are NOT BUILT - the (u, u) joint IS the marginal of u (pure redundancy: 6 of the
         fixture's 28 cells); _su_values already omitted them (the SU = 1 lock), the report / the CSV / the EFFECT_SIZE
         level never consume them (it reads the marginal only); an old cache carrying them still reads fine (the
         defensive _su_values check stays). RESULT (measured, the 28-cell fixture, the public wall runs): 36.3 s (1e6,
         pre) -> 32.7 s (2e6 only) -> 20.4 s (2e6 + thread + skip) = -44%; the joint phase ~15.8 s -> ~3.6-4.6 s (the
         instrumented runs, the machine load swings); the 4-cell VLONG worker: 18.1 s cold (the 18.5 s baseline - the
         4-cell joint is small, the win shows on the multi-cell fixtures). Peak RAM at 2e6: ~2.2 GB (the +~0.9 GB is the
         8 concurrent cell temporary buffers, the machine has 103 GB free). test_same_feature_diagonal now pins the 12
         off-diagonal cells vs the independent per-position oracle + the (0,0)/(3,3) absence; the probe + the test
         worker + the 4 mirrors updated to su-corpus-4 / 2e6; the src mirror net-zero at the 120 ceiling. THE PARKED
         NEXT STEP (the C, Roberto's + the profiling's convergence): the gen/accumulation OVERLAP (the double-buffer
         producer/consumer: the 8-core wave generation in flight while the 1-core accumulation folds the previous wave -
         it hides the ~3 s of serial work under the ~3.5 s of parallel gen, the expected cold compute ~17-18 s; the
         complexity: the threading + the 2x wave RAM + the determinism argument, parked for a dedicated campaign).

D-305 | 2026-09-23 | the 3e6-lane wave ("su-corpus-5") + the double-buffer overlap (option C) measured NULL on the
         8-core box, REVERTED TWO decisions out of the C campaign. (1) THE 3e6-LANE WAVE: the interleaved A/B (the
         28-cell 1e7 fixture, the 5 pairs, the medians) - 2e6: 20.70 s, 3e6: 19.08 s (the 5/5 pair wins, the tight 3e6
         distribution 18.92-19.92 vs the 2e6 20.27-21.19 + one 30.72 load spike) - so _WAVE_SIZE 2e6 -> 3e6 + the
         _GENERATOR_VERSION "su-corpus-4" -> "su-corpus-5" (the wave size is a generator BEHAVIOUR, the D-304 rule: the
         lineage invalidates, the D-071 R2 delete + recompute on the next 1e7 run). 4e6 stays rejected (the diminishing
         returns + the extra ~280 MB peak RAM). (2) THE DOUBLE-BUFFER OVERLAP (the option C) IS REVERTED: implemented
         (the _corpus_producer thread + the maxsize-1 handoff queue, the producer owns the PRNG - the single-threaded
         stream discipline, the corpus bit-identical to the serial loop: verified A/B against the D-304 pickle, the
         suite 948/0/97, the probes 0 mismatch, the VLONG 18.1 s) but MEASURED NULL on the 8-core box: 20.89 s
         (serial) -> 20.99 s (overlapped), the noise level. The STRUCTURAL reason: the serial schedule already SATURATES
         the 8 cores (the gen 8-thread numba prange, the idx 8-thread numba prange in pattern.py, the 8-thread joint
         pool, the 1-thread marginal) - the ~10% idle window (the per-step glue + the marg) cannot hold the overlap work
         (the idx + the joint = 16 threads): it contends the numba workqueue workers with the gen prange windows, the
         gen stretches by what the idle fills, the core-seconds are conserved -> zero by construction. The overlap would
         pay on a 16+ core machine (the gen 8 + the idx 8 + the joint 8 coexist) - not this one. The design is RECORDED
         here (the producer owns the PRNG, the backpressure, the exception propagation) for a future re-implementation
         if the box grows. The house rules applied: the measured null result is a decision, the complexity is removed
         (the YAGNI, the house minimalism). The final state: the D-304 serial compute + the 3e6-lane wave + the
         "su-corpus-5" lineage - the 28-cell cold compute 36.3 s -> ~19.1 s since the campaign start (-47%).

D-306 | 2026-09-23 | the de-history docstrings: the WHAT contract only (no D-XXX, no change history) Roberto's
         directive: the hlp_su_analysis docstrings (the module header, the constant comments, the 5 flow functions, the
         accumulators, the binio blocks, the SU kernels) carried the change history (the D-XXX provenance, the "the old
         code..." clauses, the version lineage, the benchmark numbers) — the rules.md house style (the docstrings
         explain WHAT, the observable contract; never HOW; no D-XXX provenance in the docstrings) + his spec: what it
         does, the arguments, the outputs, the state mutation, the preconditions. The rewrite (method by method, ~34
         docstrings / comments): the module header (the D-289 / D-295 / D-304 / D-298 / D-288 clauses gone), the __all__
         policy comment (the stale _feature_set_hash reference dropped), the _WAVE_SIZE comment (the 14-line benchmark
         history -> 7 lines) + the _GENERATOR_VERSION (the 17-line lineage -> 5 lines) + the _CACHE_\* / the
         _SU_DESCRIPTION / the _SU_LEGEND / the _KPI_LEGEND pointers, the 3 `#:` validation comments (the
         circular-import reason, the D-303 pointer dropped), the SuTables, the marginal + the joint accumulators (class
         / __init__ / add / result, the Args / State sections), the _joint_cell_merge (the Args / the State), the
         _signature (the INSTEAD-OF history gone), the store / the load (the Args / Returns / Raises), the statistics
         kernels (the D-301 rationale paragraph gone from _never_observed_audit; the D-299 memoization clause from
         _mutual_information; the D-278 pointers from _theoretical_configs), the _su_values / the _rarity_bins / the
         _export_csv / the statistics (the Returns / the State sections added). The HOW clauses moved to the code
         comments (the rule's home); the design pointers to source comments stay (the D-296 position language, the D-293
         column alignment — the non-obvious choices, the rules.md allowance). TWO factual fixes found in the pass: the
         _su_groups docstring said the report's "Section B" (the SU groups are the Section C — corrected); the
         _su_groups code comment claimed the "SU descending" sort (the sort is the canonical endpoint order only —
         corrected). Runtime-inert (the docstrings): the fast suite 948/0/97 + the probes 0 mismatch confirm the
         structure; the mirror docs untouched (the D-pointers are the mirror's job, the docs_rules §3.2).

D-307 | 2026-09-24 | the ANALYTICS report: the PROBABILITY / SU_PROBABILITY columns + the "SU Sample Consistency"
         verdict line Roberto's request: in the per-feature tables of the model_analytics_report.txt — (a) the
         configuration FREQUENCY as a % (the PROBABILITY), (b) the FREQUENCY % as observed in the SU_ANALYSIS corpus,
         (c) below the Eta-Squared line an OBJECTIVE measure (his: "chi_2 ???") saying whether the training sample is a
         consistent population vs the SU-observed one. Rules: SU_ANALYSIS skipped -> neither the columns nor the line;
         SU corpus too small -> a header note (the threshold: Roberto's call). THE DESIGN: (1) THE COLUMNS — both are
         (position, instance) OBSERVATION shares (Roberto's confirmation: the instances are summed, exactly what the
         logistic model does): PROBABILITY = the row frequency / the table's total frequency; SU_PROBABILITY = the
         pooled corpus count of the configuration / the corpus observation total — the marginal of
         ctx.su_analysis_tables SUMMED over the feature's instance columns (the marginal is per sub-variable, the table
         row is per feature configuration: the pooling is the only mapping that keeps the two columns directly
         comparable). Inserted after FREQUENCY; the separator widens only when present (the pattern table 135 -> 146);
         SU disabled -> the table is BYTE-IDENTICAL to the pre-D-307 layout (the rlm_01 / rlm_02 report goldens survived
         untouched). (2) THE CONSISTENCY LINE — the pooled adherence (the hlp_feature_analysis kernel, the single
         source, the D-298 split) of the pooled training distribution (the hlp_indexes over the feature's columns) vs
         the pooled corpus distribution: the line shows the TV (the robust "how different" number) + the chi-square (the
         statistic, the p, the merged-tail count) + the VERDICT over the TV bands: TV <= 0.01 CONSISTENT, TV <= 0.05
         MARGINAL, above DEVIATING. WHY TV CARRIES THE VERDICT AND NOT THE CHI-SQUARE P: with k up to 6561 categories
         and N in the hundreds of thousands the chi-square p is HYPER-SENSITIVE (any 0.1% deviation drives p to 0 —
         statistically correct, pragmatically always "inconsistent"); the TV is bounded 0..1, no log, no 0/0. The
         chi-square stays in the line as the reference (and the inf case is INFORMATION: the DB observes a code the
         corpus never shows — the kernel's disjoint-support rule). The two TV bands are UNCALIBRATED by design — the
         first production run (A2050, the 1e7 corpus vs the real DB) shows where reality sits; they are module
         constants, tunable without a format change. (3) THE TOO-SMALL RULE (Roberto's choice, supplanting the proposed
         absolute 1e5 floor): the corpus total_positions < 2x the training size -> no columns + the header line "N/A (SU
         corpus too small: N < 2x training M)". Rationale: the corpus must hold at least twice the training to be a
         meaningful reference distribution for it (a corpus smaller than the sample it is being compared against cannot
         serve as the "ideal"). (4) THE DEPENDENCY CHOICE: ANALYTICS computes the statistics ITSELF from
         ctx.su_analysis_tables + the indexes (one bincount + one adherence() call per feature — negligible) instead of
         reusing the EFFECT_SIZE output: EFFECT_SIZE is OPTIONAL (default FALSE) and the columns are tied to
         SU_ANALYSIS, not to EFFECT_SIZE; the granularity differs (the pooled per-feature vs the per-sub-variable
         adherence); the kernel is shared, so the math is the single source. VERIFICATION: the NO-DB mock-ctx suite (6
         tests over the real rlm_00 campaign stopped at FEATURES, the D-287 idiom, the synthetic 2-code concentrated
         100-position data — the hand-computed goldens: the TV 0.0 / 0.03 / 0.5 trio, the chi2 0.0 / 0.3613 / inf, the
         p 1.0 / 5.48e-01 / 0.0, the verdict counts, the too-small note, the PROBABILITY column summing to 100% within
         the 3-decimal rounding band); the DB-gated end-to-end on rlm_00 (the REAL 10,000-position corpus vs the 200
         training positions: the 5 consistency lines re-derived in the test from the ctx and asserted in the report —
         the live LMC line "TV 0.0827 chi2 14.5 (p 1.53e-01, merged 11) -> DEVIATING", the EDGE line "TV 0.5226 chi2 inf
         (p 0.00e+00, merged 2347) -> DEVIATING": the 200-position training deviates from the random-play baseline, as
         expected — the verdict measures the training's polarization toward real play, not a model defect); the fast
         suite 955/0 + the LONG=1 suite 955/0 (24 skipped); verify_analytics 0 mismatch (the A10 def count pin 7 -> 10,
         the 3 new private helpers); the rlm_01 / rlm_02 date-masked report goldens UNCHANGED (the SU-off byte-identity,
         the design property).

D-308 | 2026-09-24 | the ANALYTICS report: the INTERCEPT section (the single trained bias weight) Roberto's request: the
         model_analytics_report.txt never prints the INTERCEPT value. If present, a section for it, before the MOBILITY
         FEATURES DETAILS. Detailed analysis to evaluate together; then his decisions: (1) the compact key-value block
         (option A), (2) a SINGLE Weight line only — the Dense Weight / Status / Frequency / AVERAGE_GV are pleonastic,
         (3) 4 decimals, (4) the plain title "INTERCEPT" (not "INTERCEPT DETAILS"). Analysis: the intercept is a
         category-0 feature (fset.intercept, Feature | None) skipped by the MOBILITY (category 1) / PATTERN (category 2)
         table loops, so its trained weight appeared nowhere in the report (it was counted in the header's Total
         Parameters (W) / Dense Parameters (K) but never shown). The value is ctx.w[iwmap[iwmap_feature_offset[fid]]]
         (the single trained bias). A separate dense line is redundant (it matches the compressed weight except where
         f32 quantization bites — already the header's Substitution Delta); Status is always C and Frequency = the total
         sample count (the header's train_samples); the AVERAGE_GV is the global y-mean (the header's population
         baseline). Hence the single-line call. The SU columns are degenerate for the intercept (one configuration,
         always 100%) and are omitted. The section is emitted only when fset.intercept is not None (the existing
         feature.py API — no new surface), placed between the FEATURE SET SUMMARY and the MOBILITY details.
         VERIFICATION: 2 new NO-DB branch tests (the mock rlm_00 ctx — the "INTERCEPT:" section before the MOBILITY
         details + the single Weight line re-derived from the ctx; and fset.intercept set to None — no section) + the
         rlm_00 end-to-end INTERCEPT pin + the rlm_02 no-intercept pin. The affected report goldens (date + config hex
         masked): rlm_01 15c71c7e... -> 384d8327... (rlm_01 HAS an intercept); the full-chain A2030 rlm_04
         a9642167... -> c3522d10... (rlm_04 HAS an intercept); the full-chain A2050 rlm_03 (the VLONG-gated ~90-s
         production run) 695c151b... -> 8b2ed520... (rlm_03 HAS an intercept). rlm_02 (no intercept) UNCHANGED at
         3b4a5beb... (byte-identical, the design property) and the verify_analytics probe (rlm_02-based) UNCHANGED. The
         fast suite 957/0 + the LONG=1 suite 957/0 (24 skipped, A2050 VLONG-gated); verify_analytics 0 mismatch (the A10
         def count pin 10 -> 11, the new _format_intercept_section helper).

D-309 | 2026-09-24 | the EFFECT_SIZE level is RENAMED ANOVA (the worker, the config, the files) Roberto's request:
         evaluate renaming the EFFECT_SIZE pipeline step (6) to ANOVA. Analysis: the level's primary (always-run)
         computation is literally the one-way ANOVA effect sizes — the kernel is already anova_eta_omega, the report
         already prints "ANOVA ..." lines — so ANOVA is more specific and truthful than the generic EFFECT_SIZE. Two
         caveats accepted: (a) the level also computes the adherence (the chi-square + KL + TV distribution comparison),
         which is NOT ANOVA — it becomes the "unnamed" secondary part of the ANOVA step (acceptable, it is the
         graceful-degradation, opt-in diagnostic); (b) strictly the level computes the effect sizes (eta²/omega²), not
         the F-statistic/p-value — "ANOVA" in common usage covers this. Scope: the worker (wrk_effect_size.py ->
         wrk_anova.py, Worker("EFFECT_SIZE") -> Worker("ANOVA")), the config (EffectSizeConfig -> AnovaConfig, the field
         effect_size -> anova, the dir / report defaults), the test (test_wrk_effect_size.py -> test_wrk_anova.py), the
         probe (verify_effect_size.py -> verify_anova.py), the 2 mirror docs, + the ~150 identifier references across
         src / test / docs / probes / run_utests.sh. The historical notes (decisions / journal / the I-017 plan) are
         left as-is. The BREAKING change: the config key effect_size -> anova. Pydantic IGNORES the old key (verified: a
         config with effect_size: {enable: true} loads fine but cfg.anova.enable stays False) — so a pre-rename config
         SILENTLY disables the level. No repo fixture sets the key (all opt-in FALSE), so the repo is unaffected; any
         external / production config using effect_size: must be updated to anova: (RESOLVED: the backward-compat alias
         was REJECTED — the clean break, no alias; Roberto's decision: "Nessun ALIAS — cose semplici ed univoche").
         VERIFICATION: the fast suite 957/0 + the LONG=1 suite 957/0 (24 skipped); the 5 touched / related probes
         (anova, su_analysis, save, logistic_model, analytics) all 0 mismatch. Two rename-induced fixes: (1)
         test_wrk_anova's per-sub-variable count now keys on "eta2" (the "ANOVA report written" log line also says ANOVA
         now — the level name); (2) the verify_anova D tier (the live A2050 build area) now force-enables cfg.anova (the
         build area's config predates the key rename — it still says effect_size). docs audit clean for the 2 renamed
         mirrors; notes_format 0.

D-310 | 2026-09-25 | the ANOVA worker: the cfg_es -> cfg_anova local rename + the _up split (version B) Roberto's
         request, after reading _up: (1) the cfg_es local renamed cfg_anova — a D-309 leftover (the pre-rename file
         already named it cfg_es; the D-309 sed touched only the attribute access, ctx.cfg.effect_size ->
         ctx.cfg.anova); 8 occurrences, all in wrk_anova.py, no pin anywhere (tests / probes / docs); (2) extract ALL
         the logic out of _up, leaving it extremely simple like the other workers. Analysis: the ANOVA worker was the
         only worker whose _up carried the whole computation inline (55 lines); its siblings are thin orchestrators
         (8-35 lines) delegating to named helpers. Two variants proposed — A (a single _run) / B (the granular split,
         the wrk_positions precedent); Roberto chose B. Implementation: the two computation helpers
         (_compute_anova_lines — the eta²/omega² per sub-variable; _compute_adherence_lines — the adherence trio, the
         graceful-degradation None branch) + the existing _write_report, all private, taking ctx (the house style); _up
         is now the 8-line guard + delegate (the enable no-op stays in _up, the house pattern). Zero behavioral change:
         the log sequence is identical; the probe A5 pins survive VERBATIM ("tables = ctx.su_analysis_tables",
         "Adherence SKIPPED", "tables is not None" — the branch is kept as `if tables is not None:` with the SKIPPED
         tail); the tests + the probe import only _up / _down / wrk_anova (unchanged). VERIFICATION: the 7/7 anova
         suite; the fast suite 957/0 + the LONG=1 suite 957/0; verify_anova 0 mismatch (A5, the C and the D tiers);
         verify_analytics 0 mismatch (the canary); the mirror doc updated (the API section now lists the private
         helpers); docs audit clean.

D-311 | 2026-09-25 | the ANALYTICS eta² unification + the cross-level agreement test Roberto's question after the D-310
         review: is the eta² ALSO computed in the ANALYTICS module — two computations by different programs, but
         analogous? Analysis: in fact 3 code paths: the shared anova_eta_omega kernel (hlp_feature_analysis, the ANOVA
         level) + two hand-rolled copies in hlp_analytics (the mobility + the pattern table formatters). ANALOGOUS but
         NOT the same computation: (a) the grouping — the ANALYTICS pools ALL the instances of a feature into ONE
         classification (one number per feature), the ANOVA level computes per sub-variable (feature × instance); (b)
         the metric — the ANALYTICS reports eta² only (the biased sample share), the ANOVA the eta² + omega² pair.
         EXCEPTION: the single-instance features (n_inst == 1) have COINCIDENT groupings — the two values must agree.
         Verified on rlm_00: ALMC / LMC / DLMC are n_inst == 1 (EDGE 4, ELLIE 8). My take: not a bug (the two answer
         different questions); the only smell is the formula hand-written three times. Three options proposed: (a)
         leave-as-is / (b) the cross-invariant test / (c) the unification onto the kernel. Roberto: "(b) + (c)".
         IMPLEMENTATION (c): the two hand-rolled SS blocks (verified byte-identical — the replace_all) become the shared
         anova_eta_omega(train_flat, y_repeated)['eta2'] call; the bincount pass is KEPT (the table's FREQUENCY /
         AVERAGE_GV / RMSE_GV columns need counts / sum_y / sum_y2). The kernel's guards match the hand-rolled semantics
         (ss_tot == 0 -> 0.0; k == 1 -> 0.0). IMPLEMENTATION (b): the new DB-gated TestEtaSquaredCrossLevel
         (test_wrk_analytics, rlm_00): force-enables cfg.anova after CONFIG, runs the chain to ANALYTICS (BOTH reports
         produced), re-parses both line by line, asserts assertAlmostEqual (places=4) on the 3 single-instance features
         — DERIVED from feature_set.feature_blocks, not hardcoded (the sanity pin: at least one exists). VERIFICATION:
         the analytics suite 14/14 — the rlm_02 + rlm_01 report goldens SURVIVED UNCHANGED (the kernel's bincount-based
         SS is bit-identical to the inline one); the fast suite 958/0 (99 skipped) + the LONG=1 suite 958/0 (24
         skipped); verify_anova 0 mismatch; verify_analytics 0 mismatch; the 4 mirror docs updated (hlp_analytics,
         test_wrk_analytics, wrk_anova, hlp_feature_analysis); docs audit only the 7 pre-existing size findings;
         notes_format 0.

D-312 | 2026-09-25 | the wrk_su_analysis module docstring REMOVED (the house de-history style, the D-306 precedent)
         Roberto's review of the module docstring: "Non e' accurata, ci sta cose che non sono nel modulo, cita le
         decisioni." Clause-by-clause audit against the module body: 3 D-XXX citations (D-289 / D-288 / D-060 — the
         rules.md docstring rule, D-224/D-226: WHAT only, no D-XXX provenance in the docstrings, decisions.md is its
         home); 2 hlp internals (the binio cache flow, the consistency signature with the feature_set hash — both live
         in hlp_su_analysis; the worker only passes the cache_manager callbacks); 1 state-machine clause (the "the
         machine re-raises" — the module has NO error handling; D-060 is a state_machine decision); 1 change-history
         clause ("INSTEAD of the rds_checksum" — the exact phrasing D-306 removed from the hlp's _signature docstring);
         2 soft inaccuracies ("the enable no-op" — the disabled path PUBLISHES None on the ctx, the ANOVA level's
         graceful-degradation input; "the adherence, step 6" — consumer knowledge, not the module's). Context: 7 of the
         10 sibling workers have NO module docstring (the wrk_design_matrix majority). Two options proposed: (1) the
         thin WHAT-only rewrite / (2) the removal. Roberto's ruling: "Opzione 2 va bene. Procedi!" — the docstring
         REMOVED (the module goes straight from the license header to the imports, the house majority style). The mirror
         doc intro re-synced: module-accurate (the enable guard + the None publication, the cache_manager
         load-or-compute flow over the hlp callbacks, the ctx.use_cache gate; the binio I/O + the signature attributed
         to the hlp with the D-288 / D-291 pointers) — the D-pointers stay in the mirror (their home, the docs_rules
         §3.2). VERIFICATION: no probe / test pinned the docstring text (the grep sweep — the probe hits are the probes'
         own comments); the fast suite 958/0 (99 skipped); verify_su_analysis 0 mismatch; the docs audit only the 7
         pre-existing size findings; notes_format 0 rejoins. NOTE (open, flagged to Roberto): the wrk_anova docstring
         still ends with "The D-060 semantics." (the same violation; a separate sweep is his call).

D-313 | 2026-09-25 | the wrk_anova module docstring REMOVED (the D-312 precedent — the house de-history style) Roberto:
         "La docstring del modulo wrk_anova ha lo stesso problema — non e' accurata, ci sta cose che non sono nel
         modulo, cita le decisioni. Leggi il modulo e riformula. Eventualmente rimuoviamola come per wrk_su_analysis."
         Clause-by-clause audit: the docstring is CLEANER than the su_analysis one — only 1 D-XXX ("The D-060
         semantics." — a pure pointer with no content: the module has NO error handling; the observable fact, the down
         is a no-op that publishes nothing, is already in the _down comment + the mirror); 2 soft kernel misattributions
         (the eta²/omega² math lives in the shared anova_eta_omega kernel, the adherence trio in the shared adherence
         kernel — both hlp_feature_analysis, the module only CALLS them); everything else is in-module WHAT (the
         graceful-degradation branch, the NO-cache level fact). Two options: (1) the thin rewrite / (2) the removal.
         Roberto: "Procedi con l'opzione 2." The docstring REMOVED (the module goes straight from the license header to
         the imports; now 8 of the 10 workers have no module docstring). The mirror doc needed NO change: its intro is
         already module-accurate, carries no D-XXX in the intro, and already says "The down is a no-op — the worker
         publishes nothing on the ctx" (it had replaced the D-060 pointer with the fact long ago). The _down code
         comment ("the D-060 recovery is trivially satisfied") stays — a source comment, where design pointers are
         allowed (D-269/D-270). VERIFICATION: the fast suite 958/0 (99 skipped); verify_anova 0 mismatch; the docs audit
         only the 7 pre-existing size findings; notes_format 0 rejoins. FOLLOW-UP (Roberto, post-commit): the
         wrk_anova.py reflow to the 120-char line width — a separate step, his call on the commit.

D-314 | 2026-09-25 | the wrk_anova.py reflow to the 120-char line width + the source line-length rule Roberto, after
         the D-313 commit: "Riorganizza solo il file wrk_anova.py con lunghezza riga fino a 120 caratteri, nessun hard
         limit, in casi eccezionali le righe possono anche sorpassare il limite. Vediamo come esce esteticamente. Fatto
         ti do indicazione se procedere al commit." The reflow (purely formatting — every string value byte-identical,
         the verify_anova A1–A8 source-text pins preserved verbatim): 175 -> 144 lines, NO line > 120 (max 118 — the
         allowed exception was never needed); the multi-line string concatenations joined (the report lines, the CSV
         rows, the short logs single-lined), only the 3 long log calls stay 2-line (the message alone is 80–95 chars);
         the backslash continuations gone; the function docstrings re-wrapped to 120 (text unchanged). VERIFICATION: the
         fast suite 958/0 (99 skipped) + verify_anova 0 mismatch (the D tier live A2050 run — the report lines
         recomputed, the goldens intact). Roberto: "Va molto bene! Mi piace molto. A questo punto aggiungi la rule in
         rules.md e facciamo il commit." The rule (rules.md, the new Code style section, D-314): NO linter gate / no
         hard limit (pyproject carries no flake8/ruff); new or edited lines match the local file's wrap convention (the
         lm zone's historical ~72–76); a convention-less file defaults to <= 79 (PEP8); a full-file reflow to 120 is a
         deliberate user-directed act (this reflow is the precedent) — never an agent side-effect, and never a re-wrap
         of untouched lines; the docs/notes stay at ~120 (D-237). Context (measured): 95.1% of the src/reversi lines are
         <= 80 chars.

D-315 | 2026-09-25 | hlp_feature_analysis renamed hlp_anova + the compute/report methods moved in (the worker is the
         pure skeleton) + the D-314 reflow Roberto: the module "Vorrei rinominarlo hlp_anova. Poi vorrei applicare la
         nuova regola sulla formattazione. Vorrei poi spostare _write_report da wrk_anova a hlp_anova ... lasciano solo
         ctx. I due argomenti li calcoliamo nel codice di _write_report chiamando _compute_anova_lines e
         _compute_adherence_lines. Anche questi due metodi vanno nel modulo hlp_anova. hlp_anova esporta _write_report
         che rinominerei in write_anova_report." Analysis: the name was stale by construction (the D-298 split left
         exactly the ANOVA family — the verify_anova F5 pin said so); the impact map: 7 code references + 7 docs + the
         runner + 5 probe pins (the verify_anova A4/A5/F5 + the verify_su_analysis F6 cross-probe + the F2 family
         exclusion). My P1 flag (the write_anova_report name covered compute + write, diverging from the house pattern
         where the worker orchestrates separate hlp calls): Roberto took it — "prendo la tua proposta, teniamo i due
         metodi" — the two PUBLIC methods, the worker orchestrates. His naming lean (the hlp_anova_ prefix, "piu consoni
         ed in linea con lo standard" — the prefix is the cache-flow family standard, hlp_anova is user-directed): the
         final names hlp_anova_compute_analysis (the two passes, returns (anova_lines, adherence_lines)) +
         hlp_anova_generate_report (the TXT + the CSV). P2: the two compute helpers stay PRIVATE (_compute_anova_lines /
         _compute_adherence_lines) — the boundary is the 2 FLOW functions + the 2 kernels. P3: the module docstring
         REMOVED (the D-312/D-313 disease: the D-298 history + the stale "accumulator output" phrase). IMPLEMENTATION:
         the git mv (module + test_hlp_anova + the 2 mirrors), wrk_anova is now ~50 lines (the guard + the 2 calls; the
         csv / Path / numpy imports gone), hlp_anova.py reflowed to the D-314 width (the kernel docstrings
         text-identical), the consumers updated (hlp_analytics import + comment, test_wrk_analytics import, the test
         alias hlp_fa -> hlp_an, the runner line), the re-pins: verify_anova A4 (the two methods import), A5 (the
         degradation branch now read from hlp_anova), F5 (the family + the 2 new defs), the probe import + header;
         verify_su_analysis F6 (the worker imports the methods, hlp_anova reads ctx.su_analysis_tables) + the F2 label
         (the historical references, the family is gone). VERIFICATION: the fast suite 958/0 (99 skipped); verify_anova
         0 mismatch (the D tier live A2050 — the report goldens intact); verify_su_analysis 0 mismatch; the log sequence
         + every report value unchanged (the strings moved, not touched); the docs audit + the notes_format clean.

D-316 | 2026-09-25 | the ANALYTICS report: the Omega-Squared line after the Eta-Squared line (both feature tables)
         Roberto: anova_eta_omega is also called from hlp_analytics — only the eta2 value is used, in the "Eta-Squared
         (Discrimination)" line written for BOTH the mobility + the pattern feature tables; add a line after it that
         prints omega2 in the report as well. IMPLEMENTATION: the two formatters (the byte-identical blocks, the D-311
         replace_all) now take the full kernel dict (anova_res = anova_eta_omega(train_flat, y_repeated); eta_squared =
         anova_res['eta2']; omega_squared = anova_res['omega2']) and the header carries the "Omega-Squared
         (Discrimination): {omega_squared:.4f}" line right after the Eta-Squared line (the same raw value convention as
         the ANOVA report — omega² may be slightly negative, the null effect). VERIFICATION: the two date-masked report
         goldens RE-DERIVED (rlm_02 3b4a5beb… -> e0d3d22a…, rlm_01 384d8327… -> 176a80b5…) — only the hash line failed,
         every other pin green; the analytics suite 14/14 (LONG=1, the DB goldens + the D-311 cross-level test, whose
         regex parse is unaffected — the omega line sits AFTER the first eta match); the fast suite 958/0;
         verify_analytics 0 mismatch (the probe recomputes its masked hash at runtime — no pinned golden); the 2 mirrors
         updated (hlp_analytics, test_wrk_analytics).

D-317 | 2026-09-25 | hlp_anova: the kernels renamed hlp_anova_eta_omega / hlp_anova_adherence + the @validate_call
         boundary + the descriptive docstring style (all 9) + the boundary comment removed Roberto: (1) the boundary
         comment above __all__ is inutile — remove it (I agreed: it duplicates the mirror + carries D-298/D-315 history
         that belongs in decisions.md, and it is "obvious" — outside the design-pointer comment exception, D-269/D-270);
         (2) he PROPOSED a docstring style for adherence (the imperative first line, the explanatory body, the typed
         Google-style Args / the key-by-key Returns) — "uno stile che trovo piu' chiaro ed appropriato"; (3) Pydantic
         validation on the public calls. Analysis: the style is fully compatible with the house WHAT-only rule (the
         shape becomes explicit, no D-XXX, no HOW) — the "design section 3.5" pointer drops from the kernel docstrings
         (the mirror keeps it, the designated home); the lm idiom (verified on every hlp) = every public function
         @validate_call(config=ConfigDict( arbitrary_types_allowed=True)) EXCEPT the ctx functions (the LMContext is a
         TYPE_CHECKING import — decorating would NameError at decoration time; the hlp_design_matrix circular-import
         idiom, documented in D-303). All call sites checked: the kernels receive only Python lists / numpy arrays /
         Python-int dicts (the tolist() / int() conversions verified in _compute_adherence_lines + _su_sample_stats) —
         zero coercion risk; ~70 calls per run max (not a hot loop — the numba / numpy loops are). Roberto's rulings:
         (b) ALL 9 docstrings in the new style (the module is the unit, it becomes the exemplar); the rule codification
         "lo verifichiamo dopo"; the decorators ONLY where no ctx in the args (the 2 kernels — the 2 FLOW stay
         undecorated); the kernels RENAMED hlp_anova_eta_omega / hlp_anova_adherence (the hlp_X_ prefix family standard,
         like the D-315 FLOW names). IMPLEMENTATION: the comment gone (imports -> __all__ -> functions, the wrk_anova
         post-D-313 shape); the 4 public names all share the hlp_anova_ prefix; the 2 kernels decorated + annotated
         (npt. ArrayLike; dict[str | int, int | float] — the docstring types became the real annotations); all 9
         docstrings rewritten (the formula block of the ANOVA kernel kept — it IS the WHAT contract); the consumers
         updated (hlp_analytics import + 3 calls, test_hlp_anova import + 8 calls, test_wrk_analytics import + 2 calls,
         the verify_anova probe import + 4 calls + the F5 pin re-pinned to the new def names); wrk_anova untouched (it
         imports only the FLOW functions). VERIFICATION: the fast suite 958/0 (99 skipped); the hand-computed goldens
         intact (eta2 0.2 / omega2 -1/7, the adherence trio TV 0.6 KL 0.9336627322538263 chi2 47.77777777777778 — the
         smoke test + the suite); the guard ValueErrors survive (they raise AFTER the validation, inside the function);
         the verify_anova F5/A4/A5 + the verify_analytics + the verify_su_analysis F2/F6 green; the docs audit + the
         notes_format clean; the 5 mirrors updated.

D-318 | 2026-09-25 | the descriptive docstring style codified as the house rule (the D-317 hlp_anova style) Roberto:
         "Codifichiamo questo stile come RULE. Yes, e' un notevole miglioramento. Procedi per favore." — after seeing
         the D-317 result (the 9 hlp_anova docstrings in the new style). PROMOTION (the standing rule pattern: the rule
         that must outlive the campaign goes to rules.md in the same commit with its D-number): the new bullet in the
         rules.md Docs section, right after the WHAT-only rule it completes — the descriptive format (the imperative
         first line, the body paragraph, the Google 8-space typed Args, the key-by-key Returns; the formulas that define
         the output values stay in the docstring — they are the WHAT). The division of labor: the D-224/D-226 rule
         constrains the CONTENT (no HOW, no D-XXX), this one the FORMAT. Scope: public + private functions in src/ (the
         test / the probe docs keep their own rules, D-267/D-270); it binds the NEW docstrings + any REWRITTEN one; the
         retroactive conversion of the existing modules is USER-DIRECTED, one module at a time (the D-314 reflow
         precedent — never an agent initiative, the D-122 guard). The hlp_anova module is the exemplar (D-317); its
         mirror Conventions bullet now points at the rule (D-318) + its introducing decision.

D-319 | 2026-09-25 | the A2030 / A2050 full-chain report goldens re-derived (the D-316 Omega-Squared line missed them) +
         the mirror hash desync since D-307 fixed Roberto: "Trovo questi due test che falliscono" — the
         TestFullChainA2030 (rlm_04) + the TestFullChainA2050 (rlm_03) test_full_worker_chain hash assertions (his full
         LONG run: 958 tests, 2 failures). ROOT CAUSE (mine): at D-316 I re-derived the two report goldens in
         test_wrk_analytics (rlm_02 / rlm_01) but the ANALYTICS file report is pinned in FOUR places — the two
         full-chain goldens (c3522d10… / 8b2ed520…) were never re-derived, and my D-316 verification ran only the FAST
         tier + the analytics module (the full-chain tests are LONG-tier — the 99 vs 24 skipped difference), so they
         never ran. LESSON: after a report FORMAT change, grep _masked_report_hash across test/ + probes/ for EVERY pin,
         not just the known ones. VERIFICATION (the causal check): the scratch run of both chains to ANALYTICS
         recomputed the masked hashes — byte-identical to Roberto's run actuals (A2030 fae8fe75…, A2050 309d1dcb…) — and
         showed the report's only new content is the Omega-Squared line (2/2 features on rlm_04, 12/12 on rlm_03; SU-off
         in both fixtures, the omega line is the sole delta). GENEALOGY (git -S): the test goldens were last set
         at D-307 + D-308 (4a9c6dd) — D-311..D-317 were all behavior-preserving; the mirror hashes (a9642167… /
         695c151b…) date from the D-273 move (572b02c) — the mirror had been STALE since D-307 (that re-derivation never
         touched it). FIX: the 2 test constants + the 4 mirror occurrences -> the new values; the mirror Goldens note
         updated. VERIFICATION: A2030 re-run LONG=1 green; A2050 re-run VLONG=1 green (the class carries
         @skipUnless(tier_vlong()), L423 — the D-319 first re-run used only LONG=1 and skipped it); the fast suite 958/0
         (the goldens are DB-tier, the fast tier skips them).

D-320 | 2026-09-25 | the two stale notes docs archived to notes/analyses/historical/ (the I-017 project plan + the
         wave-tier performance baseline) Roberto: "I documenti: performance_baseline e analytical_properties_of_features
         possono essere rimossi o spostati nei documenti storici. Non sono piu' di attualita'." Analysis: (1)
         analytical_properties_of_features.md (647 lines) is the I-017 project document — I-017 is done in ideas-closed
         (T1..T19, D-156..D-189: the MT19937 PRNG port + the G0 wave generator, the SU level, the design matrix, the
         indexes — the whole feature-analysis build); the plan exhausted its function. (2) performance_baseline.md (55
         lines, the D-175/D-176 snapshot of 2026-09-13) was the reference numbers for the profiling session scheduled
         AFTER the SU level — the SU level has been complete for a while (D-288..D-311) and the session never ran; the
         immediate purpose lapsed. REPOSITORY REFERENCE MAP (the grep): the only LIVE references are the 2 overview
         index lines; the rest are historical pointers (decisions.md x3, decisions_001 x1, log_002 x1, log_003 x2 —
         append-only, never touched); ZERO code / probe / tool / rule references — pure collaboration docs. ARCHIVE
         PATTERN: the house pattern is archive, not delete (the closed decision volumes, ideas-closed, the
         analyses/historical/ with the ODP-9 material — I-017-era docs ALREADY archived there: the
         random-permutation-table analysis + 3 peer reviews). My recommendation: MOVE (the git mv with the names kept,
         so the historical pointers stay resolvable by name; the small files cost nothing; the I-017 plan is the single
         full source of the SU level WHYs; the baseline keeps the "beat these" numbers if the profiling session ever
         resumes). Roberto: "Prosegui con Piano A." IMPLEMENTATION: the git mv of both files to
         notes/analyses/historical/ (the names unchanged); the overview index: the 2 root lines removed, the content
         folded into the notes/analyses/ line (which now cites the historical/ subdir: the I-017 plan, the baseline, the
         ODP-9 material). The baseline's `> State:` line is untouched (the archive is a move, not a rewrite — the
         content stays as the historical record). VERIFICATION: the residual grep shows only the historical pointers;
         the notes_format clean; no code / docs-mirror impact.

D-321 | 2026-09-28 | the FINAL_LOG_PRINT level (the 19th, the pipeline's last): the full run log on file, the optional
         log_file_name config gate Roberto: "Vorrei valutare di aggiungere un nuovo livello. Posizionato ultimo, dopo
         PLOT. Lo chiamiamo FINAL_LOG_PRINT. Come attivita' scrive su file il LOG FULL di tutti i livelli alla massima
         rilevanza. Aggiungiamo il worker: wrk_final_log_print. Legge un parametro di configurazione dal JSON
         log_file_name, facoltativo senza valore di default (default None). Se la entry manca, il file NON viene
         generato. Per favore sviluppa una analisi dettagliata, la valutiamo insieme, ti dico poi come procedere." The
         analysis: the machine already buffers EVERY event (the LogEntry list, filled independent of the display
         verbosity gate — the "full log at maximum relevance" already exists in memory; the LogEntry docstring
         anticipated the file/DB dumps); the design follows the house pattern (the guard in the worker, the logic in the
         hlp, the PLOT idiom). Roberto: "Perfetto! Procedi." (P1 the live-line replay format, P2 the no-op log line, P3
         base_dir-relative — my recommendations, accepted as-is.) IMPLEMENTATION: (1) the generic-zone addition —
         state_machine.py: the _format_event_line static (the live-line single source of truth, the log_event print
         refactored onto it) + format_event_log() (the full buffer render, all relevances, the live-line text) + the
         context injection (self.context.format_event_log = self.format_event_log, the established injection pattern);
         (2) the config — LMConfig.log_file_name: str | None = None (the top-level field, the D-321 gate; the absent
         entry -> no file); (3) hlp_final_log_print.py — the single function hlp_final_log_print_write_log(ctx) -> Path
         (undecorated, the ctx idiom D-317; the D-318 docstring style; base_dir / log_file_name, the parents created,
         UTF-8); (4) wrk_final_log_print.py — the factory Worker("FINAL_LOG_PRINT", _up, _down); the _up gate (the
         None -> the "skipped" no-op log) + the hlp call; the _down no-op (the file is a base_dir artifact); (5) the
         registration in logistic_model (the 19th level, after PLOT — 20 workers with the sentinel); (6) the tests — the
         new test_wrk_final_log_print (5 NO-DB mock-ctx + 1 LONG-tier e2e: the rlm_00 chain, the log_file_name set
         post-CONFIG, verbosity NONE — nothing prints, the buffer captures everything; the write-asymmetry pins: the
         file carries its own "Starting" line, NOT the "Completed" nor the "full log written" lines — both post-write;
         the line count == the buffer at the write) + the test_state_machine TestDisplayGoldens
         test_format_event_log_full_replay (the frozen-clock full-replay golden, the VERY_LOW verbosity, the injection
         pin); the full-chain step pins 18/PLOT -> 19/FINAL_LOG_PRINT (both classes); run_utests.sh + the new module;
         (7) the probes — the new verify_final_log_print (12 checks, no DB: the module structure A1-A6 + the
         synthetic-machine behavior B1-B4, the write-asymmetry invariant, the independent live-line re-derivation, the
         max-relevance replay) + the hub verify_logistic_model V3c re-pin 18 -> 19 (the precedent: 10->11->...->18 at
         each level enablement). THE WRITE ASYMMETRY (documented, not a defect): the file is the buffer at the moment of
         the write — it carries the "Starting worker FINAL_LOG_PRINT, UP step" line (the machine logs it BEFORE the
         worker call) but not the post-write lines (the hlp confirmation + the "Completed UP step"). VERIFICATION: the
         fast suite 965 tests OK (100 skipped; +7: the 5 NO-DB + the 1 e2e + the 1 render golden); the LONG full-chain
         (A2030) + the VLONG (A2050) 9/9 OK (the new 19/FINAL_LOG_PRINT pins, the no-op path — the fixtures carry no
         log_file_name, the report hashes untouched); verify_final_log_print 12/12 + verify_logistic_model ALL CHECKS
         PASSED; the mirrors: 3 new (wrk/hlp/test final_log_print) + the updates (logistic_model 18->19 everywhere,
         hlp_config_schemas the field, state_machine the method + the injection, the 7 "18-level" refs, the
         test_state_machine golden count); the overview: 3 new table rows + the 19-level/965-test state line + the D-321
         recent bullet; the docs/notes audit clean. DESIGN NOTE: zero impact on the existing runs — the gate is the
         optional entry (the fixtures + the external A2030/A2050 configs untouched, the no-op path, the goldens safe);
         the "maximum relevance" is structural (the buffer fills on every log_event, independent of the display gate) —
         no logging change was needed.

D-322 | 2026-09-28 | the D-321 e2e test fix: the log_file_name must be present in the config BEFORE the CONFIG level
         (the checksum desync) + the "skipped" pin narrowed to the FINAL_LOG_PRINT line Roberto: "Vedo questo errore:
         ... ValueError: Config section checksum mismatch, expected 'ca11b76f...', recomputed '78a58cef...' ... FAILED
         (errors=1)" — the D-321 LONG-tier e2e failed in his environment. Root cause (two defects, both mine, both
         latent — the e2e never ran at the LONG tier in the D-321 verification; it sat in the fast-tier skip list): (1)
         the e2e mutated ctx.cfg.log_file_name AFTER the CONFIG level — the config checksum is fingerprinted at CONFIG
         (the sha3_256 of the normalized dump), while SAVE embeds the LIVE normalized dump; the post-CONFIG mutation put
         log_file_name in the embedded dump but not in the fingerprint -> the file's config section self-inconsistent ->
         the CLIENT_CHECK read verification raised. Fix: the entry is now present in the config FROM THE START — the
         test writes a tmp copy of the rlm_00 fixture with the log_file_name entry added (the same json5 loader the
         pipeline uses) and builds the model from it; no post-CONFIG mutation (the D-311 cross-level idiom is only safe
         for chains that STOP before SAVE — TestEtaSquaredCrossLevel stops at ANALYTICS). (2) the e2e pin "no 'skipped'
         in the file" was too broad — the max-relevance log legitimately carries the other levels' no-op notes (the
         rlm_00 "PLOT skipped"); the pin narrowed to the exact "FINAL_LOG_PRINT skipped" line. VERIFICATION: the module
         at LONG=1 6/6 OK (the e2e actually runs this time); the fast suite re-verified; the mirror + the overview
         updated (the "set post-CONFIG" wording). LESSON: a new DB-gated e2e is part of the campaign verification (run
         it at LONG=1 before the commit) — the D-319 recurrence (the pins missed by the fast-tier-only verification),
         same class of error.

D-323 | 2026-09-28 | the new code-format rules applied to the inference client: the D-314 120-char reflow + the D-318
         descriptive docstrings on client.py (the D-141 / the D-111 M5 provenance out, zero behavioral change) Roberto:
         "Applica le nuove regole di formattazione del codice a client.py. Per favore sviluppa una analisi
         dettagliata" -> "Procedi." — the two recently codified rules, applied as a pair (the hlp_anova precedent
         — D-315 the reflow, D-317 the docstrings): (1) the D-314 full-file reflow to the 120-char width (the
         deliberate, user-directed act — this request): the code was already 120-ish (max line 107, the array factory
         signature) — the reflow's visible code effect is only the GNU header (the 4 empty comment lines' trailing
         spaces cleaned to the reflowed files' clean form); (2) the D-318 descriptive docstring conversion (the
         user-directed, one-module-at-a-time retroactive pass): the 3 docstrings rewritten to the hlp_anova exemplar
         (the imperative first line, the body paragraph, the typed Google-style Args / Returns); the scalar factory
         carried only a one-line docstring, now the full form; _prepare_weights' two return values move from free-text
         to the Returns: key-by-key. PROVENANCE OUT (the D-224/D-226 + the D-269 split): the 3 D-XXX references removed
         — the 2 D-141 (the vectorized-client origin, in the _prepare_weights + the array-factory docstrings) +
         the D-111 M5 (the guard comment's review pointer); the guard's WHY stays (the PositionArray validator admits a
         2-D structured array — no ndim check — the guard keeps a clean ValueError out of the numba kernel). NOT TOUCHED
         (precedent): the numbered 1-4 step comments (the HOW in the code comments, the D-224 norm); the 2 nested ef
         closures stay docstring-less (no lm closure carries a docstring — the _up/_down family; the factory's Returns:
         section is the returned callable's contract); no module docstring (the D-312 / D-313 precedent, hlp_anova).
         VERIFICATION: the AST equality of the old and the new file with the docstrings nullified (the zero-code change
         proof) + the compile; test_client 7/0/1 (the bit-exact 1000-position parity, the u64 coercion, the N=0 edge);
         the full pre-commit LONG=1 965 OK (24 skipped — the in-chain EF pins re-verified); the verify_save statics +
         the hub verify_logistic_model clean; the mirror updated (the 136 -> 156 lines + the Conventions bullet); the
         docs/notes audit clean.

D-324 | 2026-09-28 | the new code-format rules applied to hlp_config_schemas.py: the D-314 120-char reflow + the D-318
         docstrings + the "keep it simple" description sweep (the 9 D-XXX provenance refs + the drifting ordinals out) +
         the 2 D-267 test-docstring refs removed Roberto: "Applica le nuove regole di formattazione del codice a
         hlp_config_schemas. Controlla in particolare le description, sono piene di storia, keep it simple." ->
         "Procedi, e rimuovi anche i due D-267." — the D-323 pair (the D-314 reflow + the D-318 descriptive docstrings)
         plus the description-specific sweep this request called out: DESCRIPTIONS (the "piene di storia" cleanup): the
         9 D-XXX provenance references removed — the D-149 x4 (the PLOT_NAMES import comment, the PlotConfig docstring,
         the enable + plots descriptions), the D-281 (the CorpusConfig docstring), the D-280 (the empty_count
         description — the whole migration story, including the redundant fields' names), the D-143 (the
         regab_allow_duplicate description + "the pre-existing behaviour"), the D-148 (the client_check_tol
         description), the D-321 (the log_file_name description); the drifting ordinals out ("the 18th level", "step 3"
         x2, "step 6" x2, "the 19th level" — the levels are NAMED, not numbered); the narrative bits out (the "uno per
         tutti" seed flavour, the "minutes at the wave tier" — the wave engine is RETIRED, the "mele con mele"
         constraint, the "design section 3.6" external pointer). What STAYS: the observable contracts (the Y-space
         rationale of client_check_tol, the log-only note of regab_allow_duplicate, the bin detail of rarity_thresholds,
         the "eta²/omega² + the adherence" of anova). DOCSTRINGS: the 4 verbose class docstrings compressed to the
         essential contract (PlotConfig — D-149 + the ordinal out; CorpusConfig — the design section + the D-281 + the
         flavour out; SuAnalysisConfig 15 -> 4 lines — the ordinal + the production/experiment narrative out, the bin
         detail stays in the field description; AnovaConfig — "step 6" out); the class docstring style stays the file's
         "Configuration for X." noun form (the D-318 formally binds the FUNCTIONS); the 2 "Converts" indicative
         validator docstrings -> imperative "Convert"; the noun-phrase check_su_pairs_feature_set -> imperative "Enforce
         that ..."; the other 5 validators were already imperative + WHAT (unchanged). REFLOW + HYGIENE: the 2 over-120
         lines (the min_grad / min_p_fun_decrease one-liners, 138/143) to the 3-line form; the multi-line Field(...)
         blocks re-wrapped at 120 (the seed / total_positions / dpi / cache_files_prefix / report_file_name fields
         collapse to one line); the GNU header trailing spaces cleaned; the 4 whitespace-only lines + the 2
         trailing-space lines removed; the 3 blank lines before LMBaseConfig normalized to 2; the board import merged to
         one line. D-267 (the 2 test-docstring refs, the side observation Roberto approved): test_hlp_config_schemas.py
         — the "(D-280)" in the empty_count test docstring + the "D-292" in the rarity test docstring removed (the test
         docs carry no D-xxx references). PIN STATUS (verified before the change): zero test edits needed for the
         description sweep — the 27 schema tests are bare assertRaises(ValidationError) (no message-text pins, no
         assertRaisesRegex, no .errors() content), nothing reads the .description attribute of these fields (the grep
         hits are the binio header + the regab cursor), the wrk_config checksum is over model_dump() (descriptions not
         included); the probe D-XXX mentions are the probe check-label vocabulary (D-270, untouched). MIRROR: the
         "D-280, replacing su_analysis.corpus.ec + regab_data_set.ec" migration clause out (the D-280 pointer stays —
         the mirror is the pointers' home); the 2 pre-existing audit findings on this mirror addressed in the sync: the
         unbalanced code span fixed (the `log_file_name: str | None` atomic) + the line count re-tightened (123 -> 122,
         the size finding stays at the pre-existing baseline level — reaching 120 would require cutting 2 pinned fact
         lines, left to Roberto). VERIFICATION: the model_fields comparison old (HEAD) vs new — every class, every
         field: required / default / default_factory / annotation / constraints IDENTICAL, descriptions excluded (the
         zero-behavior-change proof; the D-323 AST trick does not apply — the descriptions are data in the AST);
         test_hlp_config_schemas + test_wrk_config 41/0/0; the full pre-commit LONG=1 965 OK (24 skipped — the fixtures
         parse through the cleaned schemas, the checksums + the goldens untouched); verify_wrk_config + the hub
         verify_logistic_model ALL CHECKS PASSED; the docs/notes audit at the baseline.

D-325 | 2026-09-28 | the new code-format rules on hlp_gradient (the D-314 reflow + the D-318 docstrings) + the hardcoded
         _HP_BLOCKS moved to the config as the hi_perf_blocks field (PositiveInt, default 8), explicit in the rlm_00
         fixture Roberto: "Applica le nuove regole di formattazione del codice a hlp_gradient. Vorrei valutare di
         eliminare il valore hard coded _HP_BLOCKS e portarlo nel config, nel ramo optimization. Chiamiamolo
         hi_perf_blocks, intero maggiore di zero, default 1. Valore consigliato 8." -> "Ok, mettiamo default=8, procedi.
         Ma in almeno un JSON mettiamo il campo rlm_00 o un altro." FORMAT (part A): the D-323/D-324 pattern: the header
         trailing spaces cleaned; the sigmoid docstring imperative + the "It was computed as: return 1./(1+np.exp(-x))"
         line out (the old implementation — history, the D-224 rule); the _hp_fg_kernel docstring from the free-form "X
         : (M, P) uint32 —" block to the Google Args style (no parenthesized types — the kernel parameters carry no
         annotations, the shapes/dtypes are in the description); the hlp_gradient_compute docstring to the full D-318
         form (imperative + body + Args with the new hi_perf_blocks parameter + Returns); the _HP_BLOCKS comment block
         (5 lines) removed — the observable facts (the race-free design, the thread-count-independent determinism) moved
         to the compute docstring. FEATURE (part B): the _HP_BLOCKS = 8 constant removed; hlp_gradient_compute(ctx,
         high_performance=False, hi_perf_blocks=8); the buffers np.zeros((T, N)) from the parameter; the kernel
         unchanged (already T-parametric via g_blocks.shape[0]); wrk_gradient reads ctx.cfg.optimization.hi_perf_blocks
         and passes it — the GRADIENT log line UNCHANGED (the full-chain log pins safe);
         OptimizationConfig.hi_perf_blocks: PositiveInt (default 8, the "intero maggiore di zero"); the rlm_00.json
         fixture carries "hi_perf_blocks": 8 explicitly (Roberto's request). DEFAULT = 8 (Roberto's ruling, over the
         proposed 1): the shipped fixtures rlm_03 / rlm_04 / rlm_05 / rlm_06 enable high_performance_fg (the full-chain
         A2030 / A2050 run the HP kernel) — default 8 = the current hardcoded value = bit-identical behavior (the HP
         trajectory goldens intact: A2050 356 iters / f = 1.4453826e-03 / the w_dense sha3; A2030 71 iters). T = 1 would
         additionally have lost the prange parallelism (the kernel parallelizes ACROSS the blocks) — flagged in the
         analysis. GOLDEN CASCADE (planned, turned out ZERO): the new config field changes the config checksum (the sha3
         of the model_dump_json, wrk_config) — but the _masked_report_hash of the two test modules MASKS the "Config
         SHA3-256: <hex>" line itself (the mask exists because the fingerprint embeds the tmp base_dir) → the 4 report
         pins (test_wrk_analytics x2 + the full-chain x2) are insensitive → NO re-derivation. Verified before the
         change: test_wrk_config / verify_wrk_config pin no literal checksum; the old model files stay readable (the
         reader hashes the STORED dump text against the stored checksum — self-consistent, model_weights L176-183;
         no D-322 desync — a pydantic default, not a post-CONFIG mutation); the external A2030 / A2050 configs need no
         migration (default 8 = non-breaking). TESTS: +1 test_optimization_hi_perf_blocks (default 8, accepts 1, rejects
         0 — the schemas suite 28 -> 29; the overview's "27" was stale, corrected in place); the test_wrk_gradient mock
         (the SimpleNamespace) gained hi_perf_blocks (an AttributeError without it); +1 test_hp_block_count
         (hi_perf_blocks=2 over M=3 vs the float64 reference — hlp_gradient 14 -> 15). PROBES: verify_gradient re-pinned
         (A1 180, A8 the new sigmoid docstring, A12 L95, A14 the hi_perf_blocks parameter + the "_HP_BLOCKS not in a"
         pin, B1 65, B5 the new wiring, C1 184, G1 284 / 15 tests, G9 the new test) — 59/0 incl. the live-DB tier D (the
         rlm_02 classic-path values unchanged); verify_optimize +E4c. FOUND IN THIS CAMPAIGN: the verify_optimize E4 pin
         had been broken since D-324 (it pinned min_grad on ONE line; the D-324 reflow made it 3 — that probe was not in
         the D-324 verification list) — fixed in this commit. MIRRORS: hlp_gradient.md (the API row, the Architecture
         T-refs, 15 tests, the "10th active level" ordinals -> the level name; back to exactly 120 lines),
         wrk_gradient.md (the wiring), hlp_config_schemas.md (the API row — the 122-line size finding stays at the
         baseline), + the 3 test mirrors (15 / 29 tests + the new tests). VERIFICATION: the 3 fast modules (15 + 29 + 13
         all OK); the full pre-commit LONG=1 967 OK (24 skipped — the A2030 HP chain, the report pins, the size bands);
         the VLONG full-chain (A2050) OK; verify_gradient 59/0 + verify_optimize 78/0; the docs/notes audit clean.

D-326 | 2026-09-28 | the new code-format rules on hlp_indexes (the D-314 reflow + the D-318 docstrings) + the side files
         the user opted into (option c): the header cleanups on wrk_indexes / both test files + the single 123-char test
         line Roberto: "Applica le nuove regole di formattazione del codice a hlp_indexes. Per favore sviluppa una
         analisi dettagliata, la valutiamo insieme, ti dico poi come procedere." -> (the analysis, with the two optional
         items flagged) -> "Procedi con (c), grazie!" FORMAT: the D-323/D-324/D-325 pattern. The header GNU trailing
         spaces (4 lines) cleaned; the single 131-char line (the is_cache_consistent compare, L195) reflowed to the
         aligned-paren form; the 2 "LZ4 whole-file compression by default (D-139, as in model_weights)" docstring refs
         lost their provenance (the fact kept, the D-ref out). DOCSTRINGS (D-318, 7 functions): the class "Represents
         ..." -> "Holds the 2D index matrix together with the hash signature ..." (the phrase kept verbatim — the probe
         A9 pin rides on it); __init__ "Initializes a LMIndexes" + the numpydoc Parameters (the indexes description was
         EMPTY) -> Google Args (the description written: "the 2D (M, P) uint32 design-matrix index array (each cell is a
         weight index)"); compute_sha3_256_hash gained its docstring (it was the only undocumented public function);
         __repr__ "A concise one-line summary." -> imperative; store/load "Saves/Loads a LMIndexes" -> imperative
         "Save/Load the LMIndexes instance" + Args + Returns (the sidecar note kept, reflowed so the probe A8 phrase
         "the SHA3-256 sidecar is written by the binio writer" stays on one line); hlp_indexes_compute "Computes model
         indexes." one-liner -> full form (Args + Returns); is_cache_consistent (already imperative) + Args + Returns.
         The "a LMIndexes" grammar fixed x2. SIDE FILES (option c, user-directed): the GNU header trailing spaces on
         wrk_indexes.py (4) + test_hlp_indexes.py (4) + test_wrk_indexes.py (4); the test_wrk_indexes.py L146
         assertNotIn (123 chars) reflowed — the only >120 line in the whole zone. No test docstrings, no worker
         docstrings touched (the files' behaviour + content otherwise verbatim). ZERO BEHAVIORAL CHANGE: the
         docstring-stripped AST equality proof (pre from git HEAD vs the new file, structural dump) = identical. No
         config / no cache-format / no golden impact (the docstrings do not serialize; the rlmwf_05_INDEXES.dat bytes
         are unchanged). PROBES (verify_hlp_indexes.py, 52 checks): the minimal re-pin — A1 (197 -> 228 lines, the
         label), A8 (the pinned D-139 sentence -> the plain one), E1 (154 -> 155 test lines). Everything else stayed
         green BY CONSTRUCTION: the rewrite was written around the pinned substrings (A4 the no-validation comment
         adjacency, A5 the write order, A6 the 3 RuntimeError messages, A7 the 2 compare fragments, A9 the "together
         with the hash signature" phrase, A10 the 0 trailing ws, the 5 @validate_call). MIRROR: hlp_indexes.md (228
         lines, the drifting ordinals out as in D-325 — "5th active level / the THIRD cache_manager consumer / 5th LM
         level / at step 6" -> the level name); the 3 test mirrors needed no sync (no count refs). VERIFICATION:
         test_hlp_indexes 14/0/0 (no DB) + verify_hlp_indexes 0 mismatches (the B tier pure + the C tier live-DB
         pipeline) + the full pre-commit LONG=1 suite + the docs/notes audit.

D-327 | 2026-09-28 | the new code-format rules on hlp_optimize (the D-314 reflow + the D-318 docstrings) + option (c):
         wrk_optimize.py (header + the 2 >120 lines + the 4 D-096 comment tags) + both test-file headers Roberto:
         "Applica le nuove regole di formattazione del codice a hlp_optimize. Per favore sviluppa una analisi
         dettagliata, la valutiamo insieme, ti dico poi come procedere." -> "Procedi con opzione (c), grazie!" FORMAT:
         the D-323/D-324/D-325/D-326 pattern. The header GNU trailing spaces cleaned; the 2 >120 lines (L210/L214, both
         log_event — the RUNTIME STRINGS verbatim, only the call reflowed); the 5 D-XXX refs out (the 2x "LZ4 ...
         (D-139, as in model_weights)" docstring sentences, the "(D-096 R3)", the "(D-096 R1: ...)" — the design fact
         kept, the tag out — and the code comment "# M6 (D-096): the file stores a single length prefix plus one"
         de-tagged, the fact kept). DOCSTRINGS (D-318, 6 functions): save_optimization_checkpoint "Saves ..." ->
         imperative + the LZ4 line + the 17-arg Args block (the largest docstring growth of the campaign — the function
         has the most parameters of the pipeline); load "Loads ..." -> imperative + the body (the header + sidecar
         facts, "for this (D-096 R3)" -> "for this") + Args + Returns (the 15 keys); is_optimization_cache_consistent
         (already imperative) — the 3-gate body kept, the D-096 R1 tag out of the ridge gate, + Args + Returns;
         optimization_info_dict "Filters" -> "Filter" + Args + Returns (the 5 context keys);
         is_optimization_status_converged — the body KEPT VERBATIM (the probe-A16 phrase "judgement criterion, not part
         of the objective" rides on it) + Args + Returns; weights_compute_sha3_256_hash documented (it was the only
         undocumented function). SIDE FILES (option c, user-directed): wrk_optimize.py — the header + the 2 >120
         log_event lines (L73/L84, the strings verbatim) + the 4 D-096 comment tags (R2/M2/M5/R4 — the facts kept, the
         probe-B10 "unreachable: iters is an int" phrase untouched); test_hlp_optimize.py + test_wrk_optimize.py headers
         (the 8 "# " lines; 0 D-xxx, 0 >120 in the test files — nothing else to do there). ZERO BEHAVIORAL CHANGE: the
         docstring-stripped AST equality proof on BOTH files (pre from git vs the new, structural dump) = identical. No
         config / no checkpoint format / no log string touched (the golden cascade stays zero, as in D-325/D-326).
         PROBES (verify_optimize.py, 78 checks): the re-pin — A1 (271 -> 327), A14 (the two no-validation comment line
         indices al[176]/al[233] -> al[203]/ al[276], the D-318 growth above them), B1 (190 -> 192, the 2 reflows).
         Everything else stayed green BY CONSTRUCTION: the rewrite was written around the pinned substrings (A6 the
         module comment at al[55]/al[56] — the triple-blank house spacing had to be restored, the first probe run caught
         it; A9 the "Serialize the L-BFGS history vectors chronologically:" comment; A10 the fail-fast check + the
         ValueError message; A16 the phrase; A19 the kept "# Read header properly!"). 78/0 incl. the H tier (the live
         pipeline through OPTIMIZE, the real L-BFGS runs). MIRRORS: hlp_optimize.md (327 lines, the "11th active level
         (CREATED sentinel -> ...)" ordinal -> "the OPTIMIZE level (after GRADIENT)"; FOUND: the "83-check probe" claim
         was STALE since the D-106 class-c probe slimming — corrected to 78); wrk_optimize.md (192-line file).
         VERIFICATION: test_hlp_optimize 20/0/0 (no DB) + verify_optimize 78/0 + the full pre-commit LONG=1 967 OK (24
         skipped) + the docs/notes audit at baseline.

D-328 | 2026-09-28 | the new code-format rules on hlp_plot (the header + the ~20 D-XXX comment tags + the full D-318
         docstrings on all 15 defs) + the FEATURE: the 11 hardcoded rendering constants AND the _TXT_X/_TXT_Y label
         dicts move into the config as the 13 PlotStyle knobs Roberto: "Applica le nuove regole di formattazione del
         codice a hlp_plot." + "Verifichiamo anche la opzione di portare nel config i parametri HARDCODED: _BINNED_NOTE,
         _JITTER_SEED=42, _KDE_SEED=43, _KDE_MAX_POINTS=100_000, _JIT_FITTED_X=0.005, _JIT_Y=0.005, _JIT_GV_X=0.7,
         _KDE_GRID=512, _AXIS_GV=64.0, _AXIS_DENSITY=72.0, _TICK_STEP=8.0 — Magari tenendo questi come default ... cosa
         ne pensi ?" -> "Facciamo b, e mettiamo anche _TXT_X e _TXT_Y nel config, con il nome corretto, di cosa siano.
         Procedi!" FORMAT: the D-323..D-327 pattern. hlp_plot.py 504 -> 556 lines (the D-314 reflow to the 120-char
         width on the code + the docstrings + the comments — applied on Roberto's catch, the first commit had shipped
         the old line-wrapping — and the orphaned `#:` constants comment block REMOVED, the 11 values now config fields,
         the design facts consolidated in the PlotStyle docstring); the 4 header trailing spaces cleaned; the D-XXX tags
         out of the header block (D-149/D-148 + the "R script is a scratch artifact slated for deletion" aside) and of
         the ~20 per-plot comments (D-150 x8, D-151 x2, D-153, D-155) with the design facts KEPT (the fixed-axes ruling,
         the stale-boxplot-label bug, the box-placement fractions); the 2 Italian quotes in the plot-5 comment
         paraphrased in English (rule 4); the "(the R p0/p1/p2 ...)" docstring provenance out; _series_label got a
         docstring; the full D-318 form (imperative first line + typed Args/Returns) on all 15 defs. wrk_plot.py 121 ->
         130 (header + the 3 D-149 tags + the "18th/10th" ordinals + the style-construction comment, packed to the 120
         width). The 2 test-file headers cleaned. FEATURE: PlotConfig +13 fields (the keep-it-simple
         descriptions, D-324): binned_note (the _BINNED_NOTE str), jitter_seed 42 ge=0, kde_seed 43 ge=0, kde_max_points
         100_000 ge=1, jitter_fitted_x 0.005 ge=0, jitter_y 0.005 ge=0, jitter_gv_x 0.7 ge=0, kde_grid 512 ge=2,
         axis_gv 64.0 gt=0, axis_density 72.0 gt=0, tick_step 8.0 gt=0, series_label_x / series_label_y (Dict[str,
         float] — the _TXT_X/_TXT_Y RENAMED to what they are: the plot-1 series-label placement, x a fraction of the
         axis span from the left, y a fraction of the curve maximum). The PlotStyle dataclass lives in hlp_plot (the
         schema CANNOT import back: hlp_config_schemas imports PLOT_NAMES from hlp_plot — the circular direction); the
         11 module constants + the 2 label dicts are gone (the PlotStyle defaults carry them, field(default_factory) for
         the two dicts); the builders take (d, run_name, style); _kde_curve takes the style (the subsample seed + cap);
         wrk_plot assembles the PlotStyle from ctx.cfg.plot (the label dicts COPIED, so the schema's instances stay
         owned by it) at the single dispatch point; PLOT_BUILDERS retyped Callable[[PlotData, str, PlotStyle], Figure].
         plot_parity now consumes axis_gv (it hardcoded the 64.0 literal — the one consistency fix; at the default the
         rendering is unchanged). Fixtures UNTOUCHED (the 13 defaults travel in the dump; 11 fields x 4 fixtures was
         noise — unlike the single D-325 hi_perf_blocks, Roberto let the defaults stand). ZERO BEHAVIORAL CHANGE (at the
         defaults): the AST code-equivalence proof (the function bodies docstring-stripped, the 13 constant -> style.X
         renames applied, git HEAD pre-version vs the new one): IDENTICAL except the intended style plumbing (the
         _kde_curve third arg, the 3 explicit style.tick_step calls, the 6 parity literals -> axis_gv). The
         test_wrk_plot parity PNG golden (the pinned sha3) passes byte-identical. CASCADE: the config checksum -> the
         report "Config SHA3-256" line is MASKED (the D-325 lesson) -> no report-golden re-derivation; the plot PNGs
         have NO hash pins (existence + magic + log only) -> byte-identical at the defaults; the v2 model file GROWS
         with the 13 dump fields: A2030 measured 23562 B (band 23183-23283 -> 23512-23612), A2050 measured 517041 B
         (band 516692-516892 -> 516991-517091) — re-centered in test_lm_worker_full_chain + the verify_save explanatory
         comments (the D-149 band precedent). TESTS: test_hlp_config_schemas +1 (the 13 defaults + 6 degenerate
         rejections; 29 -> 30); test_hlp_plot the 2 _kde_curve call sites + PlotStyle() (the 11 tests otherwise
         untouched); test_wrk_plot the 13 stand-in attributes on the SimpleNamespace plot section. Suite 967 -> 968.
         PROBES: verify_plot 17 -> 19 checks (the 3 builder + 1 _kde_curve call sites + PlotStyle; the new C7 pins the
         13 defaults); no line-count pins to re-align (this probe never had any). MIRRORS: hlp_plot.md kept at 121 (the
         pre-existing size finding — +1 the PlotStyle API row, -1 the _fig mathtext clause, the "18th level" ordinal
         named, the "18-check" probe count -> 19); wrk_plot.md (the flow: the PlotStyle step + the 3-arg dispatch, the
         import surface, the ordinal); hlp_config_schemas.md API row (the 13 knobs, at 122 = the pre-existing size
         finding kept); test_hlp_config_schemas.md (29 -> 30 + the new test row). VERIFICATION: verify_plot 19/0 +
         test_hlp_plot 11/0 + test_hlp_config_schemas 30/0 + test_wrk_plot 9/0 (the parity golden) + verify_save ALL
         PASS + the full pre-commit LONG=1 968 OK (24 skipped) + VLONG A2050 on the new band + the docs/notes audit at
         baseline. CLEANUP (Roberto's second catch, follow-up commit): a blank line after the license (the '#'-'#' pair
         out); the header's "ported from the R rglm workflow" block REMOVED (history); the A2050 scale reference out of
         the PlotStyle docstring (the subsample rationale kept, now "at the full training-set scale"); the '# --- The
         seven figure builders' banner REMOVED (the builders' docstrings already say it); the redundant FIXED-axes
         inline comments (plots 1-4) + the no-legend comment REMOVED (the PlotStyle docstring carries the ruling) — the
         two UNIQUE ones kept (plot 4 the stale-boxplot-label API quirk, plot 5/7 the data-driven-axis rationale).
         hlp_plot.py 556 -> 537 lines, wrk_plot.py the license blank line; AST code diff: NONE (comments/docstrings
         only), the parity golden byte-identical, 968 OK again.

D-329 | 2026-09-28 | the new code-format rules on hlp_su_analysis (the D-314 reflow + the full D-318 docstrings on all
         32 functions + the 2 section banners out) + the approved extras: the dead import out + the report typo fixed
         Roberto: "Modulo hlp_su_analysis, verifica la lunghezza delle righe, non sono conformi alle regole, sono troppo
         corte. Fai una verifica dettagliata, proponi le opzioni, poi ti do indicazione su come procedere." -> the
         detailed analysis (max width 87, the ~72-76 wrap, 1190 lines; all 32 function docstrings pre-D-318 style — the
         descriptive first lines, the 2-space untyped Args, the 8 'State:' sections — plus _read_marginal WITHOUT a
         docstring; the 2 redundant section banners; the 13 '#:' rationale blocks NOT orphaned (the constants stay in
         the file — unlike D-328) so kept; the 3 allowed design pointers (D-293 x2, D-296); the dead `import hashlib`;
         the 'Uncertainity' typo in 2 report strings + 3 test pins) -> "Ok con (c). Procedi per favore!" (the full pass
         + the extras). FORMAT PASS: the D-314 reflow to ~115 (the code 587 -> 560 lines, the comment blocks 143 -> 97:
         the 2 banners out, the redundant inline parts merged into the docstrings, packed) + the D-318 conversion of all
         32 functions (the imperative first line, the body, the Google typed Args/Returns; the 8 'State:' sections
         dissolved into the body; _read_marginal gained its first docstring) — the docstring lines 374 -> 457 (the
         typed-Args cost), the file 1190 -> 1203 lines. The 13 '#:' blocks KEPT (packed only). EXTRAS (option c):
         `import hashlib` REMOVED (imported, never used); the report's "Symmetrical Uncertainity Analysis Report" ->
         "Symmetrical Uncertainty Analysis Report" + "Section C: Symmetrical uncertainity" -> "...uncertainty" (the
         user-visible TXT report strings) + the 3 test_hlp_su_analysis assertIn pins updated. Every other report string
         byte-identical. ZERO BEHAVIORAL CHANGE (beyond the typo strings): the AST code-equivalence proof
         (docstring-stripped, git HEAD pre-version vs the new one): IDENTICAL except the removed hashlib import + the 2
         typo strings; all 10 module constants byte-identical (the _SU_DESCRIPTION / _SU_LEGEND / _KPI_LEGEND report
         strings verified via literal_eval). VERIFICATION: test_hlp_su_analysis 38/0/0 (1.9 s) + verify_su_analysis 0
         mismatch + the full pre-commit LONG=1 968 OK (24 skipped) + the docs/notes audit at baseline. MIRRORS:
         hlp_su_analysis.md UNTOUCHED (no API / architecture / convention change — the format pass is a
         decisions/journal matter, the doc stays accurate at its 121 pre-existing baseline) — the test mirror likewise
         (the 3 pinned strings are not quoted there). OVERVIEW: the hlp_su_analysis row's stale 21/0/0 count corrected
         to 38/0/0 (the D-295 migration era). OBSERVATION (out of scope, for Roberto): test_hlp_su_analysis.py still
         carries a D-292 comment reference (the Section B bins, ~line 339) against D-267 (no D-xxx in test docs) —
         pre-existing, left as-is (the approved scope (c) covered the 3 strings only). FIX (Roberto's catch, follow-up
         commit): the 3 D-292 references REMOVED from test_hlp_su_analysis.py (the Section B bins comment, the
         section-off comment, the TestNeverObservedAudit docstring — the other D-refs stay: only the D-292 ones were
         asked); the module docstring REMOVED (the campaign modules carry none — the purpose lives in the mirror doc);
         the premature code line-breaks packed (the ~30 multi-line statements that fit in 120 collapsed to one line —
         the with binio.BinaryWriter, the writerow, the log_event, the dict returns, the comprehensions — the too-long
         ones re-balanced to 2-3 lines): 1203 -> 1161 lines, max width 119. AST code diff vs the D-329 commit: IDENTICAL
         (docstring-stripped — pure formatting), the 38 tests + the probe + the LONG=1 968 OK again.

D-330 | 2026-09-28 | the new code-format rules on hlp_validate (the D-314 reflow + the D-318 docstrings — the campaign's
         worst offender: the 55-line essay docstring condensed to the WHAT + the interpretive essay moved to the mirror
         doc) + the extras: the Dict -> dict modernization + the header cleanup Roberto: "Modulo hlp_validate, verifica
         la lunghezza delle righe, non sono conformi alle regole, sono troppo corte. Fai una verifica dettagliata,
         proponi le opzioni, poi ti do indicazione su come procedere." -> the detailed analysis (max width 94, the
         ~72-90 wrap, 193 lines; validate_model's docstring = the 55-line "Validation Metrics for Logistic Curve
         Fitting" essay with the "Physical Interpretation" / "Mathematical Weight" / "Why it matters" bullets — the
         conversational register, the 3rd-person first line, no Args/Returns; top_outliers descriptive, no Args;
         ValidationResult the bare field lines instead of the PlotData inline-comment pattern; the 4 license
         trailing-space lines; the 3 triple-blank runs; the "We need the column offsets" narrative comment; the
         old-style Dict[str, Any]) -> "prosegui con (c). Grazie!" (the full pass + the extras). FORMAT PASS: the D-314
         reflow to ~115 (193 -> 158 lines) + the D-318 conversion: validate_model the imperative first line + the
         WHAT-only body (the Z-space context + the 3 formulas + the RMSE/MAE = sqrt(pi/2) normal indicator — the 55-line
         interpretive essay CONDENSED out, its essence — the 4% scale reading, the linear-error baseline, the 0.1/0.01
         vs 0.5/0.25 penalty, the logistic-tails alarm — MOVED to the mirror doc's Architecture bullet, its legitimate
         home) + the Args/Returns; top_outliers imperative + Args; ValidationResult the short docstring + the 3 inline
         field comments (the PlotData pattern). The 4 license trailing-space lines cleaned, the 3 triple-blank runs ->
         2, the "We need" comment out, the 2 contract comments (the f32 goldens / the f64 bit-identical series) kept
         packed. EXTRAS: Dict -> dict on the ValidationResult.metrics annotation (inert at runtime under the
         future-annotations import; the probe A5 is a disjunction and passes either way) + the Dict import out. ZERO
         BEHAVIORAL CHANGE: the AST code diff (docstring-stripped) is exactly the 2 intended changes (the typing import,
         the annotation) — nothing else. VERIFICATION: test_wrk_validate 9/0/0 (the 3 DB-gated skipped at the fast tier)
         + verify_validate 18/18 (the A pins — the exact __all__ line, the underscore unpack, the 7 keys — all intact;
         no docstring pins) + the full pre-commit LONG=1 968 OK (24 skipped) + the docs/notes audit at baseline.
         MIRRORS: hlp_validate.md (76 -> 83 lines, in budget) — the Architecture bullet now carries the condensed
         interpretive content.

D-331 | 2026-09-28 | the new code-format rules on hlp_wmaps (the D-314 reflow + the full D-318 docstrings + the 3
         decision refs out) + the verify_wmaps probe re-pin (the campaign's most fragile probe: the line-count +
         line-number + docstring-substring pins) Roberto: "Modulo hlp_wmaps, verifica la lunghezza delle righe, che
         siano conformi alle regole, non siano troppo corte. Verifica che le docstring ed i commenti siano conformi alle
         regole, e non abbiano riferimenti alla storia o alle decisioni." -> the detailed analysis (max width 130, 322
         lines; 3 decision refs: the 2x "LZ4 whole-file compression by default (D-139, as in model_weights)" docstring
         lines + the "never -1 — D-086 R1" compute-docstring tag; the compute docstring = the 12-step HOW list (the
         mirror's Architecture bullet already carries the mechanism); the 3rd-person first lines on the 4 public
         functions; __init__ + compute_sha3_256_hash WITHOUT docstrings; the 41-line numpy-style Attributes block; the 3
         narrative comments; the 4 license trailing-space lines; the probe pins the line count (A1), 4 line numbers
         (A5/A10/A11/A12) and 2 docstring substrings that CONTAIN the decision refs (A7/A8)) -> "Prosegui con (c),
         grazie!" (the full pass + the extras). FORMAT PASS: the D-314 reflow to ~115 (322 -> 340 lines — the code
         shrinks, the 8 D-318 docstrings — the 2 NEW ones included — grow) + the D-318 conversion: the 6 function
         docstrings imperative (Save / Load / Compute / Check / Initialize / Compute), the 12-step HOW list CONDENSED to
         the WHAT (the dense contract + the cut-off/fallback semantics + the zero-init — the step mechanism stays in the
         mirror's Architecture bullet), the Args/Returns (+ Raises on load); the LMWMaps Attributes numpy section
         flattened to the plain field list + packed; the 3 narrative comments out; the 4 license trailing-space lines
         cleaned; the __all__ packed (the A3 substrings intact); the 3 decision refs REMOVED (the facts stay: "LZ4
         whole-file compression by default", "the indexes are unsigned and never -1" — the mirror's Conventions bullet
         already states both WITHOUT the tags). PROBE RE-PIN (minimal, the D-327 precedent): A1 322 -> 340; A5 / A10 /
         A11 / A12 the 4 line numbers (L208 / L298 / L311 / L275); A7 the substring without "— D-086 R1"; A8 the new
         imperative first line + the compression line without "(D-139, as in model_weights)". C1 (the test at 346) + B9
         untouched (the test file is NOT modified — zero behavioral change). ZERO BEHAVIORAL CHANGE: the AST code diff
         (docstring-stripped) IDENTICAL — docstrings / comments / reflow only. VERIFICATION: test_hlp_wmaps 15/0/0 +
         verify_wmaps 53/53 (the re-pinned A1-A12 + the B / C / D sections) + the full pre-commit LONG=1 968 OK (24
         skipped) + the docs/notes audit at baseline. MIRRORS: hlp_wmaps.md (82 lines, in budget) — the "module 322
         lines" pin line -> 340 + the format-pass note. OBSERVATION (out of scope, for Roberto): 2 dead assignments in
         hlp_wmaps_compute — N = pindexes.shape[0] (L225-era, never used) + stats_filtered_above = stats[~mask] (never
         used) — left as-is (the approved (c) scope did not include code removal). FIX (Roberto's approval, follow-up
         commit): the 2 dead assignments REMOVED from hlp_wmaps_compute (N = pindexes.shape[0], the stats_filtered_above
         = stats[~mask] — the stats_filtered_below twin kept, it is used) — 340 -> 338 lines; the probe re-pinned again
         (A1 338, A10/A11/A12 the shifted line numbers — A5 unchanged, the note is before the deletions); the mirror's
         pin line -> 338 (+ the catch of the "341" I wrote instead of 340 in the first mirror update). The AST diff of
         the fix: exactly the 2 Assign removals in hlp_wmaps_compute, nothing else. test_hlp_wmaps 15/0/0 + verify_wmaps
         53/53 + the LONG=1 968 OK again.

D-332 | 2026-09-29 | I-014 closed as DROPPED (the OPTIMIZE hot-restart from the checkpoint's warm weights under a
         changed `ridge_regularization` objective): Roberto has no intention of pursuing it. No code action: the entry
         moves from notes/ideas.md to notes/ideas-closed.md, compacted to statement + this pointer (the D-235 format),
         and the overview Next-steps backlog line updated in the same commit. The warm-start plumbing (the checkpoint's
         full L-BFGS state — w + sl/yl/rho + iters — + the `opt_lbfgs` warm-start kwargs, consumed on the INCOMPLETE
         resume path) is untouched and stays as the checkpoint contract.
