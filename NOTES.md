# NOTES.md — entry point

## Format rules (rigid — follow when editing this file)

This file is the entry point: current state, next steps, index.
AGENTS.md standing rule 2: keep it updated after each milestone / end
of work session. Rules:

1. Sections — exactly these seven, in this order, no others: Project · Inventory · Conventions in the code · Environment · Where we are · Next steps · Index.
2. Language: English. Dates: YYYY-MM-DD. Suite numbers: `<total>/<failures>/<skipped>`, where total = unittest's "Ran N" (e.g. 193/0/12). Arrows: →. Ellipsis: ... (three dots). References: D-NNN (notes/decisions.md), I-NNN (notes/ideas.md), session N (notes/log_NNN.md volumes, global numbering), T-NN (test defect), R# (code issue), M# (minor note). Placeholder tokens are always inline code (backticks): bare `<word>` looks like an HTML tag to Markdown renderers and corrupts the rest of the rendering.
3. Project — plain text, at most 4 sentences.
4. Inventory — table "| Item | Status | Note |", one row per tracked source file and test file (separate rows), plus the logistello-papers row. Status grammar: `analyzed <date>[ (session N)]; <terse history, semicolon-separated>; suite <total>/<f>/<s> GREEN` — it always ENDS with the CURRENT suite state of that file. Note column = the doc path (D-007 mirror).
5. Conventions in the code — "- " bullets, one convention per bullet.
6. Environment — "- " bullets, one fact per bullet, in this order: venv, packaging, dependencies, test command, suite status. Suite status grammar: `Suite status (<date>): <module> <total>/<f>/<s>, ... — all GREEN. <skip explanation>. Warm run ≈ <t> s.`
7. Where we are — "- " bullets, one per file (source and tests separately) in the order the modules were brought in; then the re-verification bullet (if any); then the plan bullet; then one context bullet. Each bullet starts with the file name. Current state only — the session-by-session detail lives in the journal volumes notes/log_NNN.md (rules: notes/log_rules.md).
8. Next steps — "- " bullets, OPEN items only (closed work belongs in Where we are); the LAST bullet is the next concrete action.
9. Index — "- " bullets, one per doc/notes file: `<path> — <one-line description>`.

## Project

File-by-file modernization of Roberto Corradini's Reversi engine
(18-year-old repo). This workspace is a staging area: only files
under active work live here. Full-repo restructure: planned, not
now (I-001; see notes/decisions.md).

## Inventory

