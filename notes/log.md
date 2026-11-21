# Session journal — volume 006 (sessions 128–...)

Format rules: notes/log_rules.md (rigid — follow when editing this file).

## 2026-11-15 — session 128 (housekeeping — the overview trim + the journal / decisions volume rotation)

- notes/overview.md — the two editorial removals per the user: the "Current state" entry "The USO (FEATURE-SET) campaign
  stands at ec20 …" (not a realization milestone in itself — its substance is 100% documented in the LaTeX book named by
  the entry just above it) and the "Next steps" entry "The FEATURE-SET campaign (the scope): …" — the campaign list now
  opens at MULTI-PLY. (D-628)
- notes/log.md + notes/decisions.md — the two volume rotations at the session boundary (the user's end-of-session
  housekeeping): the journal volume 005 (sessions 102–127, 26 sessions > the 25-session cap, 728 lines) closed as
  notes/hist\_log/log\_005.md with the H1 range final 102–127, the new volume 006 opening at session 128; the decisions
  log (D-426…D-627, 2811 lines > the 1000-line cap) closed as notes/hist\_decisions/decisions\_007.md, the new log
  opening at D-628. (D-629)
- notes/overview.md — the Index updated for the three rotated files (decisions\_007, log\_005, log.md at volume 006).
- notes/decisions.md + notes/overview.md — the record-integrity disclosure (the rules-compliance audit, zone A): D-627
  and D-463 are cited in the journals, the D-629 entry and the Index, yet exist in no decisions volume (D-627 was never
  written to the log at the session-127 close); the gaps are disclosed, the Index range corrected forward
  to D-426…D-626, the frozen volume untouched. The audit file joins the Index. (D-630)
- src/reversi/pattern.py + the 5 lm modules + probes/verify\_wmaps.py + run\_utests.sh — the R-520 rewrap: the 21 lines
  over the 120-char ceiling split back under it, no semantic change (0 lines over 120 in the tracked sources;
  test\_pattern + verify\_wmaps green). (D-631)
