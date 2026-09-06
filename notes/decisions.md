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
