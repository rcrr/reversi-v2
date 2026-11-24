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
  encapsulation must not cost performance (board.py exports the kernels — the public per-lane bitboard primitives — for
  the future numba inlining).
- src/reversi/board.py — the three GamePosition-level game-tree tools (`game_position_make_move` /
  `game_position_legal_moves` / `game_position_final_value`: the private prange kernels compose the public
  `flips_of_move` / `legal_moves_of` over the field views, the wrappers give the scalar/array contract) + `bitboard_bsf`
  (the njit ascending twin of `bitboard_bsr`) + the private `_popcount` (numba has no `np.bitwise_count`). Numba
  findings: no structured-scalar construction (the kernels work on three arrays, repacked with `make_game_position`);
  the `make_move` kernel applies the orientation rotation of `position_make_move` (the first version kept the
  orientation fixed and produced inconsistent game positions — caught by the parity smoke test). (D-657)
- `src/reversi/endgame_solver.py` — the `search` rewritten GamePosition-only on the three tools, with the user's six
  style notes: no comment lines; the root at level 0, the first statement `level += 1`; the return type in the
  definition; no `int()` cast; the `range(64)` scan replaced by the `bitboard_bsf` loop; the `None` accumulators
  replaced by the out-of-range initialisation (the new `OUT_OF_RANGE_DEFEAT_SCORE` = −66, the C constant). (D-657)
- `test/reversi/test_board.py` — 339 tests: the nine game-tree-tool tests (scalar/array parity with the position-level
  composition, the pass rotation, the out-of-range ValueError, the N-D shape) + the 1M-board PERF pair + the two
  `bitboard_bsf` tests. (D-657)
- `test/reversi/test_endgame_solver.py` + the four new C reference logs — the fixture test becomes the GENERIC case test
  (`CASES` entry + two one-line methods per case); the series grows to ffo-01-simplified 4–8 (22 tests): the references
  generated with the legacy toolchain (the C `endgame_solver -s minimax -l` + `read_game_tree_log`), the solution lines
  and final positions walked from the log's HASH links (the case-4 transpositions follow the first visit — the
  deterministic search gives the transposed visits the same best move, asserted). Suite runtime ~9 s (the 20040-node
  case 4 dominates) — the LONG territory, the numba-compiled scalar search is the next step. (D-657)
- Next: the numba-compiled scalar search on the same fixture series (the 20k-node case 4 is the target of measure), then
  the alpha-beta solver, then the vectorized design.

## 2026-11-21 — session 131 (ENDGAME-SOLVER — the numba-compiled scalar search + the fixture series 0–3)

- src/reversi/board.py — the fourth public per-lane kernel `final_value_of` (the nopython WOF twin of
  `position_final_value`, over `_popcount`; the parity test joins `TestPositionFinalValue`). (D-658)
- `src/reversi/endgame_solver.py` — the njit recursive `_search` (the nopython twin of the Python `search` closure: the
  position as the three field scalars, the four public per-lane kernels inlined) + the `minimax_solve` dispatch
  (`log is None` → the compiled fast path, the final position repacked with `make_game_position` and the njit returns
  cast through `np.uint64`; `log` given → the traced Python search). (D-658)
- `test/reversi/test_endgame_solver.py` — the fixture series grows to ffo-01-simplified 0–3 as solve-only cases (no
  trace, no CSV in the repo — the C references generated in scratch, the goldens extracted by the HASH-link walk); the
  18M-node case 0 is LONG-gated (`tier_long`). Suite: 26 tests (25 + 1 LONG). (D-658)
- The measured state: the compiled throughput is flat at ~12.5 M nodes/s across the 0–5 series (case 0: 1.43 s, case
  4: 1.6 ms vs ~7 s pure Python — ~4400x); against the legacy C the v2 is ~1.3–1.7x slower at large scale (the
  constant-factor gap closes as the cases grow: 1.7x at 18M nodes down to 1.3x at 105k) and faster at small scale (the C
  times include the process startup). The user's ruling: the numba engine is the working engine of the campaign (it will
  run for months solving the ML positions), the 1.7x is to be pursued, and the final high-perf solver will get a Rust
  version — the v2 numba engine is the reference of correctness for that port.
