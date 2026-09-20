# ideas-closed.md — the closed ideas (the record)

Role: the closed counterpart of notes/ideas.md — the ideas whose status is `done` or `dropped`. An idea MOVES here from
notes/ideas.md, compacted to its statement + the execution (or drop) pointer + the outcome, in the same commit as the
decision that closes it. The campaign history stays in notes/decisions.md and the journal volumes: this file is the
I-NNN index into it, never a narrative. Format (D-235): `I-NNN | status | ...`, ~120 chars/line, a 9-space continuation
indent, a blank line before every entry; code spans for paths / identifiers. The I-numbers are global and immutable
across the two files.

I-001 | done | Full restructure of the original repo — executed as D-133/D-134 (2026-09-08, Roberto's explicit
         decision): the twolm → reversi reorganization; the notes produced here are the new repo's documentation
         skeleton.

I-002 | done | Vectorize `position_flips` / `position_make_move` (raised by the author's own comment in board.py:
         `_kogge_stone_mm` scalar Python while `legal_moves` was numba-parallel) — executed as D-140 (2026-09-08): the
         two prange kernels + the strict dual API, the same technique as `legal_moves` (D-111).

I-003 | done | Named move constants instead of magic numbers (raised 2026-08-26). Executed as D-242 (2026-09-19):
         `MOVE_PA` / `MOVE_NA` / `MOVE_UN` in board.py (`__all__`, the `Move` domain type), the bare 64/65/66 replaced
         in board.py / random_game.py / hlp_wave.py (`PA` re-exported), the square-count 64 on `__square_max_value__`,
         the literal anchor pinned in `TestMove::test_move_constants`. The second motivation (the NumPy shift-wrap
         dependency in `position_is_move_legal`) was ALREADY fixed at D-018; the wrap survives only in
         `move_as_bitboard`, documented and pinned.

I-004 | dropped | The reserved placeholder slot ("Roberto's future-evolution ideas go here as they come up", 2026-08-26)
         — retired 2026-09-19: the backlog no longer needs a reserved slot (the later ideas, I-014 and I-018, were
         recorded as normal entries).

I-005 | done | The next session starts a NEW module (raised 2026-08-26). RESOLVED (2026-08-28, Roberto, session close):
         the plan is the pipeline port — the original repo brought in module by module with verified code and complete
         tests; the game-loop candidate is NOT in the plan. `mobility.py` was the first pipeline module completed
         (session 10).

I-006 | dropped | Legacy migration debt (raised 2026-08-27, D-024): `PatternSet.names` / `.masks` became `@property`, so
         legacy callers using the method syntax would need updating at migration time. Closed 2026-09-19: the port
         campaign is complete (D-119: the pipeline is 15/15, D-104/D-113) and no legacy call site survived the migration
         — the only `.names()` occurrence is prose in `docs/src/reversi/mobility.md`.

