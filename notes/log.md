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
