# test_board.py — test-suite analysis for `twolm.board`

Companion of `docs/src/twolm/board.md`.

Analysis 2026-08-25. Method: six independent coverage passes over
`src/twolm/test/test_board.py` (slices A 89–511, B1 512–695, B2 696–891,
C1 892–1232, C2 1233–1471, D 1472–2083), each cross-checked line by line
against `src/twolm/board.py`; all expected values re-derived independently
(pure-Python D8 math, no board.py import, no suite execution). Suite status
is a runtime fact from the joint run on 2026-08-25: GREEN — 157 tests,
0 failures, 12 skipped (all PERF=1 gates).

## 1. What this file is

2083 lines, plain `unittest`: 40 class definitions = 39 `TestCase` classes
+ 1 non-TestCase blueprint mixin (`BaseBitboardTransformationTest`).
`from twolm.board import *` (line 57). 157 test methods: 125 defined in
concrete classes + 32 inherited (4 blueprint methods × 8 D8 subclasses);
12 of the 157 are PERF-gated (`@skipUnless(PERF == '1')`), 145 ordinary.

| Area | Lines | Classes | Tests |
|---|---|---|---|
| A — Square, Move, bitboard primitives | 89–511 | 9 | 41 |
| B — D8 bitboard transformations | 512–891 | 8 + 4 | 47 (32 inherited + 15) |
| C — position: creation/eq/print/empties/legal moves | 892–1471 | 4 + 1 | 27 |
| D — position: game ops, endgame, D8 | 1472–2083 | 13 | 42 |

## 2. Suite conventions

- **Shared fixture:** nearly every position test uses the same pair
  `mover = 0x40001ccaeb400024` / `opponent = 0x92fc6234143c7848`
  (built via `bitboard_from_signed_int(np.int64(…))`). Verified:
  `mover & opponent == 0`, so every `position_check_collisions` call on
  these fixtures passes trivially.
- **Header constants (61–86):** `ar` = 0x22120a0e1222221e (19 discs) and
  its 8 D8 images (`ar_reflection_h/v/h1a8/a1h8`,
  `ar_rotate_180/90c/90a`), `full`, `empty`, corners `sqa1/sqa8/sqh1/sqh8`,
  `row_1/row_8`, `column_a/column_h`, `half_left/right/top/bottom`.
  Hand-written reference constants, no derivation inside the tests.
  ⚠ Their **names are systematically transposed** vs chess vocabulary —
  see §5.8.
- **Dual API pattern:** scalar and 1-D-array branches tested where the
  function has both; pydantic `ValidationError` / body-level
  `ValueError` / `TypeError` branches tested where they exist.
- **PERF gate:** 12 tests, all on 1M-row **uniform** populations
  (constant board repeated), warmup, `perf_counter` timing + b/s print,
  correctness re-check against a cheap reference (`np.repeat` / scalar
  fill). No throughput threshold: the gate **measures, it never fails on
  slowness**. Throughput on diverse positions is never measured.

## 3. Coverage by area

### Area A — Square, Move, bitboard primitives (89–511)

**TestSquare (89–154)** — `Square`, `square_from_str/to_str/as_bitboard`,
`square_validate_range`:
- construct 0/1/63 + equality [happy path]; `Square(-1)`, `Square(256)` →
  OverflowError, incl. array ctor [validation]; `'A1'`→0, `'UN'`→ValueError
  (a move, not a square) [validation]; `Square(0)`→`'A1'`;
  `square_as_bitboard`: 0→bit 0, 63→bit 63, **64→Bitboard(0)** — pins the
  numpy `uint64(1)<<64 == 0` wrap (R3's mechanism; the uint8 ctor accepts
  64, the map yields the empty bitboard) [edge case];
  None→ValidationError on all three fns [validation]; `validate_range`
  0..63 pass / 64 fail, both scalar and array [validation].

**TestMove (156–239)** — `Move`, `move_from_str/to_str/as_bitboard`,
`move_validate_range`:
- construct 0/1/63/64/65/66 (all PA/NA/UN codes) + equality; OverflowError
  −1/256 scalar and array; full special-code mapping A1/B1/H8/PA/NA/UN →
  0/1/63/64/65/66 [happy path]; `'NO'`→ValueError; `Move(64)`→`'PA'`
  (only one direction, only PA); `move_as_bitboard`: 0/63 → bits,
  **PA/NA/UN → Bitboard(0)** — same `<< 64` wrap, R3 dependency pinned
  incidentally and without comment [edge case]; None→ValidationError;
  `validate_range` 0..66 pass / 67 fail, scalar + array [validation];
  ⚠ the array negative case passes `Square(67)` instead of `Move(67)` —
  still green (same uint8 dtype; ValidationError ⊂ ValueError), but
  misleading (§5.11).

**TestBitboardFromSignedInt (241–288)** — R4 slice:
- int64 array [−1,−2,0,1] → uint64 bit reinterpretation, dtype pinned
  [dual API]; **zero-copy view pinned** (mutating result mutates input)
  [edge case]; **real `np.int64(−1)`** → `np.uint64(2^64−1)`, return type
  pinned (R4 working side) [dual API]; bare Python int → ValidationError,
  float64 array → ValueError [validation];
  ⚠ `test_wrong_array_raises_value_error` is **broken** — see §5.1.

