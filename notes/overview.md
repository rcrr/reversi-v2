# overview.md — entry point

## Format rules (rigid — follow when editing this file)

The rigid format rules for this file live in notes/rules.md — the "Roles of the notes files" section, the
notes/overview.md bullet. Consult it before editing.

## Project

This workspace is dedicated to the research and development of evaluation functions for Reversi positions. The methods
employed focus on machine learning techniques that leverage solved positions generated from random gameplay paths.

## Conventions in the code (respect them in any new work)

- Board vocabulary is canonical: **row** (1–8, top→bottom) and **column** (A–H, left→right) — never file/rank (chess).
  A1 = top-left (N-W) = bit 0; H8 = bottom-right (S-E) = bit 63. row_1 = [A1..H1]; column_a = [A1..A8]. Full text:
  notes/naming.md (D-013).
- Dual scalar/array API: public functions accept scalar OR 1-D array, return the input kind. Same validation pattern
  everywhere (is_scalar → atleast_1d → ndim check → dispatch → reshape back).
- `@validate_call` (pydantic, arbitrary_types_allowed) on all public functions.
- Numba `njit(cache=True)` + `prange` for hot loops; numba overloads for the four D8 primitives (fa1h8, fh1a8, fhori,
  fvert).
- Position = numpy structured dtype `[('mover', u64), ('opponent', u64)]`.
- Move codes: 0..63 = squares, 64 = PA (pass), 65 = NA, 66 = UN.
- D8 slot order is fixed and load-bearing (D-014): anti-transform slot s = T_s^{-1}; in pattern.py instance 0 = the
  ro000 image, and trans_fs/anti_trans_fs are indexed by instance (length = n_instances), not by slot.
- Pattern config indexes are base-3 uint32 over ≤ 18 squares (S ≤ 18); packed bit k ↔ the k-th square of
  `Pattern.squares` (ascending board order); principal index = min over the induced-stabilizer orbit.
- Test artifacts (D-065): unit tests write files ONLY under `workspace_root/build/tmp` and remove them afterwards (a
  `finally`/cleanup unlink, so a failing test leaves no garbage); no test writes anywhere else (notably: not the CWD).
  `build/` is gitignored.


## Environment

- Venv: `.venv/` (gitignored, D-010), Python 3.12.3.
- Packaging: `pyproject.toml` (setuptools, src layout) with the `reversi` package installed editable in .venv —
  `import reversi` works without PYTHONPATH, resolving to src/.
- Dependencies (pyproject.toml, minimal set): numpy ≥ 2.0 (bitboards / structured dtypes), pydantic ≥ 2
  (@validate_call), numba ≥ 0.60 (njit / prange / overload; pulls llvmlite), lz4 (binio), psycopg2 / pandas /
  python-dotenv (regab).
- Test command: `./run_utests.sh` (the canonical runner; tiers: default fast ~5 s, LONG=1, VLONG=1 ~10 min incl. the
  A2050 chain and implies LONG; PERF=1 adds the print-only perf tests). The standard pre-commit run is
  `LONG=1 ./run_utests.sh`; VLONG=1 only when useful. A single module:
  `.venv/bin/python -m unittest test.reversi[.zone].<module>` (the zones: lm, tools). The DB-gated suites
(test_regab + the worker suites) need a live
  PostgreSQL + .env + LONG=1, or `SKIP_REGAB_DB=1` to skip the DB tests. The runner is unittest by design (pytest is not
  a dependency).
- Probes: tracked under probes/ (hub: verify_logistic_model.py owns the pipeline-wide state; rules:
  notes/probe_rules.md).

## Where we are

Current state only — the session-by-session history lives in the journal volumes (notes/log_NNN.md) and the decision log
(notes/decisions.md); the D-pointers index that history. The file-by-file state lives in the Source files / Test files
tables at the end of this file.

- The 18-level pipeline is live and green (958 tests, LONG; the 1e6 wave benchmark — VVLONG since D-256 — replays
  bit-exact, 28065 dead lanes): the ML chain CONFIG → … → SAVE → CLIENT_CHECK → PLOT, plus the OPTIONAL SU_ANALYSIS
  (pipeline step 3) + ANOVA (pipeline step 6) — default FALSE, opt-in.
- The ANALYTICS file report carries the D-307 SU sample columns: the PROBABILITY / SU_PROBABILITY observation shares
  (after FREQUENCY, the pooled marginal over the feature's instance columns) + the "SU Sample Consistency" line under
  Eta-Squared (the pooled adherence — the TV verdict bands 0.01/0.05 + the chi-square / p / merged; the 2x-training
  too-small note). SU off → byte-identical tables (the rlm_01/rlm_02 goldens survived).
- The ANALYTICS file report carries the D-308 INTERCEPT section: the single trained bias weight (one Weight line,
  4 decimals), emitted only when the feature set has an intercept, between the FEATURE SET SUMMARY and the MOBILITY
  details. No-intercept fixtures (rlm_02) stay byte-identical; the intercept fixtures' goldens (rlm_01 / rlm_04 /
  rlm_03) were re-derived.
- The EFFECT_SIZE level is renamed ANOVA (D-309): the worker (wrk_anova.py), the config (AnovaConfig, the `anova`
  key), the test, the probe, the 2 mirrors. BREAKING: the config key `effect_size` → `anova` — a pre-rename config
  with `effect_size:` is ignored by pydantic (the level silently disables); external configs must migrate to `anova:`
  (the backward-compat alias: REJECTED — the clean break, no alias).
- The ANOVA worker is a thin orchestrator (D-310): the enable no-op stays in `_up`, the computation lives in two
  private helpers (`_compute_anova_lines` — the eta²/omega² per sub-variable; `_compute_adherence_lines` — the
  adherence trio, the graceful-degradation None branch) + the existing `_write_report`; the D-309 leftover local
  `cfg_es` is renamed `cfg_anova`. Zero behavioral change (the log sequence + the probe pins are verbatim).
