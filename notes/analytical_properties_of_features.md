# analytical_properties_of_features.md — the I-017 project

> Status: PLAN CONFIRMED (v2, 2026-09-11). D-156 kickoff;
> D-156b v1; D-156c v2; D-156d the T0c close (Roberto's "Molto
> bene" — the plan locked; ODP-9/ODP-10 closed: the lookup
> table adopted, the C source in scratch). V2 ERRATUM (the T1
> planning reconnaissance): the reordering shifts ONLY the
> POSITIONS cache slot (rlmwf_02 → rlmwf_03 — the file-less
> FEATURES takes the old step 2; INDEXES onward keep their slot
> numbers) → the production one-time cost is ONE DB extraction
> (the downstream checksum lineage survives); the size-band
> re-centering and the hub 17 → 18 count are T18 effects (the
> new config sections + levels), not T1 effects. The rglmw.R
> scratch reference removed by Roberto (the I-016 ruling
> executed). Execution starts with T1 (the detailed plan
> awaits Roberto's explicit OK — the standing workflow).

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

### 2.1 Roberto's confirmations (2026-09-11, v2 round)

- P2, P3, P4, P5, P6: **OK** as designed (v1 §3).
- P1: **OK, with the window correction**: "Sei un po' fuori
  strada ... se stiamo lavorando su un Modello ec=20, tutte le
  partite random si arrestano a ec=20. Game over. Misuriamo mele
  con mele, e pere con pere." — the DB games are ARRESTED at the
  model's ec (the regab query's `ec` parameter, 0..60): the
  synthetic generator MUST play with the same arrest rule, and
  the corpus is the population of that SAME window (no
  unfiltered-vs-filtered mismatch: the v1 ODP-2 risk is gone —
  it becomes a spec constraint, §3.2).