**TestBitboardToSignedInt (290–343)** — R4 slice:
- real `np.uint64` MSB-0 → int64 same value, type pinned [dual API];
  0xFFFF…FF→int64(−1), 0x8000…00→int64-min [edge case]; 1-D array
  dtype/shape/values [dual API]; 2-D → ValueError (ndim) [validation];
  int32 array → ValueError (dtype) [validation]. No shared-memory
  assertion in this direction (present only in the `from` direction).

**TestBitboardFromHexStr (345–410)**:
- 16-char hex scalar → Bitboard, type pinned [dual API]; case-insensitive
  [happy path]; 3-char and 18-char → ValueError [validation]; 1-D string
  array → BitboardArray [dual API]; one short string in array → ValueError;
  2-D string array → ValueError (ndim); `'G'` → ValueError [validation].

**TestBitboardBsr (412–445)** — scalar-only API:
- 0→−1, 1→0, 1<<53→53, 1<<62, 1<<63, full→63; asserts Python `int`
  (test docstring says "np.int8" — stale, §5.9) [edge case];
  bare int and int64 array → ValidationError (arrays rejected) [validation].

**TestBitboardPrint (447–470)**:
- exact 9-line 2-D string for `ar` via `output=StringIO`; expected string
  independently re-derived from `ar` bits — **matches** [happy path].
  No empty/full board, no wrong-type, no default-stdout test.

**TestBitboardCount (472–481)** — `np.bitwise_count` (R5):
- empty→0, full→64, ar→19 (19 re-derived) [happy path]; str →
  ValidationError [validation]. No array test (scalar-only API); no
  single-bit or 32-bit count.

**TestBitboardTransformationFa1h8Comp (483–511)**:
- `test_fa1h8_compositions` — 8 group compositions (fa1h8∘ro000,
  fvert∘ro090, fh1a8∘ro180, fhori∘ro270, ro270∘fvert, ro090∘fhori,
  ro000∘fa1h8, ro180∘fh1a8) all asserted equal to
  `expected = bitboard_fa1h8(ar)` — i.e. **against the implementation's own
  output**, not an independent reference (self-referential; all 8
  identities verified true independently) [other]. Golden constants
  `ar_reflection_a1h8`/`ar_reflection_h1a8` exist in the header for
  exactly this and are unused by this test — see §7.3.3.

### Area B — D8 bitboard transformations (512–891)

**BaseBitboardTransformationTest (512–606)** — blueprint, 4 methods ×
8 subclasses = 32 tests. Subclasses set `self.func` + `self.test_data`
(14 (input, expected) pairs each, from the header constants):
- `test_scalar_transformations` — per pair: value +
  `isinstance(Bitboard)`, hex diff on mismatch [happy path]
- `test_vector_transformations` — all 14 pairs packed in one array →
  ndarray, dtype == Bitboard, values; exercises the njit/prange array impl
  [dual API]
- `test_wrong_type_raises_validation_error` — `func(42)`, `func('str')`,
  int64 1-D, float64 1-D → ValidationError for all 8 fns via inheritance
  [validation]
- `test_performance_1m` — PERF=1; 1M × sqa1; warmup; timing + b/s; sanity
  = njit-array result vs constant fill of the scalar result (cross-path
  consistency, uniform population) [perf gate]

**Concrete subclasses (608–695):** Fa1h8 (608), Fh1a8 (619), Fhori (630),
Fvert (641), Ro000 (652), Ro090 (663), Ro180 (674), Ro270 (685). All
**112 expected values re-derived by hand** against the true bit layout
(bit `8·file + (rank−1)`, column-major: sqa1=bit 0, sqa8=bit 7,
sqh1=bit 56, sqh8=bit 63) — **no value mismatches**. Pinned mappings
(r=rank 1..8, c=file a..h): fa1h8 (r,c)→(c,r); fh1a8 (r,c)→(9−c,9−r);
fhori (r,c)→(r,9−c); fvert (r,c)→(9−r,c); ro000 identity;
ro090 (r,c)→(9−c,r); ro180 (r,c)→(9−r,9−c); ro270 (r,c)→(c,9−r).

Note: the 14 structural pairs are only the 14 header shapes — they never
contain a general position like `ar`; general-position correctness of the
individual primitives rests on the orbit tests below (and on the
self-referential composition test above).

Cross-check vs board.py:
- scalar impls match (fhori = 8-way byte swap, board.py:652–670;
  fvert = 3-step in-byte bit reversal, board.py:712–720);
  `ro000` = `return bb` — **same object, no copy** (board.py:753);
  ro090/ro180/ro270 are compositions of the **public pydantic wrappers**
  (board.py:776/799/822) — double validation per call, no fused numba impl.
