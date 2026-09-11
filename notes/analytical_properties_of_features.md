# analytical_properties_of_features.md — the I-017 project

> Status: DRAFT v0 — 2026-09-11 (D-156 kickoff). The plan awaits
> Roberto's confirmation on the open points (section 5). No source
> files are touched until the confirmation; execution starts with T1.

## 1. Objective

Introduce two feature-characterization capabilities into the RLM
pipeline. They answer two different questions about the feature set
× the training corpus:

- (a) SU (Symmetrical Uncertainty): "how dispersed is each
  feature's configuration, and which features are redundant with
  each other?" Purely unsupervised: the game value is NOT used.
- (b) eta² / omega² (the ANOVA effect sizes): "how much of the
  game-value variance does each feature's configuration explain?"
  Supervised: the target is the continuous game value.

The two are complementary: (a) maps the feature space alone
(degeneracy, redundancy); (b) measures the per-feature effect on
the target. Together they support feature-set design and pruning
(the "I-012 FEATURES" backlog direction).

## 2. The metrics

### 2.1 SU (approach a)

For two discrete variables (u, v) with joint counts p_xy:

    H(u)    = -sum_x p_x * log2(p_x)
    I(u;v)  = sum_xy p_xy * log2( p_xy / (p_x * p_y) )
    SU(u,v) = 2 * I(u;v) / (H(u) + H(v))      (SU = 0 if H(u)+H(v) = 0)

Range [0, 1]: 0 = independent, 1 = same information. The
normalization by the entropy sum removes the high-cardinality bias
of the plain mutual information (the reason SU is the chosen
metric). Role in the project: pairwise between the configuration
variables of DIFFERENT features (feature↔feature correlation — no
target involved). The per-variable H(u) doubles as the dispersion
measure (section 4.2).

### 2.2 eta² / omega² (approach b)

One-way ANOVA per feature variable v, the observed configuration
codes as the groups (K groups, sizes n_g, means y_g), the
continuous target y = the training game values (N observations):

    SS_tot  = sum (y - ybar)^2
    SS_eff  = sum_g n_g * (y_g - ybar)^2
    SS_err  = SS_tot - SS_eff
    eta^2   = SS_eff / SS_tot
    omega^2 = (SS_eff - (K-1) * MS_err) / (SS_tot + MS_err)
              with MS_err = SS_err / (N - K)

eta² is the sample variance share (biased up with high K); omega²
is the unbiased population estimate (the df penalty in the
numerator, MS_err in the denominator) — the "more sophisticated
successor". omega² can be slightly negative for a null effect: the
raw value is reported (the standard convention).

Guards: K = 1 (constant variable) → eta² = omega² = 0 (degenerate,
by convention); K > N → ValueError (unreachable: K ≤ N always).

## 3. Ground facts (the 2026-09-11 reconnaissance)

- The pipeline is 17 levels (CONFIG … PLOT) on the LMContext
  blackboard. Precedent for a new diagnostic level: CLIENT_CHECK
  (16th, D-148) and PLOT (17th, D-149) — both appended at the
  tail, config-piloted, no cache file.
- The per-position feature configuration is already computed and
  cached at the INDEXES level: ctx.hlp_indexes.indexes is the
  (N, I) uint32 design-index matrix — one column per
  (feature, instance) sub-variable:
  - the intercept: the constant 0 (1 column, when configured);
  - each mobility: 1 column, value = popcount(lms & mask) +
    (popcount(amask) − popcount(alms & amask)), range 0..k+a
    (n_configurations = k + a + 1);
  - each pattern: n_instances columns (the D8 orbit groups of the
    mask images), each value = the principal (orbit-minimum)
    base-3 ternary index over the S squares, range 0..3^(2S)−1.
    Value 0 = the pattern does not match at that orientation: the
    "empty" configuration is a first-class modeled category (it
    owns its design-matrix weight), so it stays a group in the
    ANOVA (ODP-4).
- The target: ctx.game_values, the (N,) float training game values
  (the continuous target of the model).
- Scale (A2050): N = 199,932; I ≈ 240 columns (derived from the
  D-145 M×P temporary measurements); the sub-variable count is a
  few hundred.
