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