- **@overload asymmetry:** the 4 reflections have `@overload`
  registrations (board.py:539/592/645/705); the 4 rotations have none.
  No JIT caller exists anywhere; tests call the plain-Python wrappers,
  so the overload branches never fire (§7.3.4).

**TestBitboardTransformations (696–784)** — `bitboard_transformations`
orbit:
- orbit slots (board.py:444–451): 0=identity, 1=fa1h8∘fhori (=ro090),
  2=fvert∘fhori (=ro180), 3=fh1a8∘fhori (=ro270), 4–7 = fvert, fh1a8,
  fhori, fa1h8 — rotations built as reflection compositions, never via
  the rotation helpers. Dispatch: scalar→(8,), 1-D (N,)→(N,8), 2-D →
  ValueError.
- `test_ar` — slot-wise vs all seven `ar_*` header constants + `ar`
  [happy path]; `test_elle` — 2nd, less-symmetric position (3-disc
  L-shape): 8 explicit hex values [happy path]; `test_elle_ar_array` —
  (2,8), rows = the two scalar orbits [dual API]; wrong array dtype →
  ValidationError ("dtype"+"int32" in message), str scalar →
  ValidationError, 2-D → ValueError with **"must be 1D"/"got shape
  (2, 2)" verbatim board.py:422** [validation]; `test_performance_1m` —
  PERF, 1M-row constant, re-check vs `np.repeat` [perf gate].
- group properties: identity implicit (slot 0); composition correctness
  only transitive (rotation slots = reflection compositions, pinned vs
  independent constants); anti∘transform == identity **not asserted
  anywhere**.

**TestBitboardAntiTransformations (785–843)** — `bitboard_anti_transformations`:
- slot construction identical to forward **except slots 1 and 3
  swapped** (ro090↔ro270) — exactly the slot-wise group inverse
  (reflections self-inverse, ro180 unchanged).
- `test_ar` / `test_elle` — scalar anti-orbits vs header constants with
  the 1↔3 swap, 8 explicit hex values [happy path];
  `test_elle_ar_array` — (2,8) [dual API]; `test_performance_1m` —
  PERF [perf gate].
- inverse semantics checked by **explicit values only** — the inverse law
  `anti ∘ transform == identity` is never computed.
- ⚠ **zero validation tests** (no wrong-type/dtype/ndim) — asymmetric
  with the forward class, which has all three; the identical dispatch
  code (board.py:476–481) is untested on the anti path.

**TestBitboardToSquareList (844–859)** — scalar-only, pure-Python
bit-peel via `bitboard_bsr`, descending (H8→A1):
- one test, three inputs: empty→[], single 0x1→[Square(0)], sparse
  3-bit `0x8000000000000003`→[Square(63), Square(1), Square(0)] —
  covers empty, single, sparse (incl. top bit 63), descending order
  [happy path]; str → ValidationError [validation].
- full board (64 squares) **untested**; array-input rejection untested.

**TestBitboardToSquareArray (860–891)** — thin wrapper
`np.array(to_square_list(bb), dtype=Square)`:
- same three inputs; additionally asserts `isinstance(np.ndarray)`,
  `dtype == Square`, shapes (0,)/(1,)/(3,) [happy path]; str →
  ValidationError [validation]. Same gaps as the list class.

### Area C — position: creation, eq, print, empties, legal moves (892–1471)

**TestPositionCreation (892–1023)** — `Position` dtype, `make_position`,
`position_check_collisions` (always on clean positions):
- `test_new_position` — raw `np.void((m,o), dtype=Position)`; field
  round-trip [other] (bypasses `make_position` — tests the dtype layout)
- `test_create_position` — scalar `make_position`: round-trip, `.item()`,
  `isinstance(np.void)`, dtype, shape () [happy path]
- `test_new_position_array_one_element` — raw `np.array([(m,o)],
  dtype=Position)` — again NOT via `make_position` [other]
- `test_new_position_array_n_element` — 1-D list input through
  `make_position`: dtype, shape (N,), both iteration styles [dual API]
- `test_make_position_length_mismatch` — (5,) vs (3,) → body-level
  ValueError (board.py:163–167) [validation]
- `test_extract_views_zero_copy` — `positions['mover']`/`['opponent']`
  are write-through Bitboard views [edge case]
- `test_make_position_2d_array` — 2-D (2×3) → PositionArray (2,3), spot
  check [dual API]
- ⚠ docstring "Guarantees zero-copy view casting … across all
  dimensionalities" (board.py:154) overstates: inputs are copied into
  `data` (board.py:177–182); only the final view is zero-copy.

**TestPositionEq (1024–1122)** — `position_eq` = `np.array_equal`:
- scalar true/false, array (3,) true/false, (3,) vs (4,) → False no
  exception, (3,) vs scalar → False, wrong type → ValidationError
  [happy path/edge/validation].
- every false case swaps **both** fields — no per-field isolation;
  empty-array equality and broadcastable shapes untested; the
  `PositionField = Annotated[np.void, SkipValidation[Any]]` hole
  (board.py:134) — a wrong-dtype `np.void` passes the gate — untested.

