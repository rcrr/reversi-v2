# Decisions log — historical record

Format: D-NNN | date | decision | rationale

This is the append-only HISTORICAL LOG: the "why" of every action
and commit in this workspace. It grows without bound and is
consulted only when needed or for historical research. The rules
in force right now live in notes/rules.md (the active
legislation): when a decision establishes an enduring rule, the
rule is promoted there with this D-number as the origin pointer
(same commit); a retirement removes the line from rules.md and
is logged here with a new D-number. D-numbers are sequential and
never reused or renumbered (the docs' State lines and the
cross-references depend on them). Volumes (D-118): the open log
keeps this name (notes/decisions.md); when it exceeds 2000
lines it closes at a session boundary as notes/decisions_NNN.md
and a new open log is opened — the D-numbers stay global across
volumes (volume 000: D-001…D-116, closed 2026-09-06).

D-117 | 2026-09-06 | Re-structured the entry-point file: renamed
        NOTES.md → notes/overview.md and split the per-file state
        into two alphabetical tables (Source files, Test files)
        with a strict one-line State grammar (Roberto: the old
        Inventory was unbalanced — 2-line entries next to
        page-long ones — and the file list appeared three times:
        Inventory, Where we are, Index; the situation sections
        should come before the file list).
        | The State cell of each row now carries a status word +
        the open/parked items + the D-pointer range (one line,
        always) — the campaign history stays in the decision log
        (the D-115 split was the premise; this removes the last
        duplication). The per-file Where-we-are bullets merged
        into the tables; Where we are keeps only the non-file
        state (the plan, the collaboration memory). New section
        order: Project · Conventions in the code · Environment ·
        Where we are · Next steps · Source files · Test files ·
        Index. The probes stay out of the tables: one
        Environment bullet (20 tracked, 20/20 green in both
        modes). The Index drops the 38 docs/ mirror bullets
        (their paths are the Doc column of the tables) and lists
        the notes/ files only. The Suite column was re-verified
        module-by-module against a live-DB run (2026-09-06):
        673/0/18 (the gated baseline: 87 skipped); several
        suites had grown since the last sweep and the old
        Inventory carried stale numbers (test_cache_manager
        21→22, test_feature 19→20, test_lm_worker_validate 3→5,
        test_lm_worker_vld_positions 3→9, test_logistic_model
        15→17). The old Environment "Suite status (2026-09-02)"
        bullet (still saying 193/64/20) replaced by the verified
        line. AGENTS.md rules 1–2 + Layout updated; the rules.md
        grammar retires the old "terse history" Status form
        (PROMOTED same commit).

D-118 | 2026-09-06 | Rotated the decision log into volumes: the
        4189-line decisions.md (D-001…D-116) closed as
        decisions_000.md; a new open decisions.md (this file)
        starts at D-117.
        | The log had crossed the 2000-line journal cap (Roberto
        proposed the same rotation as the journals). Protocol:
        the OPEN volume keeps the name decisions.md, so the
        AGENTS.md / rules.md / overview pointers never change;
        a closed volume becomes decisions_NNN.md; the D-numbers
        stay global and immutable, so every cross-reference
        survives the rotation. The protocol was PROMOTED into
        rules.md (the Roles section) in the same commit. The
        next rotation happens at a session boundary, like the
        journal volumes.

