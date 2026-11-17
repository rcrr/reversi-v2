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
