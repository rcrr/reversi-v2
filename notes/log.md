# Session journal

## 2026-08-25 — session 1
- Deep analysis of board.py (1380 lines): architecture, hand-verified D8
  transformation tables, Kogge-Stone legal-move boundary masks, flip-set
  computation. Catalogued 5 real issues (R1–R5) + minor ones → notes/board.md.
- Designed and set up the collaboration memory: AGENTS.md + NOTES.md + notes/
  (D-001..D-005). `git init` + first commit.
- Restructured: sources moved to `src/` (D-006); local git identity set to
  `rcrr <rob_corradini@yahoo.it>` per user preference (root commit re-authored).
- Code docs moved to `docs/` mirroring `src/` (D-007): board.py analysis now
  at docs/src/twolm/board.md; notes/ holds collaboration content only.
- Sources moved into the `twolm` package (D-008): src/twolm/board.py +
  minimal `__init__.py` for twolm and twolm.test; test_board.py copied by the
  user into src/twolm/test/ and committed.
- Next: run the test suite; analyze test_board.py; decide fixes for R1–R5.
- Added .gitignore (first entry `.obsidian/`), untracked
  logistello-papers/.obsidian/ (D-009); working tree clean again.
- Removed logistello-papers/.obsidian/ entirely (no longer needed);
  .gitignore extended with __pycache__/ and .venv/.
- Created .venv (Python 3.12.3) + minimal deps: numpy 2.5.2, pydantic
  2.13.4, numba 0.67.0 (D-010). Tests NOT run yet — with Roberto, next.
- Added pyproject.toml (setuptools, src layout) and installed twolm
  editable into .venv (D-011): `import twolm` now works without
  PYTHONPATH (verified from outside the workspace).
- Ran the test suite (with Roberto): 157 tests OK in ~0.5 s, 0 failures,
  12 skipped — all 12 are PERF=1 performance gates (8× inherited
  test_performance_1m from the 8 D8 transformation subclasses + 4
  standalone perf methods). Numba cache now warm in
  src/twolm/__pycache__/; warm run ≈ 1.2 s wall.

## 2026-08-25 — session 2
- Full analysis of test_board.py (2083 lines) in six passes
  (A 89–511, B1 512–695, B2 696–891, C1 892–1232, C2 1233–1471,
  D 1472–2083), each cross-checked line by line against board.py; all
  expected values re-derived independently — zero mismatches (112 D8
  primitive pairs, 120 legal-moves rows, orbit slot order, print /
  empties strings, collision messages).
- Wrote docs/src/twolm/test/test_board.md: coverage by area (39 TestCase
  classes + 1 blueprint, 157 methods), verified facts, 11 test-file
  defects, 8 docstring/behaviour mismatches, completeness analysis
  (R1–R5 status, 10 systemic gaps, verdict, P0/P1/P2 priorities).
- Test file untouched — analysis is doc-only, fixes only on explicit
  request (D-012).
- Completeness feedback delivered to Roberto (Italian): strong
  happy-path suite with a solid independently verified value base, thin
  on error branches / D8 group laws / numba surface / endgame scoring;
  bitboard_to_string_list has zero tests; 1 broken test + 2 NameError
  landmines + 1 dead assertion in the file itself.

## 2026-08-26 — session 1
- Granular fix campaign started (one atomic change per report item:
  confirm → full suite → commit; plan approved with the user).
- T01 (report §5.1): repaired test_wrong_array_raises_value_error — the
  2-D array is now actually passed to bitboard_from_signed_int; the ndim
  branch (board.py:285-286) is pinned for the first time. Suite GREEN:
  157 tests, 0 failures, 12 PERF skips.
- T02a (report §5.2): test_legal_moves_bulk debug block — undefined
  b.print() replaced by position_print(p) per user preference. Suite
  GREEN: 157/0/12.
- T02b (report §5.2): same repair in the test_position_flips_bulk debug
  block (second NameError landmine). Suite GREEN: 157/0/12.
