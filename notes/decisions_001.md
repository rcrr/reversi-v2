# Decisions log — volume 001 (closed)

Format: D-NNN | date | decision | rationale

Volume 001: D-117…D-158 (2026-09-06 → 2026-09-11); closed at the D-118 rotation (2111 lines > the 2000 cap); the open
log continues in notes/decisions.md.

D-117 | 2026-09-06 | Re-structured the entry-point file: renamed NOTES.md → notes/overview.md and split the per-file
         state into two alphabetical tables (Source files, Test files) with a strict one-line State grammar (Roberto:
         the old Inventory was unbalanced — 2-line entries next to page-long ones — and the file list appeared three
         times: Inventory, Where we are, Index; the situation sections should come before the file list).
        | The State cell of each row now carries a status word + the open/parked items + the D-pointer range (one line,
          always) — the campaign history stays in the decision log (the D-115 split was the premise; this removes the
          last duplication). The per-file Where-we-are bullets merged into the tables; Where we are keeps only the
          non-file state (the plan, the collaboration memory). New section order: Project · Conventions in the code ·
          Environment · Where we are · Next steps · Source files · Test files · Index. The probes stay out of the
          tables: one Environment bullet (20 tracked, 20/20 green in both modes). The Index drops the 38 docs/ mirror
          bullets (their paths are the Doc column of the tables) and lists the notes/ files only. The Suite column was
          re-verified module-by-module against a live-DB run (2026-09-06): 673/0/18 (the gated baseline: 87 skipped);
          several suites had grown since the last sweep and the old Inventory carried stale numbers (test_cache_manager
          21→22, test_feature 19→20, test_lm_worker_validate 3→5, test_lm_worker_vld_positions 3→9, test_logistic_model
          15→17). The old Environment "Suite status (2026-09-02)" bullet (still saying 193/64/20) replaced by the
          verified line. AGENTS.md rules 1–2 + Layout updated; the rules.md grammar retires the old "terse history"
          Status form (PROMOTED same commit).

D-118 | 2026-09-06 | Rotated the decision log into volumes: the 4189-line decisions.md (D-001…D-116) closed as
         decisions_000.md; a new open decisions.md (this file) starts at D-117.
        | The log had crossed the 2000-line journal cap (Roberto proposed the same rotation as the journals). Protocol:
          the OPEN volume keeps the name decisions.md, so the AGENTS.md / rules.md / overview pointers never change; a
          closed volume becomes decisions_NNN.md; the D-numbers stay global and immutable, so every cross-reference
          survives the rotation. The protocol was PROMOTED into rules.md (the Roles section) in the same commit. The
          next rotation happens at a session boundary, like the journal volumes.

