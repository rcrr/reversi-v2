# twolm/test/test_lm_worker_positions.py
The test module of the POSITIONS worker (Roberto's file, copied
from the original repo with the D-080-era pipeline enablement;
the D-080 T1-T4 campaign re-anchored it, and step 3 of D-106
moved the D4a-g probe unit checks into it). 2 classes / 9 tests
(2 DB-gated) / no PERF.
> State: D-106 · 585b2ad · 2026-09-04 · suite 9/0/0 (2 DB-gated)

## Coverage

| class | what it pins |
|---|---|
| `TestLMWorkerPositions` (2, `SKIP_REGAB_DB` gated) | the end-to-end cache round-trip on a real data set: `test_read_db_and_populate_cache` (move to POSITIONS, step 2 pinned — the FLAT `rlmwf_02_POSITIONS.dat` + `.SHA3-256` exist on disk and the logs contain "Extracted … positions from the database.") and `test_read_cache_on_new_instance` (a SECOND instance on the same cache dir: the logs contain "Cache successfully loaded and validated" and NOT "Extracted" / "established successfully") |
| `TestIsCacheConsistent` (7, in-memory — no DB, no cache file) | the unit semantics of `is_cache_consistent`: same cfg → True; a differing ec / bid / status / dbname → False; the `bid=`/`status=` keyword overrides win; the str-port (regab) vs int-port (schema) compares equal |

The shared setUp (both classes): the `db_long_gate` FIRST (the
SKIP_REGAB_DB + LONG gates, D-130; where applicable) + stdout patched to a StringIO (logs captured,
output clean) + the D-065 `TemporaryDirectory` idiom (the shared
`CUSTOM_TMP_BASE` from `reversi.test.paths`, `setUpClass` mkdir,
the temp dir created FIRST so a mid-setup failure still leaves a
cleanable dir) + a `LogisticModel` on the `rlm_00.json` fixture
(anchored to `WORKSPACE_ROOT`) with `base_dir_override` = the
tmp dir + a move to CONFIG (the pipeline preconditions pinned:
step 0 `CREATED`, step 1 after the move) + a defensive tearDown.
The unit class builds the cached-side metadata in memory from
the fixture values instead of warming a real cache file.

## Goldens pinned

- The flat cache file names: `rlmwf_02_POSITIONS.dat` +
  `rlmwf_02_POSITIONS.dat.SHA3-256` (the D-078 machine-level
  naming end-to-end — no `rlmwf_/` subdirectory).
- The witness log lines: "Extracted … positions from the
  database." (DB hit) and "Cache successfully loaded and
  validated" (cache hit) — with the NEGATIVE pins "Extracted" /
  "established successfully" absent on the second run.
- The fixture metadata the unit class reuses: `bid [8]`,
  `status ["CMS", "CMR"]`, `ec 20`, `tst_regab @ localhost:5432`
  (the port as the STRING `"5432"` on the regab side).

## Conventions

- The D-065 idiom + the D-085 `WORKSPACE_ROOT`/`CUSTOM_TMP_BASE`
  anchoring (shared `reversi.test.paths`).
- The `SKIP_REGAB_DB` gate at the top of setUp (the test_regab
  pattern) — without it a missing DB would fail setUp for every
  test.
- The unit class stays in memory: the same comparison the probe
  ran against a warmed cache file, but with no DB and no files.

## Integration

- The end-to-end class exercises the real pipeline (CONFIG →
  POSITIONS) through `LogisticModel` with the `rlm_00.json`
  fixture; the unit class pins `is_cache_consistent` directly.
- The two DB-gated tests are the pipeline's live-DB witnesses;
  the 21-check probe re-derives the same behaviour independently.
