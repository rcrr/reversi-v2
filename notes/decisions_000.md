# Decisions log — volume 000 (closed)

Format: D-NNN | date | decision | rationale

Volume 000: D-001…D-116 (2026-08-25 → 2026-09-06); closed at
the D-118 rotation (4189 lines > the 2000 cap); the open log
continues in notes/decisions.md.

This is the append-only HISTORICAL LOG: the "why" of every action
and commit in this workspace. It grows without bound and is
consulted only when needed or for historical research. The rules
in force right now live in notes/rules.md (the active
legislation): when a decision establishes an enduring rule, the
rule is promoted there with this D-number as the origin pointer
(same commit); a retirement removes the line from rules.md and
is logged here with a new D-number. D-numbers are sequential and
never reused or renumbered (the docs' State lines and the
cross-references depend on them).

D-001 | 2026-08-25 | Incremental staging workflow: copy one source file at a
       time into this workspace and develop here; no full-repo work now.
       | The full repo is 18 years old with many used/unused files; bringing it
       all in would be too dispersivo. The workflow must be proven here first.
       Full-repo restructure stays a later goal (I-001).

D-002 | 2026-08-25 | Notes and workspace comments: English.
       | User choice; code comments in the repo are English.
       Conversational replies to the user remain in Italian.

D-003 | 2026-08-25 | `git init` in the staging workspace.
       | Safety net for 18-year-old source files and for the notes. Verified in
       the dsh-agent-instructions source (findProjectRoot, files.ts) that
       AGENTS.md injection works with or without git (fallback root = cwd).

D-004 | 2026-08-25 | Autonomy: the agent updates NOTES.md and notes/
       autonomously after each milestone/end of work; source files are touched
       ONLY on explicit user request.
       | User choice. Keeps the knowledge layer current without waiting, and
       keeps 18-year-old code under strict human control.

D-005 | 2026-08-25 | Three-layer memory: AGENTS.md (standing instructions,
       auto-injected every session by the dsh-agent-instructions plugin) +
       NOTES.md (state/next steps, read first) + notes/ (knowledge, on demand).
       | Makes "read the state first" structural instead of relying on either
       party remembering. AGENTS.md stays small (prompt byte budget applies);
       content lives in NOTES.md/notes/.

D-006 | 2026-08-25 | All Python sources live under `src/` (src layout);
       never in the project root.
       | Python best practice: no accidental in-tree imports during tests,
       clean path to packaging at the later full restructure. Test location
       still open — to be decided when test_board.py arrives (candidates:
       top-level `tests/` or `src/tests/`). All notes must stay consistent
       with this tree.

D-007 | 2026-08-25 | Code documentation lives under `docs/` and mirrors the
       source tree: `src/X.py` → `docs/src/X.md`. `notes/` keeps only
       collaboration content (decisions, ideas, log).
       | docs/ is the universal convention for code documentation, is assumed
       by doc tooling, and migrates as-is into the restructured repo
       (I-001). Mirroring keeps the lookup rule trivial as the file count
       grows. Code knowledge and process journal are different natures and
       get different homes.

D-008 | 2026-08-25 | Sources live in the `twolm` package under src/
       (src/twolm/); unit tests inside the package at src/twolm/test/
       (resolves the open test-location item in D-006).
       | Prescribed by the code itself: test_board.py does
       `from twolm.board import *` and its header documents
       `python3 -m unittest twolm.test.test_board` (old repo: PYTHONPATH=./py).
       In staging the same invocation uses PYTHONPATH=./src. Both packages
       (twolm, twolm.test) got minimal `__init__.py` scaffolding.

D-009 | 2026-08-25 | Obsidian local vault state (`.obsidian/`) is gitignored
       at the workspace root; `logistello-papers/.obsidian/` was untracked
       (files kept on disk).
       | Obsidian rewrites workspace.json on every open, dirtying the working
       tree constantly. .gitignore only affects untracked files, so the
       already-tracked copy had to be untracked (git rm --cached).
       .gitignore is deliberately minimal for now ("per cominciare"); more
       entries (e.g. __pycache__/, .venv/) when needed.

D-010 | 2026-08-25 | Virtualenv `.venv/` at the workspace root
       (gitignored) with the minimal dependency set for the board module:
       numpy, pydantic, numba.
       | User choice: only what is necessary, nothing else. The set is
       derived from the actual third-party imports of src/twolm/board.py
       and src/twolm/test/test_board.py (none beyond these three).
       Installed 2026-08-25: numpy 2.5.2, pydantic 2.13.4, numba 0.67.0
       (llvmlite 0.49.0 transitive). Tests are NOT run yet — execution
       happens together with the user.

D-011 | 2026-08-25 | Project packaging: minimal `pyproject.toml` (setuptools,
       src layout) with twolm installed editable into .venv.
       | User request ("installa il python .venv"): make the project
       importable from the venv without PYTHONPATH. Editable install
       (PEP 660) keeps a single source of truth in src/ — no copies, no
       reinstall after edits. `dependencies` (numpy>=2.0, pydantic>=2,
       numba>=0.60) reproduces the D-010 set in a fresh venv. Test command
       becomes `.venv/bin/python -m unittest twolm.test.test_board` (the
       old PYTHONPATH=./src invocation still works as a fallback).

D-012 | 2026-08-25 | Test-suite analysis is doc-only: all defects and gaps
       are catalogued in docs/src/twolm/test/test_board.md; nothing in
       src/twolm/test/test_board.py is changed.
       | User scope for this task: analysis + completeness feedback, no
       fixes. Source/test edits only on explicit request (D-004). The 11
       defects (incl. one broken 2-D test, two NameError landmines in
       failure paths, one dead assertion) and the P0/P1/P2 priority list
       are the ready input for a follow-up fix session.

D-013 | 2026-08-26 | T08 (report §5.8) REJECTED: the 8 header constants in
       test_board.py (row_1, row_8, column_a, column_h, half_left,
       half_right, half_top, half_bottom) are NOT renamed; the code is
       correct as-is. No code change, no commit of sources.
       | The report finding used chess vocabulary ("file a", "rank 1") and
       called the constants "transposed"; the project convention is
       row/column, not file/rank — this is Reversi, not chess. Roberto
       (2026-08-26): the error was the analysis, not the code. The
       canonical convention is now recorded in notes/naming.md, with a
       standing rule in AGENTS.md and a pointer in NOTES.md, so the
       vocabulary error cannot recur in future sessions.

D-014 | 2026-08-26 | D8 board symmetries canonized in notes/naming.md:
       the 8 names, the fixed slot order [ro000, ro090, ro180, ro270,
       fvert, fh1a8, fhori, fa1h8], the anti-transformation order
       [ro000, ro270, ro180, ro090, fvert, fh1a8, fhori, fa1h8], and
       the four-corner mapping of each symmetry. T16 (report §6)
       resolved: findings (a)–(d) (diagrams swapped / wrong cells) are
       REFUTED by cell-by-cell re-verification against the compiled
       code — code, tests, and docstring diagrams agree; only the
       "rotaded" typo stood and was fixed (ro000 docstring).
       | Roberto (2026-08-26): the eight transformations are a
       geometric/algebraic property of the board; their order is
       arbitrary and he fixed it; for every slot, transformation ∘
       anti-transformation = identity (rotations pair, reflections are
       self-inverse). The false diagram verdicts stem from reading the
       diagrams under a non-canonical convention (row 1 at the bottom)
       — the same root cause as T08/D-013. Standing records in
       notes/naming.md + AGENTS.md make the concept permanent.

D-015 | 2026-08-26 | `position_final_value` diff<0 OverflowError fixed;
        `bitboard_count` annotated `-> np.uint8` (T22, report §3-D/§8)
       | Real bug, found by probe while adding the missing WOFC branch
       tests: in `position_final_value`, `ec = 64 - (mc + oc)` was
       computed with np.uint8 operands (`bitboard_count` returns the raw
       `np.bitwise_count` result), so the `diff < 0` branch
       (`delta = diff - ec`) raised OverflowError for EVERY position
       where the opponent leads by at least one disc. The `diff == 0`
       and `diff > 0` branches were unaffected (their results fit in
       uint8).
       | Fix (approved by Roberto, T22): `position_final_value` uses
       `ec = 64 - int(mc + oc)` (Roberto's form; the explicit int guards
       the arithmetic — mc+oc <= 64 always, so it stays safe under a
       future vectorization). `bitboard_count` keeps returning the raw
       `np.uint8` (no behavior change); its annotation was corrected
       from `-> int` to `-> np.uint8` so the signature is honest. A
       first T22 commit had converted the return to a Python int; it was
       reverted per Roberto's clarification. No numba impact (no
       njit/overload references it, only plain Python callers). Added
       the 3 missing WOFC branch tests (draw 1v1 -> 0; opponent leads
       1v8, 55 empties -> -62, crashed pre-fix; full board 33v31 -> 2).
       Suite 157 -> 160 tests, GREEN.