**TestPositionPrint (1123–1150)**:
- single test: exact 9-line string via `output=StringIO`; independently
  recomputed — **matches** (mover 17, opponent 27, empties 13). The
  `sq <<= 1` loop does one extra (64th) shift after H8, landing on the
  same NumPy≥2 `<<64 == 0` behaviour as R3 — no functional effect.

**TestPositionEmpties (1152–1232)** — `position_empties` =
`~(mover|opponent)`:
- scalar 4 sub-cases (0,0)→full, (0,1), (1,2), (0,full)→0 — all
  re-verified [happy path]; `position_empties(None)` → ValidationError
  (method misnamed `test_position_eq_wrong_type` — §5.4) [validation];
  (3,) uniform array [dual API]; PERF 1M [perf gate]; raw (2,2) uint64
  coerced by `validate_position_array` to 1-D (2,) PositionArray
  [edge case].
- arrays uniform-only; 2-D *Position-dtype* array would come back 2-D
  despite the "1D array inputs" docstring — untested.

**TestPositionLegalMoves (1233–1471)** — `legal_moves` (bitboard-level
dual API, board.py:1057–1086), `position_legal_moves` (thin wrapper),
`_vectorized_legal_moves` (Kogge-Stone, via public API only):
- c1 single short line; h8 via 6-disc diagonal (longest line) [happy
  path/edge]; 2-element arrays vs expected [dual API]; position wrapper
  scalar + array [dual API];
- `test_legal_moves_bulk` — **120 (mover, opponent, expected) triples**,
  asserted 3 ways: scalar loop via `make_position` +
  `position_check_collisions` + `position_legal_moves`; `make_position`
  on array columns; **zero-copy** `position_data.view(Position).reshape(−1)`
  re-assert. Data covers: zero-mover/zero-opponent/both-zero rows
  (000–009), 1-bit..4-bit expected sets (e.g. row 050), lines in all 8
  directions, short (1-disc) and long (6-disc) brackets, corners/sides/
  middle, 70 dense endgame-ish rows (050–120). All expected values
  hardcoded hex — **external reference, not self-referential**. No
  value mismatches found against Kogge-Stone semantics (generator/
  propagator/blocker per direction, bracketed only).
- `test_performance_1m` — PERF, 1M identical boards, asserts all == h8
  [perf gate].
- ⚠ NameError landmine at line 1426 (mismatch debug block calls
  `b.print()`, `b` undefined) — §5.2.
