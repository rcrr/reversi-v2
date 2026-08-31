# twolm/test/test_lm_worker_indexes.py

Analysis date: 2026-08-31 — analysis session 23 (D-083).

Roberto's file, brought in with the INDEXES enablement (a323e0f,
the line-by-line pipeline step 5). 1 class / 2 tests / no PERF.
Green on first run with the live DB. Awaiting Roberto's call:
T1-T3 + M1.

## Suite status (session 23, D-083)

- `test_lm_worker_indexes`: 2/0/0 (NO gate at arrival — the setUp
  moves through POSITIONS on a fresh base dir, so a live DB is
  required; run ungated)
- Full discover: 515 tests, 56 skipped under `SKIP_REGAB_DB=1`
  (17 PERF + 35 regab + 2 positions + 2 features), GREEN; ungated
  (live DB): 515 run, 17 skipped (PERF only), GREEN.

## Coverage

- setUp: stdout patched to a StringIO (logs captured, output
  clean) + `tempfile.mkdtemp(dir='./build/tmp')` (T1: CWD-
  relative, no D-065 idiom) + a `LogisticModel` on the
  `rlm_00.json` fixture (`base_dir_override` = the tmp dir) +
  `move_to_step('FEATURES')` (the comment L75 is ACCURATE —
  "INDEXES depends on the feature_set loaded there"; in contrast
  to the test_lm_worker_features M1 comment, which pointed at
  POSITIONS). The pipeline preconditions are pinned (step 0 /
  `CREATED`, step 3 / `FEATURES` after the move). The NO-gate
  state (T2) means the move through POSITIONS hits the DB.
- `test_compute_and_populate_cache` (L84-101): move to INDEXES
  (step 4 pinned) — the FLAT cache files
  `rlmwf_04_INDEXES.dat` + `rlmwf_04_INDEXES.dat.SHA3-256` exist
  on disk (the D-078 machine-level naming pinned end-to-end) and
  the logs contain "Executing heavy computation"; the context
  holds a non-None `rlm_indexes`.
- `test_read_cache_on_new_instance` (L103-132): the first
  instance moves to INDEXES (compute + store, warms the cache);
  a SECOND instance on the same cache dir moves to FEATURES, the
  StringIO is cleared, then to INDEXES: the logs contain "Cache
  successfully loaded and validated" and do NOT contain
  "Executing heavy computation" (cache hit, nothing recomputed);
  the context holds a non-None `rlm_indexes`.

The two tests pin the cache round-trip end-to-end on a real
domain data set: compute + store on the first run, load +
sidecar-verify + business-consistency on the second — the same
shape as test_lm_worker_positions, one level deeper. What the
tests do NOT pin (probe-only, D-083): the on-disk content /
data-checksum identity (probe C3-C5), the exact feature-set-
hash / rds-checksum metadata, the `_down` clearing (C7), and the
`rlmwf_03_FEATURES*` absence (C2).

## Defects — OPEN (awaiting Roberto's call)

- T1 (E2): NOT the D-065 idiom — `tempfile.mkdtemp(
  dir='./build/tmp')` is CWD-relative (assumes the workspace root
  as CWD and that `build/tmp` exists), with no setUpClass mkdir,
  no `TemporaryDirectory`, and a non-defensive tearDown
  (`shutil.rmtree(self.tmp_dir)`, no getattr guard). The same
  defect as test_lm_worker_positions T1 / test_lm_worker_
  features T1 — the fix is the established `__file__`-anchored
  idiom.
- T2 (E3): NO `SKIP_REGAB_DB` gate — the setUp moves to FEATURES
  (step 3), which runs POSITIONS (a DB hit on a fresh base dir).
  A no-DB environment running the canonical gated command would
  ERROR in setUp instead of skipping. The same defect as
  test_lm_worker_positions T2 / test_lm_worker_features T2 —
  the fix is the `skipTest` gate at the top of setUp.
- T3 (E4): header grammar — "How to use the unit tests
  lm_worker_indexes module." (the established pattern, cf.
  test_lm_worker_positions T4).
- M1 (E7): 13 non-comment trailing-whitespace lines (incl. the
  whitespace-only L137 at EOF). Scope as in D-078 M3: the
  license-header `# ` lines stay.

## Verdict

A good, minimal end-to-end pin of the INDEXES cache round-trip
(compute → file → file, log strings as witnesses); the
underlying behaviour is independently verified by the D-083
probe (47 checks, 0 mismatches). T1-T2 are the same robustness
fixes applied to the two earlier pipeline test files; T3 + M1
are hygiene. None changes what the two tests prove.