I-008 | dropped | Extend the papers collection beyond 2002 (dropped at D-125, 2026-09-06): the copyrighted collection
         left the workspace scope — dropped, not moved (Roberto's call).

I-009 | done | Pipeline construction boilerplate in the model client (raised 2026-08-29, session 19, R3 discussion;
         unblocked 2026-09-19 with the pipeline port). The evaluation was the deliverable: the pipeline base class
         was already realized by `BaseModel` in the port campaign, the declarative step table exists in effect
         (the 19-entry workers list in `logistic_model.py`), and the @step helper was rejected (the 76 factory
         lines + 18 imports saved would cost a registry mechanism, the 41 factory call sites in 6 test files +
         13 probes, 19 mirror docs, and zero behaviour benefit). Closed 2026-09-19 as D-264, no code action: the
         remaining explicit assembly is design, not debt; a second pipeline (DeepNetworkModel) would re-evaluate
         with concrete data.

I-011 | done | "Storicizzazione" of the JSON config used to generate a model (raised 2026-08-30, D-077 R1): Roberto
         questioned whether CONFIG needs a CACHE at all — the real need may be keeping, with history, the config that
         generated a given model. Executed as D-142 (2026-09-09) in its C1 form: at SAVE, the provenance record
         (`<output>.config.json` + the binio `.SHA3-256` sidecar) + the config fingerprint in the analytics reports; the
         versioned-history part (option B) is dropped — the JSON evolution stays in the file's VCS.

I-012 | done | Pipeline level order: move FEATURES BEFORE POSITIONS (raised 2026-08-31, D-081/D-082): Roberto confirmed
         the test setUp comment was inaccurate (FEATURES depends on the config loaded at CONFIG, step 1, not on
         POSITIONS). DONE at D-157 (2026-09-11): FEATURES is step 2, right after CONFIG; the inaccurate setUp comment
         went with the gate (`test_wrk_features` is DB-free).

I-013 | done | Study whether the GRADIENT fg closure can be sped up (raised 2026-09-01, D-094 R1). STUDIED + SHIPPED
         (D-145/D-146, session 34): fg measured at 96-99% of the A2050 OPTIMIZE time; the K3 block-parallel numba kernel
         behind the `high_performance_fg` flag (O1) + the pre-allocated f64 `out=` two-loop buffer (O2b). TOTAL (A2050):
         OPTIMIZE 321.3 s -> 22.8 s (14.1×), chain ~350 s -> 48.5 s (7.2×). Negative results: O2 (the numba two-loop,
         memory-bandwidth bound) not adopted; O3 not chosen; O4 closed by the m = 93 load-bearing finding. Full report:
         notes/analyses/optimize_performance.md.

I-015 | done | CLIENT_CHECK: a new pipeline level after SAVE — the saved-model file acceptance test (raised 2026-09-10).
         Executed as D-148 (2026-09-10): the level re-reads the model file, builds the client's array EF on the FILE
         weights and recomputes the validation residuals in Y space; they must coincide with the in-memory VALIDATE
         residuals within `client_check_tol` (default 1e-8). Bit-identity at every scale (max|diff| = 0.0: the synthetic
         2000-set, A2030, A2050); the file-corruption case measures 1.959e-01.

I-016 | done | PLOT: a new pipeline level with matplotlib — the run's diagnostic figures (raised 2026-09-10). Executed
         as D-149 (2026-09-10): the 17th and LAST level (after CLIENT_CHECK), seven Y-space figures (the three R
         classics + four extensions), the PlotConfig pilot (enable + format + dpi + dir_name + the plot-name whitelist),
         the seeded jitter / KDE. Campaign: D-149..D-155; the R reference file was a scratch artifact, removed
         2026-09-11 (D-156d) — no live doc references it.

I-017 | done | Analytical properties of the FEATURES — the SU / eta² / omega² analysis (raised 2026-09-11). Executed as
         the I-017 campaign (T1..T19, D-156..D-189): the MT19937 PRNG port + the G0 wave generator, the OPTIONAL
         FEATURE_ANALYSIS (step 3) and EFFECT_SIZE (step 6) levels — default FALSE (D-175) — and the 18-level pipeline
         live and green. Project doc: notes/analytical_properties_of_features.md.

I-018 | done | The top-20 outlier report in VALIDATE + the 20 records in the context (raised 2026-09-11, parked
         at D-189). Executed as D-243..D-246 (2026-09-19): VALIDATE now returns a `ValidationResult` (the 7 metrics +
         the f64 `y_pred` / `rn_y` series) and publishes `ctx.vld_y_pred` / `vld_rn` / `vld_outliers` (the 20 raw
         records) while LOGGING the D-150 report (the same 21 lines, step 18 -> 14; the D-150 test moved from
         `test_wrk_plot` to `test_wrk_validate`); `top_outliers` is the stable-argsort kernel. The duplication chain
         went 3 -> 1 on the validation side (CLIENT_CHECK consumes `ctx.vld_rn`, D-245) and 2 -> 1 on the training side
         (`ctx.train_dense_rn` published by ANALYTICS, D-246), so PLOT is now a PURE rendering level:
         `collect_plot_data` assembles the published series and runs no forward pass. Proof that no number moved: the
         PNG byte-determinism golden and the full-chain pins hold. A dedicated probe re-pin (D-244) cleared the stale
         step/slot pins the campaign's sweep exposed.

I-019 | done | The `run()` facade + the `target_level` consumption (raised 2026-09-19 during the P2 rename sweep,
         closed the same day). Executed as D-260: `BaseModel.run(target_level=None)` drives the stop — the first real
         level (CONFIG) runs first, then the explicit argument, else the domain hook `_configured_target_level()`
         (`LMConfig.target_level` in LogisticModel), else the last step; "last" (any case) and a blank value mean the
         whole pipeline, and any level name or index is a legal stop. A second `run()` with a deeper target RESUMES
         without re-running the levels done (verified at the 1e7 scale: one SU_ANALYSIS up, zero downs). Tests 17 -> 29
         in `test_logistic_model` (the mocked resolution cases + the real-config class); the register line in
         notes/rules.md; the hub probe's V9 gained the `run()` boundary label.