- the 7 probe files — the R-550 reword: the 8 I-XXX references in probe COMMENTS now name the change in words ("the
  level reordering", "the backlogged item realized" …), the R-580-allowed check labels untouched; 0 I-XXX in probe
  comment lines. (D-632)
- notes/rules.md (R-330) + notes/docs\_rules.md §7 + notes/overview.md — the `__init__.py` mirror-doc exception
  legislated (the user's choice (b)): the 6 package `__init__.py` files are exempt from the one-file-one-doc rule,
  declared conformant; the overview's 1:1 claim is now true again. (D-633)
- docs/test/reversi/test\_index.md — rewritten to the test-doc skeleton (the auditor's 4 sections) and un-staled: 4
  classes / 10 tests, not the 2 / 5 the old doc claimed. (D-634)
- docs/ — the batch rewrap: all 38 docs with a format finding rewrapped to the house form (the 58 over-120 lines, the 3
  split code spans healed), the 3 ragged Coverage tables repaired (escaped pipes), wrk\_vld\_positions.md back under
  120; the docs audit now reports ZERO non-size findings (the 9 size-budget items disclosed, not padded). (D-635)
- wsutils/notes\_lint.py + notes/log\_rules.md — the R-200 historical exception: the LISTMARK guard (born D-484, after
  the D-368 cleaning) no longer reaches into the frozen hist\_\* corpus — the 26 documented residue markers in closed
  journal volumes 000–003 stand; the check stays fully active on the open files. (D-638)
- notes/hist\_log/log\_000.md + log\_003.md + log\_004.md — the three H1 factual corrections (the one class the archive
  freeze allows): "1–24"→"1–23", "38–89"→"38–78", "90–101"→"90–101, 98 missing" — the 13 phantom session numbers
  resolved, no session content touched (logged as D-639: the D-636/D-637 numbers stand skipped by the mid-campaign
  renumber). (D-639)
- notes/decisions.md — the R-130/R-100 disclosure + forward ruling: the post-rule DSH/vLLM/DeepSeek infra notes and the
  Italian journal prose in the closed volumes are disclosed (with the file:line inventory); going forward the prose is
  English (verbatim user quotes exempt) and the publication edit pass is the sole sanctioned strip of the infra notes;
  the credential detail in log\_000 is noted as publication-sensitive. The frozen corpus is untouched. (D-640)
- the 7 test modules — the R-750/R-760 anchoring: every TemporaryDirectory / mkdtemp now under the shared
  CUSTOM\_TMP\_BASE (6 modules out of the system /tmp; test\_state\_machine drops its self-derived TMP\_DIR for the same
  anchor); 136 tests, 0 failures. (D-641)
- notes/rules.md — the R-060 re-sync: the domain rule-file list now names wsutils.md (not the non-existent tools.md) and
  adds latex\_rules.md + design\_principles.md; the reported missing L62 blank line re-verified as a false positive (it
  is present at HEAD). (D-642)
- The rules-compliance fix campaign CLOSES here (D-630…D-642, 11 items, the user's item-by-item approvals): 40
  violation-class findings from the audit are fixed or legislated; what stands open by decision: the 9 docs size-budget
  items (disclosed, not padded), the 19 over-long test docstrings (R-570, minor), the R-560 backlog reflow (8 files),
  the 24 W291 banner lines, the .gitignore R-300 amendment and the R-310 mirror clause (the user's open question), the 3
  stale verify\_gradient pins, and the zone-F probe naming / headers / DP-010 (the user asked for a fuller explanation
  first).
- notes/rules.md (R-300) — the .gitignore is affirmed as-is (the user's call): the 5 over-list lines are sanctioned
  functional entries (`__pycache__/`, `*.egg-info/`, the Emacs lock patterns, `.env`) and the section headers + blank
  separators are formatting — the register now says so. (D-643)
- The audit's remaining minor items are LEFT AS-IS (the user's explicit call) — they stand disclosed in the audit
  report; the R-310 mirror clause (the 6 src modules without a test mirror) awaits the user's separate decision. (D-644)
- The 6 missing test mirrors are CREATED (the user's call: brief, compact, sub-second — the anticipated DUMMY fallback
  proved UNNEDED: all 6 admit real fast NO-DB tests): test\_base\_model (9), hlp\_analytics (8), hlp\_final\_log\_print
  (3), hlp\_validate (7), model\_weights (5), wrk\_save (4) — 36 tests, 0 failures; each with its mirror doc + overview
  row; the suite is now 52 modules, all green. The R-310 mirror question is RESOLVED — no amendment needed. (D-645)
- Session 128 CLOSES: the rules-compliance audit fix campaign is complete (D-630…D-645 — the 40 violation-class findings
  fixed or legislated, the minors left as-is by the user's call, the 6 missing test mirrors created; the suite is 52
  modules, all green, the notes lint and the docs audit stand at their disclosed residue). The audit report
  (notes/analyses/rules\_compliance\_audit\_2026-11-15.md) joins the repo with this close. Next session: the project's
  campaign list stands (the overview Next steps, the MULTI-PLY first).

## 2026-11-17 — session 129 (MULTI-PLY campaign — step 1: the GamePosition entity + the gpdb reader)

- The design discussion (the user's "riflettiamo" phase) settles the step-1 contract: `GamePosition` = the structured
  dtype built from `Position`'s own `descr` + the `player` field (the "Position + player" contract by construction);
  `Player` = uint8 (0/1, the C values); the 65-char string form (64 board chars [bw.] + 1 player char, NO separator) is
  always and only a GamePosition — the legacy C `game_position_x_from_string` / `_to_string` scope (the user's 8.2
  correction: no separate `bitboards_from_board_str` in `board.py`); the v2 relative-view pivot (mover / opponent /
  player, consistent with the REGAB DB design; the player is the absolute anchor for history-less mid-game positions,
  superfluous to the ML features); the C loader flag trio mirrored with defaults; the file-format layer in the new
  module, the string↔GP conversion in `board.py`.
- src/reversi/board.py — the GamePosition entity: `Player` + `PLAYER_BLACK` / `PLAYER_WHITE` + `PlayerArray`, the
  `GamePosition` dtype, the `GamePositionField` / `GamePositionArray` pydantic hints, `make_game_position` +
  `make_game_position_from_position`, `game_position_blacks` / `game_position_whites`, `game_position_from_str` /
  `game_position_to_str` (+ the 13 `__all__` names, the docstring bullet). (D-646)
- src/reversi/game\_position\_database.py — the new module: the gpdb record format port (the `GpdbErrorType` six
  classes, the `GpdbSyntaxError`, the `GpdbEntry` dataclass, the `GamePositionDatabase` container, the
  `load_game_position_database` with the C flag trio; the parse mirrors the C `gpdb_parse_line`, the load loop composes
  the public `game_position_from_str`). (D-647)
- The tests + the fixture + the runner: the `TestGamePosition` class (14 tests) in test\_board.py; the new
  test/reversi/test\_game\_position\_database.py (22 tests); the VERBATIM legacy fixture
  test/reversi/data/gpdb-test-db.txt (md5-identical; the C `gpdb_verify` cross-validation surface — 6 entries + 11
  errors, the exact (line, type) sequence pinned, the string round trip against the file's own records); the module at
  its canonical run\_utests.sh position (after test\_board). Self-inflicted fix, disclosed: the first loader draft
  dropped the "entry is new" branch (0 entries loaded) — caught by the fixture test, repaired forward. (D-648)
- test/reversi/data/gpdb-ffo.txt + gpdb-sample-games.txt — the two legacy gpdb fixtures join the repo as VERBATIM copies
  (md5-identical, the original names) in the fixture zone (the user's call after the placement discussion:
  `test/reversi/data/`, NOT a new top-level `db/` zone — a zone without a runtime mandate; the FFO corpus is the
  cross-validation surface of the future ENDGAME-SOLVER port). (D-649)
- Suite: 1187 → 1223, GREEN 1223/0/88 (the default tier via the wsutils measurement wrapper; the LONG=1 suite\_audit
  gate measurement re-run as well).
- test/reversi/test\_board.py — the `TestPositionMakeMoveGpdbParity` class (4 tests): the `make_move` parity on the C
  make-move corpus (the four make-move-test-case-{a..d} before/after pairs of gpdb-sample-games.txt, the moves D4 / D4 /
  D4 / B4 pinned to the case table and to the fixture's own descriptions) — all 4 pass at first run. Placement: in
  test\_board (the SUT dependency stays board.py alone — the `_record` helper does minimal fixture access, the
- test/reversi/test\_board.py + docs/test/reversi/test\_board.md — forward correction of the D-650 class (the user's
  call): RENAMED `TestPositionMakeMoveGpdbParity` -> `TestPositionMakeMoveGpdb`, the docstring and the area G line
  rewritten to state what the test does — the "parity with the C" framing was a category error (`make_move` agreeing
  with the C is the rules of the game, not a pin; the fixture supplies realistic mid-game positions for the contract
  test); test docstrings state what the code does, never its history. (D-651)
 - src/reversi/endgame\_solver.py — the scalar exact endgame solver: `minimax_solve` (the DFS minimax, the static A1..H8
   move order, the strict comparison, the relative values by sign flip, the WOF leaf value from board.py, the terminal
   check preceding the pass) + the frozen `SolverResult` (the np.int8 game value). Verified node by node against the C
   game-tree log. (D-652)
 - test/reversi/test\_endgame\_solver.py + run\_utests.sh — 10 tests: the result container, the seven hand-built
   micro-endgames, and the ffo-01-simplified-8 fixture loaded through the gpdb module (value 18 / 46 nodes / 15 leaves /
   the final position / the A1-B1-H1-G2 solution line — cross-validated against the C oracle). (D-653)
 - endgame\_solver trace (D-654): the `NodeRecord` (the six fields of the first trace version) + the optional `log`
   callback of `minimax_solve` (one record per node, emitted at the node's exit); the pass is now a real recursive node;
   the C game-tree log of ffo-01-simplified-8 becomes the `es_log_ffo-01-simplified-8.csv` fixture; the new trace test
   compares 46/46 records one to one with the log.
 - endgame\_solver API polish (D-655): `SolverResult.final_game_position` is annotated `GamePositionField` (the house
   scalar alias) and the `NodeRecord` move fields use the sentinel codes `MOVE_UN` / `MOVE_NA` / `MOVE_PA` instead of
   `None`.
 - The game-value types moved from `regab.py` to `endgame_solver.py` (D-656): `GameValue` + `GameValueArray` + the
   validator are now defined at the producer (the solver, going 100% vectorized); `regab.py` imports and re-exports them
   (its public surface unchanged); `SolverResult.game_value` is annotated `GameValue`; the validator gains three direct
   tests (`TestGameValueArrayValidator`) — the module is now 100% statement / branch covered by its own suite
   (`coverage` 7.17.3, installed in the venv).
 - Next: the user's further instructions on the endgame-solver step (no commits made this session so far), then the
   MULTI-PLY step 2.

## 2026-11-18 — session 130 (ENDGAME-SOLVER — the GamePosition-only field decision + the generic fixture series 4–8)

- The user's field decision closes the design of the search: the game tree uses `GamePosition` and ONLY `GamePosition`
  (no `Position`, no `mover` / `opponent`, no standalone `player`); the elegance must be visible in the code and the
  encapsulation must not cost performance (board.py exports the kernels — the public per-lane bitboard primitives —
  for the future numba inlining).
- src/reversi/board.py — the three GamePosition-level game-tree tools (`game_position_make_move` /
  `game_position_legal_moves` / `game_position_final_value`: the private prange kernels compose the public
  `flips_of_move` / `legal_moves_of` over the field views, the wrappers give the scalar/array contract) + `bitboard_bsf`
  (the njit ascending twin of `bitboard_bsr`) + the private `_popcount` (numba has no `np.bitwise_count`). Numba
  findings: no structured-scalar construction (the kernels work on three arrays, repacked with `make_game_position`);
  the make_move kernel applies the orientation rotation of `position_make_move` (the first version kept the
  orientation fixed and produced inconsistent game positions — caught by the parity smoke test). (D-657)
- src/reversi/endgame_solver.py — the `search` rewritten GamePosition-only on the three tools, with the user's six
  style notes: no comment lines; the root at level 0, the first statement `level += 1`; the return type in the
  definition; no `int()` cast; the `range(64)` scan replaced by the `bitboard_bsf` loop; the `None` accumulators
  replaced by the out-of-range initialisation (the new `OUT_OF_RANGE_DEFEAT_SCORE` = −66, the C constant). (D-657)
- test/reversi/test_board.py — 339 tests: the nine game-tree-tool tests (scalar/array parity with the position-level
  composition, the pass rotation, the out-of-range ValueError, the N-D shape) + the 1M-board PERF pair + the two
  `bitboard_bsf` tests. (D-657)
- test/reversi/test_endgame_solver.py + the four new C reference logs — the fixture test becomes the GENERIC case
  test (`CASES` entry + two one-line methods per case); the series grows to ffo-01-simplified 4–8 (22 tests): the
  references generated with the legacy toolchain (the C `endgame_solver -s minimax -l` + `read_game_tree_log`), the
  solution lines and final positions walked from the log's HASH links (the case-4 transpositions follow the first
  visit — the deterministic search gives the transposed visits the same best move, asserted). Suite runtime ~9 s
  (the 20040-node case 4 dominates) — the LONG territory, the numba-compiled scalar search is the next step. (D-657)
- Next: the numba-compiled scalar search on the same fixture series (the 20k-node case 4 is the target of measure),
  then the alpha-beta solver, then the vectorized design.

## 2026-11-21 — session 131 (ENDGAME-SOLVER — the numba-compiled scalar search + the fixture series 0–3)

- src/reversi/board.py — the fourth public per-lane kernel `final_value_of` (the nopython WOF twin of
  `position_final_value`, over `_popcount`; the parity test joins `TestPositionFinalValue`). (D-658)
- src/reversi/endgame_solver.py — the njit recursive `_search` (the nopython twin of the Python `search` closure:
  the position as the three field scalars, the four public per-lane kernels inlined) + the `minimax_solve`
  dispatch (`log is None` → the compiled fast path, the final position repacked with `make_game_position` and the
  njit returns cast through `np.uint64`; `log` given → the traced Python search). (D-658)
- test/reversi/test_endgame_solver.py — the fixture series grows to ffo-01-simplified 0–3 as solve-only cases
  (no trace, no CSV in the repo — the C references generated in scratch, the goldens extracted by the HASH-link
  walk); the 18M-node case 0 is LONG-gated (`tier_long`). Suite: 26 tests (25 + 1 LONG). (D-658)
- The measured state: the compiled throughput is flat at ~12.5 M nodes/s across the 0–5 series (case 0: 1.43 s,
  case 4: 1.6 ms vs ~7 s pure Python — ~4400x); against the legacy C the v2 is ~1.3–1.7x slower at large scale
  (the constant-factor gap closes as the cases grow: 1.7x at 18M nodes down to 1.3x at 105k) and faster at small
  scale (the C times include the process startup). The user's ruling: the numba engine is the working engine of
  the campaign (it will run for months solving the ML positions), the 1.7x is to be pursued, and the final
  high-perf solver will get a Rust version — the v2 numba engine is the reference of correctness for that port.
- Next: the user's further instructions (the candidates: the compiled trace, the alpha-beta solver).
 - The dual search implementation was dissolved per the user (no duplicated logic): the Python `search`
   closure is deleted, the compiled `_search` carries the trace as a typed-list sink (one 6-int tuple per
   node at the node exit, None untraced — the guards compile away), replayed to the `log` callback at
   completion; `_search` is `cache=False` (the numba 0.68 cache of the full function segfaults on load in
   a fresh process — bisected in scratch); the beauty notes landed: `other_player` (the new public per-lane
   player primitive of board.py) replaced `1 - player` and deleted the `int(gp['player'])` boundary cast,
   the defensive `int(MOVE_*)` casts dropped (numba widens the uint8 sentinels implicitly), the boundary
   casts now use the domain aliases (`Bitboard` / `Player` / `Move` / `GameValue`). The 5 trace tests
   validate the compiled path record by record; case 4: untraced ~1.1 ms, traced ~78 ms. (D-659)
 - Exhaustive coverage analysis of board.py (coverage 7.17.3, branch mode): the raw 70% is mostly njit
   invisibility artefact; the real gaps were closed with 8 new tests (340 -> 348): the
   position_is_game_over post-pass False branch, the N-D array paths of the two gp tools, the three
   game_position_make_move error raises, the GamePositionArray validator raise. The 267 remaining
   "missing" lines are all untestable: the njit bodies (compiled, invisible), the 4 @overload bodies
   (empirically never executed in this numba 0.68 + pydantic-wrapped configuration — 3 cold-cache runs +
   an isolated JIT-caller probe — while the JIT path they serve is tested with goldens), and 2 redundant
   guards preempted by the pydantic gates (structurally unreachable). Zero real gaps remain. .coverage
   added to .gitignore. (D-660)
