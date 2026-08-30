# twolm/test/test_lm_worker_positions.py

Analysis date: 2026-08-30 — analysis session 22 (D-079).

Roberto's file, copied from the original repo together with the
POSITIONS enablement (601de87, the line-by-line pipeline step). 1
class / 2 tests / no PERF. Green on first run at enablement;
D-080 applied T1-T4 (Roberto: "fai tutto anche qui") — test
campaign CLOSED.

## Suite status (session 22, D-080)

- `test_lm_worker_positions`: 2/0/0 (both tests DB-gated —
  skipped under `SKIP_REGAB_DB=1`, run with the live DB)
- Full discover: 498 tests, 54 skipped under `SKIP_REGAB_DB=1`
  (17 PERF + 35 regab + 2 positions), GREEN; ungated (live DB):
  498 run, 17 skipped, GREEN.

## Coverage

- setUp: the SKIP_REGAB_DB gate FIRST (T2 — as in test_regab) +
  stdout patched to a StringIO (logs captured, output clean) +
  the D-065 `TemporaryDirectory` idiom (T1 — `CUSTOM_TMP_BASE`
  via `__file__`, setUpClass mkdir, TemporaryDirectory created
  FIRST so a mid-setup failure still leaves a cleanable dir) +
  a `LogisticModel` on the `rlm_00.json` fixture
  (`base_dir_override` = the tmp dir) + a move to CONFIG. The
  pipeline preconditions are pinned (step 0 / `CREATED`, step 1
  after the move). Defensive tearDown (stops only the patchers
  / cleans only the temp dir that exist).
- `test_read_db_and_populate_cache` (L82-100): move to
  POSITIONS (step 2 pinned) — the FLAT cache files
  `rlmwf_02_POSITIONS.dat` + `rlmwf_02_POSITIONS.dat.SHA3-256`
  exist on disk (the D-078 machine-level naming pinned
  end-to-end — the latent `rlmwf_/` subdirectory trap never
  materialized) and the logs contain "Extracted ... positions
  from the database." (DB hit).
- `test_read_cache_on_new_instance` (L102-132): the first
  instance moves to POSITIONS (DB hit, warms the cache); a
  SECOND instance on the same cache dir moves to CONFIG, the
  StringIO is cleared, then to POSITIONS: the logs contain
  "Cache successfully loaded and validated" and do NOT contain
  "Extracted" / "established successfully" (cache hit, no DB).

The two tests pin the cache round-trip end-to-end on a real
domain data set: compute + store on the first run, load +
sidecar-verify + business-consistency on the second — with the
log lines as the witnesses.

## Defects — resolved (D-080)

- T1 FIXED: `tempfile.mkdtemp(dir='./build/tmp')` (CWD-relative,
  assumed `build/tmp` existed) replaced with the D-065
  `__file__`-anchored idiom — `CUSTOM_TMP_BASE =
  Path(__file__).resolve().parents[3] / 'build' / 'tmp'` +
  setUpClass mkdir + `TemporaryDirectory` FIRST in setUp +
  defensive tearDown — exactly as applied in test_lm_worker_
  config T1 and test_cache_manager T6.
- T2 FIXED: the SKIP_REGAB_DB gate added at the top of setUp
  (`skipTest('SKIP_REGAB_DB=1: database tests skipped')`, the
  test_regab pattern) — without the gate, a missing DB failed
  setUp for every test.
- T3 FIXED: the dead `if False: sys.__stdout__.write(logs)`
  blocks in both tests removed (the test_feature T1 / D-043
  anti-pattern); the `sys` import went with them.
- T4 FIXED: the header now reads "How to run the lm_worker_
  positions unit tests." (was "How to use the unit tests
  lm_worker_positions module."), and the run note documents the
  DB requirement + the gate.

## Verdict

A good, minimal end-to-end pin of the POSITIONS cache round-trip
(DB → file → file, log strings as witnesses); the underlying
behaviour is independently verified by the D-079 probe
(re-pinned D-080 — 51 checks, 0 mismatches). T1-T4 were
hygiene/robustness; none changes what the two tests prove. Test
campaign CLOSED.