- T03 (report §5.3): test_position_count_difference dead assertion
  assertEqual(True, True) replaced by assertEqual(diff, -1) — the value is
  now pinned (1 mover vs 2 opponent discs). P0 phase complete: all 3
  suite-breaking defects fixed. Suite GREEN: 157/0/12.
- T04 (report §5.4): renamed TestPositionEmpties.test_position_eq_wrong_type
  to test_position_empties_wrong_type (body tests position_empties(None);
  the name collided with the correctly named twin in TestPositionEq).
  Suite GREEN: 157/0/12.
- T05 (report §5.5): removed the 8 identical dead if-False debug blocks in
  TestPositionTrFunctions (one per position_* transformation test).
  Suite GREEN: 157/0/12.
- T06 (report §5.6): rewrote the stale PERF-fallback comment in
  test_performance_1m — the branch keys on len(self.test_data) > 2, not on
  unbound globals as the old text claimed. Suite GREEN: 157/0/12.
- T07 (report §5.7): header — stale $(REVERSI_HOME) reference replaced
  with the actual workspace-root instruction. Suite GREEN: 157/0/12.
- T08 (report §5.8): REJECTED by the user — the 8 header constants are
  correct as-is; the report's "transposed" finding imported chess file/rank
  vocabulary into a row/column Reversi project (the analysis was wrong,
  the code was right). Naming convention recorded canonically in
  notes/naming.md + AGENTS.md standing rule + NOTES.md pointer (D-013).
  No code change; suite state unchanged (GREEN 157/0/12 at a0d79ea).
- T09 (report §5.9): test_scalar_bsr_high_bits — stale "np.int8" claim
  replaced by "int" in the docstring and the type-assert comment (the
  function is annotated -> int, board.py:363, and the assertions use
  int; np.int8 no longer exists in NumPy 2.x). Suite GREEN: 157/0/12.
- T10 (report §5.10): documented the pinned uint64 shift wrap (code
  >= 64 → 0, NumPy 2.5.2) in test_square_as_bitboard and
  test_move_as_bitboard with a reference to open decision R3
  (docs/src/twolm/board.md, I-003). Comments only; suite GREEN: 157/0/12.
- T11 (report §5.11): test_move_validate_range scalar negative case
  built Square(67) where Move(67) was intended (variable mo, move test);
  green by accident since both are np.uint8 aliases. Renamed to
  Move(67); no behaviour change. Suite GREEN: 157/0/12.
- T12 (report §6): bitboard_anti_transformations docstring table —
  slot 3 was labelled ro180 (duplicated); code (fa1h8 of fhori,
  board.py:506) and the pinned tests (slot 3 = ar_rotate_90c) say
  ro090. Verified empirically against the executable (all 8 slots
  checked); fixed the label. Suite GREEN: 157/0/12.
- T13 (report §6): bitboard_fh1a8 docstring axis line — the fa1h8
  phrase "h1 is mapped to a8" was copy-pasted, but on the h1-a8
  diagonal h1/a8 are fixed points; the swapped pair is a1↔h8. Verified
  on the executable (fh1a8(A1)=H8, fh1a8(H8)=A1, H1/A8 fixed). Diagrams
  in the same docstring are T16 territory. Suite GREEN: 157/0/12.
- T14 (report §6): bitboard_from_signed_int docstring said "Returns a
  new Bitboard" while the array path returns i.view(Bitboard), a
  zero-copy view sharing the input buffer (pinned by
  test_numpy_array_shared_memory). Docstring now states the zero-copy
  contract. Suite GREEN: 157/0/12.
- T15 (report §6): move_validate_range error messages said [0..67] while
  the check admits 0..66 (mo < __move_max_value__, where the constant is
  the count = exclusive upper bound). Fixed the visible string with
  {__move_max_value__ - 1} in both scalar and array variants (no test
  pinned it; verified: 66 accepted, 67 rejects with [0..66]).
  Suite GREEN: 157/0/12.
