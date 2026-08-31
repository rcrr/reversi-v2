# twolm/test/test_lm_worker_features.py

Analysis date: 2026-08-31 — analysis session 22 (D-081).

Roberto's file, copied from the original repo together with the
FEATURES enablement (f051dd3, the line-by-line pipeline step). 1
class / 1 test / no PERF at analysis (97 lines). Green on first
run at enablement. D-082 applied T1-T4 + M2 (Roberto: "OK" /
"fai" + the golden content test: "Dovremmo avere almeno 1
goldentest che controlla il contenuto di feature_set in
context" — added) — test campaign CLOSED. M1 (the POSITIONS-
dependency comment) left as-is per Roberto's call — recorded at
I-012 (evaluate moving the FEATURES level before POSITIONS).

## Suite status (session 22, D-082)

- `test_lm_worker_features`: 2/0/0 (both tests DB-gated —
  skipped under `SKIP_REGAB_DB=1`, run with the live DB)
- Full discover: 500 tests, 56 skipped under `SKIP_REGAB_DB=1`
  (17 PERF + 35 regab + 2 positions + 2 features), GREEN;
  ungated (live DB): 500 run, 17 skipped (PERF only), GREEN.

## Coverage

- setUp (L71-97): the SKIP_REGAB_DB gate FIRST (T2 — as in
  test_regab) + stdout patched to a StringIO (logs captured,
  output clean) + the D-065 `TemporaryDirectory` idiom (T1 —
  `CUSTOM_TMP_BASE` via `__file__`, setUpClass mkdir,
  TemporaryDirectory created FIRST so a mid-setup failure still
  leaves a cleanable dir) + a `LogisticModel` on the
  `src/twolm/test/data/rlm_00.json` fixture (CWD-relative path,
  `base_dir_override` = the tmp dir, Verbosity.LOW) + the
  pipeline preconditions pinned (step 0 / `CREATED`) + a move to
  'POSITIONS' (step 2 / `POSITIONS` pinned — the DB-dependent
  part; the "as FEATURES depends on the configuration loaded
  there" comment stays — M1 / I-012). Defensive tearDown.
- `test_build_feature_set` (L105-116): `feature_set` is None
  before the level; move to 'FEATURES' (step 3 / `FEATURES`
  pinned); `feature_set` is non-None after.
- `test_feature_set_content_golden` (L118-167, added D-082 per
  Roberto): the rlm_00.json fixture must build the exact
  expected FeatureSet — name 'NoNameFeatureSet' (the schema
  default, the fixture has no name key); the 3 golden hash
  literals (fs `453e918a...5a159` = sha3_256(b'INTERCEPT' +
  mset.hash + pset.hash), mset `2e553593...08a94` — the same
  literal test_mobility pins, pset `04d52f12...c18`); the
  intercept (INTERCEPT, 1/1); the MobilitySet 'BasicMobilitySet'
  with the 3 fixture members in the sorted (mask, amask) order
  (ALMC, LMC, DLMC); the PatternSet 'BasicPatternSet' with the 2
  fixture members in the sorted mask order (EDGE, ELLE); the
  feature list order + per-feature n_configurations /
  n_instances ([INTERCEPT 1/1, ALMC 65/1, LMC 65/1, DLMC 129/1,
  EDGE 6561/4, ELLE 81/8]) + n_instances 16. The goldens were
  independently re-derived (public API, D-081 probe B9).
- Not covered (report-only breadth): the `_down` clearing path
  (probe B12) and the zero-feature guard (probe B11). The R1
  amask log defect (fixed D-082) was DEBUG-level — invisible at
  the test's Verbosity.LOW, pinned by the probe (B8a-c) instead.

## Defects — resolved (D-082)

- T1 — FIXED: the D-065 idiom (CUSTOM_TMP_BASE under build/tmp
  via `__file__`, setUpClass mkdir, TemporaryDirectory created
  FIRST, defensive tearDown) replaces the CWD-relative
  `mkdtemp(dir='./build/tmp')` (the test now runs from any CWD
  and a setUp failure leaks no dir). Pinned by C3.
- T2 — FIXED: the SKIP_REGAB_DB gate at the top of setUp (the
  setUp moves to POSITIONS on a fresh base dir → DB hit; a
  no-DB environment now skips instead of ERRORing) — the
  test_regab pattern. Pinned by C4.
- T3 — FIXED: the dead `from pathlib import Path` import became
  load-bearing with the D-065 idiom (CUSTOM_TMP_BASE). Pinned
  by C5.
- T4 — FIXED: header grammar "How to run the lm_worker_features
  unit tests." + the run note documents the DB requirement and
  the gate. Pinned by C6.

## Minor notes

- M1 (C7): the setUp comment "Move to POSITIONS first, as
  FEATURES depends on the configuration loaded there" —
  inaccurate: FEATURES depends on the config loaded at the
  CONFIG level (step 1), not on POSITIONS; the explicit move is
  also functionally redundant (a `move_to_step('FEATURES')` from
  'CREATED' would run CONFIG + POSITIONS + FEATURES anyway),
  though it does pin the step numbering (POSITIONS = 2). LEFT
  AS-IS per Roberto's call (D-082) — he wants to EVALUATE
  moving the FEATURES level before POSITIONS: recorded at
  I-012. Pinned by C7.
- M2 (C8): FIXED — trailing whitespace on L90 (after the
  'FEATURES' assert) + the 3 whitespace-only lines (L69/L72/L84
  at analysis) removed. Pinned by C8.

## Conventions observed

- stdout patched to StringIO before the model build (as in
  test_lm_worker_positions / test_logistic_model).
- `Verbosity.LOW`: the pipeline logs stay quiet — note the R1
  amask log defect (fixed D-082) was DEBUG-level and therefore
  invisible to this test.
- CWD-relative paths: `json_config` (the header's "Run from the
  workspace root" is load-bearing); the temp base is now
  `__file__`-anchored (T1).

## Appendix — line reference

169 lines, as of D-082.

- L28-44: header (T4 grammar L30, run note L38-43)
- L46-55: imports (T3 `Path` now load-bearing L52)
- L58-60: T1 `CUSTOM_TMP_BASE` (D-065 idiom)
- L64-102: TestLMWorkerFeatures (setUpClass L68, setUp L71-97
  [T2 gate L75-76, T1 TemporaryDirectory L84-85, the M1/I-012
  comment L94], tearDown L99-102)
- L105-116: test_build_feature_set
- L118-167: test_feature_set_content_golden (D-082, per Roberto)