- Next: the user's further instructions (the candidates: the compiled trace, the alpha-beta solver).
 - The dual search implementation was dissolved per the user (no duplicated logic): the Python `search` closure is
   deleted, the compiled `_search` carries the trace as a typed-list sink (one 6-int tuple per node at the node exit,
   None untraced — the guards compile away), replayed to the `log` callback at completion; `_search` is `cache=False`
   (the numba 0.68 cache of the full function segfaults on load in a fresh process — bisected in scratch); the beauty
   notes landed: `other_player` (the new public per-lane player primitive of board.py) replaced `1 - player` and deleted
   the `int(gp['player'])` boundary cast, the defensive `int(MOVE_*)` casts dropped (numba widens the uint8 sentinels
   implicitly), the boundary casts now use the domain aliases (`Bitboard` / `Player` / `Move` / `GameValue`). The 5
   trace tests validate the compiled path record by record; case 4: untraced ~1.1 ms, traced ~78 ms. (D-659)
 - Exhaustive coverage analysis of board.py (coverage 7.17.3, branch mode): the raw 70% is mostly njit invisibility
   artefact; the real gaps were closed with 8 new tests (340 -> 348): the `position_is_game_over` post-pass False
   branch, the N-D array paths of the two gp tools, the three `game_position_make_move` error raises, the
   GamePositionArray validator raise. The 267 remaining "missing" lines are all untestable: the njit bodies (compiled,
   invisible), the 4 @overload bodies (empirically never executed in this numba 0.68 + pydantic-wrapped configuration —
   3 cold-cache runs + an isolated JIT-caller probe — while the JIT path they serve is tested with goldens), and 2
   redundant guards preempted by the pydantic gates (structurally unreachable). Zero real gaps remain. .coverage added
   to .gitignore. (D-660)
 - Two warnings from the user's full-suite run were fixed: the NumbaTypeSafetyWarning (numba promotes every small-int
   binary op to 64 bits — `other_player`'s `Player(1) - p` typed uint64, the return annotation is not enforced by the
   compiler; fixed with the explicit `Player(Player(1) - p)` re-narrowing) and the pydantic ArbitraryTypeWarning (
   `minimax_solve` annotated the parameter with the raw GamePosition dtype; fixed with the house scalar-only alias
   GamePositionField); a PERF-gated throughput test for the 1.1M-node case 1 was added with the house printout (the
   user's tagging: case 0 LONG, case 1 PERF, the rest untagged); the throughput re-verified flat at ~19 M nodes/s across
   cases 0–3 (up from the earlier ~12.5, measured under a loaded machine) — no regression. (D-661)
 - The user asked why the numba cache of `_search` segfaults — expected behaviour or a library bug: a full scratch
   bisect with the real kernels and the verbatim search body answered it — the identical body with 6 parameters (± the
   counter array, ± the UniTuple trace sink) caches and reloads fine in a fresh process, the 7-parameter form (the
   `parent_move` scalar added) segfaults the loader on cache load: a numba 0.68 bug (the designed fallback for a bad
   cache is the recompile, not a crash), triggered by the 7th scalar parameter. The reformulation dodges it:
   `parent_move` moves out of the signature into the 2-element shared state array (state[0] the entry-order counter,
   state[1] the current `parent_move`, saved/restored around each recursive call) and `cache=True` is restored.
   Verified: full suite twice (run 1 writes the cache, 43.7 s cold; run 2 loads it, 12.5 s, all green, no segfault), the
   trace tests pin the `parent_move` column of all 20,040 case-4 records against the C goldens, pure execution 55/73 ms
   at 20.2 M nodes/s, the one-time per-process cache load is 0.28/0.45 s per specialization (replacing the 3.3/4.3 s
   compiles), the warm-cache suite total is 12.1 s (was 19.2 s). Bonus bisect finding: a structural clone whose 6-tuple
   return slots are type-underdetermined is silently unified to float64 and its generated code segfaults at run time (a
   second independent codegen bug); the real `_search` escapes it because the
   `best_fm, best_fo, best_fp = mover, opponent, player` line pins the slots to uint64/uint8 — proven by the bit-exact
   final-position goldens. The LONG-vs-warmup question for the two "slow" endgame tests became moot: cache warm, case 1
   is out of the top-15 slowest and the case-4 trace is 0.59 s, dominated by the one-time traced-specialization load.
   (D-662)
 - The C alpha-beta reference logs of the ffo-01-simplified 4/6/7/8 trace cases joined the test data (generated with the
   legacy `endgame_solver -s ab` + `read_game_tree_log`, the same 21-column game-tree log format as the `es_` family):
   the ab search visits 9.9x–25x fewer nodes than the minimax on this series (case 4: 2,029 vs 20,040; case 0: 1.7M vs
   18M), the best lines and final positions are the minimax ones (the same static order + the same strict tie-break).
   The 0–3 logs stay in the legacy scratch (KPI extraction only, not committed). (D-663)
 - The alpha-beta twin `alphabeta_solve` / `_ab_search` (the zero-window negamax: the same natural move order and strict
   tie-break as the minimax, the child window the negated CURRENT parent window, the cutoff when a child value reaches
   the node beta, the node best starting at the window alpha — a fail-low node exits with its window alpha and
   `MOVE_NA`; the root window is the C ground-node initialization [−66, 66], NOT the driver's [−64, 64] default):
   node-by-node EXACT against the C alpha-beta log — all 2,029 nodes of case 4 match on `call_id` / level / player /
   `parent_move` / value and on the entry window (the log ALPHA/BETA columns), 1,628 also on the best move. The 401
   apparent best-move differences turned out to be a C LOGGING ARTIFACT, not a search difference: the C node struct
   never initializes `best_move` at a non-improving (fail-low) node, so the log carries the stale value of the previous
   occupant of the stack slot (proven 401/401: each stale value equals the best move of the previous same-depth node;
   `gts_generate_moves` leaves `best_move` untouched). The v2 records `MOVE_NA` there — the only value consistent with
   the search. Debug trail worth keeping: the first trace comparison ran with a file-major square parser (the v2 and the
   C are both rank-major: A1=0, B1=1, ..., A2=8) inflating the mismatches to 1,718, and a mid-debug window
   instrumentation recorded the EXIT alpha (the final value) and compared it to the C ENTRY alpha — both fixed before
   the real comparison. The 4-element state array (counter, parent move, alpha, beta) keeps the 6-parameter signature
   (the D-662 numba 0.68 cache-loader trigger); the cache round-trip was re-verified on the final shape (write +
   fresh-process load, both exact). Solve level: case 4 (18, 2,029, 538), case 0 (18, 1,700,428, 420,214); the full
   suite 1,276 green. (D-664)
 - `TestAlphaBetaSolveFixture` (15 tests) joined the endgame suite: the 0–8 series against the C alpha-beta reference
   (the pruned node / leaf counts, the same value / final / line as the minimax), the node-by-node trace of cases 4, 6,
   7, 8 against the committed `ab_log_*.csv` fixtures (the best-move column compared only when the v2 record has a real
   best move — the C stale-value caveat), `test_ab_minimax_parity` (value + final position, the 1–8 series: both
   searches are exact), the PERF-gated case-1 throughput run (18.9 M nodes/s — the SAME per-node rate as the minimax:
   the alpha-beta speedup is the node-count reduction pure, 25x at case 1), the 1.7M-node case 0 LONG-gated (0.247 s, vs
   the minimax ~0.95 s). The docs followed (the module doc: the API row, the Architecture bullet, the trace caveat, the
   invariants, the open issues; the test doc: the coverage row, the goldens); the suite is now 1,291 tests, green.
   (D-665)
 - Per the user's request, three corner-case GamePositions joined both the minimax and the alpha-beta fixtures:
   `black-has-to-pass` (the forced first pass: the line opens with `--`), `ffo-01-simplified-12` (the already-finished
   game of the series: the single leaf, the WOF of the full board) and `black-wins-by-wipe-out` (the wipe-out win before
   ec=0: the full −64, the one-colour final) — all three already entries of the `gpdb-sample-games.txt` corpus. Goldens
   measured with both solvers (bhp −52: 196,030/55,778 minimax vs 23,977/5,963 alpha-beta; 12: +18, 1/1; wo −64:
   4,900,474/1,367,719 vs 310,082/74,388). The solution lines were extracted ply by ply (the first static-order move
   achieving the exact value at the actual position — the search's own tie-break): the naive trace-chain walk is
   unreliable on transposed positions (several nodes share the same level / parent-move pair) and produced a wrong line
   on both pass-containing cases; the per-ply extraction replays to the golden finals. The fixtures gained `CASES[12]`
   and the `CASES_CORNER` dict + `_solve_named` (the `--` entries replay as the player-swap move, which
   `game_position_make_move` already supports); six new tests (three per fixture), the 4.9M-node wipe-out minimax in
   ~0.25 s (fast tier, untagged). The test doc and the notes followed; the suite is now 1,297 tests, green. (D-666)
 - The vectorized array solver took the worker-pool engine (B) over the frontier-vectorized core (A) — the user's "does
   the vectorization pay?" question, decided with an analysis and the user's 100% agreement: A's numba payoff is 1.5–4x
   single-core (the irregular mask/gather/cutoff control flow is not auto-vectorizable), B gives ~8x on this 8-core
   machine with ZERO new search code (every lane is its scalar `_ab_search` result — the node-level goldens carry over
   per lane for free), dynamic dispatch is optimal for the 100x solve-cost variance, and A stays available later as an
   engine upgrade behind the same API (its true home is the Rust port: the batched design for the 1M–10M-position
   datasets, 1k–10k-lane batches parallelized pool style). Milestone 1 verified the GIL: 8 threads x njit scale (65.8x
   on the 10-task set). Built: `SolverResultArray` (the parallel arrays — the "group of arrays" shape),
   `uniform_empty_count` (the batch precondition, the distinct counts named in the raise),
   `alphabeta_solve_array(gps, check_ec=False)` (one thread per CPU, the work queue, the per-lane fast path on the
   compiled search, pydantic only at the batch boundary, lane errors surfaced). Six tests: the ten ec=8 lanes of the
   `regab_prng_gp` batch 7 (the user's set) against the INDEPENDENT DB game-value goldens [14, 22, 0, 2, 8, −8, −6, 28,
   −48, −22] (which also cross-validates the scalar solver against the C/REGAB database on that set), the per-lane
   scalar parity, the mixed corner batch, the empty batch, the check gate. A parked in ideas.md. The suite is now 1,303
   tests, green. (D-667)
 - The array scale-up: the `regab_prng_gp` table turned out to be reachable from this machine (the remote host
   gandalf.skynet, the `tst_regab` user, the `reversi` schema), so the 100 / 1000 sets are pulled STRAIGHT FROM THE DB
   with independent goldens (no seeded playouts): 100 = the batch 8 ec=8 positions in seq order, 1000 = the batch 9 (the
   batch 7 holds only 20 ec=8 rows — hence a distinct batch per set size, the user's 10 stay the embedded batch 7 set).
   The pool solves the 100-lane batch in ~0.32 s and the 1000-lane batch in ~0.22 s (2.3M nodes, 10.4 M lane-nodes/s —
   the 1000 batch is FASTER than the 100 one: the larger lane pool hides the max-cost-lane tail), both fast tier. Three
   tests: the 100 / 1000 value arrays against the INDEPENDENT DB goldens (the `check_ec=True` gate on both) + the PERF
   throughput printout. The suite is now 1,306 tests, green. (D-668)
 - The unified scalar / array API (the board.py idiom — the user's consistency call): both public solvers now take a
   scalar OR an array (one function, both forms) and return the `SolverResult` / `SolverResultArray` accordingly;
   `alphabeta_solve_array` is removed from the API (subsumed), `minimax_solve` gains the array form for symmetry. The
   dispatch is one `isinstance` at the boundary — NO performance cost (the scalar path is byte-identical, the array path
   the unchanged worker pool); the honest costs are formal only (the union return type, the form-dependent `log` /
   `check_ec` parameters — `log` is scalar-only, the array form raises). The pool machinery is the private
   `_solve_pool(gps, search, make_state)` shared by both engines (the `_mm_state` / `_ab_state` factories, now shared
   with the scalar paths). The idiom is in place BEFORE the multi-ply EF step (`alphabeta_eval` inherits the unified
   contract from day one). Four new contract tests (the form dispatch both engines, the array + `log` raise, the minimax
   array form of the ten batch 7 lanes against the SAME DB goldens). The suite is now 1,310 tests, green. (D-669)
 - The EF Y output range contract — the "bug" that was not a bug: the multi-ply planning surfaced the array EF
   measuring 65.30 beyond +/-64; the first reading (and a red reproduction test) treated the open window as the defect,
   but the complete `logit_clipping` review (the `hlp_zed` + `wrk_zed` docs, the latex book) showed NO clip documented
   anywhere in the inference chain — the clipping lives only structurally in the training targets. The user did the math
   and re-framed: the values beyond ±64 are the CONFIDENCE EXCESS (how much more certain the model is than the maximum
   score), and the ~200-model campaign found higher-clipping models perform BETTER (higher c widens the band: ±65.31 at
   c=0.01, ±80 at c=0.1) — learned, valuable signal. The proposed z2y clip was WITHDRAWN (it would flatten the tail into
   a ±64 plateau). The red test was converted into the design-pinning test
   `test_output_range_affine_image_with_confidence_excess` (the bound [−64/(1−2c), 64/(1−2c)] AND the deterministic
   excess presence) and the contract is now stated explicitly in client.md, `hlp_zed.md` (the [c, 1−c] domain is a
   property of the training z vector, not of the total z2y inverse) and the latex 080. No production code changed; the
   frozen multi-ply EF will use the window derived from c, no clip. (D-670)
 - The rebuildable LM test fixtures mechanism (the ec20 member): the multi-ply EF tests need REAL saved models on disk,
   so the user's design landed — committed config JSONs in test/reversi/data/, a small helper MODULE in the test tree
   (test/reversi/fixtures.py: clean / create(`force_rebuild`) / require + the `python -m test.reversi.fixtures` CLI),
   artifacts under build/tmp/fixtures/ (git-ignored), the consumers TIER-AGNOSTIC with an actionable error (the exact
   build command) when the artifact is missing, NO manifest, FULL `rlm_04` corpus (a build costs seconds), no
   format-versioning intelligence. The build runs the standard pipeline entry stopped at `CLIENT_CHECK` (the config
   `target_level` field is dead code — the stop is explicit in the helper; plot.enable = false in the config as well).
   The ec20 fixture (`rlm_04` config, full corpus, `regab_allow_duplicate` = false) built in ~20 s, the `CLIENT_CHECK`
   gate passed (18 932 residuals, max difference 0.000e+00), the model loads with ec = 20 / `w_dense` (6 627,) and
   evaluates real positions; 12 static tests pin the mechanism (no pipeline, no DB, no artifact required). The ec19…ec16
   set members (the multi-ply depth ladder 1…4) are replicated once this round proves the cycle. (D-671)
 - The LM fixture set completed to the full five-member depth ladder: the ec20 round proved the cycle, so the four
   configs `rlm_fixture_simple_ec`{19,18,17,16}.json landed (generated from the ec20 template: the `rlm_04` config, full
   corpus, `regab_allow_duplicate` = false, `plot.enable` = false, per-member name / `empty_count` / `base_dir` /
   `output`) and the house copyright header was added to `fixtures.py` + `test_fixtures.py` (it was missing — user
   catch). The test module now pins ALL FIVE configs (per member via subTest; the `rlm_04`-inherited training sections
   with `rlm_04`.json itself as the direct reference). The four builds ran in ONE CLI call — 11.3 s total, ~2.8 s each
   (the deeper corpora are smaller) — every one passing the `CLIENT_CHECK` gate (18 844…18 929 residuals, max
   difference 0.000e+00). Smoke: all five load with the right `mw.ec` (20…16), the identical `w_dense` (6 627,) shape
   class, and agree in magnitude on the same positions (26…31). The multi-ply EF depth ladder (positions at A = ec20
   over models at B = ec20…16 → depths 0…4) is now fully on disk. (D-672)
 - The direct not-existing-fixture gate test: the user's review caught that the missing cases were pinned only via mocks
   — added `test_not_existing_fixture_raises`: `require_lm_fixture`('`not_existing_fixture`') raises the actionable
   `RuntimeError`, the message checked for the exact build command + the missing model path, NO mock (the name is never
   built, on any machine). The build command is documented in four places (the `fixtures.py` docstring, the mirror doc,
   every config description, the notes) — confirmed by the same review. 13 tests, green. (D-673)
 - The multi-ply EF unfroze — stage 1 (the compiled EF leaf): reversi/lm/`multi_ply_ef`.py landed with
   `prepare_multi_ply_plan` (the 17-tuple: the client's `expanded_offsets` + the z2y affine a1/b1 + the mobility + the
   pattern-block prepared arrays) and the two njit kernels — `_ef_leaf_indexes` (the client's njit index pipeline
   inlined, bit-exact) and `_ef_leaf_value` (gather + sequential f32 sum + the scipy piecewise f32 expit + the z2y
   affine). The parity contract was refined with measurements: the numpy pairwise sum vs the sequential f32 sum is <=
   409 ulp on the linear predictor; on 100 fixture-ec16 playout positions the real margin is max 8e-6 in Y (85/100
   bit-equal) — the test bound 0.05 is a drift detector 6000× above. 4 tests green in 0.7 s (no DB). D-675 next: the
   float32 alpha-beta + the public factory + the depth-ladder tests over the five fixtures. (D-674)
 - The multi-ply EF stage 2: the float32 alpha-beta (`_ab_eval`, the endgame-solver discipline: zero-window, static bsf
   order, strict tie-break, the pass/terminal handling, the root window [-R, +R]) + the public
   `make_evaluation_function` factory (the A >= B contract, the A == B delegation to the client EF, the worker-pool
   batch). Three findings pinned by tests: the parallel index kernels cannot run from pool threads (the LLVM
   `allocate_sched` crash) — the leaf is now a SERIAL transcription of the kernel bodies, 170-190x faster at N=1
   (depth-4: 242 -> 1.3 ms/pos); the window state must be F64 (the int64 state truncated the f32 windows and broke the
   zero-window tightening — the depth-2 oracle caught it, up to 0.7 in Y); the root window ships as [-R, +R] (the first
   version had it inverted — the values came out at the bound). 18 tests green: depth-0 anchor bit-exact, depths 1-2 vs
   the independent full-width minimax oracle, depths 3-4 structural, the search contract, the pass/sign discipline on a
   trivial intercept-only model (the scanned ec28 pass constant). 0.7 s fast / 1.8 s LONG. (D-675)
 - R-540 compliance for the multi-ply EF: the user asked to remove every D-XXX reference from the comments/docstrings of
   reversi/lm/`multi_ply_ef`.py and its tests (rules.md R-540: no D-XXX provenance in docstrings). 16 references removed
   (7 module + 9 test) - each rewritten as a plain design summary with the number dropped; the # code comments already
   carried none. The fixture files checked clean. Docstring-only: 18 tests green. (D-676)
 - Overview updated (user-approved): the ENDGAME-SOLVER + MULTI-PLY campaign entries left the Next steps (both complete)
   — a single composed 3-line entry joined them in the Current state. (D-677)

## 2026-11-23 — session 132 (the 0153 series — the best-performer feature set across ec 19..10)

- The user's request: model 0153 (the book §17.5 series reference — RMSE val 6.50, 711,853 active weights, the best
  performer) is re-built as a series "always 0153" at ec = 19..10: 10 new models with the 0153 feature set held FIXED
  (2X6COR, CASTLE, 3X4COR, R4, BARBEL, DIAG7, DIAG6, DIAG5, R2, R3 + OptMob), only the empty count varying — the
  original ec20 0153 included, the family is 11; a table of their characteristics is the deliverable.
- Environment check: the local REGAB DB (`tst_regab@localhost`) is up and its (`batch_id`, `empty_count`, `status`)
  index serves the per-level counts — batches 3/9/12 (train) and 6 (val) carry ~2M/4M/8M and ~200K positions per ec
  level 10..20 (the full corpus is there for every level); 8 cores, ~100 GB RAM free; the reference ec20/0153 full run
  took 16.5 min, so the 10 serial runs budget at ~2h45.
- The 10 configs `models/lm/ec{19..10}/0153/lm_ec{XX}_0153.json` generated from the 0153 template by literal
  substitution of the 7 ec-specific fields (name, `empty_count`, description, `base_dir`, output, `log_file_name`, the
  header file name — the feature set / `stat_model` / `optimization` sections byte-identical), each re-parsed and
  field-asserted; the user then named the series after the reference — all 10 carry ID 0153 at their level (not the
  next-sequential 0109): files, registry rows, and build dirs renamed accordingly, no pipeline re-run. The 10 registry
  `index.md` files gain their 0153 row. The first run attempt failed at CONFIG (the base dir must pre-exist) — the 10
  `build/lm/ec{XX}/0153` dirs created, the runs proceed serially ec 19 → 10.
- The `localhost` REGAB DB is an SSH tunnel to the remote server: the 14M-position extraction that took 60 s in the
  reference ec20/0153 run takes ~8 min through the tunnel, so the series budget is ~24 min/run (~3.5 h for the 10). The
  ec19 run completed clean in 24 min: RMSE train 6.23 / val 6.50 (the SAME validation RMSE as the ec20 0153), W 715,129,
  1,021 iterations (`CONVERGED_MIN_GRAD`), 13,245,762 train / 189,117 val positions. The remaining nine (ec 18..10) run
  serially in the background.
- The 0153 series completed: all 10 runs clean (18/18 steps, client check 0.000e+00). The validation RMSE is essentially
  flat across the family — 6.43 (ec10) to 6.54 (ec13) against the 6.50 of the ec20 reference — while W rises 711,853 →
  725,463 (ec12) → 722,940 (ec10); the training RMSE holds at 6.21–6.25 and the iterations at 950–1,037 (ec14/ec11/ec10
  stop on `LOW_PROGRESS`, the rest on `MIN_GRAD`). The 11-member family is registered — all 0153 (the ec20 original +
  ec 19..10).
## 2026-11-24 — session 133 (multi-ply EF — the ply-0 anchor check + the batched horizon delegation)

- The ply-0 anchor check (`scratch/multi_ply_ply0_check.py`): extracted the batch-6 / ec-20 / CMS+CMR positions from the
  local REGAB DB (199,932 rows, 1.7 s) into `scratch/regab_ec20_bid_6/` (the raw + the pipeline-deduplicated frame as
  npz), loaded the 0153 ec20 model, evaluated with the multi-ply EF (A == B → the client EF): RMSE(y) 6.5035 on the
  189,721 deduplicated positions — the 6.50 of the pipeline validation, the depth-0 anchor confirmed at corpus scale.
- The first run took 7 min 05 s: the DB extraction was only 1.7 s, the rest was the PER-LANE `client_ef` delegation in
  `_search_pool` (189,721 pydantic-wrapped one-position calls). The fix splits the batch in the factory: the A == B
  lanes go to the client EF in a SINGLE batched call (the EF is per-position, so the values are the individual ones —
  the bit-exact anchor is preserved), only the A > B lanes enter the pool. Re-run: 3.9 s total, the same 6.5035. 18
  tests green (fast tier). (D-679)
- The ply-1 search check on the 189,721 batch-6 / ec-20 positions (`scratch/multi_ply_ply1_check.py`): the 0153 ec19
  model with the 1-ply multi-ply search scores RMSE(y) 5.8662 — 1.39 below the same model evaluated WITHOUT search
  (7.2600) and 0.64 below the 0153 ec20 direct evaluation (the ply-0 baseline 6.5035): the 1-ply search BEATS the direct
  ec20 model. Cost: 8.4 s for the whole batch on 8 threads (~45 us/position).
- The depth ladder extended to 8 on a nested 1,000-position sample (seed 42, drawn from the 10k): RMSE 6.2546 (d0)
  → 5.6223 → 5.1580 → 4.8648 → 4.5339 → 4.2302 → 4.0941 → 3.9164 → 3.7164 (d8) — PERFECTLY monotone over all nine steps,
  tracking the 10k ladder within the expected sampling noise (max delta 0.20 at d0/d1, 0.02–0.07 at d4–d7; the 1k RMSE
  standard error is ~0.13). The deep per-step gains (0.14/0.18/0.20 at d6–d8) sit at the 1k noise level — significant as
  a trend (the cumulative d5→d8 drop of 0.51 is ~4 sigma), not as decimals. The per-ply wall-time growth stays
  at 4.4–4.9x (against the user's expected 3.0–3.3x — the I-024 alpha-beta / dispatching investigation is confirmed
  worthwhile).
- I-024 phase 1 (the diagnosis; the instrumented scratch copy — the production source untouched): TWO bottlenecks, both
  confirmed. (1) The worker pool runs at ~1-2 CORES, not 8: the user's htop (per-core 10-37%, load average 0.89) and the
  run's user-time ~ wall-time (106 s CPU over 103 s wall) are the ground truth — my first bracket-based "100%
  efficiency" reading was an ARTIFACT (the per-lane wall brackets overlap because the threads wait inside the bracket;
  the bracket sum counts the waits, not the work). A decisive 2/8-thread busy-njit probe: 2 threads scale (2.20x) — the
  GIL IS released by numba — but 8 threads stall at 2.18x: Python-thread parallelism over njit calls is capped at ~2
  cores in this numba 0.68 x CPython 3.14 environment. Numba's OWN threadpool scales: the batch search written as a
  single njit prange over the lanes runs the REAL `_ab_eval` at 18.2 ms/lane (flat from 100 to 1000 lanes) vs 101
  ms/lane for the pool — 5.5x faster, and BIT-EXACT (0/1000 lanes differ from the production ef at the production window
  93; an apparent 1-lane difference was the scratch test's own wrong window 67). (2) The pruning is weak: 345 / 1,646 /
  8,551 / 40,210 nodes per lane at depths 3/4/5/6 — a 4.91x per-ply growth against the ideal sqrt(b) = 3.11x (root
  branching 9.66 mean legal moves): 1.58x too many nodes — the static bsf move ordering is the lever; the C solver's
  fixed square ordering (corners first, the central four excluded) is the candidate phase-2 fix. The two fixes are
  independent and multiplicative.
- D-681 (the first I-024 fix, on the user's explicit request — "Fai solo il primo, fermati"): the multi-ply batch search
  is now a single njit `prange` over the lanes on numba's workqueue (the new `_search_prange`; the Python worker pool —
  queue + one thread per core — is gone from `multi_ply_ef.py`, with it the `os` / `queue` / `threading` imports).
  Verified: BIT-EXACT with the pool form (0/1000 lanes at depth 3 and depth 6 on the 1k sample, against the saved pool
  references), the depth-6 / 1k test case 97.4 s -> 25.8 s in the first post-change run, 1342 fast-tier tests green. The
  user will re-take the times under htop before the second fix (the move ordering) is attempted — and the ordering will
  be measured single-thread vs single-thread first (the user's methodology: no parallelism confounding the node-count /
  time comparison).
- D-682 (the second I-024 fix, on the user's explicit request — "Porta in produzione"): the `_ab_eval` move loop is the
  fixed best-first group order of the C fast endgame solver's `worst_to_best` table: 10 priority groups (the corner
  rings first, the X-squares last, the central four searched after them — unlike the C, which excludes them, so the
  value stays the exact minimax), `legal` masked per group, each group's legal bits scanned BSR-first (the user's design
  — "un loop che fa il MASK per gruppi ... con BSR dopo aver fatto i gruppi"; my first 64-scan form was slower at
  shallow depth from the per-node overhead). The new njit `_bsr` in board.py (the descending twin of `bitboard_bsf`; the
  public `bitboard_bsr` is `@validate_call` Python and not njit-callable). SINGLE-THREAD A/B first (the agreed
  methodology): the first round was INVALID — two of my scratch bugs (the table slice `[59:0:-1]` silently dropped the
  worst square, G7; a patch indentation break moved the recursion out of the scan loop and segfaulted on an unbound
  variable); the user was right to demand the re-check ("RICONTROLLA BENE !!!!!!") — with the fixed 64-square table the
  values are BIT-EXACT, 250/250 lanes at depths 5 and 6, exactly as the wide-window theorem requires (no sums or
  products in the search, only comparisons). Post-fix A/B: depth 5 -40% nodes / 2.0x faster, depth 6 -52% nodes / 1.5x
  faster (serial, 250 positions). Production: the 1k depth-5/6 values bit-exact vs the pre-change baseline (1000/1000),
  the depth-6 / 1k 8-core wall 25.8 s -> 6.4 s (4x). New tests: TestBsrNjit (2) + TestMultiPlyEfGroupOrder (3: the mask
  partition, the corner-first priority, the ground-window == wide-window value invariance) — all fast-tier. The prange
  chunking question was settled without a change: numba's workqueue dispatch is dynamic at ~n/80 chunk granularity
  (proven with the concentrated-outlier probe), and since numba exposes no chunk parameter the sub-batching workaround
  was declined by the user as too specific.
- D-683 (the fast-tier budget; the user: "ne vedo 2 della suite che sicuramente sono sopra 0.5s ... trovali"): the
  per-test timing of the 1347-test suite pinned the two — `test_depth1_vs_minimax_oracle` (5.46 s) and
  `test_normal_root_is_minus_y0` (5.72 s), both in `test_multi_ply_ef.py`. Root cause: NOT the test bodies (~0.1 s warm)
  but the one-time JIT compilation — `_search_prange` was the only njit of the module without `cache=True`, so every
  fresh process re-compiled the prange entry (~5.5 s) and the first callers paid it; the discipline test additionally
  triggers a second `_search_prange` overload (the TRIVIAL model's `horizon_stones` is int64, the fixture models'
  uint32). Fix in the source (no test change, no coverage loss): `cache=True` on `_search_prange`. Warm cache: both
  tests under 0.5 s, the 1k d5/d6 values bit-exact (1000/1000) vs the pre-change baseline, 1347 fast-tier tests green.
