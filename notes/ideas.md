# Ideas / future backlog

Format: I-NNN | status (idea | in-progress | done | dropped) | idea

I-001 | done | Full restructure of the original repo (executed as D-133/D-134: the twolm → reversi reorganization, Roberto's explicit decision, 2026-09-08).
       The notes produced here should migrate into the new repo as its
       documentation skeleton.

I-002 | done | Vectorize `position_flips` / `position_make_move`.
       The author's own comment in board.py flags this: `_kogge_stone_mm` is
       currently scalar Python while `legal_moves` is numba-parallel.
       Executed as D-140 (2026-09-08): the 2 prange kernels + the strict
       dual API, the same technique as legal_moves (D-111).

I-003 | idea | Named move constants (MOVE_PASS=64, MOVE_NOT_AVAILABLE=65,
       MOVE_UNKNOWN=66) instead of magic numbers. Would also fix the implicit
       dependency on NumPy shift-wrap semantics in `position_is_move_legal`
       (issue R3 in notes/board.md).

I-004 | idea | (placeholder — Roberto's future-evolution ideas go here as
       they come up)

I-005 | done | Next session starts a NEW module (Roberto, 2026-08-26).
       Target module to be chosen with Roberto. Candidate: a game-loop
       module (start position, turn/pass/game-over rules, history) —
       board.py is proven a complete game kernel by the 200-game random
       simulation of 2026-08-26; the loop itself is ~25 lines on top of
       the public API. Other candidate: the next source file of the
       original repo (file-by-file modernization).
       RESOLVED (2026-08-28, Roberto, session close): the plan is the
       pipeline port — the original repo brought in module by module
       with verified code and complete tests; the game-loop candidate
       is NOT in the plan. mobility.py was the first pipeline module
       completed (session 10).

I-006 | follow-up | Legacy migration debt (raised 2026-08-27, D-024):
       PatternSet.names/masks are now @property (attribute-style). If the
       original codebase contains callers using the old method syntax
       (.names() / .masks()), those call sites must be updated to
       parenthesis-free property access when that file is migrated into
       reversi. Count of affected sites unknown until that file is
       analyzed — grep the original codebase for ".names()" / ".masks()".

I-007 | follow-up | FeatureSet column-labelling helper (raised
       2026-08-28, D-041, feature module M3): FeatureSet offers no
       way to map a column of its (N, I) index matrix to the feature
       name producing it (unlike MobilitySet.names/masks, D-024).
       The pipeline's table builders will need it. Left as-is on
       Roberto's decision; design the helper when the pipeline
       module that labels columns arrives (note: each pattern
       occupies n_instances D8-instance columns, so a
       column-level labelling needs an instance-aware design).

I-009 | follow-up | Pipeline construction boilerplate (raised
        2026-08-29, session 19, R3 discussion): Roberto notes his
        pipeline client carries a bit of boilerplate in the model
        construction (worker/context/machine wiring). When the
        logistic_model/RLM pipeline module arrives in the workspace,
        evaluate a declarative step table / @step-style helper /
        pipeline base class on top of StateMachine to trim it.
        Blocked on: the pipeline module not being in the workspace
        yet (can't see the actual boilerplate).

I-010 | follow-up | Redesign of the StateMachine context injection
        (parked 2026-08-29, D-070, session 19, M9): the constructor
        injects log_event + the cache helpers as a side effect on
        the passed-in Context, so a shared context re-binds to the
        LAST machine built on it (V17). Roberto's call: leave
        as-is — the injection is fundamental, the domain workers
        (lm_worker_config, logistic_model) depend on it. To be
        evaluated once all the domain modules are in the workspace
        and their call patterns are visible: an explicit machine
        reference, or context-owned helpers.

I-011 | done | "Storicizzazione" of the JSON config used to generate a
        model (raised 2026-08-30, session 21, D-077 R1 discussion):
        Roberto questions whether the CONFIG step needs a CACHE at
        all — the cache_manager-style load-or-compute flow does not
        fit a JSON file. The real need may be a STORICIZZAZIONE:
        keeping (with history) a copy of the JSON config that
        generated a given model, as an audit/stability artifact of
        the run — distinct from a recomputable cache. D-078 keeps
        the current ad-hoc behaviour (write-if-changed, checksummed
        flat files) as-is; to be evaluated WHEN THE FULL PIPELINE IS
        COMPLETE, together with the cache-flow consistency question
        (bare-hex vs binio sidecar, the proven read asymmetry).
        Executed as D-142 (2026-09-09): the ad-hoc cache is REMOVED
        and the need is met in its C1 form — at SAVE, next to the
        model file, the provenance record (<output>.config.json, the
        normalized dump of the effective config, + the binio
        .SHA3-256 sidecar) + the config fingerprint in the analytics
        reports. The versioned-history part (option B) is explicitly
        dropped: the JSON evolution stays in the file's VCS.
I-012 | idea | Pipeline level order: evaluate moving FEATURES
        BEFORE POSITIONS (raised 2026-08-31, session 22, D-081
        test-M1 discussion, D-082): Roberto confirms the test
        setUp comment ("Move to POSITIONS first, as FEATURES
        depends on the configuration loaded there") is inaccurate
        — FEATURES depends on the config loaded at the CONFIG
        level (step 1), not on POSITIONS — and wants to EVALUATE
        moving the FEATURES level before POSITIONS in the
        pipeline. The comment is left as-is in the test for now.
        To be evaluated as a line-by-line pipeline change.

I-013 | done | Study whether the GRADIENT fg closure can be
        sped up (raised 2026-09-01, session 25, during the D-094
        R1 discussion): Roberto believes the closure is (or will
        be) the pipeline bottleneck for large models — "Quando
        avremo completato la PIPELINE, uno degli interventi da
        fare sarà verificare se sia possibile velocizzare questa
        funzione, credo sia il collo di bottiglia della PIPELINE
        per modelli di grosse dimensioni. Ma vedremo". The hot
        spots: the per-call `w[X]` fancy indexing + per-row sum
        (M×P), the sigmoid over (M,), and the broadcast +
        np.bincount gradient accumulation (M×P → N). To be
        evaluated only after the pipeline is complete (I-013 is
        the post-pipeline performance study); the float32 return
        contract (D-094 R1) is a constraint on any rewrite.
        STUDIED (session 34, 2026-09-09/10, pipeline complete):
        confirmed — fg = 96-99% of the A2050 OPTIMIZE time (418 fg
        calls × 732 ms in the 318 s production run; cProfile 99.3%).
        The two M×P temporaries per call (gather result + bincount
        buffer, 384 MB each) are the waste. A block-parallel
        numba single-pass kernel (K3: 8 fixed row-blocks, private
        f64 g-buffers, fixed final order — race-free and
        run-deterministic, numba 0.67 has no CPU atomics) measured
        46 ms/call and, run to full A2050 convergence: 321.3 s →
        25.3 s (12.7×), same CONVERGED_MIN_GRAD, Δf rel 0.07%
        (goldens re-pin required). Negative result: m=93 is
        load-bearing (m=20/10 do not converge in 500 iters and are
        slower). Full report: notes/analyses/optimize_performance.md.
        O1 SHIPPED (D-145, 2026-09-09, Roberto's ruling: "Facciamo
        solo O1 in questo modulo. Fatto finito, fatto checkin ...
        poi miglioriamo anche lbfgs on O2 ... I config rlm_03/rlm_04
        a true (gli altri no) ... Procedi!"): the
        high_performance_fg config flag (default false) + the K3
        numba kernel in hlp_gradient (the classic path kept
        verbatim) + the wrk_gradient wiring; rlm_03/rlm_04 opt in;
        the A2050 re-baseline: OPTIMIZE 26.9 s (11.9×), chain
        52.0 s (6.7×); the A2050 trajectory 356 iters / f
        1.4453826e-03 (Δrel 0.07% vs the classic). O2 = D-146
        (the two-loop, the ≈ 8.2 s / 30% second cost center):
        the numba two-loop — the original proposal — measured
        1.00-1.02× (NEGATIVE RESULT: memory-bandwidth bound +
        the serial two-loop recurrence resists prange), NOT
        adopted; O2b (Roberto's ruling) shipped instead: the
        two-loop's 2m per-op product temporaries (~58 MB
        allocated per call at A2050 scale) replaced by ONE
        pre-allocated f64 out= buffer — bit-for-bit the same
        math (no golden re-pin; the VLONG suite green on the
        exact D-145 goldens) at 1.39× (23.2 -> 16.9 ms/call).
        I-013 TOTAL (A2050): OPTIMIZE 321.3 s -> 22.8 s (14.1×),
        chain ~350 s -> 48.5 s (7.2×). O3 (the pure-numpy 1.2×
        variant) considered, not chosen. O4 closed by the m
        negative result.

I-014 | idea | Hot-restart ("restart a caldo") of the OPTIMIZE
        level from the checkpoint's warm weights (raised 2026-09-01,
        session 26, during the D-096 R1 discussion): when a
        ridge_regularization change invalidates the checkpoint,
        D-096 R1 makes the run start FROM SCRATCH — the same
        behavior as a logit_clipping (zed) change — and that is the
        behavior Roberto chose ("keep the clipping-equivalent
        behavior"); the alternative, resuming the L-BFGS from the
        checkpoint's warm state under the new objective, was
        explicitly parked. Roberto: "un'ottimizzazione che
        svilupperei solo in seguito, se capiamo che ha un valore
        pratico". The plumbing already exists (the checkpoint
        carries the full L-BFGS state — w + sl/yl/rho + iters — and
        opt_lbfgs has the warm-start kwargs, consumed on the
        INCOMPLETE resume path); the open question is whether a warm
        restart under a CHANGED objective is numerically sound /
        worth the extra semantics.

I-015 | done | CLIENT_CHECK: a new pipeline level after SAVE —
        the saved-model file acceptance test (raised 2026-09-10,
        Roberto: "iniziamo una nuova task. Aggiungiamo un LEVEL
        dopo SAVE, lo chiamiamo client_check. Legge il
        model_weights file, costruisce la evaluation function e
        ricalcola i residui della validazione. Devono coincidere
        a meno di 1e-9 con quelli della validazione."). Executed
        as D-148 (2026-09-10): the 16th level re-reads the model
        file, builds the client's array Evaluation Function on
        the FILE weights, and recomputes the validation residuals
        in Y space — they must coincide with the in-memory
        VALIDATE forward pass's residuals within
        client_check_tol (the new LMConfig field, default 1e-8,
        Roberto's "valore del config JSON. Pulito!" ruling;
        Roberto's 1e-8 for 1e-9: "non cadiamo dentro problemi di
        ordine delle somme"). A1a: the reference is recomputed
        from the in-memory ctx state (VALIDATE untouched). The
        bit-identity holds at every scale: the synthetic 2000-set
        (the scratch probe + the no-DB suite golden), A2030
        (20000, the DB-gated log pin) and A2050 (199932, VLONG)
        all measure max|diff| = 0.0; the tolerance guards
        against pipeline drift and file corruption (the
        corruption case measures 1.959e-01 — ~10^7 above).