- dispatch contract from board.py: scalar→`np.array([…])` wrap; array→
  shape check (ValueError "The shapes of mover and opponent arrays must
  be the same.") → dtype check (TypeError "The dtype of mover and
  opponent arrays must be Bitboard.") → njit; mixed scalar/array →
  TypeError. **None of the four error branches is tested** (§7.3.1).
- `legal_moves` has **no ndim guard**: a 2-D same-shape pair passes both
  checks and flows into the njit function (contrast: orbit functions
  do guard — board.py:421–422/480–481).

### Area D — position: game ops, endgame, D8 (1472–2083)

**TestPositionCollisions (1472–1501)** — `position_collisions`:
- scalar: disjoint→0, shared bit→that bit [happy path]; (3,) array with
  zero and collision elements [dual API].

**TestPositionCheckCollisions (1503–1579)**:
- scalar pass/fail, array pass, array fail-all (3/3), array fail-single
  (only index 1). Fails pin substrings "Detected 1 collision(s)",
  "out of 1 total elements", "index: 0"/"index: 1" — brittle to any
  rewording [happy path/validation/edge]. (This is the only place the
  raise path is exercised — the Area-C fixtures all pass trivially.)

**TestPositionLegalMovesCount (1581–1592)**:
- a1 vs b1 → count == 1 [happy path]. Only count==1; count 0 covered
  only indirectly via `position_has_to_pass`; multi-move counts untested.

**TestPositionFlips (1594–1730)** — `position_flips` (strictly scalar;
R2 path):
- legal a1→c1 vs b1: flips == 0x2, updated == (0x0, 0x7) (roles swap)
  [happy path]; 2-bit move → early return (Bitboard(0), None) via
  `bitboard_count(move) != 1` [edge]; 0-bit move → (0, None) [edge];
  1-bit move on empty square → (0, None) via `flips == 0` branch [edge];
  move='WRONG TYPE' → ValidationError [validation];
  `test_position_flips_bulk` — 42 rows, asserts **flips only**, never the
  updated position [other]; ⚠ NameError landmine at line 1723 (§5.2).
- R2 (`(Bitboard, None)` return) is therefore **covered**: all three
  trigger inputs (0 bits, ≥2 bits, 1 bit flipping nothing) pinned.

**TestPositionMakeMove (1732–1789)**:
- legal Move(2) → updated == make_position(0x0, 0x7) [happy path];
  wrong move type / wrong position type → ValidationError [validation];
  Move(65)/NA → ValueError "out of range [0..64]" (`move > 64` branch)
  [edge]; Move(64) with a genuine pass → mover/opponent swapped — pins
  the **explicit** `move == 64` PA branch (board.py:1198; no shift-wrap
  involved) [happy path];
- `test_position_make_move_illegal_returns_none` — illegal square E3 →
  **None**: pins the CODE side of R1 while the docstring
  (board.py:1196) says "the same board is returned" [edge]. ⚠ the
  return annotation `-> PositionField` is wrong for that path; fixing
  the code per the docstring would **break this test**.

**TestPositionCountDifference (1791–1799)**:
- computes diff (1 vs 2 discs; expected −1) then asserts
  **`assertEqual(True, True)`** — the value is never pinned (§5.3).

**TestPositionFinalValue (1801–1809)** — WOFC scoring:
- 8 vs 1 discs, 55 empties → 62; exercises **only the `diff > 0`
  branch**. Untested: `diff == 0 → 0` (draw), `diff < 0 → diff − ec`
  (opponent leader), full board (ec = 0).

**TestPositionHasToPass (1811–1825)**:
- mover with a legal move → False; 0 legal moves → True
  [happy path/edge].

**TestPositionIsGameOver (1827–1841)**:
- mover has a legal move → False (early `lmc > 0` return) [happy path];
  **full board** (mover = 0xFF..F, opponent empty) → True — the only
  true case is degenerate; a genuine double-pass game over on a non-full
  board (e.g. a1 vs h8) is untested — that is the path exercising the
  PA swap inside `position_is_game_over` (board.py:1262) with real discs.

**TestPositionIsMoveLegal (1843–1892)**:
- occupied-mover / occupied-opponent / empty-but-illegal / PA-with-moves /
  NA → all False [happy path]; legal square → True, and PA on a
  0-move position → True — this exercises the **R3-dependent path**:
  `move_as_bitboard(64)` = `uint64(1) << 64` wraps to 0, "Pass move"
  branch (board.py:1274–1275) returns `lms == 0` [edge]; two dedicated
  PA tests duplicate the 64 cases via `move_from_str('PA')`.

**TestPositionTrFunctions (1894–1995)** — the 8 public position-level
D8 functions (each test pins both fields):
- fa1h8, fh1a8, fhori, fvert, ro000, ro090, ro180, ro270 — all scalar,
  all through the pydantic-wrapped bitboard functions (Python dispatch;
  numba `@overload` NOT triggered). Each test carries a dead
  `if False:` debug block. `position_ro000` returns `p.copy()`
  (board.py:1317) — copy-vs-aliasing unpinned (contrast
  `bitboard_ro000`, which aliases).

**TestPositionTransformations (1997–2039)** /
**TestPositionAntiTransformations (2041–2083)**:
- scalar → (8,) in documented order (ro000, ro090, ro180, ro270, fvert,
  fh1a8, fhori, fa1h8); (3,) array → (3,8) via `np.tile`; the anti class
  pins the 1/3 swap (ro090↔ro270) — consistent with code, contradicting
  the board.py:463 docstring table (§6). The array tests exercise the
  `_numba_*_transformations` prange path through the public API, but not
  the four primitive `@overload`s (§7.3.4).

## 4. Verified facts (no value mismatches)

Independently re-derived and matching:
- all **112 D8 primitive pairs** (Area B1) against the column-major bit
  layout;
- all **120 legal-moves rows** (Area C2) against Kogge-Stone semantics;
- forward/anti **orbit slot order** and the 1↔3 swap (Area B2) against
  the board.py:444–451/503–510 compositions;
- the **position print** 9-line string (17/27/13 discs) and all
  **empties** values (Area C1);
- collision **message substrings** and the 2-D **"must be 1D" message
  verbatim** (board.py:422).

Function-level reach: **46 of 47 public functions of board.py are
exercised at least once. `bitboard_to_string_list` (board.py:849) has
zero tests** — the only public function with none.

## 5. Defects in the test file itself

1. **Broken test — `test_wrong_array_raises_value_error`
   (TestBitboardFromSignedInt, 284–288):** builds a 2-D int64 array `i`
   but calls `bitboard_from_signed_int(−1)` (bare int); the 2-D array is
   never passed. The test passes only because pydantic v2
   `ValidationError ⊂ ValueError`. Consequence: the 1-D ndim branch of
   `bitboard_from_signed_int` (board.py:285–286, probe-verified to raise
   ValueError) is **unpinned by the suite**.
2. **NameError landmines — broken failure paths:** line 1426
   (`test_legal_moves_bulk` debug block) and line 1723
   (`test_position_flips_bulk` debug block) call `b.print()` but `b` is
   never defined. A real mismatch would raise `NameError` and mask the
   diagnostic output.
3. **Dead assertion — line 1799:** `self.assertEqual(True, True)` in
   `test_position_count_difference`; the function's return value is
   never checked (expected for the test input: −1). The function is
   effectively untested.
4. **Misnamed duplicate:** `test_position_eq_wrong_type` exists in both
   TestPositionEq (1112) and TestPositionEmpties (1175, where it tests
   `position_empties(None)`).
5. **Dead `if False:` debug blocks** in all 8 TestPositionTrFunctions
   tests (1894–1995).
6. **Stale comment at 588:** the PERF "fallback" description says it
   triggers on unbound globals; it actually triggers on
   `len(self.test_data) > 2`.
7. **Stale header reference at line 32:** still cites `$(REVERSI_HOME)`
   (old-repo layout).
8. **Header constant names systematically transposed (78–86):** values
   are correct, names are not — `row_1` (0xff) is actually **file a**;
   `row_8` is **file h**; `column_a` (0x0101…) is **rank 1**;
   `column_h` is **rank 8**; `half_left` (0x0f…) is the **bottom rank
   band 1–4**; `half_right` the top band 5–8; `half_top` (0xffff…) is
   the **left file band a–d**; `half_bottom` the right band e–h. Any new
   test author using these constants by name gets transposed geometry.
   (The board.py docstrings use the same vocabulary, so docs and tests
   read coherently while being geometrically misleading.)
9. **Stale test docstring:** `test_scalar_bsr_high_bits` says "return
   np.int8"; code and assertion use Python `int` (np.int8 is not a
   subclass of int — the assertion as written is what passes).