- T16 (report §6): resolved — findings (a)–(d) (diagrams swapped /
  wrong cells) REFUTED by independent cell-by-cell re-verification
  against the compiled code: all six D8 diagrams match the code, and
  single-square probes confirm each function implements the symmetry
  its name promises under the canonical convention (row 1 top, column
  a left); the false verdicts read the diagrams under a non-canonical
  convention (root cause same as T08/D-013). Only the "rotaded" typo
  stood: fixed in the ro000 docstring. Per Roberto, the 8 D8
  symmetries (names, fixed slot order, anti-transformations, corner
  mappings) are now canonized in notes/naming.md (D-014), with a
  standing pointer in AGENTS.md; report §6 annotated. Suite GREEN:
  157/0/12.
- T17 (report §6): `bitboard_from_hex_str` comment corrected —
  `np.frompyfunc` wraps the Python callable in a ufunc that applies it
  element-wise (one Python call per element), not an "optimized
  C-level loop". Comment-only change; no behaviour change. Suite GREEN:
  157/0/12.
- T18 (report §6): docstring shape contract corrected —
  position_empties / position_collisions / position_check_collisions
  say "scalar and 1D array inputs" but are shape-agnostic: verified by
  probe that a 2-D Position-dtype array (2,2) comes back 2-D. The
  three position_* docstrings now say "scalar and array inputs of any
  shape" (output keeps the input shape, where an array output exists).
  The same phrase in bitboard_from_signed_int / bitboard_to_signed_int
  is CORRECT (both raise ValueError on non-1D arrays) — left as-is.
  Docstring-only change; no behaviour change. Suite GREEN: 157/0/12.
- T19 (report §6): make_position docstring corrected — the "zero-copy"
  claim only held for the final view cast: verified by probe that the
  function always allocates a fresh interleaved (shape, 2) buffer and
  COPIES the mover/opponent values in (mutating an input ndarray leaves
  the output unchanged; lists/arrays never aliased). Docstring now
  states the actual contract. Docstring-only change; no behaviour
  change. Suite GREEN: 157/0/12.
- T20 (report §7 R2): position_flips return annotation corrected —
  declared Tuple[Bitboard, PositionField] but returns (Bitboard, None)
  on non-single-bit or illegal moves; now Tuple[Bitboard,
  PositionField | None]. Annotation-only change; @validate_call does
  not validate return values by default, no behaviour change. Suite
  GREEN: 157/0/12.