D-119 | 2026-09-06 | The Project section of notes/overview.md was
        rewritten with Roberto's new identity statement,
        replacing the "file-by-file modernization" text (the
        D-115-era wording).
        | The port campaign is complete (the pipeline is 15/15,
        D-104/D-113): the workspace's identity has moved from
        "a modernization in progress" to what it actually does
        now — the research and development of evaluation
        functions for Reversi positions, machine-learning
        methods over the solved positions generated from random
        gameplay paths (the 15-level pipeline). Nothing the old
        text carried is lost: the staging constraint ("only
        files under active work live here") lives in AGENTS.md
        (auto-injected, stronger form), and the I-001
        full-repo-restructure pointer lives in notes/ideas.md
        (referenced from the Next steps). The Project section
        stays a pure identity statement; the current phase
        stays in Where we are.

D-120 | 2026-09-06 | Next-steps trim (Roberto's item-by-item
        review).
        | (1) The endgame-solver integration item removed
        (Roberto's call; the A2xxx production context stays in
        the rlm_client.md intro — its Open issues were already
        None, so nothing went stale). (2) The "Deferred" label
        of lm_worker_config R1 retired (Roberto: every item in
        Next steps is "next" by definition) — and the item is
        now LIVE: its D-078 revisit trigger (the pipeline
        completion) is met (15/15), so it becomes the last
        bullet = the next concrete action; the mirror doc
        label updated "deferred" → "revisit due" (docs only).
        (3) The journal-rotation reminder bullet removed:
        rotation is the standing log_rules.md legislation
        (log_001 → log_002 at the next session boundary), not a
        next step. (4) The stale "Next concrete action" bullet
        (pointing at the D-115 restructure) removed. Kept, with
        the explanation given in session: the parked
        test_pattern T18 (noted-only — the production code
        already casts to int; the note is for external
        expressions; no code action) + M1 (the stale PatternSet
        Raises docstring: it says TypeError, but the
        @validate_call checks raise ValidationError — a
        one-line docstring fix) and the reported-only
        test_board.py header grammar nit (the broken "How to
        use the unit tests board module." sentence; the
        'environmeant' typo itself was fixed in D-050) — both
        touch .py files, so both await Roberto's explicit
        go-ahead (AGENTS rule 3).

D-121 | 2026-09-06 | The parked test items closed (Roberto's
        calls): T18 retired, M1 fixed, the test_board header
        nit fixed.
        | T18 (the np.uint8 3**n_squares overflow) retired by
        Roberto's ruling: 3 ** n_squares is never to be computed
        from the attribute — the canonical value is
        n_configurations (it is the max value of an Index, and
        Index is uint32 on purpose). The source audit he
        requested (all 3**-sites, tests excluded, 7 found): no
        unguarded site exists — the only two legitimate
        3**n_squares consumers already cast to int
        (n_configurations = 3 ** int(n_squares), the definition
        itself; the index-dict N = 3 ** n_squares, called with
        int(self.n_squares)); the remaining sites are
        per-element 3**arange power tables and the Python-int
        Burnside sums (n_invariant/n_unique configs). No
        substitution was needed: the code already does what the
        note prescribed. M1 fixed: the PatternSet __init__
        Raises docstring now says ValidationError (the
        @validate_call checks) instead of the stale TypeError —
        docstring-only; the tests already assert ValidationError
        (the behavior was always the documented-after-fix one).
        The test_board.py header sentence fixed to the
        test_feature.py wording ("How to run the board module
        unit tests."). Next steps slimmed to two bullets (the
        ideas feed + the R1 re-evaluation, last).
        test_pattern 65/0/3 + test_board 201/0/12 green after
        the change.

D-122 | 2026-09-06 | AGENTS.md "What this is" rewritten with
        Roberto's verbatim text — the assistant's identity and
        mission: "You are Nia, an assistant for software
        development and mathematical theory definition,
        dedicated to creating a portfolio of software tools in
        the domain of Reversi, the board game also known as
        Othello."
        | The old paragraph described the completed port phase
        ("staging workspace ... copied in one at a time") —
        stale in the present; the same identity shift as the
        D-119 Project rewrite (the workspace says who it is
        now, not where it came from — the 18-year-old-repo
        history stays in the board.py header, the test headers'
        repo URL and the decision log). The "do not propose
        repo-wide reorganization" guard is NOT retired: Roberto
        promoted it to the AGENTS.md Standing rules as rule 8
        (it outlived the port campaign that wrote it; the
        principle stands — the full-repo restructure is planned
        work (I-001, notes/ideas.md), a user decision, never an
        agent initiative).

D-123 | 2026-09-06 | AGENTS.md slimmed: the title is now
        "reversi workspace" (the "staging" era is over) and the
        Naming convention paragraph reduced to guards + the bit
        anchor + the canon pointer.
        | The paragraph mixed behavioral guards (the not-chess
        vocabulary, A1 = bit 0 / H8 = bit 63, the fixed D8
        order, the diagram orientation) with reference material
        (the square-name mechanics, the row_1/column_a examples,
        the "Set 2026-08-26" date) — the latter duplicates
        notes/naming.md (the canon) and the Conventions bullet of
        notes/overview.md (the working reference). The
        auto-injected constitution now carries only what shapes
        every session (the guards); the reference material stays
        where it is read when board work happens. The 3-layer
        pattern (guards in AGENTS.md / working facts in
        overview.md / the full canon in notes/naming.md) is the
        same as the cache-flow and mirror-format lines in
        rules.md. overview.md and naming.md untouched.

D-124 | 2026-09-06 | The unittest runner choice made explicit:
        the Environment bullet of overview.md states it is by
        design; the Test discipline of rules.md carries the
        guard.
        | A clarification / leave-as-is decision (AGENTS rule 6:
        these go to the log too). The original repo is written
        in unittest and the 673 tests + goldens were built that
        way; a migration to pytest (the de-facto Python-world
        standard, and the prior the agent kept re-deriving
        against — it already cost a real "No module named
        pytest") would be a full-suite rewrite for zero
        functional gain here. The guard form ("do not propose a
        migration") follows the rule 8 / A2xxx pattern: state
        alone (the command in the bullet) does not block a
        future session's "well, let's use pytest" suggestion —
        legislation does.

D-125 | 2026-09-06 | Removed logistello-papers/ from the
        workspace ahead of the planned GitHub publication
        (Roberto): 16 copyrighted papers (1994–2002, incl. one
        IEEE) + the collection index, copied out of the workspace
        to /home/rcrr/base/prj/logistello-papers.
        | Live pointers removed in the same commit: the AGENTS.md
        rule 3 read-only clause + the Layout line; the rules.md
        Layout & tree bullet; the notes/overview.md Index line.
        I-008 (extend the collection beyond 2002) removed from
        the backlog (the collection is now out of workspace
        scope; Roberto's call: drop, not move). Historical
        journal/decision mentions of the folder kept (append-only
        records; no copyrighted content). The git-history scrub
        (the PDFs sit in all 292 pre-scrub commits — added at the
        bootstrap, never modified) follows as D-126.

D-126 | 2026-09-06 | Scrubbed the git history of
        logistello-papers/ (D-125): the 16 PDFs sat in all 292
        pre-scrub commits (added at the bootstrap, never
        modified).
        | git filter-branch (index-filter 'git rm -r --cached
        --ignore-unmatch logistello-papers') rewrote master;
        refs/original + reflog cleaned; aggressive GC.
        Verification battery: no commit on any ref touches the
        path; zero .pdf blobs in any object; content sweep
        (distinctive phrases extracted from three PDFs:
        '181,440', 'semi-automatic construction of evaluation
        functions', 'structured evaluation function
        representation', 'eight puzzle') — 0 hits across all
        objects; git fsck --full clean; tip tree identical to
        the pre-scrub tip; .git 27.2 MiB → ~2 MiB; gated suite
        673/0/87.
        The dangling present-tense folder line in the bootstrap
        commit message was also removed (surgical msg-filter);
        the four remaining message mentions (the D-125 removal
        commit + three historical records) kept — the same
        "keep historical records" ruling as the journals
        (Roberto).

D-127 | 2026-09-07 | After the VM restart (4 -> 8 vCPU) two
        DB-gated float goldens failed at the last-ULP level
        (analytics test_analytics_report_goldens,
        full_chain test_full_worker_chain). Investigation
        (Roberto): the failing quantities are float64
        reductions over up to ~2M terms (np.dot,
        rlm_analytics.py L459/L509) running through the
        multi-threaded OpenBLAS ddot (scipy-bundled 0.3.34,
        DYNAMIC_ARCH NO_AFFINITY): the last ULPs depend on
        the thread count x the CPU kernel selected at
        runtime.
        | Evidence: three different values for the same
        rlm_04 metrics (1 thread / 8 threads / the old VM);
        per-run determinism intact (3/3 identical); the drift
        across the rlm_02/04/03 chains is 2-301 ULP (rel
        2e-16...4e-14); ALL bit-exact contracts hold in the
        new environment (model file sha3, w_dense sha3, EF
        pins, report hashes, f32 train_loss/g_norm, iters,
        samples); every golden literal round-trips (full
        precision reprs - no re-recording needed).
        | Fix (Roberto's GO, as proposed): the tolerance is
        the portable contract - pinning OMP_NUM_THREADS
        would be a weaker version of the same problem
        (single-threaded DYNAMIC_ARCH is still CPU-
        dependent): new twolm/test/closecheck.py
        assert_close (math.isclose, rel 1e-9 / abs 1e-12:
        the measured drift is <= 4e-14, a genuine
        regression shows up at >= 1e-6 - ~5 orders of
        magnitude of detection margin); 56 float
        comparisons converted in test_lm_worker_analytics.
        py (16), test_lm_worker_full_chain.py (34, A2030 +
        A2050), test_lm_worker_validate.py (6). Bit-exact
        assertEqual stays for: the int/uint counts, the
        f32-quantized values (train_loss = float(opt f32),
        g_norm, the tps read-back truncations, the vld file
        read-back, the EF pins), the sha3 hashes, and the
        second-instance determinism tests (the in-run
        bit-identity contract); the hand-derived 2-position
        constants and the deterministic 3.64 mean stay
        exact.
        | Promoted to rules.md (Test discipline).
        Verification: the four worker suites 23/23 on the
        live DB (A2030 + read guards + analytics + validate
        + vld_positions; the A2050 LONG re-run
        separately); the 3 mirror docs updated.

D-128 | 2026-09-07 | Fixed the alignment of the
        state-machine live log line (Roberto): the
        [REL:VERB] field was variable-width because the
        enum names are variable-length (Relevance 4-5:
        INFO/WARN vs TRACE/DEBUG/ERROR; Verbosity 3-8: LOW
        vs VERY_LOW/MODERATE/STANDARD), so the message
        column never aligned.
        | The field is now fixed-width 16 with right-
        justified, space-filled names:
        [{relevance.name:>5}:{verbosity.name:>8}] — the 5/8
        widths exactly cover all existing names (e.g.
        [INFO:HIGH] -> [ INFO:    HIGH],
        [DEBUG:HIGH] -> [DEBUG:    HIGH]). One print line
        (state_machine.py L256-260, the M6/D-070 comment
        extended with the D-128 reference). The EVENT LOG /
        history tables are untouched (a different, left-
        justified design).
        | Impact map (closed): 11 prefix pins in
        test_state_machine.py (the 3 golden tests: live
        line, show_event_log, show_history_of_moves)
        updated; the mirror doc's format description
        updated; no other test (message-only assertIn),
        probe or DB-gated golden depends on the prefix.
        | Verification: test_state_machine 49/49; gated
        suite 673/0/87 (unchanged).

D-129 | 2026-09-07 | Pre-commit verification rule
        (Roberto): the D-127 and D-128 commits were
        verified with the GATED suite (SKIP_REGAB_DB=1,
        87 skipped) + targeted live runs, not the 100%
        live suite; Roberto ruled that every commit must
        be preceded by the full test run.
        | New bullet in rules.md (Test discipline):
        before every commit, run the full test suite with
        no gates — the live regab DB is the normal
        environment; a gated run is not a substitute.
        Retroactive: after the D-128 commit Roberto ran
        the full live suite himself — all green; the
        agent's own full live run (journal step 45)
        re-confirms the 2026-09-06 baseline on the
        8-vCPU VM: 673 tests / 0 failures / 18 skipped
        (~3 min).

D-130 | 2026-09-07 | Suite tiers LONG/VLONG + canonical
        ordered runner (Roberto-approved proposal;
        study first: per-test durations measured over the
        whole suite — 40.6 s of 44.5 s are the 14
        DB-dependent files).
        | Rename: the only LONG gate (A2050, ~10 min) is
        now VLONG; the NEW LONG tier = every DB-gated
        test (the criterion is the external-DB dependency,
        not the per-test time — the "only the six heavy
        files" alternative would leave ~9.4 s, no margin).
        VLONG=1 implies LONG. SKIP_REGAB_DB=1 stays
        orthogonal (a no-DB environment skips all DB
        tests whatever the tier).
        | New: twolm/test/tags.py db_long_gate(testcase) —
        the shared setUp gate (the T2 shape): SKIP_REGAB_DB
        or not (LONG or VLONG); the 17 gate sites in 14
        files (the 13 worker suites + test_regab) are now
        db_long_gate(self); the headers state the tiered
        state (D-080 T2).
        | New: run_utests.sh (workspace root) — the
        canonical runner: venv activation + the 34 test
        modules in canonical order (tools, board/pattern
        concepts, infrastructure, DB access, then the
        pipeline in machine order 1-14 — each data module
        immediately before its worker, the 15-level chain
        last; Roberto's merge of the rlm/lm groups); a
        new test module is inserted at its logical
        position, never appended.
        | Measured tiers (8-vCPU VM, 2026-09-07): default
        5.3 s (586 run, 87 skipped) — under the 10 s
        target with margin; LONG=1 45.5 s (655 run, 18
        skipped); VLONG=1 ~15-16 min on the loaded 8-vCPU VM
        (A2050: the full_chain module measured 794.9 s today,
        the D-104 standalone 331.7 s is the unloaded floor).
        | Impact (closed): rules.md (the tier bullet + the
        db_long_gate bullet; the D-129 bullet: full =
        VLONG=1 ./run_utests.sh); overview.md suite-status
        bullet; the 14 mirror docs (the gate-mechanism
        naming); the A2050 skipUnless is VLONG.

D-131 | 2026-09-08 | Pre-commit verification scope =
        LONG=1, not VLONG (Roberto): the D-130 wording
        ("full = VLONG=1 ./run_utests.sh") is corrected —
        the standard pre-commit suite is LONG=1
        ./run_utests.sh (the fast tier + the DB-gated
        pipeline, ~50 s); VLONG=1 (the ~10-min A2050
        chain) is used ONLY when we understand it is
        useful (e.g. a change touching the full_chain /
        A2050 code).
        | rules.md D-129 bullet amended (now D-129,
        D-131). Note: the actual D-130 pre-commit
        verification ran the VLONG tier — a superset, so
        that commit is covered.

D-132 | 2026-09-08 | measure_suite.py graduates from
        scratch/ to probes/ (Roberto's GO): the
        per-test-timing tool of the D-130 study becomes
        tracked verification apparatus.
        | It is a MEASUREMENT tool, not a verification
        probe: no a/b/c checks, no assertions — it records
        every test's duration in ms (the builtin
        unittest --durations hides sub-1 ms and reports
        seconds) and writes scratch/test_durations.txt.
        probe_rules.md §2 classifies it accordingly (outside
        the campaign sweep — it is not a check); overview.md
        probe count 20 → 21. Verified from the workspace
        root: 673 tests / 4.0 s wall / 87 skipped (the
        default tier).

D-133 | 2026-09-08 | I-001 executes: the reorganization
        campaign — twolm → reversi with the core/tools/lm
        split (Roberto's approved mapping, his written
        request; the AGENTS rule-8 guard lifts on his
        explicit decision).
        | Layout: the core game modules at the package top
        level (board, pattern, mobility, feature, base_model,
        regab); the shared infrastructure in reversi/tools/
        (binio, cache_manager, opt_lbfgs, state_machine); the
        RLM pipeline in reversi/lm/ (the 15 wrk_* workers,
        their hlp_* data modules, hlp_config_schemas,
        model_weights, client, logistic_model). The layering
        is a verified DAG: lm → core, core → tools (base_model
        → state_machine), tools imports nothing from the
        package.
        | Method scope ruling: only the identifiers embedding
        the old module name are renamed (lm_worker_* →
        wrk_*, rlm_*_* → hlp_*_*); the domain classes
        (RLMContext, LogisticModel, BaseModel,
        ReversiLogisticModel*) and the unprefixed public fns
        (sigmoid, load_from_db, ...) stay. rlm_client →
        client (Roberto: "tua proposta perfetta"). RLMContext
        → LMContext: deferred — reviewed in the final
        inventory (Roberto).
        | Mechanics: 2 commits per module (A: the file + test
        + doc moves with every repo reference updated, suite
        green; B: the method renames, suite green); the test
        files follow the new module names (test_wrk_*,
        test_hlp_*); the probe files rename only when their
        name embeds the old module name (verify_lm_worker_* →
        verify_wrk_*, verify_rlm_indexes → verify_hlp_indexes);
        the mirror-doc State line keeps its content-snapshot
        marker across a pure move (the header path line
        updates, the hash stays the last content-changing
        commit); the history notes (decisions_000.md, the log
        volumes, notes/analyses/) stay untouched. pyproject
        name twolm → reversi; packages.find auto-discovers the
        subpackages.
        | Phases: 0 the skeleton (this entry) → 1 the 36
        modules bottom-up (tools → core → lm in machine
        order) → 2 the twolm/ removal + reinstall + the
        residual sweep → 3 the closing notes wave + the full
        sweep (probe_rules §5.2).
D-134 | 2026-09-08 | I-001 / D-133 campaign closed: the
        twolm → reversi reorganization complete.
        | Execution: the 36 modules moved bottom-up (tools →
        core → lm in machine order), 2 commits each (A: the
        file + test + doc moves with every repo reference
        updated, suite green; B: the method renames —
        lm_worker_* → wrk_*, rlm_*_* → hlp_*_* — suite
        green); name-unchanged modules: phase B a verified
        no-op. 4 probe files renamed (the only names
        embedding a module name); the level probes kept
        their names, their hardcoded source/test paths and
        cross-module pins re-pointed as each module moved;
        the hub probe re-pinned (the worker-import hygiene
        literals → the wrk_ form) at the logistic_model
        move. The test helpers (paths/tags/closecheck) + the
        data fixtures + test_paths moved to reversi.test;
        the frozen analyses-file refs, the historical
        probe-header lineage and the D-pointer comments
        keep their old names (they point at frozen records).
        | Phase 2: the emptied twolm/ (src + docs) removed;
        pip install -e . under the `reversi` name; the
        global residual sweep — `twolm` survives only in the
        history notes (decisions_000, the log volumes,
        analyses/), the D-133 entry itself, the session-31
        journal, and the frozen probe headers.
        | Verification regime (the local DB down — pre-
        existing, flagged to Roberto): SKIP_REGAB_DB=1
        ./run_utests.sh per commit, 673/0/87 GREEN through-
        out; test_regab verified live against the remote DB
        (37/0/0); the probe sweep (probe_rules §5.2): 7 fully
        green, 13 environmental at the DB stage (all
        file/path stages pass).
        | Open items: RLMContext → LMContext — the inventory
        (Roberto's call, per D-133): RLMContext 106 sites in
        src (192 incl. probes + docs), RLMBaseConfig 14, the
        bare RLM token 3; the rename happens only on his
        go-ahead. Pre-existing gaps flagged: the missing
        test_usage_binio.md mirror doc (the overview row
        references it); the local PostgreSQL cluster absent
        from the machine (35 pipeline DB tests + the 13
        DB-gated probes wait for it).
        | Notes wave: rules.md (layout + the mirror rule),
        AGENTS.md (Layout bullet), probe_rules.md, naming.md,
        docs_rules.md (examples), overview.md (Environment /
        Packaging / Where-we-are / Next steps), ideas.md
        (I-001 → done), the touched mirror docs — the
        history notes stay untouched.
D-135 | 2026-09-08 | The local PostgreSQL cluster is
        restored (Roberto re-provisioned it) — the full live
        verification completes.
        | Full suite: LONG=1 ./run_utests.sh → 673/0/18 GREEN
        (the DB-gated tests now run; only 18 skipped — the
        non-DB skips).
        | The DB-gated probe sweep (the 13 probes the campaign
        ran against SKIP_REGAB_DB) surfaced the campaign's
        last cleanup: 9 probe files pinned the PRE-D-130
        test-file state — the D-130 tier note adds a header
        line (line counts +1, line anchors shift) and D-130
        replaced the literal os.getenv / skipTest gate with
        the db_long_gate(self) idiom (reversi.test.tags) —
        plus verify_analytics / verify_design_matrix pinned
        the rlm_indexes field name on the ctx mocks / the
        recomputation (D-133 renamed it to hlp_indexes).
        Re-pinned: verify_gradient, verify_optimize,
        verify_wmaps, verify_hlp_indexes, verify_wrk_features,
        verify_zed, verify_design_matrix, verify_analytics.
        The frozen labels and the rlm_0X data names stay.
        | Probe sweep (probe_rules §5.2): 21/21 green (the 20
        verify probes + measure_suite), all DB tiers live.
D-136 | 2026-09-08 | RLM → LM: the final inventory ruling
        (the D-133 deferral — Roberto: "Rinomina").
        | Scope: RLMContext → LMContext (106 sites in src, 192
        incl. probes + docs), RLMBaseConfig → LMBaseConfig
        (14), the bare RLM abbreviation in comments / prose
        (3 in src; the lm docs — "the RLM pipeline" → "the LM
        pipeline", "RLM facade" → "LM facade", "RLM level" →
        "LM level"). Applied to src (code + docstrings), the
        test files, the mirror docs, and ALL probes — the
        live pins (the source-text strings, the
        TYPE_CHECKING import pins, the LMContext(...)
        instantiations) and the hub header live refs renamed
        with the class (the live identifier; the frozen
        module-name lineage lm_worker_* in the same header
        stays). The history notes (decisions, the journal,
        analyses/) keep the old names.
        | Out of scope (flagged, D-137): the hlp test
        scaffolding classes TestRLMWmaps* (4) +
        TestRLMZedCompute — named after the original 2008
        function names; test_hlp_indexes was renamed to
        TestHlpIndexes* in phase B, so the siblings are
        inconsistent.
        | Verification: the gated suite 673/0/87 GREEN + the
        full probe sweep 21/21 (live DB).
D-137 | 2026-09-08 | The ReversiLogisticModel* data
        containers renamed to the LM family (Roberto:
        "sistemiamo anche quelle" — analysis first).
        | Analysis: the family is SIX classes (the "tre
        classi" of the request — actually 6), the per-level
        data containers of the 15-stage pipeline, one per
        data level, produced by the hlp_* data module and
        consumed by the paired wrk_* worker: LMIndexes (the
        2D index matrix + the feature-set hash;
        hlp_indexes → wrk_indexes; 31 uses), LMConfig (the
        pydantic entry config, LMBaseConfig; wrk_config /
        wrk_features / wrk_positions; 19), LMWMaps (the
        weight-map arrays; 18), LMDesignMatrix (the design
        matrix X + wmaps checksum; 17), LMDenseWeights (the
        dense w vector + checksum; 16), LMZed (the z vector
        + the y2z/z2y closures; 11). All six came from the
        original 2008 repo as-is: the "ReversiLogisticModel"
        prefix is the domain name in long form (the RLM
        abbreviation) — descriptive, NOT a module prefix,
        which is why phase B left it (the D-133 narrow
        scope). After D-133/D-136 the domain prefix is "LM"
        (LMContext / LMBaseConfig), so the long form was
        redundant inside reversi/lm/.
        | Targets: ReversiLogisticModelX → LMX (parallel to
        the LMContext blackboard that holds the instances);
        the 2 test scaffolding classes follow the class
        rename: TestReversiLogisticModelIndexes →
        TestLMIndexes, TestReversiLogisticModelZed →
        TestLMZed (the D-133 scaffolding ruling). The
        spelled-out domain prose in docstrings ("Reversi
        Logistic Model", with spaces) stays.
        | Self-contained: the indexes .bin header
        description ("LMIndexes binary data file") is
        generated and verified within the same run
        (TemporaryDirectory, D-085) — no committed .bin
        artifact carries the old string.
        | Out of scope (flagged, Roberto's call if he wants
        it): TestRLMWmaps* (4) + TestRLMZedCompute — 2008-era
        function-named scaffolding; test_hlp_indexes was
        already TestHlpIndexes* in phase B, so the siblings
        are inconsistent.
        | Verification: the gated suite 673/0/87 GREEN + the
        full probe sweep 21/21 (live DB).
D-138 | 2026-09-08 | The remaining hlp test scaffolding
        classes renamed to TestHlp* (Roberto: fix the
        inconsistency flagged in D-136/D-137).
        | The flag turned out bigger than wmaps/zed: 18
        classes across the SIX hlp test files still carried
        the 2008-era TestRLM* names (TestRLMWmaps* 4,
        TestRLMZedCompute, TestRLMDesignMatrix* 4,
        TestRLMGenerate* 4, TestRLMGradientCompute,
        TestRLMOptimize* 4), while test_hlp_indexes.py had
        already become TestHlpIndexes* in phase B. Rule:
        TestRLM<X> → TestHlp<X> (the function-named form,
        parallel to TestHlpIndexesCompute). The live probe
        pins (verify_wmaps C15, verify_zed G3,
        verify_optimize, verify_generate) + the 6 test
        mirror docs re-pinned.
        | Verification: the gated suite 673/0/87 GREEN + the
        full probe sweep 21/21 (live DB).