10. **R3 silently pinned:** `test_square_as_bitboard` /
    `test_move_as_bitboard` bless the `uint64(1)<<64 → 0` wrap without
    comment — the fragile behaviour is documented by the test only
    incidentally.
11. **`test_move_validate_range` (230–232)** passes `Square(67)` in the
    array negative case where `Move(67)` was probably intended. Still
    green (same uint8 dtype; ValidationError ⊂ ValueError) — misleading,
    not wrong.

## 6. Docstring/behaviour mismatches (cross-check findings)

Test data is consistent with the **code**, not with several docstrings
(already catalogued in board.md, now confirmed from the test side):
- `bitboard_anti_transformations` docstring table (board.py:461–463)
  lists slot 3 as "ro180" (so ro180 appears twice); code (board.py:506)
  and both orbit test classes say **ro090**. Docstring is wrong.
- `bitboard_fh1a8` docstring (board.py:571): copy-pasted axis text from
  fa1h8 ("h1 is mapped to a8 and vice versa"); h1/a8 are fixed points of
  the anti-diagonal.
- `bitboard_from_signed_int` docstring: "Returns a new Bitboard" — the
  array path is a zero-copy view (pinned by
  `test_numpy_array_shared_memory`).
- `move_validate_range` error message "range [0..67]" is off-by-one
  (max valid 66, board.py:263); no test asserts the message.