- T21 (report §7/§8 P1): test_fa1h8_compositions de-self-referenced —
  "expected = bitboard_fa1h8(ar)" (implementation's own output) replaced
  with the header golden constant ar_reflection_a1h8 (probe-verified:
  matches the implementation's output), plus a pinning assertion. The 8
  composition identities now check against an independent constant.
  Suite GREEN: 157/0/12.
- T22 (report §3-D/§8 P1): VERO BUG found and fixed — position_final_value
  diff<0 branch (opponent ahead) always raised OverflowError:
  ec = 64 - (mc + oc) was computed with np.uint8 operands (bitboard_count
  returns np.uint8), so "diff - ec" overflowed on negative diffs.
  Fix (per Roberto): ec = 64 - int(mc + oc) — explicit int guards the
  arithmetic (mc+oc <= 64 always). bitboard_count keeps returning the raw
  np.uint8; its annotation was corrected from -> int to -> np.uint8
  (honest signature; the first T22 commit had converted the return to a
  Python int, reverted per Roberto's clarification in a follow-up commit).
  Added the 3 missing WOFC branch tests: draw (1v1 -> 0), opponent leads
  (1v8, 55 empties -> -62, crashed pre-fix), full board (33v31, 0 empties
  -> 2). Probed: old 8v1 case still 62. Suite GREEN: 160/0/12.
- T23 (report §3-D P1): added the non-full position_is_game_over true
  case (per Roberto's position): mover = 0xFFFFFFFFFFFFFF00 (56 discs,
  rows 2-8), opponent = 0x00000000000000FE (7 discs, B1-H1); only A1 is
  empty and both players are stuck on it, so the PA-swap path runs and
  returns True on a not-full board (probed: lmc 0 / swapped lmc 0).
  Suite GREEN: 161/0/12.
- T24 (report §7.2 R4 / §8 P1): pinned the failing side of
  bitboard_to_signed_int — bare Python int now asserted to raise
  ValidationError (probe-verified: pydantic 2.13.4 rejects it via
  is-instance[uint64], no coercion; before T24 this was only
  probe-verified, not in the suite; the `from` side was already
  pinned). Added TestPydanticVersion: asserts pydantic MAJOR == 2
  (approved by Roberto — the suite's non-coercion pins depend on v2
  semantics; a major bump must fail loudly, a 2.x upgrade must not
  break the suite). Suite GREEN: 163/0/12.
- T25 (report §7.3.1 / §8 P1): added the four legal_moves error-
  branch tests: bare Python int -> ValidationError; shape mismatch ->
  ValueError (message pinned); non-uint64 array -> ValidationError
  (rejected by the BitboardArray BeforeValidator, not by the dispatch);
  mixed scalar/array -> TypeError (message pinned). Probe-verified all
  four on pydantic 2.13.4. Per Roberto: the dispatch dtype branch
  (TypeError "The dtype of mover and opponent arrays must be
  Bitboard.") was confirmed unreachable and REMOVED from board.py —
  see D-016. Suite GREEN: 167/0/12.
- T36/T37 (report §7.2 R1): resolved the position_make_move contract
  mismatch — Roberto chose "docstring follows the code": the docstring
  now documents the real behavior (illegal move -> None) and the return
  annotation was corrected to PositionField | None. No behavior change,
  existing None pin stays valid, board.md R1 marked resolved. See D-017.
  Suite GREEN: 167/0/12.
- T38 (report §7.2 R3): position_is_move_legal no longer detects the
  pass move through the uint64 shift wrap — explicit `move == 64` check
  now (pass legal iff position_legal_moves(p) == 0); move_as_bitboard
  documents the 64-66 -> 0 wrap (NumPy-defined shift semantics, verified
  on 2.5.2). Behavior unchanged, existing pins all pass. See D-018.
  Suite GREEN: 167/0/12.
  Style follow-up (Roberto): hoisted the single `lms =
  position_legal_moves(p)` call before the pass branch so it is invoked
  once, not in two positions. Suite GREEN: 167/0/12.
- T26–T35 (report §7.5 P2): whole P2 batch in ONE commit per Roberto's
  explicit instruction ("Facciamoli tutti, un solo commit") — sanctioned
  deviation from the per-item protocol. Test-only, no src changes. Every
  item probed (executable) before pinning; no src bug found. (1) New
  TestBitboardD8GroupLaw — identity property, ro090²==ro180,
  ro090∘ro270==id, reflections involutive, anti∘transform==id per
  canon slot, over 7 arbitrary boards; (2) new TestBitboardToStringList
  — empty/single/sparse/full/str-rejection, previously zero tests;
  (3) full-board inputs — to_square_list/array full (64, descending
  h8→a1), legal_moves_bulk rows #090/#091 (full mover board, empty vs
  full → 0 moves), position_final_value disjoint full (0), mover-all
  (64), opponent-all (-64); (4) lowercase-name rejections pinned for
  square_from_str and move_from_str (ValueError "Invalid name");
  (5) new TestPositionFieldValidation — the PositionField
  SkipValidation hole: a wrong-dtype np.void passes the pydantic gate
  and is rejected later by NumPy at the field access (ValueError "no
  field of name mover"); position_eq has no field access, so no error;
  (6) position_eq per-field isolation (mover-only / opponent-only diff
  → False), empty arrays, different lengths → unequal, no exception;
  (7) TestPositionPrint variants — default-stdout path pinned through
  the raw function's __defaults__ swap (the validate_call wrapper bakes
  real stdout into its schema), '@' overlap precedence, empty and
  full-mover boards, array input → ValidationError; (8)
  test_position_flips_bulk now asserts the updated position: None iff
  no flips, otherwise make_position(o & ~flips, m | flips | move) —
  formula verified over all 42 rows by probe. Suite GREEN: 193/0/12
  (167 baseline + 26 new tests).
- Gameplay verification (Roberto: "can the board be used for Reversi
  gameplay?"): throwaway probe (kept at /tmp/play_reversi_probe.py)
  played 200 full random games using ONLY the board public API —
  standard start (mover = d5|e4, opponent = d4|e5; note the center
  block is columns d/e, the first draft wrongly used a/d and was
  caught by the 4-legal-moves assertion), random legal moves, PA
  passes, WOF final value. All invariants held at every node: no
  overlap, disc count non-decreasing, PA legal iff no legal move
  (T38 contract), position_final_value == independent WOF
  computation. 196 games ended full board (59-60 moves), 4 by double
  pass. Verdict: board.py is a complete game kernel; the game loop
  (start position, pass/game-over rules, history) belongs to a
  separate module. No workspace files touched by the probe.
- Session closed (Roberto). Next session: start a NEW module.

## 2026-08-27 — session 1 (pattern.py review)
- Scope (Roberto): document src/twolm/pattern.py (new module, 1203 lines)
  like board.md; list code+doc defects but apply NO fixes ("le changes ed
  i fix necessari in un'altra sessione dedicata"); test_pattern.py NOT
  analyzed this time (dedicated session later). D-019 records the scope.
- Docs: docs/src/twolm/pattern.md written in 3 incremental parts (Pattern
  class → PatternSet → standalone functions + consolidated issues),
  board.md format. Covers: D8 orbit/stabilizer bookkeeping, I/S/T
  fingerprint → closed 11-type PatternType table, run-based PEXT-style
  pack plans, base-3 uint32 indexing, principal configuration index
  (min over induced-stabilizer orbit), PatternSet fused Numba pipeline
  (8 anti-transforms shared across patterns, per-pattern 3-D plan stack,
  coset-grouped min reduction), sample_pattern_data, mdp CSV export.
- Verification (scratch /tmp/pattern_check.py; nothing in-tree touched):
  fingerprint EDGE = TYPE_2 / DOTA1 = TYPE_3D / CORE = TYPE_9, 29
  samples → 11 types; EDGE principal dict == brute force, Burnside
  3321 = (6561+81)/2 (induced C2, 81 fixed); non-principal row-8 mask
  rejected with the 8-mask listing; n_instances×n_stabilizers = 8 for all
  29; Set(DOTA1, EDGE, CORE) pipeline == per-pattern reference on 200
  random collision-free positions, exact (200, 9) match — covers the
  multi-plane OR branch via CORE's two runs; suite test_pattern GREEN
  49/0/3 (PERF gates) — run, not analyzed (out of scope).
- Defect list (no fixes applied): 8 real — R1 principal-mask rule not a
  unique representative (corner case; min-BSR ties; verified
  4-corners+a2 / 4-corners+h2 both accepted; fix needs a design
  decision), R2 false invariant in docstring (DOTA1), R3 wrong
  "descending priority" wording (actually ascending), R4 "SHA256" vs
  sha3_256, R5 unused import time, R6 PatternType missing from __all__,
  R7 stale comment (compute_indexes_on_board), R8 endianness-dependent
  set hash; plus ~18 minor items (typos, stale env comment, empty-set
  max() crash, no __repr__, etc.) — full text in docs/src/twolm/pattern.md.
- Verdict: core math sound (verified against brute force + fused kernel
  equivalence); defects = 1 design gap (R1) + doc drift (R2-R4, R7) +
  hygiene (R5-R6, R8 + minors). Nothing blocks the 29 patterns or the
  GREEN suite.
- Next session (Roberto's plan): pattern.py fix campaign (R1 decision
  first), then test_pattern.py analysis.

## 2026-08-27 — session 2 (R1 fix, D-020)
 - Roberto decided R1: option (a) — principal = numerically lowest mask
   of the orbit ("corrispondenza biunivoca tra il set dei MASK e un set
   ordinabile: i numeri naturali"; BSR judged "più informatica").
   Explicit go-ahead: "Fai la modifica ora. ne abbiamo parlato,
   procedi."
 - pattern.py L314-339: `_check_mask_is_principal` now scans t1..t7 for
   a numerically lower tmasks entry (first offender reported);
   docstring: "numerically lowest mask of its orbit ... a unique
   representative (R1, D-020)".
 - test_pattern.py: +test_init_rejects_non_minimum_orbit_masks (4
   corners + b1 accepted with n_instances=8/n_stabilizers=1; +a2 and
   +h2 rejected "not principal"). Suite now 50 tests.
 - Verification, in Roberto's order: pattern suite 50/0/3 OK; full
   suite via `unittest discover -s src -p 'test_*.py'` 243/0/15 OK;
   PERF=1: pattern 50 OK, board 193 OK (perf lines printed as before).
 - Docs: pattern.md — architecture rule restated (D-020), R1 entry
   marked RESOLVED with full history (old rule, 4-corners
   characterization, counterexample, new unique principal
   0x8100000000000083), verdict updated. decisions.md + NOTES.md + this
   file updated.
 - Git: single commit (pattern.py + test_pattern.py + pattern.md +
   notes).
 - Next: pattern fix campaign for the mechanical R2-R8 + minor sweep
   (dedicated session), then test_pattern.py analysis.

## 2026-08-27 — session 3 (R2-R8 campaign)
 - Fix campaign: each of R2-R8 proposed separately, approved explicitly
   one at a time. R2-R7 applied in pattern.py (docstring/hygiene, code
   behavior untouched): R2 invariant restated (count = stabilizer
   elements inducing a non-identity permutation on the pattern squares),
   R3 squares "ascending board order (A1 first)", R4 "SHA3-256", R5
   unused `import time` removed, R6 PatternType added to __all__ (star
   import verified), R7 comment -> "Used by compute_indexes_on_position
   and the PatternSet pipeline."
 - R8 (endianness-dependent set hash) REJECTED as a code fix by Roberto:
   the legacy engine (incl. legal-moves/moves pipelines) is written and
   tested for little-endian only; all bit/byte manipulation is untested
   on non-LE platforms. Resolved as documentation: "Platform assumption:
   little-endian only" section added to docs/src/twolm/pattern.md and
   docs/src/twolm/board.md (D-022).
 - pattern.md: R2-R8 entries marked RESOLVED/CLOSED, header + verdict
   updated, platform section added. decisions.md: D-021 (R2-R7), D-022
   (R8).
 - Verification, Roberto's order: pattern suite 50/0/3 OK; discover
   243/0/15 OK; PERF=1: pattern 50 OK, board 193 OK.
 - Next: commit this campaign; then the ~18 minor sweep.

## 2026-08-27 — session 4 (minor sweep, items #1-#19)
 - Minor sweep of pattern.md "Minor issues / inconsistencies": 19/19
   items resolved, each proposed separately and approved explicitly one
   at a time (Roberto's standing rule).
 - #1 'Aauthor' typo: dedicated commit b070918 (on Roberto's demand).
 - #2-#10, #12, #13, #14, #16, #17, #18: applied in this session —
   error-message fix, doc fixes, nested-helper decorator cleanup,
   comment clarification, docstring, PatternSet Raises line, MAX_NUMBER
   renamed to MAX_NUMBER_OF_SQUARES_FOR_PATTERN (3^20 < 2^32 fact, 18
   is a project choice), fastmath removed from all four Numba kernels
   (sweep found four, analysis listed three; pure-integer kernels,
   flags only affect float IR — Roberto challenged with his own PERF
   data; 4 interleaved ON/OFF runs: no decisive effect), _unpack_bb
   scalar path -> Bitboard(result.item()) (symmetric with _pack_bb),
   __repr__ added to Pattern, empty PatternSet rejected with clear
   ValueError (fail-fast, first check in __init__), empty mask (n_squares
   = 0) rejected explicitly (previously rejected only accidentally via
   the missing [I0 x8] type-table entry, with a confusing message).
 - #6 (D-023): Pattern.__init__ wrapped in strict @validate_call
   (arbitrary_types_allowed); TypeError -> ValidationError for non-str
   name / non-uint64 mask; tests updated accordingly.
 - #15 (D-024): PatternSet.names/masks converted from methods to
   @property (whole public surface attribute-style); class docstring
   reorganized; 2 test call sites updated. KNOWN PENDING (I-006): the
   original 2008 repo may have legacy .names()/.masks() callers —
   grep at migration time.
 - #19 (D-025): leave-as-is by decision — collision precondition stays
   on the caller (tests already check before calling; upstream engine
   validates); precondition now documented in both indexing docstrings.
 - Verification: pattern suite 50/0/3 GREEN after every item; final
   battery: discover 243/0/15 OK, PERF=1 pattern 50 OK + board 193 OK.
 - docs/src/twolm/pattern.md: all 19 items tagged RESOLVED with details,
   verdict refreshed (sweep complete).
 - Next: commit decision for #2-#19 (batch vs per-item: Roberto to
   decide); then test_pattern.py analysis (dedicated session, D-019).

## 2026-08-27 — session 5 (test_pattern.py analysis)
- Request: analyze test_pattern.py and prepare test_pattern.md for the
  next session (coverage, what's good, what to fix, what's missing).
  Doc-only session: no .py edits, per the D-019 pattern.
- Read the full test file (1488 lines, 12 classes, 50 tests, 3 PERF
  gates; test_data in TestPatternSymmetries is a class attribute, not a
  collected method).
- Verification: two scratch scripts (verify_pattern_tests2.py,
  verify_pidx.py) use only twolm.board + pure arithmetic (no
  twolm.pattern import -> non-circular): 15/15 PASS; the six pack-plan
  goldens re-derived in this session (6/6 PASS); two hand-derivation
  facts (DIAG8 symmetry_fs semantics, one-record width 13). Total:
  21/21 independent re-derivations, zero value mismatches.
- Apparent DIAG8/SNAKE anomalies resolved: all goldens are consistent
  (SNAKE 0x0000000C30000000 = bits {28,29,34,35} = {E4,F4,C5,D5},
  matching the print golden; the scare came from my own scratch
  hex transcription errors, not from the file).
- Findings: 16 test-file defects (T1-T16, doc section 5): tautological
  assertEqual(p,p); dead `if False:` block referencing unimported
  position_print; 7 dead ar_* fixtures; 5 stale "raises_assertion"
  names; header typo/grammar; TestCase namedtuple shadow; weak
  empty-list CSV test; minor-sweep code with zero coverage (#16 repr,
  #17 empty PatternSet, #18 empty mask); uniform np.full arrays only
  for the public indexing pipeline; EDGE 6561 dict not pinned directly;
  self-referential PatternSet.hash golden; no direct PatternType tests;
  mdp_record goldens 2 of 29 patterns; inconsistent
  position_check_collisions usage; misleading mock records.
- Cross-checks: PatternSet stale TypeError Raises lines = known/deferred
  (not re-raised); mdp_csv_file docstring accurate; pattern.md
  "11-entry" table vs 12 PatternType members = minor doc inconsistency
  (M3).
- Deliverable: docs/src/twolm/test/test_pattern.md (coverage by area,
  21 verified facts, 16 defects, cross-checks, completeness analysis
  with P0/P1/P2 priorities - no action taken, awaiting per-item
  approval).
- P0 for the fix campaign: 3 tests for the shipped-but-uncovered
  minor-sweep paths (#16, #17, #18).
- Next: Roberto's per-item approvals for the test_pattern.py fix
  campaign (same one-at-a-time flow as pattern.py).
- Fix campaign in progress (per-item approvals):
  - D-026 (P0 1/3, T8/#16): TestPattern.test_repr added — three
    goldens (ELLE/EDGE/SNAKE) pin the one-line repr, incl. str()
    fallback (no __str__ defined). Suite GREEN 51/0/3.
  - D-027 (P0 2/3, T8/#17): TestPatternSet.
    test_init_raises_value_error_for_empty_pattern_list added. Suite
    GREEN 52/0/3.
  - D-028 (P0 3/3, T8/#18): TestPattern.
    test_init_raises_value_error_for_empty_mask added. P0 CLOSED:
    #16/#17/#18 all covered. Suite GREEN 53/0/3.
