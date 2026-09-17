# reversi/test/test_wrk_positions.py
The test module of the POSITIONS worker. 3 classes / 12 tests
(5 DB-gated) / no PERF.

## Coverage

| class | what it pins |
|---|---|
| `TestLMWorkerPositions` (2, `SKIP_REGAB_DB` gated) | the end-to-end cache round-trip on a real data set: `test_read_db_and_populate_cache` (the FLAT `rlmwf_03_POSITIONS.dat` + `.SHA3-256` exist on disk and the logs contain "Extracted … positions from the database.") and `test_read_cache_on_new_instance` (a SECOND instance on the same cache dir: the logs contain "Cache successfully loaded and validated" and NOT "Extracted" / "established successfully") |
| `TestIsCacheConsistent` (7, in-memory — no DB, no cache file) | the unit semantics of `is_cache_consistent`: same cfg → True; a differing ec / bid / status / dbname → False; the `bid=`/`status=` keyword overrides win; the str-port (regab) vs int-port (schema) compares equal |
| `TestLMWorkerPositionsDuplicates` (3, `db_long_gate` gated) | the `regab_allow_duplicate` policy on the live DB (fixture bid 8: 200 records, 11 duplicate keys, 189 distinct): `test_dedup_when_flag_false` (rlm_00 re-dumped with the flag `False` → 189 positions/game_values + pop count 189 + the "[TOTAL: 200], [REMOVED: 11], [PERCENT: 5.50%] — removed" log); `test_kept_when_flag_true` (flag `True` → 200 + the "[FOUND: 11] — kept" log); `test_cache_holds_post_policy_content` (a flag-false cache file reloads 189 records + the cache-hit log line + NO "Extracted") |

The shared setUp (both classes): the `db_long_gate` FIRST (the
SKIP_REGAB_DB + LONG gates, where applicable) + stdout patched to a StringIO (logs captured,
output clean) + the `TemporaryDirectory` idiom (the shared
`CUSTOM_TMP_BASE` from `reversi.test.paths`, `setUpClass` mkdir,
the temp dir created FIRST so a mid-setup failure still leaves a
cleanable dir) + a `LogisticModel` on the `rlm_00.json` fixture
(anchored to `WORKSPACE_ROOT`) with `base_dir_override` = the
tmp dir + a move to CONFIG (the pipeline preconditions pinned:
step 0 `CREATED`, step 1 after the move) + a defensive tearDown.
The unit class builds the cached-side metadata in memory from
the fixture values instead of warming a real cache file.

## Goldens pinned

- The flat cache file names: `rlmwf_03_POSITIONS.dat` +
  `rlmwf_03_POSITIONS.dat.SHA3-256` (slot 03 — the
  file-less FEATURES takes 02; the machine-level naming
  end-to-end — no `rlmwf_/` subdirectory).
- The witness log lines: "Extracted … positions from the
  database." (DB hit) and "Cache successfully loaded and
  validated" (cache hit) — with the NEGATIVE pins "Extracted" /
  "established successfully" absent on the second run.
- The fixture metadata the unit class reuses: `bid [8]`,
  `status ["CMS", "CMR"]`, `ec 20`, `tst_regab @ localhost:5432`
  (the port as the STRING `"5432"` on the regab side).
- The live-DB counts (fixture bid 8): **200** total records,
  **11** duplicate (mover, opponent) keys, **189** distinct — the
  `[TOTAL: 200], [REMOVED: 11], [PERCENT: 5.50%]` / `[FOUND: 11]`
  log pins + the 189/200 position-array lengths.

## Conventions

- The `TemporaryDirectory` idiom + the `WORKSPACE_ROOT`/`CUSTOM_TMP_BASE`
  anchoring (shared `reversi.test.paths`).
- The `SKIP_REGAB_DB` gate at the top of setUp (the test_regab
  pattern) — without it a missing DB would fail setUp for every
  test.
- The unit class stays in memory: the same comparison the probe
  ran against a warmed cache file, but with no DB and no files.

## Integration

- The end-to-end class exercises the real pipeline (CONFIG →
  FEATURES → POSITIONS) through
  `LogisticModel` with the `rlm_00.json` fixture; the unit class
  pins `is_cache_consistent` directly.
- The 5 DB-gated tests are the pipeline's live-DB witnesses (the
  2 round-trip + the 3 policy tests); the 21-check probe
  re-derives the same behaviour independently.