D-119 | 2026-09-06 | The Project section of notes/overview.md was rewritten with Roberto's new identity statement,
         replacing the "file-by-file modernization" text (the D-115-era wording).
        | The port campaign is complete (the pipeline is 15/15, D-104/D-113): the workspace's identity has moved from "a
          modernization in progress" to what it actually does now — the research and development of evaluation functions
          for Reversi positions, machine-learning methods over the solved positions generated from random gameplay paths
          (the 15-level pipeline). Nothing the old text carried is lost: the staging constraint ("only files under
          active work live here") lives in AGENTS.md (auto-injected, stronger form), and the I-001 full-repo-restructure
          pointer lives in notes/ideas.md (referenced from the Next steps). The Project section stays a pure identity
          statement; the current phase stays in Where we are.

D-120 | 2026-09-06 | Next-steps trim (Roberto's item-by-item review).
        | (1) The endgame-solver integration item removed (Roberto's call; the A2xxx production context stays in the
          rlm_client.md intro — its Open issues were already None, so nothing went stale). (2) The "Deferred" label of
          lm_worker_config R1 retired (Roberto: every item in Next steps is "next" by definition) — and the item is now
          LIVE: its D-078 revisit trigger (the pipeline completion) is met (15/15), so it becomes the last bullet = the
          next concrete action; the mirror doc label updated "deferred" → "revisit due" (docs only). (3) The
          journal-rotation reminder bullet removed: rotation is the standing log_rules.md legislation (log_001 → log_002
          at the next session boundary), not a next step. (4) The stale "Next concrete action" bullet (pointing at
          the D-115 restructure) removed. Kept, with the explanation given in session: the parked test_pattern T18
          (noted-only — the production code already casts to int; the note is for external expressions; no code action)
          + M1 (the stale PatternSet Raises docstring: it says TypeError, but the @validate_call checks raise
          ValidationError — a one-line docstring fix) and the reported-only test_board.py header grammar nit (the broken
          "How to use the unit tests board module." sentence; the 'environmeant' typo itself was fixed in D-050) — both
          touch .py files, so both await Roberto's explicit go-ahead (AGENTS rule 3).

D-121 | 2026-09-06 | The parked test items closed (Roberto's calls): T18 retired, M1 fixed, the test_board header nit
         fixed.
        | T18 (the np.uint8 3**n_squares overflow) retired by Roberto's ruling: 3 ** n_squares is never to be computed
          from the attribute — the canonical value is n_configurations (it is the max value of an Index, and Index is
          uint32 on purpose). The source audit he requested (all 3**-sites, tests excluded, 7 found): no unguarded site
          exists — the only two legitimate 3**n_squares consumers already cast to int (n_configurations = 3 **
          int(n_squares), the definition itself; the index-dict N = 3 ** n_squares, called with int(self.n_squares));
          the remaining sites are per-element 3**arange power tables and the Python-int Burnside sums
          (n_invariant/n_unique configs). No substitution was needed: the code already does what the note prescribed. M1
          fixed: the PatternSet __init__ Raises docstring now says ValidationError (the @validate_call checks) instead
          of the stale TypeError — docstring-only; the tests already assert ValidationError (the behavior was always the
          documented-after-fix one). The test_board.py header sentence fixed to the test_feature.py wording ("How to run
          the board module unit tests."). Next steps slimmed to two bullets (the ideas feed + the R1 re-evaluation,
          last). test_pattern 65/0/3 + test_board 201/0/12 green after the change.

D-122 | 2026-09-06 | AGENTS.md "What this is" rewritten with Roberto's verbatim text — the assistant's identity and
         mission: "You are Nia, an assistant for software development and mathematical theory definition, dedicated to
         creating a portfolio of software tools in the domain of Reversi, the board game also known as Othello."
        | The old paragraph described the completed port phase ("staging workspace ... copied in one at a time") — stale
          in the present; the same identity shift as the D-119 Project rewrite (the workspace says who it is now, not
          where it came from — the 18-year-old-repo history stays in the board.py header, the test headers' repo URL and
          the decision log). The "do not propose repo-wide reorganization" guard is NOT retired: Roberto promoted it to
          the AGENTS.md Standing rules as rule 8 (it outlived the port campaign that wrote it; the principle stands —
          the full-repo restructure is planned work (I-001, notes/ideas.md), a user decision, never an agent
          initiative).

D-123 | 2026-09-06 | AGENTS.md slimmed: the title is now "reversi workspace" (the "staging" era is over) and the Naming
         convention paragraph reduced to guards + the bit anchor + the canon pointer.
        | The paragraph mixed behavioral guards (the not-chess vocabulary, A1 = bit 0 / H8 = bit 63, the fixed D8 order,
          the diagram orientation) with reference material (the square-name mechanics, the row_1/column_a examples, the
          "Set 2026-08-26" date) — the latter duplicates notes/naming.md (the canon) and the Conventions bullet of
          notes/overview.md (the working reference). The auto-injected constitution now carries only what shapes every
          session (the guards); the reference material stays where it is read when board work happens. The 3-layer
          pattern (guards in AGENTS.md / working facts in overview.md / the full canon in notes/naming.md) is the same
          as the cache-flow and mirror-format lines in rules.md. overview.md and naming.md untouched.

D-124 | 2026-09-06 | The unittest runner choice made explicit: the Environment bullet of overview.md states it is by
         design; the Test discipline of rules.md carries the guard.
        | A clarification / leave-as-is decision (AGENTS rule 6: these go to the log too). The original repo is written
          in unittest and the 673 tests + goldens were built that way; a migration to pytest (the de-facto Python-world
          standard, and the prior the agent kept re-deriving against — it already cost a real "No module named pytest")
          would be a full-suite rewrite for zero functional gain here. The guard form ("do not propose a migration")
          follows the rule 8 / A2xxx pattern: state alone (the command in the bullet) does not block a future session's
          "well, let's use pytest" suggestion — legislation does.

D-125 | 2026-09-06 | Removed logistello-papers/ from the workspace ahead of the planned GitHub publication (Roberto): 16
         copyrighted papers (1994–2002, incl. one IEEE) + the collection index, copied out of the workspace to
         /home/rcrr/base/prj/logistello-papers.
        | Live pointers removed in the same commit: the AGENTS.md rule 3 read-only clause + the Layout line; the
          rules.md Layout & tree bullet; the notes/overview.md Index line. I-008 (extend the collection beyond 2002)
          removed from the backlog (the collection is now out of workspace scope; Roberto's call: drop, not move).
          Historical journal/decision mentions of the folder kept (append-only records; no copyrighted content). The
          git-history scrub (the PDFs sit in all 292 pre-scrub commits — added at the bootstrap, never modified) follows
          as D-126.

D-126 | 2026-09-06 | Scrubbed the git history of logistello-papers/ (D-125): the 16 PDFs sat in all 292 pre-scrub
         commits (added at the bootstrap, never modified).
        | git filter-branch (index-filter 'git rm -r --cached --ignore-unmatch logistello-papers') rewrote master;
          refs/original + reflog cleaned; aggressive GC. Verification battery: no commit on any ref touches the path;
          zero .pdf blobs in any object; content sweep (distinctive phrases extracted from three PDFs: '181,440',
          'semi-automatic construction of evaluation functions', 'structured evaluation function representation', 'eight
          puzzle') — 0 hits across all objects; git fsck --full clean; tip tree identical to the pre-scrub tip;
          .git 27.2 MiB → ~2 MiB; gated suite 673/0/87. The dangling present-tense folder line in the bootstrap commit
          message was also removed (surgical msg-filter); the four remaining message mentions (the D-125 removal commit
          + three historical records) kept — the same "keep historical records" ruling as the journals (Roberto).

D-127 | 2026-09-07 | After the VM restart (4 -> 8 vCPU) two DB-gated float goldens failed at the last-ULP level
         (analytics test_analytics_report_goldens, full_chain test_full_worker_chain). Investigation (Roberto): the
         failing quantities are float64 reductions over up to ~2M terms (np.dot, rlm_analytics.py L459/L509) running
         through the multi-threaded OpenBLAS ddot (scipy-bundled 0.3.34, DYNAMIC_ARCH NO_AFFINITY): the last ULPs depend
         on the thread count x the CPU kernel selected at runtime.
        | Evidence: three different values for the same rlm_04 metrics (1 thread / 8 threads / the old VM); per-run
          determinism intact (3/3 identical); the drift across the rlm_02/04/03 chains is 2-301 ULP (rel 2e-16...4e-14);
          ALL bit-exact contracts hold in the new environment (model file sha3, w_dense sha3, EF pins, report hashes,
          f32 train_loss/g_norm, iters, samples); every golden literal round-trips (full precision reprs - no
          re-recording needed).
        | Fix (Roberto's GO, as proposed): the tolerance is the portable contract - pinning OMP_NUM_THREADS would be a
          weaker version of the same problem (single-threaded DYNAMIC_ARCH is still CPU-dependent): new
          twolm/test/closecheck.py assert_close (math.isclose, rel 1e-9 / abs 1e-12: the measured drift is <= 4e-14, a
          genuine regression shows up at >= 1e-6 - ~5 orders of magnitude of detection margin); 56 float comparisons
          converted in test_lm_worker_analytics. py (16), test_lm_worker_full_chain.py (34, A2030 + A2050),
          test_lm_worker_validate.py (6). Bit-exact assertEqual stays for: the int/uint counts, the f32-quantized values
          (train_loss = float(opt f32), g_norm, the tps read-back truncations, the vld file read-back, the EF pins), the
          sha3 hashes, and the second-instance determinism tests (the in-run bit-identity contract); the hand-derived
          2-position constants and the deterministic 3.64 mean stay exact.
        | Promoted to rules.md (Test discipline). Verification: the four worker suites 23/23 on the live DB (A2030 +
          read guards + analytics + validate + vld_positions; the A2050 LONG re-run separately); the 3 mirror docs
          updated.

D-128 | 2026-09-07 | Fixed the alignment of the state-machine live log line (Roberto): the [REL:VERB] field was
         variable-width because the enum names are variable-length (Relevance 4-5: INFO/WARN vs TRACE/DEBUG/ERROR;
         Verbosity 3-8: LOW vs VERY_LOW/MODERATE/STANDARD), so the message column never aligned.
        | The field is now fixed-width 16 with right-justified, space-filled names:
          [{relevance.name:>5}:{verbosity.name:>8}] — the 5/8 widths exactly cover all existing names (e.g.
          [INFO:HIGH] -> [ INFO: HIGH], [DEBUG:HIGH] -> [DEBUG: HIGH]). One print line (state_machine.py L256-260, the
          M6/D-070 comment extended with the D-128 reference). The EVENT LOG / history tables are untouched (a
          different, left-justified design).
        | Impact map (closed): 11 prefix pins in test_state_machine.py (the 3 golden tests: live line, show_event_log,
          show_history_of_moves) updated; the mirror doc's format description updated; no other test (message-only
          assertIn), probe or DB-gated golden depends on the prefix.
        | Verification: test_state_machine 49/49; gated suite 673/0/87 (unchanged).

D-129 | 2026-09-07 | Pre-commit verification rule (Roberto): the D-127 and D-128 commits were verified with the GATED
         suite (SKIP_REGAB_DB=1, 87 skipped) + targeted live runs, not the 100% live suite; Roberto ruled that every
         commit must be preceded by the full test run.
        | New bullet in rules.md (Test discipline): before every commit, run the full test suite with no gates — the
          live regab DB is the normal environment; a gated run is not a substitute. Retroactive: after the D-128 commit
          Roberto ran the full live suite himself — all green; the agent's own full live run (journal step 45)
          re-confirms the 2026-09-06 baseline on the 8-vCPU VM: 673 tests / 0 failures / 18 skipped (~3 min).

D-130 | 2026-09-07 | Suite tiers LONG/VLONG + canonical ordered runner (Roberto-approved proposal; study first: per-test
         durations measured over the whole suite — 40.6 s of 44.5 s are the 14 DB-dependent files).
        | Rename: the only LONG gate (A2050, ~10 min) is now VLONG; the NEW LONG tier = every DB-gated test (the
          criterion is the external-DB dependency, not the per-test time — the "only the six heavy files" alternative
          would leave ~9.4 s, no margin). VLONG=1 implies LONG. SKIP_REGAB_DB=1 stays orthogonal (a no-DB environment
          skips all DB tests whatever the tier).
        | New: twolm/test/tags.py db_long_gate(testcase) — the shared setUp gate (the T2 shape): SKIP_REGAB_DB or not
          (LONG or VLONG); the 17 gate sites in 14 files (the 13 worker suites + test_regab) are now db_long_gate(self);
          the headers state the tiered state (D-080 T2).
        | New: run_utests.sh (workspace root) — the canonical runner: venv activation + the 34 test modules in canonical
          order (tools, board/pattern concepts, infrastructure, DB access, then the pipeline in machine order 1-14 —
          each data module immediately before its worker, the 15-level chain last; Roberto's merge of the rlm/lm
          groups); a new test module is inserted at its logical position, never appended.
        | Measured tiers (8-vCPU VM, 2026-09-07): default 5.3 s (586 run, 87 skipped) — under the 10 s target with
          margin; LONG=1 45.5 s (655 run, 18 skipped); VLONG=1 ~15-16 min on the loaded 8-vCPU VM (A2050: the full_chain
          module measured 794.9 s today, the D-104 standalone 331.7 s is the unloaded floor).
        | Impact (closed): rules.md (the tier bullet + the db_long_gate bullet; the D-129 bullet: full = VLONG=1
          ./run_utests.sh); overview.md suite-status bullet; the 14 mirror docs (the gate-mechanism naming); the A2050
          skipUnless is VLONG.

D-131 | 2026-09-08 | Pre-commit verification scope = LONG=1, not VLONG (Roberto): the D-130 wording ("full = VLONG=1
         ./run_utests.sh") is corrected — the standard pre-commit suite is LONG=1 ./run_utests.sh (the fast tier + the
         DB-gated pipeline, ~50 s); VLONG=1 (the ~10-min A2050 chain) is used ONLY when we understand it is useful (e.g.
         a change touching the full_chain / A2050 code).
        | rules.md D-129 bullet amended (now D-129, D-131). Note: the actual D-130 pre-commit verification ran the VLONG
          tier — a superset, so that commit is covered.

D-132 | 2026-09-08 | measure_suite.py graduates from scratch/ to probes/ (Roberto's GO): the per-test-timing tool of
         the D-130 study becomes tracked verification apparatus.
        | It is a MEASUREMENT tool, not a verification probe: no a/b/c checks, no assertions — it records every test's
          duration in ms (the builtin unittest --durations hides sub-1 ms and reports seconds) and writes
          scratch/test_durations.txt. probe_rules.md §2 classifies it accordingly (outside the campaign sweep — it is
          not a check); overview.md probe count 20 → 21. Verified from the workspace root: 673 tests / 4.0 s wall / 87
          skipped (the default tier).

D-133 | 2026-09-08 | I-001 executes: the reorganization campaign — twolm → reversi with the core/tools/lm split
         (Roberto's approved mapping, his written request; the AGENTS rule-8 guard lifts on his explicit decision).
        | Layout: the core game modules at the package top level (board, pattern, mobility, feature, base_model, regab);
          the shared infrastructure in reversi/tools/ (binio, cache_manager, opt_lbfgs, state_machine); the RLM pipeline
          in reversi/lm/ (the 15 wrk_* workers, their hlp_* data modules, hlp_config_schemas, model_weights, client,
          logistic_model). The layering is a verified DAG: lm → core, core → tools (base_model → state_machine), tools
          imports nothing from the package.
        | Method scope ruling: only the identifiers embedding the old module name are renamed (lm_worker_* → wrk_*,
          rlm_*_* → hlp_*_*); the domain classes (RLMContext, LogisticModel, BaseModel, ReversiLogisticModel*) and the
          unprefixed public fns (sigmoid, load_from_db, ...) stay. rlm_client → client (Roberto: "tua proposta
          perfetta"). RLMContext → LMContext: deferred — reviewed in the final inventory (Roberto).
        | Mechanics: 2 commits per module (A: the file + test + doc moves with every repo reference updated, suite
          green; B: the method renames, suite green); the test files follow the new module names (test_wrk_*,
          test_hlp_*); the probe files rename only when their name embeds the old module name (verify_lm_worker_* →
          verify_wrk_*, verify_rlm_indexes → verify_hlp_indexes); the mirror-doc State line keeps its content-snapshot
          marker across a pure move (the header path line updates, the hash stays the last content-changing commit); the
          history notes (decisions_000.md, the log volumes, notes/analyses/) stay untouched. pyproject name twolm →
          reversi; packages.find auto-discovers the subpackages.
        | Phases: 0 the skeleton (this entry) → 1 the 36 modules bottom-up (tools → core → lm in machine order) → 2 the
          twolm/ removal + reinstall + the residual sweep → 3 the closing notes wave + the full sweep (probe_rules
          §5.2).
D-134 | 2026-09-08 | I-001 / D-133 campaign closed: the twolm → reversi reorganization complete.
        | Execution: the 36 modules moved bottom-up (tools → core → lm in machine order), 2 commits each (A: the file +
          test + doc moves with every repo reference updated, suite green; B: the method renames — lm_worker_* → wrk_*,
          rlm_*_* → hlp_*_* — suite green); name-unchanged modules: phase B a verified no-op. 4 probe files renamed (the
          only names embedding a module name); the level probes kept their names, their hardcoded source/test paths and
          cross-module pins re-pointed as each module moved; the hub probe re-pinned (the worker-import hygiene literals
          → the wrk_ form) at the logistic_model move. The test helpers (paths/tags/closecheck) + the data fixtures +
          test_paths moved to reversi.test; the frozen analyses-file refs, the historical probe-header lineage and the
          D-pointer comments keep their old names (they point at frozen records).
        | Phase 2: the emptied twolm/ (src + docs) removed; pip install -e . under the `reversi` name; the global
          residual sweep — `twolm` survives only in the history notes (decisions_000, the log volumes, analyses/),
          the D-133 entry itself, the session-31 journal, and the frozen probe headers.
        | Verification regime (the local DB down — pre-existing, flagged to Roberto): SKIP_REGAB_DB=1 ./run_utests.sh
          per commit, 673/0/87 GREEN through-out; test_regab verified live against the remote DB (37/0/0); the probe
          sweep (probe_rules §5.2): 7 fully green, 13 environmental at the DB stage (all file/path stages pass).
        | Open items: RLMContext → LMContext — the inventory (Roberto's call, per D-133): RLMContext 106 sites in src
          (192 incl. probes + docs), RLMBaseConfig 14, the bare RLM token 3; the rename happens only on his go-ahead.
          Pre-existing gaps flagged: the missing test_usage_binio.md mirror doc (the overview row references it); the
          local PostgreSQL cluster absent from the machine (35 pipeline DB tests + the 13 DB-gated probes wait for it).
        | Notes wave: rules.md (layout + the mirror rule), AGENTS.md (Layout bullet), probe_rules.md, naming.md,
          docs_rules.md (examples), overview.md (Environment / Packaging / Where-we-are / Next steps), ideas.md (I-001 →
          done), the touched mirror docs — the history notes stay untouched.
D-135 | 2026-09-08 | The local PostgreSQL cluster is restored (Roberto re-provisioned it) — the full live verification
         completes.
        | Full suite: LONG=1 ./run_utests.sh → 673/0/18 GREEN (the DB-gated tests now run; only 18 skipped — the non-DB
          skips).
        | The DB-gated probe sweep (the 13 probes the campaign ran against SKIP_REGAB_DB) surfaced the campaign's last
          cleanup: 9 probe files pinned the PRE-D-130 test-file state — the D-130 tier note adds a header line (line
          counts +1, line anchors shift) and D-130 replaced the literal os.getenv / skipTest gate with the
          db_long_gate(self) idiom (reversi.test.tags) — plus verify_analytics / verify_design_matrix pinned the
          rlm_indexes field name on the ctx mocks / the recomputation (D-133 renamed it to hlp_indexes). Re-pinned:
          verify_gradient, verify_optimize, verify_wmaps, verify_hlp_indexes, verify_wrk_features, verify_zed,
          verify_design_matrix, verify_analytics. The frozen labels and the rlm_0X data names stay.
        | Probe sweep (probe_rules §5.2): 21/21 green (the 20 verify probes + measure_suite), all DB tiers live.
D-136 | 2026-09-08 | RLM → LM: the final inventory ruling (the D-133 deferral — Roberto: "Rinomina").
        | Scope: RLMContext → LMContext (106 sites in src, 192 incl. probes + docs), RLMBaseConfig → LMBaseConfig (14),
          the bare RLM abbreviation in comments / prose (3 in src; the lm docs — "the RLM pipeline" → "the LM pipeline",
          "RLM facade" → "LM facade", "RLM level" → "LM level"). Applied to src (code + docstrings), the test files, the
          mirror docs, and ALL probes — the live pins (the source-text strings, the TYPE_CHECKING import pins, the
          LMContext(...) instantiations) and the hub header live refs renamed with the class (the live identifier; the
          frozen module-name lineage lm_worker_* in the same header stays). The history notes (decisions, the journal,
          analyses/) keep the old names.
        | Out of scope (flagged, D-137): the hlp test scaffolding classes TestRLMWmaps* (4) + TestRLMZedCompute — named
          after the function names in the original codebase; test_hlp_indexes was renamed to TestHlpIndexes* in phase B,
          so the siblings are inconsistent.
        | Verification: the gated suite 673/0/87 GREEN + the full probe sweep 21/21 (live DB).
D-137 | 2026-09-08 | The ReversiLogisticModel* data containers renamed to the LM family (Roberto: "sistemiamo anche
         quelle" — analysis first).
        | Analysis: the family is SIX classes (the "tre classi" of the request — actually 6), the per-level data
          containers of the 15-stage pipeline, one per data level, produced by the hlp_* data module and consumed by the
          paired wrk_* worker: LMIndexes (the 2D index matrix + the feature-set hash; hlp_indexes → wrk_indexes; 31
          uses), LMConfig (the pydantic entry config, LMBaseConfig; wrk_config / wrk_features / wrk_positions; 19),
          LMWMaps (the weight-map arrays; 18), LMDesignMatrix (the design matrix X + wmaps checksum; 17), LMDenseWeights
          (the dense w vector + checksum; 16), LMZed (the z vector + the y2z/z2y closures; 11). All six came from the
          original codebase as-is: the "ReversiLogisticModel" prefix is the domain name in long form (the RLM
          abbreviation) — descriptive, NOT a module prefix, which is why phase B left it (the D-133 narrow scope).
          After D-133/D-136 the domain prefix is "LM" (LMContext / LMBaseConfig), so the long form was redundant inside
          reversi/lm/.
        | Targets: ReversiLogisticModelX → LMX (parallel to the LMContext blackboard that holds the instances); the 2
          test scaffolding classes follow the class rename: TestReversiLogisticModelIndexes → TestLMIndexes,
          TestReversiLogisticModelZed → TestLMZed (the D-133 scaffolding ruling). The spelled-out domain prose in
          docstrings ("Reversi Logistic Model", with spaces) stays.
        | Self-contained: the indexes .bin header description ("LMIndexes binary data file") is generated and verified
          within the same run (TemporaryDirectory, D-085) — no committed .bin artifact carries the old string.
        | Out of scope (flagged, Roberto's call if he wants it): TestRLMWmaps* (4) + TestRLMZedCompute — legacy
          function-named scaffolding; test_hlp_indexes was already TestHlpIndexes* in phase B, so the siblings are
          inconsistent.
        | Verification: the gated suite 673/0/87 GREEN + the full probe sweep 21/21 (live DB).
D-138 | 2026-09-08 | The remaining hlp test scaffolding classes renamed to TestHlp* (Roberto: fix the inconsistency
         flagged in D-136/D-137).
        | The flag turned out bigger than wmaps/zed: 18 classes across the SIX hlp test files still carried the legacy
          TestRLM* names (TestRLMWmaps* 4, TestRLMZedCompute, TestRLMDesignMatrix* 4, TestRLMGenerate* 4,
          TestRLMGradientCompute, TestRLMOptimize* 4), while test_hlp_indexes.py had already become TestHlpIndexes* in
          phase B. Rule: TestRLM<X> → TestHlp<X> (the function-named form, parallel to TestHlpIndexesCompute). The live
          probe pins (verify_wmaps C15, verify_zed G3, verify_optimize, verify_generate) + the 6 test mirror docs
          re-pinned.
        | Verification: the gated suite 673/0/87 GREEN + the full probe sweep 21/21 (live DB).
D-139 | 2026-09-08 | LZ4 whole-file compression by default in EVERY cache file function (Roberto: "Focalizziamoci sulla
         CACHE ... comprimiamo tutti i file della cache con LZ4, come facciamo per il model_weight ... usiamola
         consistentemente"; then after the A2050 probe: "Si confermo tutto. Comprimiamo. Fare i distinguo crea solo
         complessita' ... usiamolo").
        | Scope: 10 functions across 6 modules gain a trailing `compressed: bool = True`:
          hlp_indexes_{store_to_file,load_from_file}, hlp_wmaps_{store_to_file,load_from_file},
          hlp_design_matrix_{store_to_file,load_from_file}, hlp_generate_{store_to_file,load_from_file}, hlp_optimize
          {save_optimization_checkpoint, load_optimization_checkpoint}, regab {regab_store_data_set_to_file,
          regab_load_data_set_from_file}. Zero worker changes: the full-chain read guards pass compressed=False
          explicitly (they pin the uncompressed model_weights path), the worker load_fns go through the plain functions
          / the house `checksum=False` lambda — symmetric via the defaults.
        | A2050 measured (rlm_03, 1,999,179 train / 199,932 vld; the probe kept the TMP dir, every file compressed with
          the stock lz4 1.9.4 CLI — the same one Roberto's C run used): INDEXES 383.8 → 281.0 MB (73.20%),
          DESIGN_MTR 383.8 → 312.1 MB (81.31%), checkpoint 58.3 MB (100.00%), POSITIONS 34.0 MB (100.00%), WMAPS 3.5 MB
          (28.17%), VLD_POSITIONS 3.4 MB (100.00%), GENERATE 669 KB (76.87%), weights 515 KB (99.22%), CONFIG JSON 3.9
          KB (33.13% — out of scope); total 868.1 → 690.8 MB (79.58%, ~177 MB saved).
        | Uniform default, NO per-file distinguo: the incompressible files pay +51 B of frame for the consistency
          (Roberto's ruling above).
        | Self-healing: an uncompressed legacy .dat fails the LZ4 frame guard at load → the cache_manager
          delete+recompute (step 3) and the wrk_optimize (RuntimeError, BinaryFormatError, OSError) catch (D-096 R2)
          both recover; the load functions verify the sidecar BEFORE opening the reader, so a sidecar mismatch still
          raises the RuntimeError first (D-096 R3).
        | Out of scope (confirmed with Roberto): the CONFIG JSON (the D-078 R1 ad-hoc flow) and the analytics text
          report — the only open cache oddity remains the CONFIG ad-hoc flow, deferred.
        | Drive-by (flagged during analysis, fixed in the same commit): the stale sidecar docstrings in the 6 modules —
          the sidecar IS written by the binio writer (the checksum service is on by default); in the pipeline flow
          cache_manager re-writes the same sidecar (idempotent). The old "NO sidecar (cache_manager writes it)" claim
          was wrong.
        | Tests: the manual-writer tests (wrong description / version) pass compressed=True (the D-139 variant: the
          header gate is still reached); the hlp_optimize + hlp_indexes mock pins get compressed=True;
          test_checksum_mismatch_raises now corrupts the sidecar (a content-byte flip trips the LZ4 guard first); new
          pins: test_store_compressed_by_default (the LZ4 magic bytes) in all 5 hlp suites +
          test_load_defaults_reject_uncompressed_file in the 3 data-object suites; the checkpoint golden hash re-derived
          on the compressed file.
        | Probe re-pin: verify_wmaps / verify_design_matrix / verify_hlp_indexes / verify_optimize (line counts, the
          docstring pins, the manual writers, the golden hash, the test counts) + verify_save A10 — a PRE-EXISTING stale
          pin, D-130-era: it counted the inline getenv idiom that db_long_gate replaced (the test file has zero getenv
          occurrences); re-pinned to the db_long_gate x2.
        | Verification: the gated suite 680/0/87 + the full suite LONG=1 680/0/18 (live DB) + the full probe sweep 21/21
          (live DB).
D-140 | 2026-09-08 | Vectorized position_flips + position_make_move with the same technique as position_legal_moves
         (D-111) (Roberto: "Vanno vettorizzate con la stessa tecnica di position_legal_moves ... Va testato
         approfonditamente ... Serve sviluppare anche un test PERF").
        | API (strict dual — Roberto's ruling 8a "come legal_moves" + 8b "posizione in input invariata"):
          position_flips(p: PositionField | PositionArray, move: Bitboard | BitboardArray) -> (Bitboard | BitboardArray,
          PositionField | PositionArray | None); position_make_move(p, move: Move | MoveArray) -> PositionField |
          PositionArray | None. Scalar + scalar -> the pre-vectorization scalar behaviour bit-for-bit (the PA swap, the
          out-of-range ValueError, the (0, None) on illegal); array + array -> the kernel with the standard 1-D guard +
          the same-shape ValueError; mixed -> TypeError.
        | Array semantics: flips[i] = 0 for a zero or multi-bit move; updated[i] = the INPUT POSITION UNCHANGED for an
          illegal move (no per-element None in the structured array); in make_move the PA (64) swaps the players per
          element INSIDE the kernel — the former "PASS as a special case" note is resolved (no filter needed); any value
          > 64 in the array raises ValueError before the kernel.
        | Kernels: _vectorized_flips / _vectorized_make_move @njit(parallel=True, cache=True), prange over the N-board
          batch, 3-array return (flips, out_movers, out_opponents) re-assembled with make_position (the fresh
          interleaved buffer, zero-copy view); the shared per-element primitive _kogge_stone_mm is now
          @njit(inline='always') (body unchanged) — the scalar path calls it as before. The 8-direction up/down slide
          idiom is ported 1:1 per element (the 4x2 LMS idiom was the alternative; rejected: it would require re-deriving
          the blocker gt test, same cost, higher risk).
        | De-risk (scratch, before touching board.py): numba 0.67 scalar-return idiom (the njit primitive returns a
          Python int at the Python boundary -> the scalar branch re-wraps with Bitboard()); the structured-array element
          assignment from a tuple does NOT compile in numba -> the 3-arrays return design (confirmed by the de-risk
          run).
        | Fuzz invariant pinned: an EMPTY square is legal exactly when it flips something (the flip kernel and the
          legal-moves kernel share the geometry); an occupied square is never legal and the flip kernel does not check
          the move square emptiness (the pre-vectorization scalar behaviour, the caller's responsibility) — the first
          draft of the invariant (flips != 0 iff legal) was wrong for mover-occupied squares.
        | Tests: 20 new (board 201 -> 221, 12 -> 14 skipped): the 42-line bulk dataset re-played in array form (a single
          call), the mixed legal/illegal/PA batch, the all-PA batch, deterministic fuzz parity vs the scalar (2000
          cases, fixed seeds, zero/multi-bit moves + PA), the guard patterns per function (2-D p, 2-D move, shape
          mismatch, mixed kind, out-of-range/dtype) + the empty-array edge + the 2 PERF tests (PERF=1, 1M boards, the
          house print pattern).
        | Verification: the board suite 221/0/14 + the gated suite 700/0/89 + the full suite LONG=1 700/0/20 (live DB).
D-141 | 2026-09-09 | Vectorized EF client: make_evaluation_function_array (Roberto: "come fatto per la funzione
         position_make_move(), dobbiamo sviluppare il client EF vettorizzato nel modulo reversi.lm.client. Alla funzione
         make_evaluation_function() va affiancata una versione vettorizzata ... che ritorni: Callable[[PositionArray],
         npt.NDArray[np.float32]] ... Aggiungere un test PERF"; rulings on the approved analysis: 1 strict array, 2 the
         name make_evaluation_function_array, 3 @validate_call "anche sulla funzione scalare", 4 the dedicated no-DB
         test module, 5 the A2030 batch pin).
        | Design (the approved analysis): the heavy part is ALREADY a batch API — compute_indexes(positions :
          PositionArray) -> (N, I) uint32 (the numba prange kernel over N) — so NO new numba kernel: the array EF is the
          true batch + the vectorized tail (the broadcast expanded_offsets + indexes, the w_dense gather, the per-row
          f32 sum, the element-wise expit, the element-wise z2y affine). The closure setup is factored in the shared
          _prepare_weights helper (offsets, z2y, expanded_offsets — no drift between the two closures).
        | Strict array (ruling 1): the returned callable accepts a 1-D PositionArray (or a (N, 2) uint64 array, coerced
          by the PositionArray validator) and returns a (N,) float32 array; a scalar Position or bare lists are rejected
          (the Pydantic ValidationError — verified: a list of tuples does NOT slip through the coercion). Gap found and
          closed in the analysis (T4): the PositionArray BeforeValidator admits a 2-D structured array (it only checks
          the non-Position dtype 2-D case — no ndim check) — the standard 1-D guard (D-111 M5) inside the closure keeps
          a clean ValueError out of the numba kernel.
        | @validate_call (ruling 3): BOTH factories are validated (arbitrary_types_allowed) — the O5 acceptance ("no
          @validate_call on make_evaluation_function", client.md) is superseded; the array ef closure is validated too
          (the PositionArray annotation does the coercion).
        | De-risk (scratch, before touching client.py): parity vs the scalar EF is BIT-EXACT per position
          (np.array_equal on a seeded batch — the per-row f32 sum is the same 1-D reduction as the scalar np.sum); the
          (N, 2) u64 coercion equal; the N=0 edge returns (0,) f32; the synthetic rlm_04-mirror weights reproduce the
          production iwmap pin [0, 1, 66, 6627].
        | Tests: the new no-DB module test_client.py (7 tests, default tier): the synthetic rlm_04-mirror ModelWeights
          (intercept + LMC + EDGE), the 1000-position bit-exact parity, the u64 coercion, the 2-D structured guard, the
          scalar/list rejections, the N=0 edge + the PERF test (PERF=1, 1M boards, the house print pattern: 5,640,701
          b/s measured — ~1100x the scalar 5,117 b/s). The A2030 full-chain test gains the batch pin (ruling 5): the
          vectorized EF bit-exact on the same 6 pinned training positions (one batch call over the full 199932-position
          set) + the vld[42] pin on the validation batch.
        | Collateral: run_utests.sh inserts test_client at its logical position (after test_wrk_analytics, before the
          end-to-end chain — D-130); verify_save A8 re-pinned to the 2-entry __all__; client.md mirror: the stale
          "indexes int32 -> int64" dtype note corrected (uint32 + uint32 -> uint32 at runtime).
        | Verification: the default tier 707/0/90 + the full suite LONG=1 707/0/21 (live DB, incl. the A2030 batch pin)
          + the verify_save probe green.
D-142 | 2026-09-09 | CONFIG loses its ad-hoc cache — the fingerprint + the SAVE config record (Roberto: "Ora affrontiamo
         il tema sospeso della cache del LEVEL CONFIG, come e' fatta non va bene, non serve a nulla. Va ripensata. O la
         eliminiamo, ed e' finita qui. Oppure teniamo uno storico versionato delle evoluzioni del JSON .... ognuno con
         il suo checksum ... ed il checksum lo aggiungiamo in tutti i file a valle. Offre una tracciabilita' completa
         ... ma forse e' eccessivo ... Studia bene la situazione, prepara una analisi, fammi delle proposte di come
         procedere." — the D-078 R1 / I-011 revisit, the trigger met: the pipeline is 15/15; rulings on the approved
         analysis: 1 A+C1, 2 dump normalizzato, 3 fingerprint in entrambi i report).
        | Analysis: the ad-hoc flow (_store_to_file) has four defects: d1 write-only (the file is never read by the
          pipeline — the config always comes from the JSON5 source; the only "validation" is the file self-validating
          against its own sidecar); d2 ad-hoc duplicative (re-invents the hashlib + the 8192-chunk verify + a bare-hex
          sidecar where binio/cache_manager guarantee it, D-072 — the D-078 deferment node); d3 unconditional (writes
          even with use_cache off, against the declared-cache semantics of D-071); d4 the record lives in the wrong
          place (the ephemeral base_dir — in tests it dies with the tmp dir — instead of next to the ONLY durable
          artifact: the model file). The key discovery: the downstream invalidation chain is ALREADY config-aware
          without the file — POSITIONS/VLD_POSITIONS embed the query params (bid/status/ec + the DB connection) in the
          payload vs the live config; INDEXES checks rds_checksum + feature_set.hash; WMAPS the hlp_indexes_checksum +
          frequency_cut_off; DESIGN_MTR the wmaps_obj_checksum; OPTIMIZE the design_matrix_checksum + zed_checksum +
          ridge_regularization (D-096 R1); GENERATE the w_checksum. Any config change that hits the data already
          invalidates the right caches.
        | Option B (the versioned history + the config checksum stamped in all 6 downstream files) is REJECTED: (1) it
          duplicates the VCS — the JSON is a text file under git, which already gives versioned evolution with blob
          checksums; a history in base_dir would be a second source of truth; (2) it is a cross-cutting format change (a
          binio sidecar re-format = a full binio-suite re-pin, or a new field on 6 data objects + 6 formats); (3) the
          benefit lands on EPHEMERAL artifacts (the cache files die with the tmp dir — the only thing that outlives the
          run is the model); (4) "fare i distinguo crea solo complessita'" (the D-139 spirit).
        | The chosen path A+C1: A — the CONFIG level becomes a pure load+validate step (Roberto's own 2026-08-30 ruling:
          "Lo step config non ha bisogno di una cache"); C1 — at SAVE, next to the model file, the provenance record:
          <output>.config.json (the NORMALIZED dump — ruling 2: the effective configuration of the run, the base_dir
          override included, pydantic defaults resolved — exactly what _store_to_file was computing) + its .SHA3-256
          sidecar via the binio API (the same checksum service as every file). The model stays v1 (C2 — the dump
          embedded in the model file + a v2 reader — is the parked follow-up, separable, its own decision). Ruling 3:
          the fingerprint goes in BOTH analytics reports — the "Config SHA3-256" line in the COMMON header block (the 17
          → 18 lines), so the console and the file report both carry it.
        | Code: wrk_config — _store_to_file removed (6 → 5 privates); _up computes ctx.config_checksum = sha3_256(
          cfg.model_dump_json(indent=4).encode() ).hexdigest() and logs it (the single source of truth for the record
          and the report); _down resets it to None. logistic_model — LMContext gains config_checksum (the 9th *_checksum
          field; 40 → 41 fields). wrk_save — _store_config_record: the normalized dump written to
          output_path.with_suffix(".config.json") + write_sha3_256_sidecar (the binio "hash basename" format — the D-078
          R1 read-asymmetry question is moot: the record uses the canonical sidecar, verified by the binio API).
          hlp_analytics — the Config SHA3-256 line in the common header block (L388).
        | Tests: test_wrk_config 15 → 13 — the 4-test CacheLogic class removed (its facts are gone with the flow); +
          test_config_fingerprint (the independent re-derivation of the sha3_256 of the dump) +
          test_no_cache_file_written (NO rlmwf_* file in the base dir after an up); the down-reset pin extended to the
          fingerprint. test_lm_worker_full_chain: + the A2030 test_config_record_sidecar (the record exists next to the
          model file, its content == the normalized dump, the ctx fingerprint == the sha3_256 of the dump, the sidecar
          verifies via the binio API); the "Config SHA3-256" pins on the console AND the file report; the
          _masked_report_hash helper now masks the run-dependent config hex (the fingerprint embeds the tmp base_dir) —
          the two file-report goldens re-pinned (rlm_04 d44557a8... → 674f54e0..., rlm_03 57f9766b... → bc4857f1...);
          the deterministic-test comment re-anchored (6 hits = the 6 cache_manager levels — no CONFIG "stored" line
          anymore). test_wrk_analytics: the masked-hash helper + the two file-report goldens re-pinned (94a4af7e... →
          3b4a5beb..., f6b54954... → 15c71c7e...).
        | Probes (8 re-pins): verify_wrk_config overhauled 29 → 15 checks (the B7-B13 file sections + the C1-C7
          repeat/mutation sections gone; B6b the fingerprint re-derived independently; B7 no rlmwf_* file; C1 the second
          up is a pure load with a STABLE fingerprint; C3 the 3-field down reset; E5 no file-write idiom in the module
          source); verify_wrk_features B10 + verify_hlp_indexes C2 the flat census drops the CONFIG pair;
          verify_gradient D10 + verify_optimize h1 + verify_zed D11 the file tuples drop the CONFIG entries (verify_zed
          F1 the LMContext line pins shift L128-131 → L133-136 — the D-142 block); verify_analytics C6a the step-13 log
          span 21 → 22 lines, C7b the rlmwf_* set = the 6 cache levels, D3 the console report 17 → 18 lines with the
          Config line (a fixed fake checksum on the hand-built ctx); verify_logistic_model V10 the checksum-typed fields
          8 → 9.
        | The wrk_config R1 / D-078 open item is CLOSED: the ad-hoc flow is removed, the bare-hex-vs-binio asymmetry is
          gone (the record uses the canonical binio sidecar), and I-011 is REALIZED in its C1 form (the per-model config
          record at SAVE — the "storicizzazione" need met without the history; the JSON evolution stays in the file's
          VCS).
        | Suite: 707 → 706 (wrk_config -2, full chain +1). Default tier: 615 run in ~4 s / 91 skipped (71 DB-gated + 20
          PERF). LONG=1 (live DB): 685 run in ~35 s / 21 skipped (20 PERF + 1 VLONG-gated A2050). Probes: the full 20
          verify-probe sweep green (gated and live).

D-143 | 2026-09-09 | Duplicate game positions: the regab_allow_duplicate policy + the validation independence trace
         (Roberto: "Individuare i record duplicati estratti dal DB, le game positions, quelli che non sono univoci.
         Aggiungere un flag nel JSON ... allow-duplicate: boolean. Se false, loggato quanti sono in assoluto ed in
         percentuale; se true, quanti sono stati rimossi. Stessa cosa nella VALIDATION. Aggiungere un check di verifica
         se VALIDATION sia indipendente da POSITIONS. Vanno fatti dei test specifici, micro, e presi dal DB. Nel DB i
         record doppi ci sono, non sono pochi, e sono strutturali. Non altererei la query al db. Farei post una verifica
         in Python ... la chiave e' mover, opponent ... Sviluppa una analisi dettagliata, e fai una proposta operativa.
         Me la presenti, ti do feedback ed approvazione." — the post-extraction duplicate policy + the VLD-POSITIONS
         independence check; the approved analysis, then the rulings).
        | Analysis: the DB is MEASURED, not assumed — on the fixture sets every duplicate (mover, opponent) key appears
          EXACTLY twice, always one CMS row + one CMR row, with IDENTICAL game_value and player (0 multi-game_value, 0
          multi-player duplicate groups; max repeats 2): the same position recorded under two statuses, and the status
          IN ('CMS','CMR') filter returns both. Structural, as Roberto said. The counts: bid 6 = 10,211 dup rows of
          199,932 (5.11%), bid 3 = 103,290 of 1,999,179 (5.17%), bid 8 = 11 of 200 (5.50%) — the current goldens
          (199,932 / 1,999,179) are built WITH the duplicates. The cache subtlety: the dedup must live in the COMPUTE
          flow so the cache file stores the post-policy data set — a flag flip then changes the stored content and the
          rds_checksum, which invalidates the downstream levels through the EXISTING checksum lineage (no format change,
          no new consistency field). Rulings on the presented proposal: P1 OK (regab_allow_duplicate, top-level
          LMConfig, default True = keep = today's behaviour, the backward-compatible migration; false = remove; both
          settings log the absolute count + the percentage), P2 OK (post-extraction pandas drop_duplicates on (mover,
          opponent), keep= first — hash-based O(n), order-preserving, NO sort: a global sort would reorder every row and
          perturb the goldens far beyond the removed ones; "first" = lowest seq, the extraction is ORDER BY seq; the SQL
          query untouched), P3 OK (the compute-flow placement), P4 = LOG ONLY ("calcoliamo l'overlap, e lo mettiamo come
          LOG. Nessuna azione di nessun tipo. Rimane scritto. Se volessimo azioni automatiche bisogna inserire un
          parametro ... quale e' la percentuale massima ammessa ... ma allora entrerebbero altri parametri di qualita'
          ... per ora teniamo traccia e basta" — NO raise, no threshold parameter, no quality family), P5 OK (the test
          plan), P6 = NOT INCLUDED ("la pipeline NON valida i dati. Per calcolare il DB ci sono voluti anni. Verificare
          i dati e' fuori discussione al momento. Non aprirei il tema verifiche." — the same-key-different-game_value
          case is NOT a sentinel; keep-first is simply pinned as behaviour). Name: regab_allow_duplicate (the house
          snake_case, Roberto's choice).
        | Code: regab.py +2 pure @validate_call helpers — regab_dedup_mogv (L470: the drop_duplicates over the (mover,
          opponent) key; returns (deduped_df, total, removed); no logging, no validation) + regab_count_position_overlap
          (L498: the vld records whose key is also in the training set — a pandas inner-merge over the 2 key columns,
          the train side deduped first so a duplicated train key cannot inflate the count; a duplicated vld row counts
          once per record; u64 top-bit safe); both __all__-exported. hlp_config_schemas: LMConfig .regab_allow_duplicate
          (bool, default True, described field — the fixture JSONs gain the key by default, no fixture change).
          wrk_positions: extract_and_prepare (L187) — the SHARED compute path: load_from_db → regab_dedup_mogv → the
          flag branch (True: keep + "[TOTAL] [FOUND] [PERCENT] — kept" log; False: swap the deduped frame + "[TOTAL]
          [REMOVED] [PERCENT] — removed" log) → the post-policy rds; the _up compute_fn is now extract_and_prepare and a
          cache HIT logs the stored post-policy total ("[TOTAL] — data set loaded from cache (regab_allow_duplicate:
          …)"). wrk_vld_positions: reuses extract_and_prepare with the vld bid/status overrides (the A7/A8 pins
          re-pinned) + the same hit line + the D-143 validation-independence check after the pop stats (L104-112):
          regab_count_position_overlap (ctx.positions, ctx.vld_positions) → ONE INFO log ("Validation independence
          check: [OVERLAP: X of N validation records], [PERCENT: P%] — records present in both … (log only, no action)")
          — no raise, no parameter.
        | Tests: +16 — test_regab +11 no-DB micro (TestRegabDedupMogv 5: keep-first, the passthrough, all-identical,
          same-key-different-game_value keeps first WITHOUT raising (the P6 behaviour pinned), the empty frame;
          TestRegabCountPositionOverlap 6: disjoint, partial, full, the duplicated vld row counts per record, the
          duplicated train row does not inflate, the u64 top-bit keys); test_wrk_positions +3 DB-gated
          (TestLMWorkerPositions Duplicates, fixture bid 8 = 200/11/189: flag false → 189 + "[REMOVED: 11]
          [PERCENT: 5.50%]"; flag true → 200 + "[FOUND: 11] — kept"; the cache holds the POST-policy content — a
          flag-false file reloads 189 + the hit line + no "Extracted"); test_wrk_vld_positions +2 DB-gated
          (TestVldIndependenceCheck: rlm_02 train bid 6,7 / vld bid 8 → "[OVERLAP: 0 of 200], [PERCENT: 0.00%]" + no
          raise; rlm_00 train = vld = bid 8 → "[OVERLAP: 200 of 200], [PERCENT: 100.00%]" + NO raise — the log-only
          ruling pinned: the 100%-overlapping vld is traced, the worker completes).
        | Probes (2 re-pins, both the D-143 architecture): verify_wrk_positions A1 the __all__ 2 → 3 helpers
          (extract_and_prepare added); verify_vld_positions A5 (the A5 description: the file delegates extraction to
          wrk_positions.extract_and_prepare) + A7 (the import is now extract_and_prepare, is_cache_consistent) + A8 (the
          vld bid/status overrides are on extract_and_prepare + is_cache_consistent) + D8 (the reuse-identity pin now
          includes extract_and_prepare.__module__ == wrk_positions).
        | Suite: 706 → 722 (+11 micro + 5 DB-gated). Default tier: 626 run in ~4 s / 96 skipped (76 DB-gated + 20 PERF).
          LONG=1 (live DB): 701 run in ~36 s / 21 skipped (20 PERF + 1 VLONG-gated A2050). VLONG=1: the A2050 full chain
          6/6 — the goldens INTACT (the default flag True keeps today's behaviour byte-for-byte: the same 1,999,179
          train records, the same file hashes). Probes: the full 20 verify-probe sweep green. The new INFO lines (the
          duplicate count at POSITIONS/VLD + the independence trace) add nothing to the file reports — the console-only
          witness, the substring pins (assertIn) unaffected.
        | Follow-up (same session, Roberto: "Lo aggiungiamo esplicitamente nei JSON per favore"): the 5 fixture JSONs
          (rlm_00-04) now carry "regab_allow_duplicate": true explicitly (after cache_files_prefix, the schema field
          order). Zero impact on the goldens: the field is optional (Field default=True), and the fingerprint is the
          sha3_256 of the PARSED config's model_dump_json — which includes the defaults — so an explicit key equal to
          the default produces the IDENTICAL normalized dump and checksum (verified on rlm_00 + rlm_04 before/after).
          The D-143 test class was already writing the key explicitly in its re-dumped tmp JSONs (both values) — it
          never relied on the default.

D-144 | 2026-09-09 | C2 (the parked D-142 follow-up): the configuration provenance EMBEDDED in the model file — format
         v2 + the backward-compat v1 reader + config_dump/config_checksum on ModelWeights (Roberto: "Ora puoi imbarcarti
         nei lavori C2. Parti pure!"). RULINGS on the proposal (4 points): (1) ModelWeights carries BOTH the dump and
         the checksum ("checksum + dump" — the in-memory object mirrors the file); (2) the D-142 sidecar record
         (<output>.config.json + its sidecar) is ELIMINATED ("eliminiamo" — the model file is the single source of the
         run's configuration, the A2xxx models are shipped artifacts); (3) the config section goes at the HEAD of the
         body ("mettiamola in testa. Non cambiamo il prefisso." — the binio header prefix RGLM_BINARY_WEIGHTS is
         untouched, only the version constant moves 1 → 2; no v1 artifacts exist in the wild yet, the hand-built v1 test
         files are the only "v1" in existence); (4) a v2 file whose stored checksum does not cover the embedded dump
         RAISES (the sentinel idiom, as in binio).
        | Design: the v2 layout is header (RGLM_BINARY_WEIGHTS, version 2) + section 1 = the configuration provenance
          (the leading body section, the sentinel first: config_checksum — the D-142 CONFIG-level fingerprint — then
          config_dump — ctx.cfg.model_dump_json(indent=4), the same normalized dump the D-142 record used to carry, the
          effective config with the base_dir override included) + sections 2-9 = the v1 sections 1-8 VERBATIM.
          model_weights.py (237 → 276 lines): MODEL_WEIGHTS_FILE_HEADER_VER = 2; the writer gains the leading config
          section (the section comments renumbered 0-9, the header is section 0); the reader accepts version 1 OR 2 (the
          guard message is now "File header version, expected '1' or '2', found '<v>'.") — v1 files load with
          config_dump/config_checksum = None (the backward-compat the C2 spec required), v2 recompute sha3_256(dump) and
          raise "Config section checksum mismatch, expected '<stored>', recomputed '<sha3>'. " on a mismatch;
          ModelWeights gains the trailing defaulted pair config_dump: str | None = None / config_checksum: str | None =
          None (10 → 12 fields; the dataclass forces defaulted fields last although the FILE section leads the body —
          the construction sites are kwargs-only, verified). wrk_save.py (76 → 66 lines): _store_config_record + the
          binio write_sha3_256_sidecar import are GONE (the record is retired); the SAVE log span is now 2 lines (the
          "Configuration record saved to ..." line is gone); the D-142 "Config SHA3-256" line in the analytics reports
          UNTOUCHED (it is the ctx fingerprint, not the record).
        | The v2 file-level goldens are RETIRED by DESIGN (discovered the hard way): the embedded dump carries the run's
          base_dir (the mkdtemp path), so the file BYTES are legitimately run-specific — unlike v1 (no run data inside →
          byte-stable: the 5 archived A2050 v1 files are all exactly 515042 B). The sha3 literal (bcf8d918… A2030,
          3ad18058… A2050) is out; the size literal becomes a BAND: the content is 100% deterministic apart from the 8
          random base_dir chars, and those shift LZ4's match structure by a few bytes (reproduced: the identical raw
          A2050 content, 674425 B, compresses to 516459 or 516455 depending only on the random name — the 516455 case is
          EXACTLY the failed VLONG run's size, its tmp name recovered from the log). Bands: A2030 22700-22800 B, A2050
          516400-516500 B. The determinism guarantee is carried by test_second_instance_deterministic (same base dir →
          byte-identical file) + the read-back provenance pins (mw.config_dump == the live normalized dump,
          mw.config_checksum == the ctx fingerprint) + the model-file sidecar verify.
        | Tests (test_lm_worker_full_chain, 6 → 9 tests): +TestModelWeightsV2 (ungated, no DB, the
          hand-crafted/SimpleNamespace idiom): the v1 file loads with the config fields None (backward compat), the
          synthetic-ctx v2 round-trip (write → read, every field + the embedded dump + the fingerprint), the v2
          corruption sentinel (ValueError); the v1 guard's message re-pinned ("expected '1' or '2'");
          test_config_record_sidecar (D-142) CONVERTED to test_config_provenance_single_source: the record + its sidecar
          do NOT exist (retired), the model sidecar still verifies, the fingerprint semantics survive on the embedded
          fields; A2030/A2050: version 1 → 2, the file pins become the size band + sidecar, + the config provenance
          read-back pins.
        | Probes: verify_save A5 (the version constant is 2) + A6 (12 fields) re-pinned, + A6b NEW (the config section
          LEADS the body, the reader accepts v1|v2, the corruption sentinel) — the census is now 18 checks; the tier C/D
          comments re-derived. The other 19 verify-probes untouched.
        | Suite: 722 → 725 (+3 no-DB micro). Default tier: 725/0/96 in ~4 s. LONG=1 (live DB): 725/0/21 in ~36 s.
          VLONG=1: the A2050 full chain 6/6. Probes: the full 20 sweep green (gated and live). The A2xxx production
          models (A2050, A2150, A2250, ...) are the first artifacts written in v2 — no v1 file ever shipped, the
          backward-compat reader is a format guarantee (the hand-built v1 test files prove it), not a migration path.
        | Docs: model_weights.md (the v2 spec, the 12 fields, the retired goldens + the LZ4-jitter finding), wrk_save.md
          (the single artifact, the record retired, the 18-check census), test_lm_worker_full_chain.md (9 tests,
          the D-144 pins); overview.md + the session-33 journal extended.

D-145 | 2026-09-09 | I-013 O1 (the first of the fg optimization options): the high_performance_fg flag + the numba K3 fg
         kernel (Roberto: "Facciamo solo O1 in questo modulo. Fatto finito, fatto checkin ... e poi miglioriamo anche
         lbfgs on O2, quindi la tua proposta. ... I config rlm_03/rlm_04 a true (gli altri no): OK, perfetto.
         Procedi!"). RULINGS on the analysis (notes/analyses/optimize_performance.md): keep the current
         hlp_gradient_compute ("perche' per ora e' proven e tutto sommato e' 'leggibile'"); add a high_performance flag,
         default false ("con false la funzione ritorna l'implementazione attuale. Con true, ritorna la nuova versione di
         fg sviluppata con le tecniche ed idee di O1 e O2. Ben documentata"); tests verify the two functions are
         equivalent ("test breve") and leave a test for classic; the PIPELINE defaults to high_performance true; and a
         config parameter inside optimization ("high_performance_fg: boolean, default=false").
        | Design: (1) hlp_config_schemas.py — OptimizationConfig gains high_performance_fg: bool = Field(default=False,
          ...) (the one-line schema change; the config dump gains the field, the D-144 embedded provenance + the D-142
          fingerprint move with it — the re-pin is expected and accepted); (2) hlp_gradient.py (91 → 179 lines) —
          hlp_gradient_compute(ctx, high_performance=False): False → the classic closure VERBATIM (the D-094 shape kept
          — Roberto's ruling); True → the K3 kernel: _hp_fg_kernel (@njit(parallel=True, cache=True), the house numba
          idiom as in board.py / pattern.py) — one streaming pass over X, prange over T = 8 FIXED row-blocks
          (_HP_BLOCKS), each block accumulates into its PRIVATE f64 g-buffer + f64 partial norm (race-free: numba 0.67
          has no CPU atomics, CUDA-only — verified); fg_hp: buffer clear + one kernel call + the fixed-order final numpy
          reduction (f64) → float32 (the R1 (D-093) contract preserved for BOTH variants); the returned closure carries
          a high_performance bool attribute (the variant marker, pinned by the tests + the probes); (3) wrk_gradient.py
          (62 → 64 lines) — _up reads ctx.cfg.optimization.high_performance_fg and passes it, the log line names the
          built variant; (4) rlm_03.json + rlm_04.json gain "high_performance_fg": true (the two full-chain fixtures —
          Roberto's ruling; rlm_00-02 and all production configs keep the default False).
        | Why K3 (the study's kernel ladder): K0 classic 735 ms/call (1.00×); K_np pure-numpy per-column 606 (1.21×); K1
          numba fused forward + original tail 448 (1.64×); K1c per-column tail 319 (2.31×); K2s serial single-pass 203
          (3.63×); K3 block-parallel single-pass 52.3 ms f32-accum (14.1×) / 46.0 ms f64-accum (16.1×) — the production
          choice: the f64 per-block accumulators track the float64 reference to ~1e-12 rel (the f32-accum showed
          ~3.2e-06 abs) at +4.3 ms/call. Structural win: NO M×P temporary (the classic allocates the gather result + the
          bincount weight buffer, 384 MB each at A2050 scale); X read once, row-contiguous; w + the T×N f64 buffers
          L2-resident.
        | Determinism (the load-bearing argument): the block split is fixed (T = 8 regardless of the thread count) and
          the final accumulation order is fixed (block order), so the result is bit-identical across runs and machines —
          the 2nd-instance byte-identity contract holds (the full-chain second-instance test passes on the HP path;
          test_hp_deterministic pins the bit-identity directly). The f32 ROUNDING ORDER differs from the classic (a few
          ulps on f and g), so the L-BFGS trajectory shifts slightly: A2050 397 → 356 iters, f 1.4444034e-03
          → 1.4453826e-03 (Δrel 0.07%), both CONVERGED_MIN_GRAD with g_norm < 1e-05; A2030 67 → 71 iters. The mid-run
          flag switch is numerically sound (same objective; the resume re-evaluates f fresh) — no new
          checkpoint-invalidation rule.
        | Verification: (a) no-DB — the 14-test test_hlp_gradient (the 6 new TestHighPerformanceFg: the exact
          zero-weights goldens via the kernel at M = 3 < T = 8 (the empty blocks), the nonzero full math vs the
          independent float64 re-derivation at M = 5000, the classic-vs-HP equivalence rtol 1e-5, the f32 contract, the
          determinism, the markers) + the 2 no-DB TestGradientFlagWiring tests (the worker flag wiring on a
          Context-subclass mock) + the schema test; (b) the exact re-profiling (the new baseline): the A2050 full chain
          on a fresh base dir, per-level timing — OPTIMIZE 26.9 s (356 iters) vs 321.3 s classic (11.9×), the whole
          chain 52.0 s vs ~350 s (6.7×); the two-loop recursion is now the second cost center: 0.023 s/iter × 356 ≈ 8.2
          s ≈ 30% of the HP OPTIMIZE (the O2 motivation); (c) the full suite: 734 tests, 0 failures (VLONG: the A2030 +
          A2050 full chains on the HP path, the second-instance determinism, the EF bit-exact pins) + the verify probes
          re-pinned (verify_gradient A1/A9/A12/A14-A15 + B1/B5 + C1/C5/C11 + G1/G2/G9; verify_optimize E4b; verify_save
          C5 + the band comments).
        | Goldens re-pinned (the D-145 set): the full-chain A2030 + A2050 (the metric dicts, the opt iters/f/g_norm, the
          w_dense sha3 90ca05a3... / 82b329dd..., the EF pins, the two report hashes a9642167... / 695c151b..., the
          console metric rows, the size bands 22800-22900 / 516300-516500, the "Substitution Delta" sign flip -0.00
          → 0.00); the position-based goldens did NOT move (pop statistics, feature-set hash, iwmap offsets). The config
          dump gains one field per model file (the D-144 embedded provenance) — the size bands widened accordingly
          (the D-144 precedent: the band absorbs the LZ4 match jitter + the content shift).
        | Notes: the m negative result (m=20/10 do not converge in 500 iters and are slower — m=93 is load-bearing)
          closed O4; O2 (the numba two-loop in opt_lbfgs, the ~8.2 s) stays the next candidate, its own decision (D-146)
          after the re-baseline. O3 (the pure-numpy per-column variant, 1.21×) was considered and not chosen (K3 is 34×
          faster at the same determinism level).
        | Docs: hlp_gradient.md (the dual-variant architecture + the determinism argument + the perf table + the pointer
          to the study), wrk_gradient.md (the flag wiring), hlp_config_schemas.md (the field), the four test mirrors;
          the analysis stays at notes/analyses/optimize_performance.md as the pipeline documentation reference (Roberto:
          keep it).

D-146 | 2026-09-09 | I-013 O2 (the second cost center after D-145): the two-loop recursion of opt_lbfgs. NEGATIVE RESULT
         on the original proposal (the numba two-loop, the "tua proposta" of the D-145 ruling) + ADOPTION of the
         data-driven alternative O2b (Roberto's ruling: O2b — "out= senza allocazioni", the recommended option).
        | Measurement (A2050 real L-BFGS history, m=93, N=77943 f32): numpy classic two-loop 23.2 ms/call; numba scalar
          fused kernel 22.8 ms (1.02x); numba prange-vector-ops kernel 23.2 ms (1.00x) — the two-loop is
          memory-bandwidth bound and its recurrence is serial over the m pairs (the alpha chain + the beta/r chain), so
          prange over the pairs is impossible and prange over the j-vector only buys SIMD against launch overhead. The
          real cost driver: the 2m fresh per-op product temporaries per call (~58 MB allocated per call at A2050 scale —
          the f64 product of the f64-scalar-times-f32-array, downcast in place to float32).
        | O2b (adopted): _two_loop_recursion pre-allocates ONE f64 product buffer per call (prod) and computes the two
          per-op products with np.multiply(..., out=prod) + np.subtract/np.add(..., out=delta/r). The out= form
          replicates the classic dtype semantics BIT-FOR-BIT (the f64 product, the f32 in-place downcast) — the L-BFGS
          trajectory is UNCHANGED: no golden re-pin (the A2030/A2050 full-chain pins — the 356-iter trajectory, the
          w_dense sha3, the EF pins — are untouched; the VLONG suite is green on the exact D-145 goldens).
          Measured 23.2 -> 16.9 ms/call (1.39x): the A2050 two-loop ~8.2 s -> ~5.9 s, the HP OPTIMIZE 26.9 s -> ~24.6 s.
          The numba variant stays NOT adopted (1.00-1.02x = noise; a flag + buffers + a 2.8 s compile for nothing).
        | Change surface: opt_lbfgs.py (the two-loop body only — 14 lines), test_opt_lbfgs.py +1 (14 tests:
          test_out_equals_original_bit_identical — the original algorithm embedded verbatim as the reference, three
          seeded f32/f64 histories, np.array_equal), no flag (O2b improves the one path in place — there is no "classic
          two-loop" variant to preserve: the original behavior, bit-for-bit, IS the new behavior). Probes:
          verify_optimize has no two-loop body / opt_lbfgs line-count pin — no re-pin. Docs: opt_lbfgs.md (the O2b note
          + the negative result).

D-147 | 2026-09-09 | The A2030 v2 file size band re-centered (22800-22900 -> 22750-22850): Roberto's VLONG run hit the
         failure "v2 model file size 22798 outside the 22800-22900 band". The D-145 band was set from a SINGLE rebase
         run — 22811 B — whose base_dir path prefix (scratch/opt_study/rebase_a2030) differed from the real test base
         dir (build/tmp), shifting LZ4's match structure by ~9-13 B and centering the band one edge too high. The real
         distribution, measured on the real base dir (12 full-chain runs with random mkdtemp names, exactly as the test
         runs): 22798-22802 B — the same 4-byte jitter D-144 documented for A2050 (the 8 random name chars in the
         embedded config dump). The band is a 100-B sanity band centered on the distribution (22750-22850, margin >= 48
         B on each side; the determinism guarantee remains the same-base-dir byte-identity test + the read-back
         provenance pins, not the size). A2050's band (516300-516500) is untouched: Roberto's run passed it (516399
         measured on the rebase, 200 B wide, centered). Change surface: the test assertion + its D-147 comment, the
         verify_save tier-C comment, the test-mirror doc bullet. No golden moved.

D-148 | 2026-09-10 | CLIENT_CHECK: the 16th pipeline level, the saved-model file acceptance test (I-015). Roberto:
         "iniziamo una nuova task. Aggiungiamo un LEVEL dopo SAVE, lo chiamiamo client_check. Legge il model_weights
         file, costruisce la evaluation function e ricalcola i residui della validazione. Devono coincidere a meno di
         1e-9 con quelli della validazione. Svolgi una analisi accurata. Elabora una strategia per le possibili
         implementazioni. Presentami le opzioni, decidiamo insieme." Analysis: the chain is expected BIT-IDENTICAL —
         binio preserves dtype (the w_dense f32 round-trips bit-exact), the gather+offset formula is identical in
         hlp_validate (L116) and the client's _prepare_weights, np.sum(X, axis=1) ≡ X.sum(axis=1) (the same numpy
         reduction), sigmoid IS scipy expit (f32→f32, elementwise, deterministic), the z2y coefficients are
         bit-identical across the ctx (f64 intermediates) vs client (f32 file-round-trip) construction paths for ALL
         THREE fixture logit_clipping values (0.05/0.03/0.01 measured), the int8 game values make the subtraction exact.
         Rulings: (1) A1a — the reference residuals are RECOMPUTED inside CLIENT_CHECK from the in-memory ctx state (the
         hlp_validate forward pass reproduced — VALIDATE untouched, the D-101/D-102 closure stands; deterministic and
         identical to what VALIDATE computed: nothing mutates the vld artifacts between levels 13 and 16); (2) B1 —
         Y-space residuals: Roberto "ho questo dubbio: y e z sono la stessa cosa nella pipeline. Ma fuori dalla pipeline
         no. Il client è dentro e fuori della pipeline... in futuro useremo queste EF su una posizione di gioco, e
         magari confronteremo due valori di predicted value espandendo il game tree a minimax a PLY=6 e PLY=8,
         atterrando su EF diverse perché ognuna avrà il proprio EC. Ora io voglio sempre e soltanto valori
         CONFRONTABILI. E i valori sono confrontabili solo quelli di Y [-64..+64]: quelli di Z non sono confrontabili
         perché sono distorti, e la compressione potrebbe essere diversa tra le due stime" — the Y comparison is
         strength-equivalent to Z (z2y is an invertible affine, the integer subtraction is exact); (3) C1 — the array EF
         only (D-141: 1100× the scalar; the scalar stays bit-exact-pinned elsewhere); (4) the tolerance — Roberto "se
         1e-9 è molto tirata, facciamo 1e-8, ci dà tutte le rassicurazioni del caso allo stesso modo, e non cadiamo
         dentro problemi di ordine delle somme ed eventuali arrotondamenti e troncamenti, cosa ne dici? OK fare valore
         del config JSON. Pulito!" → the NEW LMConfig field client_check_tol (default 1e-8, gt=0): a JSON config value,
         not a module constant (my "scope creep" objection overruled — Roberto's call); (5) E — log only, no new ctx
         field (ANALYTICS is upstream at level 14: the reports are already written). Level mechanics:
         Worker("CLIENT_CHECK", up, down) appended after wrk_save() (the machine is domain-agnostic: no machine change);
         no cache file (the 7th non-cache deviation — the rlmwf_16 slot stays unused); the worker is stateless (re-reads
         the file on every up-move; _down logs only, as SAVE); the file path is cfg.base_dir / cfg.output (as SAVE);
         failure = the ERROR line + RuntimeError (the D-060 semantics: the machine logs, re-raises, the step stays at
         15). Cost: < 1 s at A2050 scale (the D-141 5.6M b/s measurement covers the forward pass). Verified: the scratch
         probe (the 2000-position synthetic rlm_04-mirror) measures max|diff| = 0.0, y_pred bit-equal; the corruption
         case (the 1e-3 weight perturbation) gives 1.959e-01 — ~10^7 above the tolerance (the check detects real drift
         decisively). Suite: 735 → 744 (default 648 run / 96 skipped; LONG 723 run / 21 skipped, live DB; VLONG A2050
         724 run / 20 skipped — the 199932-residual check passes at max difference 0.000e+00) + the 20/20 probe sweep
         green. Re-pins: the full-chain 14/SAVE → 15/CLIENT_CHECK + the A2030 log pin ("Client check passed: 20000
         validation residuals, max difference 0.000e+00 (tolerance 1.0e-08).") — a bit-identity golden; BOTH size bands
         HOLD (the new config field's ~28 B of dump text stays inside 22750-22850 / 516300-516500); the hub V3c 15 → 16;
         verify_zed F1 line-pin L133-136 → L134-137 (the new import line shifted the LMContext zed fields). Change
         surface: wrk_client_check.py (new — the A1a _validation_residuals_y reference + the f64-exact view so no
         rounding noise enters the comparison) + the LMConfig field + the 16th worker-list entry +
         test_wrk_client_check.py (6 no-DB: the bit-identity golden, the RuntimeError + FileNotFoundError paths, the
         cfg-tolerance pin, the factory name, the no-op down) + 3 schema tests (default / override+dump / gt=0) + the
         runner insertion (after test_client). 2 commits (the code + tests + probes, then docs + notes).

D-149 | 2026-09-10 | PLOT: the 17th pipeline level, the matplotlib diagnostics after CLIENT_CHECK (I-016). Roberto:
         "iniziamo una nuova task. Aggiungere un LEVEL per i PLOT con matplotlib. Credo sia corretto posizionarlo dopo
         SAVE, ma proponi diversamente se ritieni corretto farlo. Come gli 'antichi' di R che trovi nel file:
         scratch/rglmw.R. Non fare riferimenti al file nella documentazione, in seguito lo cancelleremo. Avevo 3 plot:
         1- Probability Density (y) vs Game Value Residuals [-64..+64] — Three lines: Reference, Training, Validation;
         2- Residuals vs Fitted Values (grafico a pallini grigi, nuvola dei dati); 3- Residuals vs Game Values (idem).
         Nel 2 e nel 3 c'è un jitter per avere l'effetto nuvola. Studia i 3 plot e replichiamoli. Se hai idee di altri
         plot presentamele, le discutiamo insieme. Proponimi una strategia su come generare i PLOT, dove archiviarli, in
         che formato, e se vanno creati sempre oppure pilotati da uno o piu flags nel JSON." My analysis: the R script's
         p0/p1/p2 (three KDE lines — Reference = the centered training target, i.e. the pipeline's "population" series;
         Training/Validation residuals; sd/mean/min/max margin labels + the training-mean vline; the two gray-dot clouds
         with the R jitter fractions 0.005/0.005/0.7 as a fraction of the data range) + four extension candidates (the
         per-EGV box plot — an R helper never shipped in the return list, the per-EGV mean-residual error bars, the
         parity plot, the normal QQ plot) + the strategy (placement after CLIENT_CHECK, the hlp/wrk split, the config
         pilot, the output location, the format, the seeded-jitter improvement over R's unseeded jitter, the D-060
         failure semantics, no cache). Roberto's rulings: the position "PLOT = livello 17 (dopo CLIENT_CHECK): OK"
         (overriding his own "dopo SAVE" default — the gate first: the figures are drawn for a VERIFIED model file); A2
         OK (hlp_plot.py + wrk_plot.py); B3 OK (the PlotConfig sub-section, the AnalyticsConfig pattern); the location
         refinement — "se la dir dentro Plot_config ha /... è assoluta e può stare fuori, se invece è 'my-plots' è
         relativa a base_dir. Default: plots"; the pilot refinement (the whitelist) — "Io prenderei dal file config i
         nomi dei plot, che sono facoltativi, se ci sono il PLOT è fatto, se manca il plot è saltato. Se i nomi ci sono
         ma enable è falso ... non fa nulla" (the names are a WHITELIST: a listed name is generated, an unlisted one is
         skipped, an empty list is a no-op; the enable master switch dominates — false = do nothing even with names);
         the format — "default pdf, ma può essere pdf | png | pdf,png (intendo and)" CORRECTED by Roberto ("stopped, I
         did a mistake ... default png is OK. not PDF") → the PNG-DEFAULT ruling; the four extensions — "4: falli tutti
         sono molto curioso!" (all of them: the box plot, the mean-residual-by-EGV, the parity, the QQ). Implementation:
         seven figures, all in Y space (the D-148 cross-model comparability ruling — the R plots were in the transformed
         [0,1] target space, the port moves them to the canonical [-64, +64] scale); hlp_plot.py (PLOT_NAMES the single
         source of truth the PlotConfig schema validates against — imported, not duplicated; the seven builders;
         collect_plot_data = the training w_dense forward pass over ctx.hlp_indexes.indexes + the validation forward
         pass, formula copies of hlp_analytics/hlp_validate, the D-148 A1a pattern; the R-semantic jitter; the EGV bins
         = the R round_gv port, 2·rint(x/2) — banker's vs round-half-away-from-zero is a measure-zero difference on a
         continuous f64; the guarded KDE: scipy Scott's rule — the R density() uses Silverman's, below plot resolution —
         the 100k seeded subsample cap, the zero-variance guard); matplotlib/scipy imported LAZILY (the schema imports
         PLOT_NAMES from hlp_plot on every run, including the client — the import must stay cheap); the seeded
         generators (jitter 42, KDE subsample 43) make the figures reproducible run over run — the R jitter was unseeded
         — and the Agg PNG output is byte-deterministic (the rendering golden). Level mechanics: Worker("PLOT", up,
         down) appended after wrk_client_check() (the 17th and LAST level); no cache file (the 8th non-cache deviation —
         the rlmwf_16 slot stays unused, the figures are derived artifacts, regenerated on every up-move); the worker is
         stateless (_down logs only, as SAVE / CLIENT_CHECK); the directory resolution is the worker's job (an absolute
         dir_name is used as-is — outside base_dir — a relative one under base_dir; the schema only carries the Path);
         failure = the D-060 semantics (the machine logs and re-raises, the step stays at 16). The rlm_03.json /
         rlm_04.json test fixtures gain the plot section whitelisting all seven names, so the chains exercise the
         generation end-to-end (the A2050 VLONG chain at the 200k-point scale: 7 PNGs 68-429 KB, chain 58.8 s).
         Verified: the scratch probe (the 200k synthetic: the PNG determinism, the scatter/KDE timings); the suite 744 →
         768 (default 672 run / 96 skipped, 9.0 s; LONG 747 run / 21 skipped, 52 s, live DB; VLONG 748 run / 20 skipped
         — the A2050 class alone re-run: "Ran 1 test in 58.830s OK"); the probe sweep 20/20 → 21/21 (the new
         verify_plot.py: 16 checks — the vocabulary, the lazy import, the seven-builder rendering, the pair formats, the
         byte-determinism, the pilot semantics). Re-pins: the full-chain 15/CLIENT_CHECK → 16/PLOT + the A2030 plot pins
         (the seven PNG magics + the "Plot 'residual_density' saved:" / "PLOT done: 7 plot(s) written to {dir}." lines)
         + the A2050 seven-PNG pin; BOTH size bands re-centered (the D-147 procedure, measured on the real base dir —
         the plot section in the embedded dump grows the file): A2030 22750-22850 → 22940-23040 (2 runs: 22990/22994),
         A2050 516300-516500 → 516500-516700 (1 run: 516551); the hub V3c 16 → 17; verify_zed F1 line-pin L134-137 →
         L135-138 (the new import line shifted the LMContext zed fields); the verify_save header + band comments
         (17-level chain). Change surface: hlp_plot.py + wrk_plot.py (new) + the PlotConfig schema + the LMConfig.plot
         field + the 17th worker-list entry + the two fixture plot sections + test_wrk_plot.py (9 no-DB: the pilot
         no-ops, the seven-PNG happy path + the per-up-move determinism, the pair formats, the absolute dir, the partial
         whitelist, the parity rendering golden, the factory, the down) + test_hlp_plot.py (9: the vocabulary lock-step,
         the jitter bounds, the EGV bins, the KDE guard) + 6 schema tests (17 → 23) + the runner insertion +
         probes/verify_plot.py (new) + the matplotlib pyproject dependency. 2 commits (the code + tests + probes, then
         docs + notes).

D-150 | 2026-09-10 | PLOT styling v2: the fixed axes, the two-line title, the Reference label up, and the top-20
         extreme-outlier report (the follow-up to D-149, after Roberto saw the seven A2050 figures). Roberto's per-plot
         ruling (verbatim, the Italian kept): gv_by_egv_box "i range degli assi devono andare sempre, indipendentemente
         dai dati da -64 a +64 sia x che y"; parity "come sopra"; resid_mean_by_egv "asse x -64 +64, sempre. le labels
         asse y piu rade ... 0, 8, 16, 24, 32, 40, 48, 64 ... (questo grafico e' stupendo ... ci dice che la sigmoid
         introduce una distorsione ... che si vede !!!)"; resid_qq "asse y -64 +64. (bellissimo, come sopra la
         distorsione si vede ...)"; residual_density "sono legato a questo grafico, fu il primo che feci. Comunque: lo
         devi sempre centrare su asse x tra valori ragionevoli. -72 +72. In teoria potremmo avere valori tra -128 e
         +128. certo che se hai tanti valori che sbagliano di piu' di 100 vuole dire che il modello e' tanto sbagliato.
         Diciamo che dovremmo avere un qualche report dei 10/20 outlier piu estremi. Sarebbe poi uno spunto capire come
         mai il modello sbarella cosi. La label grigia reference, va spostata piu in alto cosi si sovrappone alla
         linea"; resid_vs_fitted "anche qui le scale x e y: x vai sempre tra -64 e +64, y sempre simmetrico, teniamo
         valori ragionevoli"; resid_vs_gv "questo non mi torna, secondo me le labels sono invertite ... Game value(Y)
         (asse x) va da -100 a +100, e' impossibile, sono i residui che hanno questi range"; tutti "il titolo ha due
         righe. Nome del grafico, descrizione modello. va benissimo. Spazia le due righe un pochino di piu. Nome del
         grafico in grassetto. Descrizione modello corsivo ed un font piu piccolo." Diagnosis of the resid_vs_gv "swap":
         the labels were NOT swapped — the 0.7 "cloud" jitter (±44.8 units) stretched the data-driven x auto-range to
         ±108; the fix pins x on the [-64, +64] game-value domain (the jittered points beyond the domain are clipped by
         the axis). Implementation: the fixed-axis constants (_AXIS_GV=64.0, _AXIS_DENSITY=72.0, _TICK_STEP=8.0) + the
         _sym_limit helper (the max |residual| rounded UP to the tick step, the "valori ragionevoli" symmetric limit);
         the axes: the box plot BOTH axes + parity + mean-by-EGV x + the two scatter clouds' x on the full [-64, +64],
         the density on the centered [-72, +72] window (the in-theory ±128 residual is clipped there — the outlier
         report is where the broken-model cases show up), the QQ y on [-64, +64] (x, the normal theoretical tail ~±3.3,
         stays data-driven); the step-8 tick grid (0, 8, 16, ...) on the box/mean axes; the two-line title in _fig (the
         name BOLD fontsize 13, pad=26; the run name ITALIC fontsize 10 just above the axis — the "spazia le due righe
         un pochino di piu"); the density Reference label moved HIGH (0.98 of max_y, it overlapped its line at the lower
         position) + the legend REMOVED (the R original had legend.position="None" — the margin labels identify the
         curves); the D-150 OUTLIER REPORT in wrk_plot._up: the top-20 |validation residual| via the STABLE argsort
         (deterministic, tie = the lower index first), the header line + 20 lines carrying the position's bitboards (the
         mover/opponent hex — Roberto can investigate the extreme case), the game value, the fitted, the residual.
         Verified: the default suite green (the parity rendering golden re-pinned: ff459b8e... → 70c3de2b...), the LONG
         suite green (the A2030 chains exercise the new styling + the outlier pins: the header + the 20-count), the
         verify_plot probe 0 failures, the preserved A2050 run (build/tmp/a2050) regenerated with the new styling. Suite
         768 → 771 (the +1 outlier test, the +2 _sym_limit tests). No config change (the report is log-only, no new
         field — the size bands stand). 2 commits (the code + tests, then docs + notes).

D-151 | 2026-09-10 | PLOT mean-by-EGV y-axis refinement (the follow-up to D-150, after Roberto looked at the restyled
         resid_mean_by_egv.png). Ruling (verbatim): "Riduci la dimensione del font dei valori sugli assi x e y ( gli 0,
         8, 16, 24, ... ). asse x perfetto ( -64 ... +64 ). asse y usiamo i valori min e max reali del grafico.
         teniamolo sempre simmetrico, se il valoe e' nel range -16,+16 teniamolo in questo range ...". Implementation:
         the y limit is now the ACTUAL data extent (the |mean| + sd of the error bars, the full plotted content) rounded
         UP to the step-8 grid and kept SYMMETRIC (the _sym_limit reuse — his [-16, +16] example: data inside ±16 → the
         axis is ±16, not the full ±64); the y ticks are the step-8 grid WITHIN the limit (0, 8, 16, ... — the "labels
         più rade" of D-150 still apply, just over the real range); the tick labels on BOTH axes drop to fontsize 8 (the
         default 10 — his "riduci la dimensione del font"). The x axis is unchanged (the full [-64, +64] domain,
         "perfetto"). Only this one builder changed: the parity golden is untouched, the other six renderings
         byte-identical (verified in the preserved A2050 regeneration: resid_mean_by_egv.png 71550 → 59226 B, the rest
         unchanged). The test modules + the verify_plot probe green. 2 commits (the code, then docs + notes).

D-153 | 2026-09-11 | The boxplot stale-label bug (found by Roberto: "i dati sono corretti. Sono le LABELS dell'asse x
         che sono sbagliate. Partono da -62 e vanno con passo 2 fino a -30"). The diagnosis: ax.boxplot() leaves the N
         CATEGORICAL tick labels (the bin values) on the x-axis even for numeric positions; a positions-only
         ax.set_xticks(ticks) switches the locator to the 17 step-8 positions but matplotlib keeps the stale 62 labels
         and prints the FIRST 17 of them (-62..-30, the first 17 bins) under the step-8 positions. The axis LIMITS were
         always correct (verified: xlim/ylim (-64, 64) pre and post savefig, autoscale off, get_xticks() = the step-8
         grid — only the label TEXT was stale; the get_xticklabels() dump was the smoking gun). Fix:
         ax.set_xticks(ticks, labels=[str(int(t)) for t in ticks]) — the explicit labels clear the stale categorical
         ones. Reproduced minimally (a boxplot of 62 synthetic positions: 62 labels after boxplot, stale 17 after the
         positions-only set_xticks, correct 17 with explicit labels). The other six builders are unaffected (no boxplot;
         the mean-by-EGV explicit set_xticks verified correct in the rendered image). Only the boxplot PNG bytes change
         (110248 → 109169 B); the parity golden untouched; the test modules + the verify_plot probe green. Verified by
         looking at the regenerated figure: the labels now read -64, -56, ..., 64, the data diagonal unchanged.

D-154 | 2026-09-11 | The notes' scope is the Reversi portfolio: never record DSH/vLLM/harness infrastructure behavior in
         notes/decisions.md or the journals. Roberto's ruling (verbatim): "come regola non scrivere mai nelle decisioni
         e nel log a proposito del funzionamento di DSH, vllm, non sono rilevanti per reversi, e ricordati che
         pubblicheremo su github prima o poi". The notes are publication material; the collaboration tooling is not part
         of the portfolio. Applied retroactively in the same commit: the earlier infrastructure entry was removed from
         this log and from the journal (the boxplot bug entry D-153 stands on its own). Promoted to rules.md (Language &
         collaboration).

D-155 | 2026-09-11 | The PLOT label standardization + the density-label move + the A2050 PDF output. Roberto's ruling
         (verbatim, the gist): "A me piace di piu 'Evaluated game value' standardizziamo su questo. La Y tra parentesi
         rimuovila ovunque. Solo quando facciamo il binning, metti tra parentesi (binned every 2), se fosse possibile,
         le parentesi e il contenuto in corsivo con un font di 2 punti piu piccolo. Se possibile, altrimenti va bene lo
         stesso. Non diventare matta con scritte aggiuntive, se e' supportato lo facciamo, altrimenti no." + "Nel RUN
         2050, nel JSON aggiungi anche PDF, cosi guardiamo anche quelli." Applied: every axis label and title now says
         "Evaluated game value" (the two "Fitted" titles renamed); the bare "(Y)" removed from every label (the PlotData
         docstrings reworded to "the Y scale"); the two binned axes (the box + the mean-by-EGV) carry the italic
         mathtext note "(binned every 2)" (the _BINNED_NOTE constant) at the axis font size — this matplotlib 3.11 build
         has no mathtext size commands (\small and \itshape both rejected), so the "2 pt smaller" ask is the ruling's
         accepted fallback. The density Training label moved from ~x = -14 (covering the peak) to ~x = +25 (the _TXT_X
         fraction 0.40 -> 0.674), height unchanged. The A2050 config (rlm_03.json) plot format "png" -> "png,pdf" (the
         worker's native comma-split): the preserved run now writes 7 PNG + 7 PDF (the valid PDF 1.4 files); the
         chain-test assertions (the 7 PNG exist, the name-based "7 plot(s) written" log line) are unaffected. Verified
         by looking at the regenerated box + density PNGs.

D-156 | 2026-09-11 | I-017 kickoff: the project to analyze the analytical properties of the FEATURES. Roberto (the
         gist): "Iniziamo una nuova task. ... Analisi delle caratteristiche delle FEATURES. Ho in mente due approcci
         diversi: a- IMS (Informazione Mutua Simmetrica) o meglio in Inglese SU (Symmetrical Uncertainty) — non impiega
         l'informazione del game value. Misura solo la dispersione e la correlazione delle configurazioni presenti nelle
         features. b- eta_quadro e il suo successore piu sofisticato omega_quadro misurano invece l'effetto della
         feature, e quindi hanno bisogno dei game_value. Proponimi un piano di azione granulare ... Lo vediamo insieme,
         lo commento, e lo raffiniamo ... Quando il piano e' chiaro, scrivi un file md in notes dedicato a questo
         progetto, chiamiamolo analytical_properties_of_features.md. Con obiettivi, piano, tasks. Fai un commit. E solo
         in seguito cominciamo a lavora sulle task una alla volta." The plan document is written DRAFT v0 at
         notes/analytical_properties_of_features.md: proposed design = the 18th level FEATURE_ANALYSIS (step 17, after
         PLOT — the D-148/D-149 tail precedent), the (feature, instance) sub-variable as the analysis unit (the
         design-matrix unit: the intercept constant, the mobility count column, the pattern's D8-orbit ternary columns
         with code 0 = "no match" as a first-class group), the FeatureAnalysisConfig pilot (the PlotConfig pattern:
         enable + the methods whitelist {su, eta2, omega2} + top_k_pairs + dir_name/report_file_name/export_csv), no
         cache file (the rlmwf_17 slot, file-less — the 9th non-cache deviation), the TXT+CSV reports, training corpus
         only, the tasks T0..T4 one per session. Five open points (ODP-1..5) await Roberto's confirmation before T1
         starts. No source files touched.

D-156b | 2026-09-11 | I-017 plan revision v1: Roberto's redesign proposals (his words, the gist) + Nia's comments. (1)
The SU analysis must NOT use the DB positions: it depends only on the features → generate a NEW, DB-independent corpus:
random games from the initial position (board.py is fully vectorized; the positions are NOT solved — only the
configuration frequencies are wanted), a ~1M batch accumulated into the frequency dictionary keyed by the configuration
index, ~1000× (1-10e9 positions, "precise a piacere"). (2) Reorder the pipeline: FEATURES first, then the SU analysis,
then POSITIONS — enabling the STOP after the SU step to inspect the patterns' never-observed configurations before the
full pipeline. (3) OMEGA needs the DB positions + the indexes: its own level BEFORE the expensive OPTIMIZE (his
preference) rather than a section in ANALYTICS. (4) A JSON target_level parameter (default "last") for the stop. (5) The
SU level needs the CACHE, for sure (it runs once; it stays valid while the features are unchanged). (6) SU is
instance-level: a MATRIX between instances (EDGE-DIAG8 → 4×2 = 8 values; the EDGE-EDGE self-pair has the 1-diagonal) —
at the A2050 scale (~1,600 metrics) the SU pairs are specified EXPLICITLY in the config; the adherence runs for ALL
features. Nia's comments (in the document v1): the move_to_step string-name API already exists (target_level is a small
facade addition); no tracked random-game generator exists (new component in T2); the slot shift orphans the production
caches (one recompute); the reordering realizes I-012; honest cost model (1e8 ≈ 10 min, 1e9 ≈ 1-3 h — the accumulation
dominates); the pair list joins the corpus cache signature (the two-tier cache parked v2); the DB sampling window (the
"ec" filter) is the main adherence risk (ODP-2, his knowledge needed); the task split grows to T1..T7 (T1 = the
reordering, first, on its own). Document updated to DRAFT v1 (notes/analytical_properties_of_features.md); the new ODP
list: ODP-1..8. No source files touched.

D-156c | 2026-09-11 | I-017 plan revision v2: Roberto's confirmations + the PRNG ruling. (1) P2..P6 OK as designed. (2)
The P1 window correction (verbatim, the gist): "Sei un po' fuori strada Nia. se stiamo lavorando su un Modello ec=20,
tutte le partite random si arrestano a ec=20. Game over. Misuriamo mele con mele, e pere con pere." — the v1 ODP-2
"risk" is RESOLVED into a spec constraint: the synthetic generator plays the same ec arrest rule as the DB generator
(the exact ec formula is pinned at T7 against Roberto's DB code). (3) The PRNG (Roberto, the gist): the code that
generated the DB uses a library HE WROTE from the published work of two Japanese researchers — the MT19937 of Makoto
Matsumoto and Takuji Nishimura (the twisted generalized feedback shift-register "Mersenne Twister", the Mersenne-prime
period 2^19937−1, the 623-dim equi-distribution, the DIE-HARD pass): "magari potremmo pensare che sia un overkill, ma
... è difficile dire quanto fatto bene sia il random generator di una libreria generica. E pensa quanto lavoro, enorme,
ho fatto e stiamo facendo, per poi scoprire che i game non sono poi così random. ... meglio perdere un poco di tempo e
avere una cosa SOLIDA" → the line-by-line C → Python port of his library (the new core module reversi/feature_prng.py),
the bit-exact C comparison as the hard verification gate (the C source = ODP-10). (4) ODP-1: the corpus default 1e7
("che gira veloce ... se viene omesso, non interessa all'utente, teniamolo piccolo"). (5) "Le TASK falle più granulari.
Più fai granulare più siamo lucidi sul design e sulle varie implicazioni. Aggiungiamo la costruzione della libreria PRNG
... il generatore di game random" → the task split refined to T1..T19 (one focused commit each: the reordering, the PRNG
port + verification, the single-game / wave / pick / accumulators generator steps, the statistics kernels, the config,
the two workers, the wiring, the close). Nia's design addition (ODP-9): the PERMUTATION LOOKUP TABLE (the seeded {n →
permutation of 0..n−1}, n = 1..64, 2016 total PRNG draws) keeps the move pick fully vectorized — the PRNG stays the
quality anchor without becoming the bottleneck (the per-move draw alternative would be ~1e9 Python calls). Document
updated to DRAFT v2; the ODP register: ODP-1..8 closed, ODP-9/ODP-10 open. No source files touched.

D-156d | 2026-09-11 | I-017 T0c close: the plan v2 is CONFIRMED. Roberto (the gist): "Ho visto il documento con le
TASKS. Molto bene. Procediamo come sempre apriamo una TASK, tu fai il piano dettagliato di azione, io do OK esplicito. E
ci rivediamo a cose fatte. Come fatto fino ad ora. Il codice R l'ho rimosso. Ti ho copiato i sorgenti in C (anche i
moduli da cui dipende prng, dovresti avere tutto per farlo funzionare, ma portiamo solo prng). Chiudiamo la task T0c.
Siamo pronti per partire." Applied: the ODP register closed in full — ODP-9 the PERMUTATION LOOKUP TABLE adopted (the
seeded {n → permutation of 0..n−1} over n = 1..64, 2016 total PRNG draws, the pick fully vectorized); ODP-10 the C
source DELIVERED in scratch/ (prng.c 731 lines + prng.h the library + the dependencies bit_works.c/h + time_utils.c/h —
present for the build, NOT ported, per Roberto "portiamo solo prng" — + Roberto's own C test suites ut_prng.c 977 lines
+ ut_bit_works.c: the verification oracles for T2/T3). The rglmw.R scratch reference removed by Roberto (the I-016 "in
seguito lo cancelleremo" ruling executed — the ideas line annotated). The T1 planning reconnaissance refined the v2 cost
claims (the v2 erratum, in the document): the reordering shifts ONLY the POSITIONS cache slot (rlmwf_02 → rlmwf_03; the
file-less FEATURES takes the old step 2, INDEXES onward keep their slots) → the production one-time cost is ONE DB
extraction (the downstream checksum lineage survives — the INDEXES/WMAPS/DESIGN_MTR/GENERATE/VLD_POSITIONS caches still
hit); the size-band re-centering and the hub 17 → 18 count are T18 effects (the new config sections + levels), not T1
effects; the model file is byte-identical at T1 (the config dump unchanged). Scratch cleanup (Roberto's ask, before the
C source arrived): 2.9G → 16K (the closed-campaign artifacts removed — the opt_study raw data, the one-off scripts, the
logs; nothing live referenced the scratch files). The detailed T1 plan is presented for Roberto's explicit OK (the
standing workflow). No source files touched.

D-157 | 2026-09-11 | I-017 T1 executed: the pipeline reordering — FEATURES (step 2) before POSITIONS (step 3),
         realizing I-012. Roberto: "OK. Esegui T1." The adjacent transposition in the worker list (logistic_model.py) —
         nothing else moves. Consequences (verified, the hub V3c re-pin): only the POSITIONS cache slot shifts (rlmwf_02
         → rlmwf_03; the file-less FEATURES takes the old step 2, INDEXES onward keep their slots) → the production
         one-time cost is ONE DB extraction (the downstream checksum lineage survives); the model file is byte-identical
         (the config dump unchanged). The test surface: test_wrk_features is now DB-FREE (the setUp no longer moves
         through POSITIONS — the gate + the stale M1 comment removed, I-012 resolved); test_wrk_indexes setUp re-pinned
         (FEATURES = step 2); test_wrk_positions rlmwf_03 + step 3; test_logistic_model gains the dummy FEATURES worker
         (the string move to POSITIONS now crosses step 2); the full chain unchanged (PLOT stays step 16). Probes
         re-pinned: the hub V3c list; verify_wrk_features (B2/B10/B13/C1/C4/C6/C7 — the probe is now DB-free too);
         verify_wrk_positions (rlmwf_03); verify_hlp_indexes (C2/C7/E3); the file-list pins in verify_gradient D10 /
         verify_optimize H1 (rlmwf_03 + the no-rlmwf_02 negation — the old "no rlmwf_03" pinned the old FEATURES slot) /
         verify_zed D11. run_utests.sh the machine order. Mirrors updated in the same commit (D-007), including the
         level chains in the 12 downstream-level docs. Verification: default tier 771/0/94 GREEN; VLONG 771/0/20 GREEN
         (the A2050 chain on the new order); the 22-probe sweep green. I-012 → done (ideas.md).
D-158 | 2026-09-11 | The parity PNG golden re-pinned (the env drift). Found during T1 verification: the D-150 golden
         (pinned 09-10, after the matplotlib 3.11.1 upgrade at 17:25) no longer matches. Ruled out as a T1 effect (fails
         on the parent commit 753e77c with T1 stashed). The rendering is DETERMINISTIC (the same hash across runs) and
         VISUALLY IDENTICAL (the exported PNG inspected: the two-line title, the SYNTH_PLOT subtitle, the fixed axes,
         the grid, the identity line) — only the font rasterization bytes moved (the matplotlib font cache was
         regenerated 09-10 17:34, after the upgrade). The D-127 version-sensitive golden pattern applies: re-pin on
         environment drift. Committed (ed518fd) before the D-157 commit (4186e6d) as the green-suite prerequisite.
