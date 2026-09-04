<!-- ARCHIVED — D-106 step 9 (the docs/ rewrite, 2026-09-04): the
     complete session-22 test-doc (D-079/D-080) moved out of
     docs/src/twolm/test/test_lm_worker_positions.md per
     docs_rules.md §1/§4/§6. This is a frozen historical record:
     it is never updated. Stale-in-current-context notes: (1) the
     "1 class / 2 tests" figure is pre-D-106-step-3 — commit
     585b2ad added TestIsCacheConsistent (7 in-memory unit tests
     converted from the D4a-g probe; no DB, no cache file) — the
     suite is now 2 classes / 9 tests (2 DB-gated); (2) the
     D-080 T1-T4 campaign narrative below is frozen history — the
     current re-anchored state is the test file itself + the git
     log. -->

# twolm/test/test_lm_worker_positions.py

Analysis date: 2026-08-30 — analysis session 22 (D-079).

Roberto's file, copied from the original repo together with the
POSITIONS enablement (601de87, the line-by-line pipeline step). 1
class / 2 tests / no PERF. Green on first run at enablement;
D-080 applied T1-T4 (Roberto: "fai tutto anche qui") — test
campaign CLOSED. D-085 (session 23): the D-065 idiom re-anchored
to the shared twolm.test.paths module; the JSON fixture anchored
to WORKSPACE_ROOT.

## Suite status (session 22, D-080)

- `test_lm_worker_positions`: 2/0/0 (both tests DB-gated —
  skipped under `SKIP_REGAB_DB=1`, run with the live DB)
- Full discover: 498 tests, 54 skipped under `SKIP_REGAB_DB=1`
  (17 PERF + 35 regab + 2 positions), GREEN; ungated (live DB):
  498 run, 17 skipped, GREEN.

## Coverage

- setUp: the SKIP_REGAB_DB gate FIRST (T2 — as in test_regab) +
  stdout patched to a StringIO (logs captured, output clean) +
  the D-065 `TemporaryDirectory` idiom (T1, re-anchored D-085 —
  `CUSTOM_TMP_BASE` imported from the shared twolm.test.paths
  module, setUpClass mkdir, TemporaryDirectory created FIRST so
  a mid-setup failure still leaves a cleanable dir) + a
  `LogisticModel` on the `rlm_00.json` fixture (anchored to the
  same `WORKSPACE_ROOT` since D-085; `base_dir_override` = the
  tmp dir) + a move to CONFIG. The
  pipeline preconditions are pinned (step 0 / `CREATED`, step 1
  after the move). Defensive tearDown (stops only the patchers
  / cleans only the temp dir that exist).
- `test_read_db_and_populate_cache` (L96-111): move to
  POSITIONS (step 2 pinned) — the FLAT cache files
  `rlmwf_02_POSITIONS.dat` + `rlmwf_02_POSITIONS.dat.SHA3-256`
  exist on disk (the D-078 machine-level naming pinned
  end-to-end — the latent `rlmwf_/` subdirectory trap never
  materialized) and the logs contain "Extracted ... positions
  from the database." (DB hit).
- `test_read_cache_on_new_instance` (L113-143): the first
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

- T1 FIXED (re-anchored D-085): `tempfile.mkdtemp(dir='./build/
  tmp')` (CWD-relative, assumed `build/tmp` existed) replaced
  with the D-065 idiom — the shared `CUSTOM_TMP_BASE` (imported
  from twolm.test.paths since D-085; originally the per-file
  `Path(__file__).resolve().parents[3]` derivation) +
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