- `fhori`/`fvert` docstring diagrams are **swapped** (each shows the
  other's behaviour); `ro090` text+diagram describe **ro270**;
  `ro270` diagram has one wrong cell (f4 vs true g4); `ro180` diagram
  has 5 wrong cells (b-file drawn in the f-file instead of the g-file);
  `ro000` typo "rotaded". Test data agrees with the code in all cases.
- `bitboard_from_hex_str` comment (board.py:353) calls `np.frompyfunc`
  an "optimized C-level loop"; it is a Python-level object loop.
- `position_empties` docstring "Works on scalar and 1D array inputs" vs
  a 2-D Position-dtype array coming back 2-D (untested).
- `make_position` "zero-copy … across all dimensionalities" (board.py:154)
  vs inputs copied into `data` (board.py:177–182).

## 7. Completeness analysis

### 7.1 What is well covered

- **Happy paths of the classic public API:** every construction,
  conversion and D8 primitive is exercised with correct independently
  re-verified expected values — the suite's value base is solid
  (112 + 120 rows + all orbit slots + print/empties strings, zero
  mismatches).
- **Dual API dispatch** where it exists (scalar vs 1-D array) for the
  bitboard primitives, orbit functions, make_position, legal moves,
  collisions, empties, position transforms.
- **Validation of the older public functions:** Square/Move
  (OverflowError, from_str, validate_range scalar+array),
  from_signed_int/to_signed_int/from_hex_str (wrong type, dtype, ndim),
  bsr/count (scalar-only rejection), position_eq/empties/flips/make_move
  (wrong type), forward orbit (type/dtype/ndim with exact messages).
- **R2 fully pinned** (all three `position_flips` early-return triggers).
- **The legal-moves bulk data** is the strongest part of the suite:
  120 rows, external reference, all 8 directions, short/long lines,
  dense endgames, three construction paths (incl. zero-copy view).

### 7.2 Status of the known board.py issues (R1–R5)

| Issue | Test status |
|---|---|
| **R1** — `position_make_move` returns None on illegal move vs docstring (board.py:1196) | **Pinned on the buggy side.** `test_position_make_move_illegal_returns_none` asserts None; fixing the code per the docstring breaks the test. Return annotation `-> PositionField` likewise wrong. Decision needed (code-vs-doc, and the test must follow). |
| **R2** — `position_flips` can return `(Bitboard, None)`, annotation says `PositionField` | **Covered:** all three trigger inputs pinned. Annotation still wrong (doc issue). |
| **R3** — `uint64(1)<<64 → 0` wrap (NumPy ≥ 2) | **Pinned in three places** — `move_as_bitboard` (PA/NA/UN → 0), `position_is_move_legal` pass branch (the wrap-dependent path IS exercised), and incidentally `square_as_bitboard` (Square 64 → 0). The fragility remains unfixed; no comment anywhere explains why 64→0 is "expected". |
| **R4** — signed-int view paths, pydantic non-coercion | **Asymmetric:** `from` — both sides pinned (real `np.int64` scalar works; bare int → ValidationError); `to` — only the working side tested (real `np.uint64` scalars); the failing side (bare int → ValidationError) is probe-verified but **not in the suite**. The pin depends on pydantic v2 arbitrary-type non-coercion — no version pin anywhere in the suite. |
| **R5** — needs NumPy ≥ 2.0 (`np.bitwise_count`, `<< 64` wrap) | **Exercised, not pinned:** running on numpy 2.5.2 exercises it; `bitboard_count` tests are thin (empty/full/ar only; no single-bit or 32-bit counts); no functional version assertion. |

### 7.3 Systemic gaps

1. **Validation coverage is front-loaded.** Zero pydantic/error-branch
   tests for: `legal_moves` (all four branches: wrong scalar type,
   shape-mismatch ValueError, wrong-dtype TypeError, mixed TypeError),
   `position_legal_moves` (position arg), `position_legal_moves_count`,
   `position_collisions`, `position_count_difference`,
   `position_final_value`, `position_has_to_pass`,
   `position_is_game_over`, `position_is_move_legal` (move arg), all 8
   position D8 functions, `position_transformations`/
   `position_anti_transformations`, `make_position` (wrong-type inputs;
   only length-mismatch is tested), `bitboard_anti_transformations`
   (all three error branches — asymmetric with its forward twin),
   `bitboard_to_signed_int` (bare-int failing side, §7.2), the
   scalar-only `bitboard_to_square_list/array` (array-input rejection).
   For the scalar-only `PositionField` functions no test pins pydantic
   rejection of an array input.
2. **No ndim guard in `legal_moves`** — a 2-D same-shape array pair
   passes both the shape and dtype checks and flows into the njit
   function (undefined behaviour). The 8 D8 primitives also have no
   2-D/3-D input tests (their wrong-type tests cover 1-D wrong dtypes
   only).
3. **No D8 group-law tests.** Nowhere is a group property asserted as a
   composition: `ro090∘ro090 == ro180`, `ro090∘ro270 == ro000`,
   `f∘f == identity`, `anti∘transform == identity`, orbit distinctness
   as an explicit set. The only composition test
   (`test_fa1h8_compositions`) is **self-referential** (expected value =
   `bitboard_fa1h8(ar)`, the implementation's own output) — a
   consistent bug across fa1h8/fvert/fh1a8/fhori (and the rotations,
   which are reflection compositions) would still pass. The header's
   unused golden constants `ar_reflection_a1h8`/`ar_reflection_h1a8`
   exist precisely for this: one `assertEqual(expected,
   ar_reflection_a1h8)` breaks the self-reference. The B1 blueprint is
   the natural home for property tests (ro000 identity pinned on 14
   shapes only, not as a property over arbitrary bitboards).
4. **Numba `@overload`s never fire.** All 13 D8 tests call the public
   pydantic API from plain Python; the overload registrations
   (board.py:539/592/645/705) only fire inside an `@njit` caller, which
   no test provides. The rotations have no overloads at all
   (asymmetry). The prange array paths ARE exercised (via
   `_numba_*_transformations` and `_vectorized_legal_moves`), but the
   JIT-callable surface is entirely untested.
5. **Kogge-Stone internals have no direct tests** — `_kogge_stone_mm` /
   `_vectorized_legal_moves` reachable only through the public API; the
   prange path is exercised by the 2-row tests outside PERF.
6. **Endgame/scoring branches:** WOFC only `diff > 0` (§3-D);
   `position_is_game_over` true-case is the degenerate full board (the
   real double-pass path with the PA swap, board.py:1262, untested);
   `position_count_difference` effectively untested (dead assertion).
7. **Full-board inputs missing:** `bitboard_to_square_list/array`
   (max tested: 3 bits), legal-moves 120-row data (no all-64-occupied
   row), `position_final_value` (no ec=0 row), position print (no
   empty/full board), bitboard print (only `ar`).
8. **Boundary gaps:** Square 65..255 and mid-board squares in
   `square_as_bitboard`; Move 68..255; lowercase names
   (`'a1'`/`'pa'` → ValueError, unpinned); no 64-name from_str↔to_str
   round-trip; bsr mid-board bits; from_hex_str empty array / `'0x'`
   prefix / >16-char in array; out-of-range bitboard values (beyond 64
   bits) in the orbit functions.
9. **Position-level gaps:** `position_eq` false cases always swap both
   fields (no per-field isolation; empty-array and broadcastable shapes
   untested); the `PositionField = Annotated[np.void,
   SkipValidation[Any]]` hole (wrong-dtype `np.void` passes the gate,
   board.py:134) is untested; `position_print` single test (default
   stdout, array rejection, overlap `'@'` precedence
   board.py:927–929, empty/full untested); `make_position` 1-element
   list path bypassed (raw ctor used instead), 2-D mismatch and 3-D
   untested, wrong-type inputs untested; `position_empties` array tests
   uniform-only; `test_position_flips_bulk` never asserts the updated
   position across all 42 rows; `position_ro000` copy semantics unpinned
   (contrast `bitboard_ro000` aliasing, unpinned too).
10. **PERF tests uniform only** (1M identical boards everywhere) —
    throughput on diverse positions never measured; sanity checks are
    cross-path consistency, not independent correctness.

### 7.4 Verdict

The suite is a **strong happy-path + conversion suite with a solid,
independently verifiable value base**, but a **thin edge suite**:
error-branch coverage stops at the older public functions, D8 is tested
as "individual mappings vs constants" (plus one self-referential
composition) rather than as a group, the numba/JIT surface is untested,
the endgame/scoring functions are single-branch, and the suite contains
one broken test, two NameError landmines in failure paths, and one dead
assertion that let it pass on inputs it never checks.

### 7.5 Recommended priorities (no action taken — source/test edits
require an explicit request)

- **P0 — fix the suite itself:** repair
  `test_wrong_array_raises_value_error` (actually pass the 2-D array);
  fix the two `b.print()` landmines (1426, 1723); replace the dead
  assertion (1799) with `assertEqual(diff, −1)`.
- **P1 — fragile pins:** make the composition test golden-constant-based
  (use `ar_reflection_a1h8`/`ar_reflection_h1a8`); add the three missing
  WOFC branches and a non-full `is_game_over` true case; pin the R4
  failing side of `bitboard_to_signed_int` (+ consider a pydantic
  version assertion); add the four `legal_moves` error branches.
- **P2 — coverage expansion:** D8 group-law property tests in the
  B1 blueprint (identity as property, `ro090∘ro090 == ro180`,
  `anti∘transform == identity`); `bitboard_to_string_list` (currently
  zero tests); full-board inputs; lowercase-name rejections; the
  `PositionField` SkipValidation hole; per-field `position_eq`;
  `position_print` variants; updated-position assertions in
  `test_position_flips_bulk`; rename the transposed header constants
  (and the docstring diagrams in board.py that inherit the confusion).

## Appendix — class map

| Class | Lines | Tests |
|---|---|---|
| TestSquare | 89–154 | 9 |
| TestMove | 156–239 | 9 |
| TestBitboardFromSignedInt | 241–288 | 5 |
| TestBitboardToSignedInt | 290–343 | 5 |
| TestBitboardFromHexStr | 345–410 | 7 |
| TestBitboardBsr | 412–445 | 2 |
| TestBitboardPrint | 447–470 | 1 |
| TestBitboardCount | 472–481 | 2 |
| TestBitboardTransformationFa1h8Comp | 483–511 | 1 |
| BaseBitboardTransformationTest (blueprint, not a TestCase) | 512–606 | 4 × 8 |
| TestBitboardTransformationFa1h8 | 608–618 | 4 |
| TestBitboardTransformationFh1a8 | 619–629 | 4 |
| TestBitboardTransformationFhori | 630–640 | 4 |
| TestBitboardTransformationFvert | 641–651 | 4 |
| TestBitboardTransformationRo000 | 652–662 | 4 |
| TestBitboardTransformationRo090 | 663–673 | 4 |
| TestBitboardTransformationRo180 | 674–684 | 4 |
| TestBitboardTransformationRo270 | 685–695 | 4 |
| TestBitboardTransformations | 696–784 | 7 (1 PERF) |
| TestBitboardAntiTransformations | 785–843 | 4 (1 PERF) |
| TestBitboardToSquareList | 844–859 | 2 |
| TestBitboardToSquareArray | 860–891 | 2 |
| TestPositionCreation | 892–1023 | 7 |
| TestPositionEq | 1024–1122 | 7 |
| TestPositionPrint | 1123–1150 | 1 |
| TestPositionEmpties | 1152–1232 | 5 (1 PERF) |
| TestPositionLegalMoves | 1233–1471 | 7 (1 PERF) |
| TestPositionCollisions | 1472–1501 | 2 |
| TestPositionCheckCollisions | 1503–1579 | 5 |
| TestPositionLegalMovesCount | 1581–1592 | 1 |
| TestPositionFlips | 1594–1730 | 6 |
| TestPositionMakeMove | 1732–1789 | 6 |
| TestPositionCountDifference | 1791–1799 | 1 |
| TestPositionFinalValue | 1801–1809 | 1 |
| TestPositionHasToPass | 1811–1825 | 2 |
| TestPositionIsGameOver | 1827–1841 | 2 |
| TestPositionIsMoveLegal | 1843–1892 | 4 |
| TestPositionTrFunctions | 1894–1995 | 8 |
| TestPositionTransformations | 1997–2039 | 2 |
| TestPositionAntiTransformations | 2041–2083 | 2 |