- Config pilot pattern: PlotConfig (D-149) — the enable master
  switch + the name whitelist (fail-fast validation, dedupe) +
  format/dir_name. The new section follows it.

## 4. Proposed design

### 4.1 Placement: the 18th level FEATURE_ANALYSIS (step 17, after PLOT)

- New worker appended at the tail (the CLIENT_CHECK/PLOT
  precedent); it consumes only existing ctx artifacts (feature_set,
  positions, hlp_indexes, game_values — all live at that point,
  cache-hit or compute) and publishes one result object
  (LMContext.feature_analysis).
- No cache file: the 9th non-cache deviation (the rlmwf_17 slot,
  file-less — the reports are outputs, not pipeline inputs; the
  PLOT rationale).
- D-060 failure semantics; down() clears the ctx field.
- Training corpus only (the validation set is out of scope: the
  feature characterization is about the data the model is trained
  on).
- Why not a section of ANALYTICS (13th): the analysis is
  feature×corpus, model-independent; a dedicated level keeps the
  analytics level and its goldens stable. Why not an insertion
  after INDEXES: it would renumber the rlmwf_NN_ slots and re-pin
  the whole chain — cost without benefit (the level is a
  diagnostic; its position is semantically irrelevant). [ODP-3]

### 4.2 The analysis unit: the (feature, instance) sub-variable

Each index column is a categorical variable over the positions —
the design-matrix unit, the unit the model's weights live on. The
report is grouped by feature name, one row per sub-variable:

    <feature name> <category> <instance i of n>
        K_obs   H(bits)   H_norm   coverage   eta2   omega2

- K_obs: the distinct codes observed over the N positions;
- H: the entropy of the observed-code distribution (bits);
- H_norm = H / log2(K_obs) (K_obs > 1, else 0): 0 = degenerate
  (constant), 1 = uniform over the observed codes;
- coverage = K_obs / n_configurations (the theoretical range);
- eta² / omega²: section 2.2 (target = the training game values).

[ODP-2: the alternative is a feature-level aggregation — it needs
a reduction rule over the pattern's n_instances columns; less
faithful to the model; not the default.]

### 4.3 The SU pairs

- Computed between sub-variables of DIFFERENT features only (the
  same-feature instance columns are co-designs of one mask; the
  intercept is excluded — trivially degenerate [ODP-5]).
- Outputs: the full matrix (the report file / CSV) + the top-k
  strongest pairs (console + the report header) — the redundancy
  report. k = the cfg top_k_pairs (default 20).

### 4.4 Configuration (the FeatureAnalysisConfig, the PlotConfig pattern)

    feature_analysis: {
      enable: true,                    # master switch
      methods: ["su", "eta2", "omega2"],  # whitelist; empty = no-op
      top_k_pairs: 20,                 # strongest SU pairs reported
      dir_name: "feature_analysis",    # absolute as-is / relative under base_dir
      report_file_name: "feature_analysis_report.txt",
      export_csv: false                # optional CSV export of the tables
    }

- methods: fail-fast vocabulary {su, eta2, omega2} + dedupe (the
  PlotConfig validator pattern); "su" adds the pair matrix + the
  top-k; "eta2" / "omega2" add their columns; the base dispersion
  table (K_obs, H, H_norm, coverage) is always in the report when
  methods is non-empty.
- Defaults: enable true, methods EMPTY → the level is a no-op
  unless configured: the production A2050/A2030 configs stay
  untouched until we opt in.
- The rlm_00 test fixture (the full chains) opts in with all three
  methods: the chains exercise the level end-to-end; the chain log
  pins are re-pinned (the model file is NOT affected — no size-band
  change).

### 4.5 Outputs

- Console: the INFO summary (one line per feature: the
  sub-variable span + the strongest SU pair per feature) + the
  DEBUG full per-sub-variable table.
- File: the TXT report under base_dir/dir_name (always when methods
  is non-empty); the optional CSV (the sub-variable table + the SU
  matrix) for off-pipeline analysis.
- No model-file content: the size bands stand.

