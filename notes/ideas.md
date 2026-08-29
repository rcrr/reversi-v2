# Ideas / future backlog

Format: I-NNN | status (idea | in-progress | done | dropped) | idea

I-001 | idea | Full restructure of the original repo (later, not now).
       The notes produced here should migrate into the new repo as its
       documentation skeleton.

I-002 | idea | Vectorize `position_flips` / `position_make_move`.
       The author's own comment in board.py flags this: `_kogge_stone_mm` is
       currently scalar Python while `legal_moves` is numba-parallel.

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
       original 2008 repo contains callers using the old method syntax
       (.names() / .masks()), those call sites must be updated to
       parenthesis-free property access when that file is migrated into
       twolm. Count of affected sites unknown until that file is
       analyzed — grep the original repo for ".names()" / ".masks()".

I-007 | follow-up | FeatureSet column-labelling helper (raised
       2026-08-28, D-041, feature module M3): FeatureSet offers no
       way to map a column of its (N, I) index matrix to the feature
       name producing it (unlike MobilitySet.names/masks, D-024).
       The pipeline's table builders will need it. Left as-is on
       Roberto's decision; design the helper when the pipeline
       module that labels columns arrives (note: each pattern
       occupies n_instances D8-instance columns, so a
       column-level labelling needs an instance-aware design).

I-008 | idea | Extend the logistello-papers reference collection
        beyond 2002 (raised 2026-08-29, session 12, web search on
        Buro's publications): post-2002 works are missing — the
        Nao era (world champion 2015-2016) and the book "Reversi
        for Optimal Players". Start from Buro's own publications
        page (https://skatgame.net/mburo/publications.html);
        logistello-papers/ is read-only, so collection + index
        updates need Roberto's explicit go-ahead.

I-009 | follow-up | Pipeline construction boilerplate (raised
        2026-08-29, session 19, R3 discussion): Roberto notes his
        pipeline client carries a bit of boilerplate in the model
        construction (worker/context/machine wiring). When the
        logistic_model/RLM pipeline module arrives in the workspace,
        evaluate a declarative step table / @step-style helper /
        pipeline base class on top of StateMachine to trim it.
        Blocked on: the pipeline module not being in the workspace
        yet (can't see the actual boilerplate).
