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
  conversion is `game_position_from_str`; NOT a dedicated file, NOT the gpdb test module). (D-650)
- Next: the user's supervision of the step-1 work (no commits made this session so far), then the MULTI-PLY step 2.