- ODP-1: the corpus default **small and fast: 1e7** ("che gira
  veloce ... se viene omesso, non interessa all'utente,
  teniamolo piccolo"); larger values are config-driven.
- PRNG (new, Roberto): the code that generated the DB uses a
  library HE WROTE, starting from the published work of two
  Japanese researchers — the MT19937 generator of Makoto
  Matsumoto and Takuji Nishimura (the twisted generalized
  feedback shift-register "Mersenne Twister"; Mersenne-prime
  period 2^19937−1 ≈ 10^6000; equi-distributed in 623
  dimensions; passed the DIE-HARD tests). Roberto: "magari
  potremmo pensare che sia un overkill, ma sai è difficile dire
  quanto fatto bene sia il random generator di una libreria
  generica. E pensa quanto lavoro, enorme, ho fatto e stiamo
  facendo, per poi scoprire che i game non sono poi così random.
  Allora mi sono detto, meglio perdere un poco di tempo e avere
  una cosa SOLIDA." → port his C library to Python and reuse it
  as-is (the v1 document's "seeded numpy rng" is RETIRED).

## 3. The design (DRAFT v2)

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

Consequences (accepted costs, once — the T1 planning
reconnaissance refined them, the v2 erratum): the reordering
shifts ONLY the POSITIONS cache slot (rlmwf_02 → rlmwf_03 —
the file-less FEATURES takes the old step 2; the transposition
is of the two adjacent steps 2-3, so INDEXES onward keep their
slot numbers) → on the next production run ONLY the POSITIONS
cache is orphaned (one DB extraction — the rds_checksum
lineage is unchanged, so the INDEXES/WMAPS/DESIGN_MTR/
GENERATE/VLD_POSITIONS caches all still hit); the full-chain
goldens re-pin (the FEATURES/POSITIONS log lines swap, the
step pins 2/3, the cache file name in the positions suite; the
final level STAYS 16/PLOT at T1 — the 17 → 18 hub count and
the size-band re-centering are T18 effects of the new levels +
config sections, the D-148/D-149 precedent); the model file is
BYTE-IDENTICAL at T1 (the config dump is unchanged — no new
fields yet); the stale test setUp comment ("Move to POSITIONS
first, as FEATURES depends on the configuration loaded there"
— I-012) gets fixed as part of T1.

### 3.2 The PRNG library (new, per Roberto's ruling) + the
    random-play generator

The PRNG (the new core module reversi/feature_prng.py — the
mirror docs/src/reversi/feature_prng.md):
- A line-by-line C → Python port of Roberto's MT19937 library
  (the Matsumoto/Nishimura reference implementation): the 624-
  word state, the init-by-seed (the s[] table), the twist +
  temper, the uint32 output. "Tale quale" — no algorithmic
  improvisation; the port preserves the C semantics exactly.
  The C source is needed (ODP-10: where it lives — the original
  repo? a file to bring in?); it is also the VERIFICATION
  oracle.
- Verification (T3, the independent-derivation criterion):
  (1) the EXACT bit-sequence match vs the C library, same seed
  (the golden: a few thousand values exported by the C build);
  (2) the published MT19937 test vectors / the seed-init
  contract; (3) the properties (the period sanity on the small
  scale, the equi-distribution on the first 100k values, the
  seed determinism).
- Integration cost (the design choice that keeps it Python-fast,
  ODP-9): the PERMUTATION LOOKUP TABLE. The random move is NOT
  picked by a PRNG draw per move — instead, at corpus setup, the
  PRNG (seeded, the corpus seed) builds ONE table {n → a
  permutation of 0..n−1} for n = 1..64 (the total cost: 1+2+…+
  64 = 2016 PRNG draws — negligible). At steady state the pick
  is fully vectorized NumPy: for a game with n legal moves, the
  chosen move = table[n][rank of the chosen bit] (the rank via
  the popcount scan, no PRNG in the loop). Deterministic under
  the same corpus seed; the PRNG quality (MT19937) still
  governs the whole distribution (the table IS the seeded
  shuffle). Alternative (rejected for v1): one PRNG draw per
  active game per ply = ~1e9 Python calls for the 1e9 corpus →
  the PRNG becomes the bottleneck (the numba-wrapped twist would
  be mandatory); the lookup table removes the issue.

The generator (the new lm module hlp_random_play.py — the wave
engine + the frequency accumulators):
- Single-game random play (T4): from the initial position, a
  loop over plies: the legal moves (board.py, vectorized), the
  pick via the lookup table, position_make_move (D-140); no
  legal moves → the pass; two consecutive passes or a full board
  → the game over. The ec ARREST rule (the window constraint,
  §2.1): the game is stopped when the board reaches the model's
  ec (the same rule the DB generator uses — the EXACT ec formula
  must be pinned against Roberto's DB code, a T7 detail —
  "mele con mele, pere con pere"); the corpus keeps every ply of
  the arrested game.
- Concurrent waves (T5): a batch of games in parallel (an
  array of positions with a per-game side); per ply, one
  vectorized advance step (the legal moves, the pick, the make,
  the pass flips, the game-over detection, the respawn of the
  finished slots at the initial position). Positions are
  STREAMED to the frequency accumulators — never stored.
- The corpus size (ODP-1): the config total_positions, DEFAULT
  1e7 (the small-fast default); the waves run until the target
  is reached (the last wave is trimmed).
- The frequency accumulators (T7-T8): per analysis unit (§3.4),
  the MARGINAL table (code → count over the whole corpus) for
  EVERY sub-variable (the bincount where the code range allows,
  the unique-merge otherwise); the JOINT table (the (code_u,
  code_v) → count) of every REQUESTED su pair at the
  instance×instance level (P6's matrix).

### 3.3 The FEATURE_ANALYSIS level (the SU level, step 3)

Inputs: ctx.cfg + ctx.feature_set ONLY (no DB, no positions).
Two phases:

Phase 1 — the corpus (the expensive part, CACHED):
- The seeded generator of §3.2 (the PRNG seed = the corpus
  seed; the ec arrest; the wave semantics; the streaming
  accumulation).
- Cache flow: the cache_manager load-or-compute (the .SHA3-256
  sidecar, the 8192-chunk verify — D-071/D-072), the file
  rlmwf_03_FEATURE_ANALYSIS.dat. Consistency signature: the
  feature_set hash + the generation spec (the seed, the
  total_positions, the ec, the generator version, the PRNG
  version) + the su_pairs list (the canonical sorted form).
  NOTE (the P5 interaction): because the joint tables are per
  requested pair, a pair-list change invalidates the corpus
  cache → a full regeneration. The v2 refinement (parked): a
  two-tier cache (the marginals keyed on (features, spec); the
  joints keyed on (+ pairs)) so a pair experiment reuses the
  marginal corpus.
- The corpus is INDEPENDENT of the DB: the first cache level
  whose signature does NOT carry the rds_checksum (it carries
  the feature_set hash instead) — a new kind of cache lineage.

Phase 2 — the statistics (cheap, recomputed on EVERY run,
including the cache-hit):
- per sub-variable (all of them): K_obs (the distinct observed
  codes), the entropy H (bits), H_norm = H/log2(K_obs) (else 0),
  the coverage = K_obs / n_configurations (the theoretical range);
- the never-observed audit (the STOP deliverable, P2): per
  sub-variable, the number of theoretical codes never seen in
  the corpus (n_configurations − K_obs) + the rarity profile
  (the count of codes below small count thresholds) — "the
  configurations that random play never / almost never reaches:
  the weights that can never be learned";
- the requested SU pairs (P6): for each configured feature pair
  (F_i, F_j), the full n_instances(i) × n_instances(j) matrix of
  SU values, from the joint frequencies:
    SU(u, v) = 2·I(u; v) / (H(u) + H(v))   (SU = 0 if the
    denominator is 0); I from the joint counts. Range [0, 1].
  - same-feature pairs (F, F): the diagonal is the variable with
    itself → SU = 1 (OMITTED per the ODP-4 close — the 1s are a
    lock, not a measurement; the off-diagonal entries are
    reported) — the off-diagonal measures the spatial
    correlation between the D8 orientations of the same mask (an
    anisotropy measure, structurally distinct from the
    redundancy signal of the cross-feature pairs — the report
    groups the two kinds).
- The SU is computed from the IDEAL (synthetic) frequencies: a
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

### 3.4 The analysis unit: the (feature, instance) sub-variable

Each design-index column is a categorical variable over the
positions (the design-matrix unit, the unit the weights live on):
the intercept (the constant 0 — degenerate, reported, excluded
from the pairs — the ODP-8 close), each mobility (1 column: the
count popcount(lms&mask) + (popcount(amask) −
popcount(alms&amask)), range 0..k+a), each pattern (n_instances
= the D8 orbit-group columns, the principal base-3 ternary index
over the S squares, range 0..3^(2S)−1; code 0 = the "no match"
configuration, a first-class modeled category with its own
weight → it stays a group everywhere — the ODP-8 close).

P6 refinement (accepted): the SU PAIRS are specified at the
FEATURE level (the names), and the level expands each pair to its
full instance×instance matrix. The marginal dispersion + the
eta²/omega² + the adherence run over ALL sub-variables without a
list (P6: "per tutte le features").

### 3.5 The EFFECT_SIZE level (eta²/omega² + the adherence, step 6)

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
  the biased sample share (up with high K); omega² is the
  unbiased population estimate — the pair is reported together.
- The adherence (c): per sub-variable, the DB configuration
  distribution (the observed codes of the training positions) vs
  the ideal distribution (the corpus frequencies, normalized):
  the chi-square goodness-of-fit (the p-value; the low-expected
  cells are merged into an "other" tail bin until the expected
  count ≥ 5 — the standard technique, a T14 detail) + the KL
  divergence + the total variation distance (the 0..1
  "how different" number, robust) — the fixed trio (the ODP-5
  close, no config whitelist). Console: the top-N most deviant
  features (TV descending).
  Graceful degradation: if the FEATURE_ANALYSIS level was
  disabled (no corpus in the ctx), the adherence is skipped with
  a log note; the eta²/omega² runs (it does not need the corpus).
  The window note (the §2.1 correction): the corpus is the SAME
  ec-arrested population as the DB (mele con mele) — the
  adherence now measures the DB's SAMPLE deviation from the
  ideal window population (the extraction's residual selection,
  e.g. the solvability filter), not a window mismatch.
Outputs: the console + the TXT report (+ the optional CSV). No
cache (a diagnostic; the recompute is seconds). D-060 semantics.

### 3.6 target_level (P4, confirmed)

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
machinery). The semantics is the machine's existing contract:
the state "steps 1..t done" (the target included), the ctx
preserved, the resume = another move_to_step (the caches hot).
This generalizes the P2 workflow: the stop is available at ANY
level, not only after the SU.

### 3.7 The configuration (the PlotConfig pilot pattern, D-149)

    feature_analysis: {
      enable: true,                     # master switch
      corpus: {
        seed: 42,                       # the MT19937 corpus seed
        total_positions: 10000000,      # the ODP-1 default 1e7
        ec: 20                          # the arrest rule (the
                                        # model's ec — the window
                                        # constraint, §2.1)
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
any joint (the default corpus cost at 1e7 — minutes, the ODP-1
small default). An enable false makes the level a no-op (and
EFFECT_SIZE degrades, §3.5). The production A2050/A2030 configs
stay untouched until we opt in (they gain the fields by default,
and the small corpus means the opt-in is cheap). The rlm_00 test
fixture opts in with a TINY corpus (1e4-1e5) + 1-2 pairs (the
chain exercises the level end-to-end; the goldens re-pin).

## 4. The metric details (the kernels, float64, deterministic)

- Entropy / MI / SU: from the frequency tables (the counts, not
  the positions) — H = −Σ p log2 p; I = Σ p_xy log2(p_xy/(p_x
  p_y)); SU = 2I/(H_u+H_v), 0 on the 0 denominator.
- ANOVA: §3.5 (the v0 formulas stand).
- Adherence: the chi-square (the merged-tail p), the KL
  (Σ p_ideal log(p_ideal/p_db), the 0·log 0 = 0 convention, the
  zero-DB-probability cells handled by the same tail merge), the
  TV = ½·Σ |p_db − p_ideal| (in [0, 1]).

## 5. The workflow the design enables (the point of it all)

1. CONFIG → FEATURES → FEATURE_ANALYSIS (a fresh feature set:
   the corpus is generated ONCE — the cached run; a feature-set
   change: a new generation; the 1e7 default is minutes).
2. STOP (target_level = "FEATURE_ANALYSIS"): read the audit —
   the never-observed configurations per pattern (the
   over-parameterized features), the dispersion (the degenerate
   ones), the requested SU pair matrices (the redundant
   features). Decide: fix the feature set (re-run, the corpus is
   cheap if the features are unchanged) or continue.
3. Continue → POSITIONS (the DB) → INDEXES → EFFECT_SIZE: the
   eta²/omega² per feature (which features actually move the
   game value on the REAL data) + the adherence (how close the
   DB set is to the ideal SAME-WINDOW population — the
   extraction's residual selection, quantified). Another
   decision point (the target_level = "EFFECT_SIZE" stop).
4. The full chain → PLOT.

## 6. The ODP register

Closed (the v1 list, resolved in the v2 round, 2026-09-11):
- ODP-1 corpus size: the DEFAULT 1e7 (the small-fast ruling);
  config-driven beyond.
- ODP-2 the DB sampling window: RESOLVED by Roberto — the DB
  games are arrested at the model's ec (ec=20 for that model);
  the generator plays the same arrest rule → mele con mele.
  (The exact ec formula is pinned at T7 against the DB code.)
- ODP-3 level names: FEATURE_ANALYSIS + EFFECT_SIZE (confirmed
  with the P2/P3 OK).
- ODP-4 the same-feature SU diagonal: omitted (the 1s are a
  lock, not a measurement); the off-diagonal reported.
- ODP-5 the adherence metrics: the fixed trio (chi-square + KL
  + TV), no config.
- ODP-6 target_level: the field + the "last" default + the
  run() facade override — confirmed.
- ODP-7 the pair list in the corpus cache signature: the v1
  single signature confirmed (a pair change → the regeneration;
  the two-tier cache parked v2).
- ODP-8 code 0 "no match" stays a group; the intercept excluded
  from the pairs, kept in the tables — as designed.

Closed in the T0c close (2026-09-11, Roberto's "Molto bene" +
the C source delivery):
- ODP-9 the move-pick: the PERMUTATION LOOKUP TABLE adopted
  (the seeded {n → permutation of 0..n−1} over n = 1..64,
  2016 total PRNG draws, the pick fully vectorized — the
  PRNG stays the quality anchor, the throughput is NumPy's).
- ODP-10 the C source: DELIVERED in scratch/ — prng.c/h
  (the library) + the dependencies bit_works.c/h +
  time_utils.c/h (present for the build, NOT ported —
  Roberto: "portiamo solo prng") + Roberto's own C test
  suites ut_prng.c (977 lines) + ut_bit_works.c (the
  verification oracles for T2/T3).

Open: none.

## 7. The cost model (Nia's honest numbers, to be measured at T10)

- Generation: the waves are cheap (the vectorized board API; a
  wave of 1e5 concurrent games ≈ seconds of ply work). The
  default corpus 1e7 ≈ 2-4 waves (a game at ec=20 yields a few
  dozen positions) ≈ MINUTES. 1e9 ≈ 100× ≈ ~30 min.
- Accumulation: per wave, the marginal tables of ~240
  sub-variables (the bincount where the code range allows, the
  unique-merge otherwise) + the joints of the requested pairs
  (few) ≈ 1-3 min/wave at A2050 scale. 1e7 ≈ minutes; 1e9 ≈
  1-3 h.
- PRNG (the ODP-9 lookup): 2016 draws at setup — negligible;
  the alternative (the per-move draws) would be ~1e9 Python
  calls → the bottleneck (hence the lookup).
- Corpus memory: never stored (the streaming); the frequency
  tables at most GB-scale in the worst case (the distinct codes
  per sub-variable are bounded by the geometry, in practice far
  below 3^(2S)).
- The EFFECT_SIZE recompute on a cache hit: seconds.
- The one-time campaign costs: the production cache orphaning
  (the slot shift) → one A2050 recompute (~1 min chain + the DB
  extraction); the size-band re-centering (the config dump
  growth, D-147); the full-chain goldens re-pin (the log lines +
  the hub 17 → 18).

## 8. Tasks (one focused commit each, in sequence — the v2
    granular split, per Roberto's "più fai granulare più siamo
    lucidi")

- T0 (done): the document v0 (D-156).
- T0b (done): the document v1 (D-156b).
- T0c (DONE, confirmed 2026-09-11, D-156d): the document v2 —
  the ODP closure, the ec window constraint, the MT19937 PRNG
  design, the granular task split (D-156c) + the T0c close
  (D-156d): Roberto's plan confirmation, the ODP-9/10 closure,
  the v2 erratum (the slot shift is POSITIONS-only), the
  rglmw.R removal.
- T1: the reordering (I-012 realized) — the worker list
  FEATURES → POSITIONS + the slot shift + the golden re-pin
  (the full-chain A2030/A2050) + the hub probe (the order
  re-pin; the 17 → 18 count lands in T18 with the new levels) +
  the stale test comment fix + the run_utests.sh order.
  Verify: LONG=1 + VLONG (the A2050 chain).
- T2: the PRNG port — the line-by-line C → Python MT19937 in
  the new core module reversi/feature_prng.py (the s[] seed
  init, the twist, the temper, the uint32 output) + the mirror.
  (The C source per ODP-10.)
- T3: the PRNG verification suite — test_feature_prng.py: the
  EXACT bit-sequence golden vs the C library (same seed), the
  published test vectors / the seed-init contract, the
  properties (the seed determinism, the equi-distribution on
  the first 100k) + the test-doc mirror.
- T4: the single-game random play — the hlp_random_play.py game
  loop (the initial position, the legal moves, the pick, the
  make, the pass, the game over, the ec arrest) + the no-DB
  micro-suite (the hand-counted short-game trace: the moves,
  the plies, the ec values, the arrest).
- T5: the concurrent wave engine — the batch of games in
  parallel (the per-advance vectorized step, the respawn of the
  finished slots, the position stream) + the no-DB micro-suite
  (the small seeded wave, the game count + the ply count
  verified by the single-game replay).
- T6: the vectorized move pick — the permutation lookup table
  (the seeded build, the n = 1..64) + the pick kernel (the rank
  selection) + the tests (the table properties: the valid
  permutations, the reproducibility, the pick distribution on a
  tiny corpus) + the ODP-9 landing.
- T7: the marginal frequency accumulator — the per-sub-variable
  (code → count) streaming accumulation (the bincount / the
  unique-merge split) + the no-DB micro-suite (the toy corpus,
  the hand-counted frequencies) + the ec formula pin (the
  Roberto-DB cross-check, the §2.1 constraint).
- T8: the joint frequency accumulator — the per-requested-pair
  instance×instance (code_u, code_v) → count streaming
  accumulation + the no-DB micro-suite (the toy pair, the
  hand-counted joint).
- T9: the PRNG integration test — the full generator with the
  MT19937 seed: the corpus reproducibility (same seed → the
  same frequency tables, the different seed → different) + the
  small end-to-end corpus on a 2-3 feature set (the marginals
  hand-checked).
- T10: the throughput probe (scratch) — the 1e7 (and, if the
  measurement invites, the 1e8) corpus on a real feature set:
  the generation + the accumulation split timing, the §7 cost
  model check.
- T11: the SU/entropy/MI kernels — the from-frequency-tables
  math (the H, the I, the SU, the 0-denominator guard) + the
  no-DB micro-suite (the hand-computed toy tables).
- T12: the dispersion + the never-observed audit — the K_obs /
  H / H_norm / coverage per sub-variable + the audit (the
  n_configurations − K_obs, the rarity profile) + the micro-
  suite.
- T13: the ANOVA kernels — the eta² / omega² per sub-variable
  (the guards: the K=1 degeneracy, the K>N ValueError) + the
  micro-suite (the hand-computed toy groups).
- T14: the adherence kernels — the chi-square (the merged-tail
  rule), the KL, the TV (the 0-log-0 convention) + the
  micro-suite (the hand-computed toy distributions).
- T15: the config — the feature_analysis + effect_size sections
  + the target_level field (the corpus spec incl. the ec, the
  su_pairs fail-fast vocabulary + the canonical dedupe, the
  validators) + the schema tests + the mirrors.
- T16: the FEATURE_ANALYSIS worker — the step 3: the cache
  manager flow (the new signature kind: the feature_set hash +
  the spec + the pairs — no rds_checksum), the phase-2
  recompute on the cache hit, the TXT + the CSV reports, the
  ctx publication, the D-060 semantics + the no-DB worker suite
  (the no-ops, the happy path, the file pins, the failure
  paths).
- T17: the EFFECT_SIZE worker — the step 6: the eta²/omega² +
  the adherence reports, the graceful degradation + the no-DB
  worker suite.
- T18: the full wiring — the logistic_model (the 18-level list,
  the new ctx fields, the run() facade + the target_level, the
  worker-count test re-pin), the rlm_00 fixture (the tiny
  corpus + 1-2 pairs + the target_level "last"), the full-chain
  re-pin (the A2030 log + the A2050 VLONG + the size bands),
  the hub probe (17 → 18), the new probes (the
  verify_feature_analysis + the verify_effect_size), the
  run_utests.sh insertion. Verify: LONG=1 + VLONG.
- T19: the campaign close — the probe sweep (gated + live),
  the mirrors wave, the decisions (the campaign D), the
  overview (Where we are + the tables + the next steps), the
  I-012 → done + the I-017 progression.

Verification regime: the default tier at every commit; the
pre-commit always LONG=1 ./run_utests.sh (the live DB); VLONG
at T1 (the reordering touches the chain) and T18.

## 9. Files touched (planned, v2)

New: reversi/feature_prng.py (the core MT19937 port) + the
mirror, hlp_random_play.py (+ the mirror, the generator + the
accumulators), hlp_feature_analysis.py (+ the mirror, the
statistics kernels), wrk_feature_analysis.py (+ the mirror),
wrk_effect_size.py (+ the mirror), test_feature_prng.py (+ the
mirror), the hlp micro-suites (the test_hlp_random_play.py +
the test_hlp_feature_analysis.py and their mirrors),
test_wrk_feature_analysis.py (+ the mirror),
test_wrk_effect_size.py (+ the mirror),
probes/verify_feature_analysis.py, probes/verify_effect_size.py.
Modified: hlp_config_schemas.py (+ the schema suite),
logistic_model.py (+ the worker list + the ctx + the run()),
data/rlm_00.json, test_lm_worker_full_chain.py,
probes/verify_logistic_model.py (the hub), run_utests.sh,
notes/ (the decisions, the overview, the ideas: the I-012 →
done, the I-017 progression).

## 10. Risks / notes

- The reordering is the invasive step (T1 is done BEFORE the
  analysis code lands, on its own, re-pinned and green — the
  rest of the campaign builds on the new order).
- The PRNG port is the trust foundation: the bit-exact C
  comparison (T3) is a hard gate — if the C source is not
  available (ODP-10), the fallback oracle is the published
  MT19937 reference vectors (the numpy legacy RandomState is
  MT19937 and can serve as the cross-oracle, flagged as such).
- The ec arrest formula (T7): a silent mismatch would corrupt
  the whole corpus (the wrong window) — it is pinned against
  the DB code in the same task that lands the accumulator, and
  the micro-suite trace shows the ec values by hand.
- The chi-square on the wide configuration spaces: the
  merged-tail cell rule is a standard technique, but it is a
  judgment call on the p-values — the report shows the merge
  count (transparency), the metric stays descriptive.
- The corpus generation is the only long-running compute: if
  the T10 measurement is far from the §7 model, the wave size /
  the accumulation technique (a numba dict pass) adapt BEFORE
  T16 (the cache absorbs the re-run).
- The decisions.md volume is near the 2000-line rotation (the
  D-118 rhythm): the rotation may fire mid-campaign at a session
  boundary; the D-numbers stay global.