- The ANALYTICS eta² is now the shared ANOVA kernel (D-311): the pooled "Eta-Squared (Discrimination)" statistic of
  both feature tables is the `anova_eta_omega` call (the 2 hand-rolled SS blocks removed — the bincount pass stays
  for the table columns), and `TestEtaSquaredCrossLevel` (DB-gated, rlm_00) pins the cross-level invariant: on the
  single-instance features (ALMC / LMC / DLMC) the ANALYTICS eta² == the ANOVA level's eta² (the groupings coincide).
- The wrk_su_analysis module docstring is REMOVED (D-312, the house de-history style, the D-306 precedent): it cited
  decisions (D-289 / D-288 / D-060), described hlp internals (the binio flow, the consistency signature) and the
  state-machine re-raise — none of it is in the worker (7 of the 10 sibling workers have no module docstring). The
  mirror doc intro is re-synced (module-accurate; the D-pointers stay in the mirror, their home).
- The wrk_anova module docstring is REMOVED (D-313, the D-312 precedent): the same disease, milder — one D-XXX (the
  "D-060 semantics" pointer) + the two kernels misattributed to the module (they live in hlp_feature_analysis, shared
  since D-311). The mirror doc needed no change (its intro is already module-accurate and states the down fact — the
  no-op, nothing published).
- The pipeline STOP is target-driven (D-260): the facade's `run(target_level=None)` runs CONFIG first and then stops at
  the explicit argument, else at `cfg.target_level`, else at the last step — any level name (case-insensitive) or index
  is a legal stop; a second `run()` with a deeper target RESUMES (no reset, the caches hot).
- The SU/ANOVA verification posts run the REAL pipeline (D-287): the worker suites + the two probes take the
  campaign (cfg + feature_set + the `feature_blocks` layout) from the facade's `run("FEATURES")` (the target_level
  stop + the `base_dir_override`, silent) — the hlp_gate parallel loader is RETIRED (the test-infra no longer ships
  in the package).
- The wrk/hlp split (D-289): the SU_ANALYSIS worker is the ORCHESTRATION SKELETON (the wrk_design_matrix
  minimalism) — all the analysis logic (the corpus engine, the binio cache D-288, the signature, the
  statistics) lives in hlp_su_analysis, with a dedicated test_hlp_su_analysis suite (38 tests —
  the D-295 accumulator migration).