## 5. Open decision points (Roberto's call)

| #   | Question | Default proposal |
| --- | --- | --- |
| ODP-1 | The SU reading: feature↔feature, unsupervised (no target) — my reading of "misura solo la dispersione e la correlazione delle configurazioni"? (vs SU(feature, discretized game_value) — excluded by your "non impiega il game value") | feature↔feature |
| ODP-2 | The analysis unit: the (feature, instance) sub-variable = the design-matrix unit | the sub-variable (the feature-level aggregation needs a reduction rule over the pattern instances) |
| ODP-3 | Placement: the 18th level after PLOT (the tail precedent) | the 18th level |
| ODP-4 | The code-0 "no match" in the ANOVA groups: included or excluded | included (a first-class modeled category with its own weight) |
| ODP-5 | The intercept in the SU pairs | excluded (degenerate), kept in the table |

## 6. Tasks (one per session, in sequence)

- T0 (this session, done 2026-09-11): the project document + the
  I-017 idea line + the D-156 kickoff entry + the overview bullet.
  No source. (DRAFT until the ODP confirmation.)
- T1: the data module src/reversi/lm/hlp_feature_analysis.py —
  the pure float64 kernels (entropy, MI, SU, the ANOVA
  eta²/omega²) + the sub-variable-table / SU-matrix orchestrator
  (consumes feature_set + the index matrix + the game values; no
  DB) — + the no-DB micro-suite test_hlp_feature_analysis.py
  (hand-computed toy values, the independent-derivation
  criterion) + the mirror + a D entry. Verify: the default tier +
  the module suite.
- T2: the config — the FeatureAnalysisConfig schema + the
  LMConfig.feature_analysis field + the schema tests + the mirror
  + a D entry. Verify: the default tier.
- T3: the worker wrk_feature_analysis.py — the 18th level
  (up/down, the console log, the TXT report + the CSV, the D-060
  semantics, the no-cache slot) + the no-DB worker suite (the
  synthetic ctx: the no-ops, the happy path, the file pins, the
  failure paths) + the mirror + a D entry. Verify: the default
  tier.
- T4: the full wiring — logistic_model (the worker list + the
  LMContext field + the worker-count test re-pin), the rlm_00
  fixture (all three methods), the full-chain re-pins (the A2030
  log lines + the A2050 VLONG), the hub probe (17 → 18 levels),
  the new probes/verify_feature_analysis.py, the run_utests.sh
  insertion (machine-order position: after the PLOT suites, before
  the full chain), the campaign probe sweep (gated + live), the
  mirrors, the decisions (the campaign D), the overview (Where we
  are + the tables + the next steps), the I-017 status
  progression. Verify: LONG=1 pre-commit + VLONG=1 (the A2050
  chain) + the sweep green.

Verification regime: per task, the default tier at every commit;
the pre-commit is always LONG=1 ./run_utests.sh (the live DB);
VLONG only at T4.

## 7. Files touched (planned)

New: hlp_feature_analysis.py, wrk_feature_analysis.py,
test_hlp_feature_analysis.py, test_wrk_feature_analysis.py,
probes/verify_feature_analysis.py + their five mirrors.
Modified: hlp_config_schemas.py (+ the schema suite),
logistic_model.py (+ the worker-count pin), data/rlm_00.json,
test_lm_worker_full_chain.py, probes/verify_logistic_model.py,
run_utests.sh, notes/ (the decisions, the overview, the ideas).

## 8. Risks / notes

- The SU cost at A2050: ~240 sub-variables → ~28k cross-feature
  pairs × N = 199,932. Pure NumPy: minutes (measured at T1);
  fallback: a numba prange pair kernel (the D-145 K3 precedent) —
  only if the measurement says so.
- The full-chain goldens: the log pins only (the new level's lines
  + the final level name 16/PLOT → 17/FEATURE_ANALYSIS); the model
  files are unchanged (the size bands stand).
- The decisions.md volume is at ~1900 lines (the 2000-line
  rotation at a session boundary, D-118): if the rotation fires
  mid-campaign, the D-numbers stay global (the rule holds).
