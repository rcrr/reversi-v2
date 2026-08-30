# twolm/test/test_lm_worker_positions.py

Analysis date: 2026-08-30 — analysis session 22 (D-079).

Roberto's file, copied from the original repo together with the
POSITIONS enablement (601de87, the line-by-line pipeline step). 1
class / 2 tests / no PERF. Green on first run — no fixes applied
at enablement; the T-items below are OPEN.

## Suite status (session 22, D-079)

- `test_lm_worker_positions`: 2/0/0 (live DB required — T2)
- Full discover: 498 tests, 52 skipped under `SKIP_REGAB_DB=1`,
  GREEN.

## Coverage

- setUp (L60-76): stdout patched to a StringIO (logs captured,
  output clean) + `tempfile.mkdtemp(dir='./build/tmp')` (T1) +
  a `LogisticModel` on the `rlm_00.json` fixture
  (`base_dir_override` = the tmp dir) + a move to CONFIG. The
  pipeline preconditions are pinned (step 0 / `CREATED`, step 1
  after the move).
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

## Defects — OPEN (awaiting Roberto's call)

- T1: `tempfile.mkdtemp(dir='./build/tmp')` is CWD-relative and
  assumes `build/tmp` already exists — the D-065
  `__file__`-anchored idiom is missing (`CUSTOM_TMP_BASE =
  Path(__file__).resolve().parents[3] / 'build' / 'tmp'` +
  setUpClass mkdir + `TemporaryDirectory` FIRST in setUp +
  defensive tearDown), as applied in test_lm_worker_config T1
  and test_cache_manager T6. As written, the test only works
  when CWD = workspace root.
- T2: NO DB gate. Both tests hit the live regab DB (tst_regab)
  — without it, setUp fails for every test. The house pattern is
  `SKIP_REGAB_DB=1` (test_regab: 35 gated tests); a gate here
  would follow the same pattern.
- T3: the dead `if False: sys.__stdout__.write(logs)` blocks in
  BOTH tests (the test_feature T1 / D-043 anti-pattern); the
  `sys` import (L44) is dead with them.
- T4 (report-only): header grammar — "How to use the unit tests
  lm_worker_positions module."

## Verdict

A good, minimal end-to-end pin of the POSITIONS cache round-trip
(DB → file → file, log strings as witnesses); the underlying
behaviour is independently verified by the D-079 probe (49
checks, 0 mismatches). T1-T3 are hygiene/robustness; none
changes what the two tests prove.