- The LM facade is the pipeline's script entry (D-274): `python -m reversi.lm.logistic_model <config.json>
  [--verbosity {high,moderate,standard,low,very_low,none}]` (default `standard`), from the workspace root — runs the
  whole chain to the last level.
- The SU_ANALYSIS report (D-275/D-278/D-279, D-292) is the up-to-three-section "Symmetrical Uncertainity Analysis
  Report": a header (the title + the corpus / features / SU-pairs summary),
  Section A (the feature-instances — the per-sub-variable dispersion + the never-observed audit, over the THEORETICAL
  configuration space: n_unique_configs for a pattern / the value range for a mobility, D-278; some are unreachable
  by the game, D-279; a compact KPI legend above the list) + the optional Section B (the Rarity report — the
  per-bin frequencies over the half-open bins [0, t1), [t1, t2), ..., [tk, inf), the first bin the zero-frequency
  codes; the config's optional rarity_thresholds, D-292) + Section C (the SU groups — each pair DEDUPLICATED, the
  SU being symmetric so the (i, j) / (j, i) directions are shown once, the groups in the canonical endpoint order
  (the lexicographic instance order); the preamble is the report description + the SU-range legend,
  the D-293 follow-up) — the data rows are COLUMN-ALIGNED (D-293: the name / the inst left-justified
  to the max width, the numeric values right-justified to the computed max width; the Section C preamble is the
  header description + the SU-range legend, moved after its title; the Section B preamble runs at column 0, no
  parentheses).
- The ec (empty_count) is consolidated in ONE required root field (D-280..D-283): `empty_count` (int, 0..60) between
  name and description — the single source for the SU corpus generation, the DB extraction (training + validation),
  and the saved model. The redundant `su_analysis.corpus.ec` + `regab_data_set.ec` are gone; the migration was
  value-preserving (the caches, the corpus signature, and the model file keep the ec value — nothing regenerated).
- A PASS (move 0 in board.position_flips, PA = 64 in position_make_move) returns the position with the players inverted
  (the next player's view) — the position_flips scalar + array kernels swap on a zero move.
- the SU_ANALYSIS corpus generator is the random_game play-path engine (the su-corpus-3 lineage, D-284) — the hlp_wave
  wave engine is RETIRED (module + suite + mirrors removed, D-285); the model file is self-describing (format v2, the
  config provenance embedded; the backward-compat v1 reader).
- random_game (the new module): random_game_choose_move (the uniform PRNG pick) + random_game_make_move (pick a move,
  apply it via position_flips, return the resulting position + the move) + random_game_play_path (play random moves
  until the empty count reaches the target; the batch engine is the SU_ANALYSIS production corpus engine, the
  su-corpus-3 lineage, D-284). The standard start is board.initial_game_position (the CANONICAL source of the official
  Othello setup).
- The PRNG (tools/prng.py) is MINIMAL and fully numba: one class (MT19937), a seed ctor, one numba kernel (the constants
  local, the state fully internal); the class is the sole interface (get_uint64 / get_uint64_batch).
- The SU-analysis corpus is REGENERATED (D-254): the generator version bumped (`su-corpus-2`) and the 1e7 corpus on the
  A2050 feature set re-run on the official start (92.7 s: 67.2 the corpus + the SU statistics, 25.5 the ANOVA; the
  reports in `build/su_corpus_1e7/`). The pre-D-192 corpora (the swapped start) are dead — the cache signature now
  invalidates them automatically. The 2e6/1e8 experiment configs regenerate on demand.
- The mirror docs are fully consistent with the code (D-262 sweep + the D-263 execution of ALL its remaining
  findings): the independent 95-pair re-audit drove the fix campaign — the critical facts (the regab SQL
  contract, the pattern API, the FOUR analytics attributes), the 7 space-broken goldens, the tools/ zone, the
  step/level drift, the test-doc pins, the forbidden history, and the source-side stale comments (comment-only).

## Next steps

- The VVLONG tier is UNINSTRUMENTED since the wave retirement (D-285) and KEPT (D-286): the `tier_vvlong` predicate +
  the runner header stay in place (the machinery survives for a future very-long instrument).
- The last PRNG transformation passettino (the ctor's init over a numba init kernel) — parked, step-by-step.
- The PROFILING session (the OPTIMIZE pattern, the step-by-step walkthrough) — waits.
- Backlog (Roberto's call): I-014 (notes/ideas.md). I-003 executed (D-242); I-018 executed (D-243..D-246); I-019
  executed (D-260); I-009 evaluated & closed (D-264, no code); I-010 evaluated & closed (D-265, no code); I-007
  executed (D-266, the feature_blocks property + the dedup).

## Source files
One row per source file, alphabetical (the package path sorts future packages first). State = a status word + the
open/parked items (if any); the campaign history lives in the decision log. Suite = the current verified suite (live DB)
of the file's test module.

| File | State | Suite (live DB) | Doc |
| --- | --- | --- | --- |
| src/reversi/base_model.py | complete: the thin facade base over StateMachine — the pure delegation + the generic `run(target_level=None)` driver (CONFIG first, then the argument / the `_configured_target_level` hook / the last step; the resume does not reset) | 29/0/0 (via test_logistic_model) | docs/src/reversi/base_model.md |
| src/reversi/board.py | complete: the Reversi game kernel (200 random full games verified on the public API); flips / make_move dual scalar/array; a PASS swaps the players in both position_flips (move 0, a zero bitboard) and position_make_move (`MOVE_PA` = 64, the named move code); the named non-square move codes `MOVE_PA` / `MOVE_NA` / `MOVE_UN` (I-003); initial_game_position (the CANONICAL standard start); position_hash (the legacy-comparable Zobrist hash, D-213); legal_moves_of / flips_of_move (the public njit per-lane primitives — the single sources of the two geometries, D-232); no game-loop module | 246/0/15 | docs/src/reversi/board.md |
| src/reversi/tools/binio.py | complete: the binary IO layer (batch + the empty-suffix fix) | 48/0/0 (45 + 3 usage) | docs/src/reversi/tools/binio.md |
| src/reversi/tools/cache_manager.py | complete: the generic load-or-compute cache pipeline (.SHA3-256 sidecar, 8192-chunk verify) | 22/0/0 | docs/src/reversi/tools/cache_manager.md |
| src/reversi/feature.py | complete: Feature / FeatureSet (blocked __new__, 3 factories, composition, sorted order, the feature_blocks column blocks) | 25/0/1 | docs/src/reversi/feature.md |
| src/reversi/tools/prng.py | complete: the MT-19937 64-bit PRNG — MINIMAL (one class, a seed ctor, one numba kernel with local constants, the state fully internal); choose_one_from_set64 (the uniform no-removal pick, the (0, 64) empty sentinel) + extract_from_set64 — both delegating to the pick kernels; pick_one_from_set64 / pick_one_from_set64_batch (the single source of the pick technique, D-221); get_uint64_batch | 22/0/0 | docs/src/reversi/tools/prng.md |
| src/reversi/lm/wrk_analytics.py | complete: the ANALYTICS level — training metrics + console / file reports; it publishes the dense training residuals `ctx.train_dense_rn` for PLOT (I-018) | 4/0/0 | docs/src/reversi/lm/wrk_analytics.md |
| src/reversi/lm/wrk_client_check.py | complete: the CLIENT_CHECK level — the saved-model file acceptance test (re-read the file, the client's array EF, the Y-space residual comparison vs the PUBLISHED `ctx.vld_rn` series, I-018: no local re-derivation) | 6/0/0 | docs/src/reversi/lm/wrk_client_check.md |
| src/reversi/lm/hlp_plot.py | complete: the PLOT figure builders — the seven Y-space diagnostics (the three R classics + the four extensions), PlotData + `collect_plot_data` (the pure ASSEMBLY of the published series, I-018: no forward pass), the R-semantic jitter, the EGV bins, the guarded KDE; the fixed axes + the step-8 ticks + the two-line title; matplotlib/scipy lazy-imported | 11/0/0 | docs/src/reversi/lm/hlp_plot.md |
| src/reversi/lm/wrk_plot.py | complete: the PLOT level (after CLIENT_CHECK) — the whitelist pilot (enable + the optional plot names), the directory resolution, the per-name save; a PURE rendering level since I-018 (the outlier report to VALIDATE, the forward passes to the owners) | 9/0/0 | docs/src/reversi/lm/wrk_plot.md |
| src/reversi/lm/wrk_config.py | complete: the CONFIG worker — a pure load+validate step (JSON5 → config → base_dir validation) + the config fingerprint (the ad-hoc cache flow removed, the record is a SAVE artifact) | 13/0/0 | docs/src/reversi/lm/wrk_config.md |
| src/reversi/lm/wrk_design_matrix.py | complete: the DESIGN_MTR worker | 3/0/0 | docs/src/reversi/lm/wrk_design_matrix.md |
| src/reversi/lm/wrk_anova.py | the ANOVA worker (step 6) — the eta²/omega² per sub-variable + the adherence (the chi-square + the KL + the TV, DB vs the ideal corpus); the graceful degradation; NO cache (a diagnostic); optional (default FALSE) | 7/0/0 (via test_wrk_anova) | docs/src/reversi/lm/wrk_anova.md |
| src/reversi/lm/wrk_su_analysis.py | the SU_ANALYSIS worker (step 3) — the level ORCHESTRATION SKELETON (D-289, the wrk_design_matrix minimalism): the enable no-op, the cache_manager flow over the hlp binio cache (D-288), the phase-2 statistics recompute (EVERY run), the ctx publication for the ANOVA level; ALL the logic in hlp_su_analysis (the corpus engine su-corpus-5, the signature, the up-to-three-section report (the optional rarity, D-292)); optional (default FALSE) | 10/0/1 (via test_wrk_su_analysis; VLONG: 10/0/0, the 1e7 corpus) | docs/src/reversi/lm/wrk_su_analysis.md |
| src/reversi/lm/wrk_features.py | complete: the FEATURES worker (step 2, before POSITIONS) — the first pure-compute level (no cache file) | 3/0/0 (DB-free) | docs/src/reversi/lm/wrk_features.md |
| src/reversi/lm/wrk_generate.py | complete: the GENERATE level (dense weights materialization) | 3/0/0 | docs/src/reversi/lm/wrk_generate.md |
| src/reversi/lm/wrk_gradient.py | complete: the GRADIENT level (the float32 contract; the high_performance_fg flag wiring) | 4/0/0 | docs/src/reversi/lm/wrk_gradient.md |
| src/reversi/lm/wrk_indexes.py | complete: the INDEXES worker (uniform 7-kwargs cache wiring) | 2/0/0 | docs/src/reversi/lm/wrk_indexes.md |
| src/reversi/lm/wrk_optimize.py | complete: the OPTIMIZE level — the only level whose "cache" is a plain checkpoint dict via binio | 3/0/0 | docs/src/reversi/lm/wrk_optimize.md |
| src/reversi/lm/wrk_positions.py | complete: the POSITIONS worker — the first cache_manager consumer over the regab data set; the extract_and_prepare shared compute path (the duplicate policy) + the cache-hit duplicate line | 12/0/0 | docs/src/reversi/lm/wrk_positions.md |
| src/reversi/lm/wrk_save.py | complete: the SAVE level — the SINGLE artifact: the v2 model file embeds the config provenance | 9/0/1 (via test_lm_worker_full_chain) | docs/src/reversi/lm/wrk_save.md |
| src/reversi/lm/wrk_validate.py | complete: the VALIDATE level (the third non-cache worker) — it publishes `vld_metrics` + the `vld_y_pred` / `vld_rn` series + the 20 `vld_outliers` records and logs the top-20 report (I-018, moved from PLOT) | 9/0/0 | docs/src/reversi/lm/wrk_validate.md |
| src/reversi/lm/wrk_vld_positions.py | complete: the VLD_POSITIONS level (the POSITIONS twin over the validation set); the shared extract_and_prepare reuse + the LOG-ONLY independence trace | 11/0/0 | docs/src/reversi/lm/wrk_vld_positions.md |
| src/reversi/lm/wrk_wmaps.py | complete: the WMAPS worker | 3/0/0 | docs/src/reversi/lm/wrk_wmaps.md |
| src/reversi/lm/wrk_zed.py | complete: the ZED level (the first non-cache level) | 3/0/0 | docs/src/reversi/lm/wrk_zed.md |
| src/reversi/lm/logistic_model.py | complete: the LM facade — LMContext blackboard + the 18-level worker list (FEATURES before POSITIONS; SU_ANALYSIS step 3 + ANOVA step 6) + the `_configured_target_level` hook that feeds `run()` from `cfg.target_level` + the `build_model` script entry (the facade runs as `python -m reversi.lm.logistic_model <config.json>`) | 29/0/0 | docs/src/reversi/lm/logistic_model.md |
| src/reversi/mobility.py | complete: mobility / MobilitySet + popcount64 SWAR kernel (PERF tests print-only, no perf gate) | 26/0/1 | docs/src/reversi/mobility.md |
| src/reversi/lm/model_weights.py | complete: the model_weights @dataclass — the v2 format (the config provenance leads the body) + the backward-compat v1 reader + the 12-field dataclass | 9/0/1 (via test_lm_worker_full_chain) | docs/src/reversi/lm/model_weights.md |
| src/reversi/tools/opt_lbfgs.py | complete: the LBFGS solver (incl. the RuntimeException hard-bug fix); the two-loop O2b (the pre-allocated f64 out= product buffer, bit-identical, 1.39×) | 14/0/0 | docs/src/reversi/tools/opt_lbfgs.md |
| src/reversi/pattern.py | complete: principal mask = numerically lowest orbit; the Burnside attributes; PatternSet.__repr__; the PatternSet Raises docstring | 65/0/3 | docs/src/reversi/pattern.md |
| src/reversi/random_game.py | the random game (the new module): random_game_choose_move (the @validate_call pick: position_legal_moves + the prng pick — choose_one_from_set64 / the pick_one_from_set64_batch kernel, the single source D-221; dual scalar/array with the bit-identical stream contract — D-219) + random_game_make_move (pick a move, apply it via position_flips, return the resulting position + the move; a no-legal-move pass returns the swapped position + PA; dual scalar/array — D-220) + random_game_play_path (play random moves until the empty count reaches the target; the double-pass game-over break fixed — D-218; dual scalar/array, the FUSED two-kernel step engine on the board/prng per-lane primitives — D-232; the SU_ANALYSIS production corpus engine, the su-corpus-3 lineage — D-284) | 33/0/1 (via test_random_game) | docs/src/reversi/random_game.md |
| src/reversi/regab.py | complete: the PostgreSQL regab access layer; the LZ4 default in the 2 rds file functions; the pure helpers regab_dedup_mogv + regab_count_position_overlap | 48/0/0 | docs/src/reversi/regab.md |
| src/reversi/lm/hlp_analytics.py | complete: the ANALYTICS data module (the 3-metric header + Population baseline + dense metrics; the Config SHA3-256 line in the common header block); `compute_training_dense_metrics` returns a `TrainingDenseResult` (the metrics + the f64 `rn_y` series, I-018); the D-307 SU sample columns in the per-feature tables (the PROBABILITY / SU_PROBABILITY observation shares after FREQUENCY, the pooled marginal over the feature's instance columns) + the "SU Sample Consistency" header line under Eta-Squared (the pooled adherence — the TV verdict bands 0.01/0.05 + the chi-square / p / merged; the 2x-training too-small note; SU off = byte-identical tables) + the D-308 INTERCEPT section (the single trained bias weight, one Weight line 4 decimals, only when the feature set has an intercept, before the MOBILITY details) + the D-311 eta² unification (the pooled Eta-Squared statistic is the shared anova_eta_omega kernel call) | 14/0/0 | docs/src/reversi/lm/hlp_analytics.md |
| src/reversi/lm/client.py | complete: the inference client — the scalar EF + the vectorized make_evaluation_function_array (strict array, bit-exact per position, @validate_call on both factories); the in-pipeline consumer (CLIENT_CHECK) | 7/0/1 (test_client) + the EF pins via test_lm_worker_full_chain | docs/src/reversi/lm/client.md |
| src/reversi/lm/hlp_config_schemas.py | complete: the pydantic config domain (the LMConfig JSON5 entry point); the regab_allow_duplicate field (default True); the high_performance_fg flag (default False); the client_check_tol field (default 1e-8, gt=0); the PlotConfig section; the su_analysis + anova + the `target_level` stop (consumed by the facade's `run()`) + the su_pairs fail-fast | 27/0/0 | docs/src/reversi/lm/hlp_config_schemas.md |
| src/reversi/lm/hlp_design_matrix.py | complete: the DESIGN_MTR data module | 14/0/0 | docs/src/reversi/lm/hlp_design_matrix.md |
| src/reversi/lm/hlp_feature_analysis.py | the ANOVA analysis-kernels data module (the D-298 split from the SHARED data plane — the SU family moved to hlp_su_analysis; NO DB, NO positions) — the from-frequency-tables math: the ANOVA kernels (the eta²/omega²) + the adherence kernels (the chi-square + the KL + the TV — the private trio) | 16/0/0 (via test_hlp_feature_analysis) | docs/src/reversi/lm/hlp_feature_analysis.md |
| src/reversi/lm/hlp_generate.py | complete: the GENERATE data module | 16/0/0 | docs/src/reversi/lm/hlp_generate.md |
| src/reversi/lm/hlp_gradient.py | complete: the GRADIENT data module (the float32 contract; the dual fg — classic verbatim + the K3 numba kernel behind the high_performance flag) | 14/0/0 | docs/src/reversi/lm/hlp_gradient.md |
| src/reversi/lm/hlp_indexes.py | complete: the INDEXES data module | 14/0/0 | docs/src/reversi/lm/hlp_indexes.md |
| src/reversi/lm/hlp_optimize.py | complete: the OPTIMIZE data module | 20/0/0 | docs/src/reversi/lm/hlp_optimize.md |
| src/reversi/lm/hlp_su_analysis.py | the SU analysis LOGIC (D-289, the hlp of the SU worker): the frequency accumulators (the marginal + the joint — the D-295 hlp_random_play retirement, now the private _MarginalAccumulator / _JointAccumulator; the D-296 position language: add(idx) over the wave's index matrix at the D-300 loop boundary, no parallel (mover, opponent) at any module boundary; the D-298: the SU statistics kernels (the entropy / MI / SU / dispersion / never-observed audit) moved here as private from hlp_feature_analysis; the D-299 cold-compute optimization: the VECTORIZED joint merge (the per-cell sorted key arrays K/C, the searchsorted + np.add.at fold — no Python dict) + the marginal-entropy memoization in _su_values; the D-300 / I-020: the per-wave index matrix computed ONCE in the compute loop, fed to both accumulators' add(idx); the D-301: the never-observed audit's rarity profile removed (dead in production — the Section B rarity is the _rarity_bins kernel, D-292)) + the corpus generator (the random_game play-path engine, phase 1) + the binio cache I/O (the D-288 layout, the LZ4) + the consistency signature (the feature_set hash, the new cache lineage) + the statistics (phase 2: the dispersion + the never-observed audit + the SU pairs, the up-to-three-section report (the optional Section B rarity, the config's rarity_thresholds, D-292) + the CSV) — NO DB (the corpus is the level's own); the D-302: the COMPLETE signatures (the 46 parameter + the 4 return annotations, the 4 private shape aliases, the idx the IndexArray; inert at runtime); the D-303: the Pydantic boundary — the store / the load are @validate_call-ed, the store DEEP-validates the PUBLIC SuTables TypedDict (the D-292-style tables dict: signature + marginal + joint | None), the 3 ctx functions undecorated (the hlp_design_matrix circular-import idiom); the D-304/D-305 throughput: the 3e6-lane wave (the "su-corpus-5" lineage — the wave size is a generator BEHAVIOUR, it shifts the PRNG stream, so it is versioned; the D-305 5/5 interleaved A/B medians: 19.08 s at 3e6 vs 20.70 s at 2e6, the 4e6 rejected: the diminishing returns + the RAM; the D-305 double-buffer overlap measured NULL on the 8-core box — the serial schedule already saturates the cores — and is REVERTED, the design recorded in the decision), the per-cell joint merges THREAD-parallel on a ThreadPoolExecutor (the independent cells, the numpy sort releases the GIL), the same-feature diagonal cells NOT BUILT (the (u, u) joint is the marginal itself — 6 of the 28 fixture cells, never consumed downstream); the D-306 docstring de-history: the WHAT contract only — no D-XXX, no change history, the _su_groups Section B -> C fix | 21/0/0 (via test_hlp_su_analysis) | docs/src/reversi/lm/hlp_su_analysis.md |
| src/reversi/lm/hlp_validate.py | complete: the VALIDATE data module — the single forward pass returning `ValidationResult` (the 7 metrics + the f64 series) + the `top_outliers` kernel (I-018) | 9/0/0 (via test_wrk_validate) | docs/src/reversi/lm/hlp_validate.md |
| src/reversi/lm/hlp_wmaps.py | complete: the WMAPS data object | 15/0/0 | docs/src/reversi/lm/hlp_wmaps.md |
| src/reversi/lm/hlp_zed.py | complete: the ZED data module | 10/0/0 | docs/src/reversi/lm/hlp_zed.md |
| src/reversi/tools/state_machine.py | complete: the generic pipeline orchestrator (Workers up/down + Context + logging / history / CSV); standing contracts: sentinel worker 0, failure semantics, unique names, \*_for_current_level naming | 49/0/0 | docs/src/reversi/tools/state_machine.md |

## Test files
One row per test file, alphabetical.

| File | State | Suite (live DB) | Doc |
| --- | --- | --- | --- |
| test/reversi/paths.py | the single home for workspace-root-anchored test paths — helper module (0 tests) | — | docs/test/reversi/paths.md |
| test/reversi/tags.py | the suite-tier gates (D-130/D-256) — the predicates + the DB gate, the single source of the tier semantics — helper module (0 tests) | — | docs/test/reversi/tags.md |
| test/reversi/tools/test_binio.py | complete: the binary IO suite (the batch + the 3 empty-suffix tests) | 45/0/0 | docs/test/reversi/tools/test_binio.md |
| test/reversi/test_board.py | complete: the board kernel suite — the bitboard layer (the 8 D8 transformations + the group law + the numba overloads), the position layer (creation, legal moves + the count, flips / make_move, the PASS-swap on the scalar + the bulk + the array batch + the fuzz parity, empties / empty count, collisions, game over, the Zobrist hash + the legacy parity), TestInitialGame, the two per-lane njit primitives (TestNumbaPrimitives), the named move-code pin, 2 PERF | 247/0/15 | docs/test/reversi/test_board.md |
| test/reversi/tools/test_cache_manager.py | complete: 22 tests | 22/0/0 | docs/test/reversi/tools/test_cache_manager.md |
| test/reversi/lm/test_client.py | complete: the client EF suite — the synthetic rlm_04-mirror weights (no DB), the 1000-position bit-exact parity, the u64 coercion, the 2-D guard, the scalar/list rejections, the N=0 edge + the PERF 1M test | 7/0/1 | docs/test/reversi/lm/test_client.md |
| test/reversi/test_feature.py | complete: the factory + construction + feature_blocks + compute_indexes suite | 25/0/1 | docs/test/reversi/test_feature.md |
| test/reversi/tools/test_prng.py | complete: the MT19937 suite — the smoke micro-suite (the determinism, the dtype pins, the no-consume contracts) + the golden suite (the committed 18436-line golden, 20 sections) + TestChooseOneFromSet64 (the empty sentinel, the (1 << p, p) return, the no-drain, the 1000-pick golden for 7 sets, the full-set equidistribution); TestPickOneFromSet64 (the D-221 kernel-method identity draw-for-draw + the batch equivalence + the all-empty no-draw case); the get_uint64_batch pin | 22/0/0 | docs/test/reversi/tools/test_prng.md |
| test/reversi/lm/test_wrk_analytics.py | complete: the ANALYTICS worker suite (the masked-hash helper + the 2 file-report goldens + the 4 SU-off pins) + the D-307 SU sample columns: the NO-DB mock-ctx suite (8 tests, the hand-computed TV/chi2/p/verdict goldens + the 2 INTERCEPT branch tests) + the DB-gated rlm_00 end-to-end (the 10k corpus vs the 200 training, the 5 re-derived consistency lines + the INTERCEPT pin) + the D-308 INTERCEPT pins (rlm_00 present, rlm_02 absent) + the D-311 cross-level eta² agreement (the DB-gated rlm_00 single-instance pin) | 14/0/0 | docs/test/reversi/lm/test_wrk_analytics.md |
| test/reversi/lm/test_wrk_client_check.py | complete: the CLIENT_CHECK worker suite — the synthetic rlm_04-mirror ctx (no DB, the real v2 SAVE write), the bit-identity golden, the RuntimeError + FileNotFoundError paths, the cfg-tolerance pin, the factory name, the no-op down | 6/0/0 | docs/test/reversi/lm/test_wrk_client_check.md |
| test/reversi/lm/test_hlp_plot.py | complete: the PLOT pure-helper suite — the seven-name vocabulary lock-step (names ⇄ builders ⇄ titles), the symmetric-axis limit, the R-semantic jitter bounds + the zero-range identity, the EGV even-grid bins + the known-values vector, the KDE zero-variance guard + the curve shape/peak | 11/0/0 | docs/test/reversi/lm/test_hlp_plot.md |
| test/reversi/lm/test_wrk_plot.py | complete: the PLOT worker suite — the synthetic rlm_04-mirror ctx (no DB), the pilot no-ops, the seven-PNG happy path + the per-up-move byte determinism, the pdf/png pair, the absolute dir, the partial whitelist, the parity rendering golden, the factory, the no-op down (the outlier report test moved to test_wrk_validate, I-018) | 9/0/0 | docs/test/reversi/lm/test_wrk_plot.md |
| test/reversi/lm/test_wrk_config.py | complete: 13 tests (the fingerprint + no-cache pins) | 13/0/0 | docs/test/reversi/lm/test_wrk_config.md |
| test/reversi/lm/test_wrk_design_matrix.py | complete: the DESIGN_MTR worker suite | 3/0/0 | docs/test/reversi/lm/test_wrk_design_matrix.md |
| test/reversi/lm/test_wrk_anova.py | the ANOVA worker NO-DB suite — the mock-ctx suite over the rlm_00 fixture (the factory, the enable no-op, the ANOVA, the graceful degradation, the adherence computed, the report, the down) | 7/0/0 | docs/test/reversi/lm/test_wrk_anova.md |
| test/reversi/lm/test_hlp_su_analysis.py | the SU analysis LOGIC NO-DB suite (D-289) — the signature (the independent sha3_256), the binio round-trip (with / without the joint), the load guards, the compute determinism, the theoretical space (D-278/279), the SU groups + the diagonal, the report + the CSV, the cache consistency (the real-pipeline ctx stopped at FEATURES, the D-287 idiom) + the D-295 accumulator migration (the marginal / the joint micro-suite + the PRNG integration, the toy corpus, the independent oracles; D-296: the _corpus helper + the accumulators take the PositionArray; D-298: the SU kernel micro-suite — the 5 hand-computed toy-table classes from test_hlp_feature_analysis; D-299: the joint micro-suite pins the vectorized merge, the MI calls pass the pre-computed entropies; D-301: the never-observed audit rows drop the rarity goldens; D-303: the new test_store_deep_validation pins the SuTables deep validation — the structurally malformed tables dict is rejected at the boundary); D-304: test_same_feature_diagonal now pins the 12 off-diagonal cells (the 4 diagonals NOT BUILT) vs the independent per-position oracle, the signature pins "su-corpus-4" | 38/0/0 | docs/test/reversi/lm/test_hlp_su_analysis.md |
| test/reversi/lm/test_wrk_su_analysis.py | the SU_ANALYSIS worker NO-DB suite — the mock-ctx suite over the rlm_00 fixture (the factory, the enable no-op, the compute + the publish, the cache hit, the signature invalidation, the corpus determinism, the su_pairs joint, the optional CSV, the down) | 10/0/1 (VLONG: 10/0/0, the 1e7 corpus) | docs/test/reversi/lm/test_wrk_su_analysis.md |
| test/reversi/lm/test_wrk_features.py | complete: the FEATURES worker suite (DB-free) | 3/0/0 (DB-free) | docs/test/reversi/lm/test_wrk_features.md |
| test/reversi/lm/test_lm_worker_full_chain.py | the END-TO-END suite: the full 18-level chain (the A2030 + A2050 chains, the read guards, the v2 micro, the client-check + PLOT log pins, the size bands, the outlier pins) + the full saved-model round-trip; the A2050 chain VLONG-gated | 9/0/1 | docs/test/reversi/lm/test_lm_worker_full_chain.md |
| test/reversi/lm/test_wrk_generate.py | complete: the GENERATE worker suite | 3/0/0 | docs/test/reversi/lm/test_wrk_generate.md |
| test/reversi/lm/test_wrk_gradient.py | complete: the GRADIENT worker suite (the float32 contract pin; the 2 no-DB flag-wiring tests) | 4/0/0 | docs/test/reversi/lm/test_wrk_gradient.md |
| test/reversi/lm/test_wrk_indexes.py | complete: the end-to-end cache round-trip pin | 2/0/0 | docs/test/reversi/lm/test_wrk_indexes.md |
| test/reversi/lm/test_wrk_optimize.py | complete: the OPTIMIZE worker suite | 3/0/0 | docs/test/reversi/lm/test_wrk_optimize.md |
| test/reversi/lm/test_wrk_positions.py | complete: the POSITIONS worker suite (the gate + the duplicate policy + the post-policy cache) | 12/0/0 | docs/test/reversi/lm/test_wrk_positions.md |
| test/reversi/lm/test_wrk_validate.py | complete: the VALIDATE worker suite — the metric goldens + the f64 series + the outlier kernel + the outlier report (moved from test_wrk_plot, I-018) | 9/0/0 | docs/test/reversi/lm/test_wrk_validate.md |
| test/reversi/lm/test_wrk_vld_positions.py | complete: the VLD_POSITIONS worker suite (the 0% / 100% overlap, traced not raised) | 11/0/0 | docs/test/reversi/lm/test_wrk_vld_positions.md |
| test/reversi/lm/test_wrk_wmaps.py | complete: the WMAPS worker suite | 3/0/0 | docs/test/reversi/lm/test_wrk_wmaps.md |
| test/reversi/lm/test_wrk_zed.py | complete: the ZED worker suite | 3/0/0 | docs/test/reversi/lm/test_wrk_zed.md |
| test/reversi/lm/test_logistic_model.py | complete: the facade suite — the pass-through pins, the LMContext/injection pins, the `run()` driver (the mocked resolution cases + the real-config FEATURES/SU_ANALYSIS class) | 29/0/0 | docs/test/reversi/lm/test_logistic_model.md |
| test/reversi/test_mobility.py | analyzed: 13 verified facts | 26/0/1 | docs/test/reversi/test_mobility.md |
| test/reversi/tools/test_opt_lbfgs.py | complete: the LBFGS suite (the batch + 9 new tests; the O2b bit-identity test) | 14/0/0 | docs/test/reversi/tools/test_opt_lbfgs.md |
| test/reversi/test_paths.py | complete: the 3 pin tests for the workspace-root paths | 3/0/0 | docs/test/reversi/test_paths.md |
| test/reversi/test_pattern.py | complete: the pattern suite (the fix campaign closed; the goldens re-derived) | 65/0/3 | docs/test/reversi/test_pattern.md |
| test/reversi/test_random_game.py | complete: the random-game suite — TestInitialGame (the Position dtype + the Bitboard field types + the mover {E4, D5} / opponent {D4, E5} square sets, the official Othello setup); TestRandomGameChooseMove (the golden: seed 93, 1000 draws, the EXACT frequencies [258, 229, 249, 264] over {D3, C4, F5, E6}); TestRandomGameChooseMoveEC20 (the per-position validity + the equidistribution over the available options); TestRandomGameChooseMoveArray (the D-219 array case: the batch bit-identical to the sequential scalar processing + the guards); TestRandomGameMakeMove (only the two resulting boards, the position↔move consistency, one stone ahead, the no-legal-move pass → swapped position + PA); TestRandomGameMakeMoveArray (the D-220 array case: the batch bit-identical to the sequential scalar processing + the per-code cross-check + the guards); TestRandomGamePlayPath (the target-ec landing + the multi-generation distinctness via position_hash — D-216; the double-pass game-over break + the single-pass continuation — D-218); TestRandomGamePlayPathArray (the D-222 array case: the N=1 scalar bridge, the determinism, the ec contract, the as-is, the guards; the PERF 1M-games benchmark) | 33/0/1 | docs/test/reversi/test_random_game.md |
| test/reversi/test_regab.py | complete: the regab suite (the batch incl. the 4 SQL-injection tests; the db_long_gate; the no-DB micro tier: dedup + overlap) | 48/0/0 | docs/test/reversi/test_regab.md |
| test/reversi/lm/test_hlp_config_schemas.py | complete: the pydantic config domain suite (the flag test; the client_check_tol tests; the 6 PlotConfig tests; the 4 su_analysis/anova tests) | 27/0/0 | docs/test/reversi/lm/test_hlp_config_schemas.md |
| test/reversi/lm/test_hlp_design_matrix.py | complete: the dedicated 14-test data suite | 14/0/0 | docs/test/reversi/lm/test_hlp_design_matrix.md |
| test/reversi/lm/test_hlp_feature_analysis.py | the ANOVA NO-DB micro-suite (the D-298 split — the SU kernel micro-suite moved to test_hlp_su_analysis) — the hand-computed toy tables for the ANOVA + the adherence kernels (+ the private kl / TV / chi-square helpers, the module-import calls) | 16/0/0 | docs/test/reversi/lm/test_hlp_feature_analysis.md |
| test/reversi/lm/test_hlp_generate.py | complete: the GENERATE data suite | 16/0/0 | docs/test/reversi/lm/test_hlp_generate.md |
| test/reversi/lm/test_hlp_gradient.py | complete: the GRADIENT data suite (the TestHighPerformanceFg class — equivalence, f32 contract, determinism, markers) | 14/0/0 | docs/test/reversi/lm/test_hlp_gradient.md |
| test/reversi/lm/test_hlp_indexes.py | complete: 14 tests (the compressed mock pins) | 14/0/0 | docs/test/reversi/lm/test_hlp_indexes.md |
| test/reversi/lm/test_hlp_optimize.py | complete: the OPTIMIZE data suite | 20/0/0 | docs/test/reversi/lm/test_hlp_optimize.md |

| test/reversi/lm/test_hlp_wmaps.py | complete: the WMAPS data suite | 15/0/0 | docs/test/reversi/lm/test_hlp_wmaps.md |
| test/reversi/lm/test_hlp_zed.py | complete: the dedicated 10-test data suite | 10/0/0 | docs/test/reversi/lm/test_hlp_zed.md |
| test/reversi/tools/test_state_machine.py | complete: 13 original expectations independently re-derived | 49/0/0 | docs/test/reversi/tools/test_state_machine.md |
| test/reversi/tools/test_usage_binio.py | complete: the 3 usage tests | 3/0/0 | docs/test/reversi/tools/test_usage_binio.md |

Test data (test/reversi/data/): rlm_00.json (the JSON5 config), rlm_01.json (the training DB dump), rlm_02.json (the
DB dump), rlm_03.json + rlm_04.json (the validation sets) — the per-file mirror docs cover them. Plus
ffo_12_log_sample.csv (the FFO-12 legacy C solve-log sample, the `position_hash` parity fixture — D-215: the full
571_141-row log verified 100%, the committed sample is the deterministic 1002-row stride).

## Index
The docs/ mirrors (one per source/test file, D-007) are NOT listed here: their paths are the Doc column of the two
tables above.

- notes/naming.md — canonical board naming convention (row/column, D-013; D8 symmetries, D-014)
- notes/rules.md — active legislation: the register of the rules in force (one line per rule, origin D-number; lifecycle
  RECORD/PROMOTE/RETIRE)
- notes/decisions.md — open historical decision log (append-only, D-NNN; the rules in force live in notes/rules.md;
  closed volumes: decisions_NNN.md)
- notes/decisions_000.md — closed decision volume 000 (D-001…D-116, 2026-08-25 → 2026-09-06)
- notes/decisions_001.md — closed decision volume 001 (D-117…D-158, 2026-09-06 → 2026-09-11)
- notes/analyses/ — archived one-off investigations + the classification + the extracted verbatim reviews
- notes/analytical_properties_of_features.md — the I-017 project document (objective, plan, tasks T1..T19)
- notes/performance_baseline.md — the wave-tier performance baseline (the D-175/D-176 reference numbers for the
  profiling session)
- notes/ideas.md — the OPEN backlog (I-NNN, D-235)
- notes/ideas-closed.md — the CLOSED ideas (done | dropped): the compacted I-NNN record (D-235)
- notes/log_rules.md — session-journal format rules (rigid; global session numbering; volume rotation: 25 sessions /
  2000 lines per volume, only at session boundaries)
- notes/docs_rules.md — mirror-doc format rules (rigid; the current-state contract)
- notes/tools.md — the workspace-tool rules (the four requirements + the inventory, D-248/D-249)
- notes/probe_rules.md — verification-apparatus rules (rigid; the a/b/c classification + the independent-derivation
  criterion, the test/probe line, the pipeline-state centralization in the hub, the campaign sweep rule, the archive to
  notes/analyses/, the baseline)
- notes/log_000.md — session journal, volume 000 (sessions 1–24, closed 2026-09-01)
- notes/log_001.md — session journal, volume 001 (sessions 25–30, closed 2026-09-08)
- notes/log_002.md — session journal, volume 002 (sessions 31–37, closed 2026-09-18)
- notes/log_003.md — session journal, volume 003 (sessions 38–..., open)
