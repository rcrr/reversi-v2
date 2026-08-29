# Decisions log

Format: D-NNN | date | decision | rationale

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
       one-line format: Pattern(name='<NAME>', mask=0x<16-digit
       lowercase hex>) — the same info as the first line of print().
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
