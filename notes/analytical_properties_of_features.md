# analytical_properties_of_features.md — the I-017 project

> Status: DRAFT v1 — 2026-09-11 (D-156 kickoff; D-156b v1
> revision). Incorporates Roberto's redesign proposals (the
> synthetic corpus, the pipeline reordering, the target_level,
> the SU cache, the instance-level SU) with Nia's comments; the
> open points (section 6) await Roberto's confirmation. No source
> files are touched until the confirmation; execution starts with
> T1.

## 1. Objective

Introduce feature-characterization capabilities into the RLM
pipeline, built on a SYNTHETIC random-play population (not the DB
training set):

- (a) SU (Symmetrical Uncertainty): an unsupervised
  feature↔feature correlation + per-feature dispersion, computed
  on the SYNTHETIC ideal population — the precise
  random-play configuration frequencies. It includes the
  "configurations never observed" audit (the feature-set pruning
  input, inspectable BEFORE spending the pipeline on training).
- (b) eta² / omega²: the supervised ANOVA effect size per
  feature (target = the DB game values), at its own level before
  OPTIMIZE.
- (c) The adherence check: how close the DB training set's
  configuration distribution is to the ideal population
  (per feature, all features).

The workflow this enables (Roberto's): CONFIG → FEATURES →
FEATURE_ANALYSIS (SU) → STOP → inspect the audit (which
configurations of which patterns are never / almost never
observed, which features are redundant) → decide whether to
continue → the full pipeline (POSITIONS → … → EFFECT_SIZE → …).

The project also realizes I-012 (FEATURES before POSITIONS —
Roberto's parked idea, 2026-08-31): the reordering is a
prerequisite of the design, not a side effect.

## 2. Roberto's proposals (his words, digested) + the design they drive

P1. The SU analysis needs no game values: it depends only on the
    features. Instead of using the DB positions, generate a new,
    DB-independent corpus: random games from the initial position
    (board.py has everything, already vectorized; the generation
    is fast; the positions are NOT solved — only the
    configuration frequencies are wanted). A batch of ~1M
    positions, accumulated into a frequency dictionary keyed by
    configuration index, in a loop (numba if needed) ~1000× →
    1e9 positions ("1-10 miliardi", 1000× the A2050 DB). The SU
    statistics are built on THESE frequencies ("precise a
    piacere").
P2. Pipeline ordering: FEATURES first, then the SU analysis, then
    POSITIONS — with the possibility to STOP right after the SU
    step and analyze the patterns' never-observed configurations
    before running the full pipeline.
P3. OMEGA (eta²/omega²) depends on the DB positions and the index
    computation: its own level BEFORE the expensive OPTIMIZE
    (preferred) — or inside ANALYTICS post-OPTIMIZE (less
    preferred).
P4. A JSON parameter target_level (default "last"): the pipeline
    stops at the named level.
P5. The SU level needs the CACHE, for sure: it may take ~10
    minutes (Nia: see the honest cost model in §7), but it runs
    once and stays valid as long as the features do not change.
P6. SU is specific to our model: patterns have INSTANCES (8, 4,
    2, 1). The analysis is a MATRIX between instances:
    EDGE-DIAG8 (4 × 2 instances) → 8 SU values (Edge_0-Diag8_0 …
    Edge_3-Diag8_1); the same-feature measure EDGE-EDGE is also
    meaningful (the diagonal is all 1s). A2050 scale: 10+
    features → ~100 pairs × ~16 instance pairs → ~1,600 metrics.
    → specify the SU pairs EXPLICITLY in the config. Meanwhile the
    adherence analysis runs for ALL features.

## 3. The design (DRAFT v1)

### 3.1 The new pipeline order (18 domain levels)

    step  name                cache slot   notes
    0     CREATED             —            sentinel (D-059)
    1     CONFIG              —            + the config fingerprint
    2     FEATURES            —            moved here (I-012: it
                                           depends only on cfg)
    3     FEATURE_ANALYSIS    rlmwf_03     NEW — the SU level
                                           (synthetic corpus +
                                           statistics + the
                                           never-observed audit);
                                           CACHED (P5)
    4     POSITIONS           rlmwf_04     (was 02)
    5     INDEXES             rlmwf_05     (was 04)
    6     EFFECT_SIZE         —            NEW — eta²/omega² +
                                           the adherence; no
                                           cache (P3)
    7     WMAPS               rlmwf_07     (was 05)
    8     DESIGN_MTR          rlmwf_08     (was 06)
    9     ZED                 —            (was 07)
    10    GRADIENT            —            (was 08)
    11    OPTIMIZE            (checkpoint) (was 09)
    12    GENERATE            rlmwf_12     (was 10)
    13    VLD_POSITIONS       rlmwf_13     (was 11)
    14    VALIDATE            —            (was 12)
    15    ANALYTICS           —            (was 13)
    16    SAVE                —            (was 14)
    17    CLIENT_CHECK        —            (was 15)
    18    PLOT                —            (was 16)

Consequences (accepted costs, once):
- the rlmwf_NN slots of every downstream cache level shift → the
  production caches (A2050 base_dir) are orphaned on the next run
  (one full recompute: the DB extraction + the ~50 s chain —
  cheap);
- the full-chain goldens re-pin (the "N/LEVEL" log lines, the
  final level 18/PLOT, the hub probe 17 → 18 levels) — the
  D-148/D-149 campaign precedent;
- the model file content is unaffected by the reordering itself,
  but the embedded v2 config dump GROWS (the two new config
  sections + target_level) → the size bands re-center (the D-147
  procedure), like D-149 did;
- the stale test setUp comment ("Move to POSITIONS first, as
  FEATURES depends on the configuration loaded there" — I-012)
  gets fixed as part of T1.

### 3.2 The FEATURE_ANALYSIS level (the SU level, step 3)

Inputs: ctx.cfg + ctx.feature_set ONLY (no DB, no positions).
Two phases:

Phase 1 — the corpus (the expensive part, CACHED):
- A seeded, vectorized random-play generator (a new component;
  board.py's public API: legal_moves / position_make_move /
  position_is_game_over, all vectorized — nothing tracked exists
  today, the 200-game simulation was scratch). Wave semantics: a
  batch of concurrent games; per ply: compute the legal moves,
  pick a random legal move per active game (a numba kernel if the
  numpy pick is slow), make the move; no legal moves → the pass;
  two consecutive passes or a full board → the game over → the
  slot respawns at the initial position. Every ply position is
  streamed into the frequency accumulators (never stored).
- The accumulators (per the analysis unit, §3.3):
  - the MARGINAL frequency table of EVERY sub-variable
    (code → count, over the whole corpus);
  - the JOINT frequency table of every REQUESTED su pair, at the
    instance×instance level (the (code_u, code_v) → count for
    every instance pair of the two features — P6's matrix).
- Cache flow: the cache_manager load-or-compute (the .SHA3-256
  sidecar, the 8192-chunk verify — D-071/D-072), the file
  rlmwf_03_FEATURE_ANALYSIS.dat. Consistency signature: the
  feature_set hash + the generation spec (the seed, the batch
  size, the wave count, the generator version) + the su_pairs
  list (canonical sorted form). NOTE (P5 interaction): because
  the joint tables are per requested pair, a pair-list change
  invalidates the corpus cache → a full regeneration. The v2
  refinement (parked): a two-tier cache (the marginals keyed on
  (features, spec); the joints keyed on (+ pairs)) so a pair
  experiment reuses the marginal corpus.
- The corpus is INDEPENDENT of the DB: the first cache level
  whose signature does NOT carry the rds_checksum (it carries the
  feature_set hash instead) — a new kind of cache lineage.

Phase 2 — the statistics (cheap, recomputed on EVERY run,
including the cache-hit):
- per sub-variable (all of them): K_obs (the distinct observed
  codes), the entropy H (bits), H_norm = H/log2(K_obs) (else 0),
  the coverage = K_obs / n_configurations (the theoretical range);
- the never-observed audit (the STOP deliverable, P2): per
  sub-variable, the number of theoretical codes never seen in the
  corpus (n_configurations − K_obs) + the rarity profile (the
  count of codes below small count thresholds) — "the
  configurations that random play never / almost never reaches:
  the weights that can never be learned";
- the requested SU pairs (P6): for each configured feature pair
  (F_i, F_j), the full n_instances(i) × n_instances(j) matrix of
  SU values, from the joint frequencies:
    SU(u, v) = 2·I(u; v) / (H(u) + H(v))   (SU = 0 if the
    denominator is 0); I from the joint counts. Range [0, 1].
  - same-feature pairs (F, F): the diagonal is the variable with
    itself → SU = 1 (reported as a lock, or omitted — ODP-5); the
    OFF-diagonal entries measure the spatial correlation between
    the D8 orientations of the same mask (an anisotropy measure,
    structurally distinct from the redundancy signal of the
    cross-feature pairs — the report groups the two kinds).
- the SU is computed from the IDEAL (synthetic) frequencies: a
  structural property of the game geometry + the feature set,
  free of the DB sample noise.

Outputs: the console (INFO summary per feature + the top SU
pairs), the TXT report (dir_name under base_dir, the PlotConfig
pattern), the optional CSV (the per-pair instance matrices + the
marginal tables). The level publishes the corpus frequency
tables on the ctx (LMContext) so EFFECT_SIZE (step 6) can consume
them for the adherence — a cross-level blackboard artifact (the
D-099 pre-declared fields).

Failure: the D-060 semantics (the generation error → the level
fails, the machine re-raises, the domain recovery); down() clears
the ctx artifacts.

### 3.3 The analysis unit: the (feature, instance) sub-variable

Each design-index column is a categorical variable over the
positions (the design-matrix unit, the unit the weights live on):
the intercept (the constant 0 — degenerate, reported, excluded
from the pairs), each mobility (1 column: the count
popcount(lms&mask) + (popcount(amask) − popcount(alms&amask)),
range 0..k+a), each pattern (n_instances = the D8 orbit-group
columns, the principal base-3 ternary index over the S squares,
range 0..3^(2S)−1; code 0 = the "no match" configuration, a
first-class modeled category with its own weight → it stays a
group everywhere).

P6 refinement (accepted): the SU PAIRS are specified at the
FEATURE level (the names), and the level expands each pair to its
full instance×instance matrix. The marginal dispersion + the
eta²/omega² + the adherence run over ALL sub-variables without a
list (P6: "per tutte le features").

### 3.4 The EFFECT_SIZE level (eta²/omega² + the adherence, step 6)

Inputs: ctx.game_values + ctx.hlp_indexes (the DB training set) +
the ctx corpus frequency tables from FEATURE_ANALYSIS.
- eta² / omega² per sub-variable (all of them): the one-way
  ANOVA, the observed codes as the groups (K), the target = the
  continuous training game values (N):
    SS_tot = sum (y−ybar)²; SS_eff = sum_g n_g(y_g−ybar)²;
    SS_err = SS_tot − SS_eff;
    eta² = SS_eff/SS_tot;
    omega² = (SS_eff − (K−1)·MS_err)/(SS_tot + MS_err),
    MS_err = SS_err/(N−K).
  Guards: K = 1 → eta² = omega² = 0 (degenerate, by convention);
  K > N → ValueError (unreachable). omega² may be slightly
  negative (the null effect): the raw value is reported. eta² is
  the biased sample share (up with high K); omega² is the unbiased
  population estimate — the pair is reported together.
- The adherence (c): per sub-variable, the DB configuration
  distribution (the observed codes of the training positions) vs
  the ideal distribution (the corpus frequencies, normalized):
  the chi-square goodness-of-fit (the p-value; the low-expected
  cells are merged into an "other" tail bin until the expected
  count ≥ 5 — the standard technique, a T3 detail) + the KL
  divergence + the total variation distance (the 0..1
  "how different" number, robust). Console: the top-N most
  deviant features (TV descending).
  Graceful degradation: if the FEATURE_ANALYSIS level was
  disabled (no corpus in the ctx), the adherence is skipped with
  a log note; the eta²/omega² runs (it does not need the corpus).
Outputs: the console + the TXT report (+ the optional CSV). No
cache (a diagnostic; the recompute is seconds). D-060 semantics.

### 3.5 target_level (P4)

LMConfig.target_level: str = "last". The StateMachine already
accepts a worker NAME (case-insensitive, the fail-fast
ValueError) in move_to_step — the missing piece is a facade
entry that consumes the JSON:
    LogisticModel.run(target_level: str | None = None)
  → move_to_step("CONFIG") (always first — the cfg must be
  loaded) → the effective target = the explicit argument, else
  cfg.target_level, else "last" → move_to_last() for "last",
  else move_to_step(name).
An unknown name → the existing ValueError (no new validation
machinery). The semantics is the machine's existing contract: the
state "steps 1..t done" (the target included), the ctx
preserved, the resume = another move_to_step (the caches hot).
This generalizes the P2 workflow: the stop is available at ANY
level, not only after the SU.

### 3.6 The configuration (the PlotConfig pilot pattern, D-149)

    feature_analysis: {
      enable: true,                     # master switch
      corpus: {
        seed: 42,                       # the rng seed (reproducibility)
        batch_size: 1000000,            # the concurrent games per wave
        waves: 100                      # ~the total corpus (OPN — ODP-2)
      },
      su_pairs: [["EDGE", "DIAG8"]],    # P6: the explicit pairs
                                         # (feature names, fail-fast
                                         # against cfg.feature_set;
                                         # canonical order + dedupe)
      dir_name: "feature_analysis",
      report_file_name: "feature_analysis_report.txt",
      export_csv: false
    }
    effect_size: {
      enable: true,
      top_k_adherence: 20,
      dir_name: "effect_size",
      report_file_name: "effect_size_report.txt",
      export_csv: false
    }
    target_level: "last"

Defaults: the sections exist with enable true and an EMPTY
su_pairs → the FEATURE_ANALYSIS level still builds the corpus +
the marginals + the audit (the cheap-to-inspect part), without
any joint (the default corpus cost, no pair cost); an enable
false makes the level a no-op (and EFFECT_SIZE degrades, §3.4).
The production A2050/A2030 configs stay untouched until we opt in
(they gain the fields by default). The rlm_00 test fixture opts
in with a SMALL corpus + 1-2 pairs (the chain exercises the
level end-to-end; the goldens re-pin).

## 4. The metric details (the kernels, float64, deterministic)

- Entropy / MI / SU: from the frequency tables (the counts, not
  the positions) — H = −Σ p log2 p; I = Σ p_xy log2(p_xy/(p_x
  p_y)); SU = 2I/(H_u+H_v), 0 on the 0 denominator. (v0's
  formulas stand.)
- ANOVA: §3.4 (v0's formulas stand).
- Adherence: the chi-square (the merged-tail p), the KL
  (Σ p_ideal log(p_ideal/p_db), the 0·log 0 = 0 convention, the
  zero-DB-probability cells handled by the same tail merge), the
  TV = ½·Σ |p_db − p_ideal| (in [0, 1]).

## 5. The workflow the design enables (the point of it all)

1. CONFIG → FEATURES → FEATURE_ANALYSIS (a fresh feature set: the
   corpus is generated ONCE — the cached hours; a feature-set
   change: a new generation).
2. STOP (target_level = "FEATURE_ANALYSIS"): read the audit —
   the never-observed configurations per pattern (the
   over-parameterized features), the dispersion (the degenerate
   ones), the requested SU pair matrices (the redundant
   features). Decide: fix the feature set (re-run, the corpus is
   cheap if the features are unchanged) or continue.
3. Continue → POSITIONS (the DB) → INDEXES → EFFECT_SIZE: the
   eta²/omega² per feature (which features actually move the
   game value on the REAL data) + the adherence (how close the
   DB set is to the ideal population — the selection effect of
   the DB extraction, quantified). Another decision point (the
   target_level = "EFFECT_SIZE" stop).
4. The full chain → PLOT.

## 6. Open decision points (Roberto's call)

| #   | Question | Proposal |
| --- | --- | --- |
| ODP-1 | Corpus size (P1 says 1-10e9): the statistical floor is ~1e8 (50× the A2050 DB — the adherence + the SU are solid where they matter); 1e9 is the exhaustive rare-configuration audit (the "never observed" precision). The cost scales linearly. | the default 1e8 (the waves parameter), 1e9 reachable in the production config; the v1 measurement decides |
| ODP-2 | The DB sampling window: the DB positions — ALL the plies of the random games, or a suffix / a filter (the "ec" parameter)? If filtered, the ideal population must be filtered the same way or the adherence measures the selection, not the representativeness. | the generator keeps all plies by default; an optional ply-window filter is a v2 refinement IF the DB is windowed (your knowledge needed) |
| ODP-3 | Level names | "FEATURE_ANALYSIS" (the SU level) + "EFFECT_SIZE" (the eta²/omega² + adherence) |
| ODP-4 | Same-feature SU pairs (P6's EDGE-EDGE): the diagonal (the variable with itself, SU = 1) — report it or omit it? | omit the diagonal, report the off-diagonal (the anisotropy), a report note |
| ODP-5 | The adherence metric set: a fixed trio (chi-square + KL + TV) or a config whitelist? | the fixed trio, no config (the report shows all three) |
| ODP-6 | target_level (P4): the field name + the "last" default + the facade run(target_level=None) override — as in §3.5? | confirm |
| ODP-7 | The pair-list change invalidates the corpus cache (the joint tables are per pair). v1: single signature (a pair change → the regeneration); the two-tier cache (the marginals reusable) parked as a v2 refinement. | the v1 single signature |
| ODP-8 | (the v0 ODP-4/5 stand, resolved by the design): code 0 "no match" stays a group (a first-class modeled category); the intercept is excluded from the pairs, kept in the tables | as designed |

## 7. The cost model (Nia's honest numbers, to be measured at T2)

- Generation: ~120 plies/game; a wave = 1e6 concurrent games ≈
  12 s of ply work → one wave ≈ 55-60M positions. 1e8 ≈ 2
  waves ≈ minutes; 1e9 ≈ 18 waves ≈ ~30 min of generation.
- Accumulation: per wave, the marginal tables of ~240
  sub-variables (the bincount where the code range allows, the
  unique-merge otherwise) + the joints of the requested pairs
  (few) ≈ 1-3 min/wave → 1e8 ≈ 5-10 min; 1e9 ≈ 1-3 h. The
  generation is the cheap part; the accumulation dominates.
  (P5's "10 minuti" is right for 1e8; 1e9 is the hours case.)
- Corpus memory: never stored (the streaming); the frequency
  tables at most GB-scale in the worst case (the distinct codes
  per sub-variable are bounded by the geometry, in practice
  far below 3^(2S)).
- The EFFECT_SIZE recompute on a cache hit: seconds.
- The one-time campaign costs: the production cache orphaning
  (the slot shift) → one A2050 recompute (~1 min chain + the DB
  extraction); the size-band re-centering (the config dump
  growth, D-147); the full-chain goldens re-pin (the log lines +
  the hub 17 → 18).

## 8. Tasks (one per session, in sequence)

- T0 (done 2026-09-11): the project document v0 (D-156).
- T0b (this session, 2026-09-11): the document v1 — Roberto's
  proposals incorporated + the comments + the new ODP list.
- T1: the reordering (I-012 realized): the worker list
  FEATURES → POSITIONS, the slot shift, the golden re-pin
  (the full-chain A2030/A2050), the hub probe, the stale test
  comment fix, the run_utests.sh order, the mirrors, the D.
  Verify: LONG=1 + VLONG (the A2050 chain) + the sweep.
- T2: the corpus generator (hlp_feature_analysis.py, phase 1):
  the seeded vectorized random-play waves + the marginal/joint
  frequency accumulators + the small no-DB micro-suite (the
  seeded toy corpus, the hand-counted frequencies on a 2-3
  feature set) + the throughput scratch probe (the cost model
  check) + the mirror + the D.
- T3: the statistics kernels (hlp_feature_analysis.py, phase 2):
  the entropy/MI/SU from the frequency tables, the dispersion +
  the never-observed audit, the ANOVA eta²/omega², the adherence
  trio (the merged-tail chi-square, the KL, the TV) + the
  no-DB micro-suite (the hand-computed toy values) + the mirror
  + the D.
- T4: the config: the feature_analysis + effect_size sections +
  the target_level field (the schema: the fail-fast pair
  vocabulary, the corpus spec, the validators) + the schema
  tests + the mirrors + the D.
- T5: the FEATURE_ANALYSIS worker (the step 3): the cache flow
  (the new signature kind: the feature_set hash + the spec + the
  pairs — no rds_checksum), the phase-2 recompute on the cache
  hit, the reports, the ctx publication, the D-060 semantics +
  the no-DB worker suite (the no-ops, the happy path, the
  file pins, the failure paths) + the mirror + the D.
- T6: the EFFECT_SIZE worker (the step 6): the eta²/omega² +
  the adherence reports, the graceful degradation + the no-DB
  worker suite + the mirror + the D.
- T7: the full wiring: the logistic_model (the 18-level list,
  the new ctx fields, the run() facade + the target_level, the
  worker-count test re-pin), the rlm_00 fixture (the small
  corpus + 1-2 pairs + the target_level "last"), the full-chain
  re-pin (the A2030 log + the A2050 VLONG + the size bands),
  the hub probe, the new probes (the verify_feature_analysis +
  the verify_effect_size), the run_utests.sh insertion, the
  campaign probe sweep (gated + live), the mirrors, the
  decisions (the campaign D), the overview, the I-012 → done +
  the I-017 progression. Verify: LONG=1 + VLONG + the sweep
  green.

Verification regime: the default tier at every commit; the
pre-commit always LONG=1 ./run_utests.sh (the live DB); VLONG
at T1 (the reordering touches the chain) and T7.

## 9. Files touched (planned, v1)

New: hlp_feature_analysis.py (+ the mirror), wrk_feature_analysis.py
(+ the mirror), wrk_effect_size.py (+ the mirror),
test_hlp_feature_analysis.py (+ the mirror),
test_wrk_feature_analysis.py (+ the mirror),
test_wrk_effect_size.py (+ the mirror),
probes/verify_feature_analysis.py, probes/verify_effect_size.py.
Modified: hlp_config_schemas.py (+ the schema suite),
logistic_model.py (+ the worker list + the ctx + the run()),
data/rlm_00.json, test_lm_worker_full_chain.py,
probes/verify_logistic_model.py (the hub), run_utests.sh,
notes/ (the decisions, the overview, the ideas: the I-012 → done,
the I-017 progression).

## 10. Risks / notes

- The reordering is the invasive step (T1 is done BEFORE the
  analysis code lands, on its own, re-pinned and green — the
  rest of the campaign builds on the new order).
- The corpus generation is the only long-running compute: if the
  T2 measurement is far from the §7 model, the batch size / the
  accumulation technique (a numba dict pass) adapt BEFORE T5
  (the cache absorbs the re-run).
- The chi-square on the wide configuration spaces: the
  merged-tail cell rule is a standard technique, but it is a
  judgment call on the p-values — the report shows the merge
  count (transparency), the metric stays descriptive.
- The DB sampling window (ODP-2) is the main statistical risk of
  the adherence: a mismatched window makes the metric measure
  the selection, not the representativeness — hence the ODP
  before T3.
- The decisions.md volume is at ~1940 lines (the 2000-line
  rotation at a session boundary, D-118): the rotation may fire
  mid-campaign; the D-numbers stay global.
