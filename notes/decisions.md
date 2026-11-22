# Decisions log — historical record

Format rules: notes/decisions\_rules.md (rigid — follow when appending to this file).

D-628 | 2026-11-15 | notes/overview.md — the two editorial removals (the user's call): (1) the "Current state" entry
         "The USO (FEATURE-SET) campaign stands at ec20 …" — it is not a realization milestone in itself (using the
         software one develops is self-evident), and its substance is fully documented in the LaTeX book named by the
         entry just above it; (2) the "Next steps" entry "The FEATURE-SET campaign (the scope): …" — with it the
         campaign list opens at MULTI-PLY. "Current state" keeps its three entries (the 19-level pipeline, the LM
         facade, the LaTeX book); "Next steps" keeps six (MULTI-PLY, MOVE-PROB, ENDGAME-SOLVER, REGAB, TEST-BATCH, the
         LaTeX book improvements).

D-629 | 2026-11-15 | The two volume rotations at the session boundary (the user's end-of-session housekeeping): (1) the
         journal — notes/log.md volume 005 had 26 sessions (102–127, 728 lines), past its 25-session cap: it closes as
         notes/hist\_log/log\_005.md (the H1 range final 102–127) and the new notes/log.md opens volume 006 at session
         128; (2) the decisions log — notes/decisions.md had 2811 lines (D-426…D-627), past its 1000-line cap: it closes
         as notes/hist\_decisions/decisions\_007.md and the new notes/decisions.md opens at D-628. The overview Index is
         updated for the three files.

D-630 | 2026-11-15 | Record-integrity disclosure (the capillary rules-compliance audit, zone A): two D-numbers are cited
         in the journals, the D-629 rotation entry and the overview Index, yet exist in no decisions volume. (1) D-627
         (the session-127 close) was recorded in the journal (hist\_log/log\_005.md:728) and the commit message
         (2268ac7) but was never appended to the decisions log: the closed volume 007 in fact ends at D-626 (line 2794)
         — so the D-629 entry's "D-426…D-627" range and the Index range overstate the volume by one; the Index is
         corrected forward to "D-426…D-626" in this same commit (the open file is repaired forward, iron rule 3; the
         closed volume stays append-frozen). (2) D-463 is cited by hist\_log/log\_004.md:2194 ("il refuso del marker #:
         … in cache\_manager (D-463)") but has no entry in volume 007 (the entries run …D-462, D-464…). Both gaps are
         DISCLOSED, not back-filled: the numbers stand lost, as D-152 is documented as a legal lost number
         (hist\_decisions/decisions\_006.md:622).

D-631 | 2026-11-15 | R-520 rewrap (the rules-compliance fix campaign, the user's item 2): the 21 physical lines over the
         120-char hard ceiling, in 8 files, are split back under the ceiling with zero semantic change:
         src/reversi/pattern.py (14 lines — the 12 PatternType table literals each split over two lines, plus the two
         long expressions at L379/L700), src/reversi/lm/hlp\_config\_schemas.py (the `side` Field description split),
         src/reversi/lm/wrk\_optimize.py (the log\_event f-string split), src/reversi/lm/hlp\_zed.py (the
         hlp\_zed\_fun\_factory return annotation split over lines), src/reversi/lm/model\_weights.py (the raise split),
         src/reversi/lm/wrk\_vld\_positions.py (the log\_event split), probes/verify\_wmaps.py (the quoted check string
         split — the string content is unchanged), run\_utests.sh (the banner echo split into two arguments — the
         printed output is unchanged). Verified: 0 lines over 120 in the tracked .py/.sh set, test\_pattern 76/0/0,
         verify\_wmaps all checks pass.

D-632 | 2026-11-15 | R-550 reword (the rules-compliance fix campaign, the user's item 2): the 8 I-XXX references in
         PROBE COMMENTS (R-550 bans I-XXX in any docstring or comment of the probe Python code; R-580 sanctions them in
         check labels only, per the house interpretation recorded in decisions\_007) are reworded to name the change in
         words, the check labels untouched: probes/verify\_gradient.py:294 ("the I-017 reordering" → "the level
         reordering"), probes/verify\_validate.py:218 (same), probes/verify\_wrk\_features.py:41 ("I-012 realized,
         the I-017 T1" → "the backlogged item realized, the reordering T1"), probes/verify\_logistic\_model.py:84/93
         (the two dated banner lines) and :232 (the bare "I-019:" dropped), probes/verify\_save.py:209 ("I-013:"
         dropped), probes/verify\_su\_analysis.py:32 ("the I-017 step 3" → "the reordering step 3", the D-258 citation
         kept). Verified: 0 I-XXX in probe comment lines, the 6 probes compile. Observation (pre-existing, not touched):
         verify\_gradient.py carries 3 stale structural pins (C1 line count 184 vs the current 225, C5 class/test
         counts) — a re-pin candidate for the next probe-maintenance pass.

D-633 | 2026-11-15 | R-330 amendment (the rules-compliance fix campaign, the user's item 3, choice (b)): the mirror rule
         is amended to EXEMPT the package `__init__.py` files — they are not mechanically bound to the one-file-one-doc
         rule, and the 6 un-documented `__init__.py` files (src/reversi, src/reversi/lm, src/reversi/tools, and the
         three test packages) are declared conformant, no doc to be created. The register (R-330), the mirror-doc rules
         (docs\_rules.md §7) and the overview's "Mirror docs" bullet are amended in this same commit, on the user's
         explicit approval for the rule change; the overview's 1:1 claim is now true again (every MODULE file has its
         doc).

D-634 | 2026-11-15 | The test\_index.md mirror doc is rewritten to the test-doc skeleton (the rules-compliance fix
         campaign, the user's item 3): the old 14-line doc was an unschematized skeleton (a lone Coverage table + a
         provenance Note, 1/98 conforming) and was STALE — the suite has 4 classes / 10 tests since the ExtendedIndex
         space landed, the doc said 2 / 5. The new 35-line doc carries the auditor's four test-doc sections (Coverage
         with the per-class pin map, Goldens pinned = None, Conventions, Integration) and is green on the docs\_format
         audit.

D-635 | 2026-11-15 | The docs/ batch rewrap (the rules-compliance fix campaign, the user's item 3): all 38 docs carrying
         a format finding are rewrapped to the house form with the canonical re-wrapper (notes\_format \-\-write,
         self-verifying: content fingerprint + idempotence), healing the 58 lines over the 120-char width and the 3
         split code spans; then the 3 ragged Coverage tables are repaired at the cell level —
         test\_hlp\_design\_matrix.md and test\_hlp\_generate.md (the bare `str \| Path` in a cell, now escaped) and
         test\_wrk\_analytics.md (the bare pipes of `mean(\|rn\|)`, now escaped) — and the 2 residual over-120 lines of
         wrk\_vld\_positions.md are split (the validate\_fn cell re-phrased so the code span stays on one line). The
         docs\_format audit now reports ZERO non-size findings across docs/; the 9 size-budget items (4 docs under the
         60-line floor, 5 over/under the hub budget) are disclosed, not padded — reaching a line budget by adding filler
         is against the mirror-doc purpose.

D-636 | 2026-11-15 | The three H1 factual corrections in the closed journal volumes (the rules-compliance fix campaign,
         the user's item 4): log\_000 "sessions 1–24" → "1–23" (the volume holds 1–23), log\_003 "38–89" → "38–78" (it
         holds 38–78), log\_004 "90–101" → "90–101, 98 missing" (it holds 90–97 and 99–101) — the ranges were verified
         against the actual session headers before the edit. This is the ONE class of change the archive freeze allows
         (log\_rules.md: "archived volumes are read-only EXCEPT factual corrections"); the 13 phantom session numbers
         (24, 79–89, 98) are resolved, no session content is touched.

D-638 | 2026-11-15 | The R-200 historical-exception documentation (the rules-compliance fix campaign, the user's item
         4): the closed journal volumes 000–003 carry 26 line-leading `+` markers (the Obsidian nested-bullet form) that
         the LISTMARK guard flags — a rule born at D-484, which POST-DATES the D-368 volume cleaning, applied
         retroactively to a frozen corpus the archive freeze (iron rule 3) bars rewriting. The resolution: the guard
         (wsutils/notes\_lint.py) exempts the frozen hist\_\* corpus from LISTMARK (a new is\_archived() gate; the check
         stays fully active on every open file — verified with a synthetic recognized journal name), the docstring
         records the D-638 exemption, and log\_rules.md documents the residue. The closed volumes are not touched by
         this decision.

D-639 | 2026-11-15 | The three H1 factual corrections in the closed journal volumes (the rules-compliance fix campaign,
         the user's item 4): log\_000 "sessions 1–24" → "1–23" (the volume holds 1–23), log\_003 "38–89" → "38–78" (it
         holds 38–78), log\_004 "90–101" → "90–101, 98 missing" (it holds 90–97 and 99–101) — the ranges were verified
         against the actual session headers before the edit. This is the ONE class of change the archive freeze allows
         (log\_rules.md: "archived volumes are read-only EXCEPT factual corrections"); the 13 phantom session numbers
         (24, 79–89, 98) are resolved, no session content is touched. (The D-636/D-637 numbers stand skipped: a
         mid-campaign renumber — this correction was executed after D-638, and the log's D-numbers must increase
         strictly in file order.)

D-640 | 2026-11-15 | R-130 / R-100 disclosure + forward ruling (the rules-compliance fix campaign, the user's item 4):
         (1) POST-RULE infrastructure notes (the rule in force since D-154, 2026-09-11) survive in the frozen volumes:
         hist\_decisions/decisions\_006.md:1409-1410, hist\_log/log\_002.md:354,966,
         hist\_log/log\_004.md:666,678,1511-1512 (DSH mechanism / settings / subagent-OOM notes); a larger PRE-rule body
         stands as history (incl. the DEEPSEEK\_API\_KEY credential detail at hist\_log/log\_000.md:447-449 — noted as
         publication-sensitive). (2) The journal's OWN prose ran in Italian in the closed volumes 003 / 004 / 005
         (session titles and bullet prose); the decisions / ideas files carry Italian only as verbatim user quotes.
         Forward ruling (governs open files going forward, the frozen corpus untouched by this decision): (a) journal
         and decisions prose in English — R-100's standing text, with verbatim user quotes (marked as quotes) exempt;
         (b) when the notes become the GitHub publication material, the publication edit pass strips the disclosed
         infrastructure notes from the closed volumes — that pass is the sole sanctioned touch of the frozen corpus for
         this class.

D-641 | 2026-11-15 | The R-750 / R-760 test temp-dir anchoring (the rules-compliance fix campaign, the user's item 5):
         the 6 test modules that created their scratch dirs in the SYSTEM /tmp (R-750: test artifacts live ONLY under
         the workspace build/tmp) are anchored to the shared CUSTOM\_TMP\_BASE (test/reversi/paths.py) —
         test\_wrk\_anova.py, test\_hlp\_su\_analysis.py, test\_wrk\_analytics.py (4 sites),
         test\_wrk\_final\_log\_print.py, test\_wrk\_su\_analysis.py (TemporaryDirectory(dir=...)) and
         test\_usage\_binio.py (3 mkdtemp sites, dir= + the prefix kept); test\_state\_machine.py (the R-760
         shared-idiom item) drops its self-derived TMP\_DIR (parents\[3\]/build/tmp) for the same shared anchor — the
         house rule it quotes in its own comment, now imported instead of re-derived. The 7 modules pass together: 136
         tests, 0 failures.

D-643 | 2026-11-15 | R-300 amendment (the user's call after the audit): the .gitignore is affirmed as-is. The 5 lines
         over the register's minimal list are NOT blank separators — they are 5 sanctioned functional entries:
         \_\_pycache\_\_/, \*.egg-info/, the two Emacs lock patterns and .env (the DB credentials; .env.example is the
         tracked template) — and the file's comment section headers + blank separator lines are formatting, not entries.
         The register (R-300) now lists the sanctioned additions and exempts the section formatting, so the file and the
         rule agree.

D-644 | 2026-11-15 | The audit's remaining MINOR items are left as-is (the user's explicit call): the 19 over-long test
         docstrings (R-570), the 8 R-560 backlog-reflow files, the 24 W291 banner lines, the 9 docs size-budget items,
         the 3 stale verify\_gradient pins, and the zone-F probe naming / headers / DP-010 items. No change is made;
         they stand disclosed in the audit report (notes/analyses/rules\_compliance\_audit\_2026-11-15.md) and may be
         picked up by a future maintenance campaign. The R-310 mirror clause (the 6 src modules without a test mirror)
         awaits the user's separate decision.

D-645 | 2026-11-15 | The 6 missing test mirrors are CREATED (the user's call: brief, compact, each running in a few
         tenths of a second; the anticipated dummy-with-pointer-docstring fallback turned out UNNEDED — all 6 admit real
         fast NO-DB tests): test/reversi/test\_base\_model.py (9 — the facade delegation + the run/resume contract on a
         3-worker mock machine), test/reversi/lm/test\_hlp\_analytics.py (8 — the SU verdict bands + the four
         header-line forms), test/reversi/lm/test\_hlp\_final\_log\_print.py (3 — the writer on a mock ctx),
         test/reversi/lm/test\_hlp\_validate.py (7 — the outlier kernel + the hand-computed 2-position forward pass),
         test/reversi/lm/test\_model\_weights.py (5 — the v2 round trip compressed/uncompressed + the three reader
         guards), test/reversi/lm/test\_wrk\_save.py (4 — the factory, the up artifact + the bounded echo, the down
         no-op). 36 tests, all under 0.3 s, 0 failures; every module uses the NO-DB mock-ctx idiom and the shared
         CUSTOM\_TMP\_BASE anchor. Each carries its mirror doc (the test-doc skeleton) and a row in the overview Test
         files table (the suite is now 52 modules, all green); the 6 join the run\_utests.sh MODULES array in pipeline
         order (each data module immediately before its worker). The audit's "6 src modules without a test mirror"
         finding (the R-310 question) is RESOLVED — no rule amendment needed.

D-646 | 2026-11-17 | MULTI-PLY campaign, step 1 (a): the GamePosition entity in `src/reversi/board.py` (the user's spec,
         ratified in the session design discussion): `Player` = np.uint8 with `PLAYER_BLACK` = 0 / `PLAYER_WHITE` = 1
         (the legacy C values); `GamePosition` = the structured dtype built from `Position`'s own `descr` with the
         player field appended — the "Position + player" contract holds by construction (the first 16 bytes of every
         element are exactly a `Position`). DISCLOSURE (a self-correction of the pre-implementation discussion): the
         itemsize is 17, NOT 24 — NumPy applies NO end-of-struct padding (the C struct pads to 24); the field offsets
         are 0/8/16 in both, the v2 layout is simply 7 bytes more compact, and the odd elements' u64 fields sit at
         unaligned addresses — harmless on the x86 platform (R-410) and invisible through the zero-copy field views that
         are the kernel-facing contract. The public surface: `make_game_position` (the `make_position` twin: scalar
         np.void / any-shape array, fresh buffer, the three field stores), `make_game_position_from_position` (the
         bootstrap convenience), `game_position_blacks` / `game_position_whites` (the absolute-colour view: `np.where`
         over the field views, dual scalar/array), and the 65-char string form `game_position_from_str` /
         `game_position_to_str` (the port of the C `game_position_x_from_string` / `_to_string`, with the confirmed v2
         pivot: the result is the RELATIVE view — the mover / opponent follow the player).

D-647 | 2026-11-17 | MULTI-PLY campaign, step 1 (b): the new module `src/reversi/game_position_database.py` — the v2
         port of the legacy C `game_position_db` (the user's step-1 goal: read a game position from a text file): the
         same record format (`id;board;player;description;`, the `#` comments, the trailing-garbage rule), the same six
         syntax-error classes (`GpdbErrorType`, the C `gpdb_syntax_err_type_t`), the same 0-based line numbering, and
         the same loader policy flag trio with the C defaults (`duplicates_are_errors=True`, `replace_duplicates=False`,
         `stop_on_error=False`). The parse (`_parse_record`) mirrors the C `gpdb_parse_line`; the load loop is a plain
         per-line call of the public `game_position_from_str` on the 65-char board+player string — the single source of
         the string→GamePosition conversion stays in `board.py` (no duplicated parsing logic), and a vectorized bulk
         path is deliberately NOT built (the databases are small: the test / POC use, the user's 8.4). The
         `GamePositionDatabase` container keeps the C dictionary contract (the id key, the insertion order, the `find` /
         `add_or_replace` / `len` / iteration, the `positions` property stacking a 1-D `GamePositionArray`).

D-648 | 2026-11-17 | MULTI-PLY campaign, step 1 (c): the tests + the fixture + the runner. `test_board.py` gains the
         `TestGamePosition` class (14 tests: the dtype layout — names / types / offsets / the itemsize 17 / the
         Position-prefix equality — the player constants, the two constructors incl. the shape-mismatch ValueError, the
         absolute-colour accessors scalar + array, the C doc-sample string value, the four ValueError cases, the round
         trip). The new `test/reversi/test\_game\_position\_database.py` (22 tests, 4 classes): the parse mirror (10),
         the fixture load (6), the policy flags (4), the container (2). The fixture is the VERBATIM legacy
         `db/gpdb-test-db.txt` (md5-identical copy) at `test/reversi/data/gpdb-test-db.txt` — it is the C `gpdb_verify`
         cross-validation surface: 6 entries + 11 errors, the exact (line, type) sequence pinned (the file carries THREE
         wrong-player records, not two — the first read of the fixture had missed the last two lines). The module joins
         `run\_utests.sh` at its canonical position (section 1, immediately after `test\_board`). Suite: 1187 → 1223
         tests, GREEN 1223/0/88 (the default tier + the LONG=1 wrapper measurement).

D-649 | 2026-11-17 | The two legacy gpdb fixtures join the repo (the user's call, after the placement discussion):
         `gpdb-ffo.txt` (19.5 KB, 368 lines — the FFO-12 opening corpus; the natural cross-validation surface of the
         future ENDGAME-SOLVER port, the C `endgame_solver` Makefile targets point at it) and `gpdb-sample-games.txt`
         (46 KB, 1037 lines — the C solver / perf-verification corpus) land in `test/reversi/data/` as VERBATIM copies
         (md5-identical, the original names kept). Placement ruling: the fixture zone, whose bookkeeping already exists
         (the overview Test-data bullets, the mirror-doc exemption of docs\_rules §7) — `gpdb-ffo.txt` is the direct
         sibling of the `ffo_12_log_sample.csv` parity fixture. A top-level `db/` zone is NOT opened: it would be a zone
         without a mandate (nothing in v2 reads databases at runtime — the consumers are the tests and the probes), and
         a zone opening is a structural call that deserves a real consumer (YAGNI). If a runtime-data zone ever becomes
         needed, the files migrate under a dedicated decision.

D-650 | 2026-11-17 | The `make_move` parity class joins `test\_board.py`: `TestPositionMakeMoveGpdbParity` (4 tests)
         validates `position_make_move` against the C make-move corpus — the four make-move-test-case-{a..d}
         before/after pairs of the `gpdb-sample-games.txt` fixture (the move is the one named by the after record's
         description, pinned to the case table D4 / D4 / D4 / B4): the before position + the move must be legal and must
         reproduce the after position's mover / opponent exactly. PLACEMENT RULING (the user's question, after the
         dependency concern): the class lives in `test\_board.py` — NOT a dedicated test file (4 tests do not carry a
         new module + mirror doc + overview row + runner slot, and board's contracts stay in one place), NOT
         `test\_game\_position\_database.py` (the assert is a `make_move` contract, not a reader contract — the other
         placement would invert the direction). The dependency the concern targeted arises only if the test used the
         gpdb LOADER: the `_record` helper does minimal fixture access (the id line, the field split) and the string ->
         GamePosition conversion is `game_position_from_str` (board.py — the SUT), so the test depends on board.py
         alone; the gpdb format validation stays the exclusive domain of `test\_game\_position\_database`. Precedent:
         `TestPositionHashLegacyParity` (the FFO-12 CSV parity in the same file). All 4 cases pass at first run — the v2
         `position_make_move` reproduces the C corpus bit-exactly.

D-651 | 2026-11-17 | Forward correction of the D-650 class (the user's call): the test class is RENAMED
         `TestPositionMakeMoveGpdbParity` -> `TestPositionMakeMoveGpdb`, and its docstring (and the test-doc area G
         line) are rewritten to state what the test DOES. The "parity with the legacy C" framing was a CATEGORY ERROR:
         `position_make_move` implementing the game rules is equal to the C implementation BY DEFINITION (the rules of
         the game) — there is no arbitrary value to pin, so "parity" names a non-test. The fixture's role is to supply
         four realistic mid-game before positions + the documented move, against which the `make_move` CONTRACT is
         checked (the move is legal; executing it reproduces the expected after position). House rule reaffirmed for
         test docstrings: they state what the code does — never its history or provenance ("the C … corpus", "legacy
         …"); the history lives in the journal and the decisions log, which the D-650 entry and commit keep verbatim.
         The suite counts are unchanged (4 tests).

D-652 | 2026-11-17 | The `endgame_solver` module: the scalar exact endgame solver (the first step of the ENDGAME-SOLVER
         campaign). `minimax_solve(gp)` — the depth-first minimax over the game tree of a GamePosition: the legal moves
         are explored in the static square order A1..H8 (verified to be the same order the C minimax uses — the C
         `gts_generate_moves` scans the legal-move bitset LSB-first and the minimax path carries no mobility sort, which
         exists only in the exact-solver / alpha-beta framework); the comparison is strict, so an equal-value tie keeps
         the first static move; the child's value is sign-flipped at every ply (relative view: the result is seen from
         the player to move at the root); the WOF leaf value reuses `position_final_value` from board.py (the empty
         squares go to the winner, a draw is 0 with or without empty squares — the user's ruling). The pass semantics
         (verified node by node against the C game-tree log): the terminal check PRECEDES the pass — a position where
         neither player can move is a one-node leaf; otherwise the pass is a further node and the value comes back
         negated. `nodes` counts every position visited (root and leaves included); `leafs` counts the terminals
         evaluated. `SolverResult` is a frozen dataclass (the `game_value`: np.int8 — already int8 in the scalar phase,
         for conformance with the future vectorized API; `final_game_position`; nodes; leafs), to be shared with the
         future `alpha_beta`. Pure Python recursion: the scalar phase, the vectorized numba phase is the next campaign
         step.

D-653 | 2026-11-17 | The `test_endgame_solver` suite (3 classes / 10 tests) + the runner slot (section 1, after
         test\_feature): TestSolverResult (the fields, the frozen behaviour), TestMinimaxSolveMicro (seven hand-built
         endgames, each pinning (value, final position, nodes, leafs): the full board from both perspectives, the
         full-board draw, the draw-with-48-empties-is-zero WOF case, the single-empties forced move, the equal-value tie
         keeping the first static move, the pass at the root), TestMinimaxSolveFixture (the ffo-01-simplified-8 position
         of gpdb-sample-games.txt, LOADED WITH THE GPDB MODULE — the user's explicit instruction, the module was written
         for this — value 18, 46 nodes, 15 leaves, the final string, and the A1-B1-H1-G2 solution line ending at the
         final position; every component cross-validated against the legacy C `endgame_solver -s minimax` oracle, whose
         game-tree log decoded the reference final position and the solution line).

D-654 | 2026-11-17 | The endgame solver trace: the `NodeRecord` (the frozen dataclass of the first trace version —
         `call_id`, `level`, `player`, `parent_move`, `best_move`, `value`, each one matching a comparable column of the
         C game-tree log) and the optional `log` callback of `minimax_solve` (invoked once per visited node, when the
         search of the node completes — the same entry / exit discipline of the C log). The pass becomes a real
         recursive node (it was inlined in the caller's frame), so that every node, passes included, emits exactly one
         record; the search results are unchanged (the ten pre-existing tests stay green). The C game-tree log of the
         ffo-01-simplified-8 fixture position becomes a test data file
         (`test/reversi/data/es_log_ffo-01-simplified-8.csv`, regenerated cleanly from the C oracle) and the new trace
         test compares the 46 v2 records with the 46 log rows one to one on the six columns. The fields grow
         incrementally, by the user's call: each future field (the first candidates: `is_leaf`, `empty_count`, the
         legal-move set) joins with its documented reason; the C-internal columns (the Zobrist hashes, the absolute
         bitboards) never enter the v2 record.

D-655 | 2026-11-17 | Two API polishes to the endgame solver, per the user's review: (1)
         `SolverResult.final_game_position` is annotated `GamePositionField` (the house scalar alias of board.py,
         `Annotated[np.void, SkipValidation]`) instead of the bare `np.void` — the same underlying type, the annotation
         keeps the entity connection and matches the board.py public signatures; (2) the `NodeRecord` move fields drop
         the `| None` and use the domain sentinel codes: `parent_move` is `MOVE_UN` at the root, `best_move` is
         `MOVE_NA` at a leaf and `MOVE_PA` at a pass node — every node carries a `Move`, mirroring the C log `UN` / `NA`
         / `--` columns directly. The 11 tests stay green (the trace mapping now goes through `move_to_str`).

D-656 | 2026-11-17 | The game-value types moved from regab.py to `endgame_solver.py`, by the user's decision:
         `GameValue` (the `TypeAlias = np.int8`), `_validate_game_value_array`, and `GameValueArray` (the
         pydantic-validated `NDArray` built on the alias) are now defined in `endgame_solver`, which exports both names.
         Rationale: the endgame solver is the PRODUCER of the game values (it solves the endgames) and the REGAB
         database is the persistence layer of the solved games — the types live with the producer, the consumer imports
         them; the move is also required by the future, the endgame solver going 100% vectorized will need
         `GameValueArray` on the solver side. regab.py imports both names from `endgame_solver` and re-exports them in
         its `__all__` (its public surface is unchanged, `test_regab.py`'s `from reversi.regab import GameValue` keeps
         working untouched). The only references in the workspace are the two files (verified by a full-tree grep); no
         circular import (`endgame_solver` imports from board only). `SolverResult.game_value` is annotated `GameValue`.
         The now-unneeded `TypeAlias` and `numpy.typing` imports were dropped from regab.py (`BeforeValidator` stays, it
         is also used by `BidArgument`). Zero behaviour change (the same alias object, the same validator). The
         validator gained three direct tests in the endgame suite (`TestGameValueArrayValidator`: the int8 array passes
         by identity, the non-int8 array raises, the non-array input passes), which bring the module to 100% of the
         statements and branches under its own suite (measured with `coverage`, installed in the venv for this).

D-657 | 2026-11-18 | The game tree is GamePosition-only (the user's field decision): the solver code may use
         `GamePosition` and ONLY `GamePosition` — no `Position`, no `mover` / `opponent` handling, no standalone
         `player` in the search; the elegance must be VISIBLE in the code, and the encapsulation must not cost
         performance (board.py exports the kernels for the future numba inlining). board.py gains the three
         GamePosition-level game-tree tools — `game_position_make_move`, `game_position_legal_moves`,
         `game_position_final_value` (each: a private prange kernel composing the PUBLIC bitboard primitives
         `flips_of_move` / `legal_moves_of` over the position's field views + the public scalar/array wrapper) and
         `bitboard_bsf` (the njit ascending twin of `bitboard_bsr`, the shift ladder compiles to bsf/ctz). Numba
         constraints found on the way: numba cannot construct a structured scalar (the kernels work on three bitboard /
         uint8 arrays, repacked with `make_game_position`) and `np.bitwise_count` is unsupported (the private
         `_popcount`). `game_position_make_move` applies the same orientation rotation as `position_make_move` (the turn
         passes: the mover / opponent fields rotate, the player flips; the pass is the pure rotation). The solver
         `search` is rewritten on the three tools (no `Position` anywhere, the `gp['player']` read inline in the trace
         emits, no `int()` cast) with the user's six style notes: no comment lines, the root called at level 0 with the
         first statement `level += 1`, the return type in the definition (`tuple[int, GamePositionField]`), the
         `for sq in range(64)` scan replaced by the `bitboard_bsf` bit-scan loop, and the `None` accumulators replaced
         by the out-of-range initialisation (`best_value` = the new `OUT_OF_RANGE_DEFEAT_SCORE` constant, −66, the C
         constant; `best_move` = `MOVE_NA`; `best_final` = `gp`) so the strict comparison stands alone. The fixture test
         becomes the GENERIC case test: a `CASES` entry per case (value, nodes, leafs, final position string, solution
         line) + two one-line methods, and the series grows to ffo-01-simplified 4–8 — the four new C reference logs
         (`es_log_ffo-01-simplified-{4,5,6,7}.csv`, generated with the legacy toolchain: the C `endgame_solver`
         `-s minimax -l` + `read_game_tree_log`), the solution lines and final positions extracted by walking the log's
         HASH links (the case-4 transpositions — the same parent / move visited twice — follow the first visit, the
         deterministic search gives them the same best move, asserted). Tests: board 339 (the nine game-tree-tool tests
         + the 1M-board PERF pair + the two `bitboard_bsf` tests), endgame 22 (the 5 solve + 5 trace cases, 20040/6201
         the largest); the perf check shows the gp tools at the position-level throughput (the kernel computes the same
         inlined primitives, the delta is the wrapper layer that the numba phase drops).

D-658 | 2026-11-21 | The numba-compiled scalar search (the first step of the compilation phase of the ENDGAME-SOLVER
         campaign): board.py gains the fourth public per-lane kernel `final_value_of` (the nopython WOF twin of
         `position_final_value`, over `_popcount`); `endgame_solver.py` gains the njit recursive `_search` (the nopython
         twin of the Python `search` closure: the same contract, the position as the three field scalars — numba cannot
         build the structured GamePosition scalar — the four public per-lane kernels `legal_moves_of` / `flips_of_move`
         / `final_value_of` / `bitboard_bsf` inlined by the compiler) and the `minimax_solve` dispatch: `log is None`
         runs the compiled fast path (the final position repacked with `make_game_position`, the njit uint64 returns
         cast through `np.uint64` — they come back as Python ints), a `log` given runs the traced Python search (the
         compiled trace is a later step). The fixture series grows to ffo-01-simplified 0–3 as SOLVE-ONLY cases (the
         user's call: no trace for them, no CSV fixtures in the repo — the C references were generated in scratch and
         used only to extract the goldens: value, nodes, leafs, final position, solution line), and the 18M-node case 0
         is LONG-gated (the `tier_long` flag, the house convention) so the regular suite keeps the 1.1M-node case 1 as
         its largest. Measured: the compiled throughput is flat at ~12.5 M nodes/s across the 0–5 series (case 0: 1.43
         s; case 4: 1.6 ms vs ~7 s Python, ~4400x); against the legacy C the v2 is ~1.3–1.7x slower at large scale (a
         constant-factor gap that closes as the cases grow) and faster at small scale (the C times include the process
         startup). The user's reading: the numba engine is the working engine of the campaign (the solver that will run
         for months solving the ML positions), the 1.7x is to be pursued, and the final high-perf solver will get a Rust
         version — the v2 numba engine is the reference of correctness for that port.

D-659 | 2026-11-21 | One search, compiled, traced: the user rejected the dual implementation (the njit fast path + the
         Python traced closure — "non mi piace duplicare la logica") and the Python `search` closure was deleted. The
         compiled `_search` carries the trace as a typed-list sink: one UniTuple(int64 x 6) record per node, appended at
         the node exit (None in the untraced mode — the untraced specialization compiles the guards away), the records
         replayed to the `log` callback when the search completes (the trace semantics moved from "during the search" to
         "buffered, at completion" — the documented price, no live-progress consumer exists). The 1-element int64
         `counter` array threads the entry-order `call_id` through the njit recursion (numba passes scalars by value:
         the array is the pointer idiom; int64 keeps the `call_id` in the record tuple's type family — a uint64 counter
         would force the int64() cast back in, the uint64 -> int64 conversion being lossy and numba-refused). Along the
         way: (a) the numba 0.68 cache of the full `_search` (recursion + the other cached kernels + the typed-list
         sink) SEGFAULTS when a fresh process loads it (bisected in scratch: the plain recursive variant caches and
         reloads fine) — `_search` is `cache=False`, the per-process recompile is the price, to be revisited at the next
         numba upgrade; (b) the user's beauty notes: `other_player(p: Player) -> Player` (the new public per-lane player
         primitive of board.py, njit inline='always') replaced the `1 - player` spellings and, with the player now
         travelling as a pure uint8, deleted the `int(gp['player'])` cast at the boundary; the defensive
         `int(MOVE_NA / MOVE_PA / MOVE_UN)` casts were dropped (numba widens the uint8 sentinel codes to the int64
         record slots implicitly — the same widening the bare player already relied on); the boundary casts at the
         njit -> Python exit use the domain aliases (`Bitboard(fm)`, `Player(fp)`, `Move(...)`, `GameValue(value)`) —
         numba returns every integer result as a bare Python int, the pydantic-validated public API demands the numpy
         scalars, and the aliases say WHICH entity each cast rebuilds. Measured on the 20k-node case 4: untraced ~1.1 ms
         (untouched), traced ~78 ms (the sink + the 20k-record replay — 90x cheaper than the old Python trace, the
         production path pays nothing). All 26 endgame tests pass with the trace validating the COMPILED path record by
         record.

D-660 | 2026-11-21 | Exhaustive coverage analysis of board.py under `test_board` (the user's request, the
         freshly-installed `coverage` 7.17.3): the raw 70% (888 stmts, 274 missed, 13 partial branches) was shown to be
         mostly structural artefact, and the real gaps were closed with 8 new tests (340 -> 348): (a)
         `position_is_game_over` post-pass False branch (the mover stuck, the opponent moves after the pass — row 3 a3W
         b3c3B, white plays d3); (b) the N-D array paths of `game_position_legal_moves` and `game_position_final_value`
         (only scalars and 1-D arrays were tested); (c) the three `game_position_make_move` error raises (array shape
         mismatch, move code above 64, mixed scalar/array kind); (d) the `GamePositionArray` validator dtype raise. The
         remaining 267 "missing" lines are all in three UNTESTABLE classes: (1) the ~255 njit function bodies (compiled
         code is invisible to Python line coverage — functionally exercised by the 348 tests through the public API);
         (2) the 4 `@overload` bodies (the compile-time typing functions of the D8 reflections: empirically proven — 3
         cold-cache coverage runs plus an isolated fresh-JIT-caller probe — to NEVER execute in this numba 0.68 +
         pydantic-wrapped-target configuration, while the JIT calls they are meant to serve DO work and ARE tested with
         goldens by TestNumbaReflectionOverloads; the registry introspection found no entry under the wrapped or the
         original identity, the exact numba mechanism is left as a library internal); (3) two structurally unreachable
         redundant guards (the body dtype raise of `bitboard_to_signed_int` and the body TypeError of `position_hash` —
         the pydantic gates raise first, no public-API test can reach them; the first attempt at such a test empirically
         confirmed the pydantic ValidationError preemption and was deleted). Verdict: zero real gaps remain. The
         `.coverage` data file was added to .gitignore.

D-661 | 2026-11-21 | Two warning fixes surfaced by the user's full-suite run, plus the PERF throughput run: (1) the four
         NumbaTypeSafetyWarning "unsafe cast from Tuple(..., uint64, ...) to UniTuple(int64 x 6)" in the
         `endgame_solver` trace sink — root cause: numba promotes EVERY binary op on small ints to 64 bits, so
         `Player(1) - p` in `other_player` typed as uint64 (the `-> Player` return annotation is not enforced by the
         compiler — proven with `inspect_types`), the recursion passed a uint64 player, and the record tuple carried a
         uint64 slot; the fix is the explicit re-narrowing `return Player(Player(1) - p)` (documented in the docstring)
         — after it both `_search` specializations type the player uint8 and the warnings are gone; (2) the pydantic
         ArbitraryTypeWarning at the `endgame_solver` import — `minimax_solve(gp: GamePosition, ...)` annotated the
         parameter with the raw np.dtype (an arbitrary object to pydantic); the fix is the house scalar-only alias
         `gp: GamePositionField` (and the now-unused bare-dtype import dropped) — the imports are clean under
         warnings-as-errors; (3) a PERF-gated throughput test for the ffo-01-simplified-1 case (1.1M nodes) with the
         house printout ([PERF `minimax_solve` ...] N nodes in T s (X M nodes/s)) — the user's tagging scheme: case 0
         stays LONG, case 1 is PERF, the rest untagged. The throughput was re-verified after all the D-659 changes: flat
         at ~19 M nodes/s (machine dependent, up from the earlier ~12.5 measured under a loaded machine) across cases
         0–3, the 18M-node case 0 in ~0.95 s — no regression. The docs' throughput statements were updated to the
         current measurement with the machine-dependent caveat.

D-662 | 2026-11-21 | Restored `cache=True` on the compiled `_search` by reformulating the code around the numba 0.68
         cache-loader bug, after the user asked why the cache segfaults (expected behaviour or a library bug). Full
         scratch bisect with the REAL kernels and the VERBATIM search body: the identical body with 6 parameters (± the
         counter array, ± the UniTuple trace sink) caches and reloads fine in a fresh process; the 7-parameter form
         (adding the `parent_move` scalar) SEGFAULTS the loader on cache load — so it is a numba bug (the designed
         behaviour for a bad/stale cache is the fallback to recompile, not a crash), triggered specifically by the 7th
         scalar parameter of this recursive function. The workaround: `parent_move` moves out of the signature into the
         2-element shared `state` array (state[0] the entry-order counter, state[1] the current `parent_move`,
         saved/restored around each recursive call — stack discipline), returning the function to the clean 6-parameter
         shape. Verified: full suite twice (run 1 writes the cache, 43.7 s cold; run 2 loads it, 12.5 s, all green, no
         segfault); the trace tests pin the `parent_move` column of all 20,040 records of the case-4 trace against the C
         goldens (the save/restore correctness at scale); pure execution 55 ms / 73 ms (20.2 M nodes/s); the one-time
         per-process cache load is 0.28 s / 0.45 s per specialization (replacing the 3.3 s / 4.3 s per-process
         compiles); the warm-cache suite total is 12.1 s (was 19.2 s). Bonus finding from the bisect: a structural clone
         whose 6-tuple return slots are type-underdetermined is silently unified by numba to float64 and its generated
         code segfaults at run time (a second, independent codegen bug); the real `_search` escapes it because
         `best_fm, best_fo, best_fp = mover, opponent, player` pins the slots to uint64/uint8 — proven by the bit-exact
         final-position goldens (a float64 bitboard would lose the bits above 2^53). The docs' open-issue entry was
         rewritten accordingly (the scalar form is to be revisited at the next numba upgrade). The earlier
         LONG-vs-warmup question for the two "slow" endgame tests became moot: with the cache warm they are fast (case 1
         out of the top-15 slowest, case-4 trace 0.59 s dominated by the one-time traced-specialization load).

D-663 | 2026-11-21 | Committed the C alpha-beta reference logs of the ffo-01-simplified 4/6/7/8 trace cases to the test
         data (`ab_log_ffo-01-simplified-{4,6,7,8}.csv`, the same 21-column `;`-separated game-tree log format as the
         `es_log_` family, generated with the legacy `endgame_solver -s ab` + `read_game_tree_log`): the fixture surface
         of the alpha-beta port. On this series the ab search visits 9.9x–25x fewer nodes than the minimax (case 4:
         2,029 vs 20,040; case 0: 1,700,428 vs 18,055,194) at the same values, final positions and solution lines (the
         same static order + the same strict tie-break). The 0–3 logs stay in the legacy scratch (KPI extraction only).

D-665 | 2026-11-21 | `TestAlphaBetaSolveFixture` (15 tests) + docs for the alpha-beta port: the 0–8 series against the C
         alpha-beta reference (the pruned node / leaf counts 1,700,428/420,214 ... 40/13, the same value / final / line
         as the minimax), the node-by-node trace of cases 4, 6, 7, 8 against the committed `ab_log_*.csv` fixtures (the
         best-move column compared only when the v2 record has a real best move — the C stale-value artifact of D-664),
         `test_ab_minimax_parity` (value + final position, the 1–8 series: both searches are exact), the PERF-gated
         case-1 throughput (18.9 M nodes/s — the same per-node rate as the minimax: the alpha-beta speedup is the
         node-count reduction pure, 25x at case 1), the 1.7M-node case 0 LONG-gated (0.247 s, vs the minimax ~0.95 s).
         The module doc gained the `alphabeta_solve` API row, the Architecture bullet, the `T_BEST_MOVE` trace caveat,
         the invariant entries and the rewritten open issues; the test doc the coverage row and the goldens; the
         overview the campaign state and the test count (42). The suite is now 1,291 tests, green.

D-666 | 2026-11-22 | Per the user's request, three corner-case GamePositions joined BOTH the minimax and the alpha-beta
         fixtures: `black-has-to-pass` (the forced first pass), `ffo-01-simplified-12` (the already-finished game: the
         single leaf) and `black-wins-by-wipe-out` (the wipe-out win before ec=0: the full −64, the one-colour final) —
         all three already entries of the `gpdb-sample-games.txt` corpus. The goldens were measured with both solvers:
         bhp (−52, 196,030/55,778 minimax — 23,977/5,963 alpha-beta), 12 (+18, 1/1 both), wo (−64, 4,900,474/1,367,719
         minimax — 310,082/74,388 alpha-beta). The solution lines were extracted ply by ply (the first static-order move
         achieving the exact node value at the ACTUAL position — the search's own tie-break rule): the naive trace-chain
         walk is unreliable on transposed positions (several nodes share the same level / parent-move pair) and produced
         a wrong line on both pass-containing cases; the per-ply extraction is exact by construction and replays to the
         golden finals. The fixtures gained `CASES[12]` (the series entry) and the `CASES_CORNER` dict + `_solve_named`
         (the `--` line entries replay as the player-swap move, which `game_position_make_move` already supports); six
         new tests (three per fixture), the 4.9M-node wipe-out minimax in ~0.25 s (fast tier, untagged). The test doc
         and the notes follow; the suite is now 1,297 tests, green.

D-667 | 2026-11-22 | The vectorized array solver, engine B (the worker pool) — the user's question "does the frontier
         vectorization pay?" decided with an analysis and the user's 100% agreement. The honest estimate for the
         frontier-vectorized core (A) in NUMBA is 1.5–4x single-core, because the irregular mask/gather/cutoff control
         flow is exactly what LLVM does not auto-vectorize (only the regular per-lane kernels do); the worker pool (B)
         over the battle-tested scalar `_ab_search` gives ~8x on this 8-core machine with ZERO new search code (every
         lane is its scalar result — the D-664/665/666 node-level goldens carry over per lane for free), dynamic
         dispatch optimal for the 100x solve-cost variance, and it is the better ORDER: A remains available later as an
         engine upgrade behind the same API (and the true vectorized payoff lives in the Rust port, where A is the
         batched design for the 1M–10M-position datasets, run in 1k–10k-lane batches parallelized worker-pool style).
         Milestone 1 (the GIL check): 8 threads x njit scale (65.8x on the 10-task set — the njit search releases the
         GIL while running). Built: `SolverResultArray` (parallel arrays: the GameValueArray values, the
         GamePositionArray finals, the int64 node / leaf counts — the "group of arrays" shape, not an array of result
         objects), `uniform_empty_count` (the batch precondition check, the distinct counts named in the raise), and
         `alphabeta_solve_array(gps, check_ec=False)` (the worker pool: one thread per CPU, the work queue of lane
         indices, the per-lane FAST PATH calling the compiled `_ab_search` directly — the pydantic validation only at
         the batch boundary, the lane errors surfaced at the boundary, the per-lane result slots pre-allocated). Tests
         (6): the ten ec=8 lanes of the `regab_prng_gp` batch 7 (the user's set, the bitboards as the DB signed
         integers) against the INDEPENDENT DB game-value goldens [14, 22, 0, 2, 8, −8, −6, 28, −48, −22] — which also
         cross-validates the scalar solver against the C/REGAB database on that set — plus the per-lane scalar parity
         (value, final, node / leaf counts), the mixed corner batch (the forced pass, the finished game, the wipe-out, a
         plain lane), the empty batch, and the `uniform_empty_count` / `check_ec` gate. A is parked in ideas.md. The
         docs and the notes follow; the suite is now 1,303 tests, green.

D-668 | 2026-11-22 | The array-solver scale-up (the 100 / 1000-lane batches). The data: the `regab_prng_gp` table is
         reachable from this machine (the remote host gandalf.skynet, the `tst_regab` user / database, the `reversi`
         schema), so the 100 / 1000 sets are pulled STRAIGHT FROM THE DB with independent game-value goldens (no seeded
         playouts needed): 100 = the batch 8 ec=8 positions in seq order (`regab-batch8-ec8-100.tsv`), 1000 = the batch
         9 (`regab-batch9-ec8-1000.tsv`) — the batch 7 holds only 20 ec=8 rows, hence the distinct batches per set size
         (the user's 10 stay the embedded batch 7 set). The worker pool solves the 100-lane batch in ~0.32 s and the
         1000-lane batch in ~0.22 s (2.3M nodes, 10.4 M lane-nodes/s — the pool keeps the scalar per-node rate, the
         lanes run in parallel; the 1000 batch is FASTER than the 100 one: the larger pool of lanes hides the
         max-cost-lane tail), both in the fast tier. Three tests: the 100 / 1000 value arrays against the INDEPENDENT DB
         goldens (all values, the `check_ec=True` gate on both) and the PERF-gated throughput printout of the 1000-lane
         batch. The docs and the notes follow; the suite is now 1,306 tests, green.

D-669 | 2026-11-22 | The unified scalar / array API of the public solvers (the board.py idiom: one function, both forms
         — the user's consistency call, with the analysis: the 2x2 matrix (minimax / alpha-beta x scalar / array)
         collapses to two names, each taking a `Union[GamePositionField, GamePositionArray]` and returning
         `Union[SolverResult, SolverResultArray]`; NO performance cost — the dispatch is one `isinstance` at the
         boundary, the scalar path is byte-identical (the direct compiled call), the array path is the unchanged worker
         pool; the honest costs are formal only: the union return type and the form-dependent parameters (`log`
         scalar-only — the array form raises `ValueError`; `check_ec` array-only — the scalar form ignores it)).
         `alphabeta_solve_array` is REMOVED from the API (subsumed by the unified `alphabeta_solve`); `minimax_solve`
         gains the array form for symmetry (it is never used in place of alpha-beta, the user's words — consistency
         only). The worker-pool machinery is now the private `_solve_pool(gps, search, make_state)` shared by both
         public solvers (engine-agnostic: the workers run `_search` or `_ab_search` with the `_mm_state` / `_ab_state`
         factories, which the scalar paths now share too). The idiom is in place BEFORE the multi-ply EF step:
         `alphabeta_eval` will inherit the unified contract from day one. Four new contract tests
         (`TestUnifiedSolveApi`): the form dispatch (void → `SolverResult`, ndarray → `SolverResultArray`, both
         engines), the array + `log` raise, and the minimax array form of the ten batch 7 lanes against the SAME
         independent DB goldens (both engines are exact). The docs and the notes follow; the suite is now 1,310 tests,
         green.