| Item | Status | Note |
|---|---|---|
| src/twolm/board.py | analyzed 2026-08-25 (session 1); modified by the fix campaign (T20, T22, T25, T36, T37, T38); all 5 real issues resolved: R1 (D-017), R2 (T20 annotation), R3 (D-018), R4 (T24 test pin + TestPydanticVersion), R5 (NumPy ≥ 2.0 declared in pyproject.toml, D-011); suite 193/0/12 GREEN (test_board.py) | docs/src/twolm/board.md |
| src/twolm/test/test_board.py | analyzed 2026-08-25 (session 2); 11 defects + 8 docstring/behaviour mismatches documented; fix campaign COMPLETE 2026-08-26 (session 3): P0 + P1 + full P2 batch (T26–T35, one commit per Roberto's "Facciamoli tutti, un solo commit"), suite 157 → 193 GREEN throughout; header 'environmeant' typo fixed 2026-08-29 (D-050, with test_feature T4), remaining grammar nit reported-only; suite 193/0/12 GREEN | docs/src/twolm/test/test_board.md |
| src/twolm/pattern.py | analyzed 2026-08-27 (session 4, D-019 review-only); all real issues resolved: R1 (D-020) principal = numerically lowest orbit mask (unique representative) + regression test; R2-R7 doc/hygiene fixes (D-021); R8 closed as little-endian-only platform note (D-022); minor sweep complete 2026-08-27 (session 7): 19/19 items (D-023, D-024, D-025 + fail-fast checks, constant rename, doc/hygiene/API fixes); D-032 (2026-08-28, session 10): Burnside attributes n_invariant_configs / n_unique_configs; suite 64/0/3 GREEN (test_pattern.py) | docs/src/twolm/pattern.md |
| src/twolm/test/test_pattern.py | analyzed 2026-08-27 (session 8): 12 classes / 50 tests / 3 PERF; 21/21 goldens independently re-derived (0 mismatches); 16 defects T1-T16 + T17 (sqa8/sqh1 fixtures swapped names/values) documented; fix campaign CLOSED: P0 (D-026-028, 6da0803) + P1 (D-029/030/031: row independence both public indexing APIs + EDGE 6561-entry dict pin) + P2 hygiene (D-033: T1-T7, T15-T16; T19 found + fixed in T2) + P2 breadth (D-034: T11-T14 + T17); T18 noted-only, M1 deferred; suite 64/0/3 GREEN | docs/src/twolm/test/test_pattern.md |
| src/twolm/mobility.py | analyzed 2026-08-28 (session 10): Mobility/MobilitySet + popcount64 SWAR + Numba kernel; index formula + n_configurations (distinct index values) + sorted-order columns + hash verified vs independent ground truth (V1-V8, 200-position differential, popcount on 200,010 values); R1-R6 fix batch applied (D-035: docstrings + column-order contract + popcount64 test-helper + dead imports + property/repr alignment + n_instances as-is), no behavior change; M1-M5 disposed (D-036: M1 glossary shipped, M2/M3/M5 left as-is, M4 corrected — no PERF gates in any suite); suite 26/0/1 GREEN (test_mobility.py) | docs/src/twolm/mobility.md |
| src/twolm/test/test_mobility.py | analyzed 2026-08-28 (session 10): 2 classes / 23 tests / 1 PERF; 13 verified facts V1-V13 (0 mismatches, incl. 31-line popcount table and [53,13,66] golden); 9 defects T1-T9 documented; fix campaign CLOSED the same day (D-037: T1-T9, per-item approvals, single batch commit — P0 __repr__ goldens, P1 multi-position row independence, P2 hygiene/breadth incl. pinned hash literal 2e553593...208a94); suite 23 → 26, GREEN 26/0/1 | docs/src/twolm/test/test_mobility.md |
| src/twolm/feature.py | analyzed 2026-08-28 (session 11): Feature (blocked __new__ + 3 factories) + FeatureSet (intercept/mset/pset composition, sorted-order features, hash over child hash hex strings); all goldens re-derived independently (V1-V8, zero mismatches: 3x10 index matrix, 13 orbit sizes, 3 pinned hashes); R1-R4 fix batch applied (D-038: sha3_256 doc fix + column-layout contract + __init__ docstring + dead imports); M1 applied (D-039), M2 applied (D-040), M3 left as-is (D-041, follow-up I-007), M4 applied (D-042) — all disposed; suite 20/0/1 GREEN (test_feature.py, 19 run + 1 PERF) | docs/src/twolm/feature.md |
| src/twolm/test/test_feature.py | analyzed 2026-08-28 (session 11): 4 classes / 14 tests / 1 PERF; 9 verified facts W1-W9 (0 mismatches, incl. 3x10 matrix and f5663932 hash literal); 9 defects T1-T9 documented (dead if-False block w/ never-imported position_print, 6 dead imports, header grammar + "environmeant" typo, no names-order assert, partial-None FeatureSet untested, Feature repr/eq untested, cosmetic import-time spaces, no full print_summary golden); T campaign CLOSED 2026-08-29 (D-043..D-050: T6, T1, T2, T3, T5, T7, T9, T4 — both files; T8 left as-is); suite 20 tests (19 run + 1 PERF), GREEN 20/0/1 | docs/src/twolm/test/test_feature.md |
| src/twolm/binio.py | analyzed 2026-08-29 (session 14); T1-T4 fix batch applied (D-051: lz4 in pyproject.toml, dead Path import removed, "Aauthor" → "Author", test_unknown_type_code_raises added); 15 verified facts V1-V15 (0 mismatches); suite 45/0/0 GREEN (test_binio 42 + test_usage_binio 3) | docs/src/twolm/binio.md |
| src/twolm/test/test_binio.py | analyzed 2026-08-29 (session 14, with test_usage_binio.py); T4 applied (D-051): ArrayTest now 8 tests (42 total in test_binio); suite 44 → 45, GREEN 45/0/0, no PERF | docs/src/twolm/test/test_binio.md |
| src/twolm/regab.py | analyzed 2026-08-29 (session 15); T1-T7 fix batch applied (D-052: "Aauthor" → "Author", dead typing imports, psycopg2/pandas/python-dotenv in pyproject.toml, _validate_db_fields DB query deferred, SKIP_REGAB_DB=1 gate, _validate_where_clause SQL-injection guard); 5 verified facts V1-V5 (0 mismatches, sha3_256 golden); suite 37/0/0 GREEN (35 DB + 2 mocked; SKIP_REGAB_DB=1 → 35 skip) | docs/src/twolm/regab.md |
| src/twolm/test/test_regab.py | analyzed 2026-08-29 (session 15); T5+T6+T7 applied (D-052): dead imports removed, SKIP_REGAB_DB gate, 4 SQL-injection tests added (TestRegabGPAsDF 12 → 16); suite 33 → 37/0/0 GREEN | docs/src/twolm/test/test_regab.md |
| src/twolm/opt_lbfgs.py | analyzed 2026-08-29 (session 16); T1-T7 fix batch applied (D-053: RuntimeException → RuntimeError hard bug, CURVATURE_THRESHOLD used, low_progress_count spelling, hermite None fallthrough, save_fn 7-param hint+docstring, fractional docstring); 5 verified facts V1-V5 (0 mismatches); suite 13/0/0 GREEN | docs/src/twolm/opt_lbfgs.md |
| src/twolm/test/test_opt_lbfgs.py | analyzed 2026-08-29 (session 16); T7 applied + 9 new tests (D-053): TestLBFGSInputValidation (3), TestFixedSizeMaxList (4, incl. T1 regression), TestTwoLoopRecursion (2); suite 4 → 13/0/0 GREEN | docs/src/twolm/test/test_opt_lbfgs.md |
| src/twolm/state_machine.py | analyzed 2026-08-29 (session 19): generic pipeline orchestrator (Workers up/down + Context + logging/history/CSV), pure stdlib, no new deps; 17 verified facts V1-V17 (0 mismatches, 54-check probe); R1 FIXED (D-057: Verbosity.VERY_LOW=4 added, NONE=5, `>=` gate unchanged — HIGH..LOW byte-identical, NONE truly silent, old ERROR-only behaviour kept as VERY_LOW); R2 FIXED (D-058: LogEntry now a frozen dataclass — attribute access, asdict() for file/DB dumps, show_event_log migrated, observable behaviour unchanged; test-file datetime import now used → M2/T11 resolved); R3 RESOLVED as intentional sentinel (D-059: documented in class + move_to_step docstrings, pinned by test_worker_zero_is_sentinel_never_executed, no behaviour change — the RLM 'CREATED' worker runs outside the machine, logistic_model will make it explicit); R4 RESOLVED (D-060: keep + document + pin — failure semantics in move_to_step docstring, recovery = move to k-1 (k's down) then up; machine domain-agnostic, exception re-raised for the domain worker; pinned by test_retry_after_failure_skips_failed_step, closes T6); R5 RESOLVED (D-061: __init__ rejects duplicate worker names, case-insensitive ValueError fail-fast — the real ambiguity was name resolution in move_to_step itself, so uniqueness enforced instead of an index fix; move_to_last unchanged, name dispatch now unambiguous; closes M12); T2 coverage added (D-062: TestContextInjection 7 tests; M8 extended with the implicit separator contract); T3 coverage added (D-063: TestDisplayGoldens 3 end-to-end display goldens, frozen clock); minors M1-M11 (M2, M12 done) OPEN; suite 32/0/0 GREEN (test_state_machine.py) | docs/src/twolm/state_machine.md |
| src/twolm/test/test_state_machine.py | analyzed 2026-08-29 (session 19): 5 classes / 32 tests / no PERF; all 13 original expectations independently re-derived (0 mismatches); T1 FIXED (D-057: TestVerbosityGating — 6x5 gating matrix + enum values); R2 tests added (D-058: TestLogEntry 3 tests — typed record, immutability, asdict 5-key form); T6 FIXED (D-060: test_retry_after_failure_skips_failed_step — retry-skip + down-then-up recovery); R5 tests added (D-061: 2 duplicate-name tests — reject + case-insensitive, closes T10); T2 FIXED (D-062: TestContextInjection 7 tests — log_event live binding, {level:02} format, base_dir join, absolute-prefix drops base_dir, cfg-missing AttributeError, empty-workers degenerate, V17 shared-context re-bind); T3 FIXED (D-063: TestDisplayGoldens 3 end-to-end goldens — live line, show_event_log table, show_history_of_moves table, frozen clock); T11 resolved as D-058 side effect; defects T4, T5, T7-T9 OPEN (one whole area untested: move_to_last + edge semantics); suite 13 → 15 → 18 → 20 → 22 → 29 → 32, GREEN 32/0/0 | docs/src/twolm/test/test_state_machine.md |
| logistello-papers/ | reference material, read-only | user's papers |

## Conventions in the code (respect them in any new work)

- Board vocabulary is canonical: **row** (1–8, top→bottom) and
  **column** (A–H, left→right) — never file/rank (chess). A1 =
  top-left (N-W) = bit 0; H8 = bottom-right (S-E) = bit 63.
  row_1 = [A1..H1]; column_a = [A1..A8]. Full text: notes/naming.md
  (D-013).
- Dual scalar/array API: public functions accept scalar OR 1-D array,
  return the input kind. Same validation pattern everywhere
  (is_scalar → atleast_1d → ndim check → dispatch → reshape back).
- `@validate_call` (pydantic, arbitrary_types_allowed) on all public
  functions.
- Numba `njit(cache=True)` + `prange` for hot loops; numba overloads
  for the four D8 primitives (fa1h8, fh1a8, fhori, fvert).
- Position = numpy structured dtype `[('mover', u64), ('opponent',
  u64)]`.
- Move codes: 0..63 = squares, 64 = PA (pass), 65 = NA, 66 = UN.
- D8 slot order is fixed and load-bearing (D-014): anti-transform
  slot s = T_s^{-1}; in pattern.py instance 0 = the ro000 image, and
  trans_fs/anti_trans_fs are indexed by instance (length =
  n_instances), not by slot.
- Pattern config indexes are base-3 uint32 over ≤ 18 squares
  (S ≤ 18); packed bit k ↔ the k-th square of `Pattern.squares`
  (ascending board order); principal index = min over the
  induced-stabilizer orbit.

## Environment

- Venv: `.venv/` (gitignored, D-010), Python 3.12.3, created
  2026-08-25.
- Packaging: `pyproject.toml` (setuptools, src layout) with twolm
  installed editable in .venv (`pip install -e .`, D-011) —
  `import twolm` works without PYTHONPATH, resolving to src/.
- Dependencies (pyproject.toml, minimal set, kept in step with the
  modules brought in): numpy ≥ 2.0 (bitboards / structured dtypes;
  the code requires NumPy ≥ 2.0 — board.md R5), pydantic ≥ 2
  (@validate_call), numba ≥ 0.60 (njit / prange / overload; pulls
  llvmlite), lz4 (binio, D-051), psycopg2 / pandas / python-dotenv
  (regab, D-052). Installed in .venv: numpy 2.5.2, pydantic 2.13.4,
  numba 0.67.0, llvmlite 0.49.0.
- Test command: `.venv/bin/python -m unittest twolm.test.<module>`
  (the old `PYTHONPATH=./src` prefix still works as a fallback);
  test_regab needs a live PostgreSQL + .env, or `SKIP_REGAB_DB=1` to
  skip the 35 DB tests (2 mocked run).
- Suite status (2026-08-29): board 193/0/12, pattern 64/0/3,
  mobility 26/0/1, feature 20/0/1, binio 45/0/0 (42 + 3 usage),
  regab 37/0/0 (2 mocked run, 35 DB skipped under SKIP_REGAB_DB=1),
  opt_lbfgs 13/0/0, state_machine 32/0/0 — all GREEN. Totals: 430
  tests, 52 skipped under the gate (17 PERF=1 print-only performance
  tests + 35 DB-gated regab tests; no performance gates in any suite,
  D-036). Warm run ≈ 0.5 s (board) / ≈ 1.6 s (full discover, numba
  cache warm in src/twolm/__pycache__/).

## Where we are

- board.py: analyzed 2026-08-25 (session 1,
  docs/src/twolm/board.md): architecture, hand-verified D8
  transformation tables, Kogge-Stone legal-move boundary masks,
  flip-set computation. Modified by the fix campaign (T20, T22, T25,
  T36, T37, T38); all 5 real issues resolved — R1 (D-017, docstring
  follows the code), R2 (T20, return annotation), R3 (D-018, explicit
  pass check), R4 (T24, bare-int ValidationError pin +
  TestPydanticVersion), R5 (implicit NumPy ≥ 2.0 declared in
  pyproject.toml, D-011); board.md issue list re-marked 2026-08-29
  (was stale since the 08-26 campaign).
- test_board.py: analyzed 2026-08-25 (session 2,
  docs/src/twolm/test/test_board.md): coverage by area, values
  re-derived independently, 11 defects, completeness verdict +
  P0/P1/P2. Fix campaign COMPLETE 2026-08-26 (session 3): all P0 +
  P1 + full P2 batch (T26–T35, one commit per Roberto's "Facciamoli
  tutti, un solo commit"); suite 157 → 193, GREEN throughout. Header
  'environmeant' typo fixed 2026-08-29 (D-050, with test_feature
  T4); the remaining grammar nit stays reported-only. Gameplay
  verification (2026-08-26, session 3): 200 random full games on the
  public API only, zero invariant violations — board.py is a proven
  complete game kernel (the game loop belongs to a separate module —
  NOT in the port plan, I-005 resolved).
- pattern.py: analyzed 2026-08-27 (session 4,
  docs/src/twolm/pattern.md, review-only per D-019). All real issues
  resolved: R1 (D-020) principal mask = numerically lowest orbit
  mask (unique representative; the 4-corners corner case) +
  regression test; R2-R7 (D-021) docstring/hygiene, code behavior
  untouched; R8 (D-022) closed as the little-endian-only platform
  note. Minor sweep COMPLETE 2026-08-27 (session 7): 19/19 items,
  each approved one at a time — D-023 (strict @validate_call
  constructor), D-024 (names/masks → @property; legacy .names() /
  .masks() call sites tracked as I-006), D-025 (collision
  precondition stays on the caller) + fail-fast checks (#17 empty
  PatternSet, #18 empty mask), constant rename (#12), type-table
  cross-check (#11), doc/hygiene/API fixes. D-032 (2026-08-28,
  session 10): Burnside attributes n_invariant_configs /
  n_unique_configs (formulas verified 29/29 sample patterns).
- test_pattern.py: analyzed 2026-08-27 (session 8,
  docs/src/twolm/test/test_pattern.md): 12 classes / 50 tests / 3
  PERF; 21/21 goldens independently re-derived (0 mismatches); 16
  defects T1-T16 + T17 (sqa8/sqh1 fixtures swapped). Fix campaign
  CLOSED: P0 (D-026-028, 6da0803) + P1 (D-029/030/031: row
  independence both public indexing APIs + EDGE 6561-entry dict pin)
  + P2 hygiene (D-033: T1-T7, T15-T16; T19 found + fixed in T2) + P2
  breadth (D-034: T11-T14 + T17). Final suite 64/0/3 GREEN. Parked:
  T18 noted-only (np.uint8 3**n_squares overflow, no code action),
  M1 deferred (stale PatternSet Raises docstring, awaiting go-ahead).
- mobility.py: analyzed 2026-08-28 (session 10,
  docs/src/twolm/mobility.md): feature index formula,
  n_configurations = distinct index values, columns in the set's
  sorted (mask, amask) order, sha3_256 hash — all verified against
  independent ground truth (V1-V8, 200-position differential,
  popcount64 vs int.bit_count on 200,010 values). R1-R6 fix batch
  (D-035, no behavior change); M1-M5 disposed (D-036: M1 glossary
  shipped, M2/M3/M5 left as-is, M4 corrected — no PERF gates in any
  suite).
- test_mobility.py: analyzed 2026-08-28 (session 10,
  docs/src/twolm/test/test_mobility.md): 2 classes / 23 tests / 1
  PERF; 13 verified facts (0 mismatches); 9 defects T1-T9. Fix
  campaign CLOSED the same day (D-037: T1-T9, per-item approvals,
  single batch commit — P0 __repr__ goldens, P1 multi-position row
  independence, P2 hygiene/breadth incl. pinned hash literal
  2e553593...208a94). Suite 23 → 26, GREEN 26/0/1. Mobility module
  fully done.
- feature.py: analyzed 2026-08-28 (session 11,
  docs/src/twolm/feature.md) — the first integration module
  (intercept + MobilitySet + PatternSet → one (N, I) index matrix).
  All goldens re-derived independently (V1-V8, zero mismatches: 3x10
  matrix, 13 orbit sizes, 3 pinned hashes). R1-R4 (D-038) + M1-M4
  (D-039..D-042; M3 left as-is → I-007) — all disposed.
- test_feature.py: analyzed 2026-08-28 (session 11,
  docs/src/twolm/test/test_feature.md): 4 classes / 14 tests / 1
  PERF; 9 verified facts W1-W9 (0 mismatches); 9 defects T1-T9. T
  campaign CLOSED 2026-08-29 (D-043..D-050: T6, T1, T2, T3, T5, T7,
  T9, T4 — both files; T8 left as-is). Final suite 20 tests (19 run
  + 1 PERF), GREEN 20/0/1. FEATURE module fully done.
- binio.py: analyzed 2026-08-29 (session 14,
  docs/src/twolm/binio.md) — BinaryWriter/BinaryReader with MAGIC
  framing + SHA3-256 sidecar + optional LZ4 whole-file compression.
  15 verified facts V1-V15 (0 mismatches); T1-T4 fix batch (D-051:
  lz4 in pyproject.toml, dead Path import, "Aauthor" → "Author",
  test_unknown_type_code_raises). Suite 45/0/0 GREEN (42 + 3 usage).
  BINIO module done.
- test_binio.py: analyzed 2026-08-29 (session 14,
  docs/src/twolm/test/test_binio.md, with test_usage_binio.py): 12
  classes / 44 tests at analysis; T4 applied (D-051, ArrayTest now 8
  tests). Suite 44 → 45, GREEN 45/0/0, no PERF.
- regab.py: analyzed 2026-08-29 (session 15,
  docs/src/twolm/regab.md) — REversi GAme Base: psycopg2 DB access +
  RegabDataSet + binio file serialization. 5 verified facts V1-V5
  (0 mismatches, sha3_256 golden); T1-T7 fix batch (D-052: "Aauthor"
  typo, dead typing imports, psycopg2/pandas/python-dotenv in
  pyproject.toml, DB query deferred, SKIP_REGAB_DB=1 gate,
  _validate_where_clause SQL-injection guard). Suite 37/0/0 GREEN
  (35 DB + 2 mocked). REGAB module done.
- test_regab.py: analyzed 2026-08-29 (session 15,
  docs/src/twolm/test/test_regab.md): T5+T6+T7 applied (D-052): dead
  imports, SKIP_REGAB_DB gate, 4 SQL-injection tests
  (TestRegabGPAsDF 12 → 16). Suite 33 → 37/0/0 GREEN.
- opt_lbfgs.py: analyzed 2026-08-29 (session 16,
  docs/src/twolm/opt_lbfgs.md) — L-BFGS optimizer (strong Wolfe line
  search, two-loop recursion, warm-start). 5 verified facts V1-V5
  (0 mismatches); T1-T7 fix batch + 9 new tests (D-053:
  RuntimeException → RuntimeError hard bug, CURVATURE_THRESHOLD
  used, low_progress_count spelling, hermite None fallthrough,
  save_fn 7-param hint, fractional docstring, test d param). Suite
  13/0/0 GREEN. OPT_LBFGS module done.
- test_opt_lbfgs.py: analyzed 2026-08-29 (session 16,
  docs/src/twolm/test/test_opt_lbfgs.md): T7 applied + 9 new tests
  (D-053): TestLBFGSInputValidation (3), TestFixedSizeMaxList (4,
  incl. T1 regression), TestTwoLoopRecursion (2). Suite 4 → 13/0/0
  GREEN.
- state_machine.py: analyzed 2026-08-29 (session 19,
  docs/src/twolm/state_machine.md) — generic pipeline orchestrator
  (Workers up/down + shared Context + logging/timing history/CSV
  export), domain-agnostic, pure stdlib (no new deps). 17 verified
  facts V1-V17 (0 mismatches): half-open interval semantics (up c→t
  runs workers c+1..t, target included; down c→t runs c..t+1, target
  excluded, L313 reassignment required), worker 0 unreachable via the
  public API — intentional sentinel (D-059), failure leaves
  current_step at the failed step (retry of the same target skips
  it — failure semantics documented + pinned, D-060), verbosity gate
  is `relevance >= verbosity` (post
  D-057: VERY_LOW ERROR-only, NONE silent), LogEntry frozen dataclass
  (D-058), move_to_last name-based (duplicate names rejected at
  construction — dispatch unambiguous, D-061), context injection is a
  side effect (shared context
  re-binds to the last machine). R1 FIXED (D-057: Verbosity.VERY_LOW=4
  added, NONE=5, `>=` gate unchanged — HIGH..LOW byte-identical, NONE
  truly silent, old ERROR-only behaviour kept as VERY_LOW; pinned by
  T1); R2 FIXED (D-058: LogEntry → frozen dataclass, attribute access
  + asdict() for the file/DB dump worker, show_event_log migrated to
  attribute access, observable behaviour unchanged; pinned by
  TestLogEntry; test-file datetime import now load-bearing → M2/T11
  resolved); R3 RESOLVED as intentional sentinel (D-059: state model
  + sentinel documented in class and move_to_step docstrings, pinned
  by test_worker_zero_is_sentinel_never_executed, no behaviour
  change); R4 RESOLVED (D-060: keep + document + pin — failure
  semantics in move_to_step docstring, recovery = move to k-1 then
  up, machine domain-agnostic; pinned by
  test_retry_after_failure_skips_failed_step, closes T6); R5 RESOLVED
  (D-061: __init__ rejects duplicate worker names — case-insensitive
  ValueError fail-fast before any state is touched; move_to_last
  unchanged, name dispatch now unambiguous; closes M12; pinned by 2
  new tests); T2 coverage added (D-062: TestContextInjection 7 tests,
  incl. V17 shared-context re-bind; M8 extended — the prefix must end
  with a separator or the level name glues onto it). Minors M1-M11
  (M2, M12 done) OPEN; T3 coverage added (D-063: TestDisplayGoldens
  — 3 end-to-end display goldens, frozen clock). Fix campaign: next
  T4, T5, T7-T9, then M-sweep. Suite 32/0/0 GREEN.
- test_state_machine.py: analyzed 2026-08-29 (session 19,
  docs/src/twolm/test/test_state_machine.md): 5 classes / 32 tests /
  no PERF; all 13 original expectations independently re-derived
  (0 mismatches) — core move mechanics well pinned (up/down
  asymmetry, failure semantics, same-step no-op, bounds/type/name
  errors). 11 defects found (5 now resolved); three whole areas
  untested at analysis (verbosity gate, context injection, display
  methods + move_to_last + edge semantics) — verbosity, injection and
  display now pinned. T1 FIXED (D-057: TestVerbosityGating — 6x5 gating
  matrix + enum values, 2 tests; suite 13 → 15); R2 tests added
  (D-058: TestLogEntry, 3 tests; suite 15 → 18); R3 sentinel pinned
  (D-059: test_worker_zero_is_sentinel_never_executed, 1 test;
  suite 18 → 19); R4 retry/recovery pinned (D-060:
  test_retry_after_failure_skips_failed_step, 1 test; suite 19 → 20,
  closes T6); R5 tests added (D-061: 2 duplicate-name tests — reject
  + case-insensitive, closes T10; suite 20 → 22); T2 FIXED (D-062:
  TestContextInjection, 7 tests; suite 22 → 29); T3 FIXED (D-063:
  TestDisplayGoldens, 3 end-to-end goldens; suite 29 → 32); T11
  resolved as D-058 side effect; T4, T5, T7-T9 OPEN. Fix campaign:
  next T4, T5, T7-T9, then M-sweep. Suite 32/0/0 GREEN.
- Re-verification pass (2026-08-29, session 17): all three
  integration modules (binio, regab, opt_lbfgs) re-checked — every
  T-item fix in place, all suites GREEN (45/37/13), stale docs
  corrected (line numbers, identifiers, FIXED status); D-051 updated
  + D-052/D-053 written into decisions.md.
- The plan (confirmed by Roberto, 2026-08-28, session close): port
  the ENTIRE pipeline — the original repo brought in module by
  module, this staging workspace's work — with VERIFIED code and
  COMPLETE tests as the goal: a solid base before further evolution
  (Roberto's list of future changes is out of scope for the port).
  Done so far: board.py (2026-08-26, proven complete game kernel),
  pattern.py, mobility.py, feature.py (20/0/1), binio.py (45/0/0),
  regab.py (37/0/0), opt_lbfgs.py (13/0/0) — re-verified all three
  integration modules 2026-08-29 (session 17). The game-loop module
  is NOT in the plan (I-005 resolved).
- Sources live in the `twolm` package under src/ (D-008); unit tests
  in src/twolm/test/. Environment: .venv with the pinned deps (D-010,
  D-051, D-052), twolm installed editable (D-011). Git repo on
  master (D-003). Collaboration memory: AGENTS.md (auto-injected) +
  this file + notes/ (journal in rotating volumes
  log_NNN.md, format rules in log_rules.md — D-055).

## Next steps

- Parked (no action planned): test_pattern T18 noted-only (np.uint8
  3**n_squares overflow — external expressions must cast to int);
  test_pattern M1 (stale PatternSet Raises docstring) — awaiting
  Roberto's go-ahead.
- Reported-only: test_board.py header grammar nit (the
  'environmeant' typo itself fixed 2026-08-29, D-050).
- Feed notes/ideas.md with Roberto's future-evolution ideas.
- Next: state_machine fix campaign item by item — R1-R5 all resolved
  (D-057..D-063); next: T4, T5, T7-T9 (T1/T2/T3/T6/T10/T11 done),
  then M-sweep (M1-M11; M2, M12 done)
  (docs/src/twolm/state_machine.md + docs/src/twolm/test/
  test_state_machine.md).

## Index

- docs/src/twolm/board.md — board.py analysis (distilled + full
  review in appendix; R1-R5 resolved 2026-08-26/29)
- docs/src/twolm/pattern.md — pattern.py analysis (R1-R8 resolved:
  D-020, D-021, D-022; little-endian-only platform note; minor sweep
  complete 19/19: D-023/D-024/D-025 + hygiene/API fixes; Burnside
  attributes D-032)
- docs/src/twolm/test/test_board.md — test_board.py analysis
  (coverage by area, verified values, 11 defects, completeness
  verdict + priorities)
- docs/src/twolm/test/test_pattern.md — test_pattern.py analysis
  (coverage by area, 21 verified facts, defects T1-T19 (T17/T19
  found during the campaign), completeness verdict + P0/P1/P2
  priorities)
- docs/src/twolm/mobility.md — mobility.py analysis (feature index
  formula, n_configurations semantics, sorted-order columns,
  verified V1-V8, R1-R6 applied D-035, minor M1-M5 disposed D-036)
- docs/src/twolm/test/test_mobility.md — test_mobility.py analysis
  (coverage by area, 13 verified facts, defects T1-T9, completeness
  verdict + P0/P1/P2 priorities)
- docs/src/twolm/feature.md — feature.py analysis (first pipeline
  integration module: Feature factories + blocked __new__, FeatureSet
  composition/hash/column layout, verified V1-V8, R1-R4 D-038,
  M1-M4 D-039..D-042 — all disposed)
- docs/src/twolm/test/test_feature.md — test_feature.py analysis
  (coverage by area, 9 verified facts W1-W9, defects T1-T9,
  completeness verdict + P1/P2 priorities; T campaign CLOSED
  D-043..D-050, suite 20/0/1 GREEN)
- docs/src/twolm/binio.md — binio.py analysis (MAGIC framing +
  SHA3-256 sidecar + LZ4 compression; 15 verified facts V1-V15,
  T1-T4 applied D-051, suite 45/0/0 GREEN)
- docs/src/twolm/test/test_binio.md — test_binio.py +
  test_usage_binio.py analysis (12 classes, 45 tests after T4,
  coverage by area)
- docs/src/twolm/regab.md — regab.py analysis (psycopg2 DB access +
  RegabDataSet + binio serialization; 5 verified facts, T1-T7
  applied D-052, suite 37/0/0 GREEN)
- docs/src/twolm/test/test_regab.md — test_regab.py analysis
  (coverage by area, T5-T7 applied D-052, suite 37/0/0 GREEN)
- docs/src/twolm/opt_lbfgs.md — opt_lbfgs.py analysis (L-BFGS:
  strong Wolfe line search + two-loop recursion + warm-start; 5
  verified facts, T1-T7 + 9 new tests D-053, suite 13/0/0 GREEN)
- docs/src/twolm/test/test_opt_lbfgs.md — test_opt_lbfgs.py analysis
  (coverage by area, T7 + 9 new tests D-053, suite 13/0/0 GREEN)
- docs/src/twolm/state_machine.md — state_machine.py analysis (generic
  pipeline orchestrator; 17 verified facts V1-V17; R1 fixed D-057
  (VERY_LOW=4, NONE=5), R2 fixed D-058 (frozen LogEntry dataclass +
  asdict), R3 sentinel documented + pinned D-059, R4 documented +
  pinned D-060, R5 resolved D-061 (unique case-insensitive worker
  names enforced in __init__, closes M12), T2 coverage D-062 (context
  injection pinned; M8 separator contract), T3 goldens D-063 (display
  layer pinned), M1-M11 (M2 done) OPEN; suite 32/0/0 GREEN)
- docs/src/twolm/test/test_state_machine.md — test_state_machine.py
  analysis (32 tests, expectations re-derived, T1 fixed D-057,
  TestLogEntry + sentinel pin + retry pin + 2 duplicate-name + 7
  context-injection + 3 display-goldens tests added
  D-058/D-059/D-060/D-061/D-062/D-063, T11/T6/T10/T2/T3 resolved,
  T4/T5/T7-T9 OPEN, P0/P1/P2 priorities proposed)
- notes/naming.md — canonical board naming convention (row/column,
  D-013; D8 symmetries, D-014)
- notes/decisions.md — decisions log (D-NNN; D-001…D-063)
- notes/ideas.md — future backlog (I-NNN)
- notes/log_rules.md — session-journal format rules (rigid; global session numbering; volume rotation: 25 sessions / 2000 lines per volume, only at session boundaries)
- notes/log_000.md — session journal, volume 000 (sessions 1–..., open)