D-016 | 2026-08-26 | `legal_moves` dispatch dtype branch is dead code —
       removed (T25, report §7.3.1)
       | Probe-verified: the `raise TypeError("The dtype of mover and
       opponent arrays must be Bitboard.")` branch of `legal_moves` is
       unreachable. Both arguments are annotated `Bitboard |
       BitboardArray` and `BitboardArray` carries a `BeforeValidator`
       (`validate_bitboard_array`) that rejects any ndarray whose dtype
       is not uint64 before the dispatch runs, so inside the array
       branch both dtypes are always uint64. The "dtype mismatch"
       input therefore surfaces as a pydantic ValidationError ("Array
       dtype must be uint64, got ..."), not as the dispatch TypeError
       that the report (test_board.md, Area C dispatch contract)
       describes. Approved by Roberto (T25): the dead branch was
       removed from the code; the guard's intent is now carried by the
       `BitboardArray` annotation itself. Note: reachability depends on
       that annotation — re-annotating `legal_moves` with a bare
       `npt.NDArray` would make the guard reachable again. Added the
       four error-branch tests (bare Python int -> ValidationError;
       shape mismatch -> ValueError, message pinned; non-uint64 array
       -> ValidationError; mixed scalar/array -> TypeError, message
       pinned). Suite 163 -> 167 tests, GREEN.

D-017 | 2026-08-26 | R1 resolved "docstring follows the code":
       `position_make_move` illegal-move contract is None (T36/T37)
       | `position_make_move` had a three-way inconsistency: the
       docstring promised "the same board is returned" for an illegal
       move, the code returns None (`position_flips` yields
       `(Bitboard(0), None)`), and the return annotation said
       `-> PositionField`. Roberto chose option B — the docstring
       follows the code: docstring now reads "When an illegal move is
       passed None is returned." and the annotation is
       `-> PositionField | None`. Code behavior is unchanged (the
       annotation is not runtime-validated by @validate_call, which
       checks arguments only), so the existing
       `test_position_make_move_illegal_returns_none` pin stays valid
       and the suite is unaffected. Rationale: None is a useful
       rejection sentinel for callers; the "same board" line looks
       residual from the original C in-place idiom; the only internal
       caller (`position_is_game_over`, PA swap) is unaffected. docs
       updated (board.md R1 marked resolved). Suite GREEN: 167/0/12.

D-018 | 2026-08-26 | R3 resolved: explicit `move == 64` pass check in
       `position_is_move_legal` (T38)
       | `position_is_move_legal` detected the pass move (code 64)
       through the uint64 shift wrap: `move_as_bitboard(64)` computes
       `uint64(1) << 64`, which is 0 because NumPy DEFINES integer
       shifts by an amount >= the bit width as 0 (documented NumPy
       semantics; probe-verified on NumPy 2.5.2: 64/65/66 all -> 0).
       Note the attribution matters: the x86 SHL instruction masks the
       count modulo 64 (Intel SDM), so raw hardware `1 << 64` would be
       a no-op, not a zero — the guaranteed-0 behavior is NumPy's C
       implementation, not the ISA. Roberto chose the explicit-check
       option ("per chiarezza"): `position_is_move_legal` now tests
       `move == 64` directly (pass is legal iff
       `position_legal_moves(p) == 0`) and never reaches
       `move_as_bitboard(64)`; `move_as_bitboard` gained a comment
       documenting the 64-66 -> 0 wrap. Behavior is unchanged (for
       codes 0-63 the old pass branch could never trigger since
       `1 << n` is never 0), so no test change was needed: the existing
       pins (pass legal iff no legal moves, Move(65)/Move(66) illegal,
       move_as_bitboard 64/65/66 -> 0) all pass as before. Suite
       GREEN: 167/0/12.

D-019 | 2026-08-27 | pattern.py: review-only session, all fixes deferred
       to a dedicated session; test_pattern.py analysis deferred too
       | Roberto's explicit scope for the pattern module session:
       (1) document pattern.py (docs/src/twolm/pattern.md, D-007 mirror),
       (2) list the defects in code and docs but apply NO changes —
       "Poi in una altra sessione dedicata quando questo lavoro e'
       completato, faremo le changes ed i fix necessari", (3) test_pattern.py
       is out of scope for analysis entirely ("quella la faremo
       prossimamente in una sessione dedicata") — running its suite is
       fine, analyzing it is not. Result: docs/src/twolm/pattern.md
       written (Pattern, PatternSet, standalone functions, 8 real issues
       R1-R8 + minor list + conventions); pattern.py and test_pattern.py
       untouched (AGENTS.md rule 3). One flagged item needs a design
       decision when the fix session happens: R1 (the principal-mask
       rule is not a unique representative — the min-BSR check accepts
       any orbit member tied for minimal BSR; verified counterexample
       X = 0xFF000000000001FF / Y = 0xFF000000000080FF = fvert(X), both
       accepted). Options on the table: (a) unique representative =
       numerically minimum transformed mask, or (b) keep BSR-first and
       add a value tie-break (min of (BSR, value)); either way a
       regression test. Note for the fix session: R1 is the only
       non-mechanical issue; R2-R8 and the minor list are mechanical
       (doc corrections, dead import, __all__ entry, endianness).

D-020 | 2026-08-27 | R1 resolved: principal mask = numerically lowest
       orbit mask (option (a))
       | Roberto's decision after the R1 discussion: the intent is a
       bijective correspondence between the set of masks and an
       orderable set — the natural numbers; a mask is a 64-bit integer,
       so the orbit minimum is a well-defined unique representative.
       BSR was a "more computer-science-y" surrogate and is not a total
       order (all 4-corner masks tie at BSR 63 under all 8 transforms).
       Implementation (explicit "Fai la modifica ora"):
       `_check_mask_is_principal` (pattern.py L314-339) now scans t1..t7
       for a numerically lower mask, reporting the first offender;
       docstring states the new rule (doc follows code, D-016
       precedent). Regression test:
       test_init_rejects_non_minimum_orbit_masks (test_pattern.py) — 4
       corners + b1 = 0x8100000000000083 accepted (n_instances=8,
       n_stabilizers=1), the other 7 orbit members (incl. +a2, +h2)
       rejected with "not principal". Verification: 29 sample patterns
       still construct; pattern suite 50/0/3, discover 243/0/15, PERF=1
       50+193 — all GREEN. pattern.md updated (architecture rule, R1
       marked RESOLVED with full history, verdict).

D-021 | 2026-08-27 | R2-R7 resolved: docstring/hygiene fixes (code
       behavior untouched)
       | Fix campaign 2026-08-27: the user approved each item explicitly,
       one at a time. R2: docstring invariant
       len(unique_symmetric_instance_indexes) = n_stabilizers - 1 is
       false (DOTA1 counterexample: n_stabilizers=2, list empty); the
       docstring now states the count is the number of stabilizer
       elements that induce a non-identity permutation on the pattern
       squares. R3: squares docstring "descending priority" -> "ascending
       board order (A1 first)". R4: PatternSet docstring "SHA256" ->
       "SHA3-256" (code computes sha3_256; doc follows code). R5: unused
       `import time` removed. R6: PatternType added to __all__ (star
       import now exports it, verified). R7: stale comment
       "compute_indexes_on_board" -> "compute_indexes_on_position and the
       PatternSet pipeline". No behavior change; full suite stays GREEN.

D-022 | 2026-08-27 | R8 closed: no code change; engine documented as
       little-endian-only
       | User rejected the proposed big-endian hash fix: the legacy
       engine (including the legal-moves and moves pipelines) is written
       and tested for little-endian processors only, and all bit/byte
       manipulation is untested on non-LE platforms. Instead of changing
       the hash serialization, a "Platform assumption: little-endian
       only" section was added to docs/src/twolm/pattern.md and
       docs/src/twolm/board.md.

D-023 | 2026-08-27 | Pattern.__init__ moved to strict @validate_call
       (pattern minor sweep, item #6).
       | User approved converting the hand-written isinstance checks in
       Pattern.__init__ to @validate_call, with a hard requirement: only
       np.uint64 (Bitboard) scalars are valid masks for a pattern, and
       Pattern('ELLE', 107) (Python int) must be rejected. Implemented as
       @validate_call(config=ConfigDict(strict=True,
       arbitrary_types_allowed=True)) — arbitrary_types_allowed is
       required because pydantic 2.13 has no native numpy-scalar schema in
       strict mode (schema generation fails without it); strict keeps
       isinstance semantics: no coercion of ints/floats to str for name,
       no coercion of ints to np.uint64 for mask. The manual TypeError
       checks were removed. Error type at the constructor changed from
       TypeError to ValidationError (accepted by the user; other classes
       pulled into the project later will be fixed if they break). The
       two tests pinning TypeError
       (test_init_invalid_type_arg_1/2_raises_assertion) were updated to
       expect ValidationError. All Pattern(...) construction sites audited:
       every real mask is Bitboard(...) (np.uint64). Pattern suite stays
       GREEN (50 tests, 3 PERF skips).

D-024 | 2026-08-27 | PatternSet.names/masks converted from methods to
       @property (pattern minor sweep, item #15).
       | API inconsistency: PatternSet exposed name/patterns/hash as
       attributes but names()/masks() as methods. Converted both to
       @property so the whole public surface is attribute-style; class
       docstring reorganized accordingly (names/masks now under
       Attributes, documented as derived from patterns). Only two call
       sites exist in this workspace — test_pattern.py
       test_names/test_masks — updated to parenthesis-free access.
       KNOWN PENDING FOLLOW-UP (flagged by the user, to be tracked): the
       original 2008 repo may have legacy callers using the old
       .names()/.masks() method syntax; those call sites must be updated
       to property access when that file is migrated into twolm (tracked
       as I-006 in notes/ideas.md). Suite stays GREEN (50 tests, 3 PERF
       skips).

D-025 | 2026-08-27 | Pattern indexing APIs keep the collision-check
       precondition on the caller (pattern minor sweep, item #19) —
       leave-as-is decision.
       | compute_indexes_on_position (Pattern) and
       compute_principal_indexes (PatternSet) do NOT call
       position_check_collisions internally. User approved option (b):
       the "caller validates" contract is already expressed by the
       pattern tests (which call position_check_collisions before the
       indexing API) and by the upstream engine, which validates
       positions before any indexing call; duplicating the check on the
       hot path was rejected as repeated work. The precondition is now
       documented in both docstrings (Precondition: positions must be
       collision-free, e.g. via board.position_check_collisions). No
       code behavior change.

D-026 | 2026-08-27 | Pattern.__repr__ golden pinned in test_pattern.py
       (test_pattern fix campaign, P0 item 1/3, defect T8/#16).
       | __repr__ (pattern.py, added by the 2026-08-27 minor sweep)
       shipped with zero test coverage. Added TestPattern.test_repr
       with three goldens (ELLE, EDGE, SNAKE) pinning the exact
       one-line format: `Pattern(name='<NAME>', mask=0x<16-digit
       lowercase hex>)` — the same info as the first line of print().
       EDGE pins lowercase 'ff', SNAKE pins 'c' (the only hex letters
       among the sample-set principal masks); all three cover the 16-
       digit zero padding and the name repr form. Also pins str(p) ==
       repr(p): Pattern defines no __str__ (verified: '__str__' not in
       type(p).__dict__), so str() falls back to __repr__; a future
       divergent __str__ would break the test. Test file only,
       pattern.py untouched. Goldens verified read-only against the
       live behavior before approval. Suite grew 50 -> 51 tests,
       GREEN 51/0/3.

D-027 | 2026-08-27 | Empty-PatternSet ValueError test pinned in
       test_pattern.py (test_pattern fix campaign, P0 item 2/3, defect
       T8/#17).
       | The fail-fast `if not patterns: raise ValueError('Patterns
       list cannot be empty')` check (PatternSet.__init__, added by the
       2026-08-27 minor sweep) shipped with no test coverage. Added
       TestPatternSet.test_init_raises_value_error_for_empty_pattern_
       list: PatternSet('EmptySet', []) must raise ValueError with a
       message containing 'cannot be empty'. Style matches the sibling
       duplicate names/masks ValueError tests (assertRaises +
       assertIn). The pydantic constructor accepts an empty list (a
       valid List[Pattern]); the manual check is what raises. Verified
       read-only against the live behavior before approval. Test file
       only, pattern.py untouched. The stale TypeError Raises lines in
       the constructor docstring remain the known deferred item (M1,
       P2). Suite grew 51 -> 52 tests, GREEN 52/0/3.

D-028 | 2026-08-27 | Empty-mask ValueError test pinned in
       test_pattern.py (test_pattern fix campaign, P0 item 3/3, defect
       T8/#18).
       | The fail-fast `if self.n_squares == 0: raise ValueError(...)`
       check (Pattern.__init__, L298-299, added by the 2026-08-27 minor
       sweep) shipped with no test coverage. Added
       TestPattern.test_init_raises_value_error_for_empty_mask right
       after test_init_invalid_number_of_squares, so the two
       constructor guards (n_squares == 0 and n_squares > 18) sit side
       by side: Pattern('EMPTY', Bitboard(0x0)) must raise ValueError
       with a message containing 'empty mask' (the name is interpolated
       by the code and is not part of the pinned contract). The check
       fires before any derived field is computed (tmasks et al. never
       run on a zero mask). Verified read-only against the live
       behavior before approval. Test file only, pattern.py untouched.
       This closes P0: all three shipped-but-uncovered minor-sweep
       paths (#16, #17, #18) now have tests. Suite grew 52 -> 53
       tests, GREEN 53/0/3. P0 batch committed as 6da0803.

D-029 | 2026-08-27 | Multi-position row-independence test for
       Pattern.compute_indexes_on_position (test_pattern fix campaign,
       P1 item 1/3, defect T9a).
       | All array-input tests so far fed uniform np.full tiles, so a
       row-mixing bug in the 2D kernel path would be invisible. Added
       TestPatternComputeIndexes.test_compute_indexes_on_position_
       multiple_positions: EDGE (4 unique instances) pattern over 3
       distinct collision-free positions (empty; mover on A1; mover
       A1 + opponent H1). Output column j is the base-3 configuration
       of row 1 read through the j-th anti-transformation
       (unique_mask_indexes [0,1,2,3] = identity, ro270, ro180,
       ro090); digits 0 = empty, 1 = mover, 2 = opponent; square k
       (ascending A1..H1) contributes digit * 3^k. Goldens
       hand-derived from D8 geometry and the kernel digit convention,
       then verified against the live output ([[0,0,0,0],
       [1,0,0,2187], [4375,2,0,2187]]): the test pins all three digit
       values, all four anti-orientations, the base-3 digit order
       (3^7 = 2187) and row independence. position_check_collisions
       is called on the array input before indexing (D-025 caller
       precondition). Module fixtures sqa8/sqh1 deliberately NOT used:
       their names are swapped w.r.t. the canonical layout (sqa8 =
       0x80 = H1, sqh1 = 0x1000000000000000 = A8) — logged as new
       defect T17 (hygiene, P2 candidate; their only use at the
       Cayley-table inputs is identity-agnostic). Test file only.
       Suite grew 53 -> 54 tests, GREEN 54/0/3.

D-030 | 2026-08-27 | Multi-position row-independence test for
       PatternSet.compute_principal_indexes (test_pattern fix
       campaign, P1 item 2/3, defect T9b).
       | test_large_set feeds uniform np.full tiles and only checks
       row 0 (rows 1..N-1 never verified), so a row-mixing bug in
       the set-level kernel would be invisible. Added
       TestPatternSetComputePrincipalIndexes.test_compute_principal_
       indexes_multiple_positions: single-pattern set (EDGE, 4 groups
       -> 4 output columns, no multi-pattern layout ambiguity;
       col_offsets already pinned by test_large_set's J=49
       attribution) over 4 distinct collision-free positions. Each
       output column g is the principal index of that unique-mask
       instance's configuration — the min over the two stabilizer
       elements mapping the pattern onto that unique mask (g0 =
       min(ro000, fvert) row 1; g1 = min(ro090, fh1a8) col h; g2 =
       min(ro180, fhori) row 8; g3 = min(ro270, fa1h8) col a); digits
       0/1/2, square k contributes digit*3^k. Goldens hand-derived
       and verified against the live output (4/4 rows MATCH):
       [[0,0,0,0], [1,0,0,1], [2189,2,0,1], [1,0,1,2188]]. NOTE: the
       first golden attempt failed because of a bug in the scratch
       diagnostic (mislabeled the four reflection anti-columns);
       reconstructing the per-slot base-3 indexes via _pack_bb
       proved the kernel grouping is CORRECT (stabilizer min,
       consistent with compute_principal_index_dict semantics and the
       re-derived large-set goldens) — no code defect. Pins the
       stabilizer min (row 2: 1 vs 2187), the opponent digit (row 3:
       2189 = min(4375, 2189)), a symmetric configuration (row 4:
       g3 = min(2188, 2188)) and row independence (4 distinct rows).
       Test file only. Suite grew 54 -> 55 tests, GREEN 55/0/3.

D-031 | 2026-08-27 | EDGE 6561-entry principal dict pinned directly
       (test_pattern fix campaign, P1 item 3/3, defect T10).
       | Added TestPatternComputePrincipalIndexDict.
       test_edge_pattern_compute_principal_index_dict. Instead of a
       6561-entry literal, pins the full non-circular
       specification: EDGE has one non-identity stabilizer element
       (fvert = base-3 digit reversal), so dict[c] = min(c, flip(c))
       for all 6561 entries, plus length (6561), unique-principal
       count (3321 = (6561+81)/2, Burnside with 81 fixed
       configurations) and five hand-derived spot values (0, 1,
       2187->1, 27, 4375->2189). All verified read-only before
       approval. Also logged as T18 (sharp edge, no code action):
       Pattern.n_squares is np.uint8, so 3 ** p.n_squares overflows
       (6561 wraps to 161) for patterns with >= 7 squares; the
       production code already casts to int where needed
       (compute_principal_index_dict), external expressions must
       cast too. Test file only. Suite grew 55 -> 56 tests, GREEN
       56/0/3. P1 batch (D-029/D-030/D-031) committed together.

D-032 | 2026-08-28 | New Pattern attributes n_invariant_configs and
       n_unique_configs (Burnside counts; user-requested feature,
       approved with CORE added to the golden test).
       | Study (read-only, pre-approval): G' = {id} plus the distinct
       non-identity permutations induced by symmetry_fs on the S
       pattern squares (|G'| = 1 + len(symmetry_fs) exactly — the
       constructor's unique_symmetric_instance_indexes already
       dedups identical induced permutations and discards the
       trivial action; hence n_stabilizers != |G'| in general:
       DIAG8 4 vs 2, DOTA1/TWOND 2 vs 1). Formulas: n_invariant =
       3^B (B = number of G'-orbits on the squares) and n_unique =
       (1/|G'|) * sum_g 3^{c(g)} (Burnside on the 3^S configurations;
       c(g) = number of cycles of g). Verified on all 29 sample
       patterns against independent ground truth: n_invariant by
       full enumeration of the 3^S configurations (vectorized numpy,
       no Burnside used); n_unique against the production
       principal_index_count — 29/29 match (EDGE 81/3321, CORE 3/21,
       FOURC 3/21, 2X6COR 531441/531441).
       | Implementation: _compute_symmetry_burnside_counts() called
       in __init__ right after symmetry_fs/anti_symmetry_fs; both
       attributes are plain Python int (avoids the T18 np.uint8
       3**S overflow). Class docstring extended (section 5); mirror
       doc (docs/src/twolm/pattern.md) extended with a "Burnside
       counts (D-032)" paragraph. Tests: test_burnside_counts_golden
       (all 29 sample patterns, incl. CORE 3/21 per user) +
       test_burnside_counts_invariants (1 <= n_inv <= n_uni <=
       n_configurations; equality with 3^S when symmetry_fs is
       empty). Suite grew 56 -> 58 tests, GREEN 58/0/3.

D-033 | 2026-08-28 | P2 hygiene batch for test_pattern.py (T1-T7,
       T15, T16; each item approved one at a time, single batch
       commit like P0/P1).
       | T1: the test_init tautology assertEqual(p, p) replaced with
       real assertions (name, mask, n_squares, n_configurations for
       ELLE and EDGE; values verified live: ELLE 4/81, EDGE 8/6561).
       T2: the dead if False: debug block in test_one_record
       replaced by print-on-failure (Roberto's proposal: the block
       is development diagnostic, keep it but print only on
       failure): the assertion wrapped in try/except AssertionError,
       the original debug prints verbatim inside the handler, bare
       raise. Both branches verified live (failure: board + pattern
       table + indexes + shape printed, exception re-raised;
       success: silent). This uncovered NEW DEFECT T19: the block
       referenced position_print, which was never imported (dead
       code, so the NameError never fired) — added to the
       twolm.board import list as part of T2.
       T3: removed the 7 dead module-level ar_* fixtures
       (ar_reflection_h/v/h1a8/a1h8, ar_rotate_180/90c/90a); ar
       kept (used by the Cayley-table test). The same-named
       fixtures in test_board.py are that module's own, unaffected.
       T4: renamed the 5 stale tests ..._raises_assertion to
       ..._raises_validation_error (all 5 already asserted
       ValidationError; names stale since the D-023 strict
       constructor).
       T5: header grammar fix (L30) + typo "environmeant" (L34).
       Reported: test_board.py carries the same two nits (out of
       scope for this file, left for Roberto).
       T6: renamed the TestCase namedtuple to SymmetryCase (class
       name + type name; 29 test_data rows) — it shadowed
       unittest.TestCase in the class body.
       T7: test_mdp_csv_file_with_empty_list now asserts the single
       write is the CSV header itself (header verified byte-for-
       byte against mdp_csv_file, pattern.py L279-286).
       T15: the two mocked mdp_record strings in
       TestPatternMdpCsvFile.setUp replaced with the real
       mdp_record() output of EDGE and CORNER (live-verified; the
       old ones used fake-format values: "0xff" vs 16-hex, and
       "CORNER,0x0f,4,81,1,1" vs real 0x70707/9/19683/4/2).
       T16: removed the no-op tearDown (pass) from TestPatternPack.
       Test file only; no behavior change. Suite 58 tests, GREEN
       58/0/3 (test count unchanged by this batch).

D-034 | 2026-08-28 | P2 breadth batch for test_pattern.py (T11,
       T12, T13, T14 + T17 fixture fix; each item approved one at a
       time, single batch commit like P0/P1/hygiene).
       | T17 (carried from the hygiene list): sqa8/sqh1 fixture
       values corrected to the real board bit layout (sqa8 =
       0x0100000000000000 = A8 = bit 56; sqh1 = 0x0000000000000080
       = H1 = bit 7); the old values were the swapped pair.
       T11: both PatternSet.print_* tests now pin the expected hash
       5e5abf79c30a75f13b296efff45c78554924f772f94f74a311025c425ac9d10b
       (live-computed from the ELLE+SNAKE+EDGE masks) instead of
       comparing the output against pattern_set.hash (self-
       comparison).
       T12: new TestPatternType class (3 tests): 12-member closed set
       with tuple/list roundtrip through from_fingerprint; unknown
       8-tuple and 2-tuple return None; .data dict keys plus the
       orbit-stabilizer identity n_stabilizers == 8 // n_instances
       verified for all 12 members, with full-data pins for
       TYPE_2/TYPE_9/TYPE_3D. Live verification exposed a doc
       miscount ("11 members", 5 spots in docs/src/twolm/pattern.md)
       corrected to 12 — all 12 types are used by the 29 samples.
       T13: three mdp_record goldens added (SNAKE, CORE, DIAG8)
       mirroring the existing EDGE one, live-captured strings.
       T14: position_check_collisions(positions) added to
       test_one_record and test_large_set, making the D-025 caller-
       checks-collisions contract consistent at set level (pattern
       level already did this; PERF tests deliberately left
       unchecked, as at pattern level).
       Suite grew 58 -> 64 tests, GREEN 64/0/3. P2 campaign closed:
       T18 stays noted-only (np.uint8 n_squares — any 3**n_squares
       must cast to int; no code action), M1 (stale PatternSet
       Raises docstring) stays deferred pending Roberto's go-ahead.

D-035 | 2026-08-28 | mobility.py fix batch R1-R6 (each item approved
       one at a time, single batch commit, D-019 pattern).
       | R1: Mobility class docstring rewritten (feature index
       formula, n_configurations = k + a + 1 as the count of
       DISTINCT index values / feature-table size, n_instances
       note); MobilitySet docstring fixed ("mast" typo, "a
       ascending" grammar, sorted-order clause). Doc-only.
       R2: compute_indexes docstring now states the full contract:
       formula, args/returns, and the column-order rule (columns
       follow the set's sorted (mask, amask) order, same as
       names/masks, NOT the caller's insertion order). Doc-only.
       R3 (Roberto's design call, option b): popcount64 removed
       from __all__ (test/inspection helper, not public API; the
       upcoming engine "may not be Python, we'll see"); direct
       import in the test file unaffected.
       R4: dead imports bitboard_transformations and square_from_str
       removed.
       R5: names()/masks() converted to @property (D-024 alignment
       with PatternSet); __repr__ added to Mobility and
       MobilitySet (pattern-style one-liner); 4 test call-sites
       updated; docstring references updated.
       R6: n_instances = 1 left as-is (decision): mobility is a
       scalar feature — the index is a single uint32 computed
       directly from the (mask, amask) pair, no family of symmetric
       instances with separate tables as in Pattern; doc note
       shipped with R1.
       Suite 23/0/1 GREEN throughout (no behavior change).

D-036 | 2026-08-28 | mobility minor notes M1-M5 disposition (per
       Roberto, item by item).
       | M1: glossary shipped in the Mobility class docstring —
       LMC = Legal Move Count, ALMC = Anti Legal Move Count, DLMC
       = Difference Legal Move Count (expansions confirmed by
       Roberto from the 2008 program). Doc-only.
       M2 (name padding in print): left as-is, cosmetic.
       M3 (empty MobilitySet accepted, diverges from PatternSet
       fail-fast): left as-is ("lasciamo così") — deliberate and
       tested behaviour.
       M4: analysis text corrected — the doc claimed the board
       suite PERF tests "carry ±30% gates"; on Roberto's challenge
       and re-verification, NO suite in this repo has performance
       gates: every PERF test is print-only and asserts output
       correctness only. The ±30% figure is the campaign
       comparison discipline (within-campaign deltas are noise;
       never compare across sessions/machines), not a test gate.
       Mobility PERF test stays print-only (consistent).
       M5 (kernel per-element UFunc call): left as-is, observation
       only — any change would be PERF-gated engine work.

D-037 | 2026-08-28 | test_mobility.py fix campaign T1-T9 (each item
       approved one at a time, single batch commit, D-019 pattern).
       | P0: T8 — golden tests added for the R5-shipped __repr__
       pair (Mobility: LMC full-board + CORNERS partial mask;
       MobilitySet: standard triple with the pinned hash literal
       2e5535935d46d82a941ef87d43d22562735db9b6bf41db51d6eb6a8f21208a94).
       P1: T7 — test_compute_indexes_multi_position: 2 distinct
       positions (the golden one + the underflow one), per-row
       expected values [[53,13,66],[63,0,63]] in sorted column
       order; row independence of the (N) -> (N, L) kernel.
       P2: T1 — TestMobilitySet.test_init dead if-False block
       removed, real assertions added (name, length, sorted names);
       T2 — the 3 "raises_assertion" tests renamed to
       "raises_validation_error"; T3+T4 — standard-set hash
       literal pinned in test_hash_calculation_verification
       (double assert: byte formula and object) and
       test_print_summary (self-comparisons eliminated); T5 —
       header grammar ("How to run the mobility module unit
       tests."); T6 — dead imports shutil/tempfile/legal_moves
       removed (the import-time trailing space noted, left as-is);
       T9 (approved) — native assertEqual with line numbers
       replacing the print-on-failure idiom in test_popcount64.
       Suite grew 23 -> 26 tests, GREEN 26/0/1. test_mobility
       campaign CLOSED.

D-038 | 2026-08-28 | feature.py R1-R4 fix batch (all items approved
       by Roberto in one go, single batch commit; doc/hygiene only,
       no behavior change):
       R1 - FeatureSet class docstring hash description corrected:
       it is sha3_256 (not "SHA256"), over b'INTERCEPT' (if
       intercept present) + the mset then pset hash hex strings
       (if present); child hash values, not raw masks; name
       excluded.
       R2 - compute_indexes docstring now carries the verified
       Column contract: column 0 = intercept (constant 0); mobility
       columns in the MobilitySet's sorted (mask, amask) order;
       pattern blocks in the PatternSet's sorted mask order, each
       pattern expanded into n_instances columns in its unique-mask
       first-seen (D8 instance) order; columns follow the child
       sets' sorted storage order, not caller insertion order (same
       treatment as mobility R2).
       R3 - FeatureSet.__init__ docstring rewritten: real
       parameters (name, intercept, mset, pset; the stale "list of
       features" phrase removed), features-building order stated,
       Raises clause added (ValueError, wrong intercept category).
       R4 - dead imports removed from the typing import: TypeAlias,
       List, Tuple, Annotated (List/Tuple appeared only in
       docstring prose). The Mobility/Pattern imports stay: they
       are load-bearing for @validate_call annotation resolution
       under `from __future__ import annotations`.
       Suite 13/0/1 GREEN; scratch/verify_feature.py ALL CHECKS
       PASSED. Minor M1-M4 noted in the doc, disposition pending.

D-039 | 2026-08-28 | feature.py M1 disposed (approved by Roberto,
       one at a time): the dead `len(self.pset.patterns) > 0`
       clause removed from the pset branch of compute_indexes'
       active-blocks loop (behaviour identical — an empty
       PatternSet is impossible, PatternSet fail-fast; an empty
       MobilitySet is legal and its (N, 0) block is hstack-safe).
       Now symmetric with the plain `if self.mset:` branch. Suite
       13/0/1 GREEN; verifier all green. M2-M4 disposition
       pending.

D-040 | 2026-08-28 | feature.py M2 disposed (approved by Roberto,
       one at a time): the two unused `f` prefixes removed from
       print_summary's placeholder-less lines ("Intercept is
       present." / "Intercept is None."); cosmetic only, output
       identical. Suite 13/0/1 GREEN (print_summary goldens
       unchanged). M3-M4 disposition pending.

D-041 | 2026-08-28 | feature.py M3 disposed (Roberto chose option
       a): FeatureSet keeps NO column-labelling helper — left
       as-is. Rationale: it is an engine-side need (the pipeline's
       table builders), not a module requirement; the helper
       design (each pattern occupies n_instances D8-instance
       columns, so column-level labelling needs an instance-aware
       shape) is deferred until the pipeline module that labels
       columns arrives. Follow-up registered as I-007 in
       notes/ideas.md. No code change.

D-042 | 2026-08-28 | feature.py M4 disposed (approved by Roberto,
       one at a time): Feature.__new__ docstring rewritten from
       "Blocks the client to create new instances of feature via
       the Feature() call." to "Blocks direct instantiation of
       Feature: calling Feature() always raises RuntimeError. Use
       the factory methods instead (e.g.
       Feature.new_from_pattern())." Doc-only, no behaviour
       change. Suite 13/0/1 GREEN. All four feature minors (M1-M4)
       now disposed: D-039 (M1 applied), D-040 (M2 applied),
       D-041 (M3 left as-is, I-007), D-042 (M4 applied).

D-043 | 2026-08-28 | test_feature.py T campaign, item T6 (P1,
       approved by Roberto, one at a time): three new tests in
       TestFeatureSet cover the partial-None FeatureSet
       constructions — test_init_intercept_only (hash
       ab7c1b64b96fe0fb85350613ac69b258a4442f56c390d7f69e5a070611e14b12
       = sha3_256(b'INTERCEPT'), features ['INTERCEPT'],
       n_instances 1, compute_indexes (2,1) zeros),
       test_init_mobility_only (hash
       239e4df42493da52f536f6b3017712a18da05fa48925b76d12adc688d008ecf3
       = sha3_256(mset hash hex), features ['ALMC','LMC','DLMC'],
       n_instances 3, block == mset.compute_indexes),
       test_init_pattern_only (hash
       63f0a6c8b2355baa8e1f6fb733454c8d4f1c0d4cdc9a0270eb45dcf2400f5668
       = sha3_256(pset hash hex), 13 names in sorted order,
       n_instances 49, block == pset.compute_principal_indexes).
       All three hash literals re-derived from scratch (genuine
       goldens, no self-comparison). Suite 13 -> 16 run tests,
       GREEN 16/0/1. T1-T5, T7-T9 pending.

D-044 | 2026-08-29 | test_feature.py T campaign, item T1 (P2,
       approved by Roberto, one at a time): the dead `if False:`
       debug block (16 unreachable lines) removed from
       TestFeatureSetComputeIndexes.test_compute_indexes. It
       referenced position_print (never imported — a latent
       NameError if the block were ever re-activated) and the
       undefined name `indexes`; the live 3x10 golden assertion is
       unchanged. Suite 16/0/1 GREEN (test count unchanged: 16 run
       + 1 PERF skip). T2-T5, T7-T9 pending.

D-045 | 2026-08-29 | test_feature.py T campaign, item T2 (P2,
       approved by Roberto, one at a time): the six dead imports
       removed — `numpy.typing as npt` (L52),
       `numpy.testing as nptest` (L53),
       `from typing import Callable, TypeAlias, List` (L59), bare
       `import pydantic` (L61) — plus one consequent blank line.
       Each name occurs exactly once (its import line);
       `from pydantic import ValidationError` stays (used). Pure
       import hygiene, no behaviour change. Suite 16/0/1 GREEN.
       T3-T5, T7-T9 pending.

D-046 | 2026-08-29 | test_feature.py T campaign, item T3 (P2,
       approved by Roberto, one at a time): header grammar fixed,
       "How to use the unit tests feature module." -> "How to run
       the feature module unit tests." (L30). Comment-only, no
       behaviour change. Suite 16/0/1 GREEN. The "environmeant"
       typo at L34 is T4, left to Roberto's call (repo-consistency
       nit, same as test_board.py). T4-T5, T7-T9 pending.

D-047 | 2026-08-29 | test_feature.py T campaign, item T5 (P2,
       approved by Roberto, one at a time): explicit names-order
       assertion added to TestFeatureSet.test_init —
       `expected_names` = ['INTERCEPT', 'ALMC', 'LMC', 'DLMC',
       '2X5COR', 'XEDGE', 'R2', 'CORNER', 'R3', 'DIAG4', 'R4',
       'DIAG5', 'CORE', 'RCT2X4', 'DIAG6', 'DIAG7', 'DIAG8']
       asserted against [f.name for f in feature_set.features], in
       the same computed/expected style as the n_instances block.
       The 17-value n_instances list already pinned the order
       implicitly (the 8/1/2 values sit in the sorted-order
       slots); this makes the column/feature order contract
       (feature.md R2/D-038) directly asserted. Suite 16/0/1
       GREEN (assertion passes; no behaviour change). T4, T7-T9
       pending.

D-048 | 2026-08-29 | test_feature.py T campaign, item T7 (P2,
       approved by Roberto, one at a time): three new TestFeature
       tests pinning the auto-generated surface — test_repr_golden
       (the three factory reprs, incl. the mobility
       n_configurations=np.uint8(65) quirk vs the int 6561 for
       patterns), test_eq (field-wise dataclass eq with ref
       compared by OBJECT IDENTITY: Mobility and Pattern define no
       value __eq__, so distinct field-identical refs make their
       Features unequal; reflexive equality holds),
       test_unhashable (@dataclass with eq and not frozen →
       __hash__ = None, TypeError on hash()). All literals
       verified live before committing. This documents the current
       semantics as a design property of Mobility/Pattern, not a
       feature.py defect; value equality (if ever wanted) is a
       mobility.py/pattern.py change, out of the T campaign. Suite
       17 -> 20 tests (19 run + 1 PERF), GREEN 19/0/1. T4, T9
       pending.

D-049 | 2026-08-29 | test_feature.py T campaign, item T9 (P2,
       approved by Roberto, one at a time): the 11 spot-check
       assertIn in test_print_summary replaced by a single
       assertEqual against the full 38-line output captured live
       from the standard fixture (header with f566… hash,
       intercept-present line, MobilitySet line with 2e55… hash +
       3 sorted mobility rows, PatternSet line with ff97… hash +
       13 sorted-mask pattern rows, feature-table header, 17
       feature rows). Pins hex widths, `10s` name padding,
       `:10,d` thousands separators (59,049 / 19,683 / 6,561 /
       2,187), the np.uint8 mobility n_configurations rendering,
       and the IntEnum-as-int 0/1/2 category rendering end to
       end. Suite 19/0/1 GREEN. T4 ("environmeant" typo) remains
       Roberto's call; T8 (import time trailing spaces) left
       as-is.

D-050 | 2026-08-29 | test_feature.py T campaign, item T4 (P2,
       approved by Roberto — option (a) — one at a time): the
       "environmeant" header typo fixed in BOTH test files
       (test_feature.py L34 and test_board.py L34: "Activate the
       environment.") — Roberto's repo-consistency call; the
       same nit had been reported on test_board.py's header and
       left open. Comment-only; suites unchanged: test_feature
       19/0/1, test_board 193/0/12. This closes the test_feature
       T campaign: T6 (D-043), T1 (D-044), T2 (D-045), T3
       (D-046), T5 (D-047), T7 (D-048), T9 (D-049), T4 (D-050)
       all applied; T8 (import time trailing spaces) left as-is
       per the test_mobility precedent. Feature module fully done:
       analysis + R1-R4 (D-038) + M1-M4 (D-039..D-042) + test
       campaign (D-043..D-050), suite 19/0/1 GREEN.

D-051 | 2026-08-29 | binio analysis complete: 15 verified facts (V1-V15, 0
       mismatches), 4 defects T1-T4 documented. Two test files:
       test_binio.py (41 tests) + test_usage_binio.py (3 tests) = 44/0/0 GREEN,
       no PERF gates. Analysis docs: docs/src/twolm/binio.md and
       docs/src/twolm/test/test_binio.md. T1-T4 fix batch applied the same
       day: T1 = lz4 added to pyproject.toml, T2 = dead
       `from pathlib import Path` removed, T3 = "Aauthor" -> "Author",
       T4 = test_unknown_type_code_raises added to ArrayTest. Suite
       44 -> 45/0/0 GREEN. BINIO MODULE DONE.

D-052 | 2026-08-29 | regab analysis complete: 5 verified facts (V1-V5, 0
       mismatches, incl. sha3_256 golden b507cd34...), 7 defects T1-T7
       documented. test_regab.py 33 tests, all requiring live PostgreSQL.
       Analysis docs: docs/src/twolm/regab.md and
       docs/src/twolm/test/test_regab.md. T1-T7 fix batch applied the same
       day: T1 = "Aauthor" -> "Author", T2 = dead Callable/Type/Self
       typing imports removed, T3 = psycopg2/pandas/python-dotenv added to
       pyproject.toml, T4 = _validate_db_fields DB query deferred (only when
       colnames needed), T5 = dead test imports removed, T6 =
       SKIP_REGAB_DB=1 env gate added to BaseTestCase.setUp, T7 = SQL
       injection guard on where clause (_validate_where_clause +
       WhereArgument + 4 tests). Suite 33 -> 37/0/0 GREEN.
       REGAB MODULE DONE.

D-053 | 2026-08-29 | opt_lbfgs analysis complete: 5 verified facts (V1-V5,
       0 mismatches, incl. two-loop identity + Rosenbrock 5-start), 7
       defects T1-T7 documented. Analysis docs: docs/src/twolm/opt_lbfgs.md
       and docs/src/twolm/test/test_opt_lbfgs.md. T1-T7 fix batch + 9 new
       tests applied the same day: T1 = RuntimeException -> RuntimeError
       (hard bug), T2 = CURVATURE_THRESHOLD used in curvature check, T3 =
       low_progres_count -> low_progress_count, T4 =
       _hermite_cubic_interp_min returns None when neither stationary point
       is a minimum, T5 = save_fn type hint + docstring -> 7 params,
       T6 = "percentage" -> "fractional", T7 = d param removed from test
       method. New tests: TestLBFGSInputValidation (3), TestFixedSizeMaxList
       (4, incl. T1 regression), TestTwoLoopRecursion (2). Suite 4 -> 13/0/0
       GREEN. OPT_LBFGS MODULE DONE.

D-054 | 2026-08-29 | Rigid per-section format for NOTES.md + the
        session journal, rule written at the top of each file (the
        journal's block was later moved to notes/log_rules.md): fixed
        seven-section order for NOTES.md; suite numbers pinned to
        total/failures/skipped (= unittest "Ran N"); one
        "## YYYY-MM-DD — session N (title)" per session with a GLOBAL
        monotonically increasing N (never reset), mandatory title,
        0/2 bullet indentation, "Session closed (Roberto)." bullets.
        One-off renumbering of the historical per-day labels (08-26
        "session 1" → 3; 08-27 "1-5" → 4-8; nested "Session 11-14"
        bullets → own sections 14-17); cross-refs renumbered to match
        (ideas.md, 6 docs headers).
        | Roberto's report: format drift in NOTES/log had caused
        repeated update mistakes. A mechanical format with the rule
        written in place makes future updates deterministic and
        verifiable. The rewrite was verified against the live suites
        (398 tests GREEN).

D-055 | 2026-08-29 | Session journal rotates into volumes: log.md →
        log_000.md (sessions 1-17 at rotation time) + log_001.md, ...;
        a volume holds at most 25 sessions or 2000 lines (whichever
        first); rotation only at session boundaries (a volume jump
        never cuts a session); the global session counter never
        restarts across volumes; format rules consolidated in
        notes/log_rules.md (single source of truth); each volume
        starts with H1 "volume 00N (sessions X–...)" + one pointer
        line.
        | Roberto's proposal, refined per agent opinion: unbounded
        growth (≈50 lines/session) would make the journal hard to read
        and costly for agent context; closed volumes are natural era
        boundaries and enforce immutability of history; a
        session-count trigger is deterministic (line counts drift with
        re-wrapping), the line cap is a backstop.

D-056 | 2026-08-29 | state_machine.py + test_state_machine.py
        analyzed (session 19, review-only so far — no source change):
        suite 13/0/0 GREEN (full discover 411 tests, 52 skipped); 17
        verified facts V1-V17 by an independent 54-check probe (0
        mismatches); findings OPEN pending Roberto's rulings —
        R1 Verbosity.NONE prints ERROR (gate is `relevance >=
        verbosity`; choose `>` semantics vs. renaming levels),
        R2 LogEntry dead class + `logs` annotation lists LogEntry but
        holds plain dicts, R3 worker 0's up()/down() unreachable via
        the public API (step 0 sentinel vs. off-by-one), R4 failure
        leaves current_step at the failed step so a retry of the same
        target silently skips it (document vs. roll back to k-1),
        R5 move_to_last resolves by the last worker's NAME so
        duplicate names land on the first match (fix: use the index);
        12 minors M1-M12 (dead imports Any/datetime, bool accepted as
        index, misleading "for_next_level" names, cosmetics, no
        @validate_call, ...); 11 test defects T1-T11 (three whole
        areas untested: verbosity gate, context injection, display
        methods + move_to_last + edge semantics). Fix campaign to be
        proposed per the rulings.
        | House process (AGENTS.md rules 5-6): mirror docs written
        (docs/src/twolm/state_machine.md + test doc), findings
        registered before any change so each fix can reference its
        ruling; the five R items are behaviour-defining (R1 shifts
        every verbosity level if `>` is chosen; R3/R4 change which
        workers execute; R5 changes the landing step) and touch the
        contract with the not-yet-ported RLM module, so they need
        Roberto's decision instead of agent discretion.

D-057 | 2026-08-29 | state_machine R1 fix + T1 (session 19, fix
        campaign item 1, approved by Roberto): `Verbosity` gains
        `VERY_LOW = 4` and `NONE` moves 4 → 5; the `relevance >=
        verbosity` gate (L201) is UNCHANGED. HIGH/MODERATE/
        STANDARD/LOW behaviour is byte-identical; NONE is now truly
        silent and the old NONE behaviour (ERROR-only) is preserved
        under the honest name VERY_LOW. The only behavioural delta:
        call sites explicitly passing `Verbosity.NONE` now get silence
        instead of ERROR-only (such a site that wants errors visible
        should use VERY_LOW). Docstring documents the gate. Pinned by
        new `TestVerbosityGating` (T1): 6 verbosity × 5 relevance
        gating matrix on captured stdout + enum-values test (suite 13
        -> 15/0/0 GREEN; full discover 413, 52 skipped).
        | Roberto's choice (he has client-code visibility, the agent
        does not): keeping `>=` and values 0-3 means zero behaviour
        change for every existing level, which is safe for the
        unknown client; the alternative (gate `>`) would have shifted
        the effective threshold of all five levels at once.

D-058 | 2026-08-29 | state_machine R2 fix (session 19, fix campaign
        item 2, approved by Roberto): `LogEntry` is now a real typed
        record — `@dataclass(frozen=True)` (L110-120) with the 5
        fields time/step/worker_name/relevance/message, replacing the
        dead `dict` subclass. `log_event` constructs it directly
        (L197-203); `show_event_log` migrated to attribute access
        (output format unchanged); the `logs: List[LogEntry]`
        annotation is now true. Rationale for the dataclass (over
        TypedDict): attribute access is REPL-ergonomic (intended use:
        interactive log search), `dataclasses.asdict()` is the
        one-liner dict form for the planned final pipeline worker
        that dumps the log to file/DB, and frozen guarantees a log
        record is never mutated after creation. No observable
        behaviour change (prints/CSV/history identical); no client
        reads the log today (Roberto). Pinned by new `TestLogEntry`
        (3 tests: typed record + field values, FrozenInstanceError,
        asdict 5-key form); the exception-logging test migrated to
        attribute access. Side effect: the test file's `datetime`
        import is now used by TestLogEntry (T11/M2 resolved). Suite
        15 -> 18/0/0 GREEN; full discover 416, 52 skipped.
        | Roberto: no current log consumers exist; three intended
        uses (inspection clients, REPL search, log-dump worker) all
        favour a typed record; "facciamo come riteniamo meglio, non
        dovrebbe rompersi nulla" — verified: show_event_log output,
        live prints, CSV export all byte-identical.

D-059 | 2026-08-29 | state_machine R3 resolved as SENTINEL
        (session 19, fix campaign item 3, approved by Roberto):
        worker 0 is an intentional sentinel initial state — its
        up()/down() callables are never invoked by the machine by
        design; the domain's first worker (the RLM pipeline's
        'CREATED') runs outside the machine, and the logistic_model
        module (next port) will make the full role explicit. No
        behaviour change: documented in the StateMachine class
        docstring (state model + sentinel, L95-107) and the
        move_to_step docstring (up includes target / down excludes
        target, L249-258); pinned by new
        test_worker_zero_is_sentinel_never_executed (up 0→2 then
        down 2→0 never touches up[0]/down[0]). Suite 18 -> 19/0/0
        GREEN; full discover 417, 52 skipped.
        | Roberto: "Il ruolo vero è 1. È un sentinel. Quando porto
        l'implementazione della PIPELINE ... c'è un modulo
        logistic_model, ti sarà tutto chiaro." The off-by-one fix
        would have been wrong; a domain fact belongs in the docs,
        pinned so a future "cleanup" can't silently change the
        semantics. Same discussion: Roberto flagged pipeline
        construction boilerplate in his client — noted as I-009
        (follow-up, blocked on the pipeline module arriving).

D-060 | 2026-08-29 | state_machine R4 resolved (session 19, fix
        campaign item 4, approved by Roberto): keep the current
        failure semantics + document + pin (no behaviour change).
        After a failure at step k, current_step stays at k (the
        failed step — already pinned by the original test with an
        intent comment); a same-target retry executes only steps
        above k, skipping k. Documented: failure semantics added to
        the move_to_step docstring (L249-267) — recovery is
        move_to_step(k-1) (invokes k's down(), the domain rollback)
        then move up; handling a failure is the domain worker's
        responsibility (the machine re-raises and is
        domain-agnostic). Pinned by new
        test_retry_after_failure_skips_failed_step (1 test; closes
        T6). Suite 19 -> 20/0/0 GREEN; full discover 418, 52
        skipped.
        | Roberto: "La state machine non conosce nulla del DOMINIO,
        quindi non sa se ci sono delle azioni che non sono
        revertibili, oppure lo sono, ma non sono state
        rolled-back. ... il metodo esegue raise, quindi propaga la
        exception ... è il worker di dominio che la deve catchare e
        gestire." The machine cannot know whether a failed step is
        safely re-runnable, so rolling current_step back (option b)
        would assert a state the machine can't verify; honest
        reporting + documented recovery is the domain-agnostic
        choice.

D-061 | 2026-08-29 | state_machine R5 resolved (session 19, fix
        campaign item 5, ruled by Roberto): worker names are
        UNIQUE, enforced fail-fast in StateMachine.__init__
        (case-insensitive duplicate check -> ValueError, raised
        before any state is touched). Roberto REJECTED the proposed
        index-based move_to_last fix: the real ambiguity sits in
        move_to_step's name resolution itself (any duplicate pair
        would silently land on the first match), and the case does
        not occur in his client code today — so enforce the
        invariant instead of patching one call site. The check is
        case-insensitive because name resolution is
        case-insensitive (.upper()). move_to_last stays
        name-based; with unique names its dispatch is unambiguous.
        Closes M12 (duplicates impossible at construction) and
        T10 (first-match behaviour unreachable). Pinned by new
        test_duplicate_worker_names_raise +
        test_duplicate_worker_names_case_insensitive (2 tests).
        Suite 20 -> 22/0/0 GREEN; full discover 420, 52 skipped.
        | Roberto: "No, il fix non va bene. Anche il metodo
        move_to_step ha il problema nel determinante quale STATO
        raggiungere se ce ne fossero piu di uno con lo stesso
        nome... Al momento il caso NON si presenta. Quindi direi di
        modificare __init__ e forzare un check che i nomi NON siano
        duplicati. Se lo sono __init__ fallisce con raise Error
        appropriato. Bisogna anche fare un TEST a tal proposito."

D-062 | 2026-08-29 | state_machine T2 resolved (session 19, fix
        campaign item 6, approved by Roberto: "Prosegui con T2:
        sviluppa i test mancanti"): 7 new tests in the
        TestContextInjection class pin the whole context-injection
        layer (no source change — test-only): the injected
        context.log_event is the machine's live bound method
        (__self__ identity + a call records a LogEntry in this
        machine's logs); get_cache_file_path_for_next_level's
        {prefix}{level:02}_{name}.dat format with level =
        current_step at call time; get_cache_file_full_path_for_next_level
        joins cfg.base_dir for a relative prefix; an absolute
        cache_files_prefix drops base_dir (pathlib '/', V9); a
        missing cfg raises AttributeError naming 'cfg' (bare getattr,
        no default); empty workers give Path() / "UNDEFINED" /
        move_to_last guarded no-op; a shared context re-binds to the
        LAST machine built on it (V17). Side finding (recorded, no
        code action): the prefix is f-string-concatenated, so a
        prefix without a trailing separator (a str without '/', or
        ANY Path — str(Path) normalizes it away) silently glues the
        level name onto it ('cache' -> 'cache01_CONFIG.dat', verified
        live) — appended to M8 as the implicit contract.
        Suite 20 -> 22 -> 29/0/0 GREEN; full discover 427, 52
        skipped.

D-063 | 2026-08-29 | state_machine T3 resolved (session 19, fix
        campaign item 7, approved by Roberto: "procedi"): 3 new
        tests in the TestDisplayGoldens class pin the whole display
        layer (no source change — test-only). The module's datetime
        is patched with a frozen clock advancing 1ms per now()
        call, so the goldens are exact and wall-clock independent.
        test_log_event_live_print_format: the live line format
        [ts] [step:02][name:15] [rel:verb] message, incl. the
        numeric IntEnum rendering (M6) and the padding.
        test_show_event_log_golden + test_show_history_of_moves_golden:
        full end-to-end buffers (the move's live lines + the table)
        — banner, 54-dash separator, header, one row per log entry
        (step:04, name:15, numeric relevance); history table with
        80-dash rule, microsecond start stamps and duration =
        finish - start pinned at 0.003000 by the frozen clock.
        Side effect: setUp's global stdout patch is no longer just
        noise suppression — captured stdout is now asserted.
        Suite 29 -> 32/0/0 GREEN; full discover 430, 52 skipped.

D-064 | 2026-08-29 | state_machine T4 resolved (session 19, fix
        campaign item 8, approved by Roberto: "Procedi con T4"):
        3 new tests in TestStateMachine pin move_to_last (no source
        change — test-only). test_move_to_last_happy_path: from step
        0, move_to_last dispatches by the last worker's name
        (unambiguous since D-061) and runs the up chain (up[1] +
        up[2], current_step 2, history len 2).
        test_move_to_last_from_intermediate_position: from step 1,
        only the remaining up[2] executes (the already-executed
        up[1] is not re-run). test_move_to_last_single_worker_noop:
        a single-worker machine is a no-op — the only worker is the
        step-0 sentinel (D-059) and target == current (early
        return), so nothing executes. The empty-workers no-op was
        already pinned with D-062 (test_empty_workers_degenerate_
        paths); the duplicate-name misdirection (V8c) is unreachable
        since D-061. Suite 32 -> 35/0/0 GREEN; full discover 433,
        52 skipped.

D-065 | 2026-08-29 | state_machine T5 resolved (session 19, fix
        campaign item 9, approved by Roberto: "Prosegui con T5")
        + NEW HOUSE RULE (Roberto: "Scriviamo files solo dentro
        workspace_root/build/tmp ... e se il test va bene deve
        rimuoverli poi ... Non scriviamo in nessun altro posto"):
        unit tests write files ONLY under workspace_root/build/tmp
        and remove them afterwards; no test writes anywhere else
        (notably: not the CWD). build/ is already gitignored.
        Applied here: test_history_export_csv rewritten — now
        asserts the exact header field names
        (step/worker_name/direction/start_utc/finish_utc/
        duration_sec), the ISO-8601 +00:00 aware-UTC format (parsed
        back with datetime.fromisoformat, tzinfo non-None), and the
        duration_sec == finish - start identity for every row, in
        addition to the original row count + cell assertions. The
        artifact is written to a TMP_DIR constant (workspace root
        = 3 levels up from the test file) / build / tmp and is
        unlinked in a finally block, so a failing test leaves no
        garbage either. No source change; suite count unchanged
        (35 — T5 is a rewrite, not an addition). Suite 35/0/0
        GREEN; full discover 433, 52 skipped.

D-066 | 2026-08-29 | state_machine T7 resolved (session 19, fix
        campaign item 10, approved by Roberto: "procedi con T7"):
        2 new tests in TestStateMachine pin the bool/np.int64 index
        edge (no source change — test-only).
        test_bool_accepted_as_int_step: move_to_step(True) is
        silently accepted as step 1 (bool is a subclass of int and
        passes the isinstance(target_step, int) check) — up[1]
        executes; back at 0, move_to_step(False) is a same-step
        no-op (no callables, no new history entry).
        test_numpy_int64_rejected: np.int64 is NOT a Python int
        subclass, so move_to_step(np.int64(1)) raises TypeError
        ("target_step must be an integer index or a string worker
        name.") — the V7 behaviour. The optional one-line strict
        guard for bool (M3) remains Roberto's call in the M-sweep;
        the pins document the current behaviour either way.
        Suite 35 -> 37/0/0 GREEN; full discover 435, 52 skipped.

D-067 | 2026-08-29 | state_machine T8 + T9 resolved together
        (session 19, fix campaign item 11, approved by Roberto:
        "Procedi T8 e T9 insieme"): 5 new tests in
        TestStateMachine (no source change — test-only).
        T8: test_current_worker_name_tracks_current_step — the
        property is a live view of (workers, current_step):
        CREATED -> CONFIG -> POSITIONS -> CREATED across up and down
        moves; test_current_worker_name_empty_workers_undefined —
        "UNDEFINED" on an empty pipeline (V9f).
        T9: test_step_move_fields_up — for both up entries,
        step/worker_name/direction plus aware-UTC start/finish
        (utcoffset() == 0), finish >= start, and the exact
        duration == finish - start identity;
        test_step_move_fields_down — the down sequence confirms the
        excluded target (last entries: 2/POSITIONS/down then
        1/CONFIG/down) with the duration identity;
        test_step_move_recorded_on_failure — a failed step is still
        recorded by the timer's finally, now pinned at field level
        (step 1, CONFIG, up, aware-UTC finish, duration identity)
        instead of a bare len assert (V14). With this, ALL T items
        (T1-T11) are resolved; the remaining work is the source-side
        M-sweep. Suite 37 -> 42/0/0 GREEN; full discover 440, 52
        skipped.

D-068 | 2026-08-29 | state_machine M-sweep batch 1: M1 + M4 + M7 +
        M10 resolved (session 19, fix campaign item 12, approved by
        Roberto: "Fai M1, M4, M7, M10 poi mi spieghi meglio gli
        altri"): 4 source changes, all hygiene, no behaviour change
        for valid input. M1: the dead `Any` import is removed
        (V15). M4: _run_step's direction dispatch is made explicit
        — `elif direction == 'down'` and anything else raises
        ValueError ("Unknown direction ...: expected 'up' or
        'down'") instead of the implicit else-as-down; the new
        ValueError is caught by the existing except block (ERROR
        log + re-raise), consistent with a worker failure.
        M7: __repr__ added — Worker: Worker('NAME'); StateMachine:
        StateMachine(workers=N, current_step=K, verbosity=LEVEL),
        deliberately lightweight (context, logs and history can
        hold large domain data and are excluded). M10:
        export_history_of_moves_as_csv now calls
        path.parent.mkdir(parents=True, exist_ok=True) before the
        open — nested filenames work out of the box; a bare
        filename has parent '.', where the mkdir is a no-op.
        4 new tests: test_run_step_rejects_unknown_direction
        (M4), test_worker_repr + test_state_machine_repr_tracks_state
        (M7), test_csv_export_creates_missing_parent_dirs (M10;
        artifact under build/tmp, D-065 house rule). Suite 42 ->
        46/0/0 GREEN; full discover 444, 52 skipped. Remaining M
        items: M3, M5, M6, M8, M9, M11 (M2, M12 done); M3, M5, M8,
        M11 are Roberto's call items.

D-069 | 2026-08-29 | state_machine M-sweep batch 2: M3 + M5 + M8 +
        M11 resolved (session 19, fix campaign item 13, approved by
        Roberto: M3 "come proponi tu va benissimo, bool NON e'
        accettato come valor valido"; M5 "seguiamo la tua
        indicazione" (two call sites in the domain modules
        lm_worker_config and logistic_model will need the new
        names); M8 "OK"; M11 "aggiungiamo il chek @validate_call"):
        4 source changes.
        M3: bool is NOT a valid step — True/False are now rejected
        with the same TypeError + message as float/np.int64; the
        D-066 pin test_bool_accepted_as_int_step is rewritten to
        test_bool_rejected_as_int_step (machine stays untouched).
        M5: the injected cache helpers are renamed
        get_cache_file_path_for_current_level /
        get_cache_file_full_path_for_current_level — the old
        "for_next_level" names contradicted their own docstrings
        ("currently executing worker"). Follow-up (Roberto): two
        call sites in lm_worker_config and logistic_model must use
        the new names when those modules are ported.
        M8: the cache prefix is joined with pathlib (Path(prefix) /
        f"{level:02}_{name}.dat") instead of f-string-concatenated,
        so a prefix without a trailing separator (str or any Path)
        can no longer silently glue the level name onto it; the
        absolute-prefix-drops-base_dir behaviour (V9) is unchanged;
        pinned by test_path_cache_prefix_joins_without_gluing.
        M11: @validate_call(config=ConfigDict(
        arbitrary_types_allowed=True)) on Worker.__init__/up/down,
        StateMachine.__init__ (non-Worker entries / non-Context ->
        ValidationError; Context subclasses pass), log_event, and
        export_history_of_moves_as_csv; move_to_step delegates to a
        private _move_to_step_validated decorated with
        ConfigDict(arbitrary_types_allowed=True, strict=True) — the
        strict gate accepts exactly a Python int or a str (bool,
        float, np.int64, None rejected — all behaviours probed
        empirically against pydantic 2.13.4 before the change), and
        its ValidationError is re-raised as the pinned public
        TypeError (same message), so the move API's error contract
        is unchanged. New tests:
        test_constructor_rejects_non_worker_entry,
        test_constructor_rejects_non_context. The module now imports
        pydantic (already a workspace dependency; pyproject.toml
        unchanged). Suite 46 -> 49/0/0 GREEN; full discover 447, 52
        skipped. Remaining M items: M6 (cosmetic print drift), M9
        (injection side effect) — both Roberto's calls.

D-070 | 2026-08-29 | state_machine M-sweep close-out: M6 + M9
        (session 19, fix campaign item 14, approved by Roberto —
        M6: "1, pulisci"; M9: leave as-is, the context injection is
        load-bearing for the domain workers): the M-sweep is
        COMPLETE (M1-M12 all disposed).
        M6: cosmetic print cleanup, no behaviour change — the live
        log_event line now prints the enum names ([DEBUG:HIGH])
        instead of the numeric values and carries an explicit UTC
        marker after the timestamp; show_event_log's table has a
        TIMESTAMP (UTC) header, a 2-digit step column (consistent
        with the live line; was 4-digit), a RELEVANCE name column
        (was numeric), and a 66-underscore separator rule;
        show_history_of_moves' Dur (s) header is right-aligned over
        its right-aligned 6-decimal values (was left-14 vs
        right-15). The 3 frozen-clock display goldens
        (TestDisplayGoldens, D-063) were rewritten in place to the
        cleaned format — suite count unchanged 49/0/0.
        M9: the __init__ context injection (log_event binding +
        cache helpers; a shared context re-binds to the last
        machine built on it, V17) is left as-is — Roberto: the
        injection is fundamental, the domain workers depend on it.
        A future redesign (explicit machine reference /
        context-owned helpers) is parked in ideas.md as I-010, to
        be evaluated once all the domain modules are in the
        workspace and their call patterns are visible.
        Suite 49/0/0 GREEN; full discover 447 tests, 52 skipped,
        GREEN. STATE_MACHINE module fully done — R1-R5, all T
        items (T1-T11), M-sweep (M1-M12) closed, D-057..D-070.

D-071 | 2026-08-30 | cache_manager fix campaign batch 1: R1
        resolved as intentional, R2 + R4 fixed, M1-M3 fixed, T1/T2/
        T3/T4/T5/T7 pinned with 8 new tests (session 20, approved by
        Roberto: R1 "e' comportamento atteso. Quando la cache e'
        disabilitata viene forzato il ricalcolo, ma il risultato e'
        sempre trascritto nel cache_file"; R2 "risolviamo la
        asimmetria, mettiamo anche validate nel try, se validate si
        interrompe con eccezione, cancellare tutto e ricompute"; R4
        "aggiungi"; P0 "aggiungi i tests"; P1 "T1 aggiungi assert";
        P2 "aggiungi nei tests tutti i casi che mancano"; M1-M3
        "ok"): source changes + test additions.
        R1: no behaviour change — step 0 (is_allowed=False)
        computes AND stores by design (a cache-disabled run always
        warms the cache file); documented in the is_allowed
        docstring (L150-153); pinned by test_step0's new on-disk
        assertions (data + valid sidecar, T4).
        R2: validate_fn(cached_data) moved INSIDE the step-3
        try/except (L187-194) — a raising validator now deletes the
        cache files and forces recomputation, exactly like a load
        failure or a raising data checksum; the ERROR message is
        re-worded to "Failed to load or validate cache file
        '<path>': <e>. Recomputing." (covers all three callables in
        the try; the False-return WARN path is unchanged); pinned by
        test_validate_exception_forces_recomputation + the re-worded
        test_step3a pin + test_load_path_checksum_method_raises_
        recomputes.
        R4: @validate_call(config=ConfigDict(arbitrary_types_allowed=
        True)) on cache_manager_load_or_compute (L132) — house
        convention; pydantic now a module import (already a
        workspace dependency; pyproject.toml unchanged). Approved
        behaviour change: a str cache_path is coerced to Path and
        works; non-coercible values (int, None, ...) raise a
        pydantic ValidationError instead of the old bare
        AttributeError (V17 re-stated).
        M1: dead Any import removed. M2: docstring typos fixed
        ("difefrent"/"cacke" -> "different"/"cache"; "Look up for"
        -> "Look for"). M3: the step-2 WARN is now "Checksum
        validation failed for '<path>' (sidecar missing or
        mismatched). Deleting cache and recomputing." (was
        "Checksum mismatch..." — inaccurate when the sidecar is
        merely missing); both wordings pinned.
        Tests (13 -> 21): T2 (P0) 5 new TestCacheManagerPipeline
        tests + DataWithChecksum/DataWithBrokenChecksum helpers —
        compute path returns the data's own digest, load path
        returns it, missing method -> None, non-callable attribute
        -> None, raising method on the load path -> delete +
        recompute (V11/V12/V13); R2 pin: raising validate_fn ->
        delete + recompute; T1: assertIsNone(checksum) added to all
        6 existing pipeline tests; T4: test_step0 now asserts the
        on-disk warm-cache effect (R1); T5: new
        test_step2_missing_sidecar_forces_recomputation (the
        missing-sidecar variant of step 2); T3: new
        TestChecksumHelpers.test_sidecar_content_is_bare_hexdigest
        (the sidecar holds exactly the 64-hex digest, no newline, no
        filename — V15); T7: the recompute tests (step2/3a/3b + the
        two new T2/R2 recompute tests) now assert the on-disk
        replacement + a valid sidecar.
        Still OPEN: R3 (sidecar content format vs binio's
        sha3_256sum format — same sidecar file name, different
        content; a binio-written sidecar fails _verify_checksum ->
        silent recompute; options: leave + document, or tolerant
        first-token parse; detailed explanation given, awaiting
        Roberto's ruling), T6 (CWD-relative ./build/tmp artifact
        base, D-065 deviation — fix proposed: derive the workspace
        root from __file__; awaiting Roberto's OK), T8 (header
        grammar, report-only).
        Suite 13 -> 21/0/0 GREEN; full discover 460 -> 468 tests,
        52 skipped under the gate, GREEN.

D-072 | 2026-08-30 | cache_manager fix campaign batch 2: R3
        resolved (binio sidecar API adopted), T6 fixed, T3 pin
        restated, legacy-compat + malformed wrapper pins added, 2
        direct-compute helper tests dropped (session 20, approved by
        Roberto: "T6: OK"; R3 "ho capito che NON va bene. Brava ad
        aver trovato questa inconsistenza! Mia proposta: importiamo
        binio nel modulo cache_manager, e usiamo le API native di
        binio al posto di riscrivere le tre funzioni
        _compute_checksum _verify_checksum _save_checksum" —
        proposal presented with the 5-line wrapper refinement,
        "Approvato!"): source changes + test adaptations.
        R3 (RESOLVED): cache_manager now imports twolm.binio
        (BinaryFormatError, verify_sha3_256_sidecar,
        write_sha3_256_sidecar) — same package, no import cycle
        (binio imports no twolm module), no new pyproject
        dependency. Removed: `import hashlib`, `_compute_checksum`,
        `_save_checksum`. `_verify_checksum` is now a thin wrapper
        over `verify_sha3_256_sidecar(file_path,
        suffix=SHA3_256_CHECKSUM_SUFFIX)` mapping
        (FileNotFoundError, BinaryFormatError, UnicodeDecodeError)
        -> False: a missing, malformed or undecodable sidecar
        invalidates the cache, it never crashes the pipeline.
        `_compute_and_store` writes the sidecar via
        `write_sha3_256_sidecar` (binio's sha3_256sum format
        "<hex>  <basename>\n"). Sidecar naming unchanged
        (<full-name>.SHA3-256, the same scheme binio uses).
        Consequence: a binio-written sidecar now verifies (V15c
        flips); a legacy pre-D-072 bare-hex sidecar STILL verifies
        (binio's parser takes the first whitespace-separated token)
        -> zero cache invalidation for existing on-disk caches.
        T6: CUSTOM_TMP_BASE is now
        Path(__file__).resolve().parents[3] / "build" / "tmp"
        (workspace-root anchored, the D-065 idiom of
        test_state_machine.py).
        Tests (21 -> 21): the 2 direct-compute helper tests dropped
        (the hash belongs to the binio suite); TestChecksumHelpers
        reorganised: test_binio_sidecar_verifies (R3 pin),
        test_legacy_bare_hex_sidecar_still_verifies (compat pin),
        test_verify_checksum_fails_if_sidecar_mismatched,
        test_verify_checksum_fails_if_sidecar_malformed
        (BinaryFormatError + UnicodeDecodeError -> False, never
        raise), test_sidecar_content_is_binio_format (T3
        restated: "<hexdigest>  <basename>\n"); all pipeline
        set-ups switched _save_checksum -> write_sha3_256_sidecar
        (behaviour pins unchanged).
        Suite 21/0/0 GREEN (test_cache_manager); full discover 468
        tests, 52 skipped under the gate, GREEN.
        CACHE_MANAGER module CLOSED: R1-R4 + M1-M3 + T1-T7 all
        resolved; T8 (header grammar) report-only. Next: the domain
        modules lm_worker_config + logistic_model (their 2
        cache-helper call sites must use the D-069 names
        *_for_current_level).

D-073 | 2026-08-30 | Analysis of the three new domain modules
        Roberto brought in (commit 6bb45fb): base_model,
        logistic_model, test_logistic_model (session 21).
        lm_worker_config / lm_worker_positions / rlm_config_schemas
        are deliberately deferred (Roberto: "Lo faremo in seguito").
        Analysis only, NO code changes; 30-check probe
        scratch/verify_logistic_model.py, 0 mismatches.
        base_model: thin facade base over StateMachine — pure
        delegation (current_step / current_worker_name / verbosity
        get+set, move_to_step / move_to_last, 2 display methods, CSV
        export); model.context is model.sm.context (identity
        verified). OPEN: R1 no @validate_call on __init__ (house
        convention; the SM gate, D-069 M11, still catches wrong
        types at the inner boundary) — to be decided ONCE together
        with logistic_model R3; M1 missing __all__ (the only twolm
        module without one); M2 docstring forward-references the
        not-yet-ported DeepNetworkModel (informational).
        logistic_model: first concrete domain facade — RLMContext
        (@dataclass over the plain Context; 38 fields, 8
        *_checksum, the pipeline artifact blackboard) + LogisticModel
        (4-step construction: plain path validation -> context ->
        15-level worker list, DELIBERATELY partial per Roberto:
        CREATED active, CONFIG/POSITIONS imported but list entries
        commented, 12 factory imports commented — "una riga alla
        volta") + level-0 CREATED sentinel (D-059 made explicit:
        log ERROR + RuntimeError on direct call). 10 verified facts
        V1-V10. OPEN: R1 the D-069 NAME DIVERGENCE — RLMContext
        declares the injected callables under the PRE-D-069
        `_for_next_level` names (lambda no-op defaults, L157-158)
        while StateMachine injects `_for_current_level` (L179/L187);
        BOTH already-ported workers call the old names
        (lm_worker_config L102, lm_worker_positions L59) -> a
        silently-None cache path once the worker entries are
        enabled; options: (a) rename the 2 RLMContext fields + the
        2 worker call sites (4 lines, D-069-compliant — recommended),
        (b) revert the SM injection to the old names (against
        D-069), (c) defer; R2 `Union` used in 8 annotations but
        never imported — latent NameError proven via
        typing.get_type_hints(RLMContext), masked by PEP 563
        (from __future__ import annotations); fix: import Union or
        modernize to `str | None` (the file's own style); R3 no
        @validate_call on __init__ (decided once with base_model
        R1); M1 "weigth" comment typo (L139); M2 `vld__pop_stats`
        double underscore (L147) — typo for vld_pop_stats or the
        original repo's name? (inert for now, nothing references
        it); M3 directory-as-config raises FileNotFoundError where
        IsADirectoryError would be accurate (asymmetry with the
        base_dir helper's NotADirectoryError); M4 __init__ without
        docstring.
        test_logistic_model: 5 active + 2 muted (Roberto's design —
        restored line-by-line with the pipeline; the factory
        patches are currently inert; the muted tests' preconditions
        verified: 1-worker machine rejects move_to_step(1) with
        IndexError and move_to_step("POSITIONS") with ValueError).
        OPEN: T1 test_facade_methods_exist overpromises (smoke test
        with a try/except+self.fail anti-pattern, only 2 of 7
        methods exercised — propose real delegation pins + the
        verbosity round-trip + the CSV pass-through); T2
        tempfile.mkdtemp() with no dir= -> system temp dir, the
        D-065 deviation fixed in test_cache_manager T6/D-072 (fix:
        __file__-anchored build/tmp + mid-setup-failure cleanup);
        T3 the 2 muted tests (intentional, report-only); T4
        untested corners (the injected callables — a pin would have
        caught R1 —, the sentinel RuntimeError, the helper edge
        branches, the CSV pass-through); T5 dead import Relevance;
        T6 header grammar report-only.
        Suite 5/0/0 GREEN (test_logistic_model); full discover
        468 -> 473 tests, 52 skipped under the gate, GREEN.
D-074 | 2026-08-30 | logistic_model fix campaign batch 1 (session 21,
        Roberto: "parti con R1 + R2 + M1 + M2 + M3, per R2 aggiungi
        la @validate_call. M4: vld__pop_stats e' un typo, deve
        essere vld_pop_stats") — interpreted as approving R1, R2,
        R3 (the @validate_call he asks for) and M1-M4 (the vld
        rename); no test changes (the T1-T6 test batch stays
        pending). R1 RESOLVED: the 2 RLMContext injected-callable
        fields renamed _for_next_level -> _for_current_level (the
        lambda defaults are now the pre-injection fallback under
        the SAME names the machine injects, like log_event) + the 2
        already-ported worker call sites renamed (lm_worker_config
        get_cache_file_path_for_current_level, lm_worker_positions
        get_cache_file_full_path_for_current_level) — the
        silently-None cache-path trap is closed; the D-069
        follow-up in the state_machine doc is marked CLOSED
        (correction of record: the second call site was always in
        lm_worker_positions, not logistic_model). R2 RESOLVED: the
        8 `Union[str, None]` RLMContext annotations modernized to
        `str | None` (no import added — the file's own style,
        PEP 563-safe); typing.get_type_hints(RLMContext) now
        resolves. R3 RESOLVED (with base_model R1 — decided once,
        applied to both facades): @validate_call(
        config=ConfigDict(arbitrary_types_allowed=True)) on
        LogisticModel.__init__ AND BaseModel.__init__ (pydantic is
        now an import in both); approved behaviour change:
        wrong-typed constructor args (e.g. int paths) now raise a
        pydantic ValidationError at the facade boundary instead of
        the manual TypeError / the inner SM gate; valid str paths
        unchanged (str stays str until the manual helper coerces to
        Path + existence checks). M1 "weigth" -> "weight". M2
        vld__pop_stats -> vld_pop_stats (Roberto: typo). M3
        directory-as-config now raises IsADirectoryError (was
        FileNotFoundError; symmetric with the base_dir helper's
        NotADirectoryError). M4 LogisticModel.__init__ docstring
        added. NEW finding during the batch: M5 OPEN — dead
        `field` import (dataclasses.field imported, never used);
        awaiting Roberto's call. base_model M1 (missing __all__)
        NOT in the approved scope, stays OPEN. Verified: the
        injected closures bind under the renamed field names (no
        dual-name state); int args -> ValidationError; dir-as-
        config -> IsADirectoryError; no `for_next_level` reference
        left in src/. Suite 5/0/0 GREEN (test_logistic_model —
        untouched); full discover 473 tests, 52 skipped under the
        gate, GREEN.
D-075 | 2026-08-30 | logistic_model fix campaign batch 2 (session 21,
        Roberto: "M5: rimuovi. base_model M1: aggiungi. T1-T6:
        procedi"): M5 FIXED — the dead `field` import removed from
        logistic_model L30 (`from dataclasses import dataclass`);
        base_model M1 FIXED — `__all__ = ['BaseModel']` added (L39,
        the D-068 M1 pattern; the module is 89 lines). TEST campaign
        (test_logistic_model.py, 156 -> 294 lines, 5 -> 13 active
        tests, 2 muted unchanged): T1 FIXED — test_facade_methods_
        exist (the overpromising try/except smoke test) replaced by
        test_facade_delegates_to_state_machine (per-method
        patch.object(self.model.sm, ...) + assert_called_once_with
        pins for show_event_log, show_history_of_moves,
        move_to_step with BOTH an int and a name string,
        move_to_last, export_history_of_moves_as_csv) and
        test_facade_views_and_verbosity_round_trip (the 3 read-only
        views mirror model.sm; the verbosity property round-trips
        HIGH -> visible on the SM -> restored STANDARD); T2 FIXED —
        the D-065 idiom as in test_cache_manager (module-level
        CUSTOM_TMP_BASE = Path(__file__).resolve().parents[3] /
        "build" / "tmp" + setUpClass mkdir +
        tempfile.TemporaryDirectory(dir=...) created FIRST in setUp
        so a mid-setup failure still leaves a cleanable temp_dir +
        defensive tearDown that stops only the patchers that exist);
        T3 unchanged (intentional — the 2 muted tests come back
        "una riga alla volta" with the pipeline; report-only); T4
        FIXED — 7 corner tests: the injected closures' __name__s
        (_get_cache_file_path / _get_cache_file_full_path — a pin
        that would have caught R1) + log_event bound-method
        identity, the bare-context no-op-lambda fallback (helpers
        return None), the path computation through a dummy cfg
        (SimpleNamespace: cache/00_CREATED.dat,
        base/cache/00_CREATED.dat — the D-069 M8 pathlib join,
        restored via addCleanup), both sentinel RuntimeError
        messages (D-059 explicit sentinel), both helpers' edge
        branches (int -> TypeError, missing -> FileNotFoundError,
        dir -> IsADirectoryError post M3/D-074, file ->
        NotADirectoryError), the CSV pass-through (header-only file
        under the build/tmp artifact dir, header pinned to
        step,worker_name,direction,start_utc,finish_utc,duration_
        sec); T5 FIXED — the dead Relevance import removed (the
        top-level import now also pulls the 4 private helpers for
        T4); T6 unchanged (header grammar, report-only).
        Suite 13/0/0 GREEN (test_logistic_model); full discover
        473 -> 481 tests, 52 skipped under the gate, GREEN;
        build/tmp clean after the run. base_model R/M: all closed
        (M2 informational, kept by design); logistic_model: all
        R/M closed. Next: the deferred sibling modules
        (lm_worker_config / lm_worker_positions / rlm_config_
        schemas, Roberto: "Lo faremo in seguito"), then the
        pipeline grows one commented line at a time (uncommenting
        workers + restoring the 2 muted tests).
D-076 | 2026-08-30 | RLM pipeline enablement + two root-cause
        fixes (session 21, Roberto: "Ma fai girare tu i tests per
        favore e fissa gli errori. Quando i TEST vono VERDI, fai un
        git commit, e partiamo con la analisi."): (1) json5 added to
        pyproject.toml dependencies — lm_worker_config L31 +
        test_lm_worker_config import it; rlm_00.json is JSON5
        (comment header) so plain json cannot parse it (probe E6).
        (2) lm_worker_config cache naming fix (L102-110):
        `cache_files_prefix` is a FILENAME prefix per the schema
        ("Filename prefix for the level specific cache files"), so
        the physical file is flat `base_dir/rlmwf_01_CONFIG.dat`;
        the old code path-joined `Path(prefix) / level_name`,
        treating `rlmwf_` as a directory component
        (base_dir/rlmwf_/01_CONFIG.dat) → FileNotFoundError (ENOENT)
        on first write — Roberto's suspected "problema con i nomi
        della CACHE" confirmed. Now:
        `level_name = ctx.get_cache_file_path_for_current_level().
        name`, `cache_file_path = cfg.base_dir / f"{prefix}
        {level_name}"`. (3) state_machine move_to_step: the gate
        wrapped BOTH the gate and the execution in one try/except
        ValidationError, so domain pydantic ValidationErrors
        (invalid config data / base_dir problems raised inside the
        CONFIG worker) were converted to the gate's pinned
        TypeError — structurally separated into
        `_validate_target_step` (strict @validate_call, int | str,
        name resolution, bounds) + `_execute_move(target_index)`;
        the gate's pinned behaviour is byte-identical (bool /
        float / np.int64 → TypeError, unknown name →
        ValueError "Worker 'X' not found in the pipeline.",
        out of bounds → IndexError "Target step N is out of
        bounds."), domain errors propagate to the orchestrator
        (D-060). The first fix attempt (loc-based gate
        discrimination) FAILED: pydantic union errors use
        positional locs (1.int / 1.str), so loc-based
        discrimination of gate vs. domain errors is impossible.
        (4) test_lm_worker_config.py (Roberto's new file, D-076
        commit): 'py/twolm/...' → 'src/...' path typos x2; the
        invalid-config validation payload made schema-complete
        (output / stat_model / optimization.checkpoint_file /
        validation_data_set added) so each invalid test pins the
        ONE constraint under test instead of passing on any
        missing field. (5) Roberto's own changes in the same
        commit: lm_worker_config() uncommented in the pipeline
        (CREATED + CONFIG now the 2 active levels) and
        _test_move_to_step_delegates_to_state_machine restored
        (renamed without the underscore). Suite: test_lm_worker_
        config 14/0/0 (new), test_state_machine 49/0/0 (regression
        check after the gate split), test_logistic_model 14/0/0
        (13 + restored test), full discover 481 → 496 tests, 52
        skipped under SKIP_REGAB_DB=1, GREEN; build/tmp clean.
        Code commit 6ac9d74.
D-077 | 2026-08-30 | lm_worker_config analysis (session 21,
        docs/src/twolm/lm_worker_config.md): the CONFIG worker —
        JSON5 load (json5, E6) → ReversiLogisticModelConfig
        (pydantic) → base_dir validation (3 RuntimeError gates) →
        checksummed FLAT cache write: rlmwf_01_CONFIG.dat + bare-
        hex .SHA3-256 sidecar of model_dump_json(indent=4);
        ctx.cfg + ctx.use_cache set for the later workers, _down
        resets both to None. 35-check probe
        scratch/verify_lm_worker_config.py: 0 mismatches (A
        structure; B real-config behaviour incl. flat naming +
        binio-can-read-worker-sidecar; C re-runs/mutations incl.
        corruption RAISES + missing sidecar RAISES +
        worker-cannot-read-binio-sidecar asymmetry; D base_dir
        errors; E integration/D-076: domain ValidationError
        propagates, gate pins unchanged, closures need cfg,
        use_cache never consulted in _store_to_file). OPEN,
        awaiting Roberto's calls: R1 cache-flow consistency —
        ad-hoc hashlib + manual 8192-chunk verify + bare-hex
        sidecar instead of the D-072 cache_manager/binio
        standard; proven asymmetry (binio reads the worker's
        sidecar, the worker rejects a binio-format one);
        corruption RAISES (pinned) vs cache_manager's delete +
        recompute (would change the corruption test's semantics);
        use_cache copied to the context but never consulted —
        options: (a) adopt the cache_manager flow, (b) keep
        ad-hoc + document the divergence, (c) keep the raise
        semantics but write/parse binio-format sidecars. R2
        cross-ref (deferred module): the SM closure does
        Path(prefix)/name (D-069 M8) while the schema calls the
        prefix a filename prefix; lm_worker_positions L58-59 is
        latent — it passes the full-path closure result
        (rlmwf_/02_POSITIONS.dat subdirectory form) into
        cache_manager, which performs no mkdir anywhere → the
        same ENOENT on first write; resolution belongs to the
        positions round. R3 _validate_base_dir: 3x RuntimeError
        (exists / is_dir / writable, distinct logged messages) vs
        the precise OS types (FileNotFoundError /
        NotADirectoryError / PermissionError) used by the
        logistic_model helpers. M1 L71 DEBUG log prints the file
        object repr, not the config path; M2 L60 "stored to cache
        file." logged BEFORE _store_to_file runs; M3 trailing
        whitespace L91/L96; M4 no @validate_call on the public
        factory (house convention D-068 M11 — Worker.__init__ is
        already gated, convention-only delta); M5 hashlib import
        (redundant only if R1(a)/(c) adopted). T1 (test):
        mkdtemp(dir='./build/tmp') CWD-relative + no base mkdir —
        the D-065 __file__-anchored idiom; T2 test_invalid_json_
        syntax pins bare Exception (pin json5.JSON5Exception); T3
        the _down reset unpinned (cfg is None / use_cache is
        None); T4 the bare-hex sidecar format unpinned (or
        replace if R1 changes it); T5 header grammar + T6 mtime
        coarseness (report-only).
D-078 | 2026-08-30 | lm_worker_config fix campaign (session 21,
        Roberto's calls on D-077: "R1: Non cambiamo il
        funzionamento. Quando tutta la pipeline e' completa, questo e'
        un punto da rivedere. la cache costruita dalla libreria
        cache_manager, non va bene per il file JSON. Lo step config
        non ha bisogno di una cache. Forse voglio una
        'storicizzazione' del file JSON usato per generare un
        modello. R2: si ok e' da sistemare, ma perche' continua ad
        uscire? la dobbiamo sistemare in tutti i worker??? R3: OK
        cambiali con quelli corretti. M1-M5: OK. T1-T6: OK."):
        R1 RESOLVED AS DEFERRED — the ad-hoc cache flow stays
        untouched (hashlib + manual verify + bare-hex sidecar,
        unconditional write); the cache_manager/binio standard
        revisited only when the full pipeline is complete; the
        "storicizzazione" idea (keep a historical copy of the JSON
        config that generated a model — audit artifact, not a
        recomputable cache) recorded at I-011; M5 therefore closed
        as keep (the hashlib import stays). R2 RESOLVED AT MACHINE
        LEVEL (answer to Roberto's "perche' continua ad uscire":
        the problem lived in the ONE shared injected closure that
        every cache-consuming worker calls, so it would have recurred
        in every worker — fixed once instead):
        state_machine._get_cache_file_path now CONCATENATES the
        prefix onto the level name (Path(f"{prefix}{level:02}_
        {name}.dat")) instead of pathlib-joining it — the domain's
        cache_files_prefix is a filename prefix per the schema, so
        "rlmwf_" + "01_CONFIG.dat" = flat "rlmwf_01_CONFIG.dat";
        a directory-like prefix must end with a separator; this
        REPLACES the D-069 M8 join decision; the lm_worker_config
        per-worker concatenation of D-076 was replaced by a direct
        use of the injected full-path closure (uniform with
        lm_worker_positions — the rlmwf_/02_POSITIONS.dat
        subdirectory + no-mkdir trap is gone before POSITIONS is
        enabled). Re-pinned: test_state_machine
        test_path_cache_prefix_joins_without_gluing →
        test_cache_prefix_is_concatenated_verbatim (bare prefix
        'cache' glues to 'cache01_CONFIG.dat'); test_logistic_model
        T4 corner (cache00_CREATED.dat / base/cache00_CREATED.dat).
        The other 3 pinned prefix tests are byte-identical under
        concatenation (they use trailing-separator or absolute
        prefixes). R3 FIXED — _validate_base_dir raises the precise
        OS types: FileNotFoundError ("doesn't exist"),
        NotADirectoryError ("is not a directory"), PermissionError
        ("is not writable"); messages unchanged; the not-writable
        test updated to PermissionError. M1-M5 FIXED — M1: the
        DEBUG log prints ctx.config_file_path, not the file object
        repr; M2: "stored to cache file." logged AFTER
        _store_to_file; M3: trailing whitespace removed (L91/L96);
        M4: @validate_call(config=ConfigDict
        (arbitrary_types_allowed=True)) on the public factory
        lm_worker_config() (house convention D-068 M11); M5: keep
        (per R1). T1-T6: T1 FIXED — the D-065 idiom on all 4
        classes (CUSTOM_TMP_BASE = Path(__file__).resolve().
        parents[3] / "build" / "tmp" + setUpClass mkdir +
        tempfile.TemporaryDirectory FIRST in setUp + defensive
        tearDown; the dead shutil import removed; a stray per-test
        tempfile.mkdtemp(dir='./build/tmp') inside
        test_base_dir_is_a_file_raises_error removed — it leaked
        tmp dirs every run, found via build/tmp leftovers); T2
        FIXED — the bare-Exception pin replaced with ValueError
        (note: json5 0.15.0 raises a plain ValueError on a syntax
        error — the module has NO JSON5Exception attribute in this
        version, so the originally proposed JSON5Exception pin was
        not usable); T3 FIXED — the _down reset pinned (cfg is
        None / use_cache is None in test_move_down); T4 FIXED —
        the bare-hex sidecar format pinned (content ==
        sha3_256(.dat bytes) hexdigest, no binio basename column);
        T5/T6 report-only, unchanged. During the batch: the first
        not-writable-test rewrite (a read-only CHILD dir +
        addCleanup chmod-revert) FAILED — in CPython 3.12 the
        addCleanup callbacks run AFTER tearDown, so the revert hit
        a dir the TemporaryDirectory had already deleted
        (FileNotFoundError, no visible frames) — reverted to
        Roberto's original structure (the tmp dir itself is the
        read-only one, chmod-restore in tearDown). Suite:
        test_lm_worker_config 14/0/0, test_state_machine 49/0/0,
        test_logistic_model 14/0/0; full discover 496 tests, 52
        skipped under SKIP_REGAB_DB=1, GREEN; build/tmp clean; the
        35-check probe (scratch/verify_lm_worker_config.py, D1-D3
        re-pinned to the R3 types) re-run: 0 mismatches. Code
        commit d6a850e.
D-079 | 2026-08-30 | lm_worker_positions + rlm_config_schemas
        analysis (session 22 — resumed after the session-21
        crash; the probe scratch/verify_lm_worker_positions.py
        was started in the interrupted tail of session 21 and
        finalized in session 22: atexit rmtree of PROBE_TMP +
        sys.exit on failure, the house probe convention):
        POSITIONS enabled line-by-line in 601de87 (Roberto:
        uncomment lm_worker_positions() + copy the related
        test) — the pipeline now runs 3 active levels (CREATED
        sentinel → CONFIG → POSITIONS); the new
        test_lm_worker_positions.py (1 class / 2 tests,
        Roberto's file from the original repo) green on first
        run, no fixes needed; the latent rlmwf_/ subdirectory +
        no-mkdir trap re-verified GONE (flat
        rlmwf_02_POSITIONS.dat + .SHA3-256, binio-format
        sidecar). 49-check probe re-run: 0 mismatches.
        lm_worker_positions — OPEN awaiting Roberto's call: R1
        (load_from_db's 3-arg RegabDBConnection call drops port
        + password — a non-default configured port is silently
        ignored (connection always opens on 5432), a configured
        password never reaches the connection string (regab
        carries password=... only when one is passed)), M1 (no
        @validate_call on the public factory — convention-only
        delta, the D-068 M11 / D-078 M4 pattern), M2 (dead
        pathlib.Path import L33), M3 (trailing whitespace
        L73/L89/L92), M4 (the bare load_fn
        regab_load_data_set_from_file with its checksum=True
        default re-verifies the sidecar that cache_manager's
        step 3 already checked — redundant double file-checksum
        on every cache hit); cross-ref note (regab_store_data_
        set_to_file's docstring promises it "calculates the
        SHA3-256 checksum" but writes no sidecar — in this flow
        the sidecar is cache_manager's, D-072; the regab module
        is closed, Roberto's call). rlm_config_schemas — OPEN:
        R1 (OptimizationConfig.c2's description "Must be > c1"
        is docstring-only — NO cross-field validator, (c1=0.9,
        c2=0.1) validates; candidate fix = a
        model_validator(mode="after") on OptimizationConfig,
        which would give the unused M2 import a job), M1 (the
        0x-prefixed docstring example contradicts the 16-hex
        parser — bitboard_from_hex_str requires exactly 16 hex
        chars with NO 0x prefix; affects BOTH
        PatternConfig.parse_hex_to_bitboard L115 and
        MobilityFeatureConfig.parse_hex_to_bitboard L144), M2
        (model_validator imported L32, never used), M3
        (asymmetries: validation_data_set.status loose
        List[str] vs RegabDataSetConfig.status strict List[
        StatusString]; StatModelConfig extends BaseModel
        directly and lacks the RLMBaseConfig properties bag),
        M4 (bare mutable [] defaults — PatternSetConfig L128,
        MobilitySetConfig L157 — safe by pydantic's per-instance
        default copying, pinned E10, non-idiomatic next to the
        file's own Field(default_factory=...) convention).
        test_lm_worker_positions — OPEN: T1 (mkdtemp(
        dir='./build/tmp') CWD-relative + no base mkdir — the
        D-065 __file__-anchored idiom), T2 (no DB gate — both
        tests need the live regab DB; the SKIP_REGAB_DB=1
        pattern), T3 (the dead if-False blocks in both tests +
        the dead sys import — the test_feature T1 / D-043
        anti-pattern), T4 (header grammar, report-only). Docs:
        3 new mirror docs (docs/src/twolm/lm_worker_positions.
        md, docs/src/twolm/rlm_config_schemas.md,
        docs/src/twolm/test/test_lm_worker_positions.md).
        Suite: test_lm_worker_positions 2/0/0 (new, live DB);
        full discover 496 → 498 tests, 52 skipped under
        SKIP_REGAB_DB=1, GREEN; build/tmp clean (3 session-21
        probe leftovers removed; the probe now self-cleans via
        atexit).
D-080 | 2026-08-30 | D-079 fix campaign (session 22, Roberto:
        "tutte le tue considerazioni sono corrette. Correggile
        tutte" — lm_worker_positions + rlm_config_schemas; "fai
        tutto anche qui" — test): lm_worker_positions — R1
        FIXED: load_from_db now passes ALL the schema's
        connection params (RegabDBConnection(dbname, user, host,
        str(conn_params.port), conn_params.password)) — a
        non-default port is no longer silently ignored, a
        configured password reaches the connection string; the
        DEBUG connection log now includes the port (never the
        password); the fixture (no port/password) connects
        exactly as before. M1 FIXED: @validate_call
        (config=ConfigDict(arbitrary_types_allowed=True)) on the
        factory (the D-068 M11 / D-078 M4 pattern). M2 FIXED:
        the dead pathlib.Path import removed. M3 FIXED: the
        D-079-flagged trailing-whitespace lines (L73/L89/L92)
        cleaned — scope as in D-078 M3 (the remaining
        original-file trailing whitespace — license header,
        import block, is_cache_consistent body — stays, as in
        lm_worker_config post-campaign). M4 FIXED: load_fn now
        passes checksum=False (a lambda) — the redundant double
        file-checksum on every cache hit is gone. Cross-ref
        note RESOLVED: regab_store_data_set_to_file's docstring
        no longer promises the checksum calculation (in the
        pipeline flow cache_manager writes the sidecar, D-072);
        regab.md's API-table row corrected in the same batch.
        rlm_config_schemas — R1 FIXED: check_wolfe_constants, a
        model_validator(mode="after") on OptimizationConfig,
        enforces c2 > c1 (ValueError → ValidationError with both
        values) — the strong-Wolfe invariant is no longer
        docstring-only. M1 FIXED: both parse_hex_to_bitboard
        docstrings now show '0000000000000107' (16 digits, no
        0x prefix) + PatternConfig's mask field description says
        so. M2 RESOLVED BY R1: the model_validator import is
        now load-bearing. M3 FIXED: ValidationDataSetConfig.
        status is now List[StatusString] (strict, symmetric with
        RegabDataSetConfig; StatusString moved to L50, above its
        first user — a forward reference would have broken the
        class build) + StatModelConfig now extends RLMBaseConfig
        (the properties bag is present, default {}). M4 FIXED:
        both bare [] defaults → Field(default_factory=list).
        test_lm_worker_positions — T1 FIXED: the D-065 idiom
        (CUSTOM_TMP_BASE via __file__ + setUpClass mkdir +
        TemporaryDirectory FIRST in setUp + defensive
        tearDown). T2 FIXED: the SKIP_REGAB_DB gate at the top
        of setUp (the test_regab pattern). T3 FIXED: the dead
        if-False blocks in both tests + the sys import removed.
        T4 FIXED: header grammar ("How to run the
        lm_worker_positions unit tests.") + the run note
        documents the DB requirement and the gate. Approved
        behaviour changes (Roberto's call): c2<=c1 configs now
        fail schema validation (fixture c1=1e-4/c2=0.9
        unaffected); validation_data_set.status now requires 3
        uppercase letters (fixture CMS/CMR unaffected); a
        non-default port / configured password now actually
        takes effect in the DB connection (fixture has neither
        — identical connection). The 49-check probe re-pinned
        to the fixed behaviour (51 checks — E6b + E8b added;
        A4/A5/A6/E6/E7/E8/E9/F1/F2/F3 re-pinned): 0
        mismatches. Suites: gated full discover 498/0/54 GREEN
        (17 PERF + 35 regab + 2 positions); ungated full
        discover (live DB): 498 run, 17 skipped (PERF only),
        GREEN — all 35 DB tests + the 2 positions tests pass
        through the fixed 5-arg connection and the
        checksum=False load; build/tmp clean.
 D-081 | 2026-08-31 | lm_worker_features + test_lm_worker_features
         analysis (session 22; the FEATURES line-by-line enablement
         f051dd3 is Roberto's: the factory import L43 + the
         worker-list entry L209 uncommented in logistic_model.py +
         the 2 new files added — the pipeline now runs 4 active
         levels: CREATED sentinel → CONFIG → POSITIONS →
         FEATURES):
         lm_worker_features — the 4th pipeline level, and the FIRST
         pure-compute level: it builds a FeatureSet from the
         CONFIG-loaded cfg (no DB, no cache_manager, no cache file —
         the flat rlmwf_03_FEATURES* files never materialize, probe
         B10; RLMContext carries no features_checksum field,
         probe V10) and exposes ctx.feature_set. 13 verified facts
         V1-V13 (42-check probe scratch/verify_lm_worker_features.
         py, 0 mismatches): the 4-worker list; feature_set None →
         set → cleared by _down; name 'NoNameFeatureSet' (the
         FeatureSetConfig.name default — the fixture has no name
         key); the 3 fixture mobilities + 2 patterns with the
         CORRECT values (the R1 defect is log-only); feature order
         [INTERCEPT, ALMC, LMC, DLMC, EDGE, ELLE] (intercept,
         mobilities sorted (mask, amask), patterns sorted mask);
         n_features 6 / n_instances 16 (per-feature LMC 65/1,
         ALMC 65/1, DLMC 129/1, ELLE 81/8, EDGE 6561/4); hash =
         sha3_256(b'INTERCEPT' + mset.hash + pset.hash) re-derived
         independently (the public-API FeatureSet matches name +
         hash); the zero-feature guard (ValueError + ERROR log);
         cross-run identity (second instance: POSITIONS cache hit,
         FEATURES recomputed, identical set); the TYPE_CHECKING
         circular-import guard. OPEN awaiting Roberto's call: R1
         (the amask DEBUG log prints m.mask twice — L112; for the
         fixture LMC (true amask 0) logs FFFFFFFFFFFFFFFF and
         ALMC (true amask FFFFFFFFFFFFFFFF) logs 0000000000000000,
         DLMC unaffected; no data impact — the FeatureSet /
         MobilitySet are built from the correct m.amask; visible
         only at verbosity HIGH, which the test's Verbosity.LOW
         never reaches; fix = print m.amask in the amask slot), M1
         (no @validate_call on the public factory — convention-
         only, the D-080 M1 pattern), M2 (2 non-header trailing-
         whitespace lines L49/L78 — D-078 M3 scope), M3 (the orphan
         L63 comment quoting the empty-string SHA-256 hash, which
         the error message does not use). test_lm_worker_features —
         1 class / 1 test / no PERF, green on first run with the
         live DB. OPEN: T1 (not the D-065 idiom: mkdtemp(dir=
         './build/tmp') CWD-relative, no setUpClass mkdir, no
         TemporaryDirectory, the tearDown rmtree not in a finally),
         T2 (NO SKIP_REGAB_DB gate: the setUp moves to POSITIONS on
         a fresh base dir → DB hit; in a no-DB environment the
         canonical gated command would ERROR instead of skip — same
         pattern as test_lm_worker_positions T2, fixed D-080), T3
         (dead `from pathlib import Path` import), T4 (header
         grammar "How to use the unit tests ... module."), M1 (the
         setUp comment "FEATURES depends on the configuration
         loaded there" is inaccurate — the dependency is the CONFIG
         level, and the explicit POSITIONS move is functionally
         redundant though it pins the step numbering), M2 (trailing
         whitespace L90 + 3 whitespace-only lines). Housekeeping:
         scratch/verify_logistic_model.py discovered STALE — the
         session-21 original pinned the pre-D-074 state (legacy
         _for_next_level names, the latent-Union get_type_hints
         NameError, FileNotFoundError-for-a-directory, 1-worker
         boundaries) and was never re-pinned after the D-074/D-075/
         D-076 batches; re-pinned in this batch to the post-
         D-074/D-076/D-081 state (35 checks, 0 mismatches: the
         *_for_current_level lambda fields + legacy names gone,
         get_type_hints succeeds, IsADirectoryError for a directory
         as config + the facade @validate_call ValidationError, the
         4-worker list, the 4-worker boundaries — the empty {}
         config makes the CONFIG worker's pydantic ValidationError
         propagate (the D-076 gate split) and a failed move leaves
         current_step at 1 (D-060), the checksum inventory + the
         absent features_checksum). No code modified by this
         decision (analysis only; f051dd3 is Roberto's). Suites:
         gated full discover 499/0/54 GREEN (17 PERF + 35 regab +
         2 positions; the new FEATURES test RUNS ungated — it
         needs the live DB); ungated full discover (live DB): 499
         run, 17 skipped (PERF only), GREEN. Next: awaiting
         Roberto's call on the FEATURES R/M + T items; then the
         next pipeline line (lm_worker_indexes) + the last muted
         test _test_move_to_step_by_string (test file change —
         Roberto's call).
 D-082 | 2026-08-31 | D-081 fix campaign (session 22, Roberto:
         R1 "ok, fissa il bug", M1-M3 OK + "rimuovi commento
         orfano", test T1-T4 + M2 OK, plus the golden content
         test he proposed):
         lm_worker_features — R1 FIXED: the amask DEBUG log now
         prints m.amask in the amask slot (L113 — log-only
         defect, the FeatureSet / MobilitySet were always built
         from the correct values; the fixture's LMC line now
         shows amask = 0000000000000000, ALMC's amask =
         FFFFFFFFFFFFFFFF). M1 FIXED: @validate_call
         (config=ConfigDict(arbitrary_types_allowed=True)) on
         the factory (L121) + the pydantic import (L32) — the
         D-080 M1 pattern. M2 FIXED: the 2 non-header trailing-
         whitespace lines cleaned (the license-header `# ` lines
         stay, D-078 M3 scope). M3 FIXED: the orphan "Empty
         String SHA-256 Hash" comment (the hash was quoted,
         never used) removed. File now 125 lines.
         test_lm_worker_features — T1 FIXED: the D-065 idiom
         (CUSTOM_TMP_BASE under build/tmp via __file__,
         setUpClass mkdir, TemporaryDirectory created FIRST in
         setUp, defensive tearDown) replaces the CWD-relative
         mkdtemp — the test now runs from any CWD. T2 FIXED: the
         SKIP_REGAB_DB gate at the top of setUp (the setUp moves
         through POSITIONS on a fresh base dir → DB hit; a
         no-DB environment now skips instead of ERRORing). T3
         RESOLVED BY T1: the dead Path import is now
         load-bearing (CUSTOM_TMP_BASE). T4 FIXED: header
         grammar ("How to run the lm_worker_features unit
         tests.") + the run note documents the DB requirement
         and the gate. M2 FIXED: trailing whitespace (L90 + 3
         whitespace-only lines) removed. M1 LEFT AS-IS per
         Roberto's call — he wants to evaluate moving the
         FEATURES level BEFORE POSITIONS in the pipeline:
         recorded at I-012. NEW (Roberto: "Dovremmo avere almeno
         1 goldentest che controlla il contenuto di feature_set
         in context"): test_feature_set_content_golden added —
         name 'NoNameFeatureSet' (the schema default), the 3
         golden hash literals (fs 453e918a...5a159 =
         sha3_256(b'INTERCEPT' + mset.hash + pset.hash), mset
         2e553593...08a94 — the literal test_mobility pins, pset
         04d52f12...c18), the intercept (INTERCEPT, 1/1), the
         3 mobilities in the sorted (mask, amask) order (ALMC,
         LMC, DLMC), the 2 patterns in the sorted mask order
         (EDGE, ELLE), the feature order + per-feature
         n_configurations / n_instances (6 features,
         n_instances 16). Goldens independently re-derived
         (public API, D-081 probe B9). File now 169 lines.
         Probe scratch/verify_lm_worker_features.py re-pinned
         to the fixed behaviour (44 checks — A6/A7/A8/A9
         flipped, B8b/B8c re-pinned to the true amasks, C3/C4/
         C5/C6/C8 flipped, C9/C10 new for the golden test): 0
         mismatches. Suites: gated full discover 500/0/56 GREEN
         (17 PERF + 35 regab + 2 positions + 2 features);
         ungated full discover (live DB): 500 run, 17 skipped
         (PERF only), GREEN; build/tmp clean. Next: the next
         pipeline line (lm_worker_indexes) + the last muted
         test _test_move_to_step_by_string (test file change —
         Roberto's call) + the I-012 evaluation.

 D-083 | 2026-08-31 | INDEXES line-by-line enablement + analysis
         (session 23): Roberto brought in lm_worker_indexes +
         rlm_indexes + the two test files in a323e0f and
         uncommented the lm_worker_indexes() import + worker-list
         entry in logistic_model.py (the only 2 lines the commit
         touched there — the rlm_indexes / rlm_indexes_checksum
         blackboard fields were already declared in RLMContext at
         first import). The pipeline now runs 5 active levels
         (CREATED sentinel → CONFIG → POSITIONS → FEATURES →
         INDEXES). Analysis (review-only, doc-only — no source
         change): rlm_indexes.md + lm_worker_indexes.md + the two
         test mirror docs (D-007); 47-check probe
         scratch/verify_rlm_indexes.py (tiers A structure, B
         rlm_indexes runtime pure, C pipeline integration live
         DB, D worker structure, E/F test-file structure): 0
         mismatches; scratch/verify_logistic_model.py re-pinned
         to the 5-worker state (V3c; V10 unchanged — 8
         *_checksum fields, no features_checksum): 35 checks, 0
         mismatches. OPEN awaiting Roberto's call: rlm_indexes
         R1 (store docstring overpromises the checksum — the
         sidecar is cache_manager's, D-072; as in regab D-079/
         D-080) + M1-M5 (5 dead imports, "togheter" typo, 4
         trailing-whitespace lines, the version-gate literal, the
         by-design no-@validate_call on compute/consistent —
         documented circular-import constraint); lm_worker_
         indexes M1-M3 (no @validate_call on the factory, 2
         trailing-whitespace lines, load_fn bare → redundant
         sidecar re-verify, the D-080 M4 shape); test_rlm_
         indexes T1-T5 + M1-M2 (dead IndexArray import, header
         grammar, 2 broad assertRaises(Exception), the
         missing-rds_checksum test that passes for the wrong
         reason, the Italian comment, 19 whitespace lines, the
         rds-only is_cache_consistent coverage gap); test_lm_
         worker_indexes T1-T3 + M1 (no D-065 idiom, no
         SKIP_REGAB_DB gate, header grammar, 13 whitespace
         lines). Suites: full discover 515/0/56 gated + 515 run /
         17 skipped ungated (live DB), GREEN; build/tmp clean.
         Next: Roberto's calls on the INDEXES R/M/T items; then
         the next pipeline line (lm_worker_wmaps) + the last
         muted test _test_move_to_step_by_string (test file
         change — Roberto's call) + the I-012 evaluation.

 D-084 | 2026-08-31 | INDEXES fix campaign (session 23, Roberto:
         "Sì fai tutto, mi è tutto chiaro" — the full approved
         R/M/T table from D-083): rlm_indexes R1 + M1-M4 + M6
         (M5 left as-is, by design). R1 FIXED: the store
         docstring no longer promises the checksum — "Saves the
         ReversiLogisticModelIndexes instance to a binary file."
         + the regab D-080 Note ("no SHA3-256 sidecar is written
         by this function — in the pipeline flow the sidecar is
         written by cache_manager."); doc-only. M1 FIXED: the 5
         dead imports removed (IntEnum, Protocol,
         BeforeValidator, AfterValidator, Field) — the import
         block is now hashlib / TYPE_CHECKING / validate_call +
         ConfigDict / Path / binio / IndexArray / the TYPE_
         CHECKING RLMContext. M2 FIXED: the class docstring
         typo "togheter" → "together". M3 FIXED: the 4 non-
         comment trailing-whitespace lines stripped (license-
         header `# ` lines stay, D-078 M3 scope). M4 FIXED:
         the version gate compares the variable — `if version
         != expected_version:` (L150). M5 left as-is (by
         design, documented in the source L166: the RLMContext
         annotation cannot be resolved by pydantic without a
         real import; the import is deliberately under TYPE_
         CHECKING; the house convention already has sanctioned
         deviations, cf. the D-069 M11 gate functions). M6
         FIXED (optional, applied): __repr__ added to
         ReversiLogisticModelIndexes (L84-91, @validate_call —
         house style as in pattern.py / mobility.py):
         ReversiLogisticModelIndexes(rds_checksum='...',
         feature_set_hash='...', indexes=(N, 16)). File now
         190 lines (180 at arrival); 5 @validate_call
         decorators (the 5th is __repr__). lm_worker_indexes
         M1-M3 FIXED. M1 FIXED: @validate_call(config=ConfigDict
         (arbitrary_types_allowed=True)) on the factory (L77) +
         the `from pydantic import validate_call, ConfigDict`
         import (L32) — the D-080 M1 / D-082 M1 pattern. M2
         FIXED: the 2 non-comment trailing-whitespace lines
         stripped. M3 FIXED: load_fn = lambda path:
         rlm_indexes_load_from_file(path, checksum=False) (L57)
         — the redundant sidecar re-verification is gone, the
         same shape as POSITIONS' D-080 M4 fix. File now 80
         lines (77 at arrival). test_rlm_indexes T1-T5 + M1-M2
         FIXED, 13 → 14 tests. T1 FIXED: the dead `from twolm.
         pattern import IndexArray` import removed. T2 FIXED:
         header grammar "How to run the rlm_indexes unit tests.
         ". T3 FIXED: the 2 broad assertRaises(Exception)
         replaced with the precise pydantic ValidationError
         (import added, L51). T4 FIXED: test_init_fails_with_
         invalid_indexes_type now passes rds_checksum="valid_
         hash" — the invalid indexes=[[1, 2], [3, 4]] (a list
         of lists, rejected by the NDArray gate: "Input should
         be an instance of ndarray") is the thing under test,
         as the docstring claims. T5 FIXED: the Italian
         comment ("Non mockiamo il modulo...") translated to
         English. M1 FIXED: the 19 non-comment trailing-
         whitespace lines stripped. M2 FIXED: the rds-only-
         differs is_cache_consistent branch now unit-tested
         (new test_is_cache_consistent_returns_false_rds_
         differs, L287-299 — roles swapped: rds "live_hash" vs
         "outdated_cached_hash", feature_set_hash identical).
         File now 304 lines (287 at arrival). test_lm_worker_
         indexes T1-T3 + M1 FIXED. T1 FIXED: the D-065 idiom —
         CUSTOM_TMP_BASE = Path(__file__).resolve().parents[3]
         / "build" / "tmp" (L58), setUpClass mkdir (L65-67),
         TemporaryDirectory created FIRST in setUp (L85-88),
         defensive tearDown with getattr guards (L99-103); the
         CWD-relative mkdtemp + the shutil import are gone. T2
         FIXED: the SKIP_REGAB_DB gate at the top of setUp
         (L71-73, the test_regab wording). T3 FIXED: header
         grammar + the live-DB / gate run note. M1 FIXED: the
         13 non-comment trailing-whitespace lines stripped.
         File now 158 lines (137 at arrival). Verification:
         the 4 suites green (test_rlm_indexes 14/0/0 — no DB,
         no gates; test_lm_worker_indexes 2/0/0 — live DB).
         Probe scratch/verify_rlm_indexes.py re-pinned to the
         post-campaign state (56 checks, tiers A-F; the A8/A9/
         A10, D3/D5/D6, E2/E3/E4/E7, F3/F4/F5/F7/F8/F9 pins
         flipped; the A1/A3/D1/E1/F1 line counts re-anchored):
         0 mismatches (tier C live-DB). Probe
         scratch/verify_logistic_model.py unchanged (35 checks,
         0 mismatches — the worker list is untouched by this
         campaign). Suites: gated full discover 516/0/58 GREEN
         (17 PERF + 35 regab + 2 positions + 2 features + 2
         indexes — the 2 lm_worker_indexes tests now skip
         under SKIP_REGAB_DB=1); ungated full discover (live
         DB): 516 run, 17 skipped (PERF only), GREEN;
         build/tmp clean. 4 mirror docs re-stated to the FIXED
         state (campaign CLOSED): docs/src/twolm/rlm_indexes.
         md, docs/src/twolm/lm_worker_indexes.md, docs/src/
         twolm/test/test_rlm_indexes.md, docs/src/twolm/test/
         test_lm_worker_indexes.md. Next: the next pipeline
         line (lm_worker_wmaps) + the last muted test
         _test_move_to_step_by_string (test file change —
         Roberto's call) + the I-012 evaluation.
 D-085 | 2026-08-31 | TMP-dir design: the shared workspace-root-
          anchored test paths (session 23, Roberto: "Mi hai
          convinto, sono anche io per la A, con inclusi i JSON e
          .env. Procedi con la modifica." — solution A of the
          design discussion, incl. the JSON + .env anchoring):
          the design. Roberto's question: per-test or shared TMP
          dirs, and why CUSTOM_TMP_BASE is
          "Path(__file__).resolve().parents[3] / 'build' / 'tmp'"
          (a source-file reference) instead of an absolute
          workspace-root reference, the JSON files being
          workspace-relative. Answer: the base dir is SHARED
          (created once per test class in setUpClass, idempotent)
          while each test gets its OWN fresh sub-directory
          (tempfile.TemporaryDirectory(dir=CUSTOM_TMP_BASE)) and
          removes it in its defensive tearDown (D-065: no
          artifacts left, even on failure) — per-test isolation,
          shared base. And parents[3] IS the workspace root
          (src/twolm/test/ is 3 levels below it) — the file path
          is only the computation mechanism, since a test needs
          some absolute starting point. The real inconsistency
          (Roberto's) was: tmp absolute/file-anchored vs JSON
          CWD-relative in the same setUp. Solution A (chosen,
          over A' per-file documented, B package-anchored, C
          CWD + assert): new module src/twolm/test/paths.py —
          WORKSPACE_ROOT = the first ancestor of the module
          holding the workspace marker (pyproject.toml;
          marker-based, not a parents[N] level count — survives
          file moves; the only remaining "file reference" is the
          walk-up start point inside the helper, one place),
          CUSTOM_TMP_BASE = WORKSPACE_ROOT / "build" / "tmp";
          dedicated test module test_paths.py (3 tests, no DB,
          pins: root absolute + marker-holding, root ancestor of
          src/twolm/test/, CUSTOM_TMP_BASE == <root>/build/tmp
          absolute). Applied: the 6 D-065 test files
          (test_cache_manager, test_logistic_model,
          test_lm_worker_config/positions/features/indexes)
          import the constants instead of recomputing them (the
          per-file __file__ derivations + comment blocks are
          gone); the 7 json_config lines (4 files) are anchored
          to the same WORKSPACE_ROOT (were CWD-relative
          'src/twolm/test/data/rlm_00.json'); test_regab loads
          .env via load_dotenv(WORKSPACE_ROOT / ".env") (was the
          caller-relative search) and its last CWD-relative
          mkdtemp(dir='./build/tmp') uses str(CUSTOM_TMP_BASE).
          Scope note: test_regab's mkdtemp is the PRE-D-065
          mechanism (non-defensive rmtree in tearDown, the
          build/tmp existence assumption) — only the dir= anchor
          changed, per the approved scope; a full D-065
          conversion there is a future call. Verification: the
          8 touched suites green (paths 3/0/0; cache_manager +
          logistic_model 38/0/0; the 4 lm_worker 20/0/0); full
          discover 516 → 519 tests, 519/0/58 gated + 519 run /
          17 skipped ungated (live DB), GREEN; build/tmp clean;
          the 2 probes pinning the changed lines re-pinned
          (verify_rlm_indexes E1 158→153 + E2 the idiom import;
          verify_lm_worker_features C1 169→164 + C3 the idiom
          import + C5 the Path rationale) — 0 mismatches.
          Observed, out of scope (pre-existing stale behavioral
          pins, confirmed pre-existing by a stash test):
          verify_lm_worker_features B1a (pins the 4-worker list —
          the pipeline now has 5 active levels since D-084),
          verify_lm_worker_config E2/E3 (exception expectations
          stale after the pipeline growth), verify_cache_manager
          (imports the renamed-away _compute_checksum),
          verify_mobility (a TypeError) — a probe-maintenance
          batch when convenient. 2 new mirror docs
          (docs/src/twolm/test/paths.md,
          docs/src/twolm/test/test_paths.md) + 7 test docs
          updated (the idiom references, the JSON notes, the
          line anchors; test_logistic_model.md appendix
          re-anchored 294→288 lines + the muted-test table
          corrected to the current 14 active + 1 muted);
          decisions/index/journal/NOTES updated.
 D-086 | 2026-08-31 | WMAPS bring-in: analysis + the D-085
          paths idiom applied to the new test files (session 23,
          Roberto: "Ho attivato il worker WMAPS. Aggiunto i due
          moduli: lm_worker_wmaps e rlm_wmaps, con i tests.
          Tutti i tests sono GREEN, bisogna introdurre la change
          delle PATHS con il nuovo design appena finalizzato.
          Va fatta la solita analisi." — commit 73b4342, 6
          files, +1018/−2): the bring-in. Roberto's commit
          activates the 6th pipeline level (the
          lm_worker_wmaps import + list entry uncommented in
          logistic_model.py; RLMContext's 7 Wmaps fields were
          already pre-declared — the context was brought in
          whole, the pipeline grows line-by-line); 2 new source
          modules (rlm_wmaps.py 311 lines — the
          ReversiLogisticModelWMaps 6-array object
          [rlm_indexes_checksum, cut_off, feature_w_ranges
          (F,3) int64, iwmap_feature_offset (F+1,) uint32,
          iwmap (K,) int64 with −1 = unseen config, wmap (W,3)
          int64 with −1 = fallback row, wmap_fallback (F_cut,3)
          int64, w (W,) float32 zeros] + store / load / compute
          / is_cache_consistent + the duck-typed
          compute_sha3_256_hash over the 6 arrays, the 3rd
          cache_manager consumer; lm_worker_wmaps.py 87 lines —
          the uniform 7-kwargs cache wiring, flat
          rlmwf_05_WMAPS.dat + .SHA3-256, D-078 naming) + the
          rlm_01.json fixture (the golden-content variant:
          stat_model {cut_off 2, logit 0.03, ridge 0.0} vs
          rlm_00 {1, 0.05, 0.0}; intercept + LMC(65) +
          DIAG3(27) + CORE(81) → F=4, K=174) + 2 test files
          (test_rlm_wmaps 6 tests no DB: the handcrafted 4×3
          mock compute pins + consistency + store/load;
          test_lm_worker_wmaps 3 tests all DB-dependent: the
          round-trip + the rlm_01 golden content). Analysis
          (probe scratch/verify_wmaps.py, 60 checks, 0
          mismatches): the golden literals INDEPENDENTLY
          RE-DERIVED (tier E: pipeline run on rlm_01 → all 6
          arrays vs the test literals extracted from the source,
          E0-E9) — 21 weights float32, offsets [0,1,66,93,174],
          iwmap 174, wmap (21,3), wmap_fallback (10,3), the
          fallback wmap rows' freqs == the sums of the
          wmap_fallback rows, contiguous per-feature w ranges,
          no −1 sentinel rows (the fixture pindexes is dense).
          The approved change (this decision): the D-085 paths
          idiom applied to both new test files — the
          CWD-relative mkdtemp (×3) → TemporaryDirectory under
          the shared CUSTOM_TMP_BASE, the 2 CWD json_config
          lines anchored to WORKSPACE_ROOT, defensive
          tearDowns, the dead shutil imports removed, the
          twolm.test.paths imports added; test_rlm_wmaps 251 →
          259, test_lm_worker_wmaps 283 → 301; both suites
          green (6/0/0 no DB + 3/0/0 live DB). PENDING
          Roberto's call (the remaining T items, house
          classes): T1 test_lm_worker_wmaps — the missing
          SKIP_REGAB_DB gate (the header L38-39 claims one,
          "SKIP_REGAB_DB=1 skips the DB-gated tests", but no
          gate exists in the code; the 3 tests hit the DB
          through POSITIONS/INDEXES and would ERROR, not skip,
          in a no-DB environment — the D-080 T2 / D-084 T2
          class); T2 test_rlm_wmaps — the header L38-39 claims
          "a live regab DB is required" although the file is
          DB-free (the D-084 T3 header-grammar class); T3
          test_rlm_wmaps L162 — the leftover generation comment
          "(sostituisci la classe TestRLMWmapsCacheConsistency)"
          (the D-084 T5 Italian-leftover class); T4 dead
          imports — test_rlm_wmaps 'from io import StringIO'
          (L51), rlm_wmaps 'from itertools import accumulate'
          (L35) (the D-084 M1 class); T5 rlm_wmaps L307/L182 —
          is_cache_consistent + compute lack @validate_call
          with NO explanatory note (rlm_indexes carries the
          L166 note documenting the TYPE_CHECKING constraint —
          add the same comment, the decorator itself stays off);
          T6 lm_worker_wmaps L85 — the factory lacks
          @validate_call (the other 5 worker factories all have
          it, the D-084 M1 class) + the missing pydantic import;
          T7 lm_worker_wmaps L54 — load_fn is the raw
          rlm_wmaps_load_from_file (checksum defaults True →
          the sidecar is validated twice, once by
          cache_manager) — the house shape is
          lambda path: ...(path, checksum=False) (the D-080 M4
          / D-084 M3 class); T8 lm_worker_wmaps _down — clears
          the 6 arrays but NOT ctx.wmaps_obj_checksum (set in
          _up L72) — the house shape clears object + checksum
          (lm_worker_indexes._down); T9 whitespace — 68
          non-comment trailing-whitespace lines across the 4
          files (rlm_wmaps 23 incl. the L275 'above_mask =
          ~mask ' and L288 code lines, lm_worker_wmaps 4,
          test_rlm_wmaps 21, test_lm_worker_wmaps 20) (the
          D-084 M3 class); T10 (coverage, optional) — no
          golden-hash test for compute_sha3_256_hash (the
          D-081 golden-content philosophy), the checksum=True
          sidecar path is untested, the description/version
          RuntimeError branches are untested, no __init__
          ValidationError test. R1 (design, his contract) —
          the −1 input sentinel is unguarded at rlm_wmaps L252
          (f_iwmap[stats[:,0]] = stats[:,2]): if the pindexes
          matrix ever contains −1 cells (missing
          configurations), −1 becomes a "configuration" in
          np.unique — below cut-off it folds into the fallback
          (a [fid, −1, count] row enters wmap_fallback) AND
          f_iwmap[−1] overwrites the feature's LAST
          configuration slot; at/above cut-off it gets its own
          weight and still corrupts the last slot. The rlm_01
          fixture is dense (E8) so it is unexercised — needs
          his answer on whether pindexes is contractually
          dense; if not, a stats[:,0] >= 0 guard.
          Verification: both suites green post-idiom
          (test_rlm_wmaps 6/0/0 no DB, test_lm_worker_wmaps
          3/0/0 live DB); full discover 519 → 528 tests,
          528/0/58 gated + 528 run / 17 skipped ungated (live
          DB), GREEN; build/tmp clean. Notes: NOTES.md all
          sections (4 new inventory rows, Environment 528,
          where-we-are 2 bullets, next-steps the in-progress
          bullet, index D-086), journal session 23.
 D-087 | 2026-08-31 | WMAPS fix campaign — ALL approved (session
          23, Roberto: "T1: OK / T2: OK / ... / T10: OK —
          Procedi su tutto per favore. R1: non succede mai che
          un indice o un pindice (principale) sia -1. Gli indici
          sono degli uint, sono per definizione un numero compreso
          tra 0 e n_configurations - 1."): the WMAPS fix
          campaign, closing D-086. All 10 T items approved + the
          R1 design question answered. Fixes applied:
          test_lm_worker_wmaps T1 — the SKIP_REGAB_DB gate added
          to BOTH setUps (top of setUp, the D-080 T2 / D-084 T2
          shape) + import os; the header's claim now true (3/0/3
          under the gate). test_rlm_wmaps T2 — header "-1- Run
          the tests." (the file is DB-free; the false DB claim
          removed, the D-084 T3 class); T3 — the leftover
          generation comment (L162, Italian "sostituisci la
          classe...") deleted; T4 — dead imports: 'from io import
          StringIO' AND 'from unittest.mock import patch' removed
          (both zero uses, AST-verified). rlm_wmaps T4 — the
          dead 'from itertools import accumulate' removed (the
          offsets use np.cumsum); T5 — the no-validation note
          added above rlm_wmaps_compute (L181, the exact
          rlm_indexes L166 wording, covering compute +
          is_cache_consistent — the TYPE_CHECKING circular-import
          constraint); T9 — 23 non-comment trailing-whitespace
          lines stripped (incl. the 2 code lines: 'above_mask =
          ~mask ' and the fallback_details_table assignment).
          lm_worker_wmaps T6 — @validate_call
          (config=ConfigDict(arbitrary_types_allowed=True)) on
          the factory + the pydantic import (the D-080 M1 /
          D-082 M1 / D-084 M1 pattern — now all 6 worker
          factories decorated); T7 — load_fn =
          lambda path: rlm_wmaps_load_from_file(path,
          checksum=False) (the redundant double sidecar
          verification is gone — cache_manager verifies in step
          2, the raw function would verify again in step 3; the
          D-080 M4 / D-084 M3 house shape); T8 — _down now
          clears ctx.wmaps_obj_checksum (the house shape: object
          + checksum, as in lm_worker_indexes._down); T9 — 4
          whitespace-only lines stripped. test files T9 — 21
          (test_rlm_wmaps) + 20 (test_lm_worker_wmaps)
          whitespace-only lines stripped; scope as in D-078 M3:
          the license-header '# ' lines stay. test_rlm_wmaps
          T10 (the coverage batch) — +5 IO tests:
          test_compute_sha3_256_hash_golden (the duck-typed hash
          on the known IO object =
          12c3344ec23c798d7b35eb6eae01034b29ee5c539bfb2018ca2ea
          bc73c861dfa — the D-081 golden-content philosophy),
          test_load_with_valid_sidecar (the checksum=True happy
          path, the D-072 machine), test_load_with_mismatched_
          sidecar (a byte-flip → RuntimeError "checksum file
          signature doesn't match"), test_load_rejects_wrong_
          description (RuntimeError "not a proper ..."),
          test_load_rejects_version_mismatch (RuntimeError
          "version mismatch"); + the TestRLMWmapsInit class (2
          tests: valid constructor + the precise pydantic
          ValidationError on a string cut_off — the D-084 T3
          pattern). 6 → 13 tests. R1 RESOLVED as NO-GUARD, by
          Roberto's contract: the indexes are unsigned by
          definition (0..n_configurations−1), so the pindexes
          input is DENSE — no −1 cells ever, and the unguarded
          f_iwmap[stats[:,0]] (L252) is correct. The contract is
          now documented in the rlm_wmaps_compute docstring (a
          future change to the input contract is a deliberate,
          documented act). New observation (left as-is, minor,
          flagged to Roberto): the __init__ body (L101-108) is
          indented 9 spaces (one short of the house 4-space
          multiple) — valid Python, cosmetic only. Line counts
          post-campaign: rlm_wmaps 311 → 316, lm_worker_wmaps
          87 → 91, test_rlm_wmaps 259 → 325, test_lm_worker_
          wmaps 301 → 315. Docs (D-007 mirror rule, post
          fix-campaign as per the D-083/D-084 pattern): the 4
          new mirror docs written (docs/src/twolm/rlm_wmaps.md,
          lm_worker_wmaps.md, test/test_rlm_wmaps.md,
          test/test_lm_worker_wmaps.md). Probe re-pinned:
          scratch/verify_wmaps.py updated to the post-campaign
          state (all T items now pinned as FIXED, line counts
          refreshed). Verification: test_rlm_wmaps 13/0/0 (no
          DB), test_lm_worker_wmaps 3/0/0 (live DB) + 3/0/3
          under SKIP_REGAB_DB=1 (the gate works); full discover
          535 tests (528 + 7 new): 535/0/61 gated (17 PERF + 35
          regab + 2 pos + 2 feat + 2 idx + 3 wmaps) + 535 run /
          17 skipped ungated (live DB), both GREEN; build/tmp
          clean. Notes: NOTES.md all sections (inventory rows
          CLOSED + line counts, Environment 535/61, where-we-are
          bullets refreshed, next-steps Done bullet, index
          D-087 + the 4 doc rows), journal session 23.
 D-088 | 2026-08-31 | Correction — the D-087 M1 "9-space __init__
          indent" observation is a MISREAD (session 23, Roberto:
          "ReversiLogisticModelWMaps allinea ai canonici 8 spazi,
          per favore."): Roberto approved the alignment of the
          ReversiLogisticModelWMaps.__init__ body (L101-108) to
          the canonical 8-space indent. Verification (per-line
          leading-space count on the committed file, HEAD and
          working tree): every line already carries exactly 8
          spaces — the original observation was a misread of the
          displayed content (the read-tool display padding).
          No code change; the working tree file is byte-identical
          to HEAD for this file. The doc mirror
          (docs/src/twolm/rlm_wmaps.md M1) and the NOTES.md
          inventory row corrected accordingly. Lesson: verify
          whitespace/indentation claims programmatically
          (len(l) - len(l.lstrip(' '))) before reporting them.

 D-089 | 2026-08-31 | DESIGN_MTR bring-in: the NumPy 2.5 warning
          fix (APPLIED — Roberto: "Esegui la modifica. Poi analisi
          completa.") + the full analysis, opening the 7th pipeline
          level (session 23). Roberto's UNCOMMITTED bring-in:
          rlm_design_matrix.py + lm_worker_design_matrix.py +
          test_lm_worker_design_matrix.py (the logistic_model.py
          uncomment is his; the 3 files stay his staging state — no
          agent commit of them).
          FIX — the warning: "Implicit casting of output to a
          different kind is deprecated. In a future version, this
          will result in an error. (Deprecated NumPy 2.5)".
          Mechanism: X is uint32, ctx.iwmap is int64 (the -1 unseen
          config sentinel); np.take(int64, idx, out=uint32) performs
          an implicit kind cast into the output buffer — deprecated
          in NumPy 2.5.2 (the venv version). In a normal run the
          cast is value-correct (verified: identical values) and the
          warning is only emitted once (default filters hide it);
          under -W error it is FATAL — the take aborts and X keeps
          the np.empty garbage. Future NumPy: a hard error. Fix
          applied in rlm_design_matrix_compute (L122-124): the
          explicit source cast np.take(ctx.iwmap.astype(np.uint32),
          pindexes_with_offsets, out=X) + the 2-line note; K x 4
          byte temp, the out= path and the guards preserved.
          Verified: his exact -W error command OK; the full -W
          error discover clean. The alternative (X =
          iwmap[pindexes_with_offsets].astype(np.uint32)) was
          rejected — larger N x k int64 temp.
          ANALYSIS (probe scratch/verify_design_matrix.py, 54
          checks, 0 mismatches): structure pinned post-fix (135/77/
          202 lines); 4 @validate_call decorators (init/hash/store/
          load — NOT compute/is_cache_consistent, and NO
          no-validation note — the rlm_indexes L166 class); the
          worker factory has NO @validate_call + no pydantic import
          (unlike the other 6 workers); load_fn raw (checksum
          defaults True — the double sidecar check); the test
          header CLAIMS the SKIP_REGAB_DB gate but NO gate exists
          (3 DB tests); the D-085 idiom NOT applied (CWD mkdtemp
          x2 + CWD json x2); 26 ws lines (3+2+21); the triple
          blanks are house precedent (rlm_indexes carries the
          same) — not an item; the shutil import IS used
          (tearDown); _down clears BOTH attrs (the house shape).
          GOLDEN (D0-D10, live DB, rlm_01): the (10,7) uint32 X
          literal (extracted from the test source) matches the
          pipeline; the independent recompute X = iwmap[pindexes +
          repeat(offsets[:-1], n_instances)] matches; all values
          are valid w indices (< W=21); the intercept column is all
          0; the per-feature columns stay within their iwmap
          regions; the flat cache files + the data checksum are
          correct. Live layout (correcting my first reading):
          n_instances [1,1,4,1] (DIAG3 = 4 instances, CORE = 1),
          n_configurations [1,65,27,81] (K=174) — the WMAPS
          fixture, reused. Cross: RLMContext's design_matrix /
          design_matrix_checksum fields were PRE-DECLARED; the 4
          later levels remain commented (zed is next).
          PENDING Roberto's call — T: T1 the missing SKIP_REGAB_DB
          gate in both test setUps (the D-087 T1 class; needs
          import os); T2 the worker factory @validate_call +
          pydantic import; T3 raw load_fn → the lambda
          checksum=False idiom; T4 the no-validation note on
          compute/is_cache_consistent (the rlm_indexes L166
          class); T5 the 26 ws lines; T6 (coverage question) NO
          dedicated test_rlm_design_matrix.py — the WMAPS level
          has one (store/load cycle, RuntimeError pins, golden hash
          test, init ValidationError pins) — add it?; T7 the D-085
          idiom in the test file (TemporaryDirectory/CUSTOM_TMP_
          BASE + WORKSPACE_ROOT anchors + defensive tearDown). R:
          R1 the two compute guards are REDUNDANT — L115 any(== -1)
          and L118 count_nonzero(>= 0) check the same invariant
          (iwmap values are -1 or >= 0) — keep both or merge?
          R2 RESOLVED: the implicit-cast warning (above).
          | The bring-in pattern of the previous 6 levels: fix what
          was explicitly approved, analyze the rest, wait for the
          call on the T batch. The warning fix is a one-line,
          value-preserving, verified change (his explicit
          instruction). The analysis follows the WMAPS template
          (structure + golden re-derivation + cross-facts), the
          golden X re-derived from the pipeline, not transcribed.
          Suite: 538 tests (535 + 3), 538/0/61 gated + 538 run /
          17 skipped ungated, build/tmp clean (3 pre-fix leftovers
          removed). Docs (D-007): the 3 mirror docs follow the fix
          campaign, as in WMAPS.

 D-090 | 2026-08-31 | DESIGN_MTR fix campaign — ALL approved
          (session 23, Roberto: "Procedi su tutti i T, e R1. Poi
          commit."): the D-089 T batch + R1, closing the DESIGN_MTR
          bring-in. Fixes applied (source, per the explicit
          approval):
          test_lm_worker_design_matrix T1 — the SKIP_REGAB_DB gate
          added to BOTH setUps (top of setUp, the D-080 T2 /
          D-084 T2 / D-087 T1 shape) + import os; the header's
          claim now true (3/0/3 under the gate). T7 — the D-085
          idiom applied to both classes: mkdtemp('./build/tmp') →
          TemporaryDirectory under the shared CUSTOM_TMP_BASE
          created FIRST, tmp_dir = Path(_tmp.name), CWD json ×2 →
          WORKSPACE_ROOT-anchored, the shutil.rmtree teardowns →
          the defensive getattr tearDown, the dead shutil import
          gone. T5 — the 21 ws lines stripped; file 202 → 226
          lines. lm_worker_design_matrix T2 — the factory
          @validate_call (config=ConfigDict
          (arbitrary_types_allowed=True)) + the pydantic import
          (the D-080 M1 / D-082 M1 / D-084 M1 / D-087 T6 house
          convention). T3 — load_fn → lambda path:
          rlm_design_matrix_load_from_file(path, checksum=False)
          (the double sidecar check gone, D-080 M4 / D-084 M3 /
          D-087 T7 shape). T5 — the 2 ws lines stripped; file 77
          → 80 lines. rlm_design_matrix T4 — the no-validation
          note above rlm_design_matrix_compute (the rlm_indexes
          L166 wording, as in rlm_wmaps L181). R1 — the redundant
          2nd guard (count_nonzero) merged away: iwmap values are
          -1 or >= 0, so any(== -1) and count_nonzero(>= 0) !=
          size check the SAME invariant; the single -1 guard with
          the precise ValueError remains (a defensive re-check of
          the WMAPS R1 dense-pindexes contract). T5 — the 3 ws
          lines stripped; file 135 → 133 lines. T6 — the
          dedicated test_rlm_design_matrix.py ADDED (12 tests, 4
          classes, mirroring test_rlm_wmaps): 2 compute (the
          handcrafted-mock (4,3) uint32 golden, hand-derived
          X = iwmap[pindexes + col_offsets], + the guard's
          ValueError pin) + 2 consistency (the 1-field compare) +
          6 IO (store/load cycle, the golden hash
          da86a916e03c76befa6f5df70e6221b0f9a355173e356ea63fef89
          ea9719757b pinned, the valid/mismatched sidecar, the
          wrong-description + version-mismatch RuntimeError pins)
          + 2 init (ValidationError). The D-085 idiom from day
          one, no DB, no gate, no DB claim in the header.
          | All 7 T items + R1 were on the table since D-089 and
          follow the exact precedents of the 6 previous levels
          (same classes, same idioms); Roberto approved the whole
          batch. The R1 merge is value-identical (the 2 guards
          were provably equivalent for int64 iwmap values) and
          drops 1 of the 3 gathers. The T6 file closes the only
          coverage gap of the batch (the WMAPS level has the
          equivalent suite; DESIGN_MTR arrived with only the
          worker test). Verification: the 12 new tests 12/0/0
          (no DB); the worker test 3/0/3 gated + 3/0/0 live;
          full discover 550/0/64 gated + 550 run / 17 skipped
          ungated + the full -W error discover clean;
          build/tmp clean; the probe re-pinned to the
          post-campaign state (55 checks, 0 mismatches — tiers
          A/B/C re-pinned + the new G tier for the dedicated
          suite + the D0-D10 live golden re-derivation
          unchanged). The 4 D-007 mirror docs written
          (rlm_design_matrix, lm_worker_design_matrix,
          test_lm_worker_design_matrix, test_rlm_design_matrix)
          in the post-campaign state, as in WMAPS.

 D-091 | 2026-08-31 | ZED bring-in + full bring-in analysis
          (session 24, Roberto's commit 439c966 — "Ho aggiunto
          il modulo lm_worker_zed con il relativo modulo di
          dominio rlm_zed, e i tests. Procedi con la analisi,
          grazie."): the 8th pipeline level activated (the
          import L47 + the worker-list entry L213 — the only
          2 lines the commit touched in logistic_model.py;
          RLMContext's zed_checksum / y2z / z2y / z fields
          were PRE-DECLARED). rlm_zed (101 lines): the Z data
          object (ReversiLogisticModelZed: the y2z/z2y affine
          closures + z (N,) float32 — game_values mapped
          [−64, 64] → [c, 1−c], c = cfg.stat_model.
          logit_clipping) + zed_fun_factory (the pure math,
          exported in __all__) + rlm_zed_compute + the duck-
          typed compute_sha3_256_hash over z.tobytes() only;
          NO store / load / is_cache_consistent — the FIRST
          non-cache level in the pipeline (by design — the
          worker comment documents the on-the-fly choice).
          lm_worker_zed (70 lines): the "ZED" worker, NO
          cache_manager wiring (no rlmwf_07* file ever
          materializes — verified live, probe D11); _up sets
          ctx.y2z / z2y / z / zed_checksum, _down clears ALL
          FOUR (the house shape — no gap at bring-in).
          test_lm_worker_zed (138 lines): 2 classes / 2 tests
          — the isolated factory math (alpha=0.02: [-64, 0, 6,
          64] → [0.02, 0.5, 0.545, 0.98] + the round-trip) +
          the rlm_01.json integration (logit_clipping 0.03,
          y (10,) int8, z (10,) float32 golden, the step pins
          DESIGN_MTR=6 / ZED=7). Analysis (analysis-only per
          Roberto's request — no source changes): probe
          scratch/verify_zed.py, 50 checks, 0 mismatches (A
          structural rlm_zed + B worker + C test + D the live
          golden + F cross) — the golden z re-derived
          independently (the float32-exact recompute
          0.5 + y·(1−2c)/128 + the float64 reference, the
          checksum = sha3_256(z.tobytes()), the endpoints
          y2z(±64) = c / 1−c, the round-trip, the _down
          clearing, the no-cache-file check, the 8-worker
          list, the pre-declared fields, the 7 commented
          imports). NO warnings (the full −W error discover
          clean — no implicit-cast pattern this time), NO R
          items (no redundancy; the no-cache choice is
          intentional + documented). Suite 550 → 552
          (552/0/64 gated + 552 run / 17 skipped ungated,
          build/tmp clean). PENDING Roberto's call — T: T1 the
          missing SKIP_REGAB_DB gate in the test setUp (the
          header L38-39 CLAIMS it — false, as in D-089 T1
          pre-fix; verified: under the gate the 2 tests RUN on
          the live DB, ".." not "ss"); T2 the worker factory
          @validate_call + the pydantic import (all the other
          6 workers have it); T3 NO dedicated test_rlm_zed.py
          — the domain module has zero dedicated coverage (the
          compute, the class init, the hash, the factory
          edges — the D-090 T6 class gap; WMAPS and
          DESIGN_MTR have the equivalent suites); T4 the
          D-085 idiom not applied in the test (the CWD
          mkdtemp './build/tmp' L84 + the CWD json L85 + the
          dead shutil L46 + the dead Path L53 + the
          non-defensive tearDown); T5 NO _down test in the
          worker test (the D-078 T3 class — _down verified
          working live, probe D12); T6 the no-validation note
          missing above rlm_zed_compute (the rlm_indexes L166
          class — the TYPE_CHECKING constraint applies
          identically); T7 zed_fun_factory in __all__ but
          WITHOUT @validate_call (the only exported public
          function in the pipeline missing it); T8 the 12
          code ws lines (rlm_zed 2: L83/L89; worker 3:
          L46/L50/L55; test 7: L72/L86/L90/L108/L115/L118/
          L122). M (informational, no action planned): M1 the
          duck-typed hash covers z only — the closures are
          pure functions of logit_clipping (not stored on the
          object); same game_values + different clipping →
          different z → different hash, so no collision risk
          today, but a future cache would need the clipping
          in the checksum; M2 the flat-file numbering skips
          07 (FEATURES skipped 03) — the next cache level
          (GRADIENT) takes rlmwf_08.
          | The bring-in pattern of the 7 previous levels:
          full structural pin + golden re-derivation + cross-
          facts, wait for the call on the T batch. The
          no-cache design is the first deviation from the
          uniform 7-kwargs cache_manager wiring — intentional,
          documented, verified (D11); the 4 ctx attributes are
          still cleared on down (the machine contract holds,
          D12).
 D-092 | 2026-08-31 | ZED fix campaign CLOSED (Roberto: "T1-T8: OK").
          All 8 T items applied: (T1) the SKIP_REGAB_DB gate added to
          TestLMWorkerZed.setUp FIRST (the test header L38-39 claim
          was false at bring-in: under the gate the 2 worker tests
          RAN on the live DB; now 3/0/2 gated, 3/0/0 live —
          TestZedFunFactory is DB-free and not gated); (T2)
          lm_worker_zed() got the @validate_call decorator + the
          pydantic import (all 6 other workers have it); (T3) the
          dedicated test_rlm_zed.py created (10 tests, 3 classes,
          no DB: the factory goldens/inverse/round-trip/
          2-clippling endpoints, the handcrafted-mock compute
          golden (4,) exact + hash identity, the 2 init
          ValidationError pins + by-reference, the rlm_01 hash
          golden 3d49fd5d56ced2f7bb70e5c24c8100b3318a7e66e7c990de53
          ed2f16f365d9b2); (T4) the worker-test D-085 idiom
          (TemporaryDirectory under CUSTOM_TMP_BASE created FIRST,
          WORKSPACE_ROOT-anchored rlm_01.json, defensive tearDown,
          the dead shutil import gone, Path now load-bearing);
          (T5) test_down_clears_zed_attributes added (move to ZED,
          move_to_step(6), pins step 6 + worker name DESIGN_MTR +
          all 4 ctx attrs None — live-verified by the D12 probe);
          (T6) the no-validation note above rlm_zed_compute (the
          rlm_indexes L166 note class); (T7) zed_fun_factory
          decorated @validate_call (the only exported public
          function in the pipeline missing it); (T8) the 12
          non-comment ws lines emptied in place across the 3
          pre-existing files (the new file clean from day one).
          Verified: full discover 563 tests (552 + 10 + 1), 66
          skipped gated (64 + 2 zed), 17 ungated, GREEN; the
          -W error discover clean; build/tmp clean; the re-pinned
          probe scratch/verify_zed.py (60 checks, tiers A–G
          including the NEW G tier for the dedicated suite) passes
          0 mismatches. The M1/M2 informational items are recorded
          in the docs (rlm_zed.md Minor notes) and left open — the
          hash-covers-z-only choice and the 07 numbering skip are
          by design, no action. The D-007 mirror docs written for
          all 4 files (rlm_zed.md, lm_worker_zed.md,
          test_lm_worker_zed.md, test_rlm_zed.md).
 D-093 | 2026-09-01 | GRADIENT bring-in + full bring-in analysis
          (session 25, Roberto's commit a0adc6e — lm_worker_
          gradient + rlm_gradient + test_lm_worker_gradient +
          rlm_02.json + the logistic_model enablement; the 9th
          active level, the SECOND non-cache level after ZED):
          rlm_gradient is a function-only module (sigmoid = the
          scipy expit wrapper + rlm_gradient_compute, the fg
          closure builder capturing X / z / alpha =
          ridge_regularization/M; f = 0.5·(mean(rn²) + alpha·
          ‖w‖²), g via the broadcast-bincount trick; the linear
          predictor is the per-row sum of w[X[m,p]] — the
          w-INDEX sum, not X·w); no data class, no store/load/
          hash, no init validation (unlike every other rlm_*
          level). Verified (probe scratch/verify_gradient.py,
          52 checks, 0 mismatches, tiers A–E; the live D tier on
          the rlm_02 199952-position dataset): X (199952, 8)
          uint32 + w (2981,) float32 + z (199952,) float32;
          f(w=0) float32 0.020493777 and g(w=0) re-derived
          independently in float64 (np.add.at + hand-rolled
          sigmoid vs expit), matching the test goldens
          (0.02049378 / 3.558e-4 / −2.395e-4 / 1.101e-3); f + g
          at a seeded w≠0 re-derived (the ridge term included);
          the closure stateless (2 calls identical); the feature
          set (no intercept, DIAG3 + EDGE, 0 mobilities, 8
          instances); the _down live (fg None back at ZED); NO
          rlmwf_07* / rlmwf_08* files ever; RLMContext.fg pre-
          declared (L135); the 9-worker list; scipy 1.18.1
          installed but NOT in pyproject.toml;
          StatModelConfig.ridge_regularization pre-declared
          (L186, ge=0.00). Suite 563 → 564 (564/0/66 gated +
          564 run / 17 skipped ungated, −W error clean,
          build/tmp clean). The stale logistic_model probe
          re-pinned (V3c the 5-worker a323e0f pin → the 9-worker
          list — the WMAPS / DESIGN_MTR / ZED activations never
          re-pinned it). OPEN awaiting Roberto's call: R1 (the
          rlm_gradient_compute return annotation claims
          NDArray[np.float32] for the gradient but the actual g
          is FLOAT64 — np.bincount upcasts the float32 weights
          to float64; f IS float32, matching its annotation —
          fix the annotation vs cast g, the OPTIMIZE consumer's
          expectation will decide); T1-T9 (T1 scipy missing from
          pyproject.toml, T2 the worker factory without
          @validate_call + pydantic import, T3 the no-validation
          note above rlm_gradient_compute — the rlm_indexes
          L166 class, T4 the 9 source ws lines (rlm_gradient 6
          + worker 3), T5 the test NO SKIP_REGAB_DB gate (the
          header L38-39 claim is false — under the gate the
          test RAN on the live DB), T6 the test D-085 idiom not
          applied (CWD mkdtemp + CWD json + no
          TemporaryDirectory + non-defensive tearDown + the
          dead-after-idiom shutil import), T7 the test no _down
          test, T8 the test 4 ws lines, T9 the sigmoid
          docstring — "funxtion" typo, "provide" → "provides",
          the "very small values of x" stability claim
          imprecise (expit's advantage is for large |x|));
          M1-M2 (M1 no dedicated test_rlm_gradient.py —
          rlm_gradient_compute is mockable with a SimpleNamespace
          ctx, the zed pattern; M2 the exported sigmoid without
          @validate_call — decorating would reject scalar
          input); M3-M4 informational (the second non-cache
          level — the next cache level takes rlmwf_08, the /M
          normalization by design; the worker triple blank lines
          L37-39 / L41-43). The fix campaign would be D-094.
D-094 | 2026-09-01 | GRADIENT fix campaign — R1 + T1-T9 + M1
          applied, M2 / M4 left as-is (session 25, Roberto's
          call — R1: "caspita, brava, ho verificato
          indipendentemente ed in effetti hai ragione ... la
          funzione dice che ritorna float32, facciamo ritornare
          un float32 ... Quando avremo completato la PIPELINE,
          uno degli interventi da fare sarà verificare se sia
          possibile velocizzare questa funzione, credo sia il
          collo di bottiglia della PIPELINE per modelli di grosse
          dimensioni" + "T1-T9 falli tutti" + "M1: OK. M2: No,
          non metterei la validate call sulla funzione sigmoid.
          E' un wrapper, è chiamata in continuazione durante la
          ottimizzazione. M3-M4: OK."): R1 (rlm_gradient.py
          L89: `return f, g` → `return np.float32(f),
          g.astype(np.float32, copy=False)` — the behaviour
          change Roberto chose: the fg closure now returns
          (float32 f, float32 g), matching the return annotation;
          the test goldens stay valid — the value change < 1
          float32 ulp, inside the pinned tolerances; the future
          OPTIMIZE level consumes this float32 contract; the
          performance study of the closure is recorded at I-013);
          T1 (pyproject.toml: "scipy" added to the dependencies);
          T2 (lm_worker_gradient.py: the pydantic import + the
          factory @validate_call(config=ConfigDict(
          arbitrary_types_allowed=True)) — like all 7 other
          workers); T3 (rlm_gradient.py: the no-validation note
          above rlm_gradient_compute — the rlm_indexes L166
          class, "Here validation is not possible, it brings in
          a convoluted issue with circular imports"); T4 (9 ws
          lines emptied in place: rlm_gradient 6, worker 3); T5
          (test_lm_worker_gradient.py: the SKIP_REGAB_DB gate in
          setUp FIRST — the header L38-39 claim now true, 2/0/2
          under the gate); T6 (the test: the D-085 idiom —
          TemporaryDirectory under CUSTOM_TMP_BASE created first,
          WORKSPACE_ROOT-anchored rlm_02.json, the paths import,
          the dead shutil gone, the defensive tearDown); T7
          (the test: test_down_clears_gradient added — GRADIENT
          → step 8 + fg not None, back to step 7 → ZED + fg
          None); T8 (the test: 4 ws lines emptied); T9 (the
          sigmoid docstring: "funxtion" → "function", "provide"
          → "provides", "very small values of x" → "extreme
          values of x"); M1 (test_rlm_gradient.py ADDED — 8
          tests, 2 classes, no DB: the sigmoid goldens/symmetry
          vs the hand-rolled float64 1/(1+exp(−x)), the
          SimpleNamespace mock compute — the zero-weights
          goldens 4/75 + [1/30, 0, −1/30] on the (3, 2)
          handcrafted matrix, the nonzero-weights float64
          re-derivation, the ridge /M scaling (g(b)−g(a) =
          (b−a)/M·w, f(b)−f(a) = 0.5·(b−a)/M·‖w‖²), the
          minlength empty bucket (the uncovered w-index keeps
          the pure ridge term, g (N,) shape), the R1 float32
          dtype pins, the closure statelessness); M2 left as-is
          (Roberto's call: the sigmoid stays a bare wrapper —
          called in the optimization hot loop); M3
          informational (the second non-cache level — rlmwf_08
          next, the /M by design); M4 left as-is (the worker
          triple blank lines = the canonical pattern of all 8
          worker files — house style, do not strip). File
          changes: rlm_gradient.py 90 → 91 lines,
          lm_worker_gradient.py 59 → 62,
          test_lm_worker_gradient.py 118 → 142 (1 → 2 tests),
          test_rlm_gradient.py new 169 lines, pyproject.toml +1
          line. The 61-check probe re-pinned to the
          post-campaign state (tiers A–G, 0 mismatches); 5
          mirror docs written (4 new + the logistic_model.md
          9-worker update). Suite 564 → 573 (573/0/68 gated +
          573 run / 17 skipped ungated, −W error full discover
          clean, build/tmp clean).
D-095 | 2026-09-01 | binio sidecar empty-suffix guard (session
          25, Roberto's pre-OPTIMIZE question: "Cosa succede se
          il suffisso del sidecar è una stringa vuota? Viene
          sovrascritto il file dei contenuti? Se fosse così va
          introdotto un controllo che alza un errore ... cosa ne
          pensi?" → my analysis + proposal → Roberto:
          "procedi!"): VERIFIED (3-path probe, pre-fix) that with
          an empty suffix the sidecar path BE the content path
          and BOTH write paths destroy the content file —
          BinaryWriter(checksum_suffix="") truncates and
          overwrites the content with the sidecar line at
          close() (after all writes have "succeeded" — the
          nastiest part), write_sha3_256_sidecar(suffix="")
          hashes the content then replaces it with its own
          sidecar line, verify_sha3_256_sidecar(suffix="")
          raises a confusing BinaryFormatError (no data loss
          there). DECISION (as proposed, approved): ValueError
          (the argument-misuse type — the module precedent is
          the L260 "checksum service is disabled" ValueError;
          BinaryFormatError stays reserved for on-disk data) at
          ALL THREE sidecar entry points for a uniform API
          contract: BinaryWriter.__init__ fails FAST (before the
          file is opened — the pre-fix destruction happened at
          close(), after a successful-looking write),
          write_sha3_256_sidecar, verify_sha3_256_sidecar. The
          empty suffix has no legitimate use — checksum=False
          is the no-sidecar knob on the writer, and the
          standalone functions exist to create a sidecar — so
          the guard removes no functionality; the messages say
          why ("an empty suffix would overwrite the content
          file"). Zero pipeline impact: cache_manager hardcodes
          the .SHA3-256 constant (L65) and the rlm_wmaps /
          rlm_design_matrix / rlm_indexes / regab callers use
          the default suffix. 3 new tests (Sha3_256SidecarTest:
          write empty-suffix raises + content byte-identical
          after, verify empty-suffix raises; AutoChecksumTest:
          constructor raises + no file created): suite 45 →
          48/0/0. Docstrings + V16 (the guard + the pre-fix
          clobbering) + binio.md (header, components table,
          suite status, appendix re-pinned) updated.

D-096 | 2026-09-01 | OPTIMIZE bring-in analysis + fix campaign
          (session 26, Roberto's commit 1ebdd8b — lm_worker_optimize
          + rlm_optimize + the two tests + the logistic_model
          enablement, the 10th active level): analysis of the two
          modules — the only pipeline level whose "cache" is NOT a
          data class behind the store/load/is_cache_consistent trio
          but a plain CHECKPOINT DICT serialized with binio (the L56-
          57 design comment) — and the fix campaign, approved in the
          same session (Roberto: R1 keep the clipping-equivalent
          behavior, hot-restart parked as I-014 "un'ottimizzazione
          che svilupperei solo in seguito, se capiamo che ha un valore
          pratico"; R2 "mettiamo try/catch"; R3 "verifichiamo la
          checksum. Sta li per questo motivo!"; R4 _down also clears
          w_checksum + opt_info; T1-T15 "falli tutti"; M "falli
          tutti"), and applied in the same session:
          R1: the ridge gate moved INTO is_optimization_cache_
          consistent (it sat in is_optimization_status_converged) — a
          ridge_regularization change now invalidates the checkpoint
          EXACTLY like a zed-checksum change ("Starting from
          scratch"): the consistency function is now 3-gate (design
          matrix, zed, ridge — each failed gate emits its own 3×WARN
          diagnostic block; math.isclose rel_tol=1e-5 abs_tol=1e-8,
          the f32-stored value never trips it) and the status
          function is slimmed to its true job: the stored g_norm is
          re-judged against the CURRENT min_grad tolerance (a
          judgement criterion, not part of the objective — a looser
          tolerance accepts a not-converged checkpoint, a stricter
          one forces further iterations; the dead mg_is_consistent
          isclose + its TRACE log removed). The alternative — a warm
          "restart a caldo" from the checkpoint's weights under the
          new objective — is parked at I-014.
          R2: try/except (RuntimeError, binio.BinaryFormatError,
          OSError) around load_optimization_checkpoint in the
          worker's _up — a checkpoint that cannot be parsed or
          verified (e.g. truncated by a crash mid-save) is deleted
          (content + .SHA3-256 sidecar, both unlink(missing_ok=True))
          with a WARN, and the run starts from scratch instead of
          killing the worker.
          R3: load_optimization_checkpoint verifies the SHA3-256
          sidecar (binio.verify_sha3_256_sidecar) after the 2 header
          gates and BEFORE any payload is trusted — a mismatch
          raises RuntimeError "Checkpoint checksum mismatch ... does
          not match its SHA3-256 sidecar" (the sidecar "sta lì per
          questo motivo").
          R4: the worker's _down now clears ctx.fg + ctx.w_checksum +
          ctx.opt_info (was: fg only); ctx.w is deliberately KEPT —
          it is the (re-optimized) WMAPS weight vector, and the WMAPS
          cache restores the zero-initialized value when that level
          recomputes.
          T1-T15 (the two test files + source hygiene, per the 4
          mirror docs): worker test T1-T7 — the missing
          SKIP_REGAB_DB gate (the header claim was false, as in D-091
          T1 / D-093 T5), the D-085 idiom (TemporaryDirectory under
          CUSTOM_TMP_BASE first, WORKSPACE_ROOT-anchored rlm_02.json,
          defensive tearDown), the dead if-False block, the dead
          imports, the stray #: ### comment, the VACUOUS
          assertNotIn("Starting L-BFGS optimization") — opt_lbfgs
          never logs that string, so it passed trivially — replaced
          with the ACTUAL per-iteration marker "L-BFGS - [", and the
          new test_down_clears_optimize pinning R4 (fg + w_checksum +
          opt_info None, ctx.w byte-identical); worker source T8
          ("Aauthor" → "Author"), T9/T9b the dead imports (the
          worker's Path, the rlm's Tuple), T10 the factory
          @validate_call + pydantic import (all 10 worker factories
          now share the pattern); rlm source T11 the 2 no-validation
          notes above is_optimization_cache_consistent /
          is_optimization_status_converged (RLMContext is a
          TYPE_CHECKING import — the rlm_indexes L166 constraint
          class), T13 the header "rglm.py" → "rlm_optimize.py" (the
          original repo name); rlm test T14 (the header claimed "a
          live regab DB is required" although the file uses no DB —
          corrected: "no live regab DB required — pure checkpoint IO
          and cache-validation tests, as in test_rlm_gradient") +
          T15 (the 2 consistency tests renamed
          test_inconsistent_iters / test_inconsistent_m →
          ..._design_matrix_checksum / ..._zed_checksum — they test
          the checksum gates, not iters/m).
          M1-M10: worker M1 (min_grad_count unpacked but unused →
          min_grad_value, _), M2 (the trailing "state is
          unrecognized" else removed — unreachable: iters is an int,
          so iters >= max_iters or iters < max_iters always holds;
          the comment documents why), M4 ("cecksum" → "checksum" ×2
          in the worker logs), M5 (the intermediate checkpoints now
          store iters=k+1 — completed-count semantics, as the final
          save: a resume starts exactly where the interrupted run
          stopped, no redundant iteration); rlm M3 (the status
          function slimming — see R1), M6 (save_optimization_
          checkpoint fails fast with ValueError when sl/yl/rho
          differ in length — the file format is a single length
          prefix + one (s, y, rho) triple per entry and cannot
          represent asymmetric lengths; the check runs before the
          writer opens, so no file is left behind — the D-095 guard
          shape), M7 (the consistency/status functions log
          WARN/TRACE — a deviation from the silent rlm_* is_
          cache_consistent shape, resolved KEEP+DOCUMENT: those
          functions inspect the live cfg and carry the per-parameter
          diagnostics the worker's generic "Checkpoint config
          mismatch" WARN cannot), M8 (the checkpoint file name is
          config-driven — optimization.checkpoint_file, not
          rlmwf_-prefixed — intentional: a user-addressable
          checkpoint; the next cache level still takes rlmwf_08),
          M9 (the "Atomically serialize" comment dropped — there is
          no temp-file + rename; the R2 delete+scratch recovery is
          what makes a crash-mid-save recoverable); test M10
          (test_rlm_optimize expanded 4 → 19 tests in 4 classes,
          no DB, no gate: the round-trip WITH dtype pins (w/sl/yl
          float32, rho float64), the empty-history round-trip, the
          M6 fail-fast, the 2 header RuntimeError gates message-
          pinned, the R3 corrupted-content gate (last byte flipped,
          sidecar untouched), the deterministic file golden hash
          6e01ff86…1bd280 + the sidecar produced-and-matches, the 3
          helper tests (info-dict 5-keys + KeyError + the weights-
          hash golden 78a7baac…dc060 = independent sha3_256 of
          w.tobytes()), the 4 consistency branches incl. the new
          test_inconsistent_ridge (R1), the 4 status branches incl.
          the f32 round-trip and the judged-against-new-tolerance
          test (M3 semantics)).
          VERIFIED: the 92-check probe (scratch/verify_optimize.py,
          tiers A–H, re-pinned to the post-campaign state) 0
          mismatches — the deterministic checkpoint bytes + the
          binio sha3_256sum sidecar, the dtype-preserving round-
          trip, the 4 checkpoint decision paths verified LIVE on the
          10-level pipeline (completed: 2nd instance "already
          completed", zero lbfgs calls, byte-identical weights; warm-
          resume: a crafted INCOMPLETE checkpoint resumes from
          iteration 5 with the warm sl/yl/rho consumed; zed-
          inconsistent (clipping 0.01→0.02) → scratch; ridge-
          ONLY-inconsistent (R1: ridge 0.01→0.02 with an UNCHANGED
          zed checksum) → scratch, the same behavior as a clipping
          change; use_cache=False → no load but the checkpoint is
          still saved — the D-071 R1 pattern; corrupted checkpoint
          (R2+R3) → load raises, the worker deletes the file +
          sidecar, re-optimizes and re-saves a valid checkpoint), the
          f32-stored ridge/min_grad never trip the isclose gates
          (f32 relative error ~6e-8 ≪ rel_tol 1e-5/1e-3: no false
          inconsistency on a round-tripped checkpoint), and the
          GRADIENT float32 contract (D-094 R1) is consumed
          losslessly (lbfgs x0.copy() keeps float32 end-to-end —
          ctx.w is float32 after 50 iterations — so the NDArray
          [np.float32] gate of weights_compute_sha3_256_hash can
          never reject a live weight vector). The stale
          logistic_model probe re-pinned (V3c 9 → 10-worker list —
          it had gone stale at a0adc6e). Suites: 576 → 598 tests
          (598/0/71 gated + 598 run / 17 skipped ungated, −W error
          full discover clean, build/tmp clean). 5 mirror docs (4
          new + the logistic_model.md 10-worker update).

D-097 | 2026-09-02 | GENERATE bring-in analysis (session 27,
       Roberto's commit e31c061 — rlm_generate + lm_worker_
       generate + test_rlm_generate + the logistic_model
       enablement, the 11th active level): analysis findings —
       R1 (P0, blocking): lm_worker_generate L52 calls
       `ctx.get_cache_file_full_path_for_next_level()`, a method
       that does NOT exist on RLMContext (the StateMachine
       injects only `..._for_current_level`; all 8 other
       cache-using workers use it; verify_logistic_model V4a
       even pins the legacy name GONE) — the D-074 R1 trap
       re-introduced; empirically demonstrated: the rlm_02
       pipeline runs the 9 prior levels fine then dies at
       [10][GENERATE] AttributeError; the alias simulation on a
       fresh instance proves the level works end-to-end once
       renamed (file + sidecar, (6588,) float32, 2nd-instance
       cache hit, _down clearing). R2 (semantic question): the
       pattern branch assigns the frequency-weighted mean of
       the seen configs to the unseen/representative
       configurations; the trained fallback weight is logged,
       never used — Roberto's call. T1 (the load gates only the
       description — all 4 sibling data modules also gate the
       version; a version-2 file loaded SILENTLY), T2 (the 2
       no-validation notes missing — the house pattern), T3
       (the factory lacks @validate_call + the pydantic import
       — 9/10 siblings have it), T4 (test_rlm_generate thin:
       1 happy-path test vs the sibling 10-19), T5 (no
       test_lm_worker_generate at all — Roberto confirmed), T6
       (the Italian comment "AGGIUNTO ref mock" in the test),
       T7 (41 trailing-ws lines: 24 rlm_generate + 4
       lm_worker_generate + 13 test_rlm_generate), T8 (3 blank
       lines above __all__ — WITHDRAWN on re-check: 6/8 rlm_*
       data modules have exactly 3: house pattern, left as-is),
       T9 (stale probes: verify_logistic_model V3c 10 → 11
       workers, verify_optimize E1 10 → 11 / E2 5 → 4). M1 (the
       dead `f_w = w[w_min:w_max+1]` computed in every branch,
       used only for the intercept), M2 (the MOB branch
       recomputes f_wmap_mask / f_wmap — duplicates the
       feature-level lines), M3 (the RuntimeError message
       carries the literal "f.category" source-identifier
       text), M4 (the np.interp ascending precondition rests
       on rlm_wmaps' np.unique slot allocation — structurally
       guaranteed, undocumented), M5 (the dead mock field
       ctx.z in the test). | All behavior verified GREEN pre-
       campaign: the 43-check probe (scratch/verify_generate.
       py, tiers A–F — hand re-derivation of the test fixture
       golden, the data-object behavior, the live rlm_02 golden
       re-derivation: K = 6588 = 1 + 6561 (EDGE) + 27 (DIAG3),
       orbit invariance, seen-config exactness, the full
       independent re-derivation == ctx.w_dense, weighted
       means EDGE −0.022497505937226207 / DIAG3
       0.013062398455957221, total_freq 799808 = 199952 × 4,
       hash golden ec9d65453bb112bf277c79f96a86edfa9468bb01f42a2763cd82d69c5b2b15b4
       == ctx.dense_w_checksum; the pre-campaign state carried
       the 11 worklist mismatches exactly).

D-098 | 2026-09-02 | GENERATE fix campaign, CLOSED (same
       session; Roberto: R1 "esegui i fix"; R2 "il weighted
       mean è la semantica voluta ... e' un tema da
       data_science non da informatica, ci ho riflettuto a
       lungo ... durante l'inference non vedo ragioni per
       preferire il valore di fallback a quello medio per le
       configurazioni rare"; T1-T9 + M1-M5 "ok"; "Aggiungi
       anche il file test_lm_worker_generate.py con i dovuti
       tests sul worker"): R1 the one-line rename to
       `get_cache_file_full_path_for_current_level()` (the
       D-074 R1 trap closed). R2 RULED + documented in code
       (rlm_generate L188-197): at inference the
       unseen/fallback configurations inherit the frequency-
       weighted mean of the seen configs, NOT the trained
       fallback weight — the fallback slot is a SINGLE
       learnable representative: during training it keeps the
       loss well-defined and shrinks the rare configurations
       (overfitting control); at inference the regularized
       mean is the plug-in estimate of the expected pattern
       contribution under the training distribution, while the
       fallback weight is a loss proxy, noisy for the rare
       configurations; the weight stays in the logs for
       transparency. In rlm_02 (frequency_cut_off 1) there is
       no fallback slot at all (fallback = −1), so the
       weighted mean is the active behavior there. T1: the
       version gate added to rlm_generate_load_from_file (the
       4-sibling shape: expected_description / expected_
       version variables, "File version mismatch: found {v},
       expected 1"; the 2 pinned messages unchanged). T2: the
       2 house no-validation notes (L99 / L104). T3: the
       factory @validate_call + pydantic import (all 10 worker
       factories now share the pattern). T4: test_rlm_generate
       expanded 1 → 14 tests / 4 classes (no DB, no gate: the
       kept 3-feature mock golden, the unknown-category
       RuntimeError message-pinned "The feature category is
       unknown: 9", the empty-MOB zeros + exactly-one-WARN,
       the 2 consistency branches, the 6 IO tests incl. the 3
       header gates message-pinned + the hash golden
       460c993da80d5ff6fd5581660d71be905c482eadc5520718b56051f6545cd07a,
       the 3 init validations). T5: test_lm_worker_generate.py
       ADDED (1 class / 3 tests, all DB-gated — the setUp moves
       through OPTIMIZE on a fresh base dir, so a live DB is
       required; the D-085 idiom, rlm_02: the first-run golden
       (6588,) float32 + hash golden ec9d6545…b15b4 + the
       sidecar verify + "Executing heavy computation", the
       2nd-instance cache hit "Cache successfully loaded and
       validated" with no recompute, the _down clearing pin).
       T6: the Italian comment → English. T7: the 41 ws lines
       stripped (24 + 4 + 13). T8: WITHDRAWN as a false
       positive (house pattern — 6/8 rlm_* data modules have
       the triple blank above __all__; the 6/8 split is the
       3-blank majority, kept). T9: the stale probes re-pinned
       (verify_logistic_model V3c 10 → 11 incl. the session-27
       header note — 35 checks; verify_optimize E1 10 → 11 /
       E2 5 → 4 — 92 checks). M1-M5 fixed as analyzed (f_w
       into the intercept branch L138; the MOB duplicate
       removed; the msg "The feature category is unknown:
       {f.category}"; the np.interp note L156-158; ctx.z gone).
       | VERIFIED: the 43-check probe 0 mismatches (the live E
       tier: the pipeline reaches GENERATE, the golden
       re-derivation, the 2nd-instance cache hit, the _down
       clearing) — 2 probe self-defects found post-campaign
       and fixed (A2/A3 checked the literal "TYPE_CHECKING" in
       the note — the house note never mentions it → the checks
       now match the house note text; A4 expected the
       expected_version variable → the code now uses the
       4-sibling shape, better than bending the probe);
       test_rlm_generate 14/0/0 (no DB); test_lm_worker_
       generate 3/0/0 live (10.5 s) + 3/0/3 gated; full
       discover 599 → 615 tests (615/0/74 gated + 615 run / 17
       skipped ungated (35.8 s), −W error full discover clean
       (35.0 s), build/tmp clean). 5 mirror docs (4 new + the
       logistic_model.md 11-worker update, 6 spots). 2 commits
       (code+docs, then notes).

D-099 | 2026-09-02 | VLD_POSITIONS bring-in analysis (session 28,
       Roberto's commit ede2efe — lm_worker_vld_positions + the
       logistic_model enablement (import L51 + worker-list entry
       L217), the 12th active level; 3 remaining commented
       imports (validate, analytics, save); RLMContext's 4 vld_*
       fields pre-declared at L146-149, the future vld_metrics /
       analytics_report at L152/155; the rlm_02/01/00 fixtures all
       carry the validation_data_set block {bid [8], status
       CMS+CMR}): the worker is the POSITIONS TWIN over the
       validation data set — it REUSES load_from_db +
       is_cache_consistent from lm_worker_positions (the keyword
       bid/status overrides; the DB connection + ec come from the
       shared regab_data_set block) with the uniform 7-kwargs
       cache_manager wiring; the flat cache file is
       rlmwf_11_VLD_POSITIONS.dat + .SHA3-256 (the slot predicted
       in D-097/D-098: "the next cache level takes rlmwf_11").
       Analysis findings — R1 (P0, blocking, the 2nd occurrence):
       lm_worker_vld_positions L62 calls
       `ctx.get_cache_file_full_path_for_next_level()`, a method
       that does NOT exist on RLMContext (the StateMachine injects
       only `..._for_current_level`, a per-instance attribute,
       state_machine L190; verify_logistic_model V4a pins the
       legacy name GONE) — the D-074 R1 trap re-introduced, exactly
       as in lm_worker_generate (D-097 R1, fixed D-098);
       empirically demonstrated: the rlm_02 pipeline runs the 10
       prior levels fine then dies at [11][VLD_POSITIONS] with
       "Error in VLD_POSITIONS during up: 'RLMContext' object has
       no attribute 'get_cache_file_full_path_for_next_level'";
       the alias simulation (binding _for_next_level to
       _for_current_level on a fresh instance, same base dir)
       proves the level otherwise works end-to-end: rlmwf_11_
       VLD_POSITIONS.dat + .SHA3-256 exist + verify, vld_positions
       (200,2) u64 structured, int8 game values in [−58, 56], the
       golden stats count 200 / mean 3.64 / std
       23.809880302093077 / variance 566.9104, vld_rds_checksum
       e8087903437d9d42d64499626f5b4426505d3b9538539e19fb8f45dc9c9f4c48
       (distinct from the training 32da0ed3…), the 2nd-instance
       cache hit ("Cache successfully loaded and validated", no
       "Extracted"), _down clears all 4 fields. T1 (the factory
       L106 lacks @validate_call + the pydantic import — all 10
       sibling worker factories have it: D-080 M4 / D-082 M1 /
       D-084 M1 / D-090 T2 / D-092 T2 / D-094 T2 / D-096 T10 /
       D-098 T3 pattern). T2 (5 dead imports: `from pathlib
       import Path` L33 — no Path use, the cache_path comes from
       the injected closure; RegabDataSet / RegabDBConnection /
       regab_extract_data_set_from_db L37-39 — the file delegates
       extraction to lm_worker_positions.load_from_db, which uses
       all three internally; only regab_load_data_set_from_file +
       regab_store_data_set_to_file are directly needed). T3 (the
       load_fn L64 is the raw regab_load_data_set_from_file —
       checksum defaults True → the sidecar is verified twice on
       every cache hit; the house shape is the checksum=False
       lambda, D-080 M4, as in lm_worker_positions). T4 (3 ws-
       only lines in the _up/_down bodies, L76/L92/L95; the import-
       block trailing ws L37/38/40 + the license header stay — the
       D-078 M3 / D-080 M3 house scope, as in lm_worker_positions
       post-campaign). T5 (no test file at all — the bring-in
       ships zero tests; propose creating test_lm_worker_
       vld_positions.py per Roberto's call, the D-098 T5 pattern).
       M1 (informational): the vld query inherits ec from
       ctx.cfg.regab_data_set (the training block) —
       ValidationDataSetConfig declares only bid + status (no ec
       field); the shared ec (20) gates BOTH the extraction
       (load_from_db) and the consistency check — consistent across
       the two call sites (no trap), but the validation block
       cannot override ec — document. M2 (informational): the
       unpacked cache_hit is unused (L61) — the identical
       lm_worker_positions L59 shape, keep. M3 (positive): _down
       clears ALL FOUR fields (vld_positions / vld_game_values /
       vld_rds_checksum / vld_pop_stats) — the house shape, no gap
       (contrast D-096 R4). | All behavior verified GREEN pre-
       campaign via the 31-check probe (scratch/verify_vld_
       positions.py, tiers A–D; the pre-campaign state carries the
       6 worklist mismatches exactly: A2 the _for_current_level
       naming, A3 the factory gate, A4 the load_fn shape, A5 the
       dead imports, A6 the ws lines, C1 the live crash; the D
       tier pins the override semantics without a DB: full match
       → True, bid / status / ec / connection mismatch → False, no
       override → the TRAINING cfg params are used → False, i.e.
       the worker must pass the vld bid/status explicitly — it
       does). The 3 stale probes re-pinned: verify_logistic_model
       V3c 11 → 12 workers + the session-28 header note (35
       checks, 0 mismatches); verify_optimize E1 11 → 12 / E2 4 →
       3 (92 checks, 0 mismatches); verify_generate F2 4 → 3
       commented imports / F3 10 → 11 factory calls (43 checks, 0
       mismatches). Suite baseline UNCHANGED: 615/0/74 gated (2.5
       s) — no new tests, none of the 14 test_logistic_model
       tests pins the worker count. OPEN awaiting Roberto's call:
       R1 + T1-T5 + M1-M3 (the fix campaign will be D-100).

D-100 | 2026-09-02 | VLD_POSITIONS fix campaign, CLOSED (same
       session 28; Roberto: "T1 - T5: OK, M1 - M3: OK,
       Procedi, grazie."): R1 RESOLVED — the one-line rename
       (lm_worker_vld_positions L62/L65 →
       get_cache_file_full_path_for_current_level(); the 2nd
       occurrence of the D-074 R1 trap, the 1st in
       lm_worker_generate D-097 R1; post-fix the rlm_02
       pipeline reaches VLD_POSITIONS cleanly — file + sidecar,
       (200,2) u64 positions, 2nd-instance cache hit). T1 the
       factory @validate_call + pydantic import (all 11 worker
       factories now uniform). T2 the 5 dead imports removed
       (the pathlib Path + RegabDataSet + RegabDBConnection +
       regab_extract_data_set_from_db — the file delegates
       extraction to lm_worker_positions.load_from_db, which
       uses all three internally). T3 the load_fn now the
       checksum=False lambda (the D-080 M4 shape — the
       redundant double sidecar verify on every cache hit is
       gone). T4 the 3 ws-only lines stripped (L76/L92/L95);
       the import-block trailing ws (the regab_load_data_set_
       from_file line) + the license header stay — the D-078
       M3 / D-080 M3 house scope, as in lm_worker_positions.
       T5 test_lm_worker_vld_positions.py ADDED (1 class / 3
       tests, all DB-gated, the D-085 idiom, rlm_02, setUp →
       GENERATE step 10: the first-run golden (200 positions,
       the structured dtype names, vld_rds_checksum
       e8087903…f4c48, pop_stats count 200 / mean 3.64, the
       flat rlmwf_11_VLD_POSITIONS.dat + .SHA3-256 + the
       sidecar verify, "Executing heavy computation"), the
       2nd-instance cache hit ("Cache successfully loaded and
       validated", no "Executing heavy computation",
       array_equal + checksums equal), the _down pin (all four
       fields cleared on the move back to step 10)). M1
       DOCUMENTED — the vld query inherits ec from
       ctx.cfg.regab_data_set (the training block;
       ValidationDataSetConfig declares only bid + status) —
       the _up note L58-61. M2 KEEP (the unpacked cache_hit
       unused — the identical lm_worker_positions L59 shape,
       reported-only). M3 POSITIVE (the _down scope clears all
       four fields — no gap, contrast D-096 R4). | VERIFIED:
       the 31-check probe (scratch/verify_vld_positions.py,
       tiers A–D) re-pinned to the post-campaign state, 0
       mismatches (the live C tier: the pipeline reaches
       VLD_POSITIONS with NO alias fallback, the golden
       re-derivation, the 2nd-instance cache hit, the _down
       clearing); the 3 re-pinned probes stay at 0 mismatches
       (verify_logistic_model 35 checks — V3c the 12-worker
       list; verify_optimize 92 checks — E1 12 / E2 3;
       verify_generate 43 checks — F2 3 commented / F3 11
       calls). test_lm_worker_vld_positions 3/0/0 live (8.5
       s) + 3/0/3 gated. Full discover 615 → 618 tests
       (618/0/77 gated (2.6 s) + 618 run / 17 skipped ungated
       (23.6 s), −W error full discover clean (23.8 s),
       build/tmp clean). 3 mirror docs (lm_worker_vld_
       positions.md + test/test_lm_worker_vld_positions.md
       new, post-campaign state; the logistic_model.md
       12-worker update, 6 spots: header, state-per-Roberto,
       pipeline shape, the V3c sentence, the 2 appendix
       lines). File sizes: lm_worker_vld_positions 108 → 112;
       test_lm_worker_vld_positions 195 lines new. 2 commits
       (code+docs, then notes).

D-101 | 2026-09-02 | VALIDATE bring-in analysis (session 28,
        Roberto's commit 536eadc — lm_worker_validate + rlm_validate
        + the logistic_model enablement (import L52 + worker-list
        entry L218), the 13th active level; 2 remaining commented
        imports (analytics, save); the RLMContext.vld_metrics field
        pre-declared at L152): the first bring-in with a dedicated
        DATA module (rlm_validate.py) alongside the worker. VALIDATE
        has NO cache file (no cache_manager use — pure compute, like
        FEATURES/ZED/GRADIENT; the rlmwf_12 slot stays unused; the
        _down clears the single vld_metrics field the _up sets —
        scope complete, positive). validate_model reuses the
        cross-level artifacts: ctx.vld_positions / ctx.vld_game_
        values (VLD_POSITIONS), ctx.feature_set (FEATURES),
        ctx.iwmap_feature_offset (WMAPS), ctx.w_dense (GENERATE),
        ctx.y2z / ctx.z2y (ZED — zed_fun_factory, the float32 cast
        BEFORE the affine: no int8 overflow at y=64), sigmoid
        (imported from rlm_gradient — defined + exported there).
        The dense-mapping idiom differs from rlm_generate's per-
        feature start/end loop (np.repeat offsets + fancy indexing +
        np.sum axis=1 — both valid, idiom divergence noted,
        report-only). Analysis findings — R1: rlm_validate L47
        `-> Dict[str, Any]` — `Any` is NEVER imported (a latent
        NameError under get_type_hints, PEP 563 masks it; nothing in
        src/ calls get_type_hints on validate_model today — the
        D-074 R2 class; fix = the `Any` import or the annotation
        change). Unlike D-097/D-099 there is NO live crash: the
        rlm_02 pipeline reaches VALIDATE step 12 cleanly (the level
        has no cache-path call — the D-074 R1 trap does not apply
        this time). T1: the worker factory has NO @validate_call +
        no pydantic import (all 11 sibling worker factories uniform
        — the D-100 T1 pattern). T2: the dead imports — the worker
        `numpy as np` (never used), rlm_validate `RegabDBConnection
        + regab_extract_data_set_from_db` (never used — the data
        comes from the ctx.vld_* fields set by VLD_POSITIONS, not a
        DB extraction). T3: the rlm_validate L2 header says
        `# rlm_config_schemas.py` (copy-paste). T4: the ws lines —
        the worker L48/L49/L51 (2 ws-only + the trailing on the
        validate_model call), rlm_validate 27 lines (the docstring
        trailing ws + the docstring ws-only lines + L108/L118; the
        license header stays — the house scope). T5: no test file
        (propose test_lm_worker_validate.py per Roberto's call, the
        D-100 T5 pattern: 1 class / 3 tests, all DB-gated, the D-085
        idiom, rlm_02, setUp → VLD_POSITIONS step 11: the first-run
        6-metric goldens + the log lines, the 2nd-instance
        determinism (no VALIDATE cache file — the metrics recompute
        while the 6 cache_manager levels hit), the _down pin). M1:
        the worker's L57 ratio log line
        `metrics['vld_rmse_y']/metrics['vld_mae_y']` divides by
        vld_mae_y WITHOUT a zero guard — a latent
        ZeroDivisionError on a perfect Y-space fit (demonstrated
        live in the probe D tier: a hand-built ctx with mae_y == 0
        crashes the _up log line); the docstring's RMSE/MAE = 1.253
        normal-distribution indicator makes the ratio meaningful.
        M2: the unpacked vld_P (L112) is unused — keep or
        underscore. M3 (report-only): the returned dict has exactly
        6 keys (vld_loss, vld_mse_z, vld_mae_z, vld_mae_y,
        vld_rmse_y — all float() casts — + vld_samples int) and
        OMITS vld_mse_y (computed at L142 only to feed rmse_y; the
        worker logs the 5 metrics + the ratio, never MSE(y)) — by
        design or a missing key is Roberto's call. | All behavior
        verified GREEN pre-campaign via the 28-check probe
        (scratch/verify_validate.py, tiers A–D; the pre-campaign
        state carries the 8 worklist mismatches exactly: A2 the
        factory gate, A3 the worker dead import, A4 the data dead
        import, A5 the unimported Any, A6 the header name, A7a/A7b
        the ws lines, A8 the missing test file): the rlm_02 pipeline
        reaches VALIDATE (step 12) with NO crash, the 6-metric
        goldens (loss 0.00700794393196702, mse_z 0.01401588786393404,
        mae_z 0.09311295300722122, mae_y 12.161691665649414, rmse_y
        15.46301555633545, samples 200; RMSE/MAE 1.27 — the
        docstring's normal-distribution indicator is 1.253; the vld
        loss ≈ the training final loss 7.1250e-03 — no overfitting
        signal), the HIGH-verbosity log lines, the no-rlmwf_12-file
        fact, the 2nd-instance determinism (identical metrics, the 6
        cache_manager levels hit — CONFIG + the OPTIMIZE checkpoint
        have their own load flows), the _down clearing, and the D
        tier re-derives the full metric math on a hand-computed 2-
        position case (loss 0.0625 / mse_z 0.125 / mae_z 0.25 /
        mae_y 32.0 / rmse_y sqrt(2048) / samples 2) + the float()
        types + the M1 ZeroDivisionError demo. The 4 stale probes
        re-pinned: verify_logistic_model V3c 12 → 13 workers + the
        session-28 header note (35 checks, 0 mismatches);
        verify_optimize E1 12 → 13 / E2 3 → 2 (92 checks, 0
        mismatches); verify_generate F2 3 → 2 commented imports /
        F3 12 → 13 levels / 11 → 12 calls (43 checks, 0
        mismatches); verify_vld_positions B2 3 → 2 / B3 12 → 13
        (31 checks, 0 mismatches). Suite 618 → 619 (the last muted
        test _test_move_to_step_by_string restored 887880e — the
        execution of the approved D-073/D-075 T3 plan, no new D
        number): 619/0/77 gated (2.5 s) + 619 run / 17 skipped
        ungated (23.9 s), −W error full discover clean (2.5 s),
        build/tmp clean. OPEN awaiting Roberto's call: R1 + T1-T5 +
        M1-M3 (the fix campaign will be D-102).
D-102 | 2026-09-02 | VALIDATE fix campaign (session 28, Roberto:
        "R1: OK, T1: OK, T2: OK, T3, T4: OK, T5: OK, M1-M3: OK.
        Procedi." — the D-101 worklist in full):
        R1: `from typing import TYPE_CHECKING, Any, Dict` in
        rlm_validate (the unimported `Any` in the
        `Dict[str, Any]` return annotation — the PEP 563-masked
        latent NameError under get_type_hints, the D-074 R2 class;
        NO live crash: nothing in src/ calls get_type_hints on
        validate_model, and the level has no cache-path call, so
        the pipeline reached step 12 cleanly). T1: the factory
        lm_worker_validate() got @validate_call
        (config=ConfigDict(arbitrary_types_allowed=True)) + the
        pydantic import — all 12 active worker factories now share
        the pattern (the D-092/D-098/D-100 T1 convention). T2: the
        dead imports removed (the worker's `import numpy as np`
        replaced by the pydantic line; the rlm_validate
        `RegabDBConnection, regab_extract_data_set_from_db` pair —
        the data comes from ctx.vld_positions / ctx.vld_game_values
        set by VLD_POSITIONS, never from a DB call). T3: the
        rlm_validate header `# rlm_config_schemas.py` →
        `# rlm_validate.py` (copy-paste). T4: the 30 ws lines
        stripped (worker L48/49/51 — 2 ws-only + 1 trailing on the
        validate_model call — + rlm_validate 27, docstring
        trailing/ws-only included; the license headers untouched).
        T5: test_lm_worker_validate.py ADDED — 1 class / 3 tests /
        no PERF, all DB-gated (gate first in setUp; the setUp
        moves to VLD_POSITIONS step 11 on a fresh base dir, which
        runs the whole 12-level chain, so a live DB is required),
        the D-085 idiom from day one (TemporaryDirectory under the
        shared CUSTOM_TMP_BASE, WORKSPACE_ROOT-anchored
        rlm_02.json, defensive tearDown, the twolm.test.paths
        import): test_validate_model_goldens (the first run to
        VALIDATE step 12, worker name pinned: the pre-state
        vld_metrics None, the 7-key dict pinned EXACTLY — loss
        0.00700794393196702, mse_z 0.01401588786393404, mae_z
        0.09311295300722122, mae_y 12.161691665649414, mse_y
        239.10484313964844, rmse_y 15.46301555633545, samples
        200 — + the 7 INFO log lines incl. RMSE/MAE 1.27),
        test_second_instance_deterministic (a 2nd instance on the
        same base dir: identical vld_metrics — VALIDATE has no
        cache file, so determinism is the pin — + exactly 6 "Cache
        successfully loaded and validated" hits (the 6
        cache_manager levels; CONFIG + the OPTIMIZE checkpoint
        have their own load flows), NO "Extracted" / NO
        "established successfully"), test_down_clears_vld_metrics
        (back to step 11 VLD_POSITIONS: vld_metrics None — the
        single field _up sets). M1: the worker's RMSE/MAE ratio
        log line zero-guarded (a perfect Y-space fit, vld_mae_y
        == 0 — pre-campaign it RAISED ZeroDivisionError,
        demonstrated live (probe D3) — now logs the
        "n/a (vld_mae_y is 0 — perfect Y-space fit)" line).
        M2: `vld_M, _ = vld_indexes.shape` (the unused vld_P
        underscore-unpacked, the D-096 M1 pattern). M3:
        `vld_mse_y` added to the returned dict (7 keys, between
        vld_mae_y and vld_rmse_y — Roberto's call: the computed
        mse_y belongs in the dict, not only as the rmse_y feeder).
        File sizes: lm_worker_validate 71 → 75 lines (pydantic
        import + decorator + guard + 3 ws emptied); rlm_validate
        152 → 152 (net 0: −1 import + 1 dict line, 27 ws
        stripped in place); test_lm_worker_validate 179 lines new.
        The 28-check probe re-pinned post-campaign (A12 6 → 7
        keys, A13 the underscore form, C2 the mse_y golden, C4
        rmse_y² ≈ mse_y at rel_tol 1e-6 — float32-derived, the
        round-trip gap is 2.9e-8, D1 mse_y 2048.0, D3 the n/a
        branch instead of the raise): 0 mismatches, gated + live
        (the C tier re-verified the full live chain incl. the new
        golden). 3 mirror docs (2 new: lm_worker_validate.md +
        rlm_validate.md, + the test doc; the logistic_model.md
        13-worker update, 6 spots: header, state-per-Roberto,
        pipeline shape, V3c, appendix imports L41-52 active /
        L53-54 commented, appendix worker list L207-218 /
        L219-220). Report-only carried, no number: the
        dense-mapping idiom divergence (np.repeat + fancy indexing
        + np.sum vs rlm_generate's per-feature loop — both
        valid); the VALIDATE no-cache-by-design (confirmed
        intent, rlmwf_12 stays unused like 03/07/08). Suite 619 →
        622: 622/0/80 gated (2.6 s) + 622 run / 17 skipped
        ungated (30.6 s) + −W error full discover clean (31.2 s),
        build/tmp clean. VALIDATE module CLOSED (worker + data +
        test). Next bring-in: lm_worker_analytics (the next
        commented entry, logistic_model L53 / worker list L219),
        then lm_worker_save (L54 / L220). |
D-103 | 2026-09-02 | ANALYTICS bring-in + fix campaign (session 28,
        Roberto: "T1: OK, T2: OK, T4: OK, T5: OK, T6: OK, M1-M3:
        OK. Procedi!" — the D-103 worklist; T3 verified no-action,
        both headers already carry their own names):
        Bring-in (96dacb5, Roberto): lm_worker_analytics +
        rlm_analytics — the 14th active level, the 2nd bring-in
        with a dedicated data module (function-only like
        rlm_gradient / rlm_validate: 3 public functions + 3
        private helpers, no data class, no cache_manager — the
        5th non-cache level, the rlmwf_12 slot stays unused like
        03/07/08). Analysis: no P0 (the schema AnalyticsConfig is
        non-optional with a default_factory → ctx.cfg.analytics
        always exists → the worker's L60 direct access is safe);
        O1-O6 report-only, O1 (the mixed-representation
        Generalization Gap) quantified: the TRAINING column is the
        COMPRESSED forward pass (ctx.w over ctx.design_matrix —
        what lbfgs trained), the VALIDATION column the DENSE
        forward pass (ctx.w_dense); the two differ only for
        configurations whose orbit is unseen in training (the
        dense substitution: pattern orbit frequency-weighted mean
        / mobility np.interp — D-098 R2); measured on rlm_02: 0
        of the 1600 vld instances (200 × 8) hit an unseen orbit
        (EDGE seen configs 2963/6561, DIAG3 18/27 cover all
        touched orbits) → the −0.13 gap is a clean train-vs-vld
        data difference on this fixture (on sparser datasets it
        would additionally carry the substitution delta); the
        compressed design-matrix path RAISES on any −1 (the
        "should never happen" guard — the training pindexes are
        all seen by construction), which is exactly why VALIDATE
        must use the dense path.
        T1: the factory lm_worker_analytics() got @validate_call
        (config=ConfigDict(arbitrary_types_allowed=True)) + the
        pydantic import — all 13 worker factories now share the
        pattern. T2: the dead imports removed (the worker's
        `from pathlib import Path`; the rlm_analytics `import sys`
        + the unused `Optional`/`List` in the typing line). T3:
        verified no-action. T4: the 45 ws lines stripped (worker
        6 — L47/50/53/57 ws-only + L63/65 trailing — +
        rlm_analytics 39, docstring trailing/ws-only included;
        the license headers untouched). T5:
        test_lm_worker_analytics.py ADDED — 2 classes / 4 tests /
        no PERF, all DB-gated (gate first in setUp; the setUp
        moves to VALIDATE step 12 on a fresh base dir, which runs
        the whole 13-level chain, so a live DB is required), the
        D-085 idiom, the module-level _masked_report_hash helper
        (the file report embeds datetime.now() → the date-masked
        sha3_256 is the stable golden): class 1
        TestLMWorkerAnalytics (rlm_02, setUp → VALIDATE step 12):
        test_analytics_report_goldens (pre-state None/None; the
        7-key dict pinned EXACTLY — train_mae_y
        12.346794566613694, train_rmse_y 15.58872172931622,
        train_loss 0.00712497066706419 (= opt_info['f'], the
        OPTIMIZE final objective, ridge-inclusive), train_samples
        199952, pop_mae_y 21.729816221648974, pop_rmse_y
        26.40637507956623, pop_loss 0.020437248051166534; the
        console report pins incl. "Total Parameters (W) : 2,981"
        / "Dense Parameters (K) : 6,588" / "Generalization Gap
        (RMSE) : -0.13"; the file report: EDGE rows + DIAG3
        omitted (1 omitted line), no "MOBILITY FEATURE:" line,
        date-masked hash 9b97746c69436fc23fd4f7a06274174d66ed1d0c
        b8467619b78a409e7f743c66; the log lines pinned),
        test_second_instance_deterministic (identical metrics +
        report, exactly 6 "Cache successfully loaded and
        validated" hits, no "Extracted" / "established
        successfully"), test_down_clears_analytics_attributes
        (back to step 12: both None; the file remains on disk —
        artifact semantics, _down does not unlink). Class 2
        TestLMWorkerAnalyticsMobility (rlm_01, setUp → VALIDATE
        step 12): test_mobility_and_pattern_tables (the train
        goldens — mae 9.874833279184258e-05, rmse
        0.00013206900478667877, loss 4.704681197571781e-13,
        samples 10, pop_mae 15.6, pop_rmse 18.39565166010707,
        pop_loss 0.009125067852437496; "MOBILITY FEATURE: LMC
        (fid=1)", "PATTERN FEATURE: DIAG3 (fid=2)", "PATTERN
        FEATURE: CORE (fid=3)", exactly 1 "(Table rows omitted"
        line, date-masked hash 77fa815ada656152b5f8f893134624d5d0
        23ffc66e9c81e4fcda9a1ecc0c083d; the logs "Optimization
        Status : CONVERGED_MIN_GRAD (16 iters)" + "Generalization
        Gap (RMSE) : 27.22" — the 10-sample model overfits).
        4/0/0 live (7.3 s), 4/0/4 gated. T6:
        src/twolm/test/data/rlm_01.json — analytics.detailed_
        report ["DIAG3"] → ["DIAG3", "LMC"] (so the 65-row LMC
        mobility table prints; no other rlm_01-based golden
        affected — the analytics block is consumed only by the
        ANALYTICS level). M1: RLMContext pre-declares
        `train_metrics: Any = None` (L155, the "Analytic
        attributes" comment now covers both fields; the worker
        set it as an ad-hoc dataclass attribute — works, no
        __slots__ — but every other blackboard field is
        pre-declared (the D-099 idiom), and the worker's own
        comment says the SAVE worker will consume it later). M2:
        compute_training_metrics annotation Dict[str, float] →
        Dict[str, float | int] (train_samples is an int). M3: the
        hasattr(ctx.cfg, 'analytics') guard in format_file_report
        (4 lines) replaced by the direct
        `detailed_report_list = ctx.cfg.analytics.detailed_report`
        (the schema's default factory makes the field always
        exist and non-None — dead-code guard). File sizes:
        lm_worker_analytics 78 → 80 (pydantic import + decorator,
        6 ws emptied in place); rlm_analytics 456 → 453 (−1
        `import sys`, −2 net on the M3 guard, 39 ws stripped);
        logistic_model 224 → 225 (the M1 field); rlm_01.json the
        detailed_report line; test 304 lines new. The 33-check
        probe (scratch/verify_analytics.py, tiers A12 / B5 / C11 /
        D3 — the D tier the hand-computed 2-position case: mae
        10.0 / rmse 10.0 / train_loss 0.123 = opt_info['f'] /
        pop_loss 0.0030517578125, the opt_info-None branch, the
        console N/A branch 15 lines / 3×N/A) reported pre-campaign
        exactly the 7 worklist mismatches (A2, A3, A4, A6a, A6b,
        A11, A12); post D-103 all 33 pass (gated + live). The
        35-check logistic_model probe re-pinned V3c 13 → 14
        workers: 0 mismatches. 3 mirror docs (2 new:
        lm_worker_analytics.md + rlm_analytics.md + the test doc;
        the logistic_model.md 14-worker update: header,
        state-per-Roberto, pipeline shape, V3c, the 39-field
        re-pin with the M1 line-shift cascaded through the
        appendix line numbers, appendix imports L41-53 active /
        L54 commented, appendix worker list L208-220 / L221).
        Report-only carried, no number: the TRAINING "Loss
        (MSE/2)" cell is opt_info['f'] — the ridge-inclusive
        final objective — while the VALIDATION/POPULATION cells
        are pure 0.5·mean(rn²) (intentional asymmetry, documented
        in rlm_analytics.md); the ONE INFO log line from the data
        module (compute_training_metrics) — consistent with
        rlm_validate; the 3 public data functions carry no
        @validate_call (the rlm_indexes-L166 TYPE_CHECKING class,
        consistent with rlm_validate, D-102 approved without
        one); rlm_02's detailed_report lists ELLE/LMC — names
        absent from that fixture (harmless; the block looks
        copied — the fixture is Roberto's); the report file
        overwritten per run and never unlinked by _down (artifact
        semantics, like the OPTIMIZE checkpoint). Suite 622 →
        626: 626/0/84 gated (2.8 s) + 626 run / 17 skipped
        ungated (39.1 s) + −W error full discover clean (38.9 s),
        build/tmp clean. ANALYTICS module CLOSED (worker + data +
        test). Next bring-in: lm_worker_save (logistic_model L54
        / worker list L221) — the LAST commented entry; the
        pipeline then reaches 15 levels, and ctx.analytics_report
        / ctx.train_metrics are pre-stored "if needed by the SAVE
        worker later". |
D-104 | 2026-09-02 | SAVE bring-in + fix campaign (session 29,
         Roberto: "T1: OK / T2: OK / T4: OK / T5: OK / T6: OK /
         M1: OK ... O4: OK / O5: OK ... Procedi!" — the D-104
         worklist; T3 verified no-action, T7 = the house flow):
         Bring-in (fe506c6, Roberto): lm_worker_save +
         model_weights + rlm_client + test_lm_worker_full_chain +
         the rlm_03/rlm_04 fixtures — the 15th and LAST active
         level; the bring-in itself uncommented the final 2 lines
         (import L54 + worker-list entry L221): 15/15 workers
         active, 0 commented imports/entries — the pipeline is
         COMPLETE, there is no next bring-in.
         The O1 correction (Roberto, the crux of the session): my
         D-103 O1 stated forward_dense(training) ≡
         forward_compressed(training) — WRONG as a general
         statement. Roberto: "it's true only when there is no
         frequency_cut_off" (he first wrote "clipping", then
         corrected himself). VERIFIED MEASURED: the two passes
         differ exactly on training positions touching a
         below-cutoff ("IC") configuration — in the COMPRESSED
         path such configs map to the per-feature TRAINED fallback
         weight (wmap row (fid, -1, ...)); in the DENSE path
         (w_dense) they get the SUBSTITUTION value (frequency-
         weighted orbit mean for patterns, np.interp for mobility —
         rlm_generate L189-196). Measured: rlm_04 (cut 10): 1923
         of 199932 training positions differ (373 EDGE configs in
         wmap_fallback with freq < 10); max |Δy| 31.56, mean 4.98.
         rlm_01 (cut 2): 5 of 10. rlm_02/rlm_03 (cut 1): identical
         by construction (every seen config confirmed). My earlier
         "12/12 bit-equal EF" evidence was the client (dense) vs
         my own dense formula — a tautology that never compared the
         compressed pass; corrected. General rule now: dense ≡
         compressed on training data iff every seen configuration
         is confirmed (cut 1, or all frequencies ≥ cut).
         M2 (the D-103 3-metric-table proposal) REFRAMED: with
         the cut>1 distinction, the TRAINING(compressed) |
         TRAINING-DENSE (the shipped inference rules) | VALIDATION
         (dense) table is genuinely informative on cut>1 datasets
         — the middle column measures the substitution's impact on
         training data itself, and vld_dense − train_dense is the
         pure generalization gap. PENDING Roberto's decision
         (D-105 candidate): small rlm_analytics change, re-pins
         the D-103 analytics goldens.
         Naming (Roberto, report-only): "A2050" is a legacy
         production naming convention, not a test bug — A2xxx is
         the endgame-solver production model family (A2 + ec*10;
         A2050 = ec 20; production runs A2050, A2150, A2250, ...
         generating the resolved positions). No rename of the
         test classes (accepted, O3).
         T1: the lm_worker_save() factory got @validate_call
         (config=ConfigDict(arbitrary_types_allowed=True)) + the
         pydantic import — all 14 worker factories now share the
         uniform pattern (D-092/D-098/D-100/D-103 T1 convention
         completed). Also proved: SKIP_REGAB_DB is a TEST-SIDE
         convention only — no production code reads it; pre-
         campaign the ungated A2030 test passed (ran live) in
         "gated" mode and would ERROR on a DB-less machine.
         T2: dead imports removed (the worker's `from pathlib
         import Path`; the client's `model_weights_read_file`;
         the test's `numpy.testing as nptest`). T4: the 41 ws
         lines stripped (worker 2, model_weights 2, client 5,
         test 37 — 31 ws-only + 6 code-line trailing). T5: the
         test file got the D-085 idiom — the SKIP_REGAB_DB gate
         FIRST in both setUps (test_regab pattern),
         WORKSPACE_ROOT/CUSTOM_TMP_BASE (the bring-in's CWD-
         relative './build/tmp' + relative json paths were CWD-
         locked), the stray "#: ###" removed, the How-to-run
         block added. T6: the 3-4-significant-digit pins replaced
         by exact assertEqual goldens (the D-096 house pattern):
         A2030/rlm_04 — vld 7 + train 7 + pop 4 + opt 5-key +
         file 21603 B sha3 bcf8d918...abb + sidecar + full
         read-back (tps f32 truncations pinned as distinct
         values; fs hash ec4f1537...; iwmap [0,1,66,6627];
         w_dense (6627,) f32 sha3 7ecdeba6...f4f37) + EF 6
         training positions bit-exact + the O4 pin (O4 accepted
         by Roberto): ef(vld_positions[42]) =
         11.932792663574219 — rlm_04's cut 10 + bid [5]
         validation make that position exercise the w_dense
         substitution path end-to-end; NEW: the 2nd-instance
         determinism test (byte-identical file + 6 "Cache
         successfully loaded and validated" hits — 7 cache files,
         CONFIG re-stores its snapshot, a 'stored' line not a
         'hit'). A2050/rlm_03 — vld 7 + train 7 + pop 4 + opt
         (397 iters) + file 515042 B sha3 3ad18058...ff4 +
         sidecar + read-back (fs hash 2c8bb32b...; 14-entry
         boundary array; w_dense (167331,) f32 sha3
         a012689f...27fc) + EF 6 training positions bit-exact
         (cut 1: dense ≡ compressed there) + console + file-
         report (masked) pins. NEW: the TestModelWeightsRead
         Guards class (ungated, no DB): the 2 ValueError guards
         with exact messages ("File header mismatch, expected
         'RGLM_BINARY_WEIGHTS', found 'WRONG_DESC'." / "File
         header version, expected '1', found '99'."). M1:
         `__all__ = ['make_evaluation_function']` in rlm_client
         (the bring-in had no __all__; the other 3 new modules
         have one).
         Verified (scratch/verify_save.py, 30-check probe: A15
         static + B2 read guards + C13 rlm_04 live + D9 rlm_03
         LONG): pre-campaign would have reported exactly the
         worklist mismatches (A1/A2/A4/A5 class, the ungated
         A2030, the ws lines, the 3-4-digit pins); post D-104
         ALL CHECKS PASSED (A-C tiers) + D tier green under
         LONG=1 (~10 min). A2030 pair live 6.2 s (GREEN), A2050
         LONG GREEN (~10 min, all goldens).
         Docs: 4 new mirror docs (lm_worker_save.md,
         model_weights.md, rlm_client.md — incl. the dense-path
         / substitution-rule section + the measured deltas;
         test_lm_worker_full_chain.md) + the logistic_model.md
         15-worker update (header D-104, state-per-Roberto
         COMPLETE + the naming note, pipeline shape ALL 15, V3c
         15-worker re-pin, appendix L39-54 active / L208-221).
         The 35-check logistic_model probe re-pinned V3c 14 →
         15 workers: ALL CHECKS PASSED.
         Suite 628 → 631: 631/0/87 gated (2.6 s) + 631 run /
         18 skipped live (44.8 s) + −W error full discover clean
         (3.4 s). 2 commits (code+docs, then notes).
         Pipeline state: 15 levels CLOSED — no further bring-in
         exists. Open: the M2 3-metric table (D-105 candidate,
         Roberto's call) + any future endgame-solver integration
         of rlm_client (the production context for A2050). |
D-105 | 2026-09-03 | ANALYTICS 3-metric header + dense training
         metrics (session 29, Roberto: "D-105, M2: OK, facciamolo
         ora che lo abbiamo fresco e chiaro in mente. Procedi!" —
         approved while the D-104 O1 quantification was fresh):
         Design (the M2 worklist, approved as proposed):
         _format_header becomes 3-metric wide: TRAINING (the
         COMPRESSED forward pass) | TRAINING-DENSE (the DENSE
         forward pass over w_dense — the exact shipped inference
         rules of rlm_client) | VALIDATION (dense); the POPULATION
         table column becomes a "Population (baseline)  : RMSE ...
         MAE ... Loss ..." line; the Generalization Gap is
         REDEFINED dense-vs-dense (vld_rmse_y −
         train_dense_rmse_y — a pure generalization measure); NEW
         Substitution Delta row (train_dense_rmse_y −
         train_rmse_y — the compressed-vs-dense cost, the O1
         effect isolated in its own number).
         New public function compute_training_dense_metrics(ctx):
         per-instance offsets np.repeat(iwmap_feature_offset[:-1],
         n_instances_per_feature) + rlm_indexes.indexes (the same
         expanded construction as rlm_validate), forward pass over
         ctx.w_dense → sigmoid → z2y; 4-key dict
         train_dense_{mae_y,rmse_y,loss,samples}; the loss is the
         PURE 0.5·mean(rn_z²) forward-pass loss (no ridge — there
         is no dense optimizer objective). RLMContext: 40th field
         train_dense_metrics (L156, the D-099 idiom); the ANALYTICS
         worker publishes it in _up (2nd INFO line "Computing
         dense-pass metrics on the training set...") and clears it
         in _down (3 fields now).
         Goldens (measured, re-pinned in both test files + both
         probes): rlm_01 (cut 2, 10 samples, 5 IC positions):
         dense rmse 3.3556 vs compressed 0.000132 → Substitution
         Delta 3.36, gap 27.22 → 23.87 (vld 27.22 − 3.36). rlm_04
         (cut 10): dense 13.8312 → gap 0.18 (was 0.19 mixed),
         delta 0.01. rlm_02/rlm_03 (cut 1): delta "-0.00" — the
         residual is the f32 rounding of the w_dense copy (−1.6e-08
         / −1.7e-07), NOT substitution; gaps unchanged (−0.13 /
         0.32). File-report hashes re-pinned (rlm_01 f6b54954…,
         rlm_02 94a4af7e…, rlm_03 57f9766b…, rlm_04 d44557a8…);
         header 15 → 17 lines; the step-13 log span 18 → 21.
         Verified: analytics module 4/0 live + 4/0/4 gated + −W
         error clean (8.0 s); full suite 631/0/87 gated (3.2 s) +
         631 run / 18 skipped live (46.8 s); full-chain A2030 live
         GREEN + A2050 LONG GREEN (705 s, 5/0);
         scratch/verify_analytics.py 41 checks +
         scratch/verify_save.py 32 checks ALL PASSED (incl. the D
         tiers under LONG=1). Docs: rlm_analytics.md /
         lm_worker_analytics.md / logistic_model.md (39 → 40
         fields) / both test docs updated. 2 commits (code+docs,
         then notes). O1 is now RESOLVED: the table shows both
         training representations, the gap is pure, the
         substitution cost has its own row. |

D-106 | 2026-09-04 | METHOD: the notes/docs hygiene migration.
         (1) Mirror docs become current-state CONTRACTS, codified in
         the new prescriptive file notes/docs_rules.md: the 4-line
         header with the `> State:` line as the only time permitted
         in the file; 7 sections (API / Architecture / Verified
         invariants, each pinned to a test or probe / Open issues,
         open-only / Conventions / Integration / optional line-ref
         appendix); the forbidden list (provenance narrative,
         campaign tags in prose, FIXED/RESOLVED lists, verbatim
         analysis appendices — those move losslessly to
         notes/analyses/ — the global suite status, report tenses);
         the lifecycle (doc updated in the SAME commit as its code,
         rewritten not appended; a "pinned by" into the void is a
         defect); size budget 60-120 lines (hubs 150-200); the
         test-doc variant (Coverage map + Goldens pinned).
         (2) The verification apparatus is separated from the
         disposable sandbox, codified in notes/probe_rules.md:
         probes move from scratch/ (gitignored, untracked) to
         probes/ at the workspace root (tracked, one
         verify_<module>.py per module — src/ stays the twolm
         package, D-006); every check classified a/b/c (a
         independent invariant KEEP / b obsolete: b1 re-pin —
         pipeline-wide facts re-pinned ONCE in the hub
         verify_logistic_model.py, b2 retire to notes/analyses/
         with an ARCHIVED header / c overlap DELETE — with the
         operational criterion "would the check still have value if
         the duplicated test were wrong together with the code?");
         the test/probe line (cheap single-module behavior and
         hand-computed unit math become TESTS; source-text
         inspections, heavy end-to-end re-derivations and the
         pipeline state stay PROBES); the campaign sweep rule (full
         suite + all probes green before the notes commit).
         (3) Migration order: step 0 = this entry; then the a/b/c
         classification of the 28 scratch files + the
         verify_lm_worker_config E2/E3 investigation (unknown
         worker name raises no exception: contract or bug, awaiting
         ruling); then the probes/ move + hub centralization + the
         one-by-one split, scratch/ ending empty (disposable
         again); then the docs/ rewrite one file at a time,
         board.md first (schema validation), then pattern.md, the
         C-class hubs, B batches, A. | Session 30 (the Qwen3.8 QoL
         DSH setup test) became a method session on Roberto's
         observation that NOTES.md and the docs are "pesanti".
         Evidence: (a) NOTES.md is ~80% history — ~440 "Done (…)"
         bullets in Next steps, a 1196-line "Where we are",
         inventory rows carrying full campaign narratives (the
         logistic_model row even broke its table line) — while the
         same history already lives in the journal (174 KB),
         decisions.md (230 KB) and git log; (b) the 70 mirror docs
         (804 KB) drifted from contracts into analysis reports:
         board.md contradicts itself (R1 "the most important flaw"
         in the verbatim session-1 appendix, "RESOLVED" in the
         body), rlm_analytics.md is stale within two weeks of its
         creation (header pins 626 tests, body includes D-105,
         suite is 631), 34/37 production docs carry line-number
         appendices that rot with every code change; (c) the first
         full probe audit run (2026-09-04, 28 scripts, DB live,
         no gate): 14 green, 13 stale (9 duplicated pipeline-state
         pins each asserting "N active levels" at its own bring-in,
         1 stale import, 1 stale API, 2 dead one-offs), 1 to
         investigate (E2/E3) — the "verified invariants" chain
         cites artifacts a fresh clone does not contain, and the
         decay was invisible exactly because nothing tracked the
         probes. Roberto's rulings: "La storia deve stare nei
         commit GIT e nel LOG. NOTES deve contenere solo le
         informazioni DISTILLATE"; "il file NOME_MODULO.md deve
         dire cosa fa il modulo ORA"; one-off probes are archived,
         not kept green; the per-file change LOG idea declined
         (a 4th copy of facts already in git + decisions + journal —
         the per-file view is derivable via git log --follow). |

D-107 | 2026-09-04 | D-106 follow-up rulings, the three
      "stale-unruled" probes resolved at the probes/ move (step 2,
      4091e72) — no source, doc, or test touched:
      (1) verify_lm_worker_config E2/E3 — NOT a bug: the premises
      are 2-worker-era (the probe was written 2026-08-30 while the
      pipeline was [CREATED, CONFIG]; D-080, same day, enabled
      POSITIONS and every later bring-in added more). The current
      pipeline — 14 factory workers + the CREATED sentinel,
      complete since D-104 — makes "POSITIONS" a valid worker
      (index 2) and step 2 in bounds, so no exception is CORRECT;
      worse, the old E2 call would have performed a real
      CONFIG+POSITIONS move (an unintended side effect). The guard
      contract (ValueError / IndexError with the exact messages) is
      intact (state_machine.py L357/L362) and the tests pin the
      TYPE (test_state_machine L258-273) but not the IndexError
      message — so the re-pin with genuinely-invalid targets
      ('NOT_A_WORKER' -> ValueError exact message; 99 -> IndexError
      'Target step 99 is out of bounds.') stays in the probe
      (b1 -> a; verified live 2026-09-04).
      (2) verify_cache_manager V7c (the step-2 WARN message) —
      category c: test_cache_manager's
      test_step2_checksum_mismatch_forces_recomputation pins the
      exact current message + Relevance.WARN via assert_any_call;
      the probe's pinned text was stale ("Checksum mismatch" vs the
      current "Checksum validation failed for … (sidecar missing
      or mismatched) …") — DELETED at the move.
      (3) verify_cache_manager V17 — its premise ("no
      @validate_call here, the raw str reaches .exists() as an
      AttributeError") is obsolete: the function carries
      @validate_call now (the D-076-era gate idiom) and pydantic
      lax mode coerces str -> Path (verified live: the inner
      store_fn sees a pathlib.PosixPath; the flow then dies
      FileNotFoundError in the framework's sidecar write) —
      RE-PINNED as the coercion check (a: unique, no test covers
      it; the §4 test-conversion candidate now converts the
      coercion fact). | (2) and (3) were LATENT: the audit's
      ImportError masked them (the probe never ran past the import,
      so the source-only classification assumed them green), and
      the import fix exposed the next layer of staleness. Lesson
      codified in the step-2 amendment of
      scratch/classification.md: a stale-import fix must be
      followed by a full re-run of the probe — the sweep runs
      AFTER the fix, never before. |
D-108 | 2026-09-04 | D-106 step 3: the one-by-one split of the
      18 probe files carrying c checks — no source file touched,
      probes/ + tests only (Roberto's standing approval for the
      split; each deletion verified against the ACTUAL test
      source, the classification's labels being stale in BOTH
      directions):
      (1) Method (per file, one commit each, suite green per
      test-touching commit, the affected probe green per probe-
      only commit): delete the c groups (pointer comment at each
      site naming the pinning test), resolve the a?/c? marks by
      reading the test (NOT the classification's audit claims),
      keep the a groups, preserve any load-bearing side effect of
      a deleted check (the binding becomes a bare assignment with
      a comment; the chain-bootstrap calls stay).
      (2) The ~135 c deletions + the resolutions, file by file
      (18 commits, ad88299 to c36c919): mobility 5 c; hub
      verify_logistic_model 12 c (V6f to test, V6a/V7a stay a);
      lm_worker_config 6 c (D1/E2/E3/E4b to tests);
      lm_worker_features C1/C2 re-pin (206 lines / 2 classes / 3
      methods) + B11 to test; lm_worker_positions 7 c (E to NEW
      test_rlm_config_schemas.py 13 tests, D4a-g to
      TestIsCacheConsistent); vld_positions C1/C2/C5/C6/C7 to c
      + C3c/C3d to a KEEP (the test pins count 200 + mean 3.64
      but NOT std 23.809880302093077 / variance 566.9104, nor the
      int8 range [-58,56]) + D2-D7 to NEW
      test_lm_worker_vld_positions.py::TestIsCacheConsistentOver
      ride (6 DB-free tests); validate C1/C2/C3/C6/C7 to c (C6
      the classification's 'a' is stale: test_second_instance_
      deterministic pins identical metrics + no re-extraction +
      6 hits; C7 test_down_clears_vld_metrics) + D1/D3 to NEW
      test_lm_worker_validate.py::TestValidateModelUnit (2
      DB-free tests; M1 zero-guard via a REAL RLMContext since
      Worker.up is @validate_call-gated); cache_manager 11 c
      groups (V2/V9c/V10b/V16 stay a; V17 to
      TestValidateCallCoercion::test_str_cache_path_is_coerced_t
      o_Path; the dead Dummy classes + hash imports removed);
      analytics C4b/C6 to c (the '6c' overcount; the td binding
      restored — the side-effect trap); feature D1-D4 to c (in
      test_feature.py, NOT test_features.py — stale name; f_int
      kept, D5 uses it); design_matrix D0-D4/D9 to c (the
      extraction machinery removed; D5 the independent recompute
      stays a); gradient D1-D4/D11 to c (the deleted D1/D2 were
      LOAD-BEARING move_to_step bootstraps — restored
      rlm.move_to_step('GRADIENT') before the D5-D12 loop,
      otherwise 7 mismatches); wmaps E0-E8 to c (the classification
      audited a STALE probe version — E1-E12 don't match the
      actual E0-E9; E1-E6 were tautological against the test's
      verbatim pins, E7/E8 operate on the pinned literals —
      implied; E9 the live per-feature row-count invariant stays
      a); zed A13-A15/D2/D3/D4/D12 to c (the dead GOLDEN_Y/GOLDEN
      _Z removed) + D1/D8 to a KEEP (the test pins only 2 of 4
      pre-state attrs; never the z2y pre-down wiring);
      rlm_indexes B1/B14 to c (c? resolves: test_init_success
      pins all three incl. assertIs; test_init_fails_with_
      invalid_hash_type is B14) + B9/B10/B11/C1/C6a/C6b to c
      (the 'unit-test coverage gap' note is stale —
      test_is_cache_consistent_returns_false_rds_differs covers
      the rds branch); optimize F1-F10 + G1/G2/G4/G5 to c
      (TestRLMOptimizeIO pins ALL the checkpoint IO with real
      files; the helper/branch tests pin the rest; G3 the hash
      oracle + the whole H tier stay a); save B1/B2 + C1-C4 +
      C6-C14 + D1-D10 to c (the classification's C12 'a+c' and
      D8 'a' are STALE: the full-chain test pins ALL 5 report
      substrings + 2 log lines at L209-213 / L350-354) — C5
      SPLIT: converged/reason/iters are c (pinned) but the
      live-ctx f/g_norm floats (pre-f32-roundtrip) stay as the
      one a portion (the test pins f/g_norm only on the read-
      back); generate D1/D2 + D4-D10 + D12/D13 + E1/E3/E8-E11
      to c, C1/C2 to a (test-file meta, not pipeline state);
      E2/E4/E5/E7/D3/D11 stay a (the cross-derivations + hand re-
      derivation + absolute hash golden).
      (3) The section-4 test conversions (probe_rules section 4 —
      cheap deterministic single-module behavior to tests;
      source-text inspections, heavy E2E re-derivations, pipeline
      state stay probes): 631 to 664 tests.
      (4) Campaign sweep (gates the notes commit): full suite
      664/0/87 gated + 664 run/18 skipped live + -W error clean;
      all 20 probes green in BOTH gated and live modes.
      (5) scratch/ now EMPTY: the 6 o1* investigation one-offs +
      classification.md archived to notes/analyses/ (ARCHIVED
      headers); verify_t2 + verify_burnside were already archived
      at step 2. |
D-109 | 2026-09-04 | docs/ rewrite: board.md migrated to the
      docs_rules schema (D-106 step 4, first file, schema
      validation); the State-line convention established
      (docs_rules §2: D-NNN = the last decision that changed the
      module, <short-hash> = the last commit touching the
      module's source, date = that commit's date); the verbatim
      session-1 review extracted to
      notes/analyses/board_session1_review.md
      | Roberto's approval ("Procedi ora con board.md"). Method:
      docs_rules §8 — lossless extraction of the historical
      material + rewrite to the schema, one commit per file,
      board.md first as schema validation. The session-1 verbatim
      Italian review (the R1 "most important flaw" appendix that
      motivated §1 — the failure mode these rules prevent) moved
      verbatim to notes/analyses/board_session1_review.md (frozen
      record, original language kept, ARCHIVED-style header).
      Rewrite to the 7-section schema, 201 lines (hub budget
      150-200; 1 line over, driven by the 68-name API minimum):
      4-line header (State: D-018 · b070918 · 2026-08-27 · suite
      193/0/12), one 68-name API table with a family column,
      Architecture (dual scalar/array API, Numba, Pydantic, the
      zero-copy discipline, Kogge-Stone legal moves + flip set,
      the fixed D8 slot order D-014, little-endian D-022), 12
      verified invariants each pinned to a named test_board.py
      class, Open issues M1-M7 re-verified against the CURRENT
      source (the source-of-truth rule, again: the old doc's
      "Applys ×5" is actually "Aplays ×4" — a double-p typo the
      analysis mis-transcribed; the anti-transformations docstring
      typo was already fixed at 0aca5e6 and no longer exists),
      Conventions, Integration (6 consumers). No source change:
      the M items stay open pending an explicit request (AGENTS.md
      rule 3). Suite unchanged (docs-only commit): 664/0/87 gated
      re-verified. Next per §8: pattern.md, then the C-class
      hubs, then B batches, then A. |
D-110 | 2026-09-04 | feature.py OPEN R1 disposition (surfaced by
       the D-106 step-10 re-read): the `BeforeValidator` import
       (L49) is never referenced — the dtype check rides on the
       imported `IndexArray` alias (pattern.py L74: Annotated +
       BeforeValidator (validate_index_array)); the import had
       been dead since the module's first commit (b51bea6) and
       the D-038 R4 batch removed only the dead typing imports
       (TypeAlias/List/Tuple/Annotated). FIXED per Roberto's
       ruling ("fiaas ora [fix it now]"): the import line now
       carries only `validate_call, ConfigDict` (commit de01cf2,
       one-line change, no behaviour change). Suite 19/0/1
       GREEN + full gated 664/0/87 GREEN. The feature.md mirror
       updated in the same wave (State line D-110, Open issues
       None). |

D-111 | 2026-09-06 | board.py OPEN M1-M7 fix campaign: all 7 open
       issues of the session-1 analysis fixed, one commit each
       (Roberto: "fissare le sette ISSUES in board.md... una alla
       volta"). M1 (47ac5da): bitboard_ro000 now returns a fresh
       copy (arrays: bb.copy(), scalars: Bitboard(bb)) — the
       identity contract is copy at BOTH layers (position_ro000
       already copied; ro000 was the only D8 fn not allocating).
       M2 (1558321): square_validate_range now uses the existing
       (unused) __square_max_value__ constant — message text
       byte-identical. M3 (dfa12cd): the 4 D8 function/label
       tables are plain lists (were np.object arrays; pattern.py
       consumer-checked: indexing, set(), join — all compatible).
       M4 (35de3e4): fastmath=True dropped from the 6 D8 njit
       kernels (pure integer ops — fastmath is a no-op; now every
       kernel is decorated identically). M5 (ac4f15e): the doc
       claim was empirically false (the whole dual API rejects
       bare int/lists uniformly) — the REAL gap was the missing
       1-D ndim guard: a 2-D array crashed deep in the numba
       kernel with a TypingError; the standard house-pattern guard
       added on both arguments. M6 (47a4241): the 14 docstring
       typos fixed (Applays x4, arry x4, lenght x4, lovercase,
       does't, whould, Chanpionship). M7 (5ae49c0): the
       @overload registration on the @validate_call wrappers was
       empirically verified to RESOLVE in a JIT context (scalar +
       array) — the gap was the missing coverage: new
       TestNumbaReflectionOverloads (2 tests) + module-level njit
       helpers. | House rules 3/5: explicit request authorizes the
       source change; mirror rule — board.md updated per commit
       (Open issues now "None.", suite 201/0/12). New pins: 8
       tests (M1 x1, M2 message pins, M3 x3, M5 x2, M7 x2) — the
       suite grew 193 → 201 (full gated 664 → 672, 0 failures).
       No perf regressions: A/B bench for M4 (21.5/25.6M b/s with
       fastmath vs 28.2/27.5M without — equal or faster), ro000
       copy 191M b/s (not a hot kernel), M2/M5/M6/M7 have no hot-
       path surface. |

D-112 | 2026-09-06 | pattern.py OPEN M1 fix: PatternSet.__repr__
       added (the follow-up noted during the minor sweep; Pattern
       already had one). The house one-line style, mirroring
       Pattern.__repr__: name (repr-quoted), the sha3_256 set hash,
       the patterns in the mask-sorted order via their own
       Pattern.__repr__ (the list display delegates per element).
       New pin: TestPatternSet::test_repr (the full golden line for
       the 3-pattern SamplePatternSet). | House rules 3/5 (explicit
       request — "il medesimo lavoro per pattern e
       logistic_model"); mirror rule. pattern.md: API-table row +
       the TestPatternSet invariants bullet extended, Open issues =
       None. Suite 64 → 65 (full gated 672 → 673). No perf surface
       (__repr__ is a display-only cold path; the fused kernels
       and the pack/unpack hot paths are untouched).

D-113 | 2026-09-06 | logistic_model.py OPEN M1 fix: the stale
       comment "# Remove comments when modules are added." above
       the factory imports removed. It is a leftover of the
       line-by-line pipeline build (D-076 → D-104 era); the
       pipeline is 15/15 complete with 0 commented imports, so
       there is nothing left to uncomment — the line is dead and
       misleading. The accurate "# Import worker factories"
       section label stays. | Same ruling as D-112. Comment-only
       change: zero behaviour, suite unchanged 17/0/0, the
       21-check probe still GREEN. logistic_model.md Open issues =
       None. |

D-114 | 2026-09-06 | Open-issues section normalization across all
       38 module docs (Roberto: "dove non ci sono OPEN ISSUES,
       scrivi semplicemente None. ... c'è un commento che trovo
       dispersivo, rimuovilo"). Five docs carried narrative
       parentheses after the "None." (base_model, feature,
       lm_worker_features, opt_lbfgs, regab — e.g. the opt_lbfgs
       "known open coverage, frozen at D-053" remark). Now all
       five are the bare "None.", per docs_rules.md §4 which
       already prescribed exactly this: "OPEN R/M/T items only,
       with their pointers. If none: one line, None. Closed items
       never appear." The removed narratives remain traceable in
       decisions.md / the journals / the analyses archive. The
       single Deferred item (lm_worker_config R1, the D-078
       ruling) stays in place per Roberto ("quello lascialo per
       ora"). | Doc-only change, no source touched, no suite
       impact. The cross-doc audit found no remaining OPEN
       R/M/T items anywhere: the only non-"None." Open-issues
       section in the whole docs/ tree is the deferred R1. |

D-115 | 2026-09-06 | Separated the active rules from the historical log
        (Roberto: "dobbiamo assolutamente dividere i LOG
        storici, incidentali, dalle REGOLE ATTIVE. ... mantenere
        'snello il corpo legislativo', le regole, che possono
        essere lette e consultate sempre velocemente, da un LOG
        di decisioni/azioni che crescerà sempre, e va consultato
        solo in caso di reale necessità e ricerca storica"):
        notes/rules.md CREATED as the register of the active
        legislation — one rule per line or two, grouped by theme
        (roles of the notes files, language & collaboration,
        layout & tree, naming & platform, test discipline,
        pipeline contracts, docs, journal), each with its origin
        D-number, ~150-line budget, lifecycle RECORD (every
        decision → decisions.md) / PROMOTE (enduring rule →
        rules.md, same commit) / RETIRE (removal logged with a
        new D-number). decisions.md is now the pure historical
        log: append-only, all 114 D-entries kept, header
        rewritten with the role + the promote/retire protocol.
        AGENTS.md updated: rule 1 (consult notes/rules.md when a
        standing rule is in question), rule 6 (RECORD/PROMOTE/
        RETIRE wording), Layout (rules.md + the historical-log
        role). NOTES.md re-scoped to the STATE layer: the
        Where-we-are bullets reduced from the 1460-line
        campaign chronicles to state-only bullets (2–4 lines
        each, present tense, status + open/parked items + suite
        + D-pointers; a bullet shrinks back to 1–2 lines when
        its module's work closes); the 32 "Done (date)" bullets
        dropped from Next steps (their content lives in the
        decision log and the journal volumes — the D-pointers
        carry it); the rigid format rules moved from the
        NOTES.md header into rules.md (the "roles of the notes
        files" section). One-shot migration: the 114 D-entries
        audited, ~30 active rules extracted into rules.md; no
        source touched; full gated suite re-run GREEN.

D-116 | 2026-09-06 | Fixed the corrupted markdown table rows —
        the Obsidian rendering break at the Inventory's
        logistic_model.py entry (Roberto: "alla entry
        src/twolm/logistic_model.py succede qualcosa di
        sbagliato... da li in avanti la formattazione
        sparisce") + the unescaped pipes in the two mirror-doc
        tables found by the same sweep.
        | A markdown table requires one physical line per row:
        the logistic_model.py Inventory row was physically
        split across 8 lines (a wrap dating from the D-106-era
        notes wave, inherited by the D-115 trim verbatim), so
        Obsidian parsed the table only up to that point and
        lost the formatting from there on. Also, several rows
        carried literal unescaped "|" characters inside the
        Status cell (acting as phantom column separators):
        NOTES.md rlm_analytics ("Dict[str, float | int]",
        "TRAINING | TRAINING-DENSE | VALIDATION") and
        rlm_client ("max |Δy| 31.56"); mirror docs pattern.md
        ("n_instances = |Orb|", "8/|Orb|") and
        test_state_machine.md (the quoted CSV header "TIMESTAMP
        (UTC) | STEP | WORKER | RELEVANCE | MESSAGE"). Fix: the
        split row rejoined onto one line; every in-cell pipe
        escaped as \| (the standard markdown table-cell
        escape); the Obsidian alignment reformat it had written
        into the working tree dropped (a single hunk inside the
        table region — no content edits by the user). The
        lesson was PROMOTED into rules.md (table cells: one
        physical line per row; in-cell | escaped \|).
        Verification: every table in NOTES.md + all 38 docs/
        now uniform row-by-row (consistent cell-pipe counts);
        zero source touched.
