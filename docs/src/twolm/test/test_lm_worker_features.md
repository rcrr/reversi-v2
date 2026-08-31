# twolm/test/test_lm_worker_features.py

Analysis date: 2026-08-31 — analysis session 22 (D-081).

Roberto's file, copied from the original repo together with the
FEATURES enablement (f051dd3, the line-by-line pipeline step). 1
class / 1 test / no PERF (97 lines). Green on first run at
enablement; OPEN: T1-T4 + M1-M2 (awaiting Roberto's call).

## Suite status (session 22, D-081)

- `test_lm_worker_features`: 1/0/0 (DB-DEPENDENT — the setUp moves
  through POSITIONS, which hits the DB on a fresh base dir; the
  missing SKIP_REGAB_DB gate is T2; run with the live DB)
- Full discover: 499 tests, 54 skipped under `SKIP_REGAB_DB=1`
  (17 PERF + 35 regab + 2 positions; this test RUNS ungated),
  GREEN; ungated (live DB): 499 run, 17 skipped (PERF only),
  GREEN.

## Coverage

- setUp (L59-76): stdout patched to a StringIO (same idiom as the
  other RLM test files) + `tempfile.mkdtemp(dir='./build/tmp')`
  (T1 — CWD-relative, no setUpClass mkdir, no
  TemporaryDirectory) + a `LogisticModel` on the
  `src/twolm/test/data/rlm_00.json` fixture (CWD-relative path,
  `verbosity=LOW`, `base_dir_override` = the tmp dir) + the
  preconditions pinned (step 0 / `CREATED`) + a move to
  'POSITIONS' (step 2 / `POSITIONS` pinned — the DB-dependent
  part, T2).
- `test_build_feature_set` (L82-93): `feature_set` is None before
  the level; move to 'FEATURES' (step 3 / `FEATURES` pinned);
  `feature_set` is non-None after.
- Not covered (report-only breadth): the feature set CONTENT
  (name / hash / members / order / counts — pinned by the D-081
  probe V4-V8 instead), the `_down` clearing path (probe B12), the
  zero-feature guard (probe B11), and the R1 amask log defect
  (invisible at the test's Verbosity.LOW).

## Defects (OPEN)

- T1 — not the D-065 idiom: `tempfile.mkdtemp(dir='./build/tmp')`
  is CWD-relative (the test only runs from the workspace root;
  `build/tmp` must pre-exist — no setUpClass mkdir), no
  TemporaryDirectory, and the tearDown `rmtree` is not inside a
  `finally` (a setUp failure leaks the dir). Same defect pattern
  as test_lm_worker_positions T1 (fixed in D-080). Pinned by C3.
- T2 — no SKIP_REGAB_DB gate: the setUp moves to POSITIONS on a
  fresh tmp dir, so the test hits the DB; in a no-DB environment
  the canonical gated command would ERROR instead of skip. Same
  pattern as test_lm_worker_positions T2 (fixed in D-080). Pinned
  by C4.
- T3 — dead import: `from pathlib import Path` (1 occurrence =
  the import). Pinned by C5.
- T4 — header grammar: "How to use the unit tests
  lm_worker_features module." (house pattern post D-080: "How to
  run the ... unit tests." + the run note should document the DB
  requirement — and the gate, once T2 is fixed). Pinned by C6.

## Minor notes (OPEN)

- M1 (C7): the setUp comment "Move to POSITIONS first, as
  FEATURES depends on the configuration loaded there" —
  inaccurate: FEATURES depends on the config loaded at the CONFIG
  level (step 1), not on POSITIONS; the explicit move is also
  functionally redundant (a `move_to_step('FEATURES')` from
  'CREATED' would run CONFIG + POSITIONS + FEATURES anyway),
  though it does pin the step numbering (POSITIONS = 2).
  Report-only.
- M2 (C8): trailing whitespace on L90 (after the 'FEATURES'
  assert) + 3 whitespace-only lines (L69/L72/L84). Report-only
  (the D-078 M3 scope precedent).

## Conventions observed / deviations

- stdout patched to StringIO before the model build (as in
  test_lm_worker_positions / test_logistic_model).
- `Verbosity.LOW`: the pipeline logs stay quiet — note the R1
  amask log defect is DEBUG-level and therefore invisible to
  this test.
- CWD-relative paths throughout (`json_config`, the mkdtemp
  dir): the header's "Run from the workspace root" is
  load-bearing (T1).

## Appendix — line reference

97 lines, as of D-081.

- L28-41: header (T4 grammar L30, run note L40)
- L43-52: imports (T3 dead `Path` L49)
- L56-80: TestLMWorkerFeatures (setUp L59-76 [T1 L64, T2 — no
  gate, M1 comment L73], tearDown L78-80, test L82-93 [M2 L90])
