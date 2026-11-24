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

D-670 | 2026-11-22 | The EF Y output range contract — the "bug" that was not a bug. The multi-ply EF planning surfaced
         it: the array EF measured 65.30 on random positions, beyond the +/-64 game-value range. A first reading (Nia's,
         then the user's "e' un BUG ed e' grave") treated the open window as the defect and a red reproduction test was
         written (assert |y| <= 64). The complete `logit_clipping` logic review (the `hlp_zed` doc + code, the `wrk_zed`
         worker doc, the latex book 080/160/200) showed NO clip is documented anywhere in the inference chain — the
         chain ẑ = σ(η) → z2y is exactly as implemented; the clipping lives only STRUCTURALLY in the training targets
         (the y2z image of the int8 values is in [c, 1−c] by construction). The user then did the math and re-framed: Y
         is a probabilistic estimate — the values beyond ±64 are the CONFIDENCE EXCESS (how much more certain the model
         is than the maximum score), and the ~200-model campaign found higher-clipping models perform BETTER (higher c
         widens the expressible band: ±65.31 at c = 0.01, ±80 at c = 0.1) — the excess band is learned, valuable signal.
         The proposed z2y clip was therefore WITHDRAWN (a monotone clip would flatten the tail into a ±64 plateau,
         destroying the magnitude the campaign values). The red test was CONVERTED into the design-pinning test
         `test_client::test_output_range_affine_image_with_confidence_excess`: every output of the seeded 1000-position
         batch lies in [−64/(1−2c), 64/(1−2c)] (the affine image of the FULL sigmoid range — would catch a future clip
         or an affine-constant drift) AND the batch deterministically produces values beyond ±64 (the excess presence —
         would catch a future regression in the other direction). The docs state the contract explicitly where the
         ambiguity lived: client.md (the convention + the invariant), `hlp_zed.md` (the [c, 1−c] domain is a property of
         the TRAINING z vector, NOT a constraint of the total z2y inverse), the latex 080 (the native ẑ output lives in
         the full (0,1); a consumer needing a bounded score clips at its own boundary). Consequence for the frozen
         multi-ply EF: no clip anywhere, the search window derived from c (R = 64/(1−2c) + margin). No production code
         changed.

D-671 | 2026-11-22 | The rebuildable LM test fixtures mechanism (the ec20 member). The multi-ply EF tests need REAL
         saved models on disk (not the transient 424-ms in-memory SYNTH builds): the user's design — the models are
         defined by committed config JSONs in test/reversi/data/, built by a small helper module, consumed by the tests
         which ERROR (naming the exact build command) when the artifact is missing. Refinements accepted from the
         discussion: the consumers are TIER-AGNOSTIC (the fixture is sticky workspace state — built once, there for
         sessions of weeks — not a LONG-tier prerequisite); NO manifest (the per-model embedded `sha3_256` + the config
         provenance already cover it); the helper is a MODULE in the test tree (test/reversi/fixtures.py), not a wsutils
         CLI script; the corpus is the FULL `rlm_04` one (a build costs seconds); no format-versioning intelligence
         (format change → manual clean + rebuild). The helper API: `clean_lm_fixture` /
         `create_lm_fixture`(`force_rebuild`) (idempotent: an existing model file short-circuits; the CONFIG worker
         requires the base dir to exist, so the helper mkdirs first) / `require_lm_fixture` (the consumer gate) + the
         `python -m test.reversi.fixtures create|clean <name>… [--force]` CLI. The build runs the standard pipeline
         entry STOPPED at `CLIENT_CHECK` (the config's `target_level` field is dead code — no entry honors it — so the
         stop is explicit; the config also carries plot.enable = false: SAVE + the client-check integrity gate included,
         PLOT + `FINAL_LOG_PRINT` skipped). The ec20 fixture (`rlm_fixture_simple_ec20`: the `rlm_04` config, full
         corpus, `regab_allow_duplicate` = false) built in ~20 s, the `CLIENT_CHECK` gate passed (18 932 residuals, max
         difference 0.000e+00), the saved model loads with ec = 20 and `w_dense` (6 627,) and evaluates real positions.
         The 12 static tests (no pipeline, no DB, no artifact required) pin the paths, the config contract, the gate
         message and the idempotency. The other set members (ec19…ec16 — the depth ladder 1…4 of the multi-ply EF) are
         replicated once this round proves the cycle. No production code changed.

D-672 | 2026-11-22 | The LM fixture set completed to the full five-member depth ladder. The ec20 round (D-671) proved
         the cycle, so the replication landed: the four configs `rlm_fixture_simple_ec{19,18,17,16}.json` (generated
         from the ec20 template — the `rlm_04` config, full corpus, `regab_allow_duplicate = false`,
         `plot.enable = false`, per-member name / `empty_count` / `base_dir` / `output`) + the house copyright header
         added to `fixtures.py` and `test_fixtures.py` (it was missing — user catch). The test module now pins ALL FIVE
         configs (the identity / `output` location / flags per member via subTest, and the `rlm_04`-inherited training
         sections with `rlm_04`.json ITSELF as the direct reference — no hardcoded values). The four builds ran in ONE
         CLI call (11.3 s total, ~2.8 s each — the deeper corpora are smaller than ec20's), every one passing the
         `CLIENT_CHECK` gate (18 844…18 929 validation residuals, max difference 0.000e+00). Smoke: all five models load
         with the right `mw.ec` (20…16), the identical `w_dense` (6 627,) shape class, and agree in magnitude on the
         same positions (26…31). The multi-ply EF depth ladder (positions at A = ec20 over models at B = ec20…16 →
         depths 0…4) is now fully on disk. No production code changed.

D-673 | 2026-11-22 | The direct not-existing-fixture gate test. The user's review caught the gap: the missing-fixture
         cases were pinned only via MOCKS (the patched `FIXTURE_ROOT`) + the create missing-config case — there was no
         DIRECT test calling `require_lm_fixture` with a name that genuinely does not exist and capturing the exception.
         Added `test_require...::test_not_existing_fixture_raises`: `require_lm_fixture`('`not_existing_fixture`')
         raises the actionable `RuntimeError`, and the message is checked for BOTH the exact build command
         (`python -m test.reversi.fixtures create not_existing_fixture`) and the missing model path — no mock, the
         missing state is the real one (the name is never built, on any machine). The build command itself is documented
         in four places (the `fixtures.py` module docstring, the mirror doc, every config JSON's description field, the
         notes) — confirmed by the same review. 13 tests, green. No production code changed.

D-674 | 2026-11-22 | The multi-ply EF, stage 1: the compiled EF leaf kernel + the per-model index plan (the module is
         unfrozen — the D-670 range contract + the D-671/672 fixture set cleared the way). `reversi/lm/multi_ply_ef.py`
         carries: `prepare_multi_ply_plan(mw)` (the 17-tuple: the client's `expanded_offsets` + the z2y affine a1/b1
         (the EXACT `hlp_zed` formula) + the intercept flag + the mobility masks/sides + the 11 pattern-block arrays)
         and the two private njit kernels — `_ef_leaf_indexes` (the SAME njit index pipeline the client EF uses: the
         anti-transformations + the mobility + the principal-indexes kernels inlined, the pydantic wrapper removed) and
         `_ef_leaf_value` (index row + f32 gather + SEQUENTIAL f32 sum + the scipy piecewise f32 expit + the z2y
         affine). The parity contract, refined with measurements (not vibes): the INDEXES are bit-exact (same kernels —
         pinned by `assert_array_equal`); the depth-0 anchor (A == B) will be bit-exact BY DELEGATION to the client EF
         (D-675); the search leaf is deterministic and within a measured bound of the client EF — the numpy pairwise sum
         vs the sequential f32 sum was measured at <= 409 ulp on the linear predictor, and the D-674 run on 100
         fixture-ec16 playout positions shows the real margin: max 8e-6 in Y, mean 6.5e-7, 85/100 positions bit-equal —
         the test bound 0.05 is a drift detector 6000× above the measurement. The 4 tests (no DB: the fixture ec16 model
         + 100 seeded playout positions) are green in 0.7 s. D-675 next: the float32 alpha-beta search (the
         endgame-solver discipline: zero-window, static bsf order, strict tie-break, the C root window ±66 — the R =
         64/(1−2c) + margin of D-670) + the public `make_evaluation_function(mw)` factory + the depth-ladder tests over
         the five fixtures.

D-675 | 2026-11-22 | The multi-ply EF, stage 2: the float32 alpha-beta search + the public
         `make_evaluation_function(mw)` factory. The search (`_ab_eval`, njit) is the endgame-solver discipline in its
         value-only variant: the horizon node is the EF leaf, the terminal the exact WOF as f32, the no-move node passes
         (sides swap, value negated), the static bsf move order, the zero-window propagation, the cutoff at value >=
         beta, the strict > alpha rise. Three implementation findings, all pinned by tests: (1) the batch
         `parallel=True` index kernels CANNOT be called from the worker-pool threads (the LLVM `allocate_sched` crash) —
         the leaf became a SERIAL transcription of the kernel bodies (the anti-transformation scalar impls, the mobility
         loop, the pack/base-3/coset-min pipeline), which is 170-190x FASTER at N=1 (depth-4: 242 ms/pos -> 1.3 ms/pos —
         the batch forms pay a large fixed prange overhead per call); (2) the window state is F64, not the solver's
         int64: the f32 values stored in an int64 state TRUNCATE the window (2.0539 -> 2) and break the zero-window
         tightening — the depth-2 oracle caught it (up to 0.7 in Y on 6/50 positions); (3) the root window is [-R, +R]
         with R = ceil(64/(1-2c)) + 1 = 67 for c = 0.01 (the factory first shipped it inverted — the values came out at
         the window bound). The factory is strict array (the PositionArray validator), checks A >= B (ValueError naming
         the offending count), delegates the A == B lanes to the client EF (the bit-exact depth-0 anchor) and runs the A
         > B lanes on the worker pool. The 18 tests (no DB) are green in 0.7 s fast / 1.8 s LONG (the full 100-scale
         oracle + structural in the LONG tier; the fast scale is 10-20 positions per test): depth-0 anchor bit-exact,
         depths 1-2 vs the INDEPENDENT full-width minimax oracle (pure Python, no pruning — its independence is in the
         search logic, the leaves use the separately-pinned compiled leaf), depths 3-4 structural (range within
         the D-670 R, determinism), the search contract (A < B ValueError, scalar/list ValidationError, empty batch),
         and the discipline on a trivial intercept-only model (normal root -y0, pass root +y0 against the scipy-expit
         reference y0). The `endgame_solver` doc "Next" line now points at the final `reversi.lm.multi_ply_ef` /
         `make_evaluation_function` naming. v1 is value-only: the move-ordered / root-best-move stage stays deferred
         (the user: "per ora NON facciamo un dynamic ordering").

D-676 | 2026-11-22 | R-540 compliance for the multi-ply EF: all the D-XXX provenance removed from the docstrings of
         `reversi/lm/multi_ply_ef.py` (7) and `test/reversi/lm/test_multi_ply_ef.py` (9) — the references were rewritten
         as plain design summaries (the measured bound, the worker-pool idiom, the output range contract) with the
         number dropped; the `#` code comments already carried none. The mirror docs keep their D references (docs are
         not bound by R-540). The fixture files were checked and were already clean. Docstring-only change: 18 tests
         green.

D-677 | 2026-11-22 | Overview: the ENDGAME-SOLVER and the MULTI-PLY campaigns are complete (for now) — their two
         Next-steps entries were removed and replaced by a single composed Current-state entry (the ported/compiled
         endgame solver + the multi-ply evaluation function extending the LM pipeline). Next steps now open with
         MOVE-PROB.

D-678 | 2026-11-23 | The 0153 series: the book §17.5 reference model 0153 (the series best performer — RMSE val 6.50,
         711,853 active weights) is re-trained with its feature set held fixed (2X6COR, CASTLE, 3X4COR, R4, BARBEL,
         DIAG7, DIAG6, DIAG5, R2, R3 + OptMob) at ec = 19..10: 10 new models, ID 0153 at each level (the user's explicit
         naming — the series carries the reference model's id, not the registry's next-sequential id), same corpus
         (batches 3, 9, 12 train / 6 val, CMS+CMR) and same `stat_model` / `optimization` hyperparameters. The configs
         are generated from the 0153 template by literal substitution of the 7 ec-specific fields (the feature set
         byte-identical); the 10 registry indexes gain their row. The original ec20 0153 completes the 11-member family;
         a characteristics table (RMSE train/val, active weights, iterations, corpus sizes) is the deliverable.

D-679 | 2026-11-24 | Multi-ply EF performance: the batch is split BEFORE dispatch — the A == B (horizon) lanes are
         evaluated in a SINGLE batched client-EF call (the EF is per-position, so the batched values are the individual
         ones — the bit-exact depth-0 anchor is preserved), and only the A > B lanes run on the worker pool. The
         per-lane pool delegation (the pydantic-wrapped `client_ef` called one position at a time) was the bottleneck at
         batch scale: the 189,721-position ply-0 anchor check ran in ~7 min; with the split the same check runs in 3.9 s
         (the 1.7 s DB extraction + two batched EF calls), same result (6.5035 = the 6.50 of the 0153 ec20 validation).
         18 tests green (fast tier).

D-680 | 2026-11-24 | The 0153 multi-ply depth ladder: the search-based evaluation of the 0153 family is validated on the
         batch-6 / ec-20 corpus (the 189,721 deduplicated positions + the nested 10k / 1k deterministic samples): the
         RMSE(y) is monotonically decreasing over all nine rungs — 6.2546 (depth 0, the 0153 ec20 direct) → 5.6223
         → 5.1580 → 4.8648 → 4.5339 → 4.2302 → 4.0941 → 3.9164 → 3.7164 (depth 8, the 0153 ec12) — with diminishing
         per-ply gains (0.63, 0.46, 0.29, 0.33, 0.30, 0.14, 0.18, 0.20), the 1k ladder tracking the 10k / full-batch
         ladders within the sampling noise. The 1-ply search already beats the direct ec20 evaluation by 0.64 RMSE. The
         per-ply wall-time growth is 4.4–4.9x against the expected 3.0–3.3x (the I-024 alpha-beta / dispatching
         investigation is the next step). The ladder is parked at depth 8 (the user's call).

D-681 | 2026-11-24 | Multi-ply EF parallelism (I-024, first of the two fixes): the batch search over the above-horizon
         lanes is a SINGLE njit call on numba's workqueue (a `prange` over the lanes, the new `_search_prange`) instead
         of the Python worker pool (one thread per core pulling lane indices from a queue). Rationale (the I-024 phase-1
         diagnosis): in this numba 0.68 x CPython 3.14 environment the GIL IS released per njit call (a 2-thread busy
         probe scales 2.20x) but 8 Python threads over njit calls stall at 2.18x — the pool ran the depth-6 / 1k test
         case at ~1-2 cores (the user's htop: per-core 10-37%, load average 0.89; user-time ~ wall-time), while numba's
         own threadpool scales (the same test: 101 ms/lane pool -> 18-26 ms/lane prange, flat from 100 to 1000 lanes).
         The per-lane values are BIT-EXACT with the pool form (0/1000 lanes differ at depths 3 and 6, the search is
         per-lane independent). 1342 fast-tier tests green. The second I-024 fix (the move ordering, the 4.91x/ply node
         growth against the ideal sqrt(b) = 3.11x) is deliberately SEPARATE: it will be measured single-thread vs
         single-thread first, and only then combined with the parallel form (the user's call).

D-682 | 2026-11-24 | Multi-ply EF move ordering (I-024, second of the two fixes): the `_ab_eval` move loop is the FIXED
         best-first group order ported from the C fast endgame solver's `worst_to_best` table — the 64 squares in 10
         priority groups (the corner rings first, the X-squares last, the central four appended after them; the central
         four ARE searched, unlike the C which skips them, so the value stays the exact minimax), `legal` is masked with
         the groups in priority order and each group's legal bits are scanned BSR-first (the C's within-cluster
         convention; the new njit `_bsr` in board.py, the descending twin of `bitboard_bsf` — the public `bitboard_bsr`
         is the `@validate_call` Python form, not njit-callable). Measured SINGLE-THREAD vs SINGLE-THREAD first (the
         agreed methodology): on the 250-position sample, depth 5 -40% nodes / 2.0x faster, depth 6 -52% nodes / 1.5x
         faster, the values BIT-EXACT (250/250 lanes) vs the former bsf order — the wide root window contains the value
         range, so the search is the exact minimax and the ordering only changes the node counts, never the values. The
         1k depth-5/6 values are bit-exact vs the pre-change production (1000/1000 lanes); the depth-6 / 1k 8-core wall
         drops 25.8 s -> 6.4 s (4x). The first A/B round was invalidated by two scratch bugs (the table slice
         `[59:0:-1]` dropped the worst square — G7 — and a patch indentation break); after the fix the values are
         identical as the theorem requires.

D-683 | 2026-11-24 | Multi-ply EF suite compile time (the fast-tier budget): `_search_prange` was the only njit in the
         module WITHOUT `cache=True` (the other three — `_ef_leaf_indexes`, `_ef_leaf_value`, `_ab_eval` — were already
         cached), so every fresh process re-paid the ~5.5 s compilation of the prange entry point, and the first tests
         to call it carried it: `test_depth1_vs_minimax_oracle` (5.46 s) and `test_normal_root_is_minus_y0` (5.72 s) —
         the latter also triggers a SECOND `_search_prange` overload (the TRIVIAL discipline model passes
         `horizon_stones` as int64, the parsed fixture models as uint32). The test bodies themselves are ~0.1 s warm.
         Fix in the source (no test change, no coverage loss): `cache=True` on `_search_prange` — the compilation is now
         a one-time cost per source change, subsequent processes load the cached code. Warm cache: both tests under 0.5
         s, the 1k d5/d6 values bit-exact (1000/1000) vs the pre-change baseline, 1347 fast-tier tests green.

D-684 | 2026-11-24 | The LM fixture family `rlm_fixture_simple_ec*` is extended from ec16-20 to the FULL ec0-20 ladder
         (16 new committed config JSONs; the .dat artifacts stay git-ignored, rebuilt on demand via
         `python -m test.reversi.fixtures create <name>` as before). Rationale: the multi-ply EF branch tests (the
         in-search terminal, the internal pass) and the deep-search equivalence battery need small-ec models (horizon >=
         60 stones); the user: "estendiamo, generiamo da [0..20] TUTTI ... anche lo 0 che non si usa ... ma tanto per
         casistica generale". The `test_fixtures.py` registry ECS is now (20..0) and the `TestFixtureConfigs` contract
         (identity, output location, the fixture flags, the `rlm_04` inheritance) covers all 21 members automatically;
         the DB corpus is sufficient at every ec (~200k train positions per ec at bid 6, the ec0 the largest at 297k).

D-685 | 2026-11-24 | `endgame_solver` coverage — the mirror `test_minimax_check_ec_gate` (TestUnifiedSolveApi): the
         `check_ec=True` boundary guard of `minimax_solve` (the `uniform_empty_count` call) was the one genuinely
         uncovered contract line of the module — the alphabeta twin was covered by `test_check_ec_gate`, and both log
         guards by `test_array_log_raises` (the coverage study had misread line 458 as the log guard; it is the
         `check_ec` line). The remaining uncovered lines (the 403-404 / 412 worker-pool error net) are left as-is by
         design: a defensive path not triggerable with valid positions (the bit arithmetic raises nothing).

D-686 | 2026-11-24 | `multi_ply_ef` deep-branch tests (the `TestMultiPlyEfDeepBranches` class): the two `_ab_eval`
         branches the shallow fixture depths never reach. (1) The in-search TERMINAL — the double-pass node above the
         horizon returns the exact WOF (`final_value_of`); pinned with 'black-wins-by-wipe-out' (13 empties) over the
         ec0 fixture (the horizon the 64-stone board: every leaf an exact terminal) — the value asserted identical (as
         float) to the independent exact engine `alphabeta_solve` (-64.0 == -64). (2) The in-search PASS — the no-move
         node above the horizon swaps the sides and negates; pinned with 'woc18-FKvsAP-g1-03' (3 empties, 61 stones — a
         legal move leaves the opponent with no legal move, the 62-stone child the pass node) over the TRIVIAL model at
         ec1 (the horizon 63: the pass node below it, the 63-stone leaves the closed-form constant), the value asserted
         against the independent Python minimax oracle (the same contract, no pruning) — bit-identical in the prototype,
         delta 1e-4 in the test (the house TRIVIAL idiom). Both positions from the committed sample DB
         (gpdb-sample-games.txt); the pass test pins its precondition (the internal pass must exist) so the test keeps
         testing what it claims.
