# Decisions log — volume 004 (closed)

Format: D-NNN | date | decision | rationale

Volume 004: D-258…D-300 (2026-09-19 → 2026-09-23); closed at the D-333 rotation (the open log had 4460 lines > the
amended 1000 cap); the open log continues in notes/decisions.md.

D-258 | 2026-09-19 | P2: the worker rename FEATURE\_ANALYSIS -> SU\_ANALYSIS (the interrupted session's step, resumed;
         the P1-P5 list). (1) THE IDENTIFIERS — the module `wrk_feature_analysis.py` -> `wrk_su_analysis.py`, the
         factory `wrk_feature_analysis()` -> `wrk_su_analysis()`, the Worker name "FEATURE\_ANALYSIS" -> "SU\_ANALYSIS"
         (so the step-3 cache slot becomes `rlmwf_03_SU_ANALYSIS.dat`), the config class `FeatureAnalysisConfig` ->
         `SuAnalysisConfig` with the LMConfig field `feature_analysis` -> `su_analysis`, the ctx blackboard field
         `feature_analysis_tables` -> `su_analysis_tables`, the config defaults `dir_name` "feature\_analysis" ->
         "su\_analysis" + `report_file_name` "feature\_analysis\_report.txt" -> "su\_analysis\_report.txt", the test
         module `test_wrk_feature_analysis.py` -> `test_wrk_su_analysis.py` (+ its class `TestWrkFeatureAnalysis` ->
         `TestWrkSuAnalysis`), the fixtures (rlm\_00/rlm\_05/rlm\_06: the section key, the dir/report names, the
         `target_level` values), the probes (verify\_logistic\_model's V3c level list, verify\_hlp\_indexes' C2 file
         list), the runner comments. The two mirror docs move with their sources (git mv + the content re-pin). (2) THE
         KEPT NAME — `hlp_feature_analysis.py` (+ its suite and mirror) KEEPS its name on purpose: it is the SHARED
         analysis-kernels module (the SU/entropy/MI + the dispersion/audit for the SU\_ANALYSIS level, the ANOVA + the
         adherence for the EFFECT\_SIZE level), so its name states the FAMILY, not a level; the module docstring says so
         explicitly and the overview row follows. (3) THE P1 LEFTOVERS FOUND WHILE SWEEPING — the rlm\_05/rlm\_06
         `description` still said "the G0 corpus"; the two mirrors still pinned the generator version "g0-1" (the D-254
         bump was recorded in the code and the decisions, never in the docs) and the worker mirror still listed "the
         full wiring" as an open issue (done at T18); the ideas.md I-007 entry still named `wrk_feature_analysis`. All
         re-pinned. (4) THE ARTIFACT CONSEQUENCE — the cache FILE NAME is derived from the worker name, so the D-254 1e7
         corpus (build/su\_corpus\_1e7, gitignored) sat under the old name: the area was migrated (the config keys, the
         cache file + its rewritten SHA3-256 sidecar, the report dir/file) and VERIFIED end to end at the production
         scale: the run to SU\_ANALYSIS regenerated the corpus once (51.2 s, the 47 sub-variables' statistics included)
         and the second run HIT the cache (0.7 s, the phase-2 recompute + the report rewritten in
         `build/su_corpus_1e7/su_analysis/`). The corpus BYTES are untouched by a rename — only the file name moved. (5)
         THE DISCOVERY (a real gap, recorded not fixed: source changes need Roberto's GO) — `LMConfig.target_level` is
         declared, documented and validated as a string, and read by NOTHING: the design section 3.6 (P4) asks for a
         `LogisticModel.run(target_level=...)` facade entry that resolves it through `move_to_step`, and no `run()`
         exists (the facade exposes move\_to\_step / move\_to\_last only), so a bogus level name passes the CONFIG step
         and every client chains the moves by hand. Recorded as I-019 (ideas.md) + an Open-issues bullet in the
         hlp\_config\_schemas and logistic\_model mirrors. (6) VERIFICATION — the LONG tier green, the probe sweep 21/21
         (with one re-pin: verify\_hlp\_indexes C2 compares a SORTED name list, and "rlmwf\_03\_SU\_ANALYSIS.dat" sorts
         BEFORE "su\_analysis" where the old "feature\_analysis" sorted after — the expected list was reordered, not the
         check weakened), the doc audit at 9 pre-existing findings.

D-259 | 2026-09-19 | P5: the two missing probes — verify\_su\_analysis.py + verify\_effect\_size.py (the I-017 T18's
         last item; the P1-P5 list's close). (1) THE GAP — the I-017 project plan (the project doc §9, T18) named two
         probes that were never written (`verify_feature_analysis` + `verify_effect_size`), so the two analysis levels
         were the only pipeline levels with a worker, a suite and a mirror but NO campaign-level verification. With
         the D-258 rename the first is `verify_su_analysis`. (2) `probes/verify_su_analysis.py` (43 checks, 3.8 s) — A:
         the module structure (the factory, the no-DB discipline of the design §3.3, the three cache constants read from
         the module, the D-252 wave-size cap, the whitespace hygiene). B: the INDEPENDENT re-derivations with no worker
         involved — the corpus harvested count, the ec arrest recomputed as 64 - popcount over the WHOLE corpus, the
         marginal vs the FeatureSet's own batch bincount (a different route than the streaming accumulator), the joint
         vs a pure-python Counter, the SU values vs the RATIO-FORM mutual information sum p(u,v) log2(p(u,v)/p(u)p(v))
         (the DEFINITION — the kernel uses the identity H(u)+H(v)-H(u,v), so the two derivations share no formula) plus
         pure-python entropies, and the cache signature vs an independently recomputed feature\_set hash + its
         same/different semantics. C: the live rlm\_00 run — the step-3 stop, the flat cache file + its binio sidecar,
         the ctx publication, the cached signature vs the live one, the cached marginal totals, the report's 15
         sub-variable lines and its SU lines vs pure-python math, the phase-2 recompute on the cache HIT (proved by
         deleting the report before the second run and checking it comes back byte-identical while the cache file is
         untouched), the down, and the opt-in absence of BOTH artifacts. F: the runner, the RENAME-COMPLETENESS sweep
         (no FEATURE\_ANALYSIS/feature\_analysis left in src/docs/probes/tools once the shared-kernels family is
         discounted), the mirrors, the EFFECT\_SIZE consumer contract. (3) `probes/verify_effect_size.py` (29 checks, 30
         s) — A: the structure (the factory, the no-cache discipline, the two kernel imports, the degradation branch).
         B: the independent math — the ANOVA vs the F-identity eta² = (K-1)F/((K-1)F + (N-K)), vs scipy's f\_oneway,
         plus the bias relation eta² >= omega² (algebraically forced) and the negative omega² of a null effect; the
         adherence trio vs pure-python formulas with the merge rule reimplemented (E = p\_ideal \* n\_db), the Pinsker
         bound TV <= sqrt(KL/2), the disjoint-support alignment (chi2 +inf, p 0, KL +inf, finite TV). C: the mock-ctx
         report facts no test carries — the degradation REPORT line, the ANOVA numbers vs the independent recompute, the
         adherence rows vs the independent trio, and the CSV path (the export\_csv flag had NO test). D: the LIVE A2050
         tier WITHOUT a DB — the build area's cached corpus + POSITIONS + INDEXES are symlinked under build/tmp and the
         config is run to EFFECT\_SIZE (the report's 47 sub-variables, every ANOVA line recomputed from the cached
         indexes + game values, scipy's f\_oneway on the mobility column over the full 2M positions, every adherence row
         recomputed from the cached corpus marginal, the eta² >= omega² invariant on the real data, no cache file); the
         tier SKIPS itself when the gitignored build area is absent. F: the cross-file facts. (4) THE CLASSIFICATION
         DISCIPLINE (probe\_rules §3) — the facts a test already pins through the same path are NOT repeated: the
         factory names, the enable no-ops, the cache-hit log, the ANOVA line count, the degradation log, the report
         existence, the mock-ctx down. (5) THE FINDINGS the writing produced: (a) the report prints
         `chi2 0.00 (p nan, merged N)` when the merged tail collapses to a single cell (df < 1) — a real behavior of
         `chi_square_goodness` the probe's parser must accept; (b) the report writes the adherence lines for ALL the
         sub-variables while its own header says "top {top\_k\_adherence}" — the top-k bound applies to the CONSOLE
         lines only (`adherence_lines[:top_k]` in the log vs the full list in `_write_report`): a wording defect
         recorded in the wrk\_effect\_size mirror's Open issues, NOT fixed (a source change needs Roberto's GO); (c) the
         cached A2050 1e7 area makes a DB-FREE EFFECT\_SIZE run possible (the probe's tier D) — the caches are the
         inputs. (6) VERIFICATION — the full sweep 23/23 green (the two new probes included), the LONG tier green.

D-260 | 2026-09-19 | I-019 executed: the target-driven `run()` + the `target_level` it consumes (Roberto: "La I-019 va
         eseguita fino in fondo, era nata quando abbiamo constatato che lo step SU\_ANALYSIS puo essere molto lungo, e
         non e' detto che poi valga la pena andare avanti. Ma potrebbe essere utile per ogni LEVEL. Quindi va completata
         la analisi, vedere cosa c'e', cosa manca e fare gli appropriati tests"). (1) THE ANALYSIS — what existed:
         `LMConfig.target_level` (default "last", the I-017 design section 3.6 / P4) was declared, documented and
         validated as a plain string, and read by NOTHING; the machine already accepted any worker NAME
         (case-insensitive, the fail-fast ValueError) or an int index in `move_to_step`, and `move_to_last()` existed.
         What was missing: the single consumer — the facade entry that turns the field into a move. The design asked for
         `LogisticModel.run(target_level=None)`. (2) THE IMPLEMENTATION — the driver lives in `BaseModel` (the generic
         facade base, so EVERY domain facade inherits it: DeepNetworkModel included), and the DOMAIN part is one hook:
         `_configured_target_level()` returns None in the base and `cfg.target_level` in LogisticModel (via getattr, so
         an absent field or a context without a loaded config resolves to None). `run()` = (a) `move_to_step(1)` when
         the machine is still at the sentinel — the CONFIG level must run before the domain can name its target; (b) the
         target = the explicit argument, else the hook, else the last step; (c) the string "last" (ANY case) and a blank
         value mean the whole pipeline → `move_to_last()`; anything else → `move_to_step(target)`, which resolves names
         case-insensitively and accepts an int index — so ANY level is a legal stop, not just SU\_ANALYSIS. (3) THE
         SEMANTICS CHOSEN (and why it deviates from the design's literal "move\_to\_step('CONFIG') always first"): the
         unconditional CONFIG move would run the down() of every intermediate level on each call, destroying the
         published ctx artifacts — exactly what the motivating case forbids ("stop after the long SU\_ANALYSIS, inspect,
         then decide"). The `current_step < 1` guard keeps the design's invariant (the cfg IS loaded before the hook is
         read) while making a second `run()` with a deeper target a RESUME: the levels already done are not re-run, the
         ctx artifacts survive, the on-disk caches stay hot. A target BELOW the current step still moves back, running
         the down() steps (the machine's D-060 contract) — the caller asked for it. (4) NO NEW VALIDATION MACHINERY (the
         design's ruling): an unknown level name raises the machine's ValueError, a wrong-typed target its pinned
         TypeError, and the CONFIG level does NOT pre-validate the field. (5) THE CONFIG DESCRIPTION reworded (the field
         now names its consumer + the blank-means-last rule); it does not enter the config dump, so no fingerprint and
         no cache signature moves. (6) THE TESTS — `test_logistic_model.py` 17 → 29 (12 new): the mocked resolution
         cases (the explicit target with the machine history pinned, the config field honored, the
         "last"/case/blank/absent resolutions, the argument-over-field precedence, the resume with the no-op same-target
         call, the backward target's down steps, the unknown-name ValueError, the wrong-type TypeError, the generic base
         default on a bare 2-worker pipeline) + the NEW `TestRunFacadeOnARealConfig` class (the REAL pipeline, no
         factory mocks, the rlm\_00 fixture with target\_level set by a config copy: FEATURES from the field,
         SU\_ANALYSIS from the argument with the corpus tables published, and the resume leaving the tables the SAME
         object). (7) THE VERIFICATION AT SCALE — the 1e7 A2050 build config (`target_level: "SU_ANALYSIS"`) driven by
         `run()`: 0.80 s to the stop with the corpus cache HIT, the tables published, then `run("EFFECT_SIZE")` resumed
         with ONE SU\_ANALYSIS up and ZERO downs (the corpus never reworked). (8) THE DOCS/RULES — base\_model.md (the
         run() row + the hook + V5 + the Architecture note), logistic\_model.md (the two Facade rows + the target-driven
         invariant; the I-019 Open issue is GONE; a stale "17 active levels" fixed), hlp\_config\_schemas.md (the field
         line + Open issues → None), the test mirror (2 classes / 29 tests + the new goldens), the overview (the 4 rows
         + the "Where we are" bullet + the backlog line: I-019 executed), and a NEW rules.md line in the "Pipeline
         contracts (RLM)" register: the stop is target-driven through `run()`, the target step IS executed, the resume
         does not reset. The hub probe gains the V9 `run('POSITIONS')` boundary label (the empty-config failure surfaces
         through the new entry too).

D-261 | 2026-09-19 | The line-reference retirement in the mirror docs (Roberto: "uno per volta controlla tutti i
         documenti in docs, e verifica se sono aderenti allo stato del codice ... Se i docs markdown riportano uno stato
         diverso da quello trovato nel codice, aggiornali"). (1) THE MEASUREMENT — 38 of the 95 mirrors carried 423
         inline line references ("`factory` (L71)", "the L103 note", "(L216 — ...)"); a mechanical cross-check of 112
         name/line pairs found 25 already DRIFTED (the cited line no longer holds the named object) — the refs were
         stale in ~22% of the cases and every code edit re-opened the debt. (2) THE RULE — notes/docs\_rules.md §3.7
         already prescribed the opposite: the line reference is an OPTIONAL appendix, default OFF ("Default: no line
         numbers in the doc"), and NO mirror had the appendix section. Roberto chose the rule: remove them all. (3) THE
         SWEEP — the 268 parenthesized-only refs ("(L50)", "(L87-90)", "(L143, L147)") removed by a deterministic pass;
         the 155 EMBEDDED ones ("the L103 note", "(L216 — the empty-suffix guard)", "(each L31)", the dense line maps of
         binio.md / cache\_manager.md) rewritten by hand, keeping the CONTENT (the descriptors survive: "the
         no-validation note", "the by-design comment", "the ruling comment") and dropping only the coordinates; the
         prose re-wrapped to the house width with tools/notes\_format.py (CONTENT OK per file: the token sequence is
         unchanged, so no word was lost). VERIFIED: 0 refs left in docs/, the doc audit back at the 8 pre-existing
         findings (2 over-120 + 6 size), and a token-level diff against HEAD showing ONLY the ref removals + the 6
         hand-rewrites.

D-262 | 2026-09-19 | The docs-vs-code consistency sweep (Roberto: "uno per volta controlla tutti i documenti in docs, e
         verifica se sono aderenti allo stato del codice, credo che ci siano diverse incostistenze ... alla fine di
         questo check tutto deve essere consistente"). (1) THE METHOD — 95 mirrors audited against the code by 10
         parallel readers (each doc + its source + its tests + its probe), every claim classified (WRONG-API /
         WRONG-COUNT / WRONG-STRUCTURE / DEAD-POINTER / STALE-OPEN-ISSUE / MISSING-FACT / FORBIDDEN-HISTORY /
         MISLEADING) with the evidence; the mechanical layers ran in parallel (the line-reference drift of D-261, the
         per-class test counts vs the AST, the file/suite counts vs tools/suite\_audit.py, the `__all__` coverage of
         every API section, the "pinned by" pointers vs the real test methods and probe checks, the ctx-field names).
         (2) THE DOMINANT DEFECT FAMILY: the I-017 insertion (SU\_ANALYSIS at step 3 + EFFECT\_SIZE at step
         6, D-186/D-187) and I-018 (the four published series fields) left ~25 docs quoting the PRE-18-LEVEL pipeline —
         the level ordinals ("the 6th/7th/8th level" for WMAPS/DESIGN\_MTR/ZED), the step pins in the test docs (8/9 for
         GRADIENT/OPTIMIZE, 12/13 for VALIDATE/ANALYTICS, 6/7 for DESIGN\_MTR/ZED, 9/10 for OPTIMIZE/GENERATE), the
         worker lists ("the 7-worker list"), the cache-consumer ordinals (SU\_ANALYSIS was never counted: INDEXES
         "SECOND" -> THIRD, WMAPS "THIRD" -> 4th, DESIGN\_MTR "FOURTH" -> 5th, GENERATE "5th" -> 6th, VLD\_POSITIONS
         "6th" -> 7th), the flat-file slot lists ("skips 03/07/08/12/13" — those ARE the cache levels), the factory
         counts ("the 15/16 factories" -> 18, "lm\_worker\_\*" -> `wrk_*`), the LMContext shape (42 -> 46 fields, 34 ->
         38 data artifacts, 8 -> 9 checksum fields) and the suite counts (test\_opt\_lbfgs 13 -> 14, test\_pattern 64 ->
         65, test\_wrk\_gradient 2 -> 4, test\_prng 19 -> 22 with the whole `TestPickOneFromSet64` class missing,
         test\_wrk\_su\_analysis 8 -> 9, hlp\_analytics 523 -> 544 lines, wrk\_analytics 86 -> 89). (3) THE STALE
         GOLDENS: the six A2030 + six A2050 EF literals and the vld[42] value in client.md (all superseded by
         the D-243..D-246 re-pins), the two `w_dense` sha3 literals and the size bands in model\_weights.md, the two
         file-report masks in test\_wrk\_analytics.md, the split hash in test\_wrk\_vld\_positions.md, the space-broken
         hashes in hlp\_generate.md / wrk\_generate.md / test\_hlp\_design\_matrix.md, the stale `w_checksum` golden in
         wrk\_save.md (probe C5), the size band there, the 17-key -> 15-key checkpoint dict, the 71 -> 74 `__all__`
         names in board.md, the "the note" pointers left by the D-261 strip, and the dead pins (probe checks deleted
         at D-106, tests renamed, the archive-only V1-V9 / V3-V4 facts of mobility / opt\_lbfgs, the scratch script in
         board.md, the `verify_wrk_features` B11, the `wrk_plot` outlier report that lives in VALIDATE). (4) THE
         FORBIDDEN HISTORY removed (docs\_rules §4): the campaign tags in the prose (R1/R2/R3/R6/M2-M5, "the campaign
         level", the "step-3 class c deletions"), the pre/post contrasts ("no longer re-derives", "is now the second
         cost center", "the CWD-relative mkdtemp are gone", "the v1 sha3 literal is obsolete", "checked by hand"), the
         archived-analysis pointers (binio, test\_feature, mobility, test\_lm\_worker\_full\_chain's measurement
         narrative) and the D-numbered H1 of tags.md. (5) THE STRUCTURAL CORRECTIONS beyond the drift: the pattern.md
         Burnside formulas (n\_invariant = 3^orbits, n\_unique = the Burnside average — not the doc's two formulas), the
         `pack_plan` attribute (not `p_masks`/`u_masks`/`p_shifts`), the fused kernel's real shape (N, 8) with no
         transpose and the inlined pack, the PatternType 12 members (no `NONE`), mobility's `ms.names` property (the doc
         called it a method), the `bitboard_count` dual signature + the list-typed label tables + the
         `position_empty_count` row in board.md, the `njit` decorator split (4 array impls parallel+cache, 4 scalar
         `inline='always'`), the cache\_manager consumer list, the `data_checksum` flow, the opt\_lbfgs kwarg/scalar
         counts (16 kwargs / 8 config scalars) and the FixedSizeMaxList window (min\_grad\_count=3, not m), the
         `np.unique` (not bincount) adherence counts, the wrk\_plot inputs (the published series, not the forward-pass
         ctx fields) and the wrk\_vld\_positions numpy import. (6) THE REGISTERED RESIDUE (not fixed here, reported to
         Roberto): the CODE COMMENTS that carry the same stale ordinals (test\_wrk\_validate.py "the rlmwf\_12 slot",
         wrk\_plot.py / verify\_plot.py "the 17th level", test\_wrk\_client\_check.py "the 16th level",
         test\_wrk\_analytics.py "13-level chain") — a source change, left to his call; the unpinned invariants (prng's
         four bullets, hlp\_wave's four, regab's V4/V5, binio's float32 specials, the opt\_lbfgs 3-WARN diagnostics)
         which now SAY they are unpinned instead of pretending a pin; and the size-budget findings (7, all
         pre-existing).

D-263 | 2026-09-19 | The execution of ALL the remaining fix items from the independent re-verification (Roberto: "Sì
         grazie, esegui tutti i fix. Procedi." — the source-side stale comments explicitly included, rule 3 overridden
         for comment/docstring/description-only edits). Method: 8 parallel fix agents on disjoint file sets (the
         verify-then-edit protocol — every item re-verified against the code before the minimal surgical edit) + 13
         direct residual edits for the out-of-scope findings the agents flagged. Committed as the "D-263 (part 1..8)"
         series. (1) THE CRITICAL FACTS: regab.md now states the real SQL contract (the query is built by str.format()
         interpolation with a single-string execute — NO parameter binding; the StatusArgument validator enforces length
         3 ONLY, so a quote inside a 3-char status passes validation and reaches the SQL as-is; V4 reworded to the true
         contract), pattern.md (no `snames_ts` attribute, `type_info` not `type`, the flat one-line rendering not "the
         2-D diagram", the verified @validate\_call decoration set with the NON-strict PatternSet ctor, lm/hlp\_gate.py
         added to the consumers), the FOUR analytics context attributes (train\_dense\_rn was the missing 4th) + the
         22-line span arithmetic (the 2 worker INFO lines as endpoints + the 2 data-module INFO + 18 header lines), the
         unpinned "1100× speed ratio" dropped from wrk\_client\_check.md + client.md (test\_client prints b/s only — no
         ratio is pinned), model\_weights (the client suite constructs a ModelWeights directly). (2) THE GOLDENS: the 7
         mid-hex space-broken sha3\_256 literals repaired byte-exact (test\_hlp\_generate, test\_hlp\_optimize ×2,
         test\_hlp\_wmaps, test\_hlp\_zed, test\_wrk\_plot, test\_wrk\_generate). (3) THE TOOLS ZONE: opt\_lbfgs (17
         parameters = fg + x0 + 15 defaulted: the 8 config scalars
         c1/c2/min\_grad/min\_p\_fun\_decrease/max\_iters/m/log\_every\_n/save\_every\_n + the logger/save\_fn hooks +
         the 4 warm-start initial\_sl/initial\_yl/initial\_rho/initial\_iter + debug\_plot; the worker call passes 16
         kwargs; the "alpha-scaling" and "w\_init" naming never existed), state\_machine (the 14-char live line, 5+1+8),
         binio (the checksum is step 2), prng (the corpus is generated by the SU\_ANALYSIS level). (4) THE STEP/LEVEL
         DRIFT across the worker/hlp docs: the 19-worker 0-based map (INDEXES the 5th active level + THIRD cache
         consumer, WMAPS the 7th + FOURTH, DESIGN\_MTR step 8, the SU\_ANALYSIS + EFFECT\_SIZE chain insertions, the 7
         rlmwf\_materializers 03/04/05/07/08/12/13, the db\_long\_gate naming, the 19-worker chain to step 18 / PLOT,
         the seven fixtures, the wrk\_plot true inputs (the 5 ctx attributes, published by
         POSITIONS/ANALYTICS/VALIDATE/VLD\_POSITIONS/CONFIG), the 10 non-cache levels — OPTIMIZE HAS its config-named
         checkpoint cache, so PLOT is the 10th non-cache level on the rlmwf\_18 slot). (5) THE TEST DOCS: the step pins
         (GENERATE step 12, the 13-level chain), the tier\_vlong gate, the 121-row bulk, the 10 scalars, the 5
         data-checksum tests (4 over the helper classes), the plain Context(), one uint64 draw per non-empty pick, the
         two real TestStateMachine full-message pins (the E2/E3 successors), the 15-level chain in test\_wrk\_analytics,
         and the "class (line)" header retirement FINISHED (the last nine test docs). (6) THE FORBIDDEN HISTORY: the
         last campaign tags and provenance phrasings removed (tags.md, the hlp test docs, the R1 tags, the "legacy repo"
         phrasing in logistic\_model.md, the pre/post contrasts). (7) THE PROBE COUNTS (house convention N = check()
         calls, excluding the def line and comments): verify\_hlp\_indexes 53 → 52, verify\_wmaps 54 → 53, verify\_plot
         16/17 → 18 (18 call sites, 17 labels — C4 ×2), verify\_generate 17 → 18, verify\_vld\_positions 17 → 18,
         verify\_wrk\_features 40 → 41. (8) THE SOURCE-SIDE (18 comment/docstring/Field-description edits, zero
         behaviour change): wrk\_plot.py (the 18th level, the 10th non-cache level, rlmwf\_18), hlp\_config\_schemas.py
         (the 18th level; FEATURE\_ANALYSIS → SU\_ANALYSIS in the SuAnalysisConfig.enable description — no test pins
         it), test\_wrk\_plot.py (18th), test\_wrk\_client\_check.py (17th), test\_wrk\_analytics.py (the rlmwf\_15 slot
         + the 15-level chain ×2), test\_lm\_worker\_full\_chain.py (17th/18th ×3), test\_wrk\_validate.py (the
         "converted from" provenance dropped), verify\_logistic\_model.py (17th/18th + the four re-pin clauses in
         present tense), verify\_plot.py (18th). VERIFICATION: the format audit 88/95 clean (the 7 findings are all
         pre-existing size budgets; the pattern 146 size finding closed by the C1 edits); the residual scans clean (no
         FEATURE\_ANALYSIS, no D-tags, no "class (line)", no 1100×, no snames\_ts); the LONG suite 933/0/25 GREEN
         (unchanged — the source edits are comment-only).

D-264 | 2026-09-19 | I-009 (the pipeline construction boilerplate) EVALUATED and CLOSED as done, no code action
         (Roberto: "Siamo d'accordo al 100%. Chiudiamo così senza toccare il codice, opzione A"). The idea's deliverable
         was the evaluation of the three options on top of `StateMachine`, checked against the real code: (1) THE
         PIPELINE BASE CLASS was already realized — `BaseModel` (base\_model.py) was born in the port campaign to "avoid
         boilerplate in concrete domain-specific model classes (e.g., LogisticModel, DeepNetworkModel)"; every domain
         facade inherits it, and `LogisticModel.__init__` is already thin (the domain path validation, the 2-line
         LMContext construction, the workers list, super()). (2) THE DECLARATIVE STEP TABLE exists in effect — the
         19-entry workers list in `logistic_model.py` is one factory call per level in level order: a table, and the
         pipeline's table of contents (documentary value). (3) THE @STEP HELPER was evaluated and rejected: it would
         save the 76 factory lines (4 per worker, the `@validate_call` house convention) + the 18 factory imports, at
         the cost of a new registry/decorator mechanism (its own doc + tests), the imports kept anyway (then for side
         effects), the 41 factory call sites (6 test files + 13 probes) touched, the 19 mirror docs + the state machine
         doc updated, a hidden import-order dependency, and zero behaviour benefit. The `LMContext` (~100 lines) is the
         domain blackboard (the D-099 pre-declared cross-level fields), not boilerplate; the 19 `wrk_*.py` files carry
         the real domain logic. The only remaining argument for a shared mechanism is a future SECOND pipeline
         (DeepNetworkModel), which is speculative: when it arrives the 19 domain workers repeat, not the wiring lines,
         and that case is re-evaluated with concrete data (a new idea, not the completion of this one). Verdict: the
         remaining explicit assembly is design, not debt. I-009 moved to notes/ideas-closed.md.

D-265 | 2026-09-19 | I-010 (the StateMachine context-injection redesign) EVALUATED and CLOSED as done, no code action
         (Roberto's approval): the evaluation condition was met (every domain module in the workspace, the call pattern
         visible) and the evaluation CONFIRMS the D-070/M9 leave-as-is call. THE REAL CALL PATTERN: the 19 domain
         workers consume the three injected helpers uniformly through the context — 163 `ctx.log_event(...)` call sites
         + 9 `ctx.get_cache_file_*_for_current_level()` call sites (8 files); the worker unit tests build a bare
         LMContext and assign `ctx.log_event = <test lambda>` by hand (no machine instance). THE HAZARD (V17): a context
         shared by two machines re-binds to the LAST one built — exercised by exactly one test, NEVER in production: the
         single StateMachine construction site (BaseModel) gives every facade its own LMContext + machine, and a future
         second pipeline (DeepNetworkModel) would carry its own context + machine as well. THE OPTIONS: (A) the explicit
         machine reference (the worker callables take the machine, `sm.log_event` / `sm.get_cache_file_*`) removes the
         injection at the root (no side effect, no V17, no lambda no-op fallbacks) but rewrites the Worker class + the
         machine dispatch + all 19 worker \_up/\_down signatures + ~40 test callables + 163 log call sites + 9
         cache-helper sites + 3 LMContext fields + ~24 mirror docs + TestContextInjection — a large, high-risk refactor
         of the whole pipeline for a hazard that never manifests; (B) the context-owned helpers do NOT solve V17 (the
         shared context's machine reference still re-binds to the last machine — one reference instead of three).
         VERDICT: leave as-is — the uniform `ctx.` blackboard access is exactly what the injection was designed to
         serve; the D-070/M9 decision ("the injection is fundamental, the domain workers depend on it") stands, now
         confirmed by the visible call pattern. I-010 moved to notes/ideas-closed.md.

D-266 | 2026-09-19 | I-007 (the FeatureSet column-labelling helper) EXECUTED (Roberto's approval; the property name
         feature\_blocks): the D-041 deferral condition was met — the pipeline module that labels columns arrived
         (SU\_ANALYSIS + EFFECT\_SIZE) and had re-derived the same 14-line helper locally TWICE (wrk\_su\_analysis /
         wrk\_effect\_size), plus a THIRD copy inline in the hlp\_gate test loader. THE CHANGE (zero behaviour change,
         the logic byte-identical): (1) feature.py — the new FeatureSet.feature\_blocks property: the (name, col\_start,
         col\_end, n\_configurations, n\_instances) tuples over the non-intercept features, in the fset.features order
         (the compute\_indexes column layout: the intercept owns column 0 if present, then the mobilities, then the
         patterns), instance-aware (each feature occupies its n\_instances D8-instance columns); the intercept is not a
         block (it is fset.intercept). (2) wrk\_su\_analysis / wrk\_effect\_size — the duplicated \_feature\_blocks
         helpers removed, the call sites use fset.feature\_blocks. (3) hlp\_gate.load\_campaign — the inline column walk
         replaced by fset.feature\_blocks (the (cfg, fset, blocks) return signature unchanged — zero test change). (4)
         hlp\_random\_play — the two accumulator docstring phrasings "(the load\_campaign blocks)" reworded to "(the
         fset.feature\_blocks)". TESTS: test\_feature 20 -> 25 (the new TestFeatureSetFeatureBlocks class: the 16-block
         list golden with the intercept — columns 1-53 — and without it — 0-52 —, the intercept-only + empty sets -> [],
         the contiguous instance-aware tiling: every block width = its n\_instances, up to n\_instances). DOCS: the 5
         mirror docs (feature, test\_feature, wrk\_su\_analysis, wrk\_effect\_size, hlp\_gate). VERIFICATION: LONG suite
         933 -> 938/0/25 GREEN; the docs format audit 88/95 clean (the 7 findings are the pre-existing size budgets —
         zero new). The semantic name->column resolution (the JointAccumulator su\_pairs lookup, the ANOVA
         per-instance-column groups) now rides on the documented FeatureSet API; the design-matrix side was NOT touched
         (the WMAPS artifacts feature\_w\_ranges / iwmap\_feature\_offset already cover the weight-level mapping).

D-267 | 2026-09-20 | Test-file documentation cleanup of test\_lm\_worker\_full\_chain.py EXECUTED (Roberto's approval;
         the 42-site proposal list): the file's docstrings/comments carried the evolution history — the D-xxx/I-xxx
         references, the band re-centerings (D-147/D-149/D-186/D-187), the drifting level ordinals ("the full 18-level
         chain", "the PLOT is now step 18 (was 16)", "the 17th level"), the retired-record narrative ("RETIRED",
         "Roberto's ruling"). THE CHANGE (comment/docstring-only, zero behaviour change; 217 lines, -128/+89): (1) the 2
         full-chain test docstrings -> "Run the full chain up to last level on rlm\_04/rlm\_03" (+ the Long-running
         line) — Roberto's template: no drifting ordinals. (2) every D-xxx/I-xxx reference removed
         (D-105, D-127, D-130, D-141, D-142, D-143, D-144
         (C2), D-145, D-147, D-148, D-149, D-150, D-186/D-187, D-255, D-256, I-017, I-018) across the header, the class
         docstrings, the 2 setUp comments, the helper docstrings, the 8 section separators, the 2 report-fingerprint
         comments, the 3 assert messages ("retired by D-144" -> "must not exist" / "gone with the record"), the
         skipUnless message, the TestModelWeightsV2 class docstring, the v1-body comment, the corruption-sentinel
         docstring. (3) the 2 band-history blocks (26 lines A2030 + 18 lines A2050) compressed to the CURRENT rationale:
         the v2 file embeds the run's configuration (the base\_dir is a random mkdtemp path) -> no sha3 literal golden,
         the size pin is a BAND (the LZ4 match jitter on the 8 random base\_dir chars); the determinism guarantee = the
         second-instance byte-identity test + the read-back provenance pins. (4) the drifting level ordinals in comments
         replaced by the level names (CLIENT\_CHECK / PLOT / VALIDATE). (5) the synthetic dump marker "D-144" -> "SYNTH"
         (a data literal, no golden depends on the value — the checksum is computed from the dump). UNTOUCHED: the test
         pins (the `current_step == 18` assert, the goldens, the bands), the "as in test\_regab" gate cross-reference (a
         behaviour pointer, not history), the mirror doc (no D references, no verbatim docstring quotes — the
         paraphrases stay correct). RULE: the test-doc guideline promoted to notes/rules.md (the Docs section): a test
         docstring/comment states what is tested, optionally how it is realized (mechanism, pre/post conditions); no
         D-xxx/I-xxx references, no evolution history, no drifting level ordinals (name the level). VERIFICATION:
         py\_compile OK, the residual D-xxx/I-xxx/ordinal scan of the file clean; the docs format audit 88/95 clean (the
         7 pre-existing size budgets, zero new); LONG suite 938/0/25 GREEN (unchanged).

D-268 | 2026-09-20 | Test-file documentation cleanup of test\_hlp\_config\_schemas.py EXECUTED (Roberto's approval of
         the A+B+C proposal list): (A) the 15 D-xxx/I-xxx + history sites — the class docstring's probe-conversion
         narrative ("the first test file… converted from the verify\_wrk\_positions.py E section"),
         the D-076/D-079/D-080/D-142/D-148/D-149/D-175 references, the "Roberto's ruling" / "(the png-default ruling)"
         phrasings, the P6 tag, the stale 'FEATURE\_ANALYSIS' level name -> 'SU\_ANALYSIS' (the D-258 rename). (B) the 7
         probe-inherited E1..E12/T15 section labels removed (the descriptions kept; the mirror Coverage rows
         re-labelled). (C) the 4 test\_i017\_\* methods renamed (test\_su\_analysis\_defaults /
         test\_su\_pairs\_canonical\_dedupe / test\_su\_pairs\_fail\_fast / test\_target\_level\_field) + the 2 mirror
         docs (the header what-it-is rewrite, the method citations, the 2 "(the P6: …)" campaign tags).
         Comment/docstring/identifier-only, zero behaviour change (39/45 source lines); the test count unchanged
         (27/0/0). VERIFICATION: py\_compile + the residual D-xxx/I-xxx/label scan clean; module 27/0/0 GREEN; LONG
         suite 938/0/25 GREEN; the docs format audit 88/95 (the 7 pre-existing size budgets, zero new).

D-269 | 2026-09-20 | The I-017 campaign-tag sweep (the "F" scope, opzione 2) EXECUTED (Roberto's approval of the
         inventory + the 5 policy points): the SU-analysis campaign's tag family — the I-017 idea id, the task labels
         (T3-T16), the P2/P4/P5/P6 + ODP-1/4/5/8 item labels, the STOP deliverable, the campaign-internal D-numbers
         (D-173/D-174/D-175/D-177/D-178/D-181-D-184/D-186/D-187/D-191/D-192/D-194/D-195/D-199/D-254/D-256) — removed
         from ~85 sites in 14 source files (the 7 lm modules: hlp\_wave, hlp\_config\_schemas — incl. the 6 user-visible
         description= strings —, wrk\_su\_analysis — the corpus-version comment rewritten, the facts kept —,
         wrk\_effect\_size, hlp\_random\_play, hlp\_feature\_analysis, logistic\_model; + the 7 test files:
         test\_wrk\_su\_analysis, test\_wrk\_effect\_size, test\_hlp\_feature\_analysis, test\_hlp\_wave,
         test\_hlp\_random\_play, test\_logistic\_model — incl. the 12 T#(D-075) check labels the D-267 test-doc rule
         requires out —, test\_wrk\_features) + 5 mirror docs (the P6/ODP tags out, the joint-matrix + 1e7 rewordings,
         the D-256 pointer kept). POLICY (approved): (1) the tags out, the facts kept ("the T3 oracle" -> "the scalar
         W=1 reference", "the T4 loop" -> "the fixed scalar loop", "the ODP-1" -> "the 1e7"); (2) the design pointers to
         other decisions KEPT (D-059/D-060/D-065/D-068/D-099/D-157); (3) the Roberto attributions out (3 hlp\_wave
         sites); (4) the "T6 concern" -> "outside this module's scope"; (5) the probes NOT touched (their own item ids +
         the verify\_validate I-017 note). The extended scan (vs the presented inventory) added the same-kind sites
         INSIDE the approved files (I-013 in hlp\_config\_schemas, I-018 x3 in logistic\_model, I-019 in
         test\_logistic\_model, D-157 (I-012) in test\_wrk\_features, the T9/T6/T4-rate sites) — executed under the
         approved policy. Comment/docstring-only, zero behaviour change (207/208 source lines + 11/12 doc lines).
         REGISTERED RESIDUE (reported, not changed — the follow-up campaign's scope): the same tag family in the
         NON-approved files: the I-018 family (wrk\_validate / hlp\_validate / hlp\_analytics / wrk\_client\_check +
         their test files + 6 mirror docs), the I-013 family (hlp\_gradient / opt\_lbfgs + their tests), the ancient
         T#(D-0xx) check labels in the pre-campaign test files (test\_state\_machine, test\_cache\_manager,
         test\_wrk\_zed/gradient/positions/wmaps/optimize/config/indexes/design\_matrix/hlp\_generate, tags.py), I-003
         (test\_board + board.md). VERIFICATION: the 14 files py\_compile OK, the residual tag-vocabulary scan of the 14
         files clean, the 8 affected modules 121/0/2 GREEN, LONG suite 938/0/25 GREEN, the docs format audit 88/95 (the
         7 pre-existing size budgets, zero new).

D-270 | 2026-09-20 | The registered-residue campaign (the D-269 follow-up) EXECUTED (Roberto approved the Option-A
         inventory — the full D-267 test-doc-rule compliance; the 3 sub-decisions: the gate line + header note changed
         AND the probes re-pinned, the marker -> "SYNTH", the data files left as-is): the campaign-tag family is now OUT
         of the whole src/ tree. (1) SOURCE: the I-018/I-013 tags out of the 7 lm/tools modules (12 sites: hlp\_plot,
         wrk\_client\_check, hlp\_validate, wrk\_validate — the D-150 report pointer kept —, hlp\_analytics,
         hlp\_gradient, tools/opt\_lbfgs — the D-146 pointer kept —); (2) TESTS: every D-/I- reference out of 38
         test-dir files (~225 sites) per the D-267 rule — the I-018/I-013/I-003 sites, the ancient T#/R#/M#(D-0xx) check
         labels, the header tier notes + the db\_long\_gate gate-line idiom (now "see reversi.test.tags" / the bare
         comment), the bare design pointers (the D-065 house
         rule, D-085, D-142, D-143, D-149, D-157, D-105/M2, D-127, D-139, D-144, D-111
         M#, D-213, D-215, D-232, D-186/187, D-255, ...), the probe-conversion notes (the probe name kept, the "at D-106
         step 3" + the D-107 re-pin history out), the "session 22" out, the two "Roberto's ruling" attributions out (the
         fact kept), the synthetic marker "D-148" -> "SYNTH" (the D-267 precedent; the checksum is runtime-computed, no
         golden moves); (3) DOCS: the I-018/I-003 tags out of 12 mirror docs (29 sites) — the design pointers
         (D-150, D-256, ...) kept per docs\_rules; (4) PROBES: the content pins re-pinned to the new idiom (the
         gate-line + the header note in verify\_optimize / verify\_gradient / verify\_hlp\_indexes / verify\_wmaps /
         verify\_zed) — the probe's own check names kept (their own item ids, the D-269 precedent). The line counts of
         the 26 probe-pinned files were kept by in-place rewraps (no line-count re-pins were needed).
         Comment/docstring-only, zero behaviour change. FINAL RESIDUE (left as-is by the approved ruling): the data
         files test/data/rlm\_05.json + rlm\_06.json (the "I-017 Experiment 05/06" name/description + the T10 cost
         model) and prng\_golden.txt (the D-161/D-198/D-203 provenance comments) — data, not docs. VERIFICATION: the 50
         changed files py\_compile OK; the residual scans clean (the test dir: no D-/I- outside data/; lm + tools:
         no I-013/I-018/I-003; the docs: no I-tags); the 26 pinned line counts intact; LONG suite 938/0/25 GREEN; the
         docs format audit 88/95 (the 7 pre-existing size budgets, zero new); the 5 re-pinned probes green (0
         mismatches, the live tiers included — verify\_optimize 77 checks, verify\_gradient 59, verify\_zed 51,
         verify\_wmaps + verify\_hlp\_indexes all-pass).

D-271 | 2026-09-20 | The docstring/comment PRINCIPLES codified into the legislation (Roberto approved the 2-bullet
         proposal for notes/rules.md §Docs; the D-267->D-270 campaigns had been applying these distinctions
         ruling-by-ruling): (1) "Provenance" is DEFINED — the file's own change history is OUT everywhere; the DESIGN
         POINTERS to other decisions that explain a current choice stay (prescribed in mirror docs per docs\_rules.md
         §3.2, and in source comments when the choice is non-obvious — the D-150 report pointer and the D-146 two-loop
         note are the canonical kept cases). (2) The D-267 test-doc rule is EXTENDED to the probes/ docstrings and
         comments, with the single exception: the probe's own check labels and item ids are the probe's vocabulary and
         stay — only the asserted text and the surrounding comments follow the test-doc rules. Notes-only: rules.md
         §Docs is now 6 bullets; no source, no probes, no mirror docs touched. VERIFICATION: LONG suite 938/0/25 GREEN
         (the routine pre-commit sweep, probe\_rules.md §5.2).

D-272 | 2026-09-20 | The test-doc RESIDUE campaign (the post-D-271 reconnaissance, Roberto approved: all families + the
         borderline rulings, one commit per group): a full recon of src/reversi/test/ against the D-267 + D-271 rules
         found 8 families of deviations, none carrying a D-/I- numeric (the D-270 residual scan could not see them): (A)
         the third "Roberto's ruling" attribution (test\_wrk\_vld\_positions class docstring — the D-270 sweep removed
         the other two, the fact kept); (B) the level ordinals (D-267) — "the 18th/17th level" (plot, client\_check), 2
         STALE "step 11" (vld\_positions, the level is 13), the STALE "GRADIENT step 8 / ZED step 7" (gradient, they are
         10/9), "the 2nd step" (features), the 7 logistic\_model sites incl. the "now"/"new" markers + the 5 named-level
         parenthetical ordinals; (C) 27 ancient T#/V#/R# campaign labels in 4 files (no D-xxx attached — invisible to
         the D-270 scan): 18 in test\_cache\_manager, 6 in test\_state\_machine, 2 in test\_pattern, 1 in
         test\_hlp\_generate; the probe references with the probe's own check ids stay (the D-270 approved conversion
         idiom); (D) the re-pin history in the wrk\_plot rendering golden + 3 golden notes pointing at
         scratch/verify\_analytics.py + scratch/verify\_validate.py (files that do not exist — scratch/ is disposable,
         probe\_rules §2) with the "tier C" / "the campaign probe" framing; (E) 4 before/after contrasts ("the
         pre-vectorization scalar behaviour", "now ASSEMBLES instead of", "now share", "is now the count"); (F) the
         borderline rulings: OUT — the "log-only ruling" framing (the fact kept) + the date anchor in the mobility
         golden note; KEPT — the "re-pinned guard contract" conversion notes (the D-270 approved idiom), the "legacy
         bare-hexdigest sidecar" (it names the format variant the test exercises — a present contract), the "independent
         oracle" framing in test\_hlp\_random\_play (a mechanism description — D-267 allows how it is realized). All
         edits are in-place rewraps (the probe-pinned line counts preserved), comment/docstring-only, zero behaviour
         change. The wider probe sweep (all 24 probes) then caught 2 stale pins left by D-270, which had run only its 5
         re-pinned probes: verify\_wrk\_features C6 (pinned the header note 'DB-free since D-157' — the string D-270
         removed) and verify\_design\_matrix C3 (counted the old gate line with the 'D-130' suffix — D-270 made it
         bare): re-anchored to the current idiom (part G, the probes' own check names kept). VERIFICATION: the 15
         changed files py\_compile OK; LONG suite 938/0/25 GREEN; all 24 probes green (the live tiers included).

D-273 | 2026-09-20 | The TEST-TREE reorganization (Roberto's call after the PRO/CONS review of the three options —
         per-zone test/ subdirs inside src (A), a root test/ tree mirroring src (B), or a single test package with zone
         subdirs (C); B won: the GitHub-readable, standard layout is worth the extra churn): the unit tests leave src/
         and move to a ROOT test/ tree mirroring src/ one file to one file, zone by zone (the convention Roberto fixed:
         test/reversi/test\_board.py, no intermediate test/ level): test/reversi/ (the core zone: board, random\_game,
         pattern, mobility, feature, regab, paths-test), test/reversi/lm/ (32: the data modules, the workers, the
         facade, the client, the end-to-end chain), test/reversi/tools/ (6: binio, usage\_binio, opt\_lbfgs, prng,
         cache\_manager, state\_machine); the 3 shared helpers (paths/tags/closecheck) + the 9 data/ fixtures land in
         test/reversi/. git mv throughout (history preserved). The module paths become test.reversi[.zone].<module>: the
         helper imports, the header run-comments, the WORKSPACE\_ROOT-anchored data paths, the 2 CWD-relative rlm\_00
         refs (test\_wrk\_config), test\_paths' layout pin, test\_state\_machine's parents[2] and the paths.py marker
         message all follow. run\_utests.sh: the 45 modules in the SAME canonical order (D-130) under the new names;
         tools/measure\_suite.py: discover from the root test/ + the zone-agnostic module extraction. The 47 test mirror
         docs follow to docs/test/reversi{,/lm,/tools}/ (the H1s + every body reference; the D-007 mirror bullet is
         extended accordingly, docs\_rules.md §6 + the fixtures bullet updated, the auditor's source\_of handles both
         trees). Legislation: rules.md (the unit-tests bullet, the D-007 extension, the D-085 / tags / closecheck / tier
         idioms, the D-267 test-doc scope now 'in test/'), AGENTS.md layout (src/ and test/ separate entries, docs/
         mirrors both), naming.md pointer, overview.md (the single-module command, the 47-row Test files table, the Test
         data note). The 16 referencing probes re-anchor: the file-path refs + the content pins (the test.reversi.\*
         imports, the data paths, the runner registration, the wmaps L84/L185 lines), the 12 importing probes get the
         workspace root on sys.path (the test/ tree is not installed), the 3 zone-abbreviated local read helpers
         (gradient / optimize / zed) resolve against the new lm home; the probes' own check labels + item ids stay
         (the D-269/D-270 precedent). Side effect: the tests are OUT of the packaged wheel (the packages.find
         where=['src'] never saw them). VERIFICATION: test tree + probes py\_compile OK; LONG suite 938/0/25 GREEN; all
         23 probes green (the live tiers included); the mirror-doc audit 88/95 = the pre-existing baseline (the one
         transient width finding re-wrapped in place, line counts kept). POST-FIX: the test\_state\_machine parents[]
         edit was a no-op misjudged as a move — the file sat 3 levels below the root BOTH before (src/reversi/test/) and
         after (test/reversi/tools/) the move, so parents[3] was correct already; the C1 change to parents[2] redirected
         the D-065 artifacts into test/build/tmp (a stray, gitignored-looking folder Roberto spotted): reverted to
         parents[3] + the comment corrected, test/build removed. VERIFICATION: the 49-test module green standalone, LONG
         suite 938/0/25 GREEN, no test/build after the full run.

D-274 | 2026-09-21 | The logistic\_model facade gains a SCRIPT ENTRY (Roberto's change, taken in as-is — no
         pipeline-behaviour change; the module is now also runnable as a command): python -m reversi.lm.logistic\_model
         <config.json> [--verbosity {high,moderate,standard,low,very\_low,none}] (default standard), from the workspace
         root. New surface: import argparse; the module-level build\_model(json\_config: Path, verbosity: Verbosity) — a
         @validate\_call (arbitrary\_types\_allowed, consistent with the facade ctor gate) that builds the LogisticModel
         and drives it to the last level (move\_to\_last); the if \_\_name\_\_ == '\_\_main\_\_': block that parses the
         config path (argparse type=Path) + the --verbosity choice (the lowercase Verbosity names, resolved through the
         {name.lower(): member} map) and calls build\_model. A "How to run" comment block documents the two steps
         (activate the venv, run the pipeline). build\_model is NOT in \_\_all\_\_ (the CLI entry helper; the facade API
         is unchanged: \_\_all\_\_ stays ['LMContext', 'LogisticModel']). The argparse glue has no dedicated test — its
         building blocks (the facade ctor + move\_to\_last) are the already-tested surface. VERIFICATION: the hub probe
         verify\_logistic\_model.py all green (21 checks; the V3d source scan still passes — no commented `wrk_`
         import/entry introduced); LONG suite 938/0/25 GREEN (Roberto's run, re-confirmed); the mirror-doc audit 88/95 =
         the baseline.

D-275 | 2026-09-21 | The SU\_ANALYSIS report is restructured (Roberto's request, after a full pipeline run on base\_dir
         build/test\_su\_00 to validate the su level). The new format: the title "Symmetrical Uncertainity Analysis
         Report" (Roberto's spelling) + the 2-line subtitle (it evaluates the normalized relationship / dependency /
         shared variance, compensating for the bias in raw information gain) + the 6-line SU-range legend (0.0 perfect
         orthogonality; 0.0-0.1 excellent independence; 0.1-0.3 moderate correlation; 0.3-0.5 strong correlation;
         over 0.5 very strong correlation — English, per the "in inglese" ask) + a one-line summary (the corpus size,
         the model's features, the requested SU pairs) + "Section A: Properties of features selected by the logistic
         model" (the feature-instances: the per-sub-variable dispersion + the never-observed audit) + "Section B:
         Symmetrical uncertainity" (the SU groups). The pairs are DEDUPLICATED + sorted: the SU is symmetric
         (2·I/(H\_u+H\_v)), so the (i, j) and the (j, i) directions are the SAME measurement — each shown ONCE in the
         canonical endpoint order (the smaller (name, inst) first); the groups (the feature-pair header, e.g. "EDGE -
         EDGE") are sorted by the SU value descending (the strongest correlation first; a deterministic canonical
         tie-break). The pair separator is now "-" (was "x"); the CSV export is aligned to the same deduped+sorted
         groups. New wrk\_su\_analysis helpers: \_SU\_LEGEND, \_feature\_instances (the distinct feature names,
         first-seen order), \_su\_canon (the canonical endpoint order), \_su\_groups (the dedup + group + sort).
         VERIFICATION: the wrk\_su\_analysis + wrk\_effect\_size unit tests green (16, the VLONG skipped);
         verify\_su\_analysis.py is now 44 checks (the su\_rx regex x->-, + B12 the dedup [12 ordered -> 6 unordered,
         each once] + B13 the value-descending sort, on a self-pair) all green; the user's test\_su\_00 report (the 5e7
         corpus, cache hit) regenerated: 12 -> 6 pairs, the Section A values unchanged; the mirror-doc audit 88/95 = the
         baseline; the full 23-probe sweep green.

D-276 | 2026-09-21 | MAINTENANCE (POST-FIX): the verify\_zed.py F1 check went red — a PRE-EXISTING regression from D-274
         (the logistic\_model script entry), NOT from D-275. D-274 added lines above the LMContext zed fields in
         logistic\_model.py (import argparse + the script-entry block), shifting the four fields (zed\_checksum / y2z /
         z2y / z) from lines 144-147 to 147-150. The F1 check is a line-shift maintenance pin (its own comment: "the
         block shifts with every insertion above it") that hardcodes the old positions, so it went red. The previous
         span (D-274) ran only the hub probe verify\_logistic\_model.py, not the full 23-probe sweep, so the red was not
         caught then (the "23 probes all green" baseline was quietly broken). The fix: update the four indices
         143-146 -> 146-149 (the field content is unchanged, only relocated); the label's historical insertion list is
         left as-is (the kept-by-ruling probe label). VERIFICATION: verify\_zed.py 51 checks, 0 mismatches; the full
         23-probe sweep (LONG=1) 23/23 green (the baseline restored).

D-277 | 2026-09-21 | Refinement of D-275 (Roberto): the Section B SU groups are sorted by the CANONICAL ENDPOINT ORDER
         (the lexicographic (feature, instance) order: EDGE[0]-EDGE[1], EDGE[0]-EDGE[2], EDGE[0]-EDGE[3],
         EDGE[1]-EDGE[2], ...), NOT by the SU value descending (the D-275 default, the strongest correlation first). The
         \_su\_groups sort key is now ((name\_i, inst\_i), (name\_j, inst\_j)) (was (-value, ...)); the dedup is
         unchanged. The probe B13 is re-anchored (the canonical endpoint order, not the value descent); the doc mirror +
         the overview sort wording updated. VERIFICATION: the user's test\_su\_00 report regenerated in the canonical
         order (12 -> 6 pairs, the same values); the 44-check probe green; the full 23-probe sweep 23/23 green.

D-278 | 2026-09-21 | CORRECTION + the Section A KPI legend (Roberto). (1) The coverage / the never-observed denominator
         was n\_configurations (the raw 3^n) — WRONG for patterns. The pattern's observed codes are the PRINCIPAL
         indices (compute\_principal\_indexes, the orbit representatives), a scattered subset of [0, 3^n) of size
         n\_unique\_configs (the equivalence classes under the pattern's symmetry = principal\_index\_count), not the
         full raw range; the correct denominator is n\_unique\_configs (the reachable space), and n\_configurations was
         counting the (3^n - n\_unique\_configs) non-principal raw configs as "never observed". A MOBILITY's codes are
         the raw values (no reduction), so its n\_configurations was already correct. Fix: wrk\_su\_analysis computes
         the per-sub-variable REACHABLE space (n\_unique\_configs for patterns, n\_configurations for mobilities) and
         uses it for the coverage / the never-observed audit (report + CSV). Effect on the test\_su\_00 EDGE (the
         8-square row, 4 instances): 6561 -> 3321, coverage 0.458 -> 0.905, never-obs 3556 -> 316 (the 5e7 corpus). (2)
         The report's Section A now carries a compact English KPI legend (the \_KPI\_LEGEND) above the
         feature-instances. VERIFICATION: exhaustive — EDGE n\_unique\_configs = principal\_index\_count = 3321, ALL
         observed codes are valid principal indices (scattered, max 6560), the mobility (LMC, 65) unchanged; the
         test\_su\_00 report regenerated corrected; the probe C10 re-anchored (the reachable space) + the 44-check probe
         green; the full 23-probe sweep 23/23 green.

D-279 | 2026-09-21 | Naming refinement of D-278 (Roberto): the report term "reachable space" is imprecise — the
         n\_unique\_configs configurations are the THEORETICAL space (the pattern's principal-index orbit classes); with
         a large corpus (50M, the 4 EDGE instances identical) the reachable ones are all captured, and the residual
         never-observed are ~99% IMPOSSIBLE by the game dynamics (counting the impossible ones is infeasible — not
         attempted). So the denominator is the total THEORETICAL configurations, some of which are unreachable by the
         game's rules. Renamed: the report KPI legend (the \_KPI\_LEGEND) now says "theoretical" (the coverage line:
         "the ratio of observed to total theoretical configurations (some are unreachable by the game's rules)"); the
         wrk\_su\_analysis helper \_reachable\_space is renamed \_theoretical\_configs; the probe C10 + the doc mirror +
         the overview follow. The numbers are unchanged (only the naming). VERIFICATION: the report regenerated (the
         legend now "theoretical"); the 44-check probe green; the full 23-probe sweep 23/23 green.

D-280 | 2026-09-21 | Consolidating the ec (empty\_count) into ONE required root field (the start of the four-step
         migration D-280..D-283; Roberto). The ec (the "game phase" window, the "mele con mele" constraint) was defined
         twice — su\_analysis.corpus.ec (the CorpusConfig, default 20, 0..100) for the SU corpus, and
         regab\_data\_set.ec (the RegabDataSetConfig, required, 0..60) for the DB extraction (training + the validation,
         which inherits it, D-100 M1) and the saved model (model\_weights). In the fixtures both are 20 (the redundancy
         is meaningless; they must be equal). D-280 adds the required root field empty\_count (int, 0..60 — the stricter
         of the two existing bounds, tightening the corpus's 0..100; 20 is in both) between name and description; added
         to the 7 test fixtures + the 2 production configs (build/test\_su\_00, build/su\_corpus\_1e7, value-preserving
         20) + the test\_wrk\_config synthetic payload. A new test pins it (required: missing -> ValidationError;
         the 0..60 bounds: 61 / -1 -> ValidationError; the fixture value 20 accepted). The two old ec's are untouched
         this step (D-281 removes the corpus one, D-283 the regab one); the migration is value-preserving (the caches,
         the corpus signature, and the model file keep the same ec value — nothing is regenerated). VERIFICATION: the
         config tests (41) + the fixture-based LMConfig tests (24, 6 DB-gated skipped) green; rlm\_su\_1e7 loads
         (empty\_count=20); the doc mirror.

D-281 | 2026-09-21 | The SU corpus uses the root empty\_count (the empty\_count consolidation, step 2 of 4; Roberto).
         The CorpusConfig.ec field (default 20, 0..100) is REMOVED — the SU corpus generation (the seed, the
         total\_positions) stays, but the ec arrest now reads the ROOT empty\_count (the single ec source).
         wrk\_su\_analysis: the \_signature 'ec' entry now reads ctx.cfg.empty\_count (the value is 20 in the fixtures,
         so the cache signature is byte-identical — the 5e7/1e7 corpus caches are NOT invalidated); the generation log +
         the run\_wave call read the root empty\_count. The 5 configs that had su\_analysis.corpus.ec (rlm\_00 / 05 / 06
         + the 2 production) drop it. The test\_wrk\_su\_analysis \_make\_ctx sets cfg.empty\_count (not corpus.ec); the
         config defaults test drops the corpus.ec assertion; the verify\_su\_analysis B10 signature check reads
         sig\_cfg.empty\_count. VERIFICATION: the SU test + the config tests (37) green; the verify\_su\_analysis probe
         (44) green.

D-282 | 2026-09-21 | The extraction (training + validation) uses the root empty\_count (the empty\_count consolidation,
         step 3 of 4; Roberto). The DB extraction (load\_from\_db) + the cache consistency check (is\_cache\_consistent)
         now read the ec from the ROOT empty\_count (the single ec source), not from regab\_data\_set — so the
         validation extraction, which shares the same extract\_and\_prepare -> load\_from\_db path, no longer INHERITS
         the ec from the training block (the D-100 M1 inheritance is retired). regab\_data\_set keeps bid + status (its
         ec field is removed in D-283); only the saved-model write (model\_weights) still reads regab\_data\_set.ec
         until D-283. test\_wrk\_positions test\_different\_ec\_is\_inconsistent now mutates the root empty\_count (not
         regab\_data\_set.ec). The wrk\_vld\_positions M1 note + the wrk\_positions doc follow. VERIFICATION: the
         positions cache-consistency tests (12, 5 DB-gated skipped) green, including
         test\_different\_ec\_is\_inconsistent; the doc mirror.

D-283 | 2026-09-21 | The regab\_data\_set.ec is REMOVED; the saved model uses the root empty\_count (the empty\_count
         consolidation, step 4 of 4; Roberto — the migration completes). The RegabDataSetConfig.ec field
         (required, 0..60) is REMOVED — the regab\_data\_set now carries only regab\_db\_connection + bid + status. The
         saved-model write (model\_weights, the u32 metadata) reads the ROOT empty\_count (the value is 20, so the model
         file is byte-identical — no re-training). The 9 configs (the 7 test fixtures + the 2 production) drop the
         regab\_data\_set.ec. test\_hlp\_config\_schemas test\_ec\_out\_of\_range\_rejected is REMOVED (the root
         empty\_count bounds are pinned by the D-280 test); test\_wrk\_config's synthetic payload drops the ec + its
         bounds test now mutates the root empty\_count. The SimpleNamespace mock configs (full\_chain, client\_check,
         the vld is\_cache\_consistent suite) + the two probes (verify\_gradient E7, verify\_wrk\_positions D3) now use
         the root empty\_count. After this step the ec has ONE home (the root empty\_count) — the redundancy is gone.
         VERIFICATION: the config tests (40) + the FULL suite (938, 25 DB-gated skipped) + the 23-probe sweep green;
         rlm\_su\_1e7 loads (empty\_count=20; test\_su\_00 still has the pre-existing DIAG7 su\_pairs issue, unchanged);
         the doc mirror.

D-284 | 2026-09-22 | The SU corpus generator migrates from the hlp\_wave wave engine to the random\_game play-path
         engine (the D-226 replacement, PHASE 1; Roberto). wrk\_su\_analysis: the \_compute\_tables now generates the
         corpus with random\_game\_play\_path — the batch of fresh lanes from the canonical start
         (board.initial\_game\_position) played to the root empty\_count, the batch size min(\_WAVE\_SIZE, total -
         harvested), the harvested lanes are the batch lanes at EXACTLY the target ec (the double-pass game-over lanes
         are dropped, the quota filled by the next batch), the uniform pick on the injected MT19937 (one stream for the
         whole run); the accumulators (hlp\_random\_play) are fed PER BATCH (the corpus never materializes in RAM — the
         BufferSink + the flatten are gone from the worker); the hlp\_wave import is REMOVED (the worker is now
         independent of the wave). The draw consumption differs from the wave (the pass / the game-over lanes consume no
         draw), so the corpora are NOT bit-compatible: the generator version bumps su-corpus-2 -> su-corpus-3 — every
         cached corpus (the rlmwf\_03 caches) is invalidated and regenerated on the next run (the 1e7 tier ~67 s, the
         engine ~4x faster per advance, D-232). The slots provenance is dropped (the worker discarded it — the
         accumulators need only the mover/opp). hlp\_wave SURVIVES (the phase-2 retirement is Roberto's call): its
         remaining consumers are test\_hlp\_wave (the suite), the test\_hlp\_random\_play corpus fixtures (3 call sites)
         and the verify\_su\_analysis tier-B corpus (an independent code path). The verify\_su\_analysis pins follow (A4
         the batch-size cap; A7 + B10 + F5 the su-corpus-3 version). test\_wrk\_su\_analysis: the NEW
         test\_corpus\_determinism (the two fresh same-spec computes are the identical marginal tables, a different seed
         changes them — the new generator's stream is pinned). VERIFICATION: the SU suite 10/0/1 green (VLONG 10/0/0),
         the verify\_su\_analysis probe (44 checks) green, the full suite green; the mirrors follow (wrk\_su\_analysis,
         random\_game, hlp\_wave, hlp\_random\_play, the two test docs).

D-285 | 2026-09-22 | The hlp\_wave wave engine is RETIRED (the D-226 replacement, PHASE 2; Roberto). The module
         hlp\_wave.py + the suite test\_hlp\_wave.py + their two mirrors are REMOVED (after D-284 the worker is the
         random\_game play-path engine — the wave was test-only, no production consumer). The remaining consumers
         migrate to the random\_game engine: the test\_hlp\_random\_play corpus fixtures (3 call sites — the
         module-local \_corpus helper over random\_game\_play\_path, the harvested lanes at the target ec) and the
         verify\_su\_analysis tier-B corpus (the same construction, 3000 positions at ec 20 seed 42; B1 re-pinned on the
         shape). The hlp\_random\_play module docstring + the mirrors follow (the corpus is the worker's random\_game
         play-path batches). run\_utests.sh drops the test\_hlp\_wave line. The VVLONG tier LOSES its only instrument
         (the 1e6 wave benchmark): the tier\_vvlong predicate + the runner header are KEPT (the machinery survives; a
         future very-long instrument may gate on it) — the tier removal is a separate call. VERIFICATION: the full suite
         (fast tier) green (939 - 4 = 935, the wave suite removed) + the verify\_su\_analysis probe (44) green; the
         mirrors + the overview rows follow.

D-286 | 2026-09-22 | The VVLONG tier is KEPT (Roberto, after the wave retirement D-285 left it uninstrumented): the
         tier\_vvlong predicate (test/reversi/tags.py) + the runner header stay in place — the very-long tier machinery
         survives for a future instrument, the removal option is retired. Zero code change (the D-285 state already
         documents the tier as uninstrumented).

D-287 | 2026-09-22 | The hlp\_gate campaign loader is RETIRED, its consumers now run the REAL pipeline (Roberto — the
         "elegant" solution, no parallel loader): load\_campaign's only value (reuse an existing JSON + stop the
         pipeline before the level under test) is natively provided by the facade — LogisticModel(cfg,
         base\_dir\_override=...).run("FEATURES") (the D-260 target\_level stop, silent Verbosity.NONE) publishes
         context.cfg + context.feature\_set, and the feature\_blocks property (D-266) is literally what the loader used
         to return as the third element. Migrated consumers: the \_make\_ctx of the two worker suites
         (test\_wrk\_su\_analysis, test\_wrk\_effect\_size — the mock ctx is KEPT as the test seam (the log capture +
         the use\_cache), the cfg/fset now come from the real context) and the two probes (verify\_su\_analysis 4 call
         sites, verify\_effect\_size 3 — a local ~5-line \_campaign() helper each, the verify\_effect\_size one also
         serving the build/rlm\_su\_1e7.json config; the FEATURES level is cheap, the corpus size irrelevant). The
         module hlp\_gate.py + its mirror are REMOVED (the test-infra no longer ships in the package); the feature.md +
         pattern.md consumer lists, the two test mirrors + the overview row follow. The verification posts are INTACT:
         same suites, same pins. VERIFICATION: the SU suite 10/0/1 + the ES suite 7/0/0 green (17 tests in 1.7 s — the
         facade runs are cheap) + the two probes green (44 + 29 checks, 0 mismatches).

D-288 | 2026-09-22 | The SU\_ANALYSIS corpus cache moves from PICKLE to BINIO (the pipeline has no pickle; the house
         data-file idiom). The \_load\_tables / \_store\_tables are rewritten on the binio layout: the file header (the
         "SU\_ANALYSIS corpus cache" description + the format VERSION 1 — a format change bumps the version, orthogonal
         to the data signature) + the signature block (the feature\_set hash + the 5 spec fields + the su\_pairs in the
         configured order) + the marginal block (the (name, instance, n\_conf) + the codes u32 / counts i64 arrays) +
         the joint block (the presence flag + the pairs, the per-instance entries in the SORTED (ii, jj) order for a
         deterministic layout). The write is LZ4-compressed (the D-139 data-file pattern, model\_weights /
         hlp\_generate) with checksum=False (the .SHA3-256 sidecar stays owned by the cache\_manager, D-072); the load
         does the sidecar check + the header description/version guard (the hlp\_generate idiom) + the ordered block
         reads. OLD PICKLE CACHES SELF-INVALIDATE: their sidecar is still valid (the manager step 2 passes) but the
         binio reader fails loudly on the first MAGIC (a pickle never starts with the BIN1 framing), the manager's R2
         (D-071) deletes the file and recomputes — no manual cleanup, no \_GENERATOR\_VERSION bump (the data semantics
         are unchanged; the format is orthogonal). The verify\_su\_analysis C5-C7 pins migrate to the probe's OWN binio
         re-derivation of the layout (the independent read, NOT wsu.\_load\_tables — the a/b/c line); C2 is unchanged
         (already the binio sidecar). The verify\_effect\_size TIER D (the 1e7 real data) also loaded the SU cache (the
         ideal adherence marginals) — migrated to the same probe-own binio read (the header + the signature skip + the
         marginal, the joint left unread); the old BUILD pickle SELF-HEALS on the next tier-D run (the R2 recompute in
         the probe dir; the BUILD file stays untouched — the unlink semantics of \_delete\_cache\_files) and is
         regenerated as binio by the next production 1e7 run. The mock-ctx suite is format-agnostic (it runs through the
         cache flow) — unchanged. VERIFICATION: the SU suite 10/0/1 green (VLONG 10/0/0, the 1e7 corpus), the
         verify\_su\_analysis probe (44 checks) green, the verify\_effect\_size probe (29 checks, incl. tier D on the
         1e7 build area) green, the full suite (fast tier) 935/0/97 GREEN.

D-289 | 2026-09-22 | The SU\_ANALYSIS worker is split into the wrk/hlp pair (Roberto, the wrk\_design\_matrix
         minimalism): the NEW hlp\_su\_analysis.py carries ALL the analysis logic — the corpus generator (phase 1, the
         random\_game play-path engine), the binio cache I/O (the D-288 layout + the 6 block readers/writers), the
         consistency signature (+ the feature\_set hash), and the statistics (phase 2: the dispersion + the
         never-observed audit + the SU pairs + the report + the CSV) — together with the 9 module constants. The 6
         public functions (hlp\_su\_analysis\_compute / \_store\_to\_file / \_load\_from\_file / \_is\_cache\_consistent
         / \_signature / \_statistics) follow the house idiom: the compute / statistics / consistency / signature take
         the ctx (as hlp\_design\_matrix\_compute(ctx)). wrk\_su\_analysis.py becomes the ORCHESTRATION SKELETON (~100
         lines, the wrk\_design\_matrix shape): the enable no-op, the cache\_manager\_load\_or\_compute wiring over the
         hlp (the load with checksum=False — the manager already verifies the sidecar at its step 2, no double hash),
         the phase-2 recompute, the ctx publication, the D-060 recovery. NEW test\_hlp\_su\_analysis suite (11 NO-DB
         tests: the signature vs the independent sha3\_256, the binio round-trip with / without the joint, the load
         guards, the compute determinism, the theoretical space D-278/279, the SU groups dedup + canonical sort, the
         diagonal omission, the report + the CSV, the cache consistency) — the ctx is the real pipeline stopped at
         FEATURES (the D-287 idiom). test\_wrk\_su\_analysis is UNCHANGED (it imports only \_down/\_up/wrk\_su\_analysis
         — the level-flow tests, the 1e7 VLONG stays there). The verify\_su\_analysis probe re-targets: A3 / A6 cover
         the worker + the hlp files, A4 / A7 / A8 read the hlp text / constants, the B / C signature + kernel calls move
         to the hlp (44 checks unchanged). VERIFICATION: the new hlp suite 11/0/0 green, the worker suite 10/0/1 green
         (VLONG 10/0/0, the 1e7 corpus), the verify\_su\_analysis probe (44 checks) green, the full suite (fast tier)
         946/0/97 GREEN (935 + 11).

D-290 | 2026-09-22 | The \_\_all\_\_ POLICY (Roberto, standing rule): ONLY the functions used by OTHER modules are
         exposed in \_\_all\_\_ (or a designed tool-library surface, e.g. binio / state\_machine); a function called
         only by tests or probes NEVER goes in \_\_all\_\_ — the test / probe apparatus imports the module and reaches
         the name directly (no explicit from-import of a test-only name). Applied to the D-289 split:
         hlp\_su\_analysis\_signature was the INTERNAL signature (it feeds the hlp compute + the is\_cache\_consistent,
         no production consumer outside the module) — renamed \_signature (private, beside \_feature\_set\_hash), the
         \_\_all\_\_ is the 5 FLOW functions (compute / store / load / is\_cache\_consistent / statistics). The
         consumers follow: test\_hlp\_su\_analysis (2 tests) + the verify\_su\_analysis probe (5 call sites, the B8-B11
         + the C5) call hlp.\_signature directly (the probe already reaches the private kernels hlp.\_su\_values /
         hlp.\_su\_groups — the a/b/c independence lives in the math path, not the name visibility). Zero behaviour
         change. VERIFICATION: the hlp suite 11/0/0 green, the verify\_su\_analysis probe (44 checks) green, the full
         suite (fast tier) 946/0/97 GREEN.

D-291 | 2026-09-22 | The SU signature's feature\_set hash moves from the CONFIG DUMP hash to the FeatureSet DOMAIN hash
         (Roberto: hashing the JSON is a conceptual error — the FeatureSet already carries its domain hash, "a unique
         identifier for the set", built over the semantic content: the INTERCEPT marker + the child-set hashes,
         transitively the sorted mask contents). The dump hash coupled the cache signature to the pydantic SERIALIZATION
         (the key order, the indentation, the pydantic version) of the FeatureSetConfig spec instead of to the
         constructed domain object — and the cached tables are laid out by the constructed FeatureSet's columns (the
         feature\_blocks, D-266), so the signature should hash that same object. \_feature\_set\_hash is DELETED;
         \_signature stores ctx.feature\_set.hash (the full 64-char hexdigest). The only behaviour difference: a pure
         feature RENAME (same masks, new name) no longer invalidates the cache (the domain hash excludes names by
         design) — a rare deliberate change; a rename that breaks a su\_pairs reference fails fast at CONFIG anyway, and
         if name-sensitivity were ever wanted the fix is an explicit name field in the signature, not a dump hash. ALL
         existing rlmwf\_03 caches (incl. the 1e7 production) are invalidated once (the embedded old-style hash vs the
         new live signature -> mismatch -> recompute) — self-healing, no format change (the signature block still stores
         a string), no \_GENERATOR\_VERSION bump. The oracles follow: the probe B8 recomposes the domain hash
         INDEPENDENTLY from the child sets (the INTERCEPT marker + the mset / pset hash hex strings);
         test\_hlp\_su\_analysis test\_signature recomposes it the same way. VERIFICATION: the hlp suite 11/0/0 green,
         the verify\_su\_analysis probe (44 checks) green, the full suite (fast tier) 946/0/97 GREEN, the SU VLONG
         10/0/0 (the 1e7 cache regenerated with the new signature).

D-292 | 2026-09-22 | The rarity thresholds become a CONFIG input + the report gets the optional 'Section B: Rarity
         report' (Roberto): the new SuAnalysisConfig.rarity\_thresholds (Optional[List[int]], default None; the
         check\_rarity\_thresholds validator: None / empty = the section OFF — the empty list is LEGAL, the absent
         equivalent; otherwise the positive strictly-increasing integers). The section is the per-feature-instance
         frequency histogram over the half-open bins [0, t1), [t1, t2), ..., [tk, inf) — the FIRST bin the
         zero-frequency codes (the never-observed: the theoretical space minus the observed support — Roberto's
         correction to the initial [1, t1) proposal: the zero-frequency bin is the informative one) — the 'weights that
         can never be learned'. The private \_rarity\_bins (the np.searchsorted binning) replaces the module constant
         \_RARITY\_THRESHOLDS (DELETED — the values now live in the rlm\_00 fixture JSON: [1, 2, 5, 10, 100]); section
         A's audit call drops the argument (the kernel default). The SU-pairs section is ALWAYS 'Section C' now (the
         letter shift is permanent, Roberto's explicit rule). Phase-2-only: NO corpus / cache / signature impact (the
         thresholds are not in the signature — the cache stores the raw counts); the CSV is unchanged. VERIFICATION: the
         new config test (test\_rarity\_thresholds) + the hlp tests (test\_statistics\_report updated to A+B+C, the new
         test\_rarity\_bins (the independent recompute, the verbatim lines) + the test\_rarity\_empty\_off) green, the
         verify\_su\_analysis probe (44 checks, the A8 retargeted to the fixture JSON) green, the full suite (fast tier)
         949/0/97 GREEN (946 + 3).

D-293 | 2026-09-22 | The SU report cosmetic pass (Roberto, the build/test\_su\_00 report as the reference): (1) the
         header DESCRIPTION (the "It evaluates the normalized relationship..." text) moves to the SECTION C preamble
         (after the section title, before the data — the header keeps only the title + the SU legend + the
         corpus/features/pairs summary; the text is now the \_SU\_DESCRIPTION constant); (2) the Section B description
         is rewritten at COLUMN 0 (no indentation, no parentheses, the capitalized "The", two lines: the bins definition
         / the zero-frequency meaning); (3) the Section A data rows are COLUMN-ALIGNED: the name / the inst
         LEFT-justified to the max width, the numeric values RIGHT-justified to the computed max width over the section
         (the K\_obs "obs/eff" field + the never-obs field carry the +1 separator margin, the H / H\_norm / coverage
         fields a 1-space separator); (4) the Section B data rows the same: the same name / inst prefix, the bin LABELS
         at natural width, each bin VALUE right-justified to its own per-bin max width (+1 margin) — the columns of a
         bin align down the section regardless of the value length. The two-pass compute (the rows are collected first,
         the widths computed, then the lines formatted) is the implementation. VERIFICATION: the hlp suite 13/0/0 green
         (the test\_rarity\_bins recomposes the aligned lines verbatim), the worker suite green, the full suite (fast
         tier) 949/0/97 GREEN, the verify\_su\_analysis probe (44 checks, no report-text pins) green.

D-294 | 2026-09-22 | The report cosmetic pass FOLLOW-UP (Roberto): the \_SU\_LEGEND (the SU-range legend: the value
         bands + their meaning) moves from the header to the SECTION C preamble — right after the \_SU\_DESCRIPTION,
         before the data. The header keeps now only the title + the corpus / features / SU-pairs summary. No test /
         probe pins the legend (verified by grep before the move). VERIFICATION: the hlp suite 13/0/0 green, the full
         suite (fast tier) 949/0/97 GREEN, the verify\_su\_analysis probe (44 checks) green.

D-295 | 2026-09-22 | hlp\_random\_play is RETIRED (Roberto, the wrk\_su\_analysis restructure continues): the two
         accumulators move to hlp\_su\_analysis, the two position utilities are dropped as board duplicates. (1)
         Accumulators: MarginalAccumulator + JointAccumulator (with the \_to\_positions + \_DENSE\_THRESHOLD privates)
         move into hlp\_su\_analysis, renamed PRIVATE \_MarginalAccumulator / \_JointAccumulator (the D-290
         \_\_all\_\_ policy: the only src consumer is hlp\_su\_analysis itself — the tests / the probe reach the names
         directly, the \_signature precedent). hlp\_su\_analysis is now the sole home of the phase-1 frequency data
         plane. (2) Utilities: ec\_of and initial\_position had NO src consumer (only the test suite + the
         verify\_su\_analysis probe) and are BYTE-IDENTICAL to board.position\_empty\_count (64 -
         popcount(mover|opponent) = the empty-square count) and board.initial\_game\_position (the same E4+D5 / D4+E5
         hex — the D-211 canonical source); both are dropped, the probe's B2 cross-check now uses
         position\_empty\_count. (3) Tests: test\_hlp\_random\_play DELETED; TestMarginalAccumulator (3) +
         TestJointAccumulator (3) + TestPrngIntegration (2) MIGRATED to test\_hlp\_su\_analysis (13 -> 21 tests, the
         \_corpus helper travels); TestInitialPosition + TestEcPin DROPPED (not migrated) — they pin BOARD functions,
         already pinned by test\_board (the initial position + its golden, the position\_empty\_count scalar / array /
         cross-check); the 60 / 40 values on the hand-crafted positions are accepted lost (the formula is covered on
         both sides; test\_board untouched). (4) Probe: verify\_su\_analysis migrated (the accumulators via hlp.\_\*,
         position\_empty\_count for the B2 cross-check; the check count stays 44). (5) Docs: the 2 mirrors deleted; the
         hlp\_su\_analysis / test mirrors gain the accumulators; hlp\_feature\_analysis + random\_game + the board
         consumer list reworded. VERIFICATION: the full suite (fast tier) 947/0/97 GREEN (949
         - 10 deleted + 8 migrated), test\_hlp\_su\_analysis 21/0/0, the worker suite VLONG 10/0/0 (the 1e7 corpus), the
           verify\_su\_analysis probe (44 checks) green, the docs audit 92 mirrors with the 6 pre-existing findings
           only.

D-296 | 2026-09-22 | hlp\_su\_analysis SPEAKS THE POSITION LANGUAGE (Roberto, the wrk\_su\_analysis restructure
         continues): the parallel (mover, opponent) arrays no longer cross a module boundary. (1) Module:
         \_to\_positions DELETED (it only re-merged what random\_game\_play\_path already returns);
         \_MarginalAccumulator.add / \_JointAccumulator.add take the PositionArray (add(pos), one structured row per
         position); hlp\_su\_analysis\_compute builds the batch as the np.full of the initial\_game\_position structured
         scalar (no more field unpack + column\_stack round-trip) and feeds the accumulators the final[keep] slices
         directly — one masked copy per chunk instead of two (the 16n-byte rebuild is gone from the accumulation hot
         path). (2) Tests: the \_corpus helper returns a single concatenated PositionArray; the 12 add() call sites
         migrated; the 2 manual layout builds DROPPED (they pinned \_to\_positions's layout, which no longer exists —
         the layout is pinned by test\_board / test\_feature, the compute\_indexes calls now take the corpus array); the
         unused make\_position import retired. 21/0/0. (3) Probe: the CLEAN version (Roberto's choice): the B tier
         harvests the final[keep] position slices directly; the positions\_of helper DROPPED (the module has no layout
         build of its own anymore, the probe independence lives in the VALUE re-derivations); the field extraction
         pos['mover'] / pos['opponent'] only for the probe's own invariants; B2 the position\_empty\_count array
         cross-check; the NEW A10 structural check (no \_to\_positions / column\_stack / field-split feeding in the hlp)
         — 44 -> 45 checks. (4) Docs: the hlp mirror (the add(pos) + the position-language bullets + the A10 pin) + the
         test mirror reworded. CORPUS DETERMINISM UNCHANGED: the batch bytes are identical (the np.full structured
         scalar vs the column\_stack view), the PRNG stream contract untouched, the cache signature unchanged (the
         rlmwf\_03 caches stay valid). VERIFICATION: the full suite (fast tier) 947/0/97 GREEN, test\_hlp\_su\_analysis
         21/0/0, the worker suite VLONG 10/0/0 (the 1e7 corpus), the verify\_su\_analysis probe (45 checks) green, the
         verify\_effect\_size probe 29 / 0, the docs audit 92 mirrors with the 6 pre-existing findings only.

D-297 | 2026-09-22 | the frequency accumulators take ONLY the fset (Roberto, the wrk\_su\_analysis restructure
         continues): the blocks argument was a DERIVED attribute of the fset, and passing it separately was misleading.
         (1) Module: \_MarginalAccumulator.\_\_init\_\_(fset) + \_JointAccumulator .\_\_init\_\_(fset, su\_pairs) — the
         per-feature blocks are derived internally from the documented FeatureSet.feature\_blocks property (the (name,
         col\_start, col\_end, n\_configurations, n\_instances) tuples over the non-intercept features, the
         fset.features order — exactly the value hlp\_su\_analysis\_compute already passed); the self.blocks storage is
         DROPPED (nothing external reads it); the joint keeps its name -> block dict (the su\_pairs resolution).
         hlp\_su\_analysis\_compute drops the orphaned blocks local. (2) Tests: the \_toy\_blocks helper DROPPED (a
         VERBATIM copy of the feature\_blocks property body — a runtime identity check confirmed it on the toy fset; it
         pinned nothing independent); the TestJointAccumulator.\_blocks / TestPrngIntegration.\_blocks delegations
         dropped with it; all 12 accumulator constructions take the fset only; the joint cross-feature test resolves its
         block columns via fset.feature\_blocks (the test's own derivation for the manual dict oracle). 21/0/0. (3)
         Probe: the 3 accumulator call sites take the fset only; the probe's OWN blocks local (from the campaign) is
         KEPT for its A9 sub-variable expansion check + the blocks\_by\_name oracle. (4) Docs: the hlp mirror API bullet
         + the test mirror goldens bullet. NO behavior change (the same tuple values, the property computed once per
         accumulator construction, never in the hot path); no cache signature / binio layout / report change (the
         rlmwf\_03 caches stay valid). VERIFICATION: the full suite (fast tier) 947/0/97 GREEN, test\_hlp\_su\_analysis
         21/0/0, the worker suite VLONG 10/0/0 (the 1e7 corpus), the verify\_su\_analysis probe (45 checks) green, the
         verify\_effect\_size probe 29 / 0, the docs audit 92 mirrors with the 6 pre-existing findings only.

D-298 | 2026-09-22 | hlp\_feature\_analysis is SPLIT (Roberto, the wrk\_su\_analysis restructure continues): the module
         was the SHARED data plane of two levels whose kernel families proved DISJOINT (hlp\_su\_analysis consumed the 5
         SU kernels, wrk\_effect\_size the 2 ES kernels, no shared edge), and 3 adherence helpers (kl\_divergence,
         total\_variation, chi\_square\_goodness) were exported in \_\_all\_\_ though used ONLY internally. (1)
         hlp\_su\_analysis ABSORBS the 5 SU kernels as PRIVATE \_entropy / \_mutual\_information /
         \_symmetric\_uncertainty / \_dispersion / \_never\_observed\_audit (the D-290 policy: test/probe-called names
         never in \_\_all\_\_, the \_signature precedent), the 8 internal call sites renamed, the hlp\_feature\_analysis
         import block dropped. (2) hlp\_feature\_analysis becomes the EFFECT\_SIZE kernels module: \_\_all\_\_ =
         ['anova\_eta\_omega', 'adherence'], the 3 adherence helpers PRIVATE (\_kl\_divergence, \_total\_variation,
         \_chi\_square\_goodness — Roberto's "exported but only used internally"), both docstrings rewritten. (3) Tests
         (D-273): the 5 SU kernel classes (16 tests) MIGRATED to test\_hlp\_su\_analysis (4 -> 9 classes, 21 -> 37
         tests, the hlp.\_\* private-name calls); the 5 ES classes stay (32 -> 16), the 3 privatized helpers are called
         via the module import hlp\_fa.\_\* (the D-290 style). (4) Probes: the verify\_effect\_size F5 rewritten on the
         NEW split boundary (the ES family in hlp\_feature\_analysis, the SU kernels in hlp\_su\_analysis, the private
         \_symmetric\_uncertainty); the verify\_su\_analysis header comment reworded. (5) Runner: the two suite comments
         reworded (the T11 / T12 labels travel to test\_hlp\_su\_analysis). (6) Docs: the 2 mirrors rewritten
         (hlp\_feature\_analysis src + test), the hlp\_su\_analysis src mirror (the kernels LOCAL) + the test mirror
         (the 5 migrated rows / the goldens / the conventions) reworded. NO behavior change (the kernel bodies are
         verbatim, pure relocation + rename); no cache signature / binio / report change (the rlmwf\_03 caches stay
         valid); wrk\_effect\_size is UNTOUCHED (its import stays valid byte-identical). VERIFICATION: the full suite
         (fast tier) 947/0/97 GREEN, test\_hlp\_feature\_analysis 16/0/0, test\_hlp\_su\_analysis 37/0/0, the worker
         suite VLONG 10/0/0 (the 1e7 corpus), the verify\_su\_analysis probe (45 checks) green, the verify\_effect\_size
         probe (29 checks, the new F5 boundary) green, the docs audit 92 mirrors with the 6 pre-existing findings only.

D-299 | 2026-09-23 | the COLD compute of hlp\_su\_analysis is OPTIMIZED (Roberto, after the SU\_ANALYSIS profiling): the
         1e7 cold compute spends ~70% of its time in the \_JointAccumulator — the per-wave DICT-MERGE of the np.unique
         output (~8.5M dict.get per 1e6-lane wave on the 28 cells of the rlm\_test\_su\_00 fixture, the 24 off-diagonal
         cells carrying ~330k-465k observed keys each) + the 28 sorted() over the ~465k-key dicts in result(); the
         statistics phase re-runs \_entropy ~110 times over 7 sub-variables. (1) The \_JointAccumulator storage becomes,
         per cell, the OBSERVED keys K (u64, SORTED) + the counts C (int64): each wave's np.unique output is folded in
         with searchsorted + np.add.at + a re-sort of the appended new keys (the sorted-K invariant keeps the next
         wave's searchsorted valid) — NO Python dict, NO per-key loop; result() unpacks K // ncj, K % ncj, C directly
         (no sorted()). (2) \_mutual\_information takes the PRE-COMPUTED marginal entropies (joint\_counts, H\_u, H\_v)
         instead of the marginal count arrays; \_su\_values computes each sub-variable's entropy ONCE (the h\_cache).
         DEFERRED (Roberto, "magari lo vediamo dopo"): the double fset.compute\_indexes per wave (the marginal + the
         joint each recompute the same index matrix) — I-020. The MI tests pass the entropies (the hlp.\_entropy calls,
         the D-299 signature). EQUIVALENCE (the acceptance criterion): the new compute vs the dict-merge's CACHED output
         on the 1e7 corpus — the signature identical, the 7 sub-variables + the 28 joint cells bit-identical, the
         statistics report + CSV byte-identical (so the rlmwf\_03 caches stay valid). PERF (the per-wave
         micro-benchmark, 1e6-lane waves, the rlm\_test\_su\_00 fixture): joint.add 5.9 -> ~2.0 s/wave (the 4.9 s/wave
         dict loop is gone; the wave's unique 0.9 s + the re-sort remain), the whole wave 8.5 -> ~4.9 s; the full 1e7
         cold compute ~95 s -> ~37 s on the same (loaded) machine. VERIFICATION: the full suite (fast tier) 947/0/97
         GREEN, test\_hlp\_su\_analysis 37/0/0, the worker suite VLONG 10/0/0 (the 1e7 corpus — its fixture is the
         4-cell EDGE-LMC pair, where the old dict loop was already cheap), the verify\_su\_analysis probe 45 / 0, the
         verify\_effect\_size probe 29 / 0, the docs audit 92 mirrors with the 6 pre-existing findings only.

D-300 | 2026-09-23 | the per-wave index matrix is computed ONCE in the compute loop (Roberto, the I-020, raised
         after D-299): the D-299 cold compute was ~37 s but the \_MarginalAccumulator.add and the \_JointAccumulator.add
         EACH recomputed fset.compute\_indexes(pos) over the wave's harvested lanes (~173 ms/wave each on the 8-column
         uint32 index matrix, ~346 ms/wave, ~3.8 s per 1e7). (1) The compute loop now computes idx =
         fset.compute\_indexes( final[keep]) ONCE per wave and feeds the SAME matrix to both add(idx) — the old add(pos)
         computed it internally. (2) BOTH add() take the index matrix (the uint32 (N, I) array), NOT a PositionArray; n
         = idx.shape[0] (the empty guard unchanged); fset is kept ONLY for the feature\_blocks layout (D-297). The D-296
         position language stops at the loop boundary: the harvested final[keep] lanes feed compute\_indexes in the
         loop, and the accumulators speak the derived index matrix (the parallel (mover, opponent) arrays still never
         cross a module boundary — the A10 invariant intact). The 12 test add call sites + the 3 probe add call sites
         now feed fset.compute\_indexes(pos) (the probe's marginal site reuses the oracle's own idx, the two joint sites
         the in-scope idx). EQUIVALENCE: the index matrix is a PURE FUNCTION of the harvested lanes, so computing it
         once or twice yields the same values — the new compute vs the D-299 cached output on the 1e7 corpus is the
         signature identical, the 7 sub-variables + the 28 joint cells bit-identical, the statistics report + CSV
         byte-identical (the rlmwf\_03 caches stay valid). PERF: ~173 ms/wave removed per 1e7 run (~1.9 s, ~5% of
         the D-299 ~37 s) + one 32 MB index allocation per wave; the main win is clarity (the loop owns the index
         computation, the accumulators are pure index->count machines). I-020 CLOSED (moved to ideas-closed.md).
         VERIFICATION: the full suite (fast tier) 947/0/97 GREEN, test\_hlp\_su\_analysis 37/0/0, the worker suite VLONG
         10/0/0 (the 1e7 corpus), the verify\_su\_analysis probe 45 / 0, the verify\_effect\_size probe 29 / 0, the docs
         audit 92 mirrors with the 6 pre-existing findings only.
